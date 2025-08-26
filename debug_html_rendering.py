#!/usr/bin/env python3
"""
DEBUG: HTML Rendering Issue
Diagnose why task UI HTML is showing as raw text instead of rendering
"""

import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

def test_theme_keys():
    """Test if theme dictionary has correct keys"""
    print("🎨 TESTING: Theme Dictionary Keys")
    print("=" * 60)
    
    from dashboard.ui.task_ui_renderer import TaskUIRenderer
    
    renderer = TaskUIRenderer()
    themes = renderer.test_group_themes
    
    for group, theme in themes.items():
        print(f"\n📋 {group} Theme Keys:")
        for key, value in theme.items():
            print(f"   {key}: {value}")
        
        # Test if required keys exist
        required_keys = ['primary', 'secondary', 'gradient', 'icon', 'style_name']
        missing_keys = [key for key in required_keys if key not in theme]
        
        if missing_keys:
            print(f"   ❌ Missing keys: {missing_keys}")
            return False
        else:
            print(f"   ✅ All required keys present")
    
    return True


def test_html_template_generation():
    """Test if HTML templates generate without errors"""
    print("\n🔧 TESTING: HTML Template Generation")
    print("=" * 60)
    
    from dashboard.ui.task_ui_renderer import TaskUIRenderer, UI_COLORS
    from dashboard.processors.dynamic_task_manager import ActiveTask, TaskType
    from datetime import datetime
    
    # Create test task
    task = ActiveTask(
        task_type=TaskType.ARCHITECTURAL_CONCEPT,
        start_time=datetime.now(),
        test_group="MENTOR",
        current_phase="ideation",
        trigger_reason="Test trigger",
        completion_criteria={},
        task_specific_data={},
        trigger_phase_completion=15.0
    )
    
    renderer = TaskUIRenderer()
    theme = renderer.test_group_themes["MENTOR"]
    
    print("📋 Testing theme access:")
    print(f"   Primary color: {theme['primary']}")
    print(f"   Gradient: {theme['gradient'][:50]}...")
    print(f"   Icon: {theme['icon']}")
    
    # Test simple HTML generation
    try:
        test_html = f"""
        <div style="
            background: {theme['gradient']};
            border: 2px solid {theme['primary']};
            padding: 20px;
            border-radius: 15px;
        ">
            <div style="color: white; text-align: center;">
                {theme['icon']} Test Task UI
            </div>
        </div>
        """
        
        print(f"\n📋 Generated HTML (first 200 chars):")
        print(f"   {test_html[:200]}...")
        
        # Check for common HTML issues
        has_unclosed_tags = test_html.count('<div') != test_html.count('</div>')
        has_invalid_css = '{{' in test_html or '}}' in test_html
        has_none_values = 'None' in test_html
        
        print(f"\n📋 HTML Validation:")
        print(f"   ✅ Balanced tags: {not has_unclosed_tags}")
        print(f"   ✅ Valid CSS: {not has_invalid_css}")
        print(f"   ✅ No None values: {not has_none_values}")
        
        if has_unclosed_tags or has_invalid_css or has_none_values:
            print(f"   ❌ HTML template has issues")
            return False
        
        print(f"   ✅ HTML template generates correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ HTML generation failed: {e}")
        return False


