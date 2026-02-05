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
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.replace("\n", "").strip()
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
    # Summary Table PL1 2011-01
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL1", "source_file": "2011_01_Phuluc_01_2011_PL1.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-15"}
    
    data = [
        # Note: Item, Unit, Last_Year(2010), Current_Year(2011), YoY%, vs_Plan% (Empty)
        # Using visual line mapping from Step 442
        ("Gieo cấy lúa đông xuân cả nước", "1000 ha", 1881.0, 1947.6, 103.5),
        ("Chia ra: - Miền Bắc", "1000 ha", 73.9, 86.6, 117.1),
        ("- Miền Nam", "1000 ha", 1807.1, 1861.0, 103.0),
        ("Trong đó: Đồng bằng sông Cửu Long", "1000 ha", 1495.3, 1535.4, 102.7),
        ("Thu hoạch lúa mùa miền Nam", "1000 ha", 647.0, 604.9, 93.5),
        ("Trong đó: Đồng bằng sông Cửu Long", "1000 ha", 265.6, 208.1, 78.4),
        ("Gieo trồng màu lương thực", "1000 ha", 298.1, 264.7, 88.8),
        ("Trong đó: - Ngô", "1000 ha", 206.2, 186.6, 90.5),
        ("- Khoai lang", "1000 ha", 69.4, 55.7, 80.2),
        ("Gieo trồng cây công nghiệp ngắn ngày", "1000 ha", 127.2, 132.9, 104.5),
        ("Trong đó: - Đậu tương", "1000 ha", 77.2, 84.7, 109.8),
        ("- Lạc", "1000 ha", 30.3, 28.4, 93.9),
        ("Gieo trồng rau, đậu các loại", "1000 ha", 226.6, 253.6, 111.9)
    ]
    
    for row in data:
        item_raw = row[0]
        unit = "1000_ha"
        val_2011 = row[3]
        yoy = row[4]
        
        # Item mapping
        sector = "Cultivation"
        metric = "Area_Planted"
        
        if "Thu hoạch" in item_raw: metric = "Area_Harvested"
        
        loc_map = "Cả nước"
        if "Miền Bắc" in item_raw: loc_map = "Miền Bắc"
        elif "Miền Nam" in item_raw: loc_map = "Miền Nam"
        elif "Đồng bằng sông Cửu Long" in item_raw: loc_map = "Đồng bằng sông Cửu Long"
        elif "Ngô" in item_raw or "Khoai lang" in item_raw or "Đậu tương" in item_raw or "Lạc" in item_raw: loc_map = "Miền Bắc" # Not explicitly stated, BUT PL2 title says "CÁC TỈNH MIỀN BẮC".
        # WAIT. PL1 items 3, 4, 5 typically refer to "Miền Bắc" in Winter (Vu Dong). 
        # Footnote (**): "Miền Bắc bao gồm cả cây vụ đông 2010/11."
        # Item 3: "Gieo trồng màu lương thực(**)" -> Asterisk implies North.
        # Item 4: "Gieo trồng cây công nghiệp ngắn ngày(**)" -> Asterisk implies North.
        # Item 5: "Gieo trồng rau, đậu các loại(**)" -> Asterisk implies North.
        # So Items 3, 4, 5 are for "Miền Bắc".
        
        if item_raw.startswith("Chia ra:"): item_raw = item_raw.replace("Chia ra:", "").strip()
        if item_raw.startswith("-"): item_raw = item_raw.replace("-", "").strip()
        if item_raw.startswith("Trong đó:"): item_raw = item_raw.replace("Trong đó:", "").strip()
        
        # Determine Commodity
        cmd = "Lúa"
        sub = "Đông Xuân"
        
        if "lúa mùa" in item_raw.lower(): sub = "Mùa"
        elif "ngô" in item_raw.lower(): cmd = "Ngô"; sub = None
        elif "khoai lang" in item_raw.lower(): cmd = "Khoai lang"; sub = None
        elif "màu lương thực" in item_raw.lower(): cmd = "Màu lương thực"; sub = None
        elif "cây công nghiệp ngắn ngày" in item_raw.lower(): cmd = "Cây công nghiệp ngắn ngày"; sub = None
        elif "đậu tương" in item_raw.lower(): cmd = "Đậu tương"; sub = None
        elif "lạc" in item_raw.lower(): cmd = "Lạc"; sub = None
        elif "rau, đậu các loại" in item_raw.lower(): cmd = "Rau đậu các loại"; sub = None
        
        # Assign Location Correctly
        if cmd == "Lúa" and sub == "Đông Xuân":
            if "Miền Bắc" in item_raw: loc_map = "Miền Bắc"
            elif "Miền Nam" in item_raw or "Đồng bằng sông Cửu Long" in item_raw: pass # Handled
            else: loc_map = "Cả nước"
        elif cmd == "Lúa" and sub == "Mùa":
            loc_map = "Miền Nam" if "miền Nam" in item_raw else "Đồng bằng sông Cửu Long"
        else: # Items 3,4,5
             loc_map = "Miền Bắc"
             
        # Add record
        comp = {"comparison_type": "YoY", "comparison_value": float(yoy)} if yoy is not None else None
        
        records.append(create_record(metadata, t, loc_map, "Regional" if loc_map != "Cả nước" else "National", {"sector": sector, "commodity": cmd, "sub_item": sub}, {"attribute": metric, "value": float(val_2011), "unit": unit, "data_type": "Actual"}, comp))
        
    return records

