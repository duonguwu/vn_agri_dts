import json
import os
import re
from pathlib import Path

# Paths
BASE_DIR = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2")
DATA_DIR = BASE_DIR / "extracted_data"

def extract_date_from_filename(filename):
    """
    Extracts year and month from filename like:
    2009_02_PHULUC_t02_2009_FINAL_PL9.md
    """
    # Pattern: YYYY_MM or YYYY-MM
    match = re.search(r'(\d{4})[_-](\d{2})', filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # Try another common pattern: TMM_YYYY or tMM_YYYY
    match = re.search(r'[tT](\d{2})[_-](\d{4})', filename)
    if match:
        return int(match.group(2)), int(match.group(1))
    
    return None, None

def fix_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        records = data.get('records', [])
        
        for record in records:
            time_ctx = record.get('time_context', {})
            meta = record.get('metadata', {})
            source_file = meta.get('source_file', '')
            
            # Check if year/month is missing
            if not time_ctx.get('year') or not time_ctx.get('month'):
                # Try to extract from metadata's source_file
                f_year, f_month = extract_date_from_filename(source_file)
                
                # If metadata's source_file fails, try the current JSON file's path
                if not f_year or not f_month:
                    f_year, f_month = extract_date_from_filename(file_path.name)
                
                # If still fails, use directory structure (year/month)
                if not f_year or not f_month:
                    # path is .../YEAR/MONTH/filename.json
                    parts = file_path.parts
                    try:
                        # Find the part that looks like a year
                        for p in parts:
                            if re.match(r'^\d{4}$', p):
                                f_year = int(p)
                        # Find the part that looks like a month (usually after year)
                        for p in parts:
                            if re.match(r'^\d{2}$', p):
                                f_month = int(p)
                    except:
                        pass

                if f_year and not time_ctx.get('year'):
                    time_ctx['year'] = f_year
                    updated = True
                if f_month and not time_ctx.get('month'):
                    time_ctx['month'] = f_month
                    updated = True
            
            # Ensure time_context structure is intact
            record['time_context'] = time_ctx

        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

if __name__ == "__main__":
    json_files = list(DATA_DIR.rglob("*.json"))
    print(f"Checking {len(json_files)} JSON files for missing dates...")
    
    fix_count = 0
    for f_path in json_files:
        if fix_json_file(f_path):
            fix_count += 1
            print(f"Fixed: {f_path.relative_to(DATA_DIR)}")
            
    print(f"\nDone! Fixed missing dates in {fix_count} files.")
