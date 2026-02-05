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
            if len(parts[-1]) == 3 and len(parts[0]) <= 3: s = s.replace(",", "") # Thousands
            elif len(parts[-1]) != 3: s = s.replace(",", ".") # Decimal
            else: s = s.replace(",", "")
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
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg B": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "T.P Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu", "TP Đà Nẵng": "Đà Nẵng",
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

def parse_pl1():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL1.md"
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL1", "source_file": "2011_09_Phuluc_09_2011_f_PL1.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-15"}
    
    rows = extract_rows_from_file(fpath)
    for row in rows:
        if len(row) < 4: continue
        name = row[0].replace("**", "").strip()
        if "Chỉ tiêu" in name or name == "": continue
        
        val = normalize_number(row[3])
        if not val: continue
        
        loc = "Cả nước"
        if "miền Nam" in name: loc = "Miền Nam"
        elif "miền Bắc" in name or "Miền Bắc" in name: loc = "Miền Bắc"
        elif "Đồng bằng sông Cửu Long" in name or "ĐBSCL" in name: loc = "Đồng bằng sông Cửu Long"
        elif "Đồng bằng sông Hồng" in name: loc = "Đồng bằng sông Hồng"
        
        item = {"sector": "Cultivation", "commodity": name}
        if "lúa hè thu" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Hè Thu"})
        elif "lúa thu đông" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Thu Đông"})
        elif "lúa mùa" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Mùa"})
        
        attr = "Area_Planted"
        if "thu hoạch" in name.lower(): attr = "Area_Harvested"
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL2.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL2", "source_file": "2011_09_Phuluc_09_2011_f_PL2.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").replace("_", "").strip()
        if name_raw == "" or "Gieo trồng" in name_raw or "Col" in name_raw: continue
        
        # Explode
        names = [n.strip() for n in name_raw.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i]
            if name == "": continue
            gl = "Provincial"
            if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
            
            def get_val(idx):
                if idx >= len(cols): return None
                v_list = cols[idx]
                return normalize_number(v_list[i if i < len(v_list) else 0])
            
            val_mua = get_val(1)
            val_ht = get_val(2)
            val_mau = get_val(3)
            val_ngo = get_val(4)
            val_khoai = get_val(5)
            val_san = get_val(6)
            val_khac = get_val(7)
            
            if val_mua: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": val_mua/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if val_ht: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": val_ht/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if val_mau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": val_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if val_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô"}, {"attribute": "Area_Planted", "value": val_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if val_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang"}, {"attribute": "Area_Planted", "value": val_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if val_san: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn"}, {"attribute": "Area_Planted", "value": val_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if val_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác"}, {"attribute": "Area_Planted", "value": val_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL3.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL3", "source_file": "2011_09_Phuluc_09_2011_f_PL3.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").strip()
        if name_raw == "" or "DT cây" in name_raw or "Col" in name_raw: continue
        
        names = [n.strip() for n in name_raw.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i]
            if name == "": continue
            gl = "Provincial"
            if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]: gl = "Regional"
            
            def get_val(idx):
                if idx >= len(cols): return None
                v_list = cols[idx]
                return normalize_number(v_list[i if i < len(v_list) else 0])
            
            v_ccn = get_val(1)
            v_dt = get_val(2)
            v_lac = get_val(3)
            v_mia = get_val(4)
            v_tl = get_val(5)
            v_rau = get_val(7)
            
            if v_ccn: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_ccn/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dt: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu tương"}, {"attribute": "Area_Planted", "value": v_dt/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_lac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lạc"}, {"attribute": "Area_Planted", "value": v_lac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mia: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Mía"}, {"attribute": "Area_Planted", "value": v_mia/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_tl: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Thuốc lá"}, {"attribute": "Area_Planted", "value": v_tl/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_rau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại"}, {"attribute": "Area_Planted", "value": v_rau/1000, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL4.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL4", "source_file": "2011_09_Phuluc_09_2011_f_PL4.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").strip()
        if name_raw == "" or "Vùng/Tỉnh" in name_raw or "Col" in name_raw: continue
        
        names = [n.strip() for n in name_raw.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i]
            if name == "" or name == "Cà Mau": # Row 56 Cà Ma Cà Ma
                if i==0: name = "Cà Mau"
                else: continue
            gl = "Provincial"
            if name in ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
            
            def get_val(idx):
                if idx >= len(cols): return None
                v_list = cols[idx]
                return normalize_number(v_list[i if i < len(v_list) else 0])
            
            v_td = get_val(1)
            v_mua = get_val(2)
            v_mau = get_val(3)
            v_ngo = get_val(4)
            v_khoai = get_val(5)
            v_san = get_val(6)
            v_khac = get_val(7)
            
            if v_td: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Thu Đông"}, {"attribute": "Area_Planted", "value": v_td/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mua: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v_mua/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô"}, {"attribute": "Area_Planted", "value": v_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang"}, {"attribute": "Area_Planted", "value": v_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_san: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn"}, {"attribute": "Area_Planted", "value": v_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực khác"}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl5():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL5.md"
    # Actually need to use the absolute path from the survey
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_09_Phuluc_09_2011_f_PL5.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 9, "appendix_number": "PL5", "source_file": "2011_09_Phuluc_09_2011_f_PL5.md"}
    records = []
    t = {"year": 2011, "month": 9, "period_type": "Monthly", "report_date": "2011-09-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").strip()
        if name_raw == "" or "Cây công nghiệp" in name_raw or "Col" in name_raw: continue
        
        # Specific fix for "D.H Nam Trg B ộ"
        if "D.H Nam Trg B" in name_raw: name_raw = "Duyên hải Nam Trung Bộ"
        if "TP Hồ Chí Min" in name_raw: name_raw = "Hồ Chí Minh"
        
        names = [n.strip() for n in name_raw.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i]
            if name == "" or name == "h": continue
            gl = "Provincial"
            if name in ["Miền Nam", "Duyên hải Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long", "D.H Nam Trg B"]: gl = "Regional"
            
            def get_val(idx):
                if idx >= len(cols): return None
                v_list = cols[idx]
                return normalize_number(v_list[i if i < len(v_list) else 0])
            
            # 1: CCN Total, 2: Đậu tương, 3: Lạc, 4: Vừng, 5: Thuốc lá, 6: Mía, 7: Bông, 8: Đay/Lác, 9: Rau, 10: Đậu
            v_ccn = get_val(1)
            v_dt = get_val(2)
            v_lac = get_val(3)
            v_vung = get_val(4)
            v_tl = get_val(5)
            v_mia = get_val(6)
            v_bong = get_val(7)
            v_day = get_val(8)
            v_rau = get_val(9)
            v_dau = get_val(10)
            
            if v_ccn: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_ccn/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dt: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu tương"}, {"attribute": "Area_Planted", "value": v_dt/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_lac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lạc"}, {"attribute": "Area_Planted", "value": v_lac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_vung: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Vừng"}, {"attribute": "Area_Planted", "value": v_vung/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_tl: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Thuốc lá"}, {"attribute": "Area_Planted", "value": v_tl/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mia: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Mía"}, {"attribute": "Area_Planted", "value": v_mia/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_bong: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Bông"}, {"attribute": "Area_Planted", "value": v_bong/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_day: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đay, Lác"}, {"attribute": "Area_Planted", "value": v_day/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_rau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Rau các loại"}, {"attribute": "Area_Planted", "value": v_rau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu các loại"}, {"attribute": "Area_Planted", "value": v_dau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/09"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl1()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl2()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl3()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl4()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL4.json"))
    save_json({"metadata": {"year": 2011, "month": 9}, "records": parse_pl5()}, os.path.join(out_dir, "2011_09_Phuluc_09_2011_f_PL5.json"))
    
    print("Successfully parsed Batch 1 (PL1-PL5) for September 2011.")
