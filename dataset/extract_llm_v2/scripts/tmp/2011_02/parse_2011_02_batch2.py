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
        "D H N\nT\nBộ\n.am rung": "Duyên hải Nam Trung Bộ", "Long An\n": "Long An", "Kiên Giang\n": "Kiên Giang",
        "Cà Mau\n": "Cà Mau", "Lâ\nĐồ\n  m ng": "Lâm Đồng"
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

def parse_pl3():
    # Southern Rice & Crops (PL3)
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL3", "source_file": "2011_02_Phuluc_02_2011_PL3.md"}
    records = []
    t = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-15"}
    
    # [Name, Lua DX Planted, Lua DX Harv, %, Mau LT, Ngo, Khoai, San, Cay khac]
    data = [
        ["Miền Nam", 1906829, 377117, 20, 114983, 55721, 9715, 42164, 7384],
        ["D H N\nT\nBộ\n.am rung", 156454, 0, None, 37730, 13708, 3378, 20397, 247],
        ["TP Đà Nẵng", 3479, None, None, 853, 332, 220, 301, None],
        ["Quảng Nam", 42550, None, None, 14170, 5300, 2850, 5820, 200],
        ["Quảng Ngãi", 36763, None, None, 15750, 4420, 150, 11180, None],
        ["Bình Định", 47500, None, None, 2162, 2162, None, None, None],
        ["Phú Yên", 26162, None, None, 4795, 1494, 158, 3096, 47],
        ["Khánh Hoà", 0, None, None, 0, None, None, None, None],
        ["Tây Nguyên", 74619, 71, None, 18700, 11002, 2192, 5506, 0],
        ["Kon Tum", 6039, None, None, 312, 312, None, None, None],
        ["Gia Lai", 24046, None, None, 9505, 4115, 426, 4964, None],
        ["Đắc Lắc", 30191, 71, None, 3924, 2770, 612, 542, None],
        ["Đắc Nông", 4149, None, None, 3647, 2747, 900, None, None],
        ["Lâm Đồng", 10194, None, None, 1312, 1058, 254, None, None],
        ["Đông Nam Bộ", 109341, 9689, 9, 33747, 17119, 598, 15591, 439],
        ["TP Hồ Chí Minh", 5353, None, None, 500, 500, None, None, None],
        ["Ninh Thuận", 14591, None, None, 2720, 2500, 69, 151, None],
        ["Bình Phước", 2265, None, None, 1211, 349, 60, 671, 131],
        ["Tây Ninh", 38486, None, None, 13832, 2352, 32, 11438, 10],
        ["Bình Dương", 2237, None, None, 1360, 86, 54, 1118, 102],
        ["Đồng Nai", 11306, 8407, None, 9413, 7267, 85, 1890, 171],
        ["Bình Thuận", 30216, 1100, None, 3561, 2955, 260, 323, 23],
        ["Bà Rịa-V.Tàu", 4887, 182, None, 1150, 1110, 38, None, 2],
        ["ĐBS Cửu Long", 1566415, 367357, 23, 24806, 13892, 3547, 670, 6698],
        ["Long An", 253524, 78554, 31, 7324, 3990, None, None, 3334],
        ["Đồng Tháp", 206942, 47843, 23, 1399, 931, 100, None, 368],
        ["An Giang", 235402, 5890, 3, 4325, 3260, 141, 272, 652],
        ["Tiền Giang", 80351, 33550, 42, 3096, 1753, 218, 50, 1075],
        ["Vĩnh Long", 65912, 17070, 26, 2459, 302, 2083, 19, 55],
        ["Bến Tre", 20632, None, 0, 400, 250, 50, 100, None],
        ["Kiên Giang", 287383, 82528, 29, 0, None, None, None, None],
        ["Cần Thơ", 88635, 2264, 3, 252, 238, 14, None, None],
        ["Hậu Giang", 83040, 9585, 12, 803, 439, 63, None, 300],
        ["Trà Vinh", 61067, 6522, 11, 2015, 1427, 266, 159, 163],
        ["Sóc Trăng", 137945, 78023, 57, 2114, 1272, 612, 70, 160],
        ["Bạc Liêu", 45582, 5528, 12, 620, 30, None, None, 590],
        ["Cà Mau", 0, None, 0, None, None, None, None, None] # Cà Mau empty or 0
    ]
    
    regional_list = ["Miền Nam", "D H N\nT\nBộ\n.am rung", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        # Lua DX Planted
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Lua DX Harvested
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Mau LT etc.
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl5():
    # Southern Industrial & Veg (PL5)
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL5", "source_file": "2011_02_Phuluc_02_2011_PL5.md"}
    records = []
    t = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-15"}
    
    # [Name, Total CN, Dau Tuong, Lac, Vung, Thuoc La, Mia, Bong, Day, Rau, Dau]
    data = [
        ["Miền Nam", 112863, 797, 34452, 3310, 8051, 65142, 785, 326, 136707, 19243],
        ["D.H Nam Trg Bộ", 28307, 466, 18723, 57, 665, 7990, 370, 37, 17234, 17234],
        ["TP Đà Nẵng", 968, None, 671, None, None, 297, None, None, 352, None],
        ["Quảng Nam", 7976, 10, 7200, 10, 410, 150, 196, None, 4800, 2000],
        ["Quảng Ngãi", 7964, None, 3990, None, None, 3975, None, None, 5300, 1644],
        ["Bình Định", 6575, 187, 6388, None, None, None, None, None, 5067, 647],
        ["Phú Yên", 4824, 269, 474, 47, 255, 3568, 174, 37, 1715, 744],
        ["Khánh Hoà", 0, None, None, None, None, None, None, None, None, None],
        ["Tây Nguyên", 12193, 0, 75, 0, 3329, 8486, 303, 0, 19691, 3431],
        ["Kon Tum", 2157, None, 9, None, None, 2148, None, None, 714, 61],
        ["Gia Lai", 9533, None, 46, None, 2847, 6338, 303, None, 6604, 2137],
        ["Đắc Lắc", 502, None, 20, None, 482, None, None, None, 2471, 703],
        ["Đắc Nông", 0, None, None, None, None, None, None, None, 834, 220],
        ["Lâm Đồng", 0, None, None, None, None, None, None, None, 9068, 311],
        ["Đông Nam Bộ", 21611, 187, 8472, 731, 4040, 8069, 112, 0, 23032, 8247],
        ["TP Hồ Chí Minh", 2480, None, 180, None, None, 2300, None, None, 4332, None],
        ["Ninh Thuận", 1084, None, 140, 60, 782, 60, 42, None, 2720, 1366],
        ["Bình Phước", 77, 22, 37, 3, 2, 13, None, None, 598, 126],
        ["Tây Ninh", 10510, None, 6798, 442, 2151, 1119, None, None, 5128, 2289],
        ["Bình Dương", 617, None, 382, 140, None, 95, None, None, 1708, 68],
        ["Đồng Nai", 1885, 165, 210, 19, 936, 548, 7, None, 4111, 1650],
        ["Bình Thuận", 4591, None, 617, 67, 54, 3843, 10, None, 1563, 2629],
        ["Bà Rịa-V.Tàu", 367, None, 108, None, 115, 91, 53, None, 2872, 119],
        ["ĐBS Cửu Long", 50752, 144, 7182, 2522, 17, 40598, 0, 289, 76749, 2530],
        ["Long An", 18488, None, 5112, 805, None, 12571, None, None, 7636, None],
        ["Đồng Tháp", 130, None, None, 45, None, None, None, 85, 4321, 434],
        ["An Giang", 935, 85, 273, 545, 17, 15, None, None, 11982, None],
        ["Tiền Giang", 108, None, 65, None, None, 43, None, None, 16726, 65],
        ["Vĩnh Long", 276, 20, 5, 224, None, 27, None, None, 4457, 336],
        ["Bến Tre", 5880, None, 80, None, None, 5800, None, None, 1936, None],
        ["Kiên Giang", 0, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 939, 31, 5, 903, None, None, None, None, 2449, 325],
        ["Hậu Giang", 12072, None, None, None, None, 12072, None, None, 3273, 419],
        ["Trà Vinh", 5039, None, 1636, None, None, 3199, None, 204, 8106, 320],
        ["Sóc Trăng", 6885, 8, 6, None, None, 6871, None, None, 12950, 631],
        ["Bạc Liêu", 0, None, None, None, None, None, None, None, 1693, None],
        ["Cà Mau", 0, None, None, None, None, None, None, None, 1221, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl3()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl5()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL5.json"))
    print("Successfully parsed PL3, PL5 for February 2011 (Cultivation South).")
