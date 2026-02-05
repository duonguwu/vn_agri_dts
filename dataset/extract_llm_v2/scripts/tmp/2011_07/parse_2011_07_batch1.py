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
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "Trung uơng": "Trung ương"
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

def parse_pl6():
    # Forestry Summary 7M
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL6", "source_file": "2011_07_Phuluc_07_2011_PL6.md"}
    records = []
    t_7m_11 = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    
    data = [
        ("Diện tích rừng trồng mới tập trung", "1000 ha", 84.2),
        ("Rừng phòng hộ, đặc dụng", "1000 ha", 9.1),
        ("Rừng sản xuất", "1000 ha", 75.1),
        ("Diện tích rừng trồng được chăm sóc", "1000 ha", 273.3),
        ("Số cây lâm nghiệp trồng phân tán", "million_trees", 124.1),
        ("Diện tích rừng được khoanh nuôi tái sinh", "1000 ha", 695.2),
        ("Diện tích rừng được khoán bảo vệ", "1000 ha", 2349.0),
        ("Sản lượng gỗ", "1000 m3", 2349.0)
    ]
    
    for row in data:
        records.append(create_record(metadata, t_7m_11, "Cả nước", "National", {"sector": "Forestry", "commodity": row[0]}, {"attribute": "Output", "value": row[2], "unit": row[1], "data_type": "Estimate"}))
    return records

def parse_pl7():
    # Forestry Details 7M
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_07_Phuluc_07_2011_PL7.md"
    rows = extract_rows(fpath)
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL7", "source_file": "2011_07_Phuluc_07_2011_PL7.md"}
    records = []
    t_7m_11 = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    
    # 0: TT | 1: Name | 2: Total | 3: PH/DD | 4: SX | 5: Care
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "Diện tích" in name or "Tổng số" in name or "Thành phố" in name or "Col" in name or "Chỉ tiêu" in name: continue
        if name == "": continue
        
        gl = "Provincial"
        if name in ["Cả nước", "Miền bắc", "Miền Bắc", "Miền Nam", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", 
                    "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]:
            gl = "National" if name == "Cả nước" else "Regional"
        
        v_tot = normalize_number(row[2])
        v_ph = normalize_number(row[3])
        v_sx = normalize_number(row[4])
        v_care = normalize_number(row[5]) if len(row)>5 else None
        
        if v_tot: records.append(create_record(metadata, t_7m_11, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Tổng số"}, {"attribute": "Output", "value": v_tot, "unit": "ha", "data_type": "Estimate"}))
        if v_ph: records.append(create_record(metadata, t_7m_11, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Rừng phòng hộ, đặc dụng"}, {"attribute": "Output", "value": v_ph, "unit": "ha", "data_type": "Estimate"}))
        if v_sx: records.append(create_record(metadata, t_7m_11, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Rừng sản xuất"}, {"attribute": "Output", "value": v_sx, "unit": "ha", "data_type": "Estimate"}))
        if v_care: records.append(create_record(metadata, t_7m_11, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng được chăm sóc", "sub_item": "Rừng sản xuất"}, {"attribute": "Output", "value": v_care, "unit": "ha", "data_type": "Estimate"}))
        
    return records

def parse_pl8():
    # Fishery Summary 7M
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL8", "source_file": "2011_07_Phuluc_07_2011_PL8.md"}
    records = []
    t_month = {"year": 2011, "month": 7, "period_type": "Monthly", "report_date": "2011-07-31"}
    t_7m = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    
    # 0: TT | 1: Item | 2: 6M | 3: July Est | 4: 7M Est
    data = [
        ("Tổng sản lượng", 527.0, 3039.0),
        ("Sản lượng khai thác", 224.0, 1476.0),
        ("Khai thác biển", 210.0, 1380.0),
        ("Khai thác nội địa", 14.0, 96.0),
        ("Sản lượng nuôi trồng", 303.0, 1563.0)
    ]
    
    for row in data:
        item = row[0]
        records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": row[1], "unit": "1000_ton", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": row[2], "unit": "1000_ton", "data_type": "Estimate"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl6()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl7()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL7.json"))
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl8()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL8.json"))
    print("Successfully parsed Batch 1 (PL6, PL7, PL8) for July 2011.")
