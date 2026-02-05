import json
import uuid
import os

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
        if s.find(".") < s.find(","): # 1.234,5
            s = s.replace(".", "").replace(",", ".")
        else: # 1,234.5
            s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "") # Thousands
            else: s = s.replace(",", ".") # Decimal
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
        "TD và MN phía Bắc": "Đông Bắc", "TD và MN phía\nBắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trung\nBộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung B": "Duyên hải Nam Trung Bộ", "d.h nam trg b": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Cao Bằng\n": "Cao Bằng"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
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

def parse_pl1():
    # Summary Table PL1 2011-03
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL1", "source_file": "2011_03_Phuluc_03_2011_PL1.md"}
    records = []
    t = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-15"}
    
    # [Item, Unit, Last Year, This Year, YoY]
    data = [
        ("Gieo cấy lúa đông xuân cả nước", "1000 ha", 3051.8, 3073.1, 100.7),
        ("Chia ra: - Miền Bắc", "1000 ha", 1098.6, 1094.8, 99.7),
        ("Trong đó: + Đồng bằng Sông Hồng", "1000 ha", 556.4, 554.0, 99.6),
        ("+ Bắc Trung bộ", "1000 ha", 337.5, 340.2, 100.8),
        ("- Miền Nam", "1000 ha", 1953.2, 1978.3, 101.3),
        ("Trong đó: Đồng bằng sông Cửu Long", "1000 ha", 1579.1, 1607.7, 101.8),
        ("Thu hoạch lúa đông xuân miền Nam", "1000 ha", 901.3, 1016.3, 112.8),
        ("Trong đó: Đồng bằng sông Cửu Long", "1000 ha", 895.9, 991.8, 110.7),
        ("Gieo cấy lúa hè thu ở ĐBSCL", "1000 ha", 144.9, 197.5, 136.3),
        ("Gieo trồng màu lương thực(*)", "1000 ha", 560.8, 590.0, 105.2),
        ("Trong đó: - Ngô", "1000 ha", 369.2, 353.7, 95.8),
        ("- Khoai lang", "1000 ha", 78.1, 83.5, 106.9),
        ("- Sắn", "1000 ha", 110.5, 141.2, 127.8),
        ("Gieo trồng cây công nghiệp ngắn ngày(*)", "1000 ha", 387.3, 438.2, 113.1),
        ("Trong đó: - Đậu tương", "1000 ha", 111.6, 102.7, 92.0),
        ("- Lạc", "1000 ha", 148.0, 165.5, 111.8),
        ("- Mía (trồng mới)", "1000 ha", 93.9, 133.9, 142.6),
        ("- Thuốc lá", "1000 ha", 21.8, 16.9, 77.3),
        ("Gieo trồng rau, đậu các loại(*)", "1000 ha", 366.6, 405.9, 110.7)
    ]
    
    for row in data:
        item_raw = row[0]
        unit = "1000_ha"
        val_2011 = row[3]
        yoy = row[4]
        
        # Determine Logic
        sector = "Cultivation"
        metric = "Area_Planted"
        if "Thu hoạch" in item_raw: metric = "Area_Harvested"
        
        # Determining Location
        loc_map = "Cả nước"
        if "Miền Bắc" in item_raw: loc_map = "Miền Bắc"
        elif "Miền Nam" in item_raw: loc_map = "Miền Nam"
        elif "Đồng bằng sông Cửu Long" in item_raw or "ĐBSCL" in item_raw: loc_map = "Đồng bằng sông Cửu Long"
        elif "Đồng bằng Sông Hồng" in item_raw: loc_map = "Đồng bằng sông Hồng"
        elif "Bắc Trung bộ" in item_raw: loc_map = "Bắc Trung Bộ"
        
        # Clean Item Name
        item_clean = item_raw.replace("Chia ra:", "").replace("Trong đó:", "").replace("+", "").replace("-", "").replace("(*)", "").strip()
        
        # Determine Commodity
        cmd = "Lúa"
        sub = "Đông Xuân" # Default to DX unless specified
        
        if "lúa đông xuân" in item_clean.lower(): pass
        elif "lúa hè thu" in item_clean.lower(): sub = "Hè Thu"
        elif "màu lương thực" in item_clean.lower(): cmd = "Màu lương thực"; sub = None; loc_map = "Cả nước"
        elif "ngô" in item_clean.lower(): cmd = "Ngô"; sub = None; loc_map = "Cả nước"
        elif "khoai lang" in item_clean.lower(): cmd = "Khoai lang"; sub = None; loc_map = "Cả nước"
        elif "sắn" in item_clean.lower(): cmd = "Sắn"; sub = None; loc_map = "Cả nước"
        elif "cây công nghiệp ngắn ngày" in item_clean.lower(): cmd = "Cây công nghiệp ngắn ngày"; sub = None; loc_map = "Cả nước"
        elif "đậu tương" in item_clean.lower(): cmd = "Đậu tương"; sub = None; loc_map = "Cả nước"
        elif "lạc" in item_clean.lower(): cmd = "Lạc"; sub = None; loc_map = "Cả nước"
        elif "mía" in item_clean.lower(): cmd = "Mía"; sub = "Trồng mới"; loc_map = "Cả nước"
        elif "thuốc lá" in item_clean.lower(): cmd = "Thuốc lá"; sub = None; loc_map = "Cả nước"
        elif "rau, đậu các loại" in item_clean.lower(): cmd = "Rau đậu các loại"; sub = None; loc_map = "Cả nước"
        
        gl = "Regional" if loc_map != "Cả nước" else "National"
        
        comp = {"comparison_type": "YoY", "comparison_value": float(yoy)} if yoy is not None else None
        
        records.append(create_record(metadata, t, loc_map, gl, {"sector": sector, "commodity": cmd, "sub_item": sub}, {"attribute": metric, "value": float(val_2011), "unit": unit, "data_type": "Actual"}, comp))
        
    return records

