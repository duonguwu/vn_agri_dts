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

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts")
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
    """Clean and convert string to number"""
    if not value or value.strip() == "":
        return None
    
    # Remove markdown formatting
    value = re.sub(r'\*\*|~~|_|\<br\>', '', value)
    value = value.strip()
    
    if value == "" or value == "-":
        return None
    
    # Remove commas and convert
    try:
        value = value.replace(',', '').replace('.', '')
        # Handle decimal point (last occurrence)
        if ',' in value:
            value = value.replace(',', '.')
        return float(value)
    except:
        return None

def clean_text(text: str) -> str:
    """Clean text from markdown formatting"""
    if not text:
        return ""
    text = re.sub(r'\*\*|~~|_|\<br\>', '', text)
    return text.strip()

def generate_record_id(year: int, month: int, location: str, sector: str, 
                       commodity: str, attribute: str, data_type: str) -> str:
    """Generate unique record ID using MD5 hash"""
    key = f"{year}_{month}_{location}_{sector}_{commodity}_{attribute}_{data_type}"
    return hashlib.md5(key.encode()).hexdigest()[:16]

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
            
            location_raw = row[0]
            location_name = clean_text(location_raw)
            
            if not location_name or location_name.startswith("Chia ra") or \
               location_name.startswith("Trong đó"):
                continue
            
            # Detect geo level
            geo_level = detect_geo_level(location_raw)
            is_aggregated = geo_level in ["Regional", "National"]
            
            # Map region
            region_id, region_name_vn = None, None
            for key, (rid, rname) in REGION_MAPPING.items():
                if key in location_name:
                    region_id = rid
                    region_name_vn = rname
                    break
            
            # Extract commodity from row label
            commodity = None
            sub_item = None
            attribute = "Area_Planted"
            
            if "lúa đông xuân" in location_name.lower():
                commodity = "Lúa"
                sub_item = "Đông Xuân"
                if "Thu hoạch" in location_name:
                    attribute = "Area_Harvested"
            elif "màu lương thực" in location_name.lower():
                commodity = "Màu lương thực"
            elif "công nghiệp ngắn ngày" in location_name.lower():
                commodity = "Cây công nghiệp ngắn ngày"
            elif "rau, đậu" in location_name.lower():
                commodity = "Rau đậu"
            elif "ngô" in location_name.lower():
                commodity = "Ngô"
            elif "khoai lang" in location_name.lower():
                commodity = "Khoai lang"
            elif "sắn" in location_name.lower():
                commodity = "Sắn"
            elif "đậu tương" in location_name.lower():
                commodity = "Đậu tương"
            elif "lạc" in location_name.lower():
                commodity = "Lạc"
            
            # Extract values from columns
            for col_idx in range(2, min(len(row), 4)):
                value = clean_number(row[col_idx])
                if value is None:
                    continue
                
                # Determine data type from column
                data_type = "Actual"
                if col_idx == 2:
                    # Previous year
                    record_year = year - 1
                else:
                    record_year = year
                
                record = {
                    "record_id": generate_record_id(record_year, month, location_name, 
                                                    "Cultivation", commodity or "Unknown", 
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
                        "commodity": commodity or "Unknown",
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
            
            location_name = clean_text(row[0])
            
            if not location_name or location_name in ["STT", "Tỉnh", "Địa phương", "Vùng/Tỉnh"]:
                continue
            
            # Skip summary rows
            if "Tổng" in location_name or "Cộng" in location_name:
                continue
            
            geo_level = "Provincial"
            is_aggregated = False
            
            # Map region (for provincial data, we need external mapping)
            region_id, region_name_vn = None, None
            
            # Process each column (commodity/attribute)
            for col_idx in range(1, len(row)):
                value = clean_number(row[col_idx])
                if value is None:
                    continue
                
                # Determine commodity and attribute from header
                header = actual_headers[col_idx] if col_idx < len(actual_headers) else ""
                commodity = main_commodity
                attribute = "Area_Planted"
                unit = "ha"
                
                if "thu hoạch" in header.lower() or "DTTH" in header:
                    attribute = "Area_Harvested"
                elif "%" in header or "tỷ lệ" in header.lower():
                    attribute = "Harvest_Percentage"
                    unit = "percent"
                elif "sản lượng" in header.lower():
                    attribute = "Production"
                    unit = "ton"
                elif "năng suất" in header.lower():
                    attribute = "Yield"
                    unit = "ton_per_ha"
                
                # Check if header mentions other commodities
                for key, mapped_commodity in COMMODITY_MAPPING.items():
                    if key in header.lower():
                        commodity = mapped_commodity
                        break
                
                # If header is "Trong đó:" or similar, skip (it's a grouping header)
                if "trong đó" in header.lower() and len(header) < 15:
                    continue
                
                record = {
                    "record_id": generate_record_id(year, month, location_name, 
                                                    "Cultivation", commodity, 
                                                    attribute, "Actual"),
                    "time_context": {
                        "year": year,
                        "month": month,
                        "report_date": f"{year}-{month:02d}-15",
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
