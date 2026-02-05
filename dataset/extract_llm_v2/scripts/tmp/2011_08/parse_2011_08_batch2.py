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
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Trung": "Miền Trung",
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "T.P Hồ Chí Minh": "Hồ Chí Minh", 
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Bắc Giang": "Bắc Giang", "Yên Bái": "Yên Bái", "Thanh Hoá": "Thanh Hóa", "Đắc Lắc": "Đắk Lắk", "Đắc Nông": "Đắk Nông", "Lâm Đồng": "Lâm Đồng"
    }
    
    loc_clean = loc_name.strip()
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

def parse_2011_08_pl5():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL5.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL5", "source_file": "2011_08_Phuluc_08_2011_f_PL5.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-15"}
    
    for row in rows:
        if len(row) < 5: continue
        raw_name = row[0]
        if "Miền Nam" not in raw_name and row[0] == "": continue
        if "Cây công nghiệp" in raw_name or "Col" in raw_name: continue
        
        # Specific fix for Lâm Đồng (Row 43)
        if "Lâm" in raw_name and "Đồng" in raw_name:
            names = ["Lâm Đồng"]
        else:
            names = [n.strip() for n in raw_name.split("<br>")]
            
        cols = [ [v.strip() for v in c.split("<br>")] for c in row ]
        
        for i in range(len(names)):
            name = names[i].replace("**", "").replace("_", "").strip()
            if name == "": continue
            
            gl = "Provincial"
            if name in ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]:
                gl = "Regional"
                
            def get_val(col_idx):
                if col_idx >= len(cols): return None
                col_vals = cols[col_idx]
                val_idx = i if i < len(col_vals) else 0
                return normalize_number(col_vals[val_idx])

            # Col Mapping: 0: Name, 1: CCN Tot, 2: Đậu tương, 3: Lạc, 4: Vừng, 5: Thuốc lá, 6: Mía, 7: Bông, 8: Đay, 9: Rau, 10: Đậu
            # Wait, looking at file: Col 2 is "Tổng số" as sub-header. 
            # Row index 1 is CCN Tot.
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
            if v_dt: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu tương", "sub_item": None}, {"attribute": "Area_Planted", "value": v_dt/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_lac: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lạc", "sub_item": None}, {"attribute": "Area_Planted", "value": v_lac/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_vung: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Vừng", "sub_item": None}, {"attribute": "Area_Planted", "value": v_vung/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_tl: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Thuốc lá", "sub_item": None}, {"attribute": "Area_Planted", "value": v_tl/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_mia: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Mía", "sub_item": "Trồng mới"}, {"attribute": "Area_Planted", "value": v_mia/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_bong: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Bông", "sub_item": None}, {"attribute": "Area_Planted", "value": v_bong/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_day: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đay, Lác", "sub_item": None}, {"attribute": "Area_Planted", "value": v_day/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_rau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Rau các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": v_rau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            if v_dau: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Đậu các loại", "sub_item": None}, {"attribute": "Area_Planted", "value": v_dau/1000, "unit": "1000_ha", "data_type": "Actual"}))
            
    return records

def parse_2011_08_pl6():
    # Summarized Forestry Indicators 8M
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL6", "source_file": "2011_08_Phuluc_08_2011_f_PL6.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    
    data = [
        ("Diện tích rừng trồng mới tập trung", 110.8, "1000_ha"),
        ("Rừng phòng hộ, đặc dụng", 12.0, "1000_ha"),
        ("Rừng sản xuất", 98.8, "1000_ha"),
        ("Diện tích rừng trồng được chăm sóc", 302.8, "1000_ha"),
        ("Số cây lâm nghiệp trồng phân tán", 137.6, "million_trees"),
        ("Diện tích rừng được khoanh nuôi tái sinh", 696.0, "1000_ha"),
        ("Diện tích rừng được khoán bảo vệ", 2420.5, "1000_ha"),
        ("Sản lượng gỗ", 2781.0, "1000_m3")
    ]
    for item, val, unit in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Output", "value": val, "unit": unit, "data_type": "Estimate"}))
    return records

def parse_2011_08_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL7.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL7", "source_file": "2011_08_Phuluc_08_2011_f_PL7.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    
    for row in rows:
        if len(row) < 5: continue
        name = row[1].replace("**", "").replace("_", "").strip()
        if "Diện tích" in name or "Cả nước" in name or "TT" in name or "Col" in name: 
            if "Cả nước" in name: pass
            else: continue
        if name == "": continue
        
        gl = "Provincial"
        if name in ["Cả nước", "Miền bắc", "Miền Bắc", "Miền Nam", "ĐB. sông Hồng", "Trung du và miền núi phía Bắc", "Bắc Trung Bộ", 
                    "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]:
            gl = "National" if name == "Cả nước" else "Regional"
            
        # 0: TT, 1: Name, 2: Tot New, 3: PH/DD, 4: SX, 5: Care, 6: Protect
        v_new = normalize_number(row[2])
        v_ph = normalize_number(row[3])
        v_sx = normalize_number(row[4])
        v_care = normalize_number(row[5])
        v_prot = normalize_number(row[6]) if len(row) > 6 else None
        
        if v_new: records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Tổng số"}, {"attribute": "Output", "value": v_new, "unit": "ha", "data_type": "Actual"}))
        if v_ph: records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Rừng phòng hộ, đặc dụng"}, {"attribute": "Output", "value": v_ph, "unit": "ha", "data_type": "Actual"}))
        if v_sx: records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung", "sub_item": "Rừng sản xuất"}, {"attribute": "Output", "value": v_sx, "unit": "ha", "data_type": "Actual"}))
        if v_care: records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng được chăm sóc", "sub_item": "Sản xuất"}, {"attribute": "Output", "value": v_care, "unit": "ha", "data_type": "Actual"}))
        if v_prot: records.append(create_record(metadata, t, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng được khoán bảo vệ", "sub_item": "Sản xuất"}, {"attribute": "Output", "value": v_prot, "unit": "ha", "data_type": "Actual"}))
        
    return records

def parse_2011_08_pl8():
    # Fishery Summary 8M
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL8", "source_file": "2011_08_Phuluc_08_2011_f_PL8.md"}
    records = []
    t_month = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-31"}
    t_7m = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    t_8m = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    
    # [Item, July_Cum, Aug_Month, Aug_Cum]
    data = [
        ("Tổng sản lượng", 3039.0, 536.0, 3575.0),
        ("Sản lượng khai thác", 1476.0, 254.0, 1730.0),
        ("Khai thác biển", 1380.0, 239.0, 1619.0),
        ("Khai thác nội địa", 96.0, 15.0, 111.0),
        ("Sản lượng nuôi trồng", 1563.0, 282.0, 1845.0)
    ]
    for item, v7c, v8m, v8c in data:
        records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": v7c, "unit": "1000_ton", "data_type": "Actual"}))
        records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": v8m, "unit": "1000_ton", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_8m, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": v8c, "unit": "1000_ton", "data_type": "Estimate"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/08"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl5()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL5.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl6()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl7()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL7.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl8()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL8.json"))
    
    print("Successfully parsed Batch 2 (PL5, PL6, PL7, PL8) for August 2011.")
