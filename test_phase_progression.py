"""
Test Script for Phase Progression System
Demonstrates how to use the standalone phase progression system
"""

from phase_progression_system import PhaseProgressionSystem
import json

def test_phase_progression():
    """Test the phase progression system with example responses"""
    
    print("=== Phase Progression System Test ===\n")
    
    # Initialize the system
    system = PhaseProgressionSystem()
    
    # Start a new session
    session_id = "demo_session_001"
    session = system.start_session(session_id)
    
    print(f"✅ Started session: {session_id}")
    print(f"📍 Current phase: {session.current_phase.value}")
    print(f"📊 Phase weights: Ideation (25%), Visualization (35%), Materialization (40%)")
    print(f"🎯 Phase thresholds: Ideation (3.0), Visualization (3.5), Materialization (4.0)\n")
    
    # Get the first question
    first_question = system.get_next_question(session_id)
    if first_question:
        print(f"🤔 First question: {first_question.question_text}")
        print(f"📝 Step: {first_question.step.value}")
        print(f"🏷️  Keywords: {', '.join(first_question.keywords)}\n")
    
    # Example responses for each phase
    example_responses = {
        "ideation": [
            "I think we should ask about the community's current needs, what activities they want to support, and how the building can serve as a gathering place. We also need to understand the site's constraints and opportunities.",
            "Some great examples include the Tate Modern in London, which transformed a power station into an art museum, and the High Line in New York, which turned an elevated railway into a public park. These show how industrial spaces can become vibrant community assets.",
            "The industrial character is valuable because it tells the story of the site's history and gives the building authenticity. If we completely transformed it, we'd lose that sense of place and the unique character that makes this location special.",
            "I'm approaching this differently by focusing on adaptive reuse rather than demolition and new construction. I'm thinking about how to preserve the industrial aesthetic while making it welcoming for community use."
        ],
        "visualization": [
            "My spatial organization responds to the site by creating a central courtyard that preserves the industrial character while providing natural light and ventilation. The program requirements are organized around this central space with flexible areas that can adapt to different community needs.",
            "I'm drawing inspiration from the Pompidou Center in Paris for its exposed circulation and the Guggenheim Bilbao for its fluid spatial transitions. These precedents show how circulation can become an architectural feature that enhances the user experience.",
            "My form development balances functional efficiency by using a modular system that allows for flexible programming, while the architectural expression celebrates the industrial heritage through exposed structure and materials that reference the site's history.",
            "I'm most confident about the central courtyard concept and the modular spatial system. However, I need to explore how the building connects to the surrounding neighborhood and how the circulation flows between different program areas."
        ],
        "materialization": [
            "My material choices respond to both function and environmental context by using locally sourced materials that have low embodied energy. The building's function as a community center requires durable, low-maintenance materials that can withstand heavy use while creating a warm, welcoming atmosphere.",
            "Construction precedents like the Bullitt Center in Seattle demonstrate effective integration of sustainable materials. The use of cross-laminated timber and natural ventilation systems shows how innovative materials can be successfully integrated into community buildings.",
            "My technical approach balances innovation with constructability by using proven construction methods with innovative material applications. Cost considerations are addressed through careful material selection and efficient construction sequencing that minimizes waste and labor costs.",
            "If budget or time constraints required simplification, I would prioritize the structural system and envelope performance, as these are fundamental to the building's success. I would simplify interior finishes and some of the more complex spatial features while maintaining the core design concept."
        ]
    }
    
    # Process responses for each phase
    for phase_name, responses in example_responses.items():
        print(f"=== {phase_name.upper()} PHASE ===\n")
        
        for i, response in enumerate(responses):
            print(f"📝 Response {i+1}: {response[:80]}...")
            
            result = system.process_response(session_id, response)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            print(f"📊 Grade: {result['grade']['overall_score']:.2f}/5.0")
            print(f"✅ Strengths: {', '.join(result['grade']['strengths'][:2])}")
            print(f"⚠️  Areas for improvement: {', '.join(result['grade']['weaknesses'][:1])}")
            print(f"📍 Current phase: {result['current_phase']}")
            print(f"🎯 Phase complete: {result['phase_complete']}")
            
            if result['next_question']:
                print(f"🤔 Next question: {result['next_question'][:80]}...")
            else:
                print("✅ All questions in this phase completed!")
            
            print()
        
        # Show phase summary
        summary = system.get_session_summary(session_id)
        phase_summary = summary['phase_summaries'].get(phase_name, {})
        if phase_summary:
            print(f"📈 {phase_name.title()} Phase Summary:")
            print(f"   Average score: {phase_summary['average_score']:.2f}/5.0")
            print(f"   Completed: {phase_summary['completed']}")
            print(f"   Steps completed: {phase_summary['completed_steps']}/4")
            print()
    
    # Final session summary
    final_summary = system.get_session_summary(session_id)
    print("=== FINAL SESSION SUMMARY ===")
    print(f"🎯 Overall score: {final_summary['overall_score']:.2f}/5.0")
    print(f"✅ Session complete: {final_summary['session_complete']}")
    print(f"📍 Current phase: {final_summary['current_phase']}")
    print(f"⏱️  Session duration: {final_summary['session_duration']:.1f} minutes")
    print(f"💬 Total responses: {final_summary['total_responses']}")
    
    # Phase breakdown
    print("\n📊 Phase Breakdown:")
    for phase, summary in final_summary['phase_summaries'].items():
        print(f"   {phase.title()}: {summary['average_score']:.2f}/5.0 ({'✅' if summary['completed'] else '⏳'})")
    
    # Save session data
    save_result = system.save_session(session_id)
    if "success" in save_result:
        print(f"\n💾 Session saved to: {save_result['filename']}")

