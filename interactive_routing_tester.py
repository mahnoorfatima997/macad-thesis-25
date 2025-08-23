#!/usr/bin/env python3
"""
Interactive routing and gamification tester for community center design
"""

import os
import sys
import asyncio
from typing import Dict, List, Any

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
THESIS_AGENTS_DIR = os.path.join(PROJECT_ROOT, 'thesis-agents')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, THESIS_AGENTS_DIR)

from dotenv import load_dotenv
load_dotenv()

# Test sentences organized by expected behavior
TEST_SENTENCES = {
    "progressive_opening": [
        "I'm designing a community center in a converted warehouse",
        "My project is a new community center for a diverse neighborhood",
        "I need to create a community center that serves all ages"
    ],
    
    "knowledge_only_no_gamification": [
        "What are the best practices for circulation design in community centers?",
        "Can you guide me about how to create good circulation inside the building?",
        "What are ADA door width requirements for public buildings?",
        "Tell me about acoustic design principles for multi-use spaces"
    ],
    
    "design_exploration_no_gamification": [
        "I am thinking about creating nooks around the building that will serve as a transitional space",
        "How should I approach designing flexible learning spaces?",
        "What would be the best way to organize spaces considering user flow?",
        "I'm considering different approaches to wayfinding design"
    ],
    
    "socratic_clarification_with_gamification": [
        "I'm not sure how to balance privacy and openness in my design",
        "I'm confused about how to create flexible spaces that work for different activities",
        "I don't understand how to make spaces feel welcoming but not overwhelming"
    ],
    
    "cognitive_challenge_with_gamification": [
        "That makes sense",
        "OK",
        "I already know about accessibility design, what's next?",
        "This is pretty straightforward"
    ],
    
    "role_play_with_gamification": [
        "How would a visitor feel entering this space?",
        "How would an elderly person experience this layout?",
        "What would a child think about these play areas?"
    ],
    
    "creative_constraint_with_gamification": [
        "I'm completely stuck on this circulation problem",
        "I need fresh ideas for flexible programming spaces",
        "I'm having trouble with the acoustics in multi-use areas"
    ],
    
    "mystery_with_gamification": [
        "Users seem to avoid the main entrance area",
        "People aren't using the social spaces as intended",
        "The community room feels uncomfortable but I don't know why"
    ]
}

