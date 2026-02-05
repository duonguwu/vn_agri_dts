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
        "THỤY SỸ": "Switzerland", "NAUY": "Norway", "ARẬP XÊÚT": "Saudi Arabia", "GANA": "Ghana", "BĂNG LA ĐÉT": "Bangladesh", "XÊ NÊ GAN": "Senegal", "CUBA": "Cuba", "BA LAN": "Poland", "Ý": "Italy", "ITALIA": "Italy", "AI CẬP": "Egypt", "ĐAN MẠCH": "Denmark", "ĐỨC": "Germany", "BỈ": "Belgium", "TÂY BAN NHA": "Spain", "ANH": "United Kingdom", "HÀ LAN": "Netherlands", "THỔ NHĨ KỲ": "Turkey", "XINH GA PO": "Singapore", "DỨC": "Germany", "HỒNG CÔNG": "Hong Kong"
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

def parse_pl5_6(fpath, metadata):
    rows = extract_rows(fpath)
    records = []
    t2011 = {"year": 2011, "period_type": "Annual", "report_date": "2011-12-31"}
    
    if not rows: return []
    data_rows = [r for r in rows if len(r) >= 3 and "<br>" in r[0]]
    
    for row in data_rows:
        lines_label = row[0].split("<br>")
        lines_vals = row[2].split("<br>") # Column 2 is 2011
        lines_units = row[1].split("<br>") if len(row) > 3 else [""] * len(lines_label)
        
        curr_crop = None
        for i in range(len(lines_label)):
            lbl = lines_label[i].replace("**", "").replace("_", "").strip()
            if lbl == "": continue
            
            # Determine if it's a Crop or a Metric
            if "Diện tích" in lbl or "Năng suất" in lbl or "Sản lượng" in lbl or "DT" in lbl:
                if curr_crop and i < len(lines_vals):
                    val = normalize_number(lines_vals[i])
                    if val is not None:
                        unit = lines_units[i].strip() if i < len(lines_units) else ""
                        attr = "Area" if "Diện tích" in lbl or "DT" in lbl else ("Yield" if "Năng suất" in lbl else "Production")
                        records.append(create_record(metadata, t2011, "Cả nước", "National", {"sector": "Cultivation", "commodity": curr_crop}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Estimate"}))
            else:
                curr_crop = lbl
                # Sometimes production value is on the crop row
                if "Tổng" in lbl or "Chè" in lbl or "Cà phê" in lbl:
                   val = normalize_number(lines_vals[i])
                   if val is not None:
                       unit = lines_units[i].strip() if i < len(lines_units) else ""
                       records.append(create_record(metadata, t2011, "Cả nước", "National", {"sector": "Cultivation", "commodity": lbl}, {"attribute": "Production", "value": val, "unit": unit, "data_type": "Estimate"}))
    return records

def parse_pl12():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL12.md"
    rows = extract_rows(fpath)
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL12", "source_file": "2011_12_Phuluc_12_2011_f_PL12.md"}
    records = []
    t_month = {"year": 2011, "month": 12, "period_type": "Monthly", "report_date": "2011-12-31"}
    t_year = {"year": 2011, "month": 12, "period_type": "Cumulative", "report_date": "2011-12-31"}
    
    curr_type = "Export"
    for row in rows:
        if len(row) < 5: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if "XUẤT KHẨU" in name: curr_type = "Export"; continue
        if "NHẬP KHẨU" in name: curr_type = "Import"; continue
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        # 7:Qm, 8:Vm, 9:Qy, 10:Vy
        qm = normalize_number(row[7])
        vm = normalize_number(row[8])
        qy = normalize_number(row[9])
        vy = normalize_number(row[10])
        
        if qm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_type}))
        if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_type}))
        if qy: records.append(create_record(metadata, t_year, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qy, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_type}))
        if vy: records.append(create_record(metadata, t_year, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vy, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_type}))
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

def parse_pl15():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL15.md"
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL15", "source_file": "2011_12_Phuluc_12_2011_f_PL15.md"}
    records = []
    t_month = {"year": 2011, "month": 12, "period_type": "Monthly", "report_date": "2011-12-31"}
    t_year = {"year": 2011, "month": 12, "period_type": "Cumulative", "report_date": "2011-12-31"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").replace("~~", "").strip()
        if name == "" or "Danh mục" in name or "Col" in name: continue
        
        vm = normalize_number(row[4])
        vy = normalize_number(row[5])
        
        if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": vm, "unit": "million_VND", "data_type": "Estimate"}))
        if vy: records.append(create_record(metadata, t_year, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": vy, "unit": "million_VND", "data_type": "Estimate"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/12"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011}, "records": parse_pl5_6("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL5.md", {"year": 2011, "appendix_number": "PL5"})}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL5.json"))
    save_json({"metadata": {"year": 2011}, "records": parse_pl5_6("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL6.md", {"year": 2011, "appendix_number": "PL6"})}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl12()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL12.json"))
    
    t_11m_context = {"year": 2011, "month": 11, "period_type": "Cumulative", "report_date": "2011-11-30"}
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL13.md", {"year": 2011, "month": 12, "appendix_number": "PL13"}, t_11m_context, "Import")}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL13.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_market_file("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL14.md", {"year": 2011, "month": 12, "appendix_number": "PL14"}, t_11m_context, "Export")}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL14.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl15()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL15.json"))
    
    print("Successfully parsed Batch 3 (PL5, PL6, PL12-PL15) for December 2011.")
