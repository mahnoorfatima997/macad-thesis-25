#!/usr/bin/env python3
"""
RAG Conversation Tester for Mega Architectural Mentor
A text-only testing interface to debug conversation flows without the Streamlit UI
"""

import asyncio
import json
import logging
import argparse
from enum import Enum
from dataclasses import is_dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os

# Add thesis-agents to path
sys.path.append('./thesis-agents')

from state_manager import ArchMentorState, StudentProfile, DesignPhase
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
from data_collection.interaction_logger import InteractionLogger
from agents.analysis_agent import AnalysisAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_conversation_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_api_key():
    """Load API key from .env file or environment variable"""
    # First try to load from .env file
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


def make_json_safe(obj):
    """Recursively convert objects to JSON-serializable forms.

    - dataclasses → dict
    - Enum → value
    - datetime → isoformat
    - objects with __dict__ → dict of json-safe fields
    - fallback → str(obj)
    """
    # Primitives
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    # Dataclass
    if is_dataclass(obj):
        return make_json_safe(asdict(obj))
    # Enum
    if isinstance(obj, Enum):
        return obj.value
    # datetime-like
    if hasattr(obj, 'isoformat'):
        try:
            return obj.isoformat()
        except Exception:
            pass
    # Mapping
    if isinstance(obj, dict):
        return {make_json_safe(k): make_json_safe(v) for k, v in obj.items()}
    # Iterable
    if isinstance(obj, (list, tuple, set)):
        return [make_json_safe(x) for x in obj]
    # Generic object with __dict__
    if hasattr(obj, '__dict__'):
        try:
            return make_json_safe(vars(obj))
        except Exception:
            pass
    # Fallback string
    return str(obj)

class UserPersona:
    """Defines different user personas for testing"""
    
    PERSONAS = {
        "beginner_student": {
            "skill_level": "beginner",
            "learning_style": "visual",
            "cognitive_load": 0.5,
            "engagement_level": 0.8,
            "communication_style": "Asks basic questions, needs clear explanations",
            "typical_questions": [
                "What is the difference between form and function?",
                "How do I start designing a residential building?",
                "What are the basic principles of sustainable design?",
                "Can you explain the concept of scale in architecture?",
                "What software should I learn first?"
            ]
        },
        "intermediate_student": {
            "skill_level": "intermediate",
            "learning_style": "visual",
            "cognitive_load": 0.3,
            "engagement_level": 0.7,
            "communication_style": "Asks detailed questions, seeks feedback on specific projects",
            "typical_questions": [
                "How can I improve the circulation flow in my museum design?",
                "What are the best practices for integrating sustainable systems?",
                "How do I balance aesthetics with functionality in commercial spaces?",
                "Can you critique my floor plan for this office building?",
                "What are the current trends in parametric design?"
            ]
        },
        "advanced_student": {
            "skill_level": "advanced",
            "learning_style": "analytical",
            "cognitive_load": 0.2,
            "engagement_level": 0.9,
            "communication_style": "Discusses complex concepts, seeks theoretical insights",
            "typical_questions": [
                "How can I integrate biomimicry principles in urban planning?",
                "What are the implications of AI in architectural design processes?",
                "How do I develop a research methodology for my thesis?",
                "Can you analyze the cultural context of my international project?",
                "What are the emerging paradigms in computational design?"
            ]
        },
        "professional_architect": {
            "skill_level": "expert",
            "learning_style": "analytical",
            "cognitive_load": 0.1,
            "engagement_level": 0.95,
            "communication_style": "Discusses advanced concepts, seeks peer-level insights",
            "typical_questions": [
                "How can I integrate BIM workflows with sustainable certification processes?",
                "What are the implications of generative AI for architectural practice?",
                "How do I develop a firm's approach to climate-responsive design?",
                "Can you help me structure a continuing education program?",
                "What are the emerging business models in architectural services?"
            ]
        }
    }

