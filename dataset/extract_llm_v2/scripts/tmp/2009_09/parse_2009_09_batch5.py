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

def parse_pl8b_09():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL8b", "source_file": "2009_09_PHULUC_T09_2009_PL8b.md"}
    records = []
    # Title says 8 months
    m_data = {
        "Bông các loại": [["HOA KỲ", 109288, 137087, 157.81, 128.34], ["ẤN ĐỘ", 9487, 12282, 19.16, 16.08], ["BRAXIN", 8433, 11172, 251.96, 220.67], ["IN ĐÔ NÊ XI A", 2506, 2482, 75.39, 55.71], ["TRUNG QUỐC", 1262, 1981, 176.26, 164.65], ["THỤY SỸ", 1219, 1519, 13.98, 11.99], ["ĐÀI LOAN", 682, 814, 14.79, 12.63], ["ITALIA", 1113, 758, 65.43, 47.69], ["HÀN QUỐC", 399, 677, 26.81, 32.62], ["ANH", 97, 122, 2.09, 1.64]],
        "Cao su": [["THÁI LAN", 41264, 51626, 146.36, 70.32], ["CAMPUCHIA", 27306, 40527, 142.19, 76.39], ["HÀN QUỐC", 29022, 38521, 137.49, 67.60], ["NHẬT BẢN", 9073, 19119, 99.43, 62.93], ["ĐÀI LOAN", 12971, 18953, 58.33, 37.65], ["IN ĐÔ NÊ XI A", 13374, 17700, 298.73, 140.66], ["NGA", 5102, 10409, 68.33, 38.18], ["TRUNG QUỐC", 5221, 8416, 108.66, 77.76], ["MALAIXIA", 5724, 5511, 133.83, 57.99], ["HOA KỲ", 5788, 5109, 139.13, 47.31]],
        "Dầu mỡ động thực vật": [[k, None, v] for k, v in [["MALAIXIA", 138878], ["IN ĐÔ NÊ XI A", 98728], ["THÁI LAN", 25432], ["ACHENTINA", 19517], ["HOA KỲ", 14944], ["CHI LÊ", 4358], ["XINH GA PO", 1682], ["HÀN QUỐC", 1613], ["Ô X TRÂY LIA", 1364], ["TRUNG QUỐC", 603]]],
        "Lúa mì": [["Ô X TRÂY LIA", 730214, 188919, 230.42, 133.01], ["UCRAINA", 84329, 14154, 1468.38, 504.77], ["HOA KỲ", 12810, 3608, 29.43, 19.73], ["NGA", 14098, 3288, None, None], ["CA NA ĐA", 2000, 722, 2.42, 2.48], ["TRUNG QUỐC", 198, 97, 0.96, 1.52]],
        "Phân bón các loại": [["TRUNG QUỐC", 1127476, 360185, 85.94, 57.01], ["NGA", 290746, 84235, 100.21, 62.54], ["PHI LIP PIN", 193085, 77416, 260.40, 180.76], ["UCRAINA", 202277, 58562, None, None], ["HOA KỲ", 129149, 52102, 16948.69, 2943.16], ["HÀN QUỐC", 198212, 42379, 172.94, 58.93], ["CA NA ĐA", 48229, 32810, 42.49, 55.60], ["ĐÀI LOAN", 83754, 13800, 97.08, 57.90], ["NHẬT BẢN", 95502, 13144, 73.71, 36.04], ["ẤN ĐỘ", 29394, 12502, 343.83, 207.31]],
        "Sữa và sản phẩm sữa": [[k, None, v] for k, v in [["NIU ZI LÂN", 79152], ["HÀ LAN", 49891], ["ĐAN MẠCH", 35380], ["HOA KỲ", 28411], ["THÁI LAN", 22030], ["MALAIXIA", 17514], ["Ô X TRÂY LIA", 11708], ["BA LAN", 10130], ["TÂY BAN NHA", 6783], ["PHÁP", 6766]]],
        "Thức ăn gia súc và nguyên liệu": [[k, None, v] for k, v in [["ACHENTINA", 393739], ["ẤN ĐỘ", 307428], ["HOA KỲ", 110474], ["TRUNG QUỐC", 108938], ["IN ĐÔ NÊ XI A", 28392], ["THÁI LAN", 27115], ["ITALIA", 20740], ["ĐÀI LOAN", 18580], ["HÀN QUỐC", 12926]]],
        "Thuốc trừ sâu và nguyên liệu": [[k, None, v] for k, v in [["TRUNG QUỐC", 123796], ["ẤN ĐỘ", 31099], ["THỤY SỸ", 23044], ["ĐỨC", 21736], ["HÀN QUỐC", 16479], ["NHẬT BẢN", 14373], ["THÁI LAN", 13908], ["XINH GA PO", 9927], ["IN ĐÔ NÊ XI A", 9044], ["HOA KỲ", 6992]]],
    }
    for comm, pairs in m_data.items():
        for p in pairs:
            loc = p[0]; vol = p[1]; val = p[2]
            c_vol = p[3] if len(p) > 3 else None
            c_val = p[4] if len(p) > 4 else None
            gl = "Provincial"
            i = {"sector": "Trade", "commodity": comm}
            t = {"year": 2009, "month": 8, "period_type": "Cumulative"}
            if vol:
                comp = {"comparison_type": "YoY", "comparison_value": c_vol, "comparison_unit": "percentage", "reference_period": "2008"} if c_vol else None
                records.append(create_record(metadata, t, loc, gl, i, {"attribute": "Import_Volume", "value": vol, "unit": "ton", "data_type": "Actual"}, comp))
            if val:
                comp = {"comparison_type": "YoY", "comparison_value": c_val, "comparison_unit": "percentage", "reference_period": "2008"} if c_val else None
                records.append(create_record(metadata, t, loc, gl, i, {"attribute": "Import_Value", "value": val, "unit": "1000_USD", "data_type": "Actual"}, comp))
    return {"metadata": metadata, "records": records}


