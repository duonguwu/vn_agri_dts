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
        "HÀ NỘI (MỞ RỘNG)": "Hà Nội", "HÀ NỘI": "Hà Nội",
        "TP HỒ CHÍ MINH": "TP Hồ Chí Minh", "TP. HỒ CHÍ MINH": "TP Hồ Chí Minh",
        "HOA KỲ": "Hoa Kỳ", "NHẬT BẢN": "Nhật Bản", "TRUNG QUỐC": "Trung Quốc",
        "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long"
    }
    ln_up = loc_name.upper()
    if ln_up in alias_map: loc_name = alias_map[ln_up]
    
    if loc_name in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][loc_name]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][loc_name]["region_name"]
    elif loc_name in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][loc_name]
        geo_context["region_name"] = loc_name

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

def parse_pl8a_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL8a", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL7.md"}
    records = []
    # XK Rows: 0:Item, 1:val08c, 2:val11, 3:val11c, 4:cp_yoy
    xk_rows = [
        ["Tổng kim ngạch XK", None, "1300", "14033", "93.1"],
        ["Nông sản chính", None, "553", "7170", "92.1"],
        ["Cà phê", "1042", "145", "1042", "85.3"], # Unit issues in table but we'll try
        ["Cao su", "607", "92", "607", "64.6"],
        ["Gạo", "5698", "139", "5698", "92.9"],
        ["Chè", "121", "14", "121", "116.2"],
        ["Hạt điều", "160", "71", "160", "89.4"],
        ["Hạt tiêu", "124", "19", "124", "107.2"],
        ["Thuỷ sản", None, "450", "3938", "93.7"],
        ["Gỗ & sản phẩm gỗ", None, "250", "2271", "89.8"],
    ]
    # NK Rows
    nk_rows = [
        ["Tổng kim ngạch NK", None, "444", "5921", "87.1"],
        ["Phân bón các loại", "3852", "62", "3852", "83.9"],
        ["Thuốc trừ sâu & nguyên liệu", None, "35", "407", "92.0"],
        ["Lúa mỳ", "1254", "20", "1254", "114.2"],
        ["Thức ăn gia súc và nl", "1596", "90", "1596", "98.6"],
    ]
    for rows, sector in [(xk_rows, "Export"), (nk_rows, "Import")]:
        attr_val = f"{sector}_Value"
        for r in rows:
            item = r[0]
            v11, v11c, cp = normalize_number(r[2]), normalize_number(r[3]), normalize_number(r[4])
            g = "Cả nước"; gl = "National"
            if v11:
                records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Monthly"}, g, gl, {"sector": "Trade", "commodity": item}, {"attribute": attr_val, "value": v11, "unit": "million_USD", "data_type": "Actual"}))
            if v11c:
                comp = {"comparison_type": "YoY", "comparison_value": cp, "comparison_unit": "percentage", "reference_period": "2008"}
                records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Cumulative"}, g, gl, {"sector": "Trade", "commodity": item}, {"attribute": attr_val, "value": v11c, "unit": "million_USD", "data_type": "Actual"}, comp))
    return {"metadata": metadata, "records": records}


def parse_pl9_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL9", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL7.md"}
    records = []
    # Rows: 0:Item, 1:Plan, 2:TH_10T, 3: ƯTH_T11, 4: ƯTH_11T, 5: %_Plan
    rows = [
        ["Vốn thực hiện đầu tư", "2611500", "2789627", "172550", "2962177", "113.43"],
        ["Đầu tư Thuỷ lợi", "1483500", "1948632", "125000", "2073632", "139.78"],
        ["Đầu tư Nông nghiệp", "493000", "394010", "20500", "414510", "84.08"],
        ["Đầu tư Lâm nghiệp", "230000", "187485", "6800", "194285", "84.47"],
        ["Đầu tư Thuỷ sản", "24000", "20000", "1500", "21500", "89.58"],
        ["Khoa học - Công nghệ", "230000", "130500", "7500", "138000", "60.00"],
        ["Giáo dục - Đào tạo", "90000", "61000", "6250", "67250", "74.72"],
        ["Các ngành khác", "61000", "48000", "5000", "53000", "86.89"],
    ]
    for r in rows:
        item, plan, v10, v11, v11c, cp = r
        loc, gl = "Bộ NN & PTNT", "National"
        i = {"sector": "Investment", "commodity": item}
        # Monthly Nov
        val11 = normalize_number(v11)
        if val11: records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Monthly"}, loc, gl, i, {"attribute": "Investment_Amount", "value": val11, "unit": "million_VND", "data_type": "Actual"}))
        # Cumulative 11T
        val11c = normalize_number(v11c)
        if val11c:
            comp = {"comparison_type": "vs_Plan", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "Annual_Plan"}
            records.append(create_record(metadata, {"year": 2009, "month": 11, "period_type": "Cumulative"}, loc, gl, i, {"attribute": "Investment_Amount", "value": val11c, "unit": "million_VND", "data_type": "Actual"}, comp))
        # Plan
        val_p = normalize_number(plan)
        if val_p: records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, loc, gl, i, {"attribute": "Investment_Amount", "value": val_p, "unit": "million_VND", "data_type": "Plan"}))
        
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/11"
    save_json(parse_pl8a_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL8a.json"))
    save_json(parse_pl9_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL9.json"))
    print("Successfully parsed PL8a, 9 for Nov 2009.")
