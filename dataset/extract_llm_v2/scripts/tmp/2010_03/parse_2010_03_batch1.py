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
    # Special case: some MDs use dot as thousands separator (e.g., 1.098.554)
    # If there's more than one dot, or if it's a dot between digits without a following comma, it's likely a thousands separator.
    # However, to be safe and consistent with previous batches:
    # If there is a dot but no comma, and it's 3 digits from the right or from another dot, it's thousands.
    # A simpler approach: if most values are large integers, dot is thousands.
    # Let's try to detect format.
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    # If we have 1.098.554 -> we want 1098554.0
    if s.count('.') >= 1:
        # If the part after the last dot has 3 digits, it's likely a thousands separator (in VN reports)
        # UNLESS it's a known decimal like .5 or .0
        parts = s.split('.')
        if len(parts) > 2: # 1.098.554
            s = "".join(parts)
        elif len(parts) == 2:
            if len(parts[1]) == 3: # 99.870
                s = "".join(parts)
            else: # 2773.9 or something else
                pass 
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "ĐB Sông Cửu Long": "Đồng bằng sông Cửu Long",
        "DBSCL": "Đồng bằng sông Cửu Long", "Trung du và MN phía Bắc": "Đông Bắc",
        "Trung du và MN PB": "Đông Bắc",
        "D.H Nam Trung\nBộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung Bộ ": "Duyên hải Nam Trung Bộ"
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

