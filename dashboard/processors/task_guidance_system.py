"""
Task-Specific Guidance System - DISTINCT APPROACHES BY TEST GROUP
Provides different task presentations based on test logic documents for three-condition testing
"""

from typing import Dict, Any, List, Optional
from dashboard.processors.dynamic_task_manager import TaskType, ActiveTask
from dashboard.ui.task_ui_renderer import TaskUIRenderer


class TaskGuidanceSystem:
    """Generates DISTINCT task presentations for different test groups based on test documents"""
    
    def __init__(self):
        self.mentor_tasks = self._initialize_mentor_tasks()
        self.generic_ai_tasks = self._initialize_generic_ai_tasks()
        self.control_tasks = self._initialize_control_tasks()
        self.ui_renderer = TaskUIRenderer()
    
    def get_task_guidance(self, task: ActiveTask, user_input: str,
                         base_response: str, conversation_context: List[Dict]) -> str:
        """Present clean task UI separate from agent message (like gamification)"""

        # Store task for separate rendering (like gamification does)
        import streamlit as st
        st.session_state['active_task'] = {
            'task': task,
            'user_input': user_input,
            'guidance_type': self._get_guidance_type(task.test_group),
            'should_render': True
        }

        # Return only the base response - task will be rendered separately
        return base_response

    def _get_guidance_type(self, test_group: str) -> str:
        """Get guidance type based on test group"""
        if test_group == "MENTOR":
            return "socratic"
        elif test_group == "GENERIC_AI":
            return "direct"
        elif test_group == "CONTROL":
            return "minimal"
        else:
            return "minimal"
    
    def _initialize_mentor_tasks(self) -> Dict[TaskType, Dict[str, Any]]:
        """MENTOR GROUP: Socratic questioning and guided discovery"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: {
                "task_assignment": """**◉ TASK 1.1: Architectural Concept Development**

**Your Assignment**: You are tasked with designing a community center for a diverse urban neighborhood of 15,000 residents. The site is a former industrial warehouse (150m x 80m x 12m height). 

**Consider**: 
• Community needs assessment and cultural sensitivity
• Sustainability and adaptive reuse principles  
• Flexible programming for diverse activities
• Integration with existing urban fabric

**Duration**: 15 minutes""",
                "socratic_questions": [
                    "Before we proceed with design details, what do you think are the most important questions we should ask about this community?",
                    "What assumptions are you making about how this community gathers and interacts?",
                    "How are you approaching this problem differently than a typical new-build community center?",
                    "What would be lost if we completely transformed the existing industrial character?"
                ]
            },
            
            TaskType.SPATIAL_PROGRAM: {
                "task_assignment": """**◉ TASK 1.2: Spatial Program Development**

**Your Assignment**: Based on your community center concept, develop a detailed spatial program. 

**Consider**: 
• Circulation patterns and adjacency requirements
• Flexibility needs and community input integration
• Functional relationships between spaces
• How spaces reflect community social patterns

**Duration**: 10 minutes""",
                "socratic_questions": [
                    "How do the functional relationships between spaces reflect community social patterns?",
                    "What precedents can inform your adjacency decisions?",
                    "What assumptions are you making about how this community gathers and interacts?",
                    "How is your programming methodology evolving as you think through this problem?"
                ]
            },

            TaskType.VISUAL_ANALYSIS_2D: {
                "task_assignment": """**◉ TASK 2.1: 2D Design Development & Analysis**

**Your Assignment**: Transform your community center concept into visual representations. Create spatial diagrams, section studies, or perspective sketches.

**Consider**: 
• Circulation patterns and spatial relationships
• Environmental systems integration
• Scale and proportion relationships
• Communication of design intent

**Duration**: 20 minutes""",
                "socratic_questions": [
                    "I notice your main gathering space represents X% of the total area. How does this proportion relate to your intended community capacity?",
                    "Your circulation pattern creates a particular flow through spaces. What are the implications for spontaneous community interaction?",
                    "The scale relationship between your entrance and main hall suggests a hierarchy. Was this intentional?"
                ]
            },
            
            TaskType.ENVIRONMENTAL_CONTEXTUAL: {
                "task_assignment": """**◉ TASK 2.2: Environmental & Contextual Integration**

**Your Assignment**: Integrate your community center design with environmental factors: natural lighting, ventilation, solar orientation, and urban context.

**Consider**: 
• How the building responds to its surroundings
• Industrial windows and natural lighting strategy
• Neighborhood architectural context
• Environmental strategies supporting community activities

**Duration**: 10 minutes""",
                "socratic_questions": [
                    "How might the industrial windows influence your natural lighting strategy throughout the day?",
                    "What elements of the surrounding neighborhood architecture should your design respond to or contrast with?",
                    "How do your environmental strategies support community activities while honoring the building's industrial heritage?"
                ]
            },
            
            TaskType.SPATIAL_ANALYSIS_3D: {
                "task_assignment": """**◉ TASK 3.1: 3D Spatial Analysis & Material Systems**

