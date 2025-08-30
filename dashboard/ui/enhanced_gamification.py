"""
Enhanced Visual Gamification System
Creates engaging, interactive, visual game experiences with improved UI elements.
Maintains Streamlit compatibility while adding creative visual enhancements.
"""

import streamlit as st
import random
from typing import Dict, List, Any, Optional
import json
import time
import re
import openai
import os

# Load environment variables from .env file
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except ImportError:
#     # Manual .env loading if python-dotenv not available
#     env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
#     if os.path.exists(env_path):
#         with open(env_path, 'r') as f:
#             for line in f:
#                 if '=' in line and not line.startswith('#'):
#                     key, value = line.strip().split('=', 1)
#                     os.environ[key] = value.strip('"')

class RobustJSONParser:
    """
    Comprehensive JSON parsing utility for AI-generated content.
    Handles all common JSON parsing failures with intelligent recovery strategies.
    """

    @staticmethod
    def parse_ai_json(json_string: str, expected_type: str = "dict", data_type: str = "data") -> Any:
        """
        FIXED: More conservative JSON parsing that preserves rich AI content.
        Only falls back to regex extraction when absolutely necessary.

        Args:
            json_string: Raw AI response containing JSON
            expected_type: "dict", "list", or "auto"
            data_type: Description for error messages

        Returns:
            Parsed JSON data or None if parsing fails (let caller handle fallback)
        """
        if not json_string or not json_string.strip():
            print(f"⚠️ Empty {data_type} response from AI")
            return None

        # Step 1: Clean the JSON string
        cleaned_json = RobustJSONParser._clean_json_string(json_string)

        # Step 2: Try standard JSON parsing
        try:
            result = json.loads(cleaned_json)

            # Validate result type and content
            if RobustJSONParser._validate_result(result, expected_type, data_type):
                return result

        except json.JSONDecodeError as e:
            print(f"⚠️ {data_type} JSON parsing failed: {e}")
            # Don't print raw response to reduce noise

        # Step 3: Apply ONLY the most conservative repair strategies
        repaired_result = RobustJSONParser._conservative_repair_and_parse(cleaned_json, expected_type, data_type)
        if repaired_result is not None:
            return repaired_result

        # Step 4: REMOVED aggressive regex extraction - let caller handle fallback
        # This preserves the rich AI content instead of extracting shallow descriptions

        # Step 5: Return None to let caller use contextual fallbacks
        print(f"⚠️ {data_type} JSON parsing failed, caller should use contextual fallback")
        return None

    @staticmethod
    def _clean_json_string(json_string: str) -> str:
        """Clean and prepare JSON string for parsing."""
        # Remove markdown code blocks
        if "```json" in json_string:
            json_string = json_string.split("```json")[1].split("```")[0].strip()
        elif "```" in json_string:
            json_string = json_string.split("```")[1].strip()

        # Remove common prefixes/suffixes
        json_string = json_string.strip()

        # Remove trailing commas before closing braces/brackets
        json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)

        return json_string

    @staticmethod
    def _validate_result(result: Any, expected_type: str, data_type: str) -> bool:
        """Validate parsed JSON result."""
        if result is None:
            return False

        if expected_type == "dict":
            return isinstance(result, dict) and len(result) > 0
        elif expected_type == "list":
            return isinstance(result, list) and len(result) > 0
        else:  # auto
            return (isinstance(result, (dict, list)) and
                   len(result) > 0)

    @staticmethod
    def _conservative_repair_and_parse(json_string: str, expected_type: str, data_type: str) -> Any:
        """Apply ONLY conservative repair strategies that preserve rich content."""
        # Only try the most basic fixes that don't risk losing content
        try:
            # Fix 1: Add missing closing braces/brackets
            repaired = RobustJSONParser._fix_incomplete_structures(json_string, expected_type)
            if repaired != json_string:  # Only if we actually changed something
                result = json.loads(repaired)
                if RobustJSONParser._validate_result(result, expected_type, data_type):
                    print(f"✅ {data_type} repaired by adding missing closing structure")
                    return result
        except Exception:
            pass

        # Fix 2: Remove trailing commas (very safe)
        try:
            repaired = re.sub(r',(\s*[}\]])', r'\1', json_string)
            if repaired != json_string:
                result = json.loads(repaired)
                if RobustJSONParser._validate_result(result, expected_type, data_type):
                    print(f"✅ {data_type} repaired by removing trailing commas")
                    return result
        except Exception:
            pass

        return None

    @staticmethod
    def _repair_and_parse(json_string: str, expected_type: str, data_type: str) -> Any:
        """Apply intelligent repair strategies to fix common JSON issues."""
        repair_strategies = [
            RobustJSONParser._fix_unterminated_strings,
            RobustJSONParser._fix_unescaped_quotes,
            RobustJSONParser._fix_incomplete_structures,
            RobustJSONParser._fix_control_characters
        ]

        for strategy in repair_strategies:
            try:
                repaired = strategy(json_string, expected_type)
                if repaired:
                    result = json.loads(repaired)
                    if RobustJSONParser._validate_result(result, expected_type, data_type):
                        print(f"✅ {data_type} repaired using {strategy.__name__}")
                        return result
            except Exception:
                continue

        return None

    @staticmethod
    def _fix_unterminated_strings(json_string: str, expected_type: str) -> str:
        """Fix unterminated strings by adding missing quotes."""
        lines = json_string.split('\n')
        fixed_lines = []

        for line in lines:
            # Count quotes in line
            quote_count = line.count('"')

            # If odd number of quotes and line contains a colon, likely unterminated string
            if quote_count % 2 != 0 and ':' in line:
                # Add closing quote before comma or closing brace
                line = re.sub(r'([^"]*?)(\s*[,}]|$)', r'\1"\2', line)

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    @staticmethod
    def _fix_unescaped_quotes(json_string: str, expected_type: str) -> str:
        """Fix unescaped quotes within string values."""
        # Escape quotes that are inside string values
        return re.sub(r'(?<=: ")(.*?)(?=")', lambda m: m.group(1).replace('"', '\\"'), json_string)

    @staticmethod
    def _fix_incomplete_structures(json_string: str, expected_type: str) -> str:
        """Fix incomplete JSON structures."""
        json_string = json_string.strip()

        if expected_type == "dict" or (expected_type == "auto" and json_string.startswith('{')):
            if not json_string.endswith('}'):
                # Remove trailing comma and add closing brace
                json_string = json_string.rstrip(',\n ') + '\n}'
        elif expected_type == "list" or (expected_type == "auto" and json_string.startswith('[')):
            if not json_string.endswith(']'):
                # Remove trailing comma and add closing bracket
                json_string = json_string.rstrip(',\n ') + '\n]'

        return json_string

    @staticmethod
    def _fix_control_characters(json_string: str, expected_type: str) -> str:
        """Remove or fix control characters that break JSON parsing."""
        # Remove control characters except newlines and tabs
        json_string = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_string)
        return json_string

    @staticmethod
    def _extract_with_regex(json_string: str, expected_type: str, data_type: str) -> Any:
        """Extract content using regex patterns as last resort."""
        if expected_type == "dict" or expected_type == "auto":
            return RobustJSONParser._extract_dict_with_regex(json_string, data_type)
        elif expected_type == "list":
            return RobustJSONParser._extract_list_with_regex(json_string, data_type)
        return None

    @staticmethod
    def _extract_dict_with_regex(json_string: str, data_type: str) -> Dict[str, Any]:
        """Extract dictionary content using regex patterns."""
        result = {}

        # Pattern 1: Complete key-value pairs
        complete_pattern = r'"([^"]+)":\s*"([^"]*)"'
        complete_matches = re.findall(complete_pattern, json_string)

        # Pattern 2: Unterminated strings
        unterminated_pattern = r'"([^"]+)":\s*"([^"]*?)(?=\s*[,}\n]|$)'
        unterminated_matches = re.findall(unterminated_pattern, json_string)

        # Pattern 3: Array values
        array_pattern = r'"([^"]+)":\s*\[(.*?)\]'
        array_matches = re.findall(array_pattern, json_string)

        # Combine all matches
        all_matches = complete_matches + unterminated_matches

        for key, value in all_matches:
            if key and len(value.strip()) > 0:
                result[key.strip()] = value.strip()

        # Handle array matches
        for key, array_content in array_matches:
            if key and array_content:
                # Extract array items
                items = re.findall(r'"([^"]*)"', array_content)
                if items:
                    result[key.strip()] = items

        if result:
            print(f"✅ {data_type} extracted using regex patterns ({len(result)} items)")

        return result

    @staticmethod
    def _extract_list_with_regex(json_string: str, data_type: str) -> List[str]:
        """Extract list content using regex patterns."""
        # Extract quoted strings from array-like structure
        items = re.findall(r'"([^"]*)"', json_string)

        # Filter out empty items and keys (items with colons)
        filtered_items = [item.strip() for item in items if item.strip() and ':' not in item]

        if filtered_items:
            print(f"✅ {data_type} extracted using regex patterns ({len(filtered_items)} items)")

        return filtered_items

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
        # Initialize safe JSON parser
        self._safe_json_parse = self._create_safe_json_parser()

        # Initialize templates
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

    def _create_safe_json_parser(self):
        """Create a safe JSON parser method."""
        def safe_parse(json_string: str, fallback_data: Any = None, data_type: str = "data") -> Any:
            try:
                # Clean the JSON string
                json_string = json_string.strip()

                # Remove markdown code blocks if present
                if "```json" in json_string:
                    json_string = json_string.split("```json")[1].split("```")[0].strip()
                elif "```" in json_string:
                    json_string = json_string.split("```")[1].strip()

                # Parse JSON
                result = json.loads(json_string)

                # Validate result is not None or empty
                if result is None:
                    raise ValueError(f"{data_type} is None")

                if isinstance(result, dict) and len(result) == 0:
                    raise ValueError(f"{data_type} dictionary is empty")

                if isinstance(result, list) and len(result) == 0:
                    raise ValueError(f"{data_type} list is empty")

                return result

            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"⚠️ {data_type} JSON parsing failed: {e}")
                print(f"Raw response: {json_string[:200]}...")

                if fallback_data is not None:
                    print(f"Using fallback {data_type}")
                    return fallback_data

                # Return safe defaults
                if data_type.lower() in ["personas", "constraints", "transformations"]:
                    return {}
                elif data_type.lower() in ["perspectives", "chapters"]:
                    return []
                else:
                    return None

        return safe_parse

    def generate_personas_from_context(self, building_type: str, user_message: str) -> Dict[str, Dict[str, Any]]:
        """Generate contextual personas using AI for flexible content generation."""
        # CONVERSATION-AWARE CACHING: Include conversation context for better games
        conversation_context = getattr(st.session_state, 'messages', [])[-3:]  # Last 3 messages for context
        context_hash = hash(str(conversation_context) + user_message[:50])  # Include conversation in cache key
        cache_key = f"personas_{building_type}_{context_hash}"

        if hasattr(st.session_state, 'game_cache') and cache_key in st.session_state.game_cache:
            # Reduced caching - only use cache if exact same conversation context
            return st.session_state.game_cache[cache_key]

        # FLEXIBLE AI-POWERED: Generate contextual personas for ANY topic
        try:
            result = self._generate_ai_contextual_personas(building_type, user_message)
            # Cache the result
            if not hasattr(st.session_state, 'game_cache'):
                st.session_state.game_cache = {}
            st.session_state.game_cache[cache_key] = result
            return result
        except Exception as e:
            print(f"⚠️ AI persona generation failed: {e}")
            # Fallback to basic personas
            return self._generate_fallback_personas(building_type, user_message)

    def _generate_ai_contextual_personas(self, building_type: str, user_message: str) -> Dict[str, Dict[str, Any]]:
        """Generate contextual personas using AI for any architectural topic"""
        import openai
        client = openai.OpenAI()

        # Escape quotes in user message to prevent string formatting issues
        safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
        safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

        persona_prompt = f"""
        Generate 3-4 diverse user personas for an architecture student working on a {safe_building_type} project.

        User's question/context: "{safe_user_message}"
        Building type: "{safe_building_type}"

        Create personas that:
        1. Relate specifically to the user's question/topic
        2. Represent diverse users of the {building_type}
        3. Have different needs, perspectives, and experiences
        4. Are realistic and specific (not generic)
        5. Help the student think about user-centered design

        Return as JSON with this exact format:
        {{
            "persona1_name": {{
                "description": "Brief description of who they are",
                "mission": "What they want to achieve in this space and how it relates to the topic",
                "insights": ["Insight 1 about their experience", "Insight 2 about design implications"]
            }},
            "persona2_name": {{
                "description": "Brief description",
                "mission": "Their goals and needs",
                "insights": ["Insight 1", "Insight 2"]
            }}
        }}

        Make persona names specific and relatable (not generic like "User 1").
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": persona_prompt}],
            max_tokens=800,  # INCREASED: Prevent JSON truncation
            temperature=0.5  # REDUCED: More consistent JSON formatting
        )

        # ENHANCED: Use robust JSON parser
        content = response.choices[0].message.content
        if content is None:
            print("⚠️ AI response content is None, using fallback personas")
            return self._generate_fallback_personas(building_type, user_message)

        # FIXED: Try conservative JSON parsing first, preserve rich AI content
        parsed_personas = RobustJSONParser.parse_ai_json(content, "dict", "personas")

        # If parsing failed, use contextual fallback
        if parsed_personas is None:
            print("⚠️ Using contextual persona fallback to preserve rich content")
            return self._generate_fallback_personas(building_type, user_message)

        # Validate and fix persona structure
        for persona_name, persona_data in parsed_personas.items():
            if not isinstance(persona_data, dict):
                parsed_personas[persona_name] = {"description": str(persona_data)}
                persona_data = parsed_personas[persona_name]

            # Ensure required fields exist
            if 'mission' not in persona_data:
                persona_data['mission'] = f"Experience the {building_type} from this perspective"
            if 'description' not in persona_data:
                persona_data['description'] = f"A user of the {building_type}"
            if 'insights' not in persona_data:
                persona_data['insights'] = ["Consider this perspective", "Think about user needs"]

        return parsed_personas



    def _generate_fallback_personas(self, building_type: str, user_message: str) -> Dict[str, Dict[str, Any]]:
        """ENHANCED: Generate contextually relevant fallback personas based on user's message"""

        user_lower = user_message.lower()

        # Context-aware persona generation based on user's topic
        if 'elder' in user_lower or 'elderly' in user_lower or 'senior' in user_lower:
            return {
                "Elderly Visitor": {
                    "description": f"A senior citizen who uses the {building_type} regularly for social activities and services",
                    "mission": f"Access services comfortably and maintain social connections in the {building_type}",
                    "insights": ["May have mobility considerations", "Values familiar, accessible spaces", "Appreciates clear signage and seating"]
                },
                "Adult Child": {
                    "description": f"Someone accompanying an elderly parent to the {building_type}",
                    "mission": f"Help their parent navigate and feel comfortable in the {building_type}",
                    "insights": ["Concerned about accessibility", "Wants efficient, stress-free visits", "Notices safety and comfort details"]
                },
                "Staff Member": {
                    "description": f"Someone who works at the {building_type} and regularly assists elderly visitors",
                    "mission": f"Provide excellent service while managing operational efficiency",
                    "insights": ["Understands elderly visitors' needs", "Knows common accessibility challenges", "Balances assistance with independence"]
                }
            }

        elif 'workshop' in user_lower or 'market' in user_lower or 'hub' in user_lower:
            return {
                "Workshop Participant": {
                    "description": f"Someone who regularly attends workshops and classes at the {building_type}",
                    "mission": f"Learn new skills and connect with others through {building_type} programs",
                    "insights": ["Values hands-on learning spaces", "Needs storage for materials", "Appreciates flexible room layouts"]
                },
                "Market Visitor": {
                    "description": f"Someone who comes to shop and browse at the {building_type} market spaces",
                    "mission": f"Find quality products and enjoy the market atmosphere",
                    "insights": ["Wants easy circulation between vendors", "Needs places to rest and eat", "Values vibrant, welcoming atmosphere"]
                },
                "Community Organizer": {
                    "description": f"Someone who helps coordinate activities and events at the {building_type}",
                    "mission": f"Create successful programs that bring the community together",
                    "insights": ["Understands space flexibility needs", "Knows how different activities interact", "Sees the big picture of community use"]
                }
            }

        elif 'journey' in user_lower or 'flow' in user_lower or 'circulation' in user_lower:
            return {
                "First-time Visitor": {
                    "description": f"Someone experiencing the {building_type} for the first time",
                    "mission": f"Navigate confidently and understand how to use the space",
                    "insights": ["Relies on intuitive wayfinding", "Forms first impressions quickly", "Needs clear spatial hierarchy"]
                },
                "Regular User": {
                    "description": f"Someone who knows the {building_type} well and uses it efficiently",
                    "mission": f"Move through the space quickly to accomplish their goals",
                    "insights": ["Has established movement patterns", "Notices when circulation changes", "Values predictable layouts"]
                },
                "Accessibility User": {
                    "description": f"Someone who uses mobility aids or has accessibility needs",
                    "mission": f"Navigate the {building_type} safely and independently",
                    "insights": ["Needs clear, wide pathways", "Values accessible routes", "Notices barriers others might miss"]
                }
            }

        else:
            # Generic but still contextual fallback
            return {
                "Regular User": {
                    "description": f"Someone who frequently uses the {building_type} for various activities",
                    "mission": f"Make the most of what the {building_type} offers",
                    "insights": ["Familiar with the space", "Has established routines", "Knows what works and what doesn't"]
                },
                "First-time Visitor": {
                    "description": f"Someone discovering the {building_type} for the first time",
                    "mission": f"Understand the space and find what they need",
                    "insights": ["Needs clear orientation", "Forms lasting first impressions", "May feel uncertain about unwritten rules"]
                },
                "Community Member": {
                    "description": f"Someone who sees the {building_type} as part of their neighborhood identity",
                    "mission": f"Use and support the {building_type} as a community asset",
                    "insights": ["Cares about the space's role in the community", "Notices how design affects social interaction", "Values inclusive, welcoming environments"]
                }
            }

    def generate_constraints_from_context(self, building_type: str, user_message: str, challenge_data: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """Generate highly contextual constraints using AI for flexible content generation."""
        # CONVERSATION-AWARE CACHING: Include conversation context for better games
        conversation_context = getattr(st.session_state, 'messages', [])[-3:]  # Last 3 messages for context
        context_hash = hash(str(conversation_context) + user_message[:50])
        cache_key = f"constraints_{building_type}_{context_hash}"

        if hasattr(st.session_state, 'game_cache') and cache_key in st.session_state.game_cache:
            return st.session_state.game_cache[cache_key]

        # FLEXIBLE AI-POWERED: Generate contextual constraints for ANY topic
        try:
            result = self._generate_ai_contextual_constraints(building_type, user_message, challenge_data)
            # Cache the result
            if not hasattr(st.session_state, 'game_cache'):
                st.session_state.game_cache = {}
            st.session_state.game_cache[cache_key] = result
            return result
        except Exception as e:
            print(f"⚠️ AI constraint generation failed: {e}")
            # Fallback to basic constraints
            return self._generate_fallback_constraints(building_type, user_message)

    def _generate_ai_contextual_constraints(self, building_type: str, user_message: str, challenge_data: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """Generate contextual constraints using AI for any architectural topic"""
        # PERFORMANCE: Skip AI if no API key available
        import os
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️ No OpenAI API key - using fallback constraints")
            return self._generate_fallback_constraints(building_type, user_message)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Escape quotes in user message to prevent string formatting issues
            safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
            safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

            constraint_prompt = f"""
            Generate 3-4 realistic design constraints for an architecture student working on a {safe_building_type} project.

            User's question/context: "{safe_user_message}"
            Building type: "{safe_building_type}"

            Create constraints that:
            1. Relate specifically to the user's question/topic
            2. Are realistic challenges architects face
            3. Force creative problem-solving
            4. Are specific to the building type and context
            5. Have clear impacts on design decisions

            IMPORTANT: Make the "impact" descriptions rich and detailed (100-200 characters).
            Explain HOW the constraint affects the design, not just WHAT the constraint is.

            Return as JSON with this exact format:
            {{
                "constraint1_name": {{
                    "impact": "Rich, detailed description of how this constraint affects the design, including specific implications for spatial organization, user experience, and architectural decisions (100-200 characters)",
                    "challenge": "Thoughtful question that challenges the student to solve it creatively",
                    "color": "#cd766d",
                    "icon": "◐"
                }},
                "constraint2_name": {{
                    "impact": "Another rich, detailed description explaining the specific design implications and challenges this constraint creates (100-200 characters)",
                    "challenge": "Another challenging question that requires creative problem-solving",
                    "color": "#d99c66",
                    "icon": "◐"
                }}
            }}

            Make each constraint specific to the user's context and building type. Avoid generic constraints.

            Make constraint names specific and relevant (not generic like "Budget" or "Site").
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": constraint_prompt}],
                max_tokens=800,  # INCREASED: Prevent JSON truncation
                temperature=0.5,  # REDUCED: More consistent JSON formatting
                timeout=10  # PERFORMANCE: Add timeout to prevent hanging
            )

            # ENHANCED: Use robust JSON parser
            constraints_json = response.choices[0].message.content
            if not constraints_json:
                print("⚠️ Empty constraints response from AI")
                return self._generate_fallback_constraints(building_type, user_message)

            # FIXED: Try conservative JSON parsing first, preserve rich AI content
            result = RobustJSONParser.parse_ai_json(constraints_json, "dict", "constraints")

            # If parsing failed, use contextual fallback
            if result is None:
                print("⚠️ Using contextual constraint fallback to preserve rich content")
                return self._generate_fallback_constraints(building_type, user_message)

            # Validate and fix constraint structure
            for constraint_name, constraint_data in result.items():
                if not isinstance(constraint_data, dict):
                    result[constraint_name] = {"description": str(constraint_data)}
                    constraint_data = result[constraint_name]

                # Ensure required fields exist
                if 'description' not in constraint_data:
                    constraint_data['description'] = f"A design constraint for {building_type}"
                if 'impact' not in constraint_data:
                    constraint_data['impact'] = "Consider how this affects your design decisions"
                if 'examples' not in constraint_data:
                    constraint_data['examples'] = ["Think about practical implications"]

            return result
        except Exception as e:
            print(f"⚠️ AI constraint generation completely failed: {e}")
            raise e

    def _generate_fallback_constraints(self, building_type: str, user_message: str) -> Dict[str, Dict[str, Any]]:
        """ENHANCED fallback constraint generation when AI fails - ensures interactivity"""
        # CONTEXTUAL: Generate better fallbacks based on user message
        user_lower = user_message.lower()

        constraints = {}

        # Add contextual constraints based on user message
        if "circulation" in user_lower or "flow" in user_lower:
            constraints["Circulation Bottleneck"] = {
                "impact": f"Main pathways create congestion in {building_type}",
                "challenge": "How to distribute movement flows effectively?",
                "color": "#cd766d",
                "icon": "◐"
            }

        if "lighting" in user_lower or "natural light" in user_lower:
            constraints["Limited Natural Light"] = {
                "impact": f"North-facing windows limit daylight in {building_type}",
                "challenge": "How to maximize natural light penetration?",
                "color": "#d99c66",
                "icon": "◐"
            }

        if "space" in user_lower or "layout" in user_lower:
            constraints["Space Limitations"] = {
                "impact": f"Compact footprint restricts {building_type} layout",
                "challenge": "How to create spacious feeling in limited area?",
                "color": "#b87189",
                "icon": "◐"
            }

        # Always include at least 3 constraints for interactivity
        if len(constraints) < 3:
            fallback_constraints = {
                "Budget Limitation": {
                    "impact": f"Reduced funding affects {building_type} design choices",
                    "challenge": "How to maintain quality with limited resources?",
                    "color": "#cd766d",
                    "icon": "◐"
                },
                "Site Constraints": {
                    "impact": f"Physical site limitations for {building_type}",
                    "challenge": "How to work within site boundaries?",
                    "color": "#d99c66",
                    "icon": "◐"
                },
                "Program Requirements": {
                    "impact": f"Complex functional needs for {building_type}",
                    "challenge": "How to accommodate all required functions?",
                    "color": "#b87189",
                    "icon": "◐"
                },
                "Accessibility Compliance": {
                    "impact": f"ADA requirements affect {building_type} design",
                    "challenge": "How to integrate accessibility elegantly?",
                    "color": "#8b7ca6",
                    "icon": "◐"
                }
            }

            # Add fallbacks until we have at least 3 total
            for name, data in fallback_constraints.items():
                if len(constraints) >= 4:
                    break
                if name not in constraints:
                    constraints[name] = data

        # PERFORMANCE: Disable debug prints
        # print(f"🔧 FALLBACK CONSTRAINTS: Generated {len(constraints)} interactive constraints")
        return constraints

    def generate_mystery_from_context(self, building_type: str, user_message: str) -> Dict[str, Any]:
        """ENHANCED: Generate rich contextual mystery using AI for any architectural topic."""

        # PERFORMANCE: Skip AI if no API key available
        import os
        if not os.getenv('OPENAI_API_KEY'):
            return self._generate_fallback_mystery(building_type, user_message)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            # Clean user message for AI prompt
            safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
            safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

            mystery_prompt = f"""
            Create an engaging architectural detective mystery for a student working on a {safe_building_type} project.

            User's current focus: "{safe_user_message}"
            Building type: "{safe_building_type}"

            Generate a mystery that:
            1. Relates specifically to the user's architectural challenge or question
            2. Creates an intriguing problem that requires investigation
            3. Provides meaningful clues that lead to design insights
            4. Is realistic and educational for architecture students
            5. Connects to the specific building type and context

            Return as JSON with this exact structure:
            {{
                "mystery_description": "A compelling mystery description (100-150 characters)",
                "clues": ["Clue 1 with specific details", "Clue 2 with specific details", "Clue 3 with specific details"],
                "red_herrings": ["Red herring 1", "Red herring 2"],
                "solution_hint": "A hint toward the solution"
            }}

            Make the mystery engaging and specific to the user's project context.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": mystery_prompt}],
                max_tokens=800,  # Allow for rich, detailed content
                temperature=0.7  # Allow for creative, varied content
            )

            # ENHANCED: Use robust JSON parser
            mystery_json = response.choices[0].message.content
            if not mystery_json:
                print("⚠️ Empty mystery response from AI")
                return self._generate_fallback_mystery(building_type, user_message)

            # Parse using robust JSON parser
            result = RobustJSONParser.parse_ai_json(mystery_json, "dict", "mystery")

            # If parsing failed, use contextual fallback
            if result is None:
                print("⚠️ Using contextual mystery fallback to preserve rich content")
                return self._generate_fallback_mystery(building_type, user_message)

            # Validate and fix mystery structure
            if 'mystery_description' not in result:
                result['mystery_description'] = f"An intriguing design challenge has emerged in your {building_type} project"
            if 'clues' not in result or not isinstance(result['clues'], list):
                result['clues'] = ["Investigate the user flow patterns", "Examine the spatial relationships", "Consider the environmental factors"]
            if 'red_herrings' not in result or not isinstance(result['red_herrings'], list):
                result['red_herrings'] = ["The obvious solution might not be the best", "Consider alternative approaches"]
            if 'solution_hint' not in result:
                result['solution_hint'] = "The answer lies in understanding user needs and spatial relationships"

            return result

        except Exception as e:
            print(f"⚠️ AI mystery generation failed: {e}")
            return self._generate_fallback_mystery(building_type, user_message)

    def _generate_fallback_mystery(self, building_type: str, user_message: str) -> Dict[str, Any]:
        """Generate rich contextual mystery fallback when AI fails."""

        user_lower = user_message.lower()

        # Context-aware mystery generation
        if 'warehouse' in user_lower and 'community center' in user_lower:
            return {
                "mystery_description": "The warehouse conversion is creating unexpected spatial conflicts between different user groups",
                "clues": [
                    "Elderly visitors avoid certain areas during busy workshop times",
                    "The market vendors complain about noise from the cultural activities",
                    "Young families seem to cluster near the entrance instead of exploring deeper spaces"
                ],
                "red_herrings": [
                    "The lighting seems too dim in some areas",
                    "The acoustics create echo in the main hall"
                ],
                "solution_hint": "The solution involves understanding how different community groups use space and time"
            }
        elif 'elder' in user_lower or 'elderly' in user_lower:
            return {
                "mystery_description": f"Senior users are not engaging with your {building_type} as expected - what's missing?",
                "clues": [
                    "Elderly visitors spend most time near the entrance and rarely venture deeper",
                    "They prefer certain seating areas and avoid others entirely",
                    "Staff notice they often ask for directions even after multiple visits"
                ],
                "red_herrings": [
                    "The signage might be too small to read",
                    "The building might be too large and overwhelming"
                ],
                "solution_hint": "Consider how familiarity, comfort, and social connection influence spatial behavior"
            }
        else:
            return {
                "mystery_description": f"Users are not experiencing your {building_type} the way you intended - investigate why",
                "clues": [
                    "People are using spaces differently than planned",
                    "Certain areas remain empty while others are overcrowded",
                    "The flow between activities doesn't feel natural to users"
                ],
                "red_herrings": [
                    "The furniture arrangement might need adjustment",
                    "The color scheme could be more inviting"
                ],
                "solution_hint": "The answer lies in understanding the gap between design intent and user behavior"
            }

    def generate_perspectives_from_context(self, building_type: str, user_message: str) -> List[str]:
        """Generate contextual perspectives using AI for flexible content generation."""
        # CONVERSATION-AWARE CACHING: Include conversation context for better games
        conversation_context = getattr(st.session_state, 'messages', [])[-3:]  # Last 3 messages for context
        context_hash = hash(str(conversation_context) + user_message[:50])
        cache_key = f"perspectives_{building_type}_{context_hash}"

        if hasattr(st.session_state, 'game_cache') and cache_key in st.session_state.game_cache:
            return st.session_state.game_cache[cache_key]

        # FLEXIBLE AI-POWERED: Generate contextual perspectives for ANY topic
        try:
            result = self._generate_ai_contextual_perspectives(building_type, user_message)
            # Cache the result
            if not hasattr(st.session_state, 'game_cache'):
                st.session_state.game_cache = {}
            st.session_state.game_cache[cache_key] = result
            return result
        except Exception as e:
            print(f"⚠️ AI perspective generation failed: {e}")
            # Fallback to basic perspectives
            return self._generate_fallback_perspectives(building_type, user_message)

    def _generate_ai_contextual_perspectives(self, building_type: str, user_message: str) -> List[str]:
        """Generate contextual perspectives using AI for any architectural topic"""
        import openai
        client = openai.OpenAI()

        # Escape quotes in user message to prevent string formatting issues
        safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
        safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

        perspective_prompt = f"""
        Generate 4-6 diverse user perspectives for an architecture student working on a {safe_building_type} project.

        User's question/context: "{safe_user_message}"
        Building type: "{safe_building_type}"

        Create perspectives that:
        1. Relate specifically to the user's question/topic
        2. Represent different user types who would use the {building_type}
        3. Include diverse ages, abilities, and roles
        4. Are specific and realistic (not generic)
        5. Help the student think about different user needs

        Return as a simple JSON array of perspective names:
        ["Perspective 1", "Perspective 2", "Perspective 3", "Perspective 4"]

        Make perspective names specific and relatable (like "Working Parent", "Wheelchair User", "Local Artist").
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": perspective_prompt}],
            max_tokens=600,  # INCREASED: Prevent JSON truncation
            temperature=0.5  # REDUCED: More consistent JSON formatting
        )

        # ENHANCED: Use robust JSON parser
        perspectives_json = response.choices[0].message.content
        if not perspectives_json:
            print("⚠️ Empty perspectives response from AI")
            return self._generate_fallback_perspectives(building_type, user_message)

        # FIXED: Try conservative JSON parsing first, preserve rich AI content
        result = RobustJSONParser.parse_ai_json(perspectives_json, "list", "perspectives")

        # If parsing failed, use contextual fallback
        if result is None:
            print("⚠️ Using contextual perspective fallback to preserve rich content")
            return self._generate_fallback_perspectives(building_type, user_message)

        return result

    def _generate_fallback_perspectives(self, building_type: str, user_message: str) -> List[str]:
        """Fallback perspective generation when AI fails"""
        return ["Regular User", "First-time Visitor", "Staff Member", "Community Leader", "Senior Citizen", "Young Adult"]

    def generate_story_chapters_from_context(self, building_type: str, user_message: str) -> Dict[str, str]:
        """ENHANCED: Generate rich contextual story chapters using AI."""

        # PERFORMANCE: Skip AI if no API key available
        import os
        if not os.getenv('OPENAI_API_KEY'):
            return self._generate_fallback_story_chapters(building_type, user_message)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            # Clean user message for AI prompt
            safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
            safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

            story_prompt = f"""
            Create engaging story chapters for an architecture student's {safe_building_type} project.

            User's current focus: "{safe_user_message}"
            Building type: "{safe_building_type}"

            Generate 4-5 story chapters that:
            1. Tell the story of how people experience the building throughout different times/situations
            2. Are specific to the user's architectural challenge or question
            3. Show the building's role in people's lives and community
            4. Are engaging and help the student think about user experience
            5. Connect to the specific building type and context

            Return as JSON with chapter names as keys and rich descriptions as values:
            {{
                "Chapter Name 1": "Rich description of this part of the building's story (80-120 characters)",
                "Chapter Name 2": "Rich description of this part of the building's story (80-120 characters)",
                "Chapter Name 3": "Rich description of this part of the building's story (80-120 characters)",
                "Chapter Name 4": "Rich description of this part of the building's story (80-120 characters)"
            }}

            Make the chapters specific to the user's project context and building type.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=800,  # Allow for rich, detailed content
                temperature=0.7  # Allow for creative, varied content
            )

            # ENHANCED: Use robust JSON parser
            chapters_json = response.choices[0].message.content
            if not chapters_json:
                print("⚠️ Empty story chapters response from AI")
                return self._generate_fallback_story_chapters(building_type, user_message)

            # Parse using robust JSON parser
            result = RobustJSONParser.parse_ai_json(chapters_json, "dict", "story_chapters")

            # If parsing failed, use contextual fallback
            if result is None:
                print("⚠️ Using contextual story chapters fallback to preserve rich content")
                return self._generate_fallback_story_chapters(building_type, user_message)

            return result

        except Exception as e:
            print(f"⚠️ AI story chapters generation failed: {e}")
            return self._generate_fallback_story_chapters(building_type, user_message)

    def _generate_fallback_story_chapters(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate rich contextual story chapters fallback when AI fails."""

        user_lower = user_message.lower()

        # Context-aware story chapter generation
        if 'warehouse' in user_lower and 'community center' in user_lower:
            return {
                "Industrial Dawn": "The old warehouse awakens to new purpose as early morning light filters through industrial windows, revealing spaces where community life will unfold",
                "Cultural Convergence": "Artists, workshop leaders, and market vendors arrive, transforming the industrial shell into a vibrant hub of creative and commercial activity",
                "Community Crossroads": "Families, elderly residents, and young professionals intersect in the central space, each finding their place within the adaptive reuse narrative",
                "Evening Reflection": "As activities wind down, the warehouse holds the day's memories while preparing for tomorrow's community stories to unfold"
            }
        elif 'elder' in user_lower or 'elderly' in user_lower:
            return {
                "Morning Ritual": f"Senior community members begin their day at the {building_type}, finding familiar comfort in spaces designed with their needs in mind",
                "Social Connection": f"The {building_type} becomes a bridge between generations as elderly visitors share stories and wisdom with younger community members",
                "Accessible Journey": f"Every pathway and space in the {building_type} tells a story of thoughtful design that honors the dignity and independence of older adults",
                "Legacy Building": f"Through their daily presence, elderly users help shape the {building_type} into a true community anchor that serves all generations"
            }
        else:
            return {
                "First Light": f"The {building_type} comes alive as morning light reveals spaces carefully designed to serve the community's diverse needs",
                "Active Engagement": f"Throughout the day, the {building_type} adapts to different activities, showing how thoughtful architecture supports human interaction",
                "Community Rhythm": f"The {building_type} pulses with the natural rhythms of community life, each space playing its role in the larger urban story",
                "Lasting Impact": f"As evening falls, the {building_type} stands as a testament to architecture's power to strengthen communities and enrich lives"
            }

    def generate_time_periods_from_context(self, building_type: str, user_message: str) -> Dict[str, str]:
        """ENHANCED: Generate rich contextual time periods using AI."""

        # PERFORMANCE: Skip AI if no API key available
        import os
        if not os.getenv('OPENAI_API_KEY'):
            return self._generate_fallback_time_periods(building_type, user_message)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            # Clean user message for AI prompt
            safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
            safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

            time_prompt = f"""
            Create engaging time periods for an architecture student's {safe_building_type} project time travel challenge.

            User's current focus: "{safe_user_message}"
            Building type: "{safe_building_type}"

            Generate 3-4 time periods that:
            1. Show how the building and its context evolve over time
            2. Are specific to the user's architectural challenge or question
            3. Help the student understand the building's role in different eras
            4. Are engaging and educational for architecture students
            5. Connect to the specific building type and context

            Return as JSON with time period names as keys and rich descriptions as values:
            {{
                "Time Period 1": "Rich description of the building/site in this era (100-150 characters)",
                "Time Period 2": "Rich description of the building/site in this era (100-150 characters)",
                "Time Period 3": "Rich description of the building/site in this era (100-150 characters)"
            }}

            Make the time periods specific to the user's project context and building type.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": time_prompt}],
                max_tokens=800,  # Allow for rich, detailed content
                temperature=0.7  # Allow for creative, varied content
            )

            # ENHANCED: Use robust JSON parser
            periods_json = response.choices[0].message.content
            if not periods_json:
                print("⚠️ Empty time periods response from AI")
                return self._generate_fallback_time_periods(building_type, user_message)

            # Parse using robust JSON parser
            result = RobustJSONParser.parse_ai_json(periods_json, "dict", "time_periods")

            # If parsing failed, use contextual fallback
            if result is None:
                print("⚠️ Using contextual time periods fallback to preserve rich content")
                return self._generate_fallback_time_periods(building_type, user_message)

            return result

        except Exception as e:
            print(f"⚠️ AI time periods generation failed: {e}")
            return self._generate_fallback_time_periods(building_type, user_message)

    def _generate_fallback_time_periods(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate rich contextual time periods fallback when AI fails."""

        user_lower = user_message.lower()

        # Context-aware time period generation
        if 'warehouse' in user_lower and 'community center' in user_lower:
            return {
                "Industrial Era": "The site bustles with industrial activity - warehouses store goods, workers shape the neighborhood's character, and the area serves the city's economic engine",
                "Transition Period": "As industry moves elsewhere, the warehouse stands empty, its solid bones waiting for new purpose while the community around it evolves and adapts",
                "Community Renaissance": "The warehouse transforms into a vibrant community center, its industrial heritage celebrated as it becomes a hub for cultural activities, learning, and local commerce"
            }
        elif 'elder' in user_lower or 'elderly' in user_lower:
            return {
                "Foundation Years": f"The {building_type} is designed with universal accessibility in mind, anticipating the needs of an aging population and creating inclusive spaces",
                "Mature Community": f"The {building_type} becomes a cornerstone for senior services, adapting its programs and spaces to serve multiple generations with dignity and respect",
                "Intergenerational Legacy": f"The {building_type} evolves into a model for age-friendly design, where seniors and youth learn from each other in thoughtfully designed spaces"
            }
        else:
            return {
                "Vision Phase": f"The {building_type} exists first as an idea, shaped by community needs and architectural imagination, waiting to take physical form",
                "Active Life": f"The {building_type} serves its community daily, adapting to changing needs while maintaining its core mission and architectural integrity",
                "Future Evolution": f"The {building_type} continues to evolve, demonstrating how thoughtful architecture can adapt and remain relevant across generations"
            }

    def generate_transformations_from_context(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate contextual transformation types using AI for flexible content generation."""
        # ISSUE 1 FIX: Reduce caching to allow more contextual generation
        # Only cache if the exact same message is repeated (very unlikely in real conversation)
        cache_key = f"transformations_{building_type}_{hash(user_message[:100])}"  # Only hash first 100 chars

        # Skip cache for transformation responses to ensure fresh generation
        is_transformation_response = any(keyword in user_message.lower() for keyword in
                                       ['movable partitions', 'modular furniture', 'flexible spaces'])

        if (not is_transformation_response and
            hasattr(st.session_state, 'game_cache') and
            cache_key in st.session_state.game_cache):
            # ISSUE 3 FIX: Commented out cache hit print
            # print(f"🚀 CACHE HIT: Using cached transformations for {building_type}")
            return st.session_state.game_cache[cache_key]

        # FLEXIBLE AI-POWERED: Generate contextual transformations for ANY topic
        try:
            result = self._generate_ai_contextual_transformations(building_type, user_message)
            # Cache the result
            if not hasattr(st.session_state, 'game_cache'):
                st.session_state.game_cache = {}
            st.session_state.game_cache[cache_key] = result
            return result
        except Exception as e:
            print(f"⚠️ AI transformation generation failed: {e}")
            # Fallback to basic transformations
            return self._generate_fallback_transformations(building_type, user_message)

    def _generate_ai_contextual_transformations(self, building_type: str, user_message: str) -> Dict[str, str]:
        """Generate contextual transformations using AI for any architectural topic"""
        import os
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Escape quotes in user message to prevent string formatting issues
        safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
        safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

        transformation_prompt = f"""
        Generate exactly 3 transformation scenarios for an architecture student working on a {safe_building_type} project.

        User's question/context: "{safe_user_message}"
        Building type: "{safe_building_type}"

        Create transformation scenarios that:
        1. Relate specifically to the user's question/topic
        2. Show how spaces can adapt and change
        3. Are realistic and achievable
        4. Encourage creative thinking about flexibility
        5. Are specific to the building type and context

        IMPORTANT: Make descriptions rich and detailed (150-250 characters).
        Explain HOW the space transforms and WHY it's meaningful for the project.

        Format:
        {{
            "Descriptive Space Name 1": "Rich, detailed description of how this space transforms to serve different needs, including specific design strategies and user benefits (150-250 characters)",
            "Descriptive Space Name 2": "Another rich description explaining the transformation process, design implications, and community impact (150-250 characters)",
            "Descriptive Space Name 3": "Third detailed description showing creative adaptation strategies and their architectural significance (150-250 characters)"
        }}

        Use descriptive, engaging names that reflect the transformation concept.
        Make each description specific to the user's context and building type.
        Ensure all strings are properly closed with quotes.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": transformation_prompt}],
            max_tokens=600,  # INCREASED: Allow for richer, more detailed content
            temperature=0.7  # RESTORED: Allow for more creative, varied content
        )

        # ENHANCED: Use robust JSON parser
        transformations_json = response.choices[0].message.content
        if not transformations_json:
            print("⚠️ Empty transformations response from AI")
            return self._generate_fallback_transformations(building_type, user_message)

        # FIXED: Try conservative JSON parsing first, preserve rich AI content
        result = RobustJSONParser.parse_ai_json(transformations_json, "dict", "transformations")

        # If parsing failed, use contextual fallback (not generic)
        if result is None:
            print("⚠️ Using contextual transformation fallback to preserve rich content")
            return self._generate_fallback_transformations(building_type, user_message)

        return result

    def _generate_fallback_transformations(self, building_type: str, user_message: str) -> Dict[str, str]:
        """FIXED: Generate rich contextual transformation fallbacks when AI fails."""
        user_lower = user_message.lower()

        # Context-aware rich transformation generation
        if 'warehouse' in user_lower and 'community center' in user_lower:
            return {
                "Industrial Heritage Entrance": f"Transform the warehouse loading dock into a welcoming entrance that celebrates the building's industrial heritage while clearly marking its new role as a {building_type}, incorporating original steel elements and adding accessible ramps",
                "Flexible Community Spaces": f"Convert the open warehouse floor into adaptable spaces that can host everything from community meetings to cultural events, maintaining the industrial character while adding warmth through strategic lighting, acoustic treatments, and moveable partitions",
                "Cultural Activity Zones": f"Create distinct zones within the warehouse volume for different community activities - workshops, gatherings, and quiet spaces - using the existing structural elements as natural dividers while ensuring clear sightlines and accessibility for elderly users"
            }
        elif 'elder' in user_lower or 'elderly' in user_lower:
            return {
                "Comfort-Focused Social Areas": f"Transform existing spaces into comfortable social areas specifically designed for elderly users, with appropriate seating heights, good lighting for reading and conversation, and easy access to restrooms and refreshment areas",
                "Intergenerational Activity Spaces": f"Adapt spaces to encourage interaction between elderly users and other community members through shared activities like gardening, crafts, or storytelling, with flexible furniture arrangements that support both intimate conversations and larger group activities",
                "Accessible Circulation Networks": f"Redesign pathways and circulation areas to be fully accessible for elderly users with mobility aids, incorporating rest areas, clear wayfinding, and non-slip surfaces while maintaining the dignity and independence of all users"
            }
        else:
            return {
                "Adaptive Multi-Purpose Spaces": f"Transform key areas of your {building_type} into flexible spaces that can serve multiple functions throughout the day, using moveable partitions, modular furniture, and adaptable lighting systems to support diverse community activities and changing needs",
                "Community Connection Hub": f"Create a central gathering space within your {building_type} that serves as the heart of community interaction, incorporating comfortable seating areas, information displays, and informal meeting spaces that encourage spontaneous social connections",
                "Responsive Outdoor Integration": f"Develop seamless connections between indoor and outdoor spaces in your {building_type}, creating covered transition areas, outdoor activity zones, and flexible spaces that can expand or contract based on weather, season, and community programming needs"
            }

class EnhancedGamificationRenderer:
    """Enhanced visual gamification with creative interactive elements."""
    
    def __init__(self):
        self.themes = ENHANCED_THEMES
        self.content_generator = FlexibleContentGenerator()

    def _ensure_game_state(self, state_key: str, default_state: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure game state is properly initialized and return reference to session state."""
        if state_key not in st.session_state:
            st.session_state[state_key] = default_state.copy()
        return st.session_state[state_key]

    def _generate_contextual_storytelling_challenge(self, user_message: str, building_type: str) -> str:
        """Generate a contextual storytelling challenge based on user's message topic."""

        # Extract key themes from user message
        user_lower = user_message.lower()

        # Context-aware challenge generation based on user's topic
        if 'user journey' in user_lower or 'journey through' in user_lower:
            return f"Create a narrative following different visitors as they move through your {building_type}. Tell the story from arrival to departure, showing how the space guides their experience."

        elif 'narrative flow' in user_lower or 'story that guides' in user_lower:
            return f"Develop a storytelling framework for your {building_type} that naturally guides people through different experiences. How does the architecture itself tell a story?"

        elif 'central hub' in user_lower or 'hub' in user_lower:
            return f"Tell the story of your {building_type}'s central space from multiple perspectives. How does this hub connect different activities and create community?"

        elif 'workshops' in user_lower and 'market' in user_lower:
            return f"Create interconnected stories showing how workshop activities and market spaces complement each other in your {building_type}. What narratives emerge from these different uses?"

        elif 'arrival' in user_lower or 'entrance' in user_lower:
            return f"Craft a welcoming story that begins the moment someone approaches your {building_type}. How does the architecture create anticipation and guide first impressions?"

        elif 'pause' in user_lower or 'moments of' in user_lower:
            return f"Design narrative moments of rest and reflection within your {building_type}. Where do stories slow down, and how do these pauses enhance the overall experience?"

        else:
            # Generic but contextual fallback
            return f"Create a multi-layered narrative about your {building_type} that reveals different stories depending on who experiences the space and when they visit."

    def _safe_json_parse(self, json_string: str, fallback_data: Any = None, data_type: str = "data") -> Any:
        """Safely parse JSON with comprehensive error handling and validation."""
        try:
            # Clean the JSON string
            json_string = json_string.strip()

            # Remove markdown code blocks if present
            if "```json" in json_string:
                json_string = json_string.split("```json")[1].split("```")[0].strip()
            elif "```" in json_string:
                json_string = json_string.split("```")[1].strip()

            # Parse JSON
            result = json.loads(json_string)

            # Validate result is not None or empty
            if result is None:
                raise ValueError(f"{data_type} is None")

            if isinstance(result, dict) and len(result) == 0:
                raise ValueError(f"{data_type} dictionary is empty")

            if isinstance(result, list) and len(result) == 0:
                raise ValueError(f"{data_type} list is empty")

            return result

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"⚠️ {data_type} JSON parsing failed: {e}")
            print(f"Raw response: {json_string[:200]}...")

            if fallback_data is not None:
                print(f"Using fallback {data_type}")
                return fallback_data

            # Return safe defaults based on expected type
            if "dict" in str(type(fallback_data)) or data_type.lower() in ["personas", "constraints", "transformations"]:
                return {}
            elif "list" in str(type(fallback_data)) or data_type.lower() in ["perspectives", "chapters"]:
                return []
            else:
                return None

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

        # PERFORMANCE: Disable debug prints to improve speed
        # print(f"🎮 CONTEXTUAL RENDERING: User message = '{user_message}'")
        print(f"🎮 CONTEXTUAL RENDERING: Challenge type = '{challenge_type}'")
        # print(f"🎮 CONTEXTUAL RENDERING: Building type = '{building_type}'")

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
                # FIXED: Generate contextual storytelling challenge instead of using raw user message
                contextual_challenge = self._generate_contextual_storytelling_challenge(user_message, building_type)
                self._render_storytelling_game(contextual_challenge, theme, building_type)
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
        """Render compact persona game with error handling."""
        try:
            # Validate inputs
            if not theme:
                theme = {"gradient": "linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #e0ceb5 100%)",
                        "accent": "#e0ceb5", "primary": "#4f3a3e", "icon": "◉", "symbol": "▲"}
            if not building_type:
                building_type = "community center"
            if not challenge_text:
                challenge_text = "design challenge"

            # Compact header
            st.markdown(f"""
            <div style="
                background: {theme.get('gradient', 'linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #e0ceb5 100%)')};
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                text-align: center;
            ">
                <div style="
                    width: 50px;
                    height: 50px;
                    background: {theme.get('accent', '#e0ceb5')};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 10px;
                    font-size: 1.5em;
                    color: {theme.get('primary', '#4f3a3e')};
                ">
                    {theme.get('icon', '◉')}
                </div>
                <h3 style="color: white; margin: 0; font-weight: 400;">
                    {theme.get('icon', '◉')} Role Play
                </h3>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            print(f"🎮 ERROR in persona game header: {e}")
            st.markdown("### 🎭 Role Play Challenge")
            st.markdown("*Experience your design from different perspectives*")

        # Generate dynamic personas based on context with error handling
        try:
            personas = self.content_generator.generate_personas_from_context(building_type, challenge_text)
            if not personas or len(personas) == 0:
                raise Exception("No personas generated")
        except Exception as e:
            print(f"🎮 ERROR generating personas: {e}")
            # Fallback personas
            personas = {
                "Regular User": {
                    "description": f"Someone who frequently uses the {building_type}",
                    "mission": f"Navigate and use the {building_type} effectively",
                    "insights": ["Familiar with the space", "Has established routines"]
                },
                "First-time Visitor": {
                    "description": f"Someone visiting the {building_type} for the first time",
                    "mission": f"Find their way and understand how to use the space",
                    "insights": ["Needs clear wayfinding", "May feel overwhelmed"]
                }
            }

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
            symbol = theme.get('symbol', '●')
            description = persona_data.get('description', 'A user of this space')[:60]

            if st.button(
                f"{symbol} {persona_name}: {description}...",
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

            # Compact experience section with safe field access
            mission = persona_data.get('mission', f"Experience the {building_type} from this perspective")
            symbol = theme.get('symbol', '●')

            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{symbol} {persona_name}:</strong>
                <span style="color: #2c2328;">{mission}</span>
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

            if st.button(f"{symbol} Submit Experience", key=f"submit_{persona_key}", type="primary"):
                if user_response.strip():
                    persona_state['response_given'] = True
                    persona_state['persona_points'] += 30

                    # INTEGRATE WITH MENTOR: Send game response back to conversation
                    game_response = f"{user_response.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()

        # Show insights after submission
        if persona_state.get('response_given', False):
            # Compact insights display
            insights = persona_data.get('insights', ["Great thinking!"])
            symbol = theme.get('symbol', '●')

            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div style="
                    background: {theme['accent']};
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    border-left: 3px solid {theme['primary']};
                ">
                    <strong style="color: {theme['primary']};">{symbol} Insight {i+1}:</strong>
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

        # CRITICAL FIX: Generate unique key with timestamp to prevent duplicates
        import time
        unique_key = f"spin_{wheel_key}_{int(time.time() * 1000000)}"

        # Compact spin button
        if st.button(
            f"{theme['icon']} Spin Perspective Wheel",
            key=unique_key,
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
                    game_response = f"{response.strip()}"
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
                    game_response = f"{hypothesis.strip()}"
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
        """Render standardized constraint puzzle game with consistent UI."""
        # STANDARDIZED HEADER - matches other games
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="
                width: 60px;
                height: 60px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 15px;
                font-size: 1.8em;
                color: white;
                animation: {theme['animation']} 2s infinite;
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0 0 10px 0; font-weight: 600; font-size: 1.4em;">
                Constraint Challenge
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 0.95em;">
                Select constraints and create innovative solutions
            </p>
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

        # STANDARDIZED CONSTRAINT SELECTION - matches other games
        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <h4 style="color: {theme['primary']}; margin: 0 0 15px 0; font-size: 1.1em;">
                {theme['symbol']} Select Constraints (max 3):
            </h4>
        </div>
        """, unsafe_allow_html=True)

        # Display constraints in a grid layout
        constraint_items = list(constraints.items())
        for i in range(0, len(constraint_items), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(constraint_items):
                    constraint_name, constraint_data = constraint_items[i + j]
                    is_selected = constraint_name in constraint_state['selected_constraints']

                    with col:
                        # ENHANCED CONSTRAINT BUTTON with better styling
                        button_style = "primary" if is_selected else "secondary"
                        button_text = f"{'✓ ' if is_selected else ''}{constraint_data.get('icon', '◐')} {constraint_name}"

                        if st.button(
                            button_text,
                            key=f"constraint_{constraint_name}_{constraint_key}",
                            type=button_style,
                            use_container_width=True,
                            help=constraint_data.get('impact', 'Design constraint')
                        ):
                            if is_selected:
                                constraint_state['selected_constraints'].remove(constraint_name)
                            else:
                                if len(constraint_state['selected_constraints']) < 3:
                                    constraint_state['selected_constraints'].append(constraint_name)
                                else:
                                    st.warning("Maximum 3 constraints allowed. Deselect one first.")
                            st.rerun()

        # Show selection status
        if constraint_state['selected_constraints']:
            selected_count = len(constraint_state['selected_constraints'])
            st.info(f"🎯 {selected_count}/3 constraints selected: {', '.join(constraint_state['selected_constraints'])}")

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

            # ENHANCED SUBMISSION LOGIC
            col1, col2 = st.columns([3, 1])
            with col1:
                submit_button = st.button(
                    f"{theme['symbol']} Submit Solution",
                    key=f"submit_{constraint_key}",
                    type="primary",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Reset", key=f"reset_{constraint_key}", use_container_width=True):
                    constraint_state['selected_constraints'] = []
                    constraint_state['solution'] = ''
                    st.rerun()

            if submit_button:
                if solution.strip():
                    # COMPLETE SUBMISSION PROCESSING
                    constraint_state['completed'] = True
                    constraint_state['solution'] = solution
                    constraint_state['points'] += len(constraint_state['selected_constraints']) * 15

                    # Show immediate feedback
                    st.success(f"🎉 Solution submitted! +{len(constraint_state['selected_constraints']) * 15} points")
                    st.balloons()

                    # ENHANCED INTEGRATION: Format response for mentor system
                    selected_constraints_text = ", ".join(constraint_state['selected_constraints'])
                    formatted_response = f"**Constraint Challenge Response:**\n\n**Selected Constraints:** {selected_constraints_text}\n\n**My Solution:** {solution.strip()}"

                    # Send to conversation
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": formatted_response})
                    st.session_state.should_process_message = True

                    # Track completion for gamification stats
                    try:
                        from dashboard.ui.gamification_components import GamificationTracker
                        tracker = GamificationTracker()
                        tracker.add_challenge_completion("constraint_challenge", 25)
                    except Exception as e:
                        print(f"⚠️ Gamification tracking failed: {e}")

                    st.rerun()
                else:
                    st.warning("Please enter a solution before submitting.")

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
                    game_response = f"{response.strip()}"
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
        try:
            # ISSUE 3 FIX: Check if storytelling is already completed
            if st.session_state.get('storytelling_completed', False):
                st.info("🎉 Storytelling challenge already completed! You've submitted your 3-chapter story.")
                return

            # ISSUE 2 FIX: Robust storytelling state initialization with validation
            if 'storytelling_state' not in st.session_state:
                st.session_state.storytelling_state = {
                    'chapter': 1,
                    'story_points': 0,
                    'narrative_choices': [],
                    'story_complete': False,
                    'show_feedback': False,
                    'feedback_message': '',
                    'feedback_points': 0,
                    'completed': False
                }

            story_state = st.session_state.storytelling_state

            # CRITICAL FIX: Validate and repair storytelling state if corrupted
            required_keys = ['chapter', 'story_points', 'narrative_choices', 'show_feedback', 'feedback_message', 'feedback_points']
            for key in required_keys:
                if key not in story_state:
                    if key == 'chapter':
                        story_state[key] = 1
                    elif key == 'story_points':
                        story_state[key] = 0
                    elif key == 'narrative_choices':
                        story_state[key] = []
                    elif key == 'show_feedback':
                        story_state[key] = False
                    elif key == 'feedback_message':
                        story_state[key] = ''
                    elif key == 'feedback_points':
                        story_state[key] = 0
                    print(f"🔧 STORYTELLING FIX: Added missing key '{key}' to storytelling state")

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
                {challenge_text.replace('</div>', '').replace('<div>', '').strip() if challenge_text else 'Begin your storytelling journey...'}
            </div>
        </div>
        """, unsafe_allow_html=True)

            # Generate dynamic story chapters based on context
            story_chapters_dict = self.content_generator.generate_story_chapters_from_context(building_type, challenge_text)
            story_chapters = list(story_chapters_dict.values())

            # ISSUE 2 FIX: Ultra-safe state access with comprehensive validation
            try:
                chapter_num = story_state.get('chapter', 1)
                if not isinstance(chapter_num, int) or chapter_num < 1:
                    chapter_num = 1
                    story_state['chapter'] = 1

                if len(story_chapters) == 0:
                    story_chapters = ["Begin your architectural story..."]

                # Ensure chapter index is within bounds
                chapter_index = min(max(chapter_num - 1, 0), len(story_chapters) - 1)
                current_chapter = story_chapters[chapter_index]

            except Exception as chapter_error:
                print(f"🔧 STORYTELLING CHAPTER FIX: {chapter_error}")
                chapter_num = 1
                story_state['chapter'] = 1
                current_chapter = "Begin your architectural story..."

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

            # UI FIX: Show persistent feedback messages if available
            if story_state.get('show_feedback', False):
                feedback_msg = story_state.get('feedback_message', '')
                feedback_points = story_state.get('feedback_points', 0)

                if feedback_msg:
                    st.success(feedback_msg)

                if feedback_points > 0:
                    self._show_contextual_progress("Storytelling Challenge", story_state['story_points'], 100)

                # Add a dismiss button to clear feedback
                if st.button("✓ Continue", key="dismiss_feedback", use_container_width=True):
                    story_state['show_feedback'] = False
                    story_state['feedback_message'] = ''
                    story_state['feedback_points'] = 0
                    st.session_state['storytelling_state'] = story_state
                    st.rerun()

            # Story response (only show if not showing feedback)
            if not story_state.get('show_feedback', False):
                story_response = st.text_area(
                    "Continue the story - what happens next?",
                    key="storytelling_response",
                    height=100
                )

            # Only show button if not showing feedback
            if not story_state.get('show_feedback', False):
                if st.button(f"{theme['symbol']} Continue Story", key="continue_story", use_container_width=True):
                    if story_response:
                        # ISSUE 2 FIX: Safe state updates with validation
                        try:
                            story_state['chapter'] = story_state.get('chapter', 1) + 1
                            story_state['story_points'] = story_state.get('story_points', 0) + 10
                            if 'narrative_choices' not in story_state:
                                story_state['narrative_choices'] = []
                            story_state['narrative_choices'].append(story_response)
                        except Exception as update_error:
                            print(f"🔧 STORYTELLING UPDATE FIX: {update_error}")
                            # Reset to safe state
                            story_state = {
                                'chapter': 2,
                                'story_points': 35,
                                'narrative_choices': [story_response],
                                'show_feedback': False,
                                'feedback_message': '',
                                'feedback_points': 0
                            }

                        # ISSUE 3 FIX: Complete storytelling after 3 submissions
                        if len(story_state['narrative_choices']) >= 3:
                            # Story completion after 3 submissions - show immediate feedback with balloons
                            st.success("🎉 **STORYTELLING CHALLENGE COMPLETE!** You've submitted 3 story chapters!")
                            st.balloons()

                            # Show final story summary
                            with st.expander("📖 Your Complete Story", expanded=True):
                                st.write("**Your 3-Chapter Narrative Journey:**")
                                for i, choice in enumerate(story_state['narrative_choices'], 1):
                                    st.write(f"**Chapter {i}:** {choice}")

                            # Mark storytelling as permanently completed
                            st.session_state['storytelling_completed'] = True

                            # Clear storytelling state to prevent further challenges
                            st.session_state['storytelling_state'] = {
                                'chapter': 1,
                                'story_points': 0,
                                'narrative_choices': [],
                                'show_feedback': False,
                                'feedback_message': '',
                                'feedback_points': 0,
                                'completed': True  # Mark as completed
                            }

                            # Trigger message processing for follow-up
                            st.session_state.should_process_message = True
                            st.session_state.messages.append({
                                "role": "user",
                                "content": f"I completed the storytelling challenge with 3 chapters! Here's my narrative: {' '.join(story_state['narrative_choices'])}"
                            })
                        else:
                            # UI FIX: Set persistent feedback state instead of immediate display + rerun
                            story_state['show_feedback'] = True
                            story_state['feedback_message'] = "Story continues! Your narrative has been recorded."
                            story_state['feedback_points'] = 35

                        # Update session state
                        st.session_state['storytelling_state'] = story_state

                        # UI FIX: Only rerun if story is not complete (to show persistent feedback)
                        if story_state['story_points'] < 100:
                            st.rerun()

        except Exception as e:
            print(f"🎮 ERROR in storytelling game: {e}")
            st.error("⚠️ Storytelling game encountered an issue. Please try again.")
            # Reset storytelling state on error
            if 'storytelling_state' in st.session_state:
                del st.session_state.storytelling_state

    def _render_time_travel_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render interactive time travel challenge."""
        # FIXED: Properly initialize and persist session state
        if 'time_travel_state' not in st.session_state:
            st.session_state.time_travel_state = {
                'current_era': 'present',
                'time_points': 0,
                'temporal_insights': [],
                'completed': False
            }
        time_state = st.session_state.time_travel_state

        # FIXED: Check if game is completed to prevent regeneration
        if time_state.get('completed', False):
            st.success("✅ **Time Travel Challenge Completed!**")
            with st.expander("⏰ Your Temporal Journey", expanded=False):
                for i, insight in enumerate(time_state['temporal_insights'], 1):
                    st.write(f"**{i}. {insight['era']}:** {insight['insight']}")
            return

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
                Explore how your {building_type} design evolves across different time periods.
                Consider how changing needs, technologies, and social patterns affect architectural decisions.
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

                # FIXED: Add completion logic
                if time_state['time_points'] >= 45:
                    time_state['completed'] = True
                    st.session_state['time_travel_state'] = time_state
                    st.success("🎉 **TIME TRAVEL COMPLETE!** You've mastered temporal design thinking!")
                    st.balloons()

                    # Show temporal insights summary
                    with st.expander("⏰ Your Temporal Journey", expanded=True):
                        for i, insight in enumerate(time_state['temporal_insights'], 1):
                            st.write(f"**{i}. {insight['era']}:** {insight['insight']}")

                    # Trigger message processing for follow-up
                    st.session_state.should_process_message = True
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"I completed the time travel challenge! I explored: {', '.join([i['era'] for i in time_state['temporal_insights']])}"
                    })
                else:
                    st.session_state['time_travel_state'] = time_state
                    st.success("Temporal insight recorded! Time reveals new perspectives.")
                    self._show_contextual_progress("Time Travel Challenge", time_state['time_points'], 45)

    def _render_transformation_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render interactive transformation challenge."""

        # FIXED: Use proper game description instead of user message - ensure no HTML tags
        game_description = f"Design your {building_type} to adapt and transform for different uses, times, and seasons. Explore how spaces can change to serve multiple functions while maintaining their architectural integrity."

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
                {game_description}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Generate dynamic transformations based on context
        transformations_dict = self.content_generator.generate_transformations_from_context(building_type, challenge_text)

        # Initialize transformation state properly
        transform_key = f"transform_{building_type}_{hash(challenge_text)}"
        if transform_key not in st.session_state:
            st.session_state[transform_key] = {
                'selected_transformation': None,
                'transformation_data': None,
                'response_given': False,
                'transform_points': 0
            }

        transform_state = st.session_state[transform_key]

        # Show transformation options (like roleplay personas)
        st.markdown("**Choose your transformation approach:**")

        for i, (transform_name, transform_description) in enumerate(transformations_dict.items()):
            is_selected = transform_state['selected_transformation'] == transform_name

            # Show transformation button with preview (like roleplay)
            if st.button(
                f"{theme['symbol']} {transform_name}: {transform_description[:60]}...",
                key=f"select_transform_{i}_{hash(challenge_text)}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                transform_state['selected_transformation'] = transform_name
                transform_state['transformation_data'] = transform_description
                transform_state['response_given'] = False
                st.rerun()

        # Show selected transformation challenge (like roleplay experience)
        if transform_state['selected_transformation'] and transform_state['transformation_data']:
            transform_name = transform_state['selected_transformation']
            transform_description = transform_state['transformation_data']

            # Show full challenge description
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} {transform_name}:</strong><br>
                <span style="color: #2c2328;">{transform_description}</span>
            </div>
            """, unsafe_allow_html=True)

            # Response area (like roleplay)
            transform_response = st.text_area(
                "Your transformation approach:",
                placeholder=f"To implement {transform_name.lower()}, I would...",
                height=100,
                key=f"response_{transform_key}",
                help="Describe your design strategy, specific elements, and how they enable transformation"
            )

            if st.button(f"{theme['symbol']} Submit Transformation", key=f"submit_{transform_key}", type="primary"):
                if transform_response.strip():
                    transform_state['response_given'] = True
                    transform_state['transform_points'] += 30

                    # INTEGRATE WITH MENTOR: Send game response back to conversation (like roleplay)
                    game_response = f"{transform_response.strip()}"
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append({"role": "user", "content": game_response})
                    st.session_state.should_process_message = True
                    st.rerun()

        # Show completion feedback (like roleplay)
        if transform_state['response_given']:
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 10px;
                border-radius: 8px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <span style="color: #2c2328; line-height: 1.5;">✅ Transformation approach submitted! Your response will be processed by the mentor.</span>
            </div>
            """, unsafe_allow_html=True)

            # Show only contextual progress (no success message)
            self._show_contextual_progress("Transformation Challenge", transform_state['transform_points'], 30)


# Global functions for integration
def render_enhanced_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Main entry point for rendering enhanced gamified challenges."""
    try:
        # PERFORMANCE: Disable debug prints to improve speed
        print(f"🎮 ENHANCED GAMIFICATION: Starting render with data: {list(challenge_data.keys())}")

        # Validate essential data
        if not challenge_data:
            print("🎮 ENHANCED GAMIFICATION: No challenge data provided")
            st.info("💭 Continue exploring your design ideas!")
            return

        # FIXED: Remove aggressive duplicate prevention that was causing games to disappear
        # Let individual games handle their own completion logic
        # This allows games to re-render when users interact with them

        # Ensure required fields exist with safe defaults and validation
        safe_challenge_data = {
            "challenge_text": challenge_data.get("challenge_text", "Let's explore your design challenge!"),
            "challenge_type": challenge_data.get("challenge_type", "constraint_challenge"),  # FIXED: Use correct default
            "building_type": challenge_data.get("building_type", "community center"),
            "user_message": challenge_data.get("user_message", ""),
            "gamification_applied": challenge_data.get("gamification_applied", True),
            **challenge_data  # Include any additional data
        }

        # Validate critical fields
        if not safe_challenge_data["challenge_text"] or safe_challenge_data["challenge_text"].strip() == "":
            safe_challenge_data["challenge_text"] = "Let's explore your design challenge!"

        if not safe_challenge_data["building_type"] or safe_challenge_data["building_type"].strip() == "":
            safe_challenge_data["building_type"] = "community center"

        # Initialize renderer
        renderer = EnhancedGamificationRenderer()

        # Render the challenge with additional safety
        try:
            renderer.render_enhanced_challenge(safe_challenge_data)
        except Exception as render_error:
            print(f"🎮 ERROR in render_enhanced_challenge: {render_error}")
            # Try a simpler render approach
            challenge_text = safe_challenge_data.get('challenge_text', 'Continue exploring your design ideas!')
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #e0ceb5 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                text-align: center;
            ">
                <h3 style="color: white; margin: 0 0 10px 0;">Design Challenge</h3>
                <p style="color: white; margin: 0; font-size: 1.1em;">{challenge_text}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("💬 **Continue the conversation** by sharing your thoughts, questions, or insights about this challenge.")
            raise render_error  # Re-raise to trigger the outer exception handler

        # PERFORMANCE: Disable debug prints
        # print(f"🎮 ENHANCED GAMIFICATION: Render completed successfully")

    except Exception as e:
        print(f"🎮 ENHANCED GAMIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Better fallback - try to render a simple version first
        try:
            challenge_text = challenge_data.get('challenge_text', 'Continue exploring your design ideas!')
            challenge_type = challenge_data.get('challenge_type', 'general')

            # Simple challenge display without complex UI
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #e0ceb5 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                text-align: center;
            ">
                <h3 style="color: white; margin: 0 0 10px 0;">Design Challenge</h3>
                <p style="color: white; margin: 0; font-size: 1.1em;">{challenge_text}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("💬 **Continue the conversation** by sharing your thoughts, questions, or insights about this challenge.")

        except Exception as fallback_error:
            print(f"🎮 ENHANCED GAMIFICATION FALLBACK ERROR: {fallback_error}")
            # Last resort - minimal display
            st.info("💭 Continue with your design exploration!")


def inject_gamification_css() -> None:
    """Inject CSS for enhanced gamification animations."""
    # This is handled by _inject_enhanced_css in the renderer
    pass