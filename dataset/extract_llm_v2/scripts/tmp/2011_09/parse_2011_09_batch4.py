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
            if len(parts[1]) == 3: s = s.replace(",", "")
            else: s = s.replace(",", ".")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    try: return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_rows(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "": rows.append(parts[1:-1])
            elif len(parts) > 1: rows.append(parts)
    return rows

def parse_pl13():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL13.md"
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL13", "source_file": "2011_09_Phuluc_09_2011_f_PL13.md"}
    records = []
    t_month = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-30"}
    t_9m = {"year": 2011, "month": 9, "period_type": "Cumulative", "report_date": "2011-09-30"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if name == "" or "Danh mục" in name or "Col" in name: continue
        
        vm = normalize_number(row[4])
        v9 = normalize_number(row[5])
        
        if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": vm, "unit": "million_VND", "data_type": "Estimate"}))
        if v9: records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v9, "unit": "million_VND", "data_type": "Estimate"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/09"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl13()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL13.json"))
    print("Successfully parsed Batch 4 (PL13) for September 2011.")
