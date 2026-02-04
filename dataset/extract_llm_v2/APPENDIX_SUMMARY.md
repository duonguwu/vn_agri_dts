# APPENDIX SUMMARY
**Tóm tắt đặc điểm từng phụ lục - Tháng 1/2011**

---

## PL1: TỔNG HỢP SẢN XUẤT NÔNG NGHIỆP
- **Rows**: 23 | **Complexity**: ⭐⭐⭐
- **Structure**: Summary table with hierarchy
- **Key features**:
  - Nested categories: "Chia ra:", "Trong đó:"
  - Action verbs: "Gieo cấy", "Thu hoạch"
  - Comparison columns: % vs DTGC, % vs cùng kỳ
- **Extraction notes**:
  - Parse action verbs → attribute mapping
  - Keep hierarchy (don't aggregate)
  - Extract comparison data

---

## PL2: GIEO CẤY LÚA + MÀU LƯƠNG THỰC (MIỀN BẮC)
- **Rows**: 47 | **Complexity**: ⭐⭐⭐⭐
- **Structure**: Provincial data, multi-row header
- **Key features**:
  - 3-row header with "Trong đó:"
  - Columns: Lúa ĐX, Màu LT, Ngô, Khoai lang, Sắn, Cây khác
  - Regional summaries (ĐB sông Hồng, TD và MN, Bắc Trung Bộ)
- **Extraction notes**:
  - Merge header rows: Row2 + Row3
  - Each column = separate record
  - Bold rows = regional summaries (geo_level="Regional")

---

## PL3: CÂY CÔNG NGHIỆP + RAU ĐẬU (MIỀN BẮC)
- **Rows**: 52 | **Complexity**: ⭐⭐⭐
- **Structure**: Similar to PL2, simpler header
- **Key features**:
  - 2-row header
  - Columns: CN ngắn ngày, Đậu tương, Lạc, Thuốc lá, Rau đậu
- **Extraction notes**:
  - Straightforward column mapping
  - Watch for empty cells

---

## PL4: THU HOẠCH LÚA MÙA + XUỐNG GIỐNG (MIỀN NAM)
- **Rows**: 59 | **Complexity**: ⭐⭐⭐⭐
- **Structure**: Multi-period data, complex header
- **Key features**:
  - 3-row header
  - Multiple time periods: "Thu hoạch lúa mùa 2010", "Lúa Đ.xuân 2011"
  - Columns: DT thu hoạch, % vs gieo cấy, DT gieo cấy, Màu LT
- **Extraction notes**:
  - Separate records for different time periods
  - Watch for % columns (comparison data)

---

## PL5: CÂY CN + RAU ĐẬU (MIỀN NAM) ⚠️ PHỨC TẠP
- **Rows**: 65 | **Complexity**: ⭐⭐⭐⭐⭐
- **Structure**: NHIỀU "Trong đó:", dễ nhầm lẫn
- **Key features**:
  - 3-row header
  - 9 cột "Trong đó:" liên tiếp
  - Columns: Tổng số, Đậu tương, Lạc, Vừng, Thuốc lá, Mía, Bông, Đay, Rau, Đậu
- **Extraction notes**:
  - **QUAN TRỌNG**: Map theo thứ tự cột, KHÔNG theo tên "Trong đó:"
  - Tạo record riêng cho mỗi commodity
  - Rau và Đậu là 2 columns riêng (không phải "Trong đó:")

---

## PL6: THỦY SẢN
- **Rows**: 23 | **Complexity**: ⭐
- **Structure**: Simple table
- **Key features**:
  - Hierarchy: Tổng → Khai thác → Nuôi trồng
  - Columns: Năm 2010, Tháng 01/2010, Tháng 01/2011, % so sánh
- **Extraction notes**:
  - Straightforward extraction
  - sector="Fishery"

---

## PL7: NHÀ MÁY ĐƯỜNG
- **Rows**: 53 | **Complexity**: ⭐⭐⭐⭐
- **Structure**: Cumulative data, Mía + Đường
- **Key features**:
  - Multi-period: "Đến 15/12", "Từ 15/12-15/1", "Lũy kế", "KH vụ"
  - 2 commodities: Mía, Đường (alternating columns)
  - Hierarchy: Miền → Nhà máy
- **Extraction notes**:
  - **QUAN TRỌNG**: Tách Mía vs Đường thành 2 records
  - Each period = separate record (or use data_type="Cumulative")
  - sector="Sugar_Production"

---

## PL8: ĐẦU TƯ XDCB
- **Rows**: 31 | **Complexity**: ⭐⭐
- **Structure**: Investment budget table
- **Key features**:
  - Hierarchy: Tổng → Sector (Thủy lợi, Nông nghiệp, Lâm nghiệp...)
  - Columns: KH năm 2011, Ước TH T1, Tỷ lệ %
- **Extraction notes**:
  - sector="Investment"
  - attribute="Investment_Amount"
  - unit="million_VND"

---

## PL9: XUẤT NHẬP KHẨU ⚠️ QUAN TRỌNG
- **Rows**: 50 | **Complexity**: ⭐⭐⭐⭐⭐
- **Structure**: Lượng + Giá trị (ALTERNATING COLUMNS)
- **Key features**:
  - 2 sections: Xuất khẩu, Nhập khẩu
  - Alternating columns: Lượng 2010, Giá trị 2010, Lượng 2011, Giá trị 2011
  - Nested categories: "Nông sản chính" → "Cà phê", "Cao su"...
- **Extraction notes**:
  - **CRITICAL**: Tách Lượng vs Giá trị thành 2 records
  - Lượng → attribute="Export_Volume" / "Import_Volume"
  - Giá trị → attribute="Export_Value" / "Import_Value"
  - **KHÔNG** tạo 1 record với 2 values!

---

## PL10a: COMPLIANCE MIỀN BẮC
- **Rows**: 57 | **Complexity**: ⭐
- **Structure**: Metadata table
- **Key features**:
  - Checkboxes (x) for compliance status
  - Text notes in "Nhận xét" column
- **Extraction notes**:
  - sector="Compliance"
  - Có thể skip hoặc extract minimal info

---

## PL10b: COMPLIANCE MIỀN NAM
- **Rows**: 63 | **Complexity**: ⭐
- **Structure**: Same as PL10a
- **Extraction notes**: Same as PL10a

---

## 📊 COMPLEXITY RANKING

1. **PL5** (⭐⭐⭐⭐⭐): Nhiều "Trong đó:", dễ nhầm lẫn
2. **PL9** (⭐⭐⭐⭐⭐): Lượng + Giá trị alternating
3. **PL2, PL4, PL7** (⭐⭐⭐⭐): Multi-row headers, multi-period
4. **PL1, PL3** (⭐⭐⭐): Nested categories
5. **PL8** (⭐⭐): Simple hierarchy
6. **PL6, PL10a/b** (⭐): Straightforward

---

## 🎯 PRIORITY FOR TESTING

Test extraction theo thứ tự:
1. **PL6** (easiest) - Validate basic extraction
2. **PL1** - Test nested categories
3. **PL2** - Test multi-row headers
4. **PL9** - Test Lượng/Giá trị separation
5. **PL5** - Test complex "Trong đó:"

---

## 📈 ESTIMATED RECORDS

| Phụ lục | Rows | Columns | Est. Records | Notes |
|---------|------|---------|--------------|-------|
| PL1 | 23 | 4 | ~50 | Nested hierarchy |
| PL2 | 47 | 7 | ~280 | Provincial × Commodities |
| PL3 | 52 | 6 | ~260 | Provincial × Commodities |
| PL4 | 59 | 10 | ~500 | Provincial × Multi-period |
| PL5 | 65 | 11 | ~650 | Provincial × Many commodities |
| PL6 | 23 | 4 | ~60 | Simple |
| PL7 | 53 | 10 | ~500 | Factories × Periods × 2 commodities |
| PL8 | 31 | 4 | ~100 | Sectors × Periods |
| PL9 | 50 | 7 | ~300 | Commodities × 2 attributes × 2 years |
| PL10a/b | 120 | - | ~0 | Metadata, skip |

**Total**: ~2,700 records/month

---

**Version**: 1.0  
**Last updated**: 2026-02-04
