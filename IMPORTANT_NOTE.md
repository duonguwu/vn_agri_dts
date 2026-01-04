# ⚠️ LƯU Ý QUAN TRỌNG

## 📁 Cấu trúc Files

Script `convert_all.py` **CẦN** file `doc2md_enhanced.py` để hoạt động!

```
vn_agri_dts/
├── convert_all.py           ← Script chính (gọi doc2md_enhanced.py)
├── doc2md_enhanced.py       ← Script phụ (KHÔNG XÓA!)
├── Report/                  ← Folder chứa documents
└── markdown_output/         ← Output folder (tự động tạo)
```

## ⚠️ KHÔNG XÓA

- ❌ **KHÔNG** xóa `doc2md_enhanced.py`
- ❌ **KHÔNG** xóa `convert_all.py`

Chỉ xóa các file này nếu bạn không dùng nữa:
- ✅ `pdf2md.py` (script cũ, không cần thiết)
- ✅ `doc2docx.py` (helper, đã tích hợp vào convert_all.py)

## 🔄 Workflow

```
convert_all.py
    │
    ├─→ Bước 1: Convert .doc → .docx (LibreOffice)
    │
    └─→ Bước 2: Gọi doc2md_enhanced.py
            │
            └─→ Convert PDF/DOCX → .md
```

## ✅ Cách sử dụng đúng

```bash
# Chỉ cần chạy convert_all.py
python convert_all.py

# Script sẽ tự động:
# 1. Convert .doc → .docx
# 2. Gọi doc2md_enhanced.py để convert → .md
```

## 🎯 Tóm tắt

- **`convert_all.py`**: Script chính, chạy cái này
- **`doc2md_enhanced.py`**: Script phụ, được gọi bởi convert_all.py
- **Quan hệ**: convert_all.py → gọi → doc2md_enhanced.py

**Cả 2 file đều CẦN THIẾT!** ✅
