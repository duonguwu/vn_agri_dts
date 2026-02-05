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
        "TP Hồ Chí\nMinh": "Hồ Chí Minh"
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
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL1", "source_file": "2010_10_Phuluc_T10_2010_PL1.md"}
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Monthly", "report_date": "2010-10-15"}
    
    # [Item, V10] - Extracted manually from PL1
    data = [
        ["Thu hoạch lúa mùa ở miền Bắc", 892.2],
        ["Đồng bằng sông Hồng", 502.2],
        #["Vùng Bắc Trung bộ", 136.6], # Not usually included in this summary table for PL1, check file. It is!
        ["Vùng Bắc Trung bộ", 136.6],
        ["Gieo cấy lúa mùa ở miền Nam", 665.4],
        ["Đồng bằng sông Cửu Long", 303.5],
        ["Gieo cấy lúa đông xuân ở miền Nam", 200.4],
        ["Đồng bằng sông Cửu Long", 122.1], # Context: DX Nam
        ["Gieo trồng cây vụ đông ở miền Bắc", 351.4],
        ["Ngô", 154.8],
        ["Khoai lang", 30.8],
        ["Đậu tương", 83.5],
        ["Lạc", 6.8],
        ["Rau, đậu các loại", 74.0]
    ]
    
    # Logic to distinguish context
    # Item 1: Thu hoach Lua Mua Mien Bac
    # Item 4: Gieo cay Lua Mua Mien Nam
    # Item 6: Gieo cay Lua DX Mien Nam
    
    for row in data:
        item_name, v10 = row
        loc = "Cả nước"
        if "miền Bắc" in item_name or item_name == "Miền Bắc": loc = "Miền Bắc"
        if "miền Nam" in item_name or item_name == "Miền Nam": loc = "Miền Nam"
        if "Đồng bằng sông Hồng" in item_name: loc = "ĐB sông Hồng"
        if "Vùng Bắc Trung bộ" in item_name: loc = "Bắc Trung Bộ"
        if "Đồng bằng sông Cửu Long" in item_name: loc = "Đồng bằng sông Cửu Long"

        cmd = item_name
        attr = "Area_Planted"
        sub = None
        
        # Determine Context
        if "Thu hoạch lúa mùa" in item_name: # North Context
            cmd = "Lúa"; sub = "Mùa"; attr = "Area_Harvested"
        elif "Đồng bằng sông Hồng" in item_name or ("Vùng Bắc Trung bộ" in item_name): 
            # Context inherited from row 1 (Thu hoach lua mua bac)
            cmd = "Lúa"; sub = "Mùa"; attr = "Area_Harvested"
        elif "Gieo cấy lúa mùa" in item_name:
            cmd = "Lúa"; sub = "Mùa"; attr = "Area_Planted"
        elif "Gieo cấy lúa đông xuân" in item_name:
            cmd = "Lúa"; sub = "Đông Xuân"; attr = "Area_Planted"
        
        # Handle DBSCL which appears twice
        elif "Đồng bằng sông Cửu Long" in item_name:
            # Need to know which context.
            # In data list, idx 5 is Mua, idx 7 is DX.
            # Lazy way: check index in list iteration
            if row == data[5]: # After Gieo cay Lua Mua Nam
                cmd = "Lúa"; sub = "Mùa"; attr = "Area_Planted"
            elif row == data[7]: # After Gieo cay Lua DX Nam
                cmd = "Lúa"; sub = "Đông Xuân"; attr = "Area_Planted"
                
        elif "Gieo trồng cây vụ đông" in item_name: cmd = "Cây vụ đông"; sub = "Tổng số"; attr = "Area_Planted"
        elif item_name in ["Ngô", "Khoai lang", "Đậu tương", "Lạc"]:
             cmd = item_name; sub = "Vụ Đông" # Implicit context from "Gieo trong cay vu dong"
             attr = "Area_Planted"
        elif "Rau, đậu" in item_name: 
             cmd = "Rau đậu các loại"; sub = "Vụ Đông"; attr = "Area_Planted"

        gl = "National" if loc in ["Cả nước", "Miền Bắc", "Miền Nam"] else "Regional"
        
        if v10: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": attr, "value": float(v10), "unit": "1000_ha", "data_type": "Actual"}))

    return records

