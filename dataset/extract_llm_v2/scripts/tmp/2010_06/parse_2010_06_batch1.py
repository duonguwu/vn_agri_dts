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
        "Miền Trung - Tây Nguyên": "Miền Trung"
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
    elif norm_loc == "Miền Trung":
        geo_context["region_id"] = "CENTRAL"; geo_context["region_name_vn"] = "Miền Trung"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl1():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL1", "source_file": "2010_06_Phuluc_06_2010_PL1.md"}
    records = []
    t10 = {"year": 2010, "month": 6, "period_type": "Monthly", "report_date": "2010-06-15"}
    t09 = {"year": 2009, "month": 6, "period_type": "Monthly", "report_date": "2009-06-15"}
    
    # [Item, Loc, Unit, V09, V10]
    data = [
        ["Thu hoạch lúa đông xuân miền Bắc", "Miền Bắc", "1000 ha", 969.4, 1100.8],
        ["Đồng bằng sông Hồng", "Đồng bằng sông Hồng", "1000 ha", 542.7, 551.5],
        ["Bắc Trung bộ", "Bắc Trung Bộ", "1000 ha", 336.1, 341.0],
        
        ["Gieo cấy lúa hè thu cả nước", "Cả nước", "1000 ha", 2016.8, 1833.3],
        ["Miền Bắc", "Miền Bắc", "1000 ha", 129.6, 121.3],
        ["Miền Nam", "Miền Nam", "1000 ha", 1887.2, 1712.0],
        ["Đồng bằng sông Cửu Long", "Đồng bằng sông Cửu Long", "1000 ha", 1581.2, 1407.2],
        
        ["Gieo trồng màu lương thực", "Cả nước", "1000 ha", 1222.8, 1230.9],
        ["Ngô", "Cả nước", "1000 ha", 779.9, 782.4],
        ["Khoai lang", "Cả nước", "1000 ha", 112.9, 106.0],
        ["Sắn", "Cả nước", "1000 ha", 306.2, 306.9],
        
        ["Gieo trồng cây công nghiệp ngắn ngày", "Cả nước", "1000 ha", 563.2, 527.5],
        ["Lạc", "Cả nước", "1000 ha", 204.5, 189.5],
        ["Đậu tương", "Cả nước", "1000 ha", 137.9, 143.4],
        ["Thuốc lá", "Cả nước", "1000 ha", 25.5, 26.4],
        ["Mía (trồng mới)", "Cả nước", "1000 ha", 150.7, 133.8],
        
        ["Gieo trồng rau, đậu các loại", "Cả nước", "1000 ha", 533.6, 574.0],
    ]
    
    for row in data:
        item_name, loc, unit, v09, v10 = row
        
        # Determine Context
        if "Thu hoạch lúa" in item_name:
            cmd = "Lúa"; sub = "Đông Xuân"; attr = "Area_Harvested"
            if item_name == "Đồng bằng sông Hồng" or item_name == "Bắc Trung bộ": pass # Inherit
            else: pass
        elif "Gieo cấy lúa hè thu" in item_name:
            cmd = "Lúa"; sub = "Hè Thu"; attr = "Area_Planted"
            if item_name == "Miền Bắc": sub = "Hè Thu/Mùa" # Usually North has Mua
        elif "màu lương thực" in item_name:
             cmd = "Màu lương thực"; sub = "Tổng số"; attr = "Area_Planted"
        elif "cây công nghiệp" in item_name:
             cmd = "Cây công nghiệp ngắn ngày"; sub = "Tổng số"; attr = "Area_Planted"
        elif "rau, đậu" in item_name:
             cmd = "Rau đậu các loại"; sub = "Tổng số"; attr = "Area_Planted"
        elif item_name in ["Ngô", "Khoai lang", "Sắn", "Lạc", "Đậu tương", "Thuốc lá"]:
             cmd = item_name; sub = None; attr = "Area_Planted"
        elif "Mía" in item_name:
             cmd = "Mía"; sub = "Trồng mới"; attr = "Area_Planted"
        else:
             # Fallback for sub-items
             if loc == "Đồng bằng sông Hồng" or loc == "Bắc Trung bộ": # Inherit from Thu hoach lua dong xuan
                 cmd = "Lúa"; sub = "Đông Xuân"; attr = "Area_Harvested"
             elif loc == "Miền Bắc" or loc == "Miền Nam" or loc == "Đồng bằng sông Cửu Long": # Inherit from Gieo cay lua he thu
                 cmd = "Lúa"; sub = "Hè Thu"; attr = "Area_Planted"
             else:
                 cmd = item_name; sub = None; attr = "Area_Planted"

        gl = "National" if loc in ["Cả nước", "Miền Bắc", "Miền Nam"] else "Regional"
        
        if v10: records.append(create_record(metadata, t10, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))
        if v09: records.append(create_record(metadata, t09, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v09), "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2a():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL2a", "source_file": "2010_06_Phuluc_06_2010_PL2a.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Monthly", "report_date": "2010-06-15"}
    
    # [Loc, DX_Planted, DX_Harvested, HT_Planted, Mau_Total, Ngo, Khoai, San, Khac]
    data = [
        ["Miền Bắc", 1144655, 1100804, 143926, 807113, 555002, 86037, 130400, 35674],
        ["ĐB sông Hồng", 568363, 551510, 5283, 126672, 82745, 21878, 4398, 17651],
        ["Hà Nội", 101787, 100000, None, 29455, 20784, 7171, 1300, 200],
        ["Hải Phòng", 39204, 39204, None, 4610, 2110, 0, None, 2500],
        ["Vĩnh Phúc", 30857, 30857, 3233, 22997, 16515, 2625, 1722, 2135],
        ["Bắc Ninh", 37008, 32700, None, 3861, 2567, 710, None, 584],
        ["Hải Dương", 64133, 63582, 1000, 11083, 4351, 1441, None, 5291],
        ["Hưng Yên", 40383, 37080, None, 8628, 7973, 655, None, None],
        ["Hà Nam", 34765, 34765, None, 7324, 6925, 399, None, None],
        ["Nam Định", 78096, 78096, None, 9079, 3409, 870, 300, 4500],
        ["Thái Bình", 82678, 82678, None, 13368, 8530, 2893, None, 1945],
        ["Ninh Bình", 41603, 40621, 1050, 6649, 4484, 2165, None, None],
        ["Quảng Ninh", 17849, 11927, None, 9619, 5097, 2950, 1076, 496],
        ["TD và MN phía Bắc", 234329, 208252, 17329, 479125, 359047, 28907, 81507, 9663],
        ["Hà Giang", 9256, 9000, None, 44871, 38341, 649, 3761, 2119],
        ["Cao Bằng", 2882, 2882, 4180, 21752, 20886, 671, None, 195],
        ["Lào Cai", 9102, 2297, 6915, 26348, 20901, 558, 4889, None],
        ["Bắc Cạn", 7399, 7399, 30, 12416, 10711, 314, 1144, 247],
        ["Lạng Sơn", 14497, 10000, None, 15073, 13100, 0, None, 1973],
        ["Tuyên Quang", 19492, 18698, 41, 16107, 12056, 4051, None, None],
        ["Yên Bái", 17422, 17000, 1550, 28708, 14415, 1753, 12023, 517],
        ["Thái Nguyên", 28263, 28263, None, 23232, 13709, 5814, 3709, None],
        ["Phú Thọ", 35534, 35000, None, 27105, 17139, 2571, 7194, 202],
        ["Bắc Giang", 51686, 50000, None, 19719, 10115, 7404, 2200, None],
        ["Lai Châu", 5443, 3900, None, 22630, 17473, 0, 5157, None],
        ["Điện Biên", 7862, 6449, 4613, 35286, 28130, 20, 7136, None],
        ["Sơn La", 9491, 1416, None, 141524, 115249, 95, 23285, 2895],
        ["Hoà Bình", 16000, 15948, None, 44355, 26823, 5008, 11009, 1515],
        ["Bắc Trung Bộ", 341963, 341042, 121314, 201316, 113210, 35252, 44495, 8359],
        ["Thanh Hoá", 121343, 120422, None, 72344, 49312, 13123, 9200, 709],
        ["Nghệ An", 87482, 87482, 30000, 72536, 45786, 9787, 16463, 500],
        ["Hà Tĩnh", 53569, 53569, 35000, 17183, 7307, 7126, None, 2750],
        ["Quảng Bình", 28334, 28334, 15000, 14818, 5500, 1586, 5782, 1950],
        ["Quảng Trị", 24083, 24083, 21314, 14135, 3505, 630, 8000, 2000],
        ["Thừa Thiên Huế", 27152, 27152, 20000, 10300, 1800, 3000, 5050, 450],
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        # Lua
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"})) # File unit is Ha
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu/Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        # Mau
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+5])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl2b():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL2b", "source_file": "2010_06_Phuluc_06_2010_PL2b.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Monthly", "report_date": "2010-06-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Mia, ThuocLa, CayKhac_CCN, RauDau]
    data = [
        ["Miền Bắc", 293508, 120240, 126099, 26839, 13187, 7142, 309549],
        ["ĐB sông Hồng", 107675, 81968, 21234, 630, 2747, 1097, 149297],
        ["Hà Nội", 38630, 33430, 5000, 200, 0, 0, 22758],
        ["Hải Phòng", 2849, 375, 0, 0, 2347, 127, 24498],
        ["Vĩnh Phúc", 8862, 5368, 3209, 24, 0, 261, 8293],
        ["Bắc Ninh", 3981, 2733, 957, 0, 0, 292, 6157],
        ["Hải Dương", 2250, 1050, 1200, 0, 0, 0, 26415],
        ["Hưng Yên", 3794, 2758, 814, 0, 0, 222, 16321],
        ["Hà Nam", 11775, 11377, 398, 0, 0, 0, 4333],
        ["Nam Định", 4376, 1376, 3000, 0, 0, 0, 10198],
        ["Thái Bình", 15679, 13779, 1500, 0, 400, 0, 14813],
        ["Ninh Bình", 11993, 9224, 2769, 0, 0, 0, 8323],
        ["Quảng Ninh", 3486, 498, 2387, 406, 0, 195, 7188],
        ["Trung du và MN phía Bắc", 95893, 32652, 37108, 10490, 10290, 5353, 86142],
        ["Hà Giang", 11409, 6518, 4682, 0, 0, 210, 10943],
        ["Cao Bằng", 10732, 5246, 711, 1238, 3303, 234, 1738],
        ["Lào Cai", 2821, 1931, 448, 0, 442, 0, 4124],
        ["Bắc Cạn", 2130, 461, 310, 70, 1444, -155, 1599], # What? -155? Maybe typo? I'll extract it as is.
        ["Lạng Sơn", 10561, 1600, 1500, 200, 5016, 2245, 1290],
        ["Tuyên Quang", 5834, 1781, 4053, 0, 0, 0, 6320],
        ["Yên Bái", 4071, 1622, 1434, 630, 0, 385, 5657],
        ["Thái Nguyên", 4868, 1175, 3693, 0, 0, 0, 8299],
        ["Phú Thọ", 6578, 2037, 4541, 0, 0, 0, 5917],
        ["Bắc Giang", 11173, 768, 10098, 0, 85, 222, 25089],
        ["Lai Châu", 2824, 1638, 917, 0, 0, 269, 358],
        ["Điện Biên", 4609, 3147, 912, 0, 0, 550, 950],
        ["Sơn La", 5481, 3428, 370, 291, 0, 1392, 3860],
        ["Hoà Bình", 12801, 1301, 3439, 8061, 0, 0, 9998],
        ["Bắc Trung Bộ", 89939, 5620, 67757, 15719, 150, 693, 74110],
        ["Thanh Hoá", 30414, 5443, 14402, 10569, 0, 0, 29833],
        ["Nghệ An", 25391, 177, 20134, 5000, 80, 0, 20492],
        ["Hà Tĩnh", 20240, 0, 19961, 0, 0, 279, 12279],
        ["Quảng Bình", 4863, 0, 4863, 0, 0, 0, 586],
        ["Quảng Trị", 5057, 0, 4800, 0, 0, 257, 5682],
        ["Thừa Thiên Huế", 3974, 0, 3597, 150, 70, 157, 5238],
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
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

def parse_pl3a():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL3a", "source_file": "2010_06_Phuluc_06_2010_PL3a.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Monthly", "report_date": "2010-06-15"}
    
    # [Loc, DX_Planted, DX_Harvested, HT_Planted, Mau_Total, Ngo, Khoai, San]
    data = [
        ["Miền Nam", 1933734, 1921316, 1711959, 423814, 227378, 19928, 176508],
        ["D.H Nam Trung Bộ", 176256, 174156, 151005, 83589, 29103, 6952, 47534],
        ["TP Đà Nẵng", 4000, 4000, 3294, 707, 439, 268, None],
        ["Quảng Nam", 42257, 42257, 37100, 24940, 10520, 4500, 9920],
        ["Quảng Ngãi", 36973, 36973, 32746, 17427, 4427, 1900, 11100],
        ["Bình Định", 47421, 47421, 41485, 16233, 6711, None, 9522],
        ["Phú Yên", 26100, 24000, 23500, 16217, 4050, 175, 11992],
        ["Khánh Hoà", 19505, 19505, 12880, 8065, 2956, 109, 5000],
        ["Tây Nguyên", 74897, 67257, 37276, 179882, 120160, 6256, 53466],
        ["Kon Tum", 6583, 6583, None, 653, 653, None, None],
        ["Gia Lai", 23998, 17400, 9107, 45676, 22224, 418, 23034],
        ["Đắc Lắc", 29755, 29755, 17189, 77505, 61215, 1274, 15016],
        ["Đắc Nông", 3853, 2811, 4970, 42966, 23970, 3580, 15416],
        ["Lâm Đồng", 10708, 10708, 6010, 13082, 12098, 984, None],
        ["Đông Nam Bộ", 120944, 120293, 116462, 126763, 52415, 808, 73540],
        ["TP Hồ Chí Minh", 6637, 6637, 5214, 833, 833, None, None],
        ["Ninh Thuận", 13104, 13104, 8720, 6828, 6724, 104, None],
        ["Bình Phước", 2897, 2897, None, 13566, 526, 149, 12891],
        ["Tây Ninh", 45898, 45247, 48277, 35660, 4703, None, 30957],
        ["Bình Dương", 2653, 2653, 655, 2664, 177, 171, 2316],
        ["Đồng Nai", 14565, 14565, 21326, 28927, 20821, None, 8106],
        ["Bình Thuận", 29936, 29936, 28518, 18790, 7064, 339, 11387],
        ["Bà Rịa-V.Tàu", 5254, 5254, 3752, 19495, 11567, 45, 7883],
        ["ĐBS Cửu Long", 1561637, 1559610, 1407216, 33580, 25700, 5912, 1968],
        ["Long An", 251025, 251025, 190457, 4995, 4995, None, None],
        ["Đồng Tháp", 207672, 207672, 197093, 3463, 2710, 753, None],
        ["An Giang", 234212, 232185, 228051, 6307, 6187, 30, 90],
        ["Tiền Giang", 82272, 82272, 77818, 3885, 3376, 250, 259],
        ["Vĩnh Long", 66902, 66902, 62750, 3447, 664, 2671, 112],
        ["Bến Tre", 21036, 21036, 19166, 563, 406, 50, 107],
        ["Kiên Giang", 284145, 284145, 212430, None, None, None, None],
        ["Cần Thơ", 89673, 89673, 84767, 563, 563, None, None],
        ["Hậu Giang", 84505, 84505, 78060, 1655, 1655, None, None],
        ["Trà Vinh", 55916, 55916, 79258, 5296, 3264, 880, 1152],
        ["Sóc Trăng", 139648, 139648, 92447, 3406, 1880, 1278, 248],
        ["Bạc Liêu", 44631, 44631, 55749, None, None, None, None],
        ["Cà Mau", None, None, 29170, None, None, None, None],
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        # Mau
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+5])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl1()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl2a()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL2a.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl2b()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL2b.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl3a()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL3a.json"))
    print("Successfully parsed PL1, PL2a, PL2b, PL3a for June 2010.")
