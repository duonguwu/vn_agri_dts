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

def parse_pl8():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL8", "source_file": "2010_06_Phuluc_06_2010_PL8.md"}
    records = []
    t = {"year": 2010, "month": 6, "period_type": "Cumulative", "report_date": "2010-06-30"}
    
    # [Item, Vol, Val] (6 months)
    exports = [
        ["Tổng kim ngạch XK", None, 8599],
        ["Nông sản chính", None, 4604],
        ["Cà phê", 664, 925],
        ["Cao su", 207, 565],
        ["Gạo", 3641, 1870],
        ["Chè", 52, 70],
        ["Hạt điều", 77, 405],
        ["Hạt tiêu", 75, 234],
        ["Hàng rau quả", None, 221],
        ["Sắn và sản phẩm từ sắn", None, 314],
        ["Thuỷ sản", None, 1996],
        ["Lâm sản chính", None, 1586],
        ["Quế", None, 2],
        ["Gỗ & sản phẩm gỗ", None, 1484],
        ["SP mây, tre, cói, thảm", None, 100],
    ]
    
    imports = [
        ["Tổng kim ngạch NK", None, 6375],
        ["Phân bón các loại", 1422, 444],
        ["Ure", 366, 111],
        ["SA", 350, 48],
        ["DAP", 170, 73],
        ["NPK", 119, 45],
        ["Phân bón khác", 417, 167],
        ["Thuốc trừ sâu & nguyên liệu", None, 286],
        ["Lúa mỳ", 1189, 289],
        ["Thức ăn gia súc và nguyên liệu", None, 1097],
        ["Dầu mỡ động, thực vật", None, 283],
        ["Cao su", 140, 287],
        ["Bông các loại", 195, 323],
        ["Sữa &sản phẩm sữa", None, 362],
        ["Gỗ & sản phẩm gỗ", None, 487],
        ["Muối", 5.3, None],
        ["Hàng thủy sản", None, 145],
        ["Hàng rau quả", None, 125]
    ]

    for item, vol, val in exports:
        if vol: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Xuất khẩu"}, {"attribute": "Export_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))
        if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Xuất khẩu"}, {"attribute": "Export_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))
        
    for item, vol, val in imports:
        if vol: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Nhập khẩu"}, {"attribute": "Import_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))
        if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Nhập khẩu"}, {"attribute": "Import_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))

    return records

