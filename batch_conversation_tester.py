#!/usr/bin/env python3
"""
Batch Conversation Tester for Mega Architectural Mentor
Runs predefined test scenarios to validate conversation flows
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Add thesis-agents to path
sys.path.append('./thesis-agents')

from state_manager import ArchMentorState, StudentProfile, DesignPhase
from orchestration.langgraph_orchestrator import LangGraphOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_api_key():
    """Load API key using secrets manager (supports both st.secrets and environment variables)"""
    try:
        # Add thesis-agents to path for imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))
        from utils.secrets_manager import get_openai_api_key

        api_key = get_openai_api_key()
        if api_key:
            logger.info("✅ API key loaded via secrets manager")
            return api_key
        else:
            logger.warning("⚠️ API key not found via secrets manager")
            return None

    except ImportError:
        logger.warning("⚠️ Secrets manager not available, falling back to manual loading")

        # Fallback to manual .env file loading
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == 'OPENAI_API_KEY':
                                # Remove quotes if present
                                api_key = value.strip().strip('"').strip("'")
                                if api_key:
                                    logger.info("✅ API key loaded from .env file")
                                    return api_key
            except Exception as e:
                logger.warning(f"⚠️ Could not read .env file: {e}")

        # Fallback to environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info("✅ API key loaded from environment variable")
            return api_key

        return None
    except Exception as e:
        logger.error(f"❌ Error loading API key via secrets manager: {e}")
        return None

class TestScenario:
    """Defines a test scenario with expected outcomes"""
    
    def __init__(self, name: str, messages: List[str], expected_agents: List[str] = None, 
                 expected_response_types: List[str] = None):
        self.name = name
        self.messages = messages
        self.expected_agents = expected_agents or []
        self.expected_response_types = expected_response_types or []

class BatchConversationTester:
    """Batch tester for running predefined test scenarios"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._initialize_components()
        self._define_test_scenarios()
        
    def _initialize_components(self):
        """Initialize the orchestrator and state"""
        try:
            # Create a test student profile with correct parameters
            student_profile = StudentProfile(
                skill_level="intermediate",
                learning_style="visual",
                cognitive_load=0.3,
                engagement_level=0.7
            )
            
            self.arch_state = ArchMentorState(
                student_profile=student_profile,
                design_phase=DesignPhase.IDEATION,
                messages=[]
            )
            
            # Initialize orchestrator
            self.orchestrator = LangGraphOrchestrator(domain="architecture")
            
            logger.info("✅ Batch tester initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            raise
    
    def _define_test_scenarios(self):
        """Define test scenarios"""
        self.test_scenarios = [
            TestScenario(
                name="Basic Architecture Questions",
                messages=[
                    "What is the difference between form and function?",
                    "How do I start designing a residential building?",
                    "What are the basic principles of sustainable design?"
                ],
                expected_agents=["SocraticTutorAgent", "DomainExpertAgent"],
                expected_response_types=["educational", "guidance"]
            ),
            TestScenario(
                name="Technical Design Questions",
                messages=[
                    "How can I improve the circulation flow in my museum design?",
                    "What are the best practices for integrating sustainable systems?",
                    "How do I balance aesthetics with functionality in commercial spaces?"
                ],
                expected_agents=["DomainExpertAgent", "AnalysisAgent"],
                expected_response_types=["analysis", "guidance"]
            ),
            TestScenario(
                name="Advanced Concepts",
                messages=[
                    "How can I integrate biomimicry principles in urban planning?",
                    "What are the implications of AI in architectural design processes?",
                    "How do I develop a research methodology for my thesis?"
                ],
                expected_agents=["CognitiveEnhancementAgent", "DomainExpertAgent"],
                expected_response_types=["theoretical", "research"]
            ),
            TestScenario(
                name="Software and Tools",
                messages=[
                    "What software should I learn for architectural modeling?",
                    "How do I use Revit for sustainable design?",
                    "What are the best practices for BIM workflows?"
                ],
                expected_agents=["DomainExpertAgent"],
                expected_response_types=["technical", "guidance"]
            ),
            TestScenario(
                name="Project Feedback",
                messages=[
                    "Can you critique my floor plan for this office building?",
                    "How can I improve the energy efficiency of my design?",
                    "What are the potential issues with my structural approach?"
                ],
                expected_agents=["AnalysisAgent", "DomainExpertAgent"],
                expected_response_types=["critique", "analysis"]
            )
        ]
    
    async def run_single_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """Run a single test scenario"""
        
        print(f"\n🧪 Running scenario: {scenario.name}")
        print(f"📝 Messages: {len(scenario.messages)}")
        print("=" * 60)
        
        results = {
            "scenario_name": scenario.name,
            "timestamp": datetime.now().isoformat(),
            "messages": [],
            "summary": {}
        }
        
        # Clear conversation state for fresh start
        self.arch_state.messages = []
        
        for i, message in enumerate(scenario.messages, 1):
            print(f"\n--- Message {i}/{len(scenario.messages)} ---")
            print(f"👤 User: {message}")
            
            try:
                # Process through orchestrator
                result = await self.orchestrator.process_student_input(self.arch_state)
                
                response = result.get("response", "No response")
                metadata = result.get("metadata", {})
                
                print(f"🤖 Assistant: {response[:150]}...")
                
                # Log the exchange
                message_result = {
                    "message_number": i,
                    "user_message": message,
                    "assistant_response": response,
                    "metadata": metadata,
                    "success": True
                }
                
                results["messages"].append(message_result)
                
                # Update state
                self.arch_state.messages.append({"role": "user", "content": message})
                self.arch_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                logger.error(f"❌ Error in message {i}: {e}")
                message_result = {
                    "message_number": i,
                    "user_message": message,
                    "error": str(e),
                    "success": False
                }
                results["messages"].append(message_result)
                break
        
        # Generate summary
        results["summary"] = self._analyze_scenario_results(scenario, results["messages"])
        
        return results
    
    def _analyze_scenario_results(self, scenario: TestScenario, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze results for a scenario"""
        
        successful_messages = [m for m in messages if m["success"]]
        failed_messages = [m for m in messages if not m["success"]]
        
        # Collect metadata
        all_agents = []
        all_response_types = []
        all_confidence_scores = []
        
        for message in successful_messages:
            metadata = message.get("metadata", {})
            all_agents.extend(metadata.get("agents_used", []))
            all_response_types.append(metadata.get("response_type", "unknown"))
            all_confidence_scores.append(metadata.get("confidence_score", 0.5))
        
        # Calculate metrics
        success_rate = len(successful_messages) / len(messages) if messages else 0
        avg_confidence = sum(all_confidence_scores) / len(all_confidence_scores) if all_confidence_scores else 0
        unique_agents = list(set(all_agents))
        
        # Check expectations
        expected_agent_match = any(agent in unique_agents for agent in scenario.expected_agents)
        expected_response_match = any(rt in all_response_types for rt in scenario.expected_response_types)
        
        return {
            "total_messages": len(messages),
            "successful_messages": len(successful_messages),
            "failed_messages": len(failed_messages),
            "success_rate": success_rate,
            "average_confidence": avg_confidence,
            "unique_agents_used": unique_agents,
            "response_types": list(set(all_response_types)),
            "expected_agent_match": expected_agent_match,
            "expected_response_match": expected_response_match,
            "overall_score": (success_rate + (1 if expected_agent_match else 0) + (1 if expected_response_match else 0)) / 3
        }
    
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all test scenarios"""
        
        print("🧪 Running all test scenarios...")
        print("=" * 60)
        
        all_results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": {},
            "overall_summary": {}
        }
        
        for scenario in self.test_scenarios:
            result = await self.run_single_scenario(scenario)
            all_results["scenarios"][scenario.name] = result
        
        # Generate overall summary
        all_results["overall_summary"] = self._generate_overall_summary(all_results["scenarios"])
        
        return all_results
    
    def _generate_overall_summary(self, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary across all scenarios"""
        
        total_scenarios = len(scenario_results)
        successful_scenarios = 0
        total_messages = 0
        total_successful_messages = 0
        all_agents = []
        all_scores = []
        
        for scenario_name, result in scenario_results.items():
            summary = result["summary"]
            total_messages += summary["total_messages"]
            total_successful_messages += summary["successful_messages"]
            all_agents.extend(summary["unique_agents_used"])
            all_scores.append(summary["overall_score"])
            
            if summary["success_rate"] > 0.8:  # 80% success threshold
                successful_scenarios += 1
        
        return {
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "scenario_success_rate": successful_scenarios / total_scenarios if total_scenarios > 0 else 0,
            "total_messages": total_messages,
            "message_success_rate": total_successful_messages / total_messages if total_messages > 0 else 0,
            "unique_agents_used_total": list(set(all_agents)),
            "average_overall_score": sum(all_scores) / len(all_scores) if all_scores else 0,
            "scenario_performance": {
                name: {
                    "success_rate": result["summary"]["success_rate"],
                    "overall_score": result["summary"]["overall_score"]
                }
                for name, result in scenario_results.items()
            }
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_test_results_{timestamp}.json"
        
        output_path = Path("results") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"💾 Results saved to: {output_path}")
        return output_path

def main():
    """Main function"""
    
    # Load API key from .env file or environment
    api_key = load_api_key()
    if not api_key:
        print("❌ OpenAI API key not found")
        print("Please ensure you have:")
        print("1. A .env file with OPENAI_API_KEY=\"your-key-here\"")
        print("2. Or set the OPENAI_API_KEY environment variable")
        return
    
    print("🧪 Batch Conversation Tester")
    print("=" * 40)
    
    # Initialize tester
    try:
        tester = BatchConversationTester(api_key)
    except Exception as e:
        print(f"❌ Failed to initialize tester: {e}")
        return
    
    # Test options
    print(f"\nAvailable test scenarios ({len(tester.test_scenarios)}):")
    for i, scenario in enumerate(tester.test_scenarios, 1):
        print(f"{i}. {scenario.name} ({len(scenario.messages)} messages)")
    
    print("\nSelect test mode:")
    print("1. Run all scenarios")
    print("2. Run specific scenario")
    print("3. Quick validation test")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Run all scenarios
        print("\n🧪 Running all scenarios...")
        results = asyncio.run(tester.run_all_scenarios())
        
    elif choice == "2":
        # Run specific scenario
        print("\nSelect scenario (1-5):")
        scenario_choice = input("Enter scenario number: ").strip()
        
        try:
            scenario_index = int(scenario_choice) - 1
            if 0 <= scenario_index < len(tester.test_scenarios):
                scenario = tester.test_scenarios[scenario_index]
                results = asyncio.run(tester.run_single_scenario(scenario))
            else:
                print("Invalid scenario number. Exiting.")
                return
        except ValueError:
            print("Invalid input. Exiting.")
            return
        
    elif choice == "3":
        # Quick validation test
        print("\n🧪 Running quick validation test...")
        quick_scenario = TestScenario(
            name="Quick Validation",
            messages=[
                "What is sustainable design?",
                "How do I start a building project?"
            ]
        )
        results = asyncio.run(tester.run_single_scenario(quick_scenario))
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Save results
    filename = tester.save_results(results)
    
    # Print summary
    if "overall_summary" in results:
        summary = results["overall_summary"]
        print(f"\n📊 Overall Test Summary:")
        print(f"   Scenarios: {summary['total_scenarios']}")
        print(f"   Successful scenarios: {summary['successful_scenarios']}")
        print(f"   Scenario success rate: {summary['scenario_success_rate']:.1%}")
        print(f"   Message success rate: {summary['message_success_rate']:.1%}")
        print(f"   Average score: {summary['average_overall_score']:.2f}")
    else:
        summary = results["summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Messages: {summary['total_messages']}")
        print(f"   Success rate: {summary['success_rate']:.1%}")
        print(f"   Overall score: {summary['overall_score']:.2f}")
    
    print(f"\n💾 Results saved to: {filename}")

if __name__ == "__main__":
    main() 