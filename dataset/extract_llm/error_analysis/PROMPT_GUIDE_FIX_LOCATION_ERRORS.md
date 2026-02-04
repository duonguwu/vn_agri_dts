# 🎯 CHIẾN LƯỢC FIX LOCATION_NAME ERRORS - PROMPT GUIDE

## 📊 PHÂN TÍCH TÌNH HÌNH

### Top Issues (theo error_summary_by_type.csv):
1. **`typo_spacing`** (97.9% - 39,423 records): Viết liền không có khoảng trắng
   - Ví dụ: `"miềnnam"`, `"trungbộ"`, `"ngắnngày"`
   
2. **`space_in_word`** (96.43% - 38,831 records): Khoảng trắng trong từ
   - Ví dụ: `"mi ền nam"`, `"đ ậu tương"`, `"rau, đ ậu"`

3. **`only_numbers`** (1.99% - 800 records): Location_name chỉ là số
   - Ví dụ: `"1"`, `"1.1"`, `"125869.3"`

4. **`number_prefix`** (0.66% - 267 records): Số thứ tự ở đầu
   - Ví dụ: `"1. Gieo cấy lúa..."`, `"2. Thu hoạch..."`

5. **`minus_prefix`** (0.84% - 337 records): Dấu `-` ở đầu
   - Ví dụ: `"- Miền Nam"`, `"- Khoai lang"`

### Hotspots (theo error_hotspots.csv):
- **100% error rate** ở hầu hết các phụ lục
- Năm 2012, tháng 12, PL9: 38/38 records lỗi `space_in_word`
- Năm 2008-2012, PL1: Hầu hết lỗi `typo_spacing`
- Năm 2009-2010, PL5: Nhiều lỗi `only_numbers`

---

## 🔧 CHIẾN LƯỢC FIX

### **Option 1: Fix tại nguồn (LLM Extraction) - KHUYẾN NGHỊ**
Sửa logic extraction để clean data ngay khi extract từ markdown.

### **Option 2: Post-processing**
Tạo script clean data sau khi đã extract xong.

### **Option 3: Hybrid**
Kết hợp cả 2: Fix một số lỗi phổ biến trong extraction, còn lại post-process.

---

## 📝 PROMPT CHO AI AGENT - OPTION 1 (KHUYẾN NGHỊ)

