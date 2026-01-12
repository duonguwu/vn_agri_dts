# ✅ Extraction Report - March 2009

**Extraction Date**: 2026-01-08  
**Status**: ✅ **COMPLETE**

---

## 📊 SUMMARY

- **Total Records**: 799
- **Files Processed**: 10/10 (100%)
- **Validation Errors**: 0
- **Schema Version**: 2.0

---

## 📈 RECORDS BY SECTOR

| Sector | Records | Percentage |
|--------|---------|------------|
| Cultivation | 712 | 89.1% |
| Trade | 43 | 5.4% |
| Investment | 26 | 3.3% |
| Forestry | 18 | 2.3% |
| **Total** | **799** | **100%** |

---

## 📋 RECORDS BY APPENDIX

| Appendix | Title | Records |
|----------|-------|---------|
| PL1 | Tổng hợp | 26 |
| PL2 | Lúa MB | 152 |
| PL3 | CN MB | 153 |
| PL4 | Lúa MN | 185 |
| PL5 | CN MN | 196 |
| PL6 | Lâm nghiệp | 18 |
| PL8 | XNK | 43 |
| PL9 | Đầu tư | 26 |

**Note**: PL7 (Thủy sản) không có trong tháng 3/2009

---

## 🌾 TOP COMMODITIES

1. **Lúa**: 629 records (78.7%)
2. **Rau**: 33 records (4.1%)
3. **Đậu**: 28 records (3.5%)
4. **Unknown**: 12 records (1.5%)
5. **Rừng**: 8 records (1.0%)

---

## 📁 OUTPUT FILES

```
dataset/extract_llm/2009/03/
├── extracted_data_2009_03.json    (1.1 MB)
├── extracted_data_2009_03.csv     (125 KB)
└── validation_2009_03.txt         (1.6 KB)
```

---

## ✅ QUALITY METRICS

- **Extraction Confidence**: 87% (average)
- **Data Completeness**: 100%
- **Schema Compliance**: ✅ Pass
- **Unique Record IDs**: ✅ Pass

---

## 🔄 COMPARISON WITH FEBRUARY 2009

| Metric | Feb 2009 | Mar 2009 | Change |
|--------|----------|----------|--------|
| Total Records | 769 | 799 | +30 (+3.9%) |
| Files Processed | 11 | 10 | -1 |
| Cultivation | 644 | 712 | +68 (+10.6%) |
| Fishery | 44 | 0 | -44 (N/A) |
| Trade | 40 | 43 | +3 (+7.5%) |
| Forestry | 15 | 18 | +3 (+20%) |
| Investment | 26 | 26 | 0 |

**Note**: PL7 (Fishery) không có trong tháng 3

---

## 📝 NOTES

- Tháng 3 không có PL7 (Thủy sản)
- Số lượng records tăng nhẹ so với tháng 2
- Cultivation vẫn chiếm tỷ trọng lớn nhất (89.1%)
- Chất lượng dữ liệu tương đương tháng 2

---

**Generated**: 2026-01-08 12:20:00  
**Script**: `extract_data.py`  
**Command**: `python3 extract_data.py 2009 3`
