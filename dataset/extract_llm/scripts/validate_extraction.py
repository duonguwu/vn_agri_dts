#!/usr/bin/env python3
"""
Validation script for extracted data
"""
import json
import sys

def validate_extraction(filepath):
    with open(filepath) as f:
        data = json.load(f)
    
    records = data.get('records', [])
    metadata = data.get('metadata', {})
    
    print('=' * 80)
    print(f"VALIDATION REPORT - {metadata.get('year')}/{metadata.get('month'):02d}")
    print(f"Total records: {len(records)}")
    print('=' * 80)
    
    # Check 1: Large values
    print('\n✓ CHECK 1: Large values (> 1 million)')
    large_values = [r for r in records if r['metric_context']['value'] > 1_000_000]
    if large_values:
        print(f'   ⚠️  Found {len(large_values)} records:')
        for r in large_values[:5]:
            print(f"      - {r['geo_context']['location_name']}: {r['item_context']['commodity']} = {r['metric_context']['value']:,.0f}")
            print(f"        Source: {r['metadata']['source_file']}, Row: {r['metadata']['row_number']}")
    else:
        print('   ✅ No large values')
    
    # Check 2: Area_Seedling
    print('\n✓ CHECK 2: Area_Seedling attribute')
    seedling = [r for r in records if r['metric_context']['attribute'] == 'Area_Seedling']
    print(f'   Found {len(seedling)} records')
    if seedling:
        for r in seedling[:3]:
            print(f"      - {r['geo_context']['location_name']}: {r['metric_context']['value']:,.0f} ha")
    
    # Check 3: Aggregated commodities
    print('\n✓ CHECK 3: Aggregated commodities (should be 0)')
    agg_comms = ['Màu lương thực', 'Cây công nghiệp ngắn ngày']
    for comm in agg_comms:
        recs = [r for r in records if r['item_context']['commodity'] == comm]
        if recs:
            print(f'   ⚠️  {comm}: {len(recs)} records (should be 0!)')
            for r in recs[:2]:
                print(f"      - {r['geo_context']['location_name']}: {r['metadata']['source_file']}")
        else:
            print(f'   ✅ {comm}: 0 records')
    
    # Check 4: Specific commodities
    print('\n✓ CHECK 4: Specific commodities')
    for comm in ['Lúa', 'Ngô', 'Khoai lang', 'Sắn']:
        count = len([r for r in records if r['item_context']['commodity'] == comm])
        print(f'   - {comm}: {count} records')
    
    print('\n' + '=' * 80)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        validate_extraction(sys.argv[1])
    else:
        validate_extraction('2009/02/extracted_data_2009_02.json')
