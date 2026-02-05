import json
import uuid
import os
import re

import re

def generate_id():
    return str(uuid.uuid4())

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
try:
    with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
        REGION_DATA = json.load(f)
except:
    REGION_DATA = {"provinces": {}, "regions": {}}

def normalize_number(s):
    if s is None: return None
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    # Remove footnotes or formatting artifacts
    s = s.split("<br>")[0]
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    # Handle European/Vietnamese number format (1.234,56 or 1,234.56)
    if "." in s and "," in s:
        if s.find(".") < s.find(","): # Type 1.234,56 -> remove dot, replace comma
            s = s.replace(".", "").replace(",", ".")
        else: # Type 1,234.56 -> remove comma
            s = s.replace(",", "")
    elif "," in s:
        # If multiple commas, it's thousands sep: 1,234,567 -> remove all
        # If single comma and 3 decimals: 1,234 -> remove (assume int)
        # If single comma and not 3 decimals: 1,2 -> replace with dot
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[-1]) == 3 and len(parts[0]) <= 3: # Ambiguous, context needed, but usually Thousand
                s = s.replace(",", "")
            elif len(parts[-1]) != 3: # Decimal
                s = s.replace(",", ".")
            else: # 1,000 -> 1000
                s = s.replace(",", "") 
    elif "." in s:
         if s.count(".") > 1: s = s.replace(".", "")
    
    try:
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", "Trung du và miền núi\nphía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ và\nduyên hải miền Trung": "Bắc Trung Bộ và Duyên hải miền Trung", "Bắc Trung Bộ và duyên hải miền Trung": "Bắc Trung Bộ và Duyên hải miền Trung",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng", "TP.Hồ Chí Minh": "Hồ Chí Minh", "T.P Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu", "Bà Rịa- Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Tỉnh/Thành phố": "Cả nước", "Cả nước": "Cả nước", "Toàn quốc": "Cả nước",
        "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái",
        "Miền bắc": "Miền Bắc", "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Quảng Bình *": "Quảng Bình", "Quảng Nam *": "Quảng Nam"
    }
    
    loc_clean = loc_name.strip()
    # Remove regex patterns like "1", "I", "II" prefix if stuck to name, though usually separate column
    loc_clean = re.sub(r"^\d+\s", "", loc_clean) # Remove leading numbers
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name_vn"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name_vn"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    elif "Miền Bắc" in norm_loc: geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    elif "Miền Trung" in norm_loc: geo_context["region_id"] = "CENTRAL"; geo_context["region_name_vn"] = "Miền Trung"
    elif "Miền Nam" in norm_loc: geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def extract_rows_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    rows = []
    for line in lines:
        if "|" in line:
            # Clean split
            parts = [p.strip() for p in line.split("|")]
            # Remove empty first/last from markdown pipe table
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "":
                rows.append(parts[1:-1])
            elif len(parts) > 1:
                rows.append(parts)
    return rows

def parse_pl5_full():
    # PL5: Southern Crops (Detailed) - Specialized "Explode" parser for merged cells
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_06_Phuluc_06_2011_PL5.md"
    rows = extract_rows_from_file(fpath)
    
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL5", "source_file": "2011_06_Phuluc_06_2011_PL5.md"}
    records = []
    t = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-15"}
    
    # Structure mapping (0-based index from extracted columns)
    # Col 0: Name (Merged list)
    # Col 1: Tong so (Merged list)
    # ...
    
    for row in rows:
        # Check if this is a data row (must contain merged data or valid single row)
        if len(row) < 11: continue
        
        # Determine if row is "merged" type (has <br>) or "single" type
        # PL5 usually puts ALL data in one massive row after headers
        # We look for the row that starts with "Miền Nam"
        
        raw_name = row[0]
        if "Miền Nam" not in raw_name and "D.H Nam Trg Bộ" not in raw_name: continue
        
        # Explode columns
        # Function to safe split
        def safe_split(s):
            return [x.strip() for x in s.split("<br>")]
            
        cols = [safe_split(c) for c in row]
        
        # The first column (Name) dictates the number of sub-rows
        names = cols[0]
        num_subrows = len(names)
        
        for i in range(num_subrows):
            name_i = names[i].replace("**", "").strip()
            if name_i == "" or "Col" in name_i or "Đơn vị" in name_i: continue
            
            # Determine GL
            gl = "Provincial"
            if name_i in ["Miền Nam", "ĐBS Cửu Long", "Đông Nam Bộ", "Tây Nguyên", "D.H Nam Trg Bộ"]: gl = "Regional"
            
            def get_val(col_idx):
                if col_idx >= len(cols): return None
                col_vals = cols[col_idx]
                if i < len(col_vals):
                    return normalize_number(col_vals[i])
                return None

            def add_rec(commodity, subitem, val):
                if val is not None:
                     records.append(create_record(metadata, t, name_i, gl, {"sector": "Cultivation", "commodity": commodity, "sub_item": subitem}, {"attribute": "Area_Planted", "value": val/1000, "unit": "1000_ha", "data_type": "Actual"}))

            add_rec("Cây công nghiệp ngắn ngày", "Tổng số", get_val(1))
            add_rec("Đậu tương", None, get_val(2))
            add_rec("Lạc", None, get_val(3))
            add_rec("Vừng", None, get_val(4))
            add_rec("Thuốc lá", None, get_val(5))
            add_rec("Mía", "Trồng mới", get_val(6))
            add_rec("Bông", None, get_val(7))
            add_rec("Đay, Cói", None, get_val(8))
            add_rec("Rau các loại", None, get_val(9))
            add_rec("Đậu các loại", None, get_val(10))
            
    return records

