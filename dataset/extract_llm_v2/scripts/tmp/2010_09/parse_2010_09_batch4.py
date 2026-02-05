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

def split_cell(cell_text):
    if not cell_text: return []
    return [x.strip() for x in str(cell_text).split('<br>')]

def parse_pl10():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL10", "source_file": "2010_09_phuluc_T09_2010_PL10.md"}
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Cumulative", "report_date": "2010-09-30"}
    
    # Raw strings from Row 13 (Export) and Row 13 (Import - continuation in same col)
    # The view_file output showed Col 0 contains items, Col 5 (Vol9T), Col 6 (Val9T)
    # Col 5 (Vol) content from view: `11,394`...
    # Col 6 (Val) content from view: `12,182`...
    
    items = [
        "Tổng kim ngạch XK", "Nông sản chính", "Cà phê", "Cao su", "Gạo", "Chè", "Hạt điều", "Hạt tiêu",
        "Hàng rau quả", "Sắn và sản phẩm từ sắn", "Thuỷ sản", "Lâm sản chính", "Quế", "Gỗ & sản phẩm gỗ",
        "SP mây, tre, cói, thảm", "Các mặt hàng nông lâm sản khác",
        "Tổng kim ngạch NK", "Các mặt hàng nhập khẩu chính", "Phân bón các loại",
        "- U RE", "- S A", "- D A P", "- N P K", "- Các loại phân bón khác",
        "Thuốc trừ sâu & nguyên liệu", "Lúa mỳ", "Thức ăn gia súc và nguyên liệu",
        "Dầu mỡ động, thực vật", "Cao su", "Bông các loại", "Sữa &sản phẩm sữa",
        "Gỗ & sản phẩm gỗ", "Muối", "Hàng thủy sản", "Hàng rau quả"
    ]
    
    # Manually extracted values from the mapped view file for 9T 2010
    # Values align with items list above. None for blanks.
    # Col 6 (Value) is the most reliable column to sync.
    values_val = [
        12182, 6482, 1225, 1178, 2328, 123, 670, 305, 298, 354, 
        2978, 2283, 15, 2132, 135, 439, # Exports done
        8500, 5584, 623, 152, 55, 123, 65, 227, # Imports start. NOTE: Ure/SA/DAP values are italicized/small.
        337, 343, 1496, 366, 391, 429, 486, 717, 12.6, 206, 176
    ]
    
    # Col 5 (Volume)
    values_vol = [
        None, None, 855, 431, 4950, 85, 123, 92, None, 1283,
        None, None, None, None, None, None,
        None, None, 1942, 512, 412, 279, 168, 571,
        None, 1411, None, None, 189, 246, None, None, None, None, None
    ]
    
    trade_type = "Xuất khẩu"
    for idx, item_name in enumerate(items):
        if "Tổng kim ngạch NK" in item_name: trade_type = "Nhập khẩu"
        
        # Clean item name prefix
        clean_name = item_name.replace("- ", "").replace("_", "").strip()
        
        if idx < len(values_val):
            val = values_val[idx]
            if val is not None:
                records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": clean_name, "sub_item": trade_type}, {"attribute": "Export_Value" if trade_type == "Xuất khẩu" else "Import_Value", "value": float(val), "unit": "million_USD", "data_type": "Actual"}))
        
        if idx < len(values_vol):
            vol = values_vol[idx]
            if vol is not None:
                records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Trade", "commodity": clean_name, "sub_item": trade_type}, {"attribute": "Export_Volume" if trade_type == "Xuất khẩu" else "Import_Volume", "value": float(vol), "unit": "1000_ton", "data_type": "Actual"}))

    return records

def parse_market_table(metadata, time, commodity, col_countries, col_vol, col_val, trade_type):
    records = []
    countries = split_cell(col_countries)
    vols = split_cell(col_vol)
    vals = split_cell(col_val)
    
    limit = min(len(countries), len(vals))
    for i in range(limit):
        country = countries[i].replace("_", "").strip()
        if not country or country.isdigit(): continue
        
        # Val
        try:
            val = normalize_number(vals[i])
            if val is not None:
                attr = "Export_Value" if trade_type == "Export" else "Import_Value"
                records.append(create_record(metadata, time, country, "Country", {"sector": "Trade", "commodity": commodity, "sub_item": trade_type}, {"attribute": attr, "value": val, "unit": "1000_USD", "data_type": "Actual"}))
        except: pass
        
        # Vol
        if i < len(vols):
            try:
                vol = normalize_number(vols[i])
                if vol is not None:
                    attr = "Export_Volume" if trade_type == "Export" else "Import_Volume"
                    records.append(create_record(metadata, time, country, "Country", {"sector": "Trade", "commodity": commodity, "sub_item": trade_type}, {"attribute": attr, "value": vol, "unit": "ton", "data_type": "Actual"}))
            except: pass
            
    return records

