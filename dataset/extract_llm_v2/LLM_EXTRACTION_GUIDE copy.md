# LLM EXTRACTION GUIDE
**Hướng dẫn chi tiết cho LLM extract dữ liệu nông nghiệp Việt Nam**

---

## 🎯 **MỤC TIÊU**
Extract dữ liệu từ markdown tables → JSON theo `schema_improved_v2.json`

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

**Action**:
- ✅ Lấy **cell đầu tiên** làm commodity name
- ✅ Bỏ qua cells trùng lặp
- ✅ Bắt đầu extract value từ cell **khác nhau đầu tiên**

**Logic**:
```
Row: [A, A, A, B, C, D]
→ commodity=A, values=[B, C, D]

Row: [A, A, B, C, D]
→ commodity=A, values=[B, C, D]
```

---

### **Rule 3.5: Bold/Italic Formatting**

**Pattern**: Text có formatting đặc biệt

**Examples**:
```markdown
|**Miền Bắc**|**86,558**|**237,953**|
|_103.5_|_86.85_|
```

**Action**:
- **Bold** (`**...**`) → Thường là **summary row** hoặc **regional total**
  - → geo_level="Regional" hoặc is_aggregated=true
- **Italic** (`_..._`) → Thường là **comparison value** (%)
  - → comparison_value=103.5

---

### **Rule 3.6: Mixed Number Formats**

**Pattern**: Số có formats khác nhau

**Examples**:
```markdown
|1,881.0|86,558|602.0|1507|
```

**Action**:
- ✅ Remove commas: `1,881.0` → `1881.0`
- ✅ Normalize decimals: `602.0` → `602` (nếu không cần decimal)
- ✅ Parse as float: `"1,881.0"` → `1881.0`

---

## 🎯 **BƯỚC 4: MAPPING ATTRIBUTES**

### **Rule 4.1: Action Verbs → Attributes**

**Pattern**: Tên chỉ tiêu chứa động từ

**Mapping**:
```markdown
"Gieo cấy" / "Gieo trồng" / "Gieo sạ" → attribute="Area_Planted"
"Thu hoạch" → attribute="Area_Harvested"
"Sản lượng" → attribute="Production"
"Năng suất" → attribute="Yield"
"Xuất khẩu" + "Lượng" → attribute="Export_Volume"
"Xuất khẩu" + "Giá trị" → attribute="Export_Value"
"Nhập khẩu" + "Lượng" → attribute="Import_Volume"
"Nhập khẩu" + "Giá trị" → attribute="Import_Value"
"Đầu tư" / "Kế hoạch" → attribute="Investment_Amount"
"Trồng rừng" → attribute="Forest_Area_Planted"
"Khai thác gỗ" → attribute="Wood_Volume"
```

**Example**:
```markdown
|** 1. Gieo cấy lúa đông xuân cả nước**|1000 ha|1,947.6|
→ commodity="Lúa", sub_item="Đông Xuân", attribute="Area_Planted"
```

---

### **Rule 4.2: Lượng vs Giá trị - CRITICAL!** 🚨

**Pattern**: Cột "Lượng" và "Giá trị" xen kẽ

**Example**:
```markdown
|Chỉ tiêu|Lượng 2010|Giá trị 2010|Lượng 2011|Giá trị 2011|
|Cà phê|143|201|100|175|
```

**Action**:
- ✅ Tạo **4 records riêng biệt** (KHÔNG merge!)
- ✅ Record 1: attribute="Export_Volume", value=143, year=2010
- ✅ Record 2: attribute="Export_Value", value=201, year=2010
- ✅ Record 3: attribute="Export_Volume", value=100, year=2011
- ✅ Record 4: attribute="Export_Value", value=175, year=2011

**❌ SAI**:
```json
{
  "commodity": "Cà phê",
  "value": [143, 201],  // SAI!
  "unit": ["1000_ton", "million_USD"]
}
```

---

### **Rule 4.3: Multi-Period Data** 🚨

**Pattern**: Nhiều time periods trong 1 table

