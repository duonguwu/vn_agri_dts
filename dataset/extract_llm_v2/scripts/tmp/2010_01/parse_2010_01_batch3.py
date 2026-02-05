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
        geo_context["location_name"] = loc_name
    elif loc_name in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][loc_name]
        geo_context["region_name"] = loc_name
        geo_context["location_name"] = loc_name
    elif loc_name == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name"] = "Cả nước"
    elif loc_name == "Bộ NN & PTNT":
        geo_context["region_id"] = "CENTRAL"; geo_context["region_name"] = "Bộ NN & PTNT"

    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl7_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL7", "source_file": "2010_01_PhuLuc_T01_2010_PL7.md"}
    records = []
    # TT, Item, v09, plan10, v10
    rows = [
        ["I", "Tổng sản lượng", "4846", "5050", "430"],
        ["1", "Sản lượng khai thác", "2277", "2400", "230"],
        ["1.1", "Khai thác biển", "2068", "2180", "220"],
        ["1.2", "Khai thác nội địa", "209", "220", "10"],
        ["2", "Sản lượng nuôi trồng", "2569", "2650", "200"],
    ]
    for r in rows:
        tt, item, v09, p10, v10 = r
        loc, gl = "Cả nước", "National"
        # Monthly Jan 2010
        records.append(create_record(metadata, {"year": 2010, "month": 1, "period_type": "Monthly"}, loc, gl, {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": normalize_number(v10), "unit": "1000_ton", "data_type": "Actual"}))
        # 2010 Plan
        records.append(create_record(metadata, {"year": 2010, "month": 12, "period_type": "Annual"}, loc, gl, {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": normalize_number(p10), "unit": "1000_ton", "data_type": "Plan"}))
        # 2009 Actual
        records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, loc, gl, {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": normalize_number(v09), "unit": "1000_ton", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}

def parse_pl8_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL8", "source_file": "2010_01_PhuLuc_T01_2010_PL8.md"}
    records = []
    # Items for Export
    xk_items = [
        ["Tổng kim ngạch XK", None, "1000", None, "1161"],
        ["Nông sản chính", None, "522", None, "636"],
        ["Cà phê", "137", "211", "139", "193"],
        ["Cao su", "39", "50", "42", "88"],
        ["Gạo", "304", "129", "340", "161"],
    ]
    for r in xk_items:
        i, l09, v09, l10, v10 = r
        loc, gl = "Cả nước", "National"
        if v10: records.append(create_record(metadata, {"year": 2010, "month": 1, "period_type": "Monthly"}, loc, gl, {"sector": "Trade", "commodity": i}, {"attribute": "Export_Value", "value": normalize_number(v10), "unit": "million_USD", "data_type": "Actual"}))
        if l10: records.append(create_record(metadata, {"year": 2010, "month": 1, "period_type": "Monthly"}, loc, gl, {"sector": "Trade", "commodity": i}, {"attribute": "Export_Volume", "value": normalize_number(l10), "unit": "1000_ton", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}

def parse_pl9_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL9", "source_file": "2010_01_PhuLuc_T01_2010_PL9.md"}
    records = []
    rows = [
        ["Vốn ngân sách giao đầu năm", "3186262", "153850"],
        ["Vốn thực hiện đầu tư", "2771000", "144600"],
        ["Đầu tư Thuỷ lợi", "1735000", "115000"],
        ["Đầu tư Nông nghiệp", "415300", "10500"],
        ["Đầu tư Lâm nghiệp", "260000", "7250"],
        ["Đầu tư Thuỷ sản", "25000", "1000"],
    ]
    for r in rows:
        i, p10, v10 = r
        loc, gl = "Bộ NN & PTNT", "National"
        records.append(create_record(metadata, {"year": 2010, "month": 1, "period_type": "Monthly"}, loc, gl, {"sector": "Investment", "commodity": i}, {"attribute": "Investment_Amount", "value": normalize_number(v10), "unit": "million_VND", "data_type": "Actual"}))
        records.append(create_record(metadata, {"year": 2010, "month": 12, "period_type": "Annual"}, loc, gl, {"sector": "Investment", "commodity": i}, {"attribute": "Investment_Amount", "value": normalize_number(p10), "unit": "million_VND", "data_type": "Plan"}))
    return {"metadata": metadata, "records": records}

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/01"
    save_json(parse_pl7_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL7.json"))
    save_json(parse_pl8_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL8.json"))
    save_json(parse_pl9_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL9.json"))
    print("Successfully parsed PL7, PL8, PL9 for Jan 2010.")
