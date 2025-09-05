#!/usr/bin/env python3
"""
Script to clear domain expert cache entries from Streamlit session state.
This ensures fresh responses after the cache key fix.
"""

import sys
import os

def clear_cache_simulation():
    """Simulate the cache clearing logic."""
    
    print("🧹 Domain Expert Cache Clearing Simulation")
    print("=" * 60)
    
    # Simulate old cache entries that would exist
    simulated_session_state = {
        "domain_expert_-1234567890_community_center": "Old cached response about central commons...",
        "domain_expert_9876543210_warehouse": "Another old cached response...",
        "domain_expert_1111111111_project_knowledge": "Yet another cached response...",
        "other_cache_key": "Some other data",
        "validation_12345": "Validation cache",
        "domain_expert_new_hash_community_center_knowledge": "This should stay"
    }
    
    print("🔍 Simulated Session State Before Clearing:")
    print("-" * 40)
    for key, value in simulated_session_state.items():
        if key.startswith("domain_expert_"):
            print(f"   {key}: {value[:50]}...")
        else:
            print(f"   {key}: {value}")
    print()
    
    # Simulate the clearing logic
    current_cache_key = "domain_expert_new_hash_community_center_knowledge"
    old_cache_keys_to_clear = []
    
    for key in list(simulated_session_state.keys()):
        if key.startswith("domain_expert_") and key != current_cache_key:
            old_cache_keys_to_clear.append(key)
    
    print(f"🎯 Current Cache Key: {current_cache_key}")
    print(f"🧹 Keys to Clear: {old_cache_keys_to_clear}")
    print()
    
    # Clear the old keys
    for old_key in old_cache_keys_to_clear:
        del simulated_session_state[old_key]
    
    print("✅ Simulated Session State After Clearing:")
    print("-" * 40)
    for key, value in simulated_session_state.items():
        if key.startswith("domain_expert_"):
            print(f"   {key}: {value[:50]}...")
        else:
            print(f"   {key}: {value}")
    print()
    
    print("🎯 RESULTS:")
    print(f"✅ Cleared {len(old_cache_keys_to_clear)} old domain expert cache entries")
    print("✅ Preserved non-domain-expert cache entries")
    print("✅ Preserved current cache key (if it existed)")
    print()
    print("Expected Behavior:")
    print("- Users will get fresh responses that match their actual questions")
    print("- No more wrong cached responses from previous conversations")
    print("- Performance maintained for identical questions")
    print("- Other cache systems (validation, web search) unaffected")

if __name__ == "__main__":
    clear_cache_simulation()