**Your Assignment**: Develop detailed spatial model and material systems for your community center.

**Consider**: 
• 3D model development and spatial relationships
• Material selection for adaptive reuse
• Structural integration with existing systems
• Construction methodology with community involvement

**Duration**: 20 minutes""",
                "socratic_questions": [
                    "How do the existing structural elements become part of your new spatial experience?",
                    "Where will your new building systems integrate with the preserved industrial elements?",
                    "How does your vertical circulation strategy ensure inclusive access for all community members?"
                ]
            },
            
            TaskType.REALIZATION_IMPLEMENTATION: {
                "task_assignment": """**◉ TASK 3.2: Realization & Implementation Strategy**

**Your Assignment**: Develop a comprehensive implementation strategy for your community center, including: phased construction, community engagement process, funding strategies, and long-term stewardship plans.

**Consider**: 
• Stakeholder analysis and community voices
• Phasing strategy during construction
• Resource allocation and budget constraints
• Long-term adaptability for changing needs

**Duration**: 15 minutes""",
                "socratic_questions": [
                    "Your design proposals are ambitious. How would you prioritize elements if budget was reduced by 30%?",
                    "What methods will you use to ensure diverse community voices are heard in the design refinement process?",
                    "How might this community center need to adapt over the next 20 years?"
                ]
            },
            
            TaskType.DESIGN_EVOLUTION: {
                "task_assignment": """**◉ TASK 4.1: Design Evolution Analysis**

**Your Assignment**: Review your complete design process from initial concept through implementation strategy.

**Consider**: 
• How your understanding evolved throughout the phases
• Key insights that shaped your design decisions
• Critical moments in your design development
• Learning outcomes and methodology evolution

**Duration**: 10 minutes""",
                "socratic_questions": [
                    "How did your understanding of the design problem evolve throughout the three phases?",
                    "What were the most critical moments in your design development, and why?",
                    "How has your approach to community-centered design changed through this process?"
                ]
            },
            
            TaskType.KNOWLEDGE_TRANSFER: {
                "task_assignment": """**◉ TASK 4.2: Knowledge Transfer Challenge**

**Your Assignment**: Articulate your design knowledge and insights for transfer to others.

**Consider**: 
• Key principles learned about adaptive reuse
• Community engagement strategies discovered
• Design methodology insights
• Transferable knowledge for future projects

