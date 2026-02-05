import pandas as pd
import numpy as np
import json
from pathlib import Path
import glob

# Paths
BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2")
DATA_DIR = BASE_DIR / "extracted_data"
SCHEMA_PATH = BASE_DIR / "schema_improved_v2.json"
REGION_MAP_PATH = BASE_DIR / "region_map.json"
AUDIT_LOG_PATH = BASE_DIR / "scripts" / "detailed_audit_log.csv"

def load_data():
    csv_files = glob.glob(str(DATA_DIR / "**/extracted_data_*.csv"), recursive=True)
    if not csv_files:
        print("No CSV files found!")
        return None
    
    df_list = []
    for f in csv_files:
        temp_df = pd.read_csv(f)
        df_list.append(temp_df)
    
    return pd.concat(df_list, ignore_index=True)

def load_schema_enums():
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    return {
        'sector': schema['structure']['item_context']['sector']['enum'],
        'attribute': schema['structure']['metric_context']['attribute']['enum'],
        'unit': schema['structure']['metric_context']['unit']['enum'],
        'data_type': schema['structure']['metric_context']['data_type']['enum'],
        'period_type': schema['structure']['time_context']['period_type']['enum'],
        'geo_level': schema['structure']['geo_context']['geo_level']['enum']
    }

def load_region_map():
    with open(REGION_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_audit(df, enums, region_map):
    audit_results = []

    def log_error(row, error_type, detail, impacted_val=None):
        audit_results.append({
            'year': row.get('year'),
            'month': row.get('month'),
            'location_name': row.get('location_name'),
            'sector': row.get('sector'),
            'commodity': row.get('commodity'),
            'attribute': row.get('attribute'),
            'source_file': row.get('source_file'),
            'appendix_number': row.get('appendix_number'),
            'error_type': error_type,
            'error_detail': detail,
            'impacted_value': impacted_val if impacted_val is not None else row.get('value'),
            'record_id': row.get('record_id')
        })

    # 1. Missing Vital Values
    vital_cols = ['year', 'month', 'location_name', 'sector', 'attribute', 'value', 'unit', 'data_type']
    for col in vital_cols:
        missing_rows = df[df[col].isnull()]
        for _, row in missing_rows.iterrows():
            log_error(row, 'MISSING_FIELD', f"Field '{col}' is null")

    # 2. Value Conflicts (Same keys, different values)
    key_cols = ['year', 'month', 'location_name', 'sector', 'commodity', 'sub_item', 'attribute', 'data_type', 'unit']
    # Drop rows with NaN in keys for conflict check
    df_clean = df.dropna(subset=key_cols)
    duplicates = df_clean.groupby(key_cols)['value'].nunique()
    conflict_keys = duplicates[duplicates > 1].index
    
    if not conflict_keys.empty:
        for keys in conflict_keys:
            # Get all rows matching these keys
            mask = True
            for i, col in enumerate(key_cols):
                mask &= (df_clean[col] == keys[i])
            conflict_rows = df_clean[mask]
            vals = conflict_rows['value'].unique()
            for _, row in conflict_rows.iterrows():
                log_error(row, 'VALUE_CONFLICT', f"Matched keys but found multiple values: {list(vals)}")

    # 3. Enum Violations
    for col, valid_vals in enums.items():
        if col in df.columns:
            invalid_rows = df[~df[col].isin(valid_vals) & df[col].notnull()]
            for _, row in invalid_rows.iterrows():
                log_error(row, 'INVALID_ENUM', f"Value '{row[col]}' not in schema enums for '{col}'")

    # 4. Geo-Consistency
    provinces = region_map.get('provinces', {})
    for _, row in df.iterrows():
        loc = str(row.get('location_name'))
        if loc in provinces:
            expected_region_id = provinces[loc]['region_id']
            actual_region_id = row.get('region_id')
            if pd.notnull(actual_region_id) and actual_region_id != expected_region_id:
                log_error(row, 'GEO_MISMATCH', f"Province '{loc}' should be in region '{expected_region_id}' but found '{actual_region_id}'")

    # 5. Outliers & Logical Checks
    # Negative values
    neg_rows = df[df['value'] < 0]
    for _, row in neg_rows.iterrows():
        log_error(row, 'LOGIC_ERROR', f"Negative value found: {row['value']}")

    # Yield outliers (> 15 ton/ha)
    yield_outliers = df[(df['attribute'] == 'Yield') & (df['value'] > 15) & (df['unit'] == 'ton_per_ha')]
    for _, row in yield_outliers.iterrows():
        log_error(row, 'OUTLIER', f"Suspected high Yield: {row['value']} ton/ha")
    
    # Area outliers (> 10M ha)
    area_outliers = df[(df['attribute'] == 'Area_Planted') & (df['value'] > 10000) & (df['unit'] == '1000_ha')]
    for _, row in area_outliers.iterrows():
        log_error(row, 'OUTLIER', f"Suspected extreme Area: {row['value']} (1000 ha)")

    return pd.DataFrame(audit_results)

if __name__ == "__main__":
    print("Starting Deep Data Audit...")
    df = load_data()
    if df is not None:
        enums = load_schema_enums()
        region_map = load_region_map()
        
        audit_df = run_audit(df, enums, region_map)
        
        # Save results
        audit_df.to_csv(AUDIT_LOG_PATH, index=False, encoding='utf-8-sig')
        print(f"Audit completed. Found {len(audit_df)} potential issues.")
        print(f"Audit log saved to: {AUDIT_LOG_PATH}")
        
        # Summary report to console
        if not audit_df.empty:
            print("\nError Summary by Type:")
            print(audit_df['error_type'].value_counts())
            
            print("\nTop 5 Files with most errors:")
            print(audit_df['source_file'].value_counts().head(5))
