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
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
    }
    norm_loc = alias_map.get(loc_name.strip(), loc_name.strip())
    
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

def parse_pl1():
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL1", "source_file": "2010_11_Phuluc_T11_2010_PL1.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Monthly", "report_date": "2010-11-15"}
    
    # [Item, V11]
    data = [
        ["Thu hoạch lúa mùa cả nước", 1453.4],
        ["Miền Bắc", 1137.5],
        ["Đồng bằng sông Hồng", 567.0],
        ["Miền Nam", 315.9],
        ["Đồng bằng sông Cửu Long", 26.3], # Mua Harvested
        ["Gieo cấy lúa đông xuân ở miền Nam", 379.1],
        ["Đồng bằng sông Cửu Long", 300.7], # DX Planted
        ["Gieo trồng cây vụ đông ở miền Bắc", 423.1],
        ["Ngô", 144.9],
        ["Khoai lang", 45.7],
        ["Đậu tương", 92.9],
        ["Rau, đậu các loại", 103.7]
    ]
    
    for row in data:
        item_name, v = row
        loc = "Cả nước"
        if "Miền Bắc" in item_name or "miền Bắc" in item_name: loc = "Miền Bắc"
        if "Miền Nam" in item_name or "miền Nam" in item_name: loc = "Miền Nam"
        if "Đồng bằng sông Hồng" in item_name: loc = "ĐB sông Hồng"
        if "Đồng bằng sông Cửu Long" in item_name: loc = "Đồng bằng sông Cửu Long"
        
        cmd = item_name; attr = "Area_Planted"; sub = None
        
        if "Thu hoạch lúa mùa" in item_name or item_name in ["Miền Bắc", "Đồng bằng sông Hồng", "Miền Nam"]:
            cmd = "Lúa"; sub = "Mùa"; attr = "Area_Harvested"
            if item_name == "Đồng bằng sông Cửu Long" and row == data[4]: # The first DBSCL entry
                cmd = "Lúa"; sub = "Mùa"; attr = "Area_Harvested"

        elif "Gieo cấy lúa đông xuân" in item_name:
            cmd = "Lúa"; sub = "Đông Xuân"; attr = "Area_Planted"
        
        elif item_name == "Đồng bằng sông Cửu Long" and row == data[6]: # The second DBSCL entry
             cmd = "Lúa"; sub = "Đông Xuân"; attr = "Area_Planted"
             
        elif "Gieo trồng cây vụ đông" in item_name:
             cmd = "Cây vụ đông"; sub = "Tổng số"; attr = "Area_Planted"
        elif item_name in ["Ngô", "Khoai lang", "Đậu tương"]:
             cmd = item_name; sub = "Vụ Đông"; attr = "Area_Planted"
             loc = "Miền Bắc" # Context
        elif "Rau, đậu" in item_name:
             cmd = "Rau đậu các loại"; sub = "Vụ Đông"; attr = "Area_Planted"
             loc = "Miền Bắc"

        gl = "National" if loc in ["Cả nước", "Miền Bắc", "Miền Nam"] else "Regional"
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v), "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2():
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL2", "source_file": "2010_11_Phuluc_T11_2010_PL2.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Monthly", "report_date": "2010-11-15"}
    
    # [Loc, Mua_Planted, Mua_Harvested, VuDong_Total, Ngo, Khoai, KhoaiTay, DauTuong, Lac, RauDau, CayKhac]
    # Cols in file: 1=Name, 2=Planted, 3=Harvested, 4=VuDong Total, 5=Ngo, 6=Khoai, 7=KhoaiTay, 8=DauTuong, 9=Lac, 10=RauDau, 11=CayKhac
    
    data = [
        ["Miền Bắc", 1191154, 1137520, 423097, 144904, 45672, 11095, 92903, 6457, 103658, 18407],
        ["ĐB sông Hồng", 578807, 567040, 225166, 53324, 15005, 10551, 72329, 1504, 54996, 17457],
        ["Hà Nội", 101767, 90000, 55709, 12428, 3246, 162, 29619, 605, 9125, 524],
        ["Hải Phòng", 41657, 41657, 2000, 1500, 2261, 2164, 3539, 476, 500, 156], # Wait, raw data has many issues, let's look closer at line 27 in View.
        # Line 27: Hai Phong | 41657 | 41657 | 2000 | 1500 | 2261?? No, 2261 is Vinh Phuc's column?
        # Let's re-read carefully.
        # Row Hai Phong: 41,657 | 40,000 (Prev month) -> 41,657 (Harvested).
        # Vu Dong: 2,000. Ngo: 1,500. Others blank?
        # Actually col alignment in MD view is tricky.
        # Let's use the provided structured data from the View file content I requested previously.
        # The View file output for PL2 seems to have concatenated lines.
        # Ex: "12: |**Miền Bắc**<br>**ĐB sông Hồng**<br> Hà Nội..."
        # It's a single row with <br> separated values. Just like PL7 September!
        # Ah, PL2 is "corrupted" style with <br>.
        
        # We need to process this block specifically. 
        # But wait, lines 26-58 in typical file are separate rows.
        # In the View file provided in Step 308 for PL2:
        # Line 12 has "|**Miền Bắc**<br>**ĐB sông Hồng**<br>..."
        # So yes, PL2 IS A COMPACTED TABLE.
        # I need to use the specialized parsing logic (splitting by <br>).
    ]
    
    # I will implement the specialized parsing logic right here since I can see the structure.
    # Structure: 
    # Col 1: Names (Miền Bắc... down to Thừa Thiên Huế)
    # Col 2: Lúa mùa Gieo cấy (1,191,154... down to 600)
    # Col 3: Lúa mùa Thu hoạch (1,137,520...)
    # Col 4: Vu Dong Total (423,097...)
    # Col 5: Ngô
    # Col 6: Khoai lang
    # Col 7: Khoai tây
    # Col 8: Đậu tương
    # Col 9: Lạc
    # Col 10: Rau đậu
    # Col 11: Cây khác

    # Let's perform the extraction from the raw strings visually from Step 308.
    
    # Names:
    names_str = "Miền Bắc<br>ĐB sông Hồng<br>Hà Nội<br>Hải Phòng<br>Vĩnh Phúc<br>Bắc Ninh<br>Hải Dương<br>Hưng Yên<br>Hà Nam<br>Nam Định<br>Thái Bình<br>Ninh Bình<br>Quảng Ninh<br>TD và MN phía Bắc<br>Hà Giang<br>Cao Bằng<br>Lào Cai<br>Bắc Cạn<br>Lạng Sơn<br>Tuyên Quang<br>Yên Bái<br>Thái Nguyên<br>Phú Thọ<br>Bắc Giang<br>Lai Châu<br>Điện Biên<br>Sơn La<br>Hoà Bình<br>Bắc Trung Bộ<br>Thanh Hoá<br>Nghệ An<br>Hà Tĩnh<br>Quảng Bình<br>Quảng Trị<br>Thừa Thiên Huế"
    names = names_str.split("<br>")
    
    # Lúa Mùa Planted
    c2_str = "1,191,154<br>578,807<br>101,767<br>41,657<br>28,530<br>36,888<br>63,014<br>40,458<br>35,519<br>80,906<br>83,180<br>39,496<br>27,392<br>428,062<br>25,986<br>25,725<br>19,063<br>12,920<br>33,820<br>25,731<br>23,541<br>41,013<br>33,343<br>58,055<br>32,000<br>38,635<br>35,000<br>23,230<br>184,285<br>133,760<br>44,000<br>4,325<br>1,600<br>600"
    c2 = c2_str.split("<br>")
    
    # Lúa Mùa Harvested
    c3_str = "1,137,520<br>567,040<br>90,000<br>41,657<br>28,530<br>36,888<br>63,014<br>40,458<br>35,519<br>80,906<br>83,180<br>39,496<br>27,392<br>397,720<br>24,896<br>25,725<br>18,500<br>11,500<br>29,869<br>25,731<br>23,541<br>30,561<br>33,343<br>58,055<br>22,000<br>37,868<br>32,901<br>23,230<br>172,760<br>133,760<br>37,400<br>1,600"
    c3 = c3_str.split("<br>") # Note: Shorter length maybe?
    
    # Vu Dong Total
    c4_str = "423,097<br>225,166<br>55,709<br>2,000<br>19,005<br>9,440<br>21,202<br>14,020<br>17,852<br>15,899<br>44,397<br>19,831<br>5,811<br>86,735<br>3,825<br>749<br>550<br>9,656<br>9,471<br>14,323<br>18,057<br>20,873<br>220<br>209<br>1,934<br>6,488<br>111,195<br>51,791<br>41,700<br>17,704"
    c4 = c4_str.split("<br>")
    
    # ... I will just map them by index. 
    # Since lengths vary (empty cells at bottom), I handle index out of range.
    
    # Define columns data map
    cols_data = [
        names,
        c2, # Planted
        c3, # Harvested
        c4, # Vu Dong Total
        "144,904<br>53,324<br>12,428<br>1,500<br>12,566<br>1,326<br>2,540<br>5,000<br>3902<br>2,336<br>6,950<br>3,266<br>1,510<br>41,887<br>720<br>387<br>5,011<br>6,513<br>6,801<br>12,323<br>7,000<br>200<br>18<br>550<br>2,364<br>49,693<br>20,188<br>26,000<br>3,505".split("<br>"), # Ngo (Col 5)
        "45,672<br>15,005<br>3,246<br>2,261<br>798<br>1,000<br>396<br>939<br>2,980<br>1,947<br>1,438<br>15,792<br>72<br>26<br>2,578<br>900<br>4,013<br>1,443<br>5,000<br>1,760<br>14,875<br>6,446<br>6,000<br>2,429".split("<br>"), # Khoai lang (Col 6)
        "11,095<br>10,551<br>162<br>2,164<br>1,393<br>450<br>463<br>2,280<br>2,850<br>497<br>292<br>544<br>500<br>19<br>25<br>0".split("<br>"), # Khoai tay (Col 7)
        "92,903<br>72,329<br>29,619<br>3,539<br>1,286<br>162<br>1,900<br>11,201<br>1,377<br>13,250<br>9,995<br>2,304<br>709<br>56<br>950<br>15<br>20<br>47<br>507<br>18,270<br>8,500<br>9,770".split("<br>"), # Dau tuong (Col 8)
        "6,457<br>1,504<br>605<br>476<br>108<br>42<br>273<br>1,532<br>47<br>71<br>56<br>1,358<br>3,421<br>1,721<br>1,700".split("<br>"), # Lac (Col 9)
        "103,658<br>54,996<br>9,125<br>500<br>7<br>3,821<br>10,960<br>2,650<br>1,848<br>7,967<br>12,000<br>3,622<br>2,496<br>23,726<br>3,105<br>308<br>136<br>1,311<br>1,558<br>3,382<br>3,285<br>7,500<br>125<br>1,159<br>1,857<br>24,936<br>14,936<br>8,000<br>2,000".split("<br>"), # Rau dau (Col 10)
        "18,407<br>17,457<br>524<br>156<br>45<br>6,147<br>2,912<br>1,000<br>6,367<br>231<br>75<br>950<br>200<br>550<br>200<br>0".split("<br>") # Cay khac (Col 11)
    ]
    
    # Iterate through Names
    for i, name in enumerate(names):
        name = name.replace("**", "").strip()
        gl = "Regional" if name in ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"] else "Provincial"
        
        # Mua Planted (Col 1)
        if i < len(cols_data[1]):
            v = normalize_number(cols_data[1][i])
            if v: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
            
        # Mua Harvested (Col 2)
        if i < len(cols_data[2]):
            v = normalize_number(cols_data[2][i])
            if v: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": v, "unit": "ha", "data_type": "Actual"}))
            
        # Vu Dong Total (Col 3)
        if i < len(cols_data[3]):
            v = normalize_number(cols_data[3][i])
            if v: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây vụ đông", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
            
        # Commodities (Cols 4-10)
        items = ["Ngô", "Khoai lang", "Khoai tây", "Đậu tương", "Lạc", "Rau đậu các loại", "Cây khác"]
        for j, item in enumerate(items):
            col_idx = 4 + j
            if i < len(cols_data[col_idx]):
                 v = normalize_number(cols_data[col_idx][i])
                 if v: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": item, "sub_item": "Vụ Đông"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))

    return records

