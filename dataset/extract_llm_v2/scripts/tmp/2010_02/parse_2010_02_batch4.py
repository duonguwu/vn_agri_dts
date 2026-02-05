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
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl7_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL7", "source_file": "2010_02_PhuLuc_T02_2010_PL7.md"}
    records = []
    
    # Rows: Name, KH_2010, Jan_10, Feb_10_Est, 2M_10_Est
    data = [
        ["Tổng số : = A + B", 7186262, 241040, 175150, 416190],
        ["Vốn ngân sách giao đầu năm", 3186262, 151040, 115150, 266190],
        ["Vốn thực hiện đầu tư", 2771000, 144390, 110150, 254540],
        ["Đầu tư Thuỷ lợi", 1735000, 119850, 85000, 204850],
        ["Đầu tư Nông nghiệp", 415300, 9500, 8500, 18000],
        ["Đầu tư Lâm nghiệp", 260000, 6300, 6500, 12800],
        ["Đầu tư Thuỷ sản", 25000, 500, 400, 900],
        ["Khoa học - Công nghệ", 137800, 3740, 4500, 8240],
        ["Giáo dục - Đào tạo", 86900, 3500, 3750, 7250],
        ["Các ngành khác", 111000, 1000, 1500, 2500],
        ["Chương trình mục tiêu", 47262, 1650, 1000, 2650],
        ["Vốn đầu tư theo các mục tiêu nhiệm vụ", 268000, 4000, 3500, 7500],
        ["Vốn chuẩn bị đầu tư", 35000, 1000, 500, 1500],
        ["Vốn trái phiếu Chính phủ", 4000000, 90000, 60000, 150000],
        ["Các dự án có trong QĐ171", 3000000, 65000, 40000, 105000],
        ["Các dự án cấp bách bổ sung", 4000000, 11000, 9000, 20000],
        ["Các dự án thuỷ lợi ĐBSHồng", 600000, 14000, 11000, 25000],
    ]
    
    loc, gl = "Cả nước", "National"
    for r in data:
        name, kh, v_jan, v_feb, v_2m = r
        t_plan = {"year": 2010, "month": 12, "period_type": "Annual"}
        t_jan = {"year": 2010, "month": 1, "period_type": "Monthly"}
        t_feb = {"year": 2010, "month": 2, "period_type": "Monthly"}
        t_2m = {"year": 2010, "month": 2, "period_type": "Cumulative"}
        
        sector = "Investment"
        records.append(create_record(metadata, t_plan, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": kh, "unit": "million_VND", "data_type": "Plan"}))
        records.append(create_record(metadata, t_jan, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": v_jan, "unit": "million_VND", "data_type": "Actual"}))
        records.append(create_record(metadata, t_feb, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": v_feb, "unit": "million_VND", "data_type": "Estimated"}))
        records.append(create_record(metadata, t_2m, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": v_2m, "unit": "million_VND", "data_type": "Estimated"}))
        
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl7_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL7.json"))
    print("Successfully parsed PL7 (Investment) for Feb 2010. PL8a/b were skipped (Compliance metadata).")
