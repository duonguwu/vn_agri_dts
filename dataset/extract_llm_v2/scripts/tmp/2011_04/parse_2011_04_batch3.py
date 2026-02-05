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
        "HOA KỲ": "United States", "ĐỨC": "Germany", "BỈ": "Belgium", "ITALIA": "Italy",
        "TÂY BAN NHA": "Spain", "NHẬT BẢN": "Japan", "HÀ LAN": "Netherlands", "XINH GA PO": "Singapore",
        "THỤY SỸ": "Switzerland", "ANH": "United Kingdom", "TRUNG QUỐC": "China", "MALAIXIA": "Malaysia",
        "ĐÀI LOAN": "Taiwan", "HÀN QUỐC": "South Korea", "THỔ NHĨ KỲ": "Turkey", "NGA": "Russia",
        "PAKIXTAN": "Pakistan", "IN ĐÔ NÊ XI A": "Indonesia", "BA LAN": "Poland", "ARẬP XÊÚT": "Saudi Arabia",
        "TVQ ARẬP THỐNG NHẤT": "United Arab Emirates", "CUBA": "Cuba", "HỒNG CÔNG": "Hong Kong",
        "ĐÔNG TIMO": "East Timor", "PHI LIP PIN": "Philippines", "NAM PHI": "South Africa", "B RU NÂY": "Brunei", "PHÁP": "France",
        "Ô X TRÂY LIA": "Australia", "THÁI LAN": "Thailand", "CA NA ĐA": "Canada", "MÊ HI CÔ": "Mexico",
        "AI CẬP": "Egypt", "ẤN ĐỘ": "India", "BRAXIN": "Brazil", "CAMPUCHIA": "Cambodia",
        "ACHENTINA": "Argentina", "CHI LÊ": "Chile", "LÀO": "Laos", "NIU ZI LÂN": "New Zealand",
        "MI AN MA": "Myanmar", "ĐAN MẠCH": "Denmark", "NAUY": "Norway", "Cả nước": "Cả nước"
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

