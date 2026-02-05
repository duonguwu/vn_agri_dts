import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
    REGION_DATA = json.load(f)

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    # Standardize commas and dots. In these reports: 1.234,5 -> 1234.5; 1,234.5 -> 1234.5
    if "." in s and "," in s:
        # Check layout: 1.234,5 is likely VN. 1,234.5 is likely EN?
        # Agricultural data in VN reports usually use dot for thousands and comma for decimal.
        # But MD often flips them or uses them inconsistently.
        # Let's check the number of digits.
        if s.find(".") < s.find(","): # 1.234,5
            s = s.replace(".", "").replace(",", ".")
        else: # 1,234.5
            s = s.replace(",", "")
    elif "," in s:
        # If one comma, check if it's thousands or decimal. 
        # In April files, 1,123,474 (PL2a line 25) uses commas for thousands.
        # But 90.2 (PL2b line 35) uses dots. 
        # Wait, look at PL1 line 14: 1,653.2. This is thousands comma and decimal dot!
        # This is unusual for VN but common in OCR.
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "") # Thousands
            else: s = s.replace(",", ".") # Decimal
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
        else:
            # 699.3 (PL1 line 12) is decimal.
            # 1.534,3 (PL1 line 15) -> dot is thousands.
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
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ"
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

def parse_pl1_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL1", "source_file": "2010_04_Phuluc_T04_2010_PL1.md"}
    records = []
    t10 = {"year": 2010, "month": 4, "period_type": "Monthly", "report_date": "2010-04-15"}
    t09 = {"year": 2009, "month": 4, "period_type": "Monthly", "report_date": "2009-04-15"}
    
    # Rows: Name, Loc, V09, V10, Attr, Cmd, Sub
    data = [
        ["Gieo cấy lúa hè thu miền Nam", "Miền Nam", 441.2, 699.3, "Area_Planted", "Lúa", "Hè Thu"],
        ["Đồng bằng sông Cửu Long", "Đồng bằng sông Cửu Long", 414.2, 670.3, "Area_Planted", "Lúa", "Hè Thu"],
        ["Thu hoạch lúa đông xuân miền Nam", "Miền Nam", 1653.2, 1745.7, "Area_Harvested", "Lúa", "Đông Xuân"],
        ["Đồng bằng sông Cửu Long", "Đồng bằng sông Cửu Long", 1480.2, 1534.3, "Area_Harvested", "Lúa", "Đông Xuân"],
        ["Gieo trồng màu lương thực", "Cả nước", 745.4, 734.5, "Area_Planted", "Màu lương thực", "Tổng số"],
        ["Ngô", "Cả nước", 477.9, 459.2, "Area_Planted", "Ngô", None],
        ["Khoai lang", "Cả nước", 86.8, 93.3, "Area_Planted", "Khoai lang", None],
        ["Sắn", "Cả nước", 159.2, 157.1, "Area_Planted", "Sắn", None],
        ["Gieo trồng cây công nghiệp PN", "Cả nước", 352.5, 374.2, "Area_Planted", "Cây công nghiệp ngắn ngày", "Tổng số"],
        ["Đậu tương", "Cả nước", 102.3, 128.6, "Area_Planted", "Đậu tương", None],
        ["Lạc", "Cả nước", 172.2, 166.8, "Area_Planted", "Lạc", None],
        ["Thuốc lá, thuốc lào", "Cả nước", 22.4, 23.3, "Area_Planted", "Thuốc lá", None],
        ["Gieo trồng rau, đậu các loại", "Cả nước", 432.0, 459.1, "Area_Planted", "Rau đậu các loại", "Tổng số"],
    ]
    for r in data:
        loc, v09, v10, attr, cmd, sub = r[1], r[2], r[3], r[4], r[5], r[6]
        gl = "National" if loc in ["Cả nước", "Miền Nam", "Miền Bắc"] else "Regional"
        records.append(create_record(metadata, t10, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))
        records.append(create_record(metadata, t09, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v09), "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2a_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL2a", "source_file": "2010_04_Phuluc_T04_2010_PL2a.md"}
    records = []
    t = {"year": 2010, "month": 4, "period_type": "Monthly", "report_date": "2010-04-15"}
    
    # Rows: loc, ldx_gc, total_màu, ngo, khoai, san, cay_khac
    data_2a = [
        ["Miền Bắc", 1123474, 374331, 214018, 25819, 106021, 28728],
        ["ĐB sông Hồng", 560912, 56648, 27929, 7232, 4332, 11864],
        ["Hà Nội", 99870, 11717, 7217, 3000, 1300, 200],
        ["Hải Phòng", 39204, 2670, 170, None, None, 2500],
        ["Vĩnh Phúc", 30975, 6547, 2391, 299, 1722, 2135],
        ["Bắc Ninh", 36882, 1819, 1235, None, None, 584],
        ["Hải Dương", 63360, 7391, 1200, 900, None, None],
        ["Hưng Yên", 38500, 3068, 3068, None, None, None],
        ["Hà Nam", 34370, 3228, 3228, None, None, None],
        ["Nam Định", 77600, 6250, 1450, None, 300, 4500],
        ["Thái Bình", 81500, 4045, 2100, None, None, 1945],
        ["Ninh Bình", 41603, 1245, 1170, 75, None, None],
        ["Quảng Ninh", 17049, 8668, 4699, 2959, 1010, None],
        ["Trung du và MN phía Bắc", 224195, 207212, 138168, 6831, 55657, 6955],
        ["Hà Giang", 9074, 25662, 25662, None, None, None],
        ["Cao Bằng", 2300, 11756, 11561, None, None, 195],
        ["Lào Cai", 8847, 18826, 14509, 400, 4317, None],
        ["Bắc Cạn", 7270, 9525, 7980, 154, 1144, 247],
        ["Lạng Sơn", 6824, 11637, 9664, None, None, 1973],
        ["Tuyên Quang", 19492, 7333, 6933, 400, None, None],
        ["Yên Bái", 17438, 21070, 7996, 778, 11779, 517],
        ["Thái Nguyên", 27974, 10397, 6069, 1398, 2930, None],
        ["Phú Thọ", 35506, 6900, 5722, 391, 585, 202],
        ["Bắc Giang", 51259, 5234, 1470, 1564, 2200, None],
        ["Lai Châu", 5414, 13766, 8875, None, 4891, None],
        ["Điện Biên", 7862, 8500, 4500, None, 4000, None],
        ["Sơn La", 8973, 26005, 11180, 82, 12500, 2243],
        ["Hoà Bình", 15962, 30601, 16047, 1665, 11311, 1578],
        ["Bắc Trung Bộ", 338367, 110471, 47921, 11756, 46032, 9909],
        ["Thanh Hoá", 120198, 34409, 20000, 4500, 9200, 709],
        ["Nghệ An", 86500, 37190, 17400, 2340, 16950, 500],
        ["Hà Tĩnh", 53108, 5179, 2426, None, None, 2750],
        ["Quảng Bình", 27646, 13258, 4110, 1416, 5782, 1950],
        ["Quảng Trị", 23763, 12185, 2185, None, 8000, 2000],
        ["Thừa Thiên Huế", 27152, 8250, 1800, 3500, 6100, 2000],
    ]
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data_2a:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+3])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2b_2010_04():
    metadata = {"year": 2010, "month": 4, "appendix_number": "PL2b", "source_file": "2010_04_Phuluc_T04_2010_PL2b.md"}
    records = []
    t = {"year": 2010, "month": 4, "period_type": "Monthly", "report_date": "2010-04-15"}
    
    # Rows: loc, dx_gc, dx_th, dx_th_p, ht_gc, mau_total, ngo, khoai, san, khac
    data_2b = [
        ["Miền Nam", 1935918, 1745686, 90.2, 699253, 134490, 67141, 9930, 51065, 6354],
        ["D.H Nam Trung Bộ", 186308, 97432, 52.3, 19830, 42864, 16196, 2452, 24216, None],
        ["TP Đà Nẵng", 4000, 54, 1.4, None, 853, 323, 268, 262, None],
        ["Quảng Nam", 52912, 9700, 18.3, None, 15995, 5960, 115, 9920, None],
        ["Quảng Ngãi", 36664, 9057, 24.7, None, 9841, 4920, 1900, 3021, None],
        ["Bình Định", 47421, 42741, 90.1, 19830, 9869, 1877, None, 7992, None],
        ["Phú Yên", 25931, 16500, 63.6, None, 5266, 2076, 169, 3021, None],
        ["Khánh Hoà", 19380, 19380, 100.0, None, 1040, 1040, None, None, None],
        ["Tây Nguyên", 74161, 21772, 29.4, 1168, 18294, 11659, 1735, 4900, None],
        ["Kon Tum", 6583, None, None, None, 606, 606, None, None, None],
        ["Gia Lai", 23998, 4799, 20.0, None, 9040, 4417, 340, 4283, None],
        ["Đắc Lắc", 29019, 10064, 34.7, None, 4181, 2938, 626, 617, None],
        ["Đắc Nông", 3853, 1046, 27.1, None, 3482, 2713, 769, None, None],
        ["Lâm Đồng", 10708, 5863, 54.8, 1168, 985, 985, None, None, None],
        ["Đông Nam Bộ", 114037, 92197, 80.8, 7999, 44188, 19652, 365, 20469, 3702],
        ["TP Hồ Chí Minh", 6637, 3111, 46.9, None, 774, 774, None, None, None],
        ["Ninh Thuận", 13104, 7173, 54.7, None, 2264, 2264, None, None, None],
        ["Bình Phước", 2897, 2897, 100.0, None, 989, 526, 149, 314, None],
        ["Tây Ninh", 45247, 39360, 87.0, 7999, 24094, 3745, None, 17058, 3291],
        ["Bình Dương", 2546, 1700, 66.8, None, 1927, 141, 171, 1204, 411],
        ["Đồng Nai", 14565, 9921, 68.1, None, 9593, 8055, None, 1538, None],
        ["Bình Thuận", 23787, 22781, 95.8, None, 3399, 3115, None, 284, None],
        ["Bà Rịa-V.Tàu", 5254, 5254, 100.0, None, 1148, 1032, 45, 71, None],
        ["ĐBS Cửu Long", 1561412, 1534285, 98.3, 670256, 29144, 19634, 5378, 1480, 2652],
        ["Long An", 251025, 251025, 100.0, 63691, 4654, 4654, None, None, None],
        ["Đồng Tháp", 207672, 207672, 100.0, 125956, 4035, 2409, 642, None, 984],
        ["An Giang", 234212, 232185, 99.1, 128052, 3030, 2910, 30, 90, None],
        ["Tiền Giang", 82272, 82272, 100.0, 40064, 4418, 2760, None, 200, 1458],
        ["Vĩnh Long", 66902, 66920, 100.0, 52032, 3292, 660, 2484, 148, None],
        ["Bến Tre", 20812, 18324, 88.0, None, 777, 375, 64, 128, 210],
        ["Kiên Giang", 284145, 280925, 98.9, 58400, None, None, None, None, None],
        ["Cần Thơ", 89673, 89673, 100.0, 72391, 387, 387, None, None, None],
        ["Hậu Giang", 84504, 84263, 99.7, 34661, 1291, 1291, None, None, None],
        ["Trà Vinh", 55916, 53310, 95.3, 18060, 4719, 3173, 880, 666, None],
        ["Sóc Trăng", 139648, 138500, 99.2, 71244, 2541, 1015, 1278, 248, None],
        ["Bạc Liêu", 44631, 29216, 65.5, 5705, None, None, None, None, None],
    ]
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data_2b:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        v = normalize_number(row[5])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây có củ khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+6])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl1_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl2a_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL2a.json"))
    save_json({"metadata": {"year": 2010, "month": 4}, "records": parse_pl2b_2010_04()}, os.path.join(out_dir, "2010_04_Phuluc_T04_2010_PL2b.json"))
    print("Successfully parsed PL1, PL2a, PL2b for April 2010.")
