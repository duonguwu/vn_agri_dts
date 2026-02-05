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
        "TD và MN phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "Vùng Duyên hải miền Trung": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ", "Vùng Đông Nam bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Vùng Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long"
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

def parse_pl1():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL1", "source_file": "2010_05_PHULUC_T05_2010_PL1.md"}
    records = []
    t10 = {"year": 2010, "month": 5, "period_type": "Monthly", "report_date": "2010-05-15"}
    t09 = {"year": 2009, "month": 5, "period_type": "Monthly", "report_date": "2009-05-15"}
    
    # [Name, Loc, V09, V10, Attr, Cmd, Sub]
    data = [
        ["Gieo cấy lúa hè thu miền Nam", "Miền Nam", 1344.6, 1257.8, "Area_Planted", "Lúa", "Hè Thu"],
        ["Đồng bằng sông Cửu Long", "Đồng bằng sông Cửu Long", 1191.7, 1117.2, "Area_Planted", "Lúa", "Hè Thu"],
        ["Thu hoạch lúa đông xuân miền Nam", "Miền Nam", 1844.1, 1913.7, "Area_Harvested", "Lúa", "Đông Xuân"],
        ["Vùng Duyên hải miền Trung", "Duyên hải Nam Trung Bộ", 159.8, 181.5, "Area_Harvested", "Lúa", "Đông Xuân"],
        ["Vùng Tây Nguyên", "Tây Nguyên", 50.7, 59.4, "Area_Harvested", "Lúa", "Đông Xuân"],
        ["Vùng Đông Nam bộ", "Đông Nam Bộ", 89.9, 114.0, "Area_Harvested", "Lúa", "Đông Xuân"],
        ["Vùng Đồng bằng sông Cửu Long", "Đồng bằng sông Cửu Long", 1543.7, 1558.8, "Area_Harvested", "Lúa", "Đông Xuân"],
        
        # PL1 also has general national stats for other crops
        ["Gieo trồng màu lương thực", "Cả nước", 1089.5, 1071.9, "Area_Planted", "Màu lương thực", "Tổng số"],
        ["Ngô", "Cả nước", 715.0, 706.5, "Area_Planted", "Ngô", None],
        ["Khoai lang", "Cả nước", 99.4, 102.3, "Area_Planted", "Khoai lang", None],
        ["Sắn", "Cả nước", 250.9, 238.1, "Area_Planted", "Sắn", None],
        ["Gieo trồng cây công nghiệp ngắn ngày", "Cả nước", 465.4, 479.3, "Area_Planted", "Cây công nghiệp ngắn ngày", "Tổng số"],
        ["Lạc", "Cả nước", 194.5, 177.8, "Area_Planted", "Lạc", None],
        ["Đậu tương", "Cả nước", 129.8, 141.0, "Area_Planted", "Đậu tương", None],
        ["Thuốc lá, thuốc lào", "Cả nước", 19.6, 22.5, "Area_Planted", "Thuốc lá", None],
        ["Mía (trồng mới)", "Cả nước", 102.3, 113.0, "Area_Planted", "Mía", "Trồng mới"],
        ["Gieo trồng rau, đậu các loại", "Cả nước", 501.2, 508.8, "Area_Planted", "Rau đậu các loại", "Tổng số"],
    ]

    for r in data:
        loc, v09, v10, attr, cmd, sub = r[1], r[2], r[3], r[4], r[5], r[6]
        gl = "National" if loc in ["Cả nước", "Miền Nam", "Miền Bắc"] else "Regional"
        if v10: records.append(create_record(metadata, t10, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))
        if v09: records.append(create_record(metadata, t09, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v09), "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2a():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL2a", "source_file": "2010_05_PHULUC_T05_2010_PL2a.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Monthly", "report_date": "2010-05-15"}
    
    # [Name, DX_Planted, Tro, DX_Harvested, Yield, Mau_Total, Ngo, Khoai, San, Khac]
    data = [
        ["Miền Bắc", 1137330, 921562, 155679, None, 545022, 362943, 28635, 130400, 35674],
        ["ĐB sông Hồng", 563757, 512064, 14557, None, 57591, 28470, 7232, 4398, 17651],
        ["Hà Nội", 101787, 101787, 6000, 58, 11717, 7377, 3000, 1300, 200],
        ["Hải Phòng", 39204, 35000, None, 64, 2670, 170, None, None, 2500],
        ["Vĩnh Phúc", 30976, 30976, 4402, None, 6547, 2391, 299, 1722, 2135],
        ["Bắc Ninh", 37008, 29150, None, None, 1819, 1235, None, None, 584],
        ["Hải Dương", 63360, 61780, None, None, 7391, 1200, 900, None, 5291],
        ["Hưng Yên", 38500, 33898, None, None, 3068, 3068, None, None, None],
        ["Hà Nam", 34370, 34370, None, None, 3228, 3228, None, None, None],
        ["Nam Định", 77600, 77300, None, None, 6250, 1450, None, 300, 4500],
        ["Thái Bình", 81500, 51200, None, None, 4045, 2100, None, None, 1945],
        ["Ninh Bình", 41603, 41603, 3155, 59, 1245, 1170, 75, None, None],
        ["Quảng Ninh", 17849, 15000, 1000, 50, 9611, 5080, 2959, 1076, 496],
        ["TD và MN phía Bắc", 233444, 89731, 1099, None, 375359, 286552, 10105, 81507, 9663],
        ["Hà Giang", 9256, None, None, 43, 25662, 36232, 649, 3761, 2119],
        ["Cao Bằng", 2300, None, None, None, 11756, 11561, None, None, 195],
        ["Lào Cai", 9062, None, None, None, 19798, 9879, 400, 4889, None],
        ["Bắc Cạn", 7380, None, None, 46, 11356, 9707, 258, 1144, 247],
        ["Lạng Sơn", 14497, None, None, None, 15073, 13100, None, None, 1973],
        ["Tuyên Quang", 19492, 19492, 163, None, 7333, 6933, 400, None, None],
        ["Yên Bái", 17438, 17438, 100, 53, 21351, 8033, 778, 12023, 517],
        ["Thái Nguyên", 28263, None, None, 50, 11805, 6492, 1604, 3709, None],
        ["Phú Thọ", 35534, 34439, None, 49, 13896, 5863, 637, 7194, 202],
        ["Bắc Giang", 51686, None, None, 54, 5234, 1470, 1564, 2200, None],
        ["Lai Châu", 5414, None, None, None, 21949, 16792, None, 5157, None],
        ["Điện Biên", 7862, 7862, 836, 56, 30554, 23418, None, 7136, None],
        ["Sơn La", 9278, None, None, None, 141511, 115249, 82, 23285, 2895],
        ["Hoà Bình", 15982, 10500, None, 51, 38081, 21823, 3734, 11009, 1515],
        ["Bắc Trung Bộ", 340130, 319767, 140023, None, 112073, 47921, 11298, 44495, 8359],
        ["Thanh Hoá", 120198, 120198, 20525, 59, 34409, 20000, 4500, 9200, 709],
        ["Nghệ An", 87482, 81000, 30000, 60, 36745, 17400, 2382, 16463, 500],
        ["Hà Tĩnh", 53569, 53569, 37498, 51, 5176, 2426, None, None, 2750],
        ["Quảng Bình", 27646, 22000, 15000, None, 13258, 4110, 1416, 5782, 1950],
        ["Quảng Trị", 24083, 20000, 23000, None, 12185, 2185, None, 8000, 2000],
        ["Thừa Thiên Huế", 27152, 23000, 14000, None, 10300, 1800, 3000, 5050, 450],
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        # Lua DX
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Flowering", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"})) # Trỗ
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Mau
        v = normalize_number(row[5])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Crops
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+6])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2b():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL2b", "source_file": "2010_05_PHULUC_T05_2010_PL2b.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Monthly", "report_date": "2010-05-15"}
    
    # [Name, DX_Planted, DX_Harvested, HT_Planted, Mau_Total, Ngo, Khoai, San]
    data = [
        ["Miền Nam", 1935524, 1913699, 1257814, 289429, 165593, 16179, 107657],
        ["D.H Nam Trung Bộ", 186308, 181492, 59891, 70689, 24974, 6913, 38802],
        ["TP Đà Nẵng", 4000, 4000, None, 1199, 669, 268, 262],
        ["Quảng Nam", 52912, 52912, 37000, 26720, 12300, 4500, 9920],
        ["Quảng Ngãi", 36664, 36000, 1500, 17920, 4920, 1900, 11100],
        ["Bình Định", 47421, 45700, 19830, 13491, 3969, None, 9522],
        ["Phú Yên", 25931, 23500, 245, 8696, 2076, 169, 6451],
        ["Khánh Hoà", 19380, 19380, 1316, 2663, 1040, 76, 1547],
        ["Tây Nguyên", 74161, 59420, 7980, 91374, 68344, 3523, 19507],
        ["Kon Tum", 6583, 4000, None, 653, 653, None, None],
        ["Gia Lai", 23998, 17400, 1327, 11834, 7211, 340, 4283],
        ["Đắc Lắc", 29019, 28105, 1942, 41433, 36641, 868, 3924],
        ["Đắc Nông", 3853, 2811, 1245, 28272, 14972, 2000, 11300],
        ["Lâm Đồng", 10708, 7104, 3466, 9182, 8867, 315, None],
        ["Đông Nam Bộ", 114037, 114037, 72772, 93283, 46142, 365, 46776],
        ["TP Hồ Chí Minh", 6637, 6637, 2469, 821, 821, None, None],
        ["Ninh Thuận", 13104, 13104, 2000, 2264, 2264, None, None],
        ["Bình Phước", 2897, 2897, None, 989, 526, 149, 314],
        ["Tây Ninh", 45247, 45247, 37378, 20803, 3745, None, 17058],
        ["Bình Dương", 2546, 2546, 500, 1516, 141, 171, 1204],
        ["Đồng Nai", 14565, 14565, 10057, 29927, 21227, None, 8700],
        ["Bình Thuận", 23787, 23787, 19914, 22624, 7524, None, 15100],
        ["Bà Rịa-V.Tàu", 5254, 5254, 454, 14339, 9894, 45, 4400],
        ["ĐBS Cửu Long", 1561018, 1558750, 1117171, 34083, 26133, 5378, 2572],
        ["Long An", 251025, 251025, 116925, 4654, 4654, None, None],
        ["Đồng Tháp", 207672, 207672, 196841, 3051, 2409, 642, None],
        ["An Giang", 234212, 232185, 228051, 6307, 6187, 30, 90],
        ["Tiền Giang", 81878, 81878, 78636, 2960, 2760, None, 200],
        ["Vĩnh Long", 66902, 66902, 62750, 5899, 3267, 2484, 148],
        ["Bến Tre", 20812, 20812, 12700, 1091, 899, 64, 128],
        ["Kiên Giang", 284145, 284145, 144902, None, None, None, None],
        ["Cần Thơ", 89673, 89673, 82854, 387, 387, None, None],
        ["Hậu Giang", 84504, 84263, 71995, 1291, 1291, None, None],
        ["Trà Vinh", 55916, 55916, 23290, 5296, 3264, 880, 1152],
        ["Sóc Trăng", 139648, 139648, 92447, 3147, 1015, 1278, 854],
        ["Bạc Liêu", 44631, 44631, 5780, None, None, None, None],
        ["Cà Mau", None, None, None, None, None, None, None]
    ]

    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Mau
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+5])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

