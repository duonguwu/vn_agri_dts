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

def parse_pl12a():
    # Export Markets 11 months 2010
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL12a", "source_file": "2010_12_Phuluc_T12_2010_PL12a.md"}
    records = []
    t_11m = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"} # Header says PL12a is 11 months 2010
    
    # Data blocks transcribed from Step 403. Be careful with <br> split.
    
    data_structure = {
        "Cà phê": [
            ["HOA KỲ", 133571, 212694], ["ĐỨC", 138299, 208110], ["TÂY BAN NHA", 73121, 105511],
            ["ITALIA", 64145, 94409], ["NHẬT BẢN", 49778, 78084], ["BỈ", 46578, 68841],
            ["HÀN QUỐC", 28531, 42582], ["PHI LIP PIN", 28349, 40720], ["ANH", 24753, 35337], ["NGA", 25024, 35103]
        ],
        "Cao su": [
            ["TRUNG QUỐC", 405645, 1183633], ["MALAIXIA", 46064, 131259], ["ĐÀI LOAN", 28484, 89061],
            ["HÀN QUỐC", 30877, 84575], ["ĐỨC", 25257, 79927], ["ẤN ĐỘ", 19702, 63489],
            ["HOA KỲ", 20751, 54403], ["NGA", 14863, 47115], ["THỔ NHĨ KỲ", 10589, 30141], ["NHẬT BẢN", 9036, 29935]
        ],
        "Chè": [
            ["PAKIXTAN", 23217, 41034], ["ĐÀI LOAN", 19855, 24216], ["NGA", 16960, 23578],
            ["TRUNG QUỐC", 12884, 15483], ["TVQ ARẬP THỐNG NHẤT", 3076, 5818], ["IN ĐÔ NÊ XI A", 4747, 5243],
            ["ARẬP XÊÚT", 2482, 5095], ["ĐỨC", 2970, 4550], ["HOA KỲ", 4094, 4389], ["ẤN ĐỘ", 2538, 3158]
        ],
        "Gạo": [
            ["PHI LIP PIN", 1472471, 944774], ["XINH GA PO", 526442, 219908], ["IN ĐÔ NÊ XI A", 420213, 209305],
            ["CUBA", 426550, 183624], ["MALAIXIA", 355747, 159578], ["ĐÀI LOAN", 347786, 139549],
            ["HỒNG CÔNG", 121151, 58874], ["TRUNG QUỐC", 110584, 46632], ["NGA", 77472, 33187], ["NAM PHI", 30273, 12574]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["HOA KỲ", 1266776, None], ["NHẬT BẢN", 405645, None], ["TRUNG QUỐC", 369756, None],
            ["ANH", 168264, None], ["HÀN QUỐC", 124237, None], ["ĐỨC", 99913, None], ["CA NA ĐA", 77673, None],
            ["ÔXTRÂYLIA", 74756, None], ["PHÁP", 65632, None], ["HÀ LAN", 58121, None]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", 62357, None], ["NHẬT BẢN", 32391, None], ["HÀ LAN", 28387, None],
            ["NGA", 24574, None], ["HOA KỲ", 23222, None], ["ĐÀI LOAN", 18118, None],
            ["IN ĐÔ NÊ XI A", 13138, None], ["XINH GA PO", 13041, None], ["HÀN QUỐC", 10144, None], ["THÁI LAN", 9030, None]
        ],
        "Hàng thuỷ sản": [
            ["HOA KỲ", 863827, None], ["NHẬT BẢN", 806660, None], ["HÀN QUỐC", 336632, None],
            ["ĐỨC", 185960, None], ["TÂY BAN NHA", 149334, None], ["TRUNG QUỐC", 140236, None],
            ["ÔXTRÂYLIA", 138305, None], ["ITALIA", 122903, None], ["HÀ LAN", 118401, None], ["PHÁP", 110173, None]
        ],
        "Hạt điều": [
            ["HOA KỲ", 55794, 329573], ["TRUNG QUỐC", 29265, 163617], ["HÀ LAN", 22562, 132288],
            ["ÔXTRÂYLIA", 13072, 77596], ["ANH", 6882, 40328], ["CA NA ĐA", 5104, 32369],
            ["NGA", 5681, 32130], ["THÁI LAN", 3516, 21089], ["ĐỨC", 2520, 15756], ["TVQ ARẬP THỐNG NHẤT", 2439, 14895]
        ],
        "Hạt tiêu": [
            ["HOA KỲ", 15384, 54342], ["ĐỨC", 13693, 52594], ["TVQ ARẬP THỐNG NHẤT", 12393, 42926],
            ["HÀ LAN", 7782, 30080], ["ẤN ĐỘ", 5882, 17475], ["ANH", 3125, 12326],
            ["PAKIXTAN", 3801, 11984], ["NGA", 3656, 11761], ["AI CẬP", 3249, 9954], ["BA LAN", 2843, 9363]
        ],
        "Sản phẩm mây, tre, cói và thảm": [
            ["HOA KỲ", 29846, None], ["NHẬT BẢN", 26939, None], ["ĐỨC", 24393, None],
            ["ÔXTRÂYLIA", 8953, None], ["PHÁP", 8717, None], ["ĐÀI LOAN", 7599, None],
            ["HÀ LAN", 7514, None], ["ANH", 6079, None], ["ITALIA", 5727, None], ["Bỉ", 5443, None]
        ],
        "Sắn và các sản phẩm từ sắn": [
            ["TRUNG QUỐC", 1438584, 442357], ["ĐÀI LOAN", 21407, 9938], ["HÀN QUỐC", 35385, 8167],
            ["MALAIXIA", 11266, 5576], ["PHI LIP PIN", 13158, 5206], ["NHẬT BẢN", 5358, 1936], ["NGA", 1707, 1007]
        ]
    }
    
    # Note: Value/Qty swap check.
    # In PL12a Step 403:
    # Col 5 (Qty 11m 2010), Col 6 (Val 11m 2010).
    # For Go & San Pham Go:
    # Col 5 is Val? Because unit matches text.
    # NO. Look at Caphe: Col 5 (133571) < Col 6 (212694). Volume > Value? No, Coffee ~ 2000 USD/ton. 133k ton * 2k = 266M USD.
    # Wait. Unit: Lượng = tấn; Giá trị = 1.000 USD.
    # 133,571 ton. 212,694 (1000 USD) = 212 Million USD.
    # Price = 212M / 133k = 1.6 USD/kg = 1600 USD/ton. Correct for 2010 coffee prices.
    # So Col 5 is Qty, Col 6 is Value.
    
    # For Go & San Pham Go:
    # Items: HOAKY, 1266776. Is this Qty or Value?
    # Col 5 is empty "||". Col 6 is "1266776".
    # So Value only. OK.
    # In my `data_structure` above, I put Value in index 1 for `Go`, others have [Qty, Val].
    # Wait, check my tuples in `data_structure`.
    # "Gỗ & sản phẩm gỗ": [ ["HOA KỲ", 1266776, None], ... ] -> I put Value in index 1 (Qty pos).
    # Correct logic should be: if only 1 number, it's Value (Col 6). But my structure is generic.
    # Let me fix the loop logic below or the structure.
    # For "Gỗ", "Hàng rau quả", "Hàng thủy sản", "Sản phẩm mây tre": The single number is Value.
    # So for those, I should shift it to Val position.
    
    val_only_commodities = ["Gỗ & sản phẩm gỗ", "Hàng rau quả", "Hàng thuỷ sản", "Sản phẩm mây, tre, cói và thảm"]
    
    for cmd, rows in data_structure.items():
        is_val_only = cmd in val_only_commodities
        for r in rows:
            country = r[0]
            if is_val_only:
                val = r[1]; qty = None
            else:
                qty = r[1]; val = r[2]
            
            if val is not None:
                records.append(create_record(metadata, t_11m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Export"}))
            if qty is not None:
                records.append(create_record(metadata, t_11m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Export"}))
                
    return records

def parse_pl13b():
    # Import Markets 11 months 2010
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL13b", "source_file": "2010_12_Phuluc_T12_2010_PL13b.md"}
    records = []
    t_11m = {"year": 2010, "month": 11, "period_type": "Cumulative", "report_date": "2010-11-30"}
    
    # Transcribed from Step 405
    data_structure = {
        "Bông các loại": [
            ["HOA KỲ", 114232, 219954], ["ẤN ĐỘ", 54532, 92465], ["BRAXIN", 13446, 23592],
            ["THỤY SỸ", 1905, 3725], ["XINH GA PO", 1538, 3052], ["IN ĐÔ NÊ XI A", 2086, 2402],
            ["TRUNG QUỐC", 275, 1167], ["HÀN QUỐC", 485, 1018], ["ANH", 299, 590], ["ITALIA", 615, 587]
        ],
        "Cao su": [
            ["CAMPUCHIA", 32453, 100540], ["HÀN QUỐC", 42724, 93901], ["THÁI LAN", 34785, 79466],
            ["NHẬT BẢN", 21265, 62861], ["ĐÀI LOAN", 25008, 52944], ["TRUNG QUỐC", 18336, 39101],
            ["NGA", 7265, 22185], ["HOA KỲ", 19887, 17884], ["IN ĐÔ NÊ XI A", 4744, 10918], ["PHÁP", 3000, 10042]
        ],
        "Dầu mỡ động thực vật": [
            ["MALAIXIA", 287811, 149.45], # Wait, 287811 is Qty? Col 5 (Line 17 View 405)
            # Line 17: "287811<br>150606<br>..."
            # Wait, line 16 Header "Dầu mỡ động thực vật" Val Col 6 is "595095". Col 5 is "451492" (Qty?)
            # Wait, line 16 has Col 4 "451492" (Value 11m 2009?).
            # Col 5 (Qty 11m 2010) is BLANK "||".
            # Col 6 (Val 11m 2010) is "595095".
            # Recheck:
            # "||**Dầu mỡ động thực vật**|**Dầu mỡ động thực vật**|**451492**||**595095**..."
            # 451492 is in Col 4 (Val 2009).
            # Col 5 is empty. Col 6 is 595095.
            # So no Qty for this Category?
            # But line 17 has "287811<br>150606..." in Col 6 (Val).
            # Col 5 is blank "||".
            # So only Value for Oils.
            ["MALAIXIA", None, 287811], ["IN ĐÔ NÊ XI A", None, 150606], ["ACHENTINA", None, 46182],
            ["HOA KỲ", None, 39873], ["THÁI LAN", None, 34228], ["TRUNG QUỐC", None, 7333],
            ["ẤN ĐỘ", None, 3905], ["CHI LÊ", None, 3439], ["HÀN QUỐC", None, 3267], ["Ô X TRÂY LIA", None, 2232]
        ],
        "Lúa mì": [
            ["Ô X TRÂY LIA", 1262560, 342044], ["BRAXIN", 236836, 55196], ["UCRAINA", 249658, 55195],
            ["HOA KỲ", 49497, 15370], ["NGA", 60766, 13732], ["CA NA ĐA", 3742, 1237], ["TRUNG QUỐC", 515, 185]
        ],
        "Gỗ & sản phẩm gỗ": [
            ["TRUNG QUỐC", 152531, None], ["LÀO", 137923, None], ["HOA KỲ", 135988, None],
            ["MALAIXIA", 103156, None], ["THÁI LAN", 78947, None], ["NIU ZI LÂN", 69905, None],
            ["BRAXIN", 30195, None], ["IN ĐÔ NÊ XI A", 17932, None], ["CHI LÊ", 17760, None], ["PHẦN LAN", 12543, None]
        ],
        "Phân bón các loại": [
            ["TRUNG QUỐC", 1420398, 483683], ["NGA", 308260, 105118], ["CA NA ĐA", 155899, 65200],
            ["PHI LIP PIN", 159700, 57659], ["HÀN QUỐC", 112868, 35694], ["NHẬT BẢN", 183794, 27070],
            ["MALAIXIA", 67188, 20920], ["ĐÀI LOAN", 64011, 11670], ["NAUY", 23047, 9751], ["HOA KỲ", 12811, 8774]
        ],
        "Sữa và sản phẩm sữa": [
            ["NIU ZI LÂN", 151880, None], ["HOA KỲ", 132728, None], ["HÀ LAN", 86322, None],
            ["THÁI LAN", 34382, None], ["BA LAN", 24623, None], ["Ô X TRÂY LIA", 24117, None],
            ["PHÁP", 16818, None], ["ĐAN MẠCH", 12443, None], ["MALAIXIA", 11633, None], ["ĐỨC", 9177, None]
        ],
        "Thức ăn gia súc và nguyên liệu": [
            ["ACHENTINA", 473914, None], ["ẤN ĐỘ", 361981, None], ["HOA KỲ", 337876, None],
            ["MALAIXIA", 287811, None], ["TRUNG QUỐC", 84919, None], ["THÁI LAN", 79230, None],
            ["IN ĐÔ NÊ XI A", 46963, None], ["ITALIA", 36604, None], ["ĐÀI LOAN", 34008, None], ["TVQ ARẬP THỐNG NHẤT", 33777, None]
        ],
        "Thuốc trừ sâu và nguyên liệu": [
            ["TRUNG QUỐC", 199444, None], ["ẤN ĐỘ", 44271, None], ["THÁI LAN", 29363, None],
            ["ĐỨC", 25739, None], ["THỤY SỸ", 25726, None], ["ANH", 25371, None],
            ["XINH GA PO", 22489, None], ["HÀN QUỐC", 22164, None], ["NHẬT BẢN", 19225, None], ["IN ĐÔ NÊ XI A", 16400, None]
        ],
        "Hàng rau quả": [
            ["TRUNG QUỐC", 141529, None], ["THÁI LAN", 39629, None], ["HOA KỲ", 27211, None],
            ["Ô X TRÂY LIA", 10861, None], ["MALAIXIA", 3613, None], ["BRAXIN", 2495, None],
            ["CHI LÊ", 2388, None], ["IN ĐÔ NÊ XI A", 2140, None]
        ],
        "Hàng thuỷ sản": [
            ["ĐÀI LOAN", 43865, None], ["IN ĐÔ NÊ XI A", 26069, None], ["NHẬT BẢN", 23170, None],
            ["THÁI LAN", 14493, None], ["NAUY", 14311, None], ["CA NA ĐA", 12938, None],
            ["HÀN QUỐC", 12623, None], ["HOA KỲ", 12552, None], ["CHI LÊ", 11840, None], ["BA LAN", 11738, None]
        ],
        "Muối": [
            ["ẤN ĐỘ", 17162, None], ["TRUNG QUỐC", 9349, None], ["THÁI LAN", 2810, None],
            ["PA KIX TAN", 272, None], ["NIU ZI LÂN", 175, None], ["IXRAEN", 157, None],
            ["NHẬT BẢN", 153, None], ["XINH GA PO", 113, None], ["MALAIXIA", 107, None], ["ĐAN MẠCH", 106, None]
        ]
    }
    
    # Value swapping for imports too
    val_only_commodities = [
        "Dầu mỡ động thực vật", "Gỗ & sản phẩm gỗ", "Sữa và sản phẩm sữa", "Thức ăn gia súc và nguyên liệu",
        "Thuốc trừ sâu và nguyên liệu", "Hàng rau quả", "Hàng thuỷ sản", "Muối"
    ]
    # Check Muoi again.
    # In Step 405 Line 46: Muoi Qty 11m 09 is empty. Val 11m 09 is 13298? No, col 4 is 23528.
    # PL13b Line 46:
    # Col 3 (Qty 09) empty. Col 4 (Val 09) 23528.
    # Col 5 (Qty 10) empty. Col 6 (Val 10) 30677.
    # So Muoi is VALUE ONLY in PL13b.
    # My transcription `val_only_commodities` includes "Muoi".
    # Check "Dầu mỡ": Col 5 empty. Col 6 595095. Value only.
    
    for cmd, rows in data_structure.items():
        is_val_only = cmd in val_only_commodities
        for r in rows:
            country = r[0]
            if is_val_only:
                val = r[1]; qty = None
            else:
                qty = r[1]; val = r[2]
            
            if val is not None:
                records.append(create_record(metadata, t_11m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual", "trade_type": "Import"}))
            if qty is not None:
                records.append(create_record(metadata, t_11m, country, "Country", {"sector": "Trade", "commodity": cmd}, {"attribute": "Volume", "value": float(qty), "unit": "ton", "data_type": "Actual", "trade_type": "Import"}))
                
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/12"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl12a()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL12a.json"))
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl13b()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL13b.json"))
    print("Successfully parsed PL12a, PL13b for December 2010 (Trade Markets 11 months).")
