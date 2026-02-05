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
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
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
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL4", "source_file": "2010_10_Phuluc_T10_2010_PL4.md"}
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Monthly", "report_date": "2010-10-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Vung, ThuocLa, Mia, Bong, DayLac, Rau, Dau]
    data = [
        ["Miền Nam", 276328, 24388, 75606, 25575, 13199, 132692, 1006, 3862, 286145, 64633],
        ["D.H Nam Trg Bộ", 80265, 1582, 25791, 6352, 902, 45163, 434, 41, 33646, 33646],
        ["TP Đà Nẵng", 1195, None, 618, 211, None, 366, None, None, 659, 210],
        ["Quảng Nam", 13252, None, 9772, 2101, 502, 700, 177, None, 9200, 3400],
        ["Quảng Ngãi", 12026, 375, 5457, None, None, 6194, None, None, 5849, 3016],
        ["Bình Định", 13551, 881, 8893, 1576, None, 2201, None, None, 12082, 1039],
        ["Phú Yên", 24062, 326, 906, 2464, 400, 19668, 257, 41, 3616, 3926],
        ["Khánh Hoà", 16179, None, 145, None, None, 16034, None, None, 2240, 733],
        ["Tây Nguyên", 52240, 13867, 7929, 1436, 6539, 22469, None, None, 45515, 23899],
        ["Kon Tum", 4108, None, 144, None, 1867, 2097, None, None, 700, 92],
        ["Gia Lai", 13629, None, 800, 900, 4622, 7307, None, None, 8108, 8158],
        ["Đắc Lắc", 21338, 5187, 3775, 536, 50, 11790, None, None, 3540, 9078],
        ["Đắc Nông", 11965, 8680, 3210, None, None, 75, None, None, 1398, 5271],
        ["Lâm Đồng", 1200, None, None, None, None, 1200, None, None, 31769, 1300],
        ["Đông Nam Bộ", 58497, 1116, 27261, 7642, 5596, 16310, 572, None, 60484, 21874],
        ["TP Hồ Chí Minh", 2690, None, 900, None, None, 1790, None, None, 10489, None],
        ["Ninh Thuận", 1613, None, 135, 461, 32, 413, 572, None, 8820, 2097],
        ["Bình Phước", 440, 300, 130, 10, None, None, None, None, 816, 3301],
        ["Tây Ninh", 30398, None, 16174, 1502, 4632, 8090, None, None, 17838, 6335],
        ["Bình Dương", 934, None, 635, None, None, 299, None, None, 2871, 199],
        ["Đồng Nai", 10442, 564, 4100, 20, 800, 4958, None, None, 9728, 3942],
        ["Bình Thuận", 10537, 241, 4000, 5649, 31, 616, None, None, 5497, 5519],
        ["Bà Rịa-V.Tàu", 1443, 11, 1187, None, 101, 144, None, None, 4425, 481],
        ["ĐBS Cửu Long", 85326, 7823, 14625, 10145, 162, 48750, None, 3821, 146500, 6536],
        ["Long An", 25032, None, 7000, 1275, 122, 13991, None, 2644, 13036, None],
        ["Đồng Tháp", 9001, 4935, 81, 3761, 15, 124, None, 85, 10243, None],
        ["An Giang", 1586, 556, 175, 836, 1, 18, None, None, 7396, 1181],
        ["Tiền Giang", 218, None, None, None, None, 218, None, None, 26785, None],
        ["Vĩnh Long", 1941, 1101, 29, 205, None, 62, None, 544, 9595, 240],
        ["Bến Tre", 6190, None, 132, None, None, 5865, None, 193, 5833, 3],
        ["Kiên Giang", None, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 8395, 745, 3558, 4068, 24, None, None, None, 4103, 583],
        ["Hậu Giang", 13118, None, None, None, None, 13118, None, None, 18196, 77],
        ["Trà Vinh", 8782, 224, 3445, None, None, 4758, None, 355, 17800, 765],
        ["Sóc Trăng", 10932, 131, 205, None, None, 10596, None, None, 33513, 3687],
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

def parse_pl5():
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL5", "source_file": "2010_10_Phuluc_T10_2010_PL5.md"}
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Cumulative", "report_date": "2010-10-31"}
    
    # 10 months
    # Data manually parsed from PL5
    # Items: Trồng rừng tập trung, Rừng PH-DD, Rừng SX, Chăm sóc, Phân tán, Khoanh nuôi, Khoán bảo vệ, Khai thác gỗ.
    # Values col is line 20-27, col 5 (index 5 from 0 in view is 10M Actual)
    # View file: |TT|Chỉ tiêu|Đơn vị|KH|Cùng kỳ|Ước TH 10T 2010|...
    # Values from view file lines:
    # 20: 200.4
    # 21: 45.8
    # 22: 154.6
    # 23: 288.0
    # 24: 170.0
    # 25: 728.6
    # 26: 2566.5
    # 27: 3146.8
    
    data = [
        ["Trồng rừng tập trung", 200.4],
        ["Rừng phòng hộ, đặc dụng", 45.8],
        ["Rừng sản xuất", 154.6],
        ["Chăm sóc rừng trồng", 288.0],
        ["Trồng cây phân tán", 170.0],
        ["Khoanh nuôi tái sinh, trồng dặm", 728.6],
        ["Khoán bảo vệ rừng", 2566.5],
        ["Khai thác gỗ", 3146.8]
    ]
    
    for row in data:
        item, val = row
        u = "1000_ha"
        if "gỗ" in item: u = "1000_m3"
        elif "phân tán" in item: u = "million_tree"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))
    return records

