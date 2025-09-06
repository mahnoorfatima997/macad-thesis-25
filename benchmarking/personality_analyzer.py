"""
MEGA Personality Analysis Engine
Core personality trait extraction using HEXACO model and BERT
"""

import logging
import warnings
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import re
import time
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Import personality models
from personality_models import (
    PersonalityProfile, 
    HEXACOModel, 
    PERSONALITY_CONFIG,
    save_personality_profile
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalityAnalyzer:
    """
    Core personality analysis engine using HEXACO model
    
    Uses BERT-based transformer models to extract personality traits
    from user text interactions with scientific validation.
    """
    
    def __init__(self, model_name: str = "Minej/bert-base-personality", 
                 use_fallback: bool = True):
        """
        Initialize personality analyzer
        
        Args:
            model_name: Hugging Face model identifier
            use_fallback: Whether to use fallback analysis if model fails
        """
        self.model_name = model_name
        self.use_fallback = use_fallback
        self.model = None
        self.tokenizer = None
        self.is_available = False
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the BERT personality model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            logger.info(f"Loading personality model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Set to evaluation mode
            self.model.eval()
            
            self.is_available = True
            logger.info("Personality model loaded successfully")
            
        except ImportError:
            logger.warning("Transformers not available. Install with: pip install transformers torch")
            self.is_available = False
            
        except Exception as e:
            logger.error(f"Failed to load personality model: {e}")
            self.is_available = False
    
    def validate_text_input(self, text: str) -> Tuple[bool, Dict[str, Union[str, int]]]:
        """
        Validate text input for personality analysis
        
        Args:
            text: Input text to validate
            
        Returns:
            (is_valid, validation_info)
        """
        validation_info = {
            'length': len(text),
            'word_count': len(text.split()),
            'meets_minimum': False,
            'quality_score': 0.0,
            'issues': []
        }
        
        # Check minimum length
        if len(text) < PERSONALITY_CONFIG['min_text_length']:
            validation_info['issues'].append(f"Text too short. Minimum {PERSONALITY_CONFIG['min_text_length']} characters required.")
            return False, validation_info
        
        validation_info['meets_minimum'] = True
        
        # Quality assessment
        quality_score = 0.0
        
        # Length bonus (up to 0.3)
        length_score = min(len(text) / 2000, 0.3)
        quality_score += length_score
        
        # Word diversity (up to 0.3)
        words = text.lower().split()
        unique_words = set(words)
        diversity_score = min(len(unique_words) / len(words), 0.3) if words else 0
        quality_score += diversity_score
        
        # Sentence structure (up to 0.2)
        sentences = re.split(r'[.!?]+', text)
        sentence_score = min(len(sentences) / 20, 0.2)
        quality_score += sentence_score
        
        # Question presence (up to 0.2)
        question_count = len(re.findall(r'\?', text))
        question_score = min(question_count / 5, 0.2)
        quality_score += question_score
        
        validation_info['quality_score'] = quality_score
        
        # Additional quality checks
        if len(unique_words) < 50:
            validation_info['issues'].append("Low vocabulary diversity")
        
        if len(sentences) < 5:
            validation_info['issues'].append("Few sentences for comprehensive analysis")
        
        return True, validation_info
    
    def analyze_text_bert(self, text: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Analyze text using BERT model for personality traits
        
        Args:
            text: Input text to analyze
            
        Returns:
            (trait_scores, confidence_scores)
        """
        if not self.is_available:
            raise ValueError("BERT model not available")
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(text, truncation=True, padding=True, 
                                  max_length=512, return_tensors='pt')
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Convert to personality scores
            # Note: This is a simplified mapping - real implementation would
            # depend on the specific model's output format
            scores = predictions.cpu().numpy()[0]
            
            # Map to HEXACO traits 
            # Note: This BERT model is Big Five based (5 traits), not HEXACO (6 traits)
            logger.debug(f"BERT model output shape: {scores.shape}, scores: {scores}")
            
            if len(scores) == 5:
                # Big Five model - map to HEXACO with honesty_humility estimated
                trait_mapping = {
                    'openness': scores[0],
                    'conscientiousness': scores[1], 
                    'extraversion': scores[2],
                    'agreeableness': scores[3],
                    'emotionality': scores[4],  # Neuroticism in Big Five
                    'honesty_humility': self._estimate_honesty_humility(text, scores[3])  # Estimate from agreeableness
                }
            else:
                # Fallback mapping for unexpected output sizes
                trait_mapping = {
                    'openness': scores[0] if len(scores) > 0 else 0.5,
                    'conscientiousness': scores[1] if len(scores) > 1 else 0.5,
                    'extraversion': scores[2] if len(scores) > 2 else 0.5,
                    'agreeableness': scores[3] if len(scores) > 3 else 0.5,
                    'emotionality': scores[4] if len(scores) > 4 else 0.5,
                    'honesty_humility': scores[5] if len(scores) > 5 else 0.5
                }
            
            # Generate confidence scores based on prediction certainty
            confidence = {}
            for trait, score in trait_mapping.items():
                # Higher confidence for scores closer to extremes
                confidence[trait] = abs(score - 0.5) * 2
            
            return trait_mapping, confidence
            
        except Exception as e:
            logger.error(f"BERT analysis failed: {e}")
            raise
    
    def _estimate_honesty_humility(self, text: str, agreeableness_score: float) -> float:
        """
        Estimate Honesty-Humility from text analysis and agreeableness score
        
        Since Big Five models don't include Honesty-Humility, we estimate it
        using linguistic markers and correlation with agreeableness.
        """
        # Honesty-Humility linguistic markers
        honesty_markers = [
            'honest', 'sincere', 'genuine', 'fair', 'modest', 'humble', 
            'authentic', 'truthful', 'integrity', 'moral', 'ethical',
            'deserves', 'earn', 'merit', 'humble', 'simple', 'unpretentious'
        ]
        
        dishonesty_markers = [
            'deserve', 'entitled', 'special', 'superior', 'better than',
            'manipulate', 'exploit', 'cheat', 'advantage', 'unfair',
            'greedy', 'selfish', 'arrogant', 'boastful', 'pretentious'
        ]
        
        # Count markers in text
        text_lower = text.lower()
        honesty_count = sum(1 for marker in honesty_markers if marker in text_lower)
        dishonesty_count = sum(1 for marker in dishonesty_markers if marker in text_lower)
        
        # Base score influenced by agreeableness (they're correlated)
        base_score = 0.3 + (agreeableness_score * 0.4)  # Scale from agreeableness
        
        # Adjust based on text markers
        if honesty_count > dishonesty_count:
            adjustment = min((honesty_count - dishonesty_count) * 0.05, 0.2)
        else:
            adjustment = max((honesty_count - dishonesty_count) * 0.05, -0.2)
        
        # Ensure within valid range
        estimated_score = max(0.1, min(0.9, base_score + adjustment))
        
        logger.debug(f"Honesty-Humility estimation: base={base_score:.3f}, "
                    f"honesty_markers={honesty_count}, dishonesty_markers={dishonesty_count}, "
                    f"final={estimated_score:.3f}")
        
        return estimated_score
    
    def analyze_text_fallback(self, text: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Fallback personality analysis using linguistic patterns
        
        This provides basic personality analysis when BERT models are unavailable.
        Based on established linguistic markers for personality traits.
        """
        logger.info("Using fallback personality analysis")
        
        text_lower = text.lower()
        words = text_lower.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Initialize scores
        traits = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'emotionality': 0.5,
            'honesty_humility': 0.5
        }
        
        # Linguistic markers for each trait
        openness_markers = ['creative', 'imaginative', 'art', 'novel', 'idea', 'abstract', 
                           'concept', 'theory', 'philosophy', 'aesthetic', 'beauty']
        
        conscientiousness_markers = ['organize', 'plan', 'detail', 'careful', 'precise', 
                                   'systematic', 'thorough', 'complete', 'structure', 'method']
        
        extraversion_markers = ['social', 'people', 'group', 'team', 'share', 'discuss', 
                               'collaborate', 'meeting', 'present', 'communicate']
        
        agreeableness_markers = ['help', 'support', 'kind', 'friendly', 'cooperative', 
                                'understand', 'empathy', 'care', 'gentle', 'patient']
        
        emotionality_markers = ['feel', 'emotion', 'worry', 'stress', 'anxiety', 'concern',
                               'sensitive', 'mood', 'upset', 'nervous', 'afraid']
        
        honesty_markers = ['honest', 'fair', 'truth', 'genuine', 'sincere', 'modest', 
                          'humble', 'simple', 'straightforward', 'direct']
        
        marker_sets = {
            'openness': openness_markers,
            'conscientiousness': conscientiousness_markers,
            'extraversion': extraversion_markers,
            'agreeableness': agreeableness_markers,
            'emotionality': emotionality_markers,
            'honesty_humility': honesty_markers
        }
        
        # Count linguistic markers
        for trait, markers in marker_sets.items():
            count = sum(1 for word in words if any(marker in word for marker in markers))
            # Normalize by text length and apply sigmoid transformation
            normalized_count = count / len(words) * 100 if words else 0
            traits[trait] = min(max(0.3 + normalized_count * 0.4, 0.0), 1.0)
        
        # Additional patterns
        # Question usage (curiosity/openness)
        question_count = len(re.findall(r'\?', text))
        if question_count > 3:
            traits['openness'] = min(traits['openness'] + 0.1, 1.0)
        
        # Sentence length (detail orientation/conscientiousness)
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        if avg_sentence_length > 15:
            traits['conscientiousness'] = min(traits['conscientiousness'] + 0.1, 1.0)
        
        # Exclamation marks (emotional expression)
        exclamation_count = len(re.findall(r'!', text))
        if exclamation_count > 2:
            traits['emotionality'] = min(traits['emotionality'] + 0.1, 1.0)
            traits['extraversion'] = min(traits['extraversion'] + 0.05, 1.0)
        
        # Generate confidence scores (lower for fallback method)
        confidence = {trait: 0.6 for trait in traits.keys()}
        
        return traits, confidence
    
    def analyze_text(self, text: str) -> PersonalityProfile:
        """
        Main text analysis function
        
        Args:
            text: Input text to analyze
            
        Returns:
            PersonalityProfile with analysis results
        """
        start_time = time.time()
        
        # Validate input
        is_valid, validation_info = self.validate_text_input(text)
        if not is_valid:
            logger.warning(f"Text validation failed: {validation_info['issues']}")
        
        # Initialize profile
        profile = PersonalityProfile(
            session_id="",  # Will be set by caller
            text_analyzed=text[:1000] + "..." if len(text) > 1000 else text,
            text_length=len(text),
            analysis_method="HEXACO-BERT" if self.is_available else "HEXACO-Fallback"
        )
        
        try:
            # Attempt BERT analysis
            if self.is_available:
                traits, confidence = self.analyze_text_bert(text)
            elif self.use_fallback:
                traits, confidence = self.analyze_text_fallback(text)
            else:
                raise ValueError("No analysis method available")
            
            # Populate profile
            profile.traits = traits
            profile.confidence = confidence
            
            # Convert scores to categorical levels
            profile.levels = {
                trait: HEXACOModel.score_to_level(score) 
                for trait, score in traits.items()
            }
            
            # Calculate overall reliability
            profile.reliability_score = HEXACOModel.calculate_reliability_score(confidence)
            
            # Identify dominant traits
            profile.dominant_traits = HEXACOModel.identify_dominant_traits(traits)
            
            # Generate personality summary
            profile.personality_summary = HEXACOModel.generate_personality_summary(profile)
            
            analysis_time = time.time() - start_time
            logger.info(f"Personality analysis completed in {analysis_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Personality analysis failed: {e}")
            # Return minimal profile with error info
            profile.personality_summary = f"Analysis failed: {str(e)}"
        
        return profile
    
    def analyze_session_data(self, interactions_df: pd.DataFrame, 
                           session_id: str) -> PersonalityProfile:
        """
        Analyze personality from session interaction data
        
        Args:
            interactions_df: DataFrame with interaction data
            session_id: Session identifier
            
        Returns:
            PersonalityProfile for the session
        """
        # Extract user text from interactions
        user_text = self._extract_user_text(interactions_df)
        
        # Perform analysis
        profile = self.analyze_text(user_text)
        profile.session_id = session_id
        
        return profile
    
    def _extract_user_text(self, interactions_df: pd.DataFrame) -> str:
        """Extract and concatenate user text from interaction DataFrame"""
        user_texts = []
        
        # Common column names for user input
        text_columns = ['user_input', 'input', 'question', 'text', 'content']
        
        for col in text_columns:
            if col in interactions_df.columns:
                user_texts.extend(interactions_df[col].dropna().astype(str).tolist())
                break
        
        if not user_texts:
            # Try to extract from any string column
            for col in interactions_df.columns:
                if interactions_df[col].dtype == 'object':
                    texts = interactions_df[col].dropna().astype(str)
                    # Filter for likely user input (not system messages)
                    user_like_texts = [
                        t for t in texts 
                        if not t.startswith(('System:', 'Agent:', 'Response:', 'Error:'))
                        and len(t) > 10
                    ]
                    user_texts.extend(user_like_texts)
                    break
        
        # Combine all user text
        combined_text = " ".join(user_texts)
        
        # Clean and normalize
        combined_text = re.sub(r'\s+', ' ', combined_text).strip()
        
        return combined_text
    
    def batch_analyze_sessions(self, session_files: List[Path]) -> List[PersonalityProfile]:
        """
        Analyze multiple sessions in batch
        
        Args:
            session_files: List of CSV file paths containing interaction data
            
        Returns:
            List of PersonalityProfiles
        """
        profiles = []
        
        logger.info(f"Starting batch analysis of {len(session_files)} sessions")
        
        for file_path in session_files:
            try:
                # Extract session ID from filename
                session_id = file_path.stem.replace('interactions_unified_session_', '').replace('interactions_', '')
                
                # Load interaction data
                df = pd.read_csv(file_path)
                
                # Analyze session
                profile = self.analyze_session_data(df, session_id)
                profiles.append(profile)
                
                logger.info(f"Analyzed session {session_id}: {profile.dominant_traits}")
                
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
                continue
        
        logger.info(f"Batch analysis completed. {len(profiles)} profiles generated.")
        return profiles
    
    def get_model_info(self) -> Dict[str, Union[str, bool]]:
        """Get information about the current analysis model"""
        return {
            'model_name': self.model_name,
            'is_available': self.is_available,
            'use_fallback': self.use_fallback,
            'min_text_length': PERSONALITY_CONFIG['min_text_length'],
            'analysis_version': PERSONALITY_CONFIG['analysis_version']
        }

# Utility functions for integration
def analyze_session_file(file_path: Union[str, Path], 
                        analyzer: Optional[PersonalityAnalyzer] = None) -> Optional[PersonalityProfile]:
    """Convenience function to analyze a single session file"""
    if analyzer is None:
        analyzer = PersonalityAnalyzer()
    
    try:
        file_path = Path(file_path)
        session_id = file_path.stem.replace('interactions_unified_session_', '').replace('interactions_', '')
        
        df = pd.read_csv(file_path)
        profile = analyzer.analyze_session_data(df, session_id)
        
        return profile
    except Exception as e:
        logger.error(f"Failed to analyze session file {file_path}: {e}")
        return None

def create_analyzer_with_fallback() -> PersonalityAnalyzer:
    """Create analyzer with intelligent fallback handling"""
    try:
        # Try primary model
        analyzer = PersonalityAnalyzer(model_name="Minej/bert-base-personality")
        if analyzer.is_available:
            return analyzer
    except Exception:
        pass
    
    try:
        # Try alternative model
        analyzer = PersonalityAnalyzer(model_name="Nasserelsaman/microsoft-finetuned-personality")
        if analyzer.is_available:
            return analyzer
    except Exception:
        pass
    
    # Fallback to linguistic analysis only
    logger.warning("No BERT models available. Using fallback analysis only.")
    return PersonalityAnalyzer(use_fallback=True)

# Export main classes
__all__ = [
    'PersonalityAnalyzer',
    'analyze_session_file', 
    'create_analyzer_with_fallback'
]