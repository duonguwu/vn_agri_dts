# 📚 Document to Markdown Converter for Data Mining

> Công cụ tự động convert hàng loạt file PDF, DOC, DOCX sang Markdown để phục vụ Data Mining.

---

## 🎯 Tính năng chính

- ✅ **Multi-format support**: PDF, DOC, DOCX → Markdown
- ✅ **Batch processing**: Convert hàng trăm file cùng lúc
- ✅ **Auto conversion**: Tự động .doc → .docx → .md
- ✅ **Structure preservation**: Giữ nguyên cấu trúc thư mục
- ✅ **Smart skip**: Tự động bỏ qua file đã convert
- ✅ **Error handling**: Không crash khi gặp file lỗi
- ✅ **Detailed logging**: Log chi tiết mọi thao tác
- ✅ **Dependency check**: Tự động kiểm tra thiếu gì

---

## ⚡ Quick Start

```bash
# 1. Cài đặt dependencies
pip install pymupdf4llm python-docx pypandoc
sudo apt-get install libreoffice

# 2. Convert tất cả documents
python convert_all.py

# 3. Xem kết quả
ls markdown_output/
```

**Xong!** 🎉 Tất cả file đã được convert sang Markdown.

---

## 📖 Tài liệu

| File | Mô tả |
|------|-------|
| **[QUICK_START.md](QUICK_START.md)** | 📘 Hướng dẫn chi tiết cho người mới |
| **[CHEAT_SHEET.md](CHEAT_SHEET.md)** | ⚡ Quick reference commands |
| **[README_CONVERSION.md](README_CONVERSION.md)** | 🔧 Technical documentation |
| **conversion.log** | 📊 Log file (tự động tạo) |

---

## 🚀 Usage

### Cơ bản

```bash
# Convert tất cả file trong thư mục hiện tại
python convert_all.py
```

### Nâng cao

```bash
# Convert folder cụ thể
python convert_all.py --input ./2022

# Custom output directory
python convert_all.py --output ./my_markdown

# Force reconvert tất cả
python convert_all.py --no-skip

# Skip .doc conversion step
python convert_all.py --skip-doc-conversion
```

---

## 📊 Kết quả

**Input:**
```
DatasetDataset/
├── 2009/
│   ├── baocao_T10_2009_Final.pdf
│   ├── baocao_T11_2009_Final.pdf
│   └── baocao_T12_2009.pdf
├── 2019/
│   ├── Baocao_T08_2019.pdf
│   ├── Baocao_T09_2019.pdf
│   └── Baocao_T10_2019.pdf
└── 2022/
    ├── Baocao_T02_2022.doc
    ├── Baocao_T03_2022.doc
    └── Baocao_T09_2022.pdf
```

**Output:**
```
markdown_output/
├── 2009/
│   ├── baocao_T10_2009_Final.md
│   ├── baocao_T11_2009_Final.md
│   └── baocao_T12_2009.md
├── 2019/
│   ├── Baocao_T08_2019.md
│   ├── Baocao_T09_2019.md
│   └── Baocao_T10_2019.md
└── 2022/
    ├── Baocao_T02_2022.md
    ├── Baocao_T03_2022.md
    └── Baocao_T09_2022.md
```

---

## 🔧 Requirements

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

## 📝 Workflow

```
┌─────────┐
│ .doc    │──→ LibreOffice ──→ .docx ──┐
└─────────┘                             │
                                        ↓
┌─────────┐                      ┌──────────┐
│ .docx   │──→ python-docx ──→   │          │
└─────────┘                      │  Python  │──→ .md
                                 │          │
┌─────────┐                      │ Converter│
│ .pdf    │──→ pymupdf4llm ──→   │          │
└─────────┘                      └──────────┘
```

---

## 🎓 Use Cases

### 1. Data Mining Preprocessing
Convert documents sang format dễ xử lý cho text mining, NLP.

### 2. Document Archive
Chuyển đổi archive documents sang format nhẹ, dễ search.

### 3. Content Migration
Migrate content từ PDF/Word sang Markdown cho website/wiki.

### 4. Batch Processing
Xử lý hàng trăm documents cùng lúc.

---

## 📈 Performance

**Test với dataset thực tế:**
- 📄 16 documents (PDF + DOC + DOCX)
- ⏱️ ~15 giây
- ✅ 100% success rate
- 📊 Giữ nguyên format: headings, tables, lists

---

## ❓ Troubleshooting

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `pymupdf4llm not found` | Chưa cài package | `pip install pymupdf4llm` |
| `LibreOffice not found` | Chưa cài LibreOffice | `sudo apt-get install libreoffice` |
| `.doc conversion failed` | File .doc lỗi | Convert manual sang .docx |
| `Permission denied` | Không có quyền ghi | `chmod +w .` |

**Xem chi tiết:** [QUICK_START.md](QUICK_START.md#troubleshooting)

---

## 🔍 Features Detail

### Auto .doc → .docx Conversion
- Tự động detect file .doc
- Convert sang .docx bằng LibreOffice
- Skip nếu .docx đã tồn tại

### Smart Skip
- Kiểm tra file output đã tồn tại
- Tự động skip để tiết kiệm thời gian
- Option `--no-skip` để force reconvert

### Error Handling
- Không crash khi gặp file lỗi
- Log chi tiết lỗi vào file
- Continue với file tiếp theo

### Structure Preservation
- Giữ nguyên cấu trúc folder
- Tạo subfolder tự động
- Maintain relative paths

---

## 📊 Statistics

Script tự động báo cáo:
- ✅ Số file thành công
- ❌ Số file lỗi
- ⏭️ Số file đã skip
- 📂 Output directory
- ⏱️ Thời gian xử lý

**Example:**
```
============================================================
📊 CONVERSION SUMMARY
============================================================
Total files processed: 18
✅ Success: 16
❌ Failed: 0
⏭️  Skipped: 2
============================================================
```

---

## 🎯 Best Practices

1. **Backup trước khi convert**
   ```bash
   cp -r . ../backup
   ```

2. **Test với sample trước**
   ```bash
   python convert_all.py --input ./sample_folder
   ```

3. **Check log sau khi convert**
   ```bash
   cat conversion.log
   ```

4. **Verify kết quả**
   ```bash
   find markdown_output -name "*.md" | wc -l
   ```

---

## 🤝 Contributing

Nếu bạn muốn cải thiện script:
1. Test với nhiều loại documents
2. Report bugs qua log file
3. Suggest features

---

## 📜 License

MIT License - Free to use for Data Mining projects

---

## 👨‍💻 Author

Created for Data Mining preprocessing tasks at UIT.

**Version**: 2.0  
**Last Updated**: 2026-01-04  
**Status**: ✅ Production Ready

---

## 🚀 Next Steps

Sau khi convert xong:

1. **Text Preprocessing**
   - Tokenization
   - Stop words removal
   - Stemming/Lemmatization

2. **Feature Extraction**
   - TF-IDF
   - Word embeddings
   - Topic modeling

3. **Analysis**
   - Classification
   - Clustering
   - Sentiment analysis

---

## 📞 Support

- 📖 Đọc [QUICK_START.md](QUICK_START.md) cho hướng dẫn chi tiết
- ⚡ Xem [CHEAT_SHEET.md](CHEAT_SHEET.md) cho quick commands
- 📝 Check `conversion.log` cho debugging
- 🔧 Xem [README_CONVERSION.md](README_CONVERSION.md) cho technical details

---

**Happy Data Mining! 🎉📊🔍**
