# 🌾 Vietnam Agricultural Dataset - Data Mining Project

> **Đồ án Data Mining**: Xây dựng Dataset nông nghiệp Việt Nam từ dữ liệu phi cấu trúc (PDF/DOC) của Bộ Nông nghiệp và Phát triển Nông thôn

---

## 📋 Tổng quan Dự án

Dự án này nhằm xây dựng một **Dataset có cấu trúc** về nông nghiệp Việt Nam từ các **báo cáo thống kê phi cấu trúc** (PDF, DOC) của Bộ Nông nghiệp và Phát triển Nông thôn (MARD).

### 🎯 Mục tiêu

Chuyển đổi hàng trăm file báo cáo PDF/DOC (2008-2023) thành Dataset có cấu trúc để phục vụ:
- 📊 Phân tích xu hướng nông nghiệp
- 🤖 Machine Learning / Data Mining
- 📈 Dự đoán sản lượng, giá cả
- 🔍 Phân tích thị trường nông sản

### 🔄 Quy trình xây dựng Dataset

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE XÂY DỰNG DATASET                    │
└─────────────────────────────────────────────────────────────────┘

📥 PHASE 1: Thu thập & Tiền xử lý (← Hiện tại)
   ├─ Tải báo cáo PDF/DOC từ website MARD
   ├─ Convert sang Markdown (.md)
   └─ Chuẩn bị cho LLM parsing

🤖 PHASE 2: Phân tích & Trích xuất (Sắp tới)
   ├─ Sử dụng LLM để parse dữ liệu từ .md
   ├─ Trích xuất thông tin: Date, Location, Commodity, Value
   └─ Xử lý format khác nhau qua các năm

🔧 PHASE 3: Chuẩn hóa & Làm sạch (Sắp tới)
   ├─ Xử lý dữ liệu thiếu (NaN)
   ├─ Chuẩn hóa đơn vị, tên sản phẩm
   └─ Tạo Dataset cuối cùng

📊 PHASE 4: Data Mining & Analysis (Sắp tới)
   ├─ Classification, Clustering
   ├─ Time series analysis
   └─ Predictive modeling
```

---

## 📥 PHASE 1: Thu thập & Tiền xử lý Dữ liệu

> **Trạng thái**: ✅ Đang thực hiện  
> **Mục tiêu**: Tải và convert báo cáo PDF/DOC → Markdown

### 🎯 Tại sao cần Phase này?

**Vấn đề**: Báo cáo thống kê của MARD là **dữ liệu phi cấu trúc**:
- 📄 Format: PDF, DOC (không thể xử lý trực tiếp)
- 📊 Bảng biểu phức tạp, format khác nhau qua các năm
- 📝 Văn bản tự do, không có cấu trúc cố định

**Giải pháp**: Convert sang **Markdown** (.md):
- ✅ Text thuần, dễ xử lý
- ✅ Giữ được cấu trúc: headings, tables, lists
- ✅ Dễ dàng cho LLM đọc và parse (Phase 2)

---

## 📥 Bước 1: Tải dữ liệu từ MARD

### 1.1. Truy cập website

Vào link: [https://www.mard.gov.vn/Pages/default.aspx](https://www.mard.gov.vn/Pages/default.aspx)

Chọn mục **"Thống kê - Báo cáo"** theo hình dưới đây:

![Chọn mục Thống kê - Báo cáo](img/image1.png)

### 1.2. Tải báo cáo theo năm

1. Chọn **năm** mà bạn muốn lấy báo cáo (2008-2023)
2. Bấm nút **"Tải xuống"** để download file

![Chọn năm và tải xuống](img/image2.png)

### 1.3. Tổ chức dữ liệu

Lưu các file đã tải về vào **thư mục theo năm**:

```
DatasetDataset/
├── 2008/
│   ├── baocao_T01_2008.pdf
│   ├── baocao_T02_2008.pdf
│   └── ...
├── 2009/
│   ├── baocao_T10_2009_Final.pdf
│   ├── baocao_T11_2009_Final.pdf
│   └── baocao_T12_2009.pdf
├── 2010/
│   └── ...
├── ...
├── 2022/
│   ├── Baocao_T02_2022.doc
│   ├── Baocao_T03_2022.doc
│   └── Baocao_T09_2022.pdf
└── 2023/
    └── ...
