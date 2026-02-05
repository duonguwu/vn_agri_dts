# LLM EXTRACTION GUIDE
**Hướng dẫn chi tiết cho LLM extract dữ liệu nông nghiệp Việt Nam**

---

## 🎯 **MỤC TIÊU**
Extract dữ liệu từ markdown tables → JSON theo `schema_improved_v2.json` (Optimized Format)

---

## 📋 **CẤU TRÚC PHỤ LỤC**

### **PL1: Tổng hợp sản xuất**
- **Đặc điểm**: Summary table, có hierarchy (Cả nước → Miền → Vùng)
- **Vấn đề**: 
  - Nested rows: "Chia ra:", "Trong đó:"
  - Action verbs: "Gieo cấy", "Thu hoạch"
- **Cách xử lý**:
  ```
  "** 1. Gieo cấy lúa đông xuân cả nước**" 
  → commodity="Lúa", sub_item="Đông Xuân", attribute="Area_Planted", location="Cả nước"
  
  "Chia ra: - Miền Bắc"
  → location="Miền Bắc" (child of "Cả nước")
  ```

### **PL2-4: Dữ liệu canh tác theo tỉnh**
- **Đặc điểm**: Multi-row headers, provincial data
- **Vấn đề**:
  - Header 3 dòng: Row1="Col1", Row2="DT gieo cấy", Row3="Ngô"
  - Merged cells
- **Cách xử lý**:
  ```markdown
  |Col1|DT màu lương thực|Trong đó:|Trong đó:|
  |---|---|---|---|
  ||DT màu lương thực|Ngô|Khoai lang|
  
  → Merge thành: ["Location", "DT màu lương thực", "Ngô", "Khoai lang"]
  ```

### **PL5: Cây công nghiệp + Rau đậu**
- **Đặc điểm**: Nhiều "Trong đó:", dễ nhầm lẫn
- **Vấn đề**: 
  - 9 cột "Trong đó:" liên tiếp
  - Header không rõ ràng
- **Cách xử lý**:
  ```markdown
  |Tổng số|Trong đó:|Trong đó:|Trong đó:|Rau các loại|Đậu các loại|
  |Tổng số|Đậu tương|Lạc|Vừng|...|...|
  
  → Map theo thứ tự cột: Col2=Đậu tương, Col3=Lạc, Col4=Vừng
  → Tạo 2 records riêng cho "Rau" và "Đậu"
  ```

### **PL6: Thủy sản**
- **Đặc điểm**: Simple table, ít vấn đề
- **Cách xử lý**: Straightforward, extract theo row

### **PL7: Nhà máy đường**
- **Đặc điểm**: Cumulative data, có hierarchy (Miền → Nhà máy)
- **Vấn đề**:
  - Multi-period columns: "Đến 15/12", "Từ 15/12-15/1", "Lũy kế"
  - Mía vs Đường (2 commodities khác nhau)
- **Cách xử lý**:
  ```markdown
  |Mía|Đường|
  |2,074,000|161,300|
  
  → Tạo 2 records:
  Record 1: commodity="Mía", value=2074000, unit="ton"
  Record 2: commodity="Đường", value=161300, unit="ton"
  ```

### **PL8: Đầu tư XDCB**
- **Đặc điểm**: Investment data, có hierarchy (Tổng → Sector)
- **Cách xử lý**: sector="Investment", attribute="Investment_Amount"

### **PL9: Xuất nhập khẩu** ⚠️ **QUAN TRỌNG**
- **Đặc điểm**: Lượng + Giá trị trong cùng 1 table
- **Vấn đề**: 
  - 2 cột liên tiếp: "Lượng" và "Giá trị"
  - Dễ nhầm lẫn nếu không đọc header kỹ
- **Cách xử lý**:
  ```markdown
  |Chỉ tiêu|Lượng|Giá trị|Lượng|Giá trị|
  |Cà phê|143|201|100|175|
  
  → Tạo 4 records:
  Record 1: attribute="Export_Volume", value=143, unit="1000_ton"
  Record 2: attribute="Export_Value", value=201, unit="million_USD"
  Record 3: attribute="Export_Volume", value=100, unit="1000_ton"
  Record 4: attribute="Export_Value", value=175, unit="million_USD"
  
  ⚠️ KHÔNG tạo 2 records với value=[143,201] - SAI!
  ```

