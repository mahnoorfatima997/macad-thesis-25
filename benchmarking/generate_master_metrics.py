"""
Master Metrics Generation Pipeline
Generates comprehensive metrics CSV from thesis_data for benchmarking dashboard
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import glob
from datetime import datetime
from collections import defaultdict
import re

class MasterMetricsGenerator:
    def __init__(self, thesis_data_path="../thesis_data", output_path="results"):
        self.thesis_data_path = Path(thesis_data_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
        
        # Store all metrics
        self.session_metrics = {}
        self.aggregate_metrics = {}
        self.calculation_log = defaultdict(dict)
        
    def generate_master_metrics(self):
        """Main pipeline execution"""
        print("="*60)
        print("MASTER METRICS GENERATION PIPELINE")
        print("="*60)
        
        # Step 1: Load all data sources
        print("\n1. Loading data sources...")
        interactions_data = self.load_interaction_data()
        session_data = self.load_session_json_data()
        linkography_data = self.load_linkography_data()
        
        # Step 2: Calculate per-session metrics
        print("\n2. Calculating per-session metrics...")
        for session_id in interactions_data.keys():
            print(f"   Processing session: {session_id}")
            self.calculate_session_metrics(
                session_id, 
                interactions_data.get(session_id),
                session_data.get(session_id),
                linkography_data.get(session_id)
            )
        
        # Step 3: Calculate aggregate metrics
        print("\n3. Calculating aggregate metrics...")
        self.calculate_aggregate_metrics()
        
        # Step 4: Generate output files
        print("\n4. Generating output files...")
        self.save_master_csv()
        self.save_calculation_log()
        
        print("\n[COMPLETE] Master metrics generation complete!")
        print(f"  - Session metrics: {self.output_path / 'master_session_metrics.csv'}")
        print(f"  - Aggregate metrics: {self.output_path / 'master_aggregate_metrics.csv'}")
        print(f"  - Calculation log: {self.output_path / 'calculation_log.json'}")
        
    def load_interaction_data(self):
        """Load all interaction CSV files"""
        interactions = {}
        pattern = str(self.thesis_data_path / "interactions_*.csv")
        
        for file in glob.glob(pattern):
            try:
                df = pd.read_csv(file)
                if not df.empty:
                    session_id = self.extract_session_id(file)
                    interactions[session_id] = df
                    print(f"   Loaded {len(df)} interactions for session {session_id}")
            except Exception as e:
                print(f"   Error loading {file}: {e}")
                
        return interactions
    
    def load_session_json_data(self):
        """Load session JSON files for test group info"""
        sessions = {}
        pattern = str(self.thesis_data_path / "session_*.json")
        
        for file in glob.glob(pattern):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    session_id = data.get('session_id')
                    if session_id:
                        sessions[session_id] = data
            except Exception as e:
                print(f"   Error loading {file}: {e}")
                
        return sessions
    
    def load_linkography_data(self):
        """Load linkography analysis results"""
        linkography = {}
        pattern = str(self.thesis_data_path / "linkography/linkography_*.json")
        
        for file in glob.glob(pattern):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    session_id = self.extract_session_id(file)
                    linkography[session_id] = data
            except Exception as e:
                print(f"   Error loading {file}: {e}")
                
        return linkography
    
    def extract_session_id(self, filename):
        """Extract session ID from filename"""
        match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', filename)
        return match.group(1) if match else None
    
    def calculate_session_metrics(self, session_id, interactions_df, session_json, linkography_json):
        """Calculate all metrics for a single session"""
        metrics = {'session_id': session_id}
        
        if interactions_df is None or interactions_df.empty:
            self.calculation_log[session_id]['status'] = 'no_data'
            return
        
        # Basic metrics
        metrics['total_interactions'] = len(interactions_df)
        metrics['duration_minutes'] = metrics['total_interactions'] * 2  # Estimate
        
        # Core cognitive metrics
        if 'prevents_cognitive_offloading' in interactions_df.columns:
            metrics['prevention_rate'] = interactions_df['prevents_cognitive_offloading'].sum() / len(interactions_df)
            self.log_calculation(session_id, 'prevention_rate', 'direct', 'prevents_cognitive_offloading column')
        else:
            metrics['prevention_rate'] = 0.5
            self.log_calculation(session_id, 'prevention_rate', 'default', 'column not found')
            
        if 'encourages_deep_thinking' in interactions_df.columns:
            metrics['deep_thinking_rate'] = interactions_df['encourages_deep_thinking'].sum() / len(interactions_df)
            self.log_calculation(session_id, 'deep_thinking_rate', 'direct', 'encourages_deep_thinking column')
        else:
            metrics['deep_thinking_rate'] = 0.5
            self.log_calculation(session_id, 'deep_thinking_rate', 'default', 'column not found')
        
        # Improvement calculation
        baseline_prevention = 0.30
        baseline_thinking = 0.35
        metrics['improvement_score'] = ((metrics['prevention_rate'] - baseline_prevention) / baseline_prevention * 100 +
                                       (metrics['deep_thinking_rate'] - baseline_thinking) / baseline_thinking * 100) / 2
        self.log_calculation(session_id, 'improvement_score', 'calculated', 'from prevention and deep thinking vs baseline')
        
        # Proficiency level
        if metrics['prevention_rate'] > 0.8 and metrics['deep_thinking_rate'] > 0.8:
            metrics['proficiency_level'] = 'expert'
        elif metrics['prevention_rate'] > 0.6 and metrics['deep_thinking_rate'] > 0.6:
            metrics['proficiency_level'] = 'advanced'
        elif metrics['prevention_rate'] > 0.4 or metrics['deep_thinking_rate'] > 0.4:
            metrics['proficiency_level'] = 'intermediate'
        else:
            metrics['proficiency_level'] = 'beginner'
        self.log_calculation(session_id, 'proficiency_level', 'calculated', 'from prevention and deep thinking thresholds')
        
        # Detailed cognitive metrics
        detailed_metrics = self.calculate_detailed_cognitive_metrics(session_id, interactions_df)
        metrics.update(detailed_metrics)
        
        # Now override reflection_depth and problem_solving with actual values
        metrics['reflection_depth'] = metrics['deep_thinking_rate']
        metrics['problem_solving'] = metrics['prevention_rate']
        
        # Recalculate critical thinking with correct values
        if 'confidence_score' in interactions_df.columns:
            confidence = interactions_df['confidence_score'].mean()
            metrics['critical_thinking'] = (metrics['problem_solving'] + metrics['reflection_depth'] + confidence) / 3
        else:
            metrics['critical_thinking'] = (metrics['problem_solving'] + metrics['reflection_depth']) / 2
        
        # Agent effectiveness metrics
        metrics.update(self.calculate_agent_metrics(session_id, interactions_df))
        
        # Anthropomorphism indicators (basic - preserve existing analysis)
        if session_json:
            metrics['test_group'] = session_json.get('test_group', 'unknown')
        else:
            metrics['test_group'] = 'unknown'
            
        # Linkography metrics (basic - preserve existing analysis)
        if linkography_json:
            metrics['linkography_density'] = linkography_json.get('metrics', {}).get('link_density', 0)
            metrics['critical_moves'] = linkography_json.get('metrics', {}).get('critical_moves', 0)
        else:
            metrics['linkography_density'] = 0
            metrics['critical_moves'] = 0
            self.log_calculation(session_id, 'linkography_metrics', 'default', 'linkography data not found')
        
        # Data quality score
        metrics['data_quality_score'] = self.calculate_data_quality(session_id)
        
        # Store
        self.session_metrics[session_id] = metrics
        
    def calculate_detailed_cognitive_metrics(self, session_id, df):
        """Calculate detailed cognitive metrics from interaction data"""
        metrics = {}
        
        # Question Quality
        if 'cognitive_flags_count' in df.columns and 'input_length' in df.columns:
            flags_score = df['cognitive_flags_count'].mean() / 5.0  # Normalize to 0-1
            length_score = df['input_length'].mean() / 100.0  # Normalize to 0-1
            metrics['question_quality'] = min((flags_score + length_score) / 2, 1.0)
            self.log_calculation(session_id, 'question_quality', 'calculated', 'from cognitive_flags_count and input_length')
        else:
            metrics['question_quality'] = 0.5
            self.log_calculation(session_id, 'question_quality', 'default', 'required columns not found')
        
        # Reflection Depth (will be set to deep thinking rate by caller)
        metrics['reflection_depth'] = 0.5  # Temporary, will be overridden
        
        # Concept Integration
        if 'knowledge_integrated' in df.columns:
            integration_val = df['knowledge_integrated'].sum() / len(df) if len(df) > 0 else 0
            metrics['concept_integration'] = integration_val
            self.log_calculation(session_id, 'concept_integration', 'direct', 'knowledge_integrated column')
        elif 'sources_count' in df.columns:
            metrics['concept_integration'] = min(df['sources_count'].mean() / 3.0, 1.0)
            self.log_calculation(session_id, 'concept_integration', 'calculated', 'from sources_count')
        else:
            metrics['concept_integration'] = 0.5
            self.log_calculation(session_id, 'concept_integration', 'default', 'no integration data found')
        
        # Problem Solving (will be set to prevention rate by caller)
        metrics['problem_solving'] = 0.5  # Temporary, will be overridden
        
        # Critical Thinking
        if 'confidence_score' in df.columns:
            confidence = df['confidence_score'].mean()
            metrics['critical_thinking'] = (metrics['problem_solving'] + metrics['reflection_depth'] + confidence) / 3
            self.log_calculation(session_id, 'critical_thinking', 'calculated', 'from problem_solving, reflection, confidence')
        else:
            metrics['critical_thinking'] = (metrics['problem_solving'] + metrics['reflection_depth']) / 2
            self.log_calculation(session_id, 'critical_thinking', 'calculated', 'from problem_solving and reflection only')
        
        # Additional pattern metrics
        if 'provides_scaffolding' in df.columns:
            metrics['scaffolding_effectiveness'] = df['provides_scaffolding'].sum() / len(df)
        else:
            metrics['scaffolding_effectiveness'] = 0.5
            
        if 'maintains_engagement' in df.columns:
            metrics['engagement_rate'] = df['maintains_engagement'].sum() / len(df)
        else:
            metrics['engagement_rate'] = 0.5
            
        return metrics
    
    def calculate_agent_metrics(self, session_id, df):
        """Calculate agent effectiveness metrics"""
        metrics = {}
        
        if 'multi_agent_coordination' in df.columns:
            metrics['agent_coordination'] = df['multi_agent_coordination'].mean()
            self.log_calculation(session_id, 'agent_coordination', 'direct', 'multi_agent_coordination column')
        else:
            metrics['agent_coordination'] = 0.75
            self.log_calculation(session_id, 'agent_coordination', 'default', 'column not found')
            
        if 'response_coherence' in df.columns:
            metrics['response_quality'] = df['response_coherence'].mean()
        else:
            metrics['response_quality'] = 0.8
            
        if 'appropriate_agent_selection' in df.columns:
            metrics['appropriate_selection_rate'] = df['appropriate_agent_selection'].mean()
        else:
            metrics['appropriate_selection_rate'] = 0.85
            
        # Count agent usage from responses
        agent_counts = defaultdict(int)
        if 'agent_response' in df.columns:
            for response in df['agent_response'].dropna():
                response_lower = str(response).lower()
                if 'socratic' in response_lower or 'question' in response_lower:
                    agent_counts['socratic_tutor'] += 1
                if 'expert' in response_lower or 'domain' in response_lower:
                    agent_counts['domain_expert'] += 1
                if 'cognitive' in response_lower or 'thinking' in response_lower:
                    agent_counts['cognitive_enhancement'] += 1
                    
        total_responses = len(df)
        metrics['socratic_usage_rate'] = agent_counts['socratic_tutor'] / total_responses if total_responses > 0 else 0
        metrics['expert_usage_rate'] = agent_counts['domain_expert'] / total_responses if total_responses > 0 else 0
        metrics['cognitive_usage_rate'] = agent_counts['cognitive_enhancement'] / total_responses if total_responses > 0 else 0
        
        return metrics
    
    def calculate_data_quality(self, session_id):
        """Calculate data quality score based on available data"""
        log = self.calculation_log[session_id]
        
        # Count methods used
        method_counts = defaultdict(int)
        for metric, details in log.items():
            if isinstance(details, dict) and 'method' in details:
                method_counts[details['method']] += 1
        
        total = sum(method_counts.values())
        if total == 0:
            return 0
            
        # Score: direct=1.0, calculated=0.7, inferred=0.4, default=0.1
        score = (method_counts['direct'] * 1.0 + 
                method_counts['calculated'] * 0.7 + 
                method_counts['inferred'] * 0.4 + 
                method_counts['default'] * 0.1) / total
                
        return round(score, 2)
    
    def log_calculation(self, session_id, metric, method, source):
        """Log how each metric was calculated"""
        self.calculation_log[session_id][metric] = {
            'method': method,
            'source': source
        }
    
    def calculate_aggregate_metrics(self):
        """Calculate aggregate metrics across all sessions"""
        if not self.session_metrics:
            return
            
        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(list(self.session_metrics.values()))
        
        # List of numeric metrics to aggregate
        numeric_metrics = [
            'prevention_rate', 'deep_thinking_rate', 'improvement_score',
            'question_quality', 'reflection_depth', 'concept_integration',
            'problem_solving', 'critical_thinking', 'scaffolding_effectiveness',
            'engagement_rate', 'agent_coordination', 'response_quality'
        ]
        
        # Calculate aggregates by proficiency level
        for metric in numeric_metrics:
            if metric in df.columns:
                agg_data = {
                    'metric_name': metric,
                    'overall_avg': df[metric].mean(),
                    'overall_std': df[metric].std(),
                    'overall_min': df[metric].min(),
                    'overall_max': df[metric].max()
                }
                
                # By proficiency level
                for level in ['beginner', 'intermediate', 'advanced', 'expert']:
                    level_data = df[df['proficiency_level'] == level][metric]
                    agg_data[f'{level}_avg'] = level_data.mean() if len(level_data) > 0 else 0
                    agg_data[f'{level}_count'] = len(level_data)
                
                self.aggregate_metrics[metric] = agg_data
    
    def save_master_csv(self):
        """Save master metrics to CSV files"""
        # Session-level metrics
        if self.session_metrics:
            session_df = pd.DataFrame(list(self.session_metrics.values()))
            session_df.to_csv(self.output_path / 'master_session_metrics.csv', index=False)
            
        # Aggregate metrics
        if self.aggregate_metrics:
            agg_df = pd.DataFrame(list(self.aggregate_metrics.values()))
            agg_df.to_csv(self.output_path / 'master_aggregate_metrics.csv', index=False)
    
    def save_calculation_log(self):
        """Save calculation log showing data sources"""
        with open(self.output_path / 'calculation_log.json', 'w') as f:
            json.dump(dict(self.calculation_log), f, indent=2)


def main():
    """Run the master metrics generation"""
    generator = MasterMetricsGenerator()
    generator.generate_master_metrics()


if __name__ == "__main__":
    main()