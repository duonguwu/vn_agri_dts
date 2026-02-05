import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
    REGION_DATA = json.load(f)

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|": return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    if loc_name in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][loc_name]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][loc_name]["region_name"]
    elif loc_name in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][loc_name]
        geo_context["region_name"] = loc_name
        
    record = {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": geo_context,
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata
    }
    if comp: record["comparison_context"] = comp
    return record

def parse_pl1_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL1", "source_file": "2009_09_PHULUC_T09_2009_PL1.md"}
    records = []
    
    # Rows: Item, Sub, val08, val09, comp_gc, comp_yoy, loc, geo_level, attr
    rows = [
        ["Lúa", "Hè Thu", "1781.7", "1785.6", "87.6", "100.2", "Miền Nam", "Regional", "Area_Harvested"],
        ["Lúa", "Hè Thu", "1514.1", "1517.6", "86.3", "100.2", "Đồng bằng sông Cửu Long", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "1661.1", "1704.2", None, "102.6", "Cả nước", "National", "Area_Planted"],
        ["Lúa", "Mùa", "1205.4", "1237.2", None, "102.6", "Miền Bắc", "Regional", "Area_Planted"],
        ["Lúa", "Mùa", "556.7", "552.0", None, "99.2", "Đồng bằng sông Hồng", "Regional", "Area_Planted"],
        ["Lúa", "Mùa", "480.2", "491.6", None, "102.4", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Mùa", "173.1", "188.6", None, "109.0", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted"],
        ["Màu lương thực", "Tổng số", "1576.9", "1492.2", None, "94.6", "Cả nước", "National", "Area_Planted"],
        ["Ngô", None, "967.6", "940.6", None, "97.2", "Cả nước", "National", "Area_Planted"],
        ["Khoai lang", None, "134.5", "121.4", None, "90.3", "Cả nước", "National", "Area_Planted"],
        ["Sắn", None, "466.7", "425.2", None, "91.1", "Cả nước", "National", "Area_Planted"],
        ["Cây công nghiệp ngắn ngày", "Tổng số", "643.3", "657.2", None, "102.2", "Cả nước", "National", "Area_Planted"],
        ["Lạc", None, "242.9", "255.6", None, "105.2", "Cả nước", "National", "Area_Planted"],
        ["Đậu tương", None, "183.3", "191.5", None, "104.5", "Cả nước", "National", "Area_Planted"],
        ["Rau, đậu các loại", "Tổng số", "661.3", "665.2", None, "100.6", "Cả nước", "National", "Area_Planted"],
    ]

    for r in rows:
        item, sub, v08, v09, c_gc, c_yoy, loc, geo, attr = r
        t09 = {"year": 2009, "month": 9, "period_type": "Cumulative"}
        i = {"sector": "Cultivation", "commodity": item, "sub_item": sub}
        
        # 2009 record with comparison data
        val09 = normalize_number(v09)
        if val09:
            comp = None
            if normalize_number(c_yoy):
                comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, t09, loc, geo, i, {"attribute": attr, "value": val09, "unit": "1000_ha", "data_type": "Actual"}, comp))
        
        # 2008 record
        val08 = normalize_number(v08)
        if val08:
            t08 = {"year": 2008, "month": 9, "period_type": "Cumulative"}
            records.append(create_record(metadata, t08, loc, geo, i, {"attribute": attr, "value": val08, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl2_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL2", "source_file": "2009_09_PHULUC_T09_2009_PL2.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    pl2_data = [
        ["Miền Bắc", "1237209", "119882", "160267", "911720", "672380", "32552", "112832", "126508"],
        ["ĐB sông Hồng", "552030", "75855", None, "103736", "75863", "4912", "23173", "4700"],
        ["Hà Nội", "102281", "71597", None, "29509", "24109", "3000", "4700", "700"],
        ["Hải Phòng", "43000", None, None, "8380", "5000", None, "3380", None],
        ["Vĩnh Phúc", "28986", "753", None, "11666", "8493", None, "1173", "2000"],
        ["Bắc Ninh", "37338", None, None, "5704", "4704", None, "1000", None],
        ["Hải Dương", "62774", None, None, "4500", "3000", None, "1500", None],
        ["Hưng Yên", "40671", None, None, "8600", "7000", None, "1600", None],
        ["Hà Nam", "35403", None, None, "6445", "5455", None, "990", None],
        ["Nam Định", "78602", None, None, "6216", "4116", None, "2100", None],
        ["Thái Bình", "83164", None, None, "11624", "8074", "1000", "3550", None],
        ["Ninh Bình", "39811", "3505", None, "11092", "5912", "912", "3180", "2000"],
        ["Đông Bắc", "362011", "3957", None, "331443", "247138", "7991", "37933", "46372"],
        ["Hà Giang", "25600", None, None, "49609", "49159", None, "450", None],
        ["Cao Bằng", "25239", None, None, "23824", "23624", None, "100", "100"],
        ["Lào Cai", "19170", "3957", None, "37032", "28516", "7035", "516", "8000"],
        ["Bắc Cạn", "13851", None, None, "18534", "16130", "256", "356", "2048"],
        ["Lạng Sơn", "31200", None, None, "27982", "22782", None, "1200", "4000"],
        ["Tuyên Quang", "25816", None, None, "18242", "13742", None, "4500", None],
        ["Yên Bái", "41220", None, None, "41719", "21995", None, "4724", "15000"],
        ["Thái Nguyên", "41500", None, None, "35310", "22087", None, "9076", "4147"],
        ["Phú Thọ", "34000", None, None, "35477", "25775", "700", "3098", "6604"],
        ["Bắc Giang", "59442", None, None, "28689", "13715", None, "9574", "5400"],
        ["Quảng Ninh", "44973", None, None, "15025", "9613", None, "4339", "1073"],
        ["Tây Bắc", "128811", None, None, "256050", "224789", None, "7625", "23636"],
        ["Lai Châu", "33000", None, None, "17726", "17726", None, "0", None],
        ["Điện Biên", "35184", None, None, "32080", "32080", None, "0", None],
        ["Sơn La", "36417", None, None, "155138", "132296", None, "506", "22336"],
        ["Hoà Bình", "24210", None, None, "51106", "42687", None, "7119", "1300"],
        ["Bắc Trung Bộ", "194357", "40070", "160267", "220491", "124590", "19649", "44101", "51800"],
        ["Thanh Hoá", "136757", "40070", None, "73307", "46146", "19649", "12161", "15000"],
        ["Nghệ An", "45000", None, "59000", "82656", "58226", None, "12430", "12000"],
        ["Hà Tĩnh", "6500", None, "41910", "24955", "10145", None, "12010", "2800"],
        ["Quảng Bình", "1000", None, "16435", "13000", "5000", None, "1000", "7000"],
        ["Quảng Trị", "4500", None, "19000", "14573", "3073", None, "2500", "9000"],
        ["Thừa Thiên Huế", "600", None, "23922", "12000", "2000", None, "4000", "6000"],
    ]
    for row in pl2_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 9, "period_type": "Cumulative", "report_date": "2009-09-15"}
        
        # 1. Lúa Mùa Gieo cấy
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vgc / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa Mùa Thu hoạch
        vth = normalize_number(row[2])
        if vth: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": vth / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Lúa Hè Thu Thu hoạch
        vht = normalize_number(row[3])
        if vht: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": vht / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 4. Màu items
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Ngô", "Ngô đông"), ("Khoai lang", None), ("Sắn", None)]
        for idx, (c, s) in enumerate(items):
            v_alt = normalize_number(row[idx+4])
            if v_alt is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v_alt / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}

def parse_pl3_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL3", "source_file": "2009_09_PHULUC_T09_2009_PL3.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    pl3_data = [
        ["Miền Bắc", "387429", "164772", "174160", "38556", "9941", "381223"],
        ["ĐB sông Hồng", "111266", "73241", "35154", "871", "2000", "163401"],
        ["Hà Nội", "43700", "35500", "8200", None, None, "25136"],
        ["Hải Phòng", "2345", "200", "145", None, "2000", "20324"],
        ["Vĩnh Phúc", "8157", "1268", "6826", "63", None, "8029"],
        ["Bắc Ninh", "4564", "3348", "1216", None, None, "25023"],
        ["Hải Dương", "1205", "205", "1000", None, None, "25000"],
        ["Hưng Yên", "5100", "3600", "1500", None, None, "13313"],
        ["Hà Nam", "10897", "9877", "1020", None, None, "6100"],
        ["Nam Định", "11519", "3500", "8019", None, None, "15400"],
        ["Thái Bình", "10272", "7602", "2670", None, None, "18058"],
        ["Ninh Bình", "13507", "8141", "4558", "808", None, "7018"],
        ["Đông Bắc", "109026", "49752", "48692", "2825", "7757", "95006"],
        ["Hà Giang", "24543", "19543", "5000", None, None, "10000"],
        ["Cao Bằng", "11052", "6100", "1672", "1460", "1820", "5000"],
        ["Lào Cai", "7738", "6565", "1052", None, "121", "5994"],
        ["Bắc Cạn", "3373", "2010", "462", "165", "736", "2476"],
        ["Lạng Sơn", "8125", "1000", "2045", "300", "4780", "6506"],
        ["Tuyên Quang", "8666", "3904", "4762", None, None, "4534"],
        ["Yên Bái", "5883", "3451", "2432", None, None, "7170"],
        ["Thái Nguyên", "7621", "2541", "5080", None, None, "12685"],
        ["Phú Thọ", "12052", "1552", "10300", "200", None, "10000"],
        ["Bắc Giang", "15530", "2076", "12854", "300", "300", "20141"],
        ["Quảng Ninh", "4443", "1010", "3033", "400", None, "10500"],
        ["Tây Bắc", "48964", "26535", "10801", "11628", "0", "18004"],
        ["Lai Châu", "3642", "2315", "1327", None, None, "1500"],
        ["Điện Biên", "15055", "12987", "2068", None, None, "0"],
        ["Sơn La", "11120", "6742", "1095", "3283", None, "3580"],
        ["Hoà Bình", "19147", "4491", "6311", "8345", None, "12924"],
        ["Bắc Trung Bộ", "118173", "15244", "79513", "23232", "184", "104812"],
        ["Thanh Hoá", "34596", "4047", "16837", "13712", None, "45600"],
        ["Nghệ An", "37402", "1000", "26902", "9500", None, "29550"],
        ["Hà Tĩnh", "31497", "10197", "21300", None, None, "15662"],
        ["Quảng Bình", "5022", None, "5022", None, None, "7000"],
        ["Quảng Trị", "5575", None, "5452", "20", "103", "2000"],
        ["Thừa Thiên Huế", "4081", None, "4000", None, "81", "5000"],
    ]
    for row in pl3_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 9, "period_type": "Cumulative"}
        items = [("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Mía", "Trồng mới"), ("Thuốc lá", None), ("Rau, đậu các loại", None)]
        for idx, (c, s) in enumerate(items):
            v = normalize_number(row[idx+1])
            if v is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/09"
    save_json(parse_pl1_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL1.json"))
    save_json(parse_pl2_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL2.json"))
    save_json(parse_pl3_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL3.json"))
    print("Fixed Batch 1 with region map integration.")
