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
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL1", "source_file": "2010_09_phuluc_T09_2010_PL1.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Monthly", "report_date": "2010-09-15"}
    
    # [Item, V10] - Extracted manually from the file view
    data = [
        ["Thu hoạch lúa hè thu ở miền Nam", 1756.7],
        ["Đồng bằng sông Cửu Long", 1477.3],
        ["Gieo cấy lúa mùa cả nước", 1646.6],
        ["Miền Bắc", 1191.7],
        ["Đồng bằng sông Hồng", 578.4],
        ["Miền Nam", 454.9],
        ["Đồng bằng sông Cửu Long", 152.9],
        ["Gieo trồng cây lương thực, có củ", 1562.0],
        ["Ngô", 953.8],
        ["Khoai lang", 123.5],
        ["Sắn", 445.9],
        ["Gieo trồng cây công nghiệp ngắn ngày", 657.9],
        ["Lạc", 216.0],
        ["Đậu tương", 179.7],
        ["Mía", 159.7],
        ["Thuốc lá", 29.4],
        ["Gieo trồng rau, đậu các loại", 725.9]
    ]
    
    for row in data:
        item_name, v10 = row
        loc = "Cả nước"
        if "miền Nam" in item_name or item_name == "Miền Nam": loc = "Miền Nam"
        if "Miền Bắc" in item_name: loc = "Miền Bắc"
        if "Đồng bằng sông Cửu Long" in item_name: loc = "Đồng bằng sông Cửu Long"
        if "Đồng bằng sông Hồng" in item_name: loc = "ĐB sông Hồng"

        # Determine Context
        cmd = item_name
        attr = "Area_Planted"
        
        if "Thu hoạch lúa" in item_name:
             cmd = "Lúa"; sub = "Hè Thu"; attr = "Area_Harvested"
        elif "Đồng bằng sông Cửu Long" in item_name and "Thu hoạch" in data[0][0]: # Context of first item
             if row == data[1]: # DBSCL under Thu Hoach HT
                 cmd = "Lúa"; sub = "Hè Thu"; attr = "Area_Harvested"
             else: # DBSCL under Gieo Cay Lua Mua
                 cmd = "Lúa"; sub = "Mùa"; attr = "Area_Planted"
        elif "Gieo cấy lúa mùa" in item_name or item_name in ["Miền Bắc", "Miền Nam", "Đồng bằng sông Hồng"]:
             cmd = "Lúa"; sub = "Mùa"; attr = "Area_Planted"
        elif "Gieo trồng cây lương thực" in item_name: cmd = "Cây lương thực có củ"; sub = "Tổng số"; attr = "Area_Planted"
        elif "cây công nghiệp" in item_name: cmd = "Cây công nghiệp ngắn ngày"; sub = "Tổng số"; attr = "Area_Planted"
        elif "Gieo trồng rau" in item_name: cmd = "Rau đậu các loại"; sub = "Tổng số"; attr = "Area_Planted"
        elif item_name in ["Ngô", "Khoai lang", "Sắn", "Lạc", "Đậu tương", "Thuốc lá", "Mía"]:
             cmd = item_name; sub = None; attr = "Area_Planted"
        else:
             sub = None 

        gl = "National" if loc in ["Cả nước", "Miền Bắc", "Miền Nam"] else "Regional"
        
        if v10: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL2", "source_file": "2010_09_phuluc_T09_2010_PL2.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Monthly", "report_date": "2010-09-15"}
    
    # [Loc, Mua_Planted, Mua_Harvested, HeThu_Harvested, Mau_Total, Ngo, Khoai, San, Khac]
    data = [
        ["Miền Bắc", 1191688, 79894, 160626, 944807, 659402, 100709, 145982, 38713],
        ["ĐB sông Hồng", 578421, 41297, 0, 139211, 92121, 24719, 4703, 17667],
        ["Hà Nội", 101767, 39689, None, 33367, 24135, 7732, 1300, 200],
        ["Hải Phòng", 41657, None, None, 5110, 2310, 300, None, 2500],
        ["Vĩnh Phúc", 28530, None, None, 24916, 17975, 2788, 2018, 2135],
        ["Bắc Ninh", 36888, None, None, 3877, 2567, 710, None, 600],
        ["Hải Dương", 63014, None, None, 11083, 4351, 1441, None, 5291],
        ["Hưng Yên", 40458, None, None, 9568, 8913, 655, None, None],
        ["Hà Nam", 35519, None, None, 9046, 8647, 399, None, None],
        ["Nam Định", 80520, None, None, 9309, 3409, 1100, 300, 4500],
        ["Thái Bình", 83180, None, None, 13368, 8530, 2893, None, 1945],
        ["Ninh Bình", 39496, 1608, None, 6875, 4710, 2165, None, None],
        ["Quảng Ninh", 27392, None, None, 12691, 6574, 4536, 1085, 496],
        ["TD và MN phía Bắc", 428983, 6737, 0, 563432, 427486, 32040, 91219, 12687],
        ["Hà Giang", 25986, None, None, 50669, 42182, 649, 3761, 4077],
        ["Cao Bằng", 25725, None, None, 34715, 33849, 671, None, 195],
        ["Lào Cai", 19063, None, None, 39694, 30478, 820, 7787, 609],
        ["Bắc Cạn", 12920, None, None, 17637, 15878, 368, 1144, 247],
        ["Lạng Sơn", 33820, None, None, 29542, 20185, 1800, 5136, 2421],
        ["Tuyên Quang", 25731, 56, None, 11578, 11008, 570, None, None],
        ["Yên Bái", 23607, None, None, 39100, 22205, 2816, 13553, 526],
        ["Thái Nguyên", 41013, None, None, 28219, 17661, 6849, 3709, None],
        ["Phú Thọ", 33551, 6680, None, 32951, 22647, 2908, 7194, 202],
        ["Bắc Giang", 58055, None, None, 22391, 12420, 7771, 2200, None],
        ["Lai Châu", 32000, None, None, 22641, 17336, None, 5305, None],
        ["Điện Biên", 38635, None, None, 36286, 29130, 20, 7136, None],
        ["Sơn La", 35000, None, None, 142887, 116449, 258, 23285, 2895],
        ["Hoà Bình", 23877, None, None, 55122, 36058, 6540, 11009, 1515],
        ["Bắc Trung Bộ", 184284, 31860, 160626, 242164, 139795, 43950, 50060, 8359],
        ["Thanh Hoá", 133759, 30260, None, 83186, 59099, 14178, 9200, 709],
        ["Nghệ An", 44000, None, 58000, 90612, 62036, 11257, 16819, 500],
        ["Hà Tĩnh", 4325, None, 40825, 26572, 9383, 11000, 3439, 2750],
        ["Quảng Bình", None, None, 15370, 13480, 4162, 1586, 5782, 1950],
        ["Quảng Trị", 1600, 1600, 21297, 17704, 3505, 2429, 9770, 2000],
        ["Thừa Thiên Huế", 600, None, 25134, 10610, 1610, 3500, 5050, 450]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[4])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực có củ", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            try:
                if idx+5 < len(row):
                    v = normalize_number(row[idx+5])
                    if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
            
    return records

