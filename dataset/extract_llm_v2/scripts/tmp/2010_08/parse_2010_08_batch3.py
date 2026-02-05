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

def parse_pl10():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL10", "source_file": "2010_08_Phuluc_T08_2010_PL10.md"}
    records = []
    # 8 months
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    # [Item, Vol, Val] -> Col 5 (Vol), Col 6 (Val) in PL10 are "8 tháng 2010"
    exports = [
        ["Tổng kim ngạch XK", None, 12204],
        ["Nông sản chính", None, 6497],
        ["Cà phê", 840, 1201],
        ["Cao su", 417, 1149],
        ["Gạo", 5017, 2387],
        ["Chè", 85, 124],
        ["Hạt điều", 120, 656],
        ["Hạt tiêu", 94, 312],
        ["Hàng rau quả", None, 320],
        ["Sắn và sản phẩm từ sắn", 1285, 347],
        ["Thuỷ sản", None, 2948],
        ["Lâm sản chính", None, 2280],
        ["Quế", None, 15], # Vol blank
        ["Gỗ & sản phẩm gỗ", None, 2131],
        ["SP mây, tre, cói, thảm", None, 135]
    ]
    
    imports = [
        ["Tổng kim ngạch NK", None, 8473],
        ["Phân bón các loại", 1825, 576],
        ["Ure", 453, 135],
        ["SA", 425, 58],
        ["DAP", 254, 111],
        ["NPK", 144, 56],
        ["Phân bón khác", 549, 217],
        ["Thuốc trừ sâu & nguyên liệu", None, 344],
        ["Lúa mỳ", 1411, 343],
        ["Thức ăn gia súc và nguyên liệu", None, 1555],
        ["Dầu mỡ động, thực vật", None, 357],
        ["Cao su", 185, 382],
        ["Bông các loại", 244, 416],
        ["Sữa &sản phẩm sữa", None, 480],
        ["Gỗ & sản phẩm gỗ", None, 716],
        ["Muối", 13.1, None],
        ["Hàng thủy sản", None, 206],
        ["Hàng rau quả", None, 173]
    ]

    for item, vol, val in exports:
        if vol: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Xuất khẩu"}, {"attribute": "Export_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))
        if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Xuất khẩu"}, {"attribute": "Export_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))
        
    for item, vol, val in imports:
        if vol: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Nhập khẩu"}, {"attribute": "Import_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))
        if val: records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": item, "sub_item": "Nhập khẩu"}, {"attribute": "Import_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))

    return records

