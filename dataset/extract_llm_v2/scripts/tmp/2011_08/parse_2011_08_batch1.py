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
    # Remove thousand separators and handle decimals
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    # Handle VN format 1.234,5
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
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "T.P Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái", "Thanh Hoá": "Thanh Hóa", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\.\s", "", loc_clean)
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
    elif "Miền Bắc" in norm_loc: geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    elif "Miền Nam" in norm_loc: geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    
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

def parse_2011_08_pl1():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL1.md"
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL1", "source_file": "2011_08_Phuluc_08_2011_f_PL1.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-15"}
    
    data = [
        ("Thu hoạch lúa hè thu miền Nam", "Miền Nam", 1221.0, "Area_Harvested"),
        ("Đồng bằng sông Cửu Long", "Đồng bằng sông Cửu Long", 1141.5, "Area_Harvested"),
        ("Gieo cấy lúa mùa cả nước", "Cả nước", 1432.8, "Area_Planted"),
        ("Miền Bắc", "Miền Bắc", 1139.9, "Area_Planted"),
        ("Miền Nam", "Miền Nam", 292.8, "Area_Planted"),
        ("Gieo trồng màu lương thực", "Cả nước", 1612.0, "Area_Planted"),
        ("Ngô", "Cả nước", 958.9, "Area_Planted"),
        ("Khoai lang", "Cả nước", 131.6, "Area_Planted"),
        ("Sắn", "Cả nước", 484.2, "Area_Planted"),
        ("Gieo trồng cây công nghiệp ngắn ngày", "Cả nước", 648.2, "Area_Planted"),
        ("Lạc", "Cả nước", 213.2, "Area_Planted"),
        ("Đậu tương", "Cả nước", 168.2, "Area_Planted"),
        ("Thuốc lá", "Cả nước", 19.8, "Area_Planted"),
        ("Gieo trồng rau, đậu các loại", "Cả nước", 662.7, "Area_Planted")
    ]
    
    for item_name, loc, val, attr in data:
        # Determine commodity and sub_item
        if "lúa" in item_name.lower():
            commodity = "Lúa"
            sub_item = "Hè Thu" if "hè thu" in item_name.lower() else "Mùa"
        elif item_name in ["Ngô", "Khoai lang", "Sắn"]:
            commodity = item_name
            sub_item = None
        elif "cây công nghiệp" in item_name.lower():
            commodity = "Cây công nghiệp ngắn ngày"
            sub_item = "Tổng số"
        elif item_name in ["Lạc", "Đậu tương", "Thuốc lá"]:
            commodity = item_name
            sub_item = None
        elif "rau, đậu" in item_name.lower():
            commodity = "Rau đậu các loại"
            sub_item = None
        else:
            commodity = item_name
            sub_item = None
            
        gl = "National" if loc == "Cả nước" else "Regional"
        if loc == "Đồng bằng sông Cửu Long": gl = "Regional"
        
        records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": commodity, "sub_item": sub_item}, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_2011_08_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL2.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL2", "source_file": "2011_08_Phuluc_08_2011_f_PL2.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-15"}
    
    for row in rows:
        if len(row) < 5: continue
        raw_name = row[0]
        if "Gieo trồng" in raw_name or "Col" in raw_name or "|" in raw_name: continue
        
        # Split merged cells if any
        names = [n.strip() for n in raw_name.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i].replace("**", "").strip()
            if name == "" or name == "Miền Bắc": 
                if name == "Miền Bắc": pass
                else: continue
            
            gl = "Provincial"
            if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]:
                gl = "Regional"
                
            def get_val(col_idx):
                if col_idx >= len(cols): return None
                col_vals = cols[col_idx]
                val_idx = i if i < len(col_vals) else 0 # Fallback to first if only one value
                # Special case for row 24 Hà Nam where names[0]="Hà Nam" but Ngô has 2 values
                # Looking at raw file: Row 24: |Hà Nam|35,275||9,210|8,814<br>4,330|396|||
                # Actually, 4,330 might be for a different province or a sub-item. 
                # Let's just normalize as usual.
                return normalize_number(col_vals[val_idx])

            # Col Mapping: 0: Name, 1: Lúa Mùa, 2: Lúa Hè Thu, 3: Màu Tot, 4: Ngô, 5: Khoai Lang, 6: Sắn, 7: Khác
            v_mua = get_val(1)
            v_ht = get_val(2)
            v_mau = get_val(3)
            v_ngo = get_val(4)
            v_khoai = get_val(5)
            v_san = get_val(6)
            v_khac = get_val(7)
            
            if v_mua: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v_mua/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_ht: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": v_ht/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": v_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": v_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_san: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": v_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

