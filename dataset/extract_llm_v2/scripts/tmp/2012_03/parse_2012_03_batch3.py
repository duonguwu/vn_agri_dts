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
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước",
        "HOA KỲ": "United States", "ẤN ĐỘ": "India", "PAKIXTAN": "Pakistan", "Ô X TRÂY LIA": "Australia",
        "BỜ BIỂN NGÀ": "Ivory Coast", "BRAXIN": "Brazil", "ACHENTINA": "Argentina", "TRUNG QUỐC": "China",
        "PHÁP": "France", "IN ĐÔ NÊ XI A": "Indonesia", "HÀN QUỐC": "South Korea", "CAMPUCHIA": "Cambodia",
        "THÁI LAN": "Thailand", "ĐÀI LOAN": "Taiwan", "NHẬT BẢN": "Japan", "NGA": "Russia", "MALAIXIA": "Malaysia",
        "CHI LÊ": "Chile", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand", "MI AN MA": "Myanmar", "BÊ LA RÚT": "Belarus",
        "PHI LIP PIN": "Philippines", "CA NA ĐA": "Canada", "IXRAEN": "Israel", "AILEN": "Ireland", "HUNGARI": "Hungary",
        "TIỂU VƯƠNG QUỐC ARẬP THỐNG NHẤT": "United Arab Emirates", "TVQ ARẬP THỐNG NHẤT": "United Arab Emirates", 
        "THỔ NHĨ KỲ": "Turkey", "XINH GA PO": "Singapore"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
    loc_clean = loc_clean.replace("\u00a0", " ") # Handle non-breaking space
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

def parse_pl9():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL9.md"
    metadata = {"year": 2012, "month": 3, "appendix_number": "PL9", "source_file": "2012_03_Phuluc_03_2012_PL9.md"}
    records = []
    t_cm = {"year": 2012, "month": 3, "period_type": "Monthly", "report_date": "2012-03-31"}
    t_cy = {"year": 2012, "month": 3, "period_type": "Cumulative", "report_date": "2012-03-31"}
    rows = extract_rows(fpath)
    
    curr_trade = "Export"
    for row in rows:
        if len(row) < 10: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if "XUẤT KHẨU" in name: curr_trade = "Export"; continue
        if "NHẬP KHẨU" in name: curr_trade = "Import"; continue
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        # Indices:
        # TH tháng 2/2012 (3,4) -> Actual
        # TH 2 tháng/2012 (5,6) -> Actual
        # Ư TH tháng 3/2012 (7,8) -> Estimate
        # Ư TH 3 tháng 2012 (9,10) -> Estimate
        
        qm = normalize_number(row[7])
        vm = normalize_number(row[8])
        qy = normalize_number(row[9])
        vy = normalize_number(row[10])
        
        if qm: records.append(create_record(metadata, t_cm, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if vm: records.append(create_record(metadata, t_cm, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
        if qy: records.append(create_record(metadata, t_cy, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qy, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if vy: records.append(create_record(metadata, t_cy, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vy, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
    return records

def parse_market_file(fpath, metadata, time_context, trade_type):
    rows = extract_rows(fpath)
    records = []
    curr_comm = None
    for row in rows:
        if len(row) < 5: continue
        col1 = row[1].replace("**", "").replace("_", "").strip()
        if "Mặt hàng" in col1 or "Col" in col1 or "Thứ tự" in col1: continue
        
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/03"
    os.makedirs(out_dir, exist_ok=True)
    
    # PL10 and PL11 are cumulative 2-month data as of Feb
    # The header says "2 THÁNG NĂM 2012"
    t_2m_context = {"year": 2012, "month": 2, "period_type": "Cumulative", "report_date": "2012-02-29"}
    
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_pl9()}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL9.json"))
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL10.md", {"year": 2012, "month": 3, "appendix_number": "PL10"}, t_2m_context, "Export")}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL10.json"))
    save_json({"metadata": {"year": 2012, "month": 3}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_03_Phuluc_03_2012_PL11.md", {"year": 2012, "month": 3, "appendix_number": "PL11"}, t_2m_context, "Import")}, os.path.join(out_dir, "2012_03_Phuluc_03_2012_PL11.json"))
    
    print("Successfully parsed Batch 3 (PL9-PL11) for March 2012.")
