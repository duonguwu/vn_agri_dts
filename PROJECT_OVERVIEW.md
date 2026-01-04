# Project Overview - Vietnam Agricultural Dataset

> Tài liệu chi tiết về dự án xây dựng Dataset nông nghiệp Việt Nam

---

## Mục tiêu Dự án

Chuyển đổi hàng trăm file báo cáo PDF/DOC (2008-2023) thành Dataset có cấu trúc để phục vụ:
- Phân tích xu hướng nông nghiệp
- Machine Learning / Data Mining
- Dự đoán sản lượng, giá cả
- Phân tích thị trường nông sản

---

## Quy trình xây dựng Dataset (Chi tiết)

### Phase 1: Thu thập & Tiền xử lý (Hiện tại)

**Mục tiêu**: Tải và convert báo cáo PDF/DOC → Markdown

**Tại sao cần Phase này?**

Báo cáo thống kê của MARD là **dữ liệu phi cấu trúc**:
- Format: PDF, DOC (không thể xử lý trực tiếp)
- Bảng biểu phức tạp, format khác nhau qua các năm
- Văn bản tự do, không có cấu trúc cố định

**Giải pháp**: Convert sang Markdown (.md):
- Text thuần, dễ xử lý
- Giữ được cấu trúc: headings, tables, lists
- Dễ dàng cho LLM đọc và parse (Phase 2)

**Công cụ**:
- `convert_all.py`: Script chính
- `pymupdf4llm`: Convert PDF → Markdown
- `python-docx`: Xử lý DOCX
- `LibreOffice`: Convert DOC → DOCX

---

### Phase 2: LLM Parsing (Sắp tới)

**Mục tiêu**: Trích xuất dữ liệu từ Markdown sang Dataset có cấu trúc

**Phương pháp**:

1. **Thiết lập Template Dataset**:
   ```
   Date | Location | Commodity | Indicator | Value | Unit
   -----|----------|-----------|-----------|-------|-----
   2019-10 | ĐBSCL | Lúa | Sản lượng | 1000 | tấn
   ```

2. **Prompt Engineering**:
   - Viết prompt đặc thù cho từng năm
   - Hướng dẫn LLM nhận diện format khác nhau
   - Xử lý đồng nghĩa: "Lợn" = "Heo", "Tạ" = "100kg"

3. **Batch Processing**:
   - Parse từng file .md
   - Merge vào Dataset chung
   - Validate dữ liệu

**Thông tin cần trích xuất**:

| Field | Mô tả | Ví dụ |
|-------|-------|-------|
| Date | Thời gian báo cáo | 2019-10, 2022-Q3 |
| Location | Vùng/Tỉnh | Đồng bằng sông Cửu Long, Hà Nội |
| Commodity | Sản phẩm nông nghiệp | Lúa, Lợn, Cà phê |
| Indicator | Chỉ tiêu | Sản lượng, Giá, Xuất khẩu |
| Value | Giá trị | 1000 tấn, 50000 VND/kg |
| Unit | Đơn vị | tấn, kg, VND |

---

### Phase 3: Chuẩn hóa & Làm sạch (Sắp tới)

**Mục tiêu**: Tạo Dataset sạch, sẵn sàng cho Data Mining

**Công việc**:

1. **Xử lý dữ liệu thiếu (NaN)**:
   - Imputation (nội suy)
   - Forward fill / Backward fill

2. **Chuẩn hóa**:
   - Đơn vị: tấn, kg, tạ → kg
   - Tên sản phẩm: "Lợn", "Heo" → "Lợn"
   - Địa danh: "ĐBSCL" → "Đồng bằng sông Cửu Long"

3. **Validation**:
   - Kiểm tra outliers
   - Kiểm tra logic (giá trị âm, quá lớn)

---

### Phase 4: Data Mining & Analysis (Sắp tới)

**Mục tiêu**: Phân tích và khai phá dữ liệu

**Kỹ thuật**:
- **Text Mining**: TF-IDF, Word embeddings
- **Classification**: Phân loại sản phẩm, vùng miền
- **Clustering**: Nhóm các tỉnh/sản phẩm tương đồng
- **Time Series**: Dự đoán xu hướng, mùa vụ
- **Regression**: Dự đoán giá, sản lượng

---

## Đặc điểm Dữ liệu

### Thách thức

**Format thay đổi qua các năm**:
- 2008-2010: Bảng biểu theo giá so sánh 1994
- 2011-2015: Thêm chỉ số tăng trưởng (%)
- 2016-2023: Format hiện đại, nhiều chỉ tiêu hơn

**Ví dụ**:
```
Báo cáo 2010: "Sản lượng lúa (giá so sánh 1994)"
Báo cáo 2019: "Sản lượng lúa (tấn) - Tăng trưởng (%)"
```

**Giải pháp**: Dùng LLM để parse thông minh, có thể hiểu context và adapt với format khác nhau.

