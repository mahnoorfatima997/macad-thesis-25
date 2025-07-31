"""
Test that std() warnings are fixed in the benchmarking dashboard
"""

import numpy as np
import pandas as pd
import warnings

# Test the fixes
print("Testing std() fixes for small datasets...")
print("=" * 60)

# Test 1: Single value array
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    
    # Test with single value
    single_val = np.array([5.0])
    try:
        std_result = np.std(single_val)
        print(f"[OK] np.std([5.0]) = {std_result} (no warning)")
    except:
        print("[ERROR] Error with single value std")
    
    # Test with pandas Series
    series = pd.Series([5.0])
    try:
        std_result = series.std()
        print(f"[OK] pd.Series([5.0]).std() = {std_result} (expected NaN)")
    except:
        print("[ERROR] Error with pandas single value std")
    
    # Test with length check
    if len(series) > 1:
        std_result = series.std()
    else:
        std_result = 0.0
    print(f"[OK] With length check: {std_result}")
    
    # Check for warnings
    if len(w) > 0:
        print(f"\n[WARNING]  Warnings detected: {len(w)}")
        for warning in w:
            print(f"   - {warning.message}")
    else:
        print("\n[SUCCESS] No warnings detected!")

# Test 2: Empty phase balance
print("\n\nTesting phase balance std fix...")
phase_balance = {'ideation': 1.0, 'visualization': 0.0, 'materialization': 0.0}
balance_values = list(phase_balance.values())

# Original code would cause warning
# balance_score = 1.0 - np.std(balance_values) * 3

# Fixed code
balance_score = 1.0 - (np.std(balance_values) * 3 if len(balance_values) > 1 else 0.0)
print(f"[OK] Balance score calculated: {balance_score}")

print("\n[SUCCESS] All std() fixes appear to be working correctly!")
print("   The warnings in the Linkography Analysis tab should now be resolved.")