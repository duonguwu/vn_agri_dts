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
        "THỤY SỸ": "Switzerland", "NAUY": "Norway", "ARẬP XÊÚT": "Saudi Arabia", "GANA": "Ghana", "BĂNG LA ĐÉT": "Bangladesh", "XÊ NÊ GAN": "Senegal", "CUBA": "Cuba", "BA LAN": "Poland", "Ý": "Italy", "ITALIA": "Italy", "AI CẬP": "Egypt", "ĐAN MẠCH": "Denmark"
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL9.md"
    metadata = {"year": 2011, "month": 11, "appendix_number": "PL9", "source_file": "2011_11_Phuluc_11_2011_f_PL9.md"}
    records = []
    t_month = {"year": 2011, "month": 11, "period_type": "Monthly", "report_date": "2011-11-30"}
    t_11m = {"year": 2011, "month": 11, "period_type": "Cumulative", "report_date": "2011-11-30"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[0].replace("**", "").replace("~~", "").strip()
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        # 7:Qm, 8:Vm, 9:Q11, 10:V11
        qm = normalize_number(row[7])
        vm = normalize_number(row[8])
        q11 = normalize_number(row[9])
        v11 = normalize_number(row[10])
        
        # Determine trade type (PL9 in Nov is mixed, let's assume based on common commodities)
        tt = "Import"
        if name in ["Gạo", "Cà phê", "Cao su", "Hạt điều", "Chè", "Hạt tiêu", "Quế"]: tt = "Export"
        
        if qm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": tt}))
        if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": tt}))
        if q11: records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": q11, "unit": "1000_ton", "data_type": "Estimate", "trade_type": tt}))
        if v11: records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": v11, "unit": "million_USD", "data_type": "Estimate", "trade_type": tt}))
    return records

def parse_market_file(fpath, metadata, time_context, trade_type):
    rows = extract_rows(fpath)
    records = []
    curr_comm = None
    if "PL11" in fpath: curr_comm = "Muối" # Fallback for truncated PL11
    
    for row in rows:
        if len(row) < 5: continue
        col1 = row[1].replace("**", "").replace("_", "").strip()
        if "Mặt hàng" in col1 or "Col" in col1 or "Thứ tự" in col1 or "Thành tựu" in col1: continue
        
        if row[0] == "" and col1 != "":
            curr_comm = col1
            qv = normalize_number(row[4])
            vv = normalize_number(row[5])
            if qv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if vv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
            continue
            
        if curr_comm and row[0] != "" and (row[0].isdigit() or "." in row[0]):
            qv = normalize_number(row[4])
            vv = normalize_number(row[5])
            if qv: records.append(create_record(metadata, time_context, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if vv: records.append(create_record(metadata, time_context, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
    return records

def parse_pl12():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL12.md"
    metadata = {"year": 2011, "month": 11, "appendix_number": "PL12", "source_file": "2011_11_Phuluc_11_2011_f_PL12.md"}
    records = []
    t_month = {"year": 2011, "month": 11, "period_type": "Monthly", "report_date": "2011-11-30"}
    t_11m = {"year": 2011, "month": 11, "period_type": "Cumulative", "report_date": "2011-11-30"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").replace("~~", "").strip()
        if name == "" or "Danh mục" in name or "Col" in name: continue
        
        vm = normalize_number(row[4])
        v11 = normalize_number(row[5])
        
        if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": vm, "unit": "million_VND", "data_type": "Estimate"}))
        if v11: records.append(create_record(metadata, t_11m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v11, "unit": "million_VND", "data_type": "Estimate"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/11"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_pl9()}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL9.json"))
    
    t_10m_context = {"year": 2011, "month": 10, "period_type": "Cumulative", "report_date": "2011-10-31"}
    md_pl10 = {"year": 2011, "month": 11, "appendix_number": "PL10", "source_file": "2011_11_Phuluc_11_2011_f_PL10.md"}
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL10.md", md_pl10, t_10m_context, "Export")}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL10.json"))
    
    md_pl11 = {"year": 2011, "month": 11, "appendix_number": "PL11", "source_file": "2011_11_Phuluc_11_2011_f_PL11.md"}
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL11.md", md_pl11, t_10m_context, "Import")}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL11.json"))
    
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_pl12()}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL12.json"))
    
    print("Successfully parsed Batch 3 (PL9-PL12) for November 2011.")
