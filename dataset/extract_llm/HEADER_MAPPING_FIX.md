# Header Mapping Fix - Summary

## 🎯 **VẤN ĐỀ ĐÃ FIX:**

### **Problem 1: Duplicate Attributes**
**Trước:**
```json
// Cột 2: Diện tích gieo cấy lúa
{
  "commodity": "Lúa",
  "attribute": "Area_Planted",  // ✅
  "value": 933587
}

// Cột 3: Diện tích mạ đã gieo
{
  "commodity": "Lúa",
  "attribute": "Area_Planted",  // ❌ SAI! Phải là Area_Seedling
  "value": 29421
}
```

**Sau:**
```json
// Cột 2
{
  "commodity": "Lúa",
  "attribute": "Area_Planted",  // ✅
  "value": 933587
}

// Cột 3
{
  "commodity": "Lúa",
  "attribute": "Area_Seedling",  // ✅ ĐÚNG!
  "value": 29421
}
```

---

### **Problem 2: Aggregated Parent Columns**

**Bảng PL2 có cấu trúc hierarchical:**
```
| Location | Lúa | Mạ | Màu LT | Trong đó: | Trong đó: | Trong đó: |
|          |     |    |        | Ngô       | K.lang    | Sắn       |
| Miền Bắc | 933 | 29 | 206    | 139       | 17        | 24        |
```

**Trước:**
- ✅ Extract cột "Màu LT" (206) → Tổng
- ✅ Extract cột "Ngô" (139) → Chi tiết
- ❌ **Duplicate data!** (206 = 139 + 17 + 24)

**Sau:**
- ❌ **SKIP** cột "Màu LT" (aggregated parent)
- ✅ **KEEP** cột "Ngô", "K.lang", "Sắn" (chi tiết)
- ✅ Không duplicate!

---

## 🔧 **CÁC THAY ĐỔI:**

### **1. Added `Area_Seedling` Attribute**

```python
# In parse_header_for_commodity()
if "mạ" in header_lower or "mạ đã gieo" in header_lower:
    result["attribute"] = "Area_Seedling"
    result["commodity"] = "Lúa"  # Mạ is always for rice
```

**Handles:**
- "Diện tích mạ đã gieo" → Area_Seedling
- "Mạ" → Area_Seedling

---

### **2. Skip Aggregated Parent Columns**

```python
# Check if column has sub-columns
aggregated_commodities = [
    "màu lương thực", "cây màu",
    "công nghiệp ngắn ngày", "cây công nghiệp"
]

# If this column is parent of specific commodities → SKIP
if has_sub_columns:
    logger.debug(f"Skipped aggregated column: '{header}'")
    continue
```

**Logic:**
1. Detect if header contains aggregated commodity name
2. Check if next 4 columns have specific commodities (Ngô, Khoai lang, etc.)
3. If yes → This is parent column → **SKIP**
4. If no → This is standalone column → **KEEP**

---

## 📊 **EXPECTED RESULTS:**

### **For PL2 - Miền Bắc row:**

| Column | Header | Action | Reason |
|--------|--------|--------|--------|
| 2 | Diện tích gieo cấy lúa đông xuân | ✅ KEEP | Standalone column |
| 3 | Diện tích mạ đã gieo | ✅ KEEP | Standalone, Area_Seedling |
| 4 | Diện tích gieo trồng màu | ❌ SKIP | Has sub-columns (5-8) |
| 5 | Ngô | ✅ KEEP | Specific commodity |
| 6 | Khoai lang | ✅ KEEP | Specific commodity |
| 7 | Sắn | ✅ KEEP | Specific commodity |
| 8 | Cây khác | ✅ KEEP | Specific commodity |

**Records created:** 6 (not 7)

---

## ✅ **BENEFITS:**

1. ✅ **No duplicate data** - Tổng và chi tiết không bị trùng
2. ✅ **Correct attributes** - Mạ được map đúng thành Area_Seedling
3. ✅ **Granular data** - Chỉ giữ chi tiết (Ngô, Khoai lang...), không giữ tổng
4. ✅ **Flexible** - Dễ aggregate lại nếu cần

---

## 🧪 **TESTING:**

To test the fix:
```bash
cd /media/duongn/New\ Volume/UIT/aThacSy/Data\ Mining/2.\ Data\ Pre-processing/vn_agri_dts/dataset/extract_llm/scripts
python extract_data.py --year 2009 --month 2
```

Check output for:
- ✅ No "Màu lương thực" records (should be skipped)
- ✅ Has "Ngô", "Khoai lang", "Sắn" records
- ✅ "Mạ" records have `attribute: "Area_Seedling"`

---

**Date**: 2026-01-29  
**Status**: ✅ Implemented & Ready for Testing
