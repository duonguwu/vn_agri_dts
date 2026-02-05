import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
    REGION_DATA = json.load(f)

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|": return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    norm_loc = loc_name
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "ĐB sông Cửu Long": "Đồng bằng sông Cửu Long"
    }
    if loc_name in alias_map: norm_loc = alias_map[loc_name]
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name"] = "Cả nước"

    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl3_12():
    metadata = {"year": 2009, "month": 12, "appendix_number": "PL3", "source_file": "2009_12_Phuluc_T12_2009_PL3.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    pl3_data = [
        ["Miền Nam", "778256", "465583", "1240890", "26696", "10260", "4084", "8650", "3913"],
        ["D.H Nam Trung Bộ", "93799", "93799", "67990", "9344", "5686", "3658", None, None],
        ["TP Đà Nẵng", "4004", "4004", "700", None, None, None, None, None],
        ["Quảng Nam", "45128", "45128", "3051", "9344", "5686", "3658", None, None],
        ["Quảng Ngãi", "5900", "5900", "9640", None, None, None, None, None],
        ["Bình Định", "25505", "25505", "45900", None, None, None, None, None],
        ["Phú Yên", "7262", "7262", "6712", None, None, None, None, None],
        ["Khánh Hoà", "6000", "6000", "1987", None, None, None, None, None],
        ["Tây Nguyên", "131280", "120098", "9926", "1509", "1300", "180", "29", "0"],
        ["Kon Tum", "16700", "16700", None, None, None, None, None, None],
        ["Gia Lai", "46843", "36705", None, "1509", "1300", "180", "29", None],
        ["Đắc Lắc", "44167", "44167", None, None, None, None, None, None],
        ["Đắc Nông", "7000", "7000", None, None, None, None, None, None],
        ["Lâm Đồng", "16570", "15526", "9926", None, None, None, None, None],
        ["Đông Nam Bộ", "175342", "147741", "42179", "15335", "2766", "246", "8621", "3702"],
        ["TP Hồ Chí Minh", "15500", "6220", "6967", None, None, None, None, None],
        ["Ninh Thuận", "8970", "7000", "1100", None, None, None, None, None],
        ["Bình Phước", "9900", "5428", None, None, None, None, None, None],
        ["Tây Ninh", "57720", "51377", "8484", "8187", "1895", None, "3001", "3291"],
        ["Bình Dương", "4230", "3921", "97", "6202", None, "171", "5620", "411"],
        ["Đồng Nai", "29780", "25448", "5700", None, None, None, None, None],
        ["Bình Thuận", "36700", "36700", "15741", None, None, None, None, None],
        ["Bà Rịa-V.Tàu", "12542", "11647", "4090", "946", "871", "75", None, None],
        ["ĐBS Cửu Long", "377835", "103945", "1120795", "508", "508", None, None, "211"],
        ["Long An", "13071", "13071", "86794", None, None, None, None, None],
        ["Đồng Tháp", None, None, "159156", "474", "263", None, None, "211"],
        ["An Giang", "7637", None, "164054", None, None, None, None, None],
        ["Tiền Giang", None, None, "82747", None, None, None, None, None],
        ["Vĩnh Long", None, None, "66974", "108", "108", None, None, None],
        ["Bến Tre", "36245", "19293", "636", None, None, None, None, None],
        ["Kiên Giang", "62782", None, "266167", None, None, None, None, None],
        ["Cần Thơ", None, None, "83707", None, None, None, None, None],
        ["Hậu Giang", None, None, "42144", None, None, None, None, None],
        ["Trà Vinh", "91634", "49400", "34257", None, None, None, None, None],
        ["Sóc Trăng", "21746", "9788", "117261", "137", "137", None, None, None],
        ["Bạc Liêu", "68521", "12393", "16898", None, None, None, None, None],
        ["Cà Mau", "76199", None, None, None, None, None, None, None],
    ]
    for row in pl3_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 12, "period_type": "Cumulative", "report_date": "2009-12-15"}
        
        # 1. Lúa Mùa Gieo cấy
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vgc / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa Mùa Thu hoạch
        vth = normalize_number(row[2])
        if vth: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": vth / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Lúa Đông Xuân Gieo cấy
        vdx = normalize_number(row[3])
        if vdx: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": vdx / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 4. Màu lương thực items - Col 4, 5, 6, 7, 8
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (c, s) in enumerate(items):
            v_alt = normalize_number(row[idx+4])
            if v_alt is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v_alt / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/12"
    save_json(parse_pl3_12(), os.path.join(out_dir, "2009_12_Phuluc_T12_2009_PL3.json"))
    print("Successfully parsed PL3 for Dec 2009.")