class InteractiveRoutingTester:
    """Interactive tester for routing and gamification"""
    
    def __init__(self):
        self.orchestrator = None
        self.results = []
        
    async def initialize(self):
        """Initialize the testing environment"""
        try:
            from orchestration.langgraph_orchestrator import LangGraphOrchestrator
            from state_manager import ArchMentorState
            
            self.orchestrator = LangGraphOrchestrator()
            print("✅ Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
    
    async def test_single_sentence(self, sentence: str, expected_category: str) -> Dict[str, Any]:
        """Test a single sentence and return results"""
        try:
            from state_manager import ArchMentorState
            
            # Create fresh state
            state = ArchMentorState()
            
            # Add context message for non-opening sentences
            if expected_category != "progressive_opening":
                state.messages.append({
                    "role": "user", 
                    "content": "I'm working on a community center project"
                })
                state.messages.append({
                    "role": "assistant",
                    "content": "Great! Community centers are wonderful spaces for bringing people together."
                })
            
            # Add test sentence
            state.messages.append({
                "role": "user",
                "content": sentence
            })
            
            # Process the sentence
            result = await self.orchestrator.process_student_input(state)
            
            # Extract key information
            route_taken = result.get("routing_path", "unknown")
            response_content = result.get("response", "")
            
            # Analyze gamification
            gamification_triggered = self._detect_gamification(response_content)
            
            return {
                "sentence": sentence,
                "expected_category": expected_category,
                "route_taken": route_taken,
                "gamification_triggered": gamification_triggered,
                "response_length": len(response_content),
                "success": True
            }
            
        except Exception as e:
            return {
                "sentence": sentence,
                "expected_category": expected_category,
                "route_taken": "error",
                "gamification_triggered": False,
                "response_length": 0,
                "error": str(e),
                "success": False
            }
    
    def _detect_gamification(self, response_content: str) -> bool:
        """Detect if gamification was triggered in the response"""
        gamification_indicators = [
            "🎮", "challenge", "perspective", "role-play", "imagine", 
            "detective", "mystery", "constraint", "game", "wheel",
            "persona", "choose", "select", "option"
        ]
        
        content_lower = response_content.lower()
        return any(indicator in content_lower for indicator in gamification_indicators)
    
    def display_menu(self):
        """Display the interactive menu"""
        print("\n" + "="*60)
        print("🧪 INTERACTIVE ROUTING & GAMIFICATION TESTER")
        print("="*60)
        print("\nChoose a test category:")
        
        categories = list(TEST_SENTENCES.keys())
        for i, category in enumerate(categories, 1):
            sentence_count = len(TEST_SENTENCES[category])
            print(f"{i:2d}. {category.replace('_', ' ').title()} ({sentence_count} sentences)")
        
        print(f"{len(categories)+1:2d}. Test All Categories")
        print(f"{len(categories)+2:2d}. Custom Sentence")
        print(f"{len(categories)+3:2d}. Exit")
        
        return categories
    
    async def test_category(self, category: str):
        """Test all sentences in a category"""
        sentences = TEST_SENTENCES[category]
        print(f"\n🧪 Testing {category.replace('_', ' ').title()}")
        print("-" * 50)
        
        results = []
        for i, sentence in enumerate(sentences, 1):
            print(f"\n[{i}/{len(sentences)}] Testing: \"{sentence[:60]}{'...' if len(sentence) > 60 else ''}\"")
            
            result = await self.test_single_sentence(sentence, category)
            results.append(result)
            
            if result["success"]:
                route = result["route_taken"]
                gamification = "🎮 Yes" if result["gamification_triggered"] else "❌ No"
                print(f"   Route: {route}")
                print(f"   Gamification: {gamification}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Summary for category
        successful_tests = [r for r in results if r["success"]]
        print(f"\n📊 Category Summary: {len(successful_tests)}/{len(results)} successful")
        
        return results
    
    async def test_custom_sentence(self):
        """Test a custom user-provided sentence"""
        print("\n📝 Custom Sentence Test")
        print("-" * 30)
        
        sentence = input("Enter your test sentence: ").strip()
        if not sentence:
            print("❌ No sentence provided")
            return
        
        expected_category = input("Expected category (optional): ").strip() or "custom"
        
        print(f"\n🧪 Testing: \"{sentence}\"")
        result = await self.test_single_sentence(sentence, expected_category)
        
        if result["success"]:
            print(f"✅ Route: {result['route_taken']}")
            print(f"🎮 Gamification: {'Yes' if result['gamification_triggered'] else 'No'}")
            print(f"📝 Response length: {result['response_length']} characters")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    async def test_all_categories(self):
        """Test all categories systematically"""
        print("\n🎯 COMPREHENSIVE TEST - ALL CATEGORIES")
        print("="*60)
        
        all_results = []
        
        for category in TEST_SENTENCES.keys():
            category_results = await self.test_category(category)
            all_results.extend(category_results)
        
        # Overall summary
        successful_tests = [r for r in all_results if r["success"]]
        total_tests = len(all_results)
        
        print(f"\n🎊 FINAL SUMMARY")
        print("="*40)
        print(f"Total tests: {total_tests}")
        print(f"Successful: {len(successful_tests)}")
        print(f"Failed: {total_tests - len(successful_tests)}")
        print(f"Success rate: {len(successful_tests)/total_tests*100:.1f}%")
        
        # Route distribution
        routes = {}
        gamification_count = 0
        
        for result in successful_tests:
            route = result["route_taken"]
            routes[route] = routes.get(route, 0) + 1
            if result["gamification_triggered"]:
                gamification_count += 1
        
        print(f"\n📊 Route Distribution:")
        for route, count in sorted(routes.items()):
            print(f"   {route}: {count}")
        
        print(f"\n🎮 Gamification triggered: {gamification_count}/{len(successful_tests)} tests")
    
    async def run_interactive_session(self):
        """Run the interactive testing session"""
        if not await self.initialize():
            return
        
        while True:
            categories = self.display_menu()
            
            try:
                choice = input(f"\nEnter your choice (1-{len(categories)+3}): ").strip()
                
                if not choice.isdigit():
                    print("❌ Please enter a valid number")
                    continue
                
                choice_num = int(choice)
                
                if choice_num == len(categories) + 3:  # Exit
                    print("👋 Goodbye!")
                    break
                elif choice_num == len(categories) + 2:  # Custom sentence
                    await self.test_custom_sentence()
                elif choice_num == len(categories) + 1:  # Test all
                    await self.test_all_categories()
                elif 1 <= choice_num <= len(categories):  # Specific category
                    category = categories[choice_num - 1]
                    await self.test_category(category)
                else:
                    print("❌ Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function"""
    tester = InteractiveRoutingTester()
    await tester.run_interactive_session()

if __name__ == "__main__":
    asyncio.run(main())
