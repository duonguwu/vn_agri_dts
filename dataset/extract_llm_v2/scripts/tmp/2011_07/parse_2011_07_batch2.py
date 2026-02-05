import json
import uuid
import os
import re

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
try:
    with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
        REGION_DATA = json.load(f)
except:
    REGION_DATA = {"provinces": {}, "regions": {}}

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[-1]) == 3 and len(parts[0]) <= 3: s = s.replace(",", "")
            elif len(parts[-1]) != 3: s = s.replace(",", ".")
            else: s = s.replace(",", "")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    try: return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", 
        "Trung du và miền núi phía Bắc": "Đông Bắc", "Trung du và miền núi\nphía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "TP.Hồ Chí Minh": "Hồ Chí Minh", "Bà Rịa - Vũng Tà": "Bà Rịa - Vũng Tàu",
        "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
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
    elif "Miền Nam" in norm_loc: geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_rows(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "": rows.append(parts[1:-1])
            elif len(parts) > 1: rows.append(parts)
    return rows

def parse_pl9():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_07_Phuluc_07_2011_PL9.md"
    rows = extract_rows(fpath)
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL9", "source_file": "2011_07_Phuluc_07_2011_PL9.md"}
    records = []
    t_7m_20 = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-20"}
    
    # Indices: 0: TT | 1: Name | 2: Tot | 3: NT Tot | 4: NT Sweet | 5: NT Mix | 6: KT Tot | 7: KT Sea | 8: KT In
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "sản lượng" in name.lower() or "miền" in name.lower() or "tổng" in name.lower() and "tổng số" not in name.lower():
            if "miền" in name.lower(): pass # Keep regions if any
            else: continue
        if name == "" or "Col" in name: continue
        
        gl = "Provincial"
        if "Miền" in name: gl = "Regional"
        
        def add(idx, item, sub=None):
            if idx >= len(row): return
            v = normalize_number(row[idx])
            if v: records.append(create_record(metadata, t_7m_20, name, gl, {"sector": "Fishery", "commodity": item, "sub_item": sub}, {"attribute": "Production", "value": v, "unit": "ton", "data_type": "Actual"}))

        add(2, "Tổng sản lượng")
        add(3, "Sản lượng nuôi trồng", "Tổng số")
        add(4, "Sản lượng nuôi trồng", "Nước ngọt")
        add(5, "Sản lượng nuôi trồng", "Nước mặn, lợ")
        add(6, "Sản lượng khai thác", "Tổng số")
        add(7, "Sản lượng khai thác", "Khai thác biển")
        add(8, "Sản lượng khai thác", "Khai thác nội địa")
        
    return records

def parse_pl10():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_07_Phuluc_07_2011_PL10.md"
    rows = extract_rows(fpath)
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL10", "source_file": "2011_07_Phuluc_07_2011_PL10.md"}
    records = []
    t_month = {"year": 2011, "month": 7, "period_type": "Monthly", "report_date": "2011-07-31"}
    
    diseases = [
        (1, "Vịt", "Cúm gia cầm", "Chết, xử lý"),
        (2, "Vịt", "Cúm gia cầm", "Số ốm"),
        (3, "Gia cầm", "Cúm gia cầm", "Chết, xử lý"),
        (4, "Gia cầm", "Cúm gia cầm", "Số ốm"),
        (5, "Lợn", "Cúm lợn", "Chết, xử lý"),
        (6, "Lợn", "Cúm lợn", "Số ốm"),
        (7, "Lợn", "Dịch tả lợn", "Chết, xử lý"),
        (8, "Lợn", "Dịch tả lợn", "Số ốm"),
        (9, "Lợn", "Đóng dấu", "Chết, xử lý"),
        (10, "Lợn", "Đóng dấu", "Số ốm"),
        (11, "Lợn", "E.coli", "Chết, xử lý"),
        (12, "Lợn", "E.coli", "Số ốm"),
        (13, "Vịt", "E.coli", "Chết, xử lý"),
        (14, "Vịt", "E.coli", "Số ốm"),
        (15, "Lợn", "Phó thương hàn", "Chết, xử lý"),
        (16, "Lợn", "Phó thương hàn", "Số ốm"),
        (17, "Lợn", "Tiêu chảy", "Chết, xử lý"),
        (18, "Lợn", "Tiêu chảy", "Số ốm"),
        (19, "Trâu bò", "Tiêu chảy", "Số ốm"),
        (20, "Gia cầm", "Tụ huyết trùng", "Chết, xử lý"),
        (21, "Gia cầm", "Tụ huyết trùng", "Số ốm"),
        (22, "Lợn", "Tụ huyết trùng", "Chết, xử lý"),
        (23, "Lợn", "Tụ huyết trùng", "Số ốm"),
        (24, "Trâu bò", "Tụ huyết trùng", "Chết, xử lý"),
        (25, "Trâu bò", "Tụ huyết trùng", "Số ốm"),
        (26, "Lợn", "Viêm phổi", "Chết, xử lý"),
        (27, "Lợn", "Viêm phổi", "Số ốm")
    ]
    
    for row in rows:
        if len(row) < 20: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if "Tỉnh" in name or "Thành phố" in name or "Col" in name: continue
        if name == "": continue
        
        gl = "Provincial"
        if "tống số" in name.lower() or "tổng số" in name.lower():
            name = "Cả nước"
            gl = "National"
            
        for d_idx, animal, disease, indicator in diseases:
            val = normalize_number(row[d_idx])
            if val is not None:
                records.append(create_record(metadata, t_month, name, gl, {"sector": "Livestock", "commodity": animal, "disease": disease, "indicator": indicator}, {"attribute": "Heads", "value": val, "unit": "heads", "data_type": "Actual"}))
                
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl9()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL9.json"))
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl10()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL10.json"))
    print("Successfully parsed Batch 2 (PL9, PL10) for July 2011.")
