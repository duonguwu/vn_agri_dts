import json
import csv
import os
from pathlib import Path

def flatten_record(record):
    """Flattens a nested record structure based on the schema."""
    flat = {}
    
    # Top level fields
    flat['record_id'] = record.get('record_id', '')
    
    # time_context
    time_ctx = record.get('time_context', {})
    flat['year'] = time_ctx.get('year', '')
    flat['month'] = time_ctx.get('month', '')
    flat['report_date'] = time_ctx.get('report_date', '')
    flat['period_type'] = time_ctx.get('period_type', '')
    
    # geo_context
    geo_ctx = record.get('geo_context', {})
    flat['geo_level'] = geo_ctx.get('geo_level', '')
    flat['location_name'] = geo_ctx.get('location_name', '')
    flat['region_id'] = geo_ctx.get('region_id', '')
    flat['region_name_vn'] = geo_ctx.get('region_name_vn', '')
    
    # item_context
    item_ctx = record.get('item_context', {})
    flat['sector'] = item_ctx.get('sector', '')
    flat['commodity'] = item_ctx.get('commodity', '')
    flat['sub_item'] = item_ctx.get('sub_item', '')
    flat['variety'] = item_ctx.get('variety', '')
    flat['processing_level'] = item_ctx.get('processing_level', '')
    
    # metric_context
    metric_ctx = record.get('metric_context', {})
    flat['attribute'] = metric_ctx.get('attribute', '')
    flat['value'] = metric_ctx.get('value', '')
    flat['unit'] = metric_ctx.get('unit', '')
    flat['data_type'] = metric_ctx.get('data_type', '')
    
    # comparison_context
    comp_ctx = record.get('comparison_context', {})
    if comp_ctx:
        flat['comparison_type'] = comp_ctx.get('comparison_type', '')
        flat['comparison_value'] = comp_ctx.get('comparison_value', '')
        flat['base_period'] = comp_ctx.get('base_period', '')
        flat['base_value'] = comp_ctx.get('base_value', '')
    else:
        flat['comparison_type'] = ''
        flat['comparison_value'] = ''
        flat['base_period'] = ''
        flat['base_value'] = ''
        
    # metadata
    meta = record.get('metadata', {})
    flat['source_file'] = meta.get('source_file', '')
    flat['appendix_number'] = meta.get('appendix_number', '')
    
    return flat

def process_year(base_path, year):
    year_dir = base_path / str(year)
    if not year_dir.exists():
        print(f"Directory {year_dir} does not exist. Skipping.")
        return

    all_records = []
    
    # Find all JSON files in the year directory
    json_files = list(year_dir.rglob("*.json"))
    print(f"Found {len(json_files)} JSON files for year {year}")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                records = data.get('records', [])
                for record in records:
                    all_records.append(flatten_record(record))
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    if not all_records:
        print(f"No records found for year {year}")
        return

    # Write to CSV
    output_file = year_dir / f"extracted_data_{year}.csv"
    fieldnames = [
        'record_id', 'year', 'month', 'report_date', 'period_type',
        'geo_level', 'location_name', 'region_id', 'region_name_vn',
        'sector', 'commodity', 'sub_item', 'variety', 'processing_level',
        'attribute', 'value', 'unit', 'data_type',
        'comparison_type', 'comparison_value', 'base_period', 'base_value',
        'source_file', 'appendix_number'
    ]
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
    
    print(f"Saved {len(all_records)} records to {output_file}")

if __name__ == "__main__":
    BASE_EXTRACTED_DATA_PATH = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data")
    YEARS = [2009, 2010, 2011, 2012]
    
    for year in YEARS:
        process_year(BASE_EXTRACTED_DATA_PATH, year)