### **PL10a/b: Compliance metadata**
- **Đặc điểm**: Metadata, không phải số liệu
- **Cách xử lý**: Skip

---

## 🚨 **EDGE CASES ĐẶC BIỆT**

### **1. Multiple Appendices trong 1 File** 🔴 CRITICAL
```markdown
DETECT:
_**Phụ lục 6**_
[Bảng 1...]
## **_Phụ lục 7_**
[Bảng 2...]

ACTION:
✅ Tách thành 2 records riêng với appendix_number khác nhau
✅ Đọc header ## **_Phụ lục X_** để xác định appendix_number
✅ Mỗi section có sector riêng biệt
```

### **2. Merged Cells với <br> trong Data** 🔴 CRITICAL
```markdown
DETECT:
|**21,547**<br>**7,082**|
|81,171<br>|

ACTION:
✅ Nếu cell có <br> với 2 values → Tách thành 2 records
✅ Nếu cell có <br> trailing (81,171<br>) → Remove <br>
✅ Kiểm tra header để xác định 2 values thuộc columns nào
```

### **3. Strikethrough Text ~~...~~** 🟡 MEDIUM
```markdown
DETECT:
|~~Hà Giang~~|~~5,899~~|~~7,544~~|

ACTION:
⚠️ Option 1: SKIP rows có ~~text~~
⚠️ Option 2: Extract nhưng đánh dấu data_status="Cancelled"
✅ Recommended: Skip để tránh dữ liệu sai
```

### **4. Commodity Name Duplication** 🟡 MEDIUM
```markdown
DETECT:
|Quế|Quế|Quế||2.1|2.1|2.1|
|Thức ăn gia súc|Thức ăn gia súc|516||148|

ACTION:
✅ Nếu 2-3 cells đầu giống nhau → Lấy cell đầu làm commodity
✅ Bỏ qua cells trùng lặp
✅ Bắt đầu extract value từ cell khác nhau đầu tiên
```

### **5. Zero vs Empty vs Missing Cells** 🟢 LOW
```markdown
DETECT:
|Thừa Thiên Huế|0||3,741|  // 0, empty, value
|Hà Nội|||5,200|           // empty, empty, value

ACTION:
✅ 0 = valid value → Tạo record với value=0
✅ `` (empty) = skip column
✅ || (missing) = skip column
✅ Phân biệt rõ: 0 ≠ empty ≠ missing
```

### **6. Encoding Errors** 🟡 MEDIUM
```markdown
DETECT:
**b¸o c¸o t×nh h×nh thùc hiÖn**
**mét sè chØ tiªu l©m nghiÖp**

ACTION:
✅ LLM cần robust với lỗi encoding
✅ Dùng context để đoán: "b¸o c¸o" = "báo cáo"
✅ Hoặc skip title, chỉ extract data từ table
```

### **7. Multi-Period Trade Data (4+ Periods)** 🔴 CRITICAL
```markdown
DETECT:
|Chỉ tiêu|TH 3T-2008|Col3|TH 2T-2009|Col5|Ư.TH T3/09|Col7|Ư.TH 3T-2009|Col9|
|Chỉ tiêu|Lượng|Giá trị|Lượng|Giá trị|Lượng|Giá trị|Lượng|Giá trị|

ACTION:
✅ Tạo 8 records cho mỗi commodity (4 periods × 2 attributes)
✅ Map period patterns:
  - "TH 3 tháng 2008" → year=2008, period_type="Cumulative", month=3
  - "TH 2 tháng 2009" → year=2009, period_type="Cumulative", month=2  
  - "Ư. TH tháng 3/09" → year=2009, data_type="Estimated", month=3
  - "Ư. TH 3 tháng 2009" → year=2009, data_type="Estimated", period_type="Cumulative"
```

