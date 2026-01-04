# 🎯 CHEAT SHEET - Document to Markdown Converter

## ⚡ Quick Start (3 bước)

```bash
# 1. Cài đặt (chỉ làm 1 lần)
pip install pymupdf4llm python-docx pypandoc
sudo apt-get install libreoffice

# 2. Convert tất cả
python convert_all.py

# 3. Check kết quả
ls markdown_output/
```

---

## 📝 Commands thường dùng

```bash
# Convert tất cả (default)
python convert_all.py

# Convert folder cụ thể
python convert_all.py --input ./2022

# Output vào folder khác
python convert_all.py --output ./my_output

# Force convert lại tất cả
python convert_all.py --no-skip

# Bỏ qua .doc conversion
python convert_all.py --skip-doc-conversion

# Xem help
python convert_all.py --help
```

---

## 🔍 Check kết quả

```bash
# Đếm file .md
find markdown_output -name "*.md" | wc -l

# List tất cả file
find markdown_output -name "*.md"

# Xem dung lượng
du -sh markdown_output/

# Xem log
cat conversion.log

# Xem file lỗi
grep "Failed" conversion.log
```

---

## 🆘 Fix lỗi nhanh

```bash
# Lỗi: pymupdf4llm not found
pip install pymupdf4llm

# Lỗi: python-docx not found
pip install python-docx

# Lỗi: LibreOffice not found
sudo apt-get install libreoffice

# Check dependencies
python convert_all.py --help
```

---

## 📂 Cấu trúc

```
Input:  2009/*.pdf, 2022/*.doc, 2022/*.docx
Output: markdown_output/2009/*.md, markdown_output/2022/*.md
Log:    conversion.log
```

---

## ✅ Workflow

```
.doc → LibreOffice → .docx → Python → .md
.docx → Python → .md
.pdf → Python → .md
```

---

**Xem chi tiết: QUICK_START.md**
