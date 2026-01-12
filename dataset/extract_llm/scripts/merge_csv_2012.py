#!/usr/bin/env python3
"""Merge all monthly CSV files into one consolidated file for 2012"""

import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts")
DATA_DIR = BASE_DIR / "dataset/extract_llm/2012"
OUTPUT_FILE = DATA_DIR / "consolidated_2012.csv"

# Find all CSV files
csv_files = sorted(DATA_DIR.glob("*/extracted_data_2012_*.csv"))

print(f"Found {len(csv_files)} CSV files")

# Read and concatenate
dfs = []
for csv_file in csv_files:
    print(f"Reading: {csv_file.name}")
    df = pd.read_csv(csv_file)
    dfs.append(df)

# Merge
merged = pd.concat(dfs, ignore_index=True)

# Save
merged.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

print(f"\n✓ Merged {len(merged)} records")
print(f"✓ Saved to: {OUTPUT_FILE}")
print(f"✓ File size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")
