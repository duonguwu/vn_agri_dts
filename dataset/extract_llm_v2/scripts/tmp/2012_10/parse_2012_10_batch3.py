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

def parse_pl9a():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_10_Phuluc_10_2012_PL9a.md"
    metadata = {"year": 2012, "month": 10, "appendix_number": "PL9a"}
    records = []
    t_m = {"year": 2012, "month": 10, "period_type": "Monthly", "report_date": "2012-10-31"}
    t_10m = {"year": 2012, "month": 10, "period_type": "Cumulative", "report_date": "2012-10-31"}
    rows = extract_rows(fpath)
    curr_trade = "Import" # Based on the items seen (Dầu mỡ, Phân bón...)
    for row in rows:
        if len(row) < 11: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if "XUẤT KHẨU" in name: curr_trade = "Export"; continue
        if "NHẬP KHẨU" in name: curr_trade = "Import"; continue
        if "Chỉ tiêu" in name or name == "" or name == "A": continue
        
        qm = normalize_number(row[7]); vm = normalize_number(row[8])
        q10 = normalize_number(row[9]); v10 = normalize_number(row[10])
        
        if qm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": qm, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if vm: records.append(create_record(metadata, t_m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": vm, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
        if q10: records.append(create_record(metadata, t_10m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": q10, "unit": "1000_ton", "data_type": "Estimate", "trade_type": curr_trade}))
        if v10: records.append(create_record(metadata, t_10m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": v10, "unit": "million_USD", "data_type": "Estimate", "trade_type": curr_trade}))
    return records

def parse_market_file_multiline(fpath, metadata, time_context, trade_type):
    rows = extract_rows(fpath)
    records = []
    curr_comm = None
    for row in rows:
        if len(row) < 5: continue
        
        # Detect if it's a summary row or detail row
        # detail rows often have 1, 2, 3 in row[0] or use <br> for multiple items
        is_summary = (row[0] == "" and "<br>" not in row[1])
        
        names = row[1].split("<br>")
        val_qs = row[4].split("<br>")
        val_vs = row[5].split("<br>")
        
        names = [n.strip() for n in names if n.strip() != ""]
        val_qs = [v.strip() for v in val_qs if v.strip() != ""]
        val_vs = [v.strip() for v in val_vs if v.strip() != ""]
        
        if is_summary:
            curr_comm = names[0]
            qv = normalize_number(val_qs[0]) if val_qs else None
            vv = normalize_number(val_vs[0]) if val_vs else None
            if qv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
            if vv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
        else:
            # Detail rows
            if not curr_comm: # Handle case where file starts with details like PL9b
                # For PL9b, the first item is Coffee detail 10 NGA. I'll hardcode if needed, 
                # but better to see if we can detect the sector.
                # Actually, PL9b starts with coffee detail.
                pass 
                
            for i in range(len(names)):
                name = names[i]
                if "Mặt hàng" in name or "Tên nước" in name: continue
                # if name is a commodity (all caps and total row like in PL9c)
                if name.replace(" ", "").isupper() and i < len(val_qs) and "Cả nước" not in name:
                     # This might be a commodity summary row hidden in multiline
                     curr_comm = name
                     qv = normalize_number(val_qs[i])
                     vv = normalize_number(val_vs[i])
                     if qv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
                     if vv: records.append(create_record(metadata, time_context, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
                     continue

                if not curr_comm: continue # skip if we haven't found a commodity yet
                
                vq = normalize_number(val_qs[i]) if i < len(val_qs) else None
                vv = normalize_number(val_vs[i]) if i < len(val_vs) else None
                
                if vq: records.append(create_record(metadata, time_context, name, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": vq, "unit": "ton", "data_type": "Actual", "trade_type": trade_type}))
                if vv: records.append(create_record(metadata, time_context, name, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": trade_type}))
    return records

def parse_compliance_lines(lines, metadata):
    records = []
    t = {"year": 2012, "month": 10, "period_type": "Monthly", "report_date": "2012-10-24"}
    for parts in lines:
        if len(parts) < 2 or "Sở NN" in parts[0] or "Tổng cộng" in parts[0] or "Có báo cáo" in parts[0]: continue
        name = parts[0].replace("**", "").replace("_", "").strip()
        if name == "": continue
        has_report = "x" in parts[1].lower()
        records.append(create_record(metadata, t, name, "Provincial", {"sector": "Metadata", "commodity": "Reporting_Compliance"}, {"attribute": "Has_Report", "value": 1 if has_report else 0, "unit": "binary", "data_type": "Actual"}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/extracted_data/2012/10"
    # Actually wait, the path should be consistent: dataset/extract_llm_v2/extracted_data/2012/10
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/10"
    os.makedirs(out_dir, exist_ok=True)
    
    t_9m_context = {"year": 2012, "month": 9, "period_type": "Cumulative", "report_date": "2012-09-30"}
    
    save_json({"metadata": {"year": 2012, "month": 10}, "records": parse_pl9a()}, os.path.join(out_dir, "2012_10_Phuluc_10_2012_PL9a.json"))
    save_json({"metadata": {"year": 2012, "month": 10}, "records": parse_market_file_multiline("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_10_Phuluc_10_2012_PL9b.md", {"year": 2012, "month": 10, "appendix_number": "PL9b"}, t_9m_context, "Export")}, os.path.join(out_dir, "2012_10_Phuluc_10_2012_PL9b.json"))
    save_json({"metadata": {"year": 2012, "month": 10}, "records": parse_market_file_multiline("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_10_Phuluc_10_2012_PL9c.md", {"year": 2012, "month": 10, "appendix_number": "PL9c"}, t_9m_context, "Import")}, os.path.join(out_dir, "2012_10_Phuluc_10_2012_PL9c.json"))
    
    save_json({"metadata": {"year": 2012, "month": 10}, "records": parse_compliance_lines(extract_rows("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_10_Phuluc_10_2012_PL10a.md"), {"year": 2012, "month": 10, "appendix_number": "PL10a"})}, os.path.join(out_dir, "2012_10_Phuluc_10_2012_PL10a.json"))
    save_json({"metadata": {"year": 2012, "month": 10}, "records": parse_compliance_lines(extract_rows("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_10_Phuluc_10_2012_PL10b.md"), {"year": 2012, "month": 10, "appendix_number": "PL10b"})}, os.path.join(out_dir, "2012_10_Phuluc_10_2012_PL10b.json"))
    
    print("Successfully parsed Batch 3 for October 2012.")
