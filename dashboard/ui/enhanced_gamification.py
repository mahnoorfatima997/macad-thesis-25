"""
Enhanced Visual Gamification System
Creates engaging, interactive, visual game experiences with improved UI elements.
Maintains Streamlit compatibility while adding creative visual enhancements.
"""

import streamlit as st
import random
from typing import Dict, List, Any
import json
import time

# Enhanced visual themes with thesis colors
ENHANCED_THEMES = {
    "role_play": {
        "primary": "#4f3a3e",      # Dark burgundy
        "secondary": "#5c4f73",    # Deep purple
        "accent": "#e0ceb5",       # Light beige
        "gradient": "linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #e0ceb5 100%)",
        "icon": "◉",
        "animation": "bounce",
        "symbol": "▲"
    },
    "perspective_shift": {
        "primary": "#784c80",      # Rich violet
        "secondary": "#b87189",    # Dusty rose
        "accent": "#cda29a",       # Soft pink
        "gradient": "linear-gradient(135deg, #784c80 0%, #b87189 50%, #cda29a 100%)",
        "icon": "◈",
        "animation": "pulse",
        "symbol": "◆"
    },
    "detective": {
        "primary": "#cd766d",      # Coral red
        "secondary": "#d99c66",    # Soft orange
        "accent": "#dcc188",       # Warm sand
        "gradient": "linear-gradient(135deg, #cd766d 0%, #d99c66 50%, #dcc188 100%)",
        "icon": "◎",
        "animation": "shake",
        "symbol": "●"
    },
    "constraint": {
        "primary": "#5c4f73",      # Deep purple
        "secondary": "#784c80",    # Rich violet
        "accent": "#b87189",       # Dusty rose
        "gradient": "linear-gradient(135deg, #5c4f73 0%, #784c80 50%, #b87189 100%)",
        "icon": "◐",
        "animation": "rotate",
        "symbol": "■"
    },
    "storytelling": {
        "primary": "#d99c66",      # Soft orange
        "secondary": "#dcc188",    # Warm sand
        "accent": "#e0ceb5",       # Light beige
        "gradient": "linear-gradient(135deg, #d99c66 0%, #dcc188 50%, #e0ceb5 100%)",
        "icon": "◈",
        "animation": "fade",
        "symbol": "◈"
    },
    "time_travel": {
        "primary": "#b87189",      # Dusty rose
        "secondary": "#cda29a",    # Soft pink
        "accent": "#e0ceb5",       # Light beige
        "gradient": "linear-gradient(135deg, #b87189 0%, #cda29a 50%, #e0ceb5 100%)",
        "icon": "◉",
        "animation": "pulse",
        "symbol": "◉"
    },
    "transformation": {
        "primary": "#4f3a3e",      # Dark burgundy
        "secondary": "#cd766d",    # Coral red
        "accent": "#d99c66",       # Soft orange
        "gradient": "linear-gradient(135deg, #4f3a3e 0%, #cd766d 50%, #d99c66 100%)",
        "icon": "▲",
        "animation": "bounce",
        "symbol": "▲"
    }
}

