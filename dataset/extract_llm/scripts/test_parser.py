#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the universal text parser
"""

import sys
sys.path.insert(0, '/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm/scripts')

from extract_data import extract_components_from_text, parse_header_for_commodity

# Test cases for extract_components_from_text
test_cases = [
    "Gieo cấy lúa đông xuân cả nước",
    "Thu hoạch lúa đông xuân ở miền Nam",
    "Gieo trồng màu lương thực",
    "Khoai lang",
    "Gieo trồng cây công nghiệp ngắn ngày",
    "Gieo trồng rau, đậu các loại",
]

print("=" * 80)
print("TESTING extract_components_from_text()")
print("=" * 80)

for test_text in test_cases:
    result = extract_components_from_text(test_text)
    print(f"\nInput: '{test_text}'")
    print(f"  → Location: {result['location']}")
    print(f"  → Commodity: {result['commodity']}")
    print(f"  → Sub_item: {result['sub_item']}")
    print(f"  → Attribute: {result['attribute']}")
    print(f"  → Action: {result['action']}")

# Test cases for parse_header_for_commodity
header_test_cases = [
    "Diện tích gieo cấy lúa đông xuân",
    "Ngô",
    "Khoai lang",
    "Diện tích thu hoạch",
    "Năng suất",
    "Sản lượng",
    "% TH so GC",
]

print("\n" + "=" * 80)
print("TESTING parse_header_for_commodity()")
print("=" * 80)

for header in header_test_cases:
    result = parse_header_for_commodity(header)
    print(f"\nHeader: '{header}'")
    print(f"  → Commodity: {result['commodity']}")
    print(f"  → Sub_item: {result['sub_item']}")
    print(f"  → Attribute: {result['attribute']}")
    print(f"  → Unit: {result['unit']}")

print("\n" + "=" * 80)
print("✅ All tests completed!")
print("=" * 80)
