#This is the analysis_agent for the ArchMentor system
# It performs dynamic skill assessment, visual and text analysis, and synthesizes findings for cognitive enhancement
from typing import Dict, Any, List, Optional
import sys
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from datetime import datetime, timedelta

load_dotenv()  # Should already be there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.sketch_analyzer import SketchAnalyzer
from state_manager import ArchMentorState, StudentProfile, VisualArtifact
from knowledge_base.knowledge_manager import KnowledgeManager
from phase_management.milestone_questions import MilestoneType

class AnalysisAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  #memory issue
        self.domain = domain
        self.sketch_analyzer = SketchAnalyzer(domain)
        self.knowledge_manager = KnowledgeManager(domain)
        self.name = "analysis_agent"
        
        # Initialize phase detection parameters
        self.phase_indicators = self._initialize_phase_indicators()
        self.phase_weights = self._initialize_phase_weights()
        
        print(f"🔍 {self.name} initialized for domain: {domain}")
    
    def _initialize_phase_indicators(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize comprehensive phase detection indicators"""
        
        return {
            "ideation": {
                "conversation_indicators": [
                    "concept", "idea", "approach", "strategy", "vision", "philosophy",
                    "what if", "how might", "explore", "consider", "think about",
                    "precedent", "inspiration", "reference", "example", "case study",
                    "user needs", "program", "function", "purpose", "goal",
                    "site analysis", "context", "environment", "climate", "culture"
                ],
                "visual_indicators": [
                    "concept sketch", "bubble diagram", "program diagram", "site analysis",
                    "mood board", "inspiration images", "rough sketches", "flow diagrams"
                ],
                "design_indicators": [
                    "program development", "concept exploration", "site understanding",
                    "user research", "precedent study", "design philosophy"
                ]
            },
            "visualization": {
                "conversation_indicators": [
                    "form", "shape", "massing", "volume", "proportion", "scale",
                    "circulation", "flow", "layout", "plan", "section", "elevation",
                    "spatial relationship", "adjacency", "hierarchy", "organization",
                    "sketch", "drawing", "model", "3d", "perspective", "rendering",
                    "light", "shadow", "material", "texture", "color", "atmosphere",
                    # 3107-ENHANCED TILL BRACKETS: Add technical design terms that indicate visualization phase
                    "orientation", "shading", "glazing", "atrium", "light wells", 
                    "work zones", "meeting areas", "ventilation", "daylight",
                    "energy efficiency", "natural lighting", "collaborative environment",
                    "open spaces", "flexible spaces", "central space", "shared systems",
                    "district heating", "solar panels", "high-performance", "smart glass",
                    "adjustable blinds", "indoor green", "casual meeting", "open work"
                ],
                "visual_indicators": [
                    "floor plan", "site plan", "section", "elevation", "3d model",
                    "massing study", "spatial diagram", "circulation diagram",
                    "lighting study", "material study", "rendering", "perspective"
                ],
                "design_indicators": [
                    "spatial development", "form exploration", "circulation design",
                    "proportion study", "lighting design", "material exploration"
                ]
            },
            "materialization": {
                "conversation_indicators": [
                    "construction", "structure", "system", "detail", "joint", "connection",
                    "material specification", "assembly", "fabrication", "installation",
                    "technical", "engineering", "performance", "efficiency", "sustainability",
                    "code", "regulation", "standard", "requirement", "specification",
                    "cost", "budget", "timeline", "schedule", "phasing", "implementation"
                ],
                "visual_indicators": [
                    "construction detail", "structural diagram", "building section",
                    "material specification", "assembly detail", "technical drawing",
                    "sustainability diagram", "performance analysis", "cost analysis"
                ],
                "design_indicators": [
                    "technical development", "construction methodology", "material specification",
                    "performance optimization", "cost analysis", "implementation planning"
                ]
            }
        }
    
    def _initialize_phase_weights(self) -> Dict[str, Dict[str, float]]:
        """Initialize weights for different phase detection factors"""
        
        return {
            "conversation_weight": 0.4,
            "visual_weight": 0.3,
            "design_weight": 0.2,
            "temporal_weight": 0.1,
            "confidence_threshold": 0.6
        }

    def assess_student_skill_level(self, state: ArchMentorState) -> str:
        """Dynamically assess student skill level from their inputs"""
        
        # Get all user messages for analysis
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if not user_messages:
            return "intermediate"  # Default
        
        # Combine all user input for analysis
        combined_input = " ".join(user_messages)
        
        # VOCABULARY ANALYSIS
        beginner_indicators = [
            "don't know", "confused", "help", "what is", "how do", "basic", 
            "simple", "easy", "first time", "new to", "learning", "beginner"
        ]
        
        intermediate_indicators = [
            "accessibility", "circulation", "programming", "design", "space", 
            "layout", "plan", "consider", "think about", "approach", "community",
            "building", "rooms", "areas", "entrance", "windows", "doors"
        ]
        
        advanced_indicators = [
            "parti", "phenomenology", "tectonics", "typology", "morphology",
            "zoning", "egress", "life safety", "building codes", "structural systems",
            "environmental systems", "sustainable", "LEED", "passive design",
            "urban context", "precedent", "critical regionalism", "threshold",
            "spatial sequence", "materiality", "site analysis"
        ]
        
        # Count indicators
        beginner_score = sum(1 for phrase in beginner_indicators if phrase in combined_input.lower())
        intermediate_score = sum(1 for phrase in intermediate_indicators if phrase in combined_input.lower())
        advanced_score = sum(1 for phrase in advanced_indicators if phrase in combined_input.lower())
        
        # COMPLEXITY ANALYSIS
        avg_sentence_length = sum(len(msg.split()) for msg in user_messages) / len(user_messages)
        uses_technical_terms = intermediate_score + advanced_score > 0
        
        # DECISION LOGIC
        total_messages = len(user_messages)
        
        print(f"   📊 Skill indicators: Beginner({beginner_score}) Intermediate({intermediate_score}) Advanced({advanced_score})")
        print(f"   📊 Avg sentence length: {avg_sentence_length:.1f}, Technical terms: {uses_technical_terms}")
        
        # Advanced: High technical vocabulary + complex questions
        if advanced_score > 0 and (advanced_score / total_messages > 0.1 or avg_sentence_length > 15):
            return "advanced"
        
        # Beginner: Explicit beginner language or very simple inputs
        elif beginner_score > 0 or (avg_sentence_length < 6 and not uses_technical_terms):
            return "beginner"
        
        # Intermediate: Default middle ground
        else:
            return "intermediate"
    
    def calculate_skill_confidence(self, state: ArchMentorState) -> float:
        """Calculate confidence in skill level assessment"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if not user_messages:
            return 0.3
        
        # More messages = higher confidence
        message_confidence = min(len(user_messages) / 5, 1.0)  # Max confidence at 5+ messages
        
        # Longer total text = higher confidence
        total_words = sum(len(msg.split()) for msg in user_messages)
        length_confidence = min(total_words / 100, 1.0)  # Max confidence at 100+ words
        
        return (message_confidence + length_confidence) / 2

    # Contextualization methods with context agent added
    def incorporate_context_insights(self, analysis_result: Dict, context_package: Dict) -> Dict:
            """Incorporate Context Agent insights for continuity (Section 7)"""
            conversation_patterns = context_package.get("conversation_patterns", {})
            context_metadata = context_package.get("contextual_metadata", {})

            # CONTINUITY INSIGHTS - FIXED: Don't flag as repetitive if student is responding to questions
            if conversation_patterns.get("repetitive_topics"):
                #3107 ADDED Check if this is a response to a question rather than true repetition
                last_assistant_message = ""
                for msg in reversed(context_package.get("conversation_history", [])):
                    if msg.get("role") == "assistant":
                        last_assistant_message = msg.get("content", "")
                        break
                
                #Only flag as repetitive if the assistant didn't ask a question
                if "?" not in last_assistant_message:



                    analysis_result["cognitive_flags"].append("stuck_on_topic")
                    analysis_result["continuity_insights"] = ["Student returning to same topic - needs different approach"]
                #3107 ADDED
                else:
                    # Student is responding to a question - this is good engagement
                    analysis_result["cognitive_flags"].append("responding_to_question")
                    analysis_result["continuity_insights"] = ["Student actively responding to questions - good engagement"]



            if conversation_patterns.get("understanding_progression") == "progressing":
                analysis_result["cognitive_flags"].append("showing_growth")
                analysis_result["continuity_insights"] = ["Student demonstrating learning progression"]

            # LEARNING TRAJECTORY
            engagement_trend = conversation_patterns.get("engagement_trend", "stable")
            if engagement_trend == "decreasing":
                analysis_result["cognitive_flags"].append("engagement_declining")
            elif engagement_trend == "increasing":
                analysis_result["cognitive_flags"].append("engagement_improving")

            return analysis_result


    async def process(self, state: ArchMentorState, context_package: Dict = None) -> Dict[str, Any]:
        """Main analysis processing with dynamic skill assessment and phase detection"""
        
        print(f"\n🚀 {self.name} starting analysis...")
        
        # DYNAMIC SKILL ASSESSMENT FIRST
        detected_skill_level = self.assess_student_skill_level(state)
        current_skill_level = state.student_profile.skill_level
        
        # Update skill level if detection differs significantly
        if detected_skill_level != current_skill_level:
            print(f"📊 Skill level updated: {current_skill_level} → {detected_skill_level}")
            state.student_profile.skill_level = detected_skill_level
        else:
            print(f"📊 Confirmed skill level: {detected_skill_level}")
        
        # PHASE DETECTION
        print(f"🔍 {self.name}: Starting phase detection...")
        phase_analysis = self.detect_design_phase(state)
        print(f"🎯 Phase detection complete: {phase_analysis['phase']} (confidence: {phase_analysis['confidence']:.2f})")
        
        # INITIALIZE ANALYSIS RESULT
        analysis_result = {
            "agent": self.name,
            "domain": self.domain,
            "visual_analysis": {},
            "text_analysis": {},
            "synthesis": {},
            "confidence_score": 0.5,
            "key_insights": [],
            "cognitive_flags": [],
            "phase_analysis": phase_analysis,  # Add phase analysis
            "skill_assessment": {
                "detected_level": detected_skill_level,
                "previous_level": current_skill_level,
                "updated": detected_skill_level != current_skill_level,
                "confidence": self.calculate_skill_confidence(state)
            }
        }
        
        # Get current inputs
        current_sketch = state.current_sketch
        design_brief = state.current_design_brief
        
        print(f"📝 Design brief: {design_brief[:50] if design_brief else 'None'}...")
        print(f"🖼️ Current sketch: {'Available' if current_sketch else 'None'}")
        
        # VISUAL ANALYSIS (if sketch available)
        if current_sketch:
            print("🖼️ Analyzing visual content...")
            try:
                visual_analysis = await self.sketch_analyzer.analyze_sketch(current_sketch, design_brief)
                analysis_result["visual_analysis"] = visual_analysis
                print(f"✅ Visual analysis complete. Elements identified: {len(visual_analysis.get('identified_elements', []))}")
            except Exception as e:
                print(f"⚠️ Visual analysis failed: {e}")
                analysis_result["visual_analysis"] = {"error": str(e)}
        else:
            print("📝 No visual content to analyze")
        
        # TEXT ANALYSIS (if brief available)
        if design_brief:
            print("📖 Analyzing design brief...")
            text_analysis = self.analyze_design_brief(design_brief)
            analysis_result["text_analysis"] = text_analysis
            print(f"✅ Text analysis complete. Building type: {text_analysis.get('building_type', 'unknown')}")
        else:
            print("📝 No design brief provided")
        
        # Synthesize findings
        print("🧠 Synthesizing analysis for cognitive enhancement...")
        synthesis = self.synthesize_analysis(
            analysis_result["visual_analysis"], 
            analysis_result["text_analysis"],
            state.student_profile
        )
        analysis_result["synthesis"] = synthesis
        
        # Generate cognitive flags for other agents (now phase-aware)
        cognitive_flags = await self.generate_cognitive_flags(analysis_result, state.student_profile, state)
        analysis_result["cognitive_flags"] = cognitive_flags
        
        print(f"🎯 Analysis complete! Confidence: {analysis_result['confidence_score']}")
        print(f"🚩 Generated {len(cognitive_flags)} cognitive flags for other agents")
        print(f"🎯 Current phase: {phase_analysis['phase']} (confidence: {phase_analysis['confidence']:.2f})")
        
        # Enhance analysis with knowledge base
        if analysis_result["visual_analysis"] and not analysis_result["visual_analysis"].get("error"):
            enhanced_analysis = await self.enhance_with_knowledge(
                analysis_result["visual_analysis"], 
                state.current_design_brief
            )
            analysis_result["knowledge_enhanced"] = enhanced_analysis
         # INCORPORATE CONTEXT INSIGHTS (Section 7)
        if context_package:
            analysis_result = self.incorporate_context_insights(analysis_result, context_package)
            print("🔗 Incorporated context insights for continuity")
        
        return analysis_result
    
    async def enhance_with_knowledge(self, visual_analysis: Dict, design_brief: str) -> Dict:
        """Enhance visual analysis with relevant knowledge"""
        
        # Create search query from visual analysis
        elements = visual_analysis.get('identified_elements', [])
        
        search_query = f"{design_brief} {' '.join(elements[:3])}"
        
        # Search knowledge base
        knowledge_results = self.knowledge_manager.search_knowledge(search_query, n_results=3)
        
        if knowledge_results:
            return {
                "relevant_knowledge": knowledge_results,
                "knowledge_enhanced": True,
                "enhancement_confidence": max([r.get('similarity', 0) for r in knowledge_results])
            }
        else:
            return {"knowledge_enhanced": False}
    
    def analyze_design_brief(self, brief: str) -> Dict[str, Any]:
        """Analyze the textual design brief for key information using AI for better detection"""
        
        # Use AI to intelligently detect the project type
        prompt = f"""
        Analyze this architectural design brief and identify the building type:
        
        BRIEF: "{brief}"
        
        Identify the most likely building type from these options:
        - community center
        - housing/residential
        - office/workplace
        - school/educational
        - hospital/healthcare
        - library
        - museum/gallery
        - retail/commercial
        - restaurant/food service
        - industrial/manufacturing
        - mixed-use
        - cultural center
        - sports/recreation
        - transportation
        - religious/worship
        
        If the brief doesn't clearly indicate a building type, analyze the context and user's questions to infer the most likely type.
        
        Return ONLY the building type as a single word or short phrase (e.g., "community center", "housing", "office").
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            
            ai_building_type = response.choices[0].message.content.strip().lower()
            print(f"🏗️ AI detected building type: {ai_building_type}")
            
            # Fallback to keyword matching if AI fails
            if not ai_building_type or ai_building_type == "unknown":
                ai_building_type = self._fallback_building_type_detection(brief)
            
        except Exception as e:
            print(f"⚠️ AI building type detection failed: {e}")
            ai_building_type = self._fallback_building_type_detection(brief)
        
        # Expanded program type detection - covers more building types
        program_keywords = {
            "community center": {
                "requirements": ["meeting rooms", "kitchen", "flexible space", "accessibility", "parking"],
                "considerations": ["public access", "multiple user groups", "community engagement"]
            },
            "housing": {
                "requirements": ["bedrooms", "living areas", "parking", "privacy", "storage"],
                "considerations": ["family size", "privacy", "outdoor space"]
            },
            "office": {
                "requirements": ["workspaces", "meeting rooms", "reception", "storage", "parking"],
                "considerations": ["collaboration", "privacy", "technology"]
            },
            "school": {
                "requirements": ["classrooms", "cafeteria", "library", "playground", "administration"],
                "considerations": ["safety", "age groups", "accessibility", "outdoor learning"]
            },
            "hospital": {
                "requirements": ["patient rooms", "emergency", "surgery", "reception", "parking"],
                "considerations": ["accessibility", "infection control", "staff workflow", "patient comfort"]
            },
            "library": {
                "requirements": ["reading areas", "collections", "study rooms", "computers", "accessibility"],
                "considerations": ["quiet zones", "natural light", "security", "community access"]
            },
            "museum": {
                "requirements": ["exhibition spaces", "storage", "entrance", "gift shop", "accessibility"],
                "considerations": ["climate control", "lighting", "circulation", "visitor experience"]
            },
            "retail": {
                "requirements": ["sales floor", "storage", "checkout", "fitting rooms", "parking"],
                "considerations": ["customer flow", "product display", "security", "accessibility"]
            },
            "restaurant": {
                "requirements": ["dining areas", "kitchen", "restrooms", "storage", "parking"],
                "considerations": ["food service flow", "ambiance", "accessibility", "noise control"]
            },
            "industrial": {
                "requirements": ["production areas", "storage", "offices", "loading", "parking"],
                "considerations": ["workflow efficiency", "safety", "environmental controls", "logistics"]
            }
        }
        
        # Get requirements and considerations for the detected building type
        requirements = []
        considerations = []
        
        # Try to match the AI-detected type with our program keywords
        for btype, info in program_keywords.items():
            if btype in ai_building_type or ai_building_type in btype:
                requirements = info["requirements"]
                considerations = info["considerations"]
                break
        
        # Extract numbers and quantities
        numbers = re.findall(r'\d+', brief)
        
        # Extract constraints and requirements
        constraint_keywords = ["budget", "sustainable", "accessible", "limited", "small", "large", 
                             "affordable", "green", "net-zero", "LEED", "ADA"]
        constraints = [kw for kw in constraint_keywords if kw in brief.lower()]
        
        # Assess brief complexity
        word_count = len(brief.split())
        complexity = "simple" if word_count < 20 else "detailed" if word_count < 50 else "comprehensive"
        
        return {
            "building_type": ai_building_type,
            "program_requirements": requirements,
            "design_considerations": considerations,
            "numbers_mentioned": numbers,
            "constraints": constraints,
            "word_count": word_count,
            "complexity": complexity,
            "detail_level": self.assess_detail_level(brief)
        }
    
    def _fallback_building_type_detection(self, brief: str) -> str:
        """Fallback keyword-based building type detection"""
        brief_lower = brief.lower()
        
        # Simple keyword matching as fallback
        if any(word in brief_lower for word in ["community", "center", "meeting"]):
            return "community center"
        elif any(word in brief_lower for word in ["house", "home", "residential", "apartment", "housing"]):
            return "housing"
        elif any(word in brief_lower for word in ["office", "workplace", "work", "business"]):
            return "office"
        elif any(word in brief_lower for word in ["school", "education", "classroom", "student"]):
            return "school"
        elif any(word in brief_lower for word in ["hospital", "medical", "healthcare", "clinic"]):
            return "hospital"
        elif any(word in brief_lower for word in ["library", "book", "reading"]):
            return "library"
        elif any(word in brief_lower for word in ["museum", "gallery", "exhibition", "art"]):
            return "museum"
        elif any(word in brief_lower for word in ["retail", "shop", "store", "commercial"]):
            return "retail"
        elif any(word in brief_lower for word in ["restaurant", "cafe", "food", "dining"]):
            return "restaurant"
        elif any(word in brief_lower for word in ["industrial", "factory", "manufacturing"]):
            return "industrial"
        else:
            return "mixed-use"  # Better default than "unknown"
    
    def assess_detail_level(self, brief: str) -> str:
        """Assess how detailed the student's brief is"""
        detail_indicators = ["square feet","square meters", "people", "users", "specific", "include", "require", 
                           "must", "should", "will", "budget", "timeline", "site"]
        
        brief_lower = brief.lower()
        detail_count = sum(1 for indicator in detail_indicators if indicator in brief_lower)
        
        if detail_count >= 5:
            return "highly_detailed"
        elif detail_count >= 3:
            return "moderately_detailed"
        elif detail_count >= 1:
            return "basic_details"
        else:
            return "vague"
    
    # synthesize_analysis method for cognitive enhancement
    # This method synthesizes findings from visual and text analysis to identify cognitive challenges and learning opportunities

    def synthesize_analysis(self, visual: Dict, textual: Dict, student_profile: StudentProfile) -> Dict[str, Any]:
        """Enhanced synthesis for better cognitive challenge detection"""
        
        synthesis = {
            "alignment_assessment": {},
            "missing_considerations": [],
            "cognitive_challenges": [],
            "learning_opportunities": [],
            "next_focus_areas": []
        }
        
        # Enhanced cognitive challenge detection
        cognitive_challenges = []
        
        # Always check for accessibility (especially for public buildings)
        building_type = textual.get("building_type", "unknown") if textual else "unknown"
        if building_type in ["community center", "school", "library", "office"]:
            cognitive_challenges.append("accessibility_awareness")
        
        # Check for spatial relationships (if no visual provided or visual lacks spatial info)
        if not visual or not visual.get("spatial_relationships"):
            cognitive_challenges.append("spatial_relationships")
        
        # Check brief development based on detail level
        if textual:
            detail_level = textual.get("detail_level", "vague")
            if detail_level in ["vague", "basic_details"]:
                cognitive_challenges.append("brief_development")
        
        # Skill-specific challenges
        skill_level = student_profile.skill_level
        
        if skill_level == "beginner":
            cognitive_challenges.append("basic_concept_understanding")
        elif skill_level == "advanced":
            cognitive_challenges.append("systems_thinking")
        
        synthesis["cognitive_challenges"] = cognitive_challenges
        
        # Check alignment between visual design and text brief
        if visual and textual and not visual.get("error"):
            required_elements = textual.get("program_requirements", [])
            
            # Simple alignment check
            if required_elements:
                # Assume some missing for demo purposes
                missing_requirements = required_elements[:2] if len(required_elements) > 2 else []
                
                synthesis["alignment_assessment"] = {
                    "status": "needs_work" if missing_requirements else "good",
                    "missing_requirements": missing_requirements,
                    "alignment_score": 0.7
                }
                
                synthesis["missing_considerations"] = missing_requirements
        
        # Generate learning opportunities
        learning_opportunities = []
        
        if "accessibility_awareness" in cognitive_challenges:
            learning_opportunities.append("Explore universal design principles")
        
        if "spatial_relationships" in cognitive_challenges:
            learning_opportunities.append("Consider how spaces connect and flow")
        
        if "brief_development" in cognitive_challenges:
            learning_opportunities.append("Develop more detailed program requirements")
        
        synthesis["learning_opportunities"] = learning_opportunities
        
        # Suggest next focus areas
        next_focus = []
        
        if cognitive_challenges:
            next_focus.append("socratic_questioning")
        
        if synthesis["missing_considerations"]:
            next_focus.append("domain_expertise")
        
        synthesis["next_focus_areas"] = next_focus
        
        print(f"   🧠 Synthesis complete: {len(cognitive_challenges)} challenges, {len(learning_opportunities)} opportunities")
        
        return synthesis

    # Additional cognitive state assessment method
    def assess_cognitive_state(self, state: ArchMentorState) -> Dict[str, Any]:
        """Implement Section 6 cognitive state assessment"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        # ENGAGEMENT INDICATORS from your document
        avg_length = sum(len(msg.split()) for msg in user_messages) / len(user_messages) if user_messages else 0
        has_questions = any("?" in msg for msg in user_messages)
        has_elaboration = avg_length > 15
        
        if has_questions and has_elaboration:
            engagement = "high"
        elif avg_length > 8:
            engagement = "medium"
        else:
            engagement = "low"
        
        # COGNITIVE LOAD INDICATORS
        confusion_words = ["confused", "don't understand", "help"]
        shows_confusion = any(word in " ".join(user_messages).lower() for word in confusion_words)
        
        if shows_confusion:
            cognitive_load = "overloaded"
        elif engagement == "medium":
            cognitive_load = "optimal"
        else:
            cognitive_load = "underloaded"
        
        return {
            "engagement": engagement,
            "cognitive_load": cognitive_load,
            "avg_response_length": avg_length
        }


    # generate_cognitive_flags method
    async def generate_cognitive_flags(self, analysis_result: Dict, student_profile: StudentProfile, state: ArchMentorState) -> List[str]:
        """AI-powered cognitive flag generation - accurately identifies what the student is asking about"""
        
        # Get student's actual messages
        student_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        recent_input = " ".join(student_messages[-2:]) if student_messages else ""
        
        prompt = f"""
        Analyze this architecture student's question and identify what they are ACTUALLY asking about:

        STUDENT INPUT: "{recent_input}"
        PROJECT: {state.current_design_brief}
        SKILL LEVEL: {student_profile.skill_level}
        
        First, identify the MAIN TOPIC they are asking about (e.g., circulation, lighting, materials, accessibility, etc.)
        Then, identify what type of guidance they need.
        
        IMPORTANT: Look at the actual words they used. If they mention "circulation", the topic is circulation, not materials.
        
        Generate 2-3 cognitive flags that accurately reflect their question:
        
        Topic-based flags (use the actual topic they mentioned):
        - needs_circulation_guidance (if asking about movement, flow, paths)
        - needs_lighting_guidance (if asking about illumination, natural light)
        - needs_material_guidance (if asking about materials, finishes)
        - needs_acoustic_guidance (if asking about sound, noise)
        - needs_accessibility_guidance (if asking about universal design, ADA)
        - needs_sustainability_guidance (if asking about environmental issues)
        - needs_structural_guidance (if asking about building systems)
        - needs_programming_guidance (if asking about space functions/activities)
        - needs_spatial_thinking_support (if asking about space organization)
        
        Guidance type flags:
        - needs_brief_clarification (if unclear about requirements)
        - needs_technical_guidance (if asking about specific standards/codes)
        - needs_design_strategy_guidance (if asking about design approaches)
        
        Return 2-3 flags as a comma-separated list: flag1, flag2, flag3
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            flags_text = response.choices[0].message.content.strip()
            flags = [flag.strip() for flag in flags_text.split(',')]
            
            print(f"🤖 AI generated flags based on student input: {flags}")
            print(f"🤖 Student input was: {recent_input}")
            return flags
            
        except Exception as e:
            print(f"⚠️ AI flag generation failed: {e}")
            return ["needs_brief_clarification"]  # Safe fallback

    def detect_design_phase(self, state: ArchMentorState, analysis_result: Dict = None) -> Dict[str, Any]:
        """
        Comprehensive phase detection algorithm implementing scientific methodology
        
        Returns:
            Dict containing:
            - phase: "ideation" | "visualization" | "materialization"
            - confidence: float (0-1)
            - indicators: Dict of supporting evidence
            - progression_score: float indicating phase advancement
            - phase_duration: estimated time in current phase
        """
        
        print(f"🔍 {self.name}: Detecting design phase...")
        
        # 1. CONVERSATION PATTERN ANALYSIS
        conversation_analysis = self._analyze_conversation_phase_indicators(state)
        
        # 2. VISUAL CONTENT ANALYSIS
        visual_analysis = self._analyze_visual_phase_indicators(state, analysis_result)
        
        # 3. DESIGN PROGRESSION ANALYSIS
        design_analysis = self._analyze_design_progression_indicators(state)
        
        # 4. TEMPORAL ANALYSIS
        temporal_analysis = self._analyze_temporal_phase_indicators(state)
        
        # 5. COMPREHENSIVE PHASE SCORING
        phase_scores = self._calculate_phase_scores(
            conversation_analysis, visual_analysis, design_analysis, temporal_analysis
        )
        
        # 6. CONFIDENCE CALCULATION
        confidence_metrics = self._calculate_phase_confidence(
            phase_scores, conversation_analysis, visual_analysis, design_analysis
        )
        
        # 7. PHASE DETERMINATION
        detected_phase = max(phase_scores, key=phase_scores.get)
        confidence = confidence_metrics['overall_confidence']
        
        # 8. PROGRESSION ANALYSIS
        progression_analysis = self._analyze_phase_progression(state, detected_phase)
        
        result = {
            "phase": detected_phase,
            "confidence": confidence,
            "phase_scores": phase_scores,
            "indicators": {
                "conversation": conversation_analysis,
                "visual": visual_analysis,
                "design": design_analysis,
                "temporal": temporal_analysis
            },
            "confidence_metrics": confidence_metrics,
            "progression_score": progression_analysis['progression_score'],
            "phase_duration": progression_analysis['phase_duration'],
            "phase_characteristics": self._get_phase_characteristics(detected_phase),
            "recommendations": self._generate_phase_recommendations(detected_phase, confidence)
        }
        
        print(f"🎯 Phase detected: {detected_phase} (confidence: {confidence:.2f})")
        print(f"📊 Phase scores: {phase_scores}")
        
        return result
    
    def _analyze_conversation_phase_indicators(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze conversation patterns for phase indicators"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if not user_messages:
            return {"ideation": 0, "visualization": 0, "materialization": 0, "confidence": 0}
        
        # Analyze recent messages (last 5 for current focus)
        recent_messages = user_messages[-5:]
        all_text = ' '.join(recent_messages).lower()
        
        phase_scores = {}
        total_indicators = {}
        
        for phase, indicators in self.phase_indicators.items():
            conversation_indicators = indicators["conversation_indicators"]
            
            # Count indicator matches
            matches = sum(1 for indicator in conversation_indicators if indicator in all_text)
            total_indicators[phase] = len(conversation_indicators)
            
            # Calculate normalized score
            phase_scores[phase] = matches / len(conversation_indicators) if conversation_indicators else 0
        
        # Calculate confidence based on indicator density
        max_score = max(phase_scores.values())
        confidence = min(max_score * 2, 1.0)  # Scale confidence
        
        return {
            "ideation": phase_scores.get("ideation", 0),
            "visualization": phase_scores.get("visualization", 0),
            "materialization": phase_scores.get("materialization", 0),
            "confidence": confidence,
            "total_indicators": total_indicators,
            "text_analysis": {
                "message_count": len(recent_messages),
                "avg_message_length": np.mean([len(msg.split()) for msg in recent_messages]),
                "indicator_density": sum(phase_scores.values()) / len(phase_scores)
            }
        }
    
    def _analyze_visual_phase_indicators(self, state: ArchMentorState, analysis_result: Dict = None) -> Dict[str, Any]:
        """Analyze visual content for phase indicators"""
        
        if not state.current_sketch and not analysis_result:
            return {"ideation": 0, "visualization": 0, "materialization": 0, "confidence": 0}
        
        phase_scores = {}
        
        # Use existing visual analysis if available
        if analysis_result and analysis_result.get("visual_analysis"):
            visual_analysis = analysis_result["visual_analysis"]
            
            # Analyze identified elements for phase indicators
            elements = visual_analysis.get("identified_elements", [])
            design_strengths = visual_analysis.get("design_strengths", [])
            improvement_opportunities = visual_analysis.get("improvement_opportunities", [])
            
            all_visual_content = ' '.join(elements + design_strengths + improvement_opportunities).lower()
            
            for phase, indicators in self.phase_indicators.items():
                visual_indicators = indicators["visual_indicators"]
                matches = sum(1 for indicator in visual_indicators if indicator in all_visual_content)
                phase_scores[phase] = matches / len(visual_indicators) if visual_indicators else 0
        
        else:
            # Default scores if no visual analysis
            phase_scores = {"ideation": 0.1, "visualization": 0.1, "materialization": 0.1}
        
        # Calculate confidence based on visual content availability
        has_visual_content = bool(state.current_sketch or (analysis_result and analysis_result.get("visual_analysis")))
        confidence = 0.8 if has_visual_content else 0.3
        
        return {
            "ideation": phase_scores.get("ideation", 0),
            "visualization": phase_scores.get("visualization", 0),
            "materialization": phase_scores.get("materialization", 0),
            "confidence": confidence,
            "has_visual_content": has_visual_content
        }
    
    def _analyze_design_progression_indicators(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze design progression for phase indicators"""
        
        # Analyze conversation history for design progression
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) < 3:
            return {"ideation": 0.5, "visualization": 0.3, "materialization": 0.2, "confidence": 0.3}
        
        # Split conversation into thirds for progression analysis
        third = len(user_messages) // 3
        early_messages = user_messages[:third]
        middle_messages = user_messages[third:2*third]
        recent_messages = user_messages[2*third:]
        
        phase_scores = {}
        
        for phase, indicators in self.phase_indicators.items():
            design_indicators = indicators["design_indicators"]
            
            # Calculate progression through phases
            early_score = self._calculate_indicator_score(early_messages, design_indicators)
            middle_score = self._calculate_indicator_score(middle_messages, design_indicators)
            recent_score = self._calculate_indicator_score(recent_messages, design_indicators)
            
            # Weight recent messages more heavily
            progression_score = (early_score * 0.2 + middle_score * 0.3 + recent_score * 0.5)
            phase_scores[phase] = progression_score
        
        # Calculate confidence based on conversation length
        confidence = min(len(user_messages) / 10, 1.0)
        
        return {
            "ideation": phase_scores.get("ideation", 0),
            "visualization": phase_scores.get("visualization", 0),
            "materialization": phase_scores.get("materialization", 0),
            "confidence": confidence,
            "progression_analysis": {
                "conversation_length": len(user_messages),
                "early_focus": early_score if 'early_score' in locals() else 0,
                "recent_focus": recent_score if 'recent_score' in locals() else 0
            }
        }
    
    def _analyze_temporal_phase_indicators(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze temporal patterns for phase indicators"""
        
        # Analyze message timestamps for temporal patterns
        messages_with_time = [msg for msg in state.messages if msg.get('role') == 'user' and 'timestamp' in msg]
        
        if len(messages_with_time) < 2:
            return {"ideation": 0.3, "visualization": 0.3, "materialization": 0.3, "confidence": 0.2}
        
        # Calculate time intervals between messages
        intervals = []
        for i in range(1, len(messages_with_time)):
            try:
                time1 = datetime.fromisoformat(messages_with_time[i-1]['timestamp'].replace('Z', '+00:00'))
                time2 = datetime.fromisoformat(messages_with_time[i]['timestamp'].replace('Z', '+00:00'))
                interval = (time2 - time1).total_seconds() / 60  # minutes
                intervals.append(interval)
            except:
                continue
        
        if not intervals:
            return {"ideation": 0.3, "visualization": 0.3, "materialization": 0.3, "confidence": 0.2}
        
        # Analyze temporal patterns
        avg_interval = np.mean(intervals)
        interval_variance = np.var(intervals)
        
        # Phase-specific temporal patterns
        # Ideation: Longer intervals (deep thinking)
        # Visualization: Medium intervals (active sketching)
        # Materialization: Shorter intervals (detailed work)
        
        ideation_score = min(avg_interval / 10, 1.0)  # Longer intervals favor ideation
        visualization_score = 1.0 - abs(avg_interval - 5) / 5  # Medium intervals favor visualization
        materialization_score = 1.0 - (avg_interval / 10)  # Shorter intervals favor materialization
        
        confidence = min(len(intervals) / 5, 1.0)
        
        return {
            "ideation": ideation_score,
            "visualization": visualization_score,
            "materialization": materialization_score,
            "confidence": confidence,
            "temporal_metrics": {
                "avg_interval_minutes": avg_interval,
                "interval_variance": interval_variance,
                "total_duration_minutes": sum(intervals)
            }
        }
    
    def _calculate_phase_scores(self, conversation_analysis: Dict, visual_analysis: Dict, 
                               design_analysis: Dict, temporal_analysis: Dict) -> Dict[str, float]:
        """Calculate comprehensive phase scores using weighted combination"""
        
        weights = self.phase_weights
        
        phase_scores = {}
        
        for phase in ["ideation", "visualization", "materialization"]:
            # Weighted combination of all analyses
            conversation_score = conversation_analysis.get(phase, 0) * weights["conversation_weight"]
            visual_score = visual_analysis.get(phase, 0) * weights["visual_weight"]
            design_score = design_analysis.get(phase, 0) * weights["design_weight"]
            temporal_score = temporal_analysis.get(phase, 0) * weights["temporal_weight"]
            
            # Calculate weighted average
            total_score = conversation_score + visual_score + design_score + temporal_score
            phase_scores[phase] = total_score
        
        return phase_scores
    
    def _calculate_phase_confidence(self, phase_scores: Dict[str, float], 
                                   conversation_analysis: Dict, visual_analysis: Dict, 
                                   design_analysis: Dict) -> Dict[str, float]:
        """Calculate confidence metrics for phase detection"""
        
        # Overall confidence based on score separation
        scores = list(phase_scores.values())
        max_score = max(scores)
        second_max = sorted(scores)[-2]
        score_separation = max_score - second_max
        
        overall_confidence = min(score_separation * 2, 1.0)
        
        # Individual analysis confidences
        conversation_confidence = conversation_analysis.get("confidence", 0)
        visual_confidence = visual_analysis.get("confidence", 0)
        design_confidence = design_analysis.get("confidence", 0)
        
        # Weighted confidence
        weights = self.phase_weights
        weighted_confidence = (
            conversation_confidence * weights["conversation_weight"] +
            visual_confidence * weights["visual_weight"] +
            design_confidence * weights["design_weight"]
        )
        
        return {
            "overall_confidence": overall_confidence,
            "weighted_confidence": weighted_confidence,
            "score_separation": score_separation,
            "conversation_confidence": conversation_confidence,
            "visual_confidence": visual_confidence,
            "design_confidence": design_confidence
        }
    
    def _analyze_phase_progression(self, state: ArchMentorState, current_phase: str) -> Dict[str, Any]:
        """Analyze progression within the current phase using the new milestone-based system"""
        
        try:
            # Import the new progress management system
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from phase_management.progress_manager import ProgressManager
            from phase_management.milestone_questions import MilestoneType
            
            # Get or create progress manager
            progress_manager = getattr(state, 'progress_manager', None)
            if not progress_manager:
                progress_manager = ProgressManager()
                state.progress_manager = progress_manager
            
            # Get or create student profile
            student_id = getattr(state, 'student_id', 'default_student')
            project_name = getattr(state, 'project_name', 'Architectural Project')
            
            profile = progress_manager.get_assessment_profile(student_id)
            if not profile:
                profile = progress_manager.create_assessment_profile(student_id, project_name)
            
            # Get current phase progress
            current_phase_progress = profile.phases.get(current_phase)
            if not current_phase_progress:
                # Fallback to old method if phase not found
                return self._fallback_phase_progression(state, current_phase)
            
            # HYBRID APPROACH: Analyze conversation for milestone content + detect completions
            user_messages = [msg for msg in state.messages if msg.get('role') == 'user']
            
            # Analyze recent messages for milestone content
            milestone_detection = self._detect_milestone_content(user_messages, current_phase, progress_manager, student_id)
            
            # Update progress manager with detected milestone completions
            self._update_milestone_progress_from_conversation(milestone_detection, progress_manager, student_id, current_phase)
            
            # Get student assessment profile for detailed grading metrics
            try:
                # Import progress manager for detailed assessment
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                
                from phase_management.progress_manager import ProgressManager
                
                # Get or create progress manager
                progress_manager = ProgressManager()
                student_id = f"student_{hash(str(state.messages))}"  # Simple ID generation
                
                # Get assessment profile
                assessment_profile = progress_manager.load_assessment_profile(student_id)
                if not assessment_profile:
                    assessment_profile = progress_manager.create_assessment_profile(student_id)
                
                                    # Calculate progression based on actual milestone completion and grades
                    current_phase_assessment = assessment_profile.phases.get(current_phase)
                    if current_phase_assessment:
                        # Use actual milestone completion and grades
                        completed_milestones = sum(1 for milestone in current_phase_assessment.milestones.values() 
                                                 if milestone.completion_percentage > 0.7)  # 70% threshold
                        total_milestones = len(current_phase_assessment.milestones)
                        
                        # Calculate average grade for completed milestones
                        completed_grades = [milestone.average_grade for milestone in current_phase_assessment.milestones.values() 
                                          if milestone.completion_percentage > 0.7]
                        average_grade = sum(completed_grades) / len(completed_grades) if completed_grades else 0
                        
                        # Apply benchmarking formulas for comprehensive assessment
                        
                        # 1. Cognitive Offloading Prevention (COP) - 15%
                        non_direct_queries = sum(1 for msg in user_messages 
                                               if any(word in msg.get('content', '').lower() 
                                                     for word in ['how', 'why', 'what if', 'explain', 'analyze']))
                        total_queries = len(user_messages)
                        cop_score = (non_direct_queries / total_queries) if total_queries > 0 else 0
                        cop_factor = cop_score * 0.15
                        
                        # 2. Deep Thinking Engagement (DTE) - 15%
                        response_complexity = np.mean([len(msg.get('content', '').split()) for msg in user_messages])
                        reflection_indicators = sum(1 for msg in user_messages 
                                                  if any(word in msg.get('content', '').lower() 
                                                        for word in ['think', 'consider', 'maybe', 'perhaps', 'could']))
                        dte_score = min((response_complexity * reflection_indicators) / max(total_queries, 1), 1.0)
                        dte_factor = dte_score * 0.15
                        
                        # 3. Knowledge Integration (KI) - 15%
                        architectural_terms = sum(1 for msg in user_messages 
                                                if any(term in msg.get('content', '').lower() 
                                                      for term in ['circulation', 'lighting', 'spatial', 'form', 'function', 'context']))
                        ki_score = min(architectural_terms / max(total_queries, 1), 1.0)
                        ki_factor = ki_score * 0.15
                        
                        # 4. Learning Progression (LP) - 20%
                        # Base progression from milestone completion
                        milestone_progression = (completed_milestones / total_milestones) if total_milestones > 0 else 0
                        lp_factor = milestone_progression * 0.20
                        
                        # 5. Quality factor from grades (15%)
                        quality_factor = (average_grade / 100.0) * 0.15
                        
                        # 6. Engagement factor (20%)
                        engagement_factor = min(len(user_messages) * 0.02, 0.20)  # 2% per question, max 20%
                        
                        # Combine all factors for comprehensive progression
                        progression_score = min(cop_factor + dte_factor + ki_factor + lp_factor + quality_factor + engagement_factor, 1.0)
                    
                    # Store detailed metrics for UI display
                    detailed_metrics = {
                        'completed_milestones': completed_milestones,
                        'total_milestones': total_milestones,
                        'average_grade': average_grade,
                        'milestone_progression': lp_factor * 100,
                        'quality_factor': quality_factor * 100,
                        'engagement_factor': engagement_factor * 100,
                        # Benchmarking metrics
                        'cop_score': cop_score * 100,
                        'dte_score': dte_score * 100,
                        'ki_score': ki_score * 100,
                        'cop_factor': cop_factor * 100,
                        'dte_factor': dte_factor * 100,
                        'ki_factor': ki_factor * 100,
                        'assessment_profile': assessment_profile
                    }
                    
                else:
                    # Fallback to conversation-based progression
                    progression_score = min(len(user_messages) * 0.05, 1.0)  # 5% per question
                    detailed_metrics = {
                        'completed_milestones': 0,
                        'total_milestones': 0,
                        'average_grade': 0,
                        'milestone_progression': 0,
                        'quality_factor': 0,
                        'engagement_factor': progression_score * 100,
                        # Benchmarking metrics (fallback)
                        'cop_score': 0,
                        'dte_score': 0,
                        'ki_score': 0,
                        'cop_factor': 0,
                        'dte_factor': 0,
                        'ki_factor': 0,
                        'assessment_profile': None
                    }
                    
            except Exception as e:
                # Fallback to simple conversation-based progression
                progression_score = min(len(user_messages) * 0.05, 1.0)  # 5% per question
                detailed_metrics = {
                    'completed_milestones': 0,
                    'total_milestones': 0,
                    'average_grade': 0,
                    'milestone_progression': 0,
                    'quality_factor': 0,
                    'engagement_factor': progression_score * 100,
                    # Benchmarking metrics (fallback)
                    'cop_score': 0,
                    'dte_score': 0,
                    'ki_score': 0,
                    'cop_factor': 0,
                    'dte_factor': 0,
                    'ki_factor': 0,
                    'assessment_profile': None
                }
            
            # Estimate phase duration based on milestone completion
            completed_milestones = sum(1 for assessment in current_phase_progress.milestones.values() 
                                     if assessment.is_complete)
            total_milestones = len(current_phase_progress.milestones)
            phase_completion_ratio = completed_milestones / total_milestones if total_milestones > 0 else 0
            
            # Estimate duration (simplified - could be enhanced with actual time tracking)
            estimated_duration = len(user_messages) * 2
            
            return {
                "progression_score": progression_score,
                "phase_duration": estimated_duration,
                "milestone_completion": phase_completion_ratio,
                "completed_milestones": detailed_metrics['completed_milestones'],
                "total_milestones": detailed_metrics['total_milestones'],
                "next_milestone": current_phase_progress.next_milestone.value if current_phase_progress.next_milestone else None,
                "phase_recommendations": current_phase_progress.phase_recommendations,
                # Detailed grading metrics
                "average_grade": detailed_metrics['average_grade'],
                "milestone_progression": detailed_metrics['milestone_progression'],
                "quality_factor": detailed_metrics['quality_factor'],
                "engagement_factor": detailed_metrics['engagement_factor'],
                # Benchmarking metrics
                "cop_score": detailed_metrics['cop_score'],
                "dte_score": detailed_metrics['dte_score'],
                "ki_score": detailed_metrics['ki_score'],
                "cop_factor": detailed_metrics['cop_factor'],
                "dte_factor": detailed_metrics['dte_factor'],
                "ki_factor": detailed_metrics['ki_factor'],
                "assessment_profile": detailed_metrics['assessment_profile']
            }
            
        except ImportError as e:
            print(f"⚠️ Import error in phase progression analysis: {e}")
            # Fallback to old method if new system not available
            return self._fallback_phase_progression(state, current_phase)
        except Exception as e:
            print(f"⚠️ Error in new phase progression analysis: {e}")
            return self._fallback_phase_progression(state, current_phase)
    
    def _fallback_phase_progression(self, state: ArchMentorState, current_phase: str) -> Dict[str, Any]:
        """Fallback to the old progression calculation method"""
        
        # Estimate time spent in current phase
        user_messages = [msg for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) < 2:
            return {"progression_score": 0.5, "phase_duration": 0}
        
        # Calculate progression based on conversation depth and complexity
        early_messages = user_messages[:len(user_messages)//2]
        recent_messages = user_messages[len(user_messages)//2:]
        
        early_complexity = np.mean([len(msg['content'].split()) for msg in early_messages])
        recent_complexity = np.mean([len(msg['content'].split()) for msg in recent_messages])
        
        # Progression score based on complexity increase
        if early_complexity > 0:
            progression_score = min(recent_complexity / early_complexity, 2.0) / 2.0
        else:
            progression_score = 0.5
        
        # Estimate phase duration (simplified)
        phase_duration = len(user_messages) * 2  # Rough estimate: 2 minutes per message
        
        return {
            "progression_score": progression_score,
            "phase_duration": phase_duration,
            "complexity_increase": recent_complexity - early_complexity
        }
    
    def _get_phase_characteristics(self, phase: str) -> Dict[str, Any]:
        """Get characteristics and requirements for the detected phase"""
        
        characteristics = {
            "ideation": {
                "focus": "Conceptual exploration and problem framing",
                "key_activities": ["Site analysis", "Program development", "Concept exploration", "Precedent study"],
                "cognitive_demands": "High-level thinking, synthesis, creativity",
                "typical_duration": "1-3 days",
                "success_indicators": ["Clear concept statement", "Program definition", "Site understanding"]
            },
            "visualization": {
                "focus": "Spatial development and form exploration",
                "key_activities": ["Spatial planning", "Form development", "Circulation design", "Lighting study"],
                "cognitive_demands": "Spatial reasoning, visual thinking, technical drawing",
                "typical_duration": "3-7 days",
                "success_indicators": ["Clear spatial organization", "Form development", "Circulation logic"]
            },
            "materialization": {
                "focus": "Technical development and implementation",
                "key_activities": ["Construction details", "Material specification", "Technical systems", "Cost analysis"],
                "cognitive_demands": "Technical knowledge, detail thinking, practical constraints",
                "typical_duration": "5-10 days",
                "success_indicators": ["Technical feasibility", "Material specification", "Implementation plan"]
            }
        }
        
        return characteristics.get(phase, {})
    
    def _generate_phase_recommendations(self, phase: str, confidence: float) -> List[str]:
        """Generate recommendations based on detected phase and confidence"""
        
        recommendations = []
        
        if confidence < 0.6:
            recommendations.append("Phase detection confidence is low - consider explicit phase clarification")
        
        if phase == "ideation":
            recommendations.extend([
                "Focus on concept development and program definition",
                "Explore precedents and site analysis",
                "Develop clear design philosophy and approach"
            ])
        elif phase == "visualization":
            recommendations.extend([
                "Develop spatial organization and circulation",
                "Explore form and massing relationships",
                "Consider lighting and material qualities"
            ])
        elif phase == "materialization":
            recommendations.extend([
                "Develop construction and technical details",
                "Specify materials and systems",
                "Consider cost and implementation constraints"
            ])
        
        return recommendations
    
    def _calculate_indicator_score(self, messages: List[str], indicators: List[str]) -> float:
        """Calculate indicator score for a set of messages"""
        
        if not messages or not indicators:
            return 0
        
        all_text = ' '.join(messages).lower()
        matches = sum(1 for indicator in indicators if indicator in all_text)
        return matches / len(indicators)
    
    def _detect_milestone_content(self, user_messages: List[Dict], current_phase: str, progress_manager, student_id: str) -> Dict[str, Any]:
        """Detect milestone content in user messages and assess completion"""
        
        from phase_management.milestone_questions import MilestoneType
        
        # Define milestone keywords and content indicators for each milestone
        milestone_indicators = {
            MilestoneType.SITE_ANALYSIS: {
                'keywords': ['site', 'location', 'context', 'surroundings', 'environment', 'climate', 'orientation', 'views', 'access'],
                'concepts': ['site analysis', 'contextual understanding', 'environmental factors', 'site constraints', 'opportunities'],
                'threshold': 3  # Need 3+ indicators to consider milestone addressed
            },
            MilestoneType.PROGRAM_REQUIREMENTS: {
                'keywords': ['program', 'requirements', 'needs', 'functions', 'spaces', 'rooms', 'activities', 'users', 'occupants'],
                'concepts': ['program development', 'functional requirements', 'user needs', 'space requirements', 'activity analysis'],
                'threshold': 3
            },
            MilestoneType.CONCEPT_DEVELOPMENT: {
                'keywords': ['concept', 'idea', 'approach', 'strategy', 'vision', 'philosophy', 'concept development', 'design approach'],
                'concepts': ['conceptual thinking', 'design strategy', 'approach development', 'philosophical framework'],
                'threshold': 2
            },
            MilestoneType.SPATIAL_ORGANIZATION: {
                'keywords': ['spatial', 'organization', 'layout', 'arrangement', 'planning', 'zoning', 'relationships', 'adjacencies'],
                'concepts': ['spatial organization', 'layout planning', 'functional zoning', 'spatial relationships'],
                'threshold': 3
            },
            MilestoneType.CIRCULATION_DESIGN: {
                'keywords': ['circulation', 'movement', 'flow', 'paths', 'corridors', 'stairs', 'elevators', 'accessibility'],
                'concepts': ['circulation design', 'movement patterns', 'accessibility', 'flow planning'],
                'threshold': 3
            },
            MilestoneType.FORM_DEVELOPMENT: {
                'keywords': ['form', 'shape', 'massing', 'volume', 'geometry', 'aesthetics', 'appearance', 'expression'],
                'concepts': ['form development', 'massing studies', 'geometric exploration', 'aesthetic expression'],
                'threshold': 2
            },
            MilestoneType.LIGHTING_STRATEGY: {
                'keywords': ['lighting', 'light', 'natural light', 'artificial light', 'illumination', 'daylight', 'shadows'],
                'concepts': ['lighting strategy', 'natural lighting', 'artificial lighting', 'lighting design'],
                'threshold': 2
            },
            MilestoneType.CONSTRUCTION_SYSTEMS: {
                'keywords': ['construction', 'structure', 'materials', 'building systems', 'structural', 'assembly'],
                'concepts': ['construction systems', 'structural design', 'material selection', 'building assembly'],
                'threshold': 3
            },
            MilestoneType.MATERIAL_SELECTION: {
                'keywords': ['materials', 'material', 'finishes', 'texture', 'color', 'durability', 'sustainability'],
                'concepts': ['material selection', 'finish specification', 'material properties', 'sustainability'],
                'threshold': 2
            },
            MilestoneType.TECHNICAL_DETAILS: {
                'keywords': ['details', 'technical', 'specifications', 'construction details', 'junctions', 'connections'],
                'concepts': ['technical detailing', 'construction details', 'specification', 'detail design'],
                'threshold': 2
            },
            MilestoneType.PRESENTATION_PREP: {
                'keywords': ['presentation', 'communication', 'drawings', 'renderings', 'documentation', 'visualization'],
                'concepts': ['presentation preparation', 'communication strategy', 'visual documentation'],
                'threshold': 2
            },
            MilestoneType.DOCUMENTATION: {
                'keywords': ['documentation', 'drawings', 'plans', 'sections', 'elevations', 'specifications', 'contract documents'],
                'concepts': ['documentation', 'drawing preparation', 'contract documents', 'specifications'],
                'threshold': 3
            }
        }
        
        # Get current phase milestones
        phase_milestones = progress_manager.phase_structure.get(current_phase, {}).get('milestones', [])
        
        detection_results = {}
        
        for milestone in phase_milestones:
            if milestone not in milestone_indicators:
                continue
                
            indicators = milestone_indicators[milestone]
            threshold = indicators['threshold']
            
            # Analyze user messages for milestone content
            keyword_count = 0
            concept_count = 0
            detailed_responses = 0
            
            for msg in user_messages:
                content = msg.get('content', '').lower()
                
                # Count keyword matches
                for keyword in indicators['keywords']:
                    if keyword in content:
                        keyword_count += 1
                
                # Count concept matches
                for concept in indicators['concepts']:
                    if concept in content:
                        concept_count += 1
                
                # Check for detailed responses (longer, more thoughtful)
                if len(content.split()) > 20:  # Detailed response threshold
                    detailed_responses += 1
            
            # Calculate completion score
            total_indicators = keyword_count + concept_count + detailed_responses
            completion_score = min(total_indicators / threshold, 1.0)
            
            # Determine if milestone is sufficiently addressed
            is_addressed = completion_score >= 0.7  # 70% threshold
            
            detection_results[milestone] = {
                'completion_score': completion_score,
                'is_addressed': is_addressed,
                'keyword_count': keyword_count,
                'concept_count': concept_count,
                'detailed_responses': detailed_responses,
                'total_indicators': total_indicators,
                'threshold': threshold
            }
        
        return detection_results
    
    def _update_milestone_progress_from_conversation(self, milestone_detection: Dict, progress_manager, student_id: str, current_phase: str):
        """Update progress manager with detected milestone completions"""
        
        from phase_management.milestone_questions import MilestoneType
        from phase_management.progress_manager import GradingResult
        
        # Get current phase milestones
        phase_milestones = progress_manager.phase_structure.get(current_phase, {}).get('milestones', [])
        
        for milestone in phase_milestones:
            if milestone not in milestone_detection:
                continue
                
            detection = milestone_detection[milestone]
            
            if detection['is_addressed']:
                # Create a grading result based on detection quality
                completion_score = detection['completion_score']
                
                # Convert completion score to grade (0-100)
                grade = int(completion_score * 100)
                
                # Create grading result
                grading_result = GradingResult(
                    completeness=completion_score * 5,  # Convert to 0-5 scale
                    depth=completion_score * 5,
                    relevance=completion_score * 5,
                    innovation=completion_score * 5,
                    technical_understanding=completion_score * 5,
                    overall_score=completion_score * 5,
                    strengths=[f"Demonstrated understanding of {milestone.value.replace('_', ' ')}"],
                    weaknesses=[],
                    recommendations=[]
                )
                
                # Record the response in progress manager
                question_id = f"auto_detected_{milestone.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                response_text = f"Automatically detected milestone completion through conversation analysis. Score: {grade}/100"
                
                try:
                    progress_manager.record_response(
                        student_id=student_id,
                        milestone=milestone,
                        question_id=question_id,
                        response=response_text,
                        grade=grading_result
                    )
                except Exception as e:
                    print(f"Warning: Could not record milestone response: {e}")
    
    def _generate_milestone_question_if_needed(self, state: ArchMentorState, current_phase: str, progress_manager, student_id: str) -> Optional[str]:
        """Generate a milestone question if needed based on conversation gaps"""
        
        from phase_management.milestone_questions import MilestoneType
        
        # Get current phase milestones
        phase_milestones = progress_manager.phase_structure.get(current_phase, {}).get('milestones', [])
        
        # Check which milestones need attention
        profile = progress_manager.get_assessment_profile(student_id)
        if not profile:
            return None
            
        current_phase_progress = profile.phases.get(current_phase)
        if not current_phase_progress:
            return None
        
        # Find milestones with low completion
        low_completion_milestones = []
        for milestone in phase_milestones:
            milestone_assessment = current_phase_progress.milestones.get(milestone)
            if not milestone_assessment or milestone_assessment.completion_percentage < 0.5:
                low_completion_milestones.append(milestone)
        
        if not low_completion_milestones:
            return None
        
        # Select the milestone with lowest completion
        target_milestone = min(low_completion_milestones, 
                             key=lambda m: current_phase_progress.milestones.get(m, {}).completion_percentage if current_phase_progress.milestones.get(m) else 0)
        
        # Generate a question for this milestone
        question = self._generate_milestone_question(target_milestone)
        
        return question
    
    def _generate_milestone_question(self, milestone: MilestoneType) -> str:
        """Generate a specific question for a milestone"""
        
        question_templates = {
            MilestoneType.SITE_ANALYSIS: "How have you analyzed the site context and environmental factors for your project?",
            MilestoneType.PROGRAM_REQUIREMENTS: "What are the key functional requirements and user needs for your building?",
            MilestoneType.CONCEPT_DEVELOPMENT: "What is your main design concept or approach for this project?",
            MilestoneType.SPATIAL_ORGANIZATION: "How are you organizing the spaces and functional relationships in your design?",
            MilestoneType.CIRCULATION_DESIGN: "How are you designing the movement and circulation patterns?",
            MilestoneType.FORM_DEVELOPMENT: "How are you developing the form and massing of your building?",
            MilestoneType.LIGHTING_STRATEGY: "What is your approach to natural and artificial lighting?",
            MilestoneType.CONSTRUCTION_SYSTEMS: "What construction systems and structural approach are you considering?",
            MilestoneType.MATERIAL_SELECTION: "What materials and finishes are you planning to use?",
            MilestoneType.TECHNICAL_DETAILS: "How are you addressing technical details and construction junctions?",
            MilestoneType.PRESENTATION_PREP: "How are you preparing to communicate your design?",
            MilestoneType.DOCUMENTATION: "What documentation and drawings are you developing?"
        }
        
        return question_templates.get(milestone, f"Tell me about your approach to {milestone.value.replace('_', ' ')}")

# Test function
async def test_analysis_agent():
    print("🧪 Testing Analysis Agent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with accessible entrances, flexible meeting spaces, and a commercial kitchen for community events"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Add some user messages for skill detection
    state.messages.extend([
        {"role": "user", "content": "How do I design accessibility into my building?"},
        {"role": "user", "content": "I want to create spaces that everyone can use"}
    ])
    
    # Create agent
    agent = AnalysisAgent("architecture")
    
    # Test analysis
    result = await agent.process(state)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Skill Assessment: {result['skill_assessment']}")
    print(f"   Building type: {result.get('text_analysis', {}).get('building_type', 'unknown')}")
    print(f"   Cognitive flags: {result.get('cognitive_flags', [])}")
    print(f"   Final skill level: {state.student_profile.skill_level}")
    
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_analysis_agent())