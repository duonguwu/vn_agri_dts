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
    
    # Handle aliases and normalized names
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ",
        "ĐB sông Cửu Long": "Đồng bằng sông Cửu Long"
    }
    
    norm_loc = alias_map.get(loc_name, loc_name)
    
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"
        geo_context["region_name"] = "Cả nước"
        geo_context["location_name"] = "Cả nước"

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

def parse_pl1_12():
    metadata = {"year": 2009, "month": 12, "appendix_number": "PL1", "source_file": "2009_12_Phuluc_T12_2009_PL1.md"}
    records = []
    
    # Rows from PL1 summary section
    rows = [
        ["Lúa", "Đông Xuân", "1009.4", "1240.9", "122.9", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "898.8", "1120.8", "124.7", "ĐBS Cửu Long", "Regional", "Area_Planted"],
        ["Lúa", "Mùa", "453.6", "465.6", "102.6", "Miền Nam", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "110.9", "103.9", "93.7", "ĐBS Cửu Long", "Regional", "Area_Harvested"],
        ["Cây vụ đông", "Tổng số", "437.5", "440.7", "100.7", "Miền Bắc", "Regional", "Area_Planted"],
        ["Ngô", "Ngô đông", "170.6", "150.4", "88.2", "Miền Bắc", "Regional", "Area_Planted"],
        ["Khoai lang", None, "62.9", "49.1", "78.0", "Miền Bắc", "Regional", "Area_Planted"],
        ["Đậu tương", None, "64.0", "80.2", "125.2", "Miền Bắc", "Regional", "Area_Planted"],
        ["Rau, đậu các loại", None, "119.0", "120.5", "101.2", "Miền Bắc", "Regional", "Area_Planted"],
    ]
    
    for r in rows:
        item, sub, v08, v09, c_yoy, loc, geo, attr = r
        t09 = {"year": 2009, "month": 12, "period_type": "Cumulative", "report_date": "2009-12-15"}
        
        # 2009 record
        val09 = normalize_number(v09)
        if val09:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, t09, loc, geo, {"sector": "Cultivation", "commodity": item, "sub_item": sub}, {"attribute": attr, "value": val09, "unit": "1000_ha", "data_type": "Actual"}, comp))
        
        # 2008 record
        val08 = normalize_number(v08)
        if val08:
            t08 = {"year": 2008, "month": 12, "period_type": "Cumulative", "report_date": "2008-12-15"}
            records.append(create_record(metadata, t08, loc, geo, {"sector": "Cultivation", "commodity": item, "sub_item": sub}, {"attribute": attr, "value": val08, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl2_12():
    metadata = {"year": 2009, "month": 12, "appendix_number": "PL2", "source_file": "2009_12_Phuluc_T12_2009_PL1.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    pl2_data = [
        ["Miền Bắc", "440678", "150374", "49082", "80209", "7605", "120474", "17252"],
        ["ĐB sông Hồng", "236707", "53877", "14655", "74693", "1442", "64615", "12106"],
        ["Hà Nội", "64160", "13041", "4171", "30869", "608", "12407", "1052"],
        ["Hải Phòng", "5247", "1925", None, None, None, "601", None],
        ["Vĩnh Phúc", "24207", "14124", "2326", "4144", "404", "3209", "12"],
        ["Bắc Ninh", "11201", "1332", "710", "2068", "19", "4235", "2838"],
        ["Hải Dương", "23096", "3151", "541", "270", None, "14415", "372"],
        ["Hưng Yên", "16354", "4905", "655", "2758", "97", "6942", "572"],
        ["Hà Nam", "18698", "3697", "399", "11249", "42", "2907", "404"],
        ["Nam Định", "14324", "1959", "870", "618", None, "2315", "2619"],
        ["Thái Bình", "40028", "6430", "2893", "13779", None, "13313", "3443"],
        ["Ninh Bình", "19392", "3314", "2090", "8939", "272", "4272", "793"],
        ["Đông Bắc", "92127", "41272", "17462", "1119", "1947", "27247", "2718"],
        ["Hà Giang", "3646", "1109", "95", None, None, "2039", "153.5"],
        ["Cao Bằng", "453", None, None, None, None, "341", "112"],
        ["Lào Cai", "2700", "211", None, None, None, "2110", "254"],
        ["Bắc Cạn", "1001", "626", "48", None, None, "327", "78"],
        ["Tuyên Quang", "11865", "5123", "3089", "613", "51", "2873", "286"],
        ["Yên Bái", "8530", "6382", "975", "6", None, "1060", "108"],
        ["Thái Nguyên", "15490", "7217", "4166", "103", "142", "3862", None],
        ["Phú Thọ", "17141", "11276", "1934", "288", "188", "3456", None],
        ["Bắc Giang", "25449", "7856", "5840", "109", "1566", "8675", "1403"],
        ["Quảng Ninh", "5852", "1473", "1315", None, None, "2504", "323"],
        ["Tây Bắc", "8775", "2668", "1307", "649", "0", "2715", "1436"],
        ["Lai Châu", "717", "547", None, "35", None, "0", "135"],
        ["Điện Biên", "117", "46", "20", "36", None, None, "15"],
        ["Sơn La", "2063", "555", "13", None, None, "1462", "33"],
        ["Hoà Bình", "5878", "1520", "1274", "578", None, "1253", "1253"],
        ["Bắc Trung Bộ", "103069", "52557", "15658", "3748", "4216", "25897", "993"],
        ["Thanh Hoá", "52759", "22867", "7308", "3748", "1666", "16177", "993"],
        ["Nghệ An", "46750", "28200", "7550", None, "2500", "8500", None],
        ["Quảng Bình", "1610", "1390", "170", None, "50", None, None],
        ["Quảng Trị", "1950", "100", "630", None, None, "1220", None],
    ]
    for row in pl2_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 12, "period_type": "Cumulative", "report_date": "2009-12-15"}
        
        items = [("Cây vụ đông", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Đậu tương", None), ("Lạc", None), ("Rau, đậu các loại", None), ("Khoai tây", None)]
        for idx, (c, s) in enumerate(items):
            if idx+1 >= len(row): continue
            v = normalize_number(row[idx+1])
            if v is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/12"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl1_12(), os.path.join(out_dir, "2009_12_Phuluc_T12_2009_PL1.json"))
    save_json(parse_pl2_12(), os.path.join(out_dir, "2009_12_Phuluc_T12_2009_PL2.json"))
    print("Successfully parsed PL1, PL2 for Dec 2009.")