def parse_pl2():
    # Northern Winter-Spring Crop & Feb
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL2", "source_file": "2011_03_Phuluc_03_2011_PL2.md"}
    records = []
    t = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-15"}
    
    # [Name, Lua DX, Mau LT, Ngo, Khoai, San, Cay khac]
    data = [
        ["Miền Bắc", 1094767, 437510, 289652, 69615, 75959, 2284],
        ["ĐB sông Hồng", 554032, 104978, 80936, 20416, 2968, 657],
        ["Hà Nội", 100387, 26383, 20368, 4868, 690, 457],
        ["Hải Phòng", 38000, 3263, 2151, 1112, None, None],
        ["Vĩnh Phúc", 31260, 19145, 15087, 2438, 1420, 200],
        ["Bắc Ninh", 35929, 4937, 4132, 805, None, None],
        ["Hải Dương", 60077, 2540, 2540, None, None, None],
        ["Hưng Yên", 40305, 8624, 7624, 1000, None, None],
        ["Hà Nam", 33133, 7664, 7267, 396, None, None],
        ["Nam Định", 77800, 4652, 4652, 1533, None, None],
        ["Thái Bình", 82739, 12360, 9380, 2980, None, None],
        ["Ninh Bình", 41012, 9282, 5629, 2795, 858, None],
        ["Quảng Ninh", 13390, 6128, 3639, 2489, None, None],
        ["TD và MN phía Bắc", 200519, 179682, 115958, 21595, 40852, 1277],
        ["Hà Giang", 7913, 19413, 19413, None, None, None],
        ["Cao Bằng", 0, 3540, 3468, 72, None, None],
        ["Lào Cai", 3801, 5429, 5253, 176, None, None],
        ["Bắc Cạn", 1679, 3891, 3618, 42, 118, 113],
        ["Lạng Sơn", 2500, 5255, 4805, 400, None, 50],
        ["Tuyên Quang", 19562, 9284, 6447, 2837, None, None],
        ["Yên Bái", 17260, 18918, 11818, 1580, 5520, None],
        ["Thái Nguyên", 27930, 16945, 11796, 4207, 942, None],
        ["Phú Thọ", 35897, 27527, 17911, 1827, 7589, 200],
        ["Bắc Giang", 48445, 14780, 7856, 6924, None, None],
        ["Lai Châu", 4428, 736, 736, None, None, None],
        ["Điện Biên", 7897, 1013, 93, None, 920, None],
        ["Sơn La", 8706, 23943, 5180, None, 18763, None],
        ["Hoà Bình", 14501, 29008, 17564, 3530, 7000, 914],
        ["Bắc Trung Bộ", 340216, 152850, 92758, 27603, 32139, 350],
        ["Thanh Hoá", 120705, 59430, 33501, 9429, 16500, None],
        ["Nghệ An", 87500, 52157, 43247, 8910, None, None],
        ["Hà Tĩnh", 53743, 15011, 7760, 4664, 2587, None],
        ["Quảng Bình", 27100, 4300, 4300, None, None, None],
        ["Quảng Trị", 24029, 9700, 2200, 500, 7000, None],
        ["Thừa Thiên Huế", 27139, 12252, 1750, 4100, 6052, 350]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl3():
    # Northern Industrial Crops & Veg (PL3) - Note: PL3 in March corresponds to PL4 in Feb.
    # [Name, CN Total, Dau Tuong, Lac, Mia, Thuoc La, Cay khac, Rau Dau]
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL3", "source_file": "2011_03_Phuluc_03_2011_PL3.md"}
    records = []
    t = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-15"}
    
    data = [
        ["Miền Bắc", 270056, 99575, 126572, 32339, 7237, 4333, 205368],
        ["ĐB sông Hồng", 105584, 76382, 25524, 1116, 1000, 1562, 106751],
        ["Hà Nội", 38093, 31797, 5839, None, None, 457, 19677],
        ["Hải Phòng", 1000, None, None, None, 1000, None, 8559],
        ["Vĩnh Phúc", 7211, 4008, 2668, 209, None, 326, 5738],
        ["Bắc Ninh", 2580, 1309, 1271, None, None, None, 6147],
        ["Hải Dương", 162, 162, None, None, None, None, 16306],
        ["Hưng Yên", 3392, 2678, 714, None, None, None, 9631],
        ["Hà Nam", 11362, 11320, 42, None, None, None, 3009],
        ["Nam Định", 7155, 1422, 5733, None, None, None, 16907],
        ["Thái Bình", 16335, 13250, 3085, None, None, None, 12000],
        ["Ninh Bình", 15491, 9998, 4156, 907, None, 430, 5105],
        ["Quảng Ninh", 2803, 438, 2016, None, None, 349, 3672],
        ["TD và MN phía Bắc", 61796, 14692, 29773, 8523, 6187, 2621, 47008],
        ["Hà Giang", 11548, 6662, 4196, None, None, 690, 6613],
        ["Cao Bằng", 2138, 493, 20, 410, 1215, None, 430],
        ["Lào Cai", 2882, 2350, None, None, 532, None, 2195],
        ["Bắc Cạn", 1791, 551, 17, None, 1006, 217, 312],
        ["Lạng Sơn", 4134, None, None, None, 3334, 800, 3500],
        ["Tuyên Quang", 4372, 990, 3382, None, None, None, 1311],
        ["Yên Bái", 1172, None, 1172, None, None, None, 1558],
        ["Thái Nguyên", 3133, 545, 2488, None, 100, None, 5826],
        ["Phú Thọ", 5340, 1171, 4169, None, None, None, 5652],
        ["Bắc Giang", 11081, 376, 10705, None, None, None, 14288],
        ["Lai Châu", 134, 20, 114, None, None, None, 307],
        ["Điện Biên", 932, 622, 310, None, None, None, 125],
        ["Sơn La", 105, 105, None, None, None, None, 2320],
        ["Hoà Bình", 13034, 807, 3200, 8113, None, 914, 2571],
        ["Bắc Trung Bộ", 102675, 8500, 71275, 22700, 50, 150, 51609],
        ["Thanh Hoá", 36432, 8500, 15332, 12600, None, None, 16794],
        ["Nghệ An", 30223, None, 20223, 10000, None, None, 20841],
        ["Hà Tĩnh", 23777, None, 23777, None, None, None, 7358],
        ["Quảng Bình", 5100, None, 5100, None, None, None, 456],
        ["Quảng Trị", 3600, None, 3600, None, None, None, 1010],
        ["Thừa Thiên Huế", 3543, None, 3243, 100, 50, 150, 5150]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Mía", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Khác"}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl1()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl2()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl3()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL3.json"))
    print("Successfully parsed PL1, PL2, PL3 for March 2011 (Cultivation North Summary & Detail).")