### **8. Appendix Number KHÔNG Consistent** 🔴 CRITICAL
```markdown
PROBLEM:
- PL9 (2009) = Đầu tư XDCB (Investment)
- PL9 (2011) = Xuất nhập khẩu (Trade)
→ Số thứ tự phụ lục THAY ĐỔI giữa các năm!

ACTION:
⚠️ KHÔNG dùng appendix_number để xác định sector
✅ Đọc title của phụ lục để xác định sector:
  - "XUẤT NHẬP KHẨU" → sector="Trade"
  - "ĐTXDCB" / "ĐẦU TƯ" → sector="Investment"  
  - "THUỶ SẢN" → sector="Fishery"
  - "LÂM NGHIỆP" → sector="Forestry"
  - "GIEO CẤY" / "THU HOẠCH" → sector="Cultivation"
```

### **9. Hierarchical TT Column** 🟡 MEDIUM
```markdown
DETECT:
|TT|CHỈ TIÊU|Value|
|I|**Tổng sản lượng**|668|
|1|**Sản lượng khai thác**|383|
|1.1|Khai thác biển|363|
|1.2|Khai thác nội địa|20|

ACTION:
✅ Parse TT column để xác định hierarchy:
  - I, II, III = Level 1 (Main category)
  - 1, 2, 3 = Level 2 (Sub-category)  
  - 1.1, 1.2 = Level 3 (Detail)
✅ Tạo separate records cho mỗi level
✅ Không aggregate (giữ nguyên hierarchy)
```

### **10. Extra Unknown Columns** 🟢 LOW
```markdown
DETECT:
|Tổng số|Ngô|K.Lang|Sắn|Có củ #|  // "Có củ #" không rõ nghĩa

ACTION:
✅ Option 1: Map based on context - "Có củ #" → "Cây có củ khác"
✅ Option 2: Skip nếu không rõ nghĩa
✅ Recommended: Map nếu có context, skip nếu không chắc
```

### **11. Mixed Formatting in Cells** 🟢 LOW
```markdown
DETECT:
|602.0|1,234|5,678.50|  // Mixed decimal formats

ACTION:
✅ Normalize numbers: 602.0 → 602, 1,234 → 1234
✅ Remove trailing <br>: 81,171<br> → 81,171
✅ Handle thousands separator: 1,234 → 1234
```

---

## 🔧 **QUY TẮC XỬ LÝ**

### **1. Multi-row Headers**
```markdown
BEFORE:
|Col1|Col2|Trong đó:|Trong đó:|
|---|---|---|---|
||DT màu|Ngô|Khoai lang|

AFTER (merged):
["Location", "DT màu", "Ngô", "Khoai lang"]
```

**Logic**:
- Row 1 có "Trong đó:" → Placeholder, lấy từ Row 2
- Row 2 có tên cụ thể → Dùng làm column name
- Merge từ dưới lên trên

### **2. Nested Categories**
```markdown
|** 1. Gieo cấy lúa đông xuân cả nước**|1000 ha|1,881.0|
|Chia ra: - Miền Bắc|"|73.9|
|Trong đó: Đồng bằng sông Cửu Long|"|1,495.3|
```

**Hierarchy**:
- Level 1: "Cả nước" (National)
- Level 2: "Miền Bắc" (Regional) - child of "Cả nước"
- Level 3: "Đồng bằng sông Cửu Long" (Regional) - child of "Miền Nam"

**Extract**:
- Tạo 3 records riêng biệt
- Không aggregate (giữ nguyên hierarchy)

### **3. Action Verbs**
```markdown
|** 1. Gieo cấy lúa đông xuân cả nước**|
|** 2. Thu hoạch lúa mùa miền Nam**|
```

**Mapping**:
- "Gieo cấy" / "Gieo trồng" → attribute="Area_Planted"
- "Thu hoạch" → attribute="Area_Harvested"
- "Sản lượng" → attribute="Production"
- "Năng suất" → attribute="Yield"

### **4. Units Normalization**
```markdown
|Đơn vị tính|Value in table|
|1000 ha|1,881.0|
|ha|86,558|
```

