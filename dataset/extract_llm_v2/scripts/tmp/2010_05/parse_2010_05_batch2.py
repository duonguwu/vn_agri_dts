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
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "Vùng Duyên hải miền Trung": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ", "Vùng Đông Nam bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", 
        "ĐB. sông Hồng": "Đồng bằng sông Hồng", "Trung du và miền núi phía Bắc": "Đông Bắc"
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

def parse_pl3b():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL3b", "source_file": "2010_05_PHULUC_T05_2010_PL3b.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Monthly", "report_date": "2010-05-15"}
    
    # [Name, CCN_Total, DauTuong, Lac, Vung, ThuocLa, MiaTrongMoi, Bong, DayLac, Rau, Dau]
    data = [
        ["Miền Nam", 203198, 20158, 51097, 20138, 12978, 96623, 1006, 1198, 188232, 26482],
        ["D.H Nam Trg Bộ", 50356, 1199, 20631, 1901, 874, 25276, 434, 41, 25256, 25256],
        ["TP Đà Nẵng", 735, None, 618, None, None, 117, None, None, 369, 78],
        ["Quảng Nam", 9232, None, 8264, None, 502, 289, 177, None, 8500, 3400],
        ["Quảng Ngãi", 3561, None, 3561, None, None, None, None, None, 5572, 1712],
        ["Bình Định", 12095, 881, 7538, 1475, None, 2201, None, None, 8159, 1039],
        ["Phú Yên", 14676, 318, 540, 426, 372, 12722, 257, 41, 2456, 1687],
        ["Khánh Hoà", 10057, None, 110, None, None, 9947, None, None, 200, None],
        ["Tây Nguyên", 29408, 11057, 1183, 0, 6489, 10679, 0, 0, 35491, 8444],
        ["Kon Tum", 4022, None, 58, None, 1867, 2097, None, None, 8700, 92],
        ["Gia Lai", 12140, None, 211, None, 4622, 7307, None, None, 8108, 2652],
        ["Đắc Lắc", 2677, 1763, 914, None, None, None, None, None, 3312, 5085],
        ["Đắc Nông", 9369, 9294, None, None, None, 75, None, None, 1552, 200],
        ["Lâm Đồng", 1200, None, None, None, None, 1200, None, None, 13819, 415],
        ["Đông Nam Bộ", 46359, 543, 18601, 7936, 5575, 13132, 572, 0, 35662, 7528],
        ["TP Hồ Chí Minh", 2790, None, 1000, None, None, 1790, None, None, 5746, None],
        ["Ninh Thuận", 1275, None, None, 190, 32, 481, 572, None, 6825, 895],
        ["Bình Phước", 140, None, 130, 10, None, None, None, None, 816, None],
        ["Tây Ninh", 25683, None, 13085, 1292, 4611, 6695, None, None, 7704, 2677],
        ["Bình Dương", 929, None, 630, None, None, 299, None, None, 1955, 150],
        ["Đồng Nai", 9651, 291, 2251, 3128, 800, 3181, None, None, 6298, 1911],
        ["Bình Thuận", 5194, 241, 1064, 3316, 31, 542, None, None, 2118, 1763],
        ["Bà Rịa-V.Tàu", 697, 11, 441, None, 101, 144, None, None, 4200, 132],
        ["ĐBS Cửu Long", 77075, 7359, 10682, 10301, 40, 47536, 0, 1157, 91823, 2594],
        ["Long An", 21503, None, 6881, 1741, None, 12881, None, None, 8460, None],
        ["Đồng Tháp", 8665, 4879, 16, 3646, 15, 24, None, 85, 5083, None],
        ["An Giang", 1352, 322, 175, 836, 1, 18, None, None, 7396, 1181],
        ["Tiền Giang", 0, None, None, None, None, None, None, None, 19198, None],
        ["Vĩnh Long", 1989, 1101, 29, 205, None, 144, None, 510, 9845, 243],
        ["Bến Tre", 6321, None, 122, None, None, 5992, None, 207, 2317, 3],
        ["Kiên Giang", 0, None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", 4613, 702, 14, 3873, 24, None, None, None, 2994, 325],
        ["Hậu Giang", 13123, None, None, None, None, 13123, None, None, 872, 77],
        ["Trà Vinh", 8782, 224, 3445, None, None, 4758, None, 355, 14649, 765],
        ["Sóc Trăng", 10596, None, None, None, None, 10596, None, None, 21009, None],
        ["Bạc Liêu", 131, 131, None, None, None, None, None, None, None, None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        # CCN
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None)]
        for idx, (cmd, sub) in enumerate(items):
            v = normalize_number(row[idx+2])
            if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        # Rau
        v = normalize_number(row[9])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        # Dau
        v = normalize_number(row[10])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))

    return records

