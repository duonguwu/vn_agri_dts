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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "Đồng bằng Sông Hồng": "Đồng bằng sông Hồng", "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "TD và MN": "Đông Bắc", "phía Bắc": "Đông Bắc", "Trung du và MN phía Bắc": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung bộ": "Bắc Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "miền bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông",
        "Hà Nội (mở rộng)": "Hà Nội", "Hậ Giangu": "Hậu Giang", "Nih Thậ nun": "Ninh Thuận", "Yê Báin": "Yên Bái", "Trung uơng": "Trung ương"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
    loc_clean = re.sub(r"^[+-]\s", "", loc_clean)
    loc_clean = loc_clean.replace("**", "").replace("*", "").replace("<br>", "").replace("\n", "").replace("_", "").strip()
    # Remove single characters standing alone if it looks like a typo artifact
    if len(loc_clean) == 1 and loc_clean.isalpha(): loc_clean = ""
    
    norm_loc = alias_map.get(loc_clean, loc_clean)
    if norm_loc == "": return None
    
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL6.md"
    metadata = {"year": 2012, "month": 7, "appendix_number": "PL6"}
    records = []
    t_7m = {"year": 2012, "month": 7, "period_type": "Cumulative", "report_date": "2012-07-31"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("-", "").strip()
        if "Chỉ tiêu" in name or name == "": continue
        val = normalize_number(row[4])
        if val:
            rec = create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Forestry", "commodity": name}, {"attribute": "Value", "value": val, "unit": row[2].strip(), "data_type": "Estimate"})
            if rec: records.append(rec)
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL7.md"
    metadata = {"year": 2012, "month": 7, "appendix_number": "PL7"}
    records = []
    t_7m = {"year": 2012, "month": 7, "period_type": "Cumulative", "report_date": "2012-07-31"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").replace("_", "").replace("<br>", " ").strip()
        if "Tỉnh/TP" in name or "Tổng số" in name or name == "": continue
        
        gl = "Provincial"
        if name in ["Cả nước", "Miền bắc", "Miền Nam", "ĐB sông Hồng", "phía Bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng", "Trung du và miền núi phía Bắc"]:
            gl = "Regional"
            if name == "Cả nước": gl = "National"
            
        def add(idx, comm, attr, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx].replace(" ", "").replace(",", "")) # Handles broken numbers like 8 965
            if val:
                rec = create_record(metadata, t_7m, name, gl, {"sector": "Forestry", "commodity": comm}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"})
                if rec: records.append(rec)
        
        add(2, "Diện tích rừng trồng mới tập trung", "Area")
        add(6, "Diện tích rừng trồng được chăm sóc", "Area")
        add(7, "Diện tích rừng được khoán bảo vệ", "Area")
    return records

def parse_pl8():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL8.md"
    metadata = {"year": 2012, "month": 7, "appendix_number": "PL8"}
    records = []
    t_m = {"year": 2012, "month": 7, "period_type": "Monthly", "report_date": "2012-07-31"}
    t_7m = {"year": 2012, "month": 7, "period_type": "Cumulative", "report_date": "2012-07-31"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").strip()
        if "CHỈ TIÊU" in name or name == "" or name.isdigit(): continue
        vm = normalize_number(row[5])
        v7 = normalize_number(row[6])
        if vm:
            rec = create_record(metadata, t_m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"})
            if rec: records.append(rec)
        if v7:
            rec = create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": v7, "unit": "1000_ton", "data_type": "Estimate"})
            if rec: records.append(rec)
    return records

def parse_pl10():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL10.md"
    metadata = {"year": 2012, "month": 7, "appendix_number": "PL10"}
    records = []
    t_6m = {"year": 2012, "month": 6, "period_type": "Cumulative", "report_date": "2012-06-30"}
    t_7m = {"year": 2012, "month": 7, "period_type": "Cumulative", "report_date": "2012-07-31"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 10: continue
        name = row[1].replace("**", "").replace("~~", "").replace("<br>", " ").strip()
        if "Danh mục" in name or "TỔNG CỘNG" in name or name == "" or name == "A" or name == "I" or name == "B":
             if "TỔNG CỘNG" in name: name = "Tổng cộng"
             else: continue
        v6 = normalize_number(row[5])
        v7 = normalize_number(row[8])
        if v6:
            rec = create_record(metadata, t_6m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v6, "unit": "million_VND", "data_type": "Actual"})
            if rec: records.append(rec)
        if v7:
            rec = create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v7, "unit": "million_VND", "data_type": "Estimate"})
            if rec: records.append(rec)
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_pl6()}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL6.json"))
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_pl7()}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL7.json"))
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_pl8()}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL8.json"))
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_pl10()}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL10.json"))
    print("Successfully parsed Batch 2 for July 2012.")