```

**📌 Lưu ý**:
- Phạm vi: Từ năm **2008 đến 2023**
- Tần suất: **5-10 báo cáo/năm** (theo tháng hoặc quý)
- Format: **PDF** hoặc **DOC** (tùy năm)

---

## 🔄 Bước 2: Convert sang Markdown

### 2.1. Cài đặt (Chỉ làm 1 lần)

```bash
# Cài Python packages
pip install pymupdf4llm python-docx pypandoc

# Cài LibreOffice (để convert .doc → .docx)
sudo apt-get install libreoffice
```

### 2.2. Chạy script conversion

```bash
python convert_all.py
```

**Script sẽ tự động**:
1. ✅ Convert tất cả `.doc` → `.docx` (dùng LibreOffice)
2. ✅ Convert tất cả `.pdf`, `.docx` → `.md` (dùng pymupdf4llm)
3. ✅ Giữ nguyên cấu trúc thư mục theo năm
4. ✅ Lưu kết quả vào `markdown_output/`

### 2.3. Kết quả

**Output:**
```
markdown_output/
├── 2008/
│   ├── baocao_T01_2008.md
│   ├── baocao_T02_2008.md
│   └── ...
├── 2009/
│   ├── baocao_T10_2009_Final.md
│   ├── baocao_T11_2009_Final.md
│   └── baocao_T12_2009.md
├── ...
└── 2023/
    └── ...
```

**Log file**: `conversion.log` (chi tiết mọi thao tác)

---

## 📊 Đặc điểm Dữ liệu

### 🔍 Thách thức

**Format thay đổi qua các năm**:
- 📅 **2008-2010**: Bảng biểu theo giá so sánh 1994
- 📅 **2011-2015**: Thêm chỉ số tăng trưởng (%)
- 📅 **2016-2023**: Format hiện đại, nhiều chỉ tiêu hơn

**Ví dụ**:
```
Báo cáo 2010: "Sản lượng lúa (giá so sánh 1994)"
Báo cáo 2019: "Sản lượng lúa (tấn) - Tăng trưởng (%)"
```

→ **Giải pháp**: Dùng LLM để parse thông minh (Phase 2)

### 📋 Thông tin cần trích xuất (Phase 2)

Từ các file Markdown, LLM sẽ trích xuất:

| Field | Mô tả | Ví dụ |
|-------|-------|-------|
| **Date** | Thời gian báo cáo | 2019-10, 2022-Q3 |
| **Location** | Vùng/Tỉnh | Đồng bằng sông Cửu Long, Hà Nội |
| **Commodity** | Sản phẩm nông nghiệp | Lúa, Lợn, Cà phê |
| **Indicator** | Chỉ tiêu | Sản lượng, Giá, Xuất khẩu |
| **Value** | Giá trị | 1000 tấn, 50000 VND/kg |
| **Unit** | Đơn vị | tấn, kg, VND |

**📌 Lưu ý**: LLM sẽ xử lý:
- Nhận diện "Lợn" và "Heo" là cùng một đối tượng
- Chuẩn hóa đơn vị (tấn, kg, tạ)
- Xử lý format khác nhau qua các năm

---

## 🚀 Quick Start

```bash
# 1. Cài đặt dependencies
pip install pymupdf4llm python-docx pypandoc
sudo apt-get install libreoffice

# 2. Convert tất cả documents
python convert_all.py

# 3. Xem kết quả
ls markdown_output/
cat conversion.log
```

**Xong!** 🎉 Tất cả file đã được convert sang Markdown, sẵn sàng cho Phase 2.

---

## 📖 Tài liệu hỗ trợ

| File | Mô tả | Mục đích |
|------|-------|----------|
| **[QUICK_START.md](QUICK_START.md)** | 📘 Hướng dẫn chi tiết | Hướng dẫn từng bước cho người mới |
| **[CHEAT_SHEET.md](CHEAT_SHEET.md)** | ⚡ Quick reference | Commands nhanh, troubleshooting |
| **[convert_all.py](convert_all.py)** | 🔧 Script chính | Convert PDF/DOC → Markdown |
| **conversion.log** | 📊 Log file | Chi tiết quá trình conversion |

**📌 Lưu ý**: Các file này chỉ hỗ trợ cho **Phase 1** (Thu thập & Tiền xử lý)

---

## 🔧 Usage nâng cao

### Convert folder cụ thể

```bash
# Convert chỉ năm 2022
python convert_all.py --input ./2022

