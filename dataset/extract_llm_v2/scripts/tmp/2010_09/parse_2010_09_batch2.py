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
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế"
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
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl4():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL4", "source_file": "2010_09_phuluc_T09_2010_PL4.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Monthly", "report_date": "2010-09-15"}
    
    # [Loc, HT_Planted, HT_Harvested, Mua_Planted, Mau_Total, Ngo, Khoai, San]
    # Note: Col 4 is Mua_Planted (verified with PL1)
    data = [
        ["Miền Nam", 2082831, 1756726, 454911, 617158, 294397, 22811, 299950],
        ["D.H Nam Trung Bộ", 140353, 116096, 67999, 98356, 28163, 7234, 62959],
        ["TP Đà Nẵng", 3300, None, None, 1118, 578, 450, 90],
        ["Quảng Nam", 43049, 26000, 40211, 24504, 7104, 4500, 12900],
        ["Quảng Ngãi", 32256, 32256, 500, 24855, 4160, 1900, 18795],
        ["Bình Định", 21908, 18000, 22788, 19600, 6711, None, 12889],
        ["Phú Yên", 23840, 23840, 4500, 19170, 5610, 275, 13285],
        ["Khánh Hoà", 16000, 16000, None, 9109, 4000, 109, 5000],
        ["Tây Nguyên", 6489, 6489, 147097, 288257, 158183, 7359, 122715],
        ["Kon Tum", None, None, 15407, 43802, 6475, 137, 37190],
        ["Gia Lai", None, None, 38547, 85155, 39773, 752, 44630],
        ["Đắc Lắc", None, None, 44935, 98840, 73900, 1874, 23066],
        ["Đắc Nông", None, None, 33110, 40156, 21400, 3340, 15416],
        ["Lâm Đồng", 6489, 6489, 15098, 20304, 16635, 1256, 2413],
        ["Đông Nam Bộ", 169060, 156884, 86932, 187365, 73897, 1742, 111726],
        ["TP Hồ Chí Minh", 6531, 6531, 7571, 1007, 1007, None, None],
        ["Ninh Thuận", 11080, 11080, 7000, 6563, 6459, 104, None],
        ["Bình Phước", 14000, 14000, 9000, 30381, 5981, 900, 23500],
        ["Tây Ninh", 63642, 63642, 41549, 46223, 7800, None, 38423],
        ["Bình Dương", 2069, 2069, 1336, 4167, 155, 171, 3841],
        ["Đồng Nai", 25367, 18900, 1700, 37797, 25098, 133, 12566],
        ["Bình Thuận", 38709, 33000, 7987, 36427, 10797, 234, 25396],
        ["Bà Rịa-V.Tàu", 7662, 7662, 10789, 24800, 16600, 200, 8000],
        ["ĐBS Cửu Long", 1766929, 1477257, 152883, 43180, 34154, 6476, 2550],
        ["Long An", 207316, 170000, 12255, 4995, 4995, None, None],
        ["Đồng Tháp", 197078, 197078, None, 4550, 3600, 950, None],
        ["An Giang", 232488, 232488, None, 6307, 6187, 30, 90],
        ["Tiền Giang", 243468, 202118, None, 4629, 4120, 250, 259],
        ["Vĩnh Long", 62750, 62750, None, 6730, 3947, 2671, 112],
        ["Bến Tre", 23215, 4475, 35922, 1430, 906, 417, 107],
        ["Kiên Giang", 274559, 195759, 6245, None, None, None, None],
        ["Cần Thơ", 84896, 84896, None, 563, 563, None, None],
        ["Hậu Giang", 79744, 79744, None, 2209, 2209, None, None],
        ["Trà Vinh", 81356, 81356, 70500, 5913, 3881, 880, 1152],
        ["Sóc Trăng", 188565, 125115, 12000, 5854, 3746, 1278, 830],
        ["Bạc Liêu", 55827, 25000, 3068, None, None, None, None],
        ["Cà Mau", 35667, 16478, 12893, None, None, None, None]
    ]

    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for idx, (cmd, sub) in enumerate(items):
            try:
                v = normalize_number(row[idx+5])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
            
    return records

