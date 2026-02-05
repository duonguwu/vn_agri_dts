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
    if "<br>" in s:
        # For batch processing, we often see 2 months or values separated by <br>.
        # Here we just take the first one or handle it specifically in the parser.
        s = s.split("<br>")[0].strip()
    try:
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
        "DBSCL": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "Trung du và MN PB": "Đông Bắc",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
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

def parse_pl3b_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL3b", "source_file": "2010_02_PhuLuc_T02_2010_PL3b.md"}
    records = []
    # Rows: loc, total_cn, dau_tuong, lac, vung, thuoc_la, mia, bong, day_lac, rau, dau
    data = [
        ["Miền Nam", 74447, 1412, 34678, 1149, 8839, 28183, 304, 694, 99646, 17237],
        ["D.H Nam Trg Bộ", 19347, 662, 17679, 15, 0, 1863, 212, 29, 15771, 15771],
        ["TP Đà Nẵng", 733, None, 616, None, None, 117, None, None, 282, 78],
        ["Quảng Nam", 8177, None, 8000, None, None, None, 177, None, 8500, 3400],
        ["Quảng Ngãi", 3326, None, 3161, None, None, 165, None, None, 1392, 1141],
        ["Bình Định", 5843, 375, 5468, None, None, None, None, None, 4364, 555],
        ["Phú Yên", 1158, 287, 324, 15, None, 1581, 35, 29, 1033, 594],
        ["Khánh Hoà", 110, None, 110, None, None, None, None, None, 200, None],
        ["Tây Nguyên", 12590, 0, 110, 0, 5298, 6881, 0, 0, 16457, 2960],
        ["Kon Tum", 4318, None, 58, None, 2145, 2115, None, None, 582, 119],
        ["Gia Lai", 7763, None, 52, None, 2999, 4712, None, None, 6600, 1714],
        ["Đắc Lắc", 509, None, None, None, 154, 54, None, None, 1864, 1072],
        ["Đắc Nông", 0, None, None, None, None, None, None, None, 7411, 55],
        ["Lâm Đồng", 0, None, None, None, None, None, None, None, None, None],
        ["Đông Nam Bộ", 22789, 331, 14822, 635, 3513, 3396, 92, 0, 18074, 5479],
        ["TP Hồ Chí Minh", 2644, None, 644, None, None, 2000, None, None, 3481, None],
        ["Ninh Thuận", 300, None, None, None, None, None, 300, None, None, None],
        ["Bình Phước", 0, None, None, None, None, None, None, None, None, None],
        ["Tây Ninh", 16938, None, 13115, 500, 2723, 600, None, None, 5141, 3141],
        ["Bình Dương", 398, None, 99, None, None, 299, None, None, 1200, 30],
        ["Đồng Nai", 1460, 331, 98, 84, 771, 99, 77, None, 3444, 135],
        ["Bình Thuận", 874, None, 789, 51, 19, None, 15, None, 1587, 1992],
        ["Bà Rịa-V.Tàu", 175, None, 77, None, None, 98, None, None, 3221, 181],
        ["ĐBS Cửu Long", 19721, 419, 2067, 499, 28, 16043, 0, 665, 49344, 3030],
        ["Long An", 13758, None, None, 347, None, 13411, None, None, 3391, None],
        ["Đồng Tháp", 264, 158, None, None, 10, 11, None, 85, 3681, None],
        ["An Giang", 337, 100, 73, 145, 1, 18, None, None, 10741, 600],
        ["Tiền Giang", 0, None, None, None, None, None, None, None, 11411, None],
        ["Vĩnh Long", 261, 121, None, None, None, 4, None, 136, 2001, 1900],
        ["Bến Tre", 110, None, 110, None, None, None, None, None, 2050, 40],
        ["Kiên Giang", 0, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 77, 40, 13, 7, 17, None, None, None, 1185, 113],
        ["Hậu Giang", 900, None, None, None, None, 900, None, None, 5120, 77],
        ["Trà Vinh", 4014, None, 1871, None, None, 1699, None, 444, 6661, 300],
        ["Sóc Trăng", 0, None, None, None, None, None, None, None, 3103, None],
        ["Bạc Liêu", 0, None, None, None, None, None, None, None, None, None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]
    t = {"year": 2010, "month": 2, "period_type": "Monthly", "report_date": "2010-02-15"}
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); geo = "Regional" if loc in regional_list else "Provincial"
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # Rau các loại
        v = normalize_number(row[9])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # Đậu các loại
        v = normalize_number(row[10])
        if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}

