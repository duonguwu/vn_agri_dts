#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-based Data Extraction for Vietnamese Agricultural Reports
Extracts data from markdown segments and converts to structured JSON
Following schema_improved.json v2.0
"""

import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import csv
import sys
import logging
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts")
# BASE_DIR = Path("D:\\UIT\\aThacSy\\Data Mining\\2. Data Pre-processing\\vn_agri_dts")
SEGMENTS_DIR = BASE_DIR / "segments" / "2009"
OUTPUT_DIR = BASE_DIR / "dataset" / "extract_llm"

# ============================================================================
# MAPPING DICTIONARIES
# ============================================================================

REGION_MAPPING = {
    "Miền Bắc": ("North", "Miền Bắc"),
    "Đông Bắc": ("Northeast", "Đông Bắc"),
    "Tây Bắc": ("Northwest", "Tây Bắc"),
    "Bắc Trung Bộ": ("North_Central", "Bắc Trung Bộ"),
    "D.H Nam Trg Bộ": ("Central_Coast", "Duyên hải Nam Trung Bộ"),
    "Duyên hải Nam Trung Bộ": ("Central_Coast", "Duyên hải Nam Trung Bộ"),
    "Duyên hải Bắc Trung bộ": ("North_Central", "Bắc Trung Bộ"),
    "Tây Nguyên": ("Central_Highlands", "Tây Nguyên"),
    "Đông Nam Bộ": ("Southeast", "Đông Nam Bộ"),
    "ĐBS Cửu Long": ("Mekong_Delta", "Đồng bằng sông Cửu Long"),
    "Đồng bằng sông Cửu Long": ("Mekong_Delta", "Đồng bằng sông Cửu Long"),
    "ĐB sông Hồng": ("Red_River_Delta", "Đồng bằng sông Hồng"),
    "Vùng Đồng bằng sông Hồng": ("Red_River_Delta", "Đồng bằng sông Hồng"),
    "Đồng bằng sông Hồng": ("Red_River_Delta", "Đồng bằng sông Hồng"),
}

COMMODITY_MAPPING = {
    "lúa": "Lúa",
    "ngô": "Ngô",
    "khoai lang": "Khoai lang",
    "k.lang": "Khoai lang",
    "sắn": "Sắn",
    "đậu tương": "Đậu tương",
    "lạc": "Lạc",
    "mía": "Mía",
    "thuốc lá": "Thuốc lá",
    "rau": "Rau",
    "đậu": "Đậu",
    "cà phê": "Cà phê",
    "cao su": "Cao su",
    "gạo": "Gạo",
    "chè": "Chè",
    "hạt điều": "Hạt điều",
    "hạt tiêu": "Hạt tiêu",
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_number(value: str) -> Optional[float]:
    """
    Clean and convert string to number.
    
    Handles Vietnamese number formats:
    - Comma as thousands separator: 1,234,567
    - Period as decimal separator: 123.45
    - Mixed: 1,234.56
    
    Returns None if:
    - Empty or invalid
    - Contains multiple numbers (concatenated string)
    - Contains non-numeric characters (except comma, period, minus)
    """
    if not value or not isinstance(value, str):
        return None
    
    # Remove markdown formatting
    value = re.sub(r'\*\*|~~|_|<br>', '', value)
    value = value.strip()
    
    if value == "" or value == "-":
        return None
    
    # === VALIDATION: Prevent parsing concatenated strings ===
    # Check if contains multiple separate numbers (e.g., "123 456" or "123  456")
    # This prevents parsing "76,786 39,600" as one number
    if re.search(r'\d\s+\d', value):
        logger.debug(f"Skipped concatenated numbers: '{value}'")
        return None
    
    # Check if contains letters (except for scientific notation 'e')
    if re.search(r'[a-df-zA-DF-Z]', value):
        logger.debug(f"Skipped non-numeric value: '{value}'")
        return None
    
    # === PARSING ===
    try:
        # Remove all spaces
        value = value.replace(' ', '')
        
        # Determine format based on comma/period positions
        has_comma = ',' in value
        has_period = '.' in value
        
        if has_comma and has_period:
            # Mixed format: determine which is decimal separator
            # In Vietnamese: comma is thousands, period is decimal
            # Example: 1,234.56 → 1234.56
            comma_pos = value.rfind(',')
            period_pos = value.rfind('.')
            
            if period_pos > comma_pos:
                # Period is decimal separator: 1,234.56
                value = value.replace(',', '')  # Remove thousands separator
            else:
                # Comma is decimal separator (rare): 1.234,56
                value = value.replace('.', '').replace(',', '.')
        
        elif has_comma:
            # Only comma: could be thousands separator or decimal
            # Vietnamese format uses comma as thousands separator
            # Check pattern:
            # - If all parts after first comma have exactly 3 digits → thousands
            # - If last part has 1-2 digits → likely decimal
            # - If last part has 3 digits but there are multiple commas → thousands
            parts = value.split(',')
            
            if len(parts) == 2:
                # Single comma
                last_part_len = len(parts[1])
                if last_part_len == 3 and len(parts[0]) <= 3:
                    # Could be either: 123,456 or 1,234
                    # In Vietnamese data, this is THOUSANDS separator
                    value = value.replace(',', '')
                elif last_part_len <= 2:
                    # Decimal: 123,45 → 123.45
                    value = value.replace(',', '.')
                else:
                    # Default to thousands
                    value = value.replace(',', '')
            else:
                # Multiple commas → definitely thousands separator
                # 1,234,567
                value = value.replace(',', '')
        
        elif has_period:
            # Only period: assume decimal separator
            # 123.45 → 123.45 (keep as is)
            pass
        
        # Convert to float
        result = float(value)
        
        # === SANITY CHECK ===
        # Agricultural data should be reasonable
        # Max area in Vietnam: ~10 million ha
        # Max production: ~100 million tons
        # If value > 1 billion, likely parsing error
        if result > 1_000_000_000:
            logger.warning(f"Suspiciously large value: {result} from '{value}' - likely parsing error")
            return None
        
        return result
        
    except (ValueError, AttributeError) as e:
        logger.debug(f"Failed to parse number: '{value}' - {e}")
        return None

def clean_text(text: str) -> str:
    """Clean text from markdown formatting"""
    if not text:
        return ""
    text = re.sub(r'\*\*|~~|_|<br>', '', text)
    return text.strip()

def clean_location_name(location: str) -> Optional[str]:
    """
    Clean location_name from common extraction errors
    
    Handles 11 types of errors:
    1. Number prefixes (1., 2., 3., ...)
    2. Bullet prefixes (+, -, ‐)
    3. Space in word (e.g., "mi ền nam" -> "miền nam")
    4. Typo spacing (no space between words)
    5. Trailing numbers (e.g., "miền nam1,926.2" -> "miền nam")
    6. Empty parentheses ()
    7. Unclosed parentheses
    8. Multiple spaces
    9. Only numbers (invalid)
    10. Metadata keywords (invalid)
    11. Single character/Roman numerals (invalid)
    
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
    
    # 3. Fix common space-in-word patterns (Vietnamese specific)
    # Common patterns found in error analysis
    location = re.sub(r'đ\s+ậu', 'đậu', location)
    location = re.sub(r'mi\s+ền', 'miền', location)
    location = re.sub(r'trung\s+bộ', 'trung bộ', location)
    location = re.sub(r'nam\s+bộ', 'nam bộ', location)
    location = re.sub(r'tây\s+nguyên', 'tây nguyên', location)
    location = re.sub(r'đông\s+bắc', 'đông bắc', location)
    location = re.sub(r'tây\s+bắc', 'tây bắc', location)
    location = re.sub(r'cả\s+nước', 'cả nước', location)
    location = re.sub(r'rau,?\s*đ\s+ậu', 'rau, đậu', location)
    
    # 4. Fix typo spacing - detect common concatenated words
    # This is harder without a dictionary, but we can fix known patterns
    location = re.sub(r'miềnnam', 'miền nam', location, flags=re.IGNORECASE)
    location = re.sub(r'miềnbắc', 'miền bắc', location, flags=re.IGNORECASE)
    location = re.sub(r'trungbộ', 'trung bộ', location, flags=re.IGNORECASE)
    location = re.sub(r'tâynguyên', 'tây nguyên', location, flags=re.IGNORECASE)
    location = re.sub(r'đôngbắc', 'đông bắc', location, flags=re.IGNORECASE)
    location = re.sub(r'tâybắc', 'tây bắc', location, flags=re.IGNORECASE)
    
    # 5. Remove trailing numbers (e.g., "miền nam1,926.2" -> "miền nam")
    location = re.sub(r'[\d,\.]+$', '', location)
    
    # 6. Fix empty parentheses
    location = re.sub(r'\(\s*\)', '', location)
    
    # 7. Fix unclosed parentheses
    location = re.sub(r'\([^)]*$', '', location)
    
    # 8. Remove multiple spaces
    location = re.sub(r'\s{2,}', ' ', location)
    
    # 9. Trim again after all cleaning
    location = location.strip()
    
    # === VALIDATION ===
    
    # 10. Skip if empty after cleaning
    if not location or len(location) < 2:
        if original != location:
            logger.debug(f"Skipped (too short after cleaning): '{original}' -> '{location}'")
        return None
    
    # 11. Skip if only numbers
    if location.replace('.', '').replace(',', '').isdigit():
        logger.debug(f"Skipped (only numbers): '{original}'")
        return None
    
    # 12. Skip if contains metadata keywords (column headers)
    # Only skip if it's MOSTLY metadata, not if metadata is part of valid location
    # Example: "Diện tích" = skip, but "Gieo trồng rau, đậu các loại" = keep
    metadata_only_keywords = [
        'diện tích', 'năng suất', 'sản lượng', 'dt gieo', 'dt cho',
        'dt gieo trồng', 'dt cho sản phẩm', 'tạ/ha', '1000 ha',
        'trong đó:', 'chia ra:'
    ]
    location_lower = location.lower()
    
    # Check if location is ONLY metadata (exact match or very similar)
    if location_lower in metadata_only_keywords:
        logger.debug(f"Skipped (exact metadata match): '{original}'")
        return None
    
    # Check if location starts with metadata keywords (likely a header)
    if any(location_lower.startswith(kw) for kw in metadata_only_keywords):
        logger.debug(f"Skipped (starts with metadata): '{original}'")
        return None
    
    # Skip if it's a concatenated header (multiple keywords together, no spaces)
    # Example: "BôngDiện  tíchNăng suấtSản lượng"
    if len(location) > 50 and any(kw in location_lower for kw in ['diện tích', 'năng suất', 'sản lượng']):
        logger.debug(f"Skipped (concatenated metadata): '{original}'")
        return None
    
    # 13. Skip if Roman numerals (extend to longer patterns)
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 
                      'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX']
    if location.upper() in roman_numerals:
        logger.debug(f"Skipped (Roman numeral): '{original}'")
        return None
    
    # 14. Skip common invalid patterns
    # Skip if starts with number (after cleaning, shouldn't happen but double-check)
    if location[0].isdigit():
        logger.debug(f"Skipped (starts with number): '{original}'")
        return None
    
    # Log successful cleaning if changed
    if original != location:
        logger.debug(f"Cleaned location: '{original}' -> '{location}'")
    
    return location