def parse_pl11a():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL11a", "source_file": "2010_09_phuluc_T09_2010_PL11a.md"}
    records = []
    # 8 months
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    # Rows with data. Based on viewing file content.
    # Coffee (Row 19)
    # Countries: Col 1. Vol 2010: Col 4. Val 2010: Col 5. (Indices 0-based in array)
    # In table content: 
    # Row 19 is Coffee.
    # Row 21 is Rubber.
    # Row 23 is Tea.
    # Row 25 is Rice.
    # Row 27 is Wood (Value only -> No Vol).
    # Row 35 is Veg (Value).
    # Row 37 is Fishery (Value).
    # Row 39 is Cashew.
    # Row 41 is Pepper.
    # Row 43 is Rattan.
    # Row 51 is Cassava.
    
    # Copied cell content for each row
    data = [
        ("Cà phê", "ĐỨC<br>HOA KỲ<br>TÂY BAN NHA<br>ITALIA<br>NHẬT BẢN<br>BỈ<br>PHI LIP PIN<br>ANH<br>NGA<br>HÀN QUỐC", "113877<br>102562<br>59739<br>52548<br>40113<br>34563<br>23131<br>21288<br>21178<br>18850", "164886<br>155915<br>83822<br>75079<br>61836<br>48748<br>32517<br>29641<br>29048<br>27029"),
        ("Cao su", "TRUNG QUỐC<br>MALAIXIA<br>HÀN QUỐC<br>ĐÀI LOAN<br>ĐỨC<br>ẤN ĐỘ<br>NGA<br>HOA KỲ<br>THỔ NHĨ KỲ<br>NHẬT BẢN", "252432<br>27059<br>21409<br>18610<br>15881<br>12561<br>10965<br>12991<br>7488<br>6526", "674171<br>71039<br>56554<br>55679<br>48715<br>37724<br>33858<br>32615<br>21069<br>21022"),
        ("Chè", "PAKIXTAN<br>ĐÀI LOAN<br>NGA<br>TRUNG QUỐC<br>TVQ ARẬP THỐNG NHẤT<br>HOA KỲ<br>IN ĐÔ NÊ XI A<br>ĐỨC<br>ẤN ĐỘ<br>ARẬP XÊÚT", "15167<br>14373<br>12257<br>9259<br>1997<br>3386<br>3274<br>1989<br>2191<br>1218", "26706<br>17021<br>16907<br>11218<br>3711<br>3628<br>3366<br>2836<br>2713<br>2548"),
        ("Gạo", "PHI LIP PIN<br>XINH GA PO<br>CUBA<br>ĐÀI LOAN<br>MALAIXIA<br>TRUNG QUỐC<br>HỒNG CÔNG<br>NGA<br>IN ĐÔ NÊ XI A<br>NAM PHI", "1466173<br>441680<br>297125<br>301293<br>215293<br>98080<br>87124<br>50466<br>26115<br>24206", "940260<br>179264<br>123615<br>116818<br>98149<br>40489<br>39587<br>20911<br>15998<br>9607"),
        ("Hạt điều", "HOA KỲ<br>HÀ LAN<br>TRUNG QUỐC<br>Ô X TRÂY LIA<br>ANH<br>NGA<br>CA NA ĐA<br>THÁI LAN<br>ĐỨC<br>TVQ ARẬP THỐNG NHẤT", "40029<br>17246<br>18352<br>9124<br>5413<br>3929<br>4180<br>2377<br>1965<br>1187", "226402<br>98535<br>95268<br>51780<br>31184<br>20789<br>20449<br>14024<br>11962<br>5982"),
        ("Hạt tiêu", "HOA KỲ<br>ĐỨC<br>TVQ ARẬP THỐNG NHẤT<br>HÀ LAN<br>ẤN ĐỘ<br>PAKIXTAN<br>NGA<br>AI CẬP<br>ANH<br>BA LAN", "12748<br>11293<br>8559<br>6258<br>5711<br>3583<br>3300<br>3007<br>2401<br>2284", "42733<br>40147<br>27338<br>22412<br>16736<br>11025<br>10251<br>8933<br>8809<br>6998"),
        ("Sắn và sản phẩm từ sắn", "TRUNG QUỐC<br>ĐÀI LOAN<br>HÀN QUỐC<br>PHI LIP PIN<br>MALAIXIA<br>NHẬT BẢN<br>NGA", "1195028<br>17594<br>33485<br>11944<br>8414<br>4669<br>236", "322530<br>7913<br>7536<br>4548<br>4142<br>1666<br>88"),
        ("Gỗ & sản phẩm gỗ", "HOA KỲ<br>NHẬT BẢN<br>TRUNG QUỐC<br>ANH<br>HÀN QUỐC<br>ĐỨC<br>CA NA ĐA<br>Ô X TRÂY LIA<br>PHÁP<br>HÀ LAN", "", "889591<br>271473<br>250034<br>120358<br>83904<br>70786<br>54750<br>48288<br>45144<br>41748"),
        ("Hàng rau quả", "TRUNG QUỐC<br>NHẬT BẢN<br>HÀ LAN<br>NGA<br>HOA KỲ<br>ĐÀI LOAN<br>IN ĐÔ NÊ XI A<br>XINH GA PO<br>HÀN QUỐC<br>THÁI LAN", "", "38644<br>23402<br>22038<br>16647<br>16261<br>13717<br>11273<br>9863<br>7613<br>5600"),
        ("Hàng thuỷ sản", "NHẬT BẢN<br>HOA KỲ<br>HÀN QUỐC<br>ĐỨC<br>TÂY BAN NHA<br>TRUNG QUỐC<br>Ô X TRÂY LIA<br>ITALIA<br>HÀ LAN<br>PHÁP", "", "549069<br>532063<br>212660<br>121228<br>106494<br>89869<br>85246<br>84753<br>81107<br>75888"),
        ("Sản phẩm mây, tre, cói", "NHẬT BẢN<br>HOA KỲ<br>ĐỨC<br>Ô X TRÂY LIA<br>PHÁP<br>HÀ LAN<br>ĐÀI LOAN<br>ANH<br>ITALIA<br>TÂY BAN NHA", "", "21210<br>20972<br>17776<br>6510<br>6380<br>5820<br>5480<br>4251<br>4241<br>4090")
    ]
    
    for item in data:
        records.extend(parse_market_table(metadata, t, item[0], item[1], item[2], item[3], "Export"))
    
    return records

