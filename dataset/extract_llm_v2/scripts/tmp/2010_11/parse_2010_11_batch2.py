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
        "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Miền Nam": "Miền Nam", "Cả nước": "Cả nước", "Trung uơng": "Trung ương",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Hà Nội (mở rộng)": "Hà Nội"
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
    elif norm_loc == "Miền bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl4():
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL4", "source_file": "2010_11_Phuluc_T11_2010_PL4.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Monthly", "report_date": "2010-11-15"}
    
    # [Loc, CCN_Total, DauTuong, Lac, Vung, ThuocLa, Mia, Bong, Day, Rau, Dau]
    data = [
        ["Miền Nam", 343366, 31661, 87200, 28290, 13495, 172117, 5140, 5463, 351433, 86061], # Dau 86061 or 15690? Raw string has "86,061<br>15,690". Header says Dau cac loai. Maybe first is Dau cac loai, second is something else? Or two values? Let's check prev month. Oct PL4 had "64,633<br>12,324".
        # Inspecting PL4 Oct again. Last col header "Đậu các loại". Raw text has <br>. Maybe Beans vs Peas? Or Total vs Soy? 
        # But Soy (Dau tuong) is Col 2 (index 2).
        # Let's assume Top value is "Rau đậu các loại" total? No, Col 10 is Rau cac loai. Col 11 is Dau cac loai.
        # Maybe Total and Harvested? Or Planted area vs Harvested area?
        # Let's take the first value as Planted Area for now.
        
        ["D.H Nam Trg Bộ", 80927, 1563, 25312, 6699, 1042, 45548, 722, 41, 42876, 42876],
        ["TP Đà Nẵng", 1195, None, 618, 211, None, 366, None, None, 738, 210],
        ["Quảng Nam", 13252, None, 9772, 2101, 502, 700, 177, None, 9200, 3400],
        ["Quảng Ngãi", 12026, 375, 5457, None, None, 6194, None, None, 12316, 3016],
        ["Bình Định", 13426, 862, 8341, 1807, None, 2416, None, None, 13342, 1981],
        ["Phú Yên", 24599, 326, 979, 2580, 540, 19838, 295, 41, 5040, 6350],
        ["Khánh Hoà", 16429, None, 145, None, None, 16034, 250, None, 2240, 733],
        ["Tây Nguyên", 69155, 20096, 17054, 1436, 6539, 22469, 1561, 0, 48947, 29794],
        ["Kon Tum", 4108, None, 144, None, 1867, 2097, None, None, 941, 450],
        ["Gia Lai", 13629, None, 800, 900, 4622, 7307, None, None, 8108, 8158],
        ["Đắc Lắc", 30963, 8316, 8710, 536, 50, 11790, 1561, None, 5543, 14142],
        ["Đắc Nông", 18855, 11580, 7200, None, None, 75, None, None, 1855, 5744],
        ["Lâm Đồng", 1600, 200, 200, None, None, 1200, None, None, 32500, 1300],
        ["Đông Nam Bộ", 95551, 2300, 29185, 9098, 5752, 46359, 2857, 0, 72091, 33380],
        ["TP Hồ Chí Minh", 2690, None, 900, None, None, 1790, None, None, 12591, None],
        ["Ninh Thuận", 1800, None, 135, 461, 32, 600, 572, None, 8820, 2097],
        ["Bình Phước", 1510, 300, 1200, 10, None, None, None, None, 816, 3301],
        ["Tây Ninh", 51323, None, 16399, 1564, 4670, 28690, None, None, 19350, 7137],
        ["Bình Dương", 2203, None, 1904, None, None, 299, None, None, 5820, 823],
        ["Đồng Nai", 13719, 1623, 1560, 281, 855, 9380, 20, None, 13334, 7845],
        ["Bình Thuận", 20863, 366, 5900, 6782, 94, 5456, 2265, None, 6935, 11696],
        ["Bà Rịa-V.Tàu", 1443, 11, 1187, None, 101, 144, None, None, 4425, 481],
        ["ĐBS Cửu Long", 97733, 7702, 15649, 11057, 162, 57741, 0, 5422, 187519, 7197],
        ["Long An", 25032, None, 7000, 1275, 122, 13991, None, 2644, 13036, None],
        ["Đồng Tháp", 9089, 4935, 125, 3761, 15, 164, None, 89, 10512, None],
        ["An Giang", 1586, 556, 175, 836, 1, 18, None, None, 7396, 1181],
        ["Tiền Giang", 257, None, None, None, None, 257, None, None, 35106, 170],
        ["Vĩnh Long", 3159, 744, 53, 1117, None, 137, None, 1108, 21041, 438],
        ["Bến Tre", 6190, None, 132, None, None, 5865, None, 193, 5833, 3],
        ["Kiên Giang", 4106, None, None, None, None, 4106, None, None, 2033, None],
        ["Cần Thơ", 8395, 745, 3558, 4068, 24, None, None, None, 4309, 600],
        ["Hậu Giang", 13173, None, None, None, None, 13173, None, None, 16739, 77],
        ["Trà Vinh", 12111, 224, 4401, None, None, 6098, None, 1388, 27602, 1041],
        ["Sóc Trăng", 14504, 367, 205, None, None, 13932, None, None, 33513, 3687],
        ["Bạc Liêu", 131, 131, None, None, None, None, None, None, 10400, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            if idx+2 < len(row):
                v = normalize_number(row[idx+2])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        if len(row) > 9:
            v = normalize_number(row[9])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        if len(row) > 10:
            v = normalize_number(row[10]) # Taking the first value if <br> was present, as cleaned list in data var
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))

    return records

