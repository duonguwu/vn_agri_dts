import json
import uuid
import os
import re

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
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.split("<br>")[0]
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[-1]) == 3 and len(parts[0]) <= 3: s = s.replace(",", "")
            elif len(parts[-1]) != 3: s = s.replace(",", ".")
            else: s = s.replace(",", "")
    elif "." in s:
         if s.count(".") > 1: s = s.replace(".", "")
    try: return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", "Trung du và miền núi\nphía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ và\nduyên hải miền Trung": "Bắc Trung Bộ và Duyên hải miền Trung", "Bắc Trung Bộ và duyên hải miền Trung": "Bắc Trung Bộ và Duyên hải miền Trung",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng", "TP.Hồ Chí Minh": "Hồ Chí Minh", "T.P Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu", "Bà Rịa- Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Tỉnh/Thành phố": "Cả nước", "Cả nước": "Cả nước", "Toàn quốc": "Cả nước",
        "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái",
        "Miền bắc": "Miền Bắc", "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Quảng Bình *": "Quảng Bình", "Quảng Nam *": "Quảng Nam", "Kh. lang": "Khoai lang", "Huế": "Thừa Thiên Huế", "Thanh Hóa": "Thanh Hóa"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\.\s", "", loc_clean) # Remove "1. "
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean) 
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

def extract_rows_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "": rows.append(parts[1:-1])
            elif len(parts) > 1: rows.append(parts)
    return rows

def safe_split(s):
    return [x.strip() for x in s.split("<br>")]

def process_explode_row(rows, target_keyword, min_len, callback):
    for row in rows:
        if len(row) < min_len: continue
        # Find main row
        raw_name = row[0]
        if target_keyword not in raw_name: continue
        
        cols = [safe_split(c) for c in row]
        names = cols[0]
        
        for i in range(len(names)):
            name_i = names[i].replace("**", "").strip()
            if name_i == "" or "Col" in name_i or "Đơn vị" in name_i or "Vùng" in name_i: continue
            
            gl = "Provincial"
            if name_i in ["Miền Bắc", "ĐB sông Hồng", "Đồng bằng sông Hồng", "TD và MN", "Trung du và MN phía Bắc", "Bắc Trung Bộ", 
                          "Miền Nam", "ĐBS Cửu Long", "Đông Nam Bộ", "Tây Nguyên", "D.H Nam Trg Bộ", "D.H Nam Trung Bộ"]: 
                gl = "Regional"
                
            def get_val(col_idx):
                if col_idx >= len(cols): return None
                col_vals = cols[col_idx]
                if i < len(col_vals): return normalize_number(col_vals[i])
                return None
            
            callback(name_i, gl, get_val)

def parse_pl2_explode():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_06_Phuluc_06_2011_PL2.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL2", "source_file": "2011_06_Phuluc_06_2011_PL2.md"}
    records = []
    t = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-15"}
    
    def process(name, gl, get_val):
        v_dx_plant = get_val(1)
        v_dx_harv = get_val(2)
        v_yield = get_val(4)
        v_mau = get_val(5) # Note: Mapped based on previous analysis (Col 6 in file is Index 5 in 0-based split logic IF empty first col removed)
        # Wait, extract_rows removes empty first/last.
        # Let's re-verify index 5.
        # Row: |Miền Bắc|1,148...|480...|41.9|62.4|811,717|555,821|...
        # Idx 0: Name
        # Idx 1: Plant
        # Idx 2: Harv
        # Idx 3: %
        # Idx 4: Yield
        # Idx 5: Mau (811k)
        # Idx 6: Ngo (555k)
        # Idx 7: Khoai
        # Idx 8: San
        # Idx 9: Khac
        v_ngo = get_val(6)
        v_khoai = get_val(7)
        v_san = get_val(8)
        v_khac = get_val(9)

        if v_dx_plant: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v_dx_plant/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_dx_harv: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": v_dx_harv/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_yield: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Yield", "value": v_yield, "unit": "quintal_per_ha", "data_type": "Actual"}))
        if v_mau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": v_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": v_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_san: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": v_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))

    process_explode_row(rows, "Miền Bắc", 10, process)
    return records

def parse_pl3_explode():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_06_Phuluc_06_2011_PL3.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL3", "source_file": "2011_06_Phuluc_06_2011_PL3.md"}
    records = []
    t = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-15"}
    
    def process(name, gl, get_val):
        # 0 Name | 1 CN Total | 2 Dau Tuong | 3 Lac | 4 Mia | 5 Thuoc La | 6 Khac | 7 Rau dau
        v_cn = get_val(1)
        v_dt = get_val(2)
        v_lac = get_val(3)
        v_mia = get_val(4)
        v_tl = get_val(5)
        v_khac = get_val(6)
        v_rau = get_val(7)
        
        if v_cn: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_cn/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_dt: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": v_dt/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_lac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": v_lac/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_mia: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Mía", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mia/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_tl: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": v_tl/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Khác"}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if v_rau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": v_rau/1000, "unit": "1000_ha", "data_type": "Actual"}))

    process_explode_row(rows, "Miền Bắc", 8, process)
    return records

def parse_pl4_explode():
    # PL4: Southern Rice & Crops - Explode Parser (Reused)
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_06_Phuluc_06_2011_PL4.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL4", "source_file": "2011_06_Phuluc_06_2011_PL4.md"}
    records = []
    t = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-15"}

    def process(name, gl, get_val):
        # Index logic from previous analysis
        val_ht_plant = get_val(1)
        val_ht_harv = get_val(2)
        val_mua_plant = get_val(3)
        val_mau = get_val(4)
        val_ngo = get_val(5)
        val_khoai = get_val(6)
        val_san = get_val(7)
        val_other = get_val(8)
        
        if val_ht_plant is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": val_ht_plant/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_ht_harv is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": val_ht_harv/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_mua_plant is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": val_mua_plant/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_mau is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": val_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_ngo is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": val_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_khoai is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": val_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_san is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": val_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
        if val_other is not None: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": val_other/1000, "unit": "1000_ha", "data_type": "Actual"}))

    process_explode_row(rows, "Miền Nam", 9, process)
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl2_explode()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl3_explode()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl4_explode()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL4.json"))
    
    print("Successfully exploded PL2, PL3, PL4 for June 2011.")
