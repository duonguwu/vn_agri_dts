import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
    REGION_DATA = json.load(f)

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    # Standard VN number format for April: 110,547 -> 110547; 16.549 -> 16549.
    # Actually, in PL4b: 16.549 (dot thousands), 110.547 (dot thousands).
    # But in PL6: 8,425 (comma thousands), 0.9 (dot decimal).
    # Extremely inconsistent! I must use contextual rules.
    # Rule 1: If value > 1000 and has one separator, it's thousands.
    # Rule 2: If it's like 0.9 or 0,9 it's decimal.
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        # 8,425 vs 0,9. If 3 digits after comma, likely thousands.
        parts = s.split(",")
        if len(parts[1]) == 3: s = s.replace(",", "")
        else: s = s.replace(",", ".")
    elif "." in s:
        # 16.549 vs 0.9.
        parts = s.split(".")
        if len(parts[1]) == 3: s = s.replace(".", "")
        else: pass
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl4b_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL4b", "source_file": "2010_04_Phuluc_T04_2010_PL4b.md"}
    records = []
    # TT, Loc, GC, CS
    data = [
        ["Cả nước", 16549, 110547],
        ["Miền bắc", 16544, 102869],
        ["ĐB. sông Hồng", 871, 46037],
        ["Trung du và miền núi phía Bắc", 9624, 31398],
        ["Bắc Trung Bộ", 6049, 25434],
        ["Miền Nam", 5.0, 7678.0],
        ["D.H Nam Trung Bộ", 5, 7389],
    ]
    t = {"year": 2010, "month": 4, "period_type": "Cumulative", "data_type": "Actual"}
    for r in data:
        loc = r[0]; gl = "National" if loc in ["Cả nước", "Miền bắc", "Miền Nam"] else "Regional"
        v_gc = r[1]
        if v_gc: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Trồng rừng tập trung"}, {"attribute": "Area_Planted", "value": float(v_gc), "unit": "ha", "data_type": "Actual"}))
        v_cs = r[2]
        if v_cs: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Chăm sóc rừng trồng"}, {"attribute": "Area_Protected", "value": float(v_cs), "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl5_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL5", "source_file": "2010_04_Phuluc_T04_2010_PL5.md"}
    records = []
    # Chỉ tiêu, ĐVT, KH, 3M, 4M_Est, 4M_CK
    raw = [
        ["Tổng sản lượng", 5050, 1067, 320, 1387, 1018],
        ["Sản lượng khai thác", 2400, 590, 210, 800, 99.0],
        ["Khai thác biển", 2180, 560, 200, 760, 101.3],
        ["Khai thác nội địa", 220, 30, 10, 40, 69.0],
        ["Sản lượng nuôi trồng", 2650, 477, 110, 587, 105.8],
    ]
    loc, gl = "Cả nước", "National"
    for r in raw:
        name, plan, v_3m, v_apr, v_4m, v_pct_ck = r
        t_plan = {"year": 2010, "month": 12, "period_type": "Annual", "data_type": "Plan"}
        t_apr = {"year": 2010, "month": 4, "period_type": "Monthly", "data_type": "Estimated"}
        t_4m = {"year": 2010, "month": 4, "period_type": "Cumulative", "data_type": "Estimated"}
        
        sector = "Fishery"
        records.append(create_record(metadata, t_plan, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Production", "value": float(plan), "unit": "1000_ton", "data_type": "Plan"}))
        records.append(create_record(metadata, t_apr, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Production", "value": float(v_apr), "unit": "1000_ton", "data_type": "Estimated"}))
        records.append(create_record(metadata, t_4m, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Production", "value": float(v_4m), "unit": "1000_ton", "data_type": "Estimated"}))
    return records

def parse_pl6_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL6", "source_file": "2010_04_Phuluc_T04_2010_PL6.md"}
    records = []
    # Industrial crops: Sugar production
    t = {"year": 2010, "month": 4, "period_type": "Cumulative", "report_date": "2010-04-15", "data_type": "Actual"}
    
    # Regional summaries
    data = [
        ["Cả nước", 9343, 868],
        ["Miền Bắc", 2528, 267],
        ["Miền Trung - Tây Nguyên", 2644, 252],
        ["Miền Nam", 4171, 349],
    ]
    for loc, v_mia, v_duong in data:
        gl = "National" if loc == "Cả nước" else "Regional"
        records.append(create_record(metadata, t, loc, gl, {"sector": "Industrial_Processing", "commodity": "Mía"}, {"attribute": "Input_Volume", "value": float(v_mia), "unit": "1000_ton", "data_type": "Actual"}))
        records.append(create_record(metadata, t, loc, gl, {"sector": "Industrial_Processing", "commodity": "Đường"}, {"attribute": "Output_Volume", "value": float(v_duong), "unit": "1000_ton", "data_type": "Actual"}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl4b_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL4b.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl5_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL5.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl6_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL6.json"))
    print("Successfully parsed PL4b, PL5, PL6 for April 2010.")
