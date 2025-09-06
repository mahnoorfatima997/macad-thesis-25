"""
MEGA Personality Data Processor
Processes interaction data for personality analysis integration
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import json
import re
from datetime import datetime

from personality_models import PersonalityProfile, save_personality_profile
from personality_analyzer import PersonalityAnalyzer, create_analyzer_with_fallback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalityProcessor:
    """
    Processes existing interaction data for personality analysis
    Integrates with the current benchmarking pipeline
    """
    
    def __init__(self, analyzer: Optional[PersonalityAnalyzer] = None):
        """
        Initialize personality processor
        
        Args:
            analyzer: PersonalityAnalyzer instance (creates one if None)
        """
        self.analyzer = analyzer or create_analyzer_with_fallback()
        self.data_dir = Path("thesis_data")
        self.results_dir = Path("benchmarking/results/personality_reports")
        
        # Create results directory if it doesn't exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def find_session_files(self) -> Dict[str, Dict[str, Path]]:
        """
        Find all available session data files
        
        Returns:
            Dictionary mapping session IDs to file paths
        """
        session_files = {}
        
        if not self.data_dir.exists():
            logger.warning(f"Data directory not found: {self.data_dir}")
            return session_files
        
        # Look for interaction files
        interaction_patterns = [
            "interactions_unified_session_*.csv",
            "interactions_session_*.csv", 
            "interactions_*.csv"
        ]
        
        for pattern in interaction_patterns:
            for file_path in self.data_dir.glob(pattern):
                # Extract session ID from filename
                session_id = self._extract_session_id(file_path.name)
                
                if session_id not in session_files:
                    session_files[session_id] = {}
                
                session_files[session_id]['interactions'] = file_path
        
        # Look for additional data files
        additional_patterns = [
            ("design_moves_unified_session_*.csv", "design_moves"),
            ("session_summary_unified_session_*.json", "session_summary"),
            ("full_log_unified_session_*.json", "full_log")
        ]
        
        for pattern, file_type in additional_patterns:
            for file_path in self.data_dir.glob(pattern):
                session_id = self._extract_session_id(file_path.name)
                
                if session_id in session_files:
                    session_files[session_id][file_type] = file_path
        
        logger.info(f"Found {len(session_files)} sessions with data files")
        return session_files
    
    def _extract_session_id(self, filename: str) -> str:
        """Extract session ID from filename"""
        # Remove common prefixes and suffixes
        session_id = filename
        
        # Remove file extension
        session_id = session_id.replace('.csv', '').replace('.json', '')
        
        # Remove common prefixes
        prefixes_to_remove = [
            'interactions_unified_session_',
            'design_moves_unified_session_',
            'session_summary_unified_session_',
            'full_log_unified_session_',
            'interactions_session_',
            'interactions_'
        ]
        
        for prefix in prefixes_to_remove:
            if session_id.startswith(prefix):
                session_id = session_id[len(prefix):]
                break
        
        return session_id
    
    def extract_user_text_from_interactions(self, interactions_df: pd.DataFrame) -> str:
        """
        Extract user text from interactions DataFrame
        
        Args:
            interactions_df: DataFrame with interaction data
            
        Returns:
            Combined user text string
        """
        user_texts = []
        
        # Common column names that might contain user input
        possible_columns = [
            'user_input', 'input', 'question', 'user_question', 
            'text', 'content', 'message', 'query', 'prompt'
        ]
        
        # Try each possible column
        for col in possible_columns:
            if col in interactions_df.columns:
                texts = interactions_df[col].dropna()
                user_texts.extend(texts.astype(str).tolist())
                logger.debug(f"Extracted {len(texts)} entries from column '{col}'")
                break
        
        # If no standard column found, look for text-like columns
        if not user_texts:
            for col in interactions_df.columns:
                if interactions_df[col].dtype == 'object':
                    # Sample some values to check if they look like user input
                    sample_values = interactions_df[col].dropna().head(5)
                    
                    if self._looks_like_user_text(sample_values):
                        texts = interactions_df[col].dropna()
                        user_texts.extend(texts.astype(str).tolist())
                        logger.info(f"Using column '{col}' as user text source")
                        break
        
        # Clean and combine text
        cleaned_texts = []
        for text in user_texts:
            # Skip system messages and short texts
            if (not text.startswith(('System:', 'Agent:', 'Response:', 'Error:', 'DEBUG:')) 
                and len(text.strip()) > 10):
                cleaned_texts.append(text.strip())
        
        combined_text = " ".join(cleaned_texts)
        
        # Normalize whitespace
        combined_text = re.sub(r'\s+', ' ', combined_text).strip()
        
        logger.debug(f"Extracted {len(combined_text)} characters of user text")
        return combined_text
    
    def _looks_like_user_text(self, sample_values: pd.Series) -> bool:
        """Check if sample values look like user input text"""
        if sample_values.empty:
            return False
        
        # Convert to strings and check characteristics
        texts = sample_values.astype(str).tolist()
        
        # Heuristics for user text detection
        user_indicators = 0
        total_checks = 0
        
        for text in texts[:3]:  # Check first 3 samples
            if len(text) < 5:
                continue
                
            total_checks += 1
            
            # Check for question marks (users ask questions)
            if '?' in text:
                user_indicators += 1
            
            # Check for personal pronouns (users refer to themselves)
            if re.search(r'\b(I|me|my|myself)\b', text, re.IGNORECASE):
                user_indicators += 1
            
            # Check for conversational language
            conversational_words = ['help', 'how', 'what', 'why', 'can', 'could', 'would', 'please']
            if any(word in text.lower() for word in conversational_words):
                user_indicators += 1
            
            # Avoid system-like text
            system_indicators = ['status:', 'error:', 'debug:', 'response:', 'system:']
            if any(indicator in text.lower() for indicator in system_indicators):
                user_indicators -= 1
        
        return total_checks > 0 and (user_indicators / total_checks) > 0.3
    
    def extract_user_text_from_full_log(self, full_log_path: Path) -> str:
        """
        Extract user text from full log JSON file
        
        Args:
            full_log_path: Path to full log JSON file
            
        Returns:
            Combined user text string
        """
        try:
            with open(full_log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            user_texts = []
            
            # Different structures for log data
            if isinstance(log_data, list):
                # List of interactions
                for entry in log_data:
                    if isinstance(entry, dict):
                        # Look for user input keys
                        for key in ['user_input', 'input', 'question', 'message']:
                            if key in entry and entry[key]:
                                user_texts.append(str(entry[key]))
                                break
            
            elif isinstance(log_data, dict):
                # Single session object
                # Look for conversations or interactions
                for key in ['conversations', 'interactions', 'messages']:
                    if key in log_data:
                        items = log_data[key]
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict):
                                    for user_key in ['user_input', 'input', 'question']:
                                        if user_key in item and item[user_key]:
                                            user_texts.append(str(item[user_key]))
                                            break
            
            combined_text = " ".join(user_texts)
            combined_text = re.sub(r'\s+', ' ', combined_text).strip()
            
            logger.debug(f"Extracted {len(combined_text)} characters from full log")
            return combined_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from full log {full_log_path}: {e}")
            return ""
    
    def process_single_session(self, session_id: str, 
                             session_files: Dict[str, Path]) -> Optional[PersonalityProfile]:
        """
        Process a single session for personality analysis
        
        Args:
            session_id: Session identifier
            session_files: Dictionary of file paths for this session
            
        Returns:
            PersonalityProfile or None if processing fails
        """
        logger.info(f"Processing session {session_id}")
        
        user_text = ""
        
        # Try to extract text from interactions file
        if 'interactions' in session_files:
            try:
                df = pd.read_csv(session_files['interactions'])
                user_text = self.extract_user_text_from_interactions(df)
            except Exception as e:
                logger.error(f"Failed to read interactions file for session {session_id}: {e}")
        
        # If interactions didn't yield enough text, try full log
        if len(user_text) < 200 and 'full_log' in session_files:
            additional_text = self.extract_user_text_from_full_log(session_files['full_log'])
            user_text = (user_text + " " + additional_text).strip()
        
        # Check if we have enough text for analysis
        if len(user_text) < 100:
            logger.warning(f"Insufficient text for session {session_id} ({len(user_text)} characters)")
            return None
        
        # Perform personality analysis
        try:
            profile = self.analyzer.analyze_text(user_text)
            profile.session_id = session_id
            
            # Add session metadata if available
            self._add_session_metadata(profile, session_files)
            
            logger.info(f"Session {session_id} analysis: {profile.dominant_traits[:2]}")
            return profile
            
        except Exception as e:
            logger.error(f"Personality analysis failed for session {session_id}: {e}")
            return None
    
    def _add_session_metadata(self, profile: PersonalityProfile, 
                            session_files: Dict[str, Path]):
        """Add additional metadata from session files"""
        # Try to get session summary info
        if 'session_summary' in session_files:
            try:
                with open(session_files['session_summary'], 'r') as f:
                    summary_data = json.load(f)
                
                # Extract relevant metadata
                if isinstance(summary_data, dict):
                    # Could add session duration, interaction count, etc.
                    pass
                    
            except Exception as e:
                logger.debug(f"Could not read session summary: {e}")
    
    def process_all_sessions(self) -> List[PersonalityProfile]:
        """
        Process all available sessions for personality analysis
        
        Returns:
            List of PersonalityProfiles
        """
        logger.info("Starting batch processing of all sessions")
        
        session_files = self.find_session_files()
        profiles = []
        
        for session_id, files in session_files.items():
            profile = self.process_single_session(session_id, files)
            if profile:
                profiles.append(profile)
                
                # Save individual profile
                self.save_personality_profile(profile)
        
        # Save batch summary
        if profiles:
            self.save_batch_summary(profiles)
        
        logger.info(f"Completed processing {len(profiles)} sessions")
        return profiles
    
    def save_personality_profile(self, profile: PersonalityProfile) -> bool:
        """Save individual personality profile"""
        filename = f"session_{profile.session_id}_personality.json"
        filepath = self.results_dir / filename
        
        return save_personality_profile(profile, filepath)
    
    def save_batch_summary(self, profiles: List[PersonalityProfile]) -> bool:
        """Save summary of all personality profiles"""
        try:
            summary_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_sessions': len(profiles),
                'analyzer_info': self.analyzer.get_model_info(),
                'sessions': []
            }
            
            # Add session summaries
            for profile in profiles:
                session_summary = {
                    'session_id': profile.session_id,
                    'traits': profile.traits,
                    'levels': profile.levels,
                    'dominant_traits': profile.dominant_traits,
                    'reliability_score': profile.reliability_score,
                    'personality_summary': profile.personality_summary
                }
                summary_data['sessions'].append(session_summary)
            
            # Calculate aggregate statistics
            if profiles:
                trait_means = {}
                trait_stds = {}
                
                for trait in profiles[0].traits.keys():
                    trait_scores = [p.traits[trait] for p in profiles if trait in p.traits]
                    if trait_scores:
                        trait_means[trait] = np.mean(trait_scores)
                        trait_stds[trait] = np.std(trait_scores)
                
                summary_data['aggregate_stats'] = {
                    'trait_means': trait_means,
                    'trait_stds': trait_stds
                }
            
            # Convert numpy types before saving
            def convert_numpy_types(obj):
                if hasattr(obj, 'item'):
                    return obj.item()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(v) for v in obj]
                else:
                    return obj
            
            summary_data_clean = convert_numpy_types(summary_data)
            
            # Save summary
            summary_path = self.results_dir / "personality_summary_all_sessions.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data_clean, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved personality batch summary to {summary_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save batch summary: {e}")
            return False
    
    def correlate_with_cognitive_metrics(self, profiles: List[PersonalityProfile]) -> Dict[str, Any]:
        """
        Correlate personality traits with existing cognitive metrics
        
        Args:
            profiles: List of personality profiles
            
        Returns:
            Dictionary with correlation analysis
        """
        logger.info("Analyzing personality-cognitive correlations")
        
        correlations = {
            'timestamp': datetime.now().isoformat(),
            'correlations': {},
            'insights': []
        }
        
        # This would integrate with existing cognitive metric data
        # For now, return placeholder structure
        
        # Load evaluation reports if available
        eval_reports_dir = Path("benchmarking/results/evaluation_reports")
        
        if eval_reports_dir.exists():
            # Would correlate personality traits with cognitive metrics
            # from evaluation reports
            pass
        
        # Save correlation results
        corr_path = self.results_dir / "personality_cognitive_correlations.json"
        try:
            with open(corr_path, 'w', encoding='utf-8') as f:
                json.dump(correlations, f, indent=2)
            logger.info(f"Saved correlation analysis to {corr_path}")
        except Exception as e:
            logger.error(f"Failed to save correlations: {e}")
        
        return correlations
    
    def validate_data_quality(self, profiles: List[PersonalityProfile]) -> Dict[str, Any]:
        """Validate quality of personality analysis results"""
        validation = {
            'timestamp': datetime.now().isoformat(),
            'total_profiles': len(profiles),
            'quality_metrics': {},
            'recommendations': []
        }
        
        if not profiles:
            validation['recommendations'].append("No profiles to validate")
            return validation
        
        # Calculate quality metrics
        reliability_scores = [p.reliability_score for p in profiles]
        text_lengths = [p.text_length for p in profiles]
        
        validation['quality_metrics'] = {
            'mean_reliability': np.mean(reliability_scores),
            'min_reliability': np.min(reliability_scores),
            'mean_text_length': np.mean(text_lengths),
            'min_text_length': np.min(text_lengths),
            'profiles_low_reliability': sum(1 for score in reliability_scores if score < 0.6),
            'profiles_short_text': sum(1 for length in text_lengths if length < 500)
        }
        
        # Generate recommendations
        if validation['quality_metrics']['mean_reliability'] < 0.7:
            validation['recommendations'].append("Consider improving text extraction methods")
        
        if validation['quality_metrics']['profiles_short_text'] > len(profiles) * 0.3:
            validation['recommendations'].append("Many sessions have insufficient text length")
        
        return validation

def run_personality_analysis() -> List[PersonalityProfile]:
    """
    Main function to run personality analysis on all sessions
    Can be called from the benchmarking pipeline
    """
    processor = PersonalityProcessor()
    profiles = processor.process_all_sessions()
    
    if profiles:
        # Validate results
        validation = processor.validate_data_quality(profiles)
        logger.info(f"Data quality validation: {validation['quality_metrics']}")
        
        # Correlate with cognitive metrics
        correlations = processor.correlate_with_cognitive_metrics(profiles)
    
    return profiles

# Export main classes and functions
__all__ = [
    'PersonalityProcessor',
    'run_personality_analysis'
]