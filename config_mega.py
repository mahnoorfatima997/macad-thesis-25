#!/usr/bin/env python3
"""
Configuration file for Mega Architectural Mentor v2.0
Customize system behavior and settings
"""

import os
from typing import Dict, Any, List

class MegaConfig:
    """Configuration class for Mega Architectural Mentor"""
    
    def __init__(self):
        # Load from environment variables or use defaults
        self.load_from_env()
    
    def load_from_env(self):
        """Load configuration from environment variables"""
        
        # API Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        
                 # SAM Configuration (available in backend, optional in UI)
         self.sam_model_name = os.getenv("SAM_MODEL", "facebook/sam-vit-base")
         self.sam_device = os.getenv("SAM_DEVICE", "auto")  # auto, cpu, cuda
         self.enable_sam = os.getenv("ENABLE_SAM", "true").lower() == "true"  # Default backend setting
        
        # Agent Configuration
        self.domain = os.getenv("DOMAIN", "architecture")
        self.default_skill_level = os.getenv("DEFAULT_SKILL_LEVEL", "intermediate")
        self.max_agents_per_response = int(os.getenv("MAX_AGENTS_PER_RESPONSE", "3"))
        
        # Analysis Configuration
        self.analysis_confidence_threshold = float(os.getenv("ANALYSIS_CONFIDENCE_THRESHOLD", "0.7"))
        self.max_cognitive_flags = int(os.getenv("MAX_COGNITIVE_FLAGS", "5"))
        self.enable_skill_assessment = os.getenv("ENABLE_SKILL_ASSESSMENT", "true").lower() == "true"
        
        # UI Configuration
        self.page_title = os.getenv("PAGE_TITLE", "🏗️ Mega Architectural Mentor v2.0")
        self.page_icon = os.getenv("PAGE_ICON", "🏗️")
        self.layout = os.getenv("LAYOUT", "wide")
        self.sidebar_state = os.getenv("SIDEBAR_STATE", "expanded")
        
        # Debug and Development
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Performance Configuration
        self.max_image_size = int(os.getenv("MAX_IMAGE_SIZE", "2048"))  # pixels
        self.image_quality = int(os.getenv("IMAGE_QUALITY", "85"))  # percentage
        self.cache_results = os.getenv("CACHE_RESULTS", "true").lower() == "true"
        
        # Knowledge Base Configuration
        self.knowledge_base_path = os.getenv("KNOWLEDGE_BASE_PATH", "./thesis-agents/knowledge_base")
        self.vectorstore_path = os.getenv("VECTORSTORE_PATH", "./thesis-agents/knowledge_base/vectorstore")
        self.max_knowledge_results = int(os.getenv("MAX_KNOWLEDGE_RESULTS", "5"))
        
        # Interaction Configuration
        self.max_chat_history = int(os.getenv("MAX_CHAT_HISTORY", "50"))
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "3600"))  # seconds
        self.auto_save_interval = int(os.getenv("AUTO_SAVE_INTERVAL", "300"))  # seconds
    
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