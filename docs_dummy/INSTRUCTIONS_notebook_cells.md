# 📋 HƯỚNG DẪN: Thêm các ô phân tích Location_Name vào Notebook

## Copy các ô code sau vào notebook của bạn (sau phần "12. Recommendations"):

---

## ✅ Ô 1: Markdown Header

```markdown
## 13. 🔍 DEEP DIVE: Location_Name Error Analysis

### Logic kiểm tra lỗi:
1. **Số thứ tự ở đầu**: Pattern `^\d+\.\s` (ví dụ: "1. Gieo cấy...")
2. **Dấu ngoặc rỗng**: Pattern `\(\)` (ví dụ: "Gieo trồng màu lương thực()")
3. **Dấu ngoặc mở không đóng**: Pattern `\([^)]*$` (ví dụ: "Cây công nghiệp(")
4. **Số xuất hiện trong text**: Pattern `\d+` không phải ở đầu
5. **Khoảng trắng thừa**: Leading/trailing spaces, multiple spaces
6. **Ký tự đặc biệt lạ**: Tab, newline, special unicode characters
```

---

## ✅ Ô 2: Comprehensive Error Detection

```python
# Comprehensive location_name error detection
print("=" * 100)
print("🔍 COMPREHENSIVE LOCATION_NAME ERROR DETECTION")
print("=" * 100)

if 'location_name' in df_all.columns:
    # Create error flags for different types
    df_all['error_number_prefix'] = df_all['location_name'].astype(str).str.match(r'^\d+\.\s')
    df_all['error_empty_parens'] = df_all['location_name'].astype(str).str.contains(r'\(\)', regex=True)
    df_all['error_unclosed_parens'] = df_all['location_name'].astype(str).str.contains(r'\([^)]*$', regex=True)
    df_all['error_has_numbers'] = df_all['location_name'].astype(str).str.contains(r'\d', regex=True)
    df_all['error_leading_space'] = df_all['location_name'].astype(str).str.match(r'^\s')
    df_all['error_trailing_space'] = df_all['location_name'].astype(str).str.match(r'.*\s$')
    df_all['error_multiple_spaces'] = df_all['location_name'].astype(str).str.contains(r'\s{2,}', regex=True)
    
    # Count each error type
    error_counts = {
        'Số thứ tự ở đầu (1., 2., ...)': df_all['error_number_prefix'].sum(),
        'Dấu ngoặc rỗng ()': df_all['error_empty_parens'].sum(),
        'Dấu ngoặc không đóng (': df_all['error_unclosed_parens'].sum(),
        'Có chứa số': df_all['error_has_numbers'].sum(),
        'Khoảng trắng đầu': df_all['error_leading_space'].sum(),
        'Khoảng trắng cuối': df_all['error_trailing_space'].sum(),
        'Nhiều khoảng trắng liên tiếp': df_all['error_multiple_spaces'].sum()
    }
    
    print("\n📊 ERROR TYPE BREAKDOWN:")
    print("-" * 100)
    for error_type, count in error_counts.items():
        pct = (count / len(df_all)) * 100
        print(f"{error_type:40s}: {count:6,} records ({pct:5.2f}%)")
    
    # Any error
    df_all['has_any_location_error'] = (
        df_all['error_number_prefix'] | 
        df_all['error_empty_parens'] | 
        df_all['error_unclosed_parens'] | 
        df_all['error_leading_space'] | 
        df_all['error_trailing_space'] | 
        df_all['error_multiple_spaces']
    )
    
    total_errors = df_all['has_any_location_error'].sum()
    print("-" * 100)
    print(f"{'TOTAL RECORDS WITH ANY ERROR':40s}: {total_errors:6,} records ({(total_errors/len(df_all))*100:5.2f}%)")
    print("=" * 100)
else:
    print("⚠️ 'location_name' column not found")
```

---

## ✅ Ô 3: Sample Errors by Type