**Duration**: 15 minutes""",
                "socratic_questions": [
                    "What would you want another designer to know before starting a similar community center project?",
                    "Which of your design insights are specific to this project, and which are transferable?",
                    "How would you teach someone else your approach to community-centered adaptive reuse?"
                ]
            }
        }
    
    def _initialize_generic_ai_tasks(self) -> Dict[TaskType, Dict[str, Any]]:
        """GENERIC AI GROUP: Direct information delivery and examples - 5 TASKS ONLY"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: {
                "task_assignment": """**◉ TASK 1.1: Architectural Concept Development with Design Move Tracking**

**Your Assignment**: You are tasked with designing a community center for a diverse urban neighborhood of 15,000 residents. The site is a former industrial warehouse (150m x 80m x 12m height).

**Consider**:
• Community needs assessment and cultural sensitivity
• Sustainability and adaptive reuse principles
• Flexible programming for diverse activities
• Integration with existing urban fabric

**Duration**: 15 minutes""",
                "direct_information": [
                    "Successful warehouse-to-community transformations typically preserve key industrial features like exposed structure, large windows, and open floor plates.",
                    "Community centers should include: flexible meeting spaces (200-400 sq ft each), large multipurpose hall (2000+ sq ft), kitchen facilities, childcare areas, and administrative offices.",
                    "Adaptive reuse strategies: retain structural grid, insert mezzanines for program variety, use industrial materials (steel, concrete, wood) for authenticity.",
                    "Cultural sensitivity approaches: community input sessions, local art integration, flexible spaces for diverse cultural practices."
                ]
            },

            TaskType.VISUAL_ANALYSIS_2D: {
                "task_assignment": """**◉ TASK 2.1: Design Development with Multimodal Linkography**

**Your Assignment**: Transform your concept into visual representations through sketches and diagrams. Focus on spatial arrangements and visualization techniques.

**Consider**:
• Visual representation strategies for community spaces
• Architectural drawing conventions and communication methods
• Relationship between spatial program and visual expression
• Community-centered design visualization approaches

**Duration**: 20 minutes""",
                "direct_information": [
                    "Effective 2D representations include: floor plans (1:200 scale), building sections showing height relationships, circulation diagrams with flow arrows, and bubble diagrams for adjacencies.",
                    "Drawing conventions: thick walls (existing structure), thin lines (new elements), hatching for solid/void relationships, annotations for key dimensions.",
                    "Spatial analysis techniques: calculate area percentages, diagram sight lines, show natural light penetration, indicate acoustic zones.",
                    "Communication strategies: clear title blocks, north arrows, scale indicators, legend for materials and symbols."
                ]
            },

            TaskType.SPATIAL_ANALYSIS_3D: {
                "task_assignment": """**◉ TASK 3.1: Technical Implementation with Construction Logic**

**Your Assignment**: Develop technical details and construction strategies for your community center. Focus on material selection, structural systems, and implementation methodology.

**Consider**:
• Material selection for adaptive reuse
• Structural integration with existing warehouse
• Construction methodology and phasing
• Technical specifications and details

**Duration**: 20 minutes""",
                "direct_information": [
                    "3D modeling approaches: massing studies, sectional perspectives, axonometric drawings, digital models with material rendering.",
                    "Adaptive reuse materials: exposed steel structure, polished concrete floors, reclaimed wood accents, industrial lighting fixtures.",
                    "Structural strategies: steel frame infill, mezzanine insertions, seismic upgrades, accessibility ramps and elevators.",
                    "Construction methods: phased construction to maintain community use, prefabricated components, local labor training programs."
                ]
            },

            TaskType.DESIGN_EVOLUTION: {
                "task_assignment": """**◉ TASK 4.1: Design Evolution Analysis with Complete Move Network**

**Your Assignment**: Review your complete design process from initial concept through technical implementation. Analyze how your understanding evolved and what key insights shaped your decisions.

**Consider**:
• How your design thinking progressed through each phase
• Key decision points and their rationale
• Integration of technical and social considerations
• Learning outcomes from the design process

**Duration**: 10 minutes""",
                "direct_information": [
                    "Design evolution analysis: document initial assumptions vs. final decisions, identify critical turning points, trace concept development.",
                    "Move network analysis: map connections between ideas, identify influential design moves, analyze decision-making patterns.",
                    "Integration assessment: evaluate how technical, social, and cultural factors were balanced throughout the process.",
                    "Learning documentation: articulate key insights, transferable principles, and areas for future development."
                ]
            },

            TaskType.KNOWLEDGE_TRANSFER: {
                "task_assignment": """**◉ TASK 4.2: Comparative Linkographic Analysis**

**Your Assignment**: Compare your design approach with alternative methodologies and document patterns that could inform future projects.

**Consider**:
• Comparison with other design approaches
• Pattern identification across design phases
• Transferable insights and methodologies
• Cross-group learning opportunities

**Duration**: 15 minutes""",
                "direct_information": [
                    "Comparative analysis methods: side-by-side process comparison, pattern identification, methodology evaluation.",
                    "Design approach documentation: systematic vs. intuitive methods, AI-assisted vs. independent work, structured vs. exploratory processes.",
                    "Pattern recognition: recurring themes, successful strategies, common challenges, effective solutions.",
                    "Knowledge transfer strategies: principle extraction, case study development, methodology documentation, best practice identification."
                ]
            }
        }
    
    def _initialize_control_tasks(self) -> Dict[TaskType, Dict[str, Any]]:
        """CONTROL GROUP: Minimal prompts and self-direction - 5 TASKS ONLY"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: {
                "task_assignment": """**◉ TASK 1.1: Self-Directed Architectural Concept Development with Natural Move Tracking**

**Your Assignment**: You are tasked with designing a community center for a diverse urban neighborhood of 15,000 residents. The site is a former industrial warehouse (150m x 80m x 12m height). Consider: community needs, cultural sensitivity, sustainability, and adaptive reuse principles.

**System Interface**: Please work through this design challenge at your own pace. Document your thinking process, decisions, and reasoning as you develop your concept. Use the text input, sketching tools, and upload features as needed.

**Duration**: 15 minutes""",
                "minimal_prompt": "Continue developing your community center concept. Document your thinking process and design decisions as you work through the challenge."
            },

            TaskType.VISUAL_ANALYSIS_2D: {
                "task_assignment": """**◉ TASK 2.1: Self-Directed Design Development with Natural Multimodal Linkography**

**Your Assignment**: Transform your concept into visual representations through independent work. Create spatial diagrams, section studies, or perspective sketches. Work at your own pace using the available tools.

**Consider**:
• Circulation patterns and spatial relationships
• Environmental systems and site integration
• Visual communication of your design ideas
• Independent development of design solutions

**Duration**: 20 minutes""",
                "minimal_prompt": "Continue with your visual design development. Use sketches, diagrams, or written descriptions to develop your spatial ideas."
            },

            TaskType.SPATIAL_ANALYSIS_3D: {
                "task_assignment": """**◉ TASK 3.1: Autonomous Technical Implementation with Independent Construction Logic**

