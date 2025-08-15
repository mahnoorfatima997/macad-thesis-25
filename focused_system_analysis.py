#!/usr/bin/env python3
"""
Focused System Analysis - Core Functionality Testing
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, 'thesis-agents')

class FocusedSystemAnalysis:
    """Focused analysis of core system functionality"""
    
    def __init__(self):
        self.results = {
            "routing_analysis": {},
            "classification_analysis": {},
            "domain_expert_analysis": {},
            "synthesis_analysis": {},
            "overall_assessment": {}
        }
    
    async def analyze_routing_classification(self):
        """Analyze routing and classification accuracy"""
        print("🧭 ROUTING & CLASSIFICATION ANALYSIS")
        print("=" * 80)
        
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        from agents.context_agent.processors.input_classification import InputClassificationProcessor
        from state_manager import ArchMentorState
        
        router = AdvancedRoutingDecisionTree()
        classifier = InputClassificationProcessor()
        state = ArchMentorState()
        
        # Core test cases
        test_cases = [
            {
                "input": "What are some examples of community centers in hot climates?",
                "expected_route": "knowledge_only",
                "expected_classification": "example_request",
                "category": "Example Request"
            },
            {
                "input": "Can you tell me about passive cooling strategies?",
                "expected_route": "knowledge_only", 
                "expected_classification": "knowledge_seeking",
                "category": "Knowledge Request"
            },
            {
                "input": "I need help organizing spaces for different age groups",
                "expected_route": "balanced_guidance",
                "expected_classification": "design_guidance",
                "category": "Design Guidance"
            },
            {
                "input": "I don't understand spatial hierarchy",
                "expected_route": "socratic_clarification",
                "expected_classification": "confusion_expression", 
                "category": "Confusion"
            },
            {
                "input": "How should I handle circulation patterns?",
                "expected_route": "knowledge_only",
                "expected_classification": "knowledge_seeking",
                "category": "Knowledge Request"
            }
        ]
        
        routing_results = []
        classification_results = []
        
        for test_case in test_cases:
            test_input = test_case["input"]
            
            try:
                # Test AI classification
                ai_classification = await classifier.perform_core_classification(test_input, state)
                
                # Extract classification data properly
                classification_data = {
                    'interaction_type': ai_classification.interaction_type.value if hasattr(ai_classification.interaction_type, 'value') else str(ai_classification.interaction_type),
                    'confidence_level': ai_classification.confidence_level.value if hasattr(ai_classification.confidence_level, 'value') else str(ai_classification.confidence_level),
                    'understanding_level': ai_classification.understanding_level.value if hasattr(ai_classification.understanding_level, 'value') else str(ai_classification.understanding_level),
                    'engagement_level': ai_classification.engagement_level.value if hasattr(ai_classification.engagement_level, 'value') else str(ai_classification.engagement_level),
                    'user_input': test_input
                }
                
                # Test routing
                context = RoutingContext(
                    classification=classification_data,
                    context_analysis={},
                    routing_suggestions={}
                )
                decision = router.decide_route(context)
                
                # Analyze results
                routing_correct = decision.route.value == test_case["expected_route"]
                classification_correct = classification_data['interaction_type'] == test_case["expected_classification"]
                
                routing_results.append({
                    "input": test_input,
                    "category": test_case["category"],
                    "expected_route": test_case["expected_route"],
                    "actual_route": decision.route.value,
                    "correct": routing_correct,
                    "rule_applied": decision.rule_applied
                })
                
                classification_results.append({
                    "input": test_input,
                    "category": test_case["category"], 
                    "expected_classification": test_case["expected_classification"],
                    "actual_classification": classification_data['interaction_type'],
                    "correct": classification_correct,
                    "confidence": classification_data['confidence_level']
                })
                
                status_route = "✅" if routing_correct else "❌"
                status_class = "✅" if classification_correct else "❌"
                
                print(f"\n📝 {test_input[:50]}...")
                print(f"  {status_route} Route: {test_case['expected_route']} → {decision.route.value}")
                print(f"  {status_class} Class: {test_case['expected_classification']} → {classification_data['interaction_type']}")
                print(f"  Rule: {decision.rule_applied}")
                
            except Exception as e:
                print(f"❌ Error testing '{test_input[:30]}...': {e}")
        
        # Calculate accuracies
        routing_accuracy = sum(1 for r in routing_results if r["correct"]) / len(routing_results) * 100
        classification_accuracy = sum(1 for r in classification_results if r["correct"]) / len(classification_results) * 100
        
        print(f"\n📊 RESULTS:")
        print(f"  Routing Accuracy: {routing_accuracy:.1f}%")
        print(f"  Classification Accuracy: {classification_accuracy:.1f}%")
        
        self.results["routing_analysis"] = {
            "accuracy": routing_accuracy,
            "test_results": routing_results
        }
        self.results["classification_analysis"] = {
            "accuracy": classification_accuracy,
            "test_results": classification_results
        }
        
        return routing_accuracy, classification_accuracy
    
    async def analyze_domain_expert_functionality(self):
        """Analyze domain expert database and knowledge retrieval"""
        print("\n🗄️ DOMAIN EXPERT FUNCTIONALITY ANALYSIS")
        print("=" * 80)
        
        try:
            from agents.domain_expert.domain_expert import DomainExpertAgent
            
            domain_expert = DomainExpertAgent()
            
            # Test knowledge retrieval
            knowledge_tests = [
                {
                    "query": "passive cooling strategies",
                    "type": "technical_knowledge",
                    "expected": "Should return technical information about cooling"
                },
                {
                    "query": "community center examples",
                    "type": "example_projects", 
                    "expected": "Should return specific project examples"
                },
                {
                    "query": "design principles",
                    "type": "general_knowledge",
                    "expected": "Should return design principles"
                }
            ]
            
            domain_results = []
            
            for test in knowledge_tests:
                print(f"\n🔍 Testing: {test['query']}")
                
                try:
                    # Test knowledge retrieval
                    result = await domain_expert.get_knowledge(test["query"])
                    
                    analysis = {
                        "query": test["query"],
                        "type": test["type"],
                        "has_content": bool(result.get("content")),
                        "content_length": len(result.get("content", "")),
                        "source": result.get("source", "unknown"),
                        "has_references": "references" in result,
                        "quality_score": self._assess_content_quality(result.get("content", ""))
                    }
                    
                    domain_results.append(analysis)
                    
                    print(f"  Content Length: {analysis['content_length']}")
                    print(f"  Source: {analysis['source']}")
                    print(f"  Quality Score: {analysis['quality_score']:.1f}/10")
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    domain_results.append({
                        "query": test["query"],
                        "error": str(e)
                    })
            
            # Calculate domain expert performance
            successful_queries = sum(1 for r in domain_results if "error" not in r and r.get("has_content", False))
            domain_success_rate = (successful_queries / len(domain_results) * 100) if domain_results else 0
            
            print(f"\n📊 Domain Expert Success Rate: {domain_success_rate:.1f}%")
            
            self.results["domain_expert_analysis"] = {
                "success_rate": domain_success_rate,
                "test_results": domain_results
            }
            
            return domain_success_rate
            
        except ImportError as e:
            print(f"❌ Could not import domain expert: {e}")
            return 0
    
    def _assess_content_quality(self, content: str) -> float:
        """Simple content quality assessment"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Length check (reasonable length)
        if 50 <= len(content) <= 2000:
            score += 3.0
        elif len(content) > 0:
            score += 1.0
        
        # Structure check (has sentences)
        if "." in content:
            score += 2.0
        
        # Technical terms check
        technical_terms = ["design", "architecture", "space", "building", "material", "structure"]
        if any(term in content.lower() for term in technical_terms):
            score += 3.0
        
        # Coherence check (not just keywords)
        if len(content.split()) > 10:
            score += 2.0
        
        return min(score, 10.0)
    
    async def analyze_synthesis_functionality(self):
        """Analyze synthesis and response formatting"""
        print("\n🎭 SYNTHESIS FUNCTIONALITY ANALYSIS")
        print("=" * 80)
        
        try:
            from orchestration.synthesis import shape_by_route
            
            # Test synthesis for different routes
            synthesis_tests = [
                {
                    "route": "balanced_guidance",
                    "text": "Here's guidance about organizing spaces for different age groups.",
                    "expected_format": "Should have Synthesis: header with Insight/Watch/Direction"
                },
                {
                    "route": "knowledge_only", 
                    "text": "Passive cooling strategies include natural ventilation and thermal mass.",
                    "expected_format": "Should be direct information without synthesis structure"
                },
                {
                    "route": "socratic_clarification",
                    "text": "Let me help clarify spatial hierarchy concepts.",
                    "expected_format": "Should be conversational and questioning"
                }
            ]
            
            synthesis_results = []
            
            for test in synthesis_tests:
                print(f"\n🧪 Testing synthesis for: {test['route']}")
                
                try:
                    shaped_response = shape_by_route(
                        text=test["text"],
                        path=test["route"],
                        classification={"user_input": "test input"},
                        context_analysis={},
                        ordered_results={}
                    )
                    
                    analysis = {
                        "route": test["route"],
                        "has_synthesis_header": "Synthesis:" in shaped_response,
                        "has_insight": "- Insight:" in shaped_response,
                        "has_watch": "- Watch:" in shaped_response,
                        "has_direction": "- Direction:" in shaped_response,
                        "response_length": len(shaped_response),
                        "format_correct": self._check_format_correctness(test["route"], shaped_response)
                    }
                    
                    synthesis_results.append(analysis)
                    
                    print(f"  Has Synthesis Structure: {analysis['has_synthesis_header']}")
                    print(f"  Format Correct: {analysis['format_correct']}")
                    print(f"  Response Length: {analysis['response_length']}")
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    synthesis_results.append({
                        "route": test["route"],
                        "error": str(e)
                    })
            
            # Calculate synthesis success rate
            successful_synthesis = sum(1 for r in synthesis_results if "error" not in r and r.get("format_correct", False))
            synthesis_success_rate = (successful_synthesis / len(synthesis_results) * 100) if synthesis_results else 0
            
            print(f"\n📊 Synthesis Success Rate: {synthesis_success_rate:.1f}%")
            
            self.results["synthesis_analysis"] = {
                "success_rate": synthesis_success_rate,
                "test_results": synthesis_results
            }
            
            return synthesis_success_rate
            
        except ImportError as e:
            print(f"❌ Could not import synthesis module: {e}")
            return 0
    
    def _check_format_correctness(self, route: str, response: str) -> bool:
        """Check if response format matches route expectations"""
        if route == "balanced_guidance":
            return "Synthesis:" in response and "- Insight:" in response
        elif route == "knowledge_only":
            return "Synthesis:" not in response  # Should be direct
        elif route == "socratic_clarification":
            return len(response) > 0  # Should have content
        return True
    
    def generate_focused_report(self):
        """Generate focused analysis report"""
        print("\n📊 FOCUSED SYSTEM ANALYSIS REPORT")
        print("=" * 80)
        
        # Calculate overall system health
        routing_score = self.results["routing_analysis"].get("accuracy", 0)
        classification_score = self.results["classification_analysis"].get("accuracy", 0)
        domain_expert_score = self.results["domain_expert_analysis"].get("success_rate", 0)
        synthesis_score = self.results["synthesis_analysis"].get("success_rate", 0)
        
        overall_score = (routing_score + classification_score + domain_expert_score + synthesis_score) / 4
        
        print(f"🎯 Overall System Health: {overall_score:.1f}%")
        print(f"  - Routing Accuracy: {routing_score:.1f}%")
        print(f"  - Classification Accuracy: {classification_score:.1f}%")
        print(f"  - Domain Expert Success: {domain_expert_score:.1f}%")
        print(f"  - Synthesis Success: {synthesis_score:.1f}%")
        
        # Generate recommendations
        recommendations = []
        if routing_score < 90:
            recommendations.append("Improve routing decision logic")
        if classification_score < 90:
            recommendations.append("Enhance AI classification accuracy")
        if domain_expert_score < 80:
            recommendations.append("Improve domain expert knowledge retrieval")
        if synthesis_score < 90:
            recommendations.append("Fix synthesis formatting issues")
        
        if not recommendations:
            recommendations.append("System is performing well - consider advanced optimizations")
        
        print(f"\n📝 Key Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"focused_system_analysis_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: {report_filename}")
        
        return overall_score

async def main():
    """Run focused system analysis"""
    analyzer = FocusedSystemAnalysis()
    
    print("🔍 FOCUSED LEARNING TOOL SYSTEM ANALYSIS")
    print("=" * 120)
    
    # Run core analyses
    await analyzer.analyze_routing_classification()
    await analyzer.analyze_domain_expert_functionality()
    await analyzer.analyze_synthesis_functionality()
    
    # Generate report
    overall_score = analyzer.generate_focused_report()
    
    print(f"\n✅ Analysis Complete! Overall Score: {overall_score:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
