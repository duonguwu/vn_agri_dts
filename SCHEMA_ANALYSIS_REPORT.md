# SCHEMA ANALYSIS REPORT
**Phân tích và đề xuất cải tiến Schema cho dự án Vietnamese Agricultural Data**

---

## 📊 **TỔNG QUAN DỮ LIỆU**

### **Files đã phân tích:**
- ✅ `2009/PHULUC_t02_2009_FINAL.md` - 542 dòng, ~23KB
- ✅ `2010/Phuluc_06_2010.md` - 1,020 dòng, ~66KB
- ✅ `2011/Phuluc_04_2011_f.md` - 958 dòng, ~45KB
- ✅ `2012/Phuluc_02_2012.md` - 750 dòng, ~39KB

**Tổng cộng**: 4 năm, 4 tháng khác nhau, ~173KB dữ liệu

---

## 🔍 **PHÁT HIỆN QUAN TRỌNG**

### **1. Cấu trúc phụ lục (Appendix Structure)**

#### **Nhất quán qua các năm:**
| Phụ lục | Nội dung | Sector | Đặc điểm |
|---------|----------|--------|----------|
| **PL1** | Tổng hợp sản xuất nông nghiệp | Cultivation | Summary table, có action verbs |
| **PL2-5** | Dữ liệu canh tác theo tỉnh | Cultivation | Provincial data, multi-row headers |
| **PL6** | Lâm nghiệp | Forestry | Kế hoạch vs thực hiện |
| **PL7** | Thủy sản | Fishery | Sản lượng khai thác + nuôi trồng |
| **PL8** | Xuất nhập khẩu | Trade | Lượng + giá trị |
| **PL9** | Thị trường xuất khẩu | Trade | Top 10 markets |
| **PL10** | Báo cáo compliance | Compliance | Metadata |

#### **Thay đổi theo năm:**
- **2010**: Có PL2a, PL2b (chia nhỏ hơn)
- **2011**: Có thêm PL11, PL12, PL13 (chi tiết hơn)
- **2012**: Quay lại cấu trúc đơn giản

### **2. Vấn đề với bảng (Table Issues)**

#### **🔴 Multi-row headers:**
```markdown
|Col1|Col2|Col3|Col4|Đơn vị tính: ha|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
||Diện tích gieo cấy lúa đông xuân|Diện tích mạ đã gieo|Diện tích gieo trồng màu|_Trong đó:_|_Trong đó:_|_Trong đó:_|_Trong đó:_|
||Diện tích gieo cấy lúa đông xuân|Diện tích mạ đã gieo|Diện tích gieo trồng màu|Ngô|Khoai lang|Sắn|Cây khác|
```
**→ Cần logic để merge 2-3 dòng header thành 1**

#### **🔴 Merged cells:**
```markdown
|**Miền Bắc**|**933,587**|**29,421**|**206,367**|**139,010**|**16,964**|**24,054**|**27,996**|
```
**→ Cells bị merge, cần detect và xử lý**

#### **🔴 Nested categories:**
```markdown
|** 1. Gieo cấy lúa đông xuân cả nước**|1000 ha|**2,180.5**|**2,773.9**||**_127.2_**|
|Chia ra:  + Miền Bắc|"|424.2|933.6||_220.1_|
|Trong đó: - Vùng Đồng bằng sông Hồng|"|83.4|447.0||_536.0_|
```
**→ Cần parse hierarchy: Cả nước → Miền Bắc → Đồng bằng sông Hồng**

### **3. Đơn vị không nhất quán**

| Năm | Đơn vị diện tích | Đơn vị sản lượng | Đơn vị giá trị |
|-----|------------------|------------------|----------------|
| 2009 | 1000 ha | - | triệu USD |
| 2010 | ha | 1000 tấn | triệu USD |
| 2011 | ha | 1000 tấn | 1.000 USD |
| 2012 | ha | 1000 tấn | triệu USD |

