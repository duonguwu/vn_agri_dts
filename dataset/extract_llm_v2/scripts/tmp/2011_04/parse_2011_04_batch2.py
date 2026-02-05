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
        "D.H Nam TB": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Lâm Đồng": "Lâm Đồng", "Lâm\nĐồng": "Lâm Đồng"
    }
    
    # Fix broken names from <br> splits and typos
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    if "Lâm" in norm_loc and "Đồng" in norm_loc and len(norm_loc) < 20: norm_loc = "Lâm Đồng" # Fix aggressive breaks
    
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
    # Southern Rice (DX, HT) & Crops (PL4)
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL4", "source_file": "2011_04_Phuluc_04_2011_f_PL4.md"}
    records = []
    t = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-15"}
    
    # [Name, Lua DX Harv, %, Yield (Ta/ha), Prod (Ton), HT Planted, Mau Total, Ngo, Khoai, San, Cay khac]
    # Note: PL4 Structure in April is different from March.
    # April PL4:
    # Col 1: Name
    # Col 2: DX Harv Area (ha)
    # Col 3: % vs Sown
    # Col 4: Yield (Ta/ha)
    # Col 5: Production (Ton) !! - Wait, Check unit. Header "Đơn vị tính: ha". But Col 5 is "Sản lượng".
    # Usually huge numbers -> Ton? Line 29: 10,605,312 (Mien Nam). 10 million tons? reasonable for Mien Nam.
    # Col 6: HT Planted (ha).  "674,344"
    # Col 7: Mau Total
    # Col 8: Ngo
    # Col 9: Khoai
    # Col 10: San
    # Col 11: Cay khac
    
    data = [
        ["Miền Nam", 1648741, 82.8, 64.3, 10605312, 674344, 166511, 69332, 15351, 72014, 9813],
        ["D.H Nam TB", 74494, 42.3, 51.0, 379725, 22296, 56708, 15243, 3650, 36902, 913],
        ["TP Đà Nẵng", None, None, None, None, None, 853, 332, 220, 301, None],
        ["Quảng Nam", 7000, 16.4, None, None, None, 19410, 5910, 3100, 10200, 200],
        ["Quảng Ngãi", 5109, 14.0, 35.0, 17882, None, 20150, 4500, 150, 15500, None],
        ["Bình Định", 33477, 70.4, 62.5, 209106, 22146, 2288, 2288, None, None, None],
        ["Phú Yên", 9500, 36.1, 52.5, 49875, 150, 9777, 2213, 180, 7241, 143],
        ["Khánh Hoà", 19408, 100.0, 53.0, 102862, None, 4230, None, None, 3660, 570],
        ["Tây Nguyên", 19831, 25.7, 52.6, 104251, 995, 20780, 12815, 2249, 5717, None],
        ["Kon Tum", None, None, None, None, None, 636, 636, None, None, None],
        ["Gia Lai", 11300, 46.3, 52.0, 58760, None, 10122, 4587, 431, 5105, None],
        ["Đắc Lắc", 3657, 11.8, 50.0, 18285, None, 4495, 3191, 692, 612, None],
        ["Đắc Nông", 623, 13.8, 53.2, 3316, None, 3634, 2762, 872, None, None],
        ["Lâm Đồng", 4251, 39.2, 56.2, 23891, 995, 1893, 1639, 254, None, None], # Fixed name
        ["Đông Nam Bộ", 94530, 78.1, 52.1, 492891, 5648, 48283, 19371, 738, 27388, 786],
        ["TP Hồ Chí Minh", 5405, 100.0, 51.0, 27571, 650, None, None, None, None, None],
        ["Ninh Thuận", 3400, 23.3, 65.0, 22100, None, 5047, 2500, 69, 2478, None],
        ["Bình Phước", 2908, 100.0, 33.6, 9774, None, 1496, 440, 93, 832, 131],
        ["Tây Ninh", 32518, 71.8, 45.0, 146331, 4236, 23652, 3187, 127, 20051, 287],
        ["Bình Dương", 2596, 100.0, 44.6, 11570, 68, 1787, 126, None, 1489, 172],
        ["Đồng Nai", 13989, 100.0, 56.5, 79038, None, 11452, 8943, 123, 2215, 171],
        ["Bình Thuận", 29178, 93.3, 59.4, 173317, None, 3690, 3066, 278, 323, 23],
        ["Bà Rịa-V.Tàu", 4536, 92.2, 51.1, 23190, 694, 1159, 1109, 48, None, 2],
        ["ĐBS Cửu Long", 1459886, 90.3, 66.0, 9628445, 645405, 40740, 21904, 8714, 2008, 8114],
        ["Long An", 246258, 96.9, 57.9, 1426819, 50652, 8558, 4606, 48, 570, 3334],
        ["Đồng Tháp", 206195, 99.7, 70.7, 1457799, 167680, 4908, 2852, 1293, None, 763],
        ["An Giang", 211267, 89.7, 73.9, 1561822, 89547, 5843, 4364, 189, 460, 830],
        ["Tiền Giang", 80351, 100.0, 67.3, 540550, 40495, 4372, 2849, 240, 151, 1132],
        ["Vĩnh Long", 65830, 100.0, 66.0, 434775, 61227, 5528, 812, 4520, 118, 78],
        ["Bến Tre", 9366, 45.4, 53.5, 50108, None, 400, 250, 50, 100, None],
        ["Kiên Giang", 287364, 100.0, 68.4, 1965570, 57151, 730, None, None, None, 730],
        ["Cần Thơ", 88672, 100.0, 71.5, 634005, 77631, 490, 458, None, None, 32],
        ["Hậu Giang", 20317, 24.5, 69.0, 140185, 32368, 1338, 817, 221, None, 300],
        ["Trà Vinh", 47904, 78.4, 54.8, 262514, 14736, 4469, 2985, 807, 409, 268],
        ["Sóc Trăng", 122023, 88.3, 63.8, 778385, 48918, 3526, 1862, 1346, 200, 118],
        ["Bạc Liêu", 25571, 55.2, 65.0, 166212, 5000, 578, 49, None, None, 529],
        ["Cà Mau", 48768, 100.0, 43.0, 209702, None, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam TB", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        # Lua DX Harv
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Lua DX Yield
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Yield", "value": float(row[3]), "unit": "quintal_per_ha", "data_type": "Actual"}))
        
        # Lua DX Prod
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Production", "value": float(row[4])/1000, "unit": "1000_ton", "data_type": "Actual"}))
        
        # Lua HT Planted
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Mau LT etc.
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[9] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[9])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[10] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[10])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl5():
    # Southern Industrial & Veg (PL5)
    # [Name, Total CN, Dau Tuong, Lac, Vung, Thuoc La, Mia, Bong, DayLac (Col9), Rau, Dau]
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL5", "source_file": "2011_04_Phuluc_04_2011_f_PL5.md"}
    records = []
    t = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-15"}
    
    data = [
        ["Miền Nam", 179647, 4485, 40145, 16190, 9727, 107256, 865, 979, 203812, 28852],
        ["D.H Nam Trg Bộ", 52532, 506, 20676, 140, 786, 29937, 450, 37, 25930, 25930], # Rau=Dau duplicate suspect likely? Use as provided.
        ["TP Đà Nẵng", 1198, None, 784, None, None, 414, None, None, 469, None],
        ["Quảng Nam", 9258, None, 8370, None, 450, 250, 188, None, 10690, None],
        ["Quảng Ngãi", 8383, None, 4063, None, None, 4320, None, None, 5300, 1644],
        ["Bình Định", 7147, 221, 6926, None, None, None, None, None, 5432, 893],
        ["Phú Yên", 12559, 285, 533, 140, 336, 10966, 262, 37, 2571, 1866],
        ["Khánh Hoà", 13987, None, None, None, None, 13987, None, None, 1467, 976],
        ["Tây Nguyên", 13214, None, 118, None, 3502, 9292, 303, None, 28581, 4303],
        ["Kon Tum", 1769, None, 13, None, None, 1756, None, None, 749, 57],
        ["Gia Lai", 10942, None, 85, None, 3019, 7536, 303, None, 8071, 2310],
        ["Đắc Lắc", 503, None, 20, None, 483, None, None, None, 2655, 1184],
        ["Đắc Nông", 0, None, None, None, None, None, None, None, 16201, 545], # Used non-struck values
        ["Lâm Đồng", 0, None, None, None, None, None, None, None, None, None],
        ["Đông Nam Bộ", 29413, 276, 9432, 1019, 5316, 13258, 112, None, 30523, 10757],
        ["TP Hồ Chí Minh", 2300, None, None, None, None, 2300, None, None, 6295, None],
        ["Ninh Thuận", 2829, None, 131, 21, 782, 1853, 42, None, 2720, 1366],
        ["Bình Phước", 103, 24, 41, 6, 2, 30, None, None, 857, 143],
        ["Tây Ninh", 15675, None, 7687, 696, 3340, 3952, None, None, 8779, 4553],
        ["Bình Dương", 907, None, 555, 190, None, 162, None, None, 2219, 122],
        ["Đồng Nai", 2587, 252, 242, 39, 1020, 1027, 7, None, 4811, 1777],
        ["Bình Thuận", 4642, None, 668, 67, 54, 3843, 10, None, 1648, 2678],
        ["Bà Rịa-V.Tàu", 370, None, 108, None, 118, 91, 53, None, 3194, 118],
        ["ĐBS Cửu Long", 84488, 3703, 9919, 15031, 123, 54770, None, 942, 118778, 8414],
        ["Long An", 19984, None, 5635, 1697, 81, 12571, None, None, 9724, None],
        ["Đồng Tháp", 7739, 2437, 175, 4854, None, 96, None, 177, 8228, 1428],
        ["An Giang", 2647, 199, 478, 1907, 42, 21, None, None, 17272, 2979],
        ["Tiền Giang", 253, None, 98, None, None, 155, None, None, 21144, 121],
        ["Vĩnh Long", 1726, 717, 24, 918, None, 68, None, None, 11481, 430],
        ["Bến Tre", 5880, None, 80, None, None, 5800, None, None, 1936, None],
        ["Kiên Giang", 4512, None, None, None, None, 4512, None, None, 2335, None],
        ["Cần Thơ", 5877, 218, 5, 5655, None, None, None, None, 5224, 462],
        ["Hậu Giang", 13705, None, None, None, None, 13705, None, None, 6849, 561],
        ["Trà Vinh", 9615, None, 3358, None, None, 5492, None, 765, 13019, 702],
        ["Sóc Trăng", 10747, 133, 67, None, None, 10547, None, None, 14712, 1731],
        ["Bạc Liêu", 0, None, None, None, None, None, None, None, 4616, None],
        ["Cà Mau", 1803, None, None, None, None, 1803, None, None, 2237, None] # Used Line 61 values
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
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đay, Cói", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[9] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[9])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[10] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[10])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl4()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL4.json"))
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl5()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL5.json"))
    print("Successfully parsed PL4, PL5 for April 2011 (Cultivation South & Crops).")