def parse_pl5():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL5", "source_file": "2010_09_phuluc_T09_2010_PL5.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Monthly", "report_date": "2010-09-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Vung, ThuocLa, Mia, Bong, DayLac, Rau, Dau]
    data = [
        ["Miền Nam", 276187, 24388, 75465, 25575, 13199, 132692, 1006, 3862, 286145, 64633],
        ["D.H Nam Trg Bộ", 80265, 1582, 25791, 6352, 902, 45163, 434, 41, 33646, 33646],
        ["TP Đà Nẵng", 1195, None, 618, 211, None, 366, None, None, 659, 210],
        ["Quảng Nam", 13252, None, 9772, 2101, 502, 700, 177, None, 9200, 3400],
        ["Quảng Ngãi", 12026, 375, 5457, None, None, 6194, None, None, 5849, 3016],
        ["Bình Định", 13551, 881, 8893, 1576, None, 2201, None, None, 12082, 1039],
        ["Phú Yên", 24062, 326, 906, 2464, 400, 19668, 257, 41, 3616, 3926],
        ["Khánh Hoà", 16179, None, 145, None, None, 16034, None, None, 2240, 733],
        ["Tây Nguyên", 52240, 13867, 7929, 1436, 6539, 22469, 0, 0, 45515, 23899],
        ["Kon Tum", 4108, None, 144, None, 1867, 2097, None, None, 700, 92],
        ["Gia Lai", 13629, None, 800, 900, 4622, 7307, None, None, 8108, 8158],
        ["Đắc Lắc", 21338, 5187, 3775, 536, 50, 11790, None, None, 3540, 9078],
        ["Đắc Nông", 11965, 8680, 3210, None, None, 75, None, None, 1398, 5271],
        ["Lâm Đồng", 1200, None, None, None, None, 1200, None, None, 31769, 1300],
        ["Đông Nam Bộ", 58497, 1116, 27261, 7642, 5596, 16310, 572, 0, 60484, 21874],
        ["TP Hồ Chí Minh", 2690, None, 900, None, None, 1790, None, None, 10489, None],
        ["Ninh Thuận", 1613, None, 135, 461, 32, 413, 572, None, 8820, 2097],
        ["Bình Phước", 440, 300, 130, 10, None, None, None, None, 816, 3301],
        ["Tây Ninh", 30398, None, 16174, 1502, 4632, 8090, None, None, 17838, 6335],
        ["Bình Dương", 934, None, 635, None, None, 299, None, None, 2871, 199],
        ["Đồng Nai", 10442, 564, 4100, 20, 800, 4958, None, None, 9728, 3942],
        ["Bình Thuận", 10537, 241, 4000, 5649, 31, 616, None, None, 5497, 5519],
        ["Bà Rịa-V.Tàu", 1443, 11, 1187, None, 101, 144, None, None, 4425, 481],
        ["ĐBS Cửu Long", 85185, 7823, 14484, 10145, 162, 48750, 0, 3821, 146500, 6536],
        ["Long An", 25032, None, 7000, 1275, 122, 13991, None, 2644, 13036, None],
        ["Đồng Tháp", 9001, 4935, 81, 3761, 15, 124, None, 85, 10243, None],
        ["An Giang", 1586, 556, 175, 836, 1, 18, None, None, 7396, 1181],
        ["Tiền Giang", 218, None, None, None, None, 218, None, None, 26785, None],
        ["Vĩnh Long", 1941, 1101, 29, 205, None, 62, None, 544, 9595, 240],
        ["Bến Tre", 6190, None, 132, None, None, 5865, None, 193, 5833, 3],
        ["Kiên Giang", 0, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 8395, 745, 3558, 4068, 24, None, None, None, 4103, 583],
        ["Hậu Giang", 13118, None, None, None, None, 13118, None, None, 18196, 77],
        ["Trà Vinh", 8782, 224, 3445, None, None, 4758, None, 355, 17800, 765],
        ["Sóc Trăng", 10791, 131, 64, None, None, 10596, None, None, 33513, 3687],
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

def parse_pl6():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL6", "source_file": "2010_09_phuluc_T09_2010_PL6.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Cumulative", "report_date": "2010-09-30"}
    
    # 9 months
    # Data manually parsed from the view_file content of PL6
    # Items: Trồng rừng tập trung, Rừng PH-DD, Rừng SX, Chăm sóc, Phân tán, Khoanh nuôi, Khoán bảo vệ, Khai thác gỗ.
    # Values are in the "Ước thực hiện 9 tháng năm 2010" column (which is the 3rd metric column in the row 18 string block)
    # The string block is:
    # 182.6 (Tong)
    # 43.8 (PHDD)
    # 138.8 (SX)
    # 284.4 (Cham soc)
    # 163.2 (Phan tan)
    # 728.6 (Khoanh nuoi)
    # 2412.3 (Bao ve)
    
    data = [
        ["Trồng rừng tập trung", 182.6],
        ["Rừng phòng hộ, đặc dụng", 43.8],
        ["Rừng sản xuất", 138.8],
        ["Chăm sóc rừng trồng", 284.4],
        ["Trồng cây phân tán", 163.2],
        ["Khoanh nuôi tái sinh, trồng dặm", 728.6],
        ["Khoán bảo vệ rừng", 2412.3],
        ["Khai thác gỗ", 2740.8]
    ]
    
    for row in data:
        item, val = row
        u = "1000_ha"
        if "gỗ" in item: u = "1000_m3"
        elif "phân tán" in item: u = "million_tree"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/09"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl4()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl5()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL5.json"))
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl6()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL6.json"))
    print("Successfully parsed PL4-PL6 for September 2010.")