def parse_2011_08_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL3.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL3", "source_file": "2011_08_Phuluc_08_2011_f_PL3.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-15"}
    
    for row in rows:
        if len(row) < 5: continue
        raw_name = row[0]
        if "Miền Bắc" not in raw_name and row[0] == "": continue
        if "DT cây" in raw_name or "Col" in raw_name: continue
        
        names = [n.strip() for n in raw_name.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i].replace("**", "").strip()
            if name == "": continue
            
            gl = "Provincial"
            if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]:
                gl = "Regional"
                
            def get_val(col_idx):
                if col_idx >= len(cols): return None
                col_vals = cols[col_idx]
                val_idx = i if i < len(col_vals) else 0
                return normalize_number(col_vals[val_idx])

            # Col Mapping: 0: Name, 1: CCN Tot, 2: Đậu tương, 3: Lạc, 4: Mía, 5: Thuốc lá, 6: Khác, 7: Rau đậu
            v_ccn = get_val(1)
            v_dt = get_val(2)
            v_lac = get_val(3)
            v_mia = get_val(4)
            v_tl = get_val(5)
            v_khac = get_val(6)
            v_rau = get_val(7)
            
            if v_ccn: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_ccn/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dt: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": v_dt/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_lac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": v_lac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mia: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Mía", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mia/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_tl: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": v_tl/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Khác"}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_rau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": v_rau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

def parse_2011_08_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL4.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL4", "source_file": "2011_08_Phuluc_08_2011_f_PL4.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-15"}
    
    for row in rows:
        if len(row) < 8: continue
        raw_name = row[0]
        if "Miền Nam" not in raw_name and row[0] == "": continue
        if "Lúa hè thu" in raw_name or "Col" in raw_name or "Vùng/Tỉnh" in raw_name: continue
        
        names = [n.strip() for n in raw_name.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i].replace("**", "").strip()
            if name == "": continue
            
            gl = "Provincial"
            if name in ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]:
                gl = "Regional"
                
            def get_val(col_idx):
                if col_idx >= len(cols): return None
                col_vals = cols[col_idx]
                val_idx = i if i < len(col_vals) else 0
                return normalize_number(col_vals[val_idx])

            # Col Mapping (PL4):
            # 0: Name, 1: HT Harv, 2: %, 3: NS, 4: SL HT, 5: Mùa Planted, 6: TĐ Planted, 7: Màu Tot, 8: Ngô, 9: Khoai Lang, 10: Sắn, 11: Khác
            v_ht_harv = get_val(1)
            v_yield = get_val(3)
            v_mua = get_val(5)
            v_td = get_val(6)
            v_mau = get_val(7)
            v_ngo = get_val(8)
            v_khoai = get_val(9)
            v_san = get_val(10)
            v_khac = get_val(11)
            
            if v_ht_harv: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": v_ht_harv/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_yield: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Yield", "value": v_yield, "unit": "quintal_per_ha", "data_type": "Actual"}))
            if v_mua: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v_mua/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_td: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Thu Đông"}, {"attribute": "Area_Planted", "value": v_td/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô", "sub_item": None}, {"attribute": "Area_Planted", "value": v_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang", "sub_item": None}, {"attribute": "Area_Planted", "value": v_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_san: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn", "sub_item": None}, {"attribute": "Area_Planted", "value": v_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác", "sub_item": None}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/08"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl1()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl2()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl3()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl4()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL4.json"))
    
    print("Successfully parsed Batch 1 (PL1, PL2, PL3, PL4) for August 2011.")