def parse_pl2():
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL2", "source_file": "2010_10_Phuluc_T10_2010_PL2.md"}
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Monthly", "report_date": "2010-10-15"}
    
    # [Loc, Mua_Planted, Mua_Harvested, VuDong_Total, Ngo, Khoai, KhoaiTay, DauTuong, Lac, RauDau]
    # Note: PL2 header says "Thu Hoach Lua Mua va Gieo Trong Cay Vu Dong"
    # Col 1: Loc
    # Col 2: Lua Mua Gieo Cay
    # Col 3: Lua Mua Thu Hoach
    # Col 4: DT Cay Vu Dong 2010/11 Total
    # Col 5: Ngo
    # Col 6: Khoai lang
    # Col 7: Khoai tay
    # Col 8: Dau tuong
    # Col 9: Lac
    # Col 10: Rau dau
    
    data = [
        ["Miền Bắc", 1191041, 892235, 351353, 154788, 30822, 1051, 83512, 6776, 74004],
        ["ĐB sông Hồng", 578421, 502244, 167043, 50988, 9834, 532, 63540, 1392, 40757],
        ["Hà Nội", 101767, 90000, 54709, 12428, 3246, 162, 28619, 605, 9125],
        ["Hải Phòng", 41657, 40000, 2000, 1500, None, None, None, None, 500],
        ["Vĩnh Phúc", 28530, 24000, 21102, 12297, 1970, None, 3406, 403, 3014],
        ["Bắc Ninh", 36888, 28200, 4292, 1227, 235, 20, 1111, None, 1670],
        ["Hải Dương", 63014, 57561, 15013, 2195, None, 260, 114, None, 9435],
        ["Hưng Yên", 40458, 40415, 12004, 4367, 460, None, 2436, 70, 2380],
        ["Hà Nam", 35519, 35519, 17060, 3902, 396, 90, 11201, 42, 1429],
        ["Nam Định", 80520, 71000, 9309, 9309, None, None, None, None, None], # Ngo 9309?
        ["Thái Bình", 83180, 60000, 18570, 5850, None, None, 6410, None, 5210],
        ["Ninh Bình", 39496, 38564, 16243, 2963, 1281, None, 9943, 272, 1553],
        ["Quảng Ninh", 27392, 16985, 4081, 850, 1146, None, None, None, 1941],
        ["TD và MN phía Bắc", 428336, 253391, 89706, 56795, 9159, 519, 7102, 1484, 14247],
        ["Hà Giang", 25986, 11004, 188, None, None, None, None, None, 188],
        ["Cao Bằng", 25725, 12000, None, None, None, None, None, None, None],
        ["Lào Cai", 19063, 10117, None, None, None, None, None, None, None],
        ["Bắc Cạn", 12920, 12920, 500, 300, None, None, None, None, None],
        ["Lạng Sơn", 33820, 4120, 29542, 20185, 1800, None, 5136, None, 2421],
        ["Tuyên Quang", 25731, 22711, 8047, 5011, 969, None, 709, 47, 1311],
        ["Yên Bái", 23607, 23607, 9400, 6800, 900, 500, None, None, 1200],
        ["Thái Nguyên", 41013, 30561, 10464, 6332, 1970, None, 40, 25, 2097],
        ["Phú Thọ", 33551, 32289, 16118, 11638, 1060, None, 858, 54, 2508],
        ["Bắc Giang", 58055, 38107, 10311, 4234, 1760, None, 15, 1358, 2944],
        ["Lai Châu", 32000, 9585, 220, 200, None, None, 20, None, None],
        ["Điện Biên", 38635, 19260, 209, 18, None, None, 19, 47, 125],
        ["Sơn La", 35000, 5110, 1103, 450, None, None, None, None, 453],
        ["Hoà Bình", 23230, 22000, 3604, 1627, 700, None, 277, None, 1000],
        ["Bắc Trung Bộ", 184284, 136600, 94604, 47005, 11829, 0, 12870, 3900, 19000],
        ["Thanh Hoá", 133759, 130000, 37300, 19000, 4000, None, 3100, 2200, 9000],
        ["Nghệ An", 44000, 5000, 39600, 24500, 5400, None, None, 1700, 8000],
        ["Quảng Trị", 1600, 1600, 17704, 3505, 2429, None, 9770, None, 2000],
        ["Thừa Thiên Huế", 600, None, None, None, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "TD và MN phía Bắc", "Bắc Trung Bộ"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[3])
        if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Cây vụ đông", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", "Vụ Đông"), ("Khoai tây", "Vụ Đông"), ("Đậu tương", "Vụ Đông"), ("Lạc", "Vụ Đông"), ("Rau đậu các loại", "Vụ Đông")]
        for idx, (cmd, sub) in enumerate(items):
            try:
                if idx+4 < len(row):
                    v = normalize_number(row[idx+4])
                    if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
            
    return records