def parse_pl2():
    # Northern Provinces Winter/Spring Crop
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL2", "source_file": "2011_01_Phuluc_01_2011_PL2.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-15"}
    
    # Structure from Step 443
    # [Name, DT Lua DX, DT Mau LT, Ngo, Khoai Lang, San, Cay Khac]
    # Unit: ha (Header: "Đơn vị tính: ha") -> Need to convert to 1000_ha? Or keep ha? 
    # Usually datasets normalize to 1000_ha. But here values are small (3,207 ha).
    # Let's check PL1 line for Mien Bac.
    # PL1: Mien Bac Lua DX = 86.6 (1000 ha) = 86,600 ha.
    # PL2: Mien Bac Total Lua DX = 86,558 ha. Matches perfectly!
    # So unit is ha -> Convert to 1000_ha for consistency.
    
    # Transcription
    data = [
        ["Miền Bắc", 86558, 237953, 155782, 51306, 30464, 400],
        ["ĐB sông Hồng", 3207, 73215, 55570, 17445, 0, 200],
        ["Hà Nội", None, 17638, 13428, 4210, None, None],
        ["Hải Phòng", None, 3263, 2151, 1112, None, None],
        ["Vĩnh Phúc", 2847, 15237, 12776, 2261, None, 200],
        ["Bắc Ninh", None, 2373, 1568, 805, None, None],
        ["Hải Dương", None, 2540, 2540, None, None, None],
        ["Hưng Yên", None, 6000, 5000, 1000, None, None],
        ["Hà Nam", None, 4298, 3902, 396, None, None], # Note: "3902<br>2,336" in Ngo col. Wait.
        # Line 27: col 3 (Mau LT) "4,298". Col 4 (Ngo) "3902<br>2,336". And Khoai col "396".
        # This implies compacted data or error. 
        # Check Total (4298) = Ngo (3902) + Khoai (396). 3902 + 396 = 4298. Perfect.
        # So what is "2,336"? Maybe "Ngô đông"?
        # But cell format <br> implies multi-line.
        # Given Total match, I take 3902.
        ["Nam Định", None, 3275, 3275, 939, None, None], # Total 3275. Ngo 3275 + Khoai 939 = 4214 > Total?
        # Re-read Step 443 Line 28: "|Nam Định||3,275|3,275|939|||"
        # 3275 Mau LT. 3275 Ngo. 939 Khoai. Sum > Total? Unreasonable.
        # Is "3,275" a typo in Total? Or is "3,275" repeated?
        # Maybe Ngo is subset.
        # Let's assume input numbers are correct as transcribed.
        ["Thái Bình", None, 9930, 6950, 2980, None, None],
        ["Ninh Bình", 110, 5338, 3331, 2007, None, None],
        ["Quảng Ninh", 250, 3323, 1588, 1735, None, None],
        ["TD và MN phía Bắc", 1925, 66817, 42535, 16493, 7589, 200],
        ["Hà Giang", None, 720, 720, None, None, None],
        ["Cao Bằng", None, 223, 151, 72, None, None],
        ["Lào Cai", None, 588, 412, 176, None, None],
        ["Bắc Cạn", None, 429, 387, 42, None, None],
        ["Lạng Sơn", None, 0, None, None, None, None],
        ["Tuyên Quang", 27, 7589, 5011, 2578, None, None],
        ["Yên Bái", None, 7413, 6513, 900, None, None],
        ["Thái Nguyên", None, 11093, 6886, 4207, None, None],
        ["Phú Thọ", 723, 21720, 12323, 1608, 7589, 200],
        ["Bắc Giang", 280, 12000, 7000, 5000, None, None],
        ["Lai Châu", 640, 200, 200, None, None, None],
        ["Điện Biên", 220, 18, 18, None, None, None],
        ["Sơn La", 35, 550, 550, None, None, None],
        ["Hoà Bình", None, 4274, 2364, 1910, None, None],
        ["Bắc Trung Bộ", 81426, 97920, 57677, 17368, 22875, 0],
        ["Thanh Hoá", 10086, 43134, 20188, 6446, 16500, None],
        ["Nghệ An", 4000, 33657, 27047, 6610, None, None],
        ["Hà Tĩnh", 22540, 8009, 4777, 3232, None, None],
        ["Quảng Bình", 20800, 3900, 3900, None, None, None],
        ["Quảng Trị", 17000, 7000, 1500, 500, 5000, None],
        ["Thừa Thiên Huế", 7000, 2220, 265, 580, 1375, None]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        # [Name, DT Lua DX, DT Mau LT, Ngo, Khoai Lang, San, Cay Khac]
        # Lua DX
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

def parse_pl3():
    # Northern Industrial Crops & Veg
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL3", "source_file": "2011_01_Phuluc_01_2011_PL3.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-15"}
    
    # Structure from Step 444:
    # [Name, Total CCN, Dau Tuong, Lac, Thuoc La, Rau Dau Cac Loai(Col 6?)]
    # Note Col 5 "thuốc lá", Col 6 "thuốc lá" in visual table Step 444 Line 16 (Header repeated error?).
    # Line 16: "|DT cây CN<br>ngắn ngày|Đậu tương|Lạc|thuốc lá|thuốc lá|"
    # Line 17 (Data): "|94,179|84,075|9,231|873|140,459|"
    # 140,459 is huge compared to 873. Must be Rau Dau.
    # Header Line 14: "|Col1|DT cây CN|...|Col6|Rau đậu các<br>loại|"
    # So Col 6 is Rau Dau. Col 5 is Thuoc La.
    
    # Unit: ha (Implied from PL2 context, usually these appendices share units for provinces)
    
    data = [
        ["Miền Bắc", 94179, 84075, 9231, 873, 140459],
        ["ĐB sông Hồng", 75095, 73270, 1525, 300, 79719],
        ["Hà Nội", 31124, 30519, 605, None, 12125],
        ["Hải Phòng", 300, None, None, 300, 8559],
        ["Vĩnh Phúc", 4015, 3539, 476, None, 3628],
        ["Bắc Ninh", 1314, 1309, 5, None, 4387],
        ["Hải Dương", 162, 162, None, None, 16306],
        ["Hưng Yên", 2008, 1900, 108, None, 4697],
        ["Hà Nam", 11243, 11201, 42, None, 1848],
        ["Nam Định", 1377, 1377, None, None, 7967],
        ["Thái Bình", 13250, 13250, None, None, 12000],
        ["Ninh Bình", 10272, 9998, 274, None, 4530],
        ["Quảng Ninh", 30, 15, 15, None, 3672],
        ["TD và MN phía Bắc", 4452, 2305, 1582, 565, 27986],
        ["Hà Giang", 0, None, None, None, 3105],
        ["Cao Bằng", 0, None, None, None, 430],
        ["Lào Cai", 0, None, None, None, 2195],
        ["Bắc Cạn", 0, None, None, None, 199],
        ["Lạng Sơn", 565, None, None, 565, 210],
        ["Tuyên Quang", 756, 709, 47, None, 1311],
        ["Yên Bái", 0, None, None, None, 1558],
        ["Thái Nguyên", 177, 56, 121, None, 4487],
        ["Phú Thọ", 1007, 951, 56, None, 3285],
        ["Bắc Giang", 1373, 15, 1358, None, 7500],
        ["Lai Châu", 20, 20, None, None, 307],
        ["Điện Biên", 47, 47, None, None, 125],
        ["Sơn La", 0, None, None, None, 1374],
        ["Hoà Bình", 507, 507, None, None, 1900],
        ["Bắc Trung Bộ", 14632, 8500, 6124, 8, 32754],
        ["Thanh Hoá", 10221, 8500, 1721, None, 16794],
        ["Nghệ An", 1700, None, 1700, None, 9244],
        ["Hà Tĩnh", 0, None, None, None, 4455],
        ["Quảng Bình", 0, None, None, None, 456],
        ["Quảng Trị", 2600, None, 2600, None, 1010],
        ["Thừa Thiên Huế", 111, None, 103, 8, 795]
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/01"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl1()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl2()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl3()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL3.json"))
    print("Successfully parsed PL1-PL3 for January 2011 (Cultivation North).")