```markdown
# TASK: Fix Location_Name Errors in LLM Extraction Script

## Context
Tôi có file `extract_data.py` đang extract data từ markdown files. 
Hiện tại có nhiều lỗi trong cột `location_name` đã được phân tích trong các file:
- `error_summary_by_type.csv`: Tổng hợp 11 loại lỗi
- `error_hotspots.csv`: Top sources có error rate cao nhất
- `error_records_detailed.csv`: Chi tiết từng record lỗi

## Objective
Sửa file `extract_data.py` để thêm data cleaning/validation cho `location_name` 
TRƯỚC KHI tạo records, đảm bảo:
1. Loại bỏ số thứ tự đầu dòng (1., 2., 3., ...)
2. Loại bỏ ký hiệu đầu dòng (+, -, ‐)
3. Fix khoảng trắng sai (space trong từ, multiple spaces)
4. Fix typo spacing (viết liền không có space)
5. Validate: Nếu location_name chỉ là số → skip record
6. Loại bỏ số dính vào cuối text
7. Fix dấu ngoặc rỗng/không đóng

## Requirements

### 1. Tạo function `clean_location_name()`
Vị trí: Sau function `clean_text()` (line ~93-98)

```python
def clean_location_name(location: str) -> Optional[str]:
    """
    Clean location_name from common extraction errors
    
    Returns:
        Cleaned location name or None if invalid
    """
    if not location or not isinstance(location, str):
        return None
    
    original = location
    location = location.strip()
    
    # 1. Remove number prefixes (1., 2., 3., ...)
    location = re.sub(r'^\d+\.\s*', '', location)
    
    # 2. Remove bullet prefixes (+, -, ‐)
    location = re.sub(r'^[+\-‐]\s*', '', location)
    
    # 3. Fix space in word (e.g., "mi ền nam" -> "miền nam")
    # Common patterns: "đ ậu", "rau, đ ậu", etc.
    location = re.sub(r'đ\s+ậu', 'đậu', location)
    location = re.sub(r'mi\s+ền', 'miền', location)
    location = re.sub(r'trung\s+bộ', 'trung bộ', location)
    # Add more patterns as needed
    
    # 4. Fix typo spacing (e.g., "miềnnam" -> "miền nam")
    # This is harder - need dictionary or rules
    # For now, detect and flag
    
    # 5. Remove trailing numbers (e.g., "miền nam1,926.2" -> "miền nam")
    location = re.sub(r'\d+\.?\d*$', '', location)
    
    # 6. Fix empty parentheses
    location = re.sub(r'\(\)', '', location)
    
    # 7. Fix unclosed parentheses
    location = re.sub(r'\([^)]*$', '', location)
    
    # 8. Remove multiple spaces
    location = re.sub(r'\s{2,}', ' ', location)
    
    # 9. Trim again
    location = location.strip()
    
    # 10. Validation: Skip if only numbers or too short
    if not location or location.isdigit() or len(location) < 2:
        return None
    
    # 11. Validation: Skip if contains metadata keywords
    metadata_keywords = ['diện tích', 'năng suất', 'sản lượng', 'dt gieo', 'dt cho']
    if any(kw in location.lower() for kw in metadata_keywords):
        return None
    
    # 12. Validation: Skip if single character or Roman numerals
    if len(location) <= 2 and location.upper() in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']:
        return None
    
    return location
```

### 2. Update tất cả extractors
Tìm tất cả các dòng có pattern:
```python
location_name = clean_text(row[X])
```

Thay bằng:
```python
location_name = clean_location_name(row[X])
if not location_name:
    continue  # Skip invalid location
```

Các class cần update:
- `PL1Extractor.extract()` (line ~192)
- `CultivationExtractor.extract()` (line ~370)
- Các extractors khác nếu có

### 3. Add logging
Thêm logging để track số lượng records bị skip:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In clean_location_name():
if original != location:
    logger.debug(f"Cleaned location: '{original}' -> '{location}'")

if location is None:
    logger.warning(f"Skipped invalid location: '{original}'")
```

### 4. Testing
Sau khi fix, chạy lại extraction cho 1 tháng test (ví dụ: 2009/02) và verify:
- Số lượng records có giảm không? (do skip invalid locations)
- Location_name có còn lỗi không?
- Chạy lại EDA script để check

## Files to modify
- `dataset/extract_llm/scripts/extract_data.py`

## Files to reference
- `dataset/extract_llm/error_analysis/location_name_error_analysis/error_summary_by_type.csv`
- `dataset/extract_llm/error_analysis/location_name_error_analysis/error_hotspots.csv`
- `dataset/extract_llm/error_analysis/location_name_error_analysis/unique_error_locations.txt`

## Expected outcome
- Giảm error rate từ ~97% xuống < 5%
- Location_name clean, không có số thứ tự, ký hiệu, typo
- Có log rõ ràng về số records bị skip và lý do

## Notes
- Ưu tiên fix các lỗi phổ biến nhất trước (typo_spacing, space_in_word)
- Có thể cần nhiều iterations để cover hết edge cases
- Sau mỗi lần fix, chạy lại EDA để verify
```

---

## 📝 PROMPT CHO AI AGENT - OPTION 2 (POST-PROCESSING)

```markdown
# TASK: Create Post-Processing Script to Clean Location_Name

## Context
Data đã được extract nhưng có nhiều lỗi trong `location_name`.
Cần tạo script clean data sau khi đã extract.

## Objective
Tạo file `clean_location_data.py` để:
1. Load consolidated CSV files
2. Clean location_name theo rules
3. Re-generate record_id (vì location_name thay đổi)
4. Save cleaned data

