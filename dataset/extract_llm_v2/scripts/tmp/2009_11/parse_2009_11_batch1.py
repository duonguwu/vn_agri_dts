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
    if s == "" or s == "-" or s == "." or s == "||" or s == "|": return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    if loc_name in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][loc_name]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][loc_name]["region_name"]
    elif loc_name in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][loc_name]
        geo_context["region_name"] = loc_name
    elif loc_name == "Cả nước":
        geo_context["region_id"] = "NATIONAL"
        geo_context["region_name"] = "Cả nước"
    
    # Handle aliases
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ"
    }
    if loc_name in alias_map:
        real_name = alias_map[loc_name]
        geo_context["region_id"] = REGION_DATA["regions"].get(real_name)
        geo_context["region_name"] = real_name

    record = {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": geo_context,
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata
    }
    if comp: record["comparison_context"] = comp
    return record

def parse_pl1_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL1", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL1.md"}
    records = []
    
    # Rows: Item, Sub, val08, val09, comp_yoy, loc, geo_level, attr
    rows = [
        ["Lúa", "Mùa", "1455.9", "1473.3", "101.2", "Cả nước", "National", "Area_Harvested"],
        ["Lúa", "Mùa", "1145.6", "1152.5", "100.6", "Miền Bắc", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "548.3", "553.8", "101.0", "ĐB sông Hồng", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "310.4", "320.8", "103.4", "Miền Nam", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "55.0", "31.8", "57.8", "ĐBS Cửu Long", "Regional", "Area_Harvested"],
        ["Lúa", "Đông Xuân", "274.6", "332.7", "121.2", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "266.0", "223.8", "84.1", "ĐBS Cửu Long", "Regional", "Area_Planted"],
        ["Cây vụ đông", "Tổng số", "390.2", "412.8", "105.8", "Miền Bắc", "Regional", "Area_Planted"],
        ["Ngô", "Ngô đông", "165.9", "146.9", "88.6", "Miền Bắc", "Regional", "Area_Planted"],
        ["Khoai lang", None, "55.6", "44.6", "80.3", "Miền Bắc", "Regional", "Area_Planted"],
        ["Đậu tương", None, "78.0", "79.7", "102.1", "Miền Bắc", "Regional", "Area_Planted"],
        ["Rau, đậu các loại", "Tổng số", "100.4", "109.0", "108.6", "Miền Bắc", "Regional", "Area_Planted"],
    ]

    for r in rows:
        item, sub, v08, v09, c_yoy, loc, geo, attr = r
        t09 = {"year": 2009, "month": 11, "period_type": "Cumulative", "report_date": "2009-11-15"}
        
        # 2009 record
        val09 = normalize_number(v09)
        if val09:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, t09, loc, geo, {"sector": "Cultivation", "commodity": item, "sub_item": sub}, {"attribute": attr, "value": val09, "unit": "1000_ha", "data_type": "Actual"}, comp))
        
        # 2008 record
        val08 = normalize_number(v08)
        if val08:
            t08 = {"year": 2008, "month": 11, "period_type": "Cumulative", "report_date": "2008-11-15"}
            records.append(create_record(metadata, t08, loc, geo, {"sector": "Cultivation", "commodity": item, "sub_item": sub}, {"attribute": attr, "value": val08, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl2_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL2", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL2.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    # Data list to avoid complex parsing
    pl2_data = [
        ["Miền Bắc", "1188053", "1152518", None, "412837", "146925", "44629", "79702", "7454", "109012", "12521"],
        ["ĐB sông Hồng", "553864", "553799", None, "227886", "55102", "14430", "74330", "1626", "59398", "8894"],
        ["Hà Nội", "102889", "102889", None, "55186", "12284", "2570", "30668", "539", "7826", "66"],
        ["Hải Phòng", "42254", "42254", "57", "5247", "1925", None, None, None, "601", None],
        ["Vĩnh Phúc", "28986", "28986", "51", "24207", "14124", "2326", "4144", "404", "3209", None],
        ["Bắc Ninh", "37338", "37338", "57", "11386", "3314", "2088", "1906", "272", "3807", "709"],
        ["Hải Dương", "63043", "62978", "57", "23096", "3151", "541", "270", None, "14415", "372"],
        ["Hưng Yên", "40671", "40671", "61", "16354", "4905", "655", "2758", "97", "6942", "572"],
        ["Hà Nam", "35403", "35403", "57", "18666", "3697", "399", "11249", "42", "2907", "404"],
        ["Nam Định", "80304", "80304", "45", "14324", "1959", "870", "618", None, "2315", "2619"],
        ["Thái Bình", "83164", "83164", "70", "40028", "6430", "2893", "13779", None, "13313", "3443"],
        ["Ninh Bình", "39812", "39812", "56", "19392", "3314", "2088", "8939", "272", "4064", "709"],
        ["Đông Bắc", "329040", "327255", None, "89710", "40789", "16811", "1094", "1662", "27757", "2352"],
        ["Hà Giang", "25759", "25759", None, "3646", "1109", "95", None, None, "2039", "153.5"],
        ["Cao Bằng", "25516", "25516", None, None, None, None, None, None, None, None],
        ["Lào Cai", "19570", "19570", "42", "5093", None, "383", None, None, "4710", None],
        ["Bắc Cạn", "14002", "14002", "42", "602", "378", None, None, None, "224", "78"],
        ["Lạng Sơn", "31200", "30000", None, None, None, None, None, None, None, None],
        ["Tuyên Quang", "25816", "25637", "57", "11579", "5123", "2919", "613", "51", "2873", "286"],
        ["Yên Bái", "23927", "23927", "41", "8525", "6382", "975", "6", None, "1060", "108"],
        ["Thái Nguyên", "41500", "41167", "49", "13569", "7217", "3472", "87", "45", "2748", None],
        ["Phú Thọ", "34283", "34216", "48", "16267", "11252", "1812", "280", None, "2924", None],
        ["Bắc Giang", "59167", "59161", "49", "24578", "7856", "5840", "109", "1566", "8675", "1403"],
        ["Quảng Ninh", "28300", "28300", "46", "5852", "1473", "1315", None, None, "2504", "323"],
        ["Tây Bắc", "122557", "105278", None, "6551", "2246", "1294", "643", "0", "2368", "1276"],
        ["Lai Châu", "24682", "22160", "33", "239", "210", None, "29", None, None, None],
        ["Điện Biên", "37025", "36543", "32", "102", "46", "20", "36", None, None, "15"],
        ["Sơn La", "36436", "27213", "28", "1585", "470", None, None, None, "1115", "8"],
        ["Hoà Bình", "24414", "19362", "50", "4625", "1520", "1274", "578", None, "1253", "1253"],
        ["Bắc Trung Bộ", "182592", "166186", None, "88690", "48788", "12094", "3635", "4166", "19489", "0"],
        ["Thanh Hoá", "136836", "136836", "53", "42672", "20788", "4594", "3635", "1666", "11989", None],
        ["Nghệ An", "33156", "25150", "38", "45500", "28000", "7500", None, "2500", "7500", None],
        ["Hà Tĩnh", "6500", "3200", None, None, None, None, None, None, None, None],
        ["Quảng Bình", "1000", "1000", None, "518", None, None, None, None, None, None],
    ]
    for row in pl2_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 11, "period_type": "Cumulative", "report_date": "2009-11-15"}
        
        # 1. Lúa Mùa Gieo cấy
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vgc / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa Mùa Thu hoạch
        vth = normalize_number(row[2])
        if vth: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": vth / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Lúa Mùa Năng suất
        vns = normalize_number(row[3])
        if vns: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Yield", "value": vns, "unit": "quintal_per_ha", "data_type": "Actual"}))
        # 4. Cây vụ đông items
        items = [("Cây vụ đông", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Đậu tương", None), ("Lạc", None), ("Rau, đậu các loại", None), ("Khoai tây", None)]
        for idx, (c, s) in enumerate(items):
            v_vd = normalize_number(row[idx+4])
            if v_vd is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v_vd / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/11"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl1_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL1.json"))
    save_json(parse_pl2_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL2.json"))
    print("Successfully parsed PL1, PL2 for Nov 2009 with Region Mapping.")
