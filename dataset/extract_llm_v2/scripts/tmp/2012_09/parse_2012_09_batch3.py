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
        "Cả nước": "Cả nước",
        "HOA KỲ": "United States", "ĐỨC": "Germany", "ITALIA": "Italy", "TÂY BAN NHA": "Spain",
        "NHẬT BẢN": "Japan", "BỈ": "Belgium", "IN ĐÔ NÊ XI A": "Indonesia", "TRUNG QUỐC": "China",
        "MÊ HI CÔ": "Mexico", "ANH": "United Kingdom", "MALAIXIA": "Malaysia", "ẤN ĐỘ": "India",
        "ĐÀI LOAN": "Taiwan", "HÀN QUỐC": "South Korea", "THỔ NHĨ KỲ": "Turkey", "PAKIXTAN": "Pakistan",
        "NGA": "Russia", "TVQ. ARẬP THỐNG NHẤT": "United Arab Emirates", "TVQ ARẬP THỐNG NHẤT": "United Arab Emirates",
        "BA LAN": "Poland", "ARẬP XÊÚT": "Saudi Arabia", "PHI LIP PIN": "Philippines", "BỜ BIỂN NGÀ": "Ivory Coast",
        "GANA": "Ghana", "XINH GA PO": "Singapore", "XÊ NÊ GAN": "Senegal", "HỒNG CÔNG": "Hong Kong",
        "CA NA ĐA": "Canada", "Ô X TRÂY LIA": "Australia", "PHÁP": "France", "HÀ LAN": "Netherlands",
        "THÁI LAN": "Thailand", "IXRAEN": "Israel", "AI CẬP": "Egypt", "CAMPUCHIA": "Cambodia",
        "BRAXIN": "Brazil", "ACHENTINA": "Argentina", "MI AN MA": "Myanmar", "LÀO": "Laos",
        "NIU ZI LÂN": "New Zealand", "UCRAINA": "Ukraine", "BÊ LA RÚT": "Belarus", "ĐAN MẠCH": "Denmark",
        "THỤY SỸ": "Switzerland", "NAUY": "Norway", "AI XƠ LEN": "Iceland", "CHI LÊ": "Chile", "ĂNG GÔ LA": "Angola"
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

def parse_market_file(fpath, metadata, time_context, trade_type):
    rows = extract_rows(fpath)
    records = []
    curr_comm = None
    for row in rows:
        if len(row) < 5: continue
        col1 = row[1].replace("**", "").replace("_", "").strip()
        if "Mặt hàng" in col1 or "Col" in col1 or "Thứ tự" in col1 or "TT" in col1 or col1 == "": continue
        
        # If row[0] is empty, it's often a commodity header
        if row[0] == "" and not col1.isdigit():
             curr_comm = col1
             # Try row[4] and row[5] for cumulative Volume and Value (8 months)
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

def parse_compliance_lines(lines, metadata):
    records = []
    t = {"year": 2012, "month": 9, "period_type": "Monthly", "report_date": "2012-09-24"}
    for parts in lines:
        if len(parts) < 2 or "Sở NN" in parts[0] or "Tổng cộng" in parts[0] or "Có báo cáo" in parts[0]: continue
        name = parts[0].replace("**", "").strip()
        has_report = "x" in parts[1].lower()
        records.append(create_record(metadata, t, name, "Provincial", {"sector": "Metadata", "commodity": "Reporting_Compliance"}, {"attribute": "Has_Report", "value": 1 if has_report else 0, "unit": "binary", "data_type": "Actual"}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/09"
    os.makedirs(out_dir, exist_ok=True)
    
    t_8m_context = {"year": 2012, "month": 8, "period_type": "Cumulative", "report_date": "2012-08-31"}
    
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL10b.md", {"year": 2012, "month": 9, "appendix_number": "PL10b"}, t_8m_context, "Export")}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL10b.json"))
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL10c.md", {"year": 2012, "month": 9, "appendix_number": "PL10c"}, t_8m_context, "Import")}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL10c.json"))
    
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_compliance_lines(extract_rows("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL11a.md"), {"year": 2012, "month": 9, "appendix_number": "PL11a"})}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL11a.json"))
    save_json({"metadata": {"year": 2012, "month": 9}, "records": parse_compliance_lines(extract_rows("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_09_Phuluc_09_2012_PL11b.md"), {"year": 2012, "month": 9, "appendix_number": "PL11b"})}, os.path.join(out_dir, "2012_09_Phuluc_09_2012_PL11b.json"))
    
    print("Successfully parsed Batch 3 for September 2012.")
