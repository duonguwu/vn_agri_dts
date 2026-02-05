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
    norm_loc = loc_name.strip()
    geo_context["region_id"] = "NATIONAL" 
    geo_context["region_name_vn"] = "Cả nước"
    if geo_level == "Country":
         geo_context["region_id"] = "GLOBAL"
         geo_context["region_name_vn"] = norm_loc
         geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl7():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL7", "source_file": "2010_07_phuluc_07_2010_PL7.md"}
    records = []
    t = {"year": 2010, "month": 7, "period_type": "Cumulative", "report_date": "2010-07-31"}
    
    # [Item, Vol, Val] (7 months)
    exports = [
        ["Tổng kim ngạch XK", None, 10129],
        ["Nông sản chính", None, 5354],
        ["Cà phê", 754, 1061],
        ["Cao su", 299, 821],
        ["Gạo", 4007, 1970],
        ["Chè", 65, 91],
        ["Hạt điều", 100, 531],
        ["Hạt tiêu", 87, 274],
        ["Hàng rau quả", None, 262],
        ["Sắn và sản phẩm từ sắn", 1274, 342],
        ["Thuỷ sản", None, 2452],
        ["Lâm sản chính", None, 1912],
        ["Quế", 12, None], # Vol line 28: |Quế|...||12|
        ["Gỗ & sản phẩm gỗ", None, 1782],
        ["SP mây, tre, cói, thảm", None, 118]
    ]
    
    imports = [
        ["Tổng kim ngạch NK", None, 7525],
        ["Phân bón các loại", 1531, 478],
        ["Ure", 378, 114],
        ["SA", 390, 53],
        ["DAP", 202, 88],
        ["NPK", 132, 50],
        ["Phân bón khác", 429, 173],
        ["Thuốc trừ sâu & nguyên liệu", None, 314],
        ["Lúa mỳ", 1442, 350],
        ["Thức ăn gia súc và nguyên liệu", None, 1383],
        ["Dầu mỡ động, thực vật", None, 327],
        ["Cao su", 162, 335],
        ["Bông các loại", 217, 364],
        ["Sữa &sản phẩm sữa", None, 427],
        ["Gỗ & sản phẩm gỗ", None, 605],
        ["Muối", 12.2, None],
        ["Hàng thủy sản", None, 180],
        ["Hàng rau quả", None, 149]
    ]

    for item, vol, val in exports:
        if vol: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Xuất khẩu"}, {"attribute": "Export_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))
        if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Xuất khẩu"}, {"attribute": "Export_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))
        
    for item, vol, val in imports:
        if vol: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Nhập khẩu"}, {"attribute": "Import_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))
        if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Nhập khẩu"}, {"attribute": "Import_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))

    return records

def parse_pl8a():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL8a", "source_file": "2010_07_phuluc_07_2010_PL8a.md"}
    records = []
    # 6 months (Title says 6 months nam 2010 but this is July appendix)
    # Usually PL8a in July contains June data (6 months).
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    # [Item, [[Country, Vol, Val]...]]
    # Only "San pham may tre coi tham" and "San va SP tu san" and "Ai Cap/Anh/TayBanNha" fragment found in PL8a.
    # The file seems truncated or only contains end of list. 
    # Ah, PL8a starts with "Ai Cap" line 13. Where is 1-7?
    # It seems the file provided `PL8a.md` is incomplete or split?
    # I will extract whatever is there.
    
    # Fragment Ai Cap, Anh, Tay Ban Nha -> likely for "Hat Tieu" or something? 
    # Previous line 113 in June PL9a ended with Hat Tieu.
    # Let's assume these are leftovers from a previous table, likely 'Hạt tiêu' or 'Cà phê'?
    # Given countries (Ai Cap, Anh, Tay Ban Nha), likely Pepper (Hạt tiêu).
    # June PL9a Hạt tiêu: Ai Cập, Anh, TBN were bottom of list.
    # So I'll assign these to "Hạt tiêu".
    
    records.extend(process_market_data(metadata, t, "Hạt tiêu", [
        ["Ai Cập", 2586, 7329], ["Anh", 1837, 6333], ["Tây Ban Nha", 1445, 5055]
    ], "Export"))
    
    # May tre coi
    records.extend(process_market_data(metadata, t, "Sản phẩm mây, tre, cói và thảm", [
        ["Nhật Bản", None, 16204], ["Hoa Kỳ", None, 14611], ["Đức", None, 13625],
        ["Pháp", None, 5017], ["Ôxtrâylia", None, 4439], ["Hà Lan", None, 4346],
        ["Đài Loan", None, 4086], ["Italia", None, 3152], ["Tây Ban Nha", None, 3059], ["Bỉ", None, 2954]
    ], "Export"))
    
    # San (Vol + Val)
    records.extend(process_market_data(metadata, t, "Sắn và các SP từ sắn", [
        ["Trung Quốc", 1081029, 287925], ["Hàn Quốc", 27985, 6310], ["Đài Loan", 9825, 3936],
        ["Philippin", 8222, 2471], ["Malaixia", 3759, 1680], ["Nhật Bản", 3571, 1235], ["Nga", 236, 87]
    ], "Export"))

    return records