def parse_pl2a_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL2a", "source_file": "2010_03_PhuLuc_T03_2010_PL2a.md"}
    records = []
    t = {"year": 2010, "month": 3, "period_type": "Monthly", "report_date": "2010-03-15"}
    
    # Table 2a (Northern - ha)
    # Rows: loc, ldx_gc, total_màu, ngo, khoai, san, cay_khac
    data_2a = [
        ["Miền Bắc", 1098554, 232309, 128065, 11446, 59838, 25567],
        ["ĐB sông Hồng", 556365, 40015, 18084, 1664, 2534, 10342],
        ["Hà Nội", 99870, 2347, 1617, 320, 210, 200],
        ["Hải Phòng", 39565, 2670, 170, None, None, 2500],
        ["Vĩnh Phúc", 30955, 4452, 2366, 260, 1212, 613],
        ["Bắc Ninh", 36882, 1782, 1198, None, None, 584],
        ["Hải Dương", 63360, 7391, None, None, None, None],
        ["Hưng Yên", 38500, 2810, 2810, None, None, None],
        ["Hà Nam", 34370, 3228, 3228, None, None, None],
        ["Nam Định", 77600, 6250, 1450, None, 300, 4500],
        ["Thái Bình", 81500, 4045, 2100, None, None, 1945],
        ["Ninh Bình", 41069, 1245, 1170, 75, None, None],
        ["Quảng Ninh", 12694, 3795, 1974, 1009, 812, None],
        ["Trung du và MN phía Bắc", 204652, 94347, 69870, 3189, 15972, 5316],
        ["Hà Giang", 7129, 16935, 16935, None, None, None],
        ["Cao Bằng", 250, 11756, 11561, None, None, 195],
        ["Lào Cai", 5720, 1908, 1908, None, None, None],
        ["Bắc Cạn", 5436, 5039, 4670, 106, 120, 143],
        ["Lạng Sơn", 200, 2118, 145, None, None, 1973],
        ["Tuyên Quang", 19492, 5512, 5360, 152, None, None],
        ["Yên Bái", 17388, 8130, 6300, None, 1830, None],
        ["Thái Nguyên", 26700, 4895, 2713, 1052, 1130, None],
        ["Phú Thọ", 35030, 5333, 4740, 391, None, 202],
        ["Bắc Giang", 49356, 1123, 1123, None, None, None],
        ["Lai Châu", 5359, 1409, 1409, None, None, None],
        ["Điện Biên", 7814, 1800, 500, None, 1300, None],
        ["Sơn La", 9077, 9270, 4100, None, 3945, 1225],
        ["Hoà Bình", 15701, 19119, 8406, 1488, 7647, 1578],
        ["Bắc Trung Bộ", 337537, 97948, 40111, 6593, 41332, 9909],
        ["Thanh Hoá", 120198, 22926, 12240, 2877, 7100, 709],
        ["Nghệ An", 86500, 37150, 17400, 2300, 16950, 500],
        ["Hà Tĩnh", 53430, 5179, 2426, None, None, 2750],
        ["Quảng Bình", 27646, 13258, 4110, 1416, 5782, 1950],
        ["Quảng Trị", 23763, 11185, 2185, None, 7000, 2000],
        ["Thừa Thiên Huế", 26000, 8250, 1750, None, 4500, 2000],
    ]
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data_2a:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+3])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2b_2010_03():
    # Inside PL2a file
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL2b", "source_file": "2010_03_PhuLuc_T03_2010_PL2a.md"}
    records = []
    t = {"year": 2010, "month": 3, "period_type": "Monthly", "report_date": "2010-03-15"}
    
    # Rows: loc, dx_gc, dx_th, dx_yield, dx_prod, ht_gc, mau_total, ngo, khoai, san, khac
    data_2b = [
        ["Miền Nam", 1953208, 901334, None, 5818, 144949, 126654, 63121, 9179, 50652, 5481],
        ["D.H Nam Trung Bộ", 186308, 1960, 50, 10, None, 41410, 14742, 2452, 24216, None],
        ["TP Đà Nẵng", 4000, None, None, None, None, 853, 323, 268, 262, None],
        ["Quảng Nam", 52912, None, None, None, None, 15995, 5960, 115, 9920, None],
        ["Quảng Ngãi", 36664, 1960, 50, 10, None, 8387, 3466, 1900, 3021, None],
        ["Bình Định", 47421, None, None, None, None, 9869, 1877, None, 7992, None],
        ["Phú Yên", 25931, None, None, None, None, 5266, 2076, 169, 3021, None],
        ["Khánh Hoà", 19380, None, None, None, None, 1040, 1040, None, None, None],
        ["Tây Nguyên", 73772, 3450, 47, 16, None, 18092, 11644, 1744, 4.704, None], # MD says 4.704 (thousands?)
        ["Kon Tum", 6453, None, None, None, None, 606, 606, None, None, None],
        ["Gia Lai", 23739, None, None, None, None, 8838, 4402, 349, 4087, None],
        ["Đắc Lắc", 29019, None, None, None, None, 4181, 2938, 626, 617, None],
        ["Đắc Nông", 3853, None, None, None, None, 3482, 2713, 769, None, None],
        ["Lâm Đồng", 10708, 3450, 47, 16, None, 985, 985, None, None, None],
        ["Đông Nam Bộ", 114037, None, None, 0, None, 43992, 19456, 365, 20469, 3702],
        ["TP Hồ Chí Minh", 6637, None, None, None, None, 769, 769, None, None, None],
        ["Ninh Thuận", 13104, None, None, None, None, 2264, 2264, None, None, None],
        ["Bình Phước", 2897, None, None, None, None, 989, 526, 149, 314, None],
        ["Tây Ninh", 45247, None, None, None, None, 23903, 3554, None, 17058, 3291],
        ["Bình Dương", 2546, None, None, None, None, 1927, 141, 171, 1204, 411],
        ["Đồng Nai", 14565, None, None, None, None, 9593, 8055, None, 1538, None],
        ["Bình Thuận", 23787, None, None, None, None, 3399, 3115, None, 284, None],
        ["Bà Rịa-V.Tàu", 5254, None, None, None, None, 1148, 1032, 45, 71, None],
        ["ĐBS Cửu Long", 1579091, 895924, None, 5792, 144949, 23160, 17279, 4618, 1263, 1779],
        ["Long An", 250493, 115567, 55, 639, 13047, 6455, 6455, None, None, None],
        ["Đồng Tháp", 207732, 170675, 71, 1217, 28453, 1253, 826, 106, None, 321],
        ["An Giang", 252363, 8400, 72, 60, 598, 1720, 1600, 30, 90, None],
        ["Tiền Giang", 82272, 79110, 68, 538, 39612, 4096, 2438, None, 200, 1458],
        ["Vĩnh Long", 66902, 67710, 68, 416, 3824, 3292, 660, 2484, 148, None],
        ["Bến Tre", 20812, 196, 46, 1, None, 542, 350, 64, 128, None],
        ["Kiên Giang", 284145, 169641, 64, 1086, None, 0, None, None, None, None],
        ["Cần Thơ", 89673, 75303, 73, 547, 2246, 141, 141, None, None, None],
        ["Hậu Giang", 84504, 40250, 68, 273, 912, 1063, 1063, None, None, None],
        ["Trà Vinh", 55916, 29434, 59, 172, 6110, 3836, 2731, 656, 449, None],
        ["Sóc Trăng", 139648, 122702, 61, 742, 50147, 2541, 1015, 1278, 248, None],
        ["Bạc Liêu", 44631, 16936, 60, 102, None, None, None, None, None, None],
    ]
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data_2b:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Yield", "value": v/10.0, "unit": "ton_per_ha", "data_type": "Estimated"}))
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Production", "value": v/1.0, "unit": "1000_ton", "data_type": "Estimated"}))
        v = normalize_number(row[5])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[6])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây có củ khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+7])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

