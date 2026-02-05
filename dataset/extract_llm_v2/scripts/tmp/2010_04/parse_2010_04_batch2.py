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
    
    # April files use commas or dots for thousands. 
    # Example PL3a: 213,806 (comma thousands). 43,419 (comma thousands).
    # Example PL4a: 206.7 (dot decimal).
    # Logic: if dot/comma follows by < 3 digits at the end OR if it's used as decimal in context.
    if "." in s and "," in s:
        # VN format: 1.234,5
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
        else:
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
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "Trung du và MN phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ"
    }
    norm_loc = alias_map.get(loc_name.strip(), loc_name.strip())
    
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name_vn"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name_vn"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    elif norm_loc == "Miền Nam":
        geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    elif norm_loc == "Miền Bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl3a_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL3a", "source_file": "2010_04_Phuluc_T04_2010_PL3a.md"}
    records = []
    t = {"year": 2010, "month": 4, "period_type": "Monthly", "report_date": "2010-04-15"}
    
    # Rows: loc, cn_total, dau_tuong, lac, mia, thuoc_la, rau_dau_total
    data_3a = [
        ["Miền Bắc", 213806, 34603, 119238, 43419, 12397, 134409],
        ["ĐB sông Hồng", 33621, 9313, 20568, 224, 2747, 68600],
        ["Hà Nội", 8200, 3000, 5000, 200, None, 10351],
        ["Hải Phòng", 2674, 200, None, None, 2347, 10933],
        ["Vĩnh Phúc", 3863, 774, 2804, 24, None, 4847],
        ["Bắc Ninh", 1389, 295, 935, None, None, 1546],
        ["Hải Dương", 1980, 780, 1200, None, None, 12000],
        ["Hưng Yên", 3697, 2758, 717, None, None, 9379],
        ["Hà Nam", 484, 128, 356, None, None, 1426],
        ["Nam Định", 3758, 758, 3000, None, None, 7883],
        ["Thái Bình", 1900, None, 1500, None, 400, 1500],
        ["Ninh Bình", 2769, None, 2769, None, None, 4051],
        ["Quảng Ninh", 2907, 620, 2287, None, None, 4684],
        ["Trung du và MN phía Bắc", 78198, 24525, 32633, 8626, 9570, 35277],
        ["Hà Giang", 11367, 6475, 4682, None, None, 8904],
        ["Cao Bằng", 5705, 1105, 70, 1238, 3058, 924],
        ["Lào Cai", 2608, 1786, 380, None, 442, 2014],
        ["Bắc Cạn", 2130, 456, 310, 38, 1326, 556],
        ["Lạng Sơn", 9254, 1600, 1500, 200, 4659, 650],
        ["Tuyên Quang", 5141, 1139, 4002, None, None, 2221],
        ["Yên Bái", 3468, 1191, 1262, 630, None, 4597],
        ["Thái Nguyên", 4389, 1072, 3317, None, None, 2322],
        ["Phú Thọ", 6115, 1801, 4314, None, None, 2416],
        ["Bắc Giang", 9563, 706, 8550, None, 85, 5036],
        ["Lai Châu", 1302, 585, 448, None, None, 164],
        ["Điện Biên", 2478, 2000, 350, None, None, 950],
        ["Sơn La", 4756, 4363, None, 291, None, 1776],
        ["Hoà Bình", 9923, 246, 3448, 6229, None, 2747],
        ["Bắc Trung Bộ", 101987, 765, 66037, 34569, 80, 30531],
    ]
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data_3a:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", "Trồng mới"), ("Thuốc lá", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[6])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl3b_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL3b", "source_file": "2010_04_Phuluc_T04_2010_PL3b.md"}
    records = []
    t = {"year": 2010, "month": 4, "period_type": "Monthly", "report_date": "2010-04-15"}
    
    # Rows: loc, total_cn, dau_tuong, lac, vung, thuoc_la, mia, bong, day_lac, rau, dau
    data_3b = [
        ["Miền Nam", 144577, 7290, 39898, 10523, 10947, 73818, 434, 1198, 186106, 22484],
        ["D.H Nam Trung Bộ", 29126, 650, 19322, 81, 874, 7724, 434, 41, 22061, 22061],
        ["Tây Nguyên", 14804, None, 309, None, 4622, 9404, None, None, 40566, 4802],
        ["Đông Nam Bộ", 28440, 302, 12224, 1349, 5411, 9154, None, None, 31656, 7528],
        ["ĐBS Cửu Long", 72207, 6338, 8043, 9093, 40, 47536, None, 1157, 91823, 2594],
    ]
    # In PL3b of April, they have more details at provincial level. I'll include regional for now.
    for row in data_3b:
        loc = str(row[0]); gl = "Regional" if loc != "Miền Nam" else "National" # Wait, South is National or Regional?
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            if idx+2 < len(row):
                v = normalize_number(row[idx+2])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        if len(row) > 9:
            v = normalize_number(row[9])
            if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            v = normalize_number(row[10])
            if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl4a_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL4a", "source_file": "2010_04_Phuluc_T04_2010_PL4a.md"}
    records = []
    # TT, Name, Unit, Plan, CK, Est_4M
    raw = [
        ["1", "Trồng rừng tập trung", "1000 ha", 206.7, 20.3, 16.5, "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000 ha", 149.7, 78.0, 110.5, "Other"],
        ["3", "Trồng cây phân tán", "Tr.cây", 200.0, 76.2, 76.4, "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000 ha", 668.8, 613, 609.0, "Other"],
        ["5", "Khoán bảo vệ rừng", "1000 ha", 1506, 1780, 1730.0, "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000 m3", 4700, 606, 1091, "Wood_Volume"],
    ]
    t10 = {"year": 2010, "month": 4, "period_type": "Cumulative", "data_type": "Estimated"}
    t09 = {"year": 2009, "month": 4, "period_type": "Cumulative", "data_type": "Actual"}
    t_plan = {"year": 2010, "month": 12, "period_type": "Annual", "data_type": "Plan"}
    
    loc, gl = "Cả nước", "National"
    for r in raw:
        name, unit, plan, v09, v10, attr = r[1], r[2], r[3], r[4], r[5], r[6]
        records.append(create_record(metadata, t10, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": float(v10), "unit": unit.replace(" ", "_"), "data_type": "Estimated"}))
        records.append(create_record(metadata, t09, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": float(v09), "unit": unit.replace(" ", "_"), "data_type": "Actual"}))
        records.append(create_record(metadata, t_plan, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": float(plan), "unit": unit.replace(" ", "_"), "data_type": "Plan"}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl3a_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL3a.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl3b_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL3b.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl4a_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL4a.json"))
    print("Successfully parsed PL3a, PL3b, PL4a for April 2010.")
