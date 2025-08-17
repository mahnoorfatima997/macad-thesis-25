#!/usr/bin/env python3
"""
Configuration file for Mega Architectural Mentor v2.0
Customize system behavior and settings
"""

import os
import sys
from typing import Dict, Any, List

# Add thesis-agents to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))

try:
    from utils.secrets_manager import secrets_manager
except ImportError:
    # Fallback if secrets_manager is not available
    class FallbackSecretsManager:
        def get_secret(self, key: str, default: str = "") -> str:
            return os.getenv(key, default)
        def get_bool_secret(self, key: str, default: bool = False) -> bool:
            value = os.getenv(key, str(default).lower())
            return value.lower() in ('true', '1', 'yes', 'on')
        def get_int_secret(self, key: str, default: int = 0) -> int:
            try:
                return int(os.getenv(key, str(default)))
            except (ValueError, TypeError):
                return default
        def get_float_secret(self, key: str, default: float = 0.0) -> float:
            try:
                return float(os.getenv(key, str(default)))
            except (ValueError, TypeError):
                return default
    secrets_manager = FallbackSecretsManager()

class MegaConfig:
    """Configuration class for Mega Architectural Mentor"""

    def __init__(self):
        # Load from secrets manager (supports both st.secrets and environment variables)
        self.load_from_secrets()
    
    def load_from_secrets(self):
        """Load configuration from secrets manager (supports both st.secrets and environment variables)"""

        # API Configuration
        self.openai_api_key = secrets_manager.get_secret("OPENAI_API_KEY", "")
        self.openai_model = secrets_manager.get_secret("OPENAI_MODEL", "gpt-4-vision-preview")
        self.max_tokens = secrets_manager.get_int_secret("MAX_TOKENS", 4000)

        # SAM Configuration (available in backend, optional in UI)
        self.sam_model_name = secrets_manager.get_secret("SAM_MODEL", "facebook/sam-vit-base")
        self.sam_device = secrets_manager.get_secret("SAM_DEVICE", "auto")  # auto, cpu, cuda
        self.enable_sam = secrets_manager.get_bool_secret("ENABLE_SAM", True)  # Default backend setting
        
        # Agent Configuration
        self.domain = secrets_manager.get_secret("DOMAIN", "architecture")
        self.default_skill_level = secrets_manager.get_secret("DEFAULT_SKILL_LEVEL", "intermediate")
        self.max_agents_per_response = secrets_manager.get_int_secret("MAX_AGENTS_PER_RESPONSE", 3)

        # Analysis Configuration
        self.analysis_confidence_threshold = secrets_manager.get_float_secret("ANALYSIS_CONFIDENCE_THRESHOLD", 0.7)
        self.max_cognitive_flags = secrets_manager.get_int_secret("MAX_COGNITIVE_FLAGS", 5)
        self.enable_skill_assessment = secrets_manager.get_bool_secret("ENABLE_SKILL_ASSESSMENT", True)

        # UI Configuration
        self.page_title = secrets_manager.get_secret("PAGE_TITLE", "🏗️ Mega Architectural Mentor v2.0")
        self.page_icon = secrets_manager.get_secret("PAGE_ICON", "🏗️")
        self.layout = secrets_manager.get_secret("LAYOUT", "wide")
        self.sidebar_state = secrets_manager.get_secret("SIDEBAR_STATE", "expanded")

        # Debug and Development
        self.debug_mode = secrets_manager.get_bool_secret("DEBUG_MODE", False)
        self.dev_mode = secrets_manager.get_bool_secret("DEV_MODE", False)
        self.log_level = secrets_manager.get_secret("LOG_LEVEL", "INFO")

        # Performance Configuration
        self.max_image_size = secrets_manager.get_int_secret("MAX_IMAGE_SIZE", 2048)  # pixels
        self.image_quality = secrets_manager.get_int_secret("IMAGE_QUALITY", 85)  # percentage
        self.cache_results = secrets_manager.get_bool_secret("CACHE_RESULTS", True)

        # Knowledge Base Configuration
        self.knowledge_base_path = secrets_manager.get_secret("KNOWLEDGE_BASE_PATH", "./thesis-agents/knowledge_base")
        self.vectorstore_path = secrets_manager.get_secret("VECTORSTORE_PATH", "./thesis-agents/knowledge_base/vectorstore")
        self.max_knowledge_results = secrets_manager.get_int_secret("MAX_KNOWLEDGE_RESULTS", 5)
        
        # Interaction Configuration
        self.max_chat_history = secrets_manager.get_int_secret("MAX_CHAT_HISTORY", 50)
        self.session_timeout = secrets_manager.get_int_secret("SESSION_TIMEOUT", 3600)  # seconds
        self.auto_save_interval = secrets_manager.get_int_secret("AUTO_SAVE_INTERVAL", 300)  # seconds
    
    def get_sam_config(self) -> Dict[str, Any]:
        """Get SAM-specific configuration"""
        return {
            "model_name": self.sam_model_name,
            "device": self.sam_device,
            "enabled": self.enable_sam,
            "max_image_size": self.max_image_size,
            "image_quality": self.image_quality
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent-specific configuration"""
        return {
            "domain": self.domain,
            "default_skill_level": self.default_skill_level,
            "max_agents_per_response": self.max_agents_per_response,
            "confidence_threshold": self.analysis_confidence_threshold,
            "max_cognitive_flags": self.max_cognitive_flags,
            "enable_skill_assessment": self.enable_skill_assessment
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI-specific configuration"""
        return {
            "page_title": self.page_title,
            "page_icon": self.page_icon,
            "layout": self.layout,
            "sidebar_state": self.sidebar_state,
            "max_chat_history": self.max_chat_history
        }
    
    def get_knowledge_config(self) -> Dict[str, Any]:
        """Get knowledge base configuration"""
        return {
            "knowledge_base_path": self.knowledge_base_path,
            "vectorstore_path": self.vectorstore_path,
            "max_results": self.max_knowledge_results
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if self.max_tokens <= 0:
            errors.append("MAX_TOKENS must be positive")
        
        if self.analysis_confidence_threshold < 0 or self.analysis_confidence_threshold > 1:
            errors.append("ANALYSIS_CONFIDENCE_THRESHOLD must be between 0 and 1")
        
        if self.max_image_size <= 0:
            errors.append("MAX_IMAGE_SIZE must be positive")
        
        if self.image_quality < 1 or self.image_quality > 100:
            errors.append("IMAGE_QUALITY must be between 1 and 100")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "openai": {
                "api_key": "***" if self.openai_api_key else "",
                "model": self.openai_model,
                "max_tokens": self.max_tokens
            },
            "sam": self.get_sam_config(),
            "agents": self.get_agent_config(),
            "ui": self.get_ui_config(),
            "knowledge": self.get_knowledge_config(),
            "debug": {
                "debug_mode": self.debug_mode,
                "dev_mode": self.dev_mode,
                "log_level": self.log_level
            },
            "performance": {
                "max_image_size": self.max_image_size,
                "image_quality": self.image_quality,
                "cache_results": self.cache_results
            },
            "interaction": {
                "max_chat_history": self.max_chat_history,
                "session_timeout": self.session_timeout,
                "auto_save_interval": self.auto_save_interval
            }
        }
    
    def print_config(self):
        """Print current configuration"""
        print("🏗️ Mega Architectural Mentor v2.0 - Configuration")
        print("=" * 60)
        
        config_dict = self.to_dict()
        
        for section, settings in config_dict.items():
            print(f"\n📋 {section.upper()}:")
            for key, value in settings.items():
                if key == "api_key" and value:
                    print(f"  {key}: ***")
                else:
                    print(f"  {key}: {value}")
        
        # Validate configuration
        errors = self.validate()
        if errors:
            print(f"\n⚠️ Configuration Errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"\n✅ Configuration is valid")

# Global configuration instance
config = MegaConfig()

# Example usage and documentation
if __name__ == "__main__":
    config.print_config()
    
    print("\n" + "=" * 60)
    print("📝 Configuration Examples:")
    print("=" * 60)
    
    print("\n🔧 Environment Variables:")
    print("OPENAI_API_KEY=your_api_key_here")
    print("OPENAI_MODEL=gpt-4-vision-preview")
    print("SAM_DEVICE=cpu")
    print("ENABLE_SAM=false")
    print("DEBUG_MODE=true")

    print("\n🎯 Common Configurations:")
    print("\n1. Fast processing (SAM disabled in UI):")
    print("   ENABLE_SAM=false")
    print("   MAX_IMAGE_SIZE=1024")

    print("\n2. Full vision analysis (SAM enabled in UI):")
    print("   ENABLE_SAM=true")
    print("   SAM_DEVICE=cuda")
    print("   MAX_IMAGE_SIZE=2048")

    print("\n3. Development mode:")
    print("   DEBUG_MODE=true")
    print("   DEV_MODE=true")
    print("   LOG_LEVEL=DEBUG")