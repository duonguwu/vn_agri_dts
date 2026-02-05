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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "Trung du và MN phía Bắc": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc",
        "TD và MN phía Bắc": "Đông Bắc", "Trung du và miền núi": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "Vùng Duyên hải miền Trung": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ", "Vùng Đông Nam bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", 
        "Hà Nội (mở rộng)": "Hà Nội", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
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
    elif norm_loc == "Miền bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    elif norm_loc == "Trung uơng":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước - Trung ương"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl3b():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL3b", "source_file": "2010_06_Phuluc_06_2010_PL3b.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Monthly", "report_date": "2010-06-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Vung, ThuocLa, MiaT, Bong, DayLac, Rau, Dau]
    data = [
        ["Miền Nam", 233945, 23180, 63429, 22320, 13171, 106977, 1006, 3862, 221466, 42951],
        ["D.H Nam Trg Bộ", 59577, 1199, 21849, 3802, 874, 31378, 434, 41, 27467, 27467],
        ["TP Đà Nẵng", 343, None, 211, None, None, 132, None, None, 263, 78],
        ["Quảng Nam", 11032, None, 8264, 1800, 502, 289, 177, None, 8500, 3400],
        ["Quảng Ngãi", 3796, None, 3796, None, None, None, None, None, 5849, 1475],
        ["BìnhĐịnh", 13551, 881, 8893, 1576, None, 2201, None, None, 8159, 1039],
        ["Phú Yên", 14676, 318, 540, 426, 372, 12722, 257, 41, 2456, 1687],
        ["Khánh Hoà", 16179, None, 145, None, None, 16034, None, None, 2240, 733],
        ["Tây Nguyên", 43145, 13728, 7378, 3093, 6539, 12407, 0, 0, 34630, 16475],
        ["Kon Tum", 4022, None, 58, None, 1867, 2097, None, None, 8700, 92],
        ["Gia Lai", 14706, None, 211, 2566, 4622, 7307, None, None, 8108, 3488],
        ["Đắc Lắc", 9257, 4578, 2374, 527, 50, 1728, None, None, 2705, 7209],
        ["Đắc Nông", 13960, 9150, 4735, None, None, 75, None, None, 1398, 5271],
        ["Lâm Đồng", 1200, None, None, None, None, 1200, None, None, 13719, 415],
        ["Đông Nam Bộ", 49516, 671, 21845, 5280, 5596, 15552, 572, 0, 50112, 13449],
        ["TP Hồ Chí Minh", 2690, None, 900, None, None, 1790, None, None, 8092, None],
        ["Ninh Thuận", 1613, None, 135, 461, 32, 413, 572, None, 8820, 2097],
        ["Bình Phước", 140, None, 130, 10, None, None, None, None, 816, None],
        ["Tây Ninh", 26212, None, 12017, 1473, 4632, 8090, None, None, 13242, 4967],
        ["Bình Dương", 934, None, 635, None, None, 299, None, None, 2871, 199],
        ["Đồng Nai", 9613, 419, 4100, 20, 800, 4274, None, None, 9728, 3942],
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
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        # CCN
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        # Rau
        v = normalize_number(row[9])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        # Dau
        v = normalize_number(row[10])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))

    return records

def parse_pl4():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL4", "source_file": "2010_06_Phuluc_06_2010_PL4.md"}
    records = []
    # Data is 1/4/2010
    t = {"year": 2010, "month": 4, "period_type": "Monthly", "report_date": "2010-04-01"}
    
    # [Item, Unit, V2010]
    data = [
        ["Tổng số Trâu", "Con", 2902109.0],
        ["Tổng số Bò", "Con", 6019958.0],
        ["Tổng số Lợn", "Con", 27313824.0],
        ["Lợn nái", "Con", 4190622.0],
        ["Số con lợn thịt xuất chuồng", "Con", 26009231.0],
        ["Sản lượng thịt lợn xuất chuồng", "Tan", 1801098.4],
        ["Tổng số Gia cầm", "1000 con", 277437.7],
        ["Gà", "1000 con", 200832.0],
        ["Sản lượng thịt gia cầm hơi giết bán", "Tan", 330738.2],
        ["Sản lượng trứng gia cầm", "1000 qua", 3278817.3],
    ]
    
    for row in data:
        item, unit, val = row
        sector = "Livestock"
        cmd = item
        attr = "Total_Head" # Default
        
        if "thịt" in item: 
            attr = "Production"
            if "lợn" in item: cmd = "Thịt lợn"
            if "gia cầm" in item: cmd = "Thịt gia cầm"
        if "trứng" in item:
            attr = "Production"
            cmd = "Trứng gia cầm"
        if "Lợn nái" in item: cmd = "Lợn"; attr = "Total_Head"; sub = "Nái"
        else: sub = None
        
        u = "head"
        if unit == "Tan": u = "ton"
        elif "1000" in unit: u = "1000_head" # Gia cam
        if unit == "1000 qua": u = "1000_egg"
        
        if item == "Sản lượng trứng gia cầm": u = "1000_egg"
        if item == "Tổng số Gia cầm" or item == "Gà": u = "1000_head"

        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": sector, "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": val, "unit": u, "data_type": "Actual"}))
    return records

