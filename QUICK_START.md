# 📚 Hướng dẫn Convert Documents sang Markdown

> **Mục đích**: Convert hàng loạt file PDF, DOC, DOCX sang định dạng Markdown (.md) để dễ dàng xử lý cho Data Mining.

---

## 🎯 Tóm tắt nhanh

**Bạn có nhiều file PDF/DOC/DOCX và muốn convert sang Markdown?**

👉 **Chỉ cần 1 lệnh:**

```bash
python convert_all.py
```

**Kết quả:**
- ✅ Tất cả file được convert sang `.md`
- ✅ Lưu trong folder `markdown_output/`
- ✅ Giữ nguyên cấu trúc thư mục
- ✅ Tự động xử lý file .doc → .docx → .md

---

## 📦 Cài đặt (Chỉ làm 1 lần)

### Bước 1: Cài Python packages

```bash
pip install pymupdf4llm python-docx pypandoc
```

**Giải thích:**
- `pymupdf4llm`: Convert PDF sang Markdown (có hỗ trợ bảng, hình ảnh)
- `python-docx`: Đọc và xử lý file DOCX
- `pypandoc`: Hỗ trợ convert DOC (optional)

### Bước 2: Cài LibreOffice (Nếu có file .doc)

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install --cask libreoffice
```

**Tại sao cần LibreOffice?**
- File `.doc` (Word cũ) cần convert sang `.docx` trước
- LibreOffice làm việc này tự động

### Bước 3: Kiểm tra

```bash
python convert_all.py --help
```

Nếu hiện ra hướng dẫn → Cài đặt thành công! ✅

---

## 🚀 Cách sử dụng

### 🌟 Cách 1: Convert tất cả (RECOMMENDED)

```bash
python convert_all.py
```

**Script sẽ tự động:**
1. Tìm tất cả file .doc và convert sang .docx
2. Convert tất cả PDF, DOCX sang Markdown
3. Lưu vào folder `markdown_output/`
4. Giữ nguyên cấu trúc thư mục

**Ví dụ kết quả:**

```
Trước:
DatasetDataset/
├── 2009/
│   ├── baocao_T10_2009_Final.pdf
│   └── baocao_T11_2009_Final.pdf
├── 2022/
│   ├── Baocao_T02_2022.doc
│   └── Baocao_T03_2022.docx

Sau:
DatasetDataset/
├── 2009/
│   ├── baocao_T10_2009_Final.pdf
│   └── baocao_T11_2009_Final.pdf
├── 2022/
│   ├── Baocao_T02_2022.doc
│   ├── Baocao_T02_2022.docx  ← Tự động tạo
│   └── Baocao_T03_2022.docx
└── markdown_output/          ← Folder mới
    ├── 2009/
    │   ├── baocao_T10_2009_Final.md
    │   └── baocao_T11_2009_Final.md
    └── 2022/
        ├── Baocao_T02_2022.md
        └── Baocao_T03_2022.md
```

### � Cách 2: Convert folder cụ thể

```bash
# Convert chỉ folder 2022
python convert_all.py --input ./2022

# Lưu output vào folder khác
python convert_all.py --output ./my_markdown_files
```

### 🔄 Cách 3: Convert lại tất cả (Force)

```bash
# Bình thường script sẽ skip file đã convert
# Dùng --no-skip để convert lại tất cả
python convert_all.py --no-skip
```

### ⚡ Cách 4: Bỏ qua bước convert .doc

```bash
# Nếu không có file .doc hoặc đã convert rồi
python convert_all.py --skip-doc-conversion
```

---

## � Hiểu kết quả

### Output trên màn hình:

```
============================================================
🚀 ALL-IN-ONE DOCUMENT TO MARKDOWN CONVERTER
============================================================
🔍 Checking dependencies...
  ✅ pymupdf4llm
  ✅ python-docx
  ✅ LibreOffice (for .doc conversion)
✅ All required dependencies are installed!

📝 Step 1: Converting .doc files to .docx...
============================================================
Found 9 .doc file(s)

[1/9] Baocao_T02_2022.doc
  ✅ Converted to Baocao_T02_2022.docx

...

✅ Converted 9/9 .doc files

