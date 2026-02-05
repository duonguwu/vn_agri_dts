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
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh"
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
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL1", "source_file": "2010_08_Phuluc_T08_2010_PL1.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Monthly", "report_date": "2010-08-15"}
    
    # [Item, V09, V10]
    data = [
        ["Thu hoạch lúa hè thu miền Nam", 1223.8, 1193.0],
        ["Đồng bằng sông Cửu Long", 1117.0, 1102.9],
        ["Gieo cấy lúa mùa cả nước", 1464.2, 1406.9],
        ["Miền Bắc", 1170.6, 1171.9],
        ["Miền Nam", 263.7, 245.0],
        ["Gieo trồng màu lương thực", 1428.0, 1509.9],
        ["Ngô", 865.0, 923.5],
        ["Khoai lang", 117.3, 122.0],
        ["Sắn", 411.9, 426.5],
        ["Gieo trồng cây công nghiệp ngắn ngày", 622.5, 622.2],
        ["Lạc", 226.0, 209.7],
        ["Đậu tương", 167.8, 178.7],
        ["Thuốc lá", 20.5, 26.4],
        ["Gieo trồng rau, đậu các loại", 614.4, 626.3]
    ]
    
    for row in data:
        item_name, v09, v10 = row
        loc = "Cả nước"
        if "miền Nam" in item_name: loc = "Miền Nam"
        if "Miền Bắc" in item_name: loc = "Miền Bắc"
        if "Đồng bằng sông Cửu Long" in item_name: loc = "Đồng bằng sông Cửu Long"
        
        # Determine Context
        if "Thu hoạch lúa" in item_name or item_name == "Đồng bằng sông Cửu Long":
            cmd = "Lúa"; sub = "Hè Thu"; attr = "Area_Harvested"
        elif "Gieo cấy lúa mùa" in item_name or item_name in ["Miền Bắc", "Miền Nam"]:
            cmd = "Lúa"; sub = "Mùa"; attr = "Area_Planted"
        elif "màu lương thực" in item_name: cmd = "Màu lương thực"; sub = "Tổng số"; attr = "Area_Planted"
        elif "cây công nghiệp" in item_name: cmd = "Cây công nghiệp ngắn ngày"; sub = "Tổng số"; attr = "Area_Planted"
        elif "rau, đậu" in item_name: cmd = "Rau đậu các loại"; sub = "Tổng số"; attr = "Area_Planted"
        elif item_name in ["Ngô", "Khoai lang", "Sắn", "Lạc", "Đậu tương", "Thuốc lá"]:
             cmd = item_name; sub = None; attr = "Area_Planted"
        else: cmd = item_name; sub = None; attr = "Area_Planted"

        gl = "National" if loc in ["Cả nước", "Miền Bắc", "Miền Nam"] else "Regional"
        
        if v10: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL2", "source_file": "2010_08_Phuluc_T08_2010_PL2.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Monthly", "report_date": "2010-08-15"}
    
    # [Loc, LuaMua_Total, Luanuong, HeThu, Mau_Total, Ngo, Khoai, San, Khac]
    # Note: PL2 col 4 is "Lúa hè thu" (value 160643 for North, 0 for R1/R2, only Bac Trung Bo 160643).
    data = [
        ["Miền Bắc", 1171880, 48887, 160643, 915341, 642199, 100629, 134495, 38017], # Total row fixed
        ["ĐB sông Hồng", 578578, 0, 0, 138298, 91941, 24307, 4398, 17651],
        ["Hà Nội", 101767, None, None, 33367, 24135, 7732, 1300, 200],
        ["Hải Phòng", 41657, None, None, 5110, 2310, 300, None, 2500],
        ["Vĩnh Phúc", 28687, None, None, 24620, 17975, 2788, 1722, 2135],
        ["Bắc Ninh", 36888, None, None, 3861, 2567, 710, None, 584],
        ["Hải Dương", 63014, None, None, 11083, 4351, 1441, None, 5291],
        ["Hưng Yên", 40458, None, None, 9568, 8913, 655, None, None],
        ["Hà Nam", 35519, None, None, 9046, 8647, 399, None, None],
        ["Nam Định", 80520, None, None, 9079, 3409, 870, 300, 4500],
        ["Thái Bình", 83180, None, None, 13368, 8530, 2893, None, 1945],
        ["Ninh Bình", 39496, None, None, 6875, 4710, 2165, None, None],
        ["Quảng Ninh", 27392, None, None, 12320, 6394, 4354, 1076, 496],
        ["TD và MN phía Bắc", 409018, 47287, 0, 543035, 416213, 33152, 81663, 12007],
        ["Hà Giang", 25986, None, None, 50669, 42182, 649, 3761, 4077],
        ["Cao Bằng", 25725, 2071, None, 32342, 31476, 671, None, 195],
        ["Lào Cai", 18699, 268, None, 29921, 24331, 307, 4897, 386],
        ["Bắc Cạn", 12920, None, None, 16020, 14261, 368, 1144, 247],
        ["Lạng Sơn", 29565, None, None, 18940, 16967, None, None, 1973],
        ["Tuyên Quang", 25555, None, None, 17733, 13682, 4051, None, None],
        ["Yên Bái", 23778, 3980, None, 36542, 21502, 2500, 12023, 517],
        ["Thái Nguyên", 41006, None, None, 28590, 17772, 7109, 3709, None],
        ["Phú Thọ", 33428, None, None, 32951, 22647, 2908, 7194, 202],
        ["Bắc Giang", 58055, None, None, 22391, 12420, 7771, 2200, None],
        ["Lai Châu", 24789, 6181, None, 22641, 17336, None, 5305, None],
        ["Điện Biên", 38635, 22787, None, 36286, 29130, 20, 7136, None],
        ["Sơn La", 27000, 12000, None, 142887, 116449, 258, 23285, 2895],
        ["Hoà Bình", 23877, None, None, 55122, 36058, 6540, 11009, 1515],
        ["Bắc Trung Bộ", 184284, 1600, 160643, 234008, 134045, 43170, 48434, 8359],
        ["Thanh Hoá", 133759, None, None, 83186, 59099, 14178, 9200, 709],
        ["Nghệ An", 44000, None, 58000, 84236, 56286, 10987, 16463, 500],
        ["Hà Tĩnh", 4325, None, 40825, 26562, 9383, 10990, 3439, 2750],
        ["Quảng Bình", None, None, 15370, 13480, 4162, 1586, 5782, 1950],
        ["Quảng Trị", 1600, 1600, 21314, 16434, 3505, 2429, 8500, 2000],
        ["Thừa Thiên Huế", 600, None, 25134, 10110, 1610, 3000, 5050, 450]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Lúa nương"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            try:
                if idx+5 < len(row):
                    v = normalize_number(row[idx+5])
                    if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
            
    return records

def parse_pl3():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL3", "source_file": "2010_08_Phuluc_T08_2010_PL3.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Monthly", "report_date": "2010-08-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Mia, ThuocLa, CayKhac, RauDau]
    # Note: PL3 cols: Total, DauTuong, Lac, Mia, ThuocLa, OtherCCN, RauDau
    data = [
        ["Miền Bắc", 358003, 154975, 138452, 27102, 13193, 24280, 358269],
        ["ĐB sông Hồng", 130442, 89966, 24167, 657, 2747, 12904, 170190],
        ["Hà Nội", 42556, 36043, 5606, 200, None, 707, 28913],
        ["Hải Phòng", 3037, 390, None, None, 2347, 300, 27699],
        ["Vĩnh Phúc", 10508, 6192, 3592, 51, None, 673, 9406],
        ["Bắc Ninh", 5074, 3590, 1169, None, None, 315, 7896],
        ["Hải Dương", 3260, 1450, 1300, None, None, 510, 26415],
        ["Hưng Yên", 3912, 2758, 932, None, None, 222, 19395],
        ["Hà Nam", 13139, 12741, 398, None, None, None, 6385],
        ["Nam Định", 10907, 2226, 3988, None, None, 4693, 10198],
        ["Thái Bình", 20414, 13779, 1500, None, 400, 4735, 16473],
        ["Ninh Bình", 12679, 9910, 2769, None, None, None, 8323],
        ["Quảng Ninh", 4955, 887, 2913, 406, None, 749, 9087],
        ["Trung du và MN phía Bắc", 129379, 58393, 43799, 10490, 10296, 6401, 94772],
        ["Hà Giang", 23369, 17362, 5797, None, None, 210, 10943],
        ["Cao Bằng", 10732, 5246, 711, 1238, 3303, 234, 1738],
        ["Lào Cai", 3135, 1962, 589, None, 448, 136, 4124],
        ["Bắc Cạn", 4728, 2737, 322, 70, 1444, 155, 1611],
        ["Lạng Sơn", 10561, 1600, 1500, 200, 5016, 2245, 1290],
        ["Tuyên Quang", 7828, 2970, 4858, None, None, 0, 6320],
        ["Yên Bái", 6796, 3676, 2104, 630, None, 385, 7650],
        ["Thái Nguyên", 6179, 1769, 4410, None, None, 0, 10154],
        ["Phú Thọ", 8501, 3045, 5364, None, None, 92, 5917],
        ["Bắc Giang", 13391, 1807, 10766, None, 85, 733, 25955],
        ["Lai Châu", 3163, 1569, 1325, None, None, 269, 735],
        ["Điện Biên", 7609, 5647, 1412, None, None, 550, 950],
        ["Sơn La", 9098, 6757, 658, 291, None, 1392, 5460],
        ["Hoà Bình", 14290, 2246, 3983, 8061, None, 0, 11925],
        ["Bắc Trung Bộ", 98182, 6616, 70486, 15955, 150, 4975, 93307],
        ["Thanh Hoá", 34878, 6039, 15221, 10569, None, 3049, 46213],
        ["Nghệ An", 27327, 577, 21434, 5236, 80, None, 20492],
        ["Hà Tĩnh", 22064, None, 20552, None, None, 1512, 15096],
        ["Quảng Bình", 5124, None, 5124, None, None, None, 586],
        ["Quảng Trị", 4815, None, 4558, None, None, 257, 5682],
        ["Thừa Thiên Huế", 3974, None, 3597, 150, 70, 157, 5238]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", None), ("Thuốc lá", None), ("Cây công nghiệp khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            if idx+2 < len(row):
                v = normalize_number(row[idx+2])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        if len(row) > 7:
            v = normalize_number(row[7])
            if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            
    return records

def parse_pl4():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL4", "source_file": "2010_08_Phuluc_T08_2010_PL4.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Monthly", "report_date": "2010-08-15"}
    
    # [Loc, HT_Planted, HT_Harvested, TD_Planted, Mua_Planted, Mau_Total, Ngo, Khoai, San]
    # Note from file: Col 2: HT_Planted, Col 3: HT_Harvested, Col 4: TD_Harvested?, Col 5: Mua_Harvested?
    # Wait, headers in PL4:
    # 20: |Vùng/Tỉnh|Lúa hè thu|Lúa hè thu|Gieo cấy lúa thu đông|Gieo cấy lúa mùa|DT gieo trồng các cây màu lương thực|...
    # 21: |...|Diện tích gieo cấy|Diện tích thu hoạch|Diện tích thu hoạch|Diện tích thu hoạch|...
    # Wait, Col 4 title "Gieo cấy lúa thu đông" but row 21 says "Diện tích thu hoạch"? That looks like an error in row 21 of the source file or I misread.
    # Usually Col 4 is "Thu Đông Planted". Row 46 (DBSCL) Col 4 has 218,929. This is likely planted area for Thu Dong.
    # Col 5 title "Gieo cấy lúa mùa", row 21 says "Diện tích thu hoạch". This is definitely a copy-paste error in the source file header row 21. 
    # Logic dictates: Col 4 is Thu Dong Planted, Col 5 is Mua Planted.
    
    data = [
        ["Miền Nam", 1960003, 1193030, None, 258048, 594602, 28127, 21338, 291993], # Ngo 281271? PL4 row 23 says 281,271. Copied as 28127.
        ["D.H Nam Trung Bộ", 153758, 27400, None, 67499, 93198, 26017, 7134, 60047],
        ["TP Đà Nẵng", 3300, None, None, None, 1028, 578, 450, None],
        ["Quảng Nam", 37100, None, None, 40211, 23900, 6500, 4500, 12900],
        ["Quảng Ngãi", 32256, 1485, None, None, 22949, 4160, 1900, 16889],
        ["Bình Định", 41328, 24515, None, 22788, 19600, 6711, None, 12889],
        ["Phú Yên", 23774, 1400, None, 4500, 17656, 5112, 175, 12369],
        ["Khánh Hoà", 16000, None, None, None, 8065, 2956, 109, 5000],
        ["Tây Nguyên", 6489, 0, None, 139752, 284418, 154846, 7359, 122213],
        ["Kon Tum", None, None, None, 15407, 43300, 6475, 137, 36688],
        ["Gia Lai", None, None, None, 33524, 85155, 39773, 752, 44630],
        ["Đắc Lắc", None, None, None, 44935, 98840, 73900, 1874, 23066],
        ["Đắc Nông", None, None, None, 33110, 40156, 21400, 3340, 15416],
        ["Lâm Đồng", 6489, None, None, 12776, 16967, 13298, 1256, 2413],
        ["Đông Nam Bộ", 164393, 62751, None, 24446, 177227, 68626, 836, 107765],
        ["TP Hồ Chí Minh", 6214, None, None, 297, 1007, 1007, None, None],
        ["Ninh Thuận", 10640, 800, None, 1033, 6563, 6459, 104, None],
        ["Bình Phước", 14000, None, None, None, 29630, 5981, 149, 23500],
        ["Tây Ninh", 63642, 36846, None, 11972, 42262, 7800, None, 34462],
        ["Bình Dương", 2069, None, None, 1136, 4167, 155, 171, 3841],
        ["Đồng Nai", 25367, None, None, None, 37797, 25098, 133, 12566],
        ["Bình Thuận", 38709, 21929, None, 7987, 36189, 10559, 234, 25396],
        ["Bà Rịa-V.Tàu", 3752, 3176, None, 2021, 19612, 11567, 45, 8000],
        ["ĐBS Cửu Long", 1635363, 1102879, 218929, 26351, 39759, 31782, 6009, 1968],
        ["Long An", 207578, 125392, 5025, 651, 4995, 4995, None, None],
        ["Đồng Tháp", 197078, 197075, 56665, None, 4444, 3594, 850, None],
        ["An Giang", 232488, 224363, 14041, None, 6307, 6187, 30, 90],
        ["Tiền Giang", 120230, 61751, None, None, 4629, 4120, 250, 259],
        ["Vĩnh Long", 62751, 62751, 40151, None, 6730, 3947, 2671, 112],
        ["Bến Tre", 21341, None, None, None, 563, 406, 50, 107],
        ["Kiên Giang", 274559, 140837, 11653, None, 0, None, None, None],
        ["Cần Thơ", 84869, 83022, 34355, None, 563, 563, None, None],
        ["Hậu Giang", 79744, 79149, 48460, None, 2209, 2209, None, None],
        ["Trà Vinh", 81356, 35415, None, 22000, 5913, 3881, 880, 1152],
        ["Sóc Trăng", 188565, 83344, 4000, 1000, 3406, 1880, 1278, 248],
        ["Bạc Liêu", 55634, 5780, 1138, 2700, 0, None, None, None],
        ["Cà Mau", 29170, 4000, 3441, None, 0, None, None, None]
    ] # Fix Ngo value row 1: 281271
    data[0][6] = 281271

    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Thu Đông"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[5])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for idx, (cmd, sub) in enumerate(items):
            try:
                v = normalize_number(row[idx+6])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
            
    return records

def parse_pl5():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL5", "source_file": "2010_08_Phuluc_T08_2010_PL5.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Monthly", "report_date": "2010-08-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Vung, ThuocLa, Mia, Bong, DayLac, Rau, Dau]
    data = [
        ["Miền Nam", 264166, 23694, 71209, 25524, 13199, 125672, 1006, 3862, 221733, 46258],
        ["D.H Nam Trg Bộ", 71365, 1574, 23896, 6301, 902, 38217, 434, 41, 27863, 27863],
        ["TP Đà Nẵng", 1195, None, 618, 211, None, 366, None, None, 659, 78],
        ["Quảng Nam", 13252, None, 9772, 2101, 502, 700, 177, None, 8500, 3400],
        ["Quảng Ngãi", 10365, 375, 3796, None, None, 6194, None, None, 5849, 1475],
        ["Bình Định", 13551, 881, 8893, 1576, None, 2201, None, None, 8159, 1039],
        ["Phú Yên", 16823, 318, 672, 2413, 400, 12722, 257, 41, 2456, 1687],
        ["Khánh Hoà", 16179, None, 145, None, None, 16034, None, None, 2240, 733],
        ["Tây Nguyên", 51202, 13867, 6891, 1436, 6539, 22469, 0, 0, 29948, 19229],
        ["Kon Tum", 4108, None, 144, None, 1867, 2097, None, None, 700, 92],
        ["Gia Lai", 13629, None, 800, 900, 4622, 7307, None, None, 8108, 3488],
        ["Đắc Lắc", 20300, 5187, 2737, 536, 50, 11790, None, None, 3540, 9078],
        ["Đắc Nông", 11965, 8680, 3210, None, None, 75, None, None, 1398, 5271],
        ["Lâm Đồng", 1200, None, None, None, None, 1200, None, None, 16202, 1300],
        ["Đông Nam Bộ", 56719, 671, 26002, 7642, 5596, 16236, 572, 0, 54665, 14002],
        ["TP Hồ Chí Minh", 2690, None, 900, None, None, 1790, None, None, 10489, None],
        ["Ninh Thuận", 1613, None, 135, 461, 32, 413, 572, None, 8820, 2097],
        ["Bình Phước", 140, None, 130, 10, None, None, None, None, 816, None],
        ["Tây Ninh", 30398, None, 16174, 1502, 4632, 8090, None, None, 15398, 5520],
        ["Bình Dương", 934, None, 635, None, None, 299, None, None, 2871, 199],
        ["Đồng Nai", 10297, 419, 4100, 20, 800, 4958, None, None, 9728, 3942],
        ["Bình Thuận", 9950, 241, 3487, 5649, 31, 542, None, None, 2118, 1763],
        ["Bà Rịa-V.Tàu", 697, 11, 441, None, 101, 144, None, None, 4425, 481],
        ["ĐBS Cửu Long", 84880, 7582, 14420, 10145, 162, 48750, 0, 3821, 109257, 4615],
        ["Long An", 25032, None, 7000, 1275, 122, 13991, None, 2644, 13036, None],
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
            if idx+2 < len(row):
                v = normalize_number(row[idx+2])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        if len(row) > 9:
            v_rau = normalize_number(row[9])
            if v_rau is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_rau/1.0, "unit": "ha", "data_type": "Actual"}))
        
        if len(row) > 10:
            v_dau = normalize_number(row[10])
            if v_dau is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_dau/1.0, "unit": "ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/08"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl1()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl2()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL2.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl3()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL3.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl4()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl5()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL5.json"))
    print("Successfully parsed PL1-PL5 for August 2010.")