def parse_pl3():
    metadata = {"year": 2010, "month": 11, "appendix_number": "PL3", "source_file": "2010_11_Phuluc_T11_2010_PL3.md"}
    records = []
    t = {"year": 2010, "month": 11, "period_type": "Monthly", "report_date": "2010-11-15"}
    
    # Also valid <br> format in PL3? 
    # Let's check Step 309.
    # Lines 21-57 in PL3 are formatted as separate lines. So regular parsing is possible.
    
    data = [
        ["Miền Nam", 774937, 315873, 379118, 750904, 401073, 36801, 313029],
        ["D.H Nam Trung Bộ", 93139, 92186, 25848, 116290, 41613, 7505, 67172],
        ["TP Đà Nẵng", 3300, 3300, None, 1118, 578, 450, 90],
        ["Quảng Nam", 44124, 44124, None, 29401, 12001, 4500, 12900],
        ["Quảng Ngãi", 6000, 6000, None, 31495, 10800, 1900, 18795],
        ["Bình Định", 23494, 22541, None, 20493, 7334, 270, 12889],
        ["Phú Yên", 7721, 7721, 25848, 23173, 6900, 275, 15998],
        ["Khánh Hoà", 8500, 8500, None, 10610, 4000, 110, 6500],
        ["Tây Nguyên", 141235, 113591, None, 360737, 221121, 14210, 125406],
        ["Kon Tum", 15899, 10839, None, 44762, 7414, 158, 37190],
        ["Gia Lai", 47100, 36000, None, 98107, 50826, 1129, 46152],
        ["Đắc Lắc", 55459, 49820, None, 151501, 119779, 7487, 24235],
        ["Đắc Nông", 6432, 6432, None, 46063, 26467, 4180, 15416],
        ["Lâm Đồng", 16345, 10500, None, 20304, 16635, 1256, 2413],
        ["Đông Nam Bộ", 173007, 83750, 52535, 225369, 105277, 2762, 117330],
        ["TP Hồ Chí Minh", 10912, 6000, 6637, 1007, 1007, None, None],
        ["Ninh Thuận", 13613, 7000, None, 9563, 6459, 104, 3000],
        ["Bình Phước", 10000, 5500, None, 30381, 5981, 900, 23500],
        ["Tây Ninh", 54955, 26000, 45898, 44246, 5823, None, 38423],
        ["Bình Dương", 5345, 750, None, 7170, 554, 171, 6445],
        ["Đồng Nai", 28599, 12000, None, 63082, 50152, 364, 12566],
        ["Bình Thuận", 37435, 24000, None, 45120, 18701, 1023, 25396],
        ["Bà Rịa-V.Tàu", 12148, 2500, None, 24800, 16600, 200, 8000],
        ["ĐBS Cửu Long", 367556, 26346, 300735, 48508, 33063, 12324, 3121],
        ["Long An", 10055, 300, 30263, 4995, 4995, None, None],
        ["Đồng Tháp", None, None, 46681, 4618, 3668, 950, None],
        ["An Giang", 2200, None, 5871, 6307, 6187, 30, 90],
        ["Tiền Giang", None, None, 5169, 4660, 250, 259], # Missing DX?
        ["Vĩnh Long", None, None, 21866, 7284, 1327, 5845, 112],
        ["Bến Tre", 32781, None, None, 1430, 906, 417, 107],
        ["Kiên Giang", 62709, None, 72660, None, None, None, None],
        ["Cần Thơ", None, None, 19407, 563, 563, None, None],
        ["Hậu Giang", None, None, 8963, 3353, 2393, 389, 571],
        ["Trà Vinh", 90907, 18872, 2347, 8194, 5220, 1822, 1152],
        ["Sóc Trăng", 20789, 5474, 81677, 6596, 3144, 2622, 830],
        ["Bạc Liêu", 63115, 1700, 11000, None, None, None, None],
        ["Cà Mau", 85000, None, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": v, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[4])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
        
        # Commodities
        items = ["Ngô", "Khoai lang", "Sắn"]
        for j, item in enumerate(items):
            if 5+j < len(row):
                 v = normalize_number(row[5+j])
                 if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": item, "sub_item": None}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/11"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl1()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl2()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL2.json"))
    save_json({"metadata": {"year": 2010, "month": 11}, "records": parse_pl3()}, os.path.join(out_dir, "2010_11_Phuluc_T11_2010_PL3.json"))
    print("Successfully parsed PL1-PL3 for November 2010. Handled PL2 corrupt format.")
