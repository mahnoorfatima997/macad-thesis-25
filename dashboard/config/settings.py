"""
Dashboard configuration settings and constants.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env in common locations
# 1) Current working directory
load_dotenv()
# 2) Project root relative to this file
_ROOT_ENV = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(_ROOT_ENV):
    load_dotenv(_ROOT_ENV, override=True)

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "Unified Architectural Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Input mode options
INPUT_MODES = ["Text Only", "Image + Text", "Image Only"]

# Mentor type options for research comparison
MENTOR_TYPES = ["Socratic Agent", "Raw GPT"]

# Template design prompts
TEMPLATE_PROMPTS = {
    "Select a template...": "",
    "🏢 Sustainable Office Building": "I'm designing a sustainable office building for a tech company. The building should accommodate 200 employees with flexible workspaces, meeting rooms, and common areas. I want to focus on energy efficiency, natural lighting, and creating a collaborative environment. The site is in an urban area with limited green space.",
    "🏫 Community Learning Center": "I'm creating a community learning center that will serve as a hub for education, workshops, and community events. The building needs to include classrooms, a library, multipurpose spaces, and outdoor learning areas. I want it to be welcoming to all ages and accessible to everyone in the community.",
    "🏠 Residential Complex": "I'm designing a residential complex that combines modern living with community spaces. The project includes apartments, shared amenities, and green spaces. I want to create a sense of community while maintaining privacy and sustainability.",
    "🏛️ Cultural Center": "I'm designing a cultural center that will showcase local arts and provide performance spaces. The building needs to include galleries, theaters, workshops, and public gathering areas. I want it to be both functional and inspiring."
}

# Mode options
TESTING_MODES = ["MENTOR", "RAW_GPT", "GENERIC_AI", "CONTROL"]

# Skill levels
SKILL_LEVELS = ["beginner", "intermediate", "advanced"]

# Project types for phase progression
PROJECT_TYPES = [
    "Community Center", 
    "Office Building", 
    "Residential Complex", 
    "Cultural Center", 
    "Educational Facility", 
    "Custom Project"
]

# Assessment modes
ASSESSMENT_MODES = [
    "Phase-Based Socratic", 
    "Agentic Mentor", 
    "Combined Mode"
]

# Export formats
EXPORT_FORMATS = ["JSON", "CSV", "Excel"]

def get_api_key() -> str:
    """Get API key from environment or Streamlit secrets"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            api_key = st.secrets.get('OPENAI_API_KEY', '')
        except:
            api_key = ''
    return api_key 