def parse_pl6():
    # Investment (PL6)
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL6", "source_file": "2011_04_Phuluc_04_2011_f_PL6.md"}
    records = []
    
    t_4m_11 = {"year": 2011, "month": 4, "period_type": "Cumulative", "report_date": "2011-04-30"}
    t_apr_11 = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-30"}
    
    # Cols: KH, TH 3T, Est T4, Est 4T, %
    # Row 13: Dau tu thuy loi
    data = [
        ("Vốn ngân sách giao đầu năm", 3672300, 1095786, 207450, 1292036),
        ("Vốn thực hiện đầu tư", 3275300, 1071536, 195950, 1256286),
        ("Đầu tư Thuỷ lợi", 1887571, 729000, 135500, 864500),
        ("Đầu tư Nông nghiệp", 701000, 266436, 27850, 294286),
        ("Đầu tư Lâm nghiệp", 286000, 27500, 12000, 39500),
        ("Đầu tư Thuỷ sản", 20429, 4500, 1600, 6100),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 30000, 7500, 3700, 11200),
        ("Khoa học - Công nghệ", 60000, 13000, 5000, 18000),
        ("Giáo dục - Đào tạo", 90000, 10250, 3800, 14050),
        ("Các ngành khác", 200300, 13350, 6500, 19850),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 288000, 19750, 9000, 28750),
        ("Vốn chuẩn bị đầu tư", 38000, 4500, 2500, 7000),
        ("Vốn trái phiếu Chính phủ", 3500000, 532000, 244100, 776100),
        ("Các dự án có trong QĐ171", 2671100, 375000, 155000, 530000),
        ("Các dự án cấp bách bổ sung", 398000, 75000, 42550, 117550),
        ("Các dự án thuỷ lợi ĐBSHồng", 430900, 82000, 46550, 128550),
        ("Tổng vốn đầu tư : = A + B", 7172300, 1627786, 451550, 2068136)
    ]
    
    for row in data:
        item = row[0]
        records.append(create_record(metadata, t_apr_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[3]), "unit": "million_VND", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_4m_11, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(row[4]), "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_pl7():
    # Trade Summary (PL7)
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL7", "source_file": "2011_04_Phuluc_04_2011_f_PL7.md"}
    records = []
    
    t_4m_11 = {"year": 2011, "month": 4, "period_type": "Cumulative", "report_date": "2011-04-30"}
    t_apr_11 = {"year": 2011, "month": 4, "period_type": "Monthly", "report_date": "2011-04-30"}
    
    # [Item, Vol T4, Val T4, Vol 4T, Val 4T]
    items_export = [
        ("Tổng kim ngạch XK", None, 2200, None, 8047),
        ("Nông sản chính", None, 1320, None, 4994),
        ("Cà phê", 155, 325, 675, 1407),
        ("Cao su", 40, 175, 204, 897),
        ("Gạo", 890, 445, 2820, 1416),
        ("Chè", 9, 12, 33, 46),
        ("Hạt điều", 10, 70, 39, 275),
        ("Hạt tiêu", 16, 80, 42, 208),
        ("Hàng rau quả", 0, 50, None, 198), # Vol 0?
        ("Sắn và sản phẩm từ sắn", 490, 163, 1643, 548),
        ("Thuỷ sản", None, 475, None, 1619),
        ("Lâm sản chính", None, 330, None, 1213),
        ("Quế", None, 2, None, 7),
        ("Gỗ & sản phẩm gỗ", None, 310, None, 1140),
        ("SP mây, tre, cói, thảm", None, 18, None, 66)
    ]
    
    items_import = [
        ("Tổng kim ngạch NK", None, 1300, None, 4798),
        ("Các mặt hàng nhập khẩu chính", None, 931, None, 3488),
        ("Phân bón các loại", 350, 126, 1156, 416),
        ("U RE", 67, 25, 208, 78),
        ("S A", 94, 18, 325, 61),
        ("D A P", 44, 26, 165, 97),
        ("N P K", 18, 7, 53, 23),
        ("Các loại phân bón khác", 127, 49, 405, 157),
        ("Thuốc trừ sâu & nguyên liệu", None, 53, None, 198),
        ("Lúa mỳ", 240, 79, 798, 262),
        ("Thức ăn gia súc và nguyên liệu", None, 170, None, 804),
        ("Dầu mỡ động, thực vật", None, 80, None, 293),
        ("Cao su", 30, 70, 109, 270),
        ("Bông các loại", 35, 120, 138, 440),
        ("Sữa &sản phẩm sữa", None, 70, None, 247),
        ("Gỗ & sản phẩm gỗ", None, 110, None, 356),
        ("Muối", None, 1, None, 4),
        ("Hàng thủy sản", None, 35, None, 126),
        ("Hàng rau quả", None, 17, None, 74)
    ]
    
    for row in items_export:
        item, v_apr, val_apr, v_4m, val_4m = row
        if val_apr is not None: records.append(create_record(metadata, t_apr_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_apr), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_apr is not None: records.append(create_record(metadata, t_apr_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_apr), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))
        if val_4m is not None: records.append(create_record(metadata, t_4m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_4m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if v_4m is not None: records.append(create_record(metadata, t_4m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_4m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))

    for row in items_import:
        item, v_apr, val_apr, v_4m, val_4m = row
        if val_apr is not None: records.append(create_record(metadata, t_apr_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_apr), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_apr is not None: records.append(create_record(metadata, t_apr_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_apr), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))
        if val_4m is not None: records.append(create_record(metadata, t_4m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_4m), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if v_4m is not None: records.append(create_record(metadata, t_4m_11, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(v_4m), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))

    return records

def parse_pl8():
    # Export Markets Detailed 3M (PL8)
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL8", "source_file": "2011_04_Phuluc_04_2011_f_PL8.md"}
    records = []
    t_3m_11 = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-31"} # Content is 3 months 2011
    
    data_structure = {
        "Cà phê": [
            ["HOA KỲ", 57072, 133150], ["BỈ", 58005, 119113], ["ĐỨC", 49249, 105707],
            ["ITALIA", 42037, 84216], ["TÂY BAN NHA", 29102, 60218], ["NHẬT BẢN", 13990, 35229],
            ["HÀ LAN", 16338, 33737], ["ANH", 11347, 24802], ["THỤY SỸ", 11428, 23674], ["XINH GA PO", 9973, 19991]
        ],
        "Cao su": [
            ["TRUNG QUỐC", 104196, 448755], ["MALAIXIA", 8174, 37721], ["HÀN QUỐC", 8108, 34078],
            ["ĐÀI LOAN", 6655, 31318], ["ĐỨC", 5579, 27516], ["HOA KỲ", 6023, 23014],
            ["NGA", 2642, 13902], ["THỔ NHĨ KỲ", 2844, 13880], ["NHẬT BẢN", 2612, 13232], ["TÂY BAN NHA", 2356, 11463]
        ],
        "Chè": [
            ["PAKIXTAN", 4451, 7254], ["NGA", 3928, 5834], ["ĐÀI LOAN", 3225, 4015],
            ["TRUNG QUỐC", 1883, 2277], ["IN ĐÔ NÊ XI A", 1596, 1774], ["HOA KỲ", 869, 960],
            ["ĐỨC", 617, 814], ["BA LAN", 752, 730], ["ARẬP XÊÚT", 337, 698], ["TVQ ARẬP THỐNG NHẤT", 252, 424]
        ],
        "Gạo": [
            ["IN ĐÔ NÊ XI A", 684850, 343041], ["CUBA", 156700, 85098], ["MALAIXIA", 119293, 60009],
            ["XINH GA PO", 95775, 48662], ["TRUNG QUỐC", 69852, 36392], ["PHI LIP PIN", 47259, 29900],
            ["HỒNG CÔNG", 34158, 20160], ["ĐÀI LOAN", 26311, 13173], ["NGA", 11765, 5911], ["ĐÔNG TIMO", 10460, 5119]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["HOA KỲ", None, 273508], ["NHẬT BẢN", None, 122876], ["TRUNG QUỐC", None, 94526],
            ["HÀN QUỐC", None, 49857], ["ANH", None, 49646], ["ĐỨC", None, 37204],
            ["PHÁP", None, 19871], ["HÀ LAN", None, 19857], ["Ô X TRÂY LIA", None, 16909], ["CA NA ĐA", None, 16331]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 26325], ["IN ĐÔ NÊ XI A", None, 20517], ["NHẬT BẢN", None, 9017],
            ["NGA", None, 8239], ["HÀ LAN", None, 8073], ["THÁI LAN", None, 6200],
            ["HOA KỲ", None, 5666], ["XINH GA PO", None, 3810], ["HÀN QUỐC", None, 3582], ["ĐỨC", None, 2979]
        ],
        "Hàng thuỷ sản": [
            ["HOA KỲ", None, 207835], ["NHẬT BẢN", None, 169817], ["HÀN QUỐC", None, 88213],
            ["ĐỨC", None, 56500], ["TRUNG QUỐC", None, 42712], ["ITALIA", None, 35581],
            ["HÀ LAN", None, 33937], ["TÂY BAN NHA", None, 33535], ["MÊ HI CÔ", None, 29996], ["CA NA ĐA", None, 29076]
        ],
        "Hạt điều": [
            ["HOA KỲ", 9134, 66161], ["TRUNG QUỐC", 6384, 47305], ["HÀ LAN", 4444, 29718],
            ["Ô X TRÂY LIA", 1955, 13089], ["NGA", 1016, 7419], ["ANH", 755, 5314],
            ["CA NA ĐA", 558, 4614], ["ĐỨC", 392, 3020], ["THÁI LAN", 302, 2330], ["XINH GA PO", 388, 2115]
        ],
        "Hạt tiêu": [
            ["ĐỨC", 3338, 18230], ["HOA KỲ", 3623, 17844], ["HÀ LAN", 2249, 11258],
            ["ẤN ĐỘ", 1334, 6186], ["AI CẬP", 1198, 5399], ["XINH GA PO", 1030, 5194],
            ["TVQ ARẬP THỐNG NHẤT", 1029, 4858], ["NGA", 1023, 4765], ["ANH", 849, 4379], ["TÂY BAN NHA", 794, 4254]
        ],
        "Sản phẩm mây, tre, cói và thảm": [
            ["ĐỨC", None, 7791], ["HOA KỲ", None, 7194], ["NHẬT BẢN", None, 6506],
            ["HÀ LAN", None, 2529], ["PHÁP", None, 2374], ["Ô X TRÂY LIA", None, 1729],
            ["ANH", None, 1660], ["ITALIA", None, 1614], ["ĐÀI LOAN", None, 1602], ["HÀN QUỐC", None, 1166]
        ],
        "Sắn và các sản phẩm từ sắn": [
            ["TRUNG QUỐC", 1095855, 359538], ["ĐÀI LOAN", 15604, 8157], ["HÀN QUỐC", 14802, 4575],
            ["PHI LIP PIN", 9246, 3063], ["NHẬT BẢN", 1888, 827], ["MALAIXIA", 890, 502], ["NGA", 424, 248]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            qty = r[1]
            val = r[2]
            if val is not None:
                records.append(create_record(metadata, t_3m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            if qty is not None:
                records.append(create_record(metadata, t_3m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
                
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl6()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl7()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL7.json"))
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl8()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL8.json"))
    print("Successfully parsed PL6, PL7, PL8 for April 2011 (Investment, Trade Summary, Export 3M).")