def parse_pl4_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL4", "source_file": "2010_02_PhuLuc_T02_2010_PL4.md"}
    records = []
    # TT, Chỉ tiêu, ĐVT, Thực hiện cùng kỳ, Ước thực hiện 2 tháng 2010
    raw = [
        ["1", "Trồng rừng tập trung", "1000 ha", 16.0, 14.0, "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000 ha", 2.6, 2.2, "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000 ha", 13.4, 11.8, "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000 ha", 32.5, 32.3, "Other"],
        ["3", "Trồng cây nhân dân", "Tr.cây", 25.7, 28.0, "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000 ha", 18.5, 18.6, "Other"],
        ["5", "Khoán bảo vệ rừng", "1000 ha", 40.5, 40.8, "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000 m3", 182.0, 220.0, "Wood_Volume"],
    ]
    t10 = {"year": 2010, "month": 2, "period_type": "Cumulative"}
    t09 = {"year": 2009, "month": 2, "period_type": "Cumulative"}
    for r in raw:
        tt, name, unit, v09, v10, attr = r
        loc, gl = "Cả nước", "National"
        records.append(create_record(metadata, t10, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": v10, "unit": unit.replace(" ", "_"), "data_type": "Estimated"}))
        records.append(create_record(metadata, t09, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": v09, "unit": unit.replace(" ", "_"), "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}

def parse_pl5_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL5", "source_file": "2010_02_PhuLuc_T02_2010_PL5.md"}
    records = []
    # Chỉ tiêu, ĐVT, KH 2010, Jan, Feb, Cumul
    raw = [
        ["Tổng sản lượng", "1000 Tấn", 5050, 365, 340, 705, "Production", None],
        ["Sản lượng khai thác", "1000 Tấn", 2400, 210, 200, 410, "Production", "Khai thác"],
        ["Khai thác biển", "1000 Tấn", 2180, 200, 190, 390, "Production", "Khai thác biển"],
        ["Khai thác nội địa", "1000 Tấn", 220, 10, 10, 20, "Production", "Khai thác nội địa"],
        ["Sản lượng nuôi trồng", "1000 Tấn", 2650, 155, 140, 295, "Production", "Nuôi trồng"],
        ["Kim ngạch xuất khẩu TS", "Triệu USD", 4500, 313, 315, 628, "Export_Value", None],
    ]
    loc, gl = "Cả nước", "National"
    for r in raw:
        name, unit, plan, v_jan, v_feb, v_cum, attr, sub = r
        t_feb = {"year": 2010, "month": 2, "period_type": "Monthly"}
        t_jan = {"year": 2010, "month": 1, "period_type": "Monthly"}
        t_cum = {"year": 2010, "month": 2, "period_type": "Cumulative"}
        t_plan = {"year": 2010, "month": 12, "period_type": "Annual"}
        
        sector = "Fishery"
        records.append(create_record(metadata, t_feb, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": v_feb, "unit": "1000_ton" if "Tấn" in unit else "million_USD", "data_type": "Estimated"}))
        records.append(create_record(metadata, t_jan, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": v_jan, "unit": "1000_ton" if "Tấn" in unit else "million_USD", "data_type": "Actual"}))
        records.append(create_record(metadata, t_cum, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": v_cum, "unit": "1000_ton" if "Tấn" in unit else "million_USD", "data_type": "Actual"}))
        records.append(create_record(metadata, t_plan, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": plan, "unit": "1000_ton" if "Tấn" in unit else "million_USD", "data_type": "Plan"}))
        
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl3b_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL3b.json"))
    save_json(parse_pl4_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL4.json"))
    save_json(parse_pl5_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL5.json"))
    print("Successfully parsed PL3b, PL4, PL5 for Feb 2010.")
