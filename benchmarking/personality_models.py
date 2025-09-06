"""
MEGA Personality Analysis Models
HEXACO personality model implementation for thesis research
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonalityProfile:
    """Comprehensive personality analysis results"""
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # HEXACO trait scores (0.0-1.0)
    traits: Dict[str, float] = field(default_factory=dict)
    
    # Categorical levels (Low/Medium/High)
    levels: Dict[str, str] = field(default_factory=dict)
    
    # Confidence scores for each trait
    confidence: Dict[str, float] = field(default_factory=dict)
    
    # Analysis metadata
    text_analyzed: str = ""
    text_length: int = 0
    analysis_method: str = "HEXACO-BERT"
    reliability_score: float = 0.0
    
    # Additional insights
    dominant_traits: List[str] = field(default_factory=list)
    personality_summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        # Convert numpy types to native Python types for JSON serialization
        def convert_value(value):
            if hasattr(value, 'item'):  # numpy scalar
                return value.item()
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [convert_value(v) for v in value]
            else:
                return value
        
        return {
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'traits': convert_value(self.traits),
            'levels': convert_value(self.levels),
            'confidence': convert_value(self.confidence),
            'text_length': int(self.text_length),
            'analysis_method': self.analysis_method,
            'reliability_score': float(self.reliability_score),
            'dominant_traits': self.dominant_traits,
            'personality_summary': self.personality_summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityProfile':
        """Create from dictionary"""
        profile = cls(
            session_id=data.get('session_id', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            traits=data.get('traits', {}),
            levels=data.get('levels', {}),
            confidence=data.get('confidence', {}),
            text_length=data.get('text_length', 0),
            analysis_method=data.get('analysis_method', 'HEXACO-BERT'),
            reliability_score=data.get('reliability_score', 0.0),
            dominant_traits=data.get('dominant_traits', []),
            personality_summary=data.get('personality_summary', '')
        )
        return profile

class HEXACOModel:
    """HEXACO personality model implementation with scientific validation"""
    
    # HEXACO traits with reliability coefficients
    TRAITS = {
        'honesty_humility': {
            'name': 'Honesty-Humility',
            'symbol': 'H',
            'alpha': 0.88,
            'description': 'Sincerity, fairness, greed-avoidance, modesty',
            'low_desc': 'Manipulative, greedy, entitled, boastful',
            'medium_desc': 'Balanced fairness, moderate modesty',
            'high_desc': 'Sincere, fair, modest, genuine, altruistic'
        },
        'emotionality': {
            'name': 'Emotionality',
            'symbol': 'E',
            'alpha': 0.85,
            'description': 'Fearfulness, anxiety, dependence, sentimentality',
            'low_desc': 'Fearless, independent, tough, emotionally detached',
            'medium_desc': 'Balanced emotional responses, moderate sensitivity',
            'high_desc': 'Sensitive, anxious, sentimental, dependent, fearful'
        },
        'extraversion': {
            'name': 'eXtraversion',
            'symbol': 'X',
            'alpha': 0.87,
            'description': 'Social self-esteem, social boldness, sociability, liveliness',
            'low_desc': 'Shy, quiet, reserved, prefers solitude',
            'medium_desc': 'Socially balanced, comfortable in small groups',
            'high_desc': 'Outgoing, confident, sociable, energetic, bold'
        },
        'agreeableness': {
            'name': 'Agreeableness',
            'symbol': 'A',
            'alpha': 0.83,
            'description': 'Forgiveness, gentleness, flexibility, patience',
            'low_desc': 'Critical, stubborn, demanding, quick to anger',
            'medium_desc': 'Reasonably cooperative, selective forgiveness',
            'high_desc': 'Forgiving, gentle, flexible, patient, cooperative'
        },
        'conscientiousness': {
            'name': 'Conscientiousness',
            'symbol': 'C',
            'alpha': 0.86,
            'description': 'Organization, diligence, perfectionism, prudence',
            'low_desc': 'Disorganized, impulsive, careless, procrastinating',
            'medium_desc': 'Moderately organized, generally reliable',
            'high_desc': 'Highly organized, diligent, perfectionist, disciplined'
        },
        'openness': {
            'name': 'Openness to Experience',
            'symbol': 'O',
            'alpha': 0.84,
            'description': 'Aesthetic appreciation, inquisitiveness, creativity, unconventionality',
            'low_desc': 'Conventional, practical, traditional, prefers routine',
            'medium_desc': 'Moderately curious, selective creativity',
            'high_desc': 'Creative, imaginative, curious, unconventional, artistic'
        }
    }
    
    # Score thresholds for categorical levels
    LEVEL_THRESHOLDS = {
        'low': (0.0, 0.33),
        'medium': (0.34, 0.66),
        'high': (0.67, 1.0)
    }
    
    @classmethod
    def get_trait_info(cls, trait: str) -> Dict[str, Any]:
        """Get comprehensive information about a trait"""
        return cls.TRAITS.get(trait, {})
    
    @classmethod
    def score_to_level(cls, score: float) -> str:
        """Convert numerical score to categorical level"""
        if score <= 0.33:
            return 'low'
        elif score <= 0.66:
            return 'medium'
        else:
            return 'high'
    
    @classmethod
    def get_level_description(cls, trait: str, level: str) -> str:
        """Get description for a specific trait level"""
        trait_info = cls.TRAITS.get(trait, {})
        return trait_info.get(f'{level}_desc', f'{level.title()} {trait}')
    
    @classmethod
    def validate_score(cls, score: float) -> bool:
        """Validate if score is in valid range"""
        return 0.0 <= score <= 1.0
    
    @classmethod
    def calculate_reliability_score(cls, confidence_scores: Dict[str, float]) -> float:
        """Calculate overall reliability based on individual confidence scores"""
        if not confidence_scores:
            return 0.0
        
        # Weight by trait reliability (alpha coefficients)
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for trait, confidence in confidence_scores.items():
            if trait in cls.TRAITS:
                alpha = cls.TRAITS[trait]['alpha']
                weighted_sum += confidence * alpha
                weight_sum += alpha
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    @classmethod
    def identify_dominant_traits(cls, traits: Dict[str, float], n_top: int = 3) -> List[str]:
        """Identify the most dominant personality traits"""
        if not traits:
            return []
        
        # Sort traits by score in descending order
        sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N trait names
        return [trait for trait, score in sorted_traits[:n_top]]
    
    @classmethod
    def generate_personality_summary(cls, profile: PersonalityProfile) -> str:
        """Generate a natural language summary of personality profile"""
        if not profile.traits:
            return "Insufficient data for personality analysis."
        
        dominant = profile.dominant_traits[:2] if profile.dominant_traits else []
        
        summary_parts = []
        
        for trait in dominant:
            if trait in profile.levels:
                level = profile.levels[trait]
                trait_name = cls.TRAITS[trait]['name']
                description = cls.get_level_description(trait, level)
                summary_parts.append(f"{level.title()} {trait_name}: {description}")
        
        if summary_parts:
            return "; ".join(summary_parts) + "."
        else:
            return "Balanced personality profile across all traits."

class PersonalityAssetMapper:
    """Maps personality traits to visual assets"""
    
    ASSET_BASE_PATH = Path("assets/personality_features")
    
    ASSET_MAPPING = {
        'honesty_humility': {
            'low': 'hexaco_honesty_humility_low.png',
            'medium': 'hexaco_honesty_humility_medium.png',
            'high': 'hexaco_honesty_humility_high.png'
        },
        'emotionality': {
            'low': 'hexaco_emotionality_low.png',
            'medium': 'hexaco_emotionality_medium.png',
            'high': 'hexaco_emotionality_high.png'
        },
        'extraversion': {
            'low': 'hexaco_extraversion_low.png',
            'medium': 'hexaco_extraversion_medium.png',
            'high': 'hexaco_extraversion_high.png'
        },
        'agreeableness': {
            'low': 'hexaco_agreeableness_low.png',
            'medium': 'hexaco_agreeableness_medium.png',
            'high': 'hexaco_agreeableness_high.png'
        },
        'conscientiousness': {
            'low': 'hexaco_conscientiousness_low.png',
            'medium': 'hexaco_conscientiousness_medium.png',
            'high': 'hexaco_conscientiousness_high.png'
        },
        'openness': {
            'low': 'hexaco_openness_low.png',
            'medium': 'hexaco_openness_medium.png',
            'high': 'hexaco_openness_high.png'
        }
    }
    
    @classmethod
    def get_asset_path(cls, trait: str, level: str) -> Optional[Path]:
        """Get the file path for a personality trait visualization"""
        if trait not in cls.ASSET_MAPPING or level not in cls.ASSET_MAPPING[trait]:
            logger.warning(f"No asset found for {trait} - {level}")
            return None
        
        filename = cls.ASSET_MAPPING[trait][level]
        full_path = cls.ASSET_BASE_PATH / filename
        
        if full_path.exists():
            return full_path
        else:
            logger.warning(f"Asset file not found: {full_path}")
            return None
    
    @classmethod
    def get_all_assets_for_profile(cls, profile: PersonalityProfile) -> Dict[str, Optional[Path]]:
        """Get all asset paths for a personality profile"""
        assets = {}
        
        for trait, level in profile.levels.items():
            assets[trait] = cls.get_asset_path(trait, level)
        
        return assets

class PersonalityColorMapper:
    """Maps personality traits to thesis colors"""
    
    # Import thesis colors
    from thesis_colors import THESIS_COLORS, METRIC_COLORS
    
    TRAIT_COLORS = {
        'honesty_humility': THESIS_COLORS['primary_dark'],        # Dark burgundy
        'emotionality': THESIS_COLORS['primary_purple'],         # Deep purple
        'extraversion': THESIS_COLORS['primary_violet'],         # Rich violet
        'agreeableness': THESIS_COLORS['primary_rose'],          # Dusty rose
        'conscientiousness': THESIS_COLORS['primary_pink'],      # Soft pink
        'openness': THESIS_COLORS['accent_coral']                # Coral red
    }
    
    LEVEL_COLORS = {
        'low': THESIS_COLORS['accent_coral'],      # Coral (lower intensity)
        'medium': THESIS_COLORS['neutral_warm'],   # Warm sand (middle)
        'high': THESIS_COLORS['primary_dark']      # Dark burgundy (high intensity)
    }
    
    @classmethod
    def get_trait_color(cls, trait: str) -> str:
        """Get color for a specific personality trait"""
        return cls.TRAIT_COLORS.get(trait, cls.THESIS_COLORS['neutral_warm'])
    
    @classmethod
    def get_level_color(cls, level: str) -> str:
        """Get color for a trait level"""
        return cls.LEVEL_COLORS.get(level, cls.THESIS_COLORS['neutral_warm'])
    
    @classmethod
    def get_trait_gradient(cls, trait: str) -> List[str]:
        """Get color gradient for a specific trait (low -> medium -> high)"""
        base_color = cls.get_trait_color(trait)
        return [
            cls.LEVEL_COLORS['low'],
            cls.LEVEL_COLORS['medium'], 
            cls.LEVEL_COLORS['high']
        ]

# Configuration constants
PERSONALITY_CONFIG = {
    'min_text_length': 500,
    'confidence_threshold': 0.7,
    'reliability_threshold': 0.6,
    'max_batch_size': 16,
    'model_cache_timeout': 3600,  # 1 hour
    'analysis_version': '1.0.0'
}

def save_personality_profile(profile: PersonalityProfile, filepath: Union[str, Path]) -> bool:
    """Save personality profile to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save personality profile: {e}")
        return False

def load_personality_profile(filepath: Union[str, Path]) -> Optional[PersonalityProfile]:
    """Load personality profile from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return PersonalityProfile.from_dict(data)
    except Exception as e:
        logger.error(f"Failed to load personality profile: {e}")
        return None

# Export main classes and functions
__all__ = [
    'PersonalityProfile',
    'HEXACOModel', 
    'PersonalityAssetMapper',
    'PersonalityColorMapper',
    'PERSONALITY_CONFIG',
    'save_personality_profile',
    'load_personality_profile'
]