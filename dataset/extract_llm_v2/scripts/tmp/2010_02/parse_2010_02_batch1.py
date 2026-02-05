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
    if s == "" or s == "-" or s == "." or s == "||" or s == "|": return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "")
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "ĐB Sông Cửu Long": "Đồng bằng sông Cửu Long",
        "DBSCL": "Đồng bằng sông Cửu Long", "Trung du và MN phía Bắc": "Đông Bắc", # Simplified for mapping
        "Trung du và MN PB": "Đông Bắc",
        "D.H Nam Trung\nBộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung Bộ ": "Duyên hải Nam Trung Bộ"
    }
    norm_loc = alias_map.get(loc_name.strip(), loc_name.strip())
    
    # Matching logic from region_map
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name_vn"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name_vn"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"
        geo_context["region_name_vn"] = "Cả nước"
    elif norm_loc == "Miền Nam":
        geo_context["region_id"] = "SOUTH"
        geo_context["region_name_vn"] = "Miền Nam"
    elif norm_loc == "Miền Bắc":
        geo_context["region_id"] = "NORTH"
        geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": geo_context,
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata
    }
    if comp:
        record["comparison_context"] = comp
    return record

def parse_pl1_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL1", "source_file": "2010_02_PhuLuc_T02_2010_PL1.md"}
    records = []
    
    # Table 1: Summary (1000 ha)
    # Rows: Item, Unit, v09, v10, c_plan, c_yoy
    table1 = [
        ["Cả nước", "Lúa", "Đông Xuân", "Area_Planted", 2773.9, 2742.7, None, 98.9],
        ["Miền Bắc", "Lúa", "Đông Xuân", "Area_Planted", 933.6, 884.9, None, 94.8],
        ["Đồng bằng sông Hồng", "Lúa", "Đông Xuân", "Area_Planted", 447.0, 409.9, None, 91.7],
        ["Bắc Trung Bộ", "Lúa", "Đông Xuân", "Area_Planted", 321.2, 335.0, None, 104.3],
        ["Miền Nam", "Lúa", "Đông Xuân", "Area_Planted", 1840.3, 1857.8, None, 100.9],
        ["Đồng bằng sông Cửu Long", "Lúa", "Đông Xuân", "Area_Planted", 1508.5, 1530.0, None, 101.4],
        ["Miền Nam", "Lúa", "Đông Xuân", "Area_Harvested", 286.5, 268.0, 14.7, 93.5],
        ["Đồng bằng sông Cửu Long", "Lúa", "Đông Xuân", "Area_Harvested", 286.5, 268.0, 17.9, 93.5],
        ["Cả nước", "Màu lương thực", "Tổng số", "Area_Planted", 368.5, 379.3, None, 102.9],
        ["Cả nước", "Ngô", None, "Area_Planted", 248.5, 263.7, None, 106.1],
        ["Cả nước", "Khoai lang", None, "Area_Planted", 65.2, 68.5, None, 105.1],
        ["Cả nước", "Sắn", None, "Area_Planted", 54.4, 46.8, None, 86.0],
        ["Cả nước", "Cây công nghiệp ngắn ngày", "Tổng số", "Area_Planted", 233.4, 247.2, None, 105.9],
        ["Cả nước", "Đậu tương", None, "Area_Planted", 71.6, 85.0, None, 118.7],
        ["Cả nước", "Lạc", None, "Area_Planted", 110.5, 99.3, None, 89.9],
        ["Cả nước", "Rau các loại", "Rau đậu", "Area_Planted", 302.5, 310.2, None, 102.5],
    ]
    
    t10 = {"year": 2010, "month": 2, "period_type": "Monthly", "report_date": "2010-02-15"}
    t09 = {"year": 2009, "month": 2, "period_type": "Monthly", "report_date": "2009-02-15"}

    for row in table1:
        loc, cmd, sub, attr, v09, v10, cp, cy = row
        geo = "National" if loc == "Cả nước" else ("Regional" if "Miền" in loc or "Đồng bằng" in loc or "Bắc Trung Bộ" in loc else "Provincial")
        
        # Record for 2010
        comp = {}
        if cp: comp["comparison_type"] = "vs_Plan"; comp["comparison_value"] = cp
        if cy: comp["comparison_type"] = "YoY"; comp["comparison_value"] = cy; comp["base_value"] = v09
        
        records.append(create_record(metadata, t10, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, 
                                    {"attribute": attr, "value": v10, "unit": "1000_ha", "data_type": "Actual"}, comp))
        # Record for 2009
        records.append(create_record(metadata, t09, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, 
                                    {"attribute": attr, "value": v09, "unit": "1000_ha", "data_type": "Actual"}))

    # Table 2: Northern Provinces (ha)
    table2 = [
        ["Miền Bắc", 884909, 29595, 108568, 55219, 10137, 17825, 23304],
        ["ĐB sông Hồng", 409858, 7005, 28619, 14230, 2164, 0, 10142],
        ["Hà Nội", 82500, 902, 1617, 1617, None, None, None],
        ["Hải Phòng", 41500, 1435, 2500, None, None, None, 2500],
        ["Vĩnh Phúc", 23800, 438, 2407, 1705, 89, None, 613],
        ["Bắc Ninh", 10712, 235, 764, 180, None, None, 584],
        ["Hải Dương", 38171, None, 2083, None, None, None, None],
        ["Hưng Yên", 14500, 120, 2394, 2394, None, None, None],
        ["Hà Nam", 15000, 3001, 2608, 2608, None, None, None],
        ["Nam Định", 67400, None, 5240, 740, None, None, 4500],
        ["Thái Bình", 81500, 624, 4045, 2100, None, None, 1945],
        ["Ninh Bình", 24325, 250, 1245, 1170, 75, None, None],
        ["Quảng Ninh", 10450, None, 3716, 1716, 2000, None, None],
        ["Trung du và MN PB", 150656, 10923, 25014, 18856, 905, 1500, 3753],
        ["Hà Giang", 5500, None, 7500, 7500, None, None, None],
        ["Cao Bằng", 250, None, 750, 750, None, None, None],
        ["Lào Cai", 120, None, 10, 10, None, None, None],
        ["Bắc Cạn", 1700, None, 2124, 2124, None, None, None],
        ["Lạng Sơn", None, None, 2118, 145, None, None, 1973],
        ["Tuyên Quang", 16300, None, 2100, 2100, None, None, None],
        ["Yên Bái", 15700, 9267, 2700, 1200, None, 1500, None],
        ["Thái Nguyên", 18343, None, 1120, 620, 500, None, None],
        ["Phú Thọ", 33406, None, 2832, 2500, 130, None, 202],
        ["Bắc Giang", 32802, 924, 78, 78, None, None, None],
        ["Lai Châu", 4089, 390, 29, 29, None, None, None],
        ["Điện Biên", 5844, None, None, None, None, None, None],
        ["Sơn La", 3402, 92, 100, 100, None, None, None],
        ["Hoà Bình", 13200, 250, 3553, 1700, 275, None, 1578],
        ["Bắc Trung Bộ", 324395, 11667, 54935, 22133, 7068, 16325, 9409],
        ["Thanh Hoá", 110000, None, 12092, 6883, 4500, None, 709],
        ["Nghệ An", 85000, 1667, 8677, 7500, 1152, 25, None],
        ["Hà Tĩnh", 53531, None, 2750, None, None, None, 2750],
        ["Quảng Bình", 26000, None, 13166, 4000, 1416, 5800, 1950],
        ["Quảng Trị", 23864, 10000, 10000, 2000, None, 6000, 2000],
        ["Thừa Thiên Huế", 26000, None, 8250, 1750, None, 4500, 2000],
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN PB", "Bắc Trung Bộ"]
    
    for row in table2:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        
        # 1. Lúa Đông Xuân Area_Planted
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t10, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, 
                                                      {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Mạ Area_Seedling
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t10, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mạ"}, 
                                                      {"attribute": "Area_Seedling", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Màu Tổng số
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t10, loc, geo, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, 
                                                      {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 4. Ngô, Khoai lang, Sắn, Cây khác
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+4])
            if v is not None: records.append(create_record(metadata, t10, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, 
                                                          {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))

    return {"metadata": metadata, "records": records}

def parse_pl2b_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL2b", "source_file": "2010_02_PhuLuc_T02_2010_PL2b.md"}
    records = []
    
    # Rows: loc, vdx_gc, vmua_th, mau_total, ngo, khoai, san, cay_khac
    data = [
        ["Miền Nam", 1857808, 267989, 91508, 51551, 7242, 29013, 3913],
        ["D.H Nam Trung Bộ", 169074, 0, 28560, 12982, 6536, 9042, 0],
        ["TP Đà Nẵng", 4000, None, 852, 323, 267, 262, None],
        ["Quảng Nam", 41800, None, 9500, 5800, 3700, None, None],
        ["Quảng Ngãi", 36664, None, 5866, 3466, 2400, None, None],
        ["Bình Định", 46787, None, 9660, 1668, None, 7992, None],
        ["Phú Yên", 25852, None, 2302, 1345, 169, 788, None],
        ["Khánh Hoà", 13971, None, 380, 380, None, None, None],
        ["Tây Nguyên", 66822, 0, 14017, 9942, 360, 3715, 0],
        ["Kon Tum", 6678, None, 405, 405, None, None, None],
        ["Gia Lai", 21957, None, 7957, 4001, 241, 3715, None],
        ["Đắc Lắc", 24331, None, 2171, 2171, None, None, None],
        ["Đắc Nông", 3930, None, 2789, 2670, 119, None, None],
        ["Lâm Đồng", 9926, None, 695, 695, None, None, None],
        ["Đông Nam Bộ", 91821, 0, 38156, 18510, 246, 15698, 3702],
        ["TP HCM", 4293, None, 753, 753, None, None, None],
        ["Ninh Thuận", 10181, None, 2400, 2400, None, None, None],
        ["Bình Phước", 3005, None, 0, None, None, None, None],
        ["Tây Ninh", 39686, None, 20491, 4754, None, 12446, 3291],
        ["Bình Dương", 900, None, 1768, 141, 171, 1045, 411],
        ["Đồng Nai", 11214, None, 8524, 6900, None, 1624, None],
        ["Bình Thuận", 17953, None, 3203, 2691, None, 512, None],
        ["Bà Rịa-V.Tàu", 4589, None, 1017, 871, 75, 71, None],
        ["DBSCL", 1530091, 267989, 10775, 10117, 100, 558, 211],
        ["Long An", 230000, 13020, 3646, 3646, None, None, None],
        ["Đồng Tháp", 207732, 19787, 1311, 1100, None, None, 211],
        ["An Giang", 234091, None, 1720, 1600, 30, 90, None],
        ["Tiền Giang", 82272, 9700, 1376, 1176, None, 200, None],
        ["Vĩnh Long", 66974, 26145, 369, 221, None, 148, None],
        ["Bến Tre", 19808, 48, 540, 350, 70, 120, None],
        ["Kiên Giang", 283898, 97142, 0, None, None, None, None],
        ["Cần Thơ", 89564, 56, 141, 141, None, None, None],
        ["Hậu Giang", 83846, 7037, 270, 270, None, None, None],
        ["Trà Vinh", 57116, 2600, 665, 665, None, None, None],
        ["Sóc Trăng", 139240, 92000, 948, 948, None, None, None],
        ["Bạc Liêu", 35550, 454, 0, None, None, None, None],
        ["Cà Mau", None, None, 0, None, None, None, None],
    ]
    
    t = {"year": 2010, "month": 2, "period_type": "Monthly", "report_date": "2010-02-15"}
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "DBSCL"]

    for row in data:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        
        # 1. Lúa Đông Xuân Gieo cấy
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, 
                                          {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa Mùa Thu hoạch (Based on PL title)
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa 2009"}, 
                                          {"attribute": "Area_Harvested", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Màu Tổng số
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, 
                                                      {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 4. Ngô, Khoai lang, Sắn, Cây khác
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây có củ khác")]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+4])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, 
                                                          {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}

def parse_pl3a_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL3a", "source_file": "2010_02_PhuLuc_T02_2010_PL3a.md"}
    records = []
    
    # Rows: loc, cn_total, dau_tuong, lac, mia, thuoc_la, rau_dau_total
    data = [
        ["Miền Bắc", 165881, 93571, 64627, 1020, 5963, 126295],
        ["ĐB sông Hồng", 88383, 76137, 9851, 0, 2400, 68490],
        ["Hà Nội", 31185, 30529, 656, None, None, 10351],
        ["Hải Phòng", 2200, 200, None, None, 2000, 10258],
        ["Vĩnh Phúc", 5636, 4900, 736, None, None, 2961],
        ["Bắc Ninh", 2090, 2068, 22, None, None, 3228],
        ["Hải Dương", 270, 270, None, None, None, None],
        ["Hưng Yên", 3050, 2758, 297, None, None, 9379],
        ["Hà Nam", 11605, 11249, 356, None, None, 1500],
        ["Nam Định", 3758, 758, 3000, None, None, 7883],
        ["Thái Bình", 15679, 13779, 1500, None, 400, 15188],
        ["Ninh Bình", 11993, 9224, 2769, None, None, 4051],
        ["Quảng Ninh", 917, 402, 515, None, None, 3691],
        ["Trung du và MN PB", 38863, 15620, 17976, 1000, 3563, 31574],
        ["Hà Giang", 3600, 1500, 2100, None, None, 3120],
        ["Cao Bằng", 7309, 5193, 967, None, 1149, 427],
        ["Lào Cai", 516, None, None, None, 12, 2014],
        ["Bắc Cạn", 1201, None, 300, None, 901, 350],
        ["Lạng Sơn", 1501, None, None, None, 1501, 650],
        ["Tuyên Quang", 2221, 221, 1800, None, None, 2221],
        ["Yên Bái", 740, 40, 700, None, None, 2293],
        ["Thái Nguyên", 1603, 103, 1500, None, None, 4329],
        ["Phú Thọ", 2999, 199, 2800, None, None, 2710],
        ["Bắc Giang", 5465, 46, 5419, None, None, 10040],
        ["Lai Châu", 1302, 1032, 270, None, None, 0],
        ["Điện Biên", 5000, 5000, None, None, None, None],
        ["Sơn La", 35, 35, None, None, None, 1520],
        ["Hoà Bình", 5371, 2251, 2120, 1000, None, 1900],
        ["Bắc Trung Bộ", 38635, 1815, 36800, 20, 0, 26231],
        ["Thanh Hoá", 13815, 1815, 12000, None, None, 13509],
        ["Nghệ An", 14520, None, 14500, 20, None, 9136],
        ["Hà Tĩnh", 300, None, 300, None, None, 3000],
        ["Quảng Bình", 3500, None, 3500, None, None, 586],
        ["Quảng Trị", 3500, None, 3500, None, None, None],
        ["Thừa Thiên Huế", 3000, None, 3000, None, None, None],
    ]
    
    t = {"year": 2010, "month": 2, "period_type": "Monthly", "report_date": "2010-02-15"}
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Trung du và MN PB", "Bắc Trung Bộ"]

    for row in data:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        
        # 1. Cây CN ngắn ngày Tổng số
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, 
                                                      {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Đậu tương, Lạc, Mía, Thuốc lá
        items = [("Đậu tương", None), ("Lạc", None), ("Mía", "Trồng mới"), ("Thuốc lá", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, 
                                                          {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Rau, đậu các loại
        v = normalize_number(row[6])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": "Tổng số"}, 
                                                      {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
                                                      
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/02"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl1_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL1.json"))
    save_json(parse_pl2b_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL2b.json"))
    save_json(parse_pl3a_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL3a.json"))
    
    print("Successfully parsed PL1, PL2b, PL3a for Feb 2010.")
