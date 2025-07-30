#!/usr/bin/env python3
"""
Quick script to switch all models from gpt-4o to cheaper alternatives
"""

import os
import re

def switch_models_in_file(file_path: str):
    """Switch models in a single file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count changes
        gpt4o_count = content.count('gpt-4o')
        if gpt4o_count == 0:
            return False, 0
        
        # Replace gpt-4o with gpt-3.5-turbo (15x cheaper)
        updated_content = content.replace('gpt-4o', 'gpt-3.5-turbo')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, gpt4o_count
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0

def main():
    print("SWITCHING TO CHEAP MODELS")
    print("=" * 40)
    print("gpt-4o -> gpt-3.5-turbo (15x cheaper)")
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
        print("COST SAVINGS:")
        print("- GPT-4o: $0.03/1K input tokens")
        print("- GPT-3.5-turbo: $0.002/1K input tokens")
        print("- SAVINGS: ~93% cost reduction!")
        print()
        print("NOTE: Slightly lower quality responses")
        print("Perfect for development and testing")
    
    return total_changes > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\nModel switch complete! Run your Streamlit app now.")
    else:
        print("\nNo models were switched. Check file paths.")