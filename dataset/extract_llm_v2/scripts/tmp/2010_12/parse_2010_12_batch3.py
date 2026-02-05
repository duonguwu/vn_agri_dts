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
        "Hà Nội (mở rộng)": "Hà Nội",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trung\nBộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung B": "Duyên hải Nam Trung Bộ", "d.h nam trg b": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung B\nộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "ĐB. sông Hồng": "Đồng bằng sông Hồng", "Trung uơng": "Trung ương",
        "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "Trung du và miền núi phía Bắc": "Đông Bắc"
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
    elif norm_loc == "Miền bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl7():
    # Forestry National Indicators (Final 2010?)
    # Header says "Ước thực hiện 12 tháng năm".
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL7", "source_file": "2010_12_Phuluc_T12_2010_PL7.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"} 
    
    # [Item, Unit, 12M_Est]
    data = [
        ["Trồng rừng tập trung", "1000 ha", 252.0],
        ["Rừng phòng hộ, đặc dụng", "1000 ha", 61.9],
        ["Rừng sản xuất", "1000 ha", 190.1],
        ["Chăm sóc rừng trồng", "1000 ha", 306.2],
        ["Trồng cây phân tán", "Tr.cây", 181.5],
        ["Khoanh nuôi tái sinh, trồng dặm", "1000 ha", 765.4],
        ["Khoán bảo vệ rừng", "1000 ha", 2574.2],
        ["Khai thác gỗ", "1000 m3", 4042.6],
        ["Khai thác củi", "1000 Ste", 28232.4],
        ["Giá trị sản xuất lâm nghiệp (1994)", "billion_VND", 7356] # Unit in file says "Tr. Đồng" but value 7356 suggests Billion or Million? 
        # 1994 price usually low. 7356 Ty Dong is likely. Previous month PL5 didn't have this.
        # "Tr. Đồng" usually means Million Dong. But 7356 Million is 7.3 Billion. Too small for National.
        # Maybe it's Ty Dong (Billion)?
        # 2010 GDP Forestry ~ 7000-8000 Billion VND (1994 prices). So 7356 Billion VND. "Tr. Đồng" is typo for "Tỷ Đồng" or "Triệu Đồng" but scaled.
        # Let's verify value: 7043.2 same period last year.
        # 7000 Billion is reasonable.
        # I will map unit to "billion_VND".
    ]
    
    for item, unit, val in data:
        u = "1000_ha"
        if unit == "Tr.cây": u = "million_tree"
        elif unit == "1000 m3": u = "1000_m3"
        elif unit == "1000 Ste": u = "1000_ste"
        elif unit == "billion_VND": u = "billion_VND"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))

    return records

