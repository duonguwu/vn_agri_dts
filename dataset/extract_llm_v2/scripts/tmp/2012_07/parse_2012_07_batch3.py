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
        if "########" in s: return None
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Cả nước": "Cả nước",
        "ĐỨC": "Germany", "HOA KỲ": "United States", "ITALIA": "Italy", "TÂY BAN NHA": "Spain",
        "NHẬT BẢN": "Japan", "IN ĐÔ NÊ XI A": "Indonesia", "BỈ": "Belgium", "TRUNG QUỐC": "China",
        "MÊ HI CÔ": "Mexico", "ANH": "United Kingdom", "MALAIXIA": "Malaysia", "ĐÀI LOAN": "Taiwan",
        "HÀN QUỐC": "South Korea", "ẤN ĐỘ": "India", "THỔ NHĨ KỲ": "Turkey", "PAKIXTAN": "Pakistan",
        "NGA": "Russia", "TVQ. ARẬP THỐNG NHẤT": "United Arab Emirates", "ARẬP XÊÚT": "Saudi Arabia",
        "BA LAN": "Poland", "PHI LIP PIN": "Philippines", "BỜ BIỂN NGÀ": "Ivory Coast", "GANA": "Ghana",
        "XINH GA PO": "Singapore", "XÊ NÊ GAN": "Senegal", "HỒNG CÔNG": "Hong Kong", "CA NA ĐA": "Canada",
        "Ô X TRÂY LIA": "Australia", "PHÁP": "France", "HÀ LAN": "Netherlands", "THÁI LAN": "Thailand",
        "IXRAEN": "Israel", "AI CẬP": "Egypt", "CAMPUCHIA": "Cambodia", "BRAXIN": "Brazil", "ACHENTINA": "Argentina",
        "MI AN MA": "Myanmar", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand", "UCRAINA": "Ukraine", "BÊ LA RÚT": "Belarus",
        "ĐAN MẠCH": "Denmark", "THỤY SỸ": "Switzerland", "NAUY": "Norway"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
    loc_clean = loc_clean.replace("\n", "").replace("<br>", "").replace("**", "").strip()
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

def parse_pl11a():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL11a.md"
    metadata = {"year": 2012, "month": 7, "appendix_number": "PL11a"}
    records = []
    t_m = {"year": 2012, "month": 7, "period_type": "Monthly", "report_date": "2012-07-31"}
    t_7m = {"year": 2012, "month": 7, "period_type": "Cumulative", "report_date": "2012-07-31"}
    rows = extract_rows(fpath)
    curr_trade = "Export"
    for row in rows:
        if len(row) < 11: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if "XUẤT KHẨU" in name: curr_trade = "Export"; continue
        if "NHẬP KHẨU" in name: curr_trade = "Import"; continue
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        qm = normalize_number(row[7]); vm = normalize_number(row[8])
        q7 = normalize_number(row[9]); v7 = normalize_number(row[10])
        
        if qm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if vm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
        if q7: records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": q7, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if v7: records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": v7, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
    return records

def parse_market_file(fpath, metadata, time_context, trade_type):
    rows = extract_rows(fpath)
    records = []
    curr_comm = None
    for row in rows:
        if len(row) < 5: continue
        col1 = row[1].replace("**", "").replace("_", "").strip()
        if "Mặt hàng" in col1 or "Col" in col1 or "Thứ tự" in col1 or "TT" in col1: continue
        
        if row[0] == "" and col1 != "" and col1.lower() not in ["thứ tự", ""]:
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

def parse_compliance(fpath, metadata):
    rows = extract_rows(fpath)
    records = []
    t = {"year": 2012, "month": 7, "period_type": "Monthly", "report_date": "2012-07-24"}
    for row in rows:
        if len(row) < 2 or "Sở NN" in row[0] or "Tổng cộng" in row[0] or "Có báo cáo" in row[0]: continue
        name = row[0].replace("**", "").strip()
        has_report = "x" in row[1].lower()
        records.append(create_record(metadata, t, name, "Provincial", {"sector": "Metadata", "commodity": "Reporting_Compliance"}, {"attribute": "Has_Report", "value": 1 if has_report else 0, "unit": "binary", "data_type": "Actual"}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/07"
    os.makedirs(out_dir, exist_ok=True)
    
    t_6m_context = {"year": 2012, "month": 6, "period_type": "Cumulative", "report_date": "2012-06-30"}
    
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_pl11a()}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL11a.json"))
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL11b.md", {"year": 2012, "month": 7, "appendix_number": "PL11b"}, t_6m_context, "Export")}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL11b.json"))
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL11c.md", {"year": 2012, "month": 7, "appendix_number": "PL11c"}, t_6m_context, "Import")}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL11c.json"))
    
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_compliance("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL12a.md", {"year": 2012, "month": 7, "appendix_number": "PL12a"})}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL12a.json"))
    save_json({"metadata": {"year": 2012, "month": 7}, "records": parse_compliance("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_07_Phuluc_07_2012_PL12b.md", {"year": 2012, "month": 7, "appendix_number": "PL12b"})}, os.path.join(out_dir, "2012_07_Phuluc_07_2012_PL12b.json"))
    
    print("Successfully parsed Batch 3 for July 2012.")