def parse_pl9a():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL9a", "source_file": "2010_06_Phuluc_06_2010_PL9a.md"}
    records = []
    # 5 months
    t = {"year": 2010, "month": 5, "period_type": "Cumulative", "report_date": "2010-05-31"}
    
    # [Item, [[Country, Vol, Val]...]]
    # Ca phe
    records.extend(process_market_data(metadata, t, "Cà phê", [
        ["Đức", 73973, 103517], ["Hoa Kỳ", 66954, 100187], ["Tây Ban Nha", 38230, 51530],
        ["Italia", 35181, 49003], ["Nhật Bản", 27107, 41800], ["Bỉ", 21595, 30070],
        ["Nga", 17713, 24003], ["Anh", 16283, 22037], ["Malaixia", 12615, 17290], ["Hàn Quốc", 12178, 17215]
    ], "Export"))
    
    # Cao su
    records.extend(process_market_data(metadata, t, "Cao su", [
        ["Trung Quốc", 117014, 314947], ["Hàn Quốc", 9526, 24810], ["Nga", 6738, 21333],
        ["Đài Loan", 7297, 20837], ["Đức", 5939, 16767], ["Malaixia", 5598, 14416],
        ["Hoa Kỳ", 4977, 11336], ["Nhật Bản", 3410, 10234], ["Ấn Độ", 3148, 9517], ["Thổ Nhĩ Kỳ", 3300, 9476]
    ], "Export"))
    
    # Che
    records.extend(process_market_data(metadata, t, "Chè", [
        ["Nga", 7583, 10194], ["Đài Loan", 6842, 7918], ["Pakixtan", 5106, 7818],
        ["Trung Quốc", 3291, 4051], ["Ấn Độ", 2038, 2471], ["Tiểu VQ Arập thống nhất", 1305, 2457],
        ["Inđônêxia", 2295, 2359], ["Hoa Kỳ", 2074, 2201], ["Đức", 1460, 1971], ["Ba Lan", 1317, 1546]
    ], "Export"))
    
    # Gao
    records.extend(process_market_data(metadata, t, "Gạo", [
        ["Philippin", 1187793, 759024], ["Xinh Ga Po", 258175, 108037], ["Đài Loan", 234024, 91547],
        ["Malaixia", 176331, 79512], ["Cuba", 147725, 66069], ["Hồng Công", 56760, 25172],
        ["Nga", 30596, 13192], ["Inđônêxia", 16990, 10340], ["Nam Phi", 10995, 4867], ["Ucraina", 8209, 3786]
    ], "Export"))
    
    # Go (Value)
    records.extend(process_market_data(metadata, t, "Gỗ & sản phẩm gỗ", [
        ["Hoa Kỳ", None, 495362], ["Nhật Bản", None, 155037], ["Trung Quốc", None, 119447],
        ["Anh", None, 80265], ["Đức", None, 50268], ["Hàn Quốc", None, 50122],
        ["Pháp", None, 35094], ["Canađa", None, 30628], ["Hà Lan", None, 28686], ["Ôxtrâylia", None, 24964]
    ], "Export"))
    
    # Rau qua (Value)
    records.extend(process_market_data(metadata, t, "Hàng rau quả", [
        ["Trung Quốc", None, 21280], ["Nhật Bản", None, 13767], ["Hà Lan", None, 11812],
        ["Nga", None, 10901], ["Hoa Kỳ", None, 9640], ["Inđônêxia", None, 9196],
        ["Đài Loan", None, 6615], ["Xinh Ga Po", None, 5194], ["Thái Lan", None, 4437], ["Hàn Quốc", None, 4398]
    ], "Export"))
    
    # Thuy san (Value)
    records.extend(process_market_data(metadata, t, "Hàng thuỷ sản", [
        ["Hoa Kỳ", None, 258104], ["Hàn Quốc", None, 122651], ["Đức", None, 72402],
        ["Italia", None, 46570], ["Hà Lan", None, 43645], ["Bỉ", None, 37279],
        ["Đài Loan", None, 35218], ["Hồng Công", None, 31421], ["Anh", None, 30453], ["Canađa", None, 28600]
    ], "Export"))
    
    # Hat dieu
    records.extend(process_market_data(metadata, t, "Hạt điều", [
        ["Hoa Kỳ", 19052, 102970], ["Hà Lan", 8812, 48984], ["Trung Quốc", 9009, 44635],
        ["Ôxtrâylia", 4474, 24360], ["Nga", 2728, 14160], ["Anh", 2211, 12209],
        ["Canađa", 1940, 11252], ["Thái Lan", 1444, 8347], ["Đức", 1092, 6498], ["Tiểu VQ Arập thống nhất", 706, 3183]
    ], "Export"))
    
    # Hat tieu
    records.extend(process_market_data(metadata, t, "Hạt tiêu", [
        ["Hoa Kỳ", 8306, 26698], ["Đức", 8241, 25867], ["Hà Lan", 3676, 12206],
        ["Tiểu VQ Arập thống nhất", 4178, 12072], ["Ấn Độ", 4366, 12042], ["Pakixtan", 2155, 6160],
        ["Ai Cập", 1906, 5268], ["Nga", 1829, 5141], ["Anh", 1412, 4890], ["Tây Ban Nha", 1212, 4164]
    ], "Export"))

    # May tre coi (Value)
    records.extend(process_market_data(metadata, t, "Sản phẩm mây, tre, cói và thảm", [
        ["Nhật Bản", None, 12772], ["Đức", None, 12060], ["Hoa Kỳ", None, 11360],
        ["Pháp", None, 4330], ["Hà Lan", None, 3908], ["Ôxtrâylia", None, 3659],
        ["Đài Loan", None, 3351], ["Italia", None, 2757], ["Bỉ", None, 2646], ["Tây Ban Nha", None, 2413]
    ], "Export"))
    
    # San (Vol + Val)
    records.extend(process_market_data(metadata, t, "Sắn và các sản phẩm từ sắn", [
        ["Trung Quốc", 957799, 255613], ["Hàn Quốc", 27985, 6310], ["Đài Loan", 8244, 3255],
        ["Philippin", 8260, 2487], ["Malaixia", 3561, 1571], ["Nhật Bản", 3324, 1186], ["Nga", 235, 87]
    ], "Export"))

    return records