### Phạm vi dữ liệu

- **Thời gian**: 2008 - 2023 (16 năm)
- **Số báo cáo**: ~80-160 file (5-10 file/năm)
- **Sản phẩm**: Lúa, Ngô, Lợn, Gà, Cà phê, Cao su, ...
- **Vùng miền**: 63 tỉnh/thành, 8 vùng kinh tế

### Kích thước dự kiến (sau Phase 3)

- **Rows**: 10,000 - 50,000 records
- **Columns**: 8-12 features
- **Size**: ~5-20 MB (CSV)

---

## Ứng dụng thực tế

Sau khi hoàn thành Dataset:

1. **Phân tích xu hướng**:
   - Sản lượng lúa tăng/giảm qua các năm
   - Giá cả nông sản theo mùa vụ

2. **Machine Learning**:
   - Dự đoán sản lượng năm tới
   - Dự báo giá nông sản

3. **Phân tích không gian**:
   - Vùng nào trồng cây gì hiệu quả
   - So sánh năng suất giữa các tỉnh

4. **Hỗ trợ quyết định**:
   - Chính sách nông nghiệp
   - Đầu tư vào vùng/sản phẩm nào

---

## Workflow hoàn chỉnh

```
1. TẢI DỮ LIỆU
   - Vào website MARD
   - Chọn năm → Tải báo cáo
   - Lưu vào folder theo năm

2. CONVERT (← Hiện tại)
   - .doc → LibreOffice → .docx
   - .docx → python-docx → .md
   - .pdf → pymupdf4llm → .md

3. LLM PARSING (Sắp tới)
   - Đọc .md file
   - Trích xuất: Date, Location, Commodity, Value
   - Lưu vào CSV/Database

4. CHUẨN HÓA (Sắp tới)
   - Xử lý NaN
   - Chuẩn hóa đơn vị, tên
   - Validate dữ liệu

5. DATA MINING (Sắp tới)
   - Exploratory Data Analysis (EDA)
   - Feature Engineering
   - Modeling: Classification, Clustering, Regression
   - Visualization & Reporting
```

---

## FAQ

### Q: Tại sao không dùng script cố định để parse PDF?

**A**: Vì format báo cáo **thay đổi qua từng năm**. Dùng LLM linh hoạt hơn, có thể hiểu context và adapt với format khác nhau.

### Q: Tại sao convert sang Markdown thay vì xử lý trực tiếp PDF?

**A**: 
- Markdown dễ đọc cho LLM hơn PDF binary
- Giữ được cấu trúc: headings, tables, lists
- File nhẹ hơn, xử lý nhanh hơn
- Dễ debug và kiểm tra

### Q: Làm sao xử lý format khác nhau qua các năm?

**A**: Prompt Engineering cho từng năm:
```
Năm 2010: "Trích xuất bảng theo giá so sánh 1994..."
Năm 2019: "Trích xuất bảng tăng trưởng %..."
```

LLM sẽ tự động nhận diện và adapt.

### Q: Xử lý dữ liệu thiếu như thế nào?

**A**: Trong Phase 3:
- Nếu chỉ tiêu không có trong báo cáo → NaN
- Sau đó dùng Imputation: forward fill, interpolation, ...

---

## Roadmap chi tiết

### Phase 1 (Hiện tại)
- [x] Tải báo cáo từ MARD
- [x] Convert PDF/DOC → Markdown
- [x] Tổ chức dữ liệu theo năm

### Phase 2 (Q1 2026)
- [ ] Chọn 1 file .md làm mẫu
- [ ] Thiết lập Template Dataset
- [ ] Viết prompt cho LLM
- [ ] Test với 1 năm
- [ ] Scale lên toàn bộ dataset

### Phase 3 (Q2 2026)
- [ ] Xử lý dữ liệu thiếu
- [ ] Chuẩn hóa đơn vị, tên
- [ ] Validate dữ liệu
- [ ] Export Dataset cuối cùng

### Phase 4 (Q2-Q3 2026)
- [ ] Exploratory Data Analysis
- [ ] Feature Engineering
- [ ] Modeling
- [ ] Visualization & Reporting

---

## Contributing

Dự án này là đồ án Data Mining tại UIT. Nếu bạn muốn đóng góp:
1. Test với nhiều loại documents
2. Report bugs qua log file
3. Suggest improvements

---

## Project Info

**Tên dự án**: Vietnam Agricultural Dataset  
**Loại**: Đồ án Data Mining  
**Trường**: UIT (Đại học Công nghệ Thông tin)  
**Năm**: 2026

**Phase hiện tại**: Phase 1 - Thu thập & Tiền xử lý  
**Version**: 1.0  
**Last Updated**: 2026-01-04  
**Status**: Phase 1 Production Ready

---

**Quay lại**: [README.md](README.md)
