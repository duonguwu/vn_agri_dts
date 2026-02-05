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
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
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
    elif norm_loc == "Miền Bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    elif norm_loc == "Miền bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    elif norm_loc == "Trung uơng":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước - Trung ương"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL6", "source_file": "2010_08_Phuluc_T08_2010_PL6.md"}
    records = []
    # 8 months
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    data = [
        ["Trồng rừng tập trung", 149.6],
        ["Rừng phòng hộ, đặc dụng", 31.9],
        ["Rừng sản xuất", 117.7],
        ["Chăm sóc rừng trồng", 275.6],
        ["Trồng cây phân tán", 137.1], # Trieu cay
        ["Khoanh nuôi tái sinh, trồng dặm", 721.7],
        ["Khoán bảo vệ rừng", 2368.0],
        ["Khai thác gỗ", 2494.2] # 1000 m3
    ]
    
    for row in data:
        item, val = row
        u = "1000_ha"
        if "gỗ" in item: u = "1000_m3"
        elif "phân tán" in item: u = "million_tree"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))
    return records

def parse_pl7():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL7", "source_file": "2010_08_Phuluc_T08_2010_PL7.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    # [Loc, Total, PHDD, KinhTe, ChamSoc, KhoanhNuoi, KhoanBaoVe]
    data = [
        ["Cả nước", 149640, 31941, 117699, 275597, 721709, 2368011],
        ["Miền bắc", 132053, 24174, 107879, 214294, 602064, 1248291],
        ["ĐB. sông Hồng", 14492, 4091, 10401, 46883, 19535, 80803],
        ["Hà Nội", 212, 162, 50, 197, None, 8846],
        ["Vĩnh Phúc", 195, None, 195, 204, 502, 11157],
        ["Bắc Ninh", 30, 30, None, None, None, None],
        ["Quảng Ninh", 12661, 2688, 9973, 45000, 5981, 33775],
        ["Hải Dương", 130, 20, 110, 130, None, 3042],
        ["Hải Phòng", 500, 500, None, 810, 1855, 11500],
        ["Hưng Yên", None, None, None, None, None, None],
        ["Thái Bình", 454, 454, None, None, None, 7000],
        ["Hà Nam", 73, None, 73, 55, 40, 3674],
        ["Nam Định", 127, 127, None, 397, None, 1065],
        ["Ninh Bình", 110, 110, None, 90, 11157, 744],
        ["TD và MN phía Bắc", 97884, 18221, 79663, 101535, 484735, 810700],
        ["Hà Giang", 9725.0, 2685, 7040, 24584, 44695, 93471],
        ["Cao Bằng", 867, 557, 310, 210, 15050, 19020],
        ["Bắc Kạn", 9612, 1048, 8564, 1181, 18107, 20744],
        ["Tuyên Quang", 13396, 1485, 11911, 6270, 28597, 180140],
        ["Lào Cai", 5160, 1182, 3978, 2036, 5843, 101312],
        ["Yên Bái", 11980, 860, 11120, 5999, 19671, 25000],
        ["Thái Nguyên", 6361, 1306.0, 5055, 4508, 4578.0, 23413],
        ["Lạng Sơn", 8710, 1442, 7268, 6356, 6856, 16351],
        ["Bắc Giang", 5662, 450, 5212, 3330, 1230, 28321],
        ["Phú Thọ", 8876, 321, 8555, 27771, 1550, 32445],
        ["Điện Biên", 2030, 573, 1457, 798, 55350, 59163],
        ["Lai Châu", 4533, 1735, 2798, 1267, 101722.0, 131922],
        ["Sơn La", 5521, 3545.0, 1976, 8725, 179189, 20381],
        ["Hoà Bình", 5451, 1032, 4419, 8500, 2297, 59017],
        ["Bắc Trung Bộ", 19677, 1862, 17815, 65876, 97794, 356788],
        ["Thanh Hoá", 11450, 1116, 10334, 14154, 15417, 63621],
        ["Nghệ An", 7840, 713, 7127, 18615, 55000, 105000],
        ["Hà Tĩnh", 387, 33, 354, 14570, 9082, 47676],
        ["Quảng Bình", None, None, None, 740, 9000, 55337],
        ["Quảng Trị", None, None, None, 2881, 1319, 26654],
        ["Thừa Thiên Huế", None, None, None, 14916, 7976, 58500],
        ["Miền Nam", 12895.0, 5261, 7634, 53644, 115669, 1065005],
        ["D.H Nam Trung Bộ", 456, 456, 0, 43631, 91472, 296792],
        ["Đà Nẵng", 20, 20, None, 169, 121, 15000],
        ["Quảng Nam", None, None, None, 9050, 23500, 35000],
        ["Quảng Ngãi", None, None, None, 4735, 2100, 27346],
        ["Bình Định", 10, 10, None, 8894, 50143, 41324],
        ["Phú Yên", None, None, None, 11000, 3073, 22558],
        ["Khánh Hoà", None, None, None, 450, 1014, 8498],
        ["Ninh Thuận", 213, 213, None, None, 1000, 41705],
        ["Bình Thuận", 213, 213, None, 9333, 10521, 105361],
        ["Tây Nguyên", 10498, 2913, 7585, 7387, 14295, 628183],
        ["Kon Tum", 2250, 500, 1750, 1058, 8715, 75476],
        ["Gia Lai", 880, 760, 120, 4980, None, 108280],
        ["Đắk Lắk", 4255, 120, 4135, 1131, 3944, 60120],
        ["Đắk Nông", 2223, 1103, 1120, 218, 1636, 32371],
        ["Lâm Đồng", 890, 430, 460, None, None, 351936],
        ["Đông Nam Bộ", 1009, 960, 49, 1678, 9902, 94474],
        ["Bình Phước", None, None, None, None, None, 19624],
        ["Tây Ninh", 595, 546, 49, 935, 7873, 40234],
        ["Bình Dương", None, None, None, None, None, None],
        ["Đồng Nai", None, None, None, None, 889, 2000],
        ["Bà Rịa-Vũng Tàu", 354, 354, None, None, 985, 1346],
        ["TP Hồ Chí Minh", 60, 60, None, 743, 155, 31270],
        ["ĐB. sông Cửu Long", 932, 932, 0, 948, 0, 45556],
        ["Long An", None, None, None, 198, None, 300],
        ["Tiền Giang", None, None, None, None, None, 1200],
        ["Bến Tre", 22, 22, None, 77, None, 1700],
        ["Trà Vinh", None, None, None, None, None, 3000],
        ["Vĩnh Long", None, None, None, None, None, None],
        ["Đồng Tháp", None, None, None, None, None, 3260],
        ["An Giang", 910, 910, None, 61, None, 2000],
        ["Kiên Giang", None, None, None, 541, None, 13886],
        ["Cần Thơ", None, None, None, None, None, None],
        ["Hậu Giang", None, None, None, None, None, 1300],
        ["Sóc Trăng", None, None, None, 71, None, 790],
        ["Bạc Liêu", None, None, None, None, None, 800],
        ["Cà Mau", None, None, None, None, None, 17320],
        ["Trung uơng", 4692, 2506, 2186, 7659, 3976, 54715]
    ]
    
    regional_list = ["Miền bắc", "ĐB. sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ", 
                     "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
                     
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Cả nước": gl = "National"
        if loc == "Trung uơng": gl = "National"; loc = "Cả nước - Trung ương"
        
        try:
            v_total = normalize_number(row[1])
            if v_total: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_total/1.0, "unit": "ha", "data_type": "Actual"}))
            
            v_phdd = normalize_number(row[2])
            if v_phdd: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v_phdd/1.0, "unit": "ha", "data_type": "Actual"}))
            
            v_kt = normalize_number(row[3])
            if v_kt: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": v_kt/1.0, "unit": "ha", "data_type": "Actual"}))
            
            v_cs = normalize_number(row[4])
            if v_cs: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng trồng", "sub_item": None}, {"attribute": "Area_Tended", "value": v_cs/1.0, "unit": "ha", "data_type": "Actual"}))
            
            v_kn = normalize_number(row[5])
            if v_kn: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": None}, {"attribute": "Area_Regenerated", "value": v_kn/1.0, "unit": "ha", "data_type": "Actual"}))
            
            v_kbv = normalize_number(row[6])
            if v_kbv: records.append(create_record(metadata, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": None}, {"attribute": "Area_Protected", "value": v_kbv/1.0, "unit": "ha", "data_type": "Actual"}))
        except: pass
        
    return records

def parse_pl8():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL8", "source_file": "2010_08_Phuluc_T08_2010_PL8.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    # 8 months
    data = [
        ["Tổng sản lượng thủy sản", 3408],
        ["Sản lượng khai thác", 1682],
        ["Khai thác biển", 1605],
        ["Khai thác nội địa", 77],
        ["Sản lượng nuôi trồng", 1726]
    ]
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Fishery", "commodity": row[0]}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Actual"}))
    return records

def parse_pl9():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL9", "source_file": "2010_08_Phuluc_T08_2010_PL9.md"}
    records = []
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    # [Item, Value_8months] -> Col 4 in PL9 (Ước TH 8T/2010)
    data = [
        ["Đầu tư Thuỷ lợi", 2517000],
        ["Đầu tư Nông nghiệp", 400900],
        ["Đầu tư Lâm nghiệp", 162000],
        ["Đầu tư Thuỷ sản", 83500],
        ["Khoa học - Công nghệ", 33500],
        ["Giáo dục - Đào tạo", 65000],
        ["Các ngành khác", 61000],
        ["Chương trình mục tiêu", 34000],
        ["Vốn đầu tư theo các mục tiêu", 162500],
        ["Vốn chuẩn bị đầu tư", 32000],
        ["Vốn trái phiếu Chính phủ", 3116000],
        ["Các dự án có trong QĐ171", 2350000],
        ["Các dự án cấp bách bổ sung", 335000],
        ["Các dự án thuỷ lợi ĐBSHồng", 431000],
        ["Tổng vốn đầu tư", 6667400]
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/08"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl6()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL6.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl7()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL7.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl8()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL8.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl9()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL9.json"))
    print("Successfully parsed PL6-PL9 for August 2010.")
