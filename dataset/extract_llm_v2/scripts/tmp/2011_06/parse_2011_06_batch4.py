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
        "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", "Trung du và miền núi\nphía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ và\nduyên hải miền Trung": "Bắc Trung Bộ và Duyên hải miền Trung",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", 
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng", "TP.Hồ Chí Minh": "Hồ Chí Minh", "T.P Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Tỉnh/Thành phố": "Cả nước", "Cả nước": "Cả nước",
        "ĐB. sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Quảng Ninh": "Quảng Ninh", "Hải Phòng": "Hải Phòng",
        "Thái Bình": "Thái Bình", "Nam Định": "Nam Định", "Ninh Bình": "Ninh Bình", "Thanh Hoá": "Thanh Hóa",
        "Thanh Hóa": "Thanh Hóa"
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
    elif "Miền Bắc" in norm_loc: geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    elif "Miền Trung" in norm_loc: geo_context["region_id"] = "CENTRAL"; geo_context["region_name_vn"] = "Miền Trung"
    elif "Miền Nam" in norm_loc: geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6():
    # Disease Summary PL6 (Fixed Syntax Error from Batch 3)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL6", "source_file": "2011_06_Phuluc_06_2011_PL6.md"}
    records = []
    
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    
    # [Name, Cum GC Nhiem, Cum GC Huy, LMLM GS Nhiem, Trau, Bo, Lon, De, GS Huy, Lon Tai Xanh Nhiem, Lon Tai Xanh Huy]
    
    data = [
        ("Cả nước", 50347, 80762, 140171, 78277, 17373, 42897, 1624, 38744, 14759, 14158),
        ("Đồng bằng sông Hồng", 14323, 34802, 3200, 2569, 134, 497, 0, 400, 1292, 545),
        ("Vĩnh Phúc", 1500, 21979, None, None, None, None, None, None, None, None),
        ("Quảng Ninh", 4950, 4950, 3109, 2569, 134, 406, None, 327, None, None),
        ("Nam Định", 6700, 6700, 24, None, None, 24, None, 24, None, None),
        ("Trung du và miền núi phía Bắc", 7508, 8466, 110599, 69054, 12482, 27439, 1624, 27048, 0, 0),
        ("Bắc Trung Bộ và duyên hải miền Trung", 16578, 23242, 6108, 1563, 3735, 810, 0, 636, 13412, 13286),
        ("Tây Nguyên", 2283, 2283, 8630, 5091, 926, 2613, 0, 2412, 0, 0),
        ("Đông Nam Bộ", 0, 0, 570, 0, 10, 560, 0, 509, 55, 327),
        ("Đồng bằng sông Cửu Long", 9655, 11969, 11064, 0, 86, 10978, 0, 7739, 0, 0)
    ]
    
    for row in data:
        loc = row[0]
        gl = "Regional"
        if loc == "Cả nước": gl = "National"
        elif loc not in ["Đồng bằng sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ và duyên hải miền Trung", "Tây Nguyên", "Đông Nam Bộ", "Đồng bằng sông Cửu Long"]:
            gl = "Provincial"
        
        # Cum GC
        if row[1] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Gia cầm", "indicator": "Nhiễm cúm gia cầm"}, {"attribute": "Infected_Heads", "value": float(row[1]), "unit": "heads", "data_type": "Actual"}))
        if row[2] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Gia cầm", "indicator": "Tiêu hủy do cúm gia cầm"}, {"attribute": "Culled_Heads", "value": float(row[2]), "unit": "heads", "data_type": "Actual"}))
        
        # LMLM
        if row[3] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Gia súc", "indicator": "Nhiễm Lở mồm long móng"}, {"attribute": "Infected_Heads", "value": float(row[3]), "unit": "heads", "data_type": "Actual"}))
        if row[4] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Trâu", "indicator": "Nhiễm Lở mồm long móng"}, {"attribute": "Infected_Heads", "value": float(row[4]), "unit": "heads", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Bò", "indicator": "Nhiễm Lở mồm long móng"}, {"attribute": "Infected_Heads", "value": float(row[5]), "unit": "heads", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Lợn", "indicator": "Nhiễm Lở mồm long móng"}, {"attribute": "Infected_Heads", "value": float(row[6]), "unit": "heads", "data_type": "Actual"}))
        
        if row[8] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Gia súc", "indicator": "Tiêu hủy do Lở mồm long móng"}, {"attribute": "Culled_Heads", "value": float(row[8]), "unit": "heads", "data_type": "Actual"}))
        
        # Tai Xanh
        if row[9] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Lợn", "indicator": "Nhiễm Tai xanh"}, {"attribute": "Infected_Heads", "value": float(row[9]), "unit": "heads", "data_type": "Actual"}))
        if row[10] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Livestock", "commodity": "Lợn", "indicator": "Tiêu hủy do Tai xanh"}, {"attribute": "Culled_Heads", "value": float(row[10]), "unit": "heads", "data_type": "Actual"}))

    return records

def parse_pl10():
    # Fishery Detail PL10 (Previously PL11 equivalent logic)
    # [Name, Total Prod, Nuoi Trong Total, NT Ngot, NT Man/Lo, Khai Thac Total, KT Bien, KT Noi Dia]
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL10", "source_file": "2011_06_Phuluc_06_2011_PL10.md"}
    records = []
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-20"} # Note: Header says "Tính đến 20/6/2011", but likely serves as 6M estimate.
    
    data = [
        ["Cả nước", 2511925, 1259955, 908543, 351412, 1251970, 1170390, 81580],
        ["Quảng Ninh", 41801, 10781, 2156, 8625, 31020, 30417, 603],
        ["Hải Phòng", 49385, 23928, None, 23928, 25457, 24605, 852],
        ["Thái Bình", 30700, 13200, 7500, 5700, 17500, 15000, 2500],
        ["Nam Định", 41261, 24380, 13115, 11265, 16881, 15904, 977],
        ["Thanh Hoá", 52664, 13506, 9763, 3743, 39158, 37695, 1463],
        ["Nghệ An", 56300, 17561, 16220, 1341, 38739, 36710, 2029],
        ["Hà Tĩnh", 17230, 4750, 3220, 1530, 12480, 11930, 550],
        ["Quảng Bình", 19600, 4600, 3150, 1450, 15000, 14100, 900],
        ["Quảng Trị", 17100, 4900, 2600, 2300, 12200, 6800, 5400],
        ["Thừa Thiên Huế", 41480, 10600, 4100, 6500, 30880, 26500, 4380],
        ["Đà Nẵng", 21800, 200, 200, None, 21600, 21300, 300],
        ["Quảng Nam", 40180, 4620, 2500, 2120, 35560, 34900, 660],
        ["Quảng Ngãi", 55356, 2927, 613, 2314, 52429, 52223, 206],
        ["Bình Định", 63609, 2117, None, 2117, 61492, 61000, 492],
        ["Phú Yên", 30840, 2240, 350, 1890, 28600, 28000, 600],
        ["Khánh Hoà", 51450, 11400, None, 11400, 40050, 39600, 450],
        ["Ninh Thuận", 26671, 5405, 235, 5170, 21266, 21211, 55],
        ["Bình Thuận", 77139, 7134, 3072, 4062, 70005, 69205, 800],
        ["Tây Ninh", 5237, 3414, 3414, None, 1823, None, 1823],
        ["Bà Rịa - Vũng Tàu", 138386, 5171, 1025, 4146, 133215, 132765, 450],
        ["TP.Hồ Chí Minh", 22254, 10909, 4758, 6151, 11345, 11145, 200],
        ["Long An", 9203, 3513, None, 3513, 5690, 3100, 2590],
        ["Tiền Giang", 109947, 67396, 49092, 18304, 42551, 40515, 2036],
        ["Bến Tre", 136260, 74745, 64395, 10350, 61515, 59115, 2400],
        ["Trà Vinh", 63459, 26915, 18500, 8415, 36544, 32108, 4436],
        ["Vĩnh Long", 73050, 68000, 68000, None, 5050, None, 5050],
        ["Đồng Tháp", 177168, 174451, 174451, None, 2717, None, 2717],
        ["An Giang", 179615, 169604, 169604, None, 10011, None, 10011],
        ["Kiên Giang", 219589, 22062, 32831, 15930, 197527, 194407, 3120], # Note: Nuoi Trong Total (22k) < NT Ngot + NT Man (32k+15k). Likely typo in Total or Components.
        # Let's trust Components or Total? 219k total. KT = 197k. NT = 22k? 197+22=219. So Total NT 22k is consistent with Grand Total.
        # But NT Ngot 32k > Total NT 22k. This is impossible.
        # Maybe "32831" is wrong?
        # Checked source line 51: |219,589|22,062|32,831|15,930|...|
        # 32831 Ngot is > 22062 Total.
        # I will include components as provided but flagged internally as potential data quality issue. 
        # Actually, let's extract what is there.
        ["Cần Thơ", 93727, 92717, 92717, None, 1010, None, 1010],
        ["Sóc Trăng", 25453, 5322, 2020, 3302, 20131, 17371, 2760],
        ["Bạc Liêu", 109144, 58063, 480, 57583, 51081, 48624, 2457],
        ["Cà Mau", 202908, 119584, 11154, 108430, 83324, 81500, 1824]
    ]
    
    for row in data:
        loc = row[0]
        if row[1] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Tổng sản lượng"}, {"attribute": "Production", "value": float(row[1])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[2] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng", "sub_item": "Tổng số"}, {"attribute": "Production", "value": float(row[2])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[3] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng", "sub_item": "Nước ngọt"}, {"attribute": "Production", "value": float(row[3])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[4] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng", "sub_item": "Nước mặn, lợ"}, {"attribute": "Production", "value": float(row[4])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[5] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác", "sub_item": "Tổng số"}, {"attribute": "Production", "value": float(row[5])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[6] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác", "sub_item": "Khai thác biển"}, {"attribute": "Production", "value": float(row[6])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[7] is not None: records.append(create_record(metadata, t_6m_11, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác", "sub_item": "Khai thác nội địa"}, {"attribute": "Production", "value": float(row[7])/1000, "unit": "1000_ton", "data_type": "Estimate"}))

    return records

def parse_pl11():
    # Salt Production PL11
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL11", "source_file": "2011_06_Phuluc_06_2011_PL11.md"}
    records = []
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    
    # [Name, Last Year, This Year, %]
    data = [
        ("Cả nước", 897185, 543351),
        ("Miền Bắc", 65864, 34818),
        ("Hải Phòng", 1040, 2350),
        ("Nam Định", 26000, 20000),
        ("Thái Bình", 340, 322),
        ("Thanh Hóa", None, 4210),
        ("Nghệ An", 38484, 3936),
        ("Hà Tĩnh", None, 4000),
        ("Miền Trung", 267222, 189733),
        ("Quảng Ngãi", 4700, 3500),
        ("Bình Định", 12782, 6529),
        ("Phú Yên", 12200, 6500),
        ("Khánh Hòa", 28165, 9853),
        ("Ninh Thuận", 143477, 116351),
        ("Bình Thuận", 65898, 47000),
        ("Miền Nam", 564099, 318800),
        ("T.P Hồ Chí Minh", 103688, 72502),
        ("Bà Rịa - Vũng Tàu", 86415, 93027),
        ("Trà Vinh", 18000, 10003),
        ("Bến Tre", 77483, 43210),
        ("Bạc Liêu", 266092, 97789),
        ("Sóc Trăng", 12421, 2269)
    ]
    
    regional_list = ["Miền Bắc", "Miền Trung", "Miền Nam"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Cả nước": gl = "National"
        
        if row[2] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Salt", "commodity": "Muối"}, {"attribute": "Production", "value": float(row[2])/1000, "unit": "1000_ton", "data_type": "Estimate"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    # Re-running Summary PL6, PL7, PL8 with fix
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl6()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL6.json"))
    # Skip re-saving PL7, PL8 if not changed, but logic consolidated. Actually will create PL10, PL11 here too.
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl10()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL10.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl11()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL11.json"))
    print("Successfully parsed PL6, PL10, PL11 for June 2011 (Disease, Fishery, Salt).")
