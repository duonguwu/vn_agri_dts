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
    
    # We leave Country names as is
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl10a():
    # Export Markets 10 months 2010
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL10a", "source_file": "2010_11_Phuluc_T11_2010_PL10a.md"}
    records = []
    t_10m = {"year": 2010, "month": 10, "period_type": "Cumulative", "report_date": "2010-10-31"} # Header: 10 thang nam 2010
    
    # Struct: [Country, Qty10, Val10]
    # Data manually transcribed from Step 344 PL10a View
    data_blocks = {
        "Cà phê": [
            ["ĐỨC", 130288, 192923], ["HOA KỲ", 118470, 185118], ["TÂY BAN NHA", 68894, 98375], ["ITALIA", 61025, 89035],
            ["NHẬT BẢN", 46918, 72755], ["BỈ", 38779, 56030], ["PHI LIP PIN", 27677, 39608], ["HÀN QUỐC", 23616, 34639],
            ["ANH", 23504, 33048], ["NGA", 23694, 32993]
        ],
        "Cao su": [
            ["TRUNG QUỐC", 349379, 976297], ["MALAIXIA", 39926, 109238], ["ĐÀI LOAN", 25578, 78260], ["HÀN QUỐC", 27330, 73143],
            ["ĐỨC", 21137, 65434], ["ẤN ĐỘ", 15747, 47994], ["HOA KỲ", 17922, 45600], ["NGA", 13670, 42567],
            ["THỔ NHĨ KỲ", 9256, 26128], ["NHẬT BẢN", 7953, 25941]
        ],
        "Chè": [
            ["PAKIXTAN", 20319, 36200], ["ĐÀI LOAN", 18226, 22110], ["NGA", 15924, 22017], ["TRUNG QUỐC", 11515, 13876],
            ["TVQ ARẬP THỐNG NHẤT", 2751, 5159], ["IN ĐÔ NÊ XI A", 4390, 4781], ["HOA KỲ", 3846, 4130],
            ["ĐỨC", 2733, 4105], ["ARẬP XÊÚT", 1932, 4014], ["ẤN ĐỘ", 2474, 3051]
        ],
        "Gạo": [
            ["PHI LIP PIN", 1471461, 944016], ["XINH GA PO", 501827, 207447], ["CUBA", 348750, 149240], ["MALAIXIA", 311774, 141987],
            ["ĐÀI LOAN", 326484, 128832], ["IN ĐÔ NÊ XI A", 172364, 89178], ["HỒNG CÔNG", 105807, 50125],
            ["TRUNG QUỐC", 105634, 43946], ["NGA", 77222, 33065], ["NAM PHI", 29023, 11945]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["HOA KỲ", None, 1144928], ["NHẬT BẢN", None, 349125], ["TRUNG QUỐC", None, 324713], ["ANH", None, 149238],
            ["HÀN QUỐC", None, 106778], ["ĐỨC", None, 88011], ["CA NA ĐA", None, 69606], ["Ô X TRÂY LIA", None, 65555],
            ["PHÁP", None, 55686], ["HÀ LAN", None, 52038]
        ],
        "Hành rau quả": [ # Typo in code or file? Code: "Hàng rau quả"
            ["TRUNG QUỐC", None, 52146], ["NHẬT BẢN", None, 29386], ["HÀ LAN", None, 25997], ["NGA", None, 22446],
            ["HOA KỲ", None, 20279], ["ĐÀI LOAN", None, 16660], ["IN ĐÔ NÊ XI A", None, 12532], ["XINH GA PO", None, 12344],
            ["HÀN QUỐC", None, 9147], ["THÁI LAN", None, 7520]
        ],
        "Hàng thuỷ sản": [
            ["HOA KỲ", None, 757595], ["NHẬT BẢN", None, 728899], ["HÀN QUỐC", None, 292609], ["ĐỨC", None, 166877],
            ["TÂY BAN NHA", None, 133006], ["Ô X TRÂY LIA", None, 123946], ["TRUNG QUỐC", None, 121666],
            ["ITALIA", None, 109883], ["HÀ LAN", None, 108396], ["PHÁP", None, 98328]
        ],
        "Hạt điều": [
            ["HOA KỲ", 50673, 295332], ["TRUNG QUỐC", 24846, 134025], ["HÀ LAN", 20898, 121439], ["Ô X TRÂY LIA", 12072, 70820],
            ["ANH", 6378, 37376], ["NGA", 5172, 28797], ["CA NA ĐA", 5137, 27158], ["THÁI LAN", 3124, 18686],
            ["ĐỨC", 2408, 15030], ["TVQ ARẬP THỐNG NHẤT", 1916, 11041]
        ],
        "Hạt tiêu": [
            ["HOA KỲ", 14747, 51198], ["ĐỨC", 12736, 47447], ["TVQ ARẬP THỐNG NHẤT", 10559, 35184], ["HÀ LAN", 7129, 26631],
            ["ẤN ĐỘ", 5865, 17353], ["PAKIXTAN", 3733, 11664], ["ANH", 2906, 11337], ["NGA", 3528, 11205],
            ["AI CẬP", 3207, 9751], ["BA LAN", 2667, 8508]
        ],
        "Sản phẩm mây, tre, cói và thảm": [
            ["HOA KỲ", None, 26507], ["NHẬT BẢN", None, 25551], ["ĐỨC", None, 22094], ["Ô X TRÂY LIA", None, 8259],
            ["PHÁP", None, 7829], ["HÀ LAN", None, 7055], ["ĐÀI LOAN", None, 6964], ["ANH", None, 5612],
            ["ITALIA", None, 5185], ["BỈ", None, 4974]
        ],
        "Sắn và các sản phẩm từ s": [ # "s" is likely "sắn" cut off
             ["TRUNG QUỐC", 1327594, 384843], ["ĐÀI LOAN", 19906, 9150], ["HÀN QUỐC", None, 7536], # Qty missing in table for Korea
             ["MALAIXIA", 11249, 5570], ["PHI LIP PIN", 13158, 5206], ["NHẬT BẢN", 5238, 1910], ["NGA", 331, 140]
        ]
    }
    
    for cmd, rows in data_blocks.items():
        cmd_clean = "Hàng rau quả" if cmd == "Hành rau quả" else cmd
        cmd_clean = "Sắn và các sản phẩm từ sắn" if cmd_clean.startswith("Sắn") else cmd_clean
        
        for r in rows:
            country = r[0]
            qty = float(r[1]) if r[1] is not None else None
            val = float(r[2]) if r[2] is not None else None
            
            if val is not None:
                records.append(create_record(metadata, t_10m, country, "Country", {"sector": "Trade", "commodity": cmd_clean}, {"attribute": "Value", "value": val, "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            if qty is not None:
                records.append(create_record(metadata, t_10m, country, "Country", {"sector": "Trade", "commodity": cmd_clean}, {"attribute": "Volume", "value": qty, "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
                
    return records

def parse_pl10b():
    # Import Markets 10 months 2010
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL10b", "source_file": "2010_11_Phuluc_T11_2010_PL10b.md"}
    records = []
    t_10m = {"year": 2010, "month": 10, "period_type": "Cumulative", "report_date": "2010-10-31"}
    
    # Transcription from Step 345
    data_blocks = {
        "Bông các loại": [
            ["HOA KỲ", 108041, 202903], ["ẤN ĐỘ", 52578, 88098], ["BRAXIN", 9676, 17127], ["THỤY SỸ", 1905, 3725],
            ["XINH GA PO", 1538, 3052], ["IN ĐÔ NÊ XI A", 2078, 2364], ["TRUNG QUỐC", 256, 1093], ["HÀN QUỐC", 443, 959],
            ["ITALIA", 615, 587], ["ĐÀI LOAN", 371, 565]
        ],
        "Cao su": [
            ["CAMPUCHIA", 28118, 83650], ["HÀN QUỐC", 37396, 81704], ["THÁI LAN", 31331, 69910], ["NHẬT BẢN", 19028, 55895],
            ["ĐÀI LOAN", 22517, 47585], ["TRUNG QUỐC", 17192, 36901], ["NGA", 6575, 19224], ["HOA KỲ", 17064, 15559],
            ["IN ĐÔ NÊ XI A", 4693, 10913], ["MALAIXIA", 8993, 9031]
        ],
        "Dầu mỡ động thực vật": [
            ["MALAIXIA", None, 252782], ["IN ĐÔ NÊ XI A", None, 133194], ["ACHENTINA", None, 42941], ["THÁI LAN", None, 29314],
            ["HOA KỲ", None, 27095], ["TRUNG QUỐC", None, 7236], ["ẤN ĐỘ", None, 3697], ["CHI LÊ", None, 2835], 
            ["HÀN QUỐC", None, 2622], ["Ô X TRÂY LIA", None, 1934]
        ],
        "Lúa mì": [
            ["Ô X TRÂY LIA", 1091864, 283208], ["BRAXIN", 236836, 55196], ["UCRAINA", 215090, 47369], ["HOA KỲ", 48302, 14936],
            ["NGA", 60766, 13732], ["CA NA ĐA", 3742, 1237]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["TRUNG QUỐC", None, 135992], ["LÀO", None, 122578], ["HOA KỲ", None, 121484], ["MALAIXIA", None, 96558],
            ["THÁI LAN", None, 73163], ["NIU ZI LÂN", None, 63547], ["CAMPUCHIA", None, 35340], ["BRAXIN", None, 27229],
            ["IN ĐÔ NÊ XI A", None, 15950], ["CHI LÊ", None, 15232]
        ],
        "Phân bón các loại": [
             ["TRUNG QUỐC", 1073987, 340183], ["NGA", 307576, 104867], ["CA NA ĐA", 133113, 55392], ["PHI LIP PIN", 129368, 45889],
             ["HÀN QUỐC", 106568, 32429], ["NHẬT BẢN", 155830, 21987], ["MALAIXIA", 55762, 16839], ["ĐÀI LOAN", 57069, 10247], # 57069 check
             ["NAUY", 20695, 8875], ["HOA KỲ", 12666, 8371]
        ],
        "Sữa và sản phẩm sữa": [
            ["NIU ZI LÂN", None, 129845], ["HOA KỲ", None, 121729], ["HÀ LAN", None, 81615], ["THÁI LAN", None, 32143],
            ["BA LAN", None, 22668], ["Ô X TRÂY LIA", None, 22311], ["PHÁP", None, 15324], ["ĐAN MẠCH", None, 11499],
            ["MALAIXIA", None, 11367], ["ĐỨC", None, 8505]
        ],
        "Thức ăn gia súc và nguyên liệu": [
            ["ACHENTINA", None, 452262], ["HOA KỲ", None, 325812], ["ẤN ĐỘ", None, 301208], ["TRUNG QUỐC", None, 76317],
            ["THÁI LAN", None, 73601], ["IN ĐÔ NÊ XI A", None, 42860], ["ITALIA", None, 33733], ["TVQ ARẬP THỐNG NHẤT", None, 32210],
            ["ĐÀI LOAN", None, 31126], ["CHI LÊ", None, 18296]
        ],
        "Thuốc trừ sâu và nguyên liệu": [
            ["TRUNG QUỐC", None, 170703], ["ẤN ĐỘ", None, 40383], ["THỤY SỸ", None, 24763], ["THÁI LAN", None, 23242],
            ["ĐỨC", None, 22674], ["ANH", None, 22101], ["HÀN QUỐC", None, 19604], ["XINH GA PO", None, 19001],
            ["NHẬT BẢN", None, 17043], ["IN ĐÔ NÊ XI A", None, 13703]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", None, 125774], ["THÁI LAN", None, 35921], ["HOA KỲ", None, 22601], ["Ô X TRÂY LIA", None, 10347],
            ["MALAIXIA", None, 2740], ["CHI LÊ", None, 2368], ["BRAXIN", None, 2304], ["IN ĐÔ NÊ XI A", None, 2090]
        ],
        "Hàng thuỷ sản": [
            ["ĐÀI LOAN", None, 39811], ["IN ĐÔ NÊ XI A", None, 24080], ["NHẬT BẢN", None, 21027], ["THÁI LAN", None, 13008],
            ["NAUY", None, 11909], ["HÀN QUỐC", None, 11725], ["BA LAN", None, 10772], ["CA NA ĐA", None, 10683],
            ["HOA KỲ", None, 10550], ["CHI LÊ", None, 10343]
        ],
        "Muối": [
            ["ẤN ĐỘ", None, 7605], ["TRUNG QUỐC", None, 3972], ["THÁI LAN", None, 1235], ["PAKIXTAN", None, 124],
            ["NIU ZI LÂN", None, 84], ["IXRAEN", None, 76], ["NHẬT BẢN", None, 64], ["SINGAPO", None, 56],
            ["MALAIXIA", None, 50], ["ĐAN MẠCH", None, 50]
        ]
    }
    
    for cmd, rows in data_blocks.items():
        for r in rows:
            country = r[0]
            val = float(r[2]) if r[2] is not None else None
            qty = float(r[1]) if r[1] is not None else None
            
            if val is not None:
                records.append(create_record(metadata, t_10m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": val, "unit": "1000_USD", "data_type": "Actual", "trade_type": "Import"}))
            if qty is not None:
                records.append(create_record(metadata, t_10m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": qty, "unit": "ton", "data_type": "Actual", "trade_type": "Import"}))
                
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/11"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl10a()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL10a.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl10b()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL10b.json"))
    
    print("Successfully parsed PL10a, PL10b for November 2010.")
