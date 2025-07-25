#This is the analysis agent for the ArchMentor system
# It performs dynamic skill assessment, visual and text analysis, and synthesizes findings for cognitive enhancement
from typing import Dict, Any, List
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.sketch_analyzer import SketchAnalyzer
from state_manager import ArchMentorState, StudentProfile, VisualArtifact
from knowledge_base.knowledge_manager import KnowledgeManager

class AnalysisAgent:
    def __init__(self, domain="architecture"):
        self.domain = domain
        self.sketch_analyzer = SketchAnalyzer(domain)
        self.knowledge_manager = KnowledgeManager(domain)
        self.name = "analysis_agent"
        print(f"🔍 {self.name} initialized for domain: {domain}")
    
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
    
    async def process(self, state: ArchMentorState) -> Dict[str, Any]:
        """Main analysis processing with dynamic skill assessment"""
        
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
        
        # Analyze visual input if provided
        if current_sketch and current_sketch.image_path:
            try:
                print(f"📸 Analyzing image: {current_sketch.image_path}")
                visual_analysis = await self.sketch_analyzer.analyze_sketch(
                    current_sketch.image_path,
                    context=design_brief
                )
                analysis_result["visual_analysis"] = visual_analysis
                analysis_result["confidence_score"] = visual_analysis.get("confidence_score", 0.5)
                
                # Extract key insights from visual analysis
                insights = []
                if visual_analysis.get("design_strengths"):
                    insights.extend([f"Strength: {s}" for s in visual_analysis["design_strengths"][:2]])
                if visual_analysis.get("improvement_opportunities"):
                    insights.extend([f"Opportunity: {o}" for o in visual_analysis["improvement_opportunities"][:2]])
                
                analysis_result["key_insights"] = insights
                print(f"✅ Visual analysis complete. Found {len(insights)} key insights")
                
            except Exception as e:
                print(f"❌ Visual analysis failed: {e}")
                analysis_result["visual_analysis"] = {"error": str(e)}
        else:
            print("📷 No visual artifact provided")
        
        # Analyze text brief
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
        
        # Generate cognitive flags for other agents
        cognitive_flags = self.generate_cognitive_flags(analysis_result, state.student_profile)
        analysis_result["cognitive_flags"] = cognitive_flags
        
        print(f"🎯 Analysis complete! Confidence: {analysis_result['confidence_score']}")
        print(f"🚩 Generated {len(cognitive_flags)} cognitive flags for other agents")
        
        # Enhance analysis with knowledge base
        if analysis_result["visual_analysis"] and not analysis_result["visual_analysis"].get("error"):
            enhanced_analysis = await self.enhance_with_knowledge(
                analysis_result["visual_analysis"], 
                state.current_design_brief
            )
            analysis_result["knowledge_enhanced"] = enhanced_analysis
        
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
        """Analyze the textual design brief for key information"""
        
        # Program type detection
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
            }
        }
        
        # Identify building type and requirements
        building_type = "unknown"
        requirements = []
        considerations = []
        
        brief_lower = brief.lower()
        for btype, info in program_keywords.items():
            if btype in brief_lower:
                building_type = btype
                requirements = info["requirements"]
                considerations = info["considerations"]
                break
        
        # Extract numbers and quantities
        numbers = re.findall(r'\d+', brief)
        
        # Extract constraints and requirements
        constraint_keywords = ["budget", "sustainable", "accessible", "limited", "small", "large", 
                             "affordable", "green", "net-zero", "LEED", "ADA"]
        constraints = [kw for kw in constraint_keywords if kw in brief_lower]
        
        # Assess brief complexity
        word_count = len(brief.split())
        complexity = "simple" if word_count < 20 else "detailed" if word_count < 50 else "comprehensive"
        
        return {
            "building_type": building_type,
            "program_requirements": requirements,
            "design_considerations": considerations,
            "numbers_mentioned": numbers,
            "constraints": constraints,
            "word_count": word_count,
            "complexity": complexity,
            "detail_level": self.assess_detail_level(brief)
        }
    
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
    def generate_cognitive_flags(self, analysis_result: Dict, student_profile: StudentProfile) -> List[str]:
        """Generate flags for other agents about student's cognitive state"""
        
        flags = []
        
        # Check confidence level
        confidence = analysis_result.get("confidence_score", 0.5)
        if confidence < 0.3:
            flags.append("low_confidence_analysis")
        
        # Check cognitive challenges from synthesis
        synthesis = analysis_result.get("synthesis", {})
        challenges = synthesis.get("cognitive_challenges", [])
        
        if "accessibility_awareness" in challenges:
            flags.append("needs_accessibility_guidance")
        
        if "spatial_relationships" in challenges:
            flags.append("needs_spatial_thinking_support")
        
        if "brief_development" in challenges:
            flags.append("needs_brief_clarification")
        
        # SKILL-BASED FLAGS
        skill_level = student_profile.skill_level
        text_analysis = analysis_result.get("text_analysis", {})
        
        if skill_level == "beginner":
            flags.append("needs_basic_guidance")
            # Beginners with complex projects need extra support
            if text_analysis.get("complexity") in ["detailed", "comprehensive"]:
                flags.append("needs_brief_simplification")
            # Always guide beginners on accessibility
            if text_analysis.get("building_type") in ["community center", "school", "library"]:
                flags.append("needs_accessibility_guidance")
        
        elif skill_level == "intermediate":
            flags.append("needs_brief_clarification")
            flags.append("needs_spatial_thinking_support")
            # Check if they're ready for advanced concepts
            if text_analysis.get("detail_level") in ["highly_detailed", "moderately_detailed"]:
                flags.append("ready_for_systems_thinking")
        
        elif skill_level == "advanced":
            flags.append("needs_systems_thinking_challenge")
            flags.append("ready_for_advanced_challenge")
            # Advanced students with simple briefs might be disengaged
            if text_analysis.get("complexity") == "simple":
                flags.append("needs_complexity_increase")
        
        # PROJECT-SPECIFIC FLAGS
        building_type = text_analysis.get("building_type", "unknown")
        
        if building_type == "community center":
            flags.append("needs_accessibility_guidance")
            flags.append("needs_public_space_consideration")
        
        if building_type in ["housing", "residential"]:
            flags.append("needs_privacy_consideration")
        
        if building_type in ["school", "educational"]:
            flags.append("needs_safety_consideration")
        
        # Check for missing requirements
        missing_considerations = synthesis.get("missing_considerations", [])
        if missing_considerations:
            flags.append("needs_program_clarification")
        
        # Check for cognitive readiness
        if not challenges and synthesis.get("alignment_assessment", {}).get("status") == "good":
            flags.append("ready_for_advanced_challenge")
        
        # Skill-complexity mismatch
        if skill_level == "beginner" and text_analysis.get("complexity") == "comprehensive":
            flags.append("complexity_mismatch_high")
        elif skill_level == "advanced" and text_analysis.get("complexity") == "simple":
            flags.append("complexity_mismatch_low")
        
        print(f"   🚩 Generated flags: {flags}")
        
        # Remove duplicates while preserving order
        unique_flags = []
        for flag in flags:
            if flag not in unique_flags:
                unique_flags.append(flag)
        
        return unique_flags  # Return deduplicated flags

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