📄 Step 2: Converting all documents to Markdown...
============================================================
[1/25] Processing: baocao_T10_2009_Final.pdf
  ✅ Success: markdown_output/2009/baocao_T10_2009_Final.md

...

============================================================
📊 CONVERSION SUMMARY
============================================================
Total files processed: 18
✅ Success: 9
❌ Failed: 0
⏭️  Skipped: 7
============================================================

🎉 CONVERSION COMPLETE!
============================================================
📂 Output directory: ./markdown_output
📊 Check conversion.log for details
```

### Ý nghĩa các số liệu:

- **Total files processed**: Tổng số file đã xử lý
- **✅ Success**: Số file convert thành công
- **❌ Failed**: Số file bị lỗi (xem log để biết lý do)
- **⏭️ Skipped**: Số file đã có sẵn (không convert lại)

---

## 📝 File log

Mọi thông tin chi tiết được ghi vào file `conversion.log`

### Xem toàn bộ log:

```bash
cat conversion.log
```

### Xem chỉ các file lỗi:

```bash
grep "Failed" conversion.log
```

### Xem tóm tắt cuối:

```bash
tail -20 conversion.log
```

---

## ❓ Troubleshooting (Xử lý lỗi)

### ❌ Lỗi: "pymupdf4llm not found"

**Nguyên nhân:** Chưa cài package

**Giải pháp:**
```bash
pip install pymupdf4llm
```

### ❌ Lỗi: "LibreOffice not found"

**Nguyên nhân:** Chưa cài LibreOffice (cần cho file .doc)

**Giải pháp:**
```bash
sudo apt-get install libreoffice
```

**Hoặc:** Nếu không muốn cài, convert .doc sang .docx bằng Word/Google Docs trước

### ❌ File .doc không convert được

**Nguyên nhân:** File .doc bị lỗi hoặc format đặc biệt

**Giải pháp:**
1. Mở file bằng Word/LibreOffice
2. Save As → chọn .docx
3. Chạy lại script

### ❌ File PDF có bảng bị lỗi format

**Nguyên nhân:** Bảng phức tạp trong PDF

**Giải pháp:**
- Script đã tự động xử lý bảng tốt nhất có thể
- Nếu vẫn lỗi, cần chỉnh sửa manual file .md sau khi convert

### ⚠️ Một số file bị Failed

**Cách check:**
```bash
# Xem file nào failed
grep "Failed" conversion.log

# Xem lý do cụ thể
grep -A 2 "Failed" conversion.log
```

---

## 🎓 Tips & Best Practices

### 1. Chạy lần đầu với --skip-existing

```bash
python convert_all.py
```

Lần sau chỉ convert file mới:
```bash
python convert_all.py  # Tự động skip file đã có
```

### 2. Backup trước khi convert

```bash
# Tạo backup folder gốc
cp -r . ../DatasetDataset_backup
```

### 3. Kiểm tra kết quả

```bash
# Đếm số file .md đã tạo
find markdown_output -name "*.md" | wc -l

# Xem dung lượng
du -sh markdown_output/

# List tất cả file
find markdown_output -name "*.md" -ls
```

### 4. So sánh số lượng

```bash
# Đếm file gốc
find . -name "*.pdf" -o -name "*.doc" -o -name "*.docx" | wc -l

# Đếm file .md
find markdown_output -name "*.md" | wc -l

# Nên bằng nhau (trừ file lỗi)
```

---

## � Cấu trúc Project

```
DatasetDataset/
├── convert_all.py           ← Script chính (dùng cái này)
├── README_CONVERSION.md     ← Hướng dẫn chi tiết
├── QUICK_START.md          ← File này (hướng dẫn nhanh)
├── conversion.log          ← Log file (tự động tạo)
│
├── 2009/                   ← Data gốc
│   ├── *.pdf
│   └── *.md               ← File đã convert (nếu có)
│
├── 2019/
│   └── *.pdf
│
├── 2022/
│   ├── *.doc
│   ├── *.docx             ← Tự động tạo từ .doc
│   └── *.pdf
│
└── markdown_output/        ← Output folder (tự động tạo)
    ├── 2009/
    │   └── *.md
    ├── 2019/
    │   └── *.md
    └── 2022/
        └── *.md
