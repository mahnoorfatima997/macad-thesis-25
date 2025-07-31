"""
Integration bridge between test system and benchmarking pipeline
Converts test data to benchmarking format for analysis
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import os
import sys

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarking.linkography_analyzer import LinkographyAnalyzer
from benchmarking.graph_ml_benchmarking import GraphMLBenchmarking
from benchmarking.evaluation_metrics import EvaluationMetrics


class BenchmarkingIntegration:
    """Bridge between test system and benchmarking tools"""
    
    def __init__(self):
        self.test_data_dir = Path("thesis_tests/test_data")
        self.linkography_data_dir = Path("thesis_tests/linkography_data")
        self.benchmarking_input_dir = Path("benchmarking/data/sessions")
        
        # Ensure benchmarking input directory exists
        self.benchmarking_input_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_test_session_for_benchmarking(self, session_id: str):
        """Convert test session data to benchmarking format"""
        
        # Load test session data
        session_file = self.test_data_dir / f"session_{session_id}.json"
        moves_file = self.test_data_dir / f"moves_{session_id}.csv"
        interactions_file = self.test_data_dir / f"interactions_{session_id}.csv"
        metrics_file = self.test_data_dir / f"metrics_{session_id}.csv"
        linkography_file = self.linkography_data_dir / f"linkography_{session_id}.json"
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")
        
        # Load session metadata
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Load moves data
        moves_df = pd.read_csv(moves_file) if moves_file.exists() else pd.DataFrame()
        
        # Load interactions
        interactions_df = pd.read_csv(interactions_file) if interactions_file.exists() else pd.DataFrame()
        
        # Load metrics
        metrics_df = pd.read_csv(metrics_file) if metrics_file.exists() else pd.DataFrame()
        
        # Load linkography
        with open(linkography_file, 'r') as f:
            linkography_data = json.load(f) if linkography_file.exists() else {}
        
        # Convert to benchmarking format
        benchmarking_session = {
            "session_id": session_id,
            "participant_id": session_data.get("participant_id"),
            "test_group": session_data.get("test_group"),
            "start_time": session_data.get("start_time"),
            "end_time": session_data.get("end_time"),
            "duration_minutes": session_data.get("summary", {}).get("duration_minutes", 0),
            
            # Interactions in benchmarking format
            "interactions": self._convert_interactions(interactions_df),
            
            # Design moves
            "design_moves": self._convert_moves(moves_df),
            
            # Cognitive metrics history
            "cognitive_metrics": metrics_df.to_dict('records') if not metrics_df.empty else [],
            
            # Linkography data
            "linkography": linkography_data,
            
            # Assessment scores
            "pre_test_scores": session_data.get("assessments", {}).get("pre_test", {}).get("scores", {}),
            "post_test_scores": session_data.get("assessments", {}).get("post_test", {}).get("scores", {}),
            
            # Summary statistics
            "summary": {
                "total_interactions": len(interactions_df),
                "total_moves": len(moves_df),
                "avg_cognitive_score": session_data.get("summary", {}).get("avg_cognitive_score", 0),
                "cognitive_scores": session_data.get("summary", {}).get("cognitive_scores", {}),
                "phase_distribution": self._calculate_phase_distribution(moves_df)
            }
        }
        
        # Save in benchmarking format
        output_file = self.benchmarking_input_dir / f"session_{session_id}_converted.json"
        with open(output_file, 'w') as f:
            json.dump(benchmarking_session, f, indent=2)
        
        print(f"✅ Converted session {session_id} for benchmarking")
        print(f"   Output: {output_file}")
        
        return output_file
    
    def _convert_interactions(self, interactions_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert interactions to benchmarking format"""
        interactions = []
        
        for _, row in interactions_df.iterrows():
            interaction = {
                "timestamp": row.get("timestamp"),
                "user_input": row.get("user_input"),
                "system_response": row.get("system_response"),
                "interaction_type": row.get("interaction_type"),
                "phase": row.get("phase"),
                "response_time": row.get("response_time", 0),
                "cognitive_metrics": json.loads(row.get("cognitive_metrics", "{}"))
            }
            interactions.append(interaction)
        
        return interactions
    
    def _convert_moves(self, moves_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert design moves to benchmarking format"""
        moves = []
        
        for _, row in moves_df.iterrows():
            move = {
                "move_id": row.get("move_id"),
                "timestamp": row.get("timestamp"),
                "content": row.get("content"),
                "move_type": row.get("move_type"),
                "phase": row.get("phase"),
                "modality": row.get("modality"),
                "design_focus": row.get("design_focus"),
                "move_source": row.get("move_source"),
                "cognitive_load": row.get("cognitive_load"),
                "complexity_score": row.get("complexity_score", 0),
                "ai_influence_strength": row.get("ai_influence_strength"),
                "semantic_links": json.loads(row.get("semantic_links", "[]"))
            }
            moves.append(move)
        
        return moves
    
    def _calculate_phase_distribution(self, moves_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate distribution of moves across phases"""
        if moves_df.empty:
            return {"ideation": 0, "visualization": 0, "materialization": 0}
        
        phase_counts = moves_df['phase'].value_counts()
        total = len(moves_df)
        
        distribution = {}
        for phase in ['IDEATION', 'VISUALIZATION', 'MATERIALIZATION']:
            count = phase_counts.get(phase, 0)
            distribution[phase.lower()] = count / total if total > 0 else 0
        
        return distribution
    
    def batch_convert_sessions(self, session_ids: List[str]):
        """Convert multiple sessions for benchmarking"""
        converted_files = []
        
        for session_id in session_ids:
            try:
                output_file = self.convert_test_session_for_benchmarking(session_id)
                converted_files.append(output_file)
            except Exception as e:
                print(f"❌ Error converting session {session_id}: {e}")
        
        return converted_files
    
    def run_benchmarking_analysis(self, session_ids: List[str]):
        """Run full benchmarking analysis on test sessions"""
        print("🔄 Converting test sessions for benchmarking...")
        
        # Convert sessions
        converted_files = self.batch_convert_sessions(session_ids)
        
        if not converted_files:
            print("❌ No sessions converted successfully")
            return
        
        print(f"\n✅ Converted {len(converted_files)} sessions")
        
        # Run linkography analysis
        print("\n📊 Running linkography analysis...")
        linkography_analyzer = LinkographyAnalyzer()
        
        for file_path in converted_files:
            with open(file_path, 'r') as f:
                session_data = json.load(f)
            
            # Analyze linkography patterns
            linkography_results = linkography_analyzer.analyze_session(session_data)
            print(f"   - Analyzed linkography for session {session_data['session_id']}")
        
        # Run Graph ML analysis
        print("\n🧠 Running Graph ML analysis...")
        graph_ml = GraphMLBenchmarking()
        
        # Load all converted sessions
        sessions = []
        for file_path in converted_files:
            with open(file_path, 'r') as f:
                sessions.append(json.load(f))
        
        # Run graph analysis
        graph_results = graph_ml.analyze_sessions(sessions)
        
        # Calculate evaluation metrics
        print("\n📈 Calculating evaluation metrics...")
        evaluator = EvaluationMetrics()
        
        for session in sessions:
            metrics = evaluator.evaluate_session(session)
            print(f"   - Evaluated session {session['session_id']}: Composite score = {metrics.get('composite', 0):.2%}")
        
        print("\n✅ Benchmarking analysis complete!")
        print("   Run 'python benchmarking/launch_dashboard.py' to view results")
    
    def get_available_test_sessions(self) -> List[str]:
        """Get list of available test session IDs"""
        session_files = list(self.test_data_dir.glob("session_*.json"))
        session_ids = []
        
        for file_path in session_files:
            # Extract session ID from filename
            session_id = file_path.stem.replace("session_", "")
            session_ids.append(session_id)
        
        return session_ids


def main():
    """Main entry point for integration"""
    integration = BenchmarkingIntegration()
    
    # Get available sessions
    session_ids = integration.get_available_test_sessions()
    
    if not session_ids:
        print("❌ No test sessions found. Please run the test dashboard first.")
        return
    
    print(f"Found {len(session_ids)} test sessions:")
    for sid in session_ids:
        print(f"  - {sid}")
    
    # Run analysis
    print("\nStarting benchmarking analysis...")
    integration.run_benchmarking_analysis(session_ids)


if __name__ == "__main__":
    main()