```python
# Show samples for each error type
print("=" * 100)
print("📋 SAMPLE ERRORS BY TYPE")
print("=" * 100)

if 'location_name' in df_all.columns:
    # 1. Number prefix errors
    if df_all['error_number_prefix'].sum() > 0:
        print("\n1️⃣ SỐ THỨ TỰ Ở ĐẦU (Top 10):")
        print("-" * 100)
        samples = df_all[df_all['error_number_prefix']][['year', 'month', 'location_name', 'appendix_number']].head(10)
        for idx, row in samples.iterrows():
            print(f"  [{row['year']}-{row['month']:02d}] [{row['appendix_number']}] {row['location_name']}")
    
    # 2. Empty parentheses
    if df_all['error_empty_parens'].sum() > 0:
        print("\n2️⃣ DẤU NGOẶC RỖNG () (Top 10):")
        print("-" * 100)
        samples = df_all[df_all['error_empty_parens']][['year', 'month', 'location_name', 'appendix_number']].head(10)
        for idx, row in samples.iterrows():
            print(f"  [{row['year']}-{row['month']:02d}] [{row['appendix_number']}] {row['location_name']}")
    
    # 3. Unclosed parentheses
    if df_all['error_unclosed_parens'].sum() > 0:
        print("\n3️⃣ DẤU NGOẶC KHÔNG ĐÓNG ( (Top 10):")
        print("-" * 100)
        samples = df_all[df_all['error_unclosed_parens']][['year', 'month', 'location_name', 'appendix_number']].head(10)
        for idx, row in samples.iterrows():
            print(f"  [{row['year']}-{row['month']:02d}] [{row['appendix_number']}] {row['location_name']}")
    
    # 4. Multiple spaces
    if df_all['error_multiple_spaces'].sum() > 0:
        print("\n4️⃣ NHIỀU KHOẢNG TRẮNG LIÊN TIẾP (Top 10):")
        print("-" * 100)
        samples = df_all[df_all['error_multiple_spaces']][['year', 'month', 'location_name', 'appendix_number']].head(10)
        for idx, row in samples.iterrows():
            print(f"  [{row['year']}-{row['month']:02d}] [{row['appendix_number']}] '{row['location_name']}'")

print("\n" + "=" * 100)
```

---

## ✅ Ô 4: Error Distribution Analysis

```python
# Error distribution by year, month, appendix
print("=" * 100)
print("📊 ERROR DISTRIBUTION ANALYSIS")
print("=" * 100)

if 'has_any_location_error' in df_all.columns and df_all['has_any_location_error'].sum() > 0:
    errors_df = df_all[df_all['has_any_location_error']]
    
    # By year
    print("\n📅 ERRORS BY YEAR:")
    print("-" * 100)
    error_by_year = errors_df.groupby('year').size()
    total_by_year = df_all.groupby('year').size()
    error_pct = (error_by_year / total_by_year * 100).round(2)
    
    for year in sorted(df_all['year'].unique()):
        err_count = error_by_year.get(year, 0)
        total = total_by_year.get(year, 0)
        pct = error_pct.get(year, 0)
        print(f"  {year}: {err_count:4,} / {total:6,} records ({pct:5.2f}%)")
    
    # By month
    print("\n📆 ERRORS BY MONTH:")
    print("-" * 100)
    error_by_month = errors_df.groupby('month').size().sort_index()
    total_by_month = df_all.groupby('month').size()
    
    for month in sorted(df_all['month'].unique()):
        err_count = error_by_month.get(month, 0)
        total = total_by_month.get(month, 0)
        pct = (err_count / total * 100) if total > 0 else 0
        print(f"  Month {month:2d}: {err_count:4,} / {total:6,} records ({pct:5.2f}%)")
    
    # By appendix
    print("\n📑 ERRORS BY APPENDIX (Top 20):")
    print("-" * 100)
    error_by_appendix = errors_df['appendix_number'].value_counts().head(20)
    
    for appendix, count in error_by_appendix.items():
        total = (df_all['appendix_number'] == appendix).sum()
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {appendix:10s}: {count:4,} / {total:6,} records ({pct:5.2f}%)")

print("\n" + "=" * 100)
```

