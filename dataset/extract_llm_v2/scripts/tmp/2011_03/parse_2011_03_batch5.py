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
        "ĐÔNG TIMO": "East Timor", "NAM PHI": "South Africa", "B RU NÂY": "Brunei", "PHÁP": "France",
        "Ô X TRÂY LIA": "Australia", "THÁI LAN": "Thailand", "CA NA ĐA": "Canada", "MÊ HI CÔ": "Mexico",
        "AI CẬP": "Egypt", "ẤN ĐỘ": "India", "PHI LIP PIN": "Philippines", "BRAXIN": "Brazil",
        "CAMPUCHIA": "Cambodia", "ACHENTINA": "Argentina", "CHI LÊ": "Chile", "LÀO": "Laos",
        "NIU ZI LÂN": "New Zealand", "MI AN MA": "Myanmar", "ĐAN MẠCH": "Denmark", "NAUY": "Norway",
        "MỸ": "United States", "Australia": "Australia", "India": "India", "Germany": "Germany",
        "United States of America": "United States", "New Zealand": "New Zealand", "China": "China",
        "Denmark": "Denmark", "Laos": "Laos", "Malaysia": "Malaysia"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    geo_context["region_id"] = "COUNTRY"
    geo_context["region_name_vn"] = norm_loc
    geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl12():
    # Export Markets 2M 2011 (PL12)
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL12", "source_file": "2011_03_Phuluc_03_2011_PL12.md"}
    records = []
    t_2m_11 = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-28"} # Content is "2 tháng năm 2011"
    
    data_structure = {
        "Cà phê": [
            ["HOA KỲ", 33669, 74880], ["ĐỨC", 30077, 61661], ["BỈ", 29913, 57487],
            ["ITALIA", 27641, 52282], ["TÂY BAN NHA", 19130, 37237], ["NHẬT BẢN", 9043, 22288],
            ["HÀ LAN", 10500, 20501], ["XINH GA PO", 7906, 15460], ["THỤY SỸ", 7737, 15404], ["ANH", 6637, 14292]
        ],
        "Cao su": [
            ["TRUNG QUỐC", 75861, 341035], ["MALAIXIA", 6554, 30000], ["ĐÀI LOAN", 5568, 25865],
            ["HÀN QUỐC", 5758, 23268], ["HOA KỲ", 5565, 20795], ["ĐỨC", 3850, 18185],
            ["THỔ NHĨ KỲ", 2272, 10911], ["NHẬT BẢN", 2165, 10767], ["NGA", 1836, 9502], ["TÂY BAN NHA", 1698, 7918]
        ],
        "Chè": [
            ["PAKIXTAN", 3996, 6440], ["NGA", 2247, 3473], ["ĐÀI LOAN", 1843, 2343],
            ["TRUNG QUỐC", 1120, 1359], ["IN ĐÔ NÊ XI A", 750, 815], ["HOA KỲ", 606, 661],
            ["BA LAN", 522, 521], ["ĐỨC", 425, 520], ["ARẬP XÊÚT", 211, 425], ["TVQ ARẬP THỐNG NHẤT", 164, 290]
        ],
        "Gạo": [
            ["IN ĐÔ NÊ XI A", 403925, 205315], ["MALAIXIA", 70619, 33947], ["CUBA", 47750, 27904],
            ["XINH GA PO", 46432, 24314], ["HỒNG CÔNG", 14300, 8968], ["ĐÀI LOAN", 12109, 6274],
            ["TRUNG QUỐC", 9705, 6194], ["ĐÔNG TIMO", 7630, 3769], ["NAM PHI", 3050, 1568], ["B RU NÂY", 2230, 1346]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["HOA KỲ", None, 164673], ["NHẬT BẢN", None, 74794], ["TRUNG QUỐC", None, 54318],
            ["ANH", None, 29606], ["HÀN QUỐC", None, 25542], ["ĐỨC", None, 23928],
            ["PHÁP", None, 14629], ["HÀ LAN", None, 12216], ["ITALIA", None, 10111], ["Ô X TRÂY LIA", None, 10028]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 15656], ["IN ĐÔ NÊ XI A", None, 10225], ["NGA", None, 6029],
            ["NHẬT BẢN", None, 5161], ["THÁI LAN", None, 4814], ["HÀ LAN", None, 4669],
            ["HOA KỲ", None, 3235], ["XINH GA PO", None, 2239], ["HÀN QUỐC", None, 1777], ["CA NA ĐA", None, 1741]
        ],
        "Hàng thuỷ sản": [
            ["HOA KỲ", None, 130641], ["NHẬT BẢN", None, 105877], ["HÀN QUỐC", None, 49950],
            ["ĐỨC", None, 33997], ["TRUNG QUỐC", None, 26638], ["TÂY BAN NHA", None, 20340],
            ["ITALIA", None, 19651], ["CA NA ĐA", None, 18232], ["HÀ LAN", None, 17897], ["MÊ HI CÔ", None, 17066]
        ],
        "Hạt điều": [
            ["HOA KỲ", 5952, 42436], ["TRUNG QUỐC", 4328, 31801], ["HÀ LAN", 3018, 21041],
            ["Ô X TRÂY LIA", 1308, 8581], ["NGA", 792, 5852], ["CA NA ĐA", 404, 3272],
            ["ANH", 449, 3151], ["ĐỨC", 224, 1725], ["THÁI LAN", 207, 1498], ["TVQ ARẬP THỐNG NHẤT", 206, 1404]
        ],
        "Hạt tiêu": [
            ["HOA KỲ", 1766, 7994], ["ĐỨC", 1282, 6866], ["HÀ LAN", 618, 2976],
            ["NGA", 489, 2332], ["NHẬT BẢN", 350, 1935], ["AI CẬP", 439, 1901],
            ["ANH", 394, 1881], ["BA LAN", 399, 1690], ["ẤN ĐỘ", 331, 1633], ["PAKIXTAN", 338, 1488]
        ],
        "Sản phẩm mây, tre, cói và thảm": [
            ["ĐỨC", None, 5071], ["HOA KỲ", None, 4776], ["NHẬT BẢN", None, 3582],
            ["HÀ LAN", None, 1625], ["PHÁP", None, 1487], ["ANH", None, 1122],
            ["Ô X TRÂY LIA", None, 1078], ["ĐÀI LOAN", None, 961], ["ITALIA", None, 930], ["HÀN QUỐC", None, 767]
        ],
        "Sắn và các sản phẩm từ sắn": [
            ["TRUNG QUỐC", 622735, 204118.4], ["ĐÀI LOAN", 10561, 5514.993], ["PHI LIP PIN", 9056, 2951.687],
            ["HÀN QUỐC", 7569, 2299.882], ["NHẬT BẢN", 1251, 517.19], ["MALAIXIA", 682, 376.933], ["NGA", 424, 248.74]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            qty = r[1]
            val = r[2]
            
            if val is not None:
                records.append(create_record(metadata, t_2m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            if qty is not None:
                records.append(create_record(metadata, t_2m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
    return records

def parse_pl13():
    # Import Markets 2M 2011 (PL13)
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL13", "source_file": "2011_03_Phuluc_03_2011_PL13.md"}
    records = []
    t_2m_11 = {"year": 2011, "month": 2, "period_type": "Monthly", "report_date": "2011-02-28"}
    
    data_structure = {
        "Bông các loại": [
            ["HOA KỲ", 37006, 110714], ["ẤN ĐỘ", 14760, 40909], ["BRAXIN", 1523, 4667],
            ["TRUNG QUỐC", 69, 410], ["HÀN QUỐC", 136, 316], ["ĐÀI LOAN", 36, 152],
            ["ITALIA", 79, 101], ["IN ĐÔ NÊ XI A", 40, 89]
        ],
        "Cao su": [
            ["CAMPUCHIA", 6382, 31658], ["HÀN QUỐC", 7501, 22328], ["THÁI LAN", 6417, 19242],
            ["NHẬT BẢN", 3907, 13484], ["ĐÀI LOAN", 4538, 11838], ["TRUNG QUỐC", 2522, 5291],
            ["HOA KỲ", 4166, 4593], ["NGA", 1001, 3756], ["PHÁP", 679, 2330], ["ITALIA", 576, 1459]
        ],
        "Dầu mỡ động thực vật": [
            ["MALAIXIA", None, 50742], ["IN ĐÔ NÊ XI A", None, 34294], ["ACHENTINA", None, 27426],
            ["CHI LÊ", None, 1832], ["HOA KỲ", None, 912], ["THÁI LAN", None, 868],
            ["HÀN QUỐC", None, 504], ["TRUNG QUỐC", None, 434], ["ẤN ĐỘ", None, 422], ["XINH GA PO", None, 350]
        ],
        "Lúa mì": [
            ["Ô X TRÂY LIA", 290723, 96576], ["HOA KỲ", 8155, 3352]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["LÀO", None, 26177], ["TRUNG QUỐC", None, 16080], ["HOA KỲ", None, 15217],
            ["MALAIXIA", None, 13198], ["THÁI LAN", None, 8318], ["NIU ZI LÂN", None, 6511],
            ["BRAXIN", None, 3969], ["CAMPUCHIA", None, 3950], ["MI AN MA", None, 3910], ["IN ĐÔ NÊ XI A", None, 2663]
        ],
        "Phân bón các loại": [
            ["TRUNG QUỐC", 216678, 67371], ["CA NA ĐA", 43091, 18842], ["PHI LIP PIN", 20620, 10759],
            ["NHẬT BẢN", 19963, 3983], ["ĐÀI LOAN", 12804, 2981], ["NAUY", 2976, 1517],
            ["BỈ", 2223, 1219], ["ẤN ĐỘ", 331, 1073], ["HOA KỲ", 1212, 823], ["THÁI LAN", 501, 240]
        ],
        "Sữa và sản phẩm sữa": [
            ["NIU ZI LÂN", None, 38135], ["HOA KỲ", None, 20690], ["HÀ LAN", None, 9817],
            ["BA LAN", None, 3579], ["Ô X TRÂY LIA", None, 2888], ["THÁI LAN", None, 2429],
            ["PHÁP", None, 2201], ["HÀN QUỐC", None, 2150], ["ĐỨC", None, 1837], ["ĐAN MẠCH", None, 1694]
        ],
        "Thức ăn gia súc và nguyên liệu": [
            ["ẤN ĐỘ", None, 168937], ["ACHENTINA", None, 74291], ["HOA KỲ", None, 35912],
            ["TRUNG QUỐC", None, 12946], ["THÁI LAN", None, 11480], ["IN ĐÔ NÊ XI A", None, 7927],
            ["CA NA ĐA", None, 7156], ["PHI LIP PIN", None, 5180], ["ĐÀI LOAN", 4118, 4118], ["Ô X TRÂY LIA", 4076, 4076] # Note: Table has typo/merged cells for Tai/Aus in rows 94. Assuming logical reading.
        ],
        "Thuốc trừ sâu và nguyên liệu": [
            ["TRUNG QUỐC", None, 31799], ["ẤN ĐỘ", None, 9383], ["THÁI LAN", None, 6923],
            ["XINH GA PO", None, 6513], ["ANH", None, 5698], ["NHẬT BẢN", None, 5434],
            ["THỤY SỸ", None, 3245], ["HOA KỲ", None, 2207], ["ĐỨC", None, 2192], ["HÀN QUỐC", None, 1967]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 21050], ["HOA KỲ", None, 7218], ["MI AN MA", None, 2354],
            ["THÁI LAN", None, 1950], ["Ô X TRÂY LIA", None, 922], ["MALAIXIA", None, 693],
            ["BRAXIN", None, 421], ["IN ĐÔ NÊ XI A", None, 50]
        ],
        "Hàng thuỷ sản": [
            ["ĐÀI LOAN", None, 5350], ["IN ĐÔ NÊ XI A", None, 4877], ["NHẬT BẢN", None, 4386],
            ["THÁI LAN", None, 3432], ["BA LAN", None, 3150], ["NAUY", None, 3145],
            ["TRUNG QUỐC", None, 2433], ["ẤN ĐỘ", None, 2120], ["ANH", None, 1204], ["CHI LÊ", None, 1146]
        ],
        "Muối": [
            ["TRUNG QUỐC", None, 1066], ["ẤN ĐỘ", None, 961], ["THÁI LAN", None, 137],
            ["Ô X TRÂY LIA", None, 46], ["NIU ZI LÂN", None, 27], ["ĐAN MẠCH", None, 13],
            ["ĐỨC", None, 9], ["NHẬT BẢN", None, 5], ["LÀO", None, 2], ["MỸ", None, 2]
        ]
    }
    
    for cmd, rows in data_structure.items():
        for r in rows:
            country = r[0]
            qty = r[1]
            val = r[2]
            
            if val is not None:
                records.append(create_record(metadata, t_2m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Import"}))
            if qty is not None:
                records.append(create_record(metadata, t_2m_11, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl12()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL12.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl13()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL13.json"))
    print("Successfully parsed PL12, PL13 for March 2011 (Detailed Trade Markets 2M 2011).")
