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
        "HOA KỲ": "United States", "ĐỨC": "Germany", "BỈ": "Belgium", "ITALIA": "Italy", "Italia": "Italy",
        "TÂY BAN NHA": "Spain", "NHẬT BẢN": "Japan", "HÀ LAN": "Netherlands", "XINH GA PO": "Singapore",
        "THỤY SỸ": "Switzerland", "ANH": "United Kingdom", "TRUNG QUỐC": "China", "MALAIXIA": "Malaysia",
        "ĐÀI LOAN": "Taiwan", "HÀN QUỐC": "South Korea", "THỔ NHĨ KỲ": "Turkey", "NGA": "Russia",
        "PAKIXTAN": "Pakistan", "IN ĐÔ NÊ XI A": "Indonesia", "BA LAN": "Poland", "ARẬP XÊÚT": "Saudi Arabia",
        "TVQ ARẬP THỐNG NHẤT": "United Arab Emirates", "CUBA": "Cuba", "HỒNG CÔNG": "Hong Kong",
        "ĐÔNG TIMO": "East Timor", "PHI LIP PIN": "Philippines", "NAM PHI": "South Africa", "B RU NÂY": "Brunei", 
        "PHÁP": "France", "BRAXIN": "Brazil", "Braxin": "Brazil",
        "Ô X TRÂY LIA": "Australia", "THÁI LAN": "Thailand", "CA NA ĐA": "Canada", "MÊ HI CÔ": "Mexico",
        "AI CẬP": "Egypt", "ẤN ĐỘ": "India", "CAMPUCHIA": "Cambodia",
        "ACHENTINA": "Argentina", "CHI LÊ": "Chile", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand",
        "MI AN MA": "Myanmar", "ĐAN MẠCH": "Denmark", "NAUY": "Norway", "UCRAINA": "Ukraine",
        "Cả nước": "Cả nước",
        "Hoa Kỳ": "United States", "Trung Quốc": "China", "Hàn Quốc": "South Korea", "Inđônêxia": "Indonesia",
        "Thái Lan": "Thailand", "Đài Loan": "Taiwan", "Anh": "United Kingdom", "Đức": "Germany", 
        "Nhật Bản": "Japan", "Tây Ban Nha": "Spain", "Thổ Nhĩ Kỳ": "Turkey", "Hà Lan": "Netherlands",
        "Nga": "Russia", "Pháp": "France", "Malaixia": "Malaysia", "Pakixtan": "Pakistan",
        "Ba Lan": "Poland", "Arập Xêut": "Saudi Arabia", "TVQ Arập thống nhất": "United Arab Emirates",
        "Xinhgapo": "Singapore", "Philippin": "Philippines", "Cu Ba": "Cuba", "Hồng Kông": "Hong Kong",
        "Đông Timo": "East Timor", "Ôxtrâylia": "Australia", "Canađa": "Canada", "Ai cập": "Egypt",
        "Ấn Độ": "India"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    geo_context["region_id"] = "COUNTRY"
    if norm_loc == "Cả nước": geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    else: geo_context["region_name_vn"] = norm_loc; geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl12():
    # Investment (PL12)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL12", "source_file": "2011_06_Phuluc_06_2011_PL12.md"}
    records = []
    
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    t_jun_11 = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-30"}
    
    # Cols: KH, TH 5T, Est T6, Est 6T, %
    # Row 20: Von ngan sach
    data = [
        ("Vốn ngân sách giao đầu năm", 3672300, 1690144, 238650, 1912794),
        ("Vốn thực hiện đầu tư", 3275300, 1635544, 221900, 1841444),
        ("Đầu tư Thuỷ lợi", 1887571, 1078100, 125500, 1203600),
        ("Đầu tư Nông nghiệp", 701000, 363300, 58200, 421500),
        ("Đầu tư Lâm nghiệp", 286000, 83844, 14450, 98294),
        ("Đầu tư Thuỷ sản", 20429, 8100, 1500, 9600),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 30000, 12500, 3500, 16000),
        ("Khoa học - Công nghệ", 60000, 23500, 5000, 28500),
        ("Giáo dục - Đào tạo", 90000, 24900, 6250, 31150),
        ("Các ngành khác", 200300, 41300, 7500, 48800),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 288000, 44100, 12250, 56350),
        ("Vốn chuẩn bị đầu tư", 38000, 10500, 4500, 15000),
        ("Vốn trái phiếu Chính phủ", 3500000, 1675000, 210000, 1885000),
        ("Các dự án có trong QĐ171", 2671100, 1280000, 140000, 1420000),
        ("Các dự án cấp bách bổ sung", 398000, 185000, 32000, 217000),
        ("Các dự án thuỷ lợi ĐBSHồng", 430900, 210000, 38000, 248000),
        ("Tổng vốn đầu tư : = A + B", 7172300, 3365144, 448650, 3797794)
    ]
    
    for row in data:
        item = row[0]
        records.append(create_record(metadata, t_jun_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[3]), "unit": "million_VND", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_6m_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[4]), "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_pl13():
    # Trade Summary (PL13)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL13", "source_file": "2011_06_Phuluc_06_2011_PL13.md"}
    records = []
    
    t_6m_11 = {"year": 2011, "month": 6, "period_type": "Cumulative", "report_date": "2011-06-30"}
    t_jun_11 = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-30"}
    
    # [Item, Vol T6, Val T6, Vol 6T, Val 6T]
    items_export = [
        ("Tổng kim ngạch XK", None, 2100, None, 11997),
        ("Nông sản chính", None, 1012, None, 6978),
        ("Cà phê", 115, 250, 913, 1992),
        ("Cao su", 40, 160, 274, 1184),
        ("Gạo", 610, 300, 3977, 1957),
        ("Chè", 8, 12, 50, 72),
        ("Hạt điều", 13, 100, 67, 499),
        ("Hạt tiêu", 15, 80, 70, 368),
        ("Hàng rau quả", None, 50, None, 302),
        ("Sắn và sản phẩm từ sắn", 170, 60, 1711, 604),
        ("Thuỷ sản", None, 500, None, 2589),
        ("Lâm sản chính", None, 350, None, 1907),
        ("Quế", None, 2, None, 12),
        ("Gỗ & sản phẩm gỗ", None, 330, None, 1796),
        ("SP mây, tre, cói, thảm", None, 18, None, 99)
    ]
    
    items_import = [
        ("Tổng kim ngạch NK", None, 1400, None, 7590),
        ("Các mặt hàng nhập khẩu chính", None, 976, None, 5524),
        ("Phân bón các loại", 290, 110, 1810, 684),
        ("U RE", 55, 20, 384, 140),
        ("S A", 52, 10, 400, 76),
        ("D A P", 33, 20, 215, 129),
        ("N P K", 46, 20, 153, 66),
        ("Các loại phân bón khác", 103, 40, 656, 272),
        ("Thuốc trừ sâu & nguyên liệu", None, 60, None, 333),
        ("Lúa mỳ", 215, 75, 1332, 462),
        ("Thức ăn gia súc và nguyên liệu", None, 200, None, 1175),
        ("Dầu mỡ động, thực vật", None, 70, None, 429),
        ("Cao su", 28, 70, 167, 417),
        ("Bông các loại", 38, 130, 198, 672),
        ("Sữa &sản phẩm sữa", None, 70, None, 397),
        ("Gỗ & sản phẩm gỗ", None, 120, None, 605),
        ("Muối", None, 1, None, 8),
        ("Hàng thủy sản", None, 50, None, 226),
        ("Hàng rau quả", None, 20, None, 117)
    ]
    
    for row in items_export:
        item, v_apr, val_apr, v_4m, val_4m = row
        if val_apr is not None: records.append(create_record(metadata, t_jun_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_apr), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_apr is not None: records.append(create_record(metadata, t_jun_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_apr), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))
        if val_4m is not None: records.append(create_record(metadata, t_6m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_4m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_4m is not None: records.append(create_record(metadata, t_6m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_4m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))

    for row in items_import:
        item, v_apr, val_apr, v_4m, val_4m = row
        if val_apr is not None: records.append(create_record(metadata, t_jun_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_apr), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_apr is not None: records.append(create_record(metadata, t_jun_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_apr), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))
        if val_4m is not None: records.append(create_record(metadata, t_6m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_4m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_4m is not None: records.append(create_record(metadata, t_6m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_4m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl12()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL12.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl13()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL13.json"))
    
    print("Successfully parsed PL12, PL13 for June 2011 (Investment & Trade Summary).")