def interactive_test():
    """Interactive test mode for manual testing"""
    
    print("=== Interactive Phase Progression Test ===\n")
    
    system = PhaseProgressionSystem()
    session_id = "interactive_session_001"
    session = system.start_session(session_id)
    
    print(f"✅ Started interactive session: {session_id}")
    print("Type 'quit' to exit, 'summary' to see session summary\n")
    
    while True:
        # Get current question
        current_question = system.get_next_question(session_id)
        
        if not current_question:
            print("✅ All phases completed!")
            break
        
        print(f"🤔 Question ({current_question.step.value}):")
        print(f"   {current_question.question_text}")
        print(f"   Keywords: {', '.join(current_question.keywords)}")
        print()
        
        # Get user response
        response = input("📝 Your response (or 'quit'/'summary'): ").strip()
        
        if response.lower() == 'quit':
            break
        elif response.lower() == 'summary':
            summary = system.get_session_summary(session_id)
            print(f"\n📊 Session Summary:")
            print(f"   Overall score: {summary['overall_score']:.2f}/5.0")
            print(f"   Current phase: {summary['current_phase']}")
            print(f"   Session complete: {summary['session_complete']}")
            print()
            continue
        elif not response:
            print("Please provide a response.\n")
            continue
        
        # Process response
        result = system.process_response(session_id, response)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}\n")
            continue
        
        print(f"\n📊 Assessment Results:")
        print(f"   Overall score: {result['grade']['overall_score']:.2f}/5.0")
        print(f"   Completeness: {result['grade']['completeness']:.2f}/5.0")
        print(f"   Depth: {result['grade']['depth']:.2f}/5.0")
        print(f"   Relevance: {result['grade']['relevance']:.2f}/5.0")
        print(f"   Innovation: {result['grade']['innovation']:.2f}/5.0")
        print(f"   Technical: {result['grade']['technical_understanding']:.2f}/5.0")
        
        if result['grade']['strengths']:
            print(f"   ✅ Strengths: {', '.join(result['grade']['strengths'])}")
        if result['grade']['weaknesses']:
            print(f"   ⚠️  Areas for improvement: {', '.join(result['grade']['weaknesses'])}")
        if result['grade']['recommendations']:
            print(f"   💡 Recommendations: {', '.join(result['grade']['recommendations'])}")
        
        print(f"   📍 Current phase: {result['current_phase']}")
        print(f"   🎯 Phase complete: {result['phase_complete']}")
        
        if result['phase_complete']:
            print("   🎉 Phase completed! Moving to next phase...")
        
        print()

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Automated test with example responses")
    print("2. Interactive test (manual input)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        interactive_test()
    else:
        test_phase_progression()

