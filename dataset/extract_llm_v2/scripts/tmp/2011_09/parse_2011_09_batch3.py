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
        "THỤY SỸ": "Switzerland", "NAUY": "Norway", "ARẬP XÊÚT": "Saudi Arabia", "GANA": "Ghana", "BĂNG LA ĐÉT": "Bangladesh", "XÊ NÊ GAN": "Senegal", "CUBA": "Cuba"
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

def parse_pl10():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL10.md"
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL10", "source_file": "2011_09_Phuluc_09_2011_f_PL10.md"}
    records = []
    t_month = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-30"}
    t_9m = {"year": 2011, "month": 9, "period_type": "Cumulative", "report_date": "2011-09-30"}
    
    rows = extract_rows(fpath)
    curr_type = "Export"
    for row in rows:
        if len(row) < 5: continue
        name = row[0].replace("**", "").strip()
        if "XUẤT KHẨU" in name: curr_type = "Export"; continue
        if "NHẬP KHẨU" in name: curr_type = "Import"; continue
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        # 7:Qm, 8:Vm, 9:Q9, 10:V9
        qm = normalize_number(row[7])
        vm = normalize_number(row[8])
        q9 = normalize_number(row[9])
        v9 = normalize_number(row[10])
        
        if qm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_type}))
        if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_type}))
        if q9: records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": q9, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_type}))
        if v9: records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": v9, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_type}))
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
            
        if curr_comm and row[0] != "" and row[0].isdigit():
            qv = normalize_number(row[4])
            vv = normalize_number(row[5])
            if qv: records.append(create_record(metadata, time_context, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if vv: records.append(create_record(metadata, time_context, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/09"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl10()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL10.json"))
    
    t_8m = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    md_pl11 = {"year": 2011, "month": 9, "appendix_number": "PL11", "source_file": "2011_09_Phuluc_09_2011_f_PL11.md"}
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL11.md", md_pl11, t_8m, "Export")}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL11.json"))
    
    md_pl12 = {"year": 2011, "month": 9, "appendix_number": "PL12", "source_file": "2011_09_Phuluc_09_2011_f_PL12.md"}
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL12.md", md_pl12, t_8m, "Import")}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL12.json"))
    
    print("Successfully parsed Batch 3 (PL10, PL11, PL12) for September 2011.")
