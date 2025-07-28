#!/usr/bin/env python3
"""
Switch back to GPT-4o when you need high quality responses
"""

import os

def switch_models_in_file(file_path: str):
    """Switch models back to gpt-4o"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count changes
        gpt35_count = content.count('gpt-3.5-turbo')
        if gpt35_count == 0:
            return False, 0
        
        # Replace gpt-3.5-turbo back to gpt-4o
        updated_content = content.replace('gpt-3.5-turbo', 'gpt-4o')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, gpt35_count
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0

def main():
    print("SWITCHING TO HIGH QUALITY MODELS")
    print("=" * 40)
    print("gpt-3.5-turbo -> gpt-4o (higher quality)")
    print()
    
    # Files that contain model calls
    files_to_update = [
        "agents/domain_expert.py",
        "agents/context_agent.py", 
        "agents/socratic_tutor.py",
        "agents/analysis_agent.py",
        "agents/cognitive_enhancement.py",
        "orchestration/langgraph_orchestrator.py",
        "vision/sketch_analyzer.py"
    ]
    
    total_changes = 0
    updated_files = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            updated, count = switch_models_in_file(file_path)
            if updated:
                print(f"OK {file_path}: {count} changes")
                total_changes += count
                updated_files += 1
            else:
                print(f"-- {file_path}: no changes needed")
        else:
            print(f"XX {file_path}: file not found")
    
    print()
    print("SUMMARY:")
    print(f"Files updated: {updated_files}")
    print(f"Total model switches: {total_changes}")
    print()
    
    if total_changes > 0:
        print("QUALITY UPGRADE:")
        print("- GPT-3.5-turbo -> GPT-4o")
        print("- Better reasoning and responses")
        print("- Higher cost but better results")
        print("Ready for production/final testing")

if __name__ == "__main__":
    main()