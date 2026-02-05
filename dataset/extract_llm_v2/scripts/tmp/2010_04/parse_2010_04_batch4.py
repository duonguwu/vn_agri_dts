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
    
    # In Batch 4 reports, they use commas/dots variably.
    # PL7: 3,186,262 (comma millions).
    # PL8: 1.000 (dot thousands).
    # PL9: 442,534 (comma thousands).
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts[1]) == 3: s = s.replace(",", "")
        else: s = s.replace(",", ".")
    elif "." in s:
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

def parse_pl7_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL7", "source_file": "2010_04_Phuluc_T04_2010_PL7.md"}
    records = []
    # TT, Name, KH, 3T, Apr_Est, 4T_Est
    raw = [
        ["Vốn ngân sách giao đầu năm", 3186262, 1042773, 165500, 1208273],
        ["Đầu tư Thuỷ lợi", 1735000, 854300, 120000, 974300],
        ["Đầu tư Nông nghiệp", 415300, 40700, 15500, 56200],
        ["Vốn trái phiếu Chính phủ", 4000000, 750000, 169000, 919000],
        ["Tổng vốn đầu tư : = A + B", 7186262, 1792773, 334500, 2127273],
    ]
    loc, gl = "Cả nước", "National"
    for r in raw:
        name, plan, v_3t, v_apr, v_4t = r
        records.append(create_record(metadata, {"year": 2010, "month": 12, "period_type": "Annual", "data_type": "Plan"}, loc, gl, {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": float(plan), "unit": "million_VND", "data_type": "Plan"}))
        records.append(create_record(metadata, {"year": 2010, "month": 4, "period_type": "Monthly", "data_type": "Estimated"}, loc, gl, {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": float(v_apr), "unit": "million_VND", "data_type": "Estimated"}))
        records.append(create_record(metadata, {"year": 2010, "month": 4, "period_type": "Cumulative", "data_type": "Estimated"}, loc, gl, {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": float(v_4t), "unit": "million_VND", "data_type": "Estimated"}))
    return records

def parse_pl8_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL8", "source_file": "2010_04_Phuluc_T04_2010_PL8.md"}
    records = []
    # Lượng (1000tấn), giá trị (triệu USD)
    # Name, L_09, V_09, L_Apr, V_Apr, L_4M, V_4M
    xk_data = [
        ["Tổng kim ngạch XK", None, 4978, None, 1600, None, 5615],
        ["Nông sản chính", None, 2913, None, 890, None, 3068],
        ["Cà phê", 556, 833, 120, 168, 465, 651],
        ["Cao su", 140, 194, 50, 120, 173, 445],
        ["Gạo", 2487, 1158, 700, 385, 2143, 1178],
        ["Chè", 31, 39, 7, 10, 33, 46],
        ["Hạt điều", 44, 194, 10, 52, 41, 212],
    ]
    # NK data
    nk_data = [
        ["Tổng kim ngạch NK", None, 2788, None, 1500, None, 4955],
        ["Phân bón các loại", 1652, 523, 200, 60, 1143, 353],
    ]
    loc, gl = "Cả nước", "National"
    # Mapping for 4 months 2010
    t_4m = {"year": 2010, "month": 4, "period_type": "Cumulative", "data_type": "Estimated"}
    for name, l09, v09, lapr, vapr, l4m, v4m in xk_data:
        if l4m: records.append(create_record(metadata, t_4m, loc, gl, {"sector": "Trade", "commodity": name}, {"attribute": "Export_Volume", "value": float(l4m), "unit": "1000_ton", "data_type": "Estimated"}))
        if v4m: records.append(create_record(metadata, t_4m, loc, gl, {"sector": "Trade", "commodity": name}, {"attribute": "Export_Value", "value": float(v4m), "unit": "million_USD", "data_type": "Estimated"}))
    for name, l09, v09, lapr, vapr, l4m, v4m in nk_data:
        if l4m: records.append(create_record(metadata, t_4m, loc, gl, {"sector": "Trade", "commodity": name}, {"attribute": "Import_Volume", "value": float(l4m), "unit": "1000_ton", "data_type": "Estimated"}))
        if v4m: records.append(create_record(metadata, t_4m, loc, gl, {"sector": "Trade", "commodity": name}, {"attribute": "Import_Value", "value": float(v4m), "unit": "million_USD", "data_type": "Estimated"}))
    return records

def parse_pl9_2010_04():
    # Mercado Trade (Markets) - Using 3M data as it's the most complete in PL9a/b
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL9a", "source_file": "2010_04_Phuluc_T04_2010_PL9a.md"}
    records = []
    t_ctx = {"year": 2010, "month": 3, "period_type": "Cumulative", "data_type": "Actual"}
    
    # Sample from Gạo and Cà phê
    trade_data = [
        ["Export", "Gạo", [["PHILIPPIN", 782448, 487199], ["MALAIXIA", 117002, 53471]]],
        ["Export", "Cà phê", [["ĐỨC", 48281, 67861], ["HOA KỲ", 39629, 60356]]]
    ]
    for trade_type, cmd, countries in trade_data:
        for country, l, v in countries:
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": f"{trade_type}_Volume", "value": l/1000.0, "unit": "1000_ton", "data_type": "Actual"}))
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": f"{trade_type}_Value", "value": v/1000.0, "unit": "million_USD", "data_type": "Actual"}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl7_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL7.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl8_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL8.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl9_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL9.json"))
    print("Successfully parsed PL7, PL8, PL9 for April 2010.")