**Example**:
```markdown
|Chỉ tiêu|TH 3 tháng 2008|TH 2 tháng 2009|Ư. TH tháng 3/09|Ư. TH 3 tháng 2009|
|Cà phê|682|444|189|634|
```

**Action**:
- ✅ Tạo **4 records** cho mỗi commodity (1 record/period)
- ✅ Parse period từ header:
  - "TH 3 tháng 2008" → year=2008, month=3, period_type="Cumulative"
  - "TH 2 tháng 2009" → year=2009, month=2, period_type="Cumulative"
  - "Ư. TH tháng 3/09" → year=2009, month=3, data_type="Estimated"
  - "Ư. TH 3 tháng 2009" → year=2009, month=3, period_type="Cumulative", data_type="Estimated"

---

### **Rule 4.4: Hierarchical TT Column**

**Pattern**: Cột "TT" (số thứ tự) có hierarchy

**Example**:
```markdown
|TT|Chỉ tiêu|Value|
|I|Tổng sản lượng|1028|
|1|Sản lượng khai thác|613|
|1.1|Khai thác biển|568|
|1.2|Khai thác nội địa|45|
|2|Sản lượng nuôi trồng|415|
```

**Action**:
- ✅ Parse hierarchy từ TT:
  - `I` → Level 1 (National summary)
  - `1` → Level 2 (Category)
  - `1.1` → Level 3 (Sub-category)
- ✅ Map to commodity/sub_item:
  - TT=`I` → commodity="Tổng sản lượng", is_aggregated=true
  - TT=`1.1` → commodity="Khai thác", sub_item="Khai thác biển"

---

## 📏 **BƯỚC 5: UNITS NORMALIZATION**

### **Rule 5.1: Normalize Units**

**Mapping**:
```markdown
INPUT UNIT → OUTPUT UNIT (conversion)

"ha" → "1000_ha" (÷ 1000)
"1000 ha" → "1000_ha" (giữ nguyên)
"tấn" / "Tấn" → "1000_ton" (÷ 1000)
"1000 tấn" / "1000 Tấn" → "1000_ton" (giữ nguyên)
"tấn/ha" → "ton_per_ha" (giữ nguyên)
"triệu USD" / "Triệu USD" → "million_USD" (giữ nguyên)
"USD" → "million_USD" (÷ 1,000,000)
"triệu đồng" / "Triệu VND" → "million_VND" (giữ nguyên)
"VND" → "million_VND" (÷ 1,000,000)
"1000 con" / "1000 heads" → "1000_heads" (giữ nguyên)
"m3" → "1000_m3" (÷ 1000)
"1000 m3" → "1000_m3" (giữ nguyên)
"%" → "percent" (giữ nguyên)
"triệu cây" → "million_trees" (giữ nguyên)
```

**Example**:
```markdown
|Đơn vị: ha|Value|
|86,558|

→ unit="1000_ha", value=86.558 (86558 ÷ 1000)
```

---

### **Rule 5.2: Detect Unit from Context**

**Pattern**: Unit không rõ ràng, phải đoán từ context

**Examples**:
```markdown
"Diện tích" → unit="1000_ha" (default for area)
"Sản lượng" → unit="1000_ton" (default for production)
"Kim ngạch" / "Giá trị" → unit="million_USD" (default for trade value)
"Lượng" (trong trade) → unit="1000_ton"
"Đầu tư" → unit="million_VND"
```

---

## � **BƯỚC 6: HIERARCHY & NESTED DATA**

### **Rule 6.1: Nested Categories**

**Pattern**: "Chia ra:", "Trong đó:", indentation

**Example**:
```markdown
|** 1. Gieo cấy lúa đông xuân cả nước**|1,881.0|
|Chia ra: - Miền Bắc|73.9|
|Trong đó: + Đồng bằng Sông Hồng|553.6|
|- Miền Nam|1,807.1|
|Trong đó: Đồng bằng sông Cửu Long|1,543.2|
```