**→ Cần normalize về cùng đơn vị: `1000_ha`, `1000_ton`, `million_USD`**

### **4. Encoding issues**

**2010** có nhiều lỗi encoding:
```markdown
**b¸o c¸o t×nh h×nh thùc hiÖn**
**mét sè chØ tiªu l©m nghiÖp th¸ng 2 n¨m 2009**
```

**→ Cần pre-processing để fix encoding trước khi extract**

---

## 📋 **SO SÁNH SCHEMA CŨ VS MỚI**

### **Schema cũ (`schema_final.json`):**

#### ✅ **Điểm mạnh:**
- Cấu trúc rõ ràng, chia thành contexts
- Có constraints cho các fields quan trọng
- Đơn giản, dễ hiểu

#### 🔴 **Thiếu sót:**
1. **Không có `comparison_context`** - nhưng output đang dùng!
2. **Không có `data_quality`** - nhưng output đang dùng!
3. **Không có `period_type`** trong `time_context`
4. **`sector` enum thiếu** 3 loại: Investment, Compliance, Sugar_Production
5. **`attribute` không có enum** - khó validate
6. **`unit` không có enum** - dễ bị inconsistent
7. **Không có `region_name_vn`** - cần cho bilingual support

### **Schema mới (`schema_improved_v2.json`):**

#### ✅ **Cải tiến:**
1. ✅ **Thêm `comparison_context`** với đầy đủ fields
2. ✅ **Thêm `data_quality`** context
3. ✅ **Thêm `period_type`** vào `time_context`
4. ✅ **Mở rộng `sector` enum** (+3 loại mới)
5. ✅ **Thêm `attribute` enum** (17 loại attributes)
6. ✅ **Thêm `unit` enum** (15 loại units chuẩn)
7. ✅ **Thêm `region_name_vn`** cho bilingual
8. ✅ **Thêm `validation_rules`** để enforce data quality
9. ✅ **Thêm `required` flags** cho tất cả fields

---

## 🎯 **ĐỀ XUẤT HÀNH ĐỘNG**

### **Bước 1: Verify Schema mới**
- [ ] Review `schema_improved_v2.json`
- [ ] Kiểm tra xem có thiếu field nào không
- [ ] Thêm/bớt enum values nếu cần

### **Bước 2: Chuẩn bị dữ liệu**
- [ ] Fix encoding issues (đặc biệt 2010)
- [ ] Normalize units về cùng hệ thống
- [ ] Clean markdown formatting

### **Bước 3: Tạo LLM Extraction Prompt**
- [ ] Prompt chi tiết cho từng loại phụ lục
- [ ] Include schema trong prompt
- [ ] Hướng dẫn xử lý multi-row headers
- [ ] Hướng dẫn xử lý nested categories

### **Bước 4: Implement Extraction**
- [ ] Tạo script Python gọi Claude API
- [ ] Process từng file markdown (1 request/tháng)
- [ ] Validate output theo schema
- [ ] Save JSON + CSV

### **Bước 5: Quality Check**
- [ ] So sánh với output hiện tại
- [ ] Kiểm tra số lượng records
- [ ] Validate data quality
- [ ] Fix errors nếu có

---

## 📈 **PHÂN TÍCH CHI PHÍ API**

### **Ước tính cho toàn bộ dự án:**

#### **Dữ liệu:**
- **Số năm**: 2009-2012 = 4 năm
- **Số tháng/năm**: ~11 tháng (không phải tất cả tháng đều có)
- **Tổng số files**: ~44 files

#### **Token estimate:**
- **Input**: ~40KB/file × 44 files = ~1.76MB ≈ **440K tokens**
- **Output**: ~20KB JSON/file × 44 files = ~880KB ≈ **220K tokens**
- **Tổng**: ~660K tokens