def parse_pl5a():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL5a", "source_file": "2010_06_Phuluc_06_2010_PL5a.md"}
    records = []
    # 6 months
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    data = [
        ["Trồng rừng tập trung", 78.3],
        ["Rừng phòng hộ, đặc dụng", 13.5],
        ["Rừng sản xuất", 64.8],
        ["Chăm sóc rừng trồng", 194.9],
        ["Khoanh nuôi tái sinh, trồng dặm", 646.8],
        ["Khoán bảo vệ rừng", 2077.1],
        ["Khai thác gỗ", 1775], # 1000 m3
        ["Trồng cây phân tán", 107.6] # Trieu cay
    ]
    
    for row in data:
        item, val = row
        u = "1000_ha"
        if "gỗ" in item: u = "1000_m3"
        elif "phân tán" in item: u = "million_tree"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))
    return records

def parse_pl5b():
    metadata_f = {"year": 2010, "month": 6, "appendix_number": "PL5b", "source_file": "2010_06_Phuluc_06_2010_PL5b.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    # [Loc, Total, PHDD, KinhTe, ChamSoc, KhoanhNuoi, KhoanBaoVe]
    forestry_data = [
        ["Cả nước", 78315, 13463, 64852, 194894, 646762, 2077081],
        ["Miền bắc", 75322, 11470, 63852, 152234, 529766, 1176444],
        ["ĐB. sông Hồng", 11042, 2276, 8766, 46596, 7876, 31752],
        ["Hà Nội (mở rộng)", 104, 42, 62, None, None, None],
        ["Vĩnh Phúc", 50, None, 50, 204, None, 11157],
        ["Bắc Ninh", 30, 30, None, None, None, None],
        ["Quảng Ninh", 10436, 1947, 8489, 45000, 5981, None],
        ["Hải Dương", 130, 20, 110, 130, None, 3042],
        ["Hải Phòng", None, None, None, 810, 1855, 5814],
        ["Hưng Yên", None, None, None, None, None, None],
        ["Thái Bình", None, None, None, None, None, 7000],
        ["Hà Nam", 55, None, 55, 55, 40, 3674],
        ["Nam Định", 127, 127, None, 397, None, 1065],
        ["Ninh Bình", 110, 110, None, None, None, None],
        ["Trung du và miền núi", 54016, 8464, 45552, 55602, 427153, 863710],
        ["Hà Giang", 2710.0, 725, 1985, 25100, 44688, 93466],
        ["Cao Bằng", 253, 33, 220, None, None, None],
        ["Bắc Kạn", 3964, 1091, 2873, None, 10478, 15309],
        ["Tuyên Quang", 9971, 925, 9046, 3795, 28597, 180140],
        ["Lào Cai", 1809, 174, 1635, 1676, 5843, 101312],
        ["Yên Bái", 10201, None, 10201, None, None, 220484],
        ["Thái Nguyên", 5182, 979.0, 4203, None, None, None],
        ["Lạng Sơn", 4179, 1442, 2737, 5823, 5639, 13212],
        ["Bắc Giang", 1833, 220, 1613, 840, 222, 28321],
        ["Phú Thọ", 6851, 342, 6509, None, None, None],
        ["Điện Biên", 616, 287, 329, 798, 55350, 59163],
        ["Lai Châu", 758, 305, 453, None, 95090.0, 131922],
        ["Sơn La", 2100, 1440.0, 660, 9070, 179231, 20381],
        ["Hoà Bình", 3589, 501, 3088, 8500, 2015, None],
        ["Bắc Trung Bộ", 10264, 730, 9534, 50036, 94737, 280982],
        ["Thanh Hoá", 6500, 340, 6160, 14154, 15417, 63621],
        ["Nghệ An", 3377, 357, 3020, 18615, 55000, 105000],
        ["Hà Tĩnh", 387, 33, 354, 14570, 9081, 40000],
        ["Quảng Bình", None, None, None, 740, 9000, 55337],
        ["Quảng Trị", None, None, None, None, None, None],
        ["Thừa Thiên Huế", None, None, None, 1957, 6239, 17024],
        ["Miền Nam", 93.0, 93.0, 0.0, 41317.0, 115266.0, 880053.0],
        ["D.H Nam Trung Bộ", 30, 30, 0, 38096, 91069, 264138],
        ["Đà Nẵng", 20, 20, None, 169, 121, 15000],
        ["Quảng Nam", None, None, None, 9050, 23500, None],
        ["Quảng Ngãi", None, None, None, None, 2100, 27346],
        ["BìnhĐịnh", 10, 10, None, 8094, 50413, 41670],
        ["Phú Yên", None, None, None, 11000, 2400, 24558],
        ["Khánh Hoà", None, None, None, 450, 1014, 8498],
        ["Ninh Thuận", None, None, None, None, 1000, 41705],
        ["Bình Thuận", None, None, None, 9333, 10521, 105361],
        ["Tây Nguyên", 0, 0, 0, 2407, 14295, 519903],
        ["Kon Tum", None, None, None, 1058, 8715, 75476],
        ["Gia Lai", None, None, None, None, None, None],
        ["Đắk Lắk", None, None, None, 1131, 3944, 60120],
        ["Đắk Nông", None, None, None, 218, 1636, 32371],
        ["Lâm Đồng", None, None, None, None, None, 351936],
        ["Đông Nam Bộ", 63, 63, 0, 743, 9902, 91962],
        ["Bình Phước", None, None, None, None, None, 19624],
        ["Tây Ninh", 3, 3, None, None, 7873, 40234],
        ["Bình Dương", None, None, None, None, None, None],
        ["Đồng Nai", None, None, None, None, 889, None],
        ["Bà Rịa-Vũng Tàu", None, None, None, 985, 1346, None],
        ["TP Hồ Chí Minh", 60, 60, None, 743, 155, 30758],
        ["ĐB. sông Cửu Long", 0, 0, 0, 71, 0, 4050],
        ["Long An", None, None, None, None, None, None],
        ["Tiền Giang", None, None, None, None, None, None],
        ["Bến Tre", None, None, None, None, None, None],
        ["Trà Vinh", None, None, None, None, None, None],
        ["Vĩnh Long", None, None, None, None, None, None],
        ["Đồng Tháp", None, None, None, None, None, 3260],
        ["An Giang", None, None, None, None, None, None],
        ["Kiên Giang", None, None, None, None, None, None],
        ["Cần Thơ", None, None, None, None, None, None],
        ["Hậu Giang", None, None, None, None, None, None],
        ["Sóc Trăng", None, None, None, 71, None, 790],
        ["Bạc Liêu", None, None, None, None, None, None],
        ["Cà Mau", None, None, None, None, None, None],
        ["Trung uơng", 2900, 1900, 1000, 1343, 1730, 20584],
    ]
    
    regional_list = ["Miền bắc", "ĐB. sông Hồng", "Trung du và miền núi", "Bắc Trung Bộ", "Miền Nam", "D.H Nam Trung Bộ", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Tây Nguyên"]
    
    for row in forestry_data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Cả nước": gl = "National"
        if loc == "Trung uơng": gl = "National"; loc = "Cả nước - Trung ương"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[4])
        if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng trồng", "sub_item": None}, {"attribute": "Area_Tended", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[5])
        if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": None}, {"attribute": "Area_Regenerated", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[6])
        if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": None}, {"attribute": "Area_Protected", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl6():
    metadata_fish = {"year": 2010, "month": 6, "appendix_number": "PL6", "source_file": "2010_06_Phuluc_06_2010_PL5b.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    fish_data = [
        ["Tổng sản lượng thủy sản", 2488],
        ["Sản lượng khai thác", 1243],
        ["Khai thác biển", 1176],
        ["Khai thác nội địa", 67],
        ["Sản lượng nuôi trồng", 1245]
    ]
    for row in fish_data:
        records.append(create_record(metadata_fish, t, "Cả nước", "National", {"sector": "Fishery", "commodity": row[0]}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Actual"}))
    return records

def parse_pl7():
    metadata_inv = {"year": 2010, "month": 6, "appendix_number": "PL7", "source_file": "2010_06_Phuluc_06_2010_PL5b.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    inv_data = [
        ["Đầu tư Thuỷ lợi", 1707000],
        ["Đầu tư Nông nghiệp", 242500],
        ["Đầu tư Lâm nghiệp", 39000],
        ["Đầu tư Thuỷ sản", 16800],
        ["Khoa học - Công nghệ", 22500],
        ["Giáo dục - Đào tạo", 50500],
        ["Các ngành khác", 35500],
        ["Chương trình mục tiêu", 43500],
        ["Vốn đầu tư theo các mục tiêu", 92500],
        ["Vốn chuẩn bị đầu tư", 27000],
        ["Vốn trái phiếu Chính phủ", 1767000],
        ["Các dự án có trong QĐ171", 1275000],
        ["Các dự án cấp bách bổ sung", 227000],
        ["Các dự án thuỷ lợi ĐBSHồng", 265000],
        ["Tổng vốn đầu tư", 4043800]
    ]
    for row in inv_data:
        records.append(create_record(metadata_inv, t, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl3b()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL3b.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl4()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl5a()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL5a.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl5b()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL5b.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl6()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL6.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl7()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL7.json"))
    print("Successfully parsed PL3b, PL4, PL5a, PL5b, PL6, PL7 for June 2010.")