def parse_pl8():
    # Forestry Detailed (Locality)
    # North and South tables in one file.
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL8", "source_file": "2010_12_Phuluc_T12_2010_PL8.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"} 
    
    # Structure from Step 383
    # Same as PL6 Nov: Name, Total, PHDD, KT, ChamSoc, KhoanhNuoi, KhoanBaoVe
    
    # Just copying transcription from Step 383 output manually is safest.
    # But lengthy. I'll read file content? No, I have content in prompt.
    
    # Manual extraction of North data
    data_north = [
        ["Cả nước", 252028, 61911, 190118, 306154, 765415, 2574203],
        ["Miền bắc", 185313, 40340, 144973, 214250, 606992, 1402411],
        ["ĐB. sông Hồng", 19585, 7180, 12405, 46881, 20678, 74822],
        ["Hà Nội", 212, 162, 50, 197, None, 8846],
        ["Vĩnh Phúc", 365, 170, 195, 204, 502, 11157],
        ["Bắc Ninh", 50, 50, None, None, None, None],
        ["Quảng Ninh", 15124, 3147, 11977, 44998, 5981, 27794],
        ["Hải Dương", 130, 20, 110, 130, None, 3042],
        ["Hải Phòng", 2190, 2190, None, 810, 1855, 11500],
        ["Thái Bình", 993, 993, None, None, None, 7000],
        ["Hà Nam", 73, None, 73, 55, 40, 3674],
        ["Nam Định", 328, 328, None, 397, None, 1065],
        ["Ninh Bình", 120, 120, None, 90, 12300, 744],
        ["Trung du và miền núi phía Bắc", 122592, 26034, 96558, 102082, 492014, 970801],
        ["Hà Giang", 15554, 4305, 11249, 24621, 44530, 93471],
        ["Cao Bằng", 1815, 909, 906, 1008, 21061, 19590],
        ["Bắc Kạn", 9702, 1004, 8698, None, 18107, 20744],
        ["Tuyên Quang", 15583, 1976, 13607, 6998, 28597, 180140],
        ["Lào Cai", 10705, 2720, 7985, 2036, 5845, 101312],
        ["Yên Bái", 14305, 2800, 11505, 5999, 19671, 164923],
        ["Thái Nguyên", 6454, 1410, 5044, 2469, 4578, 23274],
        ["Lạng Sơn", 8564, 2264, 6300, 7949, 8287, 15381],
        ["Bắc Giang", 7234, 450, 6784, 3742, 1230, 28320],
        ["Phú Thọ", 8897, 342, 8555, 27771, 1550, 32445],
        ["Điện Biên", 3030, 573, 2457, 798, 55350, 64015],
        ["Lai Châu", 5404, 1911, 3493, 1466, 101722, 147788],
        ["Sơn La", 5485, 3510, 1975, 8725, 179189, 20381],
        ["Hoà Bình", 9860, 1860, 8000, 8500, 2297, 59017],
        ["Bắc Trung Bộ", 43136, 7126, 36010, 65287, 94300, 356788],
        ["Thanh Hoá", 15564, 1544, 14020, 14154, 15417, 63621],
        ["Nghệ An", 14713, 1177, 13536, 17880, 55000, 105000],
        ["Hà Tĩnh", 2350, 1350, 1000, 14570, 9081, 47676],
        ["Quảng Bình", 1667, 541, 1126, 886, 5507, 55337],
        ["Quảng Trị", 4842, 1380, 3462, 2881, 1319, 26654],
        ["Thừa Thiên Huế", 4000, 1134, 2866, 14916, 7976, 58500]
    ]

    # South data
    data_south = [
        ["Miền Nam", 58359, 17058.5, 41300.5, 78541, 151913, 1078404],
        ["D.H Nam Trung Bộ", 28155, 7405, 20750, 50310, 109532, 292923],
        ["Đà Nẵng", 356, 356, None, 500, 112, 15000],
        ["Quảng Nam", 980, 365, 615, 12660, 38200, 35000],
        ["Quảng Ngãi", 5376, 900, 4476, 4735, 2100, 27724],
        ["Bình Định", 6583, 979, 5604, 8894, 50412, 44311],
        ["Phú Yên", 5000, 2173, 2827, 11000, 3073, 18332],
        ["Khánh Hoà", 1310, 358, 952, 1392, 1014, 7303],
        ["Ninh Thuận", 1124, 1124, None, 1756, 1000, 41705],
        ["Bình Thuận", 7426, 1150, 6276, 9373, 13621, 103548],
        ["Tây Nguyên", 21267, 3208, 18060, 19192, 14812, 634769],
        ["Kon Tum", 6115, 750, 5365, 11000, 8715, 82718],
        ["Gia Lai", 2026, 946, 1080, 6843, 517, 108373],
        ["Đắk Lắk", 6134, 670, 5464, 1131, 3944, 60120],
        ["Đắk Nông", 2252, 191, 2062, 218, 1636, 32371],
        ["Lâm Đồng", 4740, 651, 4089, None, None, 351187],
        ["Đông Nam Bộ", 3516, 2612, 904, 3675, 26004, 98181],
        ["Bình Phước", 762, 762, None, 930, 13621, 20731],
        ["Tây Ninh", 1293, 1004, 289, 1158, 10354, 42986],
        ["Đồng Nai", 390, 230, 160, 422, 889, 2000],
        ["Bà Rịa-Vũng Tàu", 825, 370, 455, 422, 985, 1194],
        ["TP Hồ Chí Minh", 246, 246, None, 743, 155, 31270],
        ["ĐB. sông Cửu Long", 5421, 3834, 1587, 5364, 1565, 52531],
        ["Long An", 153, 153, None, 198, None, 300],
        ["Tiền Giang", 101, 101, None, None, None, 1200],
        ["Bến Tre", 72, 55, 17, 336, None, 3461],
        ["Trà Vinh", 148, 148, None, 459, 65, 4270],
        ["Đồng Tháp", 220, 50, 170, None, None, 3260],
        ["An Giang", 988, 988, None, 1270, None, 2279],
        ["Kiên Giang", 200, 200, None, 541, 1500, 13886],
        ["Sóc Trăng", 421, 421, None, 71, None, 1355],
        ["Bạc Liêu", 1100, 1100, None, 2489, None, 3900],
        ["Cà Mau", 2018, 618, 1400, None, None, 17320],
        ["Trung ương", 8356, 4512, 3844, 13363, 6510, 93388]
    ]

    full_data = data_north + data_south
    regional_list = ["Miền bắc", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", 
                     "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    for row in full_data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc in ["Cả nước", "Trung ương"]: gl = "National"
        
        # [Name, Total, PHDD, KT, ChamSoc, KhoanhNuoi, KhoanBaoVe]
        # Unit: ha (Area_Planted usually for new forest).
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        # Cham Soc
        v = normalize_number(row[4])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng trồng", "sub_item": "Chăm sóc"}, {"attribute": "Area_Care", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        # Khoanh nuoi
        v = normalize_number(row[5])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tái sinh", "sub_item": "Khoanh nuôi"}, {"attribute": "Area_Regenerated", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        # Khoan bao ve
        v = normalize_number(row[6])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": "Khoán bảo vệ"}, {"attribute": "Area_Protected", "value": v, "unit": "ha", "data_type": "Actual"}))

    return records

def parse_pl9():
    # Fishery National
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL9", "source_file": "2010_12_Phuluc_T12_2010_PL9.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"} 
    
    # [Item, 12M_Est]
    data = [
        ["Tổng sản lượng", 5157.6],
        ["Sản lượng khai thác", 2450.8],
        ["Khai thác biển", 2303.8],
        ["Khai thác nội địa", 147],
        ["Sản lượng nuôi trồng", 2706.8]
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Fishery", "commodity": row[0]}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/12"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl7()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL7.json"))
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl8()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL8.json"))
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl9()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL9.json"))
    print("Successfully parsed PL7-PL9 for December 2010 (Forestry, Fishery).")