def parse_pl5():
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL5", "source_file": "2010_11_Phuluc_T11_2010_PL5.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"}
    
    # [Item, Val_11M]
    data = [
        ["Trồng rừng tập trung", 227.2],
        ["Rừng phòng hộ, đặc dụng", 54.0],
        ["Rừng sản xuất", 173.2],
        ["Chăm sóc rừng trồng", 300.7],
        ["Trồng cây phân tán", 175.6],
        ["Khoanh nuôi tái sinh, trồng dặm", 761.5],
        ["Khoán bảo vệ rừng", 2589.9],
        ["Khai thác gỗ", 3566.8]
    ]
    
    for row in data:
        item, val = row
        u = "1000_ha"
        if "gỗ" in item: u = "1000_m3"
        elif "phân tán" in item: u = "million_tree"
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))
    return records

def parse_pl6():
    # PL6 in Nov is Detailed Forestry again (North and South).
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL6", "source_file": "2010_11_Phuluc_T11_2010_PL6.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"}
    
    # We need to extract data from PL6. It has North and South tables.
    # The file view in Step 319 shows typical structure.
    
    # Col 2: Name
    # Col 3: Total
    # Col 4: PHDD
    # Col 5: Kinh Te
    # Col 6: Cham Soc
    # Col 7: Khoanh Nuoi
    # Col 8: Khoan Bao Ve
    
    # I will put manually extracted data here to be safe and accurate.
    # NORTH
    data_north = [
        ["Cả nước", 227165, 53973, 173193],
        ["Miền bắc", 174489, 36904, 137585],
        ["ĐB. sông Hồng", 19585, 7180, 12405],
        ["Hà Nội", 212, 162, 50],
        ["Vĩnh Phúc", 365, 170, 195],
        ["Bắc Ninh", 50, 50, None],
        ["Quảng Ninh", 15124, 3147, 11977],
        ["Hải Dương", 130, 20, 110],
        ["Hải Phòng", 2190, 2190, None],
        ["Thái Bình", 993, 993, None],
        ["Hà Nam", 73, None, 73],
        ["Nam Định", 328, 328, None],
        ["Ninh Bình", 120, 120, None],
        ["TD và MN phía Bắc", 121184, 25775, 95409],
        ["Hà Giang", 15554, 4305, 11249],
        ["Cao Bằng", 1880, 980, 900],
        ["Bắc Kạn", 9652, 1052, 8600],
        ["Tuyên Quang", 15560, 1976, 13584],
        ["Lào Cai", 9332, 2402, 6930],
        ["Yên Bái", 14328, 2800, 11528],
        ["Thái Nguyên", 6454, 1410, 5044],
        ["Lạng Sơn", 8564, 2264, 6300],
        ["Bắc Giang", 7244, 450, 6794],
        ["Phú Thọ", 8897, 342, 8555],
        ["Điện Biên", 3030, 573, 2457],
        ["Lai Châu", 5404, 1911, 3493],
        ["Sơn La", 5485, 3510, 1975],
        ["Hoà Bình", 9800, 1800, 8000],
        ["Bắc Trung Bộ", 33720, 3949, 29771],
        ["Thanh Hoá", 15564, 1544, 14020],
        ["Nghệ An", 14146, 1021, 13125],
        ["Hà Tĩnh", 870, 515, 355],
        ["Quảng Bình", 522, 65, 457],
        ["Quảng Trị", 2498, 764, 1734],
        ["Thừa Thiên Huế", 120, 40, 80]
    ]
    
    # SOUTH
    data_south = [
        ["Miền Nam", 44690, 12927, 31764],
        ["D.H Nam Trung Bộ", 17955, 4609, 13346],
        ["Đà Nẵng", 20, 20, None],
        ["Quảng Nam", 410, 140, 270],
        ["Quảng Ngãi", 600, 600, None],
        ["Bình Định", 4310, 893, 3417],
        ["Phú Yên", 5000, 1000, 4000],
        ["Khánh Hoà", 630, 280, 350],
        ["Ninh Thuận", 860, 860, None],
        ["Bình Thuận", 6125, 816, 5309],
        ["Tây Nguyên", 18872, 2501, 16372],
        ["Kon Tum", 6060, 426, 5634],
        ["Gia Lai", 880, 760, 120],
        ["Đắk Lắk", 5984, 520, 5464],
        ["Đắk Nông", 2252, 191, 2062],
        ["Lâm Đồng", 3696, 604, 3092],
        ["Đông Nam Bộ", 3248, 2410, 838],
        ["Bình Phước", 762, 762, None],
        ["Tây Ninh", 1254, 1004, 250],
        ["Đồng Nai", 390, 230, 160],
        ["Bà Rịa-Vũng Tàu", 782, 354, 428],
        ["TP Hồ Chí Minh", 60, 60, None],
        ["ĐB. sông Cửu Long", 4615, 3407, 1208],
        ["Long An", 30, 30, None],
        ["Tiền Giang", 85, 85, None],
        ["Bến Tre", 80, 55, 25],
        ["Trà Vinh", 148, 148, None],
        ["Đồng Tháp", 220, 50, 170],
        ["An Giang", 910, 910, None],
        ["Hậu Giang", 200, 200, None],
        ["Sóc Trăng", 421, 421, None],
        ["Bạc Liêu", 1100, 1100, None],
        ["Cà Mau", 1421, 408, 1013],
        ["Trung ương", 7986, 4142, 3844]
    ]
    
    full_data = data_north + data_south
    regional_list = ["Miền bắc", "ĐB. sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ", 
                     "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    for row in full_data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc in ["Cả nước", "Trung ương"]: gl = "National"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/11"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl4()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl5()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL5.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl6()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL6.json"))
    print("Successfully parsed PL4-PL6 for November 2010.")
