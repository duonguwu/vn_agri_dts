# 📊 PHÂN TÍCH VÀ ĐỀ XUẤT TRÍCH XUẤT DỮ LIỆU NÔNG NGHIỆP

**Ngày tạo:** 2026-01-08  
**Phiên bản:** 1.0  
**Tác giả:** Data Mining Team

---

## 📋 MỤC LỤC

1. [Tổng quan dữ liệu](#1-tổng-quan-dữ-liệu)
2. [Đánh giá Schema hiện tại](#2-đánh-giá-schema-hiện-tại)
3. [Schema cải thiện](#3-schema-cải-thiện)
4. [Phương pháp trích xuất](#4-phương-pháp-trích-xuất)
5. [Hướng dẫn sử dụng](#5-hướng-dẫn-sử-dụng)
6. [Kết luận và đề xuất](#6-kết-luận-và-đề-xuất)

---

## 1. TỔNG QUAN DỮ LIỆU

### 1.1. Cấu trúc file hiện tại

```
vn_agri_dts/
├── markdown_output/2009/
│   └── PHULUC_t02_2009_FINAL.md (file gốc - 543 dòng)
└── segments/2009/
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL1.md   (31 dòng)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL2.md   (55 dòng)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL3.md   (46 dòng)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL4.md   (57 dòng)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL5.md
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL6.md   (Lâm nghiệp)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL7.md   (Thủy sản)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL8.md   (Xuất nhập khẩu)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL9.md   (Đầu tư XDCB)
    ├── 2009_02_PHULUC_t02_2009_FINAL_PL10a.md (Báo cáo - Miền Bắc)
    └── 2009_02_PHULUC_t02_2009_FINAL_PL10b.md (Báo cáo - Miền Nam)
```

### 1.2. Các loại dữ liệu trong phụ lục

| Phụ lục | Nội dung | Loại dữ liệu | Độ phức tạp |
|---------|----------|--------------|-------------|
| **PL1** | Tổng hợp kết quả sản xuất nông nghiệp | Cultivation (tổng hợp) | ⭐⭐ |
| **PL2** | Gieo cấy lúa và màu lương thực - Miền Bắc | Cultivation (chi tiết theo tỉnh) | ⭐⭐⭐ |
| **PL3** | Diện tích gieo trồng cây CN ngắn ngày - Miền Bắc | Cultivation (cây công nghiệp) | ⭐⭐⭐ |
| **PL4** | Gieo cấy lúa đông xuân - Miền Nam | Cultivation (chi tiết theo tỉnh) | ⭐⭐⭐ |
| **PL5** | Diện tích gieo trồng cây CN - Miền Nam | Cultivation (cây công nghiệp) | ⭐⭐⭐ |
| **PL6** | Thực hiện chỉ tiêu lâm nghiệp | Forestry | ⭐⭐⭐⭐ |
| **PL7** | Kết quả sản xuất thủy sản | Fishery | ⭐⭐⭐⭐ |
| **PL8** | Xuất nhập khẩu nông lâm thủy sản | Trade | ⭐⭐⭐⭐⭐ |
| **PL9** | Đầu tư XDCB | Investment | ⭐⭐⭐ |
| **PL10a/b** | Báo cáo chấp hành qui định | Reporting (metadata) | ⭐⭐ |

**Độ phức tạp:**
- ⭐⭐: Đơn giản - bảng 1 chiều
- ⭐⭐⭐: Trung bình - bảng nhiều cột, có phân cấp
- ⭐⭐⭐⭐: Phức tạp - có so sánh, nhiều kỳ
- ⭐⭐⭐⭐⭐: Rất phức tạp - nhiều chiều, nhiều loại so sánh

---

## 2. ĐÁNH GIÁ SCHEMA HIỆN TẠI

### 2.1. ✅ Điểm mạnh

1. **Cấu trúc rõ ràng**: Phân tách tốt các context (time, geo, item, metric)
2. **Linh hoạt**: Có thể áp dụng cho nhiều loại dữ liệu
3. **Có metadata**: Tracking source và extraction method

### 2.2. ⚠️ Vấn đề và thiếu sót

#### 2.2.1. Thiếu các trường quan trọng

**A. Comparison Context** (Ngữ cảnh so sánh)
```json
// Schema hiện tại KHÔNG có
// Nhưng dữ liệu có nhiều loại so sánh:
- "% 15/02/09 so với 15/02/08" (YoY)
- "% TH so với Kế hoạch" (vs Plan)
- "% TH 2 tháng so với cùng kỳ" (Cumulative YoY)
```

**B. Data Quality Indicators**
```json
// Không có cách phân biệt:
- Dữ liệu tổng hợp (Tổng Miền Bắc) vs chi tiết (Hà Nội)
- Dữ liệu đầy đủ vs thiếu
- Dữ liệu chính thức vs ước tính
```

**C. Appendix Metadata**
```json
// Không track được:
- Số phụ lục (PL1, PL2, ...)
- Tiêu đề phụ lục
- Số dòng trong bảng gốc
```

#### 2.2.2. Enum chưa đầy đủ

**Sector** - Thiếu:
- "Investment" (Đầu tư XDCB)
- "Reporting" (Báo cáo chấp hành)

**Attribute** - Thiếu:
- "Area_Seedling" (Diện tích mạ)
- "Export_Volume", "Export_Value" (Xuất khẩu)
- "Import_Volume", "Import_Value" (Nhập khẩu)
- "Investment_Amount", "Investment_Disbursement" (Đầu tư)

**Unit** - Thiếu:
- "million_USD" (triệu USD)
- "billion_VND" (tỷ VND)
- "million_trees" (triệu cây)
- "percent" (%)

#### 2.2.3. Không xử lý được các trường hợp đặc biệt

1. **Bảng có nhiều header rows** (PL7, PL8)
2. **Bảng có merged cells** (PL8 - "Gỗ & sản phẩm gỗ")
3. **Dữ liệu có footnotes** (Ghi chú: (*), (**))
4. **Giá trị có nhiều đơn vị trong cùng cột** (PL8 - Lượng và Giá trị)

---

## 3. SCHEMA CẢI THIỆN

### 3.1. Thay đổi chính

Đã tạo file: `schema_improved.json`

**Các cải tiến:**

1. ✅ **Thêm Comparison Context**
   - comparison_type: YoY, vs_Plan, vs_Target, MoM
   - comparison_value: Giá trị % so sánh
   - base_period: Kỳ gốc
   - base_value: Giá trị kỳ gốc

2. ✅ **Thêm Data Quality**
   - is_aggregated: Phân biệt tổng hợp vs chi tiết
   - has_missing_values: Đánh dấu dữ liệu thiếu
   - data_status: Complete, Partial, Estimated, Provisional

3. ✅ **Mở rộng Metadata**
   - appendix_number: Số phụ lục
   - appendix_title: Tiêu đề phụ lục
   - row_number: Số dòng trong bảng
   - extraction_confidence: Độ tin cậy (0-1)
   - notes: Ghi chú đặc biệt

4. ✅ **Bổ sung Enum**
   - Sector: +Investment, +Reporting
   - Attribute: +Area_Seedling, +Export_*, +Import_*, +Investment_*
   - Unit: +million_USD, +billion_VND, +million_trees, +percent

### 3.2. Ví dụ record mẫu

**Ví dụ 1: Diện tích lúa đông xuân**
```json
{
  "record_id": "2009_02_LongAn_Cultivation_Rice_Area_Planted_Actual",
  "time_context": {
    "year": 2009,
    "month": 2,
    "report_date": "2009-02-15",
    "period_type": "Seasonal"
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
    "sub_item": "Đông Xuân"
  },
  "metric_context": {
    "attribute": "Area_Planted",
    "value": 245962,
    "unit": "ha",
    "data_type": "Actual"
  },
  "comparison_context": {
    "comparison_type": "None"
  },
  "metadata": {
    "source_file": "PHULUC_t02_2009_FINAL.md",
    "appendix_number": "PL4",
    "appendix_title": "CÁC TỈNH MIỀN NAM - GIEO CẤY LÚA ĐÔNG XUÂN",
    "extraction_method": "Table_Parsing",
    "extraction_confidence": 0.95
  },
  "data_quality": {
    "is_aggregated": false,
    "has_missing_values": false,
    "data_status": "Complete"
  }
}
```

**Ví dụ 2: Xuất khẩu cà phê (có so sánh)**
```json
{
  "record_id": "2009_02_National_Trade_Coffee_Export_Value",
  "time_context": {
    "year": 2009,
    "month": 2,
    "period_type": "Cumulative"
  },
  "geo_context": {
    "geo_level": "National",
    "location_name": "Cả nước"
  },
  "item_context": {
    "sector": "Trade",
    "commodity": "Cà phê",
    "sub_item": "Xuất khẩu",
    "processing_level": "Processed"
  },
  "metric_context": {
    "attribute": "Export_Value",
    "value": 411,
    "unit": "million_USD",
    "data_type": "Actual"
  },
  "comparison_context": {
    "comparison_type": "YoY",
    "comparison_value": 88.4,
    "base_period": "2 tháng/2008",
    "base_value": 465
  },
  "metadata": {
    "source_file": "PHULUC_t02_2009_FINAL.md",
    "appendix_number": "PL8",
    "appendix_title": "TÌNH HÌNH XUẤT, NHẬP KHẨU",
    "extraction_method": "Table_Parsing",
    "extraction_confidence": 0.90,
    "notes": "Giá trị 2 tháng đầu năm"
  }
}
```

---

## 4. PHƯƠNG PHÁP TRÍCH XUẤT

### 4.1. So sánh các phương pháp

| Phương pháp | Ưu điểm | Nhược điểm | Độ chính xác | Tốc độ | Chi phí |
|-------------|---------|------------|--------------|--------|---------|
| **1. Regex + Table Parsing** | - Nhanh<br>- Không tốn chi phí<br>- Kiểm soát tốt | - Phải viết rule cho từng loại bảng<br>- Khó xử lý edge cases | 70-85% | ⚡⚡⚡ | 💰 Free |
| **2. LLM (GPT-4/Claude)** | - Linh hoạt<br>- Xử lý tốt edge cases<br>- Ít code | - Tốn chi phí<br>- Chậm hơn<br>- Cần validate | 85-95% | ⚡⚡ | 💰💰💰 |
| **3. Hybrid (Regex + LLM)** | - Cân bằng tốt<br>- Dùng LLM cho trường hợp khó | - Phức tạp hơn<br>- Cần orchestration | 90-95% | ⚡⚡ | 💰💰 |
| **4. Manual + Validation** | - Chính xác nhất<br>- Có thể QA | - Rất chậm<br>- Không scale | 95-99% | ⚡ | 💰💰💰💰 |

### 4.2. ✅ ĐỀ XUẤT: Hybrid Approach

**Lý do:**
1. Dữ liệu có nhiều loại bảng khác nhau (11 phụ lục)
2. Một số bảng đơn giản (PL1, PL2) → dùng Regex
3. Một số bảng phức tạp (PL7, PL8) → dùng LLM
4. Cần balance giữa chi phí và độ chính xác

**Workflow đề xuất:**

```
┌─────────────────┐
│  Segment Files  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  1. Pre-processing          │
│  - Detect table type        │
│  - Extract metadata         │
│  - Parse markdown table     │
└────────┬────────────────────┘
         │
         ▼
    ┌────────┐
    │ Simple?│
    └───┬─┬──┘
        │ │
    Yes │ │ No
        │ │
        ▼ ▼
┌───────────┐  ┌──────────────┐
│ 2a. Regex │  │ 2b. LLM      │
│ Parsing   │  │ Extraction   │
└─────┬─────┘  └──────┬───────┘
      │                │
      └────────┬───────┘
               ▼
┌──────────────────────────┐
│ 3. Validation            │
│ - Check schema           │
│ - Validate values        │
│ - Flag low confidence    │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 4. Output                │
│ - JSON (structured)      │
│ - CSV (for analysis)     │
│ - SQLite (for querying)  │
└──────────────────────────┘
```

### 4.3. Đánh giá khả năng Python script

**✅ CÓ THỂ cào được data từ MD bằng Python:**

**Lý do:**
1. ✅ Markdown tables có cấu trúc rõ ràng (dấu `|`)
2. ✅ Có thể dùng regex để parse
3. ✅ Có thể dùng pandas để xử lý
4. ✅ Đã segment ra từng phụ lục → dễ xử lý

**Thư viện Python hữu ích:**
```python
# Parsing
import re                    # Regex
import pandas as pd          # DataFrame processing
from markdown_it import MarkdownIt  # Markdown parser

# LLM (nếu dùng)
import openai               # OpenAI API
import anthropic            # Claude API

# Data processing
import json
import hashlib              # Generate record IDs
from pathlib import Path
```

**Độ khó:**
- **PL1-5 (Cultivation)**: ⭐⭐ Dễ - bảng đơn giản
- **PL6 (Forestry)**: ⭐⭐⭐ Trung bình - có kế hoạch/thực hiện
- **PL7 (Fishery)**: ⭐⭐⭐⭐ Khó - nhiều sub-items
- **PL8 (Trade)**: ⭐⭐⭐⭐⭐ Rất khó - nhiều chiều, merged cells
- **PL9 (Investment)**: ⭐⭐⭐ Trung bình
- **PL10 (Reporting)**: ⭐⭐ Dễ - metadata

---

## 5. HƯỚNG DẪN SỬ DỤNG

### 5.1. Cài đặt dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install pandas numpy
pip install markdown-it-py
pip install openai anthropic  # Nếu dùng LLM
```

### 5.2. Chạy script extraction (Regex-based)

```bash
# Extract data từ tất cả segment files của tháng 2/2009
python extract_data_from_md.py \
  --input-dir segments/2009 \
  --schema schema_improved.json \
  --output extracted_data_2009_02.json \
  --year 2009 \
  --month 2

# Output:
# - extracted_data_2009_02.json (structured data)
# - extracted_data_2009_02.csv (for Excel/analysis)
```

### 5.3. Validate extracted data

```bash
# Tạo script validation
python validate_extracted_data.py \
  --input extracted_data_2009_02.json \
  --schema schema_improved.json \
  --output validation_report.txt
```

### 5.4. Convert to different formats

```bash
# Convert to CSV
python convert_to_csv.py extracted_data_2009_02.json

# Convert to SQLite
python convert_to_sqlite.py extracted_data_2009_02.json

# Convert to Parquet (for big data)
python convert_to_parquet.py extracted_data_2009_02.json
```

---

## 6. KẾT LUẬN VÀ ĐỀ XUẤT

### 6.1. Kết luận

1. ✅ **Schema hiện tại có nền tảng tốt** nhưng cần cải thiện để cover hết các loại dữ liệu

2. ✅ **Python script CÓ THỂ extract được data** từ markdown files
   - Độ chính xác ước tính: **70-85%** với regex thuần
   - Độ chính xác ước tính: **85-95%** với LLM
   - Độ chính xác ước tính: **90-95%** với hybrid approach

3. ✅ **Đã segment tốt** - giúp việc extraction dễ dàng hơn nhiều

### 6.2. Roadmap đề xuất

#### Phase 1: Foundation (1-2 tuần)
- [x] Đánh giá schema hiện tại
- [x] Tạo schema cải thiện
- [x] Tạo script extraction cơ bản
- [ ] Test với 1-2 phụ lục đơn giản (PL1, PL2)
- [ ] Validate kết quả

#### Phase 2: Core Extraction (2-3 tuần)
- [ ] Implement extraction cho tất cả cultivation tables (PL1-5)
- [ ] Implement extraction cho forestry (PL6)
- [ ] Implement extraction cho fishery (PL7)
- [ ] Tạo validation framework
- [ ] Test với toàn bộ tháng 2/2009

#### Phase 3: Complex Tables (2-3 tuần)
- [ ] Implement extraction cho trade tables (PL8) - có thể dùng LLM
- [ ] Implement extraction cho investment (PL9)
- [ ] Xử lý edge cases và special characters
- [ ] Improve accuracy với post-processing rules

#### Phase 4: Scale Up (2-3 tuần)
- [ ] Extract toàn bộ năm 2009 (12 tháng)
- [ ] Extract năm 2010, 2011
- [ ] Tạo consolidated dataset
- [ ] Data quality report
- [ ] Documentation

#### Phase 5: Analysis Ready (1-2 tuần)
- [ ] Feature engineering
- [ ] Create analysis-ready datasets
- [ ] Time series aggregation
- [ ] Regional aggregation
- [ ] Export to formats for ML (Parquet, HDF5)

### 6.3. Metrics để đo lường thành công

| Metric | Target | Cách đo |
|--------|--------|---------|
| **Coverage** | >95% | % records extracted vs total possible |
| **Accuracy** | >90% | Manual validation on sample |
| **Completeness** | >85% | % fields filled vs schema |
| **Consistency** | >95% | Cross-validation between tables |
| **Processing Speed** | <5 min/month | Time to extract 1 month data |

### 6.4. Rủi ro và giảm thiểu

| Rủi ro | Mức độ | Giảm thiểu |
|--------|--------|------------|
| **Markdown format không nhất quán** | Cao | - Validate format trước khi extract<br>- Có fallback cho LLM |
| **Merged cells trong bảng** | Trung bình | - Detect và xử lý riêng<br>- Manual review |
| **Giá trị thiếu hoặc lỗi** | Trung bình | - Flag trong data_quality<br>- Có confidence score |
| **Chi phí LLM cao** | Thấp | - Chỉ dùng cho complex tables<br>- Cache results |
| **Thời gian xử lý lâu** | Thấp | - Parallel processing<br>- Optimize regex |

---

## 📚 TÀI LIỆU THAM KHẢO

1. **Schema Files:**
   - `schema_final.json` - Schema gốc
   - `schema_improved.json` - Schema cải thiện (v2.0)

2. **Scripts:**
   - `extract_data_from_md.py` - Main extraction script
   - (Sẽ tạo thêm) `validate_extracted_data.py`
   - (Sẽ tạo thêm) `convert_to_formats.py`

3. **Sample Data:**
   - `segments/2009/` - Segmented markdown files
   - (Sẽ tạo) `extracted_data_2009_02.json` - Sample output

---

## 📞 LIÊN HỆ VÀ HỖ TRỢ

Nếu có câu hỏi hoặc cần hỗ trợ:
1. Review file `schema_improved.json` để hiểu cấu trúc
2. Chạy thử script với 1-2 file segment
3. Check validation report
4. Adjust và iterate

**Good luck with your data mining project! 🚀**