def parse_pl6_regions_south():
    # PL6 in Oct seems to be Detailed Forestry for South regions (like PL7 usually is).
    # NOTE: The view file content shows PL6 contains Forestry data for South regions (starting with IV D.H Nam Trung Bo, V Tay Nguyen, VI Dong Nam Bo, VII DBSCL).
    # ALSO, Lines 60-83 contain "PL7 Fishery" inside the PL6 file view?
    # Wait, the view file content shows: 
    # Line 1: Phụ lục 6 - TỔNG HỢP KẾT QUẢ SẢN XUẤT LÂM NGHIỆP
    # ... Table with forestry data ...
    # Line 60: ## Phụ lục 7 KẾT QUẢ SẢN XUẤT THUỶ SẢN 10 THÁNG NĂM 2010
    # So both PL6 (Forestry South) and PL7 (Fishery) are in this file content? Or maybe named PL6 but contains PL7 content appended?
    # The user provided separate files: PL6.md and PL7.md.
    # Let's check PL7 content in next step. For now, extract Forestry South from PL6.
    
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL6", "source_file": "2010_10_Phuluc_T10_2010_PL6.md"}
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Cumulative", "report_date": "2010-10-31"}
    
    # Rows 20-57 contain detailed forestry data for South.
    # Columns:
    # 2: Name
    # 3: Trong rung tap trung Tong so
    # 4: PHDD
    # 5: Kinh te
    # 6: Cham soc
    # 7: Khoanh nuoi
    # 8: Khoan bao ve
    
    # I will extract this manually as there are ~25 rows.
    # Format: [Name, Total, PHDD, Kinhte] (Focus on Area Planted first)
    
    data = [
        ["Miền Nam", 27165.0, 8612.5, 18552.5],
        ["D.H Nam Trung Bộ", 4833, 1762, 3071],
        ["Đà Nẵng", 20, 20, None],
        ["Bình Định", 437, 26, 411],
        ["Khánh Hoà", 390, 40, 350],
        ["Ninh Thuận", 860, 860, None],
        ["Bình Thuận", 3126, 816, 2310],
        ["Tây Nguyên", 15661, 2101, 13561],
        ["Kon Tum", 4578, 426, 4152],
        ["Gia Lai", 880, 760, 120],
        ["Đắk Lắk", 4255, 120, 4135],
        ["Đắk Nông", 2252, 191, 2062],
        ["Lâm Đồng", 3696, 604, 3092],
        ["Đông Nam Bộ", 2874, 2161, 713],
        ["Bình Phước", 700, 700, None],
        ["Tây Ninh", 942, 817, 125],
        ["Đồng Nai", 390, 230, 160],
        ["Bà Rịa-Vũng Tàu", 782, 354, 428],
        ["TP Hồ Chí Minh", 60, 60, None],
        ["ĐB. sông Cửu Long", 3797, 2589, 1208],
        ["Tiền Giang", 20, 20, None],
        ["Bến Tre", 55, 30, 25],
        ["Trà Vinh", 116, 116, None],
        ["Đồng Tháp", 220, 50, 170],
        ["An Giang", 910, 910, None],
        ["Sóc Trăng", 310, 310, None],
        ["Bạc Liêu", 951, 951, None],
        ["Cà Mau", 1215, 202, 1013],
        ["Trung ương", 7844, 4044, 3800]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Trung ương": gl = "National"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))

    return records

def parse_pl6_fishery():
    # Helper to clean and append fishery data found at the bottom of PL6 file
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL7", "source_file": "2010_10_Phuluc_T10_2010_PL6.md"} # Yes, PL7 data in PL6 file
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Cumulative", "report_date": "2010-10-31"}
    
    # [Item, 10M]
    data = [
        ["Tổng sản lượng thủy sản", 4255],
        ["Sản lượng khai thác", 2007],
        ["Khai thác biển", 1920],
        ["Khai thác nội địa", 87],
        ["Sản lượng nuôi trồng", 2243]
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Fishery", "commodity": row[0]}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/10"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 10}, "records": parse_pl4()}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 10}, "records": parse_pl5()}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL5.json"))
    
    # PL6 contains Forestry South AND Fishery (PL7 content)
    pl6_geo = parse_pl6_regions_south()
    pl6_fishery = parse_pl6_fishery()
    
    save_json({"metadata": {"year": 2010, "month": 10}, "records": pl6_geo}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL6_Forestry.json"))
    save_json({"metadata": {"year": 2010, "month": 10}, "records": pl6_fishery}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL6_Fishery.json"))
    
    print("Successfully parsed PL4-PL6 for October 2010. Extracted Fishery from PL6 footer.")
