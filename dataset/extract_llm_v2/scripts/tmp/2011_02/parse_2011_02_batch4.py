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

def parse_pl10():
    # Export Markets 1 Month (Jan) 2011
    # File name: 2011_02_Phuluc_02_2011_PL10.md but content is for Jan 2011 (1 THÁNG NĂM 2011)
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL10", "source_file": "2011_02_Phuluc_02_2011_PL10.md"}
    records = []
    t_1m = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-31"} # Data is for Jan
    
    # We will transcribe detailed data from view_file Step 505
    data_structure = {
        "Cà phê": [
            ["BỈ", 24358, 46724], ["HOA KỲ", 17609, 39024], ["ITALIA", 18117, 33570],
            ["ĐỨC", 13024, 25691], ["TÂY BAN NHA", 11366, 20908], ["HÀ LAN", 7174, 13731],
            ["NHẬT BẢN", 5260, 12064], ["ANH", 4652, 10298], ["THỤY SỸ", 4401, 8520], ["XINH GA PO", 4292, 8141]
        ],
        "Cao su": [
            ["TRUNG QUỐC", 47437, 215806], ["MALAIXIA", 4422, 19679], ["ĐÀI LOAN", 3341, 14609],
            ["HÀN QUỐC", 3397, 13393], ["ĐỨC", 2421, 10866], ["HOA KỲ", 3147, 10500],
            ["THỔ NHĨ KỲ", 1219, 5551], ["ẤN ĐỘ", 986, 4421], ["TÂY BAN NHA", 981, 4346], ["NHẬT BẢN", 931, 4187]
        ],
        "Chè": [
            ["PAKIXTAN", 3139, 4940], ["NGA", 1492, 2265], ["ĐÀI LOAN", 1045, 1311],
            ["TRUNG QUỐC", 555, 772], ["IN ĐÔ NÊ XI A", 483, 540], ["ARẬP XÊÚT", 211, 425],
            ["ĐỨC", 341, 409], ["BA LAN", 365, 367], ["HOA KỲ", 256, 276], ["TVQ ARẬP THỐNG NHẤT", 119, 222]
        ],
        "Gạo": [
            ["IN ĐÔ NÊ XI A", 202625, 105591], ["CUBA", 47750, 27904], ["MALAIXIA", 47700, 22658],
            ["XINH GA PO", 20940, 11437], ["HỒNG CÔNG", 6285, 4172], ["ĐÔNG TIMO", 7630, 3769],
            ["TRUNG QUỐC", 2385, 1681], ["ĐÀI LOAN", 1708, 1103], ["NAM PHI", 1775, 918], ["B RU NÂY", 850, 540]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["HOA KỲ", None, 117525], ["NHẬT BẢN", None, 49094], ["TRUNG QUỐC", None, 31680],
            ["HÀN QUỐC", None, 23599], ["ANH", None, 21622], ["ĐỨC", None, 18257],
            ["PHÁP", None, 11510], ["HÀ LAN", None, 9134], ["Ô X TRÂY LIA", None, 7571], ["ITALIA", None, 7037]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 13946], ["NGA", None, 4023], ["THÁI LAN", None, 3855],
            ["NHẬT BẢN", None, 3157], ["HÀ LAN", None, 2780], ["IN ĐÔ NÊ XI A", None, 2399],
            ["HOA KỲ", None, 1774], ["CA NA ĐA", None, 1356], ["XINH GA PO", None, 1260], ["HÀN QUỐC", None, 1049]
        ],
        "Hàng thuỷ sản": [
            ["HOA KỲ", None, 83897], ["NHẬT BẢN", None, 68433], ["HÀN QUỐC", None, 34568],
            ["ĐỨC", None, 20853], ["TRUNG QUỐC", None, 15773], ["TÂY BAN NHA", None, 14060],
            ["ITALIA", None, 12791], ["CA NA ĐA", None, 12111], ["MÊ HI CÔ", None, 10975], ["PHÁP", None, 10101]
        ],
        "Hạt điều": [
            ["HOA KỲ", 3937, 28496], ["TRUNG QUỐC", 2930, 21336], ["HÀ LAN", 1989, 14491],
            ["ÔXTRÂYLIA", 911, 6280], ["NGA", 590, 4391], ["ANH", 371, 2578],
            ["CA NA ĐA", 248, 2029], ["ĐỨC", 208, 1577], ["XINH GA PO", 209, 1214], ["TVQ ARẬP THỐNG NHẤT", 146, 1002]
        ],
        "Hạt tiêu": [
            ["HOA KỲ", 920, 4221], ["ĐỨC", 514, 3161], ["HÀ LAN", 419, 2047],
            ["NHẬT BẢN", 226, 1297], ["NGA", 269, 1263], ["ANH", 184, 860],
            ["AI CẬP", 183, 751], ["BA LAN", 168, 740], ["HÀN QUỐC", 149, 715], ["ẤN ĐỘ", 145, 646]
        ],
        "Sản phẩm mây, tre, cói và thảm": [
            ["ĐỨC", None, 3749], ["HOA KỲ", None, 3308], ["NHẬT BẢN", None, 2127],
            ["PHÁP", None, 1161], ["HÀ LAN", None, 1030], ["Ô X TRÂY LIA", None, 820],
            ["ANH", None, 818], ["ĐÀI LOAN", None, 622], ["ITALIA", None, 587], ["TÂY BAN NHA", None, 569]
        ],
        "Sắn và các sản phẩm từ sắn": [
            ["TRUNG QUỐC", 322112, 108670], ["HÀN QUỐC", 7024, 2038], ["ĐÀI LOAN", 3617, 1919],
            ["PHI LIP PIN", 1330, 704], ["NHẬT BẢN", 570, 226], ["MALAIXIA", 350, 197], ["NGA", 190, 121]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            qty = r[1]
            val = r[2]
            
            if val is not None:
                records.append(create_record(metadata, t_1m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            if qty is not None:
                records.append(create_record(metadata, t_1m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
                
    return records

def parse_pl11():
    # Import Markets 1 Month (Jan) 2011
    metadata = {"year": 2011, "month": 2, "appendix_number": "PL11", "source_file": "2011_02_Phuluc_02_2011_PL11.md"}
    records = []
    t_1m = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-31"} # Data is for Jan
    
    data_structure = {
        "Bông các loại": [
            ["HOA KỲ", 17692, 52806], ["ẤN ĐỘ", 11960, 31690], ["BRAXIN", 452, 1572],
            ["TRUNG QUỐC", 37, 185], ["HÀN QUỐC", 45, 107], ["ITALIA", 78, 100],
            ["IN ĐÔ NÊ XI A", 40, 89], ["ĐÀI LOAN", 24, 72]
        ],
        "Cao su": [
            ["CAMPUCHIA", 3303, 15870], ["HÀN QUỐC", 3608, 10728], ["THÁI LAN", 3140, 8116],
            ["ĐÀI LOAN", 2422, 6307], ["NHẬT BẢN", 1850, 5645], ["TRUNG QUỐC", 1321, 2818],
            ["HOA KỲ", 1542, 2025], ["PHÁP", 414, 1400], ["NGA", 190, 895], ["MALAIXIA", 947, 610]
        ],
        "Dầu mỡ động thực vật": [
            ["MALAIXIA", None, 31187], ["ACHENTINA", None, 27397], ["IN ĐÔ NÊ XI A", None, 20106],
            ["CHI LÊ", None, 1134], ["THÁI LAN", None, 535], ["TRUNG QUỐC", None, 388],
            ["HOA KỲ", None, 325], ["HÀN QUỐC", None, 296], ["ẤN ĐỘ", None, 125], ["XINH GA PO", None, 117]
        ],
        "Lúa mì": [
            ["HOA KỲ", 4903, 1965], ["Ô X TRÂY LIA", 106677, 36264]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["LÀO", None, 21181], ["TRUNG QUỐC", None, 11412], ["HOA KỲ", None, 8917],
            ["MALAIXIA", None, 6475], ["THÁI LAN", None, 5441], ["HÀN QUỐC", None, 5115],
            ["NIU ZI LÂN", None, 3372], ["CAMPUCHIA", None, 3250], ["BRAXIN", None, 2687], ["IN ĐÔ NÊ XI A", None, 1970]
        ],
        "Phân bón các loại": [
            ["TRUNG QUỐC", 131853, 44691], ["PHI LIP PIN", 19620, 10352], ["CA NA ĐA", 23091, 9957],
            ["NHẬT BẢN", 13040, 2603], ["ĐÀI LOAN", 6327, 1510], ["NAUY", 2064, 1001],
            ["BỈ", 1748, 995], ["ẤN ĐỘ", 227, 696], ["HOA KỲ", 1141, 642], ["HÀN QUỐC", 360, 111]
        ],
        "Sữa và sản phẩm sữa": [
            ["NIU ZI LÂN", None, 19826], ["HOA KỲ", None, 9624], ["HÀ LAN", None, 3415],
            ["Ô X TRÂY LIA", None, 1522], ["BA LAN", None, 1348], ["THÁI LAN", None, 1017],
            ["ĐỨC", None, 927], ["PHÁP", None, 832], ["HÀN QUỐC", None, 755], ["ĐAN MẠCH", None, 686]
        ],
        "Thức ăn gia súc và nguyên liệu": [
            ["ẤN ĐỘ", None, 97240], ["ACHENTINA", None, 45034], ["HOA KỲ", None, 17965],
            ["TRUNG QUỐC", None, 9359], ["THÁI LAN", None, 6413], ["CA NA ĐA", None, 5813],
            ["PHI LIP PIN", None, 5033], ["IN ĐÔ NÊ XI A", None, 3051], ["ĐÀI LOAN", None, 2455], ["Ô X TRÂY LIA", None, 2325]
        ],
        "Thuốc trừ sâu và nguyên liệu": [
            ["TRUNG QUỐC", None, 19970], ["ẤN ĐỘ", None, 3798], ["ANH", None, 3608],
            ["XINH GA PO", None, 3541], ["THÁI LAN", None, 3447], ["THỤY SỸ", None, 3201],
            ["NHẬT BẢN", None, 2356], ["HÀN QUỐC", None, 1442], ["HOA KỲ", None, 1180], ["ĐỨC", None, 968]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 15360], ["HOA KỲ", None, 6137], ["MI AN MA", None, 1768],
            ["THÁI LAN", None, 1056], ["Ô X TRÂY LIA", None, 614], ["MALAIXIA", None, 577],
            ["BRAXIN", None, 299], ["IN ĐÔ NÊ XI A", None, 32]
        ],
        "Hàng thuỷ sản": [
            ["IN ĐÔ NÊ XI A", None, 2965], ["ĐÀI LOAN", None, 2773], ["NHẬT BẢN", None, 2469],
            ["NAUY", None, 2225], ["THÁI LAN", None, 1959], ["BA LAN", None, 1791],
            ["TRUNG QUỐC", None, 1482], ["ẤN ĐỘ", None, 1020], ["NGA", None, 934], ["CHI LÊ", None, 728]
        ],
        "Muối": [
            ["China", None, 738], ["Thailand", None, 62], ["Australia", None, 46],
            ["New Zealand", None, 9], ["Germany", None, 9], ["India", None, 7],
            ["Denmark", None, 6], ["Laos", None, 2], ["United States of America", None, 2], ["Malaysia", None, 1]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            qty = r[1]
            val = r[2]
            
            if val is not None:
                records.append(create_record(metadata, t_1m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Import"}))
            if qty is not None:
                records.append(create_record(metadata, t_1m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Import"}))
                
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl10()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL10.json"))
    save_json({"metadata": {"year": 2011, "month": 2}, "records": parse_pl11()}, os.path.join(out_dir, "2011_02_Phuluc_02_2011_PL11.json"))
    print("Successfully parsed PL10, PL11 for February 2011 (Trade Markets Jan).")
