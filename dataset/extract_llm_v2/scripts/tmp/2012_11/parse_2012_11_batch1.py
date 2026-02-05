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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐB sông Cửu Long": "Đồng bằng sông Cửu Long",
        "Đồng bằng Sông Hồng": "Đồng bằng sông Hồng", "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "TD và MN": "Đông Bắc", "phía Bắc": "Đông Bắc", "Trung du và MN phía Bắc": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc", "Trung du và miền núi": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam TB": "Duyên hải Nam Trung Bộ",
        "Bắc Trung bộ": "Bắc Trung Bộ", "Bắc Trung Bộ": "Bắc Trung Bộ",
        "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Bắc Cạn": "Bắc Kạn", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông",
        "Hà Nội (mở rộng)": "Hà Nội", "Trung uơng": "Trung ương"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\.\s", "", loc_clean)
    loc_clean = re.sub(r"^[+-]\s", "", loc_clean)
    loc_clean = loc_clean.replace("**", "").replace("<br>", "").replace("\n", "").replace(",", "").strip()
    
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL1.md"
    metadata = {"year": 2012, "month": 11, "appendix_number": "PL1"}
    records = []
    t = {"year": 2012, "month": 11, "period_type": "Monthly", "report_date": "2012-11-15"}
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
        elif "sông Hồng" in name: loc = "Đồng bằng sông Hồng"
        
        item = {"sector": "Cultivation", "commodity": name}
        attr = "Area_Planted"
        if "Thu hoạch" in name: attr = "Area_Harvested"
        
        lower_name = name.lower()
        if "lúa mùa" in lower_name: item.update({"commodity": "Lúa", "sub_item": "Mùa"})
        elif "đông xuân" in lower_name: item.update({"commodity": "Lúa", "sub_item": "Đông Xuân"})
        elif "cây vụ đông" in lower_name: item.update({"commodity": "Cây vụ đông"})
        elif "ngô" in lower_name: item.update({"commodity": "Ngô"})
        elif "khoai lang" in lower_name: item.update({"commodity": "Khoai lang"})
        elif "đậu tương" in lower_name: item.update({"commodity": "Đậu tương"})
        elif "rau, đậu" in lower_name: item.update({"commodity": "Rau đậu các loại"})
        elif "khoai tây" in lower_name: item.update({"commodity": "Khoai tây"})
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Estimate"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL2.md"
    metadata = {"year": 2012, "month": 11, "appendix_number": "PL2"}
    records = []
    t = {"year": 2012, "month": 11, "period_type": "Monthly", "report_date": "2012-11-15"}
    rows = extract_rows(fpath)
    
    for row in rows:
        if "Tỉnh/TP" in row[0] or "Col" in row[0]: continue
        name = row[0].replace("**", "").replace("ằ", "").strip()
        if name == "" or "ngày" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
        
        def add(idx, comm, sub, attr, unit="ha"):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val is not None:
                records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))
        
        add(1, "Lúa", "Mùa", "Area_Planted")
        add(2, "Lúa", "Mùa", "Area_Harvested")
        add(4, "Cây vụ đông", "Tổng số", "Area_Planted")
        add(5, "Ngô", None, "Area_Planted")
        add(6, "Khoai lang", None, "Area_Planted")
        add(7, "Khoai tây", None, "Area_Planted")
        add(8, "Đậu tương", None, "Area_Planted")
        add(9, "Rau đậu các loại", None, "Area_Planted")
    return records

def parse_pl3_pl4_from_file():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_11_Phuluc_11_2012_PL3.md"
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parts = content.split("|Phụ lục 4|")
    
    metadata3 = {"year": 2012, "month": 11, "appendix_number": "PL3"}
    metadata4 = {"year": 2012, "month": 11, "appendix_number": "PL4"}
    records = []
    t = {"year": 2012, "month": 11, "period_type": "Monthly", "report_date": "2012-11-15"}
    
    # Parse PL3 (part 1)
    rows3 = []
    for line in parts[0].split("\n"):
        if "|" in line:
            p = [i.strip() for i in line.split("|")]
            if len(p) > 2 and p[0] == "" and p[-1] == "": rows3.append(p[1:-1])
            elif len(p) > 1: rows3.append(p)
            
    for row in rows3:
        if "Tỉnh/TP" in row[0] or "Col" in row[0] or "Phụ lục" in row[0]: continue
        name = row[0].replace("**", "").replace("_", "").strip()
        if name == "" or "Diện tích" in name: continue
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
        def add3(idx, comm, sub, attr, unit="ha"):
            if idx >= len(row): return
            val_str = row[idx]
            if "<br>" in val_str: val_str = val_str.split("<br>")[0]
            val = normalize_number(val_str)
            if val is not None:
                records.append(create_record(metadata3, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))

        add3(1, "Lúa", "Mùa", "Area_Planted")
        add3(2, "Lúa", "Mùa", "Area_Harvested")
        add3(3, "Lúa", "Đông Xuân", "Area_Planted")
        add3(4, "Màu lương thực", "Tổng số", "Area_Planted")
        add3(5, "Ngô", None, "Area_Planted")
        add3(6, "Khoai lang", None, "Area_Planted")
        add3(7, "Sắn", None, "Area_Planted")

    # Parse PL4 (part 2)
    if len(parts) > 1:
        rows4 = []
        for line in (parts[1]).split("\n"):
            if "|" in line:
                p = [i.strip() for i in line.split("|")]
                if len(p) > 2 and p[0] == "" and p[-1] == "": rows4.append(p[1:-1])
                elif len(p) > 1: rows4.append(p)
                
        for row in rows4:
            if "Tỉnh/TP" in row[0] or "Col" in row[0] or "Ngày" in row[0]: continue
            name = row[0].replace("**", "").strip()
            if name == "" or "Tổng số" in name or "ngắn ngày" in name: continue
            gl = "Provincial"
            if name in ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
            
            def add4(idx, comm, sub):
                if idx >= len(row): return
                val_str = row[idx]
                if "<br>" in val_str: val_str = val_str.split("<br>")[0]
                val = normalize_number(val_str)
                if val is not None:
                    records.append(create_record(metadata4, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val, "unit": "ha", "data_type": "Actual"}))
            
            add4(1, "Cây công nghiệp ngắn ngày", "Tổng số")
            add4(2, "Đậu tương", None)
            add4(3, "Lạc", None)
            add4(4, "Vừng", None)
            add4(5, "Thuốc lá", None)
            add4(6, "Mía", None)
            add4(7, "Bông", None)
            add4(8, "Đay, Cói", None)
            add4(9, "Rau, đậu các loại", None)
            
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/11"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2012, "month": 11}, "records": parse_pl1()}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL1.json"))
    save_json({"metadata": {"year": 2012, "month": 11}, "records": parse_pl2()}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL2.json"))
    
    # PL3 file contains both PL3 and PL4
    all_p3_p4 = parse_pl3_pl4_from_file()
    save_json({"metadata": {"year": 2012, "month": 11}, "records": [r for r in all_p3_p4 if r["metadata"]["appendix_number"] == "PL3"]}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL3.json"))
    save_json({"metadata": {"year": 2012, "month": 11}, "records": [r for r in all_p3_p4 if r["metadata"]["appendix_number"] == "PL4"]}, os.path.join(out_dir, "2012_11_Phuluc_11_2012_PL4.json"))
    
    print("Successfully parsed Batch 1 for November 2012.")
