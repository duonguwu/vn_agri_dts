#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample Data Viewer and Schema Validator
View sample records from extracted data and validate against schema
"""

import json
from pathlib import Path
from typing import Dict, List
import random

# Paths
BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts")
DATA_FILE = BASE_DIR / "dataset/extract_llm/2009/extracted_data_2009_02.json"
SCHEMA_FILE = BASE_DIR / "schema_improved.json"

def load_data():
    """Load extracted data"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_schema():
    """Load schema"""
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_record(record: Dict, index: int = None):
    """Pretty print a single record"""
    if index is not None:
        print(f"\n{'='*80}")
        print(f"RECORD #{index + 1}")
        print(f"{'='*80}")
    
    print(f"\n📋 Record ID: {record['record_id']}")
    
    # Time Context
    tc = record['time_context']
    print(f"\n⏰ TIME CONTEXT:")
    print(f"   Year: {tc['year']}, Month: {tc['month']}")
    print(f"   Report Date: {tc.get('report_date', 'N/A')}")
    print(f"   Period Type: {tc.get('period_type', 'N/A')}")
    
    # Geo Context
    gc = record['geo_context']
    print(f"\n🌍 GEO CONTEXT:")
    print(f"   Level: {gc['geo_level']}")
    print(f"   Location: {gc['location_name']}")
    if gc.get('region_id'):
        print(f"   Region: {gc['region_name_vn']} ({gc['region_id']})")
    
    # Item Context
    ic = record['item_context']
    print(f"\n📦 ITEM CONTEXT:")
    print(f"   Sector: {ic['sector']}")
    print(f"   Commodity: {ic['commodity']}")
    if ic.get('sub_item'):
        print(f"   Sub-item: {ic['sub_item']}")
    
    # Metric Context
    mc = record['metric_context']
    print(f"\n📊 METRIC:")
    print(f"   Attribute: {mc['attribute']}")
    print(f"   Value: {mc['value']:,.2f} {mc['unit']}")
    print(f"   Data Type: {mc['data_type']}")
    
    # Metadata
    md = record['metadata']
    print(f"\n📄 METADATA:")
    print(f"   Source: {md['source_file']}")
    print(f"   Appendix: {md['appendix_number']} - {md.get('appendix_title', 'N/A')}")
    print(f"   Confidence: {md.get('extraction_confidence', 0):.2%}")
    
    # Data Quality
    dq = record['data_quality']
    print(f"\n✓ DATA QUALITY:")
    print(f"   Aggregated: {dq.get('is_aggregated', False)}")
    print(f"   Status: {dq.get('data_status', 'N/A')}")

def view_samples_by_sector(data: Dict):
    """View sample records from each sector"""
    records = data['records']
    
    # Group by sector
    by_sector = {}
    for record in records:
        sector = record['item_context']['sector']
        if sector not in by_sector:
            by_sector[sector] = []
        by_sector[sector].append(record)
    
    print(f"\n{'#'*80}")
    print(f"SAMPLE RECORDS BY SECTOR")
    print(f"{'#'*80}")
    
    for sector, sector_records in sorted(by_sector.items()):
        print(f"\n\n{'='*80}")
        print(f"SECTOR: {sector} ({len(sector_records)} records)")
        print(f"{'='*80}")
        
        # Show 2 random samples
        samples = random.sample(sector_records, min(2, len(sector_records)))
        for i, record in enumerate(samples):
            print_record(record, i)

def view_samples_by_appendix(data: Dict, appendix: str):
    """View sample records from a specific appendix"""
    records = [r for r in data['records'] if r['metadata']['appendix_number'] == appendix]
    
    print(f"\n{'#'*80}")
    print(f"APPENDIX {appendix} - {len(records)} records")
    print(f"{'#'*80}")
    
    if records:
        # Show first 3 records
        for i, record in enumerate(records[:3]):
            print_record(record, i)
    else:
        print(f"\nNo records found for appendix {appendix}")

