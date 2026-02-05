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
        "TD và MN": "Đông Bắc", "Trung du và MN phía Bắc": "Đông Bắc",
        "D.H Nam Tr.Bộ": "Duyên hải Nam Trung Bộ", "Bắc Trung bộ": "Bắc Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắc Nông",
        "Hà Gian**g**": "Hà Giang", "Cao Bằng": "Cao Bằng", "Cao Bằn**g**": "Cao Bằng"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
    loc_clean = re.sub(r"^[+-]\s", "", loc_clean)
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL1.md"
    metadata = {"year": 2012, "month": 4, "appendix_number": "PL1", "source_file": "2012_04_Phuluc_04_2012_PL1.md"}
    records = []
    t = {"year": 2012, "month": 4, "period_type": "Monthly", "report_date": "2012-04-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 3: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        val = normalize_number(row[2])
        if val is None: continue
        
        loc = "Cả nước"
        if "Miền Nam" in name: loc = "Miền Nam"
        elif "sông Cửu Long" in name: loc = "Đồng bằng sông Cửu Long"
        
        item = {"sector": "Cultivation", "commodity": name}
        attr = "Area_Planted"
        if "Thu hoạch" in name: attr = "Area_Harvested"
        
        if "lúa hè thu" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Hè Thu"})
        elif "lúa đông xuân" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Đông Xuân"})
        elif "màu lương thực" in name.lower(): item.update({"commodity": "Màu lương thực"})
        elif "cây công nghiệp" in name.lower(): item.update({"commodity": "Cây công nghiệp ngắn ngày"})
        elif "Ngô" in name: item.update({"commodity": "Ngô"})
        elif "Khoai lang" in name: item.update({"commodity": "Khoai lang"})
        elif "Sắn" in name: item.update({"commodity": "Sắn"})
        elif "Đậu tương" in name: item.update({"commodity": "Đậu tương"})
        elif "Lạc" in name: item.update({"commodity": "Lạc"})
        elif "Mía" in name: item.update({"commodity": "Mía"})
        elif "Thuốc lá" in name: item.update({"commodity": "Thuốc lá"})
        elif "rau, đậu" in name.lower(): item.update({"commodity": "Rau đậu các loại"})
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Estimate"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL2.md"
    metadata = {"year": 2012, "month": 4, "appendix_number": "PL2", "source_file": "2012_04_Phuluc_04_2012_PL2.md"}
    records = []
    t = {"year": 2012, "month": 4, "period_type": "Monthly", "report_date": "2012-04-15"}
    rows = extract_rows(fpath)
    
    items = [None, ("Lúa", "Đông Xuân"), ("Màu lương thực", "Tổng số"), "Ngô", "Khoai lang", "Sắn", "Cây khác"]
    for row in rows:
        if len(row) < len(items): continue
        name = row[0].replace("**", "").strip()
        if "Col" in name or name == "" or "Tỉnh/TP" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
        
        for i in range(1, len(items)):
            val = normalize_number(row[i])
            if val is not None:
                item_info = items[i]
                if isinstance(item_info, tuple): comm, sub = item_info
                else: comm, sub = item_info, None
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL3.md"
    metadata = {"year": 2012, "month": 4, "appendix_number": "PL3", "source_file": "2012_04_Phuluc_04_2012_PL3.md"}
    records = []
    t = {"year": 2012, "month": 4, "period_type": "Monthly", "report_date": "2012-04-15"}
    rows = extract_rows(fpath)
    
    cols = [None, ("Cây công nghiệp hàng năm", "Tổng số"), "Đậu tương", "Lạc", "Thuốc lá", "Mía", "Cây khác", "Rau đậu các loại"]
    for row in rows:
        if "Col" in row[0] or row[0] == "" or "Tỉnh/TP" in row[0]: continue
        name = row[0].replace("**", "").strip()
        gl = "Provincial"
        if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
        
        for i in range(1, len(cols)):
            if i >= len(row): break
            val = normalize_number(row[i])
            if val is not None:
                item_info = cols[i]
                if isinstance(item_info, tuple): comm, sub = item_info
                else: comm, sub = item_info, None
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL4.md"
    metadata = {"year": 2012, "month": 4, "appendix_number": "PL4", "source_file": "2012_04_Phuluc_04_2012_PL4.md"}
    records = []
    t = {"year": 2012, "month": 4, "period_type": "Monthly", "report_date": "2012-04-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 11: continue
        name = row[0].replace("**", "").strip()
        if "Col" in name or name == "" or "Tỉnh/TP" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam Tr.Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
        def add(idx, comm, sub, attr, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))
        
        add(1, "Lúa", "Đông Xuân", "Area_Harvested")
        add(2, "Lúa", "Đông Xuân", "Yield", "ta_ha")
        add(3, "Lúa", "Đông Xuân", "Production", "ton")
        add(5, "Lúa", "Hè Thu", "Area_Planted")
        add(6, "Màu lương thực", "Tổng số", "Area_Planted")
        add(7, "Ngô", None, "Area_Planted")
        add(8, "Khoai lang", None, "Area_Planted")
        add(9, "Sắn", None, "Area_Planted")
        add(10, "Cây khác", None, "Area_Planted")
    return records

def parse_pl5():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_04_Phuluc_04_2012_PL5.md"
    metadata = {"year": 2012, "month": 4, "appendix_number": "PL5", "source_file": "2012_04_Phuluc_04_2012_PL5.md"}
    records = []
    t = {"year": 2012, "month": 4, "period_type": "Monthly", "report_date": "2012-04-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if len(row) < 9: continue
        name = row[0].replace("**", "").strip()
        if "Col" in name or name == "" or "Tỉnh/TP" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam Tr.Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
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
        add(7, "Đay, Lác", None)
        add(8, "Rau các loại", None)
        add(9, "Đậu các loại", None)
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/04"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_pl1()}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL1.json"))
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_pl2()}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL2.json"))
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_pl3()}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL3.json"))
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_pl4()}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL4.json"))
    save_json({"metadata": {"year": 2012, "month": 4}, "records": parse_pl5()}, os.path.join(out_dir, "2012_04_Phuluc_04_2012_PL5.json"))
    
    print("Successfully parsed Batch 1 (Corrected) for April 2012.")
