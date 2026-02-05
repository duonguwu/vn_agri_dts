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
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "").replace("..", ".")
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts[-1]) == 3: s = s.replace(",", "")
        else: s = s.replace(",", ".")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    
    try:
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "Đồng bằng Sông Hồng": "Đồng bằng sông Hồng", "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "TD và MN": "Đông Bắc", "phía Bắc": "Đông Bắc", "Trung du và MN phía Bắc": "Đông Bắc",
        "D.H Nam TB": "Duyên hải Nam Trung Bộ", "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung bộ": "Bắc Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông",
        "Hà Nội (mở rộng)": "Hà Nội"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
    loc_clean = re.sub(r"^[+-]\s", "", loc_clean)
    loc_clean = loc_clean.replace("**", "").replace("<br>", "").replace("\n", "").strip()
    
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

def extract_rows(fpath):
    if not os.path.exists(fpath): return []
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "": rows.append(parts[1:-1])
            elif len(parts) > 1: rows.append(parts)
    return rows

def parse_pl1():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_08_Phuluc_08_2012_PL1.md"
    metadata = {"year": 2012, "month": 8, "appendix_number": "PL1"}
    records = []
    t = {"year": 2012, "month": 8, "period_type": "Monthly", "report_date": "2012-08-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 4: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        val = normalize_number(row[3])
        if val is None: continue
        
        loc = "Cả nước"
        if "Miền Nam" in name: loc = "Miền Nam"
        elif "Miền Bắc" in name: loc = "Miền Bắc"
        elif "sông Cửu Long" in name: loc = "Đồng bằng sông Cửu Long"
        
        item = {"sector": "Cultivation", "commodity": name}
        attr = "Area_Planted"
        if "Thu hoạch" in name: attr = "Area_Harvested"
        
        lower_name = name.lower()
        if "lúa hè thu" in lower_name: item.update({"commodity": "Lúa", "sub_item": "Hè Thu"})
        elif "lúa mùa" in lower_name: item.update({"commodity": "Lúa", "sub_item": "Mùa"})
        elif "màu lương thực" in lower_name: item.update({"commodity": "Màu lương thực"})
        elif "cây công nghiệp" in lower_name: item.update({"commodity": "Cây công nghiệp ngắn ngày"})
        elif "ngô" in lower_name: item.update({"commodity": "Ngô"})
        elif "khoai lang" in lower_name: item.update({"commodity": "Khoai lang"})
        elif "sắn" in lower_name: item.update({"commodity": "Sắn"})
        elif "lạc" in lower_name: item.update({"commodity": "Lạc"})
        elif "đậu tương" in lower_name: item.update({"commodity": "Đậu tương"})
        elif "thuốc lá" in lower_name: item.update({"commodity": "Thuốc lá"})
        elif "rau, đậu" in lower_name: item.update({"commodity": "Rau đậu các loại"})
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Estimate"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_08_Phuluc_08_2012_PL2.md"
    metadata = {"year": 2012, "month": 8, "appendix_number": "PL2"}
    records = []
    t = {"year": 2012, "month": 8, "period_type": "Monthly", "report_date": "2012-08-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if "Tỉnh/TP" in row[0] or "Col" in row[0]: continue
        name = row[0].replace("**", "").strip()
        if name == "": continue
        
        gl = "Provincial"
        if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
        
        def add(idx, comm, sub, attr, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))
        
        add(1, "Lúa", "Mùa", "Area_Planted")
        add(2, "Lúa", "Hè Thu", "Area_Planted")
        add(3, "Màu lương thực", "Tổng số", "Area_Planted")
        add(4, "Ngô", None, "Area_Planted")
        add(5, "Khoai lang", None, "Area_Planted")
        add(6, "Sắn", None, "Area_Planted")
        add(7, "Cây khác", None, "Area_Planted")
    return records

def parse_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_08_Phuluc_08_2012_PL3.md"
    metadata = {"year": 2012, "month": 8, "appendix_number": "PL3"}
    records = []
    t = {"year": 2012, "month": 8, "period_type": "Monthly", "report_date": "2012-08-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if "Tỉnh/TP" in row[0] or "Col" in row[0]: continue
        name = row[0].replace("**", "").strip()
        if name == "": continue
        
        gl = "Provincial"
        if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
        
        def add(idx, comm, sub):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val, "unit": "ha", "data_type": "Actual"}))
        
        add(1, "Cây công nghiệp hàng năm", "Tổng số")
        add(2, "Đậu tương", None)
        add(3, "Lạc", None)
        add(4, "Thuốc lá", None)
        add(5, "Mía", None)
        add(6, "Cây khác", None)
        add(7, "Rau đậu các loại", None)
    return records