def parse_pl3():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL3", "source_file": "2010_09_phuluc_T09_2010_PL3.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Monthly", "report_date": "2010-09-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Mia, ThuocLa, OtherCCN, RauDau]
    data = [
        ["Miền Bắc", 381736, 155318, 140515, 26998, 16223, 42681, 375150],
        ["ĐB sông Hồng", 130400, 89945, 24122, 681, 2747, 12904, 170190],
        ["Hà Nội", 42556, 36043, 5606, 200, None, 707, 28913],
        ["Hải Phòng", 3037, 390, None, None, 2347, 300, 27699],
        ["Vĩnh Phúc", 10532, 6192, 3592, 75, None, 673, 9406],
        ["Bắc Ninh", 5074, 3590, 1169, None, None, 315, 7896],
        ["Hải Dương", 3260, 1450, 1300, None, None, 510, 26415],
        ["Hưng Yên", 3912, 2758, 932, None, None, 222, 19395],
        ["Hà Nam", 13139, 12741, 398, None, None, None, 6385],
        ["Nam Định", 10907, 2226, 3988, None, None, 4693, 10198],
        ["Thái Bình", 20414, 13779, 1500, None, 400, 4735, 16473],
        ["Ninh Bình", 12679, 9910, 2769, None, None, None, 8323],
        ["Quảng Ninh", 4890, 866, 2868, 406, None, 749, 9087],
        ["Trung du và MN phía Bắc", 135973, 58942, 45707, 10362, 13326, 7636, 98363],
        ["Hà Giang", 23369, 17362, 5797, None, None, 210, 10943],
        ["Cao Bằng", 10346, 4722, 1077, 892, 3421, 234, 1738],
        ["Lào Cai", 6669, 4799, 1286, None, 448, 136, 3245],
        ["Bắc Cạn", 4756, 2737, 322, 70, 1472, 155, 1611],
        ["Lạng Sơn", 14900, 1800, 2350, 250, 7900, 2600, 5900],
        ["Tuyên Quang", 6814, 1966, 4848, None, None, 0, 6320],
        ["Yên Bái", 6833, 2791, 1979, 798, None, 1265, 7510],
        ["Thái Nguyên", 6234, 1694, 4540, None, None, 0, 10154],
        ["Phú Thọ", 8501, 3045, 5364, None, None, 92, 5917],
        ["Bắc Giang", 13391, 1807, 10766, None, 85, 733, 25955],
        ["Lai Châu", 3163, 1569, 1325, None, None, 269, 735],
        ["Điện Biên", 7609, 5647, 1412, None, None, 550, 950],
        ["Sơn La", 9098, 6757, 658, 291, None, 1392, 5460],
        ["Hoà Bình", 14290, 2246, 3983, 8061, None, 0, 11925],
        ["Bắc Trung Bộ", 115363, 6431, 70686, 15955, 150, 22141, 106597],
        ["Thanh Hoá", 34878, 6039, 15221, 10569, None, 3049, 46213],
        ["Nghệ An", 44508, 392, 21634, 5236, 80, 17166, 33782],
        ["Hà Tĩnh", 22064, None, 20552, None, None, 1512, 15096],
        ["Quảng Bình", 5124, None, 5124, None, None, None, 586],
        ["Quảng Trị", 4815, None, 4558, None, None, 257, 5682],
        ["Thừa Thiên Huế", 3974, None, 3597, 150, 70, 157, 5238]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", None), ("Thuốc lá", None), ("Cây công nghiệp khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            if idx+2 < len(row):
                v = normalize_number(row[idx+2])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        if len(row) > 7:
            v_rau = normalize_number(row[7])
            if v_rau is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_rau/1.0, "unit": "ha", "data_type": "Actual"}))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/09"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl1()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl2()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL2.json"))
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl3()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL3.json"))
    print("Successfully parsed PL1-PL3 for September 2010.")
