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
    norm_loc = alias_map.get(loc_name.strip(), loc_name.strip())
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl8():
    # Investment
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL8", "source_file": "2011_01_Phuluc_01_2011_PL8.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-31"}
    
    # [Item, Estimate Jan 2011]
    # Note: PL 8 has Plan 2011, Est Jan, Est 1 Month (Same as Jan), %
    data = [
        ("Vốn ngân sách giao đầu năm", 156500),
        ("Vốn thực hiện đầu tư", 150500),
        ("Đầu tư Thuỷ lợi", 120000),
        ("Đầu tư Nông nghiệp", 9500),
        ("Đầu tư Lâm nghiệp", 7500),
        ("Đầu tư Thuỷ sản", 500),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 2000),
        ("Khoa học - Công nghệ", 4500),
        ("Giáo dục - Đào tạo", 3500),
        ("Các ngành khác", 3000),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 5000),
        ("Vốn chuẩn bị đầu tư", 1000)
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_pl9():
    # Trade Export/Import
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL9", "source_file": "2011_01_Phuluc_01_2011_PL9.md"}
    records = []
    t_jan_11 = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-31"}
    t_jan_10 = {"year": 2010, "month": 1, "period_type": "Monthly", "report_date": "2010-01-31"}
    
    # Export Data (Jan 2010 Vol, Jan 2010 Val, Jan 2011 Vol, Jan 2011 Val)
    # Unit: 1000 ton, Million USD
    
    items_export = [
        ("Tổng kim ngạch XK", None, 1412, None, 1600),
        ("Nông sản chính", None, 763, None, 910),
        ("Cà phê", 143, 201, 100, 175),
        ("Cao su", 54, 137, 70, 250),
        ("Gạo", 381, 205, 390, 210),
        ("Chè", 11, 15, 11, 16),
        ("Hạt điều", 13, 71, 15, 98),
        ("Hạt tiêu", 8, 23, 7, 33),
        ("Hàng rau quả", None, 42, None, 33),
        ("Sắn và sản phẩm từ sắn", 253, 68, 185, 95),
        ("Thuỷ sản", None, 313, None, 320),
        ("Lâm sản chính", None, 316, None, 320),
        ("Quế", None, 1.8, None, 2), # Vol empty in view
        ("Gỗ & sản phẩm gỗ", None, 294.4, None, 298),
        ("SP mây, tre, cói, thảm", None, 19.9, None, 20),
        ("Các mặt hàng nông lâm sản khác", None, 20, None, 50)
    ]
    
    items_import = [
        ("Tổng kim ngạch NK", None, 1025, None, 1100),
        ("Các mặt hàng nhập khẩu chính", None, 758, None, 820),
        ("Phân bón các loại", 505, 146, 520, 204),
        ("U RE", 207, 66, 196, 70),
        ("S A", 153, 20, 144, 23),
        ("D A P", 58, 24, 90, 45),
        ("N P K", 28, 10, 28, 11),
        ("Các loại phân bón khác", 59, 26, 62, 55),
        ("Thuốc trừ sâu & nguyên liệu", None, 56, None, 60),
        ("Lúa mỳ", 149, 35, 179, 57),
        ("Thức ăn gia súc và nguyên liệu", None, 161, None, 160),
        ("Dầu mỡ động, thực vật", None, 56, None, 60),
        ("Cao su", 27, 45, 27, 62),
        ("Bông các loại", 33, 51, 28, 61),
        ("Sữa &sản phẩm sữa", None, 63, None, 60),
        ("Gỗ & sản phẩm gỗ", None, 89, None, 95),
        ("Muối", None, 4, None, 1),
        ("Hàng thủy sản", None, 30, None, 30),
        ("Hàng rau quả", None, 22, None, 25)
    ]
    
    # Process Export
    for row in items_export:
        item, v10, val10, v11, val11 = row
        # Jan 11 Estimate
        if val11 is not None: records.append(create_record(metadata, t_jan_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val11), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v11 is not None: records.append(create_record(metadata, t_jan_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v11), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))
        
        # Jan 10 Actual
        if val10 is not None: records.append(create_record({"year": 2010, "month": 1, "appendix_number": "PL9", "source_file": "2011_01_Phuluc_01_2011_PL9.md"}, t_jan_10, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val10), "unit": "million_USD", "data_type": "Actual", "trade_type": "Export"}))
        if v10 is not None: records.append(create_record({"year": 2010, "month": 1, "appendix_number": "PL9", "source_file": "2011_01_Phuluc_01_2011_PL9.md"}, t_jan_10, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v10), "unit": "1000_ton", "data_type": "Actual", "trade_type": "Export"}))

    # Process Import
    for row in items_import:
        item, v10, val10, v11, val11 = row
        # Jan 11 Estimate
        if val11 is not None: records.append(create_record(metadata, t_jan_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val11), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v11 is not None: records.append(create_record(metadata, t_jan_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v11), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))
        
        # Jan 10 Actual
        if val10 is not None: records.append(create_record({"year": 2010, "month": 1, "appendix_number": "PL9", "source_file": "2011_01_Phuluc_01_2011_PL9.md"}, t_jan_10, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val10), "unit": "million_USD", "data_type": "Actual", "trade_type": "Import"}))
        if v10 is not None: records.append(create_record({"year": 2010, "month": 1, "appendix_number": "PL9", "source_file": "2011_01_Phuluc_01_2011_PL9.md"}, t_jan_10, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v10), "unit": "1000_ton", "data_type": "Actual", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/01"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl8()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL8.json"))
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl9()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL9.json"))
    print("Successfully parsed PL8-PL9 for January 2011 (Investment, Trade).")