def parse_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_08_Phuluc_08_2012_PL4.md"
    metadata = {"year": 2012, "month": 8, "appendix_number": "PL4"}
    records = []
    t = {"year": 2012, "month": 8, "period_type": "Monthly", "report_date": "2012-08-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if "Tỉnh/TP" in row[0] or "Col" in row[0]: continue
        name = row[0].replace("**", "").replace("<br>", "").strip()
        if name == "" or "Diện tích" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam TB", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
        def add(idx, comm, sub, attr, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))
        
        add(1, "Lúa", "Hè Thu", "Area_Harvested")
        # Column 3 is NS (Yield) but in PL4 it is marked as NS thu hoạch (Yield)
        add(3, "Lúa", "Hè Thu", "Yield", "ta_ha")
        add(4, "Lúa", "Mùa", "Area_Planted")
        add(5, "Màu lương thực", "Tổng số", "Area_Planted")
        add(6, "Ngô", None, "Area_Planted")
        add(7, "Khoai lang", None, "Area_Planted")
        add(8, "Sắn", None, "Area_Planted")
        add(9, "Cây khác", None, "Area_Planted")
    return records

def parse_pl5():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_08_Phuluc_08_2012_PL5.md"
    metadata = {"year": 2012, "month": 8, "appendix_number": "PL5"}
    records = []
    t = {"year": 2012, "month": 8, "period_type": "Monthly", "report_date": "2012-08-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if "Tỉnh/TP" in row[0] or "Col" in row[0]: continue
        name = row[0].replace("**", "").replace("<br>", "").strip()
        if name == "" or "Tổng số" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam TB", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
        def add(idx, comm, sub):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val, "unit": "ha", "data_type": "Actual"}))
        
        add(1, "Cây công nghiệp ngắn ngày", "Tổng số")
        add(2, "Đậu tương", None)
        add(3, "Lạc", None)
        add(4, "Vừng", None)
        add(5, "Thuốc lá", None)
        add(6, "Mía", None)
        add(7, "Bông", None)
        add(8, "Đay, Lác", None)
        add(9, "Rau các loại", None)
        add(10, "Đậu các loại", None)
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/08"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 8}, "records": parse_pl1()}, os.path.join(out_dir, "2012_08_Phuluc_08_2012_PL1.json"))
    save_json({"metadata": {"year": 2012, "month": 8}, "records": parse_pl2()}, os.path.join(out_dir, "2012_08_Phuluc_08_2012_PL2.json"))
    save_json({"metadata": {"year": 2012, "month": 8}, "records": parse_pl3()}, os.path.join(out_dir, "2012_08_Phuluc_08_2012_PL3.json"))
    save_json({"metadata": {"year": 2012, "month": 8}, "records": parse_pl4()}, os.path.join(out_dir, "2012_08_Phuluc_08_2012_PL4.json"))
    save_json({"metadata": {"year": 2012, "month": 8}, "records": parse_pl5()}, os.path.join(out_dir, "2012_08_Phuluc_08_2012_PL5.json"))
    
    print("Successfully parsed Batch 1 for August 2012.")
