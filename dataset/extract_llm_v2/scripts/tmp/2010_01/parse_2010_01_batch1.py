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
    
    # Handle aliases
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Trung du và MN phía Bắc": "Trung du và miền núi phía Bắc",
        "Đông Bắc": "Đông Bắc",
        "Tây Bắc": "Tây Bắc"
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
    elif norm_loc in ["Miền Bắc", "Miền Nam"]:
        geo_context["region_id"] = "NORTH" if norm_loc == "Miền Bắc" else "SOUTH"
        geo_context["region_name"] = norm_loc
        geo_context["location_name"] = norm_loc

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

def parse_pl1_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL1", "source_file": "2010_01_PhuLuc_T01_2010_PL1.md"}
    records = []
    
    # Rows: Item, loc, v09, v10, cp_yoy, geo, attr
    rows = [
        ["Lúa", "Đông Xuân", "Cả nước", "1822.7", "1881.0", "103.2", "National", "Area_Planted"],
        ["Lúa", "Đông Xuân", "Miền Bắc", "102.5", "73.9", "72.1", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "Miền Nam", "1720.2", "1807.1", "105.1", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "ĐBS Cửu Long", "1410.5", "1495.3", "106.0", "Regional", "Area_Planted"],
        # Thu hoạch lúa mùa
        ["Lúa", "Mùa", "Miền Nam", "680.3", "647.0", "95.1", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "ĐBS Cửu Long", "265.0", "265.6", "100.2", "Regional", "Area_Harvested"],
        # Màu lương thực
        ["Màu lương thực", "Tổng số", "Cả nước", "282.4", "298.1", "105.6", "National", "Area_Planted"],
        ["Ngô", None, "Cả nước", "205.3", "206.2", "100.4", "National", "Area_Planted"],
        ["Khoai lang", None, "Cả nước", "57.8", "69.4", "120.1", "National", "Area_Planted"],
        # Cây công nghiệp ngắn ngày
        ["Cây công nghiệp ngắn ngày", "Tổng số", "Cả nước", "104.7", "127.2", "121.4", "National", "Area_Planted"],
        ["Đậu tương", None, "Cả nước", "60.2", "77.2", "128.2", "National", "Area_Planted"],
        ["Lạc", None, "Cả nước", "28.5", "30.3", "106.2", "National", "Area_Planted"],
        ["Rau, đậu các loại", "Tổng số", "Cả nước", "210.5", "226.6", "107.6", "National", "Area_Planted"],
    ]
    
    for r in rows:
        item, sub, loc, v09, v10, cp, geo, attr = r
        t10 = {"year": 2010, "month": 1, "period_type": "Cumulative", "report_date": "2010-01-15"}
        
        val10 = normalize_number(v10)
        if val10:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "2009"}
            records.append(create_record(metadata, t10, loc, geo, {"sector": "Cultivation", "commodity": item, "sub_item": sub}, {"attribute": attr, "value": val10, "unit": "1000_ha", "data_type": "Actual"}, comp))
        
        val09 = normalize_number(v09)
        if val09:
            t09 = {"year": 2009, "month": 1, "period_type": "Cumulative", "report_date": "2009-01-15"}
            records.append(create_record(metadata, t09, loc, geo, {"sector": "Cultivation", "commodity": item, "sub_item": sub}, {"attribute": attr, "value": val09, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}

def parse_pl2_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL2", "source_file": "2010_01_PhuLuc_T01_2010_PL2.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    
    pl2_data = [
        ["Miền Bắc", "73896", "26608", "23855", "9994", "1699", "4069", "10035"],
        ["ĐB sông Hồng", "3763", "4018", "5387", "2354", "3", "0", "796"],
        ["Hà Nội", None, "902", None, None, None, None, None],
        ["Hải Phòng", "186", "1435", "1714", None, None, None, None],
        ["Vĩnh Phúc", "2635", "438", "821", "606", "3", None, "212"],
        ["Bắc Ninh", None, "235", "764", "180", None, None, "584"],
        ["Hưng Yên", None, "120", None, None, None, None, None],
        ["Hà Nam", None, "14", None, None, None, None, None],
        ["Thái Bình", None, "624", "520", None, None, None, None],
        ["Ninh Bình", "125", "250", None, None, None, None, None],
        ["Quảng Ninh", "817", None, "1568", "1568", None, None, None],
        ["Trung du và MN phía Bắc", "9928", "10923", "0", "2116", "280", "0", "1780"],
        ["Hà Giang", "1100", None, None, "1700", None, None, None],
        ["Yên Bái", None, "9267", None, None, None, None, None],
        ["Phú Thọ", "2454", None, None, "289", "5", None, "202"],
        ["Bắc Giang", "295", "924", None, None, None, None, None],
        ["Lai Châu", None, "390", None, "27", None, None, None],
        ["Điện Biên", "5844", None, None, None, None, None, None],
        ["Sơn La", "235", "92", None, "100", None, None, None],
        ["Hoà Bình", None, "250", None, None, "275", None, "1578"],
        ["Bắc Trung Bộ", "60205", "11667", "18468", "5524", "1416", "4069", "7459"],
        ["Thanh Hoá", "7255", None, "1619", "910", None, None, "709"],
        ["Nghệ An", None, "1667", None, None, None, None, None],
        ["Hà Tĩnh", "30000", None, "2750", None, None, None, "2750"],
        ["Quảng Bình", "21950", None, "6505", "3520", "1416", "1569", None],
        ["Quảng Trị", None, "10000", "5300", "800", None, "2500", "2000"],
        ["Thừa Thiên Huế", "1000", None, "2294", "294", None, None, "2000"],
    ]
    
    for row in pl2_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2010, "month": 1, "period_type": "Cumulative", "report_date": "2010-01-15"}
        
        # 1. Lúa Đông Xuân Gieo cấy
        vdx = normalize_number(row[1])
        if vdx: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": vdx / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Mạ đã gieo
        vma = normalize_number(row[2])
        if vma: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Mạ"}, {"attribute": "Area_Planted", "value": vma, "unit": "ha", "data_type": "Actual"}))
        # 3. Màu gieo trồng items
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (c, s) in enumerate(items):
            v_vd = normalize_number(row[idx+3])
            if v_vd is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v_vd / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}