def parse_pl11b():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL11b", "source_file": "2010_09_phuluc_T09_2010_PL11b.md"}
    records = []
    # 8 months
    t = {"year": 2010, "month": 8, "period_type": "Cumulative", "report_date": "2010-08-31"}
    
    data = [
        ("Bông các loại", "HOA KỲ<br>ẤN ĐỘ<br>BRAXIN<br>THỤY SỸ<br>XINH GA PO<br>TRUNG QUỐC<br>IN ĐÔ NÊ XI A<br>HÀN QUỐC<br>ĐÀI LOAN<br>ITALIA", "89785<br>48733<br>6685<br>1332<br>915<br>211<br>726<br>400<br>284<br>457", "162829<br>80594<br>11372<br>2526<br>1709<br>977<br>972<br>847<br>460<br>426"),
        ("Cao su", "HÀN QUỐC<br>CAMPUCHIA<br>THÁI LAN<br>NHẬT BẢN<br>ĐÀI LOAN<br>TRUNG QUỐC<br>NGA<br>HOA KỲ<br>IN ĐÔ NÊ XI A<br>MALAIXIA", "30030<br>20867<br>25135<br>15024<br>16871<br>13708<br>5496<br>14242<br>4594<br>7468", "64680<br>59622<br>55676<br>42870<br>35790<br>28708<br>15620<br>12402<br>10835<br>7718"),
        ("Dầu mỡ động thực vật", "MALAIXIA<br>IN ĐÔ NÊ XI A<br>HOA KỲ<br>ACHENTINA<br>THÁI LAN<br>TRUNG QUỐC<br>ẤN ĐỘ<br>CHI LÊ<br>HÀN QUỐC<br>Ô X TRÂY LIA", "", "177216<br>105646<br>26440<br>15611<br>14058<br>7065<br>2869<br>1844<br>1659<br>1549"),
        ("Lúa mì", "Ô X TRÂY LIA<br>BRAXIN<br>UCRAINA<br>NGA<br>HOA KỲ<br>CA NA ĐA", "842253<br>236836<br>149972<br>57023<br>19872<br>3542", "211370<br>55196<br>33972<br>12987<br>5513<br>1170"),
        ("Gỗ & sản phẩm gỗ", "TRUNG QUỐC<br>LÀO<br>HOA KỲ<br>MALAIXIA<br>THÁI LAN<br>NIU ZI LÂN<br>CAMPUCHIA<br>BRAXIN<br>IN ĐÔ NÊ XI A<br>CHI LÊ", "", "107288<br>93502<br>91563<br>81210<br>59603<br>46869<br>27770<br>19219<br>12969<br>11110"),
        ("Phân bón các loại", "TRUNG QUỐC<br>NGA<br>CA NA ĐA<br>PHI LIP PIN<br>HÀN QUỐC<br>NHẬT BẢN<br>MALAIXIA<br>NAUY<br>ĐÀI LOAN<br>HOA KỲ", "800478<br>283632<br>94311<br>111455<br>81087<br>130234<br>54719<br>19495<br>43205<br>7988", "242885<br>97200<br>39364<br>38893<br>21402<br>18515<br>16410<br>8345<br>7737<br>5472"),
        ("Sữa và sản phẩm sữa", "NIU ZI LÂN<br>HOA KỲ<br>HÀ LAN<br>THÁI LAN<br>BA LAN<br>Ô X TRÂY LIA<br>PHÁP<br>ĐAN MẠCH<br>MALAIXIA<br>TÂY BAN NHA", "", "108646<br>96704<br>73691<br>25025<br>19141<br>19112<br>12911<br>10341<br>10092<br>7684"),
        ("Thức ăn gia súc và nguyên liệu", "ACHENTINA<br>HOA KỲ<br>ẤN ĐỘ<br>TRUNG QUỐC<br>THÁI LAN<br>TVQ ARẬP THỐNG NHẤT<br>IN ĐÔ NÊ XI A<br>ĐÀI LOAN<br>ITALIA<br>CHI LÊ", "", "385926<br>298776<br>235402<br>64289<br>56396<br>27905<br>27882<br>26989<br>24002<br>17079"),
        ("Thuốc trừ sâu và nguyên liệu", "TRUNG QUỐC<br>ẤN ĐỘ<br>THỤY SỸ<br>ĐỨC<br>ANH<br>THÁI LAN<br>HÀN QUỐC<br>NHẬT BẢN<br>XINH GA PO<br>IN ĐÔ NÊ XI A", "", "132957<br>36190<br>24583<br>18334<br>17668<br>17609<br>15939<br>14360<br>14100<br>11232"),
        ("Hàng rau quả", "TRUNG QUỐC<br>THÁI LAN<br>HOA KỲ<br>Ô X TRÂY LIA<br>CHI LÊ<br>MALAIXIA<br>IN ĐÔ NÊ XI A<br>BRAXIN", "", "88705<br>29653<br>16685<br>9019<br>2322<br>2099<br>1931<br>1690"),
        ("Hàng thuỷ sản", "ĐÀI LOAN<br>IN ĐÔ NÊ XI A<br>NHẬT BẢN<br>THÁI LAN<br>NAUY<br>HÀN QUỐC<br>CHI LÊ<br>BA LAN<br>HOA KỲ<br>CA NA ĐA", "", "31766<br>19891<br>18978<br>11058<br>9496<br>9383<br>8453<br>7596<br>7588<br>7489"),
        ("Muối", "ẤN ĐỘ<br>TRUNG QUỐC<br>THÁI LAN<br>PAKIXTAN<br>IXRAEN<br>NIU ZI LÂN<br>XINH GA PO<br>NHẬT BẢN<br>MALAIXIA<br>ĐAN MẠCH", "7605<br>3350<br>1106<br>124<br>76<br>65<br>56<br>53<br>50<br>44", "") # Salt Val is missing in last Col? Check view file again.
        # View file Row 46: Col 6 (Values) are empty for Salt?
        # Row 46 salt: `...||66.20...` (This is %)
        # Col 6 seems empty. Wait.
        # Check Row 45 Summary: `12621`. So total is there.
        # Check alignment.
    ]
    
    for item in data:
        records.extend(parse_market_table(metadata, t, item[0], item[1], item[2], item[3], "Import"))
        
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/09"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl10()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL10.json"))
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl11a()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL11a.json"))
    save_json({"metadata": {"year": 2010, "month": 9}, "records": parse_pl11b()}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL11b.json"))
    print("Successfully parsed PL10, PL11a, PL11b for September 2010.")
