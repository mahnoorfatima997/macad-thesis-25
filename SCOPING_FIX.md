# Variable Scoping Fix

## Problem: NameError - cannot access free variable 'input_text'

The benchmarking code was failing with a `NameError` because `input_text` was being referenced outside the scope where it was defined.

## Root Cause

In the `_calculate_self_awareness` method, the code structure was:

```python
if pd.notna(row['student_input']) and isinstance(row['student_input'], str):
    input_text = row['student_input'].lower()
    # ... use input_text here ...

# ERROR: input_text used here but may not be defined
if any(phrase in input_text for phrase in [...]):
    # ...
```

The second `if` statement was outside the first one, so if the first condition failed, `input_text` would never be defined.

## Solution

Moved the second check inside the first `if` block where `input_text` is guaranteed to be defined:

```python
if pd.notna(row['student_input']) and isinstance(row['student_input'], str):
    input_text = row['student_input'].lower()
    
    # First check
    if any(phrase in input_text for phrase in [...]):
        # ...
    
    # Second check - now safely inside the scope
    if any(phrase in input_text for phrase in [...]):
        # ...
```

## Impact

✅ No more NameError when processing data
✅ Proper variable scoping maintained
✅ Both checks only run when input is valid
✅ More efficient as we don't try to check invalid inputs

The benchmarking should now run without scoping errors!