**Normalize**:
- "1000 ha" → unit="1000_ha", value=1881.0 (giữ nguyên)
- "ha" → unit="1000_ha", value=86.558 (chia 1000)
- "tấn" → unit="1000_ton", value=X/1000
- "triệu USD" → unit="million_USD" (giữ nguyên)

### **5. Comparison Data**
```markdown
|% 15/01/11 so với|Col6|
|_DTGC(*)_|_15/01/2010_|
||**_103.5_**|
```

**Extract**:
- Column "% so với DTGC" → comparison_type="vs_Plan"
- Column "% so với 15/01/2010" → comparison_type="YoY"
- Value in italics (_103.5_) → comparison_value=103.5

### **6. Empty Cells**
```markdown
|Hà Nội||17,638|13,428|
```

**Xử lý**:
- Empty cell → Skip column (không tạo record)
- Không tạo record với value=null

### **7. Merged Cells (visual)**
```markdown
|**Miền Bắc**|**86,558**|**237,953**|
```

**Detect**:
- Bold text (**...**) thường là summary row
- Tạo record với geo_level="Regional"

---

## 📊 **EXAMPLES**

### **Example 1: PL1 - Simple extraction**
```markdown
INPUT:
|** 1. Gieo cấy lúa đông xuân cả nước**|1000 ha|**1,881.0**|**1,947.6**||**_103.5_**|

OUTPUT:
{
  "commodity": "Lúa",
  "sub_item": "Đông Xuân",
  "attribute": "Area_Planted",
  "value": 1947.6,
  "unit": "1000_ha",
  "location_name": "Cả nước",
  "geo_level": "National",
  "year": 2011,
  "month": 1,
  "data_type": "Actual",
  "comparison_context": {
    "comparison_type": "YoY",
    "comparison_value": 103.5,
    "base_value": 1881.0
  }
}
```

### **Example 2: PL9 - Lượng + Giá trị** ⚠️
```markdown
INPUT:
|Cà phê|143|201|100|175|_69.72_|_86.85_|

HEADER:
|Chỉ tiêu|Lượng 2010|Giá trị 2010|Lượng 2011|Giá trị 2011|% Lượng|% Giá trị|

OUTPUT (4 records):
Record 1: {
  "commodity": "Cà phê",
  "attribute": "Export_Volume",
  "value": 143,
  "unit": "1000_ton",
  "year": 2010,
  "data_type": "Actual"
}

Record 2: {
  "commodity": "Cà phê",
  "attribute": "Export_Value",
  "value": 201,
  "unit": "million_USD",
  "year": 2010,
  "data_type": "Actual"
}

Record 3: {
  "commodity": "Cà phê",
  "attribute": "Export_Volume",
  "value": 100,
  "unit": "1000_ton",
  "year": 2011,
  "data_type": "Actual",
  "comparison_context": {
    "comparison_type": "YoY",
    "comparison_value": 69.72
  }
}

Record 4: {
  "commodity": "Cà phê",
  "attribute": "Export_Value",
  "value": 175,
  "unit": "million_USD",
  "year": 2011,
  "data_type": "Actual",
  "comparison_context": {
    "comparison_type": "YoY",
    "comparison_value": 86.85
  }
}
```

### **Example 3: PL5 - Nhiều "Trong đó:"**
```markdown
INPUT:
|**Miền Nam**|**66,857**|**664**|**19,205**|**1,224**|**6,281**|**39,032**|**327**|**124**|**100,358**|**12,734**|

HEADER (3 rows):
Row 1: |Col1|Tổng số|Trong đó:|Trong đó:|Trong đó:|Trong đó:|Trong đó:|Trong đó:|Trong đó:|Rau|Đậu|
Row 2: ||Tổng số|Đậu tương|Lạc|Vừng|Thuốc lá|Mía|Bông|Đay|...|...|
Row 3: Same as Row 2

OUTPUT (9 records):
Record 1: commodity="Cây CN ngắn ngày", value=66857, location="Miền Nam"
Record 2: commodity="Đậu tương", value=664, location="Miền Nam"
Record 3: commodity="Lạc", value=19205, location="Miền Nam"
Record 4: commodity="Vừng", value=1224, location="Miền Nam"
Record 5: commodity="Thuốc lá", value=6281, location="Miền Nam"
Record 6: commodity="Mía", sub_item="Trồng mới", value=39032, location="Miền Nam"
Record 7: commodity="Bông", value=327, location="Miền Nam"
Record 8: commodity="Đay/Lác", value=124, location="Miền Nam"
Record 9: commodity="Rau các loại", value=100358, location="Miền Nam"
Record 10: commodity="Đậu các loại", value=12734, location="Miền Nam"
```

