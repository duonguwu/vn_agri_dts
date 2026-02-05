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
        "Lâ\nĐồ\n  m ng": "Lâm Đồng" # Correcting broken name
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.replace("\n", "").strip()
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

def parse_pl4():
    # Southern Provinces Rice (Harvest Mua, Planted DX) and Veg
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL4", "source_file": "2011_01_Phuluc_01_2011_PL4.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-15"}
    
    # Structure Step 452
    # [Name, Mua 2010 Harvested, % vs Planted, DX 2011 Planted, DX 2011 Harvested, Total Mau LT, Ngo, Khoai, San, Cay khac]
    
    data = [
        ["Miền Nam", 604876, 77.0, 1861021, 126339, 78160, 38562, 7394, 25551, 6653],
        ["D.H Nam Trung Bộ", 93139, 100.0, 169511, None, 19700, 9582, 3304, 6574, 240],
        ["TP Đà Nẵng", 3300, 100.0, 3469, None, 358, 92, 212, 54, None],
        ["Quảng Nam", 44124, 100.0, 42145, None, 13155, 4285, 2850, 5820, 200],
        ["Quảng Ngãi", 6000, 100.0, 36763, None, 2550, 2400, 150, None, None],
        ["Bình Định", 23494, 100.0, 47334, None, 2030, 2030, None, None, None],
        ["Phú Yên", 7721, 100.0, 25800, None, 1607, 775, 92, 700, 40],
        ["Khánh Hoà", 8500, 100.0, 14000, None, 0, None, None, None, None],
        ["Tây Nguyên", 140533, 100.0, 55310, None, 8253, 3777, 402, 4074, 0],
        ["Kon Tum", 15859, 100.0, 3900, None, 256, 256, None, None, None],
        ["Gia Lai", 46437, 100.0, 18730, None, 7997, 3521, 402, 4074, None],
        ["Đắc Lắc", 55459, 100.0, 24000, None, 0, None, None, None, None],
        ["Đắc Nông", 6432, 100.0, 80, None, 0, None, None, None, None],
        ["Lâm Đồng", 16346, 100.0, 8600, None, 0, None, None, None, None],
        ["Đông Nam Bộ", 163061, 93.4, 100801, 8407, 29909, 14616, 518, 14480, 295],
        ["TP Hồ Chí Minh", 7000, 70.0, 6637, None, 500, 500, None, None, None],
        ["Ninh Thuận", 12500, 91.8, 11055, None, 2626, 2500, 60, 66, None],
        ["Bình Phước", 10000, 100.0, 2134, None, 814, 341, 46, 308, 119],
        ["Tây Ninh", 50000, 88.7, 38486, None, 13832, 2352, 32, 11438, 10],
        ["Bình Dương", 5000, 93.5, 1661, None, 868, 83, 25, 714, 46],
        ["Đồng Nai", 28000, 97.9, 8407, 8407, 6732, 4949, 57, 1631, 95],
        ["Bình Thuận", 38561, 100.0, 27909, None, 3423, 2815, 262, 323, 23],
        ["Bà Rịa-V.Tàu", 12000, 98.8, 4512, None, 1114, 1076, 36, None, 2],
        ["ĐBS Cửu Long", 208143, 55.2, 1535398, 117932, 20298, 10587, 3170, 423, 6118],
        ["Long An", 8522, 84.6, 247488, 34687, 5371, 2241, None, None, 3130],
        ["Đồng Tháp", None, None, 206591, 7025, 1217, 817, 40, None, 360],
        ["An Giang", None, None, 233947, None, 3727, 2876, 101, 139, 611],
        ["Tiền Giang", None, None, 80351, None, 2552, 1403, 205, 35, 909],
        ["Vĩnh Long", None, None, 65912, 3116, 1984, 254, 1690, 15, 25],
        ["Bến Tre", 27348, 83.4, 14266, None, 270, 120, 50, 100, None],
        ["Kiên Giang", 19322, 31.0, 286347, 17942, 0, None, None, None, None],
        ["Cần Thơ", None, None, 88635, None, 201, 187, 14, None, None],
        ["Hậu Giang", None, None, 82210, 6390, 1975, 1291, 383, None, 300],
        ["Trà Vinh", 70066, 76.4, 55202, None, 826, 608, 109, 72, 37],
        ["Sóc Trăng", 14213, 68.4, 137945, 43792, 1585, 789, 578, 62, 156],
        ["Bạc Liêu", 27807, 44.6, 36504, 4980, 590, None, None, None, 590],
        ["Cà Mau", 40865, 46.0, None, None, 0, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        # Lua Mua 2010
        if row[1] is not None: records.append(create_record({"year": 2010, "appendix_number": "PL4", "month": 1, "source_file": "2011_01_Phuluc_01_2011_PL4.md"}, {"year": 2010, "month": 1, "period_type": "Monthly", "report_date": "2011-01-15"}, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}, {"comparison_type": "vs_Planted", "comparison_value": float(row[2])} if row[2] else None))
        
        # Lua DX 2011 Planted
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Lua DX 2011 Harvested
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Mau LT etc.
        # Mau LT
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Ngo
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Khoai
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # San
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Cay khac
        if row[9] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[9])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl5():
    # Southern Industrial Crops & Veg
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL5", "source_file": "2011_01_Phuluc_01_2011_PL5.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-15"}
    
    # Step 453 Structure
    # [Name, Total CCN, Dau Tuong, Lac, Vung, Thuoc La, Mia, Bong, Day, Rau, Dau]
    
    data = [
        ["Miền Nam", 66857, 664, 19205, 1224, 6281, 39032, 327, 124, 100358, 12734],
        ["D.H Nam Trg Bộ", 8463, 427, 7105, 16, 85, 803, 0, 27, 6306, 6306], # Rau 6306, Dau 6306? Check row 29 in view.
        # Line 29: "6,306|6,306|". Same value for Rau and Dau?
        # Maybe typo in report or manual transcription error?
        # Let's check TP Da Nang (line 30): Rau 235, Dau empty.
        # Binh Dinh (Line 33): Rau 4991, Dau 607.
        # Phu Yen: Rau 1080, Dau 571.
        # Sum Rau = 235 + ...
        # Let's assume input is correct as per view.
        ["TP Đà Nẵng", 738, None, 558, None, None, 180, None, None, 235, None],
        ["Bình Định", 6470, 187, 6283, None, None, None, None, None, 4991, 607],
        ["Phú Yên", 1255, 240, 264, 16, 85, 623, None, 27, 1080, 571],
        ["Tây Nguyên", 9492, 0, 39, 0, 2818, 6332, 303, 0, 6201, 1933],
        ["Kon Tum", 2142, None, 9, None, None, 2133, None, None, 569, 24],
        ["Gia Lai", 7350, None, 30, None, 2818, 4199, 303, None, 5632, 1909],
        ["Lâ\nĐồ\n  m ng", 0, None, None, None, None, None, None, None, None, None], # Corrected map above
        ["Đông Nam Bộ", 19602, 126, 7951, 579, 3361, 7561, 24, 0, 18514, 7634],
        ["TP Hồ Chí Minh", 2480, None, 180, None, None, 2300, None, None, 3800, None],
        ["Ninh Thuận", 670, None, 140, None, 450, 60, 20, None, 2500, 1350],
        ["Bình Phước", 65, 17, 32, 3, None, 13, None, None, 586, 120],
        ["Tây Ninh", 10510, None, 6798, 442, 2151, 1119, None, None, 5128, 2289],
        ["Bình Dương", 388, None, 240, 59, None, 89, None, None, 1452, 58],
        ["Đồng Nai", 1108, 109, 144, 8, 706, 137, 4, None, 3531, 1504],
        ["Bình Thuận", 4381, None, 417, 67, 54, 3843, None, None, 1517, 2313],
        ["ĐBS Cửu Long", 29299, 111, 4110, 629, 17, 24336, 0, 97, 69337, 1989],
        ["Long An", 16295, None, 3474, 250, None, 12571, None, None, 7190, None],
        ["Đồng Tháp", 109, None, None, 24, None, None, None, 85, 4314, 321],
        ["An Giang", 685, 79, 236, 338, 17, 15, None, None, 10270, None],
        ["Tiền Giang", 60, None, 49, None, None, 11, None, None, 12832, 56],
        ["Vĩnh Long", 0, None, None, None, None, None, None, None, 3728, 226],
        ["Bến Tre", 45, None, 45, None, None, None, None, None, 1936, None],
        ["Cần Thơ", 51, 30, 5, 17, None, None, None, None, 2046, 261],
        ["Hậu Giang", 5210, None, None, None, None, 5210, None, None, 9094, 419],
        ["Trà Vinh", 1040, None, 296, None, None, 732, None, 12, 3054, 205],
        ["Sóc Trăng", 5804, 2, 5, None, None, 5797, None, None, 12950, 501],
        ["Bạc Liêu", 0, None, None, None, None, None, None, None, 1244, None],
        ["Cà Mau", None, None, None, None, None, None, None, None, 680, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        # [Name, Total CCN, Dau Tuong, Lac, Vung, Thuoc La, Mia, Bong, Day, Rau, Dau]
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Vừng", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Mía", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Bông", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đay", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[9] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[9])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[10] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[10])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/01"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl4()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL4.json"))
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl5()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL5.json"))
    print("Successfully parsed PL4-PL5 for January 2011 (Cultivation South).")