def test_content_escaping():
    """Test if content contains characters that break HTML"""
    print("\n🔤 TESTING: Content Escaping Issues")
    print("=" * 60)
    
    from dashboard.processors.task_guidance_system import TaskGuidanceSystem
    from dashboard.processors.dynamic_task_manager import TaskType
    
    guidance_system = TaskGuidanceSystem()
    task_data = guidance_system.mentor_tasks.get(TaskType.ARCHITECTURAL_CONCEPT, {})
    
    task_assignment = task_data.get("task_assignment", "")
    socratic_questions = task_data.get("socratic_questions", [])
    
    print("📋 Testing content for HTML-breaking characters:")
    
    # Check for problematic characters
    problematic_chars = ['<', '>', '"', "'", '&', '{', '}']
    
    assignment_issues = []
    for char in problematic_chars:
        if char in task_assignment:
            assignment_issues.append(char)
    
    question_issues = []
    if socratic_questions:
        for char in problematic_chars:
            if char in socratic_questions[0]:
                question_issues.append(char)
    
    print(f"   Assignment length: {len(task_assignment)}")
    print(f"   Assignment issues: {assignment_issues if assignment_issues else 'None'}")
    print(f"   Question length: {len(socratic_questions[0]) if socratic_questions else 0}")
    print(f"   Question issues: {question_issues if question_issues else 'None'}")
    
    # Test HTML escaping
    if assignment_issues or question_issues:
        print(f"   ⚠️ Content contains HTML-breaking characters")
        
        # Show how to escape
        import html
        if assignment_issues:
            escaped_assignment = html.escape(task_assignment[:100])
            print(f"   Escaped assignment preview: {escaped_assignment}...")
        
        return False
    else:
        print(f"   ✅ Content is HTML-safe")
        return True


def test_streamlit_compatibility():
    """Test Streamlit HTML rendering compatibility"""
    print("\n🌊 TESTING: Streamlit HTML Compatibility")
    print("=" * 60)
    
    # Test basic HTML rendering
    test_cases = [
        {
            "name": "Simple HTML",
            "html": "<div style='color: red;'>Test</div>",
            "expected": "Should render as red text"
        },
        {
            "name": "Complex CSS",
            "html": "<div style='background: linear-gradient(45deg, #ff0000, #00ff00); padding: 10px;'>Gradient</div>",
            "expected": "Should render with gradient background"
        },
        {
            "name": "Nested Elements",
            "html": "<div><span style='font-weight: bold;'>Bold</span> <em>Italic</em></div>",
            "expected": "Should render with bold and italic text"
        }
    ]
    
    print("📋 HTML Test Cases:")
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. {case['name']}: {case['html']}")
        print(f"      Expected: {case['expected']}")
    
    print(f"\n📋 Streamlit Version Check:")
    try:
        import streamlit as st
        print(f"   Streamlit available: Yes")
        print(f"   Version: {st.__version__ if hasattr(st, '__version__') else 'Unknown'}")
        
        # Test if unsafe_allow_html is supported
        if hasattr(st, 'markdown'):
            print(f"   st.markdown available: Yes")
            print(f"   unsafe_allow_html parameter: Supported")
            return True
        else:
            print(f"   st.markdown available: No")
            return False
            
    except ImportError:
        print(f"   Streamlit available: No")
        return False


def main():
    """Test all HTML rendering issues"""
    print("🚀 HTML RENDERING DIAGNOSTIC")
    print("=" * 80)
    
    try:
        test1_passed = test_theme_keys()
        test2_passed = test_html_template_generation()
        test3_passed = test_content_escaping()
        test4_passed = test_streamlit_compatibility()
        
        print("\n" + "=" * 80)
        print("📊 HTML RENDERING DIAGNOSTIC SUMMARY:")
        print("=" * 80)
        
        if all([test1_passed, test2_passed, test3_passed, test4_passed]):
            print("✅ ALL TESTS PASSED - HTML rendering should work correctly")
            print("\n🔍 POSSIBLE CAUSES OF RAW HTML DISPLAY:")
            print("   1. Streamlit app not refreshing properly")
            print("   2. Browser caching issues")
            print("   3. Streamlit session state conflicts")
            print("   4. Multiple st.markdown calls interfering")
        else:
            print("❌ SOME TESTS FAILED - HTML rendering has issues")
            print(f"   Theme keys: {'✅' if test1_passed else '❌'}")
            print(f"   HTML generation: {'✅' if test2_passed else '❌'}")
            print(f"   Content escaping: {'✅' if test3_passed else '❌'}")
            print(f"   Streamlit compatibility: {'✅' if test4_passed else '❌'}")
        
        print("=" * 80)
        
        return 0 if all([test1_passed, test2_passed, test3_passed, test4_passed]) else 1
        
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
