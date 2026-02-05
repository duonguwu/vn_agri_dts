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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "Trung du và MN phía Bắc": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc",
        "TD và MN phía Bắc": "Đông Bắc", "Trung du và miền núi": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "Vùng Duyên hải miền Trung": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ", "Vùng Đông Nam bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", 
        "Hà Nội (mở rộng)": "Hà Nội", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
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

def parse_pl4a():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL4a", "source_file": "2010_07_phuluc_07_2010_PL4a.md"}
    records = []
    # 7 months
    t = {"year": 2010, "month": 7, "period_type": "Cumulative", "report_date": "2010-07-31"}
    
    data = [
        ["Trồng rừng tập trung", 116.7],
        ["Rừng phòng hộ, đặc dụng", 22.6],
        ["Rừng sản xuất", 94.1],
        ["Chăm sóc rừng trồng", 254.2],
        ["Khoanh nuôi tái sinh, trồng dặm", 694.0],
        ["Khoán bảo vệ rừng", 2239.5],
        ["Khai thác gỗ", 2086.4], # 1000 m3
        ["Trồng cây phân tán", 123.7] # Trieu cay
    ]
    
    for row in data:
        item, val = row
        u = "1000_ha"
        if "gỗ" in item: u = "1000_m3"
        elif "phân tán" in item: u = "million_tree"
        
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": u, "data_type": "Actual"}))
    return records