def parse_pl11a():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL11a", "source_file": "2010_08_Phuluc_T08_2010_PL11a.md"}
    records = []
    # 7 months (Data in PL11a is for 7 months, despite filename PL11a being in Aug)
    # The title inside PL11a says "7 THÁNG NĂM 2010". So I respect the content.
    t = {"year": 2010, "month": 7, "period_type": "Cumulative", "report_date": "2010-07-31"}
    
    # Coffee
    records.extend(process_market_data(metadata, t, "Cà phê", [
        ["Đức", 102851, 146973], ["Hoa Kỳ", 91968, 138651], ["Tây Ban Nha", 55154, 76834],
        ["Italia", 47615, 67377], ["Nhật Bản", 35823, 54874], ["Bỉ", 32734, 45893],
        ["Anh", 20327, 28018], ["Nga", 20228, 27565], ["Philippin", 18608, 25460], ["Thụy Sỹ", 17113, 24160]
    ], "Export"))
    
    # Rubber
    records.extend(process_market_data(metadata, t, "Cao su", [
        ["Trung Quốc", 187942, 509295], ["Malaixia", 19131, 49668], ["Hàn Quốc", 17899, 47549],
        ["Đài Loan", 15383, 46030], ["Đức", 13001, 39451], ["Nga", 9295, 28902],
        ["Hoa Kỳ", 9671, 23976], ["Ấn Độ", 7471, 22269], ["Nhật Bản", 5388, 17119], ["Thổ Nhĩ Kỳ", 5672, 16038]
    ], "Export"))
    
    # Tea
    records.extend(process_market_data(metadata, t, "Chè", [
        ["Pakixtan", 11506, 19642], ["Nga", 10787, 14782], ["Đài Loan", 12088, 14321],
        ["Trung Quốc", 6808, 8552], ["Tiểu VQ Arập thống nhất", 1816, 3350], ["Hoa Kỳ", 3084, 3320],
        ["Inđônêxia", 2796, 2897], ["Ấn Độ", 2117, 2604], ["Đức", 1800, 2489], ["Ba Lan", 1456, 1785]
    ], "Export"))
    
    # Rice
    records.extend(process_market_data(metadata, t, "Gạo", [
        ["Philippin", 1461883, 938860], ["Xinh Ga Po", 383183, 156407], ["Đài Loan", 296019, 114469],
        ["Cuba", 252125, 106909], ["Malaixia", 202067, 91640], ["Hồng Kông", 76439, 34557],
        ["Trung Quốc", 79208, 32932], ["Nga", 37216, 15805], ["Inđônêxia", 16545, 10024], ["Nam Phi", 22331, 8869]
    ], "Export"))
    
    # Wood (Value)
    records.extend(process_market_data(metadata, t, "Gỗ & sản phẩm gỗ", [
        ["Hoa Kỳ", None, 753877], ["Nhật Bản", None, 229752], ["Trung Quốc", None, 211195],
        ["Anh", None, 107060], ["Hàn Quốc", None, 71807], ["Đức", None, 63069],
        ["Canađa", None, 46044], ["Pháp", None, 42642], ["Ôxtrâylia", None, 39818], ["Hà Lan", None, 37546]
    ], "Export"))
    
    # Veg (Value)
    records.extend(process_market_data(metadata, t, "Hàng rau quả", [
        ["Trung Quốc", None, 30985], ["Nhật Bản", None, 19949], ["Hà Lan", None, 19468],
        ["Nga", None, 14437], ["Hoa Kỳ", None, 14089], ["Đài Loan", None, 11651],
        ["Inđônêxia", None, 10522], ["Xinh Ga Po", None, 8688], ["Hàn Quốc", None, 6727], ["Thái Lan", None, 5072]
    ], "Export"))
    
    # Fishery (Value)
    records.extend(process_market_data(metadata, t, "Hàng thuỷ sản", [
        ["Nhật Bản", None, 459043], ["Hoa Kỳ", None, 418127], ["Hàn Quốc", None, 179179],
        ["Đức", None, 102972], ["Tây Ban Nha", None, 93537], ["Trung Quốc", None, 75366],
        ["Italia", None, 72955], ["Ôxtrâylia", None, 70845], ["Hà Lan", None, 68742], ["Pháp", None, 64928]
    ], "Export"))
    
    # Cashew
    records.extend(process_market_data(metadata, t, "Hạt điều", [
        ["Hoa Kỳ", 33048, 184160], ["Hà Lan", 14525, 82128], ["Trung Quốc", 14111, 71897],
        ["Ôxtrâylia", 7273, 40457], ["Anh", 4452, 25272], ["Nga", 3494, 18329],
        ["Canađa", 3640, 17163], ["Thái Lan", 2023, 11860], ["Đức", 1743, 10514], ["Tây Ban Nha", 766, 4677]
    ], "Export"))
    
    # Pepper
    records.extend(process_market_data(metadata, t, "Hạt tiêu", [
        ["Hoa Kỳ", 11666, 38479], ["Đức", 10507, 36156], ["Tiểu VQ Arập thống nhất", 7729, 24162],
        ["Hà Lan", 5372, 18694], ["Ấn Độ", 5444, 15625], ["Pakixtan", 3570, 10972],
        ["Nga", 3053, 9290], ["Ai Cập", 2954, 8734], ["Anh", 2140, 7617], ["Tây Ban Nha", 1624, 5836]
    ], "Export"))
    
    # Rattan/Bamboo (Value)
    records.extend(process_market_data(metadata, t, "Sản phẩm mây, tre, cói và thảm", [
        ["Nhật Bản", None, 18620], ["Hoa Kỳ", None, 17794], ["Đức", None, 15743],
        ["Pháp", None, 5656], ["Ôxtrâylia", None, 5322], ["Hà Lan", None, 5017],
        ["Đài Loan", None, 4699], ["Italia", None, 3756], ["Tây Ban Nha", None, 3520], ["Anh", None, 3435]
    ], "Export"))
    
    # Cassava
    records.extend(process_market_data(metadata, t, "Sắn và các SP từ sắn", [
        ["Trung Quốc", 1139280, 303774], ["Hàn Quốc", 33485, 7536], ["Đài Loan", 12130, 5047],
        ["Philippin", 9932, 3385], ["Malaixia", 5076, 2314], ["Nhật Bản", 3877, 1367], ["Nga", 236, 88]
    ], "Export"))

    return records

