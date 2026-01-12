# 🌾 Vietnamese Agricultural Data Extraction Project

**Automated extraction of agricultural data from Vietnamese government reports (2009-2022)**

---

## 📋 Project Overview

This project extracts structured agricultural data from Vietnamese Ministry of Agriculture monthly reports. The data is converted from markdown-formatted tables into machine-learning-ready JSON format following a standardized schema.

### Key Features
- ✅ **Automated extraction** using Python scripts
- ✅ **Schema v2.0 compliant** with comprehensive contexts
- ✅ **Multi-sector support**: Cultivation, Fishery, Forestry, Trade, Investment
- ✅ **High quality**: 87% average extraction confidence
- ✅ **Multiple outputs**: JSON, CSV, validation reports

---

## 📊 Current Status

### Completed
- ✅ **Schema v2.0** designed and validated
- ✅ **February 2009** extraction complete (769 records)
- ✅ **9 extractors** implemented (PL1-PL9)
- ✅ **Validation tools** created

### In Progress
- ⏳ Processing remaining months (March-December 2009)
- ⏳ Improving Trade extractor (export/import detection)

### Planned
- 📅 Scale to 2010-2022
- 📅 Create consolidated annual datasets
- 📅 Build data mining pipeline

---

## 🗂️ Directory Structure

```
vn_agri_dts/
├── segments/                      # Source markdown files
│   └── 2009/
│       ├── 2009_02_PHULUC_t02_2009_FINAL_PL1.md
│       ├── 2009_02_PHULUC_t02_2009_FINAL_PL2.md
│       └── ... (124 files total)
│
├── dataset/
│   └── extract_llm/
│       └── 2009/
│           ├── extracted_data_2009_02.json    # Main output
│           ├── extracted_data_2009_02.csv     # CSV format
│           ├── validation_2009_02.txt         # Validation report
│           ├── EXTRACTION_SUMMARY.md          # Summary
│           └── COMPLETION_REPORT.md           # Detailed report
│
├── schema_improved.json           # Schema v2.0
├── extract_llm_2009_02.py        # Main extraction script
├── view_extracted_data.py        # Data viewer & validator
├── json_to_csv.py                # JSON to CSV converter
├── LLM_EXTRACTION_PROMPT.txt     # Extraction instructions
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python3 --version

# No external dependencies required (uses only standard library)
```

### Run Extraction
```bash
# Extract data for February 2009
python3 extract_llm_2009_02.py

# View and validate results
python3 view_extracted_data.py
```

### Output Files
After running, you'll find:
- `dataset/extract_llm/2009/extracted_data_2009_02.json` (1.0 MB)
- `dataset/extract_llm/2009/extracted_data_2009_02.csv` (120 KB)
- `dataset/extract_llm/2009/validation_2009_02.txt`

---

## 📖 Schema Overview

### Record Structure
Each record contains 7 main contexts:

```json
{
  "record_id": "unique_hash",
  "time_context": {
    "year": 2009,
    "month": 2,
    "report_date": "2009-02-15",
    "period_type": "Monthly"
  },
  "geo_context": {
    "geo_level": "Provincial",
    "location_name": "Long An",
    "region_id": "Mekong_Delta",
    "region_name_vn": "Đồng bằng sông Cửu Long"
  },
  "item_context": {
    "sector": "Cultivation",
    "commodity": "Lúa",
    "sub_item": "Đông Xuân",
    "variety": null,
    "processing_level": "Raw"
  },
  "metric_context": {
    "attribute": "Area_Planted",
    "value": 245962,
    "unit": "ha",
    "data_type": "Actual"
  },
  "comparison_context": {
    "comparison_type": "YoY",
    "comparison_value": 127.2,
    "base_period": "2008-02-15",
    "base_value": 193450
  },
  "metadata": {
    "source_file": "2009_02_PHULUC_t02_2009_FINAL_PL4.md",
    "appendix_number": "PL4",
    "extraction_method": "LLM_Extraction",
    "extraction_confidence": 0.85
  },
  "data_quality": {
    "is_aggregated": false,
    "has_missing_values": false,
    "data_status": "Complete"
  }
}
```

---

## 📊 Data Coverage

### February 2009 Statistics

| Sector | Records | Percentage |
|--------|---------|------------|
| Cultivation | 644 | 83.7% |
| Fishery | 44 | 5.7% |
| Trade | 40 | 5.2% |
| Investment | 26 | 3.4% |
| Forestry | 15 | 2.0% |
| **Total** | **769** | **100%** |

### Appendices Covered

| Code | Title | Records |
|------|-------|---------|
| PL1 | Tổng hợp sản xuất nông nghiệp | 20 |
| PL2 | Gieo cấy lúa - Miền Bắc | 177 |
| PL3 | Cây công nghiệp - Miền Bắc | 134 |
| PL4 | Gieo cấy lúa - Miền Nam | 160 |
| PL5 | Cây công nghiệp - Miền Nam | 153 |
| PL6 | Lâm nghiệp | 15 |
| PL7 | Thủy sản | 44 |
| PL8 | Xuất nhập khẩu | 40 |
| PL9 | Đầu tư XDCB | 26 |

---

## 🔧 Usage Examples

### Python - Load JSON
```python
import json

# Load data
with open('dataset/extract_llm/2009/extracted_data_2009_02.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Access records
records = data['records']
print(f"Total records: {len(records)}")

# Filter by sector
cultivation = [r for r in records if r['item_context']['sector'] == 'Cultivation']
print(f"Cultivation records: {len(cultivation)}")
```