---

## 🎯 **DETECTION PATTERNS**

### **Tự động phát hiện Edge Cases**

```markdown
PATTERN 1: Multiple Appendices
IF file contains "## **_Phụ lục" more than once
→ Split into separate processing

PATTERN 2: Merged Data Cells  
IF cell contains "<br>" with numbers on both sides
→ Split values

PATTERN 3: Cancelled Data
IF cell contains "~~text~~"  
→ Skip or mark as cancelled

PATTERN 4: Duplicate Commodity Names
IF first 2-3 cells in row are identical
→ Deduplicate, use first occurrence

PATTERN 5: Multi-Period Headers
IF header contains "TH", "Ước TH", multiple years
→ Create separate records per period

PATTERN 6: Hierarchical Numbering
IF first column contains "I", "1", "1.1" pattern
→ Parse hierarchy levels

PATTERN 7: Encoding Issues
IF text contains "¸", "×", "Ö", "è" patterns
→ Apply encoding correction or use context
```

### **Sector Detection từ Title**

```markdown
TITLE PATTERNS → SECTOR MAPPING:

"XUẤT KHẨU" | "NHẬP KHẨU" | "KIM NGẠCH" → "Trade"
"ĐẦU TƯ" | "XDCB" | "VỐN" → "Investment"  
"THUỶ SẢN" | "KHAI THÁC" | "NUÔI TRỒNG" → "Fishery"
"LÂM NGHIỆP" | "TRỒNG RỪNG" | "GỖ" → "Forestry"
"GIEO CẤY" | "THU HOẠCH" | "SẢN XUẤT" → "Cultivation"
"CHĂN NUÔI" | "GIA SÚC" | "GIA CẦM" → "Livestock"
"DỊCH HẠI" | "BỆNH" → "Pest"
```

---

## ⚠️ **COMMON MISTAKES**

### **Mistake 1: Không tách Lượng vs Giá trị**
```markdown
❌ WRONG:
{
  "commodity": "Cà phê",
  "value": [143, 201],  // SAI! Đây là 2 attributes khác nhau
  "unit": ["1000_ton", "million_USD"]
}

✅ CORRECT:
// Tạo 2 records riêng biệt
Record 1: attribute="Export_Volume", value=143
Record 2: attribute="Export_Value", value=201
```

### **Mistake 2: Nhầm lẫn "Trong đó:"**
```markdown
❌ WRONG:
{
  "commodity": "Trong đó",  // SAI!
  "value": 19205
}

✅ CORRECT:
{
  "commodity": "Lạc",  // Lấy từ row 2 của header
  "value": 19205
}
```

### **Mistake 3: Không normalize units**
```markdown
❌ WRONG:
{
  "value": 86558,
  "unit": "ha"  // SAI! Cần normalize
}

✅ CORRECT:
{
  "value": 86.558,
  "unit": "1000_ha"
}
```

### **Mistake 4: Aggregate nested data**
```markdown
❌ WRONG:
{
  "location": "Cả nước",
  "value": 1881.0 + 73.9 + 1807.1  // SAI! Không cộng
}

✅ CORRECT:
// Tạo 3 records riêng
Record 1: location="Cả nước", value=1881.0
Record 2: location="Miền Bắc", value=73.9
Record 3: location="Miền Nam", value=1807.1
```

---

## 🎯 **VALIDATION CHECKLIST**

Sau khi extract, kiểm tra:

### **Core Validation**
- [ ] **Lượng vs Giá trị**: Đã tách thành 2 records riêng?
- [ ] **Units**: Đã normalize về 1000_ha, 1000_ton, million_USD?
- [ ] **Headers**: Đã merge multi-row headers đúng?
- [ ] **Nested data**: Đã tạo records riêng cho từng level?
- [ ] **Empty cells**: Đã skip?
- [ ] **Comparison**: Đã extract % so sánh?
- [ ] **Location**: Đã map đúng geo_level (National/Regional/Provincial)?
- [ ] **Commodity**: Đã extract từ action verb (Gieo cấy → Lúa)?

### **Edge Cases Validation**
- [ ] **Multiple Appendices**: Đã detect và tách riêng?
- [ ] **Merged Cells**: Đã split values có <br>?
- [ ] **Strikethrough**: Đã skip ~~text~~?
- [ ] **Duplicate Names**: Đã deduplicate commodity names?
- [ ] **Zero Values**: Đã phân biệt 0 vs empty vs missing?
- [ ] **Multi-Period**: Đã tạo records riêng cho mỗi period?
- [ ] **Sector Detection**: Đã dùng title thay vì appendix_number?
- [ ] **Hierarchy**: Đã parse TT column (I.1.1) đúng?
- [ ] **Encoding**: Đã handle lỗi encoding?
- [ ] **Unknown Columns**: Đã map hoặc skip hợp lý?

---

## 📝 **NOTES**

1. **Ưu tiên accuracy > speed**: Đọc kỹ header trước khi extract
2. **Context matters**: Cùng 1 số nhưng khác attribute (Lượng vs Giá trị)
3. **Hierarchy**: Giữ nguyên, không aggregate
4. **Units**: Luôn normalize về cùng hệ thống
5. **Empty cells**: Skip, không tạo null records

---

## 🚀 **WORKFLOW**

### **Phase 1: Pre-Processing**
1. **Detect Multiple Appendices**: Scan for "## **_Phụ lục" patterns
2. **Split if needed**: Tách file thành sections riêng biệt
3. **Identify Sector**: Dùng title để xác định sector (KHÔNG dùng appendix_number)
4. **Check Encoding**: Detect và fix lỗi encoding nếu có

### **Phase 2: Header Processing**  
5. **Merge Multi-row Headers**: Combine rows có "Trong đó:"
6. **Detect Edge Cases**: Check for <br>, ~~text~~, duplicates
7. **Map Columns**: Column → attribute mapping
8. **Identify Periods**: Parse time periods từ headers

### **Phase 3: Data Extraction**
9. **Loop Rows**: Process từng row
10. **Handle Special Cases**: Apply edge case rules
11. **Create Records**: 1 cell = 1 record (trừ empty/cancelled)
12. **Apply Hierarchy**: Parse TT column nếu có

### **Phase 4: Post-Processing**
13. **Normalize Units**: Convert về standard units
14. **Validate**: Check theo expanded checklist  
15. **Quality Check**: Verify data_status, comparison_context
16. **Output**: JSON array theo schema

---

## 📊 **PRIORITY MATRIX**

| Edge Case | Frequency | Impact | Priority |
|-----------|-----------|---------|----------|
| Multiple Appendices | LOW | HIGH | 🔴 CRITICAL |
| Merged Cells <br> | MEDIUM | HIGH | 🔴 CRITICAL |
| Multi-Period Trade | LOW | HIGH | 🔴 CRITICAL |
| Inconsistent Appendix# | HIGH | HIGH | 🔴 CRITICAL |
| Strikethrough Text | LOW | MEDIUM | 🟡 MEDIUM |
| Commodity Duplication | MEDIUM | MEDIUM | 🟡 MEDIUM |
| Hierarchical TT | MEDIUM | MEDIUM | 🟡 MEDIUM |
| Encoding Errors | LOW | MEDIUM | 🟡 MEDIUM |
| Zero vs Empty | HIGH | LOW | 🟢 LOW |
| Unknown Columns | LOW | LOW | 🟢 LOW |
| Mixed Formatting | HIGH | LOW | 🟢 LOW |