---

## ✅ Ô 5: Error Hotspots

```python
# Identify which year-month-appendix combinations have most errors
print("=" * 100)
print("🎯 ERROR HOTSPOTS (Year-Month-Appendix combinations with most errors)")
print("=" * 100)

if 'has_any_location_error' in df_all.columns and df_all['has_any_location_error'].sum() > 0:
    errors_df = df_all[df_all['has_any_location_error']]
    
    # Group by year, month, appendix
    hotspots = errors_df.groupby(['year', 'month', 'appendix_number']).size().sort_values(ascending=False)
    
    print("\nTop 30 combinations with most errors:")
    print("-" * 100)
    print(f"{'Year':6s} {'Month':6s} {'Appendix':12s} {'Errors':8s} {'% of Total'}")
    print("-" * 100)
    
    for (year, month, appendix), count in hotspots.head(30).items():
        # Get total records for this combination
        total = len(df_all[(df_all['year'] == year) & 
                           (df_all['month'] == month) & 
                           (df_all['appendix_number'] == appendix)])
        pct = (count / total * 100) if total > 0 else 0
        print(f"{year:6d} {month:6d} {appendix:12s} {count:8,} {pct:6.2f}%")
    
    print("\n" + "=" * 100)
    print("💡 TIP: Focus on fixing these hotspots first for maximum impact!")
    print("=" * 100)
```

---

## ✅ Ô 6: Export Detailed Error Report

```python
# Export detailed error report
print("=" * 100)
print("💾 EXPORTING DETAILED LOCATION_NAME ERROR REPORT")
print("=" * 100)

if 'has_any_location_error' in df_all.columns and df_all['has_any_location_error'].sum() > 0:
    output_dir = Path(r"D:\UIT\aThacSy\Data Mining\2. Data Pre-processing\vn_agri_dts\dataset\extract_llm\error_analysis")
    output_dir.mkdir(exist_ok=True)
    
    # Export all location_name errors with error type flags
    error_columns = [
        'year', 'month', 'appendix_number', 'location_name', 'sector', 'commodity',
        'error_number_prefix', 'error_empty_parens', 'error_unclosed_parens',
        'error_leading_space', 'error_trailing_space', 'error_multiple_spaces'
    ]
    
    errors_export = df_all[df_all['has_any_location_error']][error_columns]
    error_file = output_dir / "location_name_errors_detailed.csv"
    errors_export.to_csv(error_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ Exported {len(errors_export):,} error records to:")
    print(f"   {error_file}")
    
    # Export summary by error type
    summary_data = []
    for error_col in ['error_number_prefix', 'error_empty_parens', 'error_unclosed_parens',
                      'error_leading_space', 'error_trailing_space', 'error_multiple_spaces']:
        error_type = error_col.replace('error_', '').replace('_', ' ').title()
        count = df_all[error_col].sum()
        pct = (count / len(df_all)) * 100
        summary_data.append({
            'Error_Type': error_type,
            'Count': count,
            'Percentage': round(pct, 2)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = output_dir / "location_name_error_summary.csv"
    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ Exported error summary to:")
    print(f"   {summary_file}")
    
    print("\n" + "=" * 100)
else:
    print("No location_name errors found to export.")
```

---

## 🎯 Hoặc chạy trực tiếp file Python:

Nếu không muốn copy từng ô, bạn có thể chạy trực tiếp file `eda_location_name_analysis.py` trong một ô notebook:

```python
%run eda_location_name_analysis.py
```

---

## 📊 Kết quả mong đợi:

Sau khi chạy, bạn sẽ có:

1. **Phân tích chi tiết 7 loại lỗi** trong location_name
2. **Samples cụ thể** cho từng loại lỗi
3. **Phân bố lỗi** theo năm, tháng, phụ lục
4. **Hotspots** - các combination có nhiều lỗi nhất
5. **2 file CSV export**:
   - `location_name_errors_detailed.csv` - tất cả records có lỗi
   - `location_name_error_summary.csv` - tổng hợp theo loại lỗi
