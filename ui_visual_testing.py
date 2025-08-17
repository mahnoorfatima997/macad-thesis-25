#!/usr/bin/env python3
"""
UI Visual Testing and Gamification Display Analysis
"""

import sys
import os
import asyncio
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')
sys.path.insert(0, 'dashboard')

class UIVisualTester:
    """Test UI components and visual presentation"""
    
    def __init__(self):
        self.ui_test_results = []
        self.gamification_visual_tests = []
    
    async def test_response_formatting(self):
        """Test how different response types are formatted in the UI"""
        print("🎨 UI RESPONSE FORMATTING TESTS")
        print("=" * 80)
        
        # Test different response formats
        test_responses = [
            {
                "type": "knowledge_only",
                "content": "Passive cooling strategies include natural ventilation, thermal mass, and shading. These techniques reduce energy consumption by using environmental conditions.",
                "metadata": {"response_type": "knowledge_only", "agents_used": ["domain_expert"]}
            },
            {
                "type": "balanced_guidance",
                "content": """Synthesis:

- Insight: Organizing spaces by age groups requires understanding different spatial needs and activity patterns.

- Watch: Avoid creating rigid separations that prevent intergenerational interaction and community building.

- Direction: Consider flexible boundaries using moveable partitions, varied ceiling heights, and activity-specific zones that can overlap during community events.""",
                "metadata": {"response_type": "balanced_guidance", "agents_used": ["domain_expert", "socratic_tutor"]}
            },
            {
                "type": "socratic_clarification",
                "content": "Let me help clarify spatial hierarchy. Think about how you move through a building - what spaces feel most important? What draws your attention first? Spatial hierarchy is about creating a clear order of importance through design elements like size, height, lighting, and materials.",
                "metadata": {"response_type": "socratic_clarification", "agents_used": ["socratic_tutor"]}
            },
            {
                "type": "gamified_response",
                "content": "Great question about materials! Here's what to consider...",
                "metadata": {
                    "response_type": "knowledge_only",
                    "gamification": {
                        "type": "encouragement_boost",
                        "message": "🌟 Excellent question! You're thinking like a true architect by considering material choices early in the design process.",
                        "visual_effect": "highlight_border",
                        "points_awarded": 10
                    }
                }
            }
        ]
        
        for test_response in test_responses:
            print(f"\n🧪 Testing {test_response['type']} formatting:")
            
            # Analyze response structure
            content = test_response["content"]
            metadata = test_response["metadata"]
            
            analysis = {
                "has_synthesis_structure": "Synthesis:" in content,
                "has_bullet_points": "- " in content,
                "has_sections": content.count("\n\n") > 0,
                "word_count": len(content.split()),
                "has_gamification": "gamification" in metadata,
                "response_length": "short" if len(content) < 200 else "medium" if len(content) < 500 else "long"
            }
            
            print(f"  Structure Analysis: {analysis}")
            
            # Test gamification display
            if "gamification" in metadata:
                self._test_gamification_display(metadata["gamification"])
            
            self.ui_test_results.append({
                "response_type": test_response["type"],
                "analysis": analysis,
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            })
    
    def _test_gamification_display(self, gamification_data: Dict):
        """Test gamification visual elements"""
        print(f"    🎮 Gamification Display:")
        print(f"      Type: {gamification_data.get('type', 'none')}")
        print(f"      Message: {gamification_data.get('message', 'none')}")
        print(f"      Visual Effect: {gamification_data.get('visual_effect', 'none')}")
        print(f"      Points: {gamification_data.get('points_awarded', 0)}")
        
        # Simulate UI rendering
        visual_elements = self._simulate_gamification_rendering(gamification_data)
        print(f"      Rendered Elements: {visual_elements}")
        
        self.gamification_visual_tests.append({
            "gamification_type": gamification_data.get('type'),
            "visual_elements": visual_elements,
            "user_visible": bool(gamification_data.get('message'))
        })
    
    def _simulate_gamification_rendering(self, gamification_data: Dict) -> Dict:
        """Simulate how gamification would be rendered in UI"""
        elements = {
            "message_display": bool(gamification_data.get('message')),
            "visual_effect": gamification_data.get('visual_effect', 'none'),
            "points_display": gamification_data.get('points_awarded', 0) > 0,
            "emoji_used": '🌟' in gamification_data.get('message', '') or '🎯' in gamification_data.get('message', ''),
            "color_coding": self._determine_color_coding(gamification_data.get('type', 'none'))
        }
        return elements
    
    def _determine_color_coding(self, gamification_type: str) -> str:
        """Determine color coding for different gamification types"""
        color_map = {
            "encouragement_boost": "green",
            "overconfidence_challenge": "orange", 
            "cognitive_offloading_prevention": "red",
            "exploration_prompt": "blue",
            "achievement_unlock": "gold"
        }
        return color_map.get(gamification_type, "default")
    
    async def test_conversation_flow_ui(self):
        """Test how conversation flows are displayed in UI"""
        print("\n💬 CONVERSATION FLOW UI TESTS")
        print("=" * 80)
        
        # Simulate conversation flow
        conversation_flow = [
            {
                "role": "user",
                "content": "What are some examples of community centers?",
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "role": "assistant", 
                "content": "Here are some notable community center examples:\n\n1. Gando School Library (Burkina Faso) - Uses local materials and passive cooling\n2. Medellín Library Parks (Colombia) - Integrated community spaces\n3. Tham & Videgård's Kalmar Museum (Sweden) - Flexible programming spaces",
                "metadata": {"response_type": "knowledge_only", "agents_used": ["domain_expert"]},
                "timestamp": "2025-01-01T10:00:05"
            },
            {
                "role": "user",
                "content": "How should I apply these principles to my hot climate project?",
                "timestamp": "2025-01-01T10:01:00"
            },
            {
                "role": "assistant",
                "content": """Synthesis:

- Insight: Hot climate community centers require careful attention to passive cooling, material selection, and outdoor-indoor transitions.

- Watch: Don't simply copy solutions - adapt principles to your specific climate, culture, and community needs.

- Direction: Start by analyzing your site's wind patterns, sun angles, and local materials. Consider how the Gando Library's double roof and natural ventilation could inform your approach.""",
                "metadata": {
                    "response_type": "balanced_guidance", 
                    "agents_used": ["domain_expert", "socratic_tutor"],
                    "gamification": {
                        "type": "exploration_prompt",
                        "message": "🎯 Great connection! You're learning to apply precedents thoughtfully rather than copying directly.",
                        "points_awarded": 15
                    }
                },
                "timestamp": "2025-01-01T10:01:10"
            }
        ]
        
        print("Conversation Flow Analysis:")
        for i, message in enumerate(conversation_flow):
            role_icon = "👤" if message["role"] == "user" else "🤖"
            print(f"\n{i+1}. {role_icon} {message['role'].title()}: {message['content'][:50]}...")
            
            if message["role"] == "assistant":
                metadata = message.get("metadata", {})
                print(f"   Response Type: {metadata.get('response_type', 'unknown')}")
                print(f"   Agents: {metadata.get('agents_used', [])}")
                
                if "gamification" in metadata:
                    gam = metadata["gamification"]
                    print(f"   🎮 Gamification: {gam.get('type')} (+{gam.get('points_awarded', 0)} pts)")
        
        # Analyze conversation patterns
        user_messages = [m for m in conversation_flow if m["role"] == "user"]
        assistant_messages = [m for m in conversation_flow if m["role"] == "assistant"]
        
        conversation_analysis = {
            "total_exchanges": len(user_messages),
            "response_types_used": list(set(m.get("metadata", {}).get("response_type") for m in assistant_messages if m.get("metadata"))),
            "gamification_instances": sum(1 for m in assistant_messages if m.get("metadata", {}).get("gamification")),
            "conversation_progression": "knowledge_seeking → design_application",
            "ui_complexity": "medium"  # Based on mixed response types and gamification
        }
        
        print(f"\nConversation Analysis: {conversation_analysis}")
        return conversation_analysis
    
    async def test_mobile_responsiveness(self):
        """Test mobile UI considerations"""
        print("\n📱 MOBILE RESPONSIVENESS TESTS")
        print("=" * 80)
        
        # Test different screen sizes
        screen_sizes = [
            {"name": "Mobile", "width": 375, "height": 667},
            {"name": "Tablet", "width": 768, "height": 1024}, 
            {"name": "Desktop", "width": 1920, "height": 1080}
        ]
        
        for screen in screen_sizes:
            print(f"\n📱 Testing {screen['name']} ({screen['width']}x{screen['height']}):")
            
            # Simulate responsive design considerations
            mobile_considerations = {
                "text_readability": screen["width"] > 320,
                "gamification_visibility": screen["width"] > 375,
                "synthesis_format_readable": screen["width"] > 480,
                "conversation_history_scrollable": True,
                "input_area_accessible": screen["height"] > 500
            }
            
            print(f"  Responsive Design Check: {mobile_considerations}")
            
            # Check for potential UI issues
            issues = []
            if not mobile_considerations["gamification_visibility"]:
                issues.append("Gamification elements may be too small")
            if not mobile_considerations["synthesis_format_readable"]:
                issues.append("Synthesis format may need mobile optimization")
            
            if issues:
                print(f"  ⚠️  Potential Issues: {issues}")
            else:
                print(f"  ✅ No major responsive issues detected")
    
    def generate_ui_report(self) -> Dict:
        """Generate UI testing report"""
        report = {
            "ui_formatting_tests": self.ui_test_results,
            "gamification_visual_tests": self.gamification_visual_tests,
            "ui_recommendations": [
                "Ensure gamification messages are prominently displayed",
                "Use consistent color coding for different response types",
                "Optimize synthesis format for mobile devices",
                "Add visual indicators for conversation flow progression",
                "Consider accessibility features for gamification elements"
            ]
        }
        
        print(f"\n📊 UI Testing Summary:")
        print(f"  Response Types Tested: {len(self.ui_test_results)}")
        print(f"  Gamification Displays Tested: {len(self.gamification_visual_tests)}")
        print(f"  UI Recommendations Generated: {len(report['ui_recommendations'])}")
        
        return report

async def main():
    """Run UI visual testing"""
    tester = UIVisualTester()
    
    print("🎨 UI VISUAL TESTING FRAMEWORK")
    print("=" * 80)
    
    await tester.test_response_formatting()
    await tester.test_conversation_flow_ui()
    await tester.test_mobile_responsiveness()
    
    report = tester.generate_ui_report()
    
    # Save UI report
    with open("ui_visual_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ UI Visual Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())
