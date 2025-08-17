#!/usr/bin/env python3
"""
Test HTML cleaning logic for gamification display fix.
"""

def test_html_cleaning():
    """Test the HTML cleaning logic."""
    
    # Simulate the problematic content from your example
    test_content = """<!-- Main content -->
<div style="position: relative; z-index: 1;">
    <div style="font-size: 4em;">🎭</div>
    <h2 style="color: #cd766d;">🎯 DESIGN CHALLENGE</h2>
</div>

🎯 Challenge:
Designing a community center is a multifaceted task that requires careful consideration...

🎭 Role-Play Challenge"""

    print('🧪 TESTING HTML CLEANING LOGIC')
    print('=' * 60)
    print(f'Original content length: {len(test_content)}')
    print(f'Contains HTML: {"<div style=" in test_content}')
    print(f'Original preview: {test_content[:100]}...')
    
    # Apply the cleaning logic from chat_components.py
    clean_content = test_content
    
    if "<div style=" in clean_content or "<!-- Main content -->" in clean_content or "<h2 style=" in clean_content:
        print("🧹 Detected HTML in content, applying comprehensive cleaning...")

        # Use regex to remove all HTML tags and their content
        import re

        # Remove HTML comments
        clean_content = re.sub(r'<!--.*?-->', '', clean_content, flags=re.DOTALL)

        # Remove complete HTML tags with their attributes
        clean_content = re.sub(r'<[^>]+>', '', clean_content)

        # Remove lines that are just HTML attributes or empty
        lines = clean_content.split('\n')
        clean_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Skip lines that are just CSS properties or HTML attributes
            if (line.startswith('font-size:') or line.startswith('margin:') or
                line.startswith('color:') or line.startswith('background:') or
                line.startswith('border:') or line.startswith('padding:') or
                line.startswith('text-shadow:') or line.startswith('animation:') or
                'style=' in line or line.startswith('">') or line == '>'):
                continue
            # Keep meaningful content lines
            clean_lines.append(line)

        clean_content = '\n'.join(clean_lines)
        print(f"🧹 Applied comprehensive HTML cleaning - {len(clean_lines)} lines kept")
    
    print(f'\nCleaned content length: {len(clean_content)}')
    print(f'Cleaned content preview: {clean_content[:100]}...')
    print(f'Contains HTML after cleaning: {"<div style=" in clean_content}')
    
    # Check if cleaning worked
    html_removed = "<div style=" not in clean_content
    content_preserved = "🎯 Challenge:" in clean_content
    emoji_preserved = "🎭" in clean_content
    
    print(f'\n✅ Results:')
    print(f'   HTML removed: {html_removed}')
    print(f'   Content preserved: {content_preserved}')
    print(f'   Emojis preserved: {emoji_preserved}')
    
    if html_removed and content_preserved and emoji_preserved:
        print('\n🎉 SUCCESS: HTML cleaning logic works correctly!')
        print('The gamification display should now show clean content without HTML code.')
        return True
    else:
        print('\n❌ ISSUE: HTML cleaning logic needs adjustment')
        return False

if __name__ == "__main__":
    test_html_cleaning()
