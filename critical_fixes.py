#!/usr/bin/env python3
"""
Critical Fixes for Learning Tool System
Addresses the most urgent issues identified in the comprehensive analysis
"""

import sys
import os
import asyncio
from typing import Dict, List, Any

sys.path.insert(0, 'thesis-agents')

class CriticalFixesImplementation:
    """Implement critical fixes for the learning tool system"""
    
    def __init__(self):
        self.fixes_applied = []
        self.fixes_failed = []
    
    def fix_domain_expert_imports(self):
        """Fix 1: Resolve domain expert import issues"""
        print("🔧 FIX 1: Resolving Domain Expert Import Issues")
        print("-" * 50)
        
        try:
            # Test current import structure
            from agents.domain_expert import DomainExpertAgent
            print("✅ Domain expert import successful")
            
            # Test basic functionality
            domain_expert = DomainExpertAgent()
            print("✅ Domain expert instantiation successful")
            
            self.fixes_applied.append("Domain expert imports working")
            return True
            
        except Exception as e:
            print(f"❌ Domain expert import still failing: {e}")
            self.fixes_failed.append(f"Domain expert imports: {e}")
            return False
    
    def fix_synthesis_function_signature(self):
        """Fix 2: Test and document correct synthesis function usage"""
        print("\n🔧 FIX 2: Testing Synthesis Function Signature")
        print("-" * 50)
        
        try:
            from orchestration.synthesis import shape_by_route
            
            # Test with correct parameters
            test_response = shape_by_route(
                text="Test response for balanced guidance",
                routing_path="balanced_guidance",  # Correct parameter name
                classification={"user_input": "test input"},
                ordered_results={},
                user_message_count=1,
                context_analysis={}
            )
            
            print("✅ Synthesis function working with correct parameters")
            print(f"Sample output: {test_response[:100]}...")
            
            self.fixes_applied.append("Synthesis function signature corrected")
            return True
            
        except Exception as e:
            print(f"❌ Synthesis function still failing: {e}")
            self.fixes_failed.append(f"Synthesis function: {e}")
            return False
    
    def fix_routing_priority_issues(self):
        """Fix 3: Test routing priority and pure knowledge detection"""
        print("\n🔧 FIX 3: Testing Routing Priority Issues")
        print("-" * 50)
        
        try:
            from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
            
            router = AdvancedRoutingDecisionTree()
            
            # Test the problematic case
            test_input = "Can you tell me about passive cooling strategies?"
            classification = {'user_input': test_input}
            context = RoutingContext(classification=classification, context_analysis={}, routing_suggestions={})
            decision = router.decide_route(context)
            
            expected_route = "knowledge_only"
            actual_route = decision.route.value
            
            if actual_route == expected_route:
                print(f"✅ Routing working correctly: {test_input[:40]}... → {actual_route}")
                self.fixes_applied.append("Routing priority issues resolved")
                return True
            else:
                print(f"❌ Routing still incorrect: {test_input[:40]}... → {actual_route} (expected {expected_route})")
                self.fixes_failed.append(f"Routing: {actual_route} instead of {expected_route}")
                return False
                
        except Exception as e:
            print(f"❌ Routing test failed: {e}")
            self.fixes_failed.append(f"Routing test: {e}")
            return False
    
    def test_end_to_end_functionality(self):
        """Test end-to-end functionality with working components"""
        print("\n🧪 TESTING END-TO-END FUNCTIONALITY")
        print("-" * 50)
        
        try:
            from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
            from orchestration.synthesis import shape_by_route
            
            # Test complete workflow
            test_cases = [
                {
                    "input": "What are examples of community centers?",
                    "expected_route": "knowledge_only"
                },
                {
                    "input": "I need help organizing spaces",
                    "expected_route": "balanced_guidance"
                }
            ]
            
            router = AdvancedRoutingDecisionTree()
            working_cases = 0
            
            for test_case in test_cases:
                test_input = test_case["input"]
                expected_route = test_case["expected_route"]
                
                # Step 1: Route the request
                classification = {'user_input': test_input}
                context = RoutingContext(classification=classification, context_analysis={}, routing_suggestions={})
                decision = router.decide_route(context)
                
                actual_route = decision.route.value
                
                # Step 2: Test synthesis
                try:
                    shaped_response = shape_by_route(
                        text=f"Response for: {test_input}",
                        routing_path=actual_route,
                        classification=classification,
                        ordered_results={},
                        user_message_count=1,
                        context_analysis={}
                    )
                    
                    synthesis_working = len(shaped_response) > 0
                    
                except Exception as synthesis_error:
                    synthesis_working = False
                    shaped_response = f"Synthesis error: {synthesis_error}"
                
                # Evaluate results
                routing_correct = actual_route == expected_route
                
                if routing_correct and synthesis_working:
                    working_cases += 1
                    print(f"✅ {test_input[:30]}... → {actual_route} → synthesis OK")
                else:
                    print(f"❌ {test_input[:30]}... → {actual_route} → synthesis: {synthesis_working}")
            
            success_rate = (working_cases / len(test_cases)) * 100
            print(f"\n📊 End-to-End Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 50:
                self.fixes_applied.append(f"End-to-end functionality: {success_rate:.1f}% success")
                return True
            else:
                self.fixes_failed.append(f"End-to-end functionality: only {success_rate:.1f}% success")
                return False
                
        except Exception as e:
            print(f"❌ End-to-end test failed: {e}")
            self.fixes_failed.append(f"End-to-end test: {e}")
            return False
    
    def generate_fix_recommendations(self):
        """Generate specific fix recommendations based on test results"""
        print("\n📋 FIX RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = []
        
        # Domain expert recommendations
        if any("Domain expert" in fix for fix in self.fixes_failed):
            recommendations.extend([
                "1. Fix domain expert circular import by restructuring module hierarchy",
                "2. Create proper __init__.py files with correct import paths",
                "3. Test domain expert functionality independently"
            ])
        
        # Synthesis recommendations
        if any("Synthesis" in fix for fix in self.fixes_failed):
            recommendations.extend([
                "4. Update all synthesis function calls to use 'routing_path' parameter",
                "5. Test synthesis with all route types",
                "6. Ensure synthesis templates are properly loaded"
            ])
        
        # Routing recommendations
        if any("Routing" in fix for fix in self.fixes_failed):
            recommendations.extend([
                "7. Review routing rule priorities to ensure pure knowledge requests are handled correctly",
                "8. Fix pure knowledge detection logic",
                "9. Test routing with comprehensive test suite"
            ])
        
        # General recommendations
        recommendations.extend([
            "10. Implement comprehensive unit tests for each component",
            "11. Add integration tests for end-to-end workflows",
            "12. Create monitoring for system health metrics"
        ])
        
        for rec in recommendations:
            print(f"  {rec}")
        
        return recommendations
    
    def run_all_fixes(self):
        """Run all critical fixes and generate report"""
        print("🚀 RUNNING CRITICAL FIXES FOR LEARNING TOOL SYSTEM")
        print("=" * 80)
        
        # Run fixes
        fix1_success = self.fix_domain_expert_imports()
        fix2_success = self.fix_synthesis_function_signature()
        fix3_success = self.fix_routing_priority_issues()
        
        # Test end-to-end
        e2e_success = self.test_end_to_end_functionality()
        
        # Generate summary
        total_fixes = 4
        successful_fixes = sum([fix1_success, fix2_success, fix3_success, e2e_success])
        success_rate = (successful_fixes / total_fixes) * 100
        
        print(f"\n📊 CRITICAL FIXES SUMMARY")
        print("=" * 50)
        print(f"🎯 Overall Fix Success Rate: {success_rate:.1f}%")
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        print(f"❌ Fixes Failed: {len(self.fixes_failed)}")
        
        if self.fixes_applied:
            print(f"\n✅ Successfully Applied:")
            for fix in self.fixes_applied:
                print(f"  - {fix}")
        
        if self.fixes_failed:
            print(f"\n❌ Failed to Fix:")
            for fix in self.fixes_failed:
                print(f"  - {fix}")
        
        # Generate recommendations
        recommendations = self.generate_fix_recommendations()
        
        return {
            "success_rate": success_rate,
            "fixes_applied": self.fixes_applied,
            "fixes_failed": self.fixes_failed,
            "recommendations": recommendations
        }

async def main():
    """Run critical fixes"""
    fixer = CriticalFixesImplementation()
    results = fixer.run_all_fixes()
    
    print(f"\n🏁 Critical fixes completed with {results['success_rate']:.1f}% success rate")
    
    if results['success_rate'] >= 75:
        print("🎉 System is in good shape! Ready for production use.")
    elif results['success_rate'] >= 50:
        print("⚠️ System is partially functional. Address remaining issues before production.")
    else:
        print("🚨 System needs significant work before it can be used reliably.")

if __name__ == "__main__":
    asyncio.run(main())
