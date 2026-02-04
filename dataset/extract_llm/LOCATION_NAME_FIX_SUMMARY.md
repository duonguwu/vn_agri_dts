# Location Name Error Fix - Implementation Summary

## Date: 2026-01-25

## Changes Made to `extract_data.py`

### 1. Added Logging Module (Lines 9-24)
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### 2. Added `clean_location_name()` Function (Lines 108-220)

This comprehensive function handles **11 types of location_name errors**:

#### Error Types Fixed:

1. **Number Prefixes** (`1.`, `2.`, `3.`, ...)
   - Pattern: `^\d+\.\s*`
   - Example: `"1. Gieo cấy lúa đông xuân"` → `"Gieo cấy lúa đông xuân"`

2. **Bullet Prefixes** (`+`, `-`, `‐`)
   - Pattern: `^[+\-‐]\s*`
   - Example: `"- Vùng Duyên hải Bắc Trung bộ"` → `"Vùng Duyên hải Bắc Trung bộ"`

3. **Space in Word** (khoảng trắng trong từ)
   - Patterns: `đ\s+ậu`, `mi\s+ền`, `trung\s+bộ`, etc.
   - Example: `"mi ền nam"` → `"miền nam"`
   - Fixed patterns:
     - `đ ậu` → `đậu`
     - `mi ền` → `miền`
     - `trung bộ` → `trung bộ`
     - `nam bộ` → `nam bộ`
     - `tây nguyên` → `tây nguyên`
     - `đông bắc` → `đông bắc`
     - `tây bắc` → `tây bắc`
     - `cả nước` → `cả nước`
     - `rau, đ ậu` → `rau, đậu`

4. **Typo Spacing** (viết liền không có space)
   - Patterns: `miềnnam`, `miềnbắc`, `trungbộ`, etc.
   - Example: `"miềnnam"` → `"miền nam"`
   - Fixed patterns:
     - `miềnnam` → `miền nam`
     - `miềnbắc` → `miền bắc`
     - `trungbộ` → `trung bộ`
     - `tâynguyên` → `tây nguyên`
     - `đôngbắc` → `đông bắc`
     - `tâybắc` → `tây bắc`

5. **Trailing Numbers** (số dính vào cuối text)
   - Pattern: `[\d,\.]+$`
   - Example: `"miền nam1,926.2"` → `"miền nam"`

6. **Empty Parentheses** `()`
   - Pattern: `\(\s*\)`
   - Example: `"3. Gieo trồng màu lương thực()"` → `"Gieo trồng màu lương thực"`

7. **Unclosed Parentheses**
   - Pattern: `\([^)]*$`
   - Example: `"4. Gieo trồng cây công nghiệp ngắn ngày("` → `"Gieo trồng cây công nghiệp ngắn ngày"`

8. **Multiple Spaces**
   - Pattern: `\s{2,}`
   - Example: `"-  Khoai lang"` → `"Khoai lang"`

#### Validation Rules (Skip if Invalid):

9. **Only Numbers** - Skip if location is just numbers
   - Example: `"1"`, `"1.1"`, `"1.2"` → **SKIPPED**

10. **Metadata Keywords** - Skip if contains column/header names
    - Keywords: `diện tích`, `năng suất`, `sản lượng`, `dt gieo`, `dt cho`, etc.
    - Example: `"BôngDiện  tíchNăng suấtSản lượng"` → **SKIPPED**

11. **Single Character/Roman Numerals** - Skip short invalid entries
    - Example: `"I"`, `"II"`, `"III"` → **SKIPPED**

### 3. Updated Extractors

#### PL1Extractor (Lines 299-320)
```python
location_name = clean_location_name(location_raw)

# Skip if location is invalid
if not location_name:
    logger.warning(f"PL1: Skipped invalid location at row {row_idx + 1}: '{location_raw}'")
    continue
```

#### CultivationExtractor (Lines 478-505)
```python
location_name = clean_location_name(row[0])

# Skip if location is invalid
if not location_name:
    logger.warning(f"Cultivation: Skipped invalid location at row {row_idx + 1}: '{row[0]}'")
    continue
```

## Expected Impact

Based on error analysis:

### Before Fix:
- **Total Errors**: 40,265 records (97.9% error rate)
- **Top Error Types**:
  - `typo_spacing`: 39,423 (97.9%)
  - `space_in_word`: 38,831 (96.43%)
  - `only_numbers`: 800 (1.99%)
  - `location_list`: 418 (1.04%)
  - `minus_prefix`: 337 (0.84%)
  - `number_prefix`: 267 (0.66%)

### After Fix (Expected):
- **Error Rate**: < 5%
- **Clean Locations**: All number prefixes, bullet prefixes, spacing issues fixed
- **Invalid Records**: Skipped automatically (logged for review)

## Logging Output

The script now logs:
- **DEBUG**: Each cleaned location (if changed)
- **WARNING**: Each skipped invalid location with reason
- **INFO**: General extraction progress

Example log output:
```
2026-01-25 08:30:15 - DEBUG - Cleaned location: '1. Gieo cấy lúa đông xuân cả nước' -> 'Gieo cấy lúa đông xuân cả nước'
2026-01-25 08:30:15 - DEBUG - Cleaned location: '- Vùng Duyên hải Bắc Trung bộ' -> 'Vùng Duyên hải Bắc Trung bộ'
2026-01-25 08:30:15 - WARNING - PL1: Skipped invalid location at row 5: '1'
2026-01-25 08:30:15 - DEBUG - Skipped (only numbers): '1.1'
```

## Next Steps

1. **Run the extraction script** on a sample month to verify fixes:
   ```bash
   python extract_data.py 2009 3
   ```

2. **Check the logs** for:
   - Number of locations cleaned
   - Number of records skipped
   - Any unexpected patterns

3. **Run EDA again** to verify error rate reduction:
   ```bash
   python eda_location_name_analysis.py
   ```

4. **Iterate if needed**:
   - Add more Vietnamese word patterns if new spacing errors found
   - Adjust metadata keywords list if false positives occur
   - Fine-tune validation rules based on results

## Files Modified

- `dataset/extract_llm/scripts/extract_data.py`
  - Added logging (lines 9-24)
  - Added `clean_location_name()` function (lines 108-220)
  - Updated `PL1Extractor` (lines 299-320)
  - Updated `CultivationExtractor` (lines 478-505)

## Notes

- The function is **conservative** - it skips records when unsure rather than creating bad data
- All skipped records are **logged** so you can review them
- The cleaning is **idempotent** - running it multiple times produces same result
- Vietnamese-specific patterns are based on actual error samples from the error analysis
