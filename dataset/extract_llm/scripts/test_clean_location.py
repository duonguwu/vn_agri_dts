#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for clean_location_name() function
Verifies that all 11 error types are handled correctly
"""

import re
from typing import Optional

def clean_location_name(location: str) -> Optional[str]:
    """
    Clean location_name from common extraction errors
    (Copy of function from extract_data.py for testing)
    """
    if not location or not isinstance(location, str):
        return None
    
    original = location
    location = location.strip()
    
    # 1. Remove number prefixes (1., 2., 3., ...)
    location = re.sub(r'^\d+\.\s*', '', location)
    
    # 2. Remove bullet prefixes (+, -, ‐)
    location = re.sub(r'^[+\-‐]\s*', '', location)
    
    # 3. Fix common space-in-word patterns (Vietnamese specific)
    location = re.sub(r'đ\s+ậu', 'đậu', location)
    location = re.sub(r'mi\s+ền', 'miền', location)
    location = re.sub(r'trung\s+bộ', 'trung bộ', location)
    location = re.sub(r'nam\s+bộ', 'nam bộ', location)
    location = re.sub(r'tây\s+nguyên', 'tây nguyên', location)
    location = re.sub(r'đông\s+bắc', 'đông bắc', location)
    location = re.sub(r'tây\s+bắc', 'tây bắc', location)
    location = re.sub(r'cả\s+nước', 'cả nước', location)
    location = re.sub(r'rau,?\s*đ\s+ậu', 'rau, đậu', location)
    
    # 4. Fix typo spacing
    location = re.sub(r'miềnnam', 'miền nam', location, flags=re.IGNORECASE)
    location = re.sub(r'miềnbắc', 'miền bắc', location, flags=re.IGNORECASE)
    location = re.sub(r'trungbộ', 'trung bộ', location, flags=re.IGNORECASE)
    location = re.sub(r'tâynguyên', 'tây nguyên', location, flags=re.IGNORECASE)
    location = re.sub(r'đôngbắc', 'đông bắc', location, flags=re.IGNORECASE)
    location = re.sub(r'tâybắc', 'tây bắc', location, flags=re.IGNORECASE)
    
    # 5. Remove trailing numbers
    location = re.sub(r'[\d,\.]+$', '', location)
    
    # 6. Fix empty parentheses
    location = re.sub(r'\(\s*\)', '', location)
    
    # 7. Fix unclosed parentheses
    location = re.sub(r'\([^)]*$', '', location)
    
    # 8. Remove multiple spaces
    location = re.sub(r'\s{2,}', ' ', location)
    
    # 9. Trim again
    location = location.strip()
    
    # === VALIDATION ===
    
    # 10. Skip if empty after cleaning
    if not location or len(location) < 2:
        return None
    
    # 11. Skip if only numbers
    if location.replace('.', '').replace(',', '').isdigit():
        return None
    
    # 12. Skip if contains metadata keywords (column headers)
    # Only skip if it's MOSTLY metadata, not if metadata is part of valid location
    metadata_only_keywords = [
        'diện tích', 'năng suất', 'sản lượng', 'dt gieo', 'dt cho',
        'dt gieo trồng', 'dt cho sản phẩm', 'tạ/ha', '1000 ha',
        'trong đó:', 'chia ra:'
    ]
    location_lower = location.lower()
    
    # Check if location is ONLY metadata (exact match or very similar)
    if location_lower in metadata_only_keywords:
        return None
    
    # Check if location starts with metadata keywords (likely a header)
    if any(location_lower.startswith(kw) for kw in metadata_only_keywords):
        return None
    
    # Skip if it's a concatenated header (multiple keywords together, no spaces)
    if len(location) > 50 and any(kw in location_lower for kw in ['diện tích', 'năng suất', 'sản lượng']):
        return None
    
    # 13. Skip if Roman numerals (extend to longer patterns)
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 
                      'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX']
    if location.upper() in roman_numerals:
        return None
    
    # 14. Skip if starts with number
    if location[0].isdigit():
        return None
    
    return location


# Test cases based on actual errors from error_summary_by_type.csv
test_cases = [
    # Error Type 1: number_prefix
    ("1. Gieo cấy lúa đông xuân cả nước", "Gieo cấy lúa đông xuân cả nước"),
    ("2. Thu hoạch lúa đông xuân ở miền Nam", "Thu hoạch lúa đông xuân ở miền Nam"),
    ("3. Gieo trồng màu lương thực()", "Gieo trồng màu lương thực"),
    
    # Error Type 2: minus_prefix
    ("- Vùng Duyên hải Bắc Trung bộ", "Vùng Duyên hải Bắc Trung bộ"),
    ("- Khoai lang", "Khoai lang"),
    ("- Sắn", "Sắn"),
    
    # Error Type 3: plus_prefix
    ("+ Miền Nam", "Miền Nam"),
    ("+ Bắc Trung bộ", "Bắc Trung bộ"),
    ("+ Vùng Tây Nguyên", "Vùng Tây Nguyên"),
    
    # Error Type 4: bullet_prefix
    ("‐  Miền Nam", "Miền Nam"),
    ("‐ Khoai lang", "Khoai lang"),
    
    # Error Type 5: space_in_word
    ("mi ền nam", "miền nam"),
    ("rau, đ ậu", "rau, đậu"),
    ("trung bộ", "trung bộ"),
    
    # Error Type 6: typo_spacing (no space)
    ("miềnnam", "miền nam"),
    ("miềnbắc", "miền bắc"),
    ("trungbộ", "trung bộ"),
    
    # Error Type 7: number_suffix
    ("1. Thu hoạch lúa đông xuân miền Bắc658.8", "Thu hoạch lúa đông xuân miền Bắc"),
    ("- Bắc Trung bộ294.1", "Bắc Trung bộ"),
    ("- Khoai lang111.5", "Khoai lang"),
    
    # Error Type 8: empty_parens
    ("3. Gieo trồng màu lương thực()", "Gieo trồng màu lương thực"),
    ("5. Gieo trồng rau, đậu các loại()", "Gieo trồng rau, đậu các loại"),
    ("4. Gieo trồng cây công nghiệp ngắn ngày()", "Gieo trồng cây công nghiệp ngắn ngày"),
    
    # Error Type 9: unclosed_parens
    ("4. Gieo trồng cây công nghiệp ngắn ngày(", "Gieo trồng cây công nghiệp ngắn ngày"),
    
    # Error Type 10: multiple_spaces
    ("-  Khoai lang", "Khoai lang"),
    ("-  Sắn", "Sắn"),
    ("-  Lạc", "Lạc"),
    
    # Error Type 11: only_numbers (should return None)
    ("1", None),
    ("1.1", None),
    ("1.2", None),
    
    # Error Type 12: single_char (should return None)
    ("I", None),
    ("II", None),
    ("III", None),
    
    # Valid locations (should pass through)
    ("Hà Nội", "Hà Nội"),
    ("TP. Hồ Chí Minh", "TP. Hồ Chí Minh"),
    ("Cả nước", "Cả nước"),
    ("Miền Bắc", "Miền Bắc"),
]

def run_tests():
    """Run all test cases"""
    print("=" * 80)
    print("Testing clean_location_name() function")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for input_val, expected in test_cases:
        result = clean_location_name(input_val)
        
        if result == expected:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"\n{status}")
        print(f"  Input:    '{input_val}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
