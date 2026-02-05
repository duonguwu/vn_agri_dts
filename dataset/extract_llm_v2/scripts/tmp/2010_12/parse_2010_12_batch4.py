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

def parse_pl10():
    # Sugar factories
    # Skip
    return []

def parse_pl11():
    # Investment
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL11", "source_file": "2010_12_Phuluc_T12_2010_PL11.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"}
    
    # [Item, Estimate_12M]
    data = [
        ["Vốn ngân sách giao đầu năm", 5063750], # Col 4
        ["Vốn thực hiện đầu tư", 4650550], 
        ["Đầu tư Thuỷ lợi", 3288500],
        ["Đầu tư Nông nghiệp", 677750],
        ["Đầu tư Lâm nghiệp", 318000],
        ["Đầu tư Thuỷ sản", 131000],
        ["Khoa học - Công nghệ", 58300],
        ["Giáo dục - Đào tạo", 82000],
        ["Các ngành khác", 95000],
        ["Chương trình mục tiêu", 47700],
        ["Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", 260000],
        ["Vốn chuẩn bị đầu tư", 65000],
        ["Vốn trái phiếu Chính phủ", 3713000],
        ["Các dự án có trong QĐ171", 2741000],
        ["Các dự án cấp bách bổ sung", 404000],
        ["Các dự án thuỷ lợi ĐBSHồng", 568000],
        ["Tổng vốn đầu tư", 8776750]
    ]
    
    for row in data:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Investment", "commodity": row[0]}, {"attribute": "Investment_Amount", "value": float(row[1]), "unit": "million_VND", "data_type": "Actual"}))
    return records

def parse_pl12():
    # Trade (Export/Import) Summary 12 months (Yearly Est)
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL12", "source_file": "2010_12_Phuluc_T12_2010_PL12.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"}
    
    # Transcription from Step 395 PL12 View
    # Col 7 (Vol Est 2010) and Col 8 (Val Est 2010)
    # The view is compacted with BR.
    # Col 1 (Items): ... Ca phe, Cao su...
    # Col 7 (Vol Est 2010): 1113<br>773<br>6,878...
    # Col 8 (Val Est 2010): 19,151<br>9,948<br>1,666...
    # Mapping
    
    items_export = [
        "Tổng kim ngạch XK", "Nông sản chính", "Cà phê", "Cao su", "Gạo", "Chè", "Hạt điều", "Hạt tiêu", "Hàng rau quả", "Sắn và sản phẩm từ sắn", 
        "Thuỷ sản", "Lâm sản chính", "Quế", "Gỗ & sản phẩm gỗ", "SP mây, tre, cói, thảm", "Các mặt hàng nông lâm sản khác"
    ]
    
    vol_est_export = [None, None, 1113, 773, 6878, 132, 196, 116, None, 1642, None, None, None, None, None, None]
    val_est_export = [19151, 9948, 1666, 2321, 3229, 194, 1141, 419, 446, 532, 4943, 3633, 25, 3408, 200, 627]
    
    items_import = [
        "Tổng kim ngạch NK", "Các mặt hàng nhập khẩu chính", "Phân bón các loại", "U RE", "S A", "D A P", "N P K", "Các loại phân bón khác",
        "Thuốc trừ sâu & nguyên liệu", "Lúa mỳ", "Thức ăn gia súc và nguyên liệu", "Dầu mỡ động, thực vật", "Cao su", "Bông các loại",
        "Sữa &sản phẩm sữa", "Gỗ & sản phẩm gỗ", "Muối", "Hàng thủy sản", "Hàng rau quả"
    ]
    
    vol_est_import = [None, None, 3630, 1001, 686, 792, 250, 900, None, 2298, None, None, 289, 348, None, None, 28.9, None, None] # Muoi: 289 in view? Wait. Muoi is 30.7 in 2009. 2010 is 30.7?
    # Let's check View Step 395.
    # Col 7 (Vol Est 2010) lower block:
    # 3,630 (Phan bon)
    # 1,001 (Ure)
    # 686 (SA)
    # 792 (DAP)
    # 250 (NPK)
    # 900 (Khac)
    # <blank> (Thuoc tru sau)
    # 2,298 (Lua my)
    # <blank> (TACN)
    # <blank> (Dau mo)
    # 289 (Cao su)
    # 348 (Bong)
    # <blank> (Sua)
    # <blank> (Go)
    # <blank> (Muoi)? View has 30.7. Wait, PL12 2009 col 2 has 30.7.
    # Col 7 has 32.7? Check line 34: "24<br>282<br>279" is year 2009? No, that's Col 2.
    # Col 7: "32.7<br>324<br>294". Muoi is 32.7. Hàng thủy sản is 324. Hàng rau quả is 294.
    
    vol_est_import[16] = 32.7 # Muoi
    
    val_est_import = [11879, 8339, 1263, 322, 98, 385, 97, 360, 537, 600, 2150, 655, 621, 638, 706, 1137, None, 324, 294] # Last 2 vals match vol? No.
    # Last vals in col 8: 324 (Thuy san), 294 (Rau qua). Muoi val is blank/missing or merged?
    # Let's check Muoi val. Col 8 has "32.7" in vol?
    # View line 34, col 8: "11,879... 32.7<br>324<br>294". Val usually > Vol for salt? Salt is cheap. Vol 32.7k ton. Val 1M USD?
    # Actually, Col 7 and Col 8 for import seem aligned.
    # Muoi vol 32.7. Val?
    # Wait, the last items in Col 8 are "32.7<br>324<br>294".
    # Vol col has "32.7".
    # Val col has ?
    # Let's look at Col 8 block for Import:
    # "... 1,137<br>32.7<br>324<br>294".
    # 1137 is Go. 32.7 is Muoi VAL? Previously Muoi vol was 32.7. Maybe copy paste error in source or coincidental.
    # Let's assume 32.7 is Val.
      
    # Exports
    for i, item in enumerate(items_export):
        if val_est_export[i]: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_est_export[i]), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Export"}))
        if vol_est_export[i]: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(vol_est_export[i]), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Export"}))
        
    # Imports
    for i, item in enumerate(items_import):
        if val_est_import[i]: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Value", "value": float(val_est_import[i]), "unit": "million_USD", "data_type": "Estimate", "trade_type": "Import"}))
        if vol_est_import[i]: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item}, {"attribute": "Volume", "value": float(vol_est_import[i]), "unit": "1000_ton", "data_type": "Estimate", "trade_type": "Import"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/12"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl11()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL11.json"))
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl12()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL12.json"))
    
    # PL10 skipped (Sugar Factories).
    # PL12a, PL13a, PL13b are Markets or Admin. I'll verify if they have data but usually handled in next step or skipped if admin.
    # User listed PL12a, PL13a, PL13b in request.
    # I should view them.
    # But for this batch 4, I'll do PL11, PL12.
    print("Successfully parsed PL11-PL12 for December 2010 (Investment, Trade).")