class RAGConversationTester:
    """RAG-based conversation tester for debugging the mega architectural mentor"""
    
    def __init__(self, api_key: str, persona_name: str = "intermediate_student"):
        self.api_key = api_key
        self.persona = UserPersona.PERSONAS.get(persona_name, UserPersona.PERSONAS["intermediate_student"])
        self.conversation_history = []
        self.test_results = []
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize the orchestrator and state manager"""
        try:
            # Initialize state with correct StudentProfile parameters
            student_profile = StudentProfile(
                skill_level=self.persona["skill_level"],
                learning_style=self.persona["learning_style"],
                cognitive_load=self.persona["cognitive_load"],
                engagement_level=self.persona["engagement_level"]
            )
            
            self.arch_state = ArchMentorState(
                student_profile=student_profile,
                design_phase=DesignPhase.IDEATION,
                messages=[]
            )
            
            # Initialize orchestrator
            self.orchestrator = LangGraphOrchestrator(domain="architecture")
            
            # Initialize interaction logger
            self.interaction_logger = InteractionLogger()
            
            logger.info(f"✅ Initialized RAG tester for persona: {self.persona['skill_level']} level")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
    
    async def simulate_conversation(self, num_exchanges: int = 5,
                                   custom_questions: Optional[List[str]] = None,
                                   collect_quality: bool = True) -> Dict[str, Any]:
        """Simulate a conversation with the architectural mentor"""
        
        logger.info(f"🎭 Starting conversation simulation with {self.persona['skill_level']} level student")
        logger.info(f"📝 Learning style: {self.persona['learning_style']}")
        logger.info(f"🎯 Communication style: {self.persona['communication_style']}")
        
        conversation_log = {
            "persona": self.persona,
            "timestamp": datetime.now().isoformat(),
            "exchanges": [],
            "summary": {}
        }
        
        # Use custom questions or generate from persona
        questions = custom_questions or self.persona["typical_questions"]
        
        for i in range(min(num_exchanges, len(questions))):
            user_question = questions[i]

            logger.info(f"\n--- Exchange {i+1}/{num_exchanges} ---")
            logger.info(f"👤 {self.persona['skill_level']} Student: {user_question}")

            # Push current user message into state BEFORE processing
            self.arch_state.messages.append({
                "role": "user",
                "content": user_question,
            })

            # Process through orchestrator
            try:
                result = await self.orchestrator.process_student_input(self.arch_state)
                
                assistant_response = result.get("response", "No response generated")
                metadata = result.get("metadata", {})
                quality = metadata.get("quality", {}) if isinstance(metadata, dict) else {}
                
                logger.info(f"🤖 Assistant: {assistant_response[:200]}...")
                logger.info(f"📊 Metadata: {metadata}")
                
                # Log exchange
                exchange = {
                    "exchange_number": i + 1,
                    "user_question": user_question,
                    "assistant_response": assistant_response,
                    "metadata": metadata,
                    "quality": quality if collect_quality else {},
                    "timestamp": datetime.now().isoformat()
                }
                
                conversation_log["exchanges"].append(exchange)
                
                # Update state with assistant response
                self.arch_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
                
            except Exception as e:
                logger.error(f"❌ Error in exchange {i+1}: {e}")
                exchange = {
                    "exchange_number": i + 1,
                    "user_question": user_question,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                conversation_log["exchanges"].append(exchange)
        
        # Generate conversation summary
        conversation_log["summary"] = self._analyze_conversation(conversation_log)
        if collect_quality:
            conversation_log["quality_summary"] = self._analyze_quality(conversation_log)
        
        return conversation_log
    
    def _analyze_conversation(self, conversation_log: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the conversation for insights"""
        
        exchanges = conversation_log["exchanges"]
        
        # Count successful vs failed exchanges
        successful_exchanges = len([e for e in exchanges if "assistant_response" in e])
        failed_exchanges = len([e for e in exchanges if "error" in e])
        
        # Analyze response types
        response_types = []
        agents_used = []
        confidence_scores = []
        
        for exchange in exchanges:
            if "metadata" in exchange:
                metadata = exchange["metadata"]
                response_types.append(metadata.get("response_type", "unknown"))
                agents_used.extend(metadata.get("agents_used", []))
                confidence_scores.append(metadata.get("confidence_score", 0.5))
        
        # Calculate averages
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        unique_agents = list(set(agents_used))
        
        return {
            "total_exchanges": len(exchanges),
            "successful_exchanges": successful_exchanges,
            "failed_exchanges": failed_exchanges,
            "success_rate": successful_exchanges / len(exchanges) if exchanges else 0,
            "average_confidence": avg_confidence,
            "unique_agents_used": unique_agents,
            "response_type_distribution": {rt: response_types.count(rt) for rt in set(response_types)},
            "agent_usage_distribution": {agent: agents_used.count(agent) for agent in unique_agents}
        }

    def _analyze_quality(self, conversation_log: Dict[str, Any]) -> Dict[str, Any]:
        """Compute simple pass/fail counts for quality bits per assistant turn."""
        exchanges = conversation_log.get("exchanges", [])
        q_items = [e.get("quality", {}) for e in exchanges if e.get("assistant_response")]
        total = len(q_items)
        if total == 0:
            return {"total": 0}
        ends_q = sum(1 for q in q_items if q.get("ends_with_question"))
        bullets = sum(1 for q in q_items if q.get("has_bullets"))
        synth = sum(1 for q in q_items if q.get("has_synthesis_header"))
        avg_len = sum(int(q.get("char_length", 0)) for q in q_items) / total
        return {
            "total": total,
            "ends_with_question_count": ends_q,
            "has_bullets_count": bullets,
            "has_synthesis_header_count": synth,
            "avg_char_length": avg_len,
            "ends_with_question_pct": ends_q / total,
            "has_bullets_pct": bullets / total,
            "has_synthesis_header_pct": synth / total,
        }
    
    def run_multiple_persona_tests(self, num_exchanges: int = 3) -> Dict[str, Any]:
        """Run tests with multiple personas"""
        
        logger.info("🧪 Running multi-persona conversation tests...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "persona_results": {},
            "overall_summary": {}
        }
        
        for persona_name in UserPersona.PERSONAS.keys():
            logger.info(f"\n🎭 Testing persona: {persona_name}")
            
            # Create new tester instance for each persona
            persona_tester = RAGConversationTester(self.api_key, persona_name)
            
            # Run conversation
            conversation_log = asyncio.run(
                persona_tester.simulate_conversation(num_exchanges)
            )
            
            test_results["persona_results"][persona_name] = conversation_log
        
        # Generate overall summary
        test_results["overall_summary"] = self._generate_overall_summary(test_results["persona_results"])
        
        return test_results
    
    def _generate_overall_summary(self, persona_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary across all personas"""
        
        total_exchanges = 0
        total_successful = 0
        total_failed = 0
        all_agents = []
        all_confidence_scores = []
        
        for persona_name, result in persona_results.items():
            summary = result["summary"]
            total_exchanges += summary["total_exchanges"]
            total_successful += summary["successful_exchanges"]
            total_failed += summary["failed_exchanges"]
            all_agents.extend(summary["unique_agents_used"])
            all_confidence_scores.append(summary["average_confidence"])
        
        return {
            "total_personas_tested": len(persona_results),
            "total_exchanges": total_exchanges,
            "overall_success_rate": total_successful / total_exchanges if total_exchanges > 0 else 0,
            "average_confidence_across_personas": sum(all_confidence_scores) / len(all_confidence_scores) if all_confidence_scores else 0,
            "unique_agents_used_total": list(set(all_agents)),
            "persona_performance": {
                persona: {
                    "success_rate": result["summary"]["success_rate"],
                    "average_confidence": result["summary"]["average_confidence"]
                }
                for persona, result in persona_results.items()
            }
        }
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_test_results_{timestamp}.json"
        
        output_path = Path("results") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        safe_results = make_json_safe(results)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(safe_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Test results saved to: {output_path}")
        return output_path

    def save_quality_csv(self, results: Dict[str, Any], filename: str = None):
        """Save per-exchange quality bits to a CSV in results/ if present."""
        exchanges = results.get("exchanges") or results.get("persona_results")
        # Handle single persona (dict with exchanges) vs. multi-persona (dict keyed by persona)
        rows: List[Dict[str, Any]] = []
        if isinstance(exchanges, list):
            # Single persona log
            for e in results.get("exchanges", []):
                q = e.get("quality", {}) or {}
                rows.append({
                    "exchange": e.get("exchange_number"),
                    "ends_with_question": q.get("ends_with_question"),
                    "has_bullets": q.get("has_bullets"),
                    "has_synthesis_header": q.get("has_synthesis_header"),
                    "char_length": q.get("char_length"),
                })
        elif isinstance(exchanges, dict):
            # Multi-persona: flatten
            for persona, convo in results.get("persona_results", {}).items():
                for e in convo.get("exchanges", []):
                    q = e.get("quality", {}) or {}
                    rows.append({
                        "persona": persona,
                        "exchange": e.get("exchange_number"),
                        "ends_with_question": q.get("ends_with_question"),
                        "has_bullets": q.get("has_bullets"),
                        "has_synthesis_header": q.get("has_synthesis_header"),
                        "char_length": q.get("char_length"),
                    })
        if not rows:
            return None
        import csv
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_quality_{timestamp}.csv"
        output_path = Path("results") / filename
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        logger.info(f"💾 Quality CSV saved to: {output_path}")
        return output_path

def main():
    """Main function to run RAG conversation tests"""
    # CLI args
    parser = argparse.ArgumentParser(description="RAG Conversation Tester")
    parser.add_argument("--num-exchanges", type=int, default=8, help="Number of user turns (default 8)")
    parser.add_argument("--quality-report", action="store_true", help="Collect and export quality bits per exchange")
    parser.add_argument("--save-quality-csv", action="store_true", help="Save a CSV of per-exchange quality bits")
    args, unknown = parser.parse_known_args()

    # Load API key from .env file or environment
    api_key = load_api_key()
    if not api_key:
        print("❌ OpenAI API key not found")
        print("Please ensure you have:")
        print("1. A .env file with OPENAI_API_KEY=\"your-key-here\"")
        print("2. Or set the OPENAI_API_KEY environment variable")
        return
    
    print("🧪 RAG Conversation Tester for Mega Architectural Mentor")
    print("=" * 60)
    
    # Test options
    print("\nSelect test mode:")
    print("1. Single persona test (intermediate student)")
    print("2. Multi-persona test (all personas)")
    print("3. Custom conversation test")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    tester = RAGConversationTester(api_key)
    
    if choice == "1":
        # Single persona test
        print("\n🎭 Running single persona test...")
        results = asyncio.run(tester.simulate_conversation(num_exchanges=args.num_exchanges, collect_quality=args.quality_report))
        
    elif choice == "2":
        # Multi-persona test
        print("\n🧪 Running multi-persona test...")
        results = tester.run_multiple_persona_tests(num_exchanges=args.num_exchanges)
        
    elif choice == "3":
        # Custom conversation
        print("\n💬 Custom conversation test")
        custom_questions = []
        print("Enter your questions (press Enter twice to finish):")
        
        while True:
            question = input("Question: ").strip()
            if not question:
                break
            custom_questions.append(question)
        
        if custom_questions:
            results = asyncio.run(tester.simulate_conversation(
                num_exchanges=min(args.num_exchanges, len(custom_questions)),
                custom_questions=custom_questions,
                collect_quality=args.quality_report,
            ))
        else:
            print("No questions provided. Exiting.")
            return
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Save results
    filename = tester.save_test_results(results)
    if args.quality_report and args.save_quality_csv:
        tester.save_quality_csv(results)
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total exchanges: {summary['total_exchanges']}")
        print(f"   Success rate: {summary['success_rate']:.1%}")
        print(f"   Average confidence: {summary['average_confidence']:.2f}")
        print(f"   Agents used: {', '.join(summary['unique_agents_used'])}")
        if args.quality_report and results.get("quality_summary"):
            qs = results["quality_summary"]
            print("   Quality:")
            print(f"     Ends with question: {qs.get('ends_with_question_count',0)}/{qs.get('total',0)} ({qs.get('ends_with_question_pct',0):.0%})")
            print(f"     Has bullets: {qs.get('has_bullets_count',0)}/{qs.get('total',0)} ({qs.get('has_bullets_pct',0):.0%})")
            print(f"     Has synthesis header: {qs.get('has_synthesis_header_count',0)}/{qs.get('total',0)} ({qs.get('has_synthesis_header_pct',0):.0%})")
            print(f"     Avg length (chars): {qs.get('avg_char_length',0):.0f}")
    
    elif "overall_summary" in results:
        summary = results["overall_summary"]
        print(f"\n📊 Overall Test Summary:")
        print(f"   Personas tested: {summary['total_personas_tested']}")
        print(f"   Total exchanges: {summary['total_exchanges']}")
        print(f"   Overall success rate: {summary['overall_success_rate']:.1%}")
        print(f"   Average confidence: {summary['average_confidence_across_personas']:.2f}")
    
    print(f"\n💾 Results saved to: {filename}")

if __name__ == "__main__":
    main() 