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
            if len(parts[-1]) == 3 and len(parts[0]) <= 3: s = s.replace(",", "")
            elif len(parts[-1]) != 3: s = s.replace(",", ".")
            else: s = s.replace(",", "")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    try: return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "HOA KỲ": "United States", "ĐỨC": "Germany", "BỈ": "Belgium", "ITALIA": "Italy", "Italia": "Italy",
        "TÂY BAN NHA": "Spain", "NHẬT BẢN": "Japan", "HÀ LAN": "Netherlands", "XINH GA PO": "Singapore",
        "THỤY SỸ": "Switzerland", "ANH": "United Kingdom", "TRUNG QUỐC": "China", "MALAIXIA": "Malaysia",
        "ĐÀI LOAN": "Taiwan", "HÀN QUỐC": "South Korea", "THỔ NHĨ KỲ": "Turkey", "NGA": "Russia",
        "PAKIXTAN": "Pakistan", "IN ĐÔ NÊ XI A": "Indonesia", "BA LAN": "Poland", "ARẬP XÊÚT": "Saudi Arabia",
        "TVQ ARẬP THỐNG NHẤT": "United Arab Emirates", "CUBA": "Cuba", "HỒNG CÔNG": "Hong Kong",
        "ĐÔNG TIMO": "East Timor", "PHI LIP PIN": "Philippines", "NAM PHI": "South Africa", "B RU NÂY": "Brunei", 
        "PHÁP": "France", "BRAXIN": "Brazil", "Ô X TRÂY LIA": "Australia", "THÁI LAN": "Thailand", 
        "CA NA ĐA": "Canada", "MÊ HI CÔ": "Mexico", "AI CẬP": "Egypt", "ẤN ĐỘ": "India", "CAMPUCHIA": "Cambodia",
        "ACHENTINA": "Argentina", "CHI LÊ": "Chile", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand",
        "MI AN MA": "Myanmar", "ĐAN MẠCH": "Denmark", "NAUY": "Norway", "UCRAINA": "Ukraine",
        "XÊ NÊ GAN": "Senegal", "BĂNG LA ĐÉT": "Bangladesh", "BỜ BIỂN NGÀ": "Ivory Coast", "Cả nước": "Cả nước",
        "BÊ LA RÚT": "Belarus", "IXRAEN": "Israel", "AILEN": "Ireland", "HUNGARI": "Hungary"
    }
    
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    geo_context["region_id"] = "COUNTRY"
    if norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    else:
        geo_context["region_name_vn"] = norm_loc
        geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_rows(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
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
    current_commodity = None
    
    for row in rows:
        if len(row) < 5: continue
        col_name = row[1].replace("**", "").strip()
        # Detect commodity start (Bold name or starts with title)
        # In these files, commodities often don't have TT in col 0 or it's empty.
        if row[0] == "" and col_name != "":
             current_commodity = col_name
             # Add the "Total" record for this commodity
             v_q = normalize_number(row[2]) # Col 2 is usually Prev Year Qty or this year Qty?
             # Wait, in PL13: Col 2=Q09, 3=V09, 4=Q11, 5=V11.
             # Wait, column numbering in PL13 line 16: |TT|Mặt hàng|6M/09|Col4|6M/11|Col6|...
             # So Index 2=Q_old, Index 4=Q_new, Index 5=V_new.
             q_idx = 4
             v_idx = 5
             
             q_val = normalize_number(row[q_idx])
             v_val = normalize_number(row[v_idx])
             
             if q_val: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": current_commodity}, {"attribute": "Volume", "value": q_val, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
             if v_val: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": current_commodity}, {"attribute": "Value", "value": v_val, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
             continue

        if current_commodity and row[0] != "" and row[0].isdigit():
            # This is a country row
            q_val = normalize_number(row[4])
            v_val = normalize_number(row[5])
            if q_val: records.append(create_record(metadata, time_context, col_name, "Country", {"sector": "Trade", "commodity": current_commodity}, {"attribute": "Volume", "value": q_val, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if v_val: records.append(create_record(metadata, time_context, col_name, "Country", {"sector": "Trade", "commodity": current_commodity}, {"attribute": "Value", "value": v_val, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/07"
    os.makedirs(out_dir, exist_ok=True)
    
    md_pl13 = {"year": 2011, "month": 7, "appendix_number": "PL13", "source_file": "2011_07_Phuluc_07_2011_PL13.md"}
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_07_Phuluc_07_2011_PL13.md", md_pl13, t_6m_11, "Export")}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL13.json"))

    md_pl14 = {"year": 2011, "month": 7, "appendix_number": "PL14", "source_file": "2011_07_Phuluc_07_2011_PL14.md"}
    t_7m_11 = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_07_Phuluc_07_2011_PL14.md", md_pl14, t_7m_11, "Import")}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL14.json"))

    print("Successfully parsed Batch 4 (PL13, PL14) for July 2011.")
