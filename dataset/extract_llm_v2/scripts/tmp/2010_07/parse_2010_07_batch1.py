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
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế"
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
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL1", "source_file": "2010_07_phuluc_07_2010_PL1.md"}
    records = []
    t10 = {"year": 2010, "month": 7, "period_type": "Monthly", "report_date": "2010-07-15"}
    t09 = {"year": 2009, "month": 7, "period_type": "Monthly", "report_date": "2009-07-15"}
    
    # [Item, V09, V10]
    data = [
        ["Thu hoạch lúa hè thu miền Nam", 578.1, 724.7],
        ["Đồng bằng sông Cửu Long", 557.2, 724.7],
        ["Gieo cấy lúa mùa cả nước", 1140.7, 1149.9],
        ["Miền Bắc", 927.8, 884.8],
        ["Đồng bằng sông Hồng", 450.4, 487.6],
        ["Miền Nam", 212.9, 265.1],
        ["ĐBSCL_Mua", 115.6, 149.2], # Label trick
        ["Gieo trồng màu lương thực", 1359.0, 1365.7],
        ["Ngô", 780.0, 866.9],
        ["Khoai lang", 113.5, 111.5],
        ["Sắn", 424.5, 349.4],
        ["Gieo trồng cây công nghiệp ngắn ngày", 553.6, 592.8],
        ["Lạc", 200.4, 196.2],
        ["Đậu tương", 145.8, 155.6],
        ["Thuốc lá", 24.5, 26.4],
        ["Mía (trồng mới)", 147.8, 141.2],
        ["Gieo trồng rau, đậu các loại", 559.8, 603.3]
    ]
    
    for row in data:
        item_name, v09, v10 = row
        loc = "Cả nước"
        
        if "miền Nam" in item_name: loc = "Miền Nam"
        if "Miền Bắc" in item_name: loc = "Miền Bắc"
        if "Định bằng sông Hồng" in item_name: loc = "Đồng bằng sông Hồng"
        if "Đồng bằng sông Cửu Long" in item_name: loc = "Đồng bằng sông Cửu Long"
        if item_name == "ĐBSCL_Mua": loc = "Đồng bằng sông Cửu Long"; item_name = "Lúa Mùa" # Fix trick
        
        # Determine Context
        if "Thu hoạch lúa" in item_name or item_name == "Đồng bằng sông Cửu Long":
            cmd = "Lúa"; sub = "Hè Thu"; attr = "Area_Harvested"
        elif "Gieo cấy lúa mùa" in item_name or item_name in ["Miền Bắc", "Miền Nam", "Đồng bằng sông Hồng", "Lúa Mùa"]:
            cmd = "Lúa"; sub = "Mùa"; attr = "Area_Planted"
        elif "màu lương thực" in item_name: cmd = "Màu lương thực"; sub = "Tổng số"; attr = "Area_Planted"
        elif "cây công nghiệp" in item_name: cmd = "Cây công nghiệp ngắn ngày"; sub = "Tổng số"; attr = "Area_Planted"
        elif "rau, đậu" in item_name: cmd = "Rau đậu các loại"; sub = "Tổng số"; attr = "Area_Planted"
        elif item_name in ["Ngô", "Khoai lang", "Sắn", "Lạc", "Đậu tương", "Thuốc lá"]:
             cmd = item_name; sub = None; attr = "Area_Planted"
        elif "Mía" in item_name: cmd = "Mía"; sub = "Trồng mới"; attr = "Area_Planted"
        else: cmd = item_name; sub = None; attr = "Area_Planted"

        gl = "National" if loc in ["Cả nước", "Miền Bắc", "Miền Nam"] else "Regional"
        
        if v10: records.append(create_record(metadata, t10, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))
        if v09: records.append(create_record(metadata, t09, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v09), "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2a():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL2a", "source_file": "2010_07_phuluc_07_2010_PL2a.md"}
    records = []
    t = {"year": 2010, "month": 7, "period_type": "Monthly", "report_date": "2010-07-15"}
    
    # [Loc, LuaMua, Mau_Total, Ngo, Khoai, San, Khac]
    data = [
        ["Miền Bắc", 884805, 866402, 605978, 91558, 130848, 38017],
        ["ĐB sông Hồng", 487592, 126317, 81958, 22309, 4398, 17651],
        ["Hà Nội", 100548, 25132, 16461, 7171, 1300, 200],
        ["Hải Phòng", 22710, 4910, 2110, 300, None, 2500],
        ["Vĩnh Phúc", 28687, 24151, 17539, 2755, 1722, 2135],
        ["Bắc Ninh", 22274, 3861, 2567, 710, None, 584],
        ["Hải Dương", 49953, 11083, 4351, 1441, None, 5291],
        ["Hưng Yên", 40458, 9088, 8433, 655, None, None],
        ["Hà Nam", 34836, 9150, 8751, 399, None, None],
        ["Nam Định", 68400, 9079, 3409, 870, 300, 4500],
        ["Thái Bình", 70605, 13368, 8530, 2893, None, 1945],
        ["Ninh Bình", 37431, 6875, 4710, 2165, None, None],
        ["Quảng Ninh", 11690, 9619, 5097, 2950, 1076, 496],
        ["TD và MN phía Bắc", 263247, 517352, 392320, 31370, 81655, 12007],
        ["Hà Giang", 19478, 50669, 42182, 649, 3761, 4077],
        ["Cao Bằng", 12986, 35253, 34387, 671, None, 195],
        ["Lào Cai", 10748, 27443, 21610, 558, 4889, 386],
        ["Bắc Cạn", 4500, 12416, 10711, 314, 1144, 247],
        ["Lạng Sơn", 10527, 18940, 16967, None, None, 1973],
        ["Tuyên Quang", 23889, 17720, 13669, 4051, None, None],
        ["Yên Bái", 19000, 28708, 14415, 1753, 12023, 517],
        ["Thái Nguyên", 32083, 24663, 14677, 6277, 3709, None],
        ["Phú Thọ", 31293, 29269, 19302, 2571, 7194, 202],
        ["Bắc Giang", 38415, 20334, 10730, 7404, 2200, None],
        ["Lai Châu", 18505, 22573, 17268, None, 5305, None],
        ["Điện Biên", 13887, 35286, 28130, 20, 7136, None],
        ["Sơn La", 3636, 142724, 116449, 95, 23285, 2895],
        ["Hoà Bình", 24300, 51355, 31823, 7008, 11009, 1515],
        ["Bắc Trung Bộ", 133966, 222733, 131700, 37879, 44795, 8359],
        ["Thanh Hoá", 113713, 80768, 56309, 14550, 9200, 709],
        ["Nghệ An", 4553, 84236, 56286, 10987, 16463, 500], # Check Nghệ An value: 15,700 <br> 4,553. Probably Lua Mua is 4553? Or 15700? Assume 15700? 
        # Total NTB 133k. Thanh Hoa 113k. So Nghe An small. 
        # Wait, PL2a row 49: "15,700 <br> 4,553". If total is 133966, Thanh Hoa is 113713. 
        # 133966 - 113713 = 20253.
        # Nghe An + Ha Tinh + ... = 20253.
        # Ha Tinh 18176? Wait. 113713 + 18176 = 131889.
        # So Nghe An must be small. 4553 seems safer. Let's use 4553.
        # Actually in June Nghe An was 87k (Lua DX). July is Mua. Should be small.
        ["Hà Tĩnh", 18176, 8300, 7126, None, 2750, None], # Adjusted columns based on row 50: |Hà Tĩnh|18,176|8,300|7,126||2,750|
        # Wait, row 50 is tricky. |Hà Tĩnh|18,176|8,300|7,126||2,750| -> 7126 is Ngo?
        # Header: Gieo cấy | DT màu | Ngo | Khoai | San | Cây khác
        # Hà Tĩnh: 18176 (Gieo cấy), 8300 (Mau), 7126 (Ngo?), Blank (Khoai), 2750 (San?).
        # Let's verify sum: 7126 + 2750 = 9876 > 8300. So 2750 is probably San?
        # Actually row 50 aligns as: |Hà Tĩnh|18,176|8,300|7,126||2,750|
        # This implies: Lua=18176, Mau=8300, Ngo=7126, Khoai=Missing, San=2750.
        ["Quảng Bình", None, 14818, 5500, 1586, 5782, 1950], # Lua missing in table
        ["Quảng Trị", None, 14435, 3505, 630, 8300, 2000],
        ["Thừa Thiên Huế", None, 10300, 1800, 3000, 5050, 450]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            try:
                if idx+3 < len(row):
                    v = normalize_number(row[idx+3])
                    if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
    return records

def parse_pl2b():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL2b", "source_file": "2010_07_phuluc_07_2010_PL2b.md"}
    records = []
    t = {"year": 2010, "month": 7, "period_type": "Monthly", "report_date": "2010-07-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Mia, ThuocLa, CayKhac, RauDau]
    data = [
        ["Miền Bắc", 348553, 132034, 132272, 27075, 13193, 21600, 338462],
        ["ĐB sông Hồng", 146675, 86601, 22705, 630, 2747, 11613, 158244],
        ["Hà Nội", 38630, 33430, 5000, 200, None, None, 22758],
        ["Hải Phòng", 2849, 375, None, None, 2347, 127, 24498],
        ["Vĩnh Phúc", 10642, 6526, 3430, 24, None, 662, 9528],
        ["Bắc Ninh", 4941, 3590, 1060, None, None, 292, 6774],
        ["Hải Dương", 3050, 1450, 1300, None, None, 300, 26415],
        ["Hưng Yên", 3853, 2758, 873, None, None, 222, 19055],
        ["Hà Nam", 34836, 12059, 398, None, None, 0, 5359],
        ["Nam Định", 10907, 2226, 3988, None, None, 4693, 10198],
        ["Thái Bình", 20414, 13779, 1500, None, 400, 4735, 16473],
        ["Ninh Bình", 12679, 9910, 2769, None, None, None, 8323],
        ["Quảng Ninh", 3873, 498, 2387, 406, None, 582, 8863],
        ["Trung du và MN phía Bắc", 103457, 37376, 39619, 10490, 10296, 5676, 89729],
        ["Hà Giang", 11714, 6617, 4887, None, None, 210, 10943],
        ["Cao Bằng", 10732, 5246, 711, 1238, 3303, 234, 1738],
        ["Lào Cai", 2994, 1962, 448, None, 448, 136, 4124],
        ["Bắc Cạn", 2130, 461, 310, 70, 1444, -155, 1599],
        ["Lạng Sơn", 10561, 1600, 1500, 200, 5016, 2245, 1290],
        ["Tuyên Quang", 6985, 2310, 4675, None, None, 0, 6320],
        ["Yên Bái", 4071, 1622, 1434, 630, None, 385, 5657],
        ["Thái Nguyên", 5384, 1417, 3967, None, None, 0, 8929],
        ["Phú Thọ", 7586, 3045, 4541, None, None, 0, 5917],
        ["Bắc Giang", 11900, 1208, 10198, None, 85, 409, 25955],
        ["Lai Châu", 2400, 1105, 1026, None, None, 269, 735],
        ["Điện Biên", 4609, 3147, 912, None, None, 550, 950],
        ["Sơn La", 7369, 5215, 471, 291, None, 1392, 4574],
        ["Hoà Bình", 15021, 2421, 4539, 8061, None, 0, 10998],
        ["Bắc Trung Bộ", 98421, 8057, 69948, 15955, 150, 4311, 90490],
        ["Thanh Hoá", 34836, 7480, 14402, 10569, None, 2385, 46213],
        ["Nghệ An", 27327, 577, 21434, 5236, 80, None, 20492],
        ["Hà Tĩnh", 22064, None, 20552, None, None, 1512, 12279],
        ["Quảng Bình", 4863, None, 4863, None, None, None, 586],
        ["Quảng Trị", 5357, None, 5100, None, None, 257, 5682],
        ["Thừa Thiên Huế", 3974, None, 3597, 150, 70, 157, 5238]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", None), ("Thuốc lá", None), ("Cây công nghiệp khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            
        v = normalize_number(row[7])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl3a():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL3a", "source_file": "2010_07_phuluc_07_2010_PL3a.md"}
    records = []
    t = {"year": 2010, "month": 7, "period_type": "Monthly", "report_date": "2010-07-15"}
    
    # [Loc, HT_Planted, HT_Harvested, HT_Yield_Perc, Mua_Planted, Mau_Total, Ngo, Khoai, San]
    data = [
        ["Miền Nam", 1925179, 724652, 37.6, 265128, 499379, 260873, 19928, 218578],
        ["D.H Nam Trung Bộ", 150621, None, None, 8200, 84014, 25784, 6952, 51278],
        ["TP Đà Nẵng", 3300, None, None, None, 846, 578, 268, None],
        ["Quảng Nam", 37100, None, None, None, 20920, 6500, 4500, 9920],
        ["Quảng Ngãi", 32256, None, None, None, 17160, 4160, 1900, 11100],
        ["Bình Định", 41485, None, None, 8200, 19600, 6711, None, 12889],
        ["Phú Yên", 23600, None, None, None, 17423, 4879, 175, 12369],
        ["Khánh Hoà", 12880, None, None, None, 8065, 2956, 109, 5000],
        ["Tây Nguyên", 6489, None, None, 105580, 209163, 145948, 6256, 56959],
        ["Kon Tum", None, None, None, 11294, 7388, 7388, None, None],
        ["Gia Lai", None, None, None, 26074, 53629, 30177, 418, 23034],
        ["Đắc Lắc", None, None, None, 63642, 92098, 72315, 1274, 18509],
        ["Đắc Nông", None, None, None, None, 42966, 23970, 3580, 15416],
        ["Lâm Đồng", 6489, None, None, 4570, 13082, 12098, 984, None],
        ["Đông Nam Bộ", 139287, None, None, 2162, 168722, 59541, 808, 108373],
        ["TP Hồ Chí Minh", 5214, None, None, 297, 862, 862, None, None],
        ["Ninh Thuận", 10640, None, None, None, 4698, 4594, 104, None],
        ["Bình Phước", None, None, None, None, 24175, 526, 149, 23500],
        ["Tây Ninh", 63642, None, None, 1865, 36553, 5596, None, 30957],
        ["Bình Dương", 2069, None, None, None, 2664, 177, 171, 2316],
        ["Đồng Nai", 25452, None, None, None, 40598, 25098, None, 15500],
        ["Bình Thuận", 28518, None, None, None, 39560, 11121, 339, 28100],
        ["Bà Rịa-V.Tàu", 3752, None, None, None, 19612, 11567, 45, 8000],
        ["ĐBS Cửu Long", 1628782, 724652, 44.5, 149186, 37480, 29600, 5912, 1968],
        ["Long An", 206144, 65784, 31.9, None, 4995, 4995, None, None],
        ["Đồng Tháp", 197078, 162505, 82.5, 52624, 3463, 2710, 753, None],
        ["An Giang", 232488, 120028, 51.6, 2400, 6307, 6187, 30, 90],
        ["Tiền Giang", 120230, 39742, 33.1, None, 3885, 3376, 250, 259],
        ["Vĩnh Long", 62751, 46670, 74.4, 22225, 6730, 3947, 2671, 112],
        ["Bến Tre", 21341, None, None, None, 563, 406, 50, 107],
        ["Kiên Giang", 274559, 74645, 27.2, 9737, None, None, None, None],
        ["Cần Thơ", 84767, 71895, 84.8, 32294, 563, 563, None, None],
        ["Hậu Giang", 79744, 52357, 65.7, 27206, 1655, 1655, None, None],
        ["Trà Vinh", 81356, 15345, 18.9, None, 5913, 3881, 880, 1152],
        ["Sóc Trăng", 183303, 69901, 38.1, None, 3406, 1880, 1278, 248],
        ["Bạc Liêu", 55851, 5780, 10.3, 2700, None, None, None, None],
        ["Cà Mau", 29170, None, None, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa/Thu Đông"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[5])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+6])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl3b():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL3b", "source_file": "2010_07_phuluc_07_2010_PL3b.md"}
    records = []
    t = {"year": 2010, "month": 7, "period_type": "Monthly", "report_date": "2010-07-15"}
    
    data = [
        ["Miền Nam", 244197, 23555, 63968, 24518, 13199, 114089, 1006, 3862, 221862, 42951],
        ["D.H Nam Trg Bộ", 69145, 1574, 22388, 6000, 902, 37806, 434, 41, 27863, 27863],
        ["TP Đà Nẵng", 1195, None, 618, 211, None, 366, None, None, 659, 78],
        ["Quảng Nam", 11032, None, 8264, 1800, 502, 289, 177, None, 8500, 3400],
        ["Quảng Ngãi", 10365, 375, 3796, None, None, 6194, None, None, 5849, 1475],
        ["Bình Định", 13551, 881, 8893, 1576, None, 2201, None, None, 8159, 1039],
        ["Phú Yên", 16823, 318, 672, 2413, 400, 12722, 257, 41, 2456, 1687],
        ["Khánh Hoà", 16179, None, 145, None, None, 16034, None, None, 2240, 733],
        ["Tây Nguyên", 43145, 13728, 7378, 3093, 6539, 12407, 0, 0, 34630, 16475],
        ["Kon Tum", 4022, None, 58, None, 1867, 2097, None, None, 8700, 92],
        ["Gia Lai", 14706, None, 211, 2566, 4622, 7307, None, None, 8108, 3488],
        ["Đắc Lắc", 9257, 4578, 2374, 527, 50, 1728, None, None, 2705, 7209],
        ["Đắc Nông", 13960, 9150, 4735, None, None, 75, None, None, 1398, 5271],
        ["Lâm Đồng", 1200, None, None, None, None, 1200, None, None, 13719, 415],
        ["Đông Nam Bộ", 50200, 671, 21845, 5280, 5596, 16236, 572, 0, 50112, 13449],
        ["TP Hồ Chí Minh", 2690, None, 900, None, None, 1790, None, None, 8092, None],
        ["Ninh Thuận", 1613, None, 135, 461, 32, 413, 572, None, 8820, 2097],
        ["Bình Phước", 140, None, 130, 10, None, None, None, None, 816, None],
        ["Tây Ninh", 26212, None, 12017, 1473, 4632, 8090, None, None, 13242, 4967],
        ["Bình Dương", 934, None, 635, None, None, 299, None, None, 2871, 199],
        ["Đồng Nai", 10297, 419, 4100, 20, 800, 4958, None, None, 9728, 3942],
        ["Bình Thuận", 7617, 241, 3487, 3316, 31, 542, None, None, 2118, 1763],
        ["Bà Rịa-V.Tàu", 697, 11, 441, None, 101, 144, None, None, 4425, 481],
        ["ĐBS Cửu Long", 81707, 7582, 12357, 10145, 162, 47640, 0, 3821, 109257, 4615],
        ["Long An", 21859, None, 4937, 1275, 122, 12881, None, 2644, 13036, None],
        ["Đồng Tháp", 8994, 4928, 81, 3761, 15, 124, None, 85, 8550, None],
        ["An Giang", 1352, 322, 175, 836, 1, 18, None, None, 7396, 1181],
        ["Tiền Giang", 218, None, None, None, None, 218, None, None, 26785, None],
        ["Vĩnh Long", 1941, 1101, 29, 205, None, 62, None, 544, 9595, 240],
        ["Bến Tre", 6190, None, 132, None, None, 5865, None, 193, 2544, 3],
        ["Kiên Giang", 0, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 8395, 745, 3558, 4068, 24, None, None, None, 4103, 583],
        ["Hậu Giang", 13118, None, None, None, None, 13118, None, None, 7756, 77],
        ["Trà Vinh", 8782, 224, 3445, None, None, 4758, None, 355, 14649, 765],
        ["Sóc Trăng", 10727, 131, None, None, None, 10596, None, None, 14843, 1766],
        ["Bạc Liêu", 131, 131, None, None, None, None, None, None, None, None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[9])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[10]) 
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl1()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl2a()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL2a.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl2b()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL2b.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl3a()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL3a.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl3b()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL3b.json"))
    print("Successfully parsed PL1, PL2a, PL2b, PL3a, PL3b for July 2010.")
