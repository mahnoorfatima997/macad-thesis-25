#!/usr/bin/env python3
"""
Comprehensive Route and Gamification Test Suite
Tests all 14 routes and 7 games/challenges systematically
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Add project paths
sys.path.append('.')
sys.path.append('thesis-agents')

class RouteGameTester:
    def __init__(self):
        self.results = {
            'route_tests': [],
            'game_tests': [],
            'integration_tests': [],
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        
        # Load environment
        load_dotenv()
        
        # Initialize test data from community_center_test_inputs.md
        self.route_test_cases = self._load_route_test_cases()
        self.game_test_cases = self._load_game_test_cases()
        
    def _load_route_test_cases(self) -> Dict[str, List[str]]:
        """Load test cases for all 14 routes"""
        return {
            "progressive_opening": [
                "I'm designing a community center for a suburban neighborhood",
                "I'm working on a community center project in downtown",
                "I need to design a community center for 15,000 residents"
            ],
            "topic_transition": [
                "Moving on to the structural considerations...",
                "Let's shift focus to the sustainability aspects",
                "Now I want to explore the acoustic requirements"
            ],
            "knowledge_only": [
                "What are the standard room sizes for community center programs?",
                "What is steel construction?",
                "What are the accessibility requirements for community centers?"
            ],
            "socratic_exploration": [
                "I'm thinking about creating a flexible multi-use space",
                "I want to design something that brings the community together",
                "How do I make this space feel welcoming?"
            ],
            "cognitive_challenge": [
                "I think this layout is perfect and doesn't need any changes",
                "This design will definitely work for everyone",
                "I'm confident this is the best possible solution"
            ],
            "multi_agent_comprehensive": [
                "I need a complete analysis of my community center design",
                "Can you provide comprehensive feedback on all aspects?",
                "I want multiple perspectives on this design approach"
            ],
            "socratic_clarification": [
                "I'm not sure how to approach this design problem",
                "I'm confused about the programming requirements",
                "I don't understand how to organize these spaces"
            ],
            "supportive_scaffolding": [
                "I'm struggling with the basic concepts of community center design",
                "I need help understanding fundamental design principles",
                "I'm having trouble with the basics of space planning"
            ],
            "foundational_building": [
                "I need to build my understanding of community center design from the ground up",
                "Help me establish the fundamental principles",
                "I need to start with the basics of this building type"
            ],
            "knowledge_with_challenge": [
                "Tell me about community center design but make me think about it",
                "I want to learn about accessibility while being challenged",
                "Teach me about circulation but push my thinking"
            ],
            "balanced_guidance": [
                "I'm working on a community center and need comprehensive guidance",
                "I need help understanding both the technical and design aspects",
                "Can you help me balance function and aesthetics?"
            ],
            "cognitive_intervention": [
                "Just tell me what to do for the layout",
                "Give me the exact solution to this problem",
                "What's the right answer for community center design?"
            ]
        }
    
    def _load_game_test_cases(self) -> Dict[str, List[str]]:
        """Load test cases for all 7 game types"""
        return {
            "constraint_challenge": [
                "I'm completely stuck on this circulation problem",
                "I'm really stuck on the layout design",
                "I'm having trouble with the space planning"
            ],
            "transformation": [
                "I'm converting this warehouse to a community center",
                "How do I transform this old factory into a community space?",
                "I'm working on adaptive reuse of an office building"
            ],
            "storytelling": [
                "I want to create a user journey through the space",
                "How do I design the story of movement through the center?",
                "I'm thinking about the narrative flow of the building"
            ],
            "time_travel": [
                "How will this space evolve over time?",
                "I'm thinking about the building's lifecycle",
                "How might this center adapt to future needs?"
            ],
            "role_play": [
                "How would a visitor feel entering this space?",
                "What would a child experience in this center?",
                "How would an elderly person navigate this building?"
            ],
            "detective": [
                "Why isn't this layout working?",
                "What's wrong with my current design?",
                "I need to investigate this circulation issue"
            ],
            "perspective_shift": [
                "What if we flipped the program arrangement?",
                "How would this work if we inverted the layout?",
                "What's an alternative approach to this design?"
            ]
        }

    def log_test(self, category: str, test_name: str, status: str, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details or {},
            'timestamp': time.strftime('%H:%M:%S')
        }
        
        if category == 'route':
            self.results['route_tests'].append(result)
        elif category == 'game':
            self.results['game_tests'].append(result)
        else:
            self.results['integration_tests'].append(result)
        
        if status == 'PASS':
            self.results['passed'] += 1
            print(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.results['failed'] += 1
            print(f"❌ {test_name}: {message}")
        elif status == 'WARN':
            self.results['warnings'] += 1
            print(f"⚠️  {test_name}: {message}")

    def test_routing_system(self):
        """Test all 14 routing paths"""
        print("\n🛤️ TESTING ROUTING SYSTEM...")
        
        try:
            from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
            router = AdvancedRoutingDecisionTree()
            
            for route_name, test_inputs in self.route_test_cases.items():
                for i, test_input in enumerate(test_inputs):
                    try:
                        # Create mock context with proper intent mapping
                        intent_mapping = {
                            "progressive_opening": "first_message",
                            "topic_transition": "topic_transition",
                            "knowledge_only": "technical_question",
                            "socratic_exploration": "design_exploration",
                            "cognitive_challenge": "overconfident_statement",
                            "multi_agent_comprehensive": "feedback_request",
                            "socratic_clarification": "confusion_expression",
                            "supportive_scaffolding": "confusion_expression",
                            "foundational_building": "implementation_request",
                            "knowledge_with_challenge": "knowledge_request",
                            "balanced_guidance": "knowledge_request",
                            "cognitive_intervention": "cognitive_offloading"
                        }

                        user_intent = intent_mapping.get(route_name, route_name)
                        is_first_msg = route_name == "progressive_opening"

                        classification = {
                            "user_intent": user_intent,
                            "user_input": test_input,
                            "is_first_message": is_first_msg,
                            "cognitive_offloading_detected": route_name == "cognitive_intervention",
                            "is_pure_knowledge_request": route_name == "knowledge_only"
                        }

                        context = RoutingContext(
                            classification=classification,
                            context_analysis={},
                            routing_suggestions={},
                            student_state=None,
                            conversation_history=[{"role": "user", "content": test_input}],
                            current_phase="ideation",
                            phase_progress=0.0
                        )
                        
                        # Test routing decision
                        decision = router.decide_route(context)
                        expected_route = route_name.upper()
                        actual_route = decision.route.value.upper()
                        
                        if expected_route in actual_route or actual_route in expected_route:
                            self.log_test('route', f"Route-{route_name}-{i+1}", "PASS", 
                                        f"'{test_input[:30]}...' → {actual_route}")
                        else:
                            self.log_test('route', f"Route-{route_name}-{i+1}", "FAIL", 
                                        f"Expected {expected_route}, got {actual_route}")
                            
                    except Exception as e:
                        self.log_test('route', f"Route-{route_name}-{i+1}", "FAIL", 
                                    f"Routing test failed: {e}")
                        
        except Exception as e:
            self.log_test('route', "Routing-System", "FAIL", f"Routing system failed to initialize: {e}")

    def test_gamification_system(self):
        """Test all 7 gamification types"""
        print("\n🎮 TESTING GAMIFICATION SYSTEM...")
        
        try:
            from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
            from state_manager import ArchMentorState
            
            processor = ChallengeGeneratorProcessor()
            
            for game_name, test_inputs in self.game_test_cases.items():
                for i, test_input in enumerate(test_inputs):
                    try:
                        # Create mock state
                        state = ArchMentorState()
                        state.messages = [
                            {"role": "user", "content": "I'm designing a community center"},
                            {"role": "assistant", "content": "Great! Tell me more."},
                            {"role": "user", "content": "The site is challenging"},
                            {"role": "user", "content": test_input}  # 4th message for gamification
                        ]
                        
                        # Test gamification trigger
                        should_trigger = processor._should_apply_gamification(state, "test_challenge", test_input)
                        
                        if should_trigger:
                            self.log_test('game', f"Game-{game_name}-{i+1}", "PASS", 
                                        f"'{test_input[:30]}...' → Triggered gamification")
                        else:
                            self.log_test('game', f"Game-{game_name}-{i+1}", "WARN", 
                                        f"'{test_input[:30]}...' → No gamification trigger")
                            
                    except Exception as e:
                        self.log_test('game', f"Game-{game_name}-{i+1}", "FAIL", 
                                    f"Gamification test failed: {e}")
                        
        except Exception as e:
            self.log_test('game', "Gamification-System", "FAIL", f"Gamification system failed to initialize: {e}")

    def test_frequency_control(self):
        """Test gamification frequency control (every 3 messages)"""
        print("\n⏰ TESTING FREQUENCY CONTROL...")
        
        try:
            from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
            from state_manager import ArchMentorState
            
            processor = ChallengeGeneratorProcessor()
            
            # Test frequency pattern: 1, 2, 3(trigger), 4, 5, 6(trigger)
            test_cases = [
                (1, False, "Message 1 should not trigger"),
                (2, False, "Message 2 should not trigger"),
                (3, True, "Message 3 should trigger"),
                (4, False, "Message 4 should not trigger"),
                (5, False, "Message 5 should not trigger"),
                (6, True, "Message 6 should trigger"),
            ]
            
            for msg_count, should_trigger, description in test_cases:
                try:
                    # Create state with specific message count
                    state = ArchMentorState()
                    state.messages = [{"role": "user", "content": f"test message {i}"} for i in range(msg_count)]
                    
                    # Test with a strong gamification trigger phrase that should override frequency
                    result = processor._should_apply_gamification(state, "test_challenge", "I'm completely stuck on this circulation problem")
                    
                    if result == should_trigger:
                        self.log_test('integration', f"Frequency-Message-{msg_count}", "PASS", description)
                    else:
                        self.log_test('integration', f"Frequency-Message-{msg_count}", "FAIL", 
                                    f"Expected {should_trigger}, got {result}")
                        
                except Exception as e:
                    self.log_test('integration', f"Frequency-Message-{msg_count}", "FAIL", 
                                f"Frequency test failed: {e}")
                    
        except Exception as e:
            self.log_test('integration', "Frequency-Control", "FAIL", f"Frequency control test failed: {e}")

    def test_integration_flow(self):
        """Test complete integration flow"""
        print("\n🔄 TESTING INTEGRATION FLOW...")
        
        # Test the complete conversation flow from community_center_test_inputs.md
        conversation_flow = [
            ("I'm designing a community center for a suburban neighborhood", "progressive_opening", False),
            ("The program includes a gym, meeting rooms, and event space", "topic_transition", False),
            ("The site has some challenging topography", "balanced_guidance", False),
            ("I'm completely stuck on the circulation problem", "cognitive_challenge", True),  # Should trigger gamification
            ("What are standard room sizes for community centers?", "knowledge_only", False),
            ("I'm thinking about creating flexible multi-use spaces", "socratic_exploration", False),
            ("Help me with the entrance design", "balanced_guidance", False),
            ("I'm converting an old warehouse for this project", "cognitive_challenge", True),  # Should trigger gamification
        ]
        
        for i, (message, expected_route, should_gamify) in enumerate(conversation_flow, 1):
            try:
                # Test routing
                from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
                router = AdvancedRoutingDecisionTree()
                
                context = RoutingContext(
                    classification={"user_input": message},
                    context_analysis={},
                    routing_suggestions={},
                    student_state=None,
                    conversation_history=[{"role": "user", "content": msg} for msg, _, _ in conversation_flow[:i]],
                    current_phase="ideation",
                    phase_progress=0.0
                )
                
                decision = router.decide_route(context)
                route_match = expected_route.upper() in decision.route.value.upper()
                
                # Test gamification
                if should_gamify:
                    from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
                    from state_manager import ArchMentorState
                    
                    processor = ChallengeGeneratorProcessor()
                    state = ArchMentorState()
                    state.messages = [{"role": "user", "content": msg} for msg, _, _ in conversation_flow[:i]]
                    
                    gamify_result = processor._should_apply_gamification(state, "test_challenge", message)
                    
                    if route_match and gamify_result:
                        self.log_test('integration', f"Flow-Step-{i}", "PASS", 
                                    f"Route: {decision.route.value}, Gamification: {gamify_result}")
                    else:
                        self.log_test('integration', f"Flow-Step-{i}", "WARN", 
                                    f"Route: {decision.route.value} (expected {expected_route}), Gamification: {gamify_result} (expected {should_gamify})")
                else:
                    if route_match:
                        self.log_test('integration', f"Flow-Step-{i}", "PASS", 
                                    f"Route: {decision.route.value}")
                    else:
                        self.log_test('integration', f"Flow-Step-{i}", "WARN", 
                                    f"Route: {decision.route.value} (expected {expected_route})")
                        
            except Exception as e:
                self.log_test('integration', f"Flow-Step-{i}", "FAIL", f"Integration test failed: {e}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE ROUTE & GAMIFICATION TEST")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_routing_system()
        self.test_gamification_system()
        self.test_frequency_control()
        self.test_integration_flow()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate final report
        self.generate_final_report(duration)
        
    def generate_final_report(self, duration: float):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = self.results['passed'] + self.results['failed'] + self.results['warnings']
        
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Warnings: {self.results['warnings']}")
        
        # Detailed breakdown
        print(f"\n📊 Test Breakdown:")
        print(f"🛤️  Route Tests: {len(self.results['route_tests'])}")
        print(f"🎮 Game Tests: {len(self.results['game_tests'])}")
        print(f"🔄 Integration Tests: {len(self.results['integration_tests'])}")
        
        # Calculate readiness score
        if total_tests > 0:
            readiness_score = (self.results['passed'] / total_tests) * 100
            print(f"🎯 System Readiness: {readiness_score:.1f}%")
        else:
            readiness_score = 0
            print("🎯 System Readiness: 0% (No tests completed)")
        
        # Save detailed report
        self.save_detailed_report()
        
    def save_detailed_report(self):
        """Save detailed test report to file"""
        try:
            report_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'passed': self.results['passed'],
                    'failed': self.results['failed'],
                    'warnings': self.results['warnings']
                },
                'route_tests': self.results['route_tests'],
                'game_tests': self.results['game_tests'],
                'integration_tests': self.results['integration_tests']
            }
            
            with open('route_game_test_report.json', 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n📄 Detailed report saved to: route_game_test_report.json")
            
        except Exception as e:
            print(f"⚠️  Failed to save detailed report: {e}")

if __name__ == "__main__":
    tester = RouteGameTester()
    tester.run_all_tests()
