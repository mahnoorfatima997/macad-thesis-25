"""
Task-Specific Guidance System
Provides task-specific guidance based on test logic documents for three-condition testing
"""

from typing import Dict, Any, List, Optional
from dashboard.processors.dynamic_task_manager import TaskType, ActiveTask


class TaskGuidanceSystem:
    """Generates task-specific guidance for different test conditions"""
    
    def __init__(self):
        self.mentor_guidance = self._initialize_mentor_guidance()
        self.generic_ai_guidance = self._initialize_generic_ai_guidance()
        self.control_guidance = self._initialize_control_guidance()
    
    def get_task_guidance(self, task: ActiveTask, user_input: str, 
                         base_response: str, conversation_context: List[Dict]) -> str:
        """Get task-specific guidance based on test group and task type"""
        
        if task.test_group == "MENTOR":
            return self._get_mentor_guidance(task, user_input, base_response, conversation_context)
        elif task.test_group == "GENERIC_AI":
            return self._get_generic_ai_guidance(task, user_input, base_response, conversation_context)
        elif task.test_group == "CONTROL":
            return self._get_control_guidance(task, user_input, base_response, conversation_context)
        else:
            return base_response
    
    def _initialize_mentor_guidance(self) -> Dict[TaskType, Dict[str, Any]]:
        """Initialize MENTOR test group guidance based on test documents"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: {
                "introduction": "Let's dive deeper into your community center concept through some focused exploration.",
                "socratic_questions": [
                    "Before we proceed with design details, what do you think are the most important questions we should ask about this community?",
                    "What assumptions are you making about how this community gathers and interacts?",
                    "How are you approaching this problem differently than a typical new-build community center?",
                    "What would be lost if we completely transformed the existing industrial character?"
                ],
                "follow_up_prompts": [
                    "Can you elaborate on that community need?",
                    "What evidence supports that assumption?",
                    "How might that approach affect different user groups?"
                ]
            },
            
            TaskType.SPATIAL_PROGRAM: {
                "introduction": "Now let's develop a detailed spatial program based on your concept.",
                "socratic_questions": [
                    "Based on your community center concept, what specific spaces do you envision, and how should they relate to each other?",
                    "How do circulation patterns support or hinder spontaneous community interaction?",
                    "What does the scale of your proposed spaces suggest about intended community capacity?",
                    "How can the existing warehouse structure inform your spatial organization?"
                ],
                "follow_up_prompts": [
                    "What's driving that spatial relationship?",
                    "How does that circulation pattern serve different user groups?",
                    "What are the implications of that scale choice?"
                ]
            },
            
            TaskType.VISUAL_ANALYSIS_2D: {
                "introduction": "Let's analyze your visual design development through critical examination.",
                "socratic_questions": [
                    "What does this drawing reveal about your design priorities?",
                    "How do the proportions in your drawing reflect your intended community capacity?",
                    "What spatial relationships are you establishing, and why?",
                    "How does this representation communicate your design intent to others?"
                ],
                "follow_up_prompts": [
                    "What led you to that design decision?",
                    "How might others interpret this differently?",
                    "What's not shown that might be important?"
                ]
            },
            
            TaskType.SPATIAL_ANALYSIS_3D: {
                "introduction": "Let's explore the three-dimensional and material aspects of your design.",
                "socratic_questions": [
                    "How do your material choices support both the existing industrial character and new community functions?",
                    "What does your vertical organization reveal about community hierarchy and accessibility?",
                    "How do your structural modifications work with the existing grid system?",
                    "What construction sequencing would allow the community center to remain partially operational during renovation?"
                ],
                "follow_up_prompts": [
                    "What's driving that material choice?",
                    "How does that structural approach affect the user experience?",
                    "What are the long-term implications of that construction method?"
                ]
            },
            
            TaskType.ENVIRONMENTAL_CONTEXTUAL: {
                "introduction": "Let's explore how your design responds to environmental and contextual factors.",
                "socratic_questions": [
                    "How does your community center design respond to the specific climate and environmental conditions of this location?",
                    "What contextual factors from the surrounding neighborhood should influence your design decisions?",
                    "How can the building's orientation and envelope design optimize environmental performance?",
                    "What role does the existing urban fabric play in shaping your architectural response?"
                ],
                "follow_up_prompts": [
                    "What environmental data supports that design choice?",
                    "How does that contextual response affect the user experience?",
                    "What are the long-term implications of that environmental strategy?"
                ]
            },

            TaskType.REALIZATION_IMPLEMENTATION: {
                "introduction": "Now let's focus on how your design concept can be realized through practical implementation strategies.",
                "socratic_questions": [
                    "What construction sequence would allow this adaptive reuse project to be implemented most effectively?",
                    "How do your material and system choices support both the design intent and practical construction requirements?",
                    "What are the critical coordination points between different building systems in your design?",
                    "How would you phase the construction to minimize disruption to the surrounding community?"
                ],
                "follow_up_prompts": [
                    "What construction challenges does that approach address?",
                    "How does that implementation strategy affect the project timeline?",
                    "What alternative approaches might be worth considering?"
                ]
            },

            TaskType.DESIGN_EVOLUTION: {
                "introduction": "Let's reflect on your design journey and evolution of thinking.",
                "socratic_questions": [
                    "How has your understanding of this community's needs evolved through our conversation?",
                    "What design decisions have you reconsidered, and what prompted those changes?",
                    "Which aspects of your design approach surprised you as we developed them?",
                    "How would you approach a similar project differently based on this experience?"
                ],
                "follow_up_prompts": [
                    "What caused that shift in thinking?",
                    "How did that realization change your approach?",
                    "What would you want to explore further?"
                ]
            },

            TaskType.KNOWLEDGE_TRANSFER: {
                "introduction": "Let's focus on articulating and transferring the knowledge you've developed through this design process.",
                "socratic_questions": [
                    "If you were to teach someone else about community center design, what are the most important insights you would share?",
                    "How would you explain your design methodology to a colleague working on a similar project?",
                    "What principles from this project could be applied to other adaptive reuse scenarios?",
                    "How would you document your design process to make it useful for future reference?"
                ],
                "follow_up_prompts": [
                    "What makes that insight particularly valuable?",
                    "How would you demonstrate that principle in practice?",
                    "What examples would best illustrate that concept?"
                ]
            }
        }
    
    def _initialize_generic_ai_guidance(self) -> Dict[TaskType, Dict[str, Any]]:
        """Initialize Generic AI test group guidance based on test documents"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: {
                "information_focus": "Community center design principles and adaptive reuse strategies",
                "direct_guidance": [
                    "For community center design in adaptive reuse projects, consider these key elements:",
                    "• Programming: Meeting rooms, recreational spaces, educational areas, social services, flexible multipurpose zones",
                    "• Community Analysis: Demographics, cultural needs, existing social patterns, accessibility requirements", 
                    "• Adaptive Reuse Strategy: Preserving industrial character while introducing community functions",
                    "• Site Integration: Urban context, transportation access, parking, outdoor community spaces"
                ]
            },
            
            TaskType.SPATIAL_PROGRAM: {
                "information_focus": "Spatial programming methodology and circulation design",
                "direct_guidance": [
                    "Effective spatial programming for community centers involves:",
                    "• Adjacency Analysis: Which spaces need to be connected or separated",
                    "• Circulation Hierarchy: Primary, secondary, and service circulation paths",
                    "• Flexibility Requirements: Spaces that can adapt to different uses",
                    "• Capacity Planning: Occupancy loads and peak usage scenarios",
                    "• Support Spaces: Storage, mechanical, administrative areas"
                ]
            },
            
            TaskType.VISUAL_ANALYSIS_2D: {
                "information_focus": "Architectural drawing analysis and design communication",
                "direct_guidance": [
                    "Effective architectural visualization for community centers should include:",
                    "• Spatial Diagrams: Circulation patterns, adjacency relationships, public/private zones",
                    "• Technical Drawings: Floor plans showing existing structure integration, sections revealing height utilization",
                    "• Design Communication: Clear representation of community interaction scenarios",
                    "• Accessibility Compliance: ADA requirements and universal design principles"
                ]
            },
            
            TaskType.SPATIAL_ANALYSIS_3D: {
                "information_focus": "3D spatial design and material systems for adaptive reuse",
                "direct_guidance": [
                    "Technical implementation for warehouse-to-community center conversion involves:",
                    "• Structural Systems: Assessment of existing steel/concrete frame, new load requirements",
                    "• Building Envelope: Insulation strategies, new openings, sustainable material selections",
                    "• MEP Systems: HVAC for diverse programming, electrical upgrades, plumbing for community functions",
                    "• Construction Approach: Phased construction, material sourcing, budget considerations"
                ]
            },
            
            TaskType.DESIGN_EVOLUTION: {
                "information_focus": "Design process documentation and reflection methods",
                "direct_guidance": [
                    "Design evolution analysis typically examines:",
                    "• Decision Points: Key moments where design direction changed",
                    "• Iteration Patterns: How ideas developed through multiple versions",
                    "• Constraint Response: How limitations shaped creative solutions",
                    "• Learning Outcomes: Skills and knowledge gained through the process"
                ]
            }
        }
    
    def _initialize_control_guidance(self) -> Dict[TaskType, Dict[str, Any]]:
        """Initialize Control test group guidance based on test documents"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: {
                "minimal_prompt": "Continue developing your community center concept. Document your thinking process and design decisions as you work through the challenge."
            },
            
            TaskType.SPATIAL_PROGRAM: {
                "minimal_prompt": "Proceed with developing your spatial program. Consider the relationships between different spaces and how they support community activities."
            },
            
            TaskType.VISUAL_ANALYSIS_2D: {
                "minimal_prompt": "Continue with your visual design development. Use sketches, diagrams, or written descriptions to develop your spatial ideas."
            },
            
            TaskType.SPATIAL_ANALYSIS_3D: {
                "minimal_prompt": "Work on the three-dimensional and material aspects of your design. Consider how materials and structure support your concept."
            },
            
            TaskType.DESIGN_EVOLUTION: {
                "minimal_prompt": "Reflect on your design process and how your ideas have developed. Document your key insights and decisions."
            }
        }
    
    def _get_mentor_guidance(self, task: ActiveTask, user_input: str, 
                           base_response: str, conversation_context: List[Dict]) -> str:
        """Generate MENTOR test group guidance with Socratic questions"""
        
        guidance_data = self.mentor_guidance.get(task.task_type, {})
        
        # Get introduction if this is the first interaction with this task
        if not task.progress_indicators.get("introduction_given", False):
            introduction = guidance_data.get("introduction", "")
            task.progress_indicators["introduction_given"] = True
            
            # Select appropriate Socratic question
            questions = guidance_data.get("socratic_questions", [])
            if questions:
                question_index = len(conversation_context) % len(questions)
                selected_question = questions[question_index]
                
                return f"{base_response}\n\n**Task Focus ({task.time_remaining} min remaining)**: {introduction}\n\n{selected_question}"
        
        # For subsequent interactions, add follow-up prompts
        follow_ups = guidance_data.get("follow_up_prompts", [])
        if follow_ups:
            prompt_index = len(conversation_context) % len(follow_ups)
            selected_prompt = follow_ups[prompt_index]
            
            return f"{base_response}\n\n{selected_prompt}"
        
        return base_response
    
    def _get_generic_ai_guidance(self, task: ActiveTask, user_input: str, 
                               base_response: str, conversation_context: List[Dict]) -> str:
        """Generate Generic AI test group guidance with direct information"""
        
        guidance_data = self.generic_ai_guidance.get(task.task_type, {})
        
        # Provide direct information guidance
        if not task.progress_indicators.get("information_provided", False):
            direct_guidance = guidance_data.get("direct_guidance", [])
            if direct_guidance:
                guidance_text = "\n".join(direct_guidance)
                task.progress_indicators["information_provided"] = True
                
                return f"{base_response}\n\n**Task Information ({task.time_remaining} min remaining)**:\n{guidance_text}"
        
        return base_response
    
    def _get_control_guidance(self, task: ActiveTask, user_input: str, 
                            base_response: str, conversation_context: List[Dict]) -> str:
        """Generate Control test group guidance with minimal prompts"""
        
        guidance_data = self.control_guidance.get(task.task_type, {})
        
        # Provide minimal self-directed prompt
        if not task.progress_indicators.get("prompt_given", False):
            minimal_prompt = guidance_data.get("minimal_prompt", "Continue with your design work.")
            task.progress_indicators["prompt_given"] = True
            
            return f"**Task Focus ({task.time_remaining} min remaining)**: {minimal_prompt}"
        
        # For control group, return minimal response
        return "Continue working on your design."
