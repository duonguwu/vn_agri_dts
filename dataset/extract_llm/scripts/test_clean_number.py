#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for clean_number() function
"""

import sys
sys.path.insert(0, '/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm/scripts')

from extract_data import clean_number

# Test cases
test_cases = [
    # (input, expected_output, description)
    ("1,234", 1234.0, "Thousands separator"),
    ("1,234,567", 1234567.0, "Multiple thousands separators"),
    ("123.45", 123.45, "Decimal number"),
    ("1,234.56", 1234.56, "Mixed format (Vietnamese standard)"),
    ("933,587", 933587.0, "From PL2 data"),
    ("29,421", 29421.0, "From PL2 data"),
    
    # Edge cases
    ("", None, "Empty string"),
    ("-", None, "Dash only"),
    ("123", 123.0, "Plain integer"),
    ("0", 0.0, "Zero"),
    
    # Should FAIL (return None)
    ("76,786 39,600", None, "Concatenated numbers (space separated)"),
    ("123  456", None, "Concatenated numbers (multiple spaces)"),
    ("abc", None, "Letters only"),
    ("123abc", None, "Mixed letters and numbers"),
    ("Miền Bắc 933,587", None, "Text with number"),
    
    # Sanity check
    ("999999999999", None, "Too large (> 1 billion)"),
]

print("=" * 80)
print("TESTING clean_number()")
print("=" * 80)

passed = 0
failed = 0

for input_val, expected, description in test_cases:
    result = clean_number(input_val)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"\n{status} | {description}")
    print(f"  Input:    '{input_val}'")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")

print("\n" + "=" * 80)
print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)

if failed == 0:
    print("✅ All tests passed!")
else:
    print(f"❌ {failed} test(s) failed!")
    sys.exit(1)
