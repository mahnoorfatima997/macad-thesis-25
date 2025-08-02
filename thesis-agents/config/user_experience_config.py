# config/user_experience_config.py - User Experience Configuration

class UserExperienceConfig:
    """Configuration for user experience settings"""
    
    # RESPONSE LENGTH SETTINGS
    MAX_RESPONSE_LENGTH = 200  # Reduced from 300 - Maximum words per response
    MAX_COGNITIVE_INTERVENTION_LENGTH = 120  # Reduced from 150 - Maximum words for cognitive interventions
    MAX_SOCRATIC_RESPONSE_LENGTH = 180  # Reduced from 250 - Maximum words for Socratic responses
    MAX_DOMAIN_EXPERT_RESPONSE_LENGTH = 150  # Reduced from 200 - Maximum words for domain expert responses
    
    # METRICS DISPLAY SETTINGS
    SHOW_SCIENTIFIC_METRICS = False  # Hide verbose metrics from user
    SHOW_COGNITIVE_SUMMARY = False  # Hide cognitive assessment summary
    SHOW_RESPONSE_SUMMARY = True  # Show brief processing summary
    SHOW_DEBUG_INFO = False  # Hide debug information
    
    # COGNITIVE INTERVENTION SETTINGS
    USE_SIMPLIFIED_COGNITIVE_AGENT = True  # Use simplified cognitive agent
    SHOW_COGNITIVE_PROTECTION_MESSAGE = True  # Show friendly protection message
    COGNITIVE_INTERVENTION_STYLE = "friendly"  # "friendly", "academic", "minimal"
    
    # RESPONSE STYLE SETTINGS
    RESPONSE_TONE = "encouraging"  # "encouraging", "neutral", "formal"
    USE_EMOJIS = True  # Use emojis in responses
    USE_BULLET_POINTS = True  # Use bullet points for clarity
    USE_BOLD_HEADERS = True  # Use bold headers for structure
    
    # CONVERSATION SETTINGS
    CONVERSATION_DEPTH_THRESHOLD = 3  # Minimum messages before feedback
    EXAMPLE_REQUEST_THRESHOLD = 5  # Minimum messages before examples
    MAX_CONSECUTIVE_QUESTIONS = 2  # Maximum consecutive questions from agent
    
    # PHASE DETECTION SETTINGS
    ENABLE_PHASE_DETECTION = True  # Enable three-phase journey detection
    SHOW_PHASE_INDICATORS = False  # Show current phase to user
    PHASE_SPECIFIC_GUIDANCE = True  # Provide phase-specific guidance
    
    # VISUAL ANALYSIS SETTINGS
    ENABLE_VISUAL_ANALYSIS = True  # Enable computer vision integration
    SHOW_VISUAL_FEEDBACK = True  # Show visual analysis feedback
    MAX_VISUAL_RESPONSE_LENGTH = 200  # Maximum words for visual responses
    
    # 3D ANALYSIS SETTINGS
    ENABLE_3D_ANALYSIS = True  # Enable 3D spatial analysis
    SHOW_3D_FEEDBACK = True  # Show 3D analysis feedback
    MAX_3D_RESPONSE_LENGTH = 200  # Maximum words for 3D responses
    
    # LINKOGRAPHY SETTINGS
    ENABLE_LINKOGRAPHY = True  # Enable design move tracking
    SHOW_LINKOGRAPHY_FEEDBACK = False  # Hide linkography from user
    MAX_LINKOGRAPHY_RESPONSE_LENGTH = 150  # Maximum words for linkography
    
    # ERROR HANDLING SETTINGS
    SHOW_ERROR_MESSAGES = False  # Hide technical error messages
    SHOW_FALLBACK_MESSAGES = True  # Show friendly fallback messages
    LOG_ERRORS = True  # Log errors for debugging
    
    # PERFORMANCE SETTINGS
    ENABLE_RESPONSE_CACHING = True  # Cache responses for performance
    MAX_CACHE_SIZE = 100  # Maximum cached responses
    RESPONSE_TIMEOUT = 30  # Response timeout in seconds
    
    @classmethod
    def get_response_length_limit(cls, agent_type: str) -> int:
        """Get response length limit for specific agent type"""
        limits = {
            "cognitive_enhancement": cls.MAX_COGNITIVE_INTERVENTION_LENGTH,
            "socratic_tutor": cls.MAX_SOCRATIC_RESPONSE_LENGTH,
            "domain_expert": cls.MAX_DOMAIN_EXPERT_RESPONSE_LENGTH,
            "visual_analysis": cls.MAX_VISUAL_RESPONSE_LENGTH,
            "3d_analysis": cls.MAX_3D_RESPONSE_LENGTH,
            "linkography": cls.MAX_LINKOGRAPHY_RESPONSE_LENGTH,
            "default": cls.MAX_RESPONSE_LENGTH
        }
        return limits.get(agent_type, limits["default"])
    
    @classmethod
    def should_show_metrics(cls, metric_type: str) -> bool:
        """Check if specific metric type should be shown to user"""
        if not cls.SHOW_SCIENTIFIC_METRICS:
            return False
        
        metric_settings = {
            "cognitive_summary": cls.SHOW_COGNITIVE_SUMMARY,
            "response_summary": cls.SHOW_RESPONSE_SUMMARY,
            "debug_info": cls.SHOW_DEBUG_INFO,
            "phase_indicators": cls.SHOW_PHASE_INDICATORS,
            "visual_feedback": cls.SHOW_VISUAL_FEEDBACK,
            "3d_feedback": cls.SHOW_3D_FEEDBACK,
            "linkography_feedback": cls.SHOW_LINKOGRAPHY_FEEDBACK
        }
        return metric_settings.get(metric_type, False)
    
    @classmethod
    def get_cognitive_intervention_style(cls) -> str:
        """Get cognitive intervention style setting"""
        return cls.COGNITIVE_INTERVENTION_STYLE
    
    @classmethod
    def is_feature_enabled(cls, feature: str) -> bool:
        """Check if specific feature is enabled"""
        feature_settings = {
            "simplified_cognitive_agent": cls.USE_SIMPLIFIED_COGNITIVE_AGENT,
            "phase_detection": cls.ENABLE_PHASE_DETECTION,
            "visual_analysis": cls.ENABLE_VISUAL_ANALYSIS,
            "3d_analysis": cls.ENABLE_3D_ANALYSIS,
            "linkography": cls.ENABLE_LINKOGRAPHY,
            "response_caching": cls.ENABLE_RESPONSE_CACHING
        }
        return feature_settings.get(feature, False)

# Quick access functions
def get_max_response_length(agent_type: str = "default") -> int:
    """Get maximum response length for agent type"""
    return UserExperienceConfig.get_response_length_limit(agent_type)

def should_show_metrics(metric_type: str) -> bool:
    """Check if metrics should be shown"""
    return UserExperienceConfig.should_show_metrics(metric_type)

def is_feature_enabled(feature: str) -> bool:
    """Check if feature is enabled"""
    return UserExperienceConfig.is_feature_enabled(feature)

def get_cognitive_style() -> str:
    """Get cognitive intervention style"""
    return UserExperienceConfig.get_cognitive_intervention_style() 