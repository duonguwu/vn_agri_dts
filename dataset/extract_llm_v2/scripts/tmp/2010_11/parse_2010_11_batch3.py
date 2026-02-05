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
        "Cả nước": "Cả nước", "Tổng số": "Cả nước"
    }
    norm_loc = alias_map.get(loc_name.strip(), loc_name.strip())
    
    if norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl7():
    # Fishery
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL7", "source_file": "2010_11_Phuluc_T11_2010_PL7.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"}
    
    # [Item, 11M]
    data = [
        ["Tổng sản lượng", 4683],
        ["Sản lượng khai thác", 2195],
        ["Khai thác biển", 2068],
        ["Khai thác nội địa", 127],
        ["Sản lượng nuôi trồng", 2488]
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Fishery", "commodity": row[0]}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Actual"}))
    return records

def parse_pl8():
    # Investment
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL8", "source_file": "2010_11_Phuluc_T11_2010_PL8.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"}
    
    # [Item, Estimate_11M]
    data = [
        ["Vốn ngân sách giao đầu năm", 4538250],
        ["Vốn thực hiện đầu tư", 4212550],
        ["Đầu tư Thuỷ lợi", 3055500],
        ["Đầu tư Nông nghiệp", 562750],
        ["Đầu tư Lâm nghiệp", 256000],
        ["Đầu tư Thuỷ sản", 126500],
        ["Khoa học - Công nghệ", 51800],
        ["Giáo dục - Đào tạo", 80500],
        ["Các ngành khác", 79500],
        ["Chương trình mục tiêu", 44700],
        ["Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 241500],
        ["Vốn chuẩn bị đầu tư", 39500],
        ["Vốn trái phiếu Chính phủ", 3650000],
        ["Các dự án có trong QĐ171", 2685000],
        ["Các dự án cấp bách bổ sung", 420000],
        ["Các dự án thuỷ lợi ĐBSHồng", 545000],
        ["Tổng vốn đầu tư", 8188250]
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Actual"}))
    return records

def parse_pl9():
    # Trade
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL9", "source_file": "2010_11_Phuluc_T11_2010_PL9.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"}
    
    # [Item, Type, Qty_11M, Val_11M]
    data = [
        ["Tổng kim ngạch XK", "Export", None, 17225],
        ["Nông sản chính", "Export", None, 8824],
        ["Cà phê", "Export", 1033, 1520],
        ["Cao su", "Export", 672, 1919],
        ["Gạo", "Export", 6313, 2949],
        ["Chè", "Export", 125, 182],
        ["Hạt điều", "Export", 179, 1007],
        ["Hạt tiêu", "Export", 110, 390],
        ["Hàng rau quả", "Export", None, 401],
        ["Sắn và sản phẩm từ sắn", "Export", 1496, 456],
        ["Thuỷ sản", "Export", None, 4554],
        ["Lâm sản chính", "Export", None, 3233],
        ["Quế", "Export", None, 21],
        ["Gỗ & sản phẩm gỗ", "Export", None, 3027],
        ["SP mây, tre, cói, thảm", "Export", None, 185],
        ["Các mặt hàng nông lâm sản khác", "Export", None, 615],
        
        # Imports
        ["Tổng kim ngạch NK", "Import", None, 11575],
        ["Các mặt hàng nhập khẩu chính", "Import", None, 7313],
        ["Phân bón các loại", "Import", 2793, 917],
        ["U RE", "Import", 686, 205],
        ["S A", "Import", 563, 77],
        ["D A P", "Import", 513, 239],
        ["N P K", "Import", 207, 80],
        ["Các loại phân bón khác", "Import", 824, 317],
        ["Thuốc trừ sâu & nguyên liệu", "Import", None, 459],
        ["Lúa mỳ", "Import", 2247, 561],
        ["Thức ăn gia súc và nguyên liệu", "Import", None, 1937],
        ["Dầu mỡ động, thực vật", "Import", None, 603],
        ["Cao su", "Import", 262, 549],
        ["Bông các loại", "Import", 326, 589],
        ["Sữa &sản phẩm sữa", "Import", None, 631],
        ["Gỗ & sản phẩm gỗ", "Import", None, 1028],
        ["Muối", "Import", 38.4, None],
        ["Hàng thủy sản", "Import", None, 289],
        ["Hàng rau quả", "Import", None, 264]
    ]
    
    for row in data:
        item, trade_type, qty, val = row
        
        if val is not None:
             records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val), "unit": "million_USD", "data_type": "Actual", "trade_type": trade_type}))
        
        if qty is not None:
             records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(qty), "unit": "1000_ton", "data_type": "Actual", "trade_type": trade_type}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/11"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl7()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL7.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl8()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL8.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl9()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL9.json"))
    print("Successfully parsed PL7, PL8, PL9 for November 2010.")
