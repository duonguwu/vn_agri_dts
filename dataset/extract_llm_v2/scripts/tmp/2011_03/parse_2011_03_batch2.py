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
        "D.H Nam Tr. Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
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

def parse_pl4():
    # Southern Rice (DX, HT) & Crops (PL4)
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL4", "source_file": "2011_03_Phuluc_03_2011_PL4.md"}
    records = []
    t = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-15"}
    
    # [Name, Lua DX Planted, Lua DX Harv, Lua HT Harvested(Col3 in View?), Mau Total, Ngo, Khoai, San, Cay khac]
    # Header: |Vùng/Tỉnh|Lúa đông xuân (Gieo cấy)|Lúa đông xuân (Thu hoạch)|Gieo cấy lúa hè thu (Diện tích thu hoạch?? Check logic)|...
    # Wait, Col 4 Header says "Gieo cấy lúa hè thu" then subheader "Diện tích thu hoạch".
    # Logic: March 15th. Summer-Autumn (Hè Thu) usually starts planting. Harvest is unlikely unless very early?
    # Or is it "Diện tích gieo cấy"? View says "Diện tích thu hoạch" for Col 4. 
    # But checking PL1: "3. Gieo cấy lúa hè thu ở ĐBSCL". 
    # So Col 4 is likely "Area Planted" for Summer-Autumn Rice. Let's assume Typo in subheader (very common in these reports).
    # View Step 547, Line 22: "Gieo cấy lúa hè thu". Line 23: "Diện tích thu hoạch". 
    # Value for Mien Nam: 197,527. PL1 says "3. Gieo cấy lúa hè thu ở ĐBSCL: 197.5". Matches.
    # So Col 4 is **Area Planted** for Hè Thu.
    
    data = [
        ["Miền Nam", 1978295, 1016255, 197527, 152506, 64038, 13878, 65234, 9356],
        ["D.H Nam Tr. Bộ", 176220, 7875, None, 51126, 15068, 3650, 31553, 855],
        ["TP Đà Nẵng", 3479, None, None, 853, 332, 220, 301, None],
        ["Quảng Nam", 42780, None, None, 19410, 5910, 3100, 10200, 200],
        ["Quảng Ngãi", 36763, None, None, 15830, 4500, 150, 11180, None],
        ["Bình Định", 47568, 2925, None, 2262, 2262, None, None, None],
        ["Phú Yên", 26222, None, None, 8541, 2064, 180, 6212, 85],
        ["Khánh Hoà", 19408, 4950, None, 4230, None, None, 3660, 570],
        ["Tây Nguyên", 76864, 549, None, 20535, 12480, 2346, 5710, None],
        ["Kon Tum", 6583, None, None, 636, 636, None, None, None],
        ["Gia Lai", 24409, None, None, 10122, 4587, 431, 5105, None],
        ["Đắc Lắc", 30594, 549, None, 4462, 3165, 692, 605, None],
        ["Đắc Nông", 4428, None, None, 3722, 2753, 969, None, None],
        ["Lâm Đồng", 10850, None, None, 1593, 1339, 254, None, None],
        ["Đông Nam Bộ", 117475, 16006, None, 45069, 17423, 692, 26194, 760],
        ["TP Hồ Chí Minh", 5405, 163, None, None, None, None, None, None],
        ["Ninh Thuận", 14591, 300, None, 5047, 2500, 69, 2478, None],
        ["Bình Phước", 2901, None, None, 1494, 438, 93, 832, 131],
        ["Tây Ninh", 45314, 5971, None, 22773, 2971, 127, 19388, 287],
        ["Bình Dương", 2596, 2596, None, 1541, 112, None, 1283, 146],
        ["Đồng Nai", 11306, None, None, 9413, 7267, 85, 1890, 171],
        ["Bình Thuận", 30443, 4600, None, 3650, 3026, 278, 323, 23],
        ["Bà Rịa-V.Tàu", 4919, 2376, None, 1151, 1109, 40, None, 2],
        ["ĐBS Cửu Long", 1607736, 991825, 197527, 35775, 19067, 7190, 1778, 7741],
        ["Long An", 254014, 138087, None, 8393, 4441, 48, 570, 3334],
        ["Đồng Tháp", 206941, 162336, 52038, 3046, 1998, 401, None, 647],
        ["An Giang", 235482, 78784, None, 4824, 3598, 146, 460, 620],
        ["Tiền Giang", 80351, 69458, 40300, 4015, 2584, 221, 98, 1113],
        ["Vĩnh Long", 65830, 65830, 26988, 4891, 580, 4231, 20, 60],
        ["Bến Tre", 20632, 2179, None, 400, 250, 50, 100, None],
        ["Kiên Giang", 278383, 213939, 7725, 730, None, None, None, 730],
        ["Cần Thơ", 88644, 70740, 14953, 377, 345, None, None, 32],
        ["Hậu Giang", 83040, 20317, 4104, 1057, 677, 80, None, 300],
        ["Trà Vinh", 61067, 20472, 2901, 3938, 2683, 667, 330, 258],
        ["Sóc Trăng", 138254, 94628, 48518, 3526, 1862, 1346, 200, 118],
        ["Bạc Liêu", 46329, 6287, None, 578, 49, None, None, 529],
        ["Cà Mau", 48768, 48768, None, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Tr. Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        # Lua DX Planted
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Lua DX Harvested
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Lua HT Planted
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        
        # Mau LT etc.
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl5():
    # Southern Industrial & Veg (PL5)
    # [Name, Total CN, Dau Tuong, Lac, Vung, Thuoc La, Mia, Bong, Rau, Dau]
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL5", "source_file": "2011_03_Phuluc_03_2011_PL5.md"}
    records = []
    t = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-15"}
    
    data = [
        ["Miền Nam", 168836, 3103, 38931, 12132, 9643, 101529, 862, 174730, 25786], # Note: PL5 Step 548 Val: Rau 174,730, Dau 25,786
        ["D.H Nam Trg Bộ", 48628, 506, 20595, 75, 786, 26219, 447, 25633, 25633], # View Rau=25633, Dau=25633? Similar to Jan. Check specific provinces: QNam 10690, 2000...
        # QNam Rau 10690, Dau empty in View (Line 32: 250|188|10690|| - Wait. Header order.)
        # Row 27 Header: Tong, Dau Tuong, Lac, Vung, Thuoc La, Mia, Bong (Col8), Rau (Col9), Dau (Col10).
        # Row 32 (QNam): 9258 (Tong), ||(DauTuong empty), 8370(Lac), ||(Vung), 450(ThuocLa), 250(Mia), 188(Bong), 10690(Rau?), ||(Dau?)
        # Let's map carefully.
        # QNam: Rau 10690.
        # QNgai (33): Rau 5300, Dau 1644.
        # BDinh (34): Rau 5358, Dau 871.
        # PYen (35): Rau 2348, Dau 1311.
        # KHoa (36): Rau 1467, Dau 976.
        # Sum Rau = 10690 + 5300 + 5358 + 2348 + 1467 = ~25163. Close to 25633.  Dau sum = 1644+871+1311+976 = 4702.
        # Regional Dau 25633? Mistake in Regional Row.
        # I trust Provincial data more than faulty regional summaries if evident. But will record Regional as is or correct?
        # Let's record as provided but skip if obviously duplicate or wrong?
        # The View shows "25,633" for both Rau and Dau in Line 30.
        # I will use the values from the View for provincial, and View values for Regional (even if suspicious).
        
        ["TP Đà Nẵng", 1198, None, 784, None, None, 414, None, 469, None],
        ["Quảng Nam", 9258, None, 8370, None, 450, 250, 188, 10690, None],
        ["Quảng Ngãi", 7964, None, 3990, None, None, 3975, None, 5300, 1644],
        ["Bình Định", 7147, 221, 6926, None, None, None, None, 5358, 871],
        ["Phú Yên", 9074, 285, 526, 75, 336, 7593, 259, 2348, 1311],
        ["Khánh Hoà", 13987, None, None, None, None, 13987, None, 1467, 976],
        ["Tây Nguyên", 14481, None, 118, None, 3502, 9292, 303, 25612, 4065],
        ["Kon Tum", 1769, None, 13, None, None, 1756, None, 749, 57],
        ["Gia Lai", 10942, None, 85, None, 3019, 7536, 303, 8071, 2310],
        ["Đắc Lắc", 1770, None, 20, None, 483, None, None, 2642, 933],
        ["Đắc Nông", 0, None, None, None, None, None, None, 913, 220],
        ["Lâm Đồng", 0, None, None, None, None, None, None, 13237, 545],
        ["Đông Nam Bộ", 27729, 189, 9138, 948, 5232, 12110, 112, 26641, 10402],
        ["TP Hồ Chí Minh", 2300, None, None, None, None, 2300, None, 4577, None],
        ["Ninh Thuận", 2419, None, 131, 21, 782, 1443, 42, 2720, 1366],
        ["Bình Phước", 103, 24, 41, 6, 2, 30, None, 853, 143],
        ["Tây Ninh", 15292, None, 7497, 695, 3340, 3760, None, 7609, 4325],
        ["Bình Dương", 718, None, 483, 140, None, 95, None, 1933, 122],
        ["Đồng Nai", 1885, 165, 210, 19, 936, 548, 7, 4111, 1650],
        ["Bình Thuận", 4642, None, 668, 67, 54, 3843, 10, 1648, 2678],
        ["Bà Rịa-V.Tàu", 370, None, 108, None, 118, 91, 53, 3190, 118],
        ["ĐBS Cửu Long", 77313, 2408, 9080, 11109, 123, 53909, None, 96844, 6517],
        ["Long An", 18786, None, 5118, 1016, 81, 12571, None, 7526, None],
        ["Đồng Tháp", 5790, 1690, 140, 3946, None, 14, None, 6081, 1160],
        ["An Giang", 1041, 69, 281, 628, 42, 21, None, 11488, 1817],
        ["Tiền Giang", 186, None, 83, None, None, 103, None, 19640, 76],
        ["Vĩnh Long", 955, 319, 5, 602, None, 29, None, 7740, 430],
        ["Bến Tre", 5880, None, 80, None, None, 5800, None, 1936, None],
        ["Kiên Giang", 4512, None, None, None, None, 4512, None, 2335, None],
        ["Cần Thơ", 5118, 197, 5, 4917, None, None, None, 3229, 462],
        ["Hậu Giang", 13614, None, None, None, None, 13614, None, 5732, 419],
        ["Trà Vinh", 8197, None, 3302, None, None, 4895, None, 11715, 422],
        ["Sóc Trăng", 10747, 133, 67, None, None, 10547, None, 14712, 1731],
        ["Bạc Liêu", 0, None, None, None, None, None, None, 2805, None],
        ["Cà Mau", 1803, None, None, None, None, 1803, None, 1905, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        
        if row[1] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[1])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[2] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[2])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[3] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[3])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[4] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Vừng", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[4])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[5] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[5])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Mía", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": float(row[6])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Bông", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[7])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[8] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[8])/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if row[9] is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": float(row[9])/1000, "unit": "1000_ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl4()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL4.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl5()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL5.json"))
    print("Successfully parsed PL4, PL5 for March 2011 (Cultivation South & Crops).")
