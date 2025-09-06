#!/usr/bin/env python
"""
Mega Architectural Mentor - Cognitive Benchmarking System
Main execution script for running the complete benchmarking pipeline
"""

import sys
import os

from pathlib import Path
import argparse
import json
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import benchmarking modules
from benchmarking.graph_ml_benchmarking import (
    InteractionGraph, CognitiveGNN, CognitiveBenchmarkGenerator
)
from benchmarking.evaluation_metrics import (
    CognitiveMetricsEvaluator, evaluate_all_sessions
)
from benchmarking.visualization_tools import CognitiveBenchmarkVisualizer
from benchmarking.user_proficiency_classifier import (
    UserProficiencyClassifier, generate_training_data_from_sessions
)
from benchmarking.linkography_analyzer import LinkographySessionAnalyzer
from benchmarking.pattern_recognition import CognitivePatternDetector


class BenchmarkingPipeline:
    """Complete benchmarking pipeline for cognitive assessment"""
    
    def __init__(self, data_dir: str = "./thesis_data", output_dir: str = "./benchmarking/results"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.benchmark_generator = CognitiveBenchmarkGenerator()
        self.metrics_evaluator = CognitiveMetricsEvaluator()
        self.visualizer = CognitiveBenchmarkVisualizer(style='scientific')
        self.proficiency_classifier = UserProficiencyClassifier()
        self.linkography_analyzer = LinkographySessionAnalyzer()
        self.pattern_detector = CognitivePatternDetector()
        
        # Results storage
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'sessions_analyzed': 0,
            'benchmarks_generated': {},
            'evaluation_metrics': {},
            'proficiency_classifications': {}
        }
    
    def run_full_pipeline(self, 
                         train_classifier: bool = True,
                         generate_visualizations: bool = True,
                         export_report: bool = True):
        """Run the complete benchmarking pipeline"""
        
        print("\n" + "="*60)
        print("MEGA ARCHITECTURAL MENTOR - COGNITIVE BENCHMARKING SYSTEM")
        print("="*60 + "\n")
        
        # Step 1: Load and validate data
        print("Step 1: Loading interaction data...")
        session_files = self._load_session_data()
        
        if not session_files:
            print("[X] No interaction data found. Please run some sessions first.")
            return
        
        print(f"[OK] Found {len(session_files)} session files")
        self.results['sessions_analyzed'] = len(session_files)
        
        # Warn about minimum data requirements
        if len(session_files) < 3:
            print("\n[!]  Warning: Limited data available")
            print("   - Clustering will use rule-based assignment instead of ML clustering")
            print("   - For best results, collect at least 3-5 sessions")
            print("   - Proficiency classifier requires at least 5 sessions\n")
        
        # Step 2: Process data into graphs
        print("\nStep 2: Processing data into interaction graphs...")
        graphs = self._process_interaction_graphs(session_files)
        print(f"[OK] Created {len(graphs)} interaction graphs")
        
        # Step 3: Train GNN model
        print("\nStep 3: Training Graph Neural Network model...")
        self._train_gnn_model(graphs)
        print("[OK] GNN model trained successfully")
        
        # Step 4: Generate cognitive benchmarks
        print("\nStep 4: Generating cognitive benchmarks...")
        benchmarks = self._generate_benchmarks(graphs)
        print(f"[OK] Generated {len(benchmarks)} proficiency benchmarks")
        
        # Step 5: Evaluate sessions
        print("\nStep 5: Evaluating cognitive metrics...")
        evaluation_results = self._evaluate_sessions(session_files)
        print("[OK] Session evaluation complete")
        
        # Step 6: Linkography Analysis
        print("\nStep 6: Performing linkography analysis...")
        linkography_results = self._perform_linkography_analysis(session_files)
        print(f"[OK] Linkography analysis complete for {len(linkography_results)} sessions")
        
        # Step 7: Train proficiency classifier
        if train_classifier:
            print("\nStep 7: Training user proficiency classifier...")
            self._train_proficiency_classifier(session_files)
            print("[OK] Proficiency classifier trained")
        
        # Step 8: Generate visualizations
        if generate_visualizations:
            print("\nStep 8: Generating visualizations...")
            self._generate_visualizations(graphs, benchmarks, evaluation_results, linkography_results)
            print("[OK] Visualizations generated")
        
        # Step 9: Personality Analysis
        print("\nStep 9: Performing personality analysis...")
        personality_results = self._perform_personality_analysis(session_files)
        print(f"[OK] Personality analysis complete for {len(personality_results)} sessions")
        
        # Step 10: Export comprehensive report
        if export_report:
            print("\nStep 10: Generating final report...")
            self._export_comprehensive_report()
            print("[OK] Report exported")
        
        print("\n" + "="*60)
        print("BENCHMARKING COMPLETE!")
        print("="*60)
        self._print_summary()
    
    def _load_session_data(self) -> List[Path]:
        """Load all valid session data files with required columns"""
        
        # Import session validator
        from session_validator import get_valid_session_files
        
        # Get only valid files with all required columns
        valid_files = get_valid_session_files(self.data_dir)
        
        # Additional check for non-empty files
        final_valid_files = []
        for file in valid_files:
            try:
                df = pd.read_csv(file)
                if len(df) > 0:
                    final_valid_files.append(file)
                else:
                    print(f"  [!]  Skipping empty file {file.name}")
            except Exception as e:
                print(f"  [!]  Skipping invalid file {file.name}: {str(e)}")
        
        return final_valid_files
    
    def _process_interaction_graphs(self, session_files: List[Path]) -> List[InteractionGraph]:
        """Process session data into interaction graphs"""
        
        graphs = []
        
        for i, session_file in enumerate(session_files):
            print(f"  Processing session {i+1}/{len(session_files)}...", end='\r')
            
            try:
                graph = self.benchmark_generator.process_session_data(str(session_file))
                graphs.append(graph)
            except Exception as e:
                print(f"\n  [!]  Error processing {session_file.name}: {str(e)}")
        
        print()  # New line after progress
        return graphs
    
    def _train_gnn_model(self, graphs: List[InteractionGraph]):
        """Train the Graph Neural Network model"""
        
        self.benchmark_generator.train_gnn_model(graphs, epochs=50)
        
        # Save the model
        model_path = self.output_dir / "gnn_model.pkl"
        self.benchmark_generator.save_model(str(model_path))
    
    def _generate_benchmarks(self, graphs: List[InteractionGraph]) -> Dict[str, Any]:
        """Generate cognitive benchmarks from graphs"""
        
        # Generate proficiency clusters
        cluster_analysis = self.benchmark_generator.generate_proficiency_clusters(graphs)
        
        # Create benchmark profiles
        benchmarks = self.benchmark_generator.create_benchmark_profiles(cluster_analysis)
        
        # Store results
        self.results['benchmarks_generated'] = benchmarks
        self.results['cluster_analysis'] = cluster_analysis
        
        # Generate benchmark report
        report_path = self.output_dir / "benchmark_report.json"
        self.benchmark_generator.generate_benchmark_report(str(report_path))
        
        return benchmarks
    
    def _perform_linkography_analysis(self, session_files: List[Path]) -> Dict[str, Any]:
        """Perform linkography analysis on session data"""
        
        linkography_results = {}
        
        for i, session_file in enumerate(session_files):
            print(f"  Analyzing linkography for session {i+1}/{len(session_files)}...", end='\r')
            
            try:
                # Load evaluation report for this session
                session_id = session_file.stem.replace('interactions_', '')
                eval_report_path = self.output_dir / "evaluation_reports" / f"session_{session_id}_evaluation.json"
                
                if eval_report_path.exists():
                    with open(eval_report_path, 'r') as f:
                        session_data = json.load(f)
                    
                    # Load interaction data and add to session_data
                    interactions_df = pd.read_csv(session_file)
                    session_data['interaction_analysis'] = {
                        'interactions': interactions_df.to_dict('records')
                    }
                    
                    # Perform linkography analysis
                    linkography_report = self.linkography_analyzer.analyze_session(session_data)
                    
                    if linkography_report:
                        linkography_results[session_id] = linkography_report
                
            except Exception as e:
                print(f"\n  [!]  Error in linkography analysis for {session_file.name}: {str(e)}")
        
        print()  # New line after progress
        
        # Store results
        self.results['linkography_analysis'] = linkography_results
        
        # Generate aggregated linkography report
        if linkography_results:
            aggregated_report = self._generate_aggregated_linkography_report(linkography_results)
            self.results['aggregated_linkography'] = aggregated_report
            
            # Export aggregated report
            aggregated_path = self.output_dir / "aggregated_linkography_report.json"
            with open(aggregated_path, 'w') as f:
                json.dump(aggregated_report, f, indent=2)
        
        return linkography_results
    
    def _load_session_data_for_linkography(self, session_file: Path) -> Dict[str, Any]:
        """Load session data in format suitable for linkography analysis"""
        
        try:
            # Load interaction data
            interactions_df = pd.read_csv(session_file)
            
            # Load design moves if available
            session_id = session_file.stem.replace('interactions_', '')
            design_moves_file = self.data_dir / f"design_moves_{session_id}.csv"
            
            design_moves = []
            if design_moves_file.exists():
                design_moves_df = pd.read_csv(design_moves_file)
                design_moves = design_moves_df.to_dict('records')
            
            # Load session summary if available
            session_summary_file = self.data_dir / f"session_summary_{session_id}.json"
            session_summary = {}
            if session_summary_file.exists():
                with open(session_summary_file, 'r') as f:
                    session_summary = json.load(f)
            
            return {
                "session_id": session_id,
                "interactions": interactions_df.to_dict('records'),
                "design_moves": design_moves,
                "session_summary": session_summary
            }
            
        except Exception as e:
            print(f"  [!]  Error loading session data: {str(e)}")
            return {}
    
    def _generate_aggregated_linkography_report(self, linkography_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate aggregated linkography analysis report"""
        
        if not linkography_results:
            return {}
        
        # Aggregate metrics across sessions
        # Handle LinkographSession objects
        total_moves = 0
        total_links = 0
        similarities = []
        total_overload_sessions = 0
        total_fixation_sessions = 0
        total_breakthroughs = 0
        
        for session in linkography_results.values():
            # Check if it's a LinkographSession object
            if hasattr(session, 'overall_metrics'):
                # Extract metrics from LinkographSession object
                if session.linkographs:
                    for linkograph in session.linkographs:
                        total_moves += len(linkograph.moves)
                        total_links += len(linkograph.links)
                
                if session.overall_metrics:
                    if session.overall_metrics.avg_link_strength > 0:
                        similarities.append(session.overall_metrics.avg_link_strength)
                
                # Check patterns
                for pattern in session.patterns_detected:
                    if pattern.pattern_type == 'cognitive_overload':
                        total_overload_sessions += 1
                        break
                
                for pattern in session.patterns_detected:
                    if pattern.pattern_type == 'design_fixation':
                        total_fixation_sessions += 1
                        break
                
                total_breakthroughs += len([p for p in session.patterns_detected 
                                          if p.pattern_type == 'creative_breakthrough'])
            else:
                # Fallback for dictionary format (if any)
                total_moves += session.get('moves_summary', {}).get('total_moves', 0)
                total_links += session.get('links_summary', {}).get('total_links', 0)
                avg_sim = session.get('links_summary', {}).get('average_similarity', 0)
                if avg_sim > 0:
                    similarities.append(avg_sim)
        
        avg_similarity = np.mean(similarities) if similarities else 0
        
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_sessions": len(linkography_results),
                "analysis_type": "aggregated_linkography"
            },
            "aggregated_metrics": {
                "total_moves": total_moves,
                "total_links": total_links,
                "average_similarity": avg_similarity,
                "average_moves_per_session": total_moves / len(linkography_results) if linkography_results else 0,
                "average_links_per_session": total_links / len(linkography_results) if linkography_results else 0
            },
            "cognitive_patterns_summary": {
                "sessions_with_overload": total_overload_sessions,
                "sessions_with_fixation": total_fixation_sessions,
                "total_breakthroughs": total_breakthroughs,
                "overload_percentage": (total_overload_sessions / len(linkography_results)) * 100 if linkography_results else 0,
                "fixation_percentage": (total_fixation_sessions / len(linkography_results)) * 100 if linkography_results else 0
            },
            "session_details": self._convert_linkography_sessions_to_dict(linkography_results)
        }
    
    def _convert_linkography_sessions_to_dict(self, linkography_results: Dict[str, Any]) -> Dict[str, Any]:
        """Convert LinkographSession objects to dictionaries for serialization"""
        converted = {}
        for session_id, session in linkography_results.items():
            if hasattr(session, 'overall_metrics'):
                # Convert LinkographSession to dictionary
                # Calculate totals from linkographs
                total_moves_session = sum(len(lg.moves) for lg in session.linkographs) if session.linkographs else 0
                total_links_session = sum(len(lg.links) for lg in session.linkographs) if session.linkographs else 0
                
                converted[session_id] = {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'start_time': session.start_time,
                    'end_time': session.end_time,
                    'num_linkographs': len(session.linkographs),
                    'total_moves': total_moves_session,
                    'total_links': total_links_session,
                    'overall_metrics': {
                        'link_density': session.overall_metrics.link_density if session.overall_metrics else 0,
                        'avg_link_strength': session.overall_metrics.avg_link_strength if session.overall_metrics else 0,
                        'critical_move_ratio': session.overall_metrics.critical_move_ratio if session.overall_metrics else 0,
                        'entropy': session.overall_metrics.entropy if session.overall_metrics else 0
                    },
                    'patterns_detected': [p.pattern_type for p in session.patterns_detected],
                    'cognitive_mapping': {
                        'cognitive_offloading_prevention': session.cognitive_mapping.cognitive_offloading_prevention,
                        'deep_thinking_engagement': session.cognitive_mapping.deep_thinking_engagement,
                        'knowledge_integration': session.cognitive_mapping.knowledge_integration,
                        'scaffolding_effectiveness': session.cognitive_mapping.scaffolding_effectiveness,
                        'learning_progression': session.cognitive_mapping.learning_progression,
                        'metacognitive_awareness': session.cognitive_mapping.metacognitive_awareness
                    } if session.cognitive_mapping else {}
                }
            else:
                # Already a dictionary
                converted[session_id] = session
        return converted
    
    def _evaluate_sessions(self, session_files: List[Path]) -> Dict[str, Any]:
        """Evaluate cognitive metrics for all sessions"""
        
        all_metrics = []
        
        for session_file in session_files:
            session_data = pd.read_csv(session_file)
            metrics = self.metrics_evaluator.evaluate_session(session_data)
            all_metrics.append(metrics)
        
        # Calculate aggregate metrics
        aggregate_metrics = self._calculate_aggregate_metrics(all_metrics)
        self.results['evaluation_metrics'] = aggregate_metrics
        
        # Save individual reports
        reports_dir = self.output_dir / "evaluation_reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Clean up old evaluation reports that don't match current sessions
        current_session_ids = {metrics['session_id'] for metrics in all_metrics}
        for old_report in reports_dir.glob("session_*_evaluation.json"):
            # Extract session ID from filename
            session_id = old_report.stem.replace('session_', '').replace('_evaluation', '')
            if session_id not in current_session_ids:
                old_report.unlink()  # Delete old report
        
        for metrics in all_metrics:
            report_path = reports_dir / f"session_{metrics['session_id']}_evaluation.json"
            self.metrics_evaluator.generate_evaluation_report(metrics, str(report_path))
        
        return aggregate_metrics
    
    def _train_proficiency_classifier(self, session_files: List[Path]):
        """Train the user proficiency classifier"""
        
        # Generate training data
        training_data = generate_training_data_from_sessions(
            [str(f) for f in session_files]
        )
        
        if len(training_data) < 5:
            print("  [!]  Insufficient data for classifier training (need at least 5 sessions)")
            return
        
        # Train classifier
        self.proficiency_classifier.train_classifier(training_data, model_type='ensemble')
        
        # Save model
        model_path = self.output_dir / "proficiency_classifier.pkl"
        self.proficiency_classifier.save_model(str(model_path))
        
        # Classify all sessions
        classifications = {}
        for session_file in session_files:
            session_data = pd.read_csv(session_file)
            result = self.proficiency_classifier.classify_user(session_data)
            classifications[session_file.stem] = result
        
        self.results['proficiency_classifications'] = classifications
    
    def _generate_visualizations(self, 
                               graphs: List[InteractionGraph],
                               benchmarks: Dict[str, Any],
                               evaluation_results: Dict[str, Any],
                               linkography_results: Dict[str, Any] = None):
        """Generate all visualizations"""
        
        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # 1. Interaction graph visualization (first 3 graphs)
        for i, graph in enumerate(graphs[:3]):
            graph_path = viz_dir / f"interaction_graph_{i+1}.html"
            self.visualizer.visualize_interaction_graph(
                graph.graph, 
                title=f"Session {i+1} Interaction Graph",
                save_path=str(graph_path),
                interactive=True
            )
        
        # 2. Proficiency dashboard
        if 'cluster_analysis' in self.results:
            dashboard_path = viz_dir / "proficiency_dashboard.html"
            session_metrics = self.metrics_evaluator.metrics_history
            self.visualizer.create_proficiency_dashboard(
                self.results['cluster_analysis']['cluster_profiles'],
                session_metrics,
                save_path=str(dashboard_path)
            )
        
        # 3. Benchmark comparison
        if benchmarks and self.results.get('evaluation_metrics'):
            comparison_path = viz_dir / "benchmark_comparison.html"
            self.visualizer.visualize_benchmark_comparison(
                benchmarks,
                self.results['evaluation_metrics'],
                save_path=str(comparison_path)
            )
        
        # 4. Cognitive flow diagram
        if graphs:
            # Import session validator
            from session_validator import get_valid_session_files
            
            # Combine data from valid sessions only for flow analysis
            all_data = []
            valid_files = get_valid_session_files(self.data_dir)
            for session_file in valid_files:
                df = pd.read_csv(session_file)
                all_data.append(df)
            
            if all_data:
                combined_data = pd.concat(all_data, ignore_index=True)
                flow_path = viz_dir / "cognitive_flow.html"
                self.visualizer.create_cognitive_flow_diagram(
                    combined_data,
                    save_path=str(flow_path)
                )
        
        # 5. Generate static visualizations from benchmark generator
        self.benchmark_generator.visualize_cognitive_patterns(
            graphs, 
            save_path=str(viz_dir)
        )
        
        # 6. Export all dashboard visualizations
        print("\nExporting comprehensive dashboard visualizations...")
        try:
            from benchmarking.export_all_visualizations import BenchmarkVisualizationExporter
            viz_exporter = BenchmarkVisualizationExporter(results_path=str(self.output_dir))
            viz_exporter.export_all_visualizations()
        except ImportError:
            # Try direct import if running from benchmarking directory
            try:
                from export_all_visualizations import BenchmarkVisualizationExporter
                viz_exporter = BenchmarkVisualizationExporter(results_path=str(self.output_dir))
                viz_exporter.export_all_visualizations()
            except Exception as e:
                print(f"  [!]  Warning: Could not export all visualizations: {str(e)}")
        except Exception as e:
            print(f"  [!]  Warning: Could not export all visualizations: {str(e)}")
        
        # 7. Export Graph ML visualizations
        print("\nExporting interactive Graph ML visualizations...")
        try:
            from benchmarking.graph_ml_interactive import InteractiveGraphMLVisualizer
            graph_viz = InteractiveGraphMLVisualizer(results_path=str(self.output_dir))
            graph_viz.export_all_interactive_visualizations()
        except ImportError:
            # Try direct import if running from benchmarking directory
            try:
                from graph_ml_interactive import InteractiveGraphMLVisualizer
                graph_viz = InteractiveGraphMLVisualizer(results_path=str(self.output_dir))
                graph_viz.export_all_interactive_visualizations()
            except Exception as e:
                print(f"  [!]  Warning: Could not export interactive Graph ML visualizations: {str(e)}")
        except Exception as e:
            print(f"  [!]  Warning: Could not export interactive Graph ML visualizations: {str(e)}")
        
        # 8. Export PyVis interactive visualizations
        print("\nExporting PyVis interactive visualizations...")
        try:
            from benchmarking.graph_ml_pyvis import PyVisGraphMLVisualizer
            pyvis_viz = PyVisGraphMLVisualizer(results_path=str(self.output_dir))
            pyvis_viz.export_all_visualizations()
        except ImportError:
            # Try direct import if running from benchmarking directory
            try:
                from graph_ml_pyvis import PyVisGraphMLVisualizer
                pyvis_viz = PyVisGraphMLVisualizer(results_path=str(self.output_dir))
                pyvis_viz.export_all_visualizations()
            except Exception as e:
                print(f"  [!]  Warning: Could not export PyVis visualizations: {str(e)}")
        except Exception as e:
            print(f"  [!]  Warning: Could not export PyVis visualizations: {str(e)}")
    
    def _calculate_aggregate_metrics(self, all_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all sessions"""
        
        if not all_metrics:
            return {}
        
        aggregate = {
            'total_sessions': len(all_metrics),
            'total_interactions': sum(m['total_interactions'] for m in all_metrics),
            'avg_session_duration': np.mean([m['duration_minutes'] for m in all_metrics]),
            
            # Cognitive metrics
            'avg_cognitive_offloading_prevention': np.mean([
                m['cognitive_offloading_prevention']['overall_rate'] for m in all_metrics
            ]),
            'avg_deep_thinking_engagement': np.mean([
                m['deep_thinking_engagement']['overall_rate'] for m in all_metrics
            ]),
            'avg_scaffolding_effectiveness': np.mean([
                m['scaffolding_effectiveness']['overall_rate'] for m in all_metrics
            ]),
            'avg_knowledge_integration': np.mean([
                m['knowledge_integration']['integration_rate'] for m in all_metrics
            ]),
            
            # Improvement metrics
            'avg_improvement_over_baseline': np.mean([
                m['improvement_over_baseline']['overall_improvement'] for m in all_metrics
            ]),
            
            # Skill progression
            'sessions_with_progression': sum(
                1 for m in all_metrics 
                if m['skill_progression']['progression_score'] > 0
            ),
            
            # Agent effectiveness
            'avg_agent_coordination': np.mean([
                m['agent_coordination_score'] for m in all_metrics
            ])
        }
        
        return aggregate
    
    def _perform_personality_analysis(self, session_files: List[Path]) -> List[Any]:
        """Perform personality analysis on session data"""
        
        # First, run personality analysis validation
        print("  Running personality analysis validation...")
        validation_success = self._validate_personality_setup()
        
        if not validation_success:
            print("  [!] Personality analysis validation failed - skipping analysis")
            return []
        
        try:
            # Import personality analysis modules
            from personality_processor import PersonalityProcessor
            
            print("  Initializing personality analyzer...")
            processor = PersonalityProcessor()
            
            # Find session files and process them
            session_file_map = processor.find_session_files()
            
            if not session_file_map:
                print("  [!] No session files found for personality analysis")
                return []
            
            personality_profiles = []
            total_sessions = len(session_file_map)
            
            for i, (session_id, files) in enumerate(session_file_map.items()):
                print(f"  Analyzing personality for session {i+1}/{total_sessions}: {session_id}...", end='\r')
                
                try:
                    profile = processor.process_single_session(session_id, files)
                    if profile:
                        personality_profiles.append(profile)
                        # Save individual profile
                        processor.save_personality_profile(profile)
                        
                except Exception as e:
                    print(f"\n  [!] Failed to analyze session {session_id}: {e}")
                    continue
            
            # Generate batch summary and correlations
            if personality_profiles:
                print(f"\n  Generating personality analysis summary...")
                processor.save_batch_summary(personality_profiles)
                processor.correlate_with_cognitive_metrics(personality_profiles)
                
                # Validate results
                validation = processor.validate_data_quality(personality_profiles)
                mean_reliability = validation['quality_metrics'].get('mean_reliability', 0)
                
                print(f"  [INFO] Mean analysis reliability: {mean_reliability:.2f}")
                
                if mean_reliability < 0.6:
                    print(f"  [!] Warning: Low average reliability score")
                
            return personality_profiles
            
        except ImportError:
            print("  [!] Personality analysis modules not available")
            print("      Make sure you installed all requirements: pip install -r requirements.txt")
            return []
        except Exception as e:
            print(f"  [ERROR] Personality analysis failed: {e}")
            return []
    
    def _validate_personality_setup(self) -> bool:
        """Validate personality analysis setup and dependencies"""
        
        try:
            # Test imports
            from personality_models import PersonalityProfile, HEXACOModel
            from personality_analyzer import PersonalityAnalyzer, create_analyzer_with_fallback
            from personality_processor import PersonalityProcessor
            from personality_visualizer import PersonalityVisualizer
            from personality_dashboard import PersonalityDashboard
            print("    [OK] All personality modules imported successfully")
            
            # Test analyzer initialization
            analyzer = create_analyzer_with_fallback()
            print(f"    [OK] Analyzer initialized: BERT={analyzer.is_available}, Fallback={analyzer.use_fallback}")
            
            # Test basic text analysis
            sample_text = """I enjoy working on creative projects that explore new possibilities. 
            I prefer to work systematically and organize my thoughts carefully. I like collaborating 
            with others and value different perspectives. I try to be thorough in my analysis."""
            
            profile = analyzer.analyze_text(sample_text)
            if profile.traits:
                print(f"    [OK] Text analysis working: {len(profile.traits)} traits analyzed")
            else:
                print("    [WARN] Text analysis returned no traits")
                return False
            
            # Test data directories
            results_dir = Path("benchmarking/results/personality_reports")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            viz_dir = Path("benchmarking/results/personality_visualizations")  
            viz_dir.mkdir(parents=True, exist_ok=True)
            
            print("    [OK] Data directories ready")
            
            # Test color integration
            from personality_models import PersonalityColorMapper
            from thesis_colors import THESIS_COLORS
            
            color_mapper = PersonalityColorMapper()
            trait_color = color_mapper.get_trait_color("openness")
            if trait_color in THESIS_COLORS.values():
                print("    [OK] Color scheme integration working")
            else:
                print("    [WARN] Color scheme integration issue")
            
            print("    [OK] Personality analysis validation passed")
            return True
            
        except ImportError as e:
            print(f"    [ERROR] Import failed: {e}")
            print("    [!] Install missing dependencies: pip install -r requirements.txt")
            return False
        except Exception as e:
            print(f"    [ERROR] Validation failed: {e}")
            return False
    
    def _export_comprehensive_report(self):
        """Export comprehensive benchmarking report"""
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'system_version': '1.0.0',
                'sessions_analyzed': self.results['sessions_analyzed']
            },
            'executive_summary': self._generate_executive_summary(),
            'benchmarks': self.results.get('benchmarks_generated', {}),
            'evaluation_metrics': self.results.get('evaluation_metrics', {}),
            'proficiency_analysis': self._analyze_proficiency_distribution(),
            'recommendations': self._generate_system_recommendations(),
            'thesis_insights': self._generate_thesis_insights()
        }
        
        # Save main report
        report_path = self.output_dir / "comprehensive_benchmark_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable summary
        summary_path = self.output_dir / "benchmark_summary.md"
        self._write_markdown_summary(report, summary_path)
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of benchmarking results"""
        
        metrics = self.results.get('evaluation_metrics', {})
        
        return {
            'key_findings': [
                f"Analyzed {self.results['sessions_analyzed']} tutoring sessions",
                f"Cognitive offloading prevention rate: {metrics.get('avg_cognitive_offloading_prevention', 0):.1%}",
                f"Deep thinking engagement: {metrics.get('avg_deep_thinking_engagement', 0):.1%}",
                f"Average improvement over baseline: {metrics.get('avg_improvement_over_baseline', 0):.1f}%"
            ],
            'system_effectiveness': self._assess_overall_effectiveness(),
            'primary_strengths': self._identify_primary_strengths(),
            'areas_for_improvement': self._identify_improvement_areas()
        }
    
    def _analyze_proficiency_distribution(self) -> Dict[str, Any]:
        """Analyze distribution of user proficiency levels"""
        
        classifications = self.results.get('proficiency_classifications', {})
        
        if not classifications:
            return {'message': 'No proficiency classifications available'}
        
        # Count proficiency levels
        proficiency_counts = {}
        for session, result in classifications.items():
            level = result['proficiency_level']
            proficiency_counts[level] = proficiency_counts.get(level, 0) + 1
        
        # Calculate percentages
        total = sum(proficiency_counts.values())
        proficiency_percentages = {
            level: (count / total) * 100 
            for level, count in proficiency_counts.items()
        }
        
        return {
            'distribution': proficiency_counts,
            'percentages': proficiency_percentages,
            'insights': self._generate_proficiency_insights(proficiency_percentages)
        }
    
    def _generate_system_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations for system improvement"""
        
        recommendations = []
        metrics = self.results.get('evaluation_metrics', {})
        
        # Based on cognitive metrics
        if metrics.get('avg_cognitive_offloading_prevention', 0) < 0.7:
            recommendations.append({
                'area': 'Socratic Questioning',
                'recommendation': 'Enhance Socratic agent to better prevent cognitive offloading',
                'priority': 'high',
                'implementation': 'Improve question generation algorithms and response patterns'
            })
        
        if metrics.get('avg_deep_thinking_engagement', 0) < 0.6:
            recommendations.append({
                'area': 'Critical Thinking',
                'recommendation': 'Develop more sophisticated prompts for deep thinking',
                'priority': 'high',
                'implementation': 'Add complexity layers to agent responses'
            })
        
        if metrics.get('avg_agent_coordination', 0) < 0.7:
            recommendations.append({
                'area': 'Multi-Agent Coordination',
                'recommendation': 'Improve agent orchestration for coherent responses',
                'priority': 'medium',
                'implementation': 'Refine LangGraph routing logic and state management'
            })
        
        # Based on proficiency distribution
        prof_dist = self._analyze_proficiency_distribution()
        if prof_dist.get('percentages', {}).get('beginner', 0) > 50:
            recommendations.append({
                'area': 'Beginner Support',
                'recommendation': 'Enhance scaffolding for beginner users',
                'priority': 'high',
                'implementation': 'Develop adaptive difficulty progression'
            })
        
        return recommendations
    
    def _generate_thesis_insights(self) -> Dict[str, Any]:
        """Generate insights relevant to thesis research"""
        
        metrics = self.results.get('evaluation_metrics', {})
        
        return {
            'cognitive_offloading_prevention': {
                'effectiveness': metrics.get('avg_cognitive_offloading_prevention', 0),
                'interpretation': self._interpret_offloading_prevention(
                    metrics.get('avg_cognitive_offloading_prevention', 0)
                ),
                'thesis_implication': 'System successfully encourages independent thinking'
                if metrics.get('avg_cognitive_offloading_prevention', 0) > 0.7
                else 'Further development needed to prevent cognitive dependency'
            },
            'multi_agent_effectiveness': {
                'coordination_score': metrics.get('avg_agent_coordination', 0),
                'interpretation': 'Agents work cohesively to provide comprehensive support'
                if metrics.get('avg_agent_coordination', 0) > 0.7
                else 'Agent coordination needs improvement',
                'thesis_implication': 'Multi-agent approach shows promise for educational AI'
            },
            'learning_progression': {
                'sessions_with_progression': metrics.get('sessions_with_progression', 0),
                'progression_rate': (metrics.get('sessions_with_progression', 0) / 
                                   max(metrics.get('total_sessions', 1), 1)),
                'thesis_implication': 'System supports skill development over time'
            },
            'overall_assessment': self._generate_overall_thesis_assessment()
        }
    
    def _assess_overall_effectiveness(self) -> str:
        """Assess overall system effectiveness"""
        
        metrics = self.results.get('evaluation_metrics', {})
        
        key_metrics = [
            metrics.get('avg_cognitive_offloading_prevention', 0),
            metrics.get('avg_deep_thinking_engagement', 0),
            metrics.get('avg_scaffolding_effectiveness', 0),
            metrics.get('avg_knowledge_integration', 0)
        ]
        
        avg_effectiveness = np.mean(key_metrics) if key_metrics else 0
        
        if avg_effectiveness >= 0.8:
            return "Highly Effective - System exceeds benchmarks"
        elif avg_effectiveness >= 0.6:
            return "Effective - System meets core objectives"
        elif avg_effectiveness >= 0.4:
            return "Moderately Effective - Room for improvement"
        else:
            return "Needs Improvement - Significant enhancements required"
    
    def _identify_primary_strengths(self) -> List[str]:
        """Identify primary system strengths"""
        
        strengths = []
        metrics = self.results.get('evaluation_metrics', {})
        
        if metrics.get('avg_cognitive_offloading_prevention', 0) > 0.8:
            strengths.append("Excellent at preventing cognitive offloading")
        
        if metrics.get('avg_improvement_over_baseline', 0) > 50:
            strengths.append(f"{metrics['avg_improvement_over_baseline']:.0f}% improvement over traditional methods")
        
        if metrics.get('avg_deep_thinking_engagement', 0) > 0.7:
            strengths.append("Strong deep thinking engagement")
        
        return strengths
    
    def _identify_improvement_areas(self) -> List[str]:
        """Identify areas needing improvement"""
        
        areas = []
        metrics = self.results.get('evaluation_metrics', {})
        
        if metrics.get('avg_scaffolding_effectiveness', 0) < 0.6:
            areas.append("Scaffolding effectiveness needs enhancement")
        
        if metrics.get('avg_knowledge_integration', 0) < 0.5:
            areas.append("Knowledge integration could be improved")
        
        if metrics.get('sessions_with_progression', 0) / max(metrics.get('total_sessions', 1), 1) < 0.5:
            areas.append("Skill progression tracking needs refinement")
        
        return areas
    
    def _generate_proficiency_insights(self, percentages: Dict[str, float]) -> List[str]:
        """Generate insights from proficiency distribution"""
        
        insights = []
        
        if percentages.get('beginner', 0) > 40:
            insights.append("High percentage of beginners indicates need for better onboarding")
        
        if percentages.get('expert', 0) < 5:
            insights.append("Low expert percentage suggests limited progression pathways")
        
        if percentages.get('intermediate', 0) > 50:
            insights.append("Majority at intermediate level shows effective skill building")
        
        return insights
    
    def _interpret_offloading_prevention(self, rate: float) -> str:
        """Interpret cognitive offloading prevention rate"""
        
        if rate >= 0.8:
            return "Exceptional - Users consistently engage in independent thinking"
        elif rate >= 0.6:
            return "Good - Most interactions encourage self-directed learning"
        elif rate >= 0.4:
            return "Moderate - Some tendency toward answer-seeking behavior"
        else:
            return "Poor - High cognitive dependency observed"
    
    def _generate_overall_thesis_assessment(self) -> str:
        """Generate overall assessment for thesis"""
        
        metrics = self.results.get('evaluation_metrics', {})
        improvement = metrics.get('avg_improvement_over_baseline', 0)
        
        if improvement > 60 and metrics.get('avg_cognitive_offloading_prevention', 0) > 0.7:
            return ("The Mega Architectural Mentor demonstrates significant potential "
                   "as an AI-powered educational tool that enhances rather than replaces "
                   "human cognitive capabilities in spatial design education.")
        elif improvement > 40:
            return ("The system shows promise in preventing cognitive offloading while "
                   "supporting learning, though further refinements could enhance effectiveness.")
        else:
            return ("Initial results indicate the multi-agent approach has merit, "
                   "but substantial improvements are needed to achieve thesis objectives.")
    
    def _write_markdown_summary(self, report: Dict[str, Any], path: Path):
        """Write human-readable markdown summary"""
        
        with open(path, 'w') as f:
            f.write("# Mega Architectural Mentor - Benchmarking Report\n\n")
            f.write(f"Generated: {report['metadata']['generated_at']}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            summary = report['executive_summary']
            for finding in summary['key_findings']:
                f.write(f"- {finding}\n")
            f.write(f"\n**Overall Effectiveness:** {summary['system_effectiveness']}\n\n")
            
            # Strengths
            f.write("### Primary Strengths\n\n")
            for strength in summary['primary_strengths']:
                f.write(f"- {strength}\n")
            f.write("\n")
            
            # Improvements
            f.write("### Areas for Improvement\n\n")
            for area in summary['areas_for_improvement']:
                f.write(f"- {area}\n")
            f.write("\n")
            
            # Recommendations
            f.write("## System Recommendations\n\n")
            for rec in report['recommendations']:
                f.write(f"### {rec['area']}\n")
                f.write(f"- **Recommendation:** {rec['recommendation']}\n")
                f.write(f"- **Priority:** {rec['priority']}\n")
                f.write(f"- **Implementation:** {rec['implementation']}\n\n")
            
            # Thesis Insights
            f.write("## Thesis Research Insights\n\n")
            insights = report['thesis_insights']
            f.write(f"### Cognitive Offloading Prevention\n")
            f.write(f"- Effectiveness: {insights['cognitive_offloading_prevention']['effectiveness']:.1%}\n")
            f.write(f"- {insights['cognitive_offloading_prevention']['interpretation']}\n")
            f.write(f"- **Implication:** {insights['cognitive_offloading_prevention']['thesis_implication']}\n\n")
            
            f.write(f"### Overall Assessment\n\n")
            f.write(f"{insights['overall_assessment']}\n")
    
    def _print_summary(self):
        """Print summary of benchmarking results"""
        
        print("\nBENCHMARKING SUMMARY")
        print("-" * 40)
        print(f"Sessions Analyzed: {self.results['sessions_analyzed']}")
        
        metrics = self.results.get('evaluation_metrics', {})
        if metrics:
            print(f"\nKey Metrics:")
            print(f"  - Cognitive Offloading Prevention: {metrics.get('avg_cognitive_offloading_prevention', 0):.1%}")
            print(f"  - Deep Thinking Engagement: {metrics.get('avg_deep_thinking_engagement', 0):.1%}")
            print(f"  - Improvement over Baseline: {metrics.get('avg_improvement_over_baseline', 0):.1f}%")
        
        print(f"\nResults saved to: {self.output_dir}")
        print(f"  - Benchmark Report: benchmark_report.json")
        print(f"  - Evaluation Reports: evaluation_reports/")
        print(f"  - Visualizations: visualizations/")
        print(f"  - Summary: benchmark_summary.md")
        print(f"\nNOTE: All dashboard visualizations have been exported to:")
        print(f"  - {self.output_dir}/visualizations/index.html")


def main():
    """Main entry point for benchmarking system"""
    
    parser = argparse.ArgumentParser(
        description="Run cognitive benchmarking for Mega Architectural Mentor"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./thesis_data",
        help="Directory containing interaction data (default: ./thesis_data)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./benchmarking/results",
        help="Directory for output files (default: ./benchmarking/results)"
    )
    
    parser.add_argument(
        "--no-classifier",
        action="store_true",
        help="Skip training the proficiency classifier"
    )
    
    parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Skip generating visualizations"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip generating the final report"
    )
    
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Skip launching the Streamlit dashboard after benchmarking"
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = BenchmarkingPipeline(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    # Generate master metrics first
    print("\n" + "="*60)
    print("Generating Master Metrics...")
    print("="*60)
    try:
        from generate_master_metrics import MasterMetricsGenerator
        generator = MasterMetricsGenerator(thesis_data_path=args.data_dir, output_path="results")
        generator.generate_master_metrics()
    except Exception as e:
        print(f"Warning: Could not generate master metrics: {e}")
    
    # Run benchmarking
    pipeline.run_full_pipeline(
        train_classifier=not args.no_classifier,
        generate_visualizations=not args.no_visualizations,
        export_report=not args.no_report
    )
    
    # Launch dashboard if requested
    if not args.no_dashboard:
        print("\n" + "="*60)
        print("Launching Benchmarking Dashboard...")
        print("="*60)
        import subprocess
        import sys
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", 
                         "benchmarking/benchmark_dashboard.py"])


if __name__ == "__main__":
    main()