**Your Assignment**: Develop technical details and construction strategies for your community center through independent work. Focus on material selection, structural systems, and implementation methodology.

**Consider**:
• 3D relationships and material selection for adaptive reuse
• Structural integration with existing warehouse
• Construction methodology and phasing
• Self-directed technical problem solving

**Duration**: 20 minutes""",
                "minimal_prompt": "Work on the three-dimensional and material aspects of your design. Consider how materials and structure support your concept."
            },

            TaskType.DESIGN_EVOLUTION: {
                "task_assignment": """**◉ TASK 4.1: Self-Directed Design Evolution Analysis with Natural Move Networks**

**Your Assignment**: Review your complete design process from initial concept through technical implementation through independent reflection. Consider how your understanding evolved and what key insights shaped your decisions.

**Consider**:
• How your design thinking progressed through each phase
• Key decision points and their rationale
• Self-directed learning and problem-solving approaches
• Natural cognitive development patterns

**Duration**: 10 minutes""",
                "minimal_prompt": "Reflect on your design process and how your ideas have developed. Document your key insights and decisions."
            },

            TaskType.KNOWLEDGE_TRANSFER: {
                "task_assignment": """**◉ TASK 4.2: Independent Pattern Documentation**

**Your Assignment**: Document your design approach and insights through self-assessment and natural pattern recognition. Focus on what you learned through independent work.

**Consider**:
• Self-assessment of design methodology
• Natural pattern recognition in your process
• Independent learning outcomes
• Knowledge valuable for future projects

**Duration**: 15 minutes""",
                "minimal_prompt": "Document your learning outcomes and insights. Consider what knowledge would be valuable to share with other designers."
            }
        }
    
    def _present_mentor_task(self, task: ActiveTask, user_input: str,
                           base_response: str, conversation_context: List[Dict]) -> str:
        """MENTOR: Present task assignment + Socratic questioning with enhanced UI"""

        task_data = self.mentor_tasks.get(task.task_type, {})

        # Present task assignment first time with enhanced UI
        if not task.progress_indicators.get("task_presented", False):
            task_assignment = task_data.get("task_assignment", "")
            task.progress_indicators["task_presented"] = True

            # Add first Socratic question
            questions = task_data.get("socratic_questions", [])
            if questions:
                selected_question = questions[0]
                full_task_content = f"{task_assignment}\n\n**Let's begin with guided exploration:**\n\n{selected_question}"

                # Use enhanced UI renderer
                return self.ui_renderer.render_task_as_enhanced_message(
                    task=task,
                    base_response=base_response,
                    task_content=full_task_content,
                    guidance_type="socratic"
                )

        # Continue with Socratic questions (regular format for follow-ups)
        questions = task_data.get("socratic_questions", [])
        if questions:
            question_index = len(conversation_context) % len(questions)
            selected_question = questions[question_index]
            return f"{base_response}\n\n{selected_question}"

        return base_response
    
    def _present_generic_ai_task(self, task: ActiveTask, user_input: str,
                               base_response: str, conversation_context: List[Dict]) -> str:
        """GENERIC AI: Present task assignment + Direct information with enhanced UI"""

        task_data = self.generic_ai_tasks.get(task.task_type, {})

        # Present task assignment + direct information first time with enhanced UI
        if not task.progress_indicators.get("task_presented", False):
            task_assignment = task_data.get("task_assignment", "")
            direct_info = task_data.get("direct_information", [])
            task.progress_indicators["task_presented"] = True

            if direct_info:
                info_text = "\n".join([f"• {info}" for info in direct_info])
                full_task_content = f"{task_assignment}\n\n**Here's relevant information to help you:**\n\n{info_text}"

                # Use enhanced UI renderer
                return self.ui_renderer.render_task_as_enhanced_message(
                    task=task,
                    base_response=base_response,
                    task_content=full_task_content,
                    guidance_type="direct"
                )

        return base_response
    
    def _present_control_task(self, task: ActiveTask, user_input: str,
                            base_response: str, conversation_context: List[Dict]) -> str:
        """CONTROL: Present task assignment + Minimal prompt only with enhanced UI"""

        task_data = self.control_tasks.get(task.task_type, {})

        # Present task assignment once with enhanced UI
        if not task.progress_indicators.get("task_presented", False):
            task_assignment = task_data.get("task_assignment", "")
            minimal_prompt = task_data.get("minimal_prompt", "Continue with your design work.")
            task.progress_indicators["task_presented"] = True

            full_task_content = f"{task_assignment}\n\n**{minimal_prompt}**"

            # Use enhanced UI renderer
            return self.ui_renderer.render_task_as_enhanced_message(
                task=task,
                base_response=base_response,
                task_content=full_task_content,
                guidance_type="minimal"
            )

        # Minimal ongoing support
        return "Continue working on your design."