```

---

## � Workflow hoàn chỉnh

### Lần đầu tiên:

```bash
# 1. Cài đặt dependencies
pip install pymupdf4llm python-docx pypandoc
sudo apt-get install libreoffice

# 2. Kiểm tra
python convert_all.py --help

# 3. Convert tất cả
python convert_all.py

# 4. Kiểm tra kết quả
find markdown_output -name "*.md" -ls
cat conversion.log
```

### Lần sau (có thêm file mới):

```bash
# Chỉ cần chạy lại, tự động skip file cũ
python convert_all.py

# Hoặc force convert lại tất cả
python convert_all.py --no-skip
```

---

## 🎯 Use Cases thực tế

### Case 1: Bạn có 100 file PDF cần convert

```bash
python convert_all.py
# Xong! Tất cả PDF → MD trong markdown_output/
```

### Case 2: Bạn có mix PDF + DOC + DOCX

```bash
# Cài LibreOffice trước
sudo apt-get install libreoffice

# Convert tất cả
python convert_all.py
# Script tự động: .doc → .docx → .md
```

### Case 3: Convert từng folder riêng

```bash
# Convert folder 2009
python convert_all.py --input 2009 --output markdown/2009

# Convert folder 2022
python convert_all.py --input 2022 --output markdown/2022
```

### Case 4: Chỉ có DOCX (không có .doc)

```bash
# Bỏ qua bước convert .doc
python convert_all.py --skip-doc-conversion
```

---

## 📊 Kết quả thực tế (Test)

**Dataset của bạn:**
- 3 file PDF năm 2009 ✅
- 3 file PDF năm 2019 ✅
- 1 file PDF năm 2022 ✅
- 9 file DOC năm 2022 ✅ (đã convert sang DOCX)

**Kết quả:**
```
✅ Converted 9/9 .doc files to .docx
✅ Converted 16/16 documents to Markdown
📂 Output: markdown_output/ (giữ nguyên cấu trúc)
```

---

## ✅ Checklist

- [ ] Đã cài Python packages: `pymupdf4llm`, `python-docx`
- [ ] Đã cài LibreOffice (nếu có file .doc)
- [ ] Đã test: `python convert_all.py --help`
- [ ] Đã chạy conversion: `python convert_all.py`
- [ ] Đã check output: `ls markdown_output/`
- [ ] Đã xem log: `cat conversion.log`
- [ ] Ready cho Data Mining! 🎉

---

## 🆘 Cần giúp đỡ?

1. **Xem log chi tiết**: `cat conversion.log`
2. **Xem hướng dẫn đầy đủ**: `README_CONVERSION.md`
3. **Test với 1 file**: Convert thử 1 file trước
4. **Check dependencies**: `python convert_all.py` sẽ tự động báo thiếu gì

---

## 🎓 Giải thích cho người mới

### Markdown (.md) là gì?

- Định dạng văn bản đơn giản, dễ đọc
- Dùng ký tự đặc biệt: `#` (heading), `**` (bold), `*` (italic)
- Dễ xử lý bằng Python cho Data Mining
- Ví dụ:

```markdown
# Tiêu đề
## Tiêu đề nhỏ
**Chữ đậm**
*Chữ nghiêng*
- Danh sách
```

### Tại sao convert sang Markdown?

1. **Dễ xử lý**: Text thuần, không có format phức tạp
2. **Nhẹ**: File nhỏ hơn PDF/DOC
3. **Tương thích**: Mọi tool đều đọc được
4. **Data Mining**: Dễ extract text, phân tích

### Script làm gì?

1. **Đọc** file PDF/DOC/DOCX
2. **Trích xuất** text, bảng, format
3. **Chuyển đổi** sang Markdown
4. **Lưu** vào folder mới

---

**Tạo bởi**: Enhanced Document Converter  
**Ngày**: 2026-01-04  
**Version**: 2.0  
**Status**: ✅ Production Ready

---

## 🚀 Quick Commands

```bash
# Cài đặt
pip install pymupdf4llm python-docx pypandoc
sudo apt-get install libreoffice

# Convert tất cả
python convert_all.py

# Check kết quả
find markdown_output -name "*.md" | wc -l
cat conversion.log

# Xem file markdown
cat markdown_output/2009/baocao_T10_2009_Final.md
```

**Chúc bạn thành công với Data Mining! 🎉**
