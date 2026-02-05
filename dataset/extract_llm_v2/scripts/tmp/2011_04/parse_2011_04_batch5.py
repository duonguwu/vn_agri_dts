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

def parse_pl9():
    # Import Markets Detailed 3M (PL9 - previously PL13 in March)
    metadata = {"year": 2011, "month": 4, "appendix_number": "PL9", "source_file": "2011_04_Phuluc_04_2011_f_PL9.md"}
    records = []
    t_3m_11 = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-31"}
    
    data_structure = {
        "Bông các loại": [
            ["HOA KỲ", 58549, 189687], ["ẤN ĐỘ", 19477, 58604], ["BRAXIN", 2253, 6050],
            ["TRUNG QUỐC", 108, 690], ["IN ĐÔ NÊ XI A", 217, 619], ["HÀN QUỐC", 232, 608],
            ["ĐÀI LOAN", 110, 315], ["ITALIA", 157, 218]
        ],
        "Cao su": [
            ["HÀN QUỐC", 12831, 39979], ["CAMPUCHIA", 7711, 37971], ["THÁI LAN", 9440, 30160],
            ["ĐÀI LOAN", 8223, 22874], ["NHẬT BẢN", 6567, 22255], ["TRUNG QUỐC", 4712, 9696],
            ["HOA KỲ", 6326, 6330], ["NGA", 1153, 4404], ["PHÁP", 1930, 4063], ["ITALIA", 837, 2259]
        ],
        "Dầu mỡ động thực vật": [
            ["MALAIXIA", None, 103253], ["IN ĐÔ NÊ XI A", None, 54021], ["ACHENTINA", None, 43459],
            ["CHI LÊ", None, 2277], ["HOA KỲ", None, 1283], ["THÁI LAN", None, 1241],
            ["TRUNG QUỐC", None, 1018], ["HÀN QUỐC", None, 911], ["ẤN ĐỘ", None, 816], ["XINH GA PO", None, 661]
        ],
        "Lúa mì": [
            ["Ô X TRÂY LIA", 492286, 160053], ["HOA KỲ", 63033, 21763]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["LÀO", None, 59351], ["HOA KỲ", None, 28227], ["TRUNG QUỐC", None, 27509],
            ["MALAIXIA", None, 19780], ["THÁI LAN", None, 13516], ["NIU ZI LÂN", None, 10342],
            ["CAMPUCHIA", None, 7519], ["BRAXIN", None, 7126], ["MI AN MA", None, 6794], ["IN ĐÔ NÊ XI A", None, 4349]
        ],
        "Phân bón các loại": [
            ["TRUNG QUỐC", 367091, 120322], ["CA NA ĐA", 60545, 27088], ["PHI LIP PIN", 52140, 25549],
            ["NHẬT BẢN", 66642, 13323], ["HÀN QUỐC", 39006, 10966], ["ĐÀI LOAN", 19990, 4637],
            ["MALAIXIA", 6308, 2659], ["NAUY", 5182, 2653], ["BỈ", 2963, 1646], ["HOA KỲ", 2319, 1579]
        ],
        "Sữa và sản phẩm sữa": [
            ["NIU ZI LÂN", None, 58214], ["HOA KỲ", None, 43699], ["HÀ LAN", None, 20950],
            ["Ô X TRÂY LIA", None, 7171], ["THÁI LAN", None, 6356], ["BA LAN", None, 6011],
            ["PHÁP", None, 5513], ["ĐỨC", None, 3159], ["TÂY BAN NHA", None, 2459], ["HÀN QUỐC", None, 2336]
        ],
        "Thức ăn gia súc và nguyên liệu": [
            ["ẤN ĐỘ", None, 253732], ["ACHENTINA", None, 77679], ["HOA KỲ", None, 61162],
            ["THÁI LAN", None, 21280], ["TRUNG QUỐC", None, 21186], ["IN ĐÔ NÊ XI A", None, 10307],
            ["ĐÀI LOAN", None, 9188], ["CA NA ĐA", None, 7156], ["TVQ ARẬP THỐNG NHẤT", None, 7142], ["PHI LIP PIN", None, 6882]
        ],
        "Thuốc trừ sâu và nguyên liệu": [
            ["TRUNG QUỐC", None, 55102], ["ẤN ĐỘ", None, 13060], ["XINH GA PO", None, 11377],
            ["ANH", None, 10520], ["THÁI LAN", None, 10094], ["NHẬT BẢN", None, 8782],
            ["THỤY SỸ", None, 3933], ["ĐỨC", None, 6487], ["HÀN QUỐC", None, 4474], ["IN ĐÔ NÊ XI A", None, 4211]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 27813], ["HOA KỲ", None, 8461], ["THÁI LAN", None, 5031],
            ["MI AN MA", None, 3674], ["Ô X TRÂY LIA", None, 1453], ["MALAIXIA", None, 1105],
            ["BRAXIN", None, 463], ["IN ĐÔ NÊ XI A", None, 84]
        ],
        "Hàng thuỷ sản": [
            ["ĐÀI LOAN", None, 8779], ["IN ĐÔ NÊ XI A", None, 7919], ["NHẬT BẢN", None, 6531],
            ["BA LAN", None, 5213], ["TRUNG QUỐC", None, 5148], ["NAUY", None, 4882],
            ["THÁI LAN", None, 4592], ["ẤN ĐỘ", None, 3474], ["CHI LÊ", None, 3130], ["CA NA ĐA", None, 2536]
        ],
        "Muối": [
            ["TRUNG QUỐC", None, 1676], ["ẤN ĐỘ", None, 968], ["THÁI LAN", None, 157],
            ["Ô X TRÂY LIA", None, 47], ["NIU ZI LÂN", None, 34], ["ĐAN MẠCH", None, 13],
            ["ĐỨC", None, 9], ["NHẬT BẢN", None, 7], ["HOA KỲ", None, 2], ["LÀO", None, 2]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            val = r[2]
            qty = r[1]
            if val is not None:
                records.append(create_record(metadata, t_3m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Import"}))
            if qty is not None:
                records.append(create_record(metadata, t_3m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/04"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 4}, "records": parse_pl9()}, os.path.join(out_dir, "2011_04_Phuluc_04_2011_f_PL9.json"))
    print("Successfully parsed PL9 for April 2011 (Detailed Import Markets 3M).")
