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
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "").replace("..", ".")
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts[-1]) == 3: s = s.replace(",", "")
        else: s = s.replace(",", ".")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    
    try:
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐB sông Cửu Long": "Đồng bằng sông Cửu Long",
        "Đồng bằng Sông Hồng": "Đồng bằng sông Hồng", "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "TD và MN": "Đông Bắc", "phía Bắc": "Đông Bắc", "Trung du và MN phía Bắc": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc", "Trung du và miền núi": "Đông Bắc", "miền núi phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam TB": "Duyên hải Nam Trung Bộ", "D.H Nam Trung": "Duyên hải Nam Trung Bộ",
        "Bắc Trung bộ": "Bắc Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông",
        "Hà Nội (mở rộng)": "Hà Nội", "Trung uơng": "Trung ương"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
    loc_clean = re.sub(r"^[+-]\s", "", loc_clean)
    loc_clean = loc_clean.replace("**", "").replace("<br>", "").replace("\n", "").strip()
    
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
    else:
        geo_context["region_id"] = "COUNTRY"; geo_context["region_name_vn"] = norm_loc; geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def extract_rows(fpath):
    if not os.path.exists(fpath): return []
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "": rows.append(parts[1:-1])
            elif len(parts) > 1: rows.append(parts)
    return rows

def parse_pl6():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL6.md"
    metadata = {"year": 2012, "month": 11, "appendix_number": "PL6"}
    records = []
    t_11m = {"year": 2012, "month": 11, "period_type": "Cumulative", "report_date": "2012-11-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("-", "").strip()
        if "Chỉ tiêu" in name or name == "": continue
        val = normalize_number(row[4])
        if val:
            records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Forestry", "commodity": name}, {"attribute": "Value", "value": val, "unit": row[2].strip(), "data_type": "Estimate"}))
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL7.md"
    metadata = {"year": 2012, "month": 11, "appendix_number": "PL7"}
    records = []
    t_11m = {"year": 2012, "month": 11, "period_type": "Cumulative", "report_date": "2012-11-30"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if "Tỉnh/TP" in row[1] or "TT" in row[1] or "Cả nước" in row[1]: continue
        name = row[1].replace("_", "").strip()
        if name == "" or "Miền" in name or name == "Col3": continue
        
        gl = "Provincial"
        if name in ["ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "D.H Nam Trung", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]: gl = "Regional"
        
        def add(idx, comm, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t_11m, name, gl, {"sector": "Forestry", "commodity": comm}, {"attribute": "Area", "value": val, "unit": unit, "data_type": "Actual"}))
        
        add(2, "Diện tích rừng trồng mới tập trung")
        add(6, "Diện tích rừng trồng được chăm sóc")
        add(7, "Diện tích rừng được khoán bảo vệ")
    return records

def parse_pl8():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL8.md"
    metadata = {"year": 2012, "month": 11, "appendix_number": "PL8"}
    records = []
    t_m = {"year": 2012, "month": 11, "period_type": "Monthly", "report_date": "2012-11-30"}
    t_11m = {"year": 2012, "month": 11, "period_type": "Cumulative", "report_date": "2012-11-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").strip()
        if "CHỈ TIÊU" in name or name == "" or name.isdigit(): continue
        vm = normalize_number(row[5])
        v11 = normalize_number(row[6])
        if vm:
            records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"}))
        if v11:
            records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": v11, "unit": "1000_ton", "data_type": "Estimate"}))
    return records

def parse_pl12():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL12.md"
    metadata = {"year": 2012, "month": 11, "appendix_number": "PL12"}
    records = []
    t_11m = {"year": 2012, "month": 11, "period_type": "Cumulative", "report_date": "2012-11-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 9: continue
        name = row[1].replace("**", "").strip()
        if "Danh mục" in name or name == "" or name == "A" or name == "B": continue
        
        v_total = normalize_number(row[8])
        v_in = normalize_number(row[9])
        v_ex = normalize_number(row[10])
        
        if v_total: records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Value", "value": v_total, "unit": "million_VND", "data_type": "Estimate"}))
        if v_in: records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Investment", "commodity": name, "sub_item": "Vốn trong nước"}, {"attribute": "Value", "value": v_in, "unit": "million_VND", "data_type": "Estimate"}))
        if v_ex: records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Investment", "commodity": name, "sub_item": "Vốn ngoài nước"}, {"attribute": "Value", "value": v_ex, "unit": "million_VND", "data_type": "Estimate"}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/11"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 11}, "records": parse_pl6()}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL6.json"))
    save_json({"metadata": {"year": 2012, "month": 11}, "records": parse_pl7()}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL7.json"))
    save_json({"metadata": {"year": 2012, "month": 11}, "records": parse_pl8()}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL8.json"))
    save_json({"metadata": {"year": 2012, "month": 11}, "records": parse_pl12()}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL12.json"))
    
    print("Successfully parsed Batch 2 for November 2012.")