def parse_pl9_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL9", "source_file": "2009_09_PHULUC_T09_2009_PL9.md"}
    records = []
    # Rows: 0:Item, 1:Plan, 2:TH_8T, 3: ƯTH_T9, 4: ƯTH_9T, 5: %_Plan
    rows = [
        ["Vốn thực hiện đầu tư", "2611500", "2007595", "164200", "2171795", "83.16"],
        ["Đầu tư Thuỷ lợi", "1483500", "1473126", "125000", "1598126", "107.73"],
        ["Đầu tư Nông nghiệp", "493000", "269326", "18500", "287826", "58.38"],
        ["Đầu tư Lâm nghiệp", "230000", "85278", "6200", "91478", "39.77"],
        ["Đầu tư Thuỷ sản", "24000", "19000", "1800", "20800", "86.67"],
        ["Khoa học - Công nghệ", "230000", "80783", "4500", "85283", "37.08"],
        ["Giáo dục - Đào tạo", "90000", "49042", "5200", "54242", "60.27"],
        ["Các ngành khác", "61000", "31040", "3000", "34040", "55.80"],
        ["Chương trình mục tiêu", "40263", "13500", "1750", "15250", "37.88"],
        ["Vốn đầu tư nhiệm vụ cụ thể", "208000", "97109", "6500", "103609", "49.81"],
        ["Bổ sung dự trữ Quốc gia", "65000", "65000", None, "65000", "100.00"],
        ["Vốn chuẩn bị đầu tư", "30000", "20000", "2550", "22550", "75.17"],
        ["Vốn ứng trước dự án cấp bách", "1000000", "388547", "48580", "437127", "43.71"],
        ["Vốn TPCP 171/2006", "3250000", "1866236", "145000", "2011236", "61.88"],
        ["Dự án cấp bách bổ sung", "200000", "73915", "13400", "87315", "43.66"],
        ["Dự án thuỷ lợi ĐBS Hồng", "400000", "56104", "13800", "69904", "17.48"],
    ]
    for r in rows:
        item, plan, v8, v9, v9c, cp = r
        loc, gl = "Bộ NN & PTNT", "National"
        i = {"sector": "Investment", "commodity": item}
        
        # Monthly Sep
        val9 = normalize_number(v9)
        if val9:
            records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Monthly"}, loc, gl, i, {"attribute": "Investment_Amount", "value": val9, "unit": "million_VND", "data_type": "Actual"}))
            
        # Cumulative
        val9c = normalize_number(v9c)
        if val9c:
            comp = {"comparison_type": "vs_Plan", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "Annual_Plan"}
            records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Cumulative"}, loc, gl, i, {"attribute": "Investment_Amount", "value": val9c, "unit": "million_VND", "data_type": "Actual"}, comp))
            
        # Plan
        val_p = normalize_number(plan)
        if val_p:
            records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, loc, gl, i, {"attribute": "Investment_Amount", "value": val_p, "unit": "million_VND", "data_type": "Plan"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/09"
    save_json(parse_pl8b_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL8b.json"))
    save_json(parse_pl9_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL9.json"))
    print("Successfully parsed PL8b, 9 for Sep 2009 with region map integration.")
