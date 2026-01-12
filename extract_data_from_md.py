#!/usr/bin/env python3
"""
Script để extract dữ liệu từ các file Markdown đã segment
Sử dụng regex và table parsing để trích xuất dữ liệu theo schema
"""

import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class MarkdownTableExtractor:
    """Class để extract tables từ Markdown files"""
    
    def __init__(self, schema_path: str):
        """Initialize với schema file"""
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        # Mapping tên vùng
        self.region_mapping = {
            "Miền Bắc": "North",
            "Đông Bắc": "Northeast",
            "Tây Bắc": "Northwest",
            "Bắc Trung Bộ": "North_Central",
            "Duyên hải Nam Trung Bộ": "Central_Coast",
            "D.H Nam Trg Bộ": "Central_Coast",
            "Tây Nguyên": "Central_Highlands",
            "Đông Nam Bộ": "Southeast",
            "ĐBS Cửu Long": "Mekong_Delta",
            "Đồng bằng sông Cửu Long": "Mekong_Delta",
            "ĐB sông Hồng": "Red_River_Delta"
        }
        
        # Mapping commodity names
        self.commodity_mapping = {
            "lúa": "Lúa",
            "ngô": "Ngô",
            "khoai lang": "Khoai lang",
            "k.lang": "Khoai lang",
            "sắn": "Sắn",
            "đậu tương": "Đậu tương",
            "lạc": "Lạc",
            "cà phê": "Cà phê",
            "cao su": "Cao su",
            "gạo": "Gạo",
            "chè": "Chè",
            "hạt điều": "Hạt điều",
            "hạt tiêu": "Hạt tiêu",
            "cá": "Cá",
            "tôm": "Tôm",
            "gỗ": "Gỗ"
        }
    
    def generate_record_id(self, record: Dict[str, Any]) -> str:
        """Generate unique record ID"""
        key_parts = [
            str(record['time_context']['year']),
            str(record['time_context']['month']),
            record['geo_context']['location_name'],
            record['item_context']['sector'],
            record['item_context']['commodity'],
            record['metric_context']['attribute'],
            record['metric_context']['data_type']
        ]
        key_string = "_".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def parse_markdown_table(self, md_content: str) -> List[List[str]]:
        """Parse markdown table thành list of lists"""
        lines = md_content.strip().split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            if '|' in line:
                in_table = True
                # Skip separator line
                if re.match(r'\|[\s\-:]+\|', line):
                    continue
                # Parse cells
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty first/last cells
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                table_lines.append(cells)
            elif in_table:
                break
        
        return table_lines
    
    def clean_value(self, value: str) -> Optional[float]:
        """Clean và convert giá trị số"""
        if not value or value.strip() == '':
            return None
        
        # Remove markdown formatting
        value = re.sub(r'[*_~`]', '', value)
        value = re.sub(r'<br>', '', value)
        value = value.strip()
        
        # Remove commas and convert
        value = value.replace(',', '')
        
        try:
            return float(value)
        except ValueError:
            return None
    
    def extract_year_month_from_filename(self, filename: str) -> tuple:
        """Extract year và month từ filename"""
        # Format: 2009_02_PHULUC_t02_2009_FINAL_PL1.md
        match = re.match(r'(\d{4})_(\d{2})_', filename)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None
    
    def extract_appendix_number(self, filename: str) -> str:
        """Extract appendix number từ filename"""
        # Format: 2009_02_PHULUC_t02_2009_FINAL_PL1.md
        match = re.search(r'_PL(\d+[ab]?)\.md', filename)
        if match:
            return f"PL{match.group(1)}"
        return "Unknown"
    
    def extract_title_from_content(self, content: str) -> str:
        """Extract title từ markdown content"""
        lines = content.split('\n')
        for line in lines:
            # Look for bold title
            if line.startswith('**') and line.endswith('**'):
                return line.strip('*').strip()
        return ""
    
    def detect_sector_from_title(self, title: str) -> str:
        """Detect sector từ title"""
        title_lower = title.lower()
        if 'lúa' in title_lower or 'màu' in title_lower or 'rau' in title_lower or 'cây' in title_lower:
            return "Cultivation"
        elif 'thuỷ sản' in title_lower or 'thủy sản' in title_lower:
            return "Fishery"
        elif 'lâm nghiệp' in title_lower or 'rừng' in title_lower:
            return "Forestry"
        elif 'xuất' in title_lower or 'nhập' in title_lower or 'kim ngạch' in title_lower:
            return "Trade"
        elif 'đầu tư' in title_lower:
            return "Investment"
        elif 'báo cáo' in title_lower and 'chấp hành' in title_lower:
            return "Reporting"
        return "Unknown"
    
    def extract_from_segment_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract data từ một segment file"""
        print(f"\n📄 Processing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        year, month = self.extract_year_month_from_filename(file_path.name)
        appendix_num = self.extract_appendix_number(file_path.name)
        title = self.extract_title_from_content(content)
        sector = self.detect_sector_from_title(title)
        
        print(f"   Year: {year}, Month: {month}")
        print(f"   Appendix: {appendix_num}")
        print(f"   Title: {title}")
        print(f"   Sector: {sector}")
        
        # Parse table
        table_data = self.parse_markdown_table(content)
        
        if not table_data or len(table_data) < 2:
            print(f"   ⚠️  No valid table found")
            return []
        
        print(f"   ✓ Found table with {len(table_data)} rows")
        
        # Extract records based on sector
        records = []
        
        if sector == "Cultivation":
            records = self.extract_cultivation_data(table_data, year, month, appendix_num, title, file_path.name)
        elif sector == "Fishery":
            records = self.extract_fishery_data(table_data, year, month, appendix_num, title, file_path.name)
        elif sector == "Trade":
            records = self.extract_trade_data(table_data, year, month, appendix_num, title, file_path.name)
        elif sector == "Forestry":
            records = self.extract_forestry_data(table_data, year, month, appendix_num, title, file_path.name)
        
        print(f"   ✓ Extracted {len(records)} records")
        return records
    
    def extract_cultivation_data(self, table_data: List[List[str]], year: int, month: int, 
                                 appendix_num: str, title: str, source_file: str) -> List[Dict[str, Any]]:
        """Extract cultivation data từ table"""
        records = []
        
        # Detect headers (usually first 1-2 rows)
        headers = table_data[0] if table_data else []
        data_rows = table_data[1:] if len(table_data) > 1 else []
        
        # Simple extraction for now - can be improved with more sophisticated parsing
        for idx, row in enumerate(data_rows):
            if not row or len(row) < 2:
                continue
            
            location_name = row[0].strip('*').strip()
            
            # Skip if location is empty or is a header
            if not location_name or location_name.lower() in ['col1', 'vùng/địa phương']:
                continue
            
            # Determine geo_level
            is_aggregated = '**' in row[0]
            geo_level = "Regional" if is_aggregated else "Provincial"
            
            # Get region info
            region_id = self.region_mapping.get(location_name, None)
            region_name_vn = location_name if is_aggregated else None
            
            # Extract values from remaining columns
            for col_idx in range(1, len(row)):
                value = self.clean_value(row[col_idx])
                if value is None:
                    continue
                
                # Create record
                record = {
                    "time_context": {
                        "year": year,
                        "month": month,
                        "report_date": None,
                        "period_type": "Seasonal"
                    },
                    "geo_context": {
                        "geo_level": geo_level,
                        "location_name": location_name,
                        "region_id": region_id,
                        "region_name_vn": region_name_vn
                    },
                    "item_context": {
                        "sector": "Cultivation",
                        "commodity": "Unknown",  # Need to infer from headers
                        "sub_item": None,
                        "variety": None,
                        "processing_level": "Raw"
                    },
                    "metric_context": {
                        "attribute": "Area",  # Default, should infer from headers
                        "value": value,
                        "unit": "ha",  # Default
                        "data_type": "Actual"
                    },
                    "comparison_context": {
                        "comparison_type": "None",
                        "comparison_value": None,
                        "base_period": None,
                        "base_value": None
                    },
                    "metadata": {
                        "source_file": source_file,
                        "appendix_number": appendix_num,
                        "appendix_title": title,
                        "table_index": 1,
                        "row_number": idx + 2,  # +2 for header row
                        "extraction_method": "Table_Parsing",
                        "extraction_confidence": 0.7,
                        "notes": None
                    },
                    "data_quality": {
                        "is_aggregated": is_aggregated,
                        "has_missing_values": any(self.clean_value(cell) is None for cell in row[1:]),
                        "data_status": "Complete"
                    }
                }
                
                # Generate record ID
                record["record_id"] = self.generate_record_id(record)
                
                records.append(record)
        
        return records
    
    def extract_fishery_data(self, table_data: List[List[str]], year: int, month: int,
                            appendix_num: str, title: str, source_file: str) -> List[Dict[str, Any]]:
        """Extract fishery data"""
        # Similar structure to cultivation
        return []
    
    def extract_trade_data(self, table_data: List[List[str]], year: int, month: int,
                          appendix_num: str, title: str, source_file: str) -> List[Dict[str, Any]]:
        """Extract trade data"""
        return []
    
    def extract_forestry_data(self, table_data: List[List[str]], year: int, month: int,
                             appendix_num: str, title: str, source_file: str) -> List[Dict[str, Any]]:
        """Extract forestry data"""
        return []


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract data from segmented markdown files')
    parser.add_argument('--input-dir', type=str, required=True, help='Directory containing segment files')
    parser.add_argument('--schema', type=str, default='schema_improved.json', help='Schema file path')
    parser.add_argument('--output', type=str, default='extracted_data.json', help='Output JSON file')
    parser.add_argument('--year', type=int, help='Filter by year')
    parser.add_argument('--month', type=int, help='Filter by month')
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = MarkdownTableExtractor(args.schema)
    
    # Find all segment files
    input_path = Path(args.input_dir)
    segment_files = sorted(input_path.glob('*.md'))
    
    print(f"\n🔍 Found {len(segment_files)} segment files in {input_path}")
    
    # Filter by year/month if specified
    if args.year:
        segment_files = [f for f in segment_files if f.name.startswith(f"{args.year}_")]
    if args.month:
        month_str = f"{args.month:02d}"
        segment_files = [f for f in segment_files if f"_{month_str}_" in f.name]
    
    print(f"📊 Processing {len(segment_files)} files after filtering")
    
    # Extract data from all files
    all_records = []
    for file_path in segment_files:
        records = extractor.extract_from_segment_file(file_path)
        all_records.extend(records)
    
    # Save to JSON
    output_data = {
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_records": len(all_records),
            "source_directory": str(input_path),
            "schema_version": "2.0"
        },
        "records": all_records
    }
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Extraction complete!")
    print(f"   Total records: {len(all_records)}")
    print(f"   Output file: {output_path}")
    
    # Also save as CSV for easier viewing
    if all_records:
        csv_path = output_path.with_suffix('.csv')
        # Flatten records for CSV
        flat_records = []
        for record in all_records:
            flat_record = {
                'record_id': record['record_id'],
                'year': record['time_context']['year'],
                'month': record['time_context']['month'],
                'location': record['geo_context']['location_name'],
                'geo_level': record['geo_context']['geo_level'],
                'sector': record['item_context']['sector'],
                'commodity': record['item_context']['commodity'],
                'attribute': record['metric_context']['attribute'],
                'value': record['metric_context']['value'],
                'unit': record['metric_context']['unit'],
                'data_type': record['metric_context']['data_type'],
                'appendix': record['metadata']['appendix_number'],
                'source_file': record['metadata']['source_file']
            }
            flat_records.append(flat_record)
        
        df = pd.DataFrame(flat_records)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"   CSV file: {csv_path}")


if __name__ == '__main__':
    main()
