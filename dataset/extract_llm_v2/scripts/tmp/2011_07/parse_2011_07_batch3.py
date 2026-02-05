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
            if len(parts[-1]) == 3 and len(parts[0]) <= 3: s = s.replace(",", "")
            elif len(parts[-1]) != 3: s = s.replace(",", ".")
            else: s = s.replace(",", "")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    try: return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {"Cả nước": "Cả nước", "Toàn quốc": "Cả nước"}
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    if norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    else:
        geo_context["region_id"] = "COUNTRY"; geo_context["region_name_vn"] = norm_loc; geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl11():
    # Investment
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL11", "source_file": "2011_07_Phuluc_07_2011_PL11.md"}
    records = []
    t_month = {"year": 2011, "month": 7, "period_type": "Monthly", "report_date": "2011-07-31"}
    t_7m = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    
    # [Item, Unit, T7, 7T]
    # Row indices in file: 20 (A), 21 (I)
    data = [
        ("Vốn ngân sách giao đầu năm", 201800, 2228200),
        ("Vốn thực hiện đầu tư", 184500, 2139400),
        ("Đầu tư Thuỷ lợi", 120000, 1270100),
        ("Đầu tư Nông nghiệp", 18500, 611300),
        ("Đầu tư Lâm nghiệp", 19450, 116450),
        ("Đầu tư Thuỷ sản", 1750, 11750),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 2500, 16500),
        ("Khoa học - Công nghệ", 4550, 30050),
        ("Giáo dục - Đào tạo", 7500, 37500),
        ("Các ngành khác", 10250, 62250),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 12500, 69000),
        ("Vốn chuẩn bị đầu tư", 4800, 19800),
        ("Vốn trái phiếu Chính phủ", 195000, 2225000),
        ("Các dự án có trong QĐ171", 125000, 1700000),
        ("Các dự án cấp bách bổ sung", 30000, 260000),
        ("Các dự án thuỷ lợi ĐBSHồng", 40000, 265000),
        ("Tổng vốn đầu tư : = A + B", 396800, 4453200)
    ]
    
    for row in data:
        records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[2]), "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_pl12():
    # Trade Summary
    metadata = {"year": 2011, "month": 7, "appendix_number": "PL12", "source_file": "2011_07_Phuluc_07_2011_PL12.md"}
    records = []
    t_month = {"year": 2011, "month": 7, "period_type": "Monthly", "report_date": "2011-07-31"}
    t_7m = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    
    xk_items = [
        ("Tổng kim ngạch XK", None, 2000, None, 13945),
        ("Nông sản chính", None, 1060, None, 8056),
        ("Cà phê", 65, 145, 930, 2044),
        ("Cao su", 60, 260, 349, 1522),
        ("Gạo", 700, 340, 4734, 2319),
        ("Chè", 12, 20, 65, 98),
        ("Hạt điều", 15, 130, 84, 656),
        ("Hạt tiêu", 15, 90, 85, 465),
        ("Hàng rau quả", None, 50, None, 356),
        ("Sắn và sản phẩm từ sắn", 55, 25, 1656, 596),
        ("Thuỷ sản", None, 500, None, 3106),
        ("Lâm sản chính", None, 320, None, 2215),
        ("Gỗ & sản phẩm gỗ", None, 300, None, 2085),
        ("SP mây, tre, cói, thảm", None, 18, None, 116)
    ]
    
    nk_items = [
        ("Tổng kim ngạch NK", None, 1400, None, 9000),
        ("Các mặt hàng nhập khẩu chính", None, 952, None, 6080),
        ("Phân bón các loại", 300, 130, 2141, 846),
        ("U RE", 40, 14, 408, 146),
        ("S A", 40, 8, 431, 83),
        ("D A P", 70, 42, 322, 194),
        ("N P K", 15, 7, 137, 60),
        ("Các loại phân bón khác", 135, 59, 843, 363),
        ("Thuốc trừ sâu & nguyên liệu", None, 60, None, 386),
        ("Lúa mỳ", 200, 65, 1522, 518),
        ("Thức ăn gia súc và nguyên liệu", None, 200, None, 1373),
        ("Dầu mỡ động, thực vật", None, 80, None, 515),
        ("Cao su", 30, 75, 202, 502),
        ("Bông các loại", 20, 80, 201, 709),
        ("Sữa &sản phẩm sữa", None, 80, None, 490),
        ("Gỗ & sản phẩm gỗ", None, 120, None, 727),
        ("Muối", None, 2, None, 13.1),
        ("Hàng thủy sản", None, 30, None, 242),
        ("Hàng rau quả", None, 30, None, 154)
    ]
    
    def process_list(items, trade_type):
        for name, q_m, v_m, q_7, v_7 in items:
            if v_m: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": float(v_m), "unit": "million_USD", "data_type": "Estimate", "trade_type": trade_type}))
            if q_m: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": float(q_m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": trade_type}))
            if v_7: records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": float(v_7), "unit": "million_USD", "data_type": "Estimate", "trade_type": trade_type}))
            if q_7: records.append(create_record(metadata, t_7m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": float(q_7), "unit": "1000_ton", "data_type": "Estimate", "trade_type": trade_type}))

    process_list(xk_items, "Export")
    process_list(nk_items, "Import")
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl11()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL11.json"))
    save_json({"metadata": {"year": 2011, "month": 7}, "records": parse_pl12()}, os.path.join(out_dir, "2011_07_Phuluc_07_2011_PL12.json"))
    print("Successfully parsed Batch 3 (PL11, PL12) for July 2011.")