def parse_pl3_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL3", "source_file": "2010_01_PhuLuc_T01_2010_PL3.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    pl3_data = [
        ["Miền Bắc", "448714", "156897", "51138", "80238", "6847", "122477", "17252"],
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
        ["Đông Bắc", "92448", "41272", "18068", "1148", "1947", "28750", "2718"],
        ["Hà Giang", "3646", "1109", "95", None, None, "2039", "153.5"],
        ["Cao Bằng", "453", None, None, None, None, "341", "112"],
        ["Lào Cai", "2700", "211", None, None, None, "2110", "254"],
        ["Bắc Cạn", "1001", "626", "48", None, None, "327", "78"],
        ["Tuyên Quang", "11865", "5123", "3651", "642", "51", "4099", "286"],
        ["Yên Bái", "8530", "6382", "975", "6", None, "1060", "108"],
        ["Thái Nguyên", "15811", "7217", "4210", "103", "142", "4139", None],
        ["Phú Thọ", "17141", "11276", "1934", "288", "188", "3456", None],
        ["Bắc Giang", "25449", "7856", "5840", "109", "1566", "8675", "1403"],
        ["Quảng Ninh", "5852", "1473", "1315", None, None, "2504", "323"],
        ["Tây Bắc", "13441", "7334", "1307", "649", "0", "2715", "1436"],
        ["Lai Châu", "717", "547", None, "35", None, "0", "135"],
        ["Điện Biên", "4783", "4712", "20", "36", None, None, "15"],
        ["Sơn La", "2063", "555", "13", None, None, "1462", "33"],
        ["Hoà Bình", "5878", "1520", "1274", "578", None, "1253", "1253"],
        ["Bắc Trung Bộ", "106118", "54414", "17108", "3748", "3458", "26397", "993"],
        ["Thanh Hoá", "52759", "22867", "7308", "3748", "1666", "16177", "993"],
        ["Nghệ An", "49799", "30057", "9000", None, "1742", "9000", None],
        ["Quảng Bình", "1610", "1390", "170", None, "50", None, None],
        ["Quảng Trị", "1950", "100", "630", None, None, "1220", None],
    ]
    for row in pl3_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        # Since it's Winter crop 2009-2010 reported in Jan 2010
        t = {"year": 2010, "month": 1, "period_type": "Cumulative", "report_date": "2010-01-15"}
        
        items = [("Cây vụ đông", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Đậu tương", None), ("Lạc", None), ("Rau, đậu các loại", None), ("Khoai tây", None)]
        for idx, (c, s) in enumerate(items):
            if idx+1 >= len(row): continue
            v = normalize_number(row[idx+1])
            if v is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/01"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl1_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL1.json"))
    save_json(parse_pl2_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL2.json"))
    save_json(parse_pl3_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL3.json"))
    print("Successfully parsed PL1, PL2, PL3 for Jan 2010.")