def parse_pl3a():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL3a", "source_file": "2010_05_PHULUC_T05_2010_PL3a.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Monthly", "report_date": "2010-05-15"}
    
    # [Name, CCN_Total, DauTuong, Lac, Mia, ThuocLa, CCN_Khac, RauDau]
    data = [
        ["Miền Bắc", 202332, 35138, 119032, 26433, 13187, 8544, 148053],
        ["ĐB sông Hồng", 34957, 8220, 21436, 224, 2747, 2331, 68604],
        ["Hà Nội", 9108, 1907, 5767, 200, None, 1234, 10351],
        ["Hải Phòng", 2674, 200, None, None, 2347, 127, 10933],
        ["Vĩnh Phúc", 3864, 774, 2805, 24, None, 261, 4847],
        ["Bắc Ninh", 1521, 295, 935, None, None, 292, 1550],
        ["Hải Dương", 1980, 780, 1200, None, None, None, 12000],
        ["Hưng Yên", 3697, 2758, 717, None, None, 222, 9379],
        ["Hà Nam", 484, 128, 356, None, None, None, 1426],
        ["Nam Định", 3758, 758, 3000, None, None, None, 7883],
        ["Thái Bình", 1900, None, 1500, None, 400, None, 1500],
        ["Ninh Bình", 2769, None, 2769, None, None, None, 4051],
        ["Quảng Ninh", 3202, 620, 2387, None, None, 195, 4684],
        ["TC và MN phía Bắc", 86506, 26153, 34054, 10490, 10290, 5520, 44212],
        ["Hà Giang", 11196, 6517, 4469, None, None, 210, 8713],
        ["Cao Bằng", 5950, 1105, 70, 1238, 3303, 234, 924],
        ["Lào Cai", 2821, 1931, 448, None, 442, None, 2014],
        ["Bắc Cạn", 2285, 461, 310, 70, 1444, None, 985],
        ["Lạng Sơn", 10561, 1600, 1500, 200, 5016, 2245, 650],
        ["Tuyên Quang", 5141, 1139, 4002, None, None, None, 2221],
        ["Yên Bái", 4065, 1616, 1434, 630, None, 385, 4597],
        ["Thái Nguyên", 4895, 1344, 3551, None, None, None, 4160],
        ["Phú Thọ", 6115, 1749, 4353, None, None, 13, 2461],
        ["Bắc Giang", 9563, 706, 8550, None, 85, 222, 5036],
        ["Lai Châu", 1637, 723, 645, None, None, 269, 358],
        ["Điện Biên", 4573, 3111, 912, None, None, 550, 950],
        ["Sơn La", 5481, 3428, 370, 291, None, 1392, 2398],
        ["Hoà Bình", 12223, 723, 3439, 8061, None, None, 8745],
        ["Bắc Trung Bộ", 80869, 765, 63542, 15719, 150, 693, 35237],
        ["Thanh Hoá", 23184, 465, 12150, 10569, None, None, 11000],
        ["Nghệ An", 24151, 300, 18771, 5000, 80, None, 11168],
        ["Hà Tĩnh", 19940, None, 19661, None, None, 279, 3366],
        ["Quảng Bình", 4863, None, 4863, None, None, None, 586],
        ["Quảng Trị", 4757, None, 4500, None, None, 257, 3879],
        ["Thừa Thiên Huế", 3974, None, 3597, 150, 70, 157, 5238],
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TC và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        # CCN
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", None), ("Thuốc lá", None), ("Cây công nghiệp khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            
        # Rau Dau
        v = normalize_number(row[7])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/05"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl1()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl2a()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL2a.json"))
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl2b()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL2b.json"))
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl3a()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL3a.json"))
    print("Successfully parsed PL1, PL2a, PL2b, PL3a for May 2010.")