def parse_pl8b():
    metadata = {"year": 2010, "month": 7, "appendix_number": "PL8b", "source_file": "2010_07_phuluc_07_2010_PL8b.md"}
    records = []
    # 6 months
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    # Bong
    records.extend(process_market_data(metadata, t, "Bông các loại", [
        ["Hoa Kỳ", 61995, 106290], ["Ấn Độ", 46705, 76852], ["Braxin", 5535, 9568],
        ["Thụy Sỹ", 882, 1589], ["Xinh Ga Po", 711, 1281], ["Trung Quốc", 151, 791],
        ["Inđônêxia", 471, 629], ["Hàn Quốc", 233, 534], ["Italia", 331, 300], ["Đài Loan", 128, 180]
    ], "Import"))
    
    # Cao su
    records.extend(process_market_data(metadata, t, "Cao su", [
        ["Hàn Quốc", 22475, 47520], ["Thái Lan", 21753, 47365], ["Campuchia", 13949, 40338],
        ["Nhật Bản", 11917, 33569], ["Đài Loan", 11675, 24367], ["Trung Quốc", 9383, 20340],
        ["Nga", 4212, 11493], ["Hoa Kỳ", 10685, 9912], ["Inđônêxia", 3876, 9511], ["Malaixia", 4691, 7020]
    ], "Import"))

    # Dau mo (Value)
    records.extend(process_market_data(metadata, t, "Dầu mỡ động thực vật", [
        ["Malaixia", None, 132941], ["Inđônêxia", None, 81448], ["Hoa Kỳ", None, 25957],
        ["Thái Lan", None, 8560], ["Achentina", None, 7107], ["Trung Quốc", None, 4558],
        ["Ấn Độ", None, 2139], ["Hàn Quốc", None, 1336], ["Chilê", None, 1248], ["Ôxtrâylia", None, 1122]
    ], "Import"))
    
    # Lua mi
    records.extend(process_market_data(metadata, t, "Lúa mì", [
        ["Ôxtrâylia", 688553, 173027], ["Braxin", 236836, 55196], ["Ucraina", 129554, 29343],
        ["Nga", 48785, 11167], ["Hoa Kỳ", 17489, 4914], ["Canađa", 2500, 811]
    ], "Import"))
    
    # Go (Value)
    records.extend(process_market_data(metadata, t, "Gỗ & sản phẩm gỗ", [
        ["Trung Quốc", None, 76598], ["Hoa Kỳ", None, 68533], ["Lào", None, 65233],
        ["Malaixia", None, 59556], ["Thái Lan", None, 44131], ["Niuzilân", None, 32573],
        ["Campuchia", None, 19058], ["Braxin", None, 12272], ["Inđônêxia", None, 10064], ["Chilê", None, 8212]
    ], "Import"))
    
    # Phan bon
    records.extend(process_market_data(metadata, t, "Phân bón các loại", [
        ["Trung Quốc", 532464, 157880], ["Nga", 197347, 64151], ["Canađa", 68898, 28873],
        ["Philippin", 80394, 27108], ["Nhật Bản", 116792, 16725], ["Hàn Quốc", 62556, 14464],
        ["Malaixia", 38362, 11792], ["Đài Loan", 37070, 6775], ["Nauy", 12290, 5117], ["Ấn Độ", 3970, 3352]
    ], "Import"))
    
    # Sua (Value)
    records.extend(process_market_data(metadata, t, "Sữa và sản phẩm sữa", [
        ["Niuzilân", None, 79113], ["Hà Lan", None, 61565], ["Hoa Kỳ", None, 58635],
        ["Thái Lan", None, 16977], ["Ôxtrâylia", None, 15598], ["Ba Lan", None, 13234],
        ["Pháp", None, 9778], ["Malaixia", None, 9349], ["Đan Mạch", None, 8772], ["Tây Ban Nha", None, 5613]
    ], "Import"))
    
    # Thuc an gia suc (Value)
    records.extend(process_market_data(metadata, t, "Thức ăn gia súc và nguyên liệu", [
        ["Achentina", None, 300291], ["Hoa Kỳ", None, 268244], ["Ấn Độ", None, 201336],
        ["Trung Quốc", None, 50668], ["Thái Lan", None, 37533], ["Tiểu VQ Arập thống nhất", None, 20408],
        ["Đài Loan", None, 17649], ["Italia", None, 17608], ["Inđônêxia", None, 17550], ["Canađa", None, 11814]
    ], "Import"))
    
    # Thuoc tru sau (Value)
    records.extend(process_market_data(metadata, t, "Thuốc trừ sâu và nguyên liệu", [
        ["Trung Quốc", None, 111144], ["Ấn Độ", None, 28386], ["Thụy Sỹ", None, 19755],
        ["Đức", None, 14676], ["Hàn Quốc", None, 14317], ["Anh", None, 14306],
        ["Thái Lan", None, 13947], ["Nhật Bản", None, 11636], ["Xinh Ga Po", None, 10981], ["Inđônêxia", None, 9033]
    ], "Import"))
    
    # Rau qua (Value)
    records.extend(process_market_data(metadata, t, "Hàng rau quả", [
        ["Trung Quốc", None, 59137], ["Thái Lan", None, 21277], ["Hoa Kỳ", None, 12770],
        ["Ôxtrâylia", None, 5508], ["Chilê", None, 2191], ["Inđônêxia", None, 1728],
        ["Malaixia", None, 1543], ["Braxin", None, 1315]
    ], "Import"))
    
    # Thuy san (Value)
    records.extend(process_market_data(metadata, t, "Hàng thuỷ sản", [
        ["Đài Loan", None, 25916], ["Inđônêxia", None, 13670], ["Nhật Bản", None, 13323],
        ["Thái Lan", None, 8293], ["Hàn Quốc", None, 8074], ["Chilê", None, 6895],
        ["Nauy", None, 6299], ["Ba Lan", None, 5858], ["Canađa", None, 5125], ["Trung Quốc", None, 4782]
    ], "Import"))

    return records

