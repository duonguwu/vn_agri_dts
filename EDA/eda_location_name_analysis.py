"""
COMPREHENSIVE LOCATION_NAME ERROR ANALYSIS
==========================================

Phân tích toàn diện các lỗi trong location_name dựa trên patterns thực tế
Tạo báo cáo chi tiết để trace lỗi về năm-tháng-phụ lục

Author: Data Quality Team
Date: 2026-01-25
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_PATH = Path(r"D:\UIT\aThacSy\Data Mining\2. Data Pre-processing\vn_agri_dts\dataset\extract_llm")
OUTPUT_DIR = BASE_PATH / "error_analysis" / "location_name_error_analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load consolidated data
print("=" * 100)
print("📂 LOADING DATA")
print("=" * 100)

files = {
    2009: BASE_PATH / "2009" / "consolidated_2009.csv",
    2010: BASE_PATH / "2010" / "consolidated_2010.csv",
    2011: BASE_PATH / "2011" / "consolidated_2011.csv",
    2012: BASE_PATH / "2012" / "consolidated_2012.csv"
}

dfs = {}
for year, path in files.items():
    if path.exists():
        df = pd.read_csv(path)
        dfs[year] = df
        print(f"✅ {year}: {len(df):,} rows")
    else:
        print(f"❌ {year}: File not found")

df_all = pd.concat(dfs.values(), ignore_index=True)
print(f"\n📊 Total: {len(df_all):,} rows")
print("=" * 100)


# ============================================================================
# ERROR DETECTION PATTERNS
# ============================================================================
print("\n" + "=" * 100)
print("🔍 DEFINING ERROR DETECTION PATTERNS")
print("=" * 100)

ERROR_PATTERNS = {
    # Category 1: Số thứ tự và ký hiệu đầu dòng
    'number_prefix': {
        'pattern': r'^\d+\.\s',
        'description': 'Số thứ tự ở đầu (1., 2., 3., ...)',
        'example': '1. Gieo cấy lúa đông xuân cả nước'
    },
    'plus_prefix': {
        'pattern': r'^\+\s',
        'description': 'Dấu + ở đầu',
        'example': '+ bắc trung bộ'
    },
    'minus_prefix': {
        'pattern': r'^-\s',
        'description': 'Dấu - ở đầu',
        'example': '- miền nam'
    },
    'bullet_prefix': {
        'pattern': r'^‐\s',
        'description': 'Dấu bullet (‐) ở đầu',
        'example': '‐ khoai lang'
    },
    
    # Category 2: Số dính vào text
    'number_suffix': {
        'pattern': r'[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+\d+\.?\d*$',
        'description': 'Số dính vào cuối text',
        'example': 'miền nam1,926.2', 'lạc172.2'
    },
    'number_in_middle': {
        'pattern': r'\d+\.?\d*[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+',
        'description': 'Số ở giữa text',
        'example': '1000ha', '2=3+7'
    },
    
    # Category 3: Dấu ngoặc
    'empty_parens': {
        'pattern': r'\(\)',
        'description': 'Dấu ngoặc rỗng ()',
        'example': 'Gieo trồng màu lương thực()'
    },
    'unclosed_parens': {
        'pattern': r'\([^)]*$',
        'description': 'Dấu ngoặc không đóng',
        'example': 'Cây công nghiệp ngắn ngày('
    },
    
    # Category 4: Khoảng trắng
    'leading_space': {
        'pattern': r'^\s+',
        'description': 'Khoảng trắng đầu',
        'example': ' Cả nước'
    },
    'trailing_space': {
        'pattern': r'\s+$',
        'description': 'Khoảng trắng cuối',
        'example': 'Cả nước '
    },
    'multiple_spaces': {
        'pattern': r'\s{2,}',
        'description': 'Nhiều khoảng trắng liên tiếp',
        'example': 'Cả  nước'
    },
    'space_in_word': {
        'pattern': r'[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+\s[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+(?=[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])',
        'description': 'Khoảng trắng trong từ',
        'example': 'mi ền nam', 'đ ậu tương'
    },
    
    # Category 5: Nhiều location ghép lại (không có dấu phân cách)
    'concatenated_locations': {
        'pattern': r'[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]{50,}',
        'description': 'Text quá dài (nhiều location ghép lại)',
        'example': 'phi lip pinxinh ga pocubađài loanmalaixia...'
    },
    
    # Category 6: Ký tự lạ / encoding issues
    'special_chars': {
        'pattern': r'[®©™æœ¬̧̃±×÷§¶†‡•‰′″‴※‼⁇⁈⁉]',
        'description': 'Ký tự đặc biệt lạ (encoding issues)',
        'example': 'tæng sè tr©u'
    },
    'unicode_issues': {
        'pattern': r'[ằẳẵặắằẳẵặ]{2,}',
        'description': 'Unicode bị lỗi (dấu trùng)',
        'example': 'cbằ ao ng'
    },
    
    # Category 7: Chỉ là số (không phải location)
    'only_numbers': {
        'pattern': r'^\d+\.?\d*$',
        'description': 'Chỉ toàn số (không phải location)',
        'example': '125869.3', '14.585'
    },
    
    # Category 8: Chỉ là ký tự đơn
    'single_char': {
        'pattern': r'^[ivxIVX]+$',
        'description': 'Chỉ là chữ số La Mã hoặc ký tự đơn',
        'example': 'i', 'ii', 'iii', 'iv', 'v'
    },
    
    # Category 9: Typo / viết sai
    'typo_spacing': {
        'pattern': r'[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ][A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]',
        'description': 'Không có khoảng trắng giữa từ (viết liền)',
        'example': 'miềnnam', 'ngắnngày', 'trungbộ'
    },
    
    # Category 10: Chứa metadata (không phải location)
    'contains_metadata': {
        'pattern': r'(diện tích|năng suất|sản lượng|dt gieo|dt cho|1000\s*ha|tạ/ha)',
        'description': 'Chứa metadata (header/column names)',
        'example': 'diện tích', 'dt gieo trồng', 'năng suất'
    },
    
    # Category 11: Chứa nhiều location (danh sách)
    'location_list': {
        'pattern': r'([a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+\s){5,}',
        'description': 'Danh sách nhiều location',
        'example': 'hoa kỳ nhật bản trung quốc anh hàn quốc đức'
    }
}

print(f"✅ Defined {len(ERROR_PATTERNS)} error patterns")
for key, info in ERROR_PATTERNS.items():
    print(f"  - {key:25s}: {info['description']}")
print("=" * 100)


# ============================================================================
# DETECT ERRORS
# ============================================================================
print("\n" + "=" * 100)
print("🔍 DETECTING ERRORS IN LOCATION_NAME")
print("=" * 100)

if 'location_name' not in df_all.columns:
    print("❌ ERROR: 'location_name' column not found!")
    exit(1)

# Create error flags
for error_type, info in ERROR_PATTERNS.items():
    col_name = f'error_{error_type}'
    df_all[col_name] = df_all['location_name'].astype(str).str.contains(
        info['pattern'], 
        regex=True, 
        case=False,
        na=False
    )
    count = df_all[col_name].sum()
    pct = (count / len(df_all)) * 100
    print(f"{info['description']:50s}: {count:6,} ({pct:5.2f}%)")

# Create combined error flag
error_cols = [f'error_{key}' for key in ERROR_PATTERNS.keys()]
df_all['has_any_error'] = df_all[error_cols].any(axis=1)

total_errors = df_all['has_any_error'].sum()
print("-" * 100)
print(f"{'TOTAL RECORDS WITH ANY ERROR':50s}: {total_errors:6,} ({(total_errors/len(df_all))*100:5.2f}%)")
print("=" * 100)


# ============================================================================
# ERROR SUMMARY BY TYPE
# ============================================================================
print("\n" + "=" * 100)
print("📊 ERROR SUMMARY BY TYPE")
print("=" * 100)

error_summary = []
for error_type, info in ERROR_PATTERNS.items():
    col_name = f'error_{error_type}'
    count = df_all[col_name].sum()
    pct = (count / len(df_all)) * 100
    
    # Get sample
    samples = df_all[df_all[col_name]]['location_name'].unique()[:3]
    
    error_summary.append({
        'Error_Type': error_type,
        'Description': info['description'],
        'Count': count,
        'Percentage': round(pct, 2),
        'Sample_1': samples[0] if len(samples) > 0 else '',
        'Sample_2': samples[1] if len(samples) > 1 else '',
        'Sample_3': samples[2] if len(samples) > 2 else ''
    })

df_error_summary = pd.DataFrame(error_summary).sort_values('Count', ascending=False)
print(df_error_summary[['Error_Type', 'Description', 'Count', 'Percentage']].to_string(index=False))


# ============================================================================
# ERROR DISTRIBUTION BY YEAR-MONTH-APPENDIX
# ============================================================================
print("\n" + "=" * 100)
print("📍 ERROR DISTRIBUTION BY YEAR-MONTH-APPENDIX")
print("=" * 100)

errors_df = df_all[df_all['has_any_error']].copy()

# Group by year, month, appendix
error_distribution = errors_df.groupby(['year', 'month', 'appendix_number']).agg({
    'location_name': 'count',
    **{f'error_{key}': 'sum' for key in ERROR_PATTERNS.keys()}
}).reset_index()

error_distribution.rename(columns={'location_name': 'total_errors'}, inplace=True)

# Sort by total errors
error_distribution = error_distribution.sort_values('total_errors', ascending=False)

print(f"\nTop 30 Year-Month-Appendix combinations with most errors:")
print("-" * 100)
print(error_distribution.head(30).to_string(index=False))


# ============================================================================
# DETAILED ERROR RECORDS
# ============================================================================
print("\n" + "=" * 100)
print("📋 CREATING DETAILED ERROR REPORT")
print("=" * 100)

# Create detailed error report
error_records = errors_df[[
    'year', 'month', 'appendix_number', 'location_name', 
    'sector', 'commodity', 'sub_item', 'attribute', 'value'
] + error_cols].copy()

# Add error type summary column
def get_error_types(row):
    errors = []
    for error_type in ERROR_PATTERNS.keys():
        if row[f'error_{error_type}']:
            errors.append(error_type)
    return ', '.join(errors)

error_records['error_types'] = error_records.apply(get_error_types, axis=1)

# Sort by year, month, appendix
error_records = error_records.sort_values(['year', 'month', 'appendix_number', 'location_name'])

print(f"✅ Created detailed error report with {len(error_records):,} records")


# ============================================================================
# ERROR HOTSPOTS (Most problematic combinations)
# ============================================================================
print("\n" + "=" * 100)
print("🎯 ERROR HOTSPOTS ANALYSIS")
print("=" * 100)

# Find which year-month-appendix has highest error rate
hotspots = []
for (year, month, appendix), group in df_all.groupby(['year', 'month', 'appendix_number']):
    total = len(group)
    errors = group['has_any_error'].sum()
    error_rate = (errors / total * 100) if total > 0 else 0
    
    if errors > 0:
        # Count each error type
        error_breakdown = {}
        for error_type in ERROR_PATTERNS.keys():
            error_breakdown[error_type] = group[f'error_{error_type}'].sum()
        
        # Find most common error type
        most_common_error = max(error_breakdown.items(), key=lambda x: x[1])
        
        hotspots.append({
            'Year': year,
            'Month': month,
            'Appendix': appendix,
            'Total_Records': total,
            'Error_Records': errors,
            'Error_Rate_%': round(error_rate, 2),
            'Most_Common_Error': most_common_error[0],
            'Most_Common_Count': most_common_error[1]
        })

df_hotspots = pd.DataFrame(hotspots).sort_values('Error_Rate_%', ascending=False)

print("\nTop 30 hotspots (highest error rate):")
print("-" * 100)
print(df_hotspots.head(30).to_string(index=False))


# ============================================================================
# EXPORT RESULTS
# ============================================================================
print("\n" + "=" * 100)
print("💾 EXPORTING RESULTS")
print("=" * 100)

# 1. Error summary by type
summary_file = OUTPUT_DIR / "error_summary_by_type.csv"
df_error_summary.to_csv(summary_file, index=False, encoding='utf-8-sig')
print(f"✅ Exported error summary: {summary_file}")

# 2. Error distribution by year-month-appendix
distribution_file = OUTPUT_DIR / "error_distribution_by_source.csv"
error_distribution.to_csv(distribution_file, index=False, encoding='utf-8-sig')
print(f"✅ Exported error distribution: {distribution_file}")

# 3. Detailed error records
detailed_file = OUTPUT_DIR / "error_records_detailed.csv"
error_records.to_csv(detailed_file, index=False, encoding='utf-8-sig')
print(f"✅ Exported detailed error records: {detailed_file}")

# 4. Error hotspots
hotspots_file = OUTPUT_DIR / "error_hotspots.csv"
df_hotspots.to_csv(hotspots_file, index=False, encoding='utf-8-sig')
print(f"✅ Exported error hotspots: {hotspots_file}")

# 5. Unique error locations (for manual review)
unique_errors = errors_df['location_name'].unique()
unique_file = OUTPUT_DIR / "unique_error_locations.txt"
with open(unique_file, 'w', encoding='utf-8') as f:
    for i, loc in enumerate(sorted(unique_errors), 1):
        f.write(f"{i:4d}. {loc}\n")
print(f"✅ Exported unique error locations: {unique_file}")


# ============================================================================
# FINAL SUMMARY TABLE
# ============================================================================
print("\n" + "=" * 100)
print("📊 FINAL SUMMARY TABLE")
print("=" * 100)

summary_table = df_hotspots.head(20)[['Year', 'Month', 'Appendix', 'Error_Records', 'Error_Rate_%', 'Most_Common_Error']]
print("\nTop 20 sources to fix (prioritized by error rate):")
print("-" * 100)
print(summary_table.to_string(index=False))

print("\n" + "=" * 100)
print("✅ ANALYSIS COMPLETE!")
print("=" * 100)
print(f"\n📁 All results saved to: {OUTPUT_DIR}")
print("\n🎯 NEXT STEPS:")
print("  1. Review error_hotspots.csv to prioritize fixes")
print("  2. Check error_summary_by_type.csv to understand error patterns")
print("  3. Use error_records_detailed.csv to trace specific errors")
print("  4. Fix extraction logic for top hotspots first")
print("=" * 100)
