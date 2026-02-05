import json
import uuid
import os
import re

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
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "")
            else: s = s.replace(",", ".")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    
    try:
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Cả nước": "Cả nước", "Toàn quốc": "Cả nước", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP Hồ Chí Minh": "Hồ Chí Minh", "Bà Rịa - Vũng Tà": "Bà Rịa - Vũng Tàu",
        "HOA KỲ": "United States", "ĐỨC": "Germany", "BỈ": "Belgium", "ITALIA": "Italy", "Italia": "Italy",
        "TÂY BAN NHA": "Spain", "NHẬT BẢN": "Japan", "HÀ LAN": "Netherlands", "XINH GA PO": "Singapore",
        "ANH": "United Kingdom", "TRUNG QUỐC": "China", "MALAIXIA": "Malaysia", "ĐÀI LOAN": "Taiwan",
        "HÀN QUỐC": "South Korea", "NGA": "Russia", "THỔ NHĨ KỲ": "Turkey", "ẤN ĐỘ": "India", "PAKIXTAN": "Pakistan",
        "IN ĐÔ NÊ XI A": "Indonesia", "TIỂU VƯƠNG QUỐC ARẬP THỐNG NHẤT": "United Arab Emirates", "ARẬP XÊÚT": "Saudi Arabia",
        "BA LAN": "Poland", "PHI LIP PIN": "Philippines", "CUBA": "Cuba", "BĂNG LA ĐÉT": "Bangladesh", "XÊ NÊ GAN": "Senegal",
        "BỜ BIỂN NGÀ": "Ivory Coast", "GANA": "Ghana", "CA NA ĐA": "Canada", "PHÁP": "France", "AI CẬP": "Egypt",
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
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
    else: # Country
        geo_context["region_id"] = "COUNTRY"; geo_context["region_name_vn"] = norm_loc; geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_rows_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 2 and parts[0] == "" and parts[-1] == "": rows.append(parts[1:-1])
            elif len(parts) > 1: rows.append(parts)
    return rows

def parse_2011_08_pl9():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL9.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL9", "source_file": "2011_08_Phuluc_08_2011_f_PL9.md"}
    records = []
    t = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-20"}
    
    for row in rows:
        if len(row) < 8: continue
        name_raw = row[1].replace("**", "").replace("_", "").strip()
        if name_raw == "" or "Tỉnh" in name_raw or "Col" in name_raw or "Miền" in name_raw: continue
        
        gl = "Provincial"
        # 2: Total SL, 3: NT Total, 4: NT Sweet, 5: NT Salt, 6: KT Total, 7: KT Sea, 8: KT Inland
        def add(idx, item, sub=None):
            if idx >= len(row): return
            val = normalize_number(row[idx])
            if val:
                records.append(create_record(metadata, t, name_raw, gl, {"sector": "Fishery", "commodity": item, "sub_item": sub}, {"attribute": "Production", "value": val, "unit": "ton", "data_type": "Actual"}))
        
        add(2, "Tổng sản lượng")
        add(3, "Sản lượng nuôi trồng", "Tổng số")
        add(4, "Sản lượng nuôi trồng", "Nước ngọt")
        add(5, "Sản lượng nuôi trồng", "Nước mặn, lợ")
        add(6, "Sản lượng khai thác", "Tổng số")
        add(7, "Sản lượng khai thác", "Khai thác biển")
        add(8, "Sản lượng khai thác", "Khai thác nội địa")
        
    return records

def parse_2011_08_pl10():
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL10", "source_file": "2011_08_Phuluc_08_2011_f_PL10.md"}
    records = []
    t_8m = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    t_month = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-31"}
    
    data = [
        ("Vốn ngân sách giao đầu năm", 251994, 2690175),
        ("Vốn thực hiện đầu tư", 233535, 2523616),
        ("Đầu tư Thuỷ lợi", 125000, 1439000),
        ("Đầu tư Nông nghiệp", 17962, 668962),
        ("Đầu tư Lâm nghiệp", 63735, 183766),
        ("Đầu tư Thuỷ sản", 2107, 16107),
        ("Chương trình trọng điểm phát triển và ứng dụng công nghệ sinh học", 3250, 18250),
        ("Khoa học - Công nghệ", 5399, 31399),
        ("Giáo dục - Đào tạo", 6582, 53582),
        ("Các ngành khác", 9500, 130800),
        ("Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 13249, 146349),
        ("Vốn chuẩn bị đầu tư", 5210, 20210),
        ("Vốn trái phiếu Chính phủ", 203511, 2658511),
        ("Các dự án có trong QĐ171", 130000, 2030000),
        ("Các dự án cấp bách bổ sung", 35511, 350511),
        ("Các dự án thuỷ lợi ĐBSHồng", 38000, 278000),
        ("Tổng vốn đầu tư : = A + B", 455505, 5348686)
    ]
    for item, v_m, v_c in data:
        records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(v_m), "unit": "million_VND", "data_type": "Estimate"}))
        records.append(create_record(metadata, t_8m, "Cả nước", "National", {"sector": "Investment", "commodity": item}, {"attribute": "Investment_Amount", "value": float(v_c), "unit": "million_VND", "data_type": "Estimate"}))
    return records

