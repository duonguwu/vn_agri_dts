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
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước",
        "HOA KỲ": "United States", "ẤN ĐỘ": "India", "PAKIXTAN": "Pakistan", "Ô X TRÂY LIA": "Australia",
        "BỜ BIỂN NGÀ": "Ivory Coast", "BRAXIN": "Brazil", "ACHENTINA": "Argentina", "TRUNG QUỐC": "China",
        "PHÁP": "France", "IN ĐÔ NÊ XI A": "Indonesia", "HÀN QUỐC": "South Korea", "CAMPUCHIA": "Cambodia",
        "THÁI LAN": "Thailand", "ĐÀI LOAN": "Taiwan", "NHẬT BẢN": "Japan", "NGA": "Russia", "MALAIXIA": "Malaysia",
        "CHI LÊ": "Chile", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand", "MI AN MA": "Myanmar", "BÊ LA RÚT": "Belarus",
        "PHI LIP PIN": "Philippines", "CA NA ĐA": "Canada", "IXRAEN": "Israel", "AILEN": "Ireland", "HUNGARI": "Hungary"
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

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_01_Phuluc_01_2012_PL6.md"
    metadata = {"year": 2012, "month": 1, "appendix_number": "PL6", "source_file": "2012_01_Phuluc_01_2012_PL6.md"}
    records = []
    t = {"year": 2012, "month": 1, "period_type": "Monthly", "report_date": "2012-01-31"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 4: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "Tổng sản lượng" in name or "Sản lượng" in name or "Khai thác" in name:
            val = normalize_number(row[3])
            if val is not None:
                records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": val, "unit": "1000_ton", "data_type": "Estimate"}))
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_01_Phuluc_01_2012_PL7.md"
    metadata = {"year": 2012, "month": 1, "appendix_number": "PL7", "source_file": "2012_01_Phuluc_01_2012_PL7.md"}
    records = []
    t = {"year": 2012, "month": 1, "period_type": "Monthly", "report_date": "2012-01-31"}
    
    rows = extract_rows(fpath)
    # Search for the row containing super-condensed data
    data_row = None
    for r in rows:
        if len(r) > 5 and "<br>" in r[1] and "<br>" in r[5]:
            data_row = r
            break
            
    if data_row:
        labels = data_row[1].split("<br>")
        vals = data_row[5].split("<br>")  # ƯTH tháng 1/2012 Tổng số
        
        for i in range(min(len(labels), len(vals))):
            lbl = labels[i].replace("**", "").replace("_", "").strip()
            v = normalize_number(vals[i])
            if lbl and v is not None:
                records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Investment", "commodity": lbl}, {"attribute": "Investment_Amount", "value": v, "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_pl8():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_01_Phuluc_01_2012_PL8.md"
    metadata = {"year": 2012, "month": 1, "appendix_number": "PL8", "source_file": "2012_01_Phuluc_01_2012_PL8.md"}
    records = []
    t = {"year": 2012, "month": 1, "period_type": "Monthly", "report_date": "2012-01-31"}
    
    rows = extract_rows(fpath)
    data_row = None
    for r in rows:
        if len(r) > 4 and "<br>" in r[0]:
            data_row = r
            break
            
    if data_row:
        labels = data_row[0].split("<br>")
        labels_clean = [l.replace("**", "").replace("_", "").strip() for l in labels]
        qs = data_row[3].split("<br>")
        vs = data_row[4].split("<br>")
        
        curr_trade = "Export"
        for i in range(len(labels_clean)):
            lbl = labels_clean[i]
            if "XUẤT KHẨU" in lbl: curr_trade = "Export"; continue
            if "NHẬP KHẨU" in lbl: curr_trade = "Import"; continue
            
            q = normalize_number(qs[i]) if i < len(qs) else None
            v = normalize_number(vs[i]) if i < len(vs) else None
            
            if q is not None:
                 records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": lbl}, {"attribute": "Volume", "value": q, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
            if v is not None:
                 records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": lbl}, {"attribute": "Value", "value": v, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/01"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 1}, "records": parse_pl6()}, os.path.join(out_dir, "2012_01_Phuluc_01_2012_PL6.json"))
    save_json({"metadata": {"year": 2012, "month": 1}, "records": parse_pl7()}, os.path.join(out_dir, "2012_01_Phuluc_01_2012_PL7.json"))
    save_json({"metadata": {"year": 2012, "month": 1}, "records": parse_pl8()}, os.path.join(out_dir, "2012_01_Phuluc_01_2012_PL8.json"))
    
    print("Successfully parsed Batch 2 (PL6-PL8) for January 2012.")
