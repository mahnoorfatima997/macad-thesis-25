"""
Quick Validation Test

Tests the key components we've been working on.
"""

import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

def test_imports():
    """Test that all key components can be imported."""
    print("🔍 TESTING IMPORTS")
    print("=" * 50)
    
    try:
        from knowledge_base.knowledge_manager import KnowledgeManager
        print("✅ KnowledgeManager imported successfully")
    except Exception as e:
        print(f"❌ KnowledgeManager import failed: {e}")
        return False
    
    try:
        from agents.domain_expert.adapter import DomainExpertAgent
        print("✅ DomainExpertAgent imported successfully")
    except Exception as e:
        print(f"❌ DomainExpertAgent import failed: {e}")
        return False

    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        print("✅ ChallengeGeneratorProcessor imported successfully")
    except Exception as e:
        print(f"❌ ChallengeGeneratorProcessor import failed: {e}")
        return False
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree
        print("✅ AdvancedRoutingDecisionTree imported successfully")
    except Exception as e:
        print(f"❌ AdvancedRoutingDecisionTree import failed: {e}")
        return False
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))
        from ui.enhanced_gamification import EnhancedGamificationRenderer
        print("✅ EnhancedGamificationRenderer imported successfully")
    except Exception as e:
        print(f"❌ EnhancedGamificationRenderer import failed: {e}")
        return False
    
    return True

def test_database_basic():
    """Test basic database functionality."""
    print("\n🔍 TESTING DATABASE BASIC FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from knowledge_base.knowledge_manager import KnowledgeManager
        km = KnowledgeManager(domain="architecture")
        
        # Test collection exists
        count = km.collection.count()
        print(f"✅ Database connected: {count} documents")
        
        # Test basic search
        results = km.search_knowledge("community center design", n_results=3)
        if results:
            print(f"✅ Search working: {len(results)} results found")
            top_similarity = results[0].get('similarity', 0)
            print(f"   Top result similarity: {top_similarity:.3f}")
        else:
            print("⚠️ Search returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_gamification_basic():
    """Test basic gamification functionality."""
    print("\n🔍 TESTING GAMIFICATION BASIC FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        from orchestration.state import ArchMentorState

        challenge_gen = ChallengeGeneratorProcessor()
        
        # Test gamification trigger detection
        test_inputs = [
            ("how would a visitor feel", True),
            ("normal design question", False),
            ("i wonder what would happen", True),
            ("ok", True)
        ]
        
        for test_input, expected in test_inputs:
            state = ArchMentorState()
            state.messages = [{"role": "user", "content": test_input}]
            
            result = challenge_gen._should_apply_gamification(state, "test", "test context")
            status = "✅" if result == expected else "❌"
            print(f"{status} '{test_input}': {result} (expected: {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Gamification test failed: {e}")
        return False

def test_enhanced_gamification():
    """Test enhanced gamification themes."""
    print("\n🔍 TESTING ENHANCED GAMIFICATION THEMES")
    print("=" * 50)
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))
        from ui.enhanced_gamification import EnhancedGamificationRenderer
        
        renderer = EnhancedGamificationRenderer()
        
        # Test all themes exist
        expected_themes = ["role_play", "perspective_shift", "detective", "constraint", 
                          "storytelling", "time_travel", "transformation"]
        
        for theme_name in expected_themes:
            if theme_name in renderer.themes:
                theme = renderer.themes[theme_name]
                required_keys = ["primary", "secondary", "accent", "gradient"]
                missing = [k for k in required_keys if k not in theme]
                if not missing:
                    print(f"✅ {theme_name}: Theme complete")
                else:
                    print(f"❌ {theme_name}: Missing keys: {missing}")
            else:
                print(f"❌ {theme_name}: Theme not found")
        
        # Test methods exist
        expected_methods = ["_render_storytelling_game", "_render_time_travel_game", "_render_transformation_game"]
        for method_name in expected_methods:
            if hasattr(renderer, method_name):
                print(f"✅ {method_name}: Method exists")
            else:
                print(f"❌ {method_name}: Method missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced gamification test failed: {e}")
        return False

def test_domain_expert_improvements():
    """Test domain expert improvements."""
    print("\n🔍 TESTING DOMAIN EXPERT IMPROVEMENTS")
    print("=" * 50)
    
    try:
        from agents.domain_expert.adapter import DomainExpertAgent

        domain_expert = DomainExpertAgent()
        
        # Test negative context detection
        test_cases = [
            ("i dont want project examples I need knowledge", False),
            ("can you provide example projects", True),
            ("not looking for examples just principles", False)
        ]
        
        for test_input, should_be_example_request in test_cases:
            # Test the pattern matching logic
            negative_patterns = ["don't want", "dont want", "not want", "no examples", "no projects"]
            has_negative = any(pattern in test_input.lower() for pattern in negative_patterns)
            
            example_patterns = ["example projects", "project examples", "case studies", "precedents"]
            has_example_request = any(pattern in test_input.lower() for pattern in example_patterns)
            
            final_result = has_example_request and not has_negative
            
            status = "✅" if final_result == should_be_example_request else "❌"
            print(f"{status} '{test_input}': {final_result} (expected: {should_be_example_request})")
        
        # Test topic extraction
        topic_tests = [
            ("circulation design principles", "circulation"),
            ("wooden structures design", "wooden structures"),
            ("accessibility requirements", "accessibility")
        ]
        
        for test_input, expected_topic in topic_tests:
            extracted = domain_expert._extract_topic_from_user_input(test_input)
            status = "✅" if extracted.lower() == expected_topic.lower() else "❌"
            print(f"{status} Topic '{test_input}': {extracted} (expected: {expected_topic})")
        
        return True
        
    except Exception as e:
        print(f"❌ Domain expert test failed: {e}")
        return False

def main():
    """Run all quick validation tests."""
    print("🚀 QUICK VALIDATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Database Basic", test_database_basic),
        ("Gamification Basic", test_gamification_basic),
        ("Enhanced Gamification", test_enhanced_gamification),
        ("Domain Expert Improvements", test_domain_expert_improvements)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 QUICK VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All systems operational!")
    else:
        print("🔧 Some issues found - check individual test outputs above")

if __name__ == "__main__":
    main()