def parse_pl3a_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL3a", "source_file": "2010_03_PhuLuc_T03_2010_PL3a.md"}
    records = []
    t = {"year": 2010, "month": 3, "period_type": "Monthly", "report_date": "2010-03-15"}
    
    # Rows: loc, cn_total, dau_tuong, lac, mia, thuoc_la, rau_dau_total
    data_3a = [
        ["Miền Bắc", 247703, 106405, 108693, 35019, 8840, 174709],
        ["ĐB sông Hồng", 90886, 76754, 14743, 16, 2747, 90753],
        ["Hà Nội", 31185, 30529, 656, None, None, 10351],
        ["Hải Phòng", 2547, 200, None, None, 2347, 10258],
        ["Vĩnh Phúc", 5636, 4876, 2799, 16, None, 4847],
        ["Bắc Ninh", 2090, 2363, 918, None, None, 4679],
        ["Hải Dương", 270, 270, None, None, None, 19000],
        ["Hưng Yên", 3251, 2758, 493, None, None, 9379],
        ["Hà Nam", 11605, 11377, 356, None, None, 1426],
        ["Nam Định", 3758, 758, 3000, None, None, 7883],
        ["Thái Bình", 15679, 13779, 1500, None, 400, 15188],
        ["Ninh Bình", 11993, 9224, 2769, None, None, 4051],
        ["Quảng Ninh", 2872, 620, 2252, None, None, 3691],
        ["Trung du và MN phía Bắc", 57213, 26980, 27562, 4529, 6013, 35159],
        ["Hà Giang", 9680, 5364, 4316, None, None, 4843],
        ["Cao Bằng", 4702, 6086, 20, 731, 3058, 453],
        ["Lào Cai", 1895, 1565, None, None, 330, 2014],
        ["Bắc Cạn", 1839, 367, 310, 38, 1124, 556],
        ["Lạng Sơn", 1501, None, None, None, 1501, 650],
        ["Tuyên Quang", 4280, 925, 3355, None, None, 2221],
        ["Yên Bái", 1445, 702, 743, None, None, 2293],
        ["Thái Nguyên", 3775, 795, 2980, None, None, 5606],
        ["Phú Thọ", 5545, 1549, 3995, None, None, 2710],
        ["Bắc Giang", 9016, 647, 8369, None, None, 10040],
        ["Lai Châu", 1302, 1171, 109, None, None, None],
        ["Điện Biên", 5000, 5300, 150, None, None, None],
        ["Sơn La", 55, 50, None, 5, None, 1520],
        ["Hoà Bình", 7178, 2459, 3215, 3755, None, 2253],
        ["Bắc Trung Bộ", 99604, 2671, 66388, 30474, 80, 48797],
        ["Thanh Hoá", 21700, 2371, 12864, 6474, None, 21542],
        ["Nghệ An", 45443, 300, 21063, 24000, 80, 19424],
        ["Hà Tĩnh", 20240, None, 20240, None, None, 3366],
        ["Quảng Bình", 4863, None, 4863, None, None, 586],
        ["Quảng Trị", 4358, None, 4358, None, None, 3879],
        ["Thừa Thiên Huế", 3000, None, 3000, None, None, None],
    ]
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data_3a:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", "Trồng mới"), ("Thuốc lá", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[6])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl3b_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL3b", "source_file": "2010_03_PhuLuc_T03_2010_PL3b.md"}
    records = []
    t = {"year": 2010, "month": 3, "period_type": "Monthly", "report_date": "2010-03-15"}
    
    # Rows: loc, total_cn, dau_tuong, lac, vung, thuoc_la, mia, bong, day_lac, rau, dau
    data_3b = [
        ["Miền Nam", 117611, 5173, 39350, 5551, 12989, 58867, 394, 1186, 171554, 20386],
        ["D.H Nam Trg Bộ", 21725, 659, 19689, 71, 869, 6402, 394, 29, 19949, 19949],
        ["TP Đà Nẵng", 735, None, 618, None, None, 117, None, None, 369, 78],
        ["Quảng Nam", 9232, None, 8264, None, 502, 289, 177, None, 8500, 3400],
        ["Quảng Ngãi", 3924, None, 3924, None, None, None, None, None, 3900, 1450],
        ["Bình Định", 6566, 334, 6232, None, None, None, None, None, 4964, 683],
        ["Phú Yên", 1158, 325, 541, 71, 367, 5996, 217, 29, 2016, 1183],
        ["Khánh Hoà", 110, None, 110, None, None, None, None, None, 200, None],
        ["Tây Nguyên", 16745, None, 168, None, 6684, 9404, None, None, 32448, 3891],
        ["Kon Tum", 4300, None, 58, None, 2145, 2097, None, None, 854, 119],
        ["Gia Lai", 11936, None, 90, None, 4539, 7307, None, None, 7836, 1714],
        ["Đắc Lắc", 509, None, 20, None, None, None, None, None, 2528, 1588],
        ["Đắc Nông", 0, None, None, None, None, None, None, None, 7411, 55],
        ["Lâm Đồng", 0, None, None, None, None, None, None, None, 13819, 415],
        ["Đông Nam Bộ", 28588, 302, 11694, 2042, 5396, 9154, None, None, 27478, 7364],
        ["TP Hồ Chí Minh", 1980, None, 190, None, None, 1790, None, None, 4275, None],
        ["Ninh Thuận", 300, None, None, None, None, 300, None, None, 2819, 895],
        ["Bình Phước", None, None, None, None, None, None, None, None, 816, None],
        ["Tây Ninh", 22030, None, 9499, 1240, 4596, 6695, None, None, 7178, 2513],
        ["Bình Dương", 929, None, 630, None, None, 299, None, None, 1955, 150],
        ["Đồng Nai", 2122, 291, 261, 770, 800, None, None, None, 4117, 1911],
        ["Bình Thuận", 1096, None, 1064, 32, None, None, None, None, 2118, 1763],
        ["Bà Rịa-V.Tàu", 131, 11, 50, None, None, 70, None, None, 4200, 132],
        ["ĐBS Cửu Long", 50553, 4212, 7799, 3438, 40, 33907, None, 1157, 91679, 2337],
        ["Long An", 4775, None, 4242, 533, None, None, None, None, 8460, None],
        ["Đồng Tháp", 5387, 2975, 16, 2283, 15, 13, None, 85, 5083, None],
        ["An Giang", 337, 100, 73, 145, 1, 18, None, None, 10741, 1181],
        ["Tiền Giang", None, None, None, None, None, None, None, None, 19198, None],
        ["Vĩnh Long", 1588, 700, 29, 205, None, 144, None, 510, 9845, 243],
        ["Bến Tre", 6321, None, 122, None, None, 5992, None, 207, 2317, 3],
        ["Kiên Giang", None, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 614, 304, 14, 272, 24, None, None, None, 2246, 222],
        ["Hậu Giang", 13123, None, None, None, None, 13123, None, None, 872, 77],
        ["Trà Vinh", 7681, 2, 3303, None, None, 4021, None, 355, 11908, 611],
        ["Sóc Trăng", 10596, None, None, None, None, 10596, None, None, 21009, None],
        ["Bạc Liêu", 131, 131, None, None, None, None, None, None, None, None],
    ]
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data_3b:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[9])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[10])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/03"
    os.makedirs(out_dir, exist_ok=True)
    all_records = []
    all_records.extend(parse_pl2a_2010_03())
    all_records.extend(parse_pl2b_2010_03())
    all_records.extend(parse_pl3a_2010_03())
    all_records.extend(parse_pl3b_2010_03())
    
    # Split into separate files as per convention or save as one?
    # Convention is one JSON per MD appendix.
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl2a_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL2a.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl2b_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL2b.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl3a_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL3a.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl3b_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL3b.json"))
    
    print("Successfully parsed PL2a, PL2b, PL3a, PL3b for March 2010.")