def parse_pl11b():
    metadata = {"year": 2010, "month": 8, "appendix_number": "PL11b", "source_file": "2010_08_Phuluc_T08_2010_PL11b.md"}
    records = []
    # 7 months as per content
    t = {"year": 2010, "month": 7, "period_type": "Cumulative", "report_date": "2010-07-31"}
    
    # Cotton
    records.extend(process_market_data(metadata, t, "Bông các loại", [
        ["Hoa Kỳ", 75457, 133508], ["Ấn Độ", 46705, 76852], ["Braxin", 5535, 9568],
        ["Thụy Sỹ", 1076, 1992], ["Xinh Ga Po", 711, 1281], ["Inđônêxia", 659, 870],
        ["Trung Quốc", 168, 862], ["Hàn Quốc", 294, 684], ["Đài Loan", 250, 404], ["Italia", 331, 300]
    ], "Import"))
    
    # Rubber
    records.extend(process_market_data(metadata, t, "Cao su", [
        ["Hàn Quốc", 26182, 56271], ["Thái Lan", 23264, 51134], ["Campuchia", 16392, 46939],
        ["Nhật Bản", 13439, 38356], ["Đài Loan", 14444, 30511], ["Trung Quốc", 11852, 25138],
        ["Nga", 4808, 13242], ["Hoa Kỳ", 12788, 11220], ["Inđônêxia", 4301, 10329], ["Malaixia", 6348, 7429]
    ], "Import"))
    
    # Oil/Fat (Value)
    records.extend(process_market_data(metadata, t, "Dầu mỡ động thực vật", [
        ["Malaixia", None, 151817], ["Inđônêxia", None, 90678], ["Hoa Kỳ", None, 26200],
        ["Achentina", None, 15579], ["Thái Lan", None, 9080], ["Trung Quốc", None, 4930],
        ["Ấn Độ", None, 2475], ["Hàn Quốc", None, 1462], ["Ôxtrâylia", None, 1451], ["Chilê", None, 1409]
    ], "Import"))
    
    # Wheat
    records.extend(process_market_data(metadata, t, "Lúa mì", [
        ["Ôxtrâylia", 762983, 191657], ["Braxin", 236836, 55196], ["Ucraina", 143214, 32499],
        ["Nga", 53068, 12129], ["Hoa Kỳ", 19602, 5455], ["Canađa", 3542, 1170]
    ], "Import"))
    
    # Wood (Value)
    records.extend(process_market_data(metadata, t, "Gỗ & sản phẩm gỗ", [
        ["Trung Quốc", None, 91616], ["Lào", None, 89116], ["Hoa Kỳ", None, 79946],
        ["Malaixia", None, 69731], ["Thái Lan", None, 51260], ["Niuzilân", None, 39037],
        ["Campuchia", None, 23115], ["Braxin", None, 14232], ["Inđônêxia", None, 11587], ["Chilê", None, 9469]
    ], "Import"))
    
    # Fertilizer
    records.extend(process_market_data(metadata, t, "Phân bón các loại", [
        ["Trung Quốc", 638509, 191005], ["Nga", 236195, 79413], ["Canađa", 82298, 34367],
        ["Philippin", 84214, 28538], ["Nhật Bản", 122802, 17477], ["Hàn Quốc", 69286, 15247],
        ["Malaixia", 41874, 12760], ["Đài Loan", 43157, 7658], ["Nauy", 14167, 5994], ["Hoa Kỳ", 7842, 5272]
    ], "Import"))
    
    # Milk (Value)
    records.extend(process_market_data(metadata, t, "Sữa và sản phẩm sữa", [
        ["Niuzilân", None, 97140], ["Hoa Kỳ", None, 77230], ["Hà Lan", None, 66620],
        ["Thái Lan", None, 21106], ["Ôxtrâylia", None, 17512], ["Ba Lan", None, 17047],
        ["Pháp", None, 11705], ["Đan Mạch", None, 9719], ["Malaixia", None, 9636], ["Tây Ban Nha", None, 6875]
    ], "Import"))
    
    # Feed (Value)
    records.extend(process_market_data(metadata, t, "Thức ăn gia súc và nguyên liệu", [
        ["Achentina", None, 361364], ["Hoa Kỳ", None, 282636], ["Ấn Độ", None, 219792],
        ["Trung Quốc", None, 57518], ["Thái Lan", None, 46872], ["Tiểu VQ Arập thống nhất", None, 23096],
        ["Đài Loan", None, 22875], ["Inđônêxia", None, 21921], ["Italia", None, 21487], ["Chilê", None, 14318]
    ], "Import"))
    
    # Pesticide (Value)
    records.extend(process_market_data(metadata, t, "Thuốc trừ sâu và nguyên liệu", [
        ["Trung Quốc", None, 121734], ["Ấn Độ", None, 31855], ["Thụy Sỹ", None, 22991],
        ["Anh", None, 16893], ["Đức", None, 16169], ["Thái Lan", None, 15949],
        ["Hàn Quốc", None, 15021], ["Nhật Bản", None, 13190], ["Xinh Ga Po", None, 13057], ["Inđônêxia", None, 10757]
    ], "Import"))
    
    # Veg (Value)
    records.extend(process_market_data(metadata, t, "Hàng rau quả", [
        ["Trung Quốc", None, 72587], ["Thái Lan", None, 25717], ["Hoa Kỳ", None, 14404],
        ["Ôxtrâylia", None, 7309], ["Chilê", None, 2259], ["Malaixia", None, 1790],
        ["Inđônêxia", None, 1757], ["Braxin", None, 1571]
    ], "Import"))
    
    # Fishery (Value)
    records.extend(process_market_data(metadata, t, "Hàng thuỷ sản", [
        ["Đài Loan", None, 28139], ["Nhật Bản", None, 16326], ["Inđônêxia", None, 16055],
        ["Thái Lan", None, 9646], ["Hàn Quốc", None, 8994], ["Nauy", None, 7625],
        ["Chi Lê", None, 7449], ["Canađa", None, 6803], ["Ba Lan", None, 6479], ["Hoa Kỳ", None, 5804]
    ], "Import"))
    
    # Salt
    records.extend(process_market_data(metadata, t, "Muối", [
        ["Ấn Độ", None, 6615], ["Trung Quốc", None, 3031], ["Thái Lan", None, 891],
        ["Pakixtan", None, 124], ["Ixraen", None, 76], ["Niuzilân", None, 58],
        ["Singapo", None, 56], ["Malaixia", None, 50], ["Đan Mạch", None, 44], ["Nhật Bản", None, 34]
    ], "Import"))

    return records

def process_market_data(metadata, t, commodity, rows, trade_type):
    records = []
    for row in rows:
        country, vol, val = row[0], row[1], row[2]
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
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/08"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl10()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL10.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl11a()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL11a.json"))
    save_json({"metadata": {"year": 2010, "month": 8}, "records": parse_pl11b()}, os.path.join(out_dir, "2010_08_Phuluc_T08_2010_PL11b.json"))
    print("Successfully parsed PL10, PL11a, PL11b for August 2010.")
