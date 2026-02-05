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
    # Summary Table PL1 2011-04
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL1", "source_file": "2011_04_Phuluc_04_2011_f_PL1.md"}
    records = []
    t = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-15"}
    
    # [Item, Unit, Last Year, This Year, YoY]
    # Units in PL1: 1000 ha
    data = [
        ("Gieo cấy lúa hè thu miền Nam", "1000 ha", 699.3, 674.3, 96.4),
        ("Trong đó: - Đồng bằng sông Cửu Long", "1000 ha", 670.3, 645.4, 96.3),
        ("Thu hoạch lúa đông xuân miền Nam", "1000 ha", 1745.7, 1648.7, 94.4),
        ("Trong đó: - Đồng bằng sông Cửu Long", "1000 ha", 1534.3, 1459.9, 95.2),
        ("Gieo trồng màu lương thực", "1000 ha", 734.5, 798.2, 108.7),
        ("Trong đó: - Ngô", "1000 ha", 459.2, 502.8, 109.5),
        ("- Khoai lang", "1000 ha", 93.3, 94.0, 100.8),
        ("- Sắn", "1000 ha", 157.1, 186.0, 118.4),
        ("Gieo trồng cây công nghiệp", "1000 ha", 457.5, 468.9, 102.5),
        ("Trong đó: - Đậu tương", "1000 ha", 128.6, 112.3, 87.4),
        ("- Lạc", "1000 ha", 166.8, 172.1, 103.2),
        ("- Mía", "1000 ha", 117.2, 142.7, 121.8),
        ("- Thuốc lá", "1000 ha", 23.3, 18.9, 81.1),
        ("Gieo trồng rau, đậu các loại", "1000 ha", 423.2, 447.2, 105.7)
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
        if "Miền Nam" in item_raw: loc_map = "Miền Nam"
        elif "Đồng bằng sông Cửu Long" in item_raw: loc_map = "Đồng bằng sông Cửu Long"
        
        # Clean Item Name
        item_clean = item_raw.replace("Chia ra:", "").replace("Trong đó:", "").replace("+", "").replace("-", "").strip()
        
        # Determine Commodity
        cmd = "Lúa"
        sub = "Đông Xuân" # Default?
        
        if "lúa hè thu" in item_clean.lower(): sub = "Hè Thu"
        elif "lúa đông xuân" in item_clean.lower(): sub = "Đông Xuân"
        elif "màu lương thực" in item_clean.lower(): cmd = "Màu lương thực"; sub = None; loc_map = "Cả nước"
        elif "ngô" in item_clean.lower(): cmd = "Ngô"; sub = None; loc_map = "Cả nước"
        elif "khoai lang" in item_clean.lower(): cmd = "Khoai lang"; sub = None; loc_map = "Cả nước"
        elif "sắn" in item_clean.lower(): cmd = "Sắn"; sub = None; loc_map = "Cả nước"
        elif "cây công nghiệp" in item_clean.lower(): cmd = "Cây công nghiệp ngắn ngày"; sub = None; loc_map = "Cả nước"
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
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL2", "source_file": "2011_04_Phuluc_04_2011_f_PL2.md"}
    records = []
    t = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-15"}
    
    # [Name, Lua DX, Mau LT, Ngo, Khoai, San, Cay khac]
    data = [
        ["Miền Bắc", 1129388, 631695, 433511, 78629, 113990, 5566],
        ["ĐB sông Hồng", 564005, 109389, 82121, 21746, 4099, 1422],
        ["Hà Nội", 100387, 26383, 20368, 4868, 690, 457],
        ["Hải Phòng", 38507, 3263, 2151, 1112, None, None],
        ["Vĩnh Phúc", 31371, 19145, 15087, 2438, 1420, 200],
        ["Bắc Ninh", 35929, 4937, 4132, 805, None, None],
        ["Hải Dương", 63817, 3462, 2540, 922, None, None],
        ["Hưng Yên", 40305, 8624, 7624, 1000, None, None],
        ["Hà Nam", 34522, 7664, 7267, 396, None, None],
        ["Nam Định", 77800, 4652, 4652, 1533, None, None],
        ["Thái Bình", 82739, 12360, 9380, 2980, None, None],
        ["Ninh Bình", 41594, 9353, 5629, 2795, 929, None],
        ["Quảng Ninh", 17034, 9546, 4824, 2897, 1060, 765],
        ["TD và MN phía Bắc", 224965, 355330, 257940, 23743, 69852, 3794],
        ["Hà Giang", 9907, 34528, 34528, None, None, None],
        ["Cao Bằng", 2683, 24631, 24559, 72, None, None],
        ["Lào Cai", 9198, 21597, 21421, 176, None, None],
        ["Bắc Cạn", 7501, 9526, 8573, 92, 748, 113],
        ["Lạng Sơn", 8254, 14001, 10465, 696, 2790, 50],
        ["Tuyên Quang", 19653, 9542, 6705, 2837, None, None],
        ["Yên Bái", 17840, 30059, 15832, 1580, 12647, None],
        ["Thái Nguyên", 29267, 22000, 13659, 5795, 2546, None],
        ["Phú Thọ", 35897, 27527, 17911, 1827, 7589, 200],
        ["Bắc Giang", 48445, 15123, 8061, 7062, None, None],
        ["Lai Châu", 4428, 17813, 13352, None, 4461, None],
        ["Điện Biên", 7858, 13954, 8983, None, 4971, None],
        ["Sơn La", 9047, 79959, 55550, 76, 22102, 2231],
        ["Hoà Bình", 14987, 35069, 18341, 3530, 11998, 1200],
        ["Bắc Trung Bộ", 340418, 166977, 93449, 33139, 40039, 350],
        ["Thanh Hoá", 120705, 59430, 33501, 9429, 16500, None],
        ["Nghệ An", 87500, 52157, 43247, 8910, None, None],
        ["Hà Tĩnh", 53764, 16738, 8151, 6000, 2587, None],
        ["Quảng Bình", 27100, 14400, 4300, 4200, 5900, None],
        ["Quảng Trị", 24029, 12000, 2500, 500, 9000, None],
        ["Thừa Thiên Huế", 27320, 12252, 1750, 4100, 6052, 350]
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
    # Northern Industrial Crops & Veg (PL3)
    # [Name, CN Total, Dau Tuong, Lac, Mia, Thuoc La, Cay khac, Rau Dau]
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL3", "source_file": "2011_04_Phuluc_04_2011_f_PL3.md"}
    records = []
    t = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-15"}
    
    data = [
        ["Miền Bắc", 289277, 107860, 131932, 35473, 9180, 4831, 214511],
        ["ĐB sông Hồng", 106698, 76502, 26080, 1531, 1000, 1584, 110812],
        ["Hà Nội", 38093, 31797, 5839, None, None, 457, 19677],
        ["Hải Phòng", 1000, None, None, None, 1000, None, 11230],
        ["Vĩnh Phúc", 7260, 4008, 2679, 247, None, 326, 5738],
        ["Bắc Ninh", 2580, 1309, 1271, None, None, None, 6147],
        ["Hải Dương", 262, 211, 51, None, None, None, 16306],
        ["Hưng Yên", 3392, 2678, 714, None, None, None, 9631],
        ["Hà Nam", 11440, 11320, 119, None, None, None, 3009],
        ["Nam Định", 7155, 1422, 5733, None, None, None, 16907],
        ["Thái Bình", 16335, 13250, 3085, None, None, None, 12000],
        ["Ninh Bình", 15560, 9998, 4225, 907, None, 430, 5105],
        ["Quảng Ninh", 3621, 509, 2364, 377, None, 371, 5062],
        ["TD và MN phía Bắc", 79085, 22858, 33758, 11242, 8130, 3097, 50376],
        ["Hà Giang", 12099, 6809, 4600, None, None, 690, 6613],
        ["Cao Bằng", 5780, 1318, 211, 1209, 3042, None, 430],
        ["Lào Cai", 3127, 2517, None, None, 610, None, 2195],
        ["Bắc Cạn", 2737, 854, 259, 60, 1044, 520, 389],
        ["Lạng Sơn", 4681, 547, None, None, 3334, 800, 3500],
        ["Tuyên Quang", 4516, 1092, 3424, None, None, None, 1311],
        ["Yên Bái", 1462, None, 1462, None, None, None, 1558],
        ["Thái Nguyên", 4356, 1066, 3190, None, 100, None, 7199],
        ["Phú Thọ", 6551, 1238, 5313, None, None, None, 6123],
        ["Bắc Giang", 11440, 488, 10952, None, None, None, 14509],
        ["Lai Châu", 1154, 517, 637, None, None, None, 307],
        ["Điện Biên", 2105, 1595, 510, None, None, None, 125],
        ["Sơn La", 5263, 4010, None, 1253, None, None, 3030],
        ["Hoà Bình", 13814, 807, 3200, 8720, None, 1087, 3087],
        ["Bắc Trung Bộ", 103494, 8500, 72094, 22700, 50, 150, 53323],
        ["Thanh Hoá", 36432, 8500, 15332, 12600, None, None, 16794],
        ["Nghệ An", 30223, None, 20223, 10000, None, None, 20841],
        ["Hà Tĩnh", 23777, None, 23777, None, None, None, 8672],
        ["Quảng Bình", 5100, None, 5100, None, None, None, 456],
        ["Quảng Trị", 4300, None, 4300, None, None, None, 1010],
        ["Thừa Thiên Huế", 3662, None, 3362, 100, 50, 150, 5550]
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl1()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl2()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl3()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL3.json"))
    print("Successfully parsed PL1, PL2, PL3 for April 2011 (Cultivation North Summary & Detail).")
