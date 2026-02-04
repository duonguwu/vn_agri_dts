#!/usr/bin/env python3
"""
Convert JSON files to full CSV with all columns flattened
Merge all months into yearly CSV files
"""

import json
import pandas as pd
from pathlib import Path
import sys

def flatten_record(record):
    """Flatten nested JSON record into flat dictionary for CSV"""
    flat = {}
    
    # Record ID
    flat['record_id'] = record.get('record_id')
    
    # Time context
    tc = record.get('time_context', {})
    flat['year'] = tc.get('year')
    flat['month'] = tc.get('month')
    flat['report_date'] = tc.get('report_date')
    flat['period_type'] = tc.get('period_type')
    
    # Geo context
    gc = record.get('geo_context', {})
    flat['geo_level'] = gc.get('geo_level')
    flat['location_name'] = gc.get('location_name')
    flat['region_id'] = gc.get('region_id')
    flat['region_name_vn'] = gc.get('region_name_vn')
    
    # Item context
    ic = record.get('item_context', {})
    flat['sector'] = ic.get('sector')
    flat['commodity'] = ic.get('commodity')
    flat['sub_item'] = ic.get('sub_item')
    flat['variety'] = ic.get('variety')
    flat['processing_level'] = ic.get('processing_level')
    
    # Metric context
    mc = record.get('metric_context', {})
    flat['attribute'] = mc.get('attribute')
    flat['value'] = mc.get('value')
    flat['unit'] = mc.get('unit')
    flat['data_type'] = mc.get('data_type')
    
    # Comparison context
    cc = record.get('comparison_context', {})
    flat['comparison_type'] = cc.get('comparison_type')
    flat['comparison_value'] = cc.get('comparison_value')
    flat['base_period'] = cc.get('base_period')
    flat['base_value'] = cc.get('base_value')
    
    # Metadata
    md = record.get('metadata', {})
    flat['source_file'] = md.get('source_file')
    flat['appendix_number'] = md.get('appendix_number')
    flat['appendix_title'] = md.get('appendix_title')
    flat['table_index'] = md.get('table_index')
    flat['row_number'] = md.get('row_number')
    flat['extraction_method'] = md.get('extraction_method')
    flat['extraction_confidence'] = md.get('extraction_confidence')
    flat['notes'] = md.get('notes')
    
    # Data quality
    dq = record.get('data_quality', {})
    flat['is_aggregated'] = dq.get('is_aggregated')
    flat['has_missing_values'] = dq.get('has_missing_values')
    flat['data_status'] = dq.get('data_status')
    
    return flat

def process_year(base_dir, year):
    """Process all months for a given year and create consolidated CSV"""
    year_dir = base_dir / str(year)
    
    if not year_dir.exists():
        print(f"⚠️  Year {year} directory not found, skipping...")
        return
    
    all_records = []
    months_processed = 0
    
    # Process each month
    for month in range(1, 13):
        month_dir = year_dir / f"{month:02d}"
        json_file = month_dir / f"extracted_data_{year}_{month:02d}.json"
        
        if not json_file.exists():
            continue
        
        # Load JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('records', [])
        print(f"  Reading {year}/{month:02d}: {len(records)} records")
        
        # Flatten each record
        for record in records:
            flat_record = flatten_record(record)
            all_records.append(flat_record)
        
        months_processed += 1
    
    if not all_records:
        print(f"⚠️  No records found for {year}")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_records)
    
    # Sort by date and location
    df = df.sort_values(['year', 'month', 'location_name', 'commodity'])
    
    # Save to CSV
    output_file = year_dir / f"consolidated_{year}_full.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    
    print(f"✅ {year}: {len(all_records)} records from {months_processed} months")
    print(f"   → {output_file}")
    print(f"   → {file_size_mb:.2f} MB, {len(df.columns)} columns\n")

def main():
    base_dir = Path(__file__).parent.parent
    
    # Get year range from command line or use default
    if len(sys.argv) > 2:
        start_year = int(sys.argv[1])
        end_year = int(sys.argv[2])
    else:
        start_year = 2009
        end_year = 2013
    
    print("=" * 80)
    print(f"Converting JSON to Full CSV ({start_year}-{end_year})")
    print("=" * 80)
    print()
    
    for year in range(start_year, end_year + 1):
        print(f"Processing {year}...")
        process_year(base_dir, year)
    
    print("=" * 80)
    print("✅ All years processed!")
    print("=" * 80)

if __name__ == '__main__':
    main()