## Requirements

### Script structure:
```python
import pandas as pd
import re
from pathlib import Path

def clean_location_name(location: str) -> str:
    # Same logic as Option 1
    pass

def clean_csv_file(input_file: Path, output_file: Path):
    df = pd.read_csv(input_file)
    
    # Clean location_name
    df['location_name_original'] = df['location_name']
    df['location_name'] = df['location_name'].apply(clean_location_name)
    
    # Remove invalid records
    df = df[df['location_name'].notna()]
    
    # Re-generate record_id
    # ... (same logic as extract_data.py)
    
    df.to_csv(output_file, index=False)
    
    print(f"Cleaned {input_file}")
    print(f"  Original: {len(df)} records")
    print(f"  After cleaning: {len(df)} records")

# Process all years
for year in [2009, 2010, 2011, 2012]:
    input_file = f"dataset/extract_llm/{year}/consolidated_{year}.csv"
    output_file = f"dataset/extract_llm/{year}/consolidated_{year}_cleaned.csv"
    clean_csv_file(Path(input_file), Path(output_file))
```

## Files to create
- `dataset/extract_llm/scripts/clean_location_data.py`

## Expected outcome
- 4 file cleaned CSV
- Giảm error rate xuống < 5%
```

---

## 🎯 KHUYẾN NGHỊ

**Nên dùng OPTION 1** vì:
1. ✅ Fix tại nguồn → data sạch ngay từ đầu
2. ✅ Không cần re-process toàn bộ data
3. ✅ Dễ maintain hơn
4. ✅ Tránh duplicate effort

**Workflow đề xuất:**
1. Fix `extract_data.py` theo Option 1
2. Re-run extraction cho 1 tháng test → verify
3. Nếu OK → re-run cho toàn bộ data
4. Chạy lại EDA để confirm

---

## 📋 CHECKLIST

- [ ] Tạo function `clean_location_name()`
- [ ] Update tất cả extractors
- [ ] Add logging
- [ ] Test với 1 tháng
- [ ] Verify bằng EDA
- [ ] Re-run toàn bộ nếu OK
- [ ] Update documentation

---

## 💡 TIPS KHI PROMPT AI AGENT

1. **Chia nhỏ task**: Đừng yêu cầu fix hết 1 lúc
   - Step 1: Tạo function clean
   - Step 2: Update 1 extractor
   - Step 3: Test
   - Step 4: Update các extractors còn lại

2. **Cung cấp context đầy đủ**:
   - Attach error CSV files
   - Attach extract_data.py
   - Show examples cụ thể

3. **Yêu cầu validation**:
   - "Sau khi fix, chạy test với file X"
   - "Log ra số lượng records bị skip"

4. **Iterative approach**:
   - Fix lỗi phổ biến nhất trước
   - Chạy EDA lại
   - Fix tiếp các lỗi còn lại

---

## 🚀 SAMPLE PROMPT (COPY-PASTE READY)

```
Tôi cần fix lỗi trong file extract_data.py để clean location_name.

Context:
- File: dataset/extract_llm/scripts/extract_data.py
- Vấn đề: 97% records có lỗi trong location_name
- Error analysis: dataset/extract_llm/error_analysis/location_name_error_analysis/

Task:
1. Tạo function clean_location_name() để:
   - Remove số thứ tự đầu (1., 2., ...)
   - Remove ký hiệu (+, -, ‐)
   - Fix space trong từ ("đ ậu" -> "đậu")
   - Remove số cuối text ("miền nam123" -> "miền nam")
   - Remove dấu ngoặc rỗng ()
   - Validate: skip nếu chỉ là số hoặc metadata

2. Update PL1Extractor và CultivationExtractor để dùng function này

3. Add logging để track số records bị skip

Yêu cầu:
- Code phải clean, có comments
- Test với 1 file trước khi apply toàn bộ
- Log rõ ràng số lượng cleaned vs skipped

Bắt đầu với Step 1: Tạo function clean_location_name()
```