### **Implementation Order**
1. **🔴 CRITICAL**: Implement first - high impact on data quality
2. **🟡 MEDIUM**: Implement second - moderate impact  
3. **🟢 LOW**: Implement last - minor impact, can be handled gracefully

---

**Version**: 2.1
**Last updated**: 2026-02-05
**Changes**: Added Compacted Tables (<br>), Mixed Content strategies, and Unit Context Awareness.

---

## 🏗️ **ADVANCED STRATEGIES (v2.1)**

### **12. Compacted Tables (Dữ liệu bị nén bằng <br>)** 🔴 CRITICAL
```markdown
DETECT:
|**Miền Nam**<br>**D.H Nam Trg Bộ**<br>TP Đà Nẵng...|**372,693**<br>**82,970**<br>1,195...|
|---|---|
| (Chỉ có 1 dòng dữ liệu chứa toàn bộ thông tin về tên tỉnh và số liệu) | |

PROBLEM:
- Bảng Markdown bị nén thành 1 dòng duy nhất, các giá trị ngăn cách bởi thẻ <br>.
- Các cột dữ liệu thưa (sparse columns) có số lượng phần tử KHÔNG KHỚP với cột tên tỉnh (do các ô trống bị bỏ qua hoặc gộp).
- Regex thông thường sẽ lệch index.

ACTION:
✅ **Tuyệt đối không dùng Regex** để đoán vị trí.
✅ **Xác định cột neo (Anchor Columns):** Thường là cột Tên Tỉnh và cột Tổng Số (Total) vì chúng luôn đầy đủ dữ liệu.
✅ **Manual Transcription (Copy-Paste thông minh) - "Hard-code is okay":**
  - Đối với các cột thưa (ít số liệu), hãy copy nguyên chuỗi raw string từ `view_file` vào Python script dưới dạng list string `data = "123<br>456".split("<br>")`.
  - Dùng mắt thường (khi view file) để mapping thủ công nếu cần thiết cho các cột quan trọng.
✅ **Safety First:** Nếu không chắc chắn về sự thẳng hàng (alignment) của các cột thưa, hãy **BỎ QUA** các cột đó và chỉ extract cột neo (Tổng số). Thà thiếu dữ liệu chi tiết còn hơn sai lệch gán số liệu tỉnh này sang tỉnh kia.
```

### **13. Mixed Content Tables (Bảng hỗn hợp Nam/Bắc)** 🟡 MEDIUM
```markdown
DETECT:
File PL6 chứa cả:
- Bảng Lâm Nghiệp Miền Bắc
- Bảng Lâm Nghiệp Miền Nam
(Nối tiếp nhau trong cùng 1 file, không tách thành Appendix riêng)

ACTION:
✅ Đọc tuần tự từ trên xuống.
✅ Khi gặp keyword chuyển vùng (VD: "Miền Nam", "II. Các tỉnh phía Nam"), reset hoặc cập nhật biến `current_region_context`.
✅ Combine dữ liệu từ cả 2 phần vào chung một Json output nếu chúng cùng schema.
```

### **14. Unit Context Awareness (Ngữ cảnh đơn vị)** 🟢 LOW
```markdown
DETECT:
Header: "Giá trị sản xuất (Giá CĐ 1994)"
Unit ghi trong bảng: "Tr.Đồng" (Triệu đồng)
Value: 7,356 (cho cả nước)

ANALYSIS:
- Cả nước không thể chỉ làm ra 7 tỷ đồng (7,356 triệu) cho toàn ngành Lâm nghiệp.
- Năm 1994 giá trị nhỏ hơn hiện tại, nhưng quy mô quốc gia thường tính bằng Tỷ đồng.
- Context check: So sánh với năm trước hoặc logic kinh tế.

ACTION:
✅ Nếu nghi ngờ đơn vị quy mô quá nhỏ so với thực tế (National Level), hãy kiểm tra khả năng là Tỷ đồng hoặc quy đổi sai.
✅ **Safe bet:** Map unit theo đúng text trong bảng (million_VND) nhưng note lại hoặc nếu chắc chắn (như GDP) thì map sang billion_VND. Với datasets này, ưu tiên giữ nguyên text unit nếu không sure.
```