**Action**:
- ✅ Tạo **5 records riêng biệt** (KHÔNG aggregate!)
- ✅ Detect hierarchy:
  - "Cả nước" → geo_level="National"
  - "Miền Bắc" / "Miền Nam" → geo_level="Regional"
  - "Đồng bằng..." → geo_level="Regional" (sub-region)
  - Province names → geo_level="Provincial"

**❌ SAI**: Không cộng: 73.9 + 1807.1 = 1881.0

---

### **Rule 6.2: Regional Summaries**

**Pattern**: Bold rows = summary

**Example**:
```markdown
|**Miền Bắc**|**1,097,635**|**274,166**|
|Hà Nội|99,791|8,076|
|Hải Phòng|49,688|2,796|
```

**Action**:
- ✅ "Miền Bắc" → geo_level="Regional", is_aggregated=true
- ✅ "Hà Nội" → geo_level="Provincial", is_aggregated=false

---

## 📊 **BƯỚC 7: COMPARISON DATA**

### **Rule 7.1: Extract Comparison Values**

**Pattern**: Cột "% so với...", values in italics

**Example**:
```markdown
|% so với|Col6|
|_DTGC_|_Cùng kỳ 2010_|
||**_103.5_**|
```

**Action**:
- ✅ Column header "% so với DTGC" → comparison_type="vs_Plan"
- ✅ Column header "% so với cùng kỳ" → comparison_type="YoY"
- ✅ Value `_103.5_` → comparison_value=103.5

**Mapping**:
```markdown
"DTGC" / "Kế hoạch" / "KH" → comparison_type="vs_Plan"
"Cùng kỳ" / "C.kỳ" → comparison_type="YoY"
"Tháng trước" → comparison_type="MoM"
```

---

## 🎯 **BƯỚC 8: SPECIAL CASES**

### **Rule 8.1: Unknown/Extra Columns**

**Pattern**: Cột không rõ nghĩa

**Example**:
```markdown
|Tổng số|Ngô|K.Lang|Sắn|Có củ #|
```

**Action**:
- ✅ "Có củ #" → commodity="Cây có củ khác" (best guess)
- ✅ Hoặc skip nếu không thể đoán

---

### **Rule 8.2: Merged Commodity + Sub-item**

**Pattern**: Commodity và sub-item trong cùng 1 cell

**Example**:
```markdown
|Mía (trồng mới)|54.1|
|Lúa đông xuân|1,947.6|
```

**Action**:
- ✅ Parse: "Mía (trồng mới)" → commodity="Mía", sub_item="Trồng mới"
- ✅ Parse: "Lúa đông xuân" → commodity="Lúa", sub_item="Đông Xuân"

---

### **Rule 8.3: Ditto Mark `"`**

**Pattern**: Dấu `"` = lặp lại giá trị trên

**Example**:
```markdown
|Đơn vị tính|Value|
|1000 ha|1,881.0|
|"|73.9|
|"|1,807.1|
```

**Action**:
- ✅ `"` → Copy value from cell above
- ✅ Row 2: unit="1000 ha" (same as row 1)

---

## ✅ **VALIDATION CHECKLIST**

Sau khi extract, kiểm tra:

- [ ] **Sector**: Đã xác định đúng từ title?
- [ ] **Multiple appendices**: Đã split nếu có nhiều phụ lục trong 1 file?
- [ ] **Lượng vs Giá trị**: Đã tách thành records riêng?
- [ ] **Multi-period**: Đã tạo records riêng cho mỗi period?
- [ ] **Units**: Đã normalize về 1000_ha, 1000_ton, million_USD?
- [ ] **Headers**: Đã merge multi-row headers đúng?
- [ ] **Nested data**: Đã tạo records riêng cho từng level (KHÔNG aggregate)?
- [ ] **Empty/Zero cells**: Đã phân biệt `0` vs empty?
- [ ] **Strikethrough**: Đã skip `~~text~~`?
- [ ] **Merged cells**: Đã split values có `<br>`?
- [ ] **Commodity duplication**: Đã deduplicate?
- [ ] **Comparison**: Đã extract % so sánh?
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

**Version**: 2.0  
**Last updated**: 2026-02-04  
**Changes**: Added comprehensive edge cases analysis and detection patterns
