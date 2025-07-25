# This is socratic tutor agent
# It generates Socratic questions to guide users.
import sys
from typing import Dict, Any, List
import os
from openai import OpenAI
from dotenv import load_dotenv
# Add parent directory to path to import from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState  

load_dotenv()

class SocraticTutorAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "socratic_tutor"
        
        # Question templates for different cognitive gaps
        self.question_strategies = {
            "accessibility_awareness": {
                "discovery_questions": [
                    "I notice your entrance design. Can you walk me through how different people might access your building?",
                    "What do you think someone using a wheelchair would experience when approaching your entrance?",
                    "How might parents with strollers navigate your design?",
                ],
                "follow_up_prompts": [
                    "What building codes might apply here?",
                    "Can you think of any barriers you might have unintentionally created?",
                    "How could you test if your design is truly accessible?"
                ]
            },
            
            "spatial_relationships": {
                "discovery_questions": [
                    "I'm curious about the flow between your spaces. Can you walk me through a visitor's journey from entrance to exit?",
                    "How do you imagine the different spaces in your building will relate to each other?",
                    "What happens when someone needs to move from the main space to the restrooms?",
                ],
                "follow_up_prompts": [
                    "What activities might create conflicts in circulation?",
                    "How might noise from one area affect adjacent spaces?",
                    "Where do you expect people to naturally gather or pause?"
                ]
            },
            
            "brief_development": {
                "discovery_questions": [
                    "Tell me more about who will be using this space. What are their specific needs?",
                    "What activities do you envision happening in your design?",
                    "How many people need to use this space at once? What does that mean for your design?",
                ],
                "follow_up_prompts": [
                    "What constraints might you be forgetting about?",
                    "How will your design handle different times of day or seasons?",
                    "What support spaces might these activities require?"
                ]
            },
            
            "systems_thinking": {
                "discovery_questions": [
                    "How do you think the building systems (heating, lighting, ventilation) might influence your design?",
                    "What happens to your design in different weather conditions?",
                    "How might your design perform over time - in 5 or 10 years?",
                ],
                "follow_up_prompts": [
                    "What maintenance considerations might affect your choices?",
                    "How do your material choices connect to your design goals?",
                    "What environmental factors should influence your design?"
                ]
            }
        }
        
        print(f"🤔 {self.name} initialized for domain: {domain}")
    
    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Socratic response based on cognitive flags"""
        
        print(f"\n🤔 {self.name} generating Socratic response...")
        
        # Get cognitive flags from analysis
        cognitive_flags = analysis_result.get('cognitive_flags', [])
        synthesis = analysis_result.get('synthesis', {})
        visual_analysis = analysis_result.get('visual_analysis', {})
        text_analysis = analysis_result.get('text_analysis', {})
        
        print(f"📋 Processing {len(cognitive_flags)} cognitive flags")
        
        # Determine primary cognitive gap to address
        primary_gap = self.identify_primary_gap(cognitive_flags, synthesis)
        print(f"🎯 Primary cognitive gap: {primary_gap}")
        
        # Generate contextual Socratic question
        socratic_response = await self.craft_contextual_question(
            primary_gap, 
            analysis_result, 
            state
        )
        
        # Determine follow-up strategy
        follow_up_strategy = self.plan_follow_up(cognitive_flags, state.student_profile)
        
        response_data = {
            "agent": self.name,
            "primary_gap_addressed": primary_gap,
            "question_type": socratic_response.get("type", "discovery"),
            "response_text": socratic_response.get("text", ""),
            "pedagogical_intent": socratic_response.get("intent", ""),
            "follow_up_strategy": follow_up_strategy,
            "cognitive_flags_processed": cognitive_flags
        }
        
        print(f"✅ Generated {socratic_response.get('type', 'unknown')} question")
        print(f"🎯 Intent: {socratic_response.get('intent', 'guide discovery')}")
        
        return response_data
    
    def identify_primary_gap(self, cognitive_flags: List[str], synthesis: Dict) -> str:
        """Identify the most important cognitive gap to address first"""
        
        # Priority order for addressing cognitive gaps
        gap_priority = {
            "needs_brief_clarification": 1,  # Foundation first
            "needs_accessibility_guidance": 2,  # Safety/legal requirements
            "needs_spatial_thinking_support": 3,  # Core design skill
            "low_confidence_analysis": 4,  # Build confidence
            "complexity_mismatch_high": 5,  # Adjust difficulty
            "complexity_mismatch_low": 6   # Challenge appropriately
        }
        
        # Find highest priority gap
        relevant_gaps = []
        for flag in cognitive_flags:
            if flag in gap_priority:
                relevant_gaps.append((flag, gap_priority[flag]))
        
        if relevant_gaps:
            # Sort by priority and return highest priority gap
            relevant_gaps.sort(key=lambda x: x[1])
            primary_gap = relevant_gaps[0][0]
        else:
            # Default to spatial thinking if no specific flags
            primary_gap = "spatial_relationships"
        
        # Map flags to question categories
        gap_mapping = {
            "needs_accessibility_guidance": "accessibility_awareness",
            "needs_spatial_thinking_support": "spatial_relationships", 
            "needs_brief_clarification": "brief_development",
            "low_confidence_analysis": "brief_development",
            "complexity_mismatch_high": "brief_development",
            "complexity_mismatch_low": "systems_thinking"
        }
        
        return gap_mapping.get(primary_gap, "spatial_relationships")
    

    # Craft a contextual Socratic question based on the primary gap ENHANCED I HOPE
    async def craft_contextual_question(self, gap_type: str, analysis_result: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Generate a contextual Socratic question using GPT-4"""

        # Get conversation history for context
        recent_messages = state.messages[-3:] if len(state.messages) > 3 else state.messages
        conversation_context = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in recent_messages
        ])

        # Get visual context
        visual_context = self.extract_visual_context(analysis_result.get('visual_analysis', {}))
        text_context = analysis_result.get('text_analysis', {})
        student_level = state.student_profile.skill_level

        # Build better context for GPT-4
        context_prompt = f"""
        You are a Socratic tutor for architecture students. Your role is to ask guiding questions that help students discover insights themselves.

        CURRENT CONVERSATION CONTEXT:
        {conversation_context}

        STUDENT'S PROJECT: {state.current_design_brief}
        BUILDING TYPE: {text_context.get('building_type', 'unknown')}
        STUDENT LEVEL: {student_level}
        
        VISUAL OBSERVATIONS: {visual_context}
        COGNITIVE GAP TO ADDRESS: {gap_type}
        
        IMPORTANT GUIDELINES:
        1. ASK QUESTIONS that directly relate to what the student just said
        2. BUILD ON their previous responses - don't ignore their input
        3. If they asked about "central space enhancement", focus on that topic
        4. Don't repeat the same question type multiple times
        5. Reference their specific project context
        6. Guide them toward discovering the missing consideration ({gap_type})
        
        Generate ONE specific, contextual question that:
        - Directly addresses what the student just asked about
        - Guides them toward the {gap_type} consideration
        - Shows you understood their previous message
        - Is appropriate for a {student_level} student
        
        RESPOND WITH JUST THE QUESTION - no explanation.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Socratic tutor. Ask one specific, contextual question that builds on the student's previous input and guides discovery."
                    },
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ],
                max_tokens=100,  # Shorter for focused questions
                temperature=0.7
            )
            
            question_text = response.choices[0].message.content.strip()
            
            return {
                "text": question_text,
                "type": "contextual_discovery",
                "intent": self.get_pedagogical_intent(gap_type),
                "gap_addressed": gap_type
            }
            
        except Exception as e:
            print(f"❌ Error generating contextual question: {e}")
            
            # Better fallback based on user's actual input
            last_user_message = ""
            for msg in reversed(state.messages):
                if msg.get('role') == 'user':
                    last_user_message = msg['content']
                    break
                    
            if last_user_message:
                fallback_question = f"Can you explain your thinking behind: \"{last_user_message}\"?"
            else:
                fallback_question = "Can you walk me through your thinking on the most important aspect of your design?"

            return {
                "text": fallback_question,
                "type": "contextual_fallback",
                "intent": self.get_pedagogical_intent(gap_type),
                "gap_addressed": gap_type
            }
    



    def extract_visual_context(self, visual_analysis: Dict) -> str:
        """Extract key visual observations for context"""
        
        if not visual_analysis or visual_analysis.get('error'):
            return "No visual analysis available"
        
        context_parts = []
        
        # Add elements found
        elements = visual_analysis.get('identified_elements', [])
        if elements:
            context_parts.append(f"Elements identified: {', '.join(elements[:5])}")
        
        # Add key observations from raw analysis
        raw_analysis = visual_analysis.get('raw_analysis', '')
        if raw_analysis:
            # Extract first sentence for context
            first_sentence = raw_analysis.split('.')[0] if '.' in raw_analysis else raw_analysis[:100]
            context_parts.append(f"Visual observation: {first_sentence}")
        
        # Add accessibility notes
        accessibility = visual_analysis.get('accessibility_notes', [])
        if accessibility:
            context_parts.append(f"Accessibility observations: {accessibility[0]}")
        
        return "; ".join(context_parts) if context_parts else "General architectural sketch"
    
    def get_pedagogical_intent(self, gap_type: str) -> str:
        """Get the educational intent for addressing this gap"""
        
        intents = {
            "accessibility_awareness": "Guide discovery of universal design principles and legal requirements",
            "spatial_relationships": "Encourage thinking about circulation, flow, and spatial connections", 
            "brief_development": "Help clarify project requirements and constraints",
            "systems_thinking": "Promote understanding of building systems and long-term considerations"
        }
        
        return intents.get(gap_type, "Encourage deeper architectural thinking")
    
    def plan_follow_up(self, cognitive_flags: List[str], student_profile) -> Dict[str, Any]:
        """Plan the follow-up strategy based on student response"""
        
        follow_up = {
            "if_student_struggles": "Provide more specific prompts",
            "if_student_succeeds": "Move to next cognitive gap or add complexity",
            "next_focus_areas": [],
            "scaffolding_level": "medium"
        }
        
        # Adjust scaffolding based on student level
        if student_profile.skill_level == "beginner":
            follow_up["scaffolding_level"] = "high"
            follow_up["if_student_struggles"] = "Break down into smaller, more specific questions"
        elif student_profile.skill_level == "advanced":
            follow_up["scaffolding_level"] = "low"  
            follow_up["if_student_succeeds"] = "Introduce advanced challenges or edge cases"
        
        # Plan next focus areas
        remaining_gaps = [flag for flag in cognitive_flags if flag not in ["low_confidence_analysis"]]
        follow_up["next_focus_areas"] = remaining_gaps[:2]  # Next 2 areas to address
        
        return follow_up

    # In socratic_tutor.py - Add understanding-based questioning:
    def generate_question_by_level(self, understanding_level: str, confidence_level: str, topic: str) -> str:
        """Generate questions based on student level (per document Section 5)"""
        import random  # Add this import at the top of your file if not present

        if understanding_level == "low":
            # Clarification questions
            templates = [
                f"What do you mean by {topic}?",
                f"Can you help me understand your thinking about {topic}?",
                f"What's your current understanding of {topic}?"
            ]
        elif understanding_level == "medium":
            # Exploratory questions  
            templates = [
                f"What possibilities do you see for {topic}?",
                f"How might you approach {topic}?",
                f"What factors should we consider for {topic}?"
            ]
        else:  # high understanding
            # Analytical questions
            templates = [
                f"Why do you think this approach to {topic} would work?",
                f"What are the potential drawbacks or challenges of this approach to {topic}?",
                f"How does this solution for {topic} compare with others you considered?"
            ]
        
        # Select a random template
        question = random.choice(templates)
        
        return question
    
# Test function
async def test_socratic_tutor():
    print("🧪 Testing Socratic Tutor Agent...")
    
    from agents.analysis_agent import AnalysisAgent
    from state_manager import ArchMentorState, StudentProfile
    
    # Create test scenario with cognitive gaps
    state = ArchMentorState()
    state.current_design_brief = "Design a community center"  # Vague brief
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # First get analysis with cognitive gaps
    analysis_agent = AnalysisAgent("architecture")
    analysis_result = await analysis_agent.process(state)
    
    print(f"📊 Analysis found {len(analysis_result.get('cognitive_flags', []))} cognitive flags")
    print(f"🚩 Flags: {analysis_result.get('cognitive_flags', [])}")
    
    # Now test Socratic response
    socratic_agent = SocraticTutorAgent("architecture")
    socratic_response = await socratic_agent.generate_response(state, analysis_result)
    
    print(f"\n🤔 Socratic Response:")
    print(f"   Primary gap addressed: {socratic_response['primary_gap_addressed']}")