def parse_pl4a():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL4a", "source_file": "2010_05_PHULUC_T05_2010_PL4a.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Cumulative", "report_date": "2010-05-15"}
    
    # [Item, Unit, Actual]
    data = [
        ["Trồng rừng tập trung", "1000 ha", 49.2],
        ["Rừng phòng hộ, đặc dụng", "1000 ha", 6.1],
        ["Rừng sản xuất", "1000 ha", 43.2],
        ["Chăm sóc rừng trồng", "1000 ha", 132.3],
        ["Trồng cây phân tán", "Trieu cay", 89.4],
        ["Khoanh nuôi tái sinh, trồng dặm", "1000 ha", 609.5],
        ["Khoán bảo vệ rừng", "1000 ha", 1733.0],
        ["Khai thác gỗ", "1000 m3", 1481.0],
    ]
    
    for row in data:
        item, unit, val = row
        u = "1000_ha"
        if unit == "Trieu cay": u = "million_tree"
        elif "m3" in unit: u = "1000_m3"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": val, "unit": u, "data_type": "Actual"}))
    return records

def parse_pl4b():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL4b", "source_file": "2010_05_PHULUC_T05_2010_PL4b.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Cumulative", "report_date": "2010-05-15"}
    
    # [Name, TrongRung_Total, PHDD, KinhTe, ChamSoc]
    data = [
        ["Cả nước", 49210, 6052, 43158, 132294],
        ["Miền bắc", 46685, 4527, 42158, 112742],
        ["ĐB. sông Hồng", 5765, 727, 5038, 46037],
        ["Hà Nội", 104, 42, 62, None],
        ["Vĩnh Phúc", 50, None, 50, None],
        ["Quảng Ninh", 5520, 640, 4880, 45000],
        ["Hải Phòng", None, None, None, 810],
        ["Hà Nam", 46, None, 46, 55],
        ["Nam Định", 45, 45, None, 172],
        ["Trung du và miền núi phía Bắc", 30656, 3143, 27513, 41271],
        ["Hà Giang", 500.0, None, 500, 25100],
        ["Cao Bằng", 90, 20, 70, None],
        ["Bắc Kạn", 2324, 254, 2070, None],
        ["Tuyên Quang", 3238, 298, 2940, None],
        ["Lào Cai", 630, 335, 295, 1050],
        ["Yên Bái", 8408, None, 8408, None],
        ["Thái Nguyên", 3334, 549.0, 2785, None],
        ["Lạng Sơn", 1921, 337, 1584, 5823],
        ["Bắc Giang", 1718, 220, 1498, None],
        ["Phú Thọ", 4718, 342, 4376, None],
        ["Điện Biên", 616, 287, 329, 798],
        ["Hoà Bình", 3159, 501, 2658, 8500],
        ["Bắc Trung Bộ", 10264, 657, 9607, 25434],
        ["Thanh Hoá", 6500, 300, 6200, 4857],
        ["Nghệ An", 3377, 357, 3020, 17880],
        ["Hà Tĩnh", 387, None, 387, None],
        ["Quảng Bình", None, None, None, 740],
        ["Miền Nam", 25.0, 25.0, 0.0, 19552.0],
        ["D.H Nam Trung Bộ", 25, 25, 0, 19263],
        ["Đà Nẵng", 20, 20, None, 169],
        ["Bình Định", 5, 5, None, 8094],
        ["Phú Yên", None, None, None, 11000],
        ["Trung uơng", 2500, 1500, 1000, None]
    ]
    
    regional_list = ["Miền bắc", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", "Miền Nam", "D.H Nam Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Cả nước": gl = "National"
        if loc == "Trung uơng": gl = "National"; loc = "Cả nước - Trung ương"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng sản xuất", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng trồng", "sub_item": None}, {"attribute": "Area_Tended", "value": v/1.0, "unit": "ha", "data_type": "Actual"})) # Chăm sóc

    return records

def parse_pl5():
    metadata = {"year": 2010, "month": 5, "appendix_number": "PL5", "source_file": "2010_05_PHULUC_T05_2010_PL5.md"}
    records = []
    t = {"year": 2010, "month": 5, "period_type": "Cumulative", "report_date": "2010-05-15"}
    
    data = [
        ["Tổng sản lượng thủy sản", 1883],
        ["Sản lượng khai thác", 1011],
        ["Khai thác biển", 956],
        ["Khai thác nội địa", 55],
        ["Sản lượng nuôi trồng", 872]
    ]
    
    for row in data:
        item, val = row
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(val), "unit": "1000_ton", "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/05"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl3b()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL3b.json"))
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl4a()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL4a.json"))
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl4b()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL4b.json"))
    save_json({"metadata": {"year": 2010, "month": 5}, "records": parse_pl5()}, os.path.join(out_dir, "2010_05_PHULUC_T05_2010_PL5.json"))
    print("Successfully parsed PL3b, PL4a, PL4b, PL5 for May 2010.")