# Custom output directory
python convert_all.py --output ./my_markdown
```

### Force reconvert

```bash
# Convert lại tất cả (bỏ qua skip)
python convert_all.py --no-skip
```

### Skip .doc conversion

```bash
# Nếu đã convert .doc → .docx rồi
python convert_all.py --skip-doc-conversion
```

**Xem thêm**: [QUICK_START.md](QUICK_START.md) và [CHEAT_SHEET.md](CHEAT_SHEET.md)

---

## 📈 Kế hoạch tiếp theo (Roadmap)

### ✅ Phase 1: Thu thập & Tiền xử lý (Hiện tại)
- [x] Tải báo cáo từ MARD
- [x] Convert PDF/DOC → Markdown
- [x] Tổ chức dữ liệu theo năm

### 🔄 Phase 2: LLM Parsing (Sắp tới)

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

### 🔧 Phase 3: Chuẩn hóa & Làm sạch (Sắp tới)

**Mục tiêu**: Tạo Dataset sạch, sẵn sàng cho Data Mining

**Công việc**:
- Xử lý dữ liệu thiếu (NaN):
  - Imputation (nội suy)
  - Forward fill / Backward fill
- Chuẩn hóa:
  - Đơn vị: tấn, kg, tạ → kg
  - Tên sản phẩm: "Lợn", "Heo" → "Lợn"
  - Địa danh: "ĐBSCL" → "Đồng bằng sông Cửu Long"
- Validation:
  - Kiểm tra outliers
  - Kiểm tra logic (giá trị âm, quá lớn)

### 📊 Phase 4: Data Mining & Analysis (Sắp tới)

**Mục tiêu**: Phân tích và khai phá dữ liệu

**Kỹ thuật**:
- **Text Mining**: TF-IDF, Word embeddings
- **Classification**: Phân loại sản phẩm, vùng miền
- **Clustering**: Nhóm các tỉnh/sản phẩm tương đồng
- **Time Series**: Dự đoán xu hướng, mùa vụ
- **Regression**: Dự đoán giá, sản lượng

---

## 📊 Thống kê Dataset (Dự kiến)

**Phạm vi dữ liệu**:
- 📅 **Thời gian**: 2008 - 2023 (16 năm)
- 📄 **Số báo cáo**: ~80-160 file (5-10 file/năm)
- 🌾 **Sản phẩm**: Lúa, Ngô, Lợn, Gà, Cà phê, Cao su, ...
- 📍 **Vùng miền**: 63 tỉnh/thành, 8 vùng kinh tế

**Kích thước dự kiến** (sau Phase 3):
- 📊 **Rows**: 10,000 - 50,000 records
- 📋 **Columns**: 8-12 features
- 💾 **Size**: ~5-20 MB (CSV)

---

## 🎯 Ứng dụng thực tế

Sau khi hoàn thành Dataset, có thể:

1. **📈 Phân tích xu hướng**:
   - Sản lượng lúa tăng/giảm qua các năm
   - Giá cả nông sản theo mùa vụ

2. **🤖 Machine Learning**:
   - Dự đoán sản lượng năm tới
   - Dự báo giá nông sản

3. **🗺️ Phân tích không gian**:
   - Vùng nào trồng cây gì hiệu quả
   - So sánh năng suất giữa các tỉnh

4. **💡 Hỗ trợ quyết định**:
   - Chính sách nông nghiệp
   - Đầu tư vào vùng/sản phẩm nào

---

## 🔍 Workflow chi tiết

```
┌─────────────────────────────────────────────────────────────────┐
│                         WORKFLOW HOÀN CHỈNH                      │
└─────────────────────────────────────────────────────────────────┘

1. 📥 TẢI DỮ LIỆU
   ├─ Vào website MARD
   ├─ Chọn năm → Tải báo cáo
   └─ Lưu vào folder theo năm

2. 🔄 CONVERT (← Hiện tại)
   ├─ .doc → LibreOffice → .docx
   ├─ .docx → python-docx → .md
   └─ .pdf → pymupdf4llm → .md