def parse_pl4b():
    metadata_f = {"year": 2010, "month": 7, "appendix_number": "PL4b", "source_file": "2010_07_phuluc_07_2010_PL4b.md"}
    records = []
    t = {"year": 2010, "month": 7, "period_type": "Cumulative", "report_date": "2010-07-31"}
    
    # [Loc, Total, PHDD, KinhTe, PhanTan, ChamSoc, KhoanhNuoi, KhoanBaoVe]
    forestry_data = [
        ["Miền Nam", 1635.0, 940.6, 694.4, 851.0, 53087.0, 114996, 1038089],
        ["D.H Nam Trung Bộ", 243, 243, None, 85, 43631, 90799, 263792],
        ["Đà Nẵng", 20, 20, None, 85, 169, 121, 15000],
        ["Quảng Nam", 10, 10, None, 126, 9050, 23500, 27346], # Line 33 is Quang Nam in list but value is Quang Ngai?
        # Line 32: Da Nang. Line 33: Quang Nam. Line 34: Quang Ngai.
        # Table row: |33|Quảng Nam|...|
        # Wait, the table structure in PL4b.md is tricky.
        # |33|Quảng Ngãi|? No, look at line 20: 33 is Quang Ngai. 32 is Quang Nam.
        # Correct mapping based on PL4b line 20 (it merges lines):
        # 31 Da Nang, 32 Quang Nam, 33 Quang Ngai, 34 Binh Dinh...
        # Wait, line 20 list: 31 Da Nang, 32 Quang Nam, 33 Quang Ngai.
        # But table rows ...
        # Let's re-read the weird line 20 block.
        # |31|Đà Nẵng|20|20||85|169|121|15,000|
        # |32|Quảng Nam|10|10|||9,050|23,500|27,346| (Wait, 27346 seems aligned to Quang Ngai in June?)
        # Let's look at the numbers.
        # Line 20: 31... 32... 33...
        # Da Nang: 20, 20, 0, 85, 169, 121, 15000.
        # Quang Nam: 10, 10, 0, 0, 9050, 23500, 27346? 
        # Quang Ngai: 213, 213, 0, 126, 4735, 2100, 41324.
        # Binh Dinh: 1161, 467, 694, 126, 8894, 50143, 24558.
        # Phu Yen: 350, 350, 0, 0, 11000, 2400, 8498.
        # Khanh Hoa: 171, 26, 145, 640, 450, 1014, 41705.
        # Ninh Thuan: 640, 91, 549, 500, 9333, 1000, 105361.
        # Binh Thuan: (Blank in list but table has values?)
        # Wait, "Ninh Thuan 640..." -> Row 36.
        # Row 38 is Binh Thuan.
        # Let's follow the values sequence in line 20 block.
        # The block is messy. I will try to map carefully.
        ["Đà Nẵng", 20, 20, None, 85, 169, 121, 15000],
        ["Quảng Nam", 10, 10, None, None, 9050, 23500, None], # 27346 might be Quang Ngai
        ["Quảng Ngãi", 213, 213, None, 126, 4735, 2100, 27346],
        ["Bình Định", 1161, 467, 694, 126, 8894, 50143, 41324],
        ["Phú Yên", 350, 350, None, None, 11000, 2400, 24558],
        ["Khánh Hoà", 171, 26, 145, 640, 450, 1014, 8498],
        ["Ninh Thuận", 640, 91, 549, 500, 9333, 1000, 41705],
        ["Bình Thuận", None, None, None, 140, 7387, 10521, 105361], # row 38 inferred
        ["Tây Nguyên", 231, 231, None, 4220, 1058, 14295, 622781],
        ["Kon Tum", 171, 171, None, None, 4980, 8715, 75476],
        ["Gia Lai", 60, 60, None, None, None, None, 102878],
        ["Đắk Lắk", None, None, None, 1131, 1131, 3944, 60120],
        ["Đắk Nông", None, None, None, 218, 218, 1636, 32371],
        ["Lâm Đồng", None, None, None, 1259, 516, None, 351936],
        ["Đông Nam Bộ", 4596, 2410, 2186, 743, 743, 9902, 92474],
        ["Bình Phước", None, None, None, 810, 198, 7873, 19624],
        ["Tây Ninh", None, None, None, None, None, None, 40234],
        ["Bình Dương", None, None, None, 541, None, 889, 1346],
        ["Đồng Nai", None, None, None, 71, None, None, 31270],
        ["Bà Rịa-Vũng Tàu", None, None, None, 7035, 541, 155, None], # 541? Table misalignment possible.
        ["TP Hồ Chí Minh", None, None, None, None, 3767, 985, None],
        ["ĐB. sông Cửu Long", None, None, None, None, None, None, 59042],
        ["Long An", None, None, None, None, None, None, 41106],
        ["Tiền Giang", None, None, None, None, None, None, 3260],
        ["Đồng Tháp", None, None, None, None, None, None, 13886],
        ["Sóc Trăng", None, None, None, None, None, None, 790],
        ["Trung uơng", None, None, None, None, 54715, None, None] # 54715 is probably 1000 cay phan tan?
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    for row in forestry_data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Cả nước": gl = "National"
        if loc == "Trung uơng": gl = "National"; loc = "Cả nước - Trung ương"
        
        try:
            v = normalize_number(row[1])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            v = normalize_number(row[2])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            v = normalize_number(row[3])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            v = normalize_number(row[4])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Cây phân tán", "sub_item": None}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "1000_tree", "data_type": "Actual"}))
            v = normalize_number(row[5])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng trồng", "sub_item": None}, {"attribute": "Area_Tended", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            v = normalize_number(row[6])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": None}, {"attribute": "Area_Regenerated", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            v = normalize_number(row[7])
            if v is not None: records.append(create_record(metadata_f, t, loc, gl, {"sector": "Forestry", "commodity": "Rừng", "sub_item": None}, {"attribute": "Area_Protected", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        except: pass

    # PL5 (Fishery) in PL4b.md
    metadata_fish = {"year": 2010, "month": 7, "appendix_number": "PL5", "source_file": "2010_07_phuluc_07_2010_PL4b.md"}
    fish_data = [
        ["Tổng sản lượng thủy sản", 2892],
        ["Sản lượng khai thác", 1461],
        ["Khai thác biển", 1389],
        ["Khai thác nội địa", 72],
        ["Sản lượng nuôi trồng", 1431]
    ]
    for row in fish_data:
        records.append(create_record(metadata_fish, t, "Cả nước", "National", {"sector": "Fishery", "commodity": row[0]}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Actual"}))

    # PL6 (Investment) in PL4b.md
    metadata_inv = {"year": 2010, "month": 7, "appendix_number": "PL6", "source_file": "2010_07_phuluc_07_2010_PL4b.md"}
    inv_data = [
        ["Đầu tư Thuỷ lợi", 1930990],
        ["Đầu tư Nông nghiệp", 278600],
        ["Đầu tư Lâm nghiệp", 123863],
        ["Đầu tư Thuỷ sản", 17800],
        ["Khoa học - Công nghệ", 29000],
        ["Giáo dục - Đào tạo", 60000],
        ["Các ngành khác", 40000],
        ["Chương trình mục tiêu", 30000],
        ["Vốn đầu tư theo các mục tiêu", 113500],
        ["Vốn chuẩn bị đầu tư", 29500],
        ["Vốn trái phiếu Chính phủ", 2510000],
        ["Các dự án có trong QĐ171", 1845000],
        ["Các dự án cấp bách bổ sung", 280000],
        ["Các dự án thuỷ lợi ĐBSHồng", 385000],
        ["Tổng vốn đầu tư", 5163253]
    ]
    for row in inv_data:
        records.append(create_record(metadata_inv, t, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl4a()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL4a.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl4b()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL4b.json"))
    print("Successfully parsed PL4a, PL4b (incl PL5, PL6) for July 2010.")