def process_market_data(metadata, t, commodity, rows, trade_type):
    # trade_type: "Export" or "Import"
    records = []
    for row in rows:
        country, vol, val = row[0], row[1], row[2]
        
        # Determine Units
        vol_unit = "ton"
        val_unit = "1000_USD"
        
        if trade_type == "Export":
            attr_vol = "Export_Volume"
            attr_val = "Export_Value"
        else:
            attr_vol = "Import_Volume"
            attr_val = "Import_Value"
        
        if vol is not None:
             records.append(create_record(metadata, t, country, "Country", {"sector": "Trade", "commodity": commodity, "sub_item": trade_type}, {"attribute": attr_vol, "value": float(vol), "unit": vol_unit, "data_type": "Actual"}))
        if val is not None:
             records.append(create_record(metadata, t, country, "Country", {"sector": "Trade", "commodity": commodity, "sub_item": trade_type}, {"attribute": attr_val, "value": float(val), "unit": val_unit, "data_type": "Actual"}))
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/07"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl7()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL7.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl8a()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL8a.json"))
    save_json({"metadata": {"year": 2010, "month": 7}, "records": parse_pl8b()}, os.path.join(out_dir, "2010_07_phuluc_07_2010_PL8b.json"))
    print("Successfully parsed PL7, PL8a, PL8b for July 2010.")