def validate_schema(data: Dict, schema: Dict):
    """Basic schema validation"""
    print(f"\n{'#'*80}")
    print(f"SCHEMA VALIDATION")
    print(f"{'#'*80}")
    
    records = data['records']
    errors = []
    warnings = []
    
    # Check required fields
    required_contexts = ['time_context', 'geo_context', 'item_context', 'metric_context', 'metadata', 'data_quality']
    
    for i, record in enumerate(records):
        # Check top-level contexts
        for context in required_contexts:
            if context not in record:
                errors.append(f"Record {i}: Missing {context}")
        
        # Check required fields in time_context
        if 'time_context' in record:
            tc = record['time_context']
            if not (2008 <= tc.get('year', 0) <= 2022):
                errors.append(f"Record {i}: Invalid year {tc.get('year')}")
            if not (1 <= tc.get('month', 0) <= 12):
                errors.append(f"Record {i}: Invalid month {tc.get('month')}")
        
        # Check geo_level enum
        if 'geo_context' in record:
            gc = record['geo_context']
            valid_levels = ["National", "Regional", "Provincial"]
            if gc.get('geo_level') not in valid_levels:
                errors.append(f"Record {i}: Invalid geo_level {gc.get('geo_level')}")
        
        # Check sector enum
        if 'item_context' in record:
            ic = record['item_context']
            valid_sectors = ["Cultivation", "Livestock", "Fishery", "Forestry", "Trade", "Pest", "Investment", "Reporting"]
            if ic.get('sector') not in valid_sectors:
                errors.append(f"Record {i}: Invalid sector {ic.get('sector')}")
        
        # Check value >= 0
        if 'metric_context' in record:
            mc = record['metric_context']
            if mc.get('value', 0) < 0:
                errors.append(f"Record {i}: Negative value {mc.get('value')}")
    
    # Print results
    print(f"\n✓ Total Records Checked: {len(records)}")
    print(f"✓ Errors Found: {len(errors)}")
    print(f"✓ Warnings Found: {len(warnings)}")
    
    if errors:
        print(f"\n❌ ERRORS:")
        for error in errors[:10]:  # Show first 10
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    else:
        print(f"\n✅ All records passed validation!")
    
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in warnings[:10]:
            print(f"   - {warning}")

def show_statistics(data: Dict):
    """Show detailed statistics"""
    records = data['records']
    
    print(f"\n{'#'*80}")
    print(f"DETAILED STATISTICS")
    print(f"{'#'*80}")
    
    # By sector and commodity
    sector_commodity = {}
    for record in records:
        sector = record['item_context']['sector']
        commodity = record['item_context']['commodity']
        key = f"{sector}::{commodity}"
        sector_commodity[key] = sector_commodity.get(key, 0) + 1
    
    print(f"\n📊 Top 20 Sector-Commodity Combinations:")
    sorted_items = sorted(sector_commodity.items(), key=lambda x: x[1], reverse=True)
    for i, (key, count) in enumerate(sorted_items[:20], 1):
        sector, commodity = key.split("::")
        print(f"   {i:2d}. {sector:15s} | {commodity:30s} : {count:4d} records")
    
    # By attribute
    attributes = {}
    for record in records:
        attr = record['metric_context']['attribute']
        attributes[attr] = attributes.get(attr, 0) + 1
    
    print(f"\n📏 Attributes Distribution:")
    for attr, count in sorted(attributes.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(records) * 100
        print(f"   {attr:25s} : {count:4d} ({pct:5.1f}%)")
    
    # By data type
    data_types = {}
    for record in records:
        dt = record['metric_context']['data_type']
        data_types[dt] = data_types.get(dt, 0) + 1
    
    print(f"\n📋 Data Types:")
    for dt, count in sorted(data_types.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(records) * 100
        print(f"   {dt:15s} : {count:4d} ({pct:5.1f}%)")

def main():
    """Main function"""
    print(f"\n{'#'*80}")
    print(f"EXTRACTED DATA VIEWER & VALIDATOR")
    print(f"{'#'*80}")
    
    # Load data
    print(f"\n📂 Loading data from: {DATA_FILE.name}")
    data = load_data()
    
    print(f"\n📊 Metadata:")
    for key, value in data['metadata'].items():
        print(f"   {key}: {value}")
    
    # Show statistics
    show_statistics(data)
    
    # Validate schema
    schema = load_schema()
    validate_schema(data, schema)
    
    # Show samples by sector
    view_samples_by_sector(data)
    
    # Show samples from specific appendices
    print(f"\n\n{'='*80}")
    print(f"SPECIFIC APPENDIX SAMPLES")
    print(f"{'='*80}")
    
    for appendix in ['PL6', 'PL7', 'PL8', 'PL9']:
        view_samples_by_appendix(data, appendix)

if __name__ == "__main__":
    main()
