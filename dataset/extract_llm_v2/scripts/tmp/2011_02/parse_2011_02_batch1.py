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
        "ThừThiê H ế\n  a n u": "Thừa Thiên Huế", "Bắc Giang\n": "Bắc Giang", "Quảng Ninh\n": "Quảng Ninh"
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
    # Summary Table PL1 2011-02
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL1", "source_file": "2011_02_Phuluc_02_2011_PL1.md"}
    records = []
    t = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-15"}
    
    # [Item, Unit, Last Year, This Year, YoY]
    data = [
        ("Gieo cấy lúa đông xuân cả nước", "1000 ha", 2742.7, 2580.7, 94.1),
        ("Chia ra: + Miền Bắc", "1000 ha", 884.9, 673.9, 76.2),
        ("Trong đó: - Vùng Đồng bằng sông Hồng", "1000 ha", 409.9, 299.8, 73.2),
        ("- Vùng Duyên hải Bắc Trung bộ", "1000 ha", 335.0, 298.6, 89.2),
        ("+ Miền Nam", "1000 ha", 1857.8, 1906.8, 102.6),
        ("Trong đó: Đồng bằng sông Cửu Long", "1000 ha", 1530.0, 1566.4, 102.4),
        ("Thu hoạch lúa đông xuân ở miền Nam", "1000 ha", 268.0, 377.1, 140.7),
        ("Trong đó: Đồng bằng sông Cửu Long", "1000 ha", 268.0, 367.4, 137.1),
        ("Gieo trồng màu lương thực", "1000 ha", 428.3, 414.7, 96.8),
        ("Trong đó: - Ngô", "1000 ha", 263.7, 245.8, 93.2),
        ("- Khoai lang", "1000 ha", 68.5, 63.8, 93.0),
        ("- Sắn", "1000 ha", 95.8, 97.2, 101.4),
        ("Gieo trồng cây công nghiệp ngắn ngày", "1000 ha", 247.2, 263.7, 106.7),
        ("Trong đó: - Đậu tương", "1000 ha", 85.0, 89.1, 104.8),
        ("- Lạc", "1000 ha", 99.3, 95.1, 95.7),
        ("Gieo trồng rau, đậu các loại", "1000 ha", 310.2, 320.0, 103.2)
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
        
        # Determining Location from Item Text
        loc_map = "Cả nước"
        if "Miền Bắc" in item_raw: loc_map = "Miền Bắc"
        elif "Miền Nam" in item_raw: loc_map = "Miền Nam"
        elif "Đồng bằng sông Cửu Long" in item_raw: loc_map = "Đồng bằng sông Cửu Long"
        elif "Đồng bằng sông Hồng" in item_raw: loc_map = "Đồng bằng sông Hồng"
        elif "Duyên hải Bắc Trung bộ" in item_raw: loc_map = "Bắc Trung Bộ"
        
        # Clean Item Name
        item_clean = item_raw.replace("Chia ra:", "").replace("Trong đó:", "").replace("+", "").replace("-", "").strip()
        
        # Determine Commodity
        cmd = "Lúa"
        sub = "Đông Xuân"
        
        if "lúa đông xuân" in item_clean.lower(): pass
        elif "màu lương thực" in item_clean.lower(): cmd = "Màu lương thực"; sub = None; loc_map = "Cả nước" # Assuming national for items 3,4,5
        elif "ngô" in item_clean.lower(): cmd = "Ngô"; sub = None; loc_map = "Cả nước"
        elif "khoai lang" in item_clean.lower(): cmd = "Khoai lang"; sub = None; loc_map = "Cả nước"
        elif "sắn" in item_clean.lower(): cmd = "Sắn"; sub = None; loc_map = "Cả nước"
        elif "cây công nghiệp ngắn ngày" in item_clean.lower(): cmd = "Cây công nghiệp ngắn ngày"; sub = None; loc_map = "Cả nước"
        elif "đậu tương" in item_clean.lower(): cmd = "Đậu tương"; sub = None; loc_map = "Cả nước"
        elif "lạc" in item_clean.lower(): cmd = "Lạc"; sub = None; loc_map = "Cả nước"
        elif "rau, đậu các loại" in item_clean.lower(): cmd = "Rau đậu các loại"; sub = None; loc_map = "Cả nước"
        
        # Refine Location for Items 3,4,5. 
        # Footnote (**): "Miền Bắc bao gồm cả cây vụ đông 2010/11."
        # Unlike Jan, in Feb PL1 items 3,4,5 don't have asterisk explicitly in every line but item 3 header has (**).
        # Actually in Step 488 View: "3. Gieo trồng màu lương thực(**)". "4. Gieo trồng cây công nghiệp ngắn ngày(**)". "5. ...~~(**)~~"
        # Since it's Feb, data usually covers Whole Country for these items, but with North's Winter crop included.
        # So "Cả nước" is correct context.
        
        gl = "Regional" if loc_map != "Cả nước" else "National"
        
        comp = {"comparison_type": "YoY", "comparison_value": float(yoy)} if yoy is not None else None
        
        records.append(create_record(metadata, t, loc_map, gl, {"sector": sector, "commodity": cmd, "sub_item": sub}, {"attribute": metric, "value": float(val_2011), "unit": unit, "data_type": "Actual"}, comp))
        
    return records

def parse_pl2():
    # Northern Winter-Spring Crop
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL2", "source_file": "2011_02_Phuluc_02_2011_PL2.md"}
    records = []
    t = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-15"}
    
    # [Name, Lua DX, Mau LT, Ngo, Khoai, San, Cay khac]
    
    data = [
        ["Miền Bắc", 673920, 299753, 190043, 54039, 55036, 635],
        ["ĐB sông Hồng", 299838, 76989, 58340, 17675, 774, 200],
        ["Hà Nội", 80000, 17638, 13428, 4210, None, None],
        ["Hải Phòng", 18934, 3263, 2151, 1112, None, None],
        ["Vĩnh Phúc", 17923, 15711, 12776, 2261, 474, 200],
        ["Bắc Ninh", 650, 3342, 2537, 805, None, None],
        ["Hải Dương", 35153, 2540, 2540, None, None, None],
        ["Hưng Yên", 14000, 6000, 5000, 1000, None, None],
        ["Hà Nam", 15000, 4298, 3902, 396, None, None], # Adjusted Ngo to 3902 based on Jan logic
        ["Nam Định", 3040, 3828, 3828, 939, None, None],
        ["Thái Bình", 75000, 9930, 6950, 2980, None, None],
        ["Ninh Bình", 32632, 6562, 4055, 2207, 300, None],
        ["Quảng Ninh", 7506, 3877, 2112, 1765, None, None],
        ["TD và MN phía Bắc", 75443, 97081, 53748, 16581, 26552, 200],
        ["Hà Giang", 0, 4627, 4627, None, None, None],
        ["Cao Bằng", 0, 3540, 3468, 72, None, None],
        ["Lào Cai", 0, 676, 500, 176, None, None],
        ["Bắc Cạn", 0, 429, 387, 42, None, None],
        ["Lạng Sơn", 0, 397, 309, 88, None, None],
        ["Tuyên Quang", 4946, 7589, 5011, 2578, None, None],
        ["Yên Bái", 6820, 7613, 6513, 900, 200, None],
        ["Thái Nguyên", 4106, 11093, 6886, 4207, None, None],
        ["Phú Thọ", 29823, 25132, 15735, 1608, 7589, 200],
        ["Bắc Giang", 4388, 12000, 7000, 5000, None, None],
        ["Lai Châu", 4000, 200, 200, None, None, None],
        ["Điện Biên", 5000, 18, 18, None, None, None],
        ["Sơn La", 3360, 19493, 730, None, 18763, None],
        ["Hoà Bình", 13000, 4274, 2364, 1910, None, None],
        ["Bắc Trung Bộ", 298639, 125683, 77955, 19783, 27710, 235],
        ["Thanh Hoá", 106600, 53922, 30781, 6641, 16500, None],
        ["Nghệ An", 65000, 42057, 34447, 7610, None, None],
        ["Hà Tĩnh", 48364, 8009, 4777, 3232, None, None],
        ["Quảng Bình", 26930, 4300, 4300, None, None, None],
        ["Quảng Trị", 24029, 9700, 2200, 500, 7000, None],
        ["Thừa Thiên Huế", 27716, 7695, 1450, 1800, 4210, 235]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        # Lua
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Mau LT
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Ngo
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Khoai
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # San
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        # Cay khac
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl4():
    # Northern Industrial Crops & Feb
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL4", "source_file": "2011_02_Phuluc_02_2011_PL4.md"}
    records = []
    t = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-15"}
    
    # [Name, CN Total, Dau Tuong, Lac, Thuoc La, Rau Dau]
    data = [
        ["Miền Bắc", 150874, 88315, 60599, 1960, 164097],
        ["ĐB sông Hồng", 86117, 73628, 12189, 300, 90476],
        ["Hà Nội", 31124, 30519, 605, None, 12125],
        ["Hải Phòng", 300, None, None, 300, 8559],
        ["Vĩnh Phúc", 5349, 3539, 1810, None, 3628],
        ["Bắc Ninh", 1700, 1309, 391, None, 5301],
        ["Hải Dương", 162, 162, None, None, 16306],
        ["Hưng Yên", 2321, 2213, 108, None, 7080],
        ["Hà Nam", 11243, 11201, 42, None, 1848],
        ["Nam Định", 5855, 1422, 4433, None, 15427],
        ["Thái Bình", 14250, 13250, 1000, None, 12000],
        ["Ninh Bình", 13646, 9998, 3648, None, 4530],
        ["Quảng Ninh", 167, 15, 152, None, 3672],
        ["TD và MN phía Bắc", 13246, 6187, 5431, 1628, 32442],
        ["Hà Giang", 3301, 2521, 780, None, 5503],
        ["Cao Bằng", 1711, 493, 3, 1215, 430],
        ["Lào Cai", 861, 750, None, 111, 2195],
        ["Bắc Cạn", 5, 5, None, None, 199],
        ["Lạng Sơn", 302, None, None, 302, 2268],
        ["Tuyên Quang", 756, 709, 47, None, 1311],
        ["Yên Bái", 0, None, None, None, 1558],
        ["Thái Nguyên", 177, 56, 121, None, 4487],
        ["Phú Thọ", 3864, 1064, 2800, None, 3285],
        ["Bắc Giang", 1695, 15, 1680, None, 7500],
        ["Lai Châu", 20, 20, None, None, 307],
        ["Điện Biên", 47, 47, None, None, 125],
        ["Sơn La", 0, None, None, None, 1374],
        ["Hoà Bình", 507, 507, None, None, 1900],
        ["Bắc Trung Bộ", 51511, 8500, 42979, 32, 41179],
        ["Thanh Hoá", 23832, 8500, 15332, None, 16794],
        ["Nghệ An", 13000, None, 13000, None, 14744],
        ["Hà Tĩnh", 5847, None, 5847, None, 4455],
        ["Quảng Bình", 4090, None, 4090, None, 456],
        ["Quảng Trị", 3600, None, 3600, None, 1010],
        ["Thừa Thiên Huế", 1142, None, 1110, 32, 3720]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl1()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl2()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl4()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL4.json"))
    print("Successfully parsed PL1, PL2, PL4 for February 2011 (Cultivation North).")
