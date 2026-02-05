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
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL1.md"
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL1", "source_file": "2011_12_Phuluc_12_2011_f_PL1.md"}
    records = []
    t = {"year": 2011, "month": 12, "period_type": "Monthly", "report_date": "2011-12-15"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 4: continue
        name = row[0].replace("**", "").strip()
        val_str = row[3]
        val = normalize_number(val_str)
        if val is None: continue
        
        loc = "Cả nước"
        if "miền Nam" in name: loc = "Miền Nam"
        if "miền Bắc" in name: loc = "Miền Bắc"
        if "Đồng bằng sông Cửu Long" in name: loc = "Đồng bằng sông Cửu Long"
        
        item = {"sector": "Cultivation", "commodity": name}
        attr = "Area_Planted"
        if "Thu hoạch" in name: attr = "Area_Harvested"
        
        if "lúa đông xuân" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Đông Xuân"})
        elif "lúa mùa" in name.lower(): item.update({"commodity": "Lúa", "sub_item": "Mùa"})
        elif "vụ đông" in name.lower(): item.update({"commodity": "Cây vụ đông"})
        elif "Ngô" in name: item.update({"commodity": "Ngô"})
        elif "Khoai lang" in name: item.update({"commodity": "Khoai lang"})
        elif "Đậu tương" in name: item.update({"commodity": "Đậu tương"})
        elif "Rau, đậu" in name: item.update({"commodity": "Rau đậu các loại"})
        
        records.append(create_record(metadata, t, loc, "National" if loc == "Cả nước" else "Regional", item, {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Actual"}))
    return records

def parse_pl2():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL2.md"
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL2", "source_file": "2011_12_Phuluc_12_2011_f_PL2.md"}
    records = []
    t = {"year": 2011, "month": 12, "period_type": "Monthly", "report_date": "2011-12-15"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 9: continue
        name = row[0].replace("**", "").strip()
        if "Col" in name or name == "" or "DT" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN", "Bắc Trung Bộ"]: gl = "Regional"
        
        def add(idx, comm, sub=None):
            val = normalize_number(row[idx])
            if val: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
        add(1, "Cây vụ đông", "Tổng số")
        add(2, "Ngô")
        add(3, "Khoai lang")
        add(4, "Khoai tây")
        add(5, "Đậu tương")
        add(6, "Lạc")
        add(7, "Cây khác")
        add(8, "Rau đậu các loại")
    return records

def parse_pl3():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL3.md"
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL3", "source_file": "2011_12_Phuluc_12_2011_f_PL3.md"}
    records = []
    t = {"year": 2011, "month": 12, "period_type": "Monthly", "report_date": "2011-12-15"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 8: continue
        # Handle weird spaced names for Binh Phuoc in PL3
        name = row[0].replace("**", "").replace(" ", "").strip()
        if "BìnhPhước" in name: name = "Bình Phước"
        if "Vùng/Tỉnh" in name or name == "" or "Thuhoạch" in name: continue
        
        gl = "Provincial"
        if name in ["MiềnNam", "D.HNamTrungBộ", "TâyNguyên", "ĐôngNamBộ", "ĐBS sCửuLong"]: 
            gl = "Regional"
            if "D.HNamTrungBộ" in name: name = "Duyên hải Nam Trung Bộ"
            if "MiềnNam" in name: name = "Miền Nam"
            if "ĐBS sCửuLong" in name: name = "Đồng bằng sông Cửu Long"
            
        def add(idx, comm, sub=None, attr="Area_Planted"):
            val = normalize_number(row[idx])
            if val: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": attr, "value": val/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
        add(1, "Lúa", "Mùa", "Area_Harvested")
        add(3, "Lúa", "Đông Xuân")
        add(4, "Màu lương thực", "Tổng số")
        add(5, "Ngô")
        add(6, "Khoai lang")
        add(7, "Sắn")
        add(8, "Cây lương thực có củ khác")
    return records

def parse_pl4():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL4.md"
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL4", "source_file": "2011_12_Phuluc_12_2011_f_PL4.md"}
    records = []
    t = {"year": 2011, "month": 12, "period_type": "Monthly", "report_date": "2011-12-15"}
    
    rows = extract_rows(fpath)
    for row in rows:
        if len(row) < 10: continue
        name = row[0].replace("**", "").strip()
        if "Col" in name or name == "" or "Tổng" in name: continue
        
        gl = "Provincial"
        if name in ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]: gl = "Regional"
        
        def add(idx, comm, sub=None):
            val = normalize_number(row[idx])
            if val: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": comm, "sub_item": sub}, {"attribute": "Area_Planted", "value": val/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
        add(1, "Cây công nghiệp ngắn ngày", "Tổng số")
        add(2, "Đậu tương")
        add(3, "Lạc")
        add(4, "Vừng")
        add(5, "Thuốc lá")
        add(6, "Mía")
        add(7, "Bông")
        add(8, "Đay, Lác")
        add(9, "Rau các loại")
        add(10, "Đậu các loại")
    return records

def parse_pl11():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_12_Phuluc_12_2011_f_PL11.md"
    metadata = {"year": 2011, "month": 12, "appendix_number": "PL11", "source_file": "2011_12_Phuluc_12_2011_f_PL11.md"}
    records = []
    
    rows = extract_rows(fpath)
    # This table tracks progress by month. We only take the "Tháng 12" row for Dec status.
    for row in rows:
        if len(row) < 7: continue
        month_name = row[0].strip()
        if month_name != "Tháng 12": continue
        
        t = {"year": 2011, "month": 12, "period_type": "Cumulative", "report_date": "2011-12-31"}
        
        def add(idx, sub, attr, unit):
            val = normalize_number(row[idx])
            if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Salt", "commodity": "Muối", "sub_item": sub}, {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"}))
            
        add(1, "Tổng số", "Area_Planted", "ha")
        add(2, "Muối thủ công", "Area_Planted", "ha")
        add(3, "Muối CN", "Area_Planted", "ha")
        add(4, "Tổng số", "Production", "ton")
        add(5, "Muối thủ công", "Production", "ton")
        add(6, "Muối CN", "Production", "ton")
        
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/12"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl1()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL1.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl2()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL2.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl3()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL3.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl4()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL4.json"))
    save_json({"metadata": {"year": 2011, "month": 12}, "records": parse_pl11()}, os.path.join(out_dir, "2011_12_Phuluc_12_2011_f_PL11.json"))
    
    print("Successfully parsed Batch 1 (PL1-PL4, PL11) for December 2011.")