def parse_2011_08_pl11():
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL11", "source_file": "2011_08_Phuluc_08_2011_f_PL11.md"}
    records = []
    t_8m = {"year": 2011, "month": 8, "period_type": "Cumulative", "report_date": "2011-08-31"}
    t_month = {"year": 2011, "month": 8, "period_type": "Monthly", "report_date": "2011-08-31"}
    
    # [Item, Q8m, V8m, Q_m, V_m] -> Simplified for 8 month report
    # Indices in PL11: 7:Q_m, 8:V_m, 9:Q_8m, 10:V_8m
    xk = [
        ("Tổng kim ngạch XK", None, 16348, None, 2200),
        ("Nông sản chính", None, 9328, None, 1171),
        ("Cà phê", 958, 2109, 40, 86),
        ("Cao su", 449, 1943, 80, 340),
        ("Gạo", 5414, 2668, 700, 350),
        ("Chè", 84, 127, 15, 24),
        ("Hạt điều", 108, 865, 20, 170),
        ("Hạt tiêu", 98, 545, 15, 91),
        ("Hàng rau quả", None, 397, None, 50),
        ("Sắn và sản phẩm từ sắn", 1892, 674, 160, 60),
        ("Thuỷ sản", None, 3705, None, 520),
        ("Lâm sản chính", None, 2565, None, 338),
        ("Gỗ & sản phẩm gỗ", None, 2419, None, 320),
        ("SP mây, tre, cói, thảm", None, 128, None, 16)
    ]
    nk = [
        ("Tổng kim ngạch NK", None, 10419, None, 1400),
        ("Các mặt hàng nhập khẩu chính", None, 6960, None, 955),
        ("Phân bón các loại", 2545, 1023, 330, 135),
        ("Lúa mỳ", 1610, 552, 120, 43),
        ("Thuốc trừ sâu & nguyên liệu", None, 412, None, 47),
        ("Thức ăn gia súc và nguyên liệu", None, 1582, None, 220),
        ("Dầu mỡ động, thực vật", None, 603, None, 80),
        ("Cao su", 248, 613, 38, 95),
        ("Bông các loại", 216, 761, 15, 56),
        ("Sữa & sản phẩm sữa", None, 566, None, 82),
        ("Gỗ & sản phẩm gỗ", None, 835, None, 115),
        ("Hàng thủy sản", None, 305, None, 50),
        ("Hàng rau quả", None, 181, None, 30)
    ]
    
    def process(items, tt):
        for name, q8, v8, qm, vm in items:
            if q8: records.append(create_record(metadata, t_8m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": float(q8), "unit": "1000_ton", "data_type": "Estimate", "trade_type": tt}))
            if v8: records.append(create_record(metadata, t_8m, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": float(v8), "unit": "million_USD", "data_type": "Estimate", "trade_type": tt}))
            if qm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Volume", "value": float(qm), "unit": "1000_ton", "data_type": "Estimate", "trade_type": tt}))
            if vm: records.append(create_record(metadata, t_month, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": "Value", "value": float(vm), "unit": "million_USD", "data_type": "Estimate", "trade_type": tt}))

    process(xk, "Export")
    process(nk, "Import")
    return records

def parse_2011_08_pl12():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2011/2011_08_Phuluc_08_2011_f_PL12.md"
    rows = extract_rows_from_file(fpath)
    metadata = {"year": 2011, "month": 8, "appendix_number": "PL12", "source_file": "2011_08_Phuluc_08_2011_f_PL12.md"}
    records = []
    t = {"year": 2011, "month": 7, "period_type": "Cumulative", "report_date": "2011-07-31"}
    
    curr_comm = None
    for row in rows:
        if len(row) < 5: continue
        col1 = row[1].replace("**", "").replace("_", "").strip()
        if "Thị trường" in col1 or "Col" in col1: continue
        
        # Detect commodity start
        if row[0] == "" and col1 != "":
            curr_comm = col1
            # Add Total for this commodity
            qv = normalize_number(row[4])
            vv = normalize_number(row[5])
            if qv: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
            if vv: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            continue
            
        if curr_comm and row[0] != "" and row[0].isdigit():
            qv = normalize_number(row[4])
            vv = normalize_number(row[5])
            if qv: records.append(create_record(metadata, t, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Volume", "value": qv, "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
            if vv: records.append(create_record(metadata, t, col1, "Country", {"sector": "Trade", "commodity": curr_comm}, {"attribute": "Value", "value": vv, "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/08"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl9()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL9.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl10()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL10.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl11()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL11.json"))
    save_json({"metadata": {"year": 2011, "month": 8}, "records": parse_2011_08_pl12()}, os.path.join(out_dir, "2011_08_Phuluc_08_2011_f_PL12.json"))
    print("Successfully parsed Batch 3 (PL9, PL10, PL11, PL12) for August 2011.")