### Python - Load CSV with Pandas
```python
import pandas as pd

# Load CSV
df = pd.read_csv('dataset/extract_llm/2009/extracted_data_2009_02.csv')

# Filter rice data
rice = df[df['commodity'] == 'Lúa']

# Group by location
by_location = rice.groupby('location_name')['value'].sum()
print(by_location.head())
```

### Python - Analyze by Sector
```python
import pandas as pd

df = pd.read_csv('dataset/extract_llm/2009/extracted_data_2009_02.csv')

# Count by sector
sector_counts = df['sector'].value_counts()
print(sector_counts)

# Calculate total area planted
cultivation = df[df['attribute'] == 'Area_Planted']
total_area = cultivation['value'].sum()
print(f"Total area planted: {total_area:,.0f} ha")
```

---

## 🛠️ Scripts Documentation

### 1. `extract_llm_2009_02.py`
Main extraction script with 6 extractor classes.

**Features:**
- Parses markdown tables
- Extracts data according to schema v2.0
- Generates JSON, CSV, and validation reports
- 87% average extraction confidence

**Usage:**
```bash
python3 extract_llm_2009_02.py
```

### 2. `view_extracted_data.py`
Data viewer and validator.

**Features:**
- Shows sample records by sector
- Validates against schema
- Generates statistics
- Checks data quality

**Usage:**
```bash
python3 view_extracted_data.py
```

### 3. `json_to_csv.py`
Converts JSON to CSV format.

**Features:**
- Flattens nested JSON structure
- Creates Excel-friendly CSV
- Preserves all key information

**Usage:**
```bash
python3 json_to_csv.py
```

---

## 📐 Schema Details

### Sectors
- **Cultivation**: Rice, corn, vegetables, industrial crops
- **Livestock**: Pigs, cattle, poultry (not in Feb 2009)
- **Fishery**: Catch, aquaculture, exports
- **Forestry**: Planting, care, harvesting
- **Trade**: Exports, imports
- **Investment**: Infrastructure investment
- **Pest**: Pest control (not in Feb 2009)
- **Reporting**: Metadata (skipped)

### Attributes
- **Area_Planted**: Diện tích gieo trồng
- **Area_Harvested**: Diện tích thu hoạch
- **Production**: Sản lượng
- **Yield**: Năng suất
- **Catch**: Khai thác
- **Aquaculture**: Nuôi trồng
- **Export_Volume**: Lượng xuất khẩu
- **Export_Value**: Giá trị xuất khẩu
- **Investment_Amount**: Vốn đầu tư

### Units
- **ha**: Hectare
- **1000_ha**: Thousand hectares
- **ton**: Metric ton
- **1000_ton**: Thousand metric tons
- **million_USD**: Million US dollars
- **billion_VND**: Billion Vietnamese dong
- **percent**: Percentage

---

## 🎯 Quality Metrics

### Extraction Confidence
- **High (90-100%)**: PL1, PL9
- **Medium-High (85-89%)**: PL2-7
- **Medium (80-84%)**: PL8

### Data Completeness
- **Complete**: 91.8%
- **Estimated**: 3.9%
- **Plan**: 2.6%
- **Cumulative**: 1.7%

### Validation
- ✅ 0 schema errors
- ✅ 0 constraint violations
- ✅ 100% unique record IDs

---

## ⚠️ Known Issues

### Minor Issues
1. **Location names in PL1** include row numbers
   - Impact: Low (0.5%)
   - Can be cleaned in post-processing

2. **Export/Import detection in PL8** needs improvement
   - Impact: Medium (40 records)
   - All currently marked as "Export"

3. **Unknown commodities** in 4 records
   - Impact: Low (0.5%)
   - Acceptable for now

---

## 🚀 Next Steps

### Short-term
1. ⏳ Process remaining months (March-December 2009)
2. ⏳ Improve Trade extractor
3. ⏳ Add comparison_context extraction

### Long-term
1. 📅 Scale to 2010-2022
2. 📅 Create consolidated datasets
3. 📅 Build data mining pipeline
4. 📅 Implement ML models

---

## 📚 Documentation

- **Schema**: `schema_improved.json`
- **Extraction Guide**: `LLM_EXTRACTION_PROMPT.txt`
- **Completion Report**: `dataset/extract_llm/2009/COMPLETION_REPORT.md`
- **Summary**: `dataset/extract_llm/2009/EXTRACTION_SUMMARY.md`

---

## 🤝 Contributing

This is a data mining project for academic purposes. The extraction scripts can be reused for other months/years with minimal modifications.

### To process a new month:
1. Update `year` and `month` in `extract_llm_2009_02.py`
2. Run the script
3. Validate results with `view_extracted_data.py`

---

## 📄 License

This project is for academic research purposes.

---

## 📞 Contact

For questions about the data or extraction process, refer to:
- Validation reports in `dataset/extract_llm/2009/`
- Source markdown files in `segments/2009/`

---

## 🎓 Citation

If you use this data in your research, please cite:
```
Vietnamese Agricultural Data Extraction Project
Data Mining Course, University of Information Technology
Year: 2026
Schema Version: 2.0
```

---

**Last Updated**: 2026-01-08  
**Status**: 🟢 Production Ready (February 2009)  
**Next Release**: March 2009 extraction