def parse_pl6_full():
    # PL6: Disease Full
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_06_Phuluc_06_2011_PL6.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL6", "source_file": "2011_06_Phuluc_06_2011_PL6.md"}
    records = []
    t = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    
    # Indices in extracted list (0-based) based on Step 672 view:
    # Row "Cả nước": |Cả nước|50,347|80,762|140,171|78,277|17,373|42,897|1,624|38,744|14,759|14,158|
    # Note: Column 0 might be TT (if existing).
    # Let's inspect a data row: |2|Vĩnh Phúc|1,500|21,979|||||||||
    # 0: TT (2)
    # 1: Name (Vinh Phuc)
    # 2: Cum Nhiem
    # 3: Cum Huy
    # 4: LMLM Nhiem
    # 5: Trau
    # 6: Bo
    # 7: Lon
    # 8: De
    # 9: LMLM Huy
    # 10: Tai Xanh Nhiem
    # 11: Tai Xanh Huy
    
    for row in rows:
        if len(row) < 12: continue # Ensure minimum length
        
        # Identify Name Column. Usually index 1.
        # Check if index 0 is short (TT)
        name_candidate = row[1].replace("**", "").strip()
        
        # Check if header
        if "Gia súc" in name_candidate or "Tỉnh/Thành" in name_candidate or "Cúm" in name_candidate: continue
        
        # "Cả nước" handling (Usually no TT column or merged?)
        # Row 25 Step 672: ||Cả nước|50,347...
        # So index 0 is empty, index 1 is "Cả nước".
        # Row 26: |I|Đồng bằng sông Hồng|...
        # So structure looks consistent: Col 0 = TT/Code, Col 1 = Name.
        
        loc_name = name_candidate
        if loc_name == "": continue
        
        gl = "Provincial"
        if loc_name in ["Cả nước", "Đồng bằng sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ và duyên hải miền Trung", "Tây Nguyên", "Đông Nam Bộ", "Đồng bằng sông Cửu Long", "Miền Bắc", "Miền Nam"]:
            if loc_name == "Cả nước": gl = "National"
            else: gl = "Regional"
            
        def process_val(idx, comm, indic):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, loc_name, gl, {"sector": "Livestock", "commodity": comm, "indicator": indic}, {"attribute": "Heads", "value": val, "unit": "heads", "data_type": "Actual"}))

        process_val(2, "Gia cầm", "Nhiễm cúm gia cầm")
        process_val(3, "Gia cầm", "Tiêu hủy do cúm gia cầm")
        process_val(4, "Gia súc", "Nhiễm Lở mồm long móng")
        process_val(5, "Trâu", "Nhiễm Lở mồm long móng")
        process_val(6, "Bò", "Nhiễm Lở mồm long móng")
        process_val(7, "Lợn", "Nhiễm Lở mồm long móng")
        process_val(8, "Dê", "Nhiễm Lở mồm long móng") # Col 9 in Step 672 view index 8 
        process_val(9, "Gia súc", "Tiêu hủy do Lở mồm long móng")
        process_val(10, "Lợn", "Nhiễm Tai xanh")
        process_val(11, "Lợn", "Tiêu hủy do Tai xanh")

    return records

def parse_pl8_full():
    # PL8: Forestry Detail
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_06_Phuluc_06_2011_PL8.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL8", "source_file": "2011_06_Phuluc_06_2011_PL8.md"}
    records = []
    t = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    
    # Structure from Step 674:
    # |TT|Col2|Diện tích rừng trồng mới tập trung|Col4|Col5|Diện tích rừng trồng được chăm sóc|Diện tích rừng được khoán bảo vệ|
    # Row "Cả nước": ||Cả nước|53,768|2,852|50,916|261,736|2,088,330|
    # Indices:
    # 0: TT (Empty or numbering)
    # 1: Name
    # 2: Total New
    # 3: PH/DD
    # 4: SX New
    # 5: SX Care
    # 6: SX Protect
    
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "Diện tích" in name or "Tổng số" in name or "Thành phố" in name or "Col" in name: continue
        if name == "": continue
        
        gl = "Provincial"
        if name in ["Cả nước", "Miền bắc", "Miền Bắc", "Miền Nam", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]:
             if name == "Cả nước": gl = "National"
             else: gl = "Regional"

        def process_val(idx, comm, subitem=None):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                 records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": comm, "sub_item": subitem}, {"attribute": "Output", "value": val, "unit": "ha", "data_type": "Estimate"}))

        process_val(2, "Diện tích rừng trồng mới tập trung", "Tổng số")
        process_val(3, "Diện tích rừng trồng mới tập trung", "Rừng phòng hộ, đặc dụng")
        process_val(4, "Diện tích rừng trồng mới tập trung", "Rừng sản xuất")
        process_val(5, "Diện tích rừng trồng được chăm sóc", "Rừng sản xuất")
        process_val(6, "Diện tích rừng được khoán bảo vệ", "Rừng sản xuất")
        
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl5_full()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL5.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl6_full()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl8_full()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL8.json"))
    
    print("Successfully re-parsed full detailed data for PL5, PL6, PL8 (June 2011).")
