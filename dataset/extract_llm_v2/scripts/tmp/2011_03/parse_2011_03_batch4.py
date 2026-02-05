import json
import uuid
import os

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
        if s.find(".") < s.find(","): # 1.234,5
            s = s.replace(".", "").replace(",", ".")
        else: # 1,234.5
            s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "") # Thousands
            else: s = s.replace(",", ".") # Decimal
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
        else:
            parts = s.split(".")
            if len(parts[1]) == 3: s = s.replace(".", "")
            else: pass
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Cả nước": "Cả nước",
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.strip()
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

def parse_pl10():
    # Investment
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL10", "source_file": "2011_03_Phuluc_03_2011_PL10.md"}
    records = []
    
    t_3m_11 = {"year": 2011, "month": 3, "period_type": "Cumulative", "report_date": "2011-03-31"}
    t_mar_11 = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-31"}
    # Cols: KH Nam 2011, TH 2T 2011, Est T3 2011, Est 3T 2011, %
    
    data = [
        ("Vốn ngân sách giao đầu năm", 3672300, 770211, 200750, 963461),
        ("Vốn thực hiện đầu tư", 3275300, 756711, 190000, 939211),
        ("Đầu tư Thuỷ lợi", 1887571, 470000, 135000, 605000),
        ("Đầu tư Nông nghiệp", 701000, 241186, 25250, 266436),
        ("Đầu tư Lâm nghiệp", 286000, 15175, 11500, 26675),
        ("Đầu tư Thuỷ sản", 20429, 3000, 1500, 4500),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 30000, 4500, 3000, 7500),
        ("Khoa học - Công nghệ", 60000, 8500, 4500, 13000),
        ("Giáo dục - Đào tạo", 90000, 6500, 3750, 10250),
        ("Các ngành khác", 200300, 7850, 5500, 13350),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 288000, 11000, 8750, 19750),
        ("Vốn chuẩn bị đầu tư", 38000, 2500, 2000, 4500),
        ("Vốn trái phiếu Chính phủ", 3500000, 312000, 220000, 532000),
        ("Các dự án có trong QĐ171", 2671100, 230000, 145000, 375000),
        ("Các dự án cấp bách bổ sung", 398000, 40000, 35000, 75000),
        ("Các dự án thuỷ lợi ĐBSHồng", 430900, 42000, 40000, 82000),
        ("Tổng vốn đầu tư : = A + B", 7172300, 1082211, 420750, 1495461)
    ]
    
    for row in data:
        item = row[0]
        records.append(create_record(metadata, t_mar_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[3]), "unit": "million_VND", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[4]), "unit": "million_VND", "data_type": "Estimate"}))
        
    return records

def parse_pl11():
    # Trade Summary
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL11", "source_file": "2011_03_Phuluc_03_2011_PL11.md"}
    records = []
    
    t_3m_11 = {"year": 2011, "month": 3, "period_type": "Cumulative", "report_date": "2011-03-31"}
    t_mar_11 = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-31"}
    
    # [Item, Vol T3, Val T3, Vol 3T, Val 3T]
    items_export = [
        ("Tổng kim ngạch XK", None, 1800, None, 5352),
        ("Nông sản chính", None, 1090, None, 3402),
        ("Cà phê", 145, 290, 504, 1007),
        ("Cao su", 56, 250, 179, 798),
        ("Gạo", 600, 300, 1636, 823),
        ("Chè", 9, 12, 26, 36),
        ("Hạt điều", 8, 56, 28, 194),
        ("Hạt tiêu", 8, 38, 18, 85),
        ("Hàng rau quả", None, 44, None, 139),
        ("Sắn và sản phẩm từ sắn", 300, 100, 962, 321),
        ("Thuỷ sản", None, 400, None, 1092),
        ("Lâm sản chính", None, 280, None, 809),
        ("Quế", None, 2, None, 5),
        ("Gỗ & sản phẩm gỗ", None, 260, None, 756),
        ("SP mây, tre, cói, thảm", None, 18, None, 48)
    ]
    
    items_import = [
        ("Tổng kim ngạch NK", None, 1100, None, 3251),
        ("Các mặt hàng nhập khẩu chính", None, 758, None, 2248),
        ("Phân bón các loại", 204, 73, 614, 220),
        ("U RE", 32, 12, 88, 33),
        ("S A", 55, 10, 161, 29),
        ("D A P", 30, 17, 90, 50),
        ("N P K", 11, 5, 22, 10),
        ("Các loại phân bón khác", 76, 29, 253, 98),
        ("Thuốc trừ sâu & nguyên liệu", None, 44, None, 131),
        ("Lúa mỳ", 161, 54, 461, 154),
        ("Thức ăn gia súc và nguyên liệu", None, 194, None, 582),
        ("Dầu mỡ động, thực vật", None, 59, None, 179),
        ("Cao su", 25, 66, 73, 193),
        ("Bông các loại", 33, 96, 98, 284),
        ("Sữa &sản phẩm sữa", None, 51, None, 148),
        ("Gỗ & sản phẩm gỗ", None, 74, None, 210),
        ("Muối", None, 1, None, 3),
        ("Hàng thủy sản", None, 27, None, 84),
        ("Hàng rau quả", None, 19, None, 59)
    ]
    
    for row in items_export:
        item, v_mar, val_mar, v_3m, val_3m = row
        # Mar 11
        if val_mar is not None: records.append(create_record(metadata, t_mar_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_mar), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_mar is not None: records.append(create_record(metadata, t_mar_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_mar), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))
        # 3M 11
        if val_3m is not None: records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_3m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_3m is not None: records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_3m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))

    for row in items_import:
        item, v_mar, val_mar, v_3m, val_3m = row
        # Mar 11
        if val_mar is not None: records.append(create_record(metadata, t_mar_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_mar), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_mar is not None: records.append(create_record(metadata, t_mar_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_mar), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))
        # 3M 11
        if val_3m is not None: records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_3m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_3m is not None: records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_3m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl10()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL10.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl11()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL11.json"))
    print("Successfully parsed PL10, PL11 for March 2011 (Investment & Trade Summary).")
