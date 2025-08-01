# Compact Analysis Agent for ArchMentor System
from typing import Dict, Any, List
import sys, os, re, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.sketch_analyzer import SketchAnalyzer
from state_manager import ArchMentorState, StudentProfile
from knowledge_base.knowledge_manager import KnowledgeManager

class AnalysisAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.sketch_analyzer = SketchAnalyzer(domain)
        self.knowledge_manager = KnowledgeManager(domain)
        self.name = "analysis_agent"
        
        # Compact phase definitions
        self.phases = {
            "ideation": {"next": "visualization", "activities": ["site analysis", "program development"]},
            "visualization": {"next": "materialization", "activities": ["spatial planning", "form development"]},
            "materialization": {"next": "completion", "activities": ["construction details", "material specification"]},
            "completion": {"next": None, "activities": ["final details", "presentation"]}
        }
        
        print(f"🔍 {self.name} initialized")

    async def process(self, state: ArchMentorState, context_package: Dict = None) -> Dict[str, Any]:
        """Main analysis processing - compact and efficient"""
        
        print(f"\n🚀 {self.name} starting analysis...")
        
        # Get student messages for analysis
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        combined_input = " ".join(user_messages).lower()
        
        print(f"📝 Analyzing {len(user_messages)} user messages")
        print(f"📝 Combined input: {combined_input[:100]}...")
        
        # Quick skill assessment
        skill_level = self._assess_skill(combined_input)
        if skill_level != state.student_profile.skill_level:
            state.student_profile.skill_level = skill_level
            print(f"📊 Skill level updated: {skill_level}")
        
        # Unified LLM analysis
        print("🧠 Starting LLM analysis...")
        llm_analysis = await self._analyze_with_llm(state, combined_input)
        
        # Debug phase analysis
        phase_analysis = llm_analysis.get("phase_analysis", {})
        current_phase = phase_analysis.get("current_phase", "unknown")
        phase_completion = phase_analysis.get("phase_completion", 0)
        
        # Calculate confidence based on response quality
        confidence = self._calculate_phase_confidence(llm_analysis, phase_analysis)
        phase_analysis["confidence"] = confidence
        
        print(f"🎯 Phase analysis result: {current_phase} ({phase_completion}% complete, {confidence:.2f} confidence)")
        
        # Visual analysis if available
        visual_analysis = {}
        if state.current_sketch:
            try:
                print("🖼️ Analyzing visual content...")
                visual_analysis = await self.sketch_analyzer.analyze_sketch(
                    state.current_sketch, state.current_design_brief
                )
                print(f"✅ Visual analysis complete")
            except Exception as e:
                visual_analysis = {"error": str(e)}
                print(f"⚠️ Visual analysis failed: {e}")
        else:
            print("📝 No visual content to analyze")
        
        # Knowledge enhancement
        knowledge_enhanced = {}
        if visual_analysis and not visual_analysis.get("error"):
            knowledge_enhanced = await self._enhance_with_knowledge(visual_analysis, state.current_design_brief)
        
        # Build result
        result = {
            "agent": self.name,
            "domain": self.domain,
            "visual_analysis": visual_analysis,
            "text_analysis": llm_analysis.get("text_analysis", {}),
            "synthesis": llm_analysis.get("synthesis", {}),
            "confidence_score": confidence,  # Use phase confidence as overall confidence
            "cognitive_flags": llm_analysis.get("cognitive_flags", []),
            "phase_analysis": phase_analysis,  # Ensure this is included with confidence
            "skill_assessment": {
                "detected_level": skill_level,
                "previous_level": state.student_profile.skill_level,
                "updated": skill_level != state.student_profile.skill_level,
                "confidence": min(len(user_messages) / 5, 1.0)
            },
            "knowledge_enhanced": knowledge_enhanced
        }
        
        # Add context insights if available
        if context_package:
            result = self._add_context_insights(result, context_package)
        
        print(f"✅ Analysis complete! Phase: {current_phase}, Flags: {len(result['cognitive_flags'])}, Confidence: {confidence:.2f}")
        return result

    async def _analyze_with_llm(self, state: ArchMentorState, combined_input: str) -> Dict[str, Any]:
        """Unified LLM analysis - single call for multiple insights"""
        
        # Handle edge cases first
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if not user_messages or len(combined_input.strip()) < 5:
            print("📝 Using edge case handler for short/empty input")
            return self._handle_edge_cases(state)
        
        recent_messages = state.messages[-10:] if len(state.messages) > 10 else state.messages
        conversation_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in recent_messages])
        
        # Simplified, more focused prompt
        prompt = f"""
        Analyze this architectural design conversation and determine the current design phase.

        CONVERSATION: {conversation_text}
        PROJECT: {state.current_design_brief}
        STUDENT INPUT: {combined_input}

        Based on the conversation and project brief, determine:
        1. Current design phase: ideation, visualization, materialization, or completion
        2. Phase completion percentage (0-100)
        3. Building type from the project brief (be specific: office building, community center, residential, etc.)
        4. Main cognitive challenges the student faces

        IMPORTANT: For building type, look at the project brief and identify the specific type of building being designed.
        Examples: "office building", "community center", "residential house", "school", "hospital", "museum", etc.

        Return ONLY valid JSON in this exact format (no markdown formatting):
        {{
            "phase_analysis": {{
                "current_phase": "ideation",
                "phase_completion": 75
            }},
            "text_analysis": {{
                "building_type": "office building",
                "program_requirements": ["meeting rooms", "kitchen"]
            }},
            "synthesis": {{
                "cognitive_challenges": ["needs_program_development"]
            }},
            "cognitive_flags": ["needs_program_development", "needs_brief_clarification"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,  # Increased from 300 to prevent cut-off responses
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"🔍 LLM Response: {response_text[:200]}...")  # Debug output
            
            # Clean the response text - remove markdown formatting if present
            cleaned_response = self._extract_json_from_response(response_text)
            
            analysis = json.loads(cleaned_response)
            
            # Validate the response structure
            if not analysis.get("phase_analysis") or not analysis["phase_analysis"].get("current_phase"):
                print("⚠️ LLM response missing phase_analysis structure")
                return self._fallback_analysis(state)
            
            current_phase = analysis["phase_analysis"]["current_phase"]
            phase_completion = analysis["phase_analysis"].get("phase_completion", 15)  # More conservative default
            
            # Validate phase is one of the expected values
            valid_phases = ["ideation", "visualization", "materialization", "completion"]
            if current_phase not in valid_phases:
                print(f"⚠️ Invalid phase detected: {current_phase}, using fallback")
                current_phase = "ideation"
                phase_completion = 15  # More conservative default
            
            # Ensure building type is detected - add fallback if needed
            text_analysis = analysis.get("text_analysis", {})
            building_type = text_analysis.get("building_type", "unknown")
            
            # Fallback building type detection if LLM didn't detect it
            if building_type == "unknown" or not building_type:
                building_type = self._detect_building_type_fallback(state.current_design_brief)
                text_analysis["building_type"] = building_type
                analysis["text_analysis"] = text_analysis
                print(f"🔍 Fallback building type detection: {building_type}")
            
            # Calculate confidence
            confidence = self._calculate_phase_confidence(analysis, analysis["phase_analysis"])
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"⚠️ Raw response: {response_text}")
            return self._fallback_analysis(state)
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
            return self._fallback_analysis(state)
    
    def _detect_building_type_fallback(self, design_brief: str) -> str:
        """Fallback building type detection using keyword matching"""
        brief_lower = design_brief.lower()
        
        # Building type keywords
        building_types = {
            "office": ["office", "workplace", "corporate", "business", "tech company", "employees"],
            "community center": ["community", "center", "gathering", "social", "public space"],
            "residential": ["house", "home", "residential", "apartment", "housing", "dwelling"],
            "school": ["school", "education", "learning", "classroom", "academic"],
            "hospital": ["hospital", "medical", "healthcare", "clinic", "treatment"],
            "museum": ["museum", "gallery", "exhibition", "art", "cultural"],
            "hotel": ["hotel", "lodging", "accommodation", "guest", "visitor"],
            "restaurant": ["restaurant", "dining", "food", "cafe", "kitchen"],
            "library": ["library", "books", "reading", "study", "research"],
            "theater": ["theater", "performance", "stage", "auditorium", "entertainment"]
        }
        
        # Count matches for each building type
        scores = {}
        for building_type, keywords in building_types.items():
            score = sum(1 for keyword in keywords if keyword in brief_lower)
            if score > 0:
                scores[building_type] = score
        
        # Return the building type with the highest score
        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            return best_match[0]
        
        # Default fallback
        return "mixed-use building"

    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from response, handling markdown formatting"""
        
        # Remove markdown code blocks if present
        if "```json" in response_text:
            # Extract content between ```json and ```
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end != -1:
                return response_text[start:end].strip()
        
        # Remove markdown code blocks without language specifier
        if "```" in response_text:
            # Extract content between ``` and ```
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end != -1:
                return response_text[start:end].strip()
        
        # If no markdown formatting, return as is
        return response_text.strip()

    def _assess_skill(self, combined_input: str) -> str:
        """Quick skill assessment from keywords"""
        
        beginner = ["don't know", "confused", "help", "what is", "how do", "basic", "simple", "first time"]
        advanced = ["parti", "phenomenology", "tectonics", "typology", "morphology", "zoning", "egress", 
                   "life safety", "building codes", "structural systems", "LEED", "passive design"]
        
        if any(phrase in combined_input for phrase in advanced):
            return "advanced"
        elif any(phrase in combined_input for phrase in beginner):
            return "beginner"
        else:
            return "intermediate"

    async def _enhance_with_knowledge(self, visual_analysis: Dict, design_brief: str) -> Dict:
        """Enhance analysis with knowledge base"""
        elements = visual_analysis.get('identified_elements', [])
        search_query = f"{design_brief} {' '.join(elements[:3])}"
        knowledge_results = self.knowledge_manager.search_knowledge(search_query, n_results=3)
        
        return {
            "relevant_knowledge": knowledge_results,
            "knowledge_enhanced": bool(knowledge_results)
        } if knowledge_results else {"knowledge_enhanced": False}

    def _add_context_insights(self, result: Dict, context_package: Dict) -> Dict:
        """Add context insights for continuity"""
        patterns = context_package.get("conversation_patterns", {})
        
        if patterns.get("repetitive_topics"):
            result["cognitive_flags"].append("stuck_on_topic")
        if patterns.get("understanding_progression") == "progressing":
            result["cognitive_flags"].append("showing_growth")
        
        return result
    
    def _fallback_analysis(self, state: ArchMentorState) -> Dict[str, Any]:
        """Fallback analysis when LLM fails"""
        
        # Use fallback building type detection
        building_type = self._detect_building_type_fallback(state.current_design_brief)
        
        return {
            "phase_analysis": {
                "current_phase": "ideation",
                "phase_completion": 15,  # More conservative early stage
                "confidence": 0.2,  # Very low confidence for fallback
                "overall_progress": 3.75
            },
            "text_analysis": {
                "building_type": building_type,
                "program_requirements": [],
                "complexity": "simple"
            },
            "synthesis": {
                "cognitive_challenges": ["needs_brief_clarification"],
                "learning_opportunities": ["Develop project understanding", "Explore design principles"]
            },
            "cognitive_flags": ["needs_brief_clarification"],
            "confidence_score": 0.2
        }

    def _handle_edge_cases(self, state: ArchMentorState) -> Dict[str, Any]:
        """Handle edge cases like empty conversations or very short inputs"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        # If no user messages, return default ideation phase
        if not user_messages:
            return {
                "phase_analysis": {
                    "current_phase": "ideation",
                    "phase_completion": 5,  # Very early stage
                    "confidence": 0.2,
                    "overall_progress": 1.25
                },
                "text_analysis": {
                    "building_type": "unknown",
                    "program_requirements": [],
                    "complexity": "unknown"
                },
                "synthesis": {
                    "cognitive_challenges": ["needs_project_start"],
                    "learning_opportunities": ["Begin with project definition"],
                    "next_focus_areas": ["project_setup"]
                },
                "cognitive_flags": ["needs_project_start"]
            }
        
        # If very short input, use keyword-based phase detection
        combined_input = " ".join(user_messages).lower()
        
        # More conservative keyword-based phase detection for edge cases
        if any(word in combined_input for word in ["start", "begin", "first", "new", "what", "help", "how"]):
            phase = "ideation"
            completion = 10  # Early ideation
        elif any(word in combined_input for word in ["layout", "plan", "arrange", "space", "room", "design"]):
            phase = "visualization"
            completion = 25  # Early visualization
        elif any(word in combined_input for word in ["material", "construction", "detail", "build", "technical"]):
            phase = "materialization"
            completion = 45  # Early materialization
        elif any(word in combined_input for word in ["finish", "complete", "present", "final", "done"]):
            phase = "completion"
            completion = 75  # Early completion
        else:
            # Default to very early ideation for unclear inputs
            phase = "ideation"
            completion = 8  # Very early stage
        
        return {
            "phase_analysis": {
                "current_phase": phase,
                "phase_completion": completion,
                "confidence": 0.3,  # Lower confidence for keyword-based detection
                "overall_progress": completion * 0.25
            },
            "text_analysis": {
                "building_type": "mixed-use",
                "program_requirements": [],
                "complexity": "simple"
            },
            "synthesis": {
                "cognitive_challenges": ["needs_brief_clarification"],
                "learning_opportunities": ["Develop project understanding"],
                "next_focus_areas": ["socratic_questioning"]
            },
            "cognitive_flags": ["needs_brief_clarification"]
        }

    def _calculate_phase_confidence(self, llm_analysis: Dict, phase_analysis: Dict) -> float:
        """Calculate confidence in phase detection based on response quality"""
        
        confidence = 0.5  # Base confidence
        
        # Check if we have a valid phase
        current_phase = phase_analysis.get("current_phase", "unknown")
        if current_phase != "unknown" and current_phase in ["ideation", "visualization", "materialization", "completion"]:
            confidence += 0.3
        
        # Check if we have phase completion
        if phase_analysis.get("phase_completion") is not None:
            confidence += 0.1
        
        # Check if we have cognitive flags
        if llm_analysis.get("cognitive_flags"):
            confidence += 0.1
        
        # Check if we have text analysis
        if llm_analysis.get("text_analysis", {}).get("building_type"):
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0

    # Utility methods for external use
    async def get_phase_guidance(self, state: ArchMentorState) -> Dict[str, Any]:
        """Get guidance for current phase"""
        analysis = await self._analyze_with_llm(state, "")
        current_phase = analysis["phase_analysis"]["current_phase"]
        completion = analysis["phase_analysis"]["phase_completion"]
        
        if completion < 30:
            message = f"Begin {current_phase} phase. Focus on: {', '.join(self.phases[current_phase]['activities'][:2])}"
        elif completion < 70:
            message = f"Continue developing {current_phase}. Consider: {', '.join(self.phases[current_phase]['activities'][2:])}"
        elif completion < 90:
            message = f"Almost ready to complete {current_phase} phase."
        else:
            next_phase = self.phases[current_phase]["next"]
            message = f"Ready to move to {next_phase}!" if next_phase else "Excellent! All phases complete."
        
        return {
            "current_phase": current_phase,
            "phase_completion": completion,
            "message": message,
            "next_phase": self.phases[current_phase]["next"]
        }