# ============================================================================
# UNIVERSAL TEXT PARSING UTILITIES
# ============================================================================

def extract_components_from_text(text: str) -> Dict[str, Optional[str]]:
    """
    Extract structured components from complex Vietnamese text.
    
    Handles patterns like:
    - "Gieo cấy lúa đông xuân cả nước" → location="Cả nước", commodity="Lúa", sub_item="Đông Xuân"
    - "Thu hoạch lúa đông xuân ở miền Nam" → location="Miền Nam", commodity="Lúa", attribute="Area_Harvested"
    - "Gieo trồng màu lương thực" → commodity="Màu lương thực", location="Cả nước"
    
    Returns:
        dict with keys: location, commodity, sub_item, attribute, action
    """
    if not text:
        return {"location": None, "commodity": None, "sub_item": None, "attribute": None, "action": None}
    
    text_lower = text.lower()
    result = {
        "location": None,
        "commodity": None,
        "sub_item": None,
        "attribute": "Area_Planted",  # default
        "action": None
    }
    
    # === 1. DETECT ACTION & ATTRIBUTE ===
    if "thu hoạch" in text_lower or "dtth" in text_lower:
        result["action"] = "Thu hoạch"
        result["attribute"] = "Area_Harvested"
    elif "gieo cấy" in text_lower or "gieo trồng" in text_lower:
        result["action"] = "Gieo cấy"
        result["attribute"] = "Area_Planted"
    elif "sản lượng" in text_lower:
        result["attribute"] = "Production"
    elif "năng suất" in text_lower:
        result["attribute"] = "Yield"
    
    # === 2. EXTRACT LOCATION ===
    # Pattern: "... ở [location]" or "... [location]" at the end
    location_patterns = [
        r'ở\s+(miền\s+(?:bắc|nam))',
        r'ở\s+(đồng\s+bằng\s+sông\s+cửu\s+long)',
        r'ở\s+([\w\s]+)$',  # "ở [location]" at end
        r'(cả\s+nước)',
        r'(miền\s+(?:bắc|nam))',
        r'(vùng\s+[\w\s]+)',
        r'(đồng\s+bằng\s+sông\s+(?:cửu\s+long|hồng))',
        r'(đông\s+bắc|tây\s+bắc|tây\s+nguyên|đông\s+nam\s+bộ)',
        r'(bắc\s+trung\s+bộ|nam\s+trung\s+bộ)',
        r'(duyên\s+hải\s+[\w\s]+)',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text_lower)
        if match:
            location_raw = match.group(1).strip()
            # Capitalize properly
            location_clean = clean_location_name(location_raw.title())
            if location_clean:
                result["location"] = location_clean
                break
    
    # If no location found, default to "Cả nước" for summary rows
    if not result["location"]:
        result["location"] = "Cả nước"
    
    # === 3. EXTRACT COMMODITY & SUB_ITEM ===
    # Check for specific commodities with sub-items
    if "lúa" in text_lower:
        result["commodity"] = "Lúa"
        if "đông xuân" in text_lower:
            result["sub_item"] = "Đông Xuân"
        elif "hè thu" in text_lower or "hạ thu" in text_lower:
            result["sub_item"] = "Hè Thu"
        elif "mùa" in text_lower:
            result["sub_item"] = "Mùa"
    elif "màu lương thực" in text_lower or "cây màu" in text_lower:
        result["commodity"] = "Màu lương thực"
    elif "công nghiệp ngắn ngày" in text_lower:
        result["commodity"] = "Cây công nghiệp ngắn ngày"
    elif "rau" in text_lower and "đậu" in text_lower:
        result["commodity"] = "Rau đậu"
    elif "ngô" in text_lower:
        result["commodity"] = "Ngô"
    elif "khoai lang" in text_lower or "k.lang" in text_lower:
        result["commodity"] = "Khoai lang"
    elif "sắn" in text_lower:
        result["commodity"] = "Sắn"
    elif "đậu tương" in text_lower:
        result["commodity"] = "Đậu tương"
    elif "lạc" in text_lower:
        result["commodity"] = "Lạc"
    elif "mía" in text_lower:
        result["commodity"] = "Mía"
    elif "cà phê" in text_lower:
        result["commodity"] = "Cà phê"
    elif "cao su" in text_lower:
        result["commodity"] = "Cao su"
    elif "chè" in text_lower:
        result["commodity"] = "Chè"
    elif "hạt điều" in text_lower:
        result["commodity"] = "Hạt điều"
    elif "hạt tiêu" in text_lower:
        result["commodity"] = "Hạt tiêu"
    
    return result

def detect_table_type(first_column_samples: List[str]) -> str:
    """
    Detect table type based on first column content.
    
    Returns:
        - "SUMMARY": PL1 type (complex descriptions with actions)
        - "PROVINCIAL": PL2-5 type (location names only)
    """
    if not first_column_samples:
        return "PROVINCIAL"
    
    # Check if first column contains action verbs (summary table)
    action_keywords = ["gieo cấy", "gieo trồng", "thu hoạch", "chăm sóc", "trồng"]
    
    for sample in first_column_samples[:5]:  # Check first 5 rows
        sample_lower = sample.lower() if sample else ""
        if any(keyword in sample_lower for keyword in action_keywords):
            return "SUMMARY"
    
    return "PROVINCIAL"

def parse_header_for_commodity(header: str) -> Dict[str, Optional[str]]:
    """
    Parse column header to extract commodity and attribute.
    
    Examples:
        "Diện tích gieo cấy lúa đông xuân" → commodity="Lúa", sub_item="Đông Xuân", attribute="Area_Planted"
        "Diện tích mạ đã gieo" → commodity="Lúa", attribute="Area_Seedling"
        "Ngô" → commodity="Ngô", attribute="Area_Planted"
        "Năng suất" → attribute="Yield"
    """
    result = {
        "commodity": None,
        "sub_item": None,
        "attribute": "Area_Planted",  # default
        "unit": "ha"  # default
    }
    
    if not header:
        return result
    
    header_lower = header.lower()
    
    # Detect attribute (order matters - check specific before general)
    if "mạ" in header_lower or "mạ đã gieo" in header_lower:
        # Seedling area (for rice)
        result["attribute"] = "Area_Seedling"
        result["commodity"] = "Lúa"  # Mạ is always for rice
    elif "thu hoạch" in header_lower or "dtth" in header_lower:
        result["attribute"] = "Area_Harvested"
    elif "gieo cấy" in header_lower or "gieo trồng" in header_lower or "dt gieo" in header_lower:
        result["attribute"] = "Area_Planted"
    elif "sản lượng" in header_lower:
        result["attribute"] = "Production"
        result["unit"] = "ton"
    elif "năng suất" in header_lower:
        result["attribute"] = "Yield"
        result["unit"] = "ton_per_ha"
    elif "%" in header or "tỷ lệ" in header_lower:
        result["attribute"] = "Percentage"
        result["unit"] = "percent"
    
    # Detect commodity (same logic as extract_components_from_text)
    # Skip if already set (e.g., for mạ)
    if not result["commodity"]:
        for key, mapped_commodity in COMMODITY_MAPPING.items():
            if key in header_lower:
                result["commodity"] = mapped_commodity
                break
    
    # Detect sub_item
    if "đông xuân" in header_lower:
        result["sub_item"] = "Đông Xuân"
    elif "hè thu" in header_lower or "hạ thu" in header_lower:
        result["sub_item"] = "Hè Thu"
    elif "mùa" in header_lower:
        result["sub_item"] = "Mùa"
    
    return result

def generate_record_id(year: int, month: int, location: str, sector: str, 
                       commodity: str, attribute: str, data_type: str) -> str:
    """Generate unique record ID using random UUID"""
    return str(uuid.uuid4())

def detect_geo_level(location_name: str) -> str:
    """Detect geographic level from location name"""
    if "**" in location_name or location_name.startswith("Miền") or \
       location_name.startswith("Vùng") or "Đồng bằng" in location_name:
        return "Regional"
    elif location_name == "Cả nước":
        return "National"
    else:
        return "Provincial"

def parse_filename(filename: str) -> Dict[str, Any]:
    """Extract metadata from filename"""
    # Example: 2009_03_PHULUC_T03_2009_FINAL_PL1.md
    parts = filename.replace('.md', '').split('_')
    
    year = int(parts[0])
    month = int(parts[1])
    appendix = parts[-1]  # PL1, PL2, etc.
    
    return {
        "year": year,
        "month": month,
        "appendix": appendix,
        "filename": filename
    }

