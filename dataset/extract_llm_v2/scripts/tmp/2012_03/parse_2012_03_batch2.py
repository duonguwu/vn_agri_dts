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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ", "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắc Nông"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
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

def parse_pl5():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL5.md"
    metadata = {"year": 2012, "month": 3, "appendix_number": "PL5", "source_file": "2012_03_Phuluc_03_2012_PL5.md"}
    records = []
    t = {"year": 2012, "month": 3, "period_type": "Monthly", "report_date": "2012-03-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 10: continue
        name = row[0].replace("**", "").strip()
        if "Col" in name or name == "" or "Cây công nghiệp" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
        def add(idx, comm, sub):
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val, "unit": "ha", "data_type": "Actual"}))
        
        add(1, "Cây công nghiệp ngắn ngày", "Tổng số")
        add(2, "Đậu tương", None)
        add(3, "Lạc", None)
        add(4, "Vừng", None)
        add(5, "Thuốc lá", None)
        add(6, "Mía", None)
        add(7, "Bông", None)
        add(8, "Đay, Lác", None)
        add(9, "Rau các loại", None)
        add(10, "Đậu các loại", None)
    return records

def parse_pl6():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL6.md"
    metadata = {"year": 2012, "month": 3, "appendix_number": "PL6", "source_file": "2012_03_Phuluc_03_2012_PL6.md"}
    records = []
    t_3m = {"year": 2012, "month": 3, "period_type": "Cumulative", "report_date": "2012-03-31"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "Chỉ tiêu" in name or name == "": continue
        
        val = normalize_number(row[4])
        unit = row[2].strip()
        if "1000 ha" in unit: unit = "1000_ha"
        elif "1000 m3" in unit: unit = "1000_m3"
        elif "Tr.cây" in unit: unit = "million_trees"
        
        if val is not None:
            records.append(create_record(metadata, t_3m, "Cả nước", "National", {"sector": "Forestry", "commodity": name}, {"attribute": "Value", "value": val, "unit": unit, "data_type": "Estimate"}))
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL7.md"
    metadata = {"year": 2012, "month": 3, "appendix_number": "PL7", "source_file": "2012_03_Phuluc_03_2012_PL7.md"}
    records = []
    t_m = {"year": 2012, "month": 3, "period_type": "Monthly", "report_date": "2012-03-31"}
    t_3m = {"year": 2012, "month": 3, "period_type": "Cumulative", "report_date": "2012-03-31"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "CHỈ TIÊU" in name or name == "1" or name == "2": continue
        
        vm = normalize_number(row[3])
        v3 = normalize_number(row[4])
        
        if vm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"}))
        if v3: records.append(create_record(metadata, t_3m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": v3, "unit": "1000_ton", "data_type": "Estimate"}))
    return records

def parse_pl8():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL8.md"
    metadata = {"year": 2012, "month": 3, "appendix_number": "PL8", "source_file": "2012_03_Phuluc_03_2012_PL8.md"}
    records = []
    t_2m = {"year": 2012, "month": 2, "period_type": "Cumulative", "report_date": "2012-02-29"}
    t_3m = {"year": 2012, "month": 3, "period_type": "Cumulative", "report_date": "2012-03-31"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 10: continue
        name = row[1].replace("**", "").replace("_", "").replace("<br>", " ").strip()
        if "Danh mục" in name or "TT" in name: continue
        
        v2 = normalize_number(row[5])
        v3 = normalize_number(row[8])
        
        if v2: records.append(create_record(metadata, t_2m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v2, "unit": "million_VND", "data_type": "Actual"}))
        if v3: records.append(create_record(metadata, t_3m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v3, "unit": "million_VND", "data_type": "Estimate"}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/03"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_pl5()}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL5.json"))
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_pl6()}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL6.json"))
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_pl7()}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL7.json"))
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_pl8()}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL8.json"))
    
    print("Successfully parsed Batch 2 (PL5-PL8) for March 2012.")
