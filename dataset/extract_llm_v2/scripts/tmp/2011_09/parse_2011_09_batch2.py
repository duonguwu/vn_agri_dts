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
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "")
            else: s = s.replace(",", ".")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    
    try:
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", 
        "Hồ Chí Minh (mở rộng)": "Hồ Chí Minh", "Hà Nội (mở rộng)": "Hà Nội", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Bắc Cạn": "Bắc Kạn", "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái", "Thanh Hoá": "Thanh Hóa", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
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

def parse_pl6():
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL6", "source_file": "2011_09_Phuluc_09_2011_f_PL6.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Cumulative", "report_date": "2011-09-30"}
    data = [
        ("Diện tích rừng trồng mới tập trung", 129.7, "1000_ha"),
        ("Rừng phòng hộ, đặc dụng", 14.2, "1000_ha"),
        ("Rừng sản xuất", 115.5, "1000_ha"),
        ("Diện tích rừng trồng được chăm sóc", 306.9, "1000_ha"),
        ("Số cây lâm nghiệp trồng phân tán", 163.6, "million_trees"),
        ("Diện tích rừng được khoanh nuôi tái sinh", 697.0, "1000_ha"),
        ("Diện tích rừng được khoán bảo vệ", 2349.0, "1000_ha"),
        ("Sản lượng gỗ", 3066.0, "1000_m3")
    ]
    for item, val, unit in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Output", "value": val, "unit": unit, "data_type": "Estimate"}))
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL7.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL7", "source_file": "2011_09_Phuluc_09_2011_f_PL7.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Cumulative", "report_date": "2011-09-30"}
    
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "Diện tích" in name or name == "" or "Col" in name or "TT" in name: continue
        
        gl = "Provincial"
        if name in ["Cả nước", "Miền bắc", "ĐB. sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ", 
                    "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]:
            gl = "National" if name == "Cả nước" else "Regional"
        
        def add(idx, comm, sub=None):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val: records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": comm, "sub_item": sub}, {"attribute": "Output", "value": val, "unit": "ha", "data_type": "Actual"}))
            
        add(2, "Diện tích rừng trồng mới tập trung", "Tổng số")
        add(3, "Diện tích rừng trồng mới tập trung", "Phòng hộ, đặc dụng")
        add(4, "Diện tích rừng trồng mới tập trung", "Sản xuất")
        add(5, "Diện tích rừng trồng được chăm sóc", "Sản xuất")
        add(6, "Diện tích rừng được khoanh nuôi tái sinh", "Sản xuất")
        add(7, "Diện tích rừng được khoán bảo vệ", "Sản xuất")
    return records

def parse_pl8():
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL8", "source_file": "2011_09_Phuluc_09_2011_f_PL8.md"}
    records = []
    t_8m = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    t_month = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-30"}
    t_9m = {"year": 2011, "month": 9, "period_type": "Cumulative", "report_date": "2011-09-30"}
    
    # [Item, v8c, vm, v9c]
    data = [
        ("Tổng sản lượng", 3574.0, 562.0, 4136.0),
        ("Sản lượng khai thác", 1729.0, 244.0, 1973.0),
        ("Khai thác biển", 1619.0, 214.0, 1833.0),
        ("Khai thác nội địa", 110.0, 30.0, 140.0),
        ("Sản lượng nuôi trồng", 1845.0, 318.0, 2163.0)
    ]
    for item, v8c, vm, v9c in data:
        records.append(create_record(metadata, t_8m, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": v8c, "unit": "1000_ton", "data_type": "Actual"}))
        records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_9m, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": v9c, "unit": "1000_ton", "data_type": "Estimate"}))
    return records

def parse_pl9():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL9.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL9", "source_file": "2011_09_Phuluc_09_2011_f_PL9.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Cumulative", "report_date": "2011-09-20"}
    
    for row in rows:
        if len(row) < 8: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if name == "" or "Col" in name or "Miền" in name or "Tỉnh" in name: continue
        
        gl = "Provincial"
        def add(idx, comm, sub=None):
            val = normalize_number(row[idx])
            if val: records.append(create_record(metadata, t, name, gl, {"sector": "Fishery", "commodity": comm, "sub_item": sub}, {"attribute": "Production", "value": val, "unit": "ton", "data_type": "Actual"}))
            
        add(1, "Tổng sản lượng")
        add(2, "Sản lượng nuôi trồng", "Tổng số")
        add(3, "Sản lượng nuôi trồng", "Nước ngọt")
        add(4, "Sản lượng nuôi trồng", "Nước mặn, lợ")
        add(5, "Sản lượng khai thác", "Tổng số")
        add(6, "Sản lượng khai thác", "Khai thác biển")
        add(7, "Sản lượng khai thác", "Khai thác nội địa")
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/09"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl6()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl7()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL7.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl8()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL8.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl9()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL9.json"))
    
    print("Successfully parsed Batch 2 (PL6-PL9) for September 2011.")
