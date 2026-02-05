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
    
    # Handle weird cases like "13549,6"
    if "," in s and "." not in s:
        parts = s.split(",")
        if len(parts[1]) == 3: s = s.replace(",", "") # Thousand
        else: s = s.replace(",", ".") # Decimal
    elif "." in s and "," not in s:
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

def extract_rows_from_file(file_path):
    if not os.path.exists(file_path): return []
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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_10_Phuluc_10_2011_f_PL1.md"
    metadata = {"year": 2011, "month": 10, "appendix_number": "PL1", "source_file": "2011_10_Phuluc_10_2011_f_PL1.md"}
    records = []
    t = {"year": 2011, "month": 10, "period_type": "Monthly", "report_date": "2011-10-15"}
    
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
        elif "Đồng bằng sông Cửu Long" in name: loc = "Đồng bằng sông Cửu Long"
        elif "Đồng bằng sông Hồng" in name: loc = "Đồng bằng sông Hồng"
        elif "Bắc Trung bộ" in name: loc = "Bắc Trung Bộ"
        
        item = {"sector": "Cultivation", "commodity": name}
        if "lúa mùa" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Mùa"})
        elif "lúa đông xuân" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Đông Xuân"})
        elif "vụ đông" in name.lower(): item.update({"commodity": "Cây vụ đông"})
        
        attr = "Area_Planted"
        if "thu hoạch" in name.lower(): attr = "Area_Harvested"
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_10_Phuluc_10_2011_f_PL2.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 10, "appendix_number": "PL2", "source_file": "2011_10_Phuluc_10_2011_f_PL2.md"}
    records = []
    t = {"year": 2011, "month": 10, "period_type": "Monthly", "report_date": "2011-10-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").replace("_", "").strip()
        if name_raw == "" or "Thu hoạch" in name_raw or "Col" in name_raw: continue
        
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
            
            v_hv = get_val(1)
            v_vudong = get_val(3)
            v_ngo = get_val(4)
            v_khoai = get_val(5)
            v_dt = get_val(6)
            v_lac = get_val(7)
            v_khac = get_val(8)
            v_rau = get_val(9)
            
            if v_hv: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": v_hv/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_vudong: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây vụ đông", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_vudong/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô"}, {"attribute": "Area_Planted", "value": v_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang"}, {"attribute": "Area_Planted", "value": v_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dt: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu tương"}, {"attribute": "Area_Planted", "value": v_dt/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_lac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lạc"}, {"attribute": "Area_Planted", "value": v_lac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây trồng khác"}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_rau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Rau đậu các loại"}, {"attribute": "Area_Planted", "value": v_rau/1000, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_10_Phuluc_10_2011_f_PL3.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 10, "appendix_number": "PL3", "source_file": "2011_10_Phuluc_10_2011_f_PL3.md"}
    records = []
    t = {"year": 2011, "month": 10, "period_type": "Monthly", "report_date": "2011-10-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").replace("_", "").strip()
        if name_raw == "" or "Vùng/Tỉnh" in name_raw or "Col" in name_raw: continue
        
        names = [n.strip() for n in name_raw.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i]
            if name == "" or "10,556" in name: continue
            gl = "Provincial"
            if name in ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
            
            def get_val(idx):
                if idx >= len(cols): return None
                v_list = cols[idx]
                return normalize_number(v_list[i if i < len(v_list) else 0])
            
            v_mua = get_val(1)
            v_dx = get_val(2)
            v_mau = get_val(3)
            v_ngo = get_val(4)
            v_khoai = get_val(5)
            v_san = get_val(6)
            v_khac = get_val(7)
            
            if v_mua: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v_mua/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dx: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v_dx/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v_mau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_ngo: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Ngô"}, {"attribute": "Area_Planted", "value": v_ngo/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khoai: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Khoai lang"}, {"attribute": "Area_Planted", "value": v_khoai/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_san: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Sắn"}, {"attribute": "Area_Planted", "value": v_san/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_khac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây lương thực có củ khác"}, {"attribute": "Area_Planted", "value": v_khac/1000, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_10_Phuluc_10_2011_f_PL4.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 10, "appendix_number": "PL4", "source_file": "2011_10_Phuluc_10_2011_f_PL4.md"}
    records = []
    t = {"year": 2011, "month": 10, "period_type": "Monthly", "report_date": "2011-10-15"}
    
    for row in rows:
        if len(row) < 5: continue
        name_raw = row[0].replace("**", "").replace("_", "").strip()
        if name_raw == "" or "Cây công nghiệp" in name_raw or "Col" in name_raw: continue
        
        names = [n.strip() for n in name_raw.split("<br>")]
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i]
            if name == "" or name == "27,875": continue
            gl = "Provincial"
            if name in ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
            
            def get_val(idx):
                if idx >= len(cols): return None
                v_list = cols[idx]
                return normalize_number(v_list[i if i < len(v_list) else 0])
            
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/10"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 10}, "records": parse_pl1()}, os.path.join(out_dir, "2011_10_Phuluc_10_2011_f_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 10}, "records": parse_pl2()}, os.path.join(out_dir, "2011_10_Phuluc_10_2011_f_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 10}, "records": parse_pl3()}, os.path.join(out_dir, "2011_10_Phuluc_10_2011_f_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 10}, "records": parse_pl4()}, os.path.join(out_dir, "2011_10_Phuluc_10_2011_f_PL4.json"))
    
    print("Successfully parsed Batch 1 (PL1-PL4) for October 2011.")