# ============================================================================
# MARKDOWN TABLE PARSER
# ============================================================================

def parse_markdown_table(content: str) -> Tuple[List[str], List[List[str]]]:
    """Parse markdown table into headers and rows"""
    lines = content.strip().split('\n')
    
    # Find table start
    table_lines = []
    in_table = False
    for line in lines:
        if '|' in line:
            in_table = True
            table_lines.append(line)
        elif in_table and line.strip() == "":
            break
    
    if len(table_lines) < 3:
        return [], []
    
    # Parse header
    header_line = table_lines[0]
    headers = [clean_text(h) for h in header_line.split('|')[1:-1]]

    # Skip separator line (line with ---)
    # Parse data rows
    data_rows = []
    for line in table_lines[2:]:
        if '---' in line:
            continue
        cells = [clean_text(c) for c in line.split('|')[1:-1]]
        if cells and any(cells):  # Skip empty rows
            data_rows.append(cells)
    
    return headers, data_rows

# ============================================================================
# APPENDIX-SPECIFIC EXTRACTORS
# ============================================================================

class PL1Extractor:
    """Extract data from PL1 - Tổng hợp sản xuất nông nghiệp"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        for row_idx, row in enumerate(rows):
            if len(row) < 4:
                continue
            
            row_text = row[0]
            
            # Skip header-like rows
            if not row_text or row_text.lower() in ["stt", "tt", "col1"]:
                continue
            
            # === USE UNIVERSAL TEXT PARSER ===
            components = extract_components_from_text(row_text)
            
            location_name = components["location"]
            commodity = components["commodity"]
            sub_item = components["sub_item"]
            attribute = components["attribute"]
            
            # Skip if no valid location or commodity
            if not location_name or not commodity:
                logger.debug(f"PL1: Skipped row {row_idx + 1}: location='{location_name}', commodity='{commodity}', text='{row_text}'")
                continue
            
            # Skip grouping rows
            if row_text.startswith("Chia ra") or row_text.startswith("Trong đó"):
                continue
            
            # Detect geo level
            geo_level = detect_geo_level(location_name)
            is_aggregated = geo_level in ["Regional", "National"]
            
            # Map region
            region_id, region_name_vn = None, None
            for key, (rid, rname) in REGION_MAPPING.items():
                if key in location_name:
                    region_id = rid
                    region_name_vn = rname
                    break
            
            # Extract values from columns (skip column 1 which is description)
            for col_idx in range(2, min(len(row), 4)):
                value = clean_number(row[col_idx])
                if value is None:
                    continue
                
                # Determine data type and year from column
                data_type = "Actual"
                if col_idx == 2:
                    # Column 2: Previous year (15/02/08)
                    record_year = year - 1
                else:
                    # Column 3: Current year (15/02/09)
                    record_year = year
                
                record = {
                    "record_id": generate_record_id(record_year, month, location_name, 
                                                    "Cultivation", commodity, 
                                                    attribute, data_type),
                    "time_context": {
                        "year": record_year,
                        "month": month,
                        "report_date": f"{record_year}-{month:02d}-15",
                        "period_type": "Seasonal" if sub_item else "Monthly"
                    },
                    "geo_context": {
                        "geo_level": geo_level,
                        "location_name": location_name,
                        "region_id": region_id,
                        "region_name_vn": region_name_vn
                    },
                    "item_context": {
                        "sector": "Cultivation",
                        "commodity": commodity,
                        "sub_item": sub_item,
                        "variety": None,
                        "processing_level": "Raw"
                    },
                    "metric_context": {
                        "attribute": attribute,
                        "value": value,
                        "unit": "1000_ha",
                        "data_type": data_type
                    },
                    "comparison_context": {
                        "comparison_type": "None",
                        "comparison_value": None,
                        "base_period": None,
                        "base_value": None
                    },
                    "metadata": {
                        "source_file": metadata['filename'],
                        "appendix_number": metadata['appendix'],
                        "appendix_title": "TỔNG HỢP KẾT QUẢ SẢN XUẤT NÔNG NGHIỆP",
                        "table_index": 1,
                        "row_number": row_idx + 1,
                        "extraction_method": "LLM_Extraction",
                        "extraction_confidence": 0.90,
                        "notes": f"Original text: {row_text}"
                    },
                    "data_quality": {
                        "is_aggregated": is_aggregated,
                        "has_missing_values": False,
                        "data_status": "Complete"
                    }
                }
                
                records.append(record)
        
        return records


class CultivationExtractor:
    """Extract data from PL2-5 - Cultivation data"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        appendix = metadata['appendix']
        
        # Detect title to determine commodity and sub_item
        title_match = re.search(r'\*\*(.*?)\*\*', content)
        title = title_match.group(1) if title_match else ""
        
        # Determine main commodity and sub_item from title
        main_commodity = "Lúa"
        sub_item = None
        
        if "ĐÔNG XUÂN" in title.upper():
            sub_item = "Đông Xuân"
        elif "HÈ THU" in title.upper():
            sub_item = "Hè Thu"
        elif "MÙA" in title.upper():
            sub_item = "Mùa"
        
        # Check if first row is actually a second header row (contains commodity names)
        # This happens when table has multi-row headers
        actual_headers = headers
        start_row_idx = 0
        
        if rows and len(rows) > 0:
            first_row = rows[0]
            # Check if first row contains header-like content (e.g., "Trong đó:", commodity names)
            if any("trong đó" in str(cell).lower() or 
                   "diện tích" in str(cell).lower()
                   for cell in first_row if cell):
                # First row is a sub-header, check if row 1 has actual commodity names
                if len(rows) > 1:
                    second_row = rows[1]
                    if any("ngô" in str(cell).lower() or 
                           "khoai" in str(cell).lower() or
                           "sắn" in str(cell).lower() or
                           "đậu" in str(cell).lower() or
                           "lạc" in str(cell).lower()
                           for cell in second_row if cell):
                        # Row 1 has commodity names - use it as header
                        actual_headers = second_row
                        start_row_idx = 2  # Start from row 2
                    else:
                        # Row 0 is the header
                        actual_headers = first_row
                        start_row_idx = 1
        
        for row_idx, row in enumerate(rows[start_row_idx:], start=start_row_idx):
            if len(row) < 2:
                continue
            
            location_name = clean_location_name(row[0])
            
            # Skip if location is invalid
            if not location_name:
                logger.warning(f"Cultivation: Skipped invalid location at row {row_idx + 1}: '{row[0]}'")
                continue
            
            if location_name in ["STT", "Tỉnh", "Địa phương", "Vùng/Tỉnh"]:
                continue
            
            # Skip summary rows
            if "Tổng" in location_name or "Cộng" in location_name:
                continue
            
            # Detect geo level (improved)
            geo_level = detect_geo_level(location_name)
            is_aggregated = geo_level in ["Regional", "National"]
            
            # Map region
            region_id, region_name_vn = None, None
            for key, (rid, rname) in REGION_MAPPING.items():
                if key in location_name:
                    region_id = rid
                    region_name_vn = rname
                    break
            
            # Process each column (commodity/attribute)
            for col_idx in range(1, len(row)):
                value = clean_number(row[col_idx])
                if value is None:
                    continue
                
                # === USE UNIVERSAL HEADER PARSER ===
                header = actual_headers[col_idx] if col_idx < len(actual_headers) else ""
                header_info = parse_header_for_commodity(header)
                
                # Use parsed info, fallback to main_commodity if not found in header
                commodity = header_info["commodity"] or main_commodity
                attribute = header_info["attribute"]
                unit = header_info["unit"]
                header_sub_item = header_info["sub_item"]
                
                # Use sub_item from header if available, otherwise from title
                final_sub_item = header_sub_item or sub_item
                
                # === SKIP AGGREGATED/PARENT COLUMNS ===
                header_lower = header.lower()
                
                # Skip "Trong đó:" columns (these are parent headers)
                if "trong đó" in header_lower and len(header) < 15:
                    logger.debug(f"Skipped parent column: '{header}'")
                    continue
                
                # Skip aggregated commodity columns that have sub-columns
                # Example: "Diện tích gieo trồng màu" is parent of "Ngô", "Khoai lang", "Sắn"
                aggregated_commodities = [
                    "màu lương thực", "cây màu",
                    "công nghiệp ngắn ngày", "cây công nghiệp"
                ]
                
                is_aggregated_column = False
                for agg_comm in aggregated_commodities:
                    if agg_comm in header_lower:
                        # Check if next columns have specific commodities (sub-columns)
                        has_sub_columns = False
                        for next_idx in range(col_idx + 1, min(col_idx + 5, len(actual_headers))):
                            next_header = actual_headers[next_idx].lower() if next_idx < len(actual_headers) else ""
                            # If next columns have specific commodities, this is a parent
                            if any(comm in next_header for comm in ["ngô", "khoai", "sắn", "đậu tương", "lạc", "cây khác"]):
                                has_sub_columns = True
                                break
                        
                        if has_sub_columns:
                            is_aggregated_column = True
                            logger.debug(f"Skipped aggregated column: '{header}' (has sub-columns)")
                            break
                
                if is_aggregated_column:
                    continue
                
                record = {
                    "record_id": generate_record_id(year, month, location_name, 
                                                    "Cultivation", commodity, 
                                                    attribute, "Actual"),
                    "time_context": {
                        "year": year,
                        "month": month,
                        "report_date": f"{year}-{month:02d}-15",
                        "period_type": "Seasonal" if final_sub_item else "Monthly"
                    },
                    "geo_context": {
                        "geo_level": geo_level,
                        "location_name": location_name,
                        "region_id": region_id,
                        "region_name_vn": region_name_vn
                    },
                    "item_context": {
                        "sector": "Cultivation",
                        "commodity": commodity,
                        "sub_item": final_sub_item,
                        "variety": None,
                        "processing_level": "Raw"
                    },
                    "metric_context": {
                        "attribute": attribute,
                        "value": value,
                        "unit": unit,
                        "data_type": "Actual"
                    },
                    "comparison_context": {
                        "comparison_type": "None",
                        "comparison_value": None,
                        "base_period": None,
                        "base_value": None
                    },
                    "metadata": {
                        "source_file": metadata['filename'],
                        "appendix_number": metadata['appendix'],
                        "appendix_title": title,
                        "table_index": 1,
                        "row_number": row_idx + 1,
                        "extraction_method": "LLM_Extraction",
                        "extraction_confidence": 0.85,
                        "notes": None
                    },
                    "data_quality": {
                        "is_aggregated": is_aggregated,
                        "has_missing_values": False,
                        "data_status": "Complete"
                    }
                }
                
                records.append(record)
        
        return records