3. 🤖 LLM PARSING (Sắp tới)
   ├─ Đọc .md file
   ├─ Trích xuất: Date, Location, Commodity, Value
   └─ Lưu vào CSV/Database

4. 🔧 CHUẨN HÓA (Sắp tới)
   ├─ Xử lý NaN
   ├─ Chuẩn hóa đơn vị, tên
   └─ Validate dữ liệu

5. 📊 DATA MINING (Sắp tới)
   ├─ Exploratory Data Analysis (EDA)
   ├─ Feature Engineering
   ├─ Modeling: Classification, Clustering, Regression
   └─ Visualization & Reporting
```

---

## ❓ FAQ

### Q: Tại sao không dùng script cố định để parse PDF?

**A**: Vì format báo cáo **thay đổi qua từng năm**:
- Năm 2010: Bảng theo giá so sánh 1994
- Năm 2019: Bảng theo tăng trưởng %
- Năm 2023: Format mới hoàn toàn

→ Dùng **LLM** linh hoạt hơn, có thể hiểu context và adapt với format khác nhau.

### Q: Tại sao convert sang Markdown thay vì xử lý trực tiếp PDF?

**A**: 
- ✅ **Markdown** dễ đọc cho LLM hơn PDF binary
- ✅ Giữ được cấu trúc: headings, tables, lists
- ✅ File nhẹ hơn, xử lý nhanh hơn
- ✅ Dễ debug và kiểm tra

### Q: Làm sao xử lý format khác nhau qua các năm?

**A**: **Prompt Engineering** cho từng năm:
```
Năm 2010: "Trích xuất bảng theo giá so sánh 1994..."
Năm 2019: "Trích xuất bảng tăng trưởng %..."
```

LLM sẽ tự động nhận diện và adapt.

### Q: Xử lý dữ liệu thiếu như thế nào?

**A**: Trong Phase 3:
- Nếu chỉ tiêu không có trong báo cáo → NaN
- Sau đó dùng **Imputation**: forward fill, interpolation, ...

---

## 🛠️ Requirements

### Python Packages

```bash
pip install pymupdf4llm python-docx pypandoc
```

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install --cask libreoffice
```

---

## 📝 Troubleshooting

### ❌ Lỗi: "pymupdf4llm not found"

```bash
pip install pymupdf4llm
```

### ❌ Lỗi: "LibreOffice not found"

```bash
sudo apt-get install libreoffice
```

### ❌ File .doc không convert được

**Giải pháp**:
1. Mở file bằng Word/LibreOffice
2. Save As → .docx
3. Chạy lại script

**Xem chi tiết**: [QUICK_START.md#troubleshooting](QUICK_START.md#troubleshooting)

---

## 🤝 Contributing

Dự án này là đồ án Data Mining tại UIT. Nếu bạn muốn đóng góp:
1. Test với nhiều loại documents
2. Report bugs qua log file
3. Suggest improvements

---

## 📜 License

MIT License - Free to use for educational and research purposes

---

## 👨‍💻 Project Info

**Tên dự án**: Vietnam Agricultural Dataset  
**Loại**: Đồ án Data Mining  
**Trường**: UIT (Đại học Công nghệ Thông tin)  
**Năm**: 2026

**Phase hiện tại**: Phase 1 - Thu thập & Tiền xử lý  
**Version**: 1.0  
**Last Updated**: 2026-01-04  
**Status**: ✅ Phase 1 Production Ready

---

## 📞 Support

- 📖 Đọc [QUICK_START.md](QUICK_START.md) cho hướng dẫn chi tiết
- ⚡ Xem [CHEAT_SHEET.md](CHEAT_SHEET.md) cho quick commands
- 📝 Check `conversion.log` cho debugging
- 🔧 Xem [convert_all.py](convert_all.py) source code

---

## 🎯 Next Steps

Sau khi hoàn thành Phase 1:

1. **Kiểm tra kết quả**:
   ```bash
   find markdown_output -name "*.md" | wc -l
   cat conversion.log
   ```

2. **Chuẩn bị cho Phase 2**:
   - Chọn 1 file .md làm mẫu
   - Thiết lập Template Dataset
   - Viết prompt cho LLM

3. **Bắt đầu LLM Parsing**:
   - Test với 1 năm trước
   - Scale lên toàn bộ dataset

---

**Happy Data Mining! 🎉📊🌾**
