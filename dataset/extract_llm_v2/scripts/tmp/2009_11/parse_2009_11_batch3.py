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
    if loc_name in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][loc_name]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][loc_name]["region_name"]
    elif loc_name in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][loc_name]
        geo_context["region_name"] = loc_name
    elif loc_name == "Cả nước":
        geo_context["region_id"] = "NATIONAL"
        geo_context["region_name"] = "Cả nước"
    
    # Handle aliases
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ"
    }
    if loc_name in alias_map:
        real_name = alias_map[loc_name]
        geo_context["region_id"] = REGION_DATA["regions"].get(real_name)
        geo_context["region_name"] = real_name

    record = {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": geo_context,
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata
    }
    if comp: record["comparison_context"] = comp
    return record

def parse_pl5_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL5", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL5.md"}
    records = []
    # TT, Item, Unit, Plan, TH CK, ƯTH 11T
    rows = [
        ["1", "Trồng rừng tập trung", "1000_ha", "227.3", "197.7", "187.8", "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000_ha", "60.0", "32.4", "39.6", "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000_ha", "167.3", "165.3", "148.2", "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000_ha", "149.7", "248.2", "240.6", "Other"],
        ["3", "Trồng cây nhân dân", "million_trees", "200", "180.0", "174.0", "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000_ha", "506.0", "649.6", "768.8", "Other"],
        ["5", "Khoán bảo vệ rừng", "1000_ha", "1524", "2127.0", "2533.6", "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000_m3", "4380.0", "3113.7", "3320.0", "Wood_Volume"],
    ]
    for r in rows:
        tt, item, unit, plan, ck, uth, attr = r
        loc, geo = "Cả nước", "National"
        # Cumulative 11 months
        t11c = {"year": 2009, "month": 11, "period_type": "Cumulative"}
        v_uth = normalize_number(uth)
        if v_uth:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(ck), "reference_period": "2008"} # Simplified comparison
            records.append(create_record(metadata, t11c, loc, geo, {"sector": "Forestry", "commodity": item}, {"attribute": attr, "value": v_uth, "unit": unit, "data_type": "Actual"}, comp))
        # Plan
        v_plan = normalize_number(plan)
        if v_plan:
            tp = {"year": 2009, "month": 12, "period_type": "Annual"}
            records.append(create_record(metadata, tp, loc, geo, {"sector": "Forestry", "commodity": item}, {"attribute": attr, "value": v_plan, "unit": unit, "data_type": "Plan"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl6_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL6", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL6.md"}
    records = []
    # TT, Item, Plan, TH 10T, ƯTH T11, 11T, TH 11T/08
    rows = [
        ["I", "Tổng sản lượng", "4600", "4020", "397", "4417", "4172"],
        ["1", "Sản lượng khai thác", "2200", "1843", "167", "2010", "1932"],
        ["1.1", "Khai thác biển", "2000", "1689", "147", "1836", "1757"],
        ["1.2", "Khai thác nội địa", "200", "154", "20", "174", "175"],
        ["2", "Sản lượng nuôi trồng", "2400", "2177", "230", "2407", "2240"],
    ]
    for r in rows:
        tt, item, plan, v10, v11, v11c, v08c = r
        loc, geo = "Cả nước", "National"
        i = {"sector": "Fishery", "commodity": item}
        # Monthly Nov
        val11 = normalize_number(v11)
        if val11: records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Monthly"}, loc, geo, i, {"attribute": "Production", "value": val11, "unit": "1000_ton", "data_type": "Actual"}))
        # Cumulative 11 months
        val11c = normalize_number(v11c)
        if val11c:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(v08c), "reference_period": "2008"}
            records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Cumulative"}, loc, geo, i, {"attribute": "Production", "value": val11c, "unit": "1000_ton", "data_type": "Actual"}, comp))
        # Plan
        val_p = normalize_number(plan)
        if val_p: records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, loc, geo, i, {"attribute": "Production", "value": val_p, "unit": "1000_ton", "data_type": "Plan"}))
        
    return {"metadata": metadata, "records": records}


def parse_pl7_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL7", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL7.md"}
    records = []
    # Storm 11 damage update to 20/11/2009
    # Types: Lúa ngập (ha), màu ngập (ha), cây cn hư hại (ha), cây ăn quả (ha).
    cols = ["Quảng Ngãi", "Bình Định", "Phú Yên", "Khánh Hoà", "Ninh Thuận", "Đắc Lắc", "Gia Lai"]
    pl7_rows = [
        ["Tổng diện tích lúa bị úng, ngập", "Ha", [35, 4340, 3875, 3632, 2410, 276, 4725], "Lúa"],
        ["Tổng diện tích hoa mầu bị ngập", "Ha", [620, 6294, 25738, 7503, 658, 13468, 1868], "Màu lương thực"],
        ["DT cây công nghiệp hư hại", "Ha", [820, 964, 656, None, None, None, 6125], "Cây công nghiệp"],
        ["DT cây ăn quả hư hại", "ha", [None, None, None, None, 321, None, None], "Cây ăn quả"],
    ]
    for r in pl7_rows:
        item_name, unit, vals, commodity = r
        for i, val in enumerate(vals):
            v = normalize_number(val)
            if v:
                records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Event", "event_name": "Bão số 11"}, cols[i], "Provincial", {"sector": "Cultivation", "commodity": commodity, "item_raw": item_name}, {"attribute": "Area_Damaged", "value": v, "unit": "ha", "data_type": "Actual"}))
                
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/11"
    save_json(parse_pl5_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL5.json"))
    save_json(parse_pl6_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL6.json"))
    save_json(parse_pl7_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL7.json"))
    print("Successfully parsed PL5, PL6, PL7 for Nov 2009.")
