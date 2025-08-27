#!/usr/bin/env python3
"""
DYNAMIC TASK SYSTEM EXAMPLES
Demonstrates what users actually see when tasks trigger
"""

# Example 1: Test 1.1 (Architectural Concept) - Triggers at 0-15% ideation
def example_architectural_concept_trigger():
    """
    SCENARIO: User is at 10% ideation phase completion
    USER INPUT: "I'm starting to think about my community center design"
    
    WITHOUT TASK (normal response):
    "That sounds like an interesting project. What aspects of community center design are you most interested in exploring?"
    
    WITH TASK 1.1 ACTIVE (enhanced response):
    "That sounds like an interesting project. What aspects of community center design are you most interested in exploring?

    **Task Focus (Phase: 0-15% ideation)**: Let's dive deeper into your community center concept through some focused exploration.

    Before we proceed with design details, what do you think are the most important questions we should ask about this community?
    
    🎯 **Active Task**: Architectural Concept Development
    📊 **Phase Range**: 0-15% ideation completion
    ⏱️ **Triggered at**: 10.0% phase completion
    """
    pass

# Example 2: Test 2.1 (Visual Analysis 2D) - Triggers when image uploaded at 0-50% visualization
def example_visual_analysis_trigger():
    """
    SCENARIO: User uploads floor plan at 25% visualization phase completion
    USER INPUT: "Here's my initial floor plan sketch" + [IMAGE UPLOADED]
    
    WITHOUT TASK (normal response):
    "I can see your floor plan. The layout shows some interesting spatial relationships."
    
    WITH TASK 2.1 ACTIVE (enhanced response):
    "I can see your floor plan. The layout shows some interesting spatial relationships.

    **Task Focus (Phase: 0-50% visualization)**: Let's analyze your visual design development in detail.

    Looking at your floor plan, I notice several design decisions. Can you walk me through your thinking about the circulation patterns and how they support community interaction?
    
    🎯 **Active Task**: 2D Visual Analysis
    📊 **Phase Range**: 0-50% visualization completion  
    ⏱️ **Triggered at**: 25.0% phase completion
    🖼️ **Image Analysis**: Floor plan detected
    """
    pass

# Example 3: Test 4.1 (Design Evolution) - Triggers at 75-90% any phase
def example_design_evolution_trigger():
    """
    SCENARIO: User is at 80% materialization phase completion
    USER INPUT: "I think I'm getting close to finalizing my material choices"
    
    WITHOUT TASK (normal response):
    "That's great progress on your material selection. What factors are guiding your final decisions?"
    
    WITH TASK 4.1 ACTIVE (enhanced response):
    "That's great progress on your material selection. What factors are guiding your final decisions?

    **Task Focus (Phase: 75-90% completion)**: Let's reflect on your design journey and evolution.

    As you near completion of this phase, take a moment to reflect: How has your understanding of this community center project evolved since you began? What key insights have shaped your design decisions?
    
    🎯 **Active Task**: Design Evolution Analysis
    📊 **Phase Range**: 75-90% any phase completion
    ⏱️ **Triggered at**: 80.0% phase completion
    🔄 **Reflection Focus**: Design journey and key decisions
    """
    pass

# Example 4: Different Test Groups Experience Different Guidance
def example_test_group_differences():
    """
    SAME TRIGGER SCENARIO: Test 1.2 (Spatial Program) at 25% ideation
    USER INPUT: "I'm thinking about how to organize the different spaces"
    
    MENTOR GROUP (Socratic questioning):
    "I'm thinking about how to organize the different spaces.

    **Task Focus (Phase: 20-35% ideation)**: Let's explore your spatial programming through guided inquiry.

    What assumptions are you making about how different community groups will use these spaces? How might those assumptions influence your spatial organization?
    
    🎯 **Active Task**: Spatial Program Development
    🤔 **Approach**: Socratic questioning and guided discovery"
    
    GENERIC_AI GROUP (Direct information):
    "I'm thinking about how to organize the different spaces.

    **Task Information (Phase: 20-35% ideation)**:
    Consider these key spatial programming principles:
    • Adjacency relationships between complementary functions
    • Circulation efficiency and wayfinding clarity  
    • Flexibility for multiple uses and community events
    • Acoustic separation between quiet and active zones
    
    🎯 **Active Task**: Spatial Program Development
    📚 **Approach**: Direct information and best practices"
    
    CONTROL GROUP (Minimal prompt):
    "**Task Focus (Phase: 20-35% ideation)**: Proceed with developing your spatial program. Consider the relationships between different spaces and how they support community activities.
    
    🎯 **Active Task**: Spatial Program Development
    🔧 **Approach**: Self-directed with minimal guidance"
    """
    pass

# Example 5: Task Completion Criteria and Progression
def example_task_completion():
    """
    TASK COMPLETION CRITERIA (shown in sidebar):
    
    🎯 Active Tasks
    ├── Architectural Concept (0-15%)
    │   ├── Group: MENTOR
    │   ├── Phase: ideation  
    │   ├── Triggered at: 10.0% phase completion
    │   ├── Completion Criteria:
    │   │   • User has articulated initial design concept
    │   │   • Key design principles identified
    │   │   • Community needs considered
    │   └── [Complete Task] button
    
    TASK PROGRESSION:
    1. Task triggers automatically at phase completion threshold
    2. Task enhances mentor responses with specific guidance
    3. Task tracks progress through completion criteria
    4. Task completes when criteria met or phase advances beyond range
    5. Next task in sequence becomes eligible to trigger
    """
    pass

# Example 6: Context Awareness and Conversation Integration
def example_context_awareness():
    """
    CONTEXT INTEGRATION EXAMPLE:
    
    Previous conversation:
    User: "I'm working on a community center in an old warehouse"
    Assistant: "Adaptive reuse projects offer unique opportunities..."
    User: "The building is 150m x 80m with 12m height"
    Assistant: "That's substantial space with great ceiling height..."
    
    WHEN TASK 3.1 TRIGGERS (Spatial Analysis 3D at 15% materialization):
    User: "I'm starting to think about the structural systems"
    
    CONTEXT-AWARE ENHANCED RESPONSE:
    "Given the substantial 150m x 80m warehouse space you're working with, structural systems will be crucial.

    **Task Focus (Phase: 0-40% materialization)**: Let's analyze the three-dimensional and material aspects of your adaptive reuse project.

    Considering the existing 12m ceiling height and the industrial character of your warehouse, how are you thinking about integrating new structural elements while preserving the spatial qualities that make this building special for community use?
    
    🎯 **Active Task**: 3D Spatial Analysis & Material Systems
    🏗️ **Building Context**: 150m x 80m warehouse, 12m height
    📊 **Phase Range**: 0-40% materialization completion
    🔧 **Focus**: Structural integration and material systems"
    """
    pass

if __name__ == "__main__":
    print("🎯 DYNAMIC TASK SYSTEM - USER EXPERIENCE EXAMPLES")
    print("=" * 60)
    print("This file demonstrates what users actually see when tasks trigger.")
    print("Tasks enhance mentor responses with phase-appropriate guidance.")
    print("Different test groups receive different types of support.")
    print("Tasks are context-aware and reference previous conversation.")
