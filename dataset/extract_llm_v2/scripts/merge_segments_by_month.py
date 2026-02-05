#!/usr/bin/env python3
"""
Script merge segments theo tháng
Quét folder segments/{year}/ và gộp các file theo pattern {year}_{month}_*_PL*.md
Output: segment_month/{year}_{month:02d}.md
"""

import os
import re
import glob
from pathlib import Path
from collections import defaultdict

def extract_year_month_from_filename(filename):
    """
    Extract year and month from filename
    Examples:
    - 2009_02_PHULUC_t02_2009_FINAL_PL1.md → (2009, 2)
    - 2009_12_Phuluc_T12_2009_PL15.md → (2009, 12)
    """
    pattern = r'^(\d{4})_(\d{1,2})_'
    match = re.match(pattern, filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year, month
    return None, None

def get_appendix_number(filename):
    """
    Extract appendix number from filename
    Examples:
    - 2009_02_PHULUC_t02_2009_FINAL_PL1.md → PL1
    - 2009_12_Phuluc_T12_2009_PL15.md → PL15
    """
    pattern = r'_PL(\d+[ab]?)\.md$'
    match = re.search(pattern, filename)
    if match:
        return f"PL{match.group(1)}"
    return "Unknown"

def merge_segments_by_month(segments_root, output_root):
    """
    Merge segments by month
    
    Args:
        segments_root: Path to segments folder
        output_root: Path to output segment_month folder
    """
    segments_path = Path(segments_root)
    output_path = Path(output_root)
    
    # Create output directory if not exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Dictionary to group files by year_month
    monthly_files = defaultdict(list)
    
    # Scan all year folders
    for year_folder in segments_path.iterdir():
        if not year_folder.is_dir():
            continue
            
        year = year_folder.name
        print(f"📁 Processing year: {year}")
        
        # Scan all segment files in year folder
        for segment_file in year_folder.glob("*.md"):
            filename = segment_file.name
            file_year, file_month = extract_year_month_from_filename(filename)
            
            if file_year and file_month:
                month_key = f"{file_year}_{file_month:02d}"
                monthly_files[month_key].append({
                    'path': segment_file,
                    'filename': filename,
                    'appendix': get_appendix_number(filename)
                })
    
    # Process each month
    for month_key, files in monthly_files.items():
        print(f"📋 Processing month: {month_key} ({len(files)} files)")
        
        # Sort files by appendix number for consistent order
        files.sort(key=lambda x: x['appendix'])
        
        # Create merged content
        merged_content = []
        merged_content.append(f"# MERGED SEGMENTS - {month_key.upper()}")
        merged_content.append(f"**Tổng hợp các phụ lục tháng {month_key.replace('_', '/')}**")
        merged_content.append("")
        merged_content.append("---")
        merged_content.append("")
        
        # Add table of contents
        merged_content.append("## 📋 **MỤC LỤC**")
        merged_content.append("")
        for file_info in files:
            merged_content.append(f"- **{file_info['appendix']}**: {file_info['filename']}")
        merged_content.append("")
        merged_content.append("---")
        merged_content.append("")
        
        # Merge all files
        for i, file_info in enumerate(files):
            print(f"  📄 Adding {file_info['appendix']}: {file_info['filename']}")
            
            # Add separator
            merged_content.append(f"## **{file_info['appendix']}** - {file_info['filename']}")
            merged_content.append("")
            
            # Read and add file content
            try:
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    merged_content.append(content)
            except Exception as e:
                print(f"  ⚠️  Error reading {file_info['filename']}: {e}")
                merged_content.append(f"**ERROR**: Could not read file - {e}")
            
            merged_content.append("")
            merged_content.append("---")
            merged_content.append("")
        
        # Write merged file
        output_file = output_path / f"{month_key}.md"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(merged_content))
            print(f"  ✅ Saved: {output_file}")
            print(f"  📊 Total appendices: {len(files)}")
        except Exception as e:
            print(f"  ❌ Error saving {output_file}: {e}")
        
        print()

def main():
    """Main function"""
    # Paths
    segments_root = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments"
    output_root = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/segment_month"
    
    print("🚀 Starting segment merge by month...")
    print(f"📂 Input: {segments_root}")
    print(f"📁 Output: {output_root}")
    print()
    
    merge_segments_by_month(segments_root, output_root)
    
    print("✅ Merge completed!")
    
    # Show summary
    output_path = Path(output_root)
    if output_path.exists():
        merged_files = list(output_path.glob("*.md"))
        print(f"📊 Total merged files: {len(merged_files)}")
        for f in sorted(merged_files):
            print(f"  - {f.name}")

if __name__ == "__main__":
    main()