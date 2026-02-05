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

def parse_pl6():
    # Fishery
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL6", "source_file": "2011_02_Phuluc_02_2011_PL6.md"}
    records = []
    
    # [Item, Est Feb 11, Est 2M 11, Act Feb 10, Act 2M 10]
    data = [
        ("Tổng sản lượng", 355.4, 790.4, 340, 770),
        ("Sản lượng khai thác", 212.4, 442.4, 200, 430),
        ("Khai thác biển", 202, 422, 190, 410),
        ("Khai thác nội địa", 10.4, 20.4, 10, 20),
        ("Sản lượng nuôi trồng", 143, 348, 140, 340)
    ]
    
    t_feb_11 = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-28"}
    t_2m_11 = {"year": 2011, "month": 2, "period_type": "Cumulative", "report_date": "2011-02-28"}
    
    t_feb_10 = {"year": 2010, "month": 2, "period_type": "Monthly", "report_date": "2010-02-28"}
    t_2m_10 = {"year": 2010, "month": 2, "period_type": "Cumulative", "report_date": "2010-02-28"}
    
    for row in data:
        item = row[0]
        # Est Feb 11
        if row[1] is not None: records.append(create_record(metadata, t_feb_11, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Estimate"}))
        # Est 2M 11
        if row[2] is not None: records.append(create_record(metadata, t_2m_11, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[2]), "unit": "1000_ton", "data_type": "Estimate"}))
        
        # Act Feb 10
        if row[3] is not None: records.append(create_record({"year": 2010, "month": 2, "appendix_number": "PL6", "source_file": "2011_02_Phuluc_02_2011_PL6.md"}, t_feb_10, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[3]), "unit": "1000_ton", "data_type": "Actual"}))
        # Act 2M 10
        if row[4] is not None: records.append(create_record({"year": 2010, "month": 2, "appendix_number": "PL6", "source_file": "2011_02_Phuluc_02_2011_PL6.md"}, t_2m_10, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[4]), "unit": "1000_ton", "data_type": "Actual"}))

    return records

def parse_pl8():
    # Investment
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL8", "source_file": "2011_02_Phuluc_02_2011_PL8.md"}
    records = []
    
    t_feb_11 = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-28"}
    t_2m_11 = {"year": 2011, "month": 2, "period_type": "Cumulative", "report_date": "2011-02-28"}
    
    # [Item, Est Feb 11, Est 2M 11]
    data = [
        ("Vốn ngân sách giao đầu năm", 208350, 555421),
        ("Vốn thực hiện đầu tư", 200850, 542421),
        ("Đầu tư Thuỷ lợi", 154000, 469571),
        ("Đầu tư Nông nghiệp", 23500, 33000),
        ("Đầu tư Lâm nghiệp", 8000, 15500),
        ("Đầu tư Thuỷ sản", 1000, 1500),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 2500, 4500),
        ("Khoa học - Công nghệ", 4000, 8500),
        ("Giáo dục - Đào tạo", 3000, 6500),
        ("Các ngành khác", 4850, 7850),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 6000, 10500),
        ("Vốn chuẩn bị đầu tư", 1500, 2500),
        ("Vốn trái phiếu Chính phủ", 170000, 170000),
        ("Các dự án có trong QĐ171", 125000, 125000),
        ("Các dự án cấp bách bổ sung", 25000, 25000),
        ("Các dự án thuỷ lợi ĐBSHồng", 20000, 20000),
        ("Tổng vốn đầu tư : = A + B", 378350, 725421)
    ]
    
    for row in data:
        item = row[0]
        records.append(create_record(metadata, t_feb_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_2m_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[2]), "unit": "million_VND", "data_type": "Estimate"}))
        
    return records

def parse_pl9():
    # Trade Summary
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL9", "source_file": "2011_02_Phuluc_02_2011_PL9.md"}
    records = []
    
    # [Item, Vol T2, Val T2, Vol 2T, Val 2T] (All Estimates 2011)
    # Unit 1000 ton, Million USD
    # Note: Column order in data block: Jan 11 (Act), Feb 11 (Est), 2M 11 (Est)
    
    items_export = [
        ("Tổng kim ngạch XK", None, 1500, None, 3596),
        ("Nông sản chính", None, 816, None, 2013),
        ("Cà phê", 80, 155, 225, 438),
        ("Cao su", 30, 135, 106, 467),
        ("Gạo", 600, 310, 1141, 592),
        ("Chè", 11, 16, 22, 32),
        ("Hạt điều", 10, 70, 24, 166),
        ("Hạt tiêu", 6, 30, 11, 53),
        ("Hàng rau quả", None, 30, None, 77),
        ("Sắn và sản phẩm từ sắn", 200, 70, 543, 187),
        ("Thuỷ sản", None, 400, None, 835),
        ("Lâm sản chính", None, 222, None, 594),
        ("Quế", None, 2, None, 5),
        ("Gỗ & sản phẩm gỗ", None, 200, None, 548),
        ("SP mây, tre, cói, thảm", None, 20, None, 41),
        ("Các mặt hàng nông lâm sản khác", None, 62, None, 154)
    ]
    
    items_import = [
        ("Tổng kim ngạch NK", None, 1000, None, 2267),
        ("Các mặt hàng nhập khẩu chính", None, 740, None, 1543),
        ("Phân bón các loại", 280, 107, 558, 212),
        ("U RE", 30, 11, 60, 22),
        ("S A", 60, 11, 118, 21),
        ("D A P", 50, 28, 100, 56),
        ("N P K", 10, 4, 19, 8),
        ("Các loại phân bón khác", 130, 53, 260, 105),
        ("Thuốc trừ sâu & nguyên liệu", None, 50, None, 98),
        ("Lúa mỳ", 100, 35, 212, 73),
        ("Thức ăn gia súc và nguyên liệu", None, 200, None, 428),
        ("Dầu mỡ động, thực vật", None, 80, None, 163),
        ("Cao su", 20, 52, 43, 112),
        ("Bông các loại", 30, 85, 67, 189),
        ("Sữa &sản phẩm sữa", None, 40, None, 83),
        ("Gỗ & sản phẩm gỗ", None, 90, None, 182),
        ("Muối", None, 1, None, 2),
        ("Hàng thủy sản", None, 30, None, 62),
        ("Hàng rau quả", None, 25, None, 53)
    ]
    
    t_feb_11 = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-28"}
    t_2m_11 = {"year": 2011, "month": 2, "period_type": "Cumulative", "report_date": "2011-02-28"}
    
    for row in items_export:
        item, v_feb, val_feb, v_2m, val_2m = row
        # Feb 11
        if val_feb is not None: records.append(create_record(metadata, t_feb_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_feb), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_feb is not None: records.append(create_record(metadata, t_feb_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_feb), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))
        
        # 2M 11
        if val_2m is not None: records.append(create_record(metadata, t_2m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_2m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_2m is not None: records.append(create_record(metadata, t_2m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_2m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))

    for row in items_import:
        item, v_feb, val_feb, v_2m, val_2m = row
        # Feb 11
        if val_feb is not None: records.append(create_record(metadata, t_feb_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_feb), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_feb is not None: records.append(create_record(metadata, t_feb_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_feb), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))
        
        # 2M 11
        if val_2m is not None: records.append(create_record(metadata, t_2m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_2m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_2m is not None: records.append(create_record(metadata, t_2m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_2m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl6()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl8()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL8.json"))
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl9()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL9.json"))
    print("Successfully parsed PL6, PL8, PL9 for February 2011 (Fishery, Investment, Trade Summary). PL7 Skipped.")