def parse_pl3():
    metadata = {"year": 2010, "month": 10, "appendix_number": "PL3", "source_file": "2010_10_Phuluc_T10_2010_PL3.md"}
    records = []
    t = {"year": 2010, "month": 10, "period_type": "Monthly", "report_date": "2010-10-15"}
    
    # [Loc, Mua_Planted, DX_Planted, Mau_Total, Ngo, Khoai, San]
    # Note: PL3 title "Xuong giong lua mua, lua dong xuan va trong mau"
    # Column mapping:
    # 2: Gieo cay lau mua (Planted Mua)
    # 3: Gieo cay lua DX (Planted DX)
    # 4: DT Gieo trong cay mau Tong so
    # 5: Ngo
    # 6: Khoai lang
    # 7: San (Mi)
    
    data = [
        ["Miền Nam", 665399, 200436, 648016, 316586, 27962, 303468],
        ["D.H Nam Trung Bộ", 86484, 25848, 108289, 35383, 7234, 65672],
        ["TP Đà Nẵng", 3300, None, 1118, 578, 450, 90],
        ["Quảng Nam", 44124, None, 29401, 12001, 4500, 12900],
        ["Quảng Ngãi", 6000, None, 24855, 4160, 1900, 18795],
        ["Bình Định", 23494, None, 21923, 9034, None, 12889],
        ["Phú Yên", 7721, 25848, 21883, 5610, 275, 15998],
        ["Khánh Hoà", 1845, None, 9109, 4000, 109, 5000],
        ["Tây Nguyên", 140731, None, 312666, 175919, 12510, 124237],
        ["Kon Tum", 15899, None, 44762, 7414, 158, 37190],
        ["Gia Lai", 47100, None, 98107, 50826, 1129, 46152],
        ["Đắc Lắc", 54955, None, 109337, 79644, 6627, 23066],
        ["Đắc Nông", 6432, None, 40156, 21400, 3340, 15416],
        ["Lâm Đồng", 16345, None, 20304, 16635, 1256, 2413],
        ["Đông Nam Bộ", 134658, 52535, 184732, 71981, 1742, 111009],
        ["TP Hồ Chí Minh", 10000, 6637, 1007, 1007, None, None],
        ["Ninh Thuận", 13613, None, 6563, 6459, 104, None],
        ["Bình Phước", 9700, None, 30381, 5981, 900, 23500],
        ["Tây Ninh", 54955, 45898, 44167, 5744, None, 38423],
        ["Bình Dương", 5345, None, 3590, 295, 171, 3124],
        ["Đồng Nai", 28599, None, 37797, 25098, 133, 12566],
        ["Bình Thuận", 298, None, 36427, 10797, 234, 25396],
        ["Bà Rịa-V.Tàu", 12148, None, 24800, 16600, 200, 8000],
        ["ĐBS Cửu Long", 303526, 122053, 42329, 33303, 6476, 2550],
        ["Long An", 8811, 39664, 4995, 4995, None, None],
        ["Đồng Tháp", None, None, 4550, 3600, 950, None],
        ["An Giang", 2200, None, 6307, 6187, 30, 90],
        ["Tiền Giang", None, None, 4629, 4120, 250, 259],
        ["Vĩnh Long", None, None, 6730, 3947, 2671, 112],
        ["Bến Tre", 24781, None, 1430, 906, 417, 107],
        ["Kiên Giang", 54915, 24577, None, None, None, None],
        ["Cần Thơ", None, None, 563, 563, None, None],
        ["Hậu Giang", None, 8212, 2209, 2209, None, None],
        ["Trà Vinh", 77025, None, 5913, 3881, 880, 1152],
        ["Sóc Trăng", 17428, 44600, 5003, 2895, 1278, 830],
        ["Bạc Liêu", 63115, 5000, None, None, None, None],
        ["Cà Mau", 55251, None, None, None, None, None]
    ]
    
    regional_list = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    for row in data:
        loc = str(row[0]); gl = "Regional" if loc in regional_list else "Provincial"
        
        v = normalize_number(row[1])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        v = normalize_number(row[2])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        v = normalize_number(row[3])
        if v: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
        
        items = [("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for idx, (cmd, sub) in enumerate(items):
            try:
                v = normalize_number(row[idx+4])
                if v is not None: records.append(create_record(metadata, t, loc, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": sub}, {"attribute": "Area_Planted", "value": v/1.0, "unit": "ha", "data_type": "Actual"}))
            except: pass
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/10"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 10}, "records": parse_pl1()}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL1.json"))
    save_json({"metadata": {"year": 2010, "month": 10}, "records": parse_pl2()}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL2.json"))
    save_json({"metadata": {"year": 2010, "month": 10}, "records": parse_pl3()}, os.path.join(out_dir, "2010_10_Phuluc_T10_2010_PL3.json"))
    print("Successfully parsed PL1-PL3 for October 2010.")
