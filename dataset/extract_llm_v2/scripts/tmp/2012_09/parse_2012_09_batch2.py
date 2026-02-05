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
        "TD và MN": "Đông Bắc", "phía Bắc": "Đông Bắc", "Trung du và MN phía Bắc": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc", "Trung du và miền núi": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam TB": "Duyên hải Nam Trung Bộ",
        "Bắc Trung bộ": "Bắc Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông",
        "Hà Nội (mở rộng)": "Hà Nội", "Trung uơng": "Trung ương", "Tâ Ni h": "Tây Ninh", "y n": "Tây Ninh"
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL6.md"
    metadata = {"year": 2012, "month": 9, "appendix_number": "PL6"}
    records = []
    t_9m = {"year": 2012, "month": 9, "period_type": "Cumulative", "report_date": "2012-09-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("-", "").strip()
        if "Chỉ tiêu" in name or name == "": continue
        val = normalize_number(row[4])
        if val:
            records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Forestry", "commodity": name}, {"attribute": "Value", "value": val, "unit": row[2].strip(), "data_type": "Estimate"}))
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL7.md"
    metadata = {"year": 2012, "month": 9, "appendix_number": "PL7"}
    records = []
    t_9m = {"year": 2012, "month": 9, "period_type": "Cumulative", "report_date": "2012-09-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").replace("_", "").replace("~~", "").strip()
        if "Tỉnh/TP" in name or "Tổng số" in name or name == "": continue
        
        gl = "Provincial"
        if name in ["Cả nước", "Miền bắc", "Miền Nam", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]:
            gl = "Regional"
            if name == "Cả nước": gl = "National"
            
        def add(idx, comm, attr, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val:
                records.append(create_record(metadata, t_9m, name, gl, {"sector": "Forestry", "commodity": comm}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))
        
        add(2, "Diện tích rừng trồng mới tập trung", "Area")
        add(6, "Diện tích rừng trồng được chăm sóc", "Area")
        add(7, "Diện tích rừng được khoán bảo vệ", "Area")
    return records

def parse_pl8():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL8.md"
    metadata = {"year": 2012, "month": 9, "appendix_number": "PL8"}
    records = []
    t_m = {"year": 2012, "month": 9, "period_type": "Monthly", "report_date": "2012-09-30"}
    t_9m = {"year": 2012, "month": 9, "period_type": "Cumulative", "report_date": "2012-09-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 7: continue
        name = row[1].replace("**", "").strip()
        if "CHỈ TIÊU" in name or name == "" or name.isdigit(): continue
        vm = normalize_number(row[5])
        v9 = normalize_number(row[6])
        if vm:
            records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"}))
        if v9:
            records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": v9, "unit": "1000_ton", "data_type": "Estimate"}))
    return records

def parse_pl9():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL9.md"
    metadata = {"year": 2012, "month": 9, "appendix_number": "PL9"}
    records = []
    t_8m = {"year": 2012, "month": 8, "period_type": "Cumulative", "report_date": "2012-08-31"}
    t_9m = {"year": 2012, "month": 9, "period_type": "Cumulative", "report_date": "2012-09-30"}
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 10: continue
        name = row[1].replace("**", "").replace("~~", "").strip()
        if "Danh mục" in name or "TỔNG CỘNG" in name or name == "" or name == "A" or name == "I" or name == "B" or "VỐN NGÂN SÁCH" in name:
             continue
        v8 = normalize_number(row[5])
        v9 = normalize_number(row[8])
        if v8:
            records.append(create_record(metadata, t_8m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v8, "unit": "million_VND", "data_type": "Actual"}))
        if v9:
            records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v9, "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_pl10a():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL10a.md"
    metadata = {"year": 2012, "month": 9, "appendix_number": "PL10a"}
    records = []
    t_m = {"year": 2012, "month": 9, "period_type": "Monthly", "report_date": "2012-09-30"}
    t_9m = {"year": 2012, "month": 9, "period_type": "Cumulative", "report_date": "2012-09-30"}
    rows = extract_rows(fpath)
    curr_trade = "Export"
    for row in rows:
        if len(row) < 11: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if "XUẤT KHẨU" in name: curr_trade = "Export"; continue
        if "NHẬP KHẨU" in name: curr_trade = "Import"; continue
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        qm = normalize_number(row[7]); vm = normalize_number(row[8])
        q9 = normalize_number(row[9]); v9 = normalize_number(row[10])
        
        if qm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if vm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
        if q9: records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": q9, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if v9: records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": v9, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/09"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_pl6()}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL6.json"))
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_pl7()}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL7.json"))
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_pl8()}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL8.json"))
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_pl9()}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL9.json"))
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_pl10a()}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL10a.json"))
    
    print("Successfully parsed Batch 2 for September 2012.")
