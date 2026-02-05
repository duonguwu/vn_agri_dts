import pandas as pd
import numpy as np
import os
import glob
import json
from pathlib import Path

# Paths
BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2")
DATA_DIR = BASE_DIR / "extracted_data"
SCHEMA_PATH = BASE_DIR / "schema_improved_v2.json"
OUTPUT_REPORT = BASE_DIR / "scripts" / "eda_report.md"

def load_data():
    csv_files = glob.glob(str(DATA_DIR / "**/extracted_data_*.csv"), recursive=True)
    if not csv_files:
        print("No CSV files found!")
        return None
    
    print(f"Loading {len(csv_files)} CSV files...")
    df_list = []
    for f in csv_files:
        temp_df = pd.read_csv(f)
        df_list.append(temp_df)
    
    return pd.concat(df_list, ignore_index=True)

def load_schema_enums():
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    enums = {
        'sectors': schema['structure']['item_context']['sector']['enum'],
        'attributes': schema['structure']['metric_context']['attribute']['enum'],
        'units': schema['structure']['metric_context']['unit']['enum'],
        'data_types': schema['structure']['metric_context']['data_type']['enum'],
        'period_types': schema['structure']['time_context']['period_type']['enum'],
        'geo_levels': schema['structure']['geo_context']['geo_level']['enum']
    }
    return enums

def perform_eda(df, enums):
    report = []
    report.append("# 📊 Agricultural Data EDA & Quality Report")
    report.append(f"**Total Records:** {len(df):,}")
    report.append(f"**Date Analysis:** {df['year'].min()} - {df['year'].max()}")
    
    # 1. Missing Values
    report.append("\n## 1. Missing Values (Nulls)")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({'Missing Count': missing, 'Percentage (%)': missing_pct.round(2)})
    report.append(missing_df[missing_df['Missing Count'] > 0].to_markdown())

    # 2. Duplicates Analysis
    report.append("\n## 2. Duplicate & Conflict Analysis")
    
    # Precise duplicates
    full_dupes = df.duplicated().sum()
    report.append(f"- **Strict Duplicates (all columns same):** {full_dupes:,} records")
    
    # Logical Conflicts: Same keys but different values
    # Keys defined by schema as "unique keys"
    key_cols = ['year', 'month', 'location_name', 'sector', 'commodity', 'sub_item', 'attribute', 'data_type', 'unit']
    
    # Exclude rows with NaN in keys for conflict analysis
    df_clean_keys = df.dropna(subset=key_cols)
    
    conflicts = df_clean_keys.groupby(key_cols)['value'].nunique()
    conflict_instances = conflicts[conflicts > 1]
    
    report.append(f"- **Logic Conflicts (Same Object, Different Values):** {conflict_instances.count():,} cases found")
    if not conflict_instances.empty:
        report.append("\n   Sample Conflict Groups (Keys with >1 unique values):")
        # Show top 5 conflicts
        sample_conflicts = conflict_instances.head(5).reset_index()
        report.append(sample_conflicts.to_markdown())

    # 3. Enum Validity
    report.append("\n## 3. Schema Validity (Enums)")
    for col, valid_values in enums.items():
        col_name = col.rstrip('s') # sectors -> sector
        if col_name in df.columns:
            invalid = df[~df[col_name].isin(valid_values) & df[col_name].notnull()][col_name].unique()
            if len(invalid) > 0:
                report.append(f"- ❌ **{col_name}**: Found {len(invalid)} invalid values: `{list(invalid[:10])}`")
            else:
                report.append(f"- ✅ **{col_name}**: All values valid.")

    # 4. Outlier & Range Check
    report.append("\n## 4. Value Distribution & Outliers")
    stats = df['value'].describe().to_frame().T
    report.append(stats.to_markdown())
    
    negative_values = df[df['value'] < 0]
    if not negative_values.empty:
        report.append(f"\n- ⚠️ **Negative Values Found:** {len(negative_values)} records.")
    
    # Extreme values (e.g. Area > 10,000k ha or Yield > 100 ton/ha - heuristic)
    extreme_area = df[(df['attribute'] == 'Area_Planted') & (df['value'] > 5000) & (df['unit'] == '1000_ha')]
    if not extreme_area.empty:
        report.append(f"- ⚠️ **Suspected Extreme Area (>5M ha):** {len(extreme_area)} records.")

    # 5. Data Coverage (Leakage & Gaps)
    report.append("\n## 5. Coverage Analysis")
    coverage = df.groupby(['year', 'month']).size().unstack(fill_value=0)
    report.append("\nRecords per Month/Year:")
    report.append(coverage.to_markdown())

    # 6. Sector Distribution
    report.append("\n## 6. Sector & Geography Distribution")
    sector_dist = df['sector'].value_counts().to_frame()
    report.append(sector_dist.to_markdown())
    
    geo_dist = df['geo_level'].value_counts().to_frame()
    report.append("\n" + geo_dist.to_markdown())

    return "\n".join(report)

if __name__ == "__main__":
    try:
        data = load_data()
        if data is not None:
            enums = load_schema_enums()
            report_content = perform_eda(data, enums)
            
            with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"EDA Report generated successfully: {OUTPUT_REPORT}")
            
            # Print a quick summary to console
            print("\nQuick Summary:")
            print(f"Rows: {len(data)}")
            print(f"Strict Duplicates: {data.duplicated().sum()}")
            key_cols = ['year', 'month', 'location_name', 'sector', 'commodity', 'sub_item', 'attribute', 'data_type', 'unit']
            conflicts = data.dropna(subset=key_cols).groupby(key_cols)['value'].nunique()
            print(f"Conflict Cases: {(conflicts > 1).sum()}")
            
    except Exception as e:
        print(f"Error during EDA: {e}")
        import traceback
        traceback.print_exc()