class FlexibleContentGenerator:
    """Generate dynamic game content based on user input and context."""

    def __init__(self):
        self.persona_templates = {
            "community center": ["Community Leader", "Parent with Children", "Teenager", "Senior Citizen", "Person with Disability"],
            "library": ["Student", "Researcher", "Parent with Toddler", "Senior Reader", "Librarian"],
            "school": ["Student", "Teacher", "Parent", "Administrator", "Maintenance Staff"],
            "hospital": ["Patient", "Visitor", "Doctor", "Nurse", "Emergency Responder"],
            "museum": ["Art Enthusiast", "Tourist", "School Group Leader", "Researcher", "Security Guard"]
        }

        self.constraint_templates = {
            "budget": ["Limited Budget", "Cost Overrun", "Funding Cut", "Value Engineering"],
            "site": ["Difficult Terrain", "Small Site", "Flood Zone", "Historic District"],
            "program": ["Changing Requirements", "Multi-Use Needs", "Accessibility", "Technology Integration"],
            "time": ["Tight Schedule", "Phased Construction", "Seasonal Constraints", "Permit Delays"]
        }

        self.mystery_templates = {
            "circulation": ["People avoid main entrance", "Confusing wayfinding", "Bottlenecks in corridors"],
            "comfort": ["Spaces feel uncomfortable", "Poor acoustics", "Temperature issues"],
            "usage": ["Spaces underutilized", "Unexpected user behavior", "Maintenance problems"]
        }

    def generate_personas_from_context(self, building_type: str, user_message: str) -> Dict[str, Dict[str, Any]]:
        """Generate contextual personas based on user message and building type."""

        # Analyze user message to understand what they're asking about
        user_message_lower = user_message.lower()

        # Extract personas mentioned in the user's actual question
        mentioned_personas = []

        # Dynamic persona extraction based on user's words
        persona_indicators = {
            # Age groups
            "child": "Child", "kid": "Child", "children": "Children", "baby": "Parent with Baby",
            "elderly": "Senior Citizen", "senior": "Senior Citizen", "old": "Older Adult", "aging": "Senior",
            "teen": "Teenager", "young": "Young Adult", "youth": "Young Person",
            "adult": "Adult", "parent": "Parent", "family": "Family Member",

            # Abilities
            "disabled": "Person with Disability", "wheelchair": "Wheelchair User",
            "blind": "Visually Impaired Person", "deaf": "Hearing Impaired Person",
            "mobility": "Person with Mobility Needs",

            # Roles/Activities
            "visitor": "Visitor", "tourist": "Tourist", "guest": "Guest", "newcomer": "First-time Visitor",
            "staff": "Staff Member", "employee": "Employee", "worker": "Worker",
            "volunteer": "Volunteer", "organizer": "Event Organizer",

            # Context-specific
            "student": "Student", "teacher": "Educator", "artist": "Artist", "performer": "Performer"
        }

        # Find personas mentioned in user's question
        for indicator, persona in persona_indicators.items():
            if indicator in user_message_lower:
                mentioned_personas.append(persona)

        # If no specific personas mentioned, infer from question context
        if not mentioned_personas:
            if "different" in user_message_lower or "various" in user_message_lower:
                # User asking about different types of users
                mentioned_personas = ["Community Member", "Visitor", "Regular User", "Occasional User"]
            elif "experience" in user_message_lower:
                # User asking about user experience
                mentioned_personas = ["First-time User", "Regular User", "Staff Member"]
            else:
                # Default to building-appropriate personas
                building_defaults = {
                    "community center": ["Community Member", "Parent", "Senior", "Youth"],
                    "library": ["Student", "Researcher", "Parent with Child", "Senior"],
                    "school": ["Student", "Teacher", "Parent", "Visitor"],
                    "hospital": ["Patient", "Visitor", "Staff", "Emergency User"],
                    "museum": ["Tourist", "Art Enthusiast", "Student", "Researcher"]
                }
                mentioned_personas = building_defaults.get(building_type, ["User", "Visitor", "Staff"])

        # Limit to 5 personas
        all_personas = mentioned_personas[:5]

        # Generate persona data with all required fields
        personas = {}
        for i, persona_name in enumerate(all_personas):
            personas[persona_name] = {
                "description": f"Experience your {building_type} as a {persona_name.lower()}",
                "mission": f"Navigate and use this {building_type} effectively as a {persona_name.lower()}",
                "icon": ["👤", "👥", "🧑", "👨", "👩"][i % 5],
                "challenge": f"How does a {persona_name.lower()} navigate and use this space?",
                "insights": [f"{persona_name} has unique needs in this space", "Consider accessibility and comfort"]
            }

        return personas

    def generate_constraints_from_context(self, building_type: str, user_message: str, challenge_data: Dict = None) -> Dict[str, Dict[str, Any]]:
        """Generate highly contextual constraints based on user message and challenge data."""
        constraints = {}

        # Use rich context data if available
        context_data = challenge_data or {}
        specific_constraint = context_data.get("specific_constraint", "").lower()
        context_keywords = context_data.get("context_keywords", [])
        specific_elements = context_data.get("specific_elements", [])

        # CONTEXT-AWARE CONSTRAINT GENERATION
        detected_constraints = []

        # Check for circulation-specific constraints
        if "circulation" in specific_constraint or any("circulation" in str(kw).lower() for kw in context_keywords):
            detected_constraints.extend(["circulation", "flow"])

        # Check for warehouse conversion constraints
        elif "warehouse" in user_message.lower() or "conversion" in specific_constraint:
            detected_constraints.extend(["conversion", "structure"])

        # Check for space planning constraints
        elif "layout" in user_message.lower() or "space" in specific_constraint:
            detected_constraints.extend(["space", "program"])

        # Fallback to keyword detection
        else:
            constraint_keywords = {
                "budget": ["budget", "cost", "money", "expensive", "cheap", "funding"],
                "site": ["site", "location", "terrain", "flood", "small", "limited space"],
                "time": ["time", "schedule", "deadline", "fast", "quick", "delay"],
                "program": ["requirements", "needs", "users", "function", "multi-use"]
            }

            for category, keywords in constraint_keywords.items():
                if any(keyword in user_message.lower() for keyword in keywords):
                    detected_constraints.append(category)

        # If no specific constraints detected, use general ones
        if not detected_constraints:
            detected_constraints = ["budget", "site", "program"]

        # Generate constraint data with context-aware options
        constraint_options = {
            # CONTEXT-SPECIFIC CONSTRAINTS
            "circulation": {
                "Entrance Bottleneck": {"impact": f"Main entrance creates congestion in {building_type}", "color": "#cd766d", "challenge": "How to distribute arrival flows?", "icon": "◐"},
                "Vertical Circulation": {"impact": "Stairs interrupt horizontal flow", "color": "#d99c66", "challenge": "How to integrate vertical movement seamlessly?", "icon": "◐"}
            },
            "flow": {
                "Dead-End Spaces": {"impact": "Some areas become isolated", "color": "#b87189", "challenge": "How to create continuous circulation loops?", "icon": "◐"},
                "Conflicting Paths": {"impact": "Different user groups cross paths", "color": "#5c4f73", "challenge": "How to separate incompatible flows?", "icon": "◐"}
            },
            "conversion": {
                "Industrial Scale": {"impact": f"Warehouse spaces feel overwhelming for {building_type}", "color": "#4f3a3e", "challenge": "How to create human-scale spaces within large volume?", "icon": "◐"},
                "Existing Structure": {"impact": "Concrete columns limit layout flexibility", "color": "#e0ceb5", "challenge": "How to work with structural constraints?", "icon": "◐"}
            },
            "structure": {
                "Column Grid": {"impact": "Structural grid doesn't match program needs", "color": "#dcc188", "challenge": "How to align structure with function?", "icon": "◐"},
                "Load Limitations": {"impact": "Floor can't support heavy loads", "color": "#cda29a", "challenge": "How to distribute weight effectively?", "icon": "◐"}
            },
            "space": {
                "Irregular Shape": {"impact": "Odd building geometry creates challenges", "color": "#cd766d", "challenge": "How to make awkward spaces functional?", "icon": "◐"},
                "Low Ceiling Height": {"impact": "Limited vertical space", "color": "#d99c66", "challenge": "How to maximize spatial quality with height limits?", "icon": "◐"}
            },
            # GENERIC CONSTRAINTS (fallback)
            "budget": {
                "Budget Cut": {"impact": "50% reduction in funds", "color": "#cd766d", "challenge": "How to maintain quality with less money?", "icon": "◐"},
                "Value Engineering": {"impact": "Cost optimization required", "color": "#d99c66", "challenge": "What can be simplified without losing function?", "icon": "◐"}
            },
            "site": {
                "Small Site": {"impact": "Limited building footprint", "color": "#b87189", "challenge": "How to fit the program in less space?", "icon": "◐"},
                "Difficult Access": {"impact": "Construction challenges", "color": "#5c4f73", "challenge": "How to build with limited access?", "icon": "◐"}
            },
            "program": {
                "Multi-Use Requirements": {"impact": "Spaces must serve multiple functions", "color": "#4f3a3e", "challenge": "How to design flexible spaces?", "icon": "◐"},
                "Accessibility Compliance": {"impact": "Full universal design", "color": "#e0ceb5", "challenge": "How to include everyone?", "icon": "◐"}
            },
            "time": {
                "Tight Schedule": {"impact": "Accelerated timeline", "color": "#dcc188", "challenge": "How to design faster without compromising quality?", "icon": "◐"},
                "Phased Construction": {"impact": "Building in stages", "color": "#cda29a", "challenge": "How to maintain functionality during construction?", "icon": "◐"}
            }
        }

        # Select constraints based on detected categories
        for category in detected_constraints[:3]:  # Limit to 3 categories
            if category in constraint_options:
                constraints.update(constraint_options[category])

        return constraints

    def generate_mystery_from_context(self, building_type: str, user_message: str) -> Dict[str, Any]:
        """Generate FLEXIBLE contextual mystery based on ANY architectural topic in user message."""

        # Extract the main architectural topic from user message
        user_lower = user_message.lower()

        # Flexible topic detection for ANY architectural element
        architectural_topics = {
            # Spatial
            "circulation": "circulation patterns", "flow": "movement flow", "wayfinding": "navigation",
            "entrance": "entry experience", "lobby": "arrival sequence", "corridor": "circulation paths",

            # Building Systems
            "facade": "building exterior", "envelope": "building skin", "exterior": "building facade",
            "landscape": "site design", "garden": "outdoor spaces", "courtyard": "landscape integration",
            "structure": "structural system", "foundation": "structural support", "frame": "building structure",

            # Environmental
            "lighting": "illumination", "acoustic": "sound environment", "ventilation": "air quality",
            "thermal": "temperature comfort", "daylight": "natural lighting", "shadow": "light and shadow",

            # Materials & Finishes
            "material": "material selection", "finish": "surface treatments", "texture": "tactile qualities",
            "color": "color palette", "pattern": "visual patterns",

            # Program & Function
            "program": "functional requirements", "space": "spatial organization", "room": "space planning",
            "function": "functional design", "activity": "programmatic needs"
        }

        detected_topic = "design challenge"
        for keyword, topic in architectural_topics.items():
            if keyword in user_lower:
                detected_topic = topic
                break

        # Generate flexible problem statement
        detected_problem = f"There's an unexpected issue with the {detected_topic} in your {building_type}"



        # Generate FLEXIBLE clues based on detected topic
        topic_clue_templates = {
            "circulation patterns": [
                "The main pathways create bottlenecks during peak hours",
                "Users are taking unexpected routes through the space",
                "Key destinations are not clearly connected"
            ],
            "building exterior": [
                "The facade doesn't respond to local climate conditions",
                "Material choices don't align with the building's function",
                "The building's scale feels inappropriate for the context"
            ],
            "site design": [
                "The landscape doesn't support the building's program",
                "Outdoor spaces lack clear connections to interior functions",
                "Site drainage and grading create accessibility issues"
            ],
            "structural system": [
                "The structural grid doesn't align with programmatic needs",
                "Column placement interferes with spatial flexibility",
                "The structural expression doesn't match the architectural intent"
            ],
            "illumination": [
                "Natural light distribution is uneven throughout the day",
                "Artificial lighting doesn't support different activities",
                "Glare and shadows create visual discomfort"
            ],
            "material selection": [
                "Material performance doesn't match environmental conditions",
                "Surface treatments don't support the intended use patterns",
                "Material transitions create maintenance challenges"
            ]
        }

        # Find matching clues or generate generic ones
        clues = topic_clue_templates.get(detected_topic, [
            f"The {detected_topic} doesn't meet user expectations",
            f"Environmental factors affect the {detected_topic}",
            f"The {detected_topic} needs better integration with other systems"
        ])

        # Add red herrings
        red_herrings = [
            "The building's exterior color is too bold",
            "The parking lot is slightly too small",
            "The landscaping needs more variety"
        ]

        return {
            "mystery_description": detected_problem,
            "clues": clues,
            "red_herrings": red_herrings[:2],  # Add 2 red herrings
            "solution_hint": "Consider how design elements affect user behavior and comfort"
        }

    def generate_perspectives_from_context(self, building_type: str, user_message: str) -> List[str]:
        """Generate contextual perspectives based on user message."""

        # Base perspectives for different building types
        base_perspectives = {
            "community center": ["Community Leader", "Local Resident", "Youth Program Coordinator", "Senior Citizen", "Parent"],
            "library": ["Librarian", "Student", "Researcher", "Parent with Children", "Senior Reader"],
            "school": ["Teacher", "Student", "Principal", "Parent", "Maintenance Staff"],
            "hospital": ["Doctor", "Nurse", "Patient", "Visitor", "Administrator"],
            "museum": ["Curator", "Visitor", "Tour Guide", "Security", "Researcher"]
        }

        # Analyze message for specific perspectives mentioned
        perspective_keywords = {
            "accessibility": "Accessibility Advocate",
            "sustainability": "Environmental Consultant",
            "safety": "Safety Inspector",
            "technology": "IT Specialist",
            "budget": "Financial Planner",
            "maintenance": "Facility Manager",
            "community": "Community Organizer",
            "design": "Design Critic",
            "user": "User Experience Expert",
            "function": "Functional Analyst"
        }

        perspectives = base_perspectives.get(building_type, ["User", "Designer", "Manager", "Visitor", "Expert"])

        # Add contextual perspectives based on message
        for keyword, perspective in perspective_keywords.items():
            if keyword in user_message.lower():
                perspectives.append(perspective)

        return perspectives[:6]  # Limit to 6 perspectives

    def generate_story_chapters_from_context(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate contextual story chapters based on user message and building type."""

        # Analyze message for temporal keywords
        temporal_keywords = {
            "morning": "Early Morning",
            "day": "Midday",
            "evening": "Evening",
            "night": "Night",
            "busy": "Peak Hours",
            "quiet": "Quiet Hours",
            "weekend": "Weekend",
            "weekday": "Weekday"
        }

        # Default chapters
        chapters = {
            "Opening": f"The {building_type} awakens - first users arrive",
            "Activity": f"The {building_type} comes alive with purpose",
            "Peak": f"The {building_type} at its busiest moment",
            "Transition": f"The {building_type} shifts between activities",
            "Closing": f"The {building_type} prepares for rest"
        }

        # Customize based on message context
        if "community" in user_message.lower():
            chapters["Community"] = f"The {building_type} brings people together"
        if "learning" in user_message.lower() or "education" in user_message.lower():
            chapters["Discovery"] = f"Knowledge flows through the {building_type}"
        if "healing" in user_message.lower() or "health" in user_message.lower():
            chapters["Care"] = f"The {building_type} provides comfort and healing"

        return chapters

    def generate_time_periods_from_context(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate contextual time periods based on user message."""

        # Analyze for temporal scope
        if "history" in user_message.lower() or "heritage" in user_message.lower():
            return {
                "Historical": f"This {building_type} in its historical context",
                "Present": f"The {building_type} as it exists today",
                "Legacy": f"The {building_type}'s lasting impact on the community"
            }
        elif "future" in user_message.lower() or "adapt" in user_message.lower():
            return {
                "Current": f"The {building_type} meeting today's needs",
                "Evolving": f"The {building_type} adapting to change",
                "Future": f"The {building_type} transformed for tomorrow"
            }
        else:
            return {
                "Past": f"The {building_type} in earlier times",
                "Present": f"The {building_type} today",
                "Future": f"The {building_type} in years to come"
            }

    def generate_transformations_from_context(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate contextual transformation types based on user message."""

        transformations = {}

        # Analyze message for transformation keywords
        if "flexible" in user_message.lower() or "multi" in user_message.lower():
            transformations["Flexible"] = f"Your {building_type} adapts to multiple uses throughout the day"

        if "season" in user_message.lower() or "weather" in user_message.lower():
            transformations["Seasonal"] = f"Your {building_type} transforms with the changing seasons"

        if "community" in user_message.lower() or "grow" in user_message.lower():
            transformations["Community"] = f"Your {building_type} evolves as the community grows"

        if "technology" in user_message.lower() or "digital" in user_message.lower():
            transformations["Digital"] = f"Your {building_type} integrates new technologies over time"

        # Default transformations if none detected
        if not transformations:
            transformations = {
                "Adaptive": f"Your {building_type} changes based on user needs",
                "Functional": f"Your {building_type} shifts between different uses",
                "Responsive": f"Your {building_type} responds to community feedback",
                "Evolutionary": f"Your {building_type} grows and develops organically"
            }

        return transformations

class EnhancedGamificationRenderer:
    """Enhanced visual gamification with creative interactive elements."""
    
    def __init__(self):
        self.themes = ENHANCED_THEMES
        self.content_generator = FlexibleContentGenerator()

    def _get_personas_for_building(self, building_type: str) -> Dict[str, Dict[str, Any]]:
        """Return personas for a given building type."""
        # Example personas for demonstration
        personas_data = {
            "community center": {
                "Parent": {
                    "description": "A parent seeking a safe, engaging space for their children.",
                    "mission": "Find activities and spaces that foster learning and play.",
                    "insights": ["Parents value safety and visibility.", "Flexible spaces are appreciated."]
                },
                "Teen": {
                    "description": "A teenager looking for a place to hang out and express themselves.",
                    "mission": "Discover creative zones and social areas.",
                    "insights": ["Teens want autonomy and creative outlets.", "Social spaces are important."]
                },
                "Senior": {
                    "description": "An older adult seeking community and accessibility.",
                    "mission": "Locate accessible paths and welcoming gathering spots.",
                    "insights": ["Accessibility is crucial.", "Quiet, comfortable areas are valued."]
                }
            },
            "hospital": {
                "Patient": {
                    "description": "A patient navigating the hospital for treatment.",
                    "mission": "Find clear directions and comfortable waiting areas.",
                    "insights": ["Wayfinding is essential.", "Comfort reduces stress."]
                },
                "Visitor": {
                    "description": "A visitor supporting a loved one.",
                    "mission": "Locate patient rooms and amenities easily.",
                    "insights": ["Clear signage helps visitors.", "Amenities improve experience."]
                },
                "Staff": {
                    "description": "A staff member working long shifts.",
                    "mission": "Access efficient workspaces and rest areas.",
                    "insights": ["Efficiency and rest spaces matter.", "Staff need quick access to resources."]
                }
            }
        }
        return personas_data.get(building_type, personas_data["community center"])
        
    def render_enhanced_challenge(self, challenge_data: Dict[str, Any]) -> None:
        """Render an enhanced visual challenge experience with CONTEXTUAL content generation."""
        challenge_type = challenge_data.get("challenge_type", "alternative_challenge")  # FIXED: Use correct default
        challenge_text = challenge_data.get("challenge_text", "")
        building_type = challenge_data.get("building_type", "community center")

        # Store challenge data in session state for context-aware rendering
        st.session_state['current_challenge_data'] = challenge_data

        # CRITICAL: Get user's original message for contextual content generation
        user_message = challenge_data.get("user_message", "")
        gamification_applied = challenge_data.get("gamification_applied", False)

        print(f"🎮 CONTEXTUAL RENDERING: User message = '{user_message}'")
        print(f"🎮 CONTEXTUAL RENDERING: Challenge type = '{challenge_type}'")
        print(f"🎮 CONTEXTUAL RENDERING: Building type = '{building_type}'")

        # Check for cognitive enhancement patterns in the text
        is_cognitive_enhancement = self._is_cognitive_enhancement_challenge(challenge_text)

        # Map challenge types to enhanced versions
        type_mapping = {
            "perspective_challenge": "role_play",
            "metacognitive_challenge": "detective",
            "constraint_challenge": "constraint",
            "alternative_challenge": "perspective_shift",
            "spatial_storytelling": "storytelling",
            "time_travel_challenge": "time_travel",
            "space_transformation": "transformation",
            "lifecycle_adventure": "time_travel",
            "daily_rhythm_challenge": "time_travel"
        }

        enhanced_type = type_mapping.get(challenge_type, challenge_type)
        if not enhanced_type:  # Only fallback if truly empty/None
            enhanced_type = "constraint"
        theme = self.themes.get(enhanced_type, self.themes["role_play"])

        # Inject enhanced CSS
        self._inject_enhanced_css()

        # If this is a rich cognitive enhancement challenge, render with full content
        if is_cognitive_enhancement and challenge_text:
            self._render_cognitive_enhancement_challenge(challenge_text, enhanced_type, theme, building_type)
        else:
            # Render CONTEXTUAL interactive games using user's actual message
            if enhanced_type == "role_play":
                self._render_enhanced_persona_game(user_message, theme, building_type)
            elif enhanced_type == "perspective_shift":
                self._render_spinning_wheel_game(user_message, theme, building_type)
            elif enhanced_type == "detective":
                self._render_animated_mystery_game(user_message, theme, building_type)
            elif enhanced_type == "constraint":
                self._render_interactive_constraint_game(user_message, theme, building_type)
            elif enhanced_type == "storytelling":
                self._render_storytelling_game(user_message, theme, building_type)
            elif enhanced_type == "time_travel":
                self._render_time_travel_game(user_message, theme, building_type)
            elif enhanced_type == "transformation":
                self._render_transformation_game(user_message, theme, building_type)
    
    def _inject_enhanced_css(self):
        """Inject compact CSS with thesis colors only."""
        st.markdown("""
        <style>
        /* Compact Animations */
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-8px); }
            60% { transform: translateY(-4px); }
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(120, 76, 128, 0.4);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 0 0 15px rgba(120, 76, 128, 0.1);
            }
            100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(120, 76, 128, 0);
            }
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0) rotate(0deg); }
            10% { transform: translateX(-3px) rotate(-1deg); }
            20% { transform: translateX(3px) rotate(1deg); }
            30% { transform: translateX(-3px) rotate(-1deg); }
            40% { transform: translateX(3px) rotate(1deg); }
            50% { transform: translateX(-2px) rotate(-0.5deg); }
            60% { transform: translateX(2px) rotate(0.5deg); }
            70% { transform: translateX(-2px) rotate(-0.5deg); }
            80% { transform: translateX(2px) rotate(0.5deg); }
            90% { transform: translateX(-1px) rotate(-0.5deg); }
        }

        @keyframes rotate {
            0% { transform: rotate(0deg) scale(1); }
            25% { transform: rotate(90deg) scale(1.1); }
            50% { transform: rotate(180deg) scale(1); }
            75% { transform: rotate(270deg) scale(1.1); }
            100% { transform: rotate(360deg) scale(1); }
        }

        @keyframes wheelSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(1800deg); }
        }

        @keyframes cardFlip {
            0% { transform: rotateY(0deg); }
            50% { transform: rotateY(90deg); }
            100% { transform: rotateY(0deg); }
        }

        @keyframes slideInScale {
            0% {
                opacity: 0;
                transform: translateY(30px) scale(0.8);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes glow {
            0% {
                box-shadow: 0 0 15px rgba(79, 58, 62, 0.3), 0 0 30px rgba(79, 58, 62, 0.2);
                transform: scale(1);
            }
            50% {
                box-shadow: 0 0 25px rgba(79, 58, 62, 0.6), 0 0 50px rgba(79, 58, 62, 0.4);
                transform: scale(1.02);
            }
            100% {
                box-shadow: 0 0 15px rgba(79, 58, 62, 0.3), 0 0 30px rgba(79, 58, 62, 0.2);
                transform: scale(1);
            }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(180deg); }
        }

        /* Enhanced Button Styles */
        .stButton > button {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 20px;
            white-space: normal !important;
            height: auto !important;
            min-height: 80px;
            padding: 20px 25px !important;
            text-align: center !important;
            line-height: 1.6 !important;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 3px solid transparent;
            position: relative;
            overflow: hidden;
            font-weight: 600 !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }

        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.6s;
        }

        .stButton > button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            border-color: rgba(79, 58, 62, 0.5);
            background: linear-gradient(135deg, rgba(79, 58, 62, 0.1), rgba(92, 79, 115, 0.1));
        }

        .stButton > button:hover::before {
            left: 100%;
        }

        .stButton > button:active {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        }

        /* Wheel Animation */
        .spinning-wheel {
            animation: wheelSpin 3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        /* Card Flip Animation */
        .card-flip {
            animation: cardFlip 0.6s ease-in-out;
        }

        /* Glowing Elements */
        .glow-effect {
            animation: glow 2s ease-in-out infinite;
        }

        /* Progressive Loading Bar */
        .progress-bar {
            width: 100%;
            height: 15px;
            background: rgba(224, 206, 181, 0.3);
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4f3a3e, #5c4f73, #784c80);
            border-radius: 10px;
            transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 10px rgba(79, 58, 62, 0.3);
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        /* Interactive Cards */
        .interactive-card {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .interactive-card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        }

        .interactive-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.6s;
        }

        .interactive-card:hover::before {
            left: 100%;
        }

        /* Floating Elements */
        .floating-element {
            animation: float 6s ease-in-out infinite;
        }

        /* Text Area Enhancements - Fix double border issue */
        .stTextArea > div > div {
            border-radius: 12px !important;
            border: none !important;
            background: transparent !important;
        }

        .stTextArea > div > div > textarea {
            border-radius: 12px !important;
            border: 2px solid #e0ceb5 !important;
            transition: all 0.3s ease !important;
            font-size: 1.1em !important;
            line-height: 1.6 !important;
            padding: 20px !important;
            background: white !important;
        }

        .stTextArea > div > div > textarea:focus {
            border-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 0 0 0 transparent !important;
            outline: none !important;
        }

        /* Button Hover & Active States - Thesis Purple Theme */
        .stButton > button {
            transition: all 0.3s ease !important;
            border: 1px solid #e0ceb5 !important;
            box-shadow: none !important;
        }

        .stButton > button:hover {
            background-color: #5c4f73 !important;
            border-color: #5c4f73 !important;
            color: white !important;
            transform: translateY(-1px) !important;
            box-shadow: none !important;
        }

        .stButton > button:active, .stButton > button:focus {
            background-color: #5c4f73 !important;
            border-color: #ffffff !important;
            color: white !important;
            transform: translateY(0px) !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Primary Button Styling - Remove dark borders */
        .stButton > button[kind="primary"] {
            background-color: #5c4f73 !important;
            border-color: #fffff !important;
            color: white !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #5c4f73 !important;
            border-color: #5c4f73 !important;
            opacity: 0.9 !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="primary"]:active, .stButton > button[kind="primary"]:focus {
            background-color: #5c4f73 !important;
            border-color: #ffffff !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Secondary Button Styling */
        .stButton > button[kind="secondary"] {
            background-color: transparent !important;
            border-color: #e0ceb5 !important;
            color: #4f3a3e !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="secondary"]:hover {
            background-color: #5c4f73 !important;
            border-color: #5c4f73 !important;
            color: white !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="secondary"]:active, .stButton > button[kind="secondary"]:focus {
            background-color: #5c4f73 !important;
            border-color: #fffff    !important;
            color: white !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Text Input Styling - Fix double border issue */
        .stTextInput > div > div {
            border-radius: 12px !important;
            border: none !important;
            background: transparent !important;
        }

        .stTextInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid #e0ceb5 !important;
            transition: all 0.3s ease !important;
            font-size: 1.1em !important;
            padding: 12px 20px !important;
            background: white !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 0 0 0 transparent !important;
            outline: none !important;
        }

        /* Number Input Styling - Fix double border issue */
        .stNumberInput > div > div {
            border-radius: 12px !important;
            border: none !important;
            background: transparent !important;
        }

        .stNumberInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid #e0ceb5 !important;
            transition: all 0.3s ease !important;
            font-size: 1.1em !important;
            padding: 12px 20px !important;
            background: white !important;
        }

        .stNumberInput > div > div > input:focus {
            border-color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 0 0 0 transparent !important;
            outline: none !important;
        }

        /* Chat Input Area - Fix double border issue */
        .stChatInput > div > div {
            border-radius: 12px !important;
            border: none !important;
            background: transparent !important;
        }

        .stChatInput > div > div > textarea {
            border-radius: 12px !important;
            border: 2px solid #e0ceb5 !important;
            transition: all 0.3s ease !important;
            background: white !important;
        }

        .stChatInput > div > div > textarea:focus {
            border-color: #5fffff !important;
            border-radius: 12px !important;
            box-shadow: 0 0 0 0 transparent !important;
            outline: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

    def _render_enhanced_persona_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact persona game."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Role Play
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic personas based on context
        personas = self.content_generator.generate_personas_from_context(building_type, challenge_text)

        # Initialize persona state
        persona_key = f"persona_{building_type}_{hash(challenge_text)}"
        if persona_key not in st.session_state:
            st.session_state[persona_key] = {
                'selected_persona': None,
                'persona_data': None,
                'response_given': False,
                'persona_points': 0
            }

        persona_state = st.session_state[persona_key]

        # Compact persona selection
        for i, (persona_name, persona_data) in enumerate(personas.items()):
            is_selected = persona_state['selected_persona'] == persona_name

            # Compact persona card with click interaction
            if st.button(
                f"{theme['symbol']} {persona_name}: {persona_data['description'][:60]}...",
                key=f"select_persona_{i}_{hash(challenge_text)}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                persona_state['selected_persona'] = persona_name
                persona_state['persona_data'] = persona_data
                persona_state['response_given'] = False
                st.rerun()


        #ADDED 2008'selected_persona']...` block
        persona_data: dict[str, Any] = {}
        persona_name: str = ""

        
        # Show selected persona experience
        if persona_state['selected_persona'] and persona_state['persona_data']:
            persona_data = persona_state['persona_data']
            persona_name = persona_state['selected_persona']

            # Compact experience section
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} {persona_name}:</strong>
                <span style="color: #2c2328;">{persona_data['mission']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Compact response area
            user_response = st.text_area(
                "Your experience:",
                placeholder=f"As {persona_name}, I feel...",
                height=100,
                key=f"response_{persona_key}",
                help="Describe your thoughts, feelings, and observations from this persona's perspective"
            )

            if st.button(f"{theme['symbol']} Submit Experience", key=f"submit_{persona_key}", type="primary"):
                if user_response.strip():
                    persona_state['response_given'] = True
                    persona_state['persona_points'] += 30

                    # INTEGRATE WITH MENTOR: Send game response back to conversation
                    game_response = f"🎭 Role-Play Experience: {user_response.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()

        # Show insights after submission
        if persona_state.get('response_given', False):
            # Compact insights display
            insights = persona_data.get('insights', ["Great thinking!"])
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div style="
                    background: {theme['accent']};
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    border-left: 3px solid {theme['primary']};
                ">
                    <strong style="color: {theme['primary']};">{theme['symbol']} Insight {i+1}:</strong>
                    <span style="color: #2c2328; line-height: 1.5;">{insight}</span>
                </div>
                """, unsafe_allow_html=True)

            # Show only contextual progress (no success message)
            self._show_contextual_progress("Role Play", persona_state['persona_points'], 30)

    def _render_spinning_wheel_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact perspective wheel game."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Perspective Wheel
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Initialize wheel state
        wheel_key = f"wheel_{building_type}_{hash(challenge_text)}"
        if wheel_key not in st.session_state:
            st.session_state[wheel_key] = {
                'spun_perspective': None,
                'response_given': False,
                'perspective_points': 0,
                'spins_count': 0,
                'is_spinning': False
            }

        wheel_state = st.session_state[wheel_key]

        # Generate dynamic perspectives based on context
        perspective_names = self.content_generator.generate_perspectives_from_context(building_type, challenge_text)

        # Create perspective objects with thesis colors and geometric icons
        icons = ["●", "■", "▲", "◆", "◉", "◈"]
        colors = [theme['primary'], theme['secondary'], theme['accent']]

        perspectives = []
        for i, name in enumerate(perspective_names):
            perspectives.append({
                "name": f"{name}'s View",
                "icon": icons[i % len(icons)],
                "color": colors[i % len(colors)],
                "challenge": f"From a {name.lower()}'s perspective: How does this {building_type} serve their specific needs?"
            })

        # Compact spin button
        if st.button(
            f"{theme['icon']} Spin Perspective Wheel",
            key=f"spin_{wheel_key}",
            type="primary",
            use_container_width=True
        ):
                selected_perspective = random.choice(perspectives)
                wheel_state['spun_perspective'] = selected_perspective
                wheel_state['response_given'] = False
                wheel_state['spins_count'] += 1
                st.rerun()

        # Show spun perspective
        if wheel_state['spun_perspective']:
            perspective = wheel_state['spun_perspective']

            # Compact perspective display
            st.markdown(f"""
            <div style="
                background: {perspective['color']};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
            ">
                <div style="font-size: 1.5em; margin-bottom: 8px; color: white;">{perspective['icon']}</div>
                <h4 style="margin: 8px 0; color: white;">{perspective['name']}</h4>
                <p style="margin: 8px 0; color: white; font-size: 0.9em;">{perspective['challenge']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Compact response area
            response = st.text_area(
                "Your insight:",
                placeholder=f"From this perspective, I see...",
                height=100,
                key=f"perspective_response_{wheel_key}"
            )

            if st.button(f"{theme['symbol']} Submit Perspective", key=f"submit_perspective_{wheel_key}", type="primary"):
                if response.strip():
                    wheel_state['response_given'] = True
                    wheel_state['perspective_points'] += 20

                    # INTEGRATE WITH MENTOR: Send game response back to conversation
                    game_response = f"🎡 Perspective Shift: {response.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()

        # Show progress after submission
        if wheel_state.get('response_given', False):
            # Show only contextual progress (no success message)
            self._show_contextual_progress("Perspective Challenge", wheel_state['perspective_points'], 20)



    def _render_animated_mystery_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact mystery investigation game with user input."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Mystery Investigation
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic mystery based on context
        mystery_data = self.content_generator.generate_mystery_from_context(building_type, challenge_text)

        mystery = {
            "case": mystery_data["mystery_description"],
            "clues": mystery_data["clues"],
            "red_herrings": mystery_data["red_herrings"],
            "solution": mystery_data["solution_hint"]
        }

        # Compact case presentation
        st.markdown(f"""
        <div style="
            background: {theme['accent']};
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid {theme['primary']};
        ">
            <strong style="color: {theme['primary']};">{theme['symbol']} The Mystery:</strong>
            <span style="color: #2c2328;">{mystery['case']}</span>
        </div>
        """, unsafe_allow_html=True)

        # Initialize investigation state
        investigation_key = f"investigation_{building_type}_{hash(mystery['case'])}"
        if investigation_key not in st.session_state:
            st.session_state[investigation_key] = {
                'investigated_clues': [],
                'detective_points': 0,
                'mystery_solved': False
            }

        investigation_state = st.session_state[investigation_key]

        # Compact clue investigation
        all_clues = mystery['clues'] + mystery['red_herrings']

        # Display clues as compact buttons
        for i, clue in enumerate(all_clues):
            is_investigated = clue in investigation_state['investigated_clues']
            is_important = clue in mystery['clues']

            if is_investigated:
                if is_important:
                    button_type = "primary"
                    prefix = f"{theme['symbol']} ◉"
                else:
                    button_type = "secondary"
                    prefix = f"{theme['symbol']} ◯"
            else:
                button_type = "secondary"
                prefix = f"{theme['symbol']}"

            if st.button(f"{prefix} {clue}", key=f"clue_{i}_{investigation_key}", type=button_type, use_container_width=True):
                if is_investigated:
                    # Allow unselecting clues
                    investigation_state['investigated_clues'].remove(clue)
                    if is_important and investigation_state['detective_points'] >= 10:
                        investigation_state['detective_points'] -= 10
                else:
                    # Select new clue
                    investigation_state['investigated_clues'].append(clue)
                    if is_important:
                        investigation_state['detective_points'] += 10
                st.rerun()

        # Add user input for hypothesis
        if len(investigation_state['investigated_clues']) >= 2:
            st.markdown("### Your Investigation")

            hypothesis = st.text_area(
                "What do you think is causing the problem?",
                placeholder="Based on the evidence, I believe the issue is...",
                height=100,
                key=f"hypothesis_{investigation_key}"
            )

            if st.button(f"{theme['symbol']} Submit Solution", key=f"solve_{investigation_key}", type="primary"):
                if hypothesis.strip():
                    investigation_state['mystery_solved'] = True
                    investigation_state['detective_points'] += 20

                    # INTEGRATE WITH MENTOR: Send game response back to conversation
                    game_response = f"🕵️ Investigation Complete: {hypothesis.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()

        # Show solution after mystery is solved
        if investigation_state.get('mystery_solved', False):
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} Solution:</strong>
                <span style="color: #2c2328;">{mystery['solution']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Show only contextual progress (no success message)
            self._show_contextual_progress("Mystery Investigation", investigation_state['detective_points'], 20)






    def _render_interactive_constraint_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact constraint puzzle game."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Constraint Puzzle
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic constraints based on context
        challenge_data = getattr(st.session_state, 'current_challenge_data', {})
        constraints = self.content_generator.generate_constraints_from_context(building_type, challenge_text, challenge_data)

        # Initialize constraint selection
        constraint_key = f"constraints_{building_type}_{hash(challenge_text)}"
        if constraint_key not in st.session_state:
            st.session_state[constraint_key] = {
                'selected_constraints': [],
                'solution': '',
                'points': 0,
                'completed': False
            }

        constraint_state = st.session_state[constraint_key]

        # Compact constraint selection
        for constraint_name, constraint_data in constraints.items():
            is_selected = constraint_name in constraint_state['selected_constraints']

            if st.button(
                f"{constraint_data['icon']} {constraint_name}: {constraint_data['impact']}",
                key=f"constraint_{constraint_name}_{constraint_key}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                if is_selected:
                    constraint_state['selected_constraints'].remove(constraint_name)
                else:
                    if len(constraint_state['selected_constraints']) < 3:
                        constraint_state['selected_constraints'].append(constraint_name)
                st.rerun()

        # Show solution area when constraints are selected
        if constraint_state['selected_constraints']:
            # Compact challenge display
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} Active Constraints:</strong>
                <span style="color: #2c2328;">{', '.join(constraint_state['selected_constraints'])}</span>
            </div>
            """, unsafe_allow_html=True)

            # Compact solution area
            solution = st.text_area(
                "Your creative solution:",
                placeholder="With these constraints, I would...",
                height=120,
                key=f"solution_{constraint_key}"
            )

            if st.button(f"{theme['symbol']} Submit Solution", key=f"submit_{constraint_key}", type="primary"):
                if solution.strip():
                    constraint_state['completed'] = True
                    constraint_state['solution'] = solution
                    constraint_state['points'] += len(constraint_state['selected_constraints']) * 15

                    # INTEGRATE WITH MENTOR: Send game response back to conversation
                    game_response = f"🎯 Constraint Solution: {solution.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()

        # Show progress after completion
        if constraint_state.get('completed', False):
            # Show only contextual progress (no success message)
            self._show_contextual_progress("Constraint Challenge", constraint_state['points'], 15)

    def _render_cognitive_enhancement_challenge(self, challenge_text: str, challenge_type: str, theme: Dict, building_type: str) -> None:
        """Render rich cognitive enhancement challenges with enhanced visuals."""
        # Parse the challenge text to extract components
        challenge_parts = self._parse_cognitive_challenge_text(challenge_text)

        # Render enhanced header based on challenge type
        self._render_enhanced_challenge_header(challenge_parts, challenge_type, theme)

        # Render main challenge content with rich formatting
        self._render_enhanced_challenge_content(challenge_parts, theme)

        # Add interactive response area
        self._render_enhanced_response_area(challenge_parts, challenge_type, theme, building_type)

    def _parse_cognitive_challenge_text(self, challenge_text: str) -> Dict[str, str]:
        """Parse cognitive enhancement challenge text into components."""
        parts = {
            "title": "",
            "subtitle": "",
            "main_content": challenge_text,
            "question": ""
        }

        lines = challenge_text.split('\n')

        # Extract title (lines with emojis and caps)
        for line in lines:
            line = line.strip()
            if line and ('🎭' in line or '🎯' in line or '🔍' in line or '🏗️' in line or '🎨' in line):
                if line.isupper() or ':' in line:
                    parts["title"] = line
                    break

        # Extract subtitle (lines in italics)
        for line in lines:
            line = line.strip()
            if line.startswith('*') and line.endswith('*'):
                parts["subtitle"] = line.strip('*')
                break

        # Extract question (lines ending with ?)
        for line in reversed(lines):
            line = line.strip()
            if line.endswith('?'):
                parts["question"] = line
                break

        # Clean main content
        content_lines = []
        skip_patterns = [parts["title"], f"*{parts['subtitle']}*", parts["question"]]

        for line in lines:
            line = line.strip()
            if line and not any(pattern in line for pattern in skip_patterns if pattern):
                content_lines.append(line)

        parts["main_content"] = '\n'.join(content_lines)

        return parts

    def _is_cognitive_enhancement_challenge(self, challenge_text: str) -> bool:
        """Detect if this is a rich cognitive enhancement challenge vs basic interactive game."""
        if not challenge_text:
            return False

        # Look for cognitive enhancement patterns
        cognitive_patterns = [
            "🎨 SPATIAL STORYTELLING",
            "DESIGN CHALLENGE:",
            "*Your building",
            "Phase Transition",
            "materialization phase",
            "Reflect on how",
            "Consider the spatial",
            "Think about how",
            "As you evaluate",
            "What story does"
        ]

        # Check if the text contains rich cognitive enhancement content
        text_lower = challenge_text.lower()
        has_cognitive_patterns = any(pattern.lower() in text_lower for pattern in cognitive_patterns)

        # Check for multi-line structured content (cognitive enhancement is usually longer and structured)
        lines = [line.strip() for line in challenge_text.split('\n') if line.strip()]
        has_structured_content = len(lines) > 3

        # Check for italicized content (cognitive enhancement uses *text* format)
        has_italics = '*' in challenge_text and challenge_text.count('*') >= 2

        return has_cognitive_patterns or (has_structured_content and has_italics)

    def _render_enhanced_challenge_header(self, challenge_parts: Dict, challenge_type: str, theme: Dict) -> None:
        """Render enhanced challenge header with rich styling."""
        title = challenge_parts.get("title", f"{theme['icon']} Challenge")
        subtitle = challenge_parts.get("subtitle", "")

        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        ">
            <div style="
                width: 80px;
                height: 80px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                font-size: 2.5em;
                color: {theme['primary']};
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            ">
                {theme['icon']}
            </div>
            <h2 style="
                color: white;
                margin: 0 0 10px 0;
                font-weight: 300;
                font-size: 1.8em;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">
                {title}
            </h2>
            {f'<p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 1.1em; font-style: italic;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)

    def _render_enhanced_challenge_content(self, challenge_parts: Dict, theme: Dict) -> None:
        """Render main challenge content with enhanced formatting."""
        main_content = challenge_parts.get("main_content", "")

        if main_content:
            st.markdown(f"""
            <div style="
                background: white;
                border-left: 5px solid {theme['primary']};
                padding: 25px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            ">
                <div style="
                    color: #2c2328;
                    font-size: 1.1em;
                    line-height: 1.7;
                ">
                    {main_content.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    def _render_enhanced_response_area(self, challenge_parts: Dict, challenge_type: str, theme: Dict, building_type: str) -> None:
        """Render interactive response area for cognitive challenges."""
        question = challenge_parts.get("question", "What are your thoughts on this challenge?")

        # Create unique key for this challenge
        challenge_key = f"cognitive_challenge_{challenge_type}_{hash(question) % 10000}"

        # Initialize session state
        if challenge_key not in st.session_state:
            st.session_state[challenge_key] = {
                'response': '',
                'submitted': False,
                'points': 0
            }

        challenge_state = st.session_state[challenge_key]

        # Question display
        st.markdown(f"""
        <div style="
            background: {theme['accent']};
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 4px solid {theme['primary']};
        ">
            <strong style="color: {theme['primary']}; font-size: 1.1em;">
                {theme['symbol']} Reflection Question:
            </strong>
            <p style="color: #2c2328; margin: 10px 0 0 0; font-size: 1.05em;">
                {question}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Response input
        if not challenge_state['submitted']:
            response = st.text_area(
                "Your thoughtful response:",
                placeholder="Share your insights and reflections...",
                height=150,
                key=f"response_{challenge_key}"
            )

            if st.button(f"{theme['symbol']} Submit Reflection", key=f"submit_{challenge_key}", type="primary"):
                if response.strip():
                    challenge_state['response'] = response
                    challenge_state['submitted'] = True
                    challenge_state['points'] = 25

                    # INTEGRATE WITH MENTOR: Send game response back to conversation
                    game_response = f"📚 Storytelling Reflection: {response.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()
        else:
            # Show submitted response
            st.success("Challenge completed! Your reflection has been recorded.")
            self._show_contextual_progress("Cognitive Challenge", challenge_state['points'], 25)

    def _show_contextual_progress(self, challenge_name: str, points: int, max_points: int) -> None:
        """Show contextual progress for completed challenges with thesis colors."""
        progress_percentage = (points / max_points) * 100 if max_points > 0 else 0

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4f3a3e 0%, #5c4f73 100%);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #d99c66;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: white;
            ">
                <span style="font-weight: 500;">◉ {challenge_name} Complete</span>
                <span style="
                    background: #d99c66;
                    color: #4f3a3e;
                    padding: 4px 12px;
                    border-radius: 15px;
                    font-size: 0.9em;
                    font-weight: 600;
                ">
                    +{points} points
                </span>
            </div>
            <div style="
                background: rgba(224, 206, 181, 0.3);
                border-radius: 10px;
                height: 6px;
                margin-top: 8px;
                overflow: hidden;
            ">
                <div style="
                    background: #d99c66;
                    height: 100%;
                    width: {progress_percentage}%;
                    border-radius: 10px;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_storytelling_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render interactive storytelling challenge."""
        story_state = st.session_state.get('storytelling_state', {
            'chapter': 1,
            'story_points': 0,
            'narrative_choices': []
        })

        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid {theme['primary']};
            color: white;
        ">
            <h3 style="margin: 0 0 15px 0; color: white;">
                {theme['icon']} Storytelling Challenge
            </h3>
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            ">
                {challenge_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic story chapters based on context
        story_chapters_dict = self.content_generator.generate_story_chapters_from_context(building_type, challenge_text)
        story_chapters = list(story_chapters_dict.values())

        current_chapter = story_chapters[min(story_state['chapter'] - 1, len(story_chapters) - 1)]

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            font-style: italic;
        ">
            {current_chapter}
        </div>
        """, unsafe_allow_html=True)

        # Story response
        story_response = st.text_area(
            "Continue the story - what happens next?",
            key="storytelling_response",
            height=100
        )

        if st.button(f"{theme['symbol']} Continue Story", key="continue_story", use_container_width=True):
            if story_response:
                story_state['chapter'] += 1
                story_state['story_points'] += 10
                story_state['narrative_choices'].append(story_response)
                st.session_state['storytelling_state'] = story_state
                st.success("Story continues! Your narrative has been recorded.")
                self._show_contextual_progress("Storytelling Challenge", story_state['story_points'], 40)

    def _render_time_travel_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render interactive time travel challenge."""
        time_state = st.session_state.get('time_travel_state', {
            'current_era': 'present',
            'time_points': 0,
            'temporal_insights': []
        })

        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid {theme['primary']};
            color: white;
        ">
            <h3 style="margin: 0 0 15px 0; color: white;">
                {theme['icon']} Time Travel Challenge
            </h3>
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            ">
                {challenge_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic time periods based on context
        time_periods = self.content_generator.generate_time_periods_from_context(building_type, challenge_text)

        # Dynamic time period selector
        period_keys = list(time_periods.keys())

        for period_key in time_periods.keys():
            if st.button(f"{theme['symbol']} {period_key}", key=f"time_{period_key}", use_container_width=True):
                time_state['current_era'] = period_key
                st.session_state['time_travel_state'] = time_state

        # Show current time period
        current_era = time_state.get('current_era', period_keys[0] if period_keys else 'present')
        current_description = time_periods.get(current_era, f"Your {building_type} in the current time")
        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            font-style: italic;
        ">
            {current_description}
        </div>
        """, unsafe_allow_html=True)

        # Temporal insight
        temporal_response = st.text_area(
            f"What do you observe in the {time_state['current_era']}? How does time affect your design?",
            key="temporal_response",
            height=100
        )

        if st.button(f"{theme['symbol']} Record Temporal Insight", key="record_temporal", use_container_width=True):
            if temporal_response:
                time_state['time_points'] += 15
                time_state['temporal_insights'].append({
                    'era': time_state['current_era'],
                    'insight': temporal_response
                })
                st.session_state['time_travel_state'] = time_state
                st.success("Temporal insight recorded! Time reveals new perspectives.")
                self._show_contextual_progress("Time Travel Challenge", time_state['time_points'], 45)

    def _render_transformation_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render interactive transformation challenge."""
        transform_state = st.session_state.get('transformation_state', {
            'transformation_type': None,
            'transform_points': 0,
            'transformations': []
        })

        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid {theme['primary']};
            color: white;
        ">
            <h3 style="margin: 0 0 15px 0; color: white;">
                {theme['icon']} Transformation Challenge
            </h3>
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            ">
                {challenge_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic transformations based on context
        transformations_dict = self.content_generator.generate_transformations_from_context(building_type, challenge_text)

        # Format for display with theme symbols
        transformations = {}
        for key, description in transformations_dict.items():
            transformations[key.lower().replace(' ', '_')] = f"{theme['symbol']} {key}: {description}"

        # Transformation selector
        st.markdown("**Choose your transformation type:**")

        for key, description in transformations.items():
            if st.button(description, key=f"transform_{key}", use_container_width=True):
                transform_state['transformation_type'] = key
                st.session_state['transformation_state'] = transform_state

        # Show selected transformation
        if transform_state['transformation_type']:
            selected = transformations.get(transform_state['transformation_type'], "Transformation selected")
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border-left: 3px solid {theme['accent']};
            ">
                <strong>Selected:</strong> {selected}
            </div>
            """, unsafe_allow_html=True)

            # Transformation description
            transform_response = st.text_area(
                "Describe how your space transforms. What changes and why?",
                key="transformation_response",
                height=100
            )

            if st.button(f"{theme['symbol']} Apply Transformation", key="apply_transform", use_container_width=True):
                if transform_response:
                    transform_state['transform_points'] += 20
                    transform_state['transformations'].append({
                        'type': transform_state['transformation_type'],
                        'description': transform_response
                    })
                    st.session_state['transformation_state'] = transform_state
                    st.success("Transformation applied! Your space has evolved.")
                    self._show_contextual_progress("Transformation Challenge", transform_state['transform_points'], 60)


# Global functions for integration
def render_enhanced_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Main entry point for rendering enhanced gamified challenges."""
    try:
        print(f"🎮 ENHANCED GAMIFICATION: Starting render with data: {list(challenge_data.keys())}")

        # Validate essential data
        if not challenge_data:
            print("🎮 ENHANCED GAMIFICATION: No challenge data provided")
            st.info("💭 Continue exploring your design ideas!")
            return

        # Ensure required fields exist with safe defaults
        safe_challenge_data = {
            "challenge_text": challenge_data.get("challenge_text", "Let's explore your design challenge!"),
            "challenge_type": challenge_data.get("challenge_type", "constraint_challenge"),  # FIXED: Use correct default
            "building_type": challenge_data.get("building_type", "community center"),
            "user_message": challenge_data.get("user_message", ""),
            "gamification_applied": challenge_data.get("gamification_applied", True),
            **challenge_data  # Include any additional data
        }

        # Initialize renderer
        renderer = EnhancedGamificationRenderer()

        # Render the challenge
        renderer.render_enhanced_challenge(safe_challenge_data)

        print(f"🎮 ENHANCED GAMIFICATION: Render completed successfully")

    except Exception as e:
        print(f"🎮 ENHANCED GAMIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Fallback to simple display
        try:
            st.error("⚠️ Enhanced gamification temporarily unavailable")
            challenge_text = challenge_data.get('challenge_text', 'Continue exploring your design ideas!')
            st.markdown(f"**Challenge:** {challenge_text}")
            st.markdown("💬 Continue the conversation by sharing your thoughts, questions, or insights.")
        except Exception as fallback_error:
            print(f"🎮 ENHANCED GAMIFICATION FALLBACK ERROR: {fallback_error}")
            st.info("💭 Continue with your design exploration!")


def inject_gamification_css() -> None:
    """Inject CSS for enhanced gamification animations."""
    # This is handled by _inject_enhanced_css in the renderer
    pass