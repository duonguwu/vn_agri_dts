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
    
    # Check for formats
    if "," in s and "." in s:
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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐB. sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc", "TD và MN": "Đông Bắc", "Trung du và miền núi phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", 
        "Hồ Chí Minh (mở rộng)": "Hồ Chí Minh", "Hà Nội (mở rộng)": "Hà Nội", "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu",
        "Bắc Cạn": "Bắc Kạn", "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái", "Thanh Hoá": "Thanh Hóa", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắc Nông"
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL1.md"
    metadata = {"year": 2011, "month": 11, "appendix_number": "PL1", "source_file": "2011_11_Phuluc_11_2011_f_PL1.md"}
    records = []
    t = {"year": 2011, "month": 11, "period_type": "Monthly", "report_date": "2011-11-15"}
    
    # PL1 in Nov has a very weird inline list. 
    # Let's extract the key values manually if normalization from table fails.
    # Actually it's one big cell in line 19.
    rows = extract_rows(fpath)
    if not rows: return []
    
    row = rows[-1] # The data row
    names_raw = row[0].split("<br>")
    vals_raw = row[3].split("<br>")
    
    # Mapping logic for PL1
    for i in range(len(names_raw)):
        name = names_raw[i].strip()
        if i >= len(vals_raw): continue
        val = normalize_number(vals_raw[i])
        if not val: continue
        
        loc = "Cả nước"
        if "Miền Bắc" in name: loc = "Miền Bắc"
        elif "Miền Nam" in name: loc = "Miền Nam"
        elif "Đồng bằng sông Hồng" in name: loc = "Đồng bằng sông Hồng"
        elif "Đồng bằng sông Cửu Long" in name: loc = "Đồng bằng sông Cửu Long"
        
        item = {"sector": "Cultivation", "commodity": name}
        if "lúa mùa" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Mùa"})
        elif "lúa đông xuân" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Đông Xuân"})
        elif "vụ đông" in name.lower(): item.update({"commodity": "Cây vụ đông"})
        elif "Ngô" in name: item.update({"commodity": "Ngô"})
        elif "Khoai lang" in name: item.update({"commodity": "Khoai lang"})
        elif "Đậu tương" in name: item.update({"commodity": "Đậu tương"})
        elif "Rau, đậu" in name: item.update({"commodity": "Rau đậu các loại"})
        elif "Khoai tây" in name: item.update({"commodity": "Khoai tây"})
        
        attr = "Area_Planted"
        if "thu hoạch" in name.lower(): attr = "Area_Harvested"
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_super_row(fpath, metadata, time_context, mappings):
    rows = extract_rows(fpath)
    records = []
    for row in rows:
        if len(row) < 5: continue
        if "Col" in row[0] or "DT" in row[1]: continue
        
        name_cell = row[0]
        names = [n.strip() for n in name_cell.split("<br>")]
        
        cols_data = []
        for cell in row:
            cols_data.append([c.strip() for c in cell.split("<br>")])
            
        for i in range(len(names)):
            name = names[i]
            if name == "" or "Vùng/Tỉnh" in name: continue
            
            gl = "Provincial"
            if name in ["Miền Bắc", "Miền Nam", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long", "D.H Nam Trg Bộ"]:
                gl = "Regional"
                
            for col_idx, item_info in mappings.items():
                if col_idx >= len(cols_data): continue
                val_list = cols_data[col_idx]
                val_str = val_list[i] if i < len(val_list) else val_list[0]
                val = normalize_number(val_str)
                if val:
                    # Item info is (comm, sub, attr, unit_scale)
                    comm, sub, attr, scale = item_info
                    records.append(create_record(metadata, time_context, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val/scale, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL2.md"
    metadata = {"year": 2011, "month": 11, "appendix_number": "PL2", "source_file": "2011_11_Phuluc_11_2011_f_PL2.md"}
    t = {"year": 2011, "month": 11, "period_type": "Monthly", "report_date": "2011-11-15"}
    # Mapping: cell_idx -> (comm, sub, attr, scale)
    mappings = {
        1: ("Lúa", "Mùa", "Area_Harvested", 1000),
        3: ("Cây vụ đông", "Tổng số", "Area_Planted", 1000),
        4: ("Ngô", None, "Area_Planted", 1000),
        5: ("Khoai lang", None, "Area_Planted", 1000),
        6: ("Khoai tây", None, "Area_Planted", 1000),
        7: ("Đậu tương", None, "Area_Planted", 1000),
        8: ("Lạc", None, "Area_Planted", 1000),
        9: ("Cây khác", None, "Area_Planted", 1000),
        10: ("Rau đậu các loại", None, "Area_Planted", 1000)
    }
    return parse_super_row(fpath, metadata, t, mappings)

def parse_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL3.md"
    metadata = {"year": 2011, "month": 11, "appendix_number": "PL3", "source_file": "2011_11_Phuluc_11_2011_f_PL3.md"}
    t = {"year": 2011, "month": 11, "period_type": "Monthly", "report_date": "2011-11-15"}
    mappings = {
        1: ("Lúa", "Mùa", "Area_Planted", 1000),
        2: ("Lúa", "Mùa", "Area_Harvested", 1000), # Note: PL3 has both Gieo cay and Thu hoach
        3: ("Lúa", "Đông Xuân", "Area_Planted", 1000),
        4: ("Màu lương thực", "Tổng số", "Area_Planted", 1000),
        5: ("Ngô", None, "Area_Planted", 1000),
        6: ("Khoai lang", None, "Area_Planted", 1000),
        7: ("Sắn", None, "Area_Planted", 1000),
        8: ("Cây lương thực có củ khác", None, "Area_Planted", 1000)
    }
    return parse_super_row(fpath, metadata, t, mappings)

def parse_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_11_Phuluc_11_2011_f_PL4.md"
    metadata = {"year": 2011, "month": 11, "appendix_number": "PL4", "source_file": "2011_11_Phuluc_11_2011_f_PL4.md"}
    t = {"year": 2011, "month": 11, "period_type": "Monthly", "report_date": "2011-11-15"}
    mappings = {
        1: ("Cây công nghiệp ngắn ngày", "Tổng số", "Area_Planted", 1000),
        2: ("Đậu tương", None, "Area_Planted", 1000),
        3: ("Lạc", None, "Area_Planted", 1000),
        4: ("Vừng", None, "Area_Planted", 1000),
        5: ("Thuốc lá", None, "Area_Planted", 1000),
        6: ("Mía", None, "Area_Planted", 1000),
        7: ("Bông", None, "Area_Planted", 1000),
        8: ("Đay, Lác", None, "Area_Planted", 1000),
        9: ("Rau các loại", None, "Area_Planted", 1000),
        10: ("Đậu các loại", None, "Area_Planted", 1000)
    }
    return parse_super_row(fpath, metadata, t, mappings)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/11"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_pl1()}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_pl2()}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_pl3()}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 11}, "records": parse_pl4()}, os.path.join(out_dir, "2011_11_Phuluc_11_2011_f_PL4.json"))
    
    print("Successfully parsed Batch 1 (PL1-PL4) for November 2011.")
