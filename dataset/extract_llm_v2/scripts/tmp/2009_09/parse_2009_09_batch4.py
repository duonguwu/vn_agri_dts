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

def parse_pl8_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL8", "source_file": "2009_09_PHULUC_T09_2009_PL8.md"}
    records = []
    
    # XK Rows: 0:Item, 1:v9_vol, 2:v9_val, 3:v9c_vol, 4:v9c_val, 5:cp_vol, 6:cp_val
    xk_rows = [
        ["Tổng kim ngạch XK", None, "1330", None, "11079", None, "87.91"],
        ["Nông sản chính", None, "610", None, "6151", None, "90.04"],
        ["Cà phê", "54", "76", "893", "1319", "116.84", "81.91"],
        ["Cao su", "79", "129", "489", "732", "108.94", "59.99"],
        ["Gạo", "430", "174", "5062", "2288", "135.47", "93.56"],
        ["Chè", "15", "20", "97", "126", "122.35", "113.74"],
        ["Hạt điều", "20", "97", "134", "621", "109.86", "90.38"],
        ["Hạt tiêu", "14", "38", "111", "269", "153.80", "106.30"],
        ["Hàng rau quả", None, "40", None, "322", None, "113.51"],
        ["Sắn và sản phẩm từ sắn", "158", "36", None, "473", "215.50", None],
        ["Thuỷ sản", None, "430", None, "3047", None, "90.82"],
        ["Lâm sản chính", None, "215", None, "1882", None, "84.68"],
        ["Quế", "13", "13", "13", "15", "118.07", None],
        ["Gỗ & sản phẩm gỗ", None, "200", None, "1753", None, "85.74"],
        ["SP mây, tre, cói, thảm", None, "13", None, "127", None, "77.05"],
    ]
    # NK Rows
    nk_rows = [
        ["Tổng kim ngạch NK", None, "940", None, "7511", None, "91.84"],
        ["Các mặt hàng nhập khẩu chính", None, "620", None, "5005", None, "84.40"],
        ["Phân bón các loại", "400", "114", "3253", "1033", "123.15", "80.34"],
        ["Thuốc trừ sâu & nguyên liệu", None, "34", None, "338", None, "86.94"],
        ["Lúa mỳ", "100", "24", "969", "241", "173.85", "100.38"],
        ["Thức ăn gia súc và nl", None, "181", None, "1453", None, "100.59"],
        ["Dầu mỡ động, thực vật", None, "40", None, "366", None, "67.94"],
        ["Cao su", "32", "38", "210", "274", "137.86", "65.94"],
        ["Bông các loại", "35", "47", "221", "277", "100.37", "81.34"],
        ["Sữa &sản phẩm sữa", None, "50", None, "367", None, "93.06"],
        ["Gỗ & sản phẩm gỗ", None, "90", None, "636", None, "73.31"],
        ["Muối", "2", None, "21", None, "134.94", None],
    ]

    for rows, sector in [(xk_rows, "Export"), (nk_rows, "Import")]:
        attr_vol = "Export_Volume" if sector == "Export" else "Import_Volume"
        attr_val = "Export_Value" if sector == "Export" else "Import_Value"
        for r in rows:
            item = r[0]
            v9_vol, v9_val, v9c_vol, v9c_val, cp_vol, cp_val = r[1], r[2], r[3], r[4], r[5], r[6]
            loc, gl = "Cả nước", "National"
            i = {"sector": "Trade", "commodity": item}
            
            # Monthly
            if normalize_number(v9_vol):
                records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Monthly"}, loc, gl, i, {"attribute": attr_vol, "value": normalize_number(v9_vol), "unit": "1000_ton", "data_type": "Actual"}))
            if normalize_number(v9_val):
                records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Monthly"}, loc, gl, i, {"attribute": attr_val, "value": normalize_number(v9_val), "unit": "million_USD", "data_type": "Actual"}))
            
            # Cumulative
            if normalize_number(v9c_vol):
                comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp_vol), "comparison_unit": "percentage", "reference_period": "2008"} if cp_vol else None
                records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Cumulative"}, loc, gl, i, {"attribute": attr_vol, "value": normalize_number(v9c_vol), "unit": "1000_ton", "data_type": "Actual"}, comp))
            if normalize_number(v9c_val):
                comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp_val), "comparison_unit": "percentage", "reference_period": "2008"} if cp_val else None
                records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Cumulative"}, loc, gl, i, {"attribute": attr_val, "value": normalize_number(v9c_val), "unit": "million_USD", "data_type": "Actual"}, comp))
    return {"metadata": metadata, "records": records}


