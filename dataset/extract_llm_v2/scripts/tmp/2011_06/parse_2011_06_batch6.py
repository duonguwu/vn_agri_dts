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
        "Ấn Độ": "India", "Bỉ": "Belgium"
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

def parse_pl14():
    # Import Markets 5M (PL14)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL14", "source_file": "2011_06_Phuluc_06_2011_PL14.md"}
    records = []
    t_5m_11 = {"year": 2011, "month": 5, "period_type": "Monthly", "report_date": "2011-05-31"} # Data is 5 Months 2011
    
    data_structure = {
        "Bông các loại": [
            ["HOA KỲ", 88734, 314108], ["ẤN ĐỘ", 23636, 77737], ["BRAXIN", 3171, 8870],
            ["TRUNG QUỐC", 274, 1537], ["HÀN QUỐC", 335, 1041], ["ĐÀI LOAN", 206, 821],
            ["IN ĐÔ NÊ XI A", 237, 689], ["THỤY SỸ", 242, 531], ["ITALIA", 232, 330]
        ],
        "Cao su": [
            ["HÀN QUỐC", 22028, 71055], ["CAMPUCHIA", 12782, 61062], ["THÁI LAN", 15490, 52691],
            ["ĐÀI LOAN", 13695, 40215], ["NHẬT BẢN", 10062, 34699], ["TRUNG QUỐC", 9627, 21895],
            ["HOA KỲ", 9597, 11338], ["NGA", 1945, 8529], ["PHÁP", 3986, 6467], ["MALAIXIA", 3392, 2863]
        ],
        "Dầu mỡ động thực vật": [
            ["MALAIXIA", None, 198568], ["IN ĐÔ NÊ XI A", None, 92646], ["ACHENTINA", None, 46821],
            ["CHI LÊ", None, 2856], ["TRUNG QUỐC", None, 2683], ["HOA KỲ", None, 2289],
            ["THÁI LAN", None, 1718], ["HÀN QUỐC", None, 1599], ["ẤN ĐỘ", None, 1515], ["XINH GA PO", None, 1295]
        ],
        "Lúa mì": [
            ["Ô X TRÂY LIA", 960478, 325167], ["HOA KỲ", 138519, 54430], ["CA NA ĐA", 11886, 5165]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["LÀO", None, 129483], ["TRUNG QUỐC", None, 57110], ["HOA KỲ", None, 54480],
            ["MALAIXIA", None, 36488], ["THÁI LAN", None, 26303], ["NIU ZI LÂN", None, 21474],
            ["CAMPUCHIA", None, 16009], ["MI AN MA", None, 14042], ["BRAXIN", None, 10737], ["IN ĐÔ NÊ XI A", None, 7965]
        ],
        "Phân bón các loại": [
            ["TRUNG QUỐC", 561356, 191035], ["PHI LIP PIN", 122687, 56676], ["CA NA ĐA", 90535, 41239],
            ["NHẬT BẢN", 108820, 21763], ["HÀN QUỐC", 46133, 12680], ["MALAIXIA", 24783, 10039],
            ["ĐÀI LOAN", 35853, 8397], ["UCRAINA", 20884, 8121], ["NAUY", 13912, 7091], ["BỈ", 5041, 2811]
        ],
        "Sữa và sản phẩm sữa": [
            ["NIU ZI LÂN", None, 96918], ["HOA KỲ", None, 82921], ["HÀ LAN", None, 36360],
            ["Ô X TRÂY LIA", None, 21345], ["THÁI LAN", None, 11422], ["BA LAN", None, 10353],
            ["PHÁP", None, 10058], ["ĐỨC", None, 6499], ["ĐAN MẠCH", None, 4549], ["TÂY BAN NHA", None, 3702]
        ],
        "Thức ăn gia súc và nguyên liệu": [
            ["ẤN ĐỘ", None, 331497], ["ACHENTINA", None, 136060], ["HOA KỲ", None, 100573],
            ["THÁI LAN", None, 45741], ["TRUNG QUỐC", None, 43414], ["IN ĐÔ NÊ XI A", None, 26039],
            ["ĐÀI LOAN", None, 17657], ["CA NA ĐA", None, 14270], ["TVQ ARẬP THỐNG NHẤT", None, 12416], ["PHI LIP PIN", None, 11389]
        ],
        "Thuốc trừ sâu và nguyên liệu": [
            ["TRUNG QUỐC", None, 109181], ["ẤN ĐỘ", None, 23137], ["ANH", None, 19913],
            ["XINH GA PO", None, 18555], ["THÁI LAN", None, 18498], ["NHẬT BẢN", None, 14846],
            ["ĐỨC", None, 12830], ["HÀN QUỐC", None, 9886], ["IN ĐÔ NÊ XI A", None, 7132], ["MALAIXIA", None, 5183]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 42031], ["THÁI LAN", None, 12691], ["HOA KỲ", None, 11343],
            ["MI AN MA", None, 6022], ["Ô X TRÂY LIA", None, 5880], ["MALAIXIA", None, 1878],
            ["CHI LÊ", None, 1426], ["BRAXIN", None, 743], ["IN ĐÔ NÊ XI A", None, 167]
        ],
        "Hàng thuỷ sản": [
            ["ĐÀI LOAN", None, 23668], ["IN ĐÔ NÊ XI A", None, 12244], ["NHẬT BẢN", None, 10755],
            ["NAUY", None, 9447], ["TRUNG QUỐC", None, 9215], ["BA LAN", None, 7932],
            ["THÁI LAN", None, 7669], ["HOA KỲ", None, 7179], ["HÀN QUỐC", None, 6987], ["ẤN ĐỘ", None, 6041]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            val = r[2]
            qty = r[1]
            if val is not None:
                records.append(create_record(metadata, t_5m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Import"}))
            if qty is not None:
                records.append(create_record(metadata, t_5m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Import"}))

    return records

def parse_pl15():
    # Export Markets 5M (PL15)
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL15", "source_file": "2011_06_Phuluc_06_2011_PL15.md"}
    records = []
    t_5m_11 = {"year": 2011, "month": 5, "period_type": "Monthly", "report_date": "2011-05-31"} # Data is 5 Months 2011
    
    data_structure = {
        "Cà phê": [
            ["Hoa Kỳ", 77718, 187560], ["Bỉ", 81107, 178482], ["Đức", 77539, 172342],
            ["Italia", 58261, 121741], ["Tây Ban Nha", 43738, 94147], ["Nhật Bản", 22926, 60171],
            ["Hà Lan", 22791, 49013], ["Anh", 19920, 45230], ["Trung Quốc", 16766, 37793], ["Hàn Quốc", 15382, 31442]
        ],
        "Cao su": [
            ["Trung Quốc", 143952, 609303], ["Malaixia", 15657, 70776], ["Hàn Quốc", 11703, 50494],
            ["Đài Loan", 9226, 43942], ["Đức", 8678, 43534], ["Hoa Kỳ", 7020, 27232],
            ["Nga", 4278, 22431], ["Nhật Bản", 3875, 20072], ["Thổ Nhĩ Kỳ", 4096, 19766], ["Tây Ban Nha", 3157, 15593]
        ],
        "Chè": [
            ["Pakixtan", 5656, 9488], ["Nga", 6240, 9253], ["Đài Loan", 6564, 8378],
            ["Trung Quốc", 3418, 4174], ["Inđônêxia", 2795, 3225], ["Hoa Kỳ", 1520, 1632],
            ["Đức", 1145, 1610], ["Ba Lan", 1017, 1050], ["Arập Xêut", 375, 768], ["TVQ Arập thống nhất", 456, 730]
        ],
        "Gạo": [
            ["Inđônêxia", 687525, 345170], ["Philippin", 460840, 224089], ["Malaixia", 261948, 137680],
            ["Cu Ba", 259900, 135523], ["Xinhgapo", 193250, 94498], ["Trung Quốc", 191085, 94406],
            ["Hồng Kông", 74605, 41006], ["Đài Loan", 56408, 28711], ["Nga", 21148, 10539], ["Đông Timo", 21060, 9734]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["Hoa Kỳ", None, 505048], ["Trung Quốc", None, 222806], ["Nhật Bản", None, 205781],
            ["Hàn Quốc", None, 84837], ["Anh", None, 76725], ["Đức", None, 51743],
            ["Ôxtrâylia", None, 29577], ["Pháp", None, 29134], ["Hà Lan", None, 29106], ["Canađa", None, 28177]
        ],
        "Hàng rau quả": [
            ["Trung Quốc", None, 44214], ["Inđônêxia", None, 26323], ["Nhật Bản", None, 17220],
            ["Hà Lan", None, 13953], ["Nga", None, 13201], ["Hoa Kỳ", None, 11120],
            ["Hàn Quốc", None, 8487], ["Thái Lan", None, 8428], ["Xinhgapo", None, 6856], ["Đài Loan", None, 6614]
        ],
        "Hàng thuỷ sản": [
            ["Hoa Kỳ", None, 385999], ["Nhật Bản", None, 301339], ["Hàn Quốc", None, 163495],
            ["Đức", None, 100846], ["Trung Quốc", None, 84931], ["Hà Lan", None, 67413],
            ["Italia", None, 66922], ["Tây Ban Nha", None, 57758], ["Ôxtrâylia", None, 49307], ["Canađa", None, 48162]
        ],
        "Hạt điều": [
            ["Hoa Kỳ", 16502, 124832], ["Trung Quốc", 11567, 88308], ["Hà Lan", 7687, 55317],
            ["Ôxtrâylia", 3778, 27502], ["Nga", 1973, 15119], ["Anh", 1379, 10054],
            ["Canađa", 978, 8207], ["Đức", 925, 7116], ["Thái Lan", 763, 6188], ["Đài Loan", 575, 4972]
        ],
        "Hạt tiêu": [
            ["Hoa Kỳ", 8290, 45456], ["Đức", 5879, 34366], ["Hà Lan", 4085, 22859],
            ["TVQ Arập thống nhất", 4126, 21289], ["Ấn Độ", 3098, 15152], ["Ai cập", 2779, 13802],
            ["Pakixtan", 2184, 10983], ["Tây Ban Nha", 1745, 9920], ["Nga", 1929, 9604], ["Xinhgapo", 1923, 9589]
        ],
        "Sản phẩm mây, tre, cói và thảm": [
            ["Hoa Kỳ", None, 12265], ["Đức", None, 11828], ["Nhật Bản", None, 11775],
            ["Pháp", None, 3812], ["Hà Lan", None, 3418], ["Ôxtrâylia", None, 3342],
            ["Anh", None, 3057], ["Đài Loan", None, 3042], ["Italia", None, 2550], ["Hàn Quốc", None, 2368]
        ],
        "Sắn và các sản phẩm": [
            ["Trung Quốc", 1458492, 508738], ["Đài Loan", 18317, 9607], ["Hàn Quốc", 15703, 4980],
            ["Philippin", 9372, 3163], ["Nhật Bản", 2722, 1751], ["Malaixia", 1196, 692], ["Nga", 671, 395]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            val = r[2]
            qty = r[1]
            if val is not None:
                records.append(create_record(metadata, t_5m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            if qty is not None:
                records.append(create_record(metadata, t_5m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl14()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL14.json"))
    save_json({"metadata": {"year": 2011, "month": 6}, "records": parse_pl15()}, os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL15.json"))
    print("Successfully parsed PL14, PL15 for June 2011 (Detailed 5M Export/Import Markets).")