def parse_pl9b():
    metadata = {"year": 2010, "month": 6, "appendix_number": "PL9b", "source_file": "2010_06_Phuluc_06_2010_PL9b.md"}
    records = []
    # 5 months
    t = {"year": 2010, "month": 5, "period_type": "Cumulative", "report_date": "2010-05-31"}
    
    # [Item, [[Country, Vol, Val]...]]
    # Bong
    records.extend(process_market_data(metadata, t, "Bông các loại", [
        ["Hoa Kỳ", 49358, 81594], ["Ấn Độ", 44993, 74012], ["Braxin", 4866, 8422],
        ["Thụy Sỹ", 686, 1197], ["Xinh Ga Po", 510, 901], ["Trung Quốc", 112, 642],
        ["Inđônêxia", 310, 409], ["Hàn Quốc", 175, 400], ["Italia", 208, 183], ["Đài Loan", 119, 149]
    ], "Import"))
    
    # Cao su
    records.extend(process_market_data(metadata, t, "Cao su", [
        ["Thái Lan", 19560, 41721], ["Hàn Quốc", 18212, 38411], ["Campuchia", 11444, 33750],
        ["Nhật Bản", 10476, 28693], ["Đài Loan", 8973, 18234], ["Trung Quốc", 7156, 15638],
        ["Nga", 3597, 9419], ["Inđônêxia", 3347, 8210], ["Hoa Kỳ", 8714, 7287], ["Malaixia", 4469, 6747]
    ], "Import"))

    # Dau mo (Value)
    records.extend(process_market_data(metadata, t, "Dầu mỡ động thực vật", [
        ["Malaixia", None, 114890], ["Inđônêxia", None, 67837], ["Hoa Kỳ", None, 25740],
        ["Thái Lan", None, 6636], ["Trung Quốc", None, 4198], ["Ấn Độ", None, 1878],
        ["Chilê", None, 1141], ["Hàn Quốc", None, 1133], ["Ôxtrâylia", None, 867], ["Xinh Ga Po", None, 664]
    ], "Import"))
    
    # Lua mi
    records.extend(process_market_data(metadata, t, "Lúa mì", [
        ["Ôxtrâylia", 516199, 130949], ["Braxin", 236836, 55196], ["Ucraina", 112183, 25380],
        ["Nga", 35430, 8132], ["Hoa Kỳ", 16197, 4539], ["Canađa", 500, 151]
    ], "Import"))
    
    # Go (Value)
    records.extend(process_market_data(metadata, t, "Gỗ & sản phẩm gỗ", [
        ["Trung Quốc", None, 60399], ["Hoa Kỳ", None, 54984], ["Lào", None, 49561],
        ["Malaixia", None, 48720], ["Thái Lan", None, 34988], ["Braxin", None, 8823],
        ["Inđônêxia", None, 7922], ["Chilê", None, 6910], ["Đài Loan", None, 2941], ["Italia", None, 2059]
    ], "Import"))
    
    # Phan bon
    records.extend(process_market_data(metadata, t, "Phân bón các loại", [
        ["Trung Quốc", 469363, 139344], ["Nga", 190997, 61373], ["Philippin", 74809, 25005],
        ["Canađa", 55058, 22878], ["Hàn Quốc", 62533, 14452], ["Nhật Bản", 99398, 14361],
        ["Malaixia", 34450, 10754], ["Đài Loan", 35775, 10754], ["Nauy", 10178, 6416], ["Ấn Độ", 3944, 4366]
    ], "Import"))
    
    # Sua (Value)
    records.extend(process_market_data(metadata, t, "Sữa và sản phẩm sữa", [
        ["Niuzilân", None, 65392], ["Hà Lan", None, 52516], ["Hoa Kỳ", None, 44387],
        ["Ôxtrâylia", None, 14442], ["Thái Lan", None, 13882], ["Ba Lan", None, 10773],
        ["Pháp", None, 8909], ["Malaixia", None, 8546], ["Đan Mạch", None, 8037], ["Tây Ban Nha", None, 4738]
    ], "Import"))
    
    # Thuc an gia suc (Value)
    records.extend(process_market_data(metadata, t, "Thức ăn gia súc và nguyên liệu", [
        ["Hoa Kỳ", None, 242686], ["Ấn Độ", None, 192795], ["Achentina", None, 187827],
        ["Trung Quốc", None, 44461], ["Thái Lan", None, 26540], ["Tiểu VQ Arập thống nhất", None, 16508],
        ["Italia", None, 14163], ["Đài Loan", None, 12362], ["Canađa", None, 9598], ["Philippin", None, 8482]
    ], "Import"))
    
    # Thuoc tru sau (Value)
    records.extend(process_market_data(metadata, t, "Thuốc trừ sâu và nguyên liệu", [
        ["Trung Quốc", None, 94295], ["Ấn Độ", None, 24477], ["Thụy Sỹ", None, 19059],
        ["Hàn Quốc", None, 12780], ["Đức", None, 12696], ["Thái Lan", None, 11706],
        ["Anh", None, 11238], ["Xinh Ga Po", None, 10176], ["Nhật Bản", None, 9890], ["Inđônêxia", None, 8396]
    ], "Import"))
    
    # Rau qua (Value)
    records.extend(process_market_data(metadata, t, "Hàng rau quả", [
        ["Trung Quốc", None, 49208], ["Thái Lan", None, 16663], ["Hoa Kỳ", None, 10763],
        ["Ôxtrâylia", None, 3775], ["Chilê", None, 1510], ["Malaixia", None, 1349],
        ["Inđônêxia", None, 1179], ["Braxin", None, 1118]
    ], "Import"))
    
    # Thuy san (Value)
    records.extend(process_market_data(metadata, t, "Hàng thuỷ sản", [
        ["Đài Loan", None, 23772], ["Nhật Bản", None, 11097], ["Inđônêxia", None, 10721],
        ["Thái Lan", None, 5989], ["Hàn Quốc", None, 5338], ["Ba Lan", None, 5098],
        ["Nauy", None, 5072], ["Chilê", None, 4683], ["Trung Quốc", None, 4492], ["Canađa", None, 3832]
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
        
        # If trade_type Export
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl8()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL8.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl9a()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL9a.json"))
    save_json({"metadata": {"year": 2010, "month": 6}, "records": parse_pl9b()}, os.path.join(out_dir, "2010_06_Phuluc_06_2010_PL9b.json"))
    print("Successfully parsed PL8, PL9a, PL9b for June 2010.")