def parse_pl8a_09():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL8a", "source_file": "2009_09_PHULUC_T09_2009_PL8a.md"}
    records = []
    # Title says 8 months
    m_data = {
        "Cà phê": [["BỈ", 118739, 171824, 289.94, 196.75], ["ĐỨC", 92355, 137444, 101.32, 70.75], ["HOA KỲ", 86261, 130097, 122.15, 87.70], ["ITALIA", 78680, 117450, 136.86, 96.95], ["TÂY BAN NHA", 55068, 81298, 103.16, 71.64], ["NHẬT BẢN", 46561, 73779, 107.31, 75.78], ["HÀ LAN", 30254, 43408, 294.19, 199.60], ["HÀN QUỐC", 21630, 32413, 76.09, 54.63], ["PHÁP", 21564, 31862, 126.60, 90.41], ["ANH", 20284, 29918, 80.33, 56.36]],
        "Cao su": [["TRUNG QUỐC", 284986, 420391, 116.02, 61.53], ["MALAIXIA", 16897, 23803, 178.54, 95.30], ["HÀN QUỐC", 18132, 23598, 94.77, 52.75], ["ĐÀI LOAN", 13508, 21242, 101.76, 57.30], ["ĐỨC", 11081, 17595, 70.45, 42.00], ["HOA KỲ", 8736, 11605, 120.33, 70.05], ["NGA", 6794, 11257, 66.63, 36.90], ["NHẬT BẢN", 5271, 8457, 62.30, 36.30], ["THỔ NHĨ KỲ", 5591, 8320, 89.09, 56.59], ["ẤN ĐỘ", 4623, 6686, 255.27, 139.93]],
        "Chè": [["PAKIXTAN", 20016, 28750, 136.48, 122.61], ["NGA", 13554, 16285, 160.92, 150.11], ["ĐÀI LOAN", 13043, 15379, 103.17, 103.97], ["TRUNG QUỐC", 4784, 5056, 106.45, 106.89], ["ẤN ĐỘ", 4487, 4896, 224.01, 244.09], ["IN ĐÔ NÊ XI A", 3673, 3479, 172.77, 187.63], ["HOA KỲ", 3010, 2818, 117.81, 150.74], ["ĐỨC", 1496, 1909, 101.42, 76.35], ["BA LAN", 1031, 1163, 68.01, 61.71], ["TIỂU VƯƠNG QUỐC", 526, 896, 15.57, 17.31]],
        "Gạo": [["PHI LIP PIN", 1573126, 852337, 98.92, 78.28], ["MALAIXIA", 438135, 192340, 150.98, 103.37], ["CUBA", 378750, 161183, 86.85, 41.48], ["XINH GA PO", 229937, 94369, 827.41, 612.62], ["IRẮC", 168000, 67540, 125.37, 97.40], ["ĐÀI LOAN", 119661, 48470, 703.06, 565.36], ["NGA", 66252, 28790, 154.30, 116.47], ["NAM PHI", 33523, 14560, 895.62, 848.53], ["UCRAINA", 29041, 12448, 295.58, 205.16], ["HỒNG CÔNG", 28076, 12180, 1296.21, 892.31]],
        "Hàng hải sản": [["NHẬT BẢN", 69271, 455631, 75.35, 84.32], ["MỸ", 76928, 442842, 117.21, 101.34], ["HÀN QUỐC", 62402, 186862, 96.47, 87.90], ["ĐỨC", 39184, 132868, 108.17, 104.74], ["TÂY BAN NHA", 43376, 106635, 103.48, 94.95], ["Ô X TRÂY LIA", 15349, 75939, 97.93, 91.14], ["HÀ LAN", 22339, 74638, 79.40, 79.85], ["ITALIA", 25994, 73494, 76.96, 65.30], ["BỈ", 16417, 65752, 96.64, 95.68], ["CANAĐA", 12589, 64794, 112.01, 95.53]],
    }
    for comm, pairs in m_data.items():
        for p in pairs:
            loc, vol, val, c_vol, c_val = p
            gl = "Provincial"
            i = {"sector": "Trade", "commodity": comm}
            # Cumulative 8 months
            t = {"year": 2009, "month": 8, "period_type": "Cumulative"}
            if vol:
                records.append(create_record(metadata, t, loc, gl, i, {"attribute": "Export_Volume", "value": vol, "unit": "ton", "data_type": "Actual"}, {"comparison_type": "YoY", "comparison_value": c_vol, "comparison_unit": "percentage", "reference_period": "2008"}))
            if val:
                records.append(create_record(metadata, t, loc, gl, i, {"attribute": "Export_Value", "value": val, "unit": "1000_USD", "data_type": "Actual"}, {"comparison_type": "YoY", "comparison_value": c_val, "comparison_unit": "percentage", "reference_period": "2008"}))
                
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/09"
    save_json(parse_pl8_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL8.json"))
    save_json(parse_pl8a_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL8a.json"))
    print("Successfully parsed PL8, 8a for Sep 2009 with region map integration.")