#### **Chi phí (Claude 3.5 Sonnet):**
- Input: $3/million tokens × 0.44M = **$1.32**
- Output: $15/million tokens × 0.22M = **$3.30**
- **Tổng**: ~**$4.62** cho toàn bộ dự án

**→ RẤT RẺ! Hoàn toàn khả thi!**

---

## 🚨 **VẤN ĐỀ CẦN GIẢI QUYẾT TRƯỚC KHI EXTRACT**

### **1. Encoding Issues (Ưu tiên cao)**
File 2010 có nhiều lỗi encoding:
```
b¸o c¸o → báo cáo
§¬n vÞ → Đơn vị
```

**Giải pháp:**
- Re-convert PDF → Markdown với encoding đúng
- Hoặc dùng LLM để fix (Claude rất giỏi việc này)

### **2. Multi-row Headers (Ưu tiên cao)**
Cần hướng dẫn LLM cách merge headers:
```
Row 1: |Col1|Col2|Col3|Trong đó:|Trong đó:|
Row 2: |Col1|Col2|Col3|Ngô|Khoai lang|

→ Merged: |Col1|Col2|Col3|Ngô|Khoai lang|
```

### **3. Nested Categories (Ưu tiên trung bình)**
Cần extract hierarchy:
```
"Gieo cấy lúa đông xuân cả nước" → location="Cả nước"
"Chia ra: + Miền Bắc" → location="Miền Bắc", parent="Cả nước"
```

### **4. Unit Normalization (Ưu tiên trung bình)**
Cần convert tất cả về cùng hệ:
```
"ha" → "1000_ha" (chia cho 1000)
"tấn" → "1000_ton" (chia cho 1000)
```

---

## 💡 **GỢI Ý TIẾP THEO**

### **Option A: Fix Encoding trước**
1. Re-convert file 2010 với encoding đúng
2. Hoặc dùng script Python để fix encoding
3. Sau đó mới extract

### **Option B: Dùng LLM luôn**
1. LLM (Claude) rất giỏi xử lý encoding issues
2. Có thể fix encoding + extract cùng lúc
3. Tiết kiệm thời gian

### **Option C: Hybrid**
1. Fix encoding cho files có vấn đề
2. Dùng LLM extract cho tất cả
3. Validate và clean sau

---

## 🎯 **KHUYẾN NGHỊ**

### **Mình đề xuất:**

1. **Dùng Schema mới** (`schema_improved_v2.json`)
   - Đầy đủ hơn, có validation rules
   - Support comparison và data quality tracking

2. **Dùng LLM extraction** với file markdown lớn
   - 1 request/tháng thay vì 11 requests/tháng
   - Tiết kiệm ~40% chi phí
   - Context tốt hơn

3. **Để LLM xử lý encoding issues**
   - Claude rất giỏi việc này
   - Không cần re-convert PDF

4. **Tạo validation script**
   - Validate output theo schema mới
   - Detect và report errors
   - Auto-fix một số lỗi đơn giản

---

## 📝 **CHECKLIST TRƯỚC KHI BẮT ĐẦU**

- [ ] Review và approve `schema_improved_v2.json`
- [ ] Quyết định: Fix encoding hay để LLM xử lý?
- [ ] Quyết định: Dùng file segment hay file markdown lớn?
- [ ] Tạo LLM extraction prompt
- [ ] Tạo Python script gọi API
- [ ] Test với 1 file trước
- [ ] Validate kết quả
- [ ] Scale lên toàn bộ dataset

---

## 🚀 **BƯỚC TIẾP THEO**

**Bạn muốn mình làm gì tiếp?**

1. **Tạo LLM extraction prompt** chi tiết?
2. **Viết Python script** để gọi Claude API?
3. **Fix encoding issues** cho file 2010?
4. **Test extraction** với 1 file mẫu?
5. **Cải tiến schema** thêm nữa?

Cho mình biết bạn muốn ưu tiên gì nhé! 💪
