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

- [ ] **Lượng vs Giá trị**: Đã tách thành 2 records riêng?
- [ ] **Units**: Đã normalize về 1000_ha, 1000_ton, million_USD?
- [ ] **Headers**: Đã merge multi-row headers đúng?
- [ ] **Nested data**: Đã tạo records riêng cho từng level?
- [ ] **Empty cells**: Đã skip?
- [ ] **Comparison**: Đã extract % so sánh?
- [ ] **Location**: Đã map đúng geo_level (National/Regional/Provincial)?
- [ ] **Commodity**: Đã extract từ action verb (Gieo cấy → Lúa)?

---

## 📝 **NOTES**

1. **Ưu tiên accuracy > speed**: Đọc kỹ header trước khi extract
2. **Context matters**: Cùng 1 số nhưng khác attribute (Lượng vs Giá trị)
3. **Hierarchy**: Giữ nguyên, không aggregate
4. **Units**: Luôn normalize về cùng hệ thống
5. **Empty cells**: Skip, không tạo null records

---

## 🚀 **WORKFLOW**

1. **Đọc header**: Merge multi-row headers
2. **Identify columns**: Map column → attribute
3. **Extract rows**: Loop qua từng row
4. **Create records**: 1 cell = 1 record (trừ empty)
5. **Validate**: Check theo checklist
6. **Output**: JSON array theo schema

---

**Version**: 1.0  
**Last updated**: 2026-02-04