class ForestryExtractor:
    """Extract data from PL6 - Lâm nghiệp"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        for row_idx, row in enumerate(rows):
            if len(row) < 5:
                continue
            
            # Skip header rows
            if row[0] in ["TT", "A"]:
                continue
            
            indicator_name = clean_text(row[1])
            if not indicator_name:
                continue
            
            # Determine commodity and attribute
            commodity = "Rừng"
            attribute = "Area"
            unit = "1000_ha"
            
            if "Trồng rừng" in indicator_name:
                attribute = "Area_Planted"
                if "phòng hộ" in indicator_name.lower():
                    commodity = "Rừng phòng hộ"
                elif "sản xuất" in indicator_name.lower():
                    commodity = "Rừng sản xuất"
            elif "Chăm sóc" in indicator_name:
                attribute = "Area"
                commodity = "Rừng trồng"
            elif "Khai thác gỗ" in indicator_name:
                attribute = "Production"
                commodity = "Gỗ"
                unit = "1000_m3"
            elif "cây nhân dân" in indicator_name.lower():
                attribute = "Area_Planted"
                commodity = "Cây nhân dân"
                unit = "million_trees"
            elif "Khoanh nuôi" in indicator_name:
                attribute = "Area"
                commodity = "Rừng tái sinh"
            elif "Khoán bảo vệ" in indicator_name:
                attribute = "Area"
                commodity = "Rừng bảo vệ"
            
            # Extract actual value (current period)
            if len(row) > 5:
                value = clean_number(row[5])
                if value is not None:
                    record = {
                        "record_id": generate_record_id(year, month, "Cả nước", 
                                                        "Forestry", commodity, 
                                                        attribute, "Actual"),
                        "time_context": {
                            "year": year,
                            "month": month,
                            "report_date": f"{year}-{month:02d}-15",
                            "period_type": "Monthly"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Forestry",
                            "commodity": commodity,
                            "sub_item": None,
                            "variety": None,
                            "processing_level": "Raw"
                        },
                        "metric_context": {
                            "attribute": attribute,
                            "value": value,
                            "unit": unit,
                            "data_type": "Estimated"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "TÌNH HÌNH THỰC HIỆN LÂM NGHIỆP",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.88,
                            "notes": None
                        },
                        "data_quality": {
                            "is_aggregated": True,
                            "has_missing_values": False,
                            "data_status": "Estimated"
                        }
                    }
                    records.append(record)
            
            # Plan value
            if len(row) > 3:
                plan_value = clean_number(row[3])
                if plan_value is not None:
                    record = {
                        "record_id": generate_record_id(year, month, "Cả nước", 
                                                        "Forestry", commodity, 
                                                        attribute, "Plan"),
                        "time_context": {
                            "year": year,
                            "month": month,
                            "report_date": f"{year}-{month:02d}-15",
                            "period_type": "Monthly"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Forestry",
                            "commodity": commodity,
                            "sub_item": None,
                            "variety": None,
                            "processing_level": "Raw"
                        },
                        "metric_context": {
                            "attribute": attribute,
                            "value": plan_value,
                            "unit": unit,
                            "data_type": "Plan"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "TÌNH HÌNH THỰC HIỆN LÂM NGHIỆP",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.88,
                            "notes": None
                        },
                        "data_quality": {
                            "is_aggregated": True,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
        
        return records


class TradeExtractor:
    """Extract data from PL8 - Xuất nhập khẩu"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        for row_idx, row in enumerate(rows):
            if len(row) < 5:
                continue
            
            # Skip header rows and section markers
            if row[0] in ["Chỉ tiêu", "A"] or "XUẤT KHẨU" in row[0] or "NHẬP KHẨU" in row[0]:
                continue
            
            commodity_name = clean_text(row[0])
            if not commodity_name:
                continue
            
            # Skip total rows
            if "Tổng" in commodity_name or "kim ngạch" in commodity_name.lower():
                continue
            
            # Process month 1 - Volume and Value
            if len(row) > 4:
                # Volume (column 3)
                volume = clean_number(row[3])
                if volume is not None:
                    record = {
                        "record_id": generate_record_id(year, 1, "Cả nước", 
                                                        "Trade", commodity_name, 
                                                        "Export_Volume", "Actual"),
                        "time_context": {
                            "year": year,
                            "month": 1,
                            "report_date": f"{year}-01-31",
                            "period_type": "Monthly"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": commodity_name,
                            "sub_item": "Xuất khẩu",
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": "Export_Volume",
                            "value": volume,
                            "unit": "1000_ton",
                            "data_type": "Actual"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "TÌNH HÌNH XUẤT, NHẬP KHẨU NÔNG LÂM THUỶ SẢN",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.80,
                            "notes": None
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
                
                # Value (column 4)
                value_usd = clean_number(row[4])
                if value_usd is not None:
                    record = {
                        "record_id": generate_record_id(year, 1, "Cả nước", 
                                                        "Trade", commodity_name, 
                                                        "Export_Value", "Actual"),
                        "time_context": {
                            "year": year,
                            "month": 1,
                            "report_date": f"{year}-01-31",
                            "period_type": "Monthly"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": commodity_name,
                            "sub_item": "Xuất khẩu",
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": "Export_Value",
                            "value": value_usd,
                            "unit": "million_USD",
                            "data_type": "Actual"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "TÌNH HÌNH XUẤT, NHẬP KHẨU NÔNG LÂM THUỶ SẢN",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.80,
                            "notes": None
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
        
        return records


class InvestmentExtractor:
    """Extract data from PL9 - Đầu tư XDCB"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        for row_idx, row in enumerate(rows):
            if len(row) < 5:
                continue
            
            # Skip header rows
            if row[0] in ["TT", "A"] or row[1] in ["B", "Danh mục"]:
                continue
            
            category_name = clean_text(row[1])
            if not category_name or category_name == "":
                continue
            
            commodity = category_name
            attribute = "Investment_Amount"
            unit = "million_VND"
            
            # Plan value
            if len(row) > 2:
                plan_value = clean_number(row[2])
                if plan_value is not None:
                    record = {
                        "record_id": generate_record_id(year, month, "Cả nước", 
                                                        "Investment", commodity, 
                                                        attribute, "Plan"),
                        "time_context": {
                            "year": year,
                            "month": month,
                            "report_date": f"{year}-{month:02d}-15",
                            "period_type": "YTD"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Investment",
                            "commodity": commodity,
                            "sub_item": None,
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": attribute,
                            "value": plan_value,
                            "unit": unit,
                            "data_type": "Plan"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "BÁO CÁO THỰC HIỆN KẾ HOẠCH ĐẦU TƯ XDCB",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.90,
                            "notes": None
                        },
                        "data_quality": {
                            "is_aggregated": "Tổng" in commodity or "Vốn" in commodity,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
            
            # Actual value (cumulative)
            if len(row) > 5:
                actual_value = clean_number(row[5])
                if actual_value is not None:
                    record = {
                        "record_id": generate_record_id(year, month, "Cả nước", 
                                                        "Investment", commodity, 
                                                        attribute, "Cumulative"),
                        "time_context": {
                            "year": year,
                            "month": month,
                            "report_date": f"{year}-{month:02d}-28",
                            "period_type": "Cumulative"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Investment",
                            "commodity": commodity,
                            "sub_item": None,
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": attribute,
                            "value": actual_value,
                            "unit": unit,
                            "data_type": "Cumulative"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "BÁO CÁO THỰC HIỆN KẾ HOẠCH ĐẦU TƯ XDCB",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.90,
                            "notes": None
                        },
                        "data_quality": {
                            "is_aggregated": "Tổng" in commodity or "Vốn" in commodity,
                            "has_missing_values": False,
                            "data_status": "Estimated"
                        }
                    }
                    records.append(record)
        
        return records


class TradeAnnualExtractor:
    """Extract data from PL10 - Xuất nhập khẩu cả năm (December only)"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        # Track if we're in export or import section
        current_section = "Export"
        
        for row_idx, row in enumerate(rows):
            if len(row) < 7:
                continue
            
            # Detect section markers
            if "XUẤT KHẨU" in row[0]:
                current_section = "Export"
                continue
            elif "NHẬP KHẨU" in row[0]:
                current_section = "Import"
                continue
            
            # Skip header and total rows
            if row[0] in ["Chỉ tiêu", "A"] or "Tổng kim ngạch" in row[0]:
                continue
            
            commodity_name = clean_text(row[0])
            if not commodity_name or commodity_name == "":
                continue
            
            # Extract annual data (columns 9-10: Ước TH cả năm 2009)
            if len(row) > 10:
                # Volume
                volume = clean_number(row[9])
                if volume is not None:
                    attribute = "Export_Volume" if current_section == "Export" else "Import_Volume"
                    sub_item = "Xuất khẩu" if current_section == "Export" else "Nhập khẩu"
                    
                    record = {
                        "record_id": generate_record_id(year, 12, "Cả nước", 
                                                        "Trade", commodity_name, 
                                                        attribute, "Annual"),
                        "time_context": {
                            "year": year,
                            "month": 12,
                            "report_date": f"{year}-12-31",
                            "period_type": "Annual"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": commodity_name,
                            "sub_item": sub_item,
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": attribute,
                            "value": volume,
                            "unit": "1000_ton",
                            "data_type": "Estimated"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "TÌNH HÌNH XUẤT, NHẬP KHẨU TOÀN NGÀNH",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.85,
                            "notes": "Annual estimate"
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Estimated"
                        }
                    }
                    records.append(record)
                
                # Value
                value_usd = clean_number(row[10])
                if value_usd is not None:
                    attribute = "Export_Value" if current_section == "Export" else "Import_Value"
                    sub_item = "Xuất khẩu" if current_section == "Export" else "Nhập khẩu"
                    
                    record = {
                        "record_id": generate_record_id(year, 12, "Cả nước", 
                                                        "Trade", commodity_name, 
                                                        attribute, "Annual"),
                        "time_context": {
                            "year": year,
                            "month": 12,
                            "report_date": f"{year}-12-31",
                            "period_type": "Annual"
                        },
                        "geo_context": {
                            "geo_level": "National",
                            "location_name": "Cả nước",
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": commodity_name,
                            "sub_item": sub_item,
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": attribute,
                            "value": value_usd,
                            "unit": "million_USD",
                            "data_type": "Estimated"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "TÌNH HÌNH XUẤT, NHẬP KHẨU TOÀN NGÀNH",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.85,
                            "notes": "Annual estimate"
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Estimated"
                        }
                    }
                    records.append(record)
        
        return records


class ExportMarketExtractor:
    """Extract data from PL11 - Thị trường xuất khẩu (December only)"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        current_commodity = None
        
        for row_idx, row in enumerate(rows):
            if len(row) < 6:
                continue
            
            # Detect commodity header rows (col[0] is empty, col[1] has commodity name)
            if (not row[0] or row[0].strip() == "") and row[1] and row[1].strip():
                # Skip actual header row
                if "Mặt hàng" in row[1] or "Tên nước" in row[1]:
                    continue
                current_commodity = clean_text(row[1])
                continue
            
            # Skip header rows and rows without country name
            if row[0] in ["Thứ tự", ""] or not row[1]:
                continue
            
            country_name = clean_text(row[1])
            if not country_name or country_name == "":
                continue
            
            # Extract 11 months 2009 data (columns 4-5)
            if len(row) > 5 and current_commodity:
                # Volume
                volume = clean_number(row[4])
                if volume is not None:
                    record = {
                        "record_id": generate_record_id(year, 11, country_name, 
                                                        "Trade", current_commodity, 
                                                        "Export_Volume", "YTD"),
                        "time_context": {
                            "year": year,
                            "month": 11,
                            "report_date": f"{year}-11-30",
                            "period_type": "YTD"
                        },
                        "geo_context": {
                            "geo_level": "International",
                            "location_name": country_name,
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": current_commodity,
                            "sub_item": "Xuất khẩu",
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": "Export_Volume",
                            "value": volume,
                            "unit": "ton",
                            "data_type": "Actual"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "THỊ TRƯỜNG XUẤT KHẨU CHÍNH",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.88,
                            "notes": f"Export to {country_name}"
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
                
                # Value
                value_usd = clean_number(row[5])
                if value_usd is not None:
                    record = {
                        "record_id": generate_record_id(year, 11, country_name, 
                                                        "Trade", current_commodity, 
                                                        "Export_Value", "YTD"),
                        "time_context": {
                            "year": year,
                            "month": 11,
                            "report_date": f"{year}-11-30",
                            "period_type": "YTD"
                        },
                        "geo_context": {
                            "geo_level": "International",
                            "location_name": country_name,
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": current_commodity,
                            "sub_item": "Xuất khẩu",
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": "Export_Value",
                            "value": value_usd,
                            "unit": "1000_USD",
                            "data_type": "Actual"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "THỊ TRƯỜNG XUẤT KHẨU CHÍNH",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.88,
                            "notes": f"Export to {country_name}"
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
        
        return records


class ImportSourceExtractor:
    """Extract data from PL12 - Nguồn nhập khẩu (December only)"""
    
    @staticmethod
    def extract(content: str, metadata: Dict) -> List[Dict]:
        records = []
        headers, rows = parse_markdown_table(content)
        
        if not rows or not headers:
            return records
        
        year = metadata['year']
        month = metadata['month']
        
        current_commodity = None
        
        for row_idx, row in enumerate(rows):
            if len(row) < 6:
                continue
            
            # Detect commodity header rows (col[0] is empty, col[1] has commodity name)
            if (not row[0] or row[0].strip() == "") and row[1] and row[1].strip():
                # Skip actual header row
                if "Mặt hàng" in row[1] or "Tên nước" in row[1]:
                    continue
                current_commodity = clean_text(row[1])
                continue
            
            # Skip header rows and rows without country name
            if row[0] in ["Thứ tự", ""] or not row[1]:
                continue
            
            country_name = clean_text(row[1])
            if not country_name or country_name == "":
                continue
            
            # Extract 11 months 2009 data (columns 4-5)
            if len(row) > 5 and current_commodity:
                # Volume
                volume = clean_number(row[4])
                if volume is not None:
                    record = {
                        "record_id": generate_record_id(year, 11, country_name, 
                                                        "Trade", current_commodity, 
                                                        "Import_Volume", "YTD"),
                        "time_context": {
                            "year": year,
                            "month": 11,
                            "report_date": f"{year}-11-30",
                            "period_type": "YTD"
                        },
                        "geo_context": {
                            "geo_level": "International",
                            "location_name": country_name,
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": current_commodity,
                            "sub_item": "Nhập khẩu",
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": "Import_Volume",
                            "value": volume,
                            "unit": "ton",
                            "data_type": "Actual"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "NGUỒN NHẬP KHẨU CHÍNH",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.88,
                            "notes": f"Import from {country_name}"
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
                
                # Value
                value_usd = clean_number(row[5])
                if value_usd is not None:
                    record = {
                        "record_id": generate_record_id(year, 11, country_name, 
                                                        "Trade", current_commodity, 
                                                        "Import_Value", "YTD"),
                        "time_context": {
                            "year": year,
                            "month": 11,
                            "report_date": f"{year}-11-30",
                            "period_type": "YTD"
                        },
                        "geo_context": {
                            "geo_level": "International",
                            "location_name": country_name,
                            "region_id": None,
                            "region_name_vn": None
                        },
                        "item_context": {
                            "sector": "Trade",
                            "commodity": current_commodity,
                            "sub_item": "Nhập khẩu",
                            "variety": None,
                            "processing_level": None
                        },
                        "metric_context": {
                            "attribute": "Import_Value",
                            "value": value_usd,
                            "unit": "1000_USD",
                            "data_type": "Actual"
                        },
                        "comparison_context": {
                            "comparison_type": "None",
                            "comparison_value": None,
                            "base_period": None,
                            "base_value": None
                        },
                        "metadata": {
                            "source_file": metadata['filename'],
                            "appendix_number": metadata['appendix'],
                            "appendix_title": "NGUỒN NHẬP KHẨU CHÍNH",
                            "table_index": 1,
                            "row_number": row_idx + 1,
                            "extraction_method": "LLM_Extraction",
                            "extraction_confidence": 0.88,
                            "notes": f"Import from {country_name}"
                        },
                        "data_quality": {
                            "is_aggregated": False,
                            "has_missing_values": False,
                            "data_status": "Complete"
                        }
                    }
                    records.append(record)
        
        return records


# ============================================================================
# MAIN EXTRACTION ORCHESTRATOR
# ============================================================================

def extract_from_file(filepath: Path) -> List[Dict]:
    """Extract data from a single markdown file"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = parse_filename(filepath.name)
    appendix = metadata['appendix']
    
    # Route to appropriate extractor
    if appendix == "PL1":
        return PL1Extractor.extract(content, metadata)
    elif appendix in ["PL2", "PL3", "PL4", "PL5"] or appendix.startswith("PL2") or appendix.startswith("PL3") or appendix.startswith("PL4") or appendix.startswith("PL5"):
        return CultivationExtractor.extract(content, metadata)
    elif appendix == "PL6" or appendix.startswith("PL6"):
        return ForestryExtractor.extract(content, metadata)
    elif appendix == "PL7":
        # PL7 not in all months
        return []
    elif appendix == "PL8" or appendix.startswith("PL8"):
        return TradeExtractor.extract(content, metadata)
    elif appendix == "PL9" or appendix.startswith("PL9"):
        return InvestmentExtractor.extract(content, metadata)
    # December-specific appendices
    elif appendix == "PL10":
        return TradeAnnualExtractor.extract(content, metadata)
    elif appendix == "PL11" or appendix.startswith("PL11"):
        return ExportMarketExtractor.extract(content, metadata)
    elif appendix == "PL12" or appendix.startswith("PL12"):
        return ImportSourceExtractor.extract(content, metadata)
    elif appendix == "PL13":
        return InvestmentExtractor.extract(content, metadata)  # Reuse PL9 extractor
    else:
        return []


def extract_month_data(year: int, month: int) -> Dict:
    """Extract all data for a specific month"""
    
    all_records = []
    files_processed = 0
    
    # Dynamic segments directory based on year
    segments_dir = BASE_DIR / "segments" / str(year)
    
    # Find all files for this month
    pattern = f"{year}_{month:02d}_*.md"
    files = sorted(segments_dir.glob(pattern))
    
    print(f"\n{'='*60}")
    print(f"Processing {year}/{month:02d}")
    print(f"{'='*60}")
    print(f"Found {len(files)} files\n")
    
    for filepath in files:
        print(f"Processing: {filepath.name}")
        
        try:
            records = extract_from_file(filepath)
            all_records.extend(records)
            files_processed += 1
            print(f"  ✓ Extracted {len(records)} records")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Create output structure
    output = {
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_records": len(all_records),
            "total_files_processed": files_processed,
            "year": year,
            "month": month,
            "schema_version": "2.0",
            "extraction_method": "LLM_Extraction"
        },
        "records": all_records
    }
    
    return output


def save_outputs(data: Dict, year: int, month: int):
    """Save JSON, CSV, and validation report"""
    
    # Create output directory
    month_dir = OUTPUT_DIR / str(year) / f"{month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = month_dir / f"extracted_data_{year}_{month:02d}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved JSON: {json_file}")
    
    # Save CSV
    csv_file = month_dir / f"extracted_data_{year}_{month:02d}.csv"
    if data['records']:
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'record_id', 'year', 'month', 'location_name', 'geo_level',
                'sector', 'commodity', 'sub_item', 'attribute', 'value', 
                'unit', 'data_type', 'appendix_number'
            ])
            writer.writeheader()
            
            for record in data['records']:
                writer.writerow({
                    'record_id': record['record_id'],
                    'year': record['time_context']['year'],
                    'month': record['time_context']['month'],
                    'location_name': record['geo_context']['location_name'],
                    'geo_level': record['geo_context']['geo_level'],
                    'sector': record['item_context']['sector'],
                    'commodity': record['item_context']['commodity'],
                    'sub_item': record['item_context'].get('sub_item', ''),
                    'attribute': record['metric_context']['attribute'],
                    'value': record['metric_context']['value'],
                    'unit': record['metric_context']['unit'],
                    'data_type': record['metric_context']['data_type'],
                    'appendix_number': record['metadata']['appendix_number']
                })
        print(f"✓ Saved CSV: {csv_file}")
    
    # Save validation report
    report_file = month_dir / f"validation_{year}_{month:02d}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"VALIDATION REPORT - {year}/{month:02d}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Total Records: {data['metadata']['total_records']}\n")
        f.write(f"Files Processed: {data['metadata']['total_files_processed']}\n\n")
        
        # Count by appendix
        by_appendix = {}
        by_sector = {}
        by_commodity = {}
        
        for record in data['records']:
            appendix = record['metadata']['appendix_number']
            sector = record['item_context']['sector']
            commodity = record['item_context']['commodity']
            
            by_appendix[appendix] = by_appendix.get(appendix, 0) + 1
            by_sector[sector] = by_sector.get(sector, 0) + 1
            by_commodity[commodity] = by_commodity.get(commodity, 0) + 1
        
        f.write("Records by Appendix:\n")
        for appendix, count in sorted(by_appendix.items()):
            f.write(f"  {appendix}: {count}\n")
        
        f.write("\nRecords by Sector:\n")
        for sector, count in sorted(by_sector.items()):
            f.write(f"  {sector}: {count}\n")
        
        f.write("\nRecords by Commodity:\n")
        for commodity, count in sorted(by_commodity.items()):
            f.write(f"  {commodity}: {count}\n")
    
    print(f"✓ Saved validation report: {report_file}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Get year and month from command line or use default
    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    else:
        year = 2009
        month = 3  # Default to March 2009
    
    # Extract data
    data = extract_month_data(year, month)
    
    # Save outputs
    save_outputs(data, year, month)
    
    print(f"\n{'='*60}")
    print("EXTRACTION COMPLETE!")
    print(f"{'='*60}")
    print(f"Total records extracted: {data['metadata']['total_records']}")
    print(f"Files processed: {data['metadata']['total_files_processed']}")
