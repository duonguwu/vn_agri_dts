# 🛠️ Extraction Scripts

This folder contains scripts for extracting agricultural data from markdown segments.

---

## 📜 SCRIPTS

### `extract_data.py`
Main extraction script with support for all appendix types (PL1-PL9).

**Usage:**
```bash
# Extract specific month
python3 extract_data.py <year> <month>

# Examples
python3 extract_data.py 2009 2   # February 2009
python3 extract_data.py 2009 3   # March 2009
python3 extract_data.py 2009 4   # April 2009
```

**Features:**
- ✅ 6 extractor classes (PL1, PL2-5, PL6, PL8, PL9)
- ✅ Schema v2.0 compliant
- ✅ Automatic validation
- ✅ Multiple output formats (JSON, CSV, TXT)
- ✅ Command-line arguments

**Output:**
```
dataset/extract_llm/<year>/<month>/
├── extracted_data_<year>_<month>.json
├── extracted_data_<year>_<month>.csv
└── validation_<year>_<month>.txt
```

---

## 🎯 SUPPORTED APPENDICES

| Code | Extractor | Description |
|------|-----------|-------------|
| PL1 | `PL1Extractor` | Tổng hợp sản xuất nông nghiệp |
| PL2-5 | `CultivationExtractor` | Gieo cấy lúa và cây công nghiệp |
| PL6 | `ForestryExtractor` | Lâm nghiệp |
| PL7 | *(Skipped)* | Thủy sản (not in all months) |
| PL8 | `TradeExtractor` | Xuất nhập khẩu |
| PL9 | `InvestmentExtractor` | Đầu tư XDCB |
| PL10a/b | *(Skipped)* | Báo cáo chấp hành |

---

## 📊 EXTRACTION RESULTS

### February 2009
- **Records**: 769
- **Files**: 11
- **Sectors**: Cultivation (644), Fishery (44), Trade (40), Investment (26), Forestry (15)

### March 2009
- **Records**: 799
- **Files**: 10
- **Sectors**: Cultivation (712), Trade (43), Investment (26), Forestry (18)

---

## 🔧 TECHNICAL DETAILS

### Dependencies
- Python 3.8+
- Standard library only (no external packages)

### Key Functions
- `parse_markdown_table()`: Parse markdown tables
- `clean_number()`: Clean and convert numbers
- `generate_record_id()`: Generate unique IDs
- `extract_from_file()`: Route to appropriate extractor

### Extractors
Each extractor class has:
- `extract(content, metadata)`: Main extraction method
- Returns: `List[Dict]` of records

---

## 📝 NOTES

### Known Limitations
1. **PL7 (Fishery)**: Not available in all months
2. **Export/Import**: Currently all marked as "Export" in PL8
3. **Comparison data**: Not fully extracted yet

### Future Improvements
- [ ] Add FisheryExtractor for months with PL7
- [ ] Improve Trade extractor (export vs import)
- [ ] Extract comparison_context data
- [ ] Add data quality checks

---

## 🚀 QUICK START

```bash
# Navigate to project root
cd "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts"

# Extract March 2009
python3 dataset/extract_llm/scripts/extract_data.py 2009 3

# Check results
ls -lh dataset/extract_llm/2009/03/
cat dataset/extract_llm/2009/03/validation_2009_03.txt
```

---

## 📖 DOCUMENTATION

- **Schema**: `schema_improved.json`
- **Prompt**: `LLM_EXTRACTION_PROMPT.txt`
- **Results**: `dataset/extract_llm/<year>/<month>/`

---

**Last Updated**: 2026-01-08  
**Version**: 1.0  
**Status**: ✅ Production Ready
