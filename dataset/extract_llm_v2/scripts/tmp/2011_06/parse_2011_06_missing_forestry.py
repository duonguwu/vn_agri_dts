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

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "Trung du và MN phía Bắc": "Đông Bắc",
        "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", "Trung du và miền núi\nphía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ và\nduyên hải miền Trung": "Bắc Trung Bộ và Duyên hải miền Trung",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", 
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "Tỉnh/Thành phố": "Cả nước", "Cả nước": "Cả nước",
        "ĐB. sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái",
        "Miền bắc": "Miền Bắc"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.strip()
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
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl7():
    # Forestry 6M Summary (PL7)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL7", "source_file": "2011_06_Phuluc_06_2011_PL7.md"}
    records = []
    
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    
    # [Item, Unit, Last Year, Est This Year]
    data = [
        ("Diện tích rừng trồng mới tập trung", "1000 ha", 78.3, 53.8),
        ("Rừng phòng hộ, đặc dụng", "1000 ha", 13.5, 2.9),
        ("Rừng sản xuất", "1000 ha", 64.8, 50.9),
        ("Diện tích rừng trồng được chăm sóc", "1000 ha", 194.9, 261.7),
        ("Số cây lâm nghiệp trồng phân tán", "Tr.cây", 107.6, 108.0),
        ("Diện tích rừng được khoanh nuôi tái sinh", "1000 ha", 646.8, 647.2),
        ("Diện tích rừng được khoán bảo vệ", "1000 ha", 2077.1, 2088.3),
        ("Sản lượng gỗ", "1000 m3", 1775.0, 2007.0)
    ]
    
    for row in data:
        item = row[0]
        unit = "1000_ha"
        if row[1] == "Tr.cây": unit = "million_trees"
        elif row[1] == "1000 m3": unit = "1000_m3"
        
        records.append(create_record(metadata, t_6m_11, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Output", "value": float(row[3]), "unit": unit, "data_type": "Estimate"}))

    return records

def parse_pl8():
    # Forestry Detail 6M (PL8)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL8", "source_file": "2011_06_Phuluc_06_2011_PL8.md"}
    records = []
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    
    # [Name, Total Planted, PH/DD Planted, SX Planted, Cham Soc SX, Khoan Bao Ve SX]
    
    data = [
        ("Cả nước", 53768, 2852, 50916, 261736, 2088330),
        ("Miền bắc", 46228, 2142, 44086, 224385, 1235304),
        ("ĐB. sông Hồng", 5959, 203, 5756, 48783, 57404),
        ("Trung du và miền núi phía Bắc", 33858, 1654, 32204, 113092, 989935),
        ("Bắc Trung Bộ", 6411, 285, 6126, 62510, 187965),
        ("Miền Nam", 7540, 710, 6830, 37351, 853026),
        ("D.H Nam Trung Bộ", 760, 0, 760, 31161, 377734),
        ("Tây Nguyên", 4940, 100, 4840, 1919, 399204),
        ("Đông Nam Bộ", 1010, 530, 480, 1531, 75146),
        ("ĐB. sông Cửu Long", 830, 80, 750, 2740, 942)
    ]
    
    regional_list = ["Miền bắc", "Miền Nam", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    for row in data:
        loc = row[0]
        gl = "Regional" if loc in regional_list else "Provincial"
        if loc == "Cả nước": gl = "National"
        if loc == "Miền bắc": loc = "Miền Bắc"
        
        # Total Planted
        if row[1] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Tổng số"}, {"attribute": "Output", "value": float(row[1]), "unit": "ha", "data_type": "Estimate"}))
        # PH/DD
        if row[2] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Rừng phòng hộ, đặc dụng"}, {"attribute": "Output", "value": float(row[2]), "unit": "ha", "data_type": "Estimate"}))
        # SX
        if row[3] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Rừng sản xuất"}, {"attribute": "Output", "value": float(row[3]), "unit": "ha", "data_type": "Estimate"}))
        # Cham Soc
        if row[4] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng được chăm sóc", "sub_item": "Rừng sản xuất"}, {"attribute": "Output", "value": float(row[4]), "unit": "ha", "data_type": "Estimate"}))
        # Khoan Bao Ve
        if row[5] is not None: records.append(create_record(metadata, t_6m_11, loc, gl, {"sector": "Forestry", "commodity": "Diện tích rừng được khoán bảo vệ", "sub_item": "Rừng sản xuất"}, {"attribute": "Output", "value": float(row[5]), "unit": "ha", "data_type": "Estimate"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl7()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL7.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl8()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL8.json"))
    print("Successfully corrected PL7, PL8 for June 2011 (Forestry Summary & Detail).")
