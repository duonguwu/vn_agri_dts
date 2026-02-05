import json
import uuid
import os
import re

def generate_id():
    return str(uuid.uuid4())

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
        "Cả nước": "Cả nước",
        "HOA KỲ": "United States", "ẤN ĐỘ": "India", "PAKIXTAN": "Pakistan", "Ô X TRÂY LIA": "Australia",
        "BỜ BIỂN NGÀ": "Ivory Coast", "BRAXIN": "Brazil", "ACHENTINA": "Argentina", "TRUNG QUỐC": "China",
        "PHÁP": "France", "IN ĐÔ NÊ XI A": "Indonesia", "HÀN QUỐC": "South Korea", "CAMPUCHIA": "Cambodia",
        "THÁI LAN": "Thailand", "ĐÀI LOAN": "Taiwan", "NHẬT BẢN": "Japan", "NGA": "Russia", "MALAIXIA": "Malaysia",
        "CHI LÊ": "Chile", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand", "MI AN MA": "Myanmar", "BÊ LA RÚT": "Belarus",
        "PHI LIP PIN": "Philippines", "CA NA ĐA": "Canada", "IXRAEN": "Israel", "AILEN": "Ireland", "HUNGARI": "Hungary",
        "TIỂU VƯƠNG QUỐC ARẬP THỐNG NHẤT": "United Arab Emirates"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    if norm_loc == "Cả nước":
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

def parse_market_file(fpath, metadata, time_context, trade_type):
    rows = extract_rows(fpath)
    records = []
    curr_comm = None
    for row in rows:
        if len(row) < 5: continue
        col1 = row[1].replace("**", "").replace("_", "").replace("<br>", " ").strip()
        if "Mặt hàng" in col1 or "Col" in col1 or "Thứ tự" in col1 or "TT" in col1: continue
        
        # Super row/Category check
        if row[0] == "" and col1 != "":
            curr_comm = col1
            qv = normalize_number(row[4])
            vv = normalize_number(row[5])
            if qv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if vv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
            continue
            
        if curr_comm:
            val_q = normalize_number(row[4])
            val_v = normalize_number(row[5])
            if val_q: records.append(create_record(metadata, time_context, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": val_q, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if val_v: records.append(create_record(metadata, time_context, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": val_v, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/04"
    os.makedirs(out_dir, exist_ok=True)
    
    t_3m_context = {"year": 2012, "month": 3, "period_type": "Cumulative", "report_date": "2012-03-31"}
    
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL10b.md", {"year": 2012, "month": 4, "appendix_number": "PL10b"}, t_3m_context, "Export")}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL10b.json"))
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL10c.md", {"year": 2012, "month": 4, "appendix_number": "PL10c"}, t_3m_context, "Import")}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL10c.json"))
    
    print("Successfully parsed Batch 3 for April 2012.")
