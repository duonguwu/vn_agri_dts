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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "Trung du và MN phía Bắc": "Đông Bắc",
        "TD và MN phía Bắc": "Đông Bắc", "TD và MN phía\nBắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trung\nBộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung B": "Duyên hải Nam Trung Bộ", "d.h nam trg b": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Miền Tr- TN": "Duyên hải Nam Trung Bộ"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.replace("\n", "").strip()
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
    elif norm_loc == "Miền Nam":
        geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    elif norm_loc == "Miền Bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6():
    # Fishery Production Jan 2011 + Jan 2010 + 2010 Total
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL6", "source_file": "2011_01_Phuluc_01_2011_PL6.md"}
    records = []
    
    # Step 461 View:
    # 2010 Total (Col 1), Jan 2010 (Col 3), Jan 2011 (Col 6? No, View has "Ước thực hiện tháng 01/2011". Column order 5?)
    # Header row 18: |1|3|6|5|...
    # Row 16: |TT|CHỈ TIÊU|Thực hiện cả năm 2010|Thực hiện tháng 01/2010|Ước thực hiện tháng 01/2011|% so cùng kỳ|
    # Values:
    # Tong san luong: 5184.6 | 430 | 435 | 101.2
    # Khai thac: 2477.8 | 230 | 230 | 100.0
    # Bien: 2340.8 | 220 | 220 | 100.0
    # Noi dia: 137 | 10 | 10 | 100.0
    # Nuoi trong: 2706.8 | 200 | 205 | 102.5
    
    # We should extract Jan 2011 Estimate and Jan 2010 Actual.
    # Also 2010 Total? Maybe. But focusing on Monthly report.
    
    data = [
        ("Tổng sản lượng", 430, 435, 101.2),
        ("Sản lượng khai thác", 230, 230, 100.0),
        ("Khai thác biển", 220, 220, 100.0),
        ("Khai thác nội địa", 10, 10, 100.0),
        ("Sản lượng nuôi trồng", 200, 205, 102.5)
    ]
    
    # Time context
    t_jan_11 = {"year": 2011, "month": 1, "period_type": "Monthly", "report_date": "2011-01-31"}
    t_jan_10 = {"year": 2010, "month": 1, "period_type": "Monthly", "report_date": "2010-01-31"}
    
    for row in data:
        item = row[0]
        val_10 = row[1]
        val_11 = row[2]
        yoy = row[3]
        
        # Jan 2011
        records.append(create_record(metadata, t_jan_11, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(val_11), "unit": "1000_ton", "data_type": "Estimate"}, {"comparison_type": "YoY", "comparison_value": float(yoy)}))
        
        # Jan 2010
        records.append(create_record({"year": 2010, "month": 1, "appendix_number": "PL6", "source_file": "2011_01_Phuluc_01_2011_PL6.md"}, t_jan_10, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(val_10), "unit": "1000_ton", "data_type": "Actual"}))

    return records

def parse_pl7():
    # Sugar Factories Production
    # This is "Nhà máy đường". Previous months I skipped because schema mismatch.
    # But user might want it? "TỔNG HỢP TÌNH HÌNH SẢN XUẤT, TIÊU THỤ CỦA NHÀ MÁY ĐƯỜNG"
    # Columns: Mía (Cane) and Đường (Sugar).
    # Units usually Ton.
    # Let's extract this time since it's cleaner.
    # Structure: Factory Name, Period 1 (To Dec 15), Period 2 (Dec 15 - Jan 15), Period 3 (Cumulative to Jan 15).
    # We prioritize "Cumulative to Jan 15" (Lũy kế đến 15/1/11).
    # Step 462, Col 8 (Mia Luy ke), Col 9 (Duong Luy ke) (Actually headers span 2 cols).
    # Row 11: |Col6|Luỹ kế đến 15/1/11|Col8|
    # Row 12: |_Mía_|_Đường_|
    # So "Luỹ kế" block has [Mía, Đường].
    
    metadata = {"year": 2011, "month": 1, "appendix_number": "PL7", "source_file": "2011_01_Phuluc_01_2011_PL7.md"}
    records = []
    t = {"year": 2011, "month": 1, "period_type": "Cumulative", "report_date": "2011-01-15"}
    
    # Factory list
    factories = [
        "Sơn Dương", "Cao Bằng", "Sơn La", "Hoà Bình", "Lam Sơn", "Việt - Đài", "Nông Cống", 
        "N.An-Tate&Lyle", "Sông Lam", "Sông Con", "Phổ Phong", "An Khê", "Bình Định", 
        "KCP Phú Yên", "Tuy Hoà", "Ninh Hoà", "Khánh Hoà", "Gia Lai", "Kon Tum", 
        "333 Đắc Lắc", "Đắc Nông", "Phan Rang", "Sugar VN", "Biên Hoà Trị An", "La Ngà", 
        "Hiệp Hoà", "Biên Hòa TN", "Bourbon TN", "NIVL", "Nước Trong", "Sóc Trăng", 
        "Kiên Giang", "Bến Tre", "Phụng Hiệp", "Vị Thanh", "Long Mỹ Phát", "Cà Mau", "Trà Vinh"
    ]
    # Data extraction logic (manual transcription for key factories or full list?)
    # Since list is long, I will extract based on text parsing logic if I read file content. But here I write based on View.
    # I already have factory names and values in view.
    # Let's verify Mien Bac block.
    # Son Duong: Mia 97,000, Duong 9,000.
    # Cao Bang: Mia 40,000, Duong 4,000.
    # ...
    # This is factory level data. "Non-standard" location.
    # Schema says "Location Name". Can be "Nhà máy Sơn Dương"?
    # Geo Level "Factory"? No standard geo level.
    # "Provincial"? Factories are in provinces but name is factory.
    # "Other"?
    # I will SKIP PL7 again to maintain schema consistency with geo-locations. Processing factories requires a "Factory" entity which complicates downstream aggregation.
    # Unless user specifically asked for "Sugar Factories".
    return []

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/01"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 1}, "records": parse_pl6()}, os.path.join(out_dir, "2011_01_Phuluc_01_2011_PL6.json"))
    # PL7 Skipped
    print("Successfully parsed PL6 for January 2011 (Fishery). PL7 (Sugar Factories) skipped.")
