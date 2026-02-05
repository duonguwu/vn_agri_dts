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
    # Enrichment with region map
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

def parse_pl1_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL1", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL1.md"}
    records = []
    # Item, Sub, v08, v09, c_gc, c_yoy, loc, geo, attr
    rows = [
        ["Lúa", "Mùa", "704.7", "885.1", "74.6", "125.6", "Miền Bắc", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "346.8", "441.1", "80.0", "127.2", "Đồng bằng sông Hồng", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "135.6", "155.8", "85.3", "114.9", "Bắc Trung Bộ", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "774.5", "759.5", None, "98.1", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Mùa", "411.3", "407.5", None, "99.1", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "234.9", "221.6", None, "94.3", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "160.3", "144.4", None, "90.1", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted"],
        ["Cây vụ đông", "Tổng số", "337.4", "331.7", None, "98.3", "Miền Bắc", "Regional", "Area_Planted"],
        ["Ngô", "Vụ đông", "143.4", "137.3", None, "95.7", "Miền Bắc", "Regional", "Area_Planted"],
        ["Khoai lang", "Vụ đông", "35.7", "30.8", None, "86.2", "Miền Bắc", "Regional", "Area_Planted"],
        ["Đậu tương", "Vụ đông", "68.8", "72.8", None, "105.9", "Miền Bắc", "Regional", "Area_Planted"],
        ["Lạc", "Vụ đông", "8.1", "7.0", None, "86.3", "Miền Bắc", "Regional", "Area_Planted"],
        ["Rau, đậu các loại", "Vụ đông", "68.7", "69.5", None, "101.3", "Miền Bắc", "Regional", "Area_Planted"],
    ]
    for r in rows:
        item, sub, v08, v09, c_gc, c_yoy, loc, geo, attr = r
        t09 = {"year": 2009, "month": 10, "period_type": "Cumulative"}
        i = {"sector": "Cultivation", "commodity": item, "sub_item": sub}
        
        val09 = normalize_number(v09)
        if val09:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"} if c_yoy else None
            records.append(create_record(metadata, t09, loc, geo, i, {"attribute": attr, "value": val09, "unit": "1000_ha", "data_type": "Actual"}, comp))
        
        val08 = normalize_number(v08)
        if val08:
            records.append(create_record(metadata, {"year": 2008, "month": 10, "period_type": "Cumulative"}, loc, geo, i, {"attribute": attr, "value": val08, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl2_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL2", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL2.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    # Loc, Mùa_GC, Mùa_TH, NS_DựKiến, VD_Total, Ngô, K.lang, Đ.tương, Lạc, Rau_Đậu
    pl2_data = [
        ["Miền Bắc", "1185883", "885128", None, "331728", "137277", "30780", "72846", "7004", "69526"],
        ["ĐB sông Hồng", "551892", "441083", None, "177256", "50126", "7693", "67683", "1272", "36828"],
        ["Hà Nội", "102889", "98487", None, "55186", "12284", "2570", "30668", "539", "7826"],
        ["Hải Phòng", "42254", "34840", "57", "5247", "1925", None, None, None, "601"],
        ["Vĩnh Phúc", "28986", "22740", "51", "21372", "12838", "2141", "3900", "366", "2127"],
        ["Bắc Ninh", "37338", "33000", "57", "5010", "1288", "156", "1906", "14", "1647"],
        ["Hải Dương", "62774", "56516", None, "16091", "2885", None, "197", None, "9271"],
        ["Hưng Yên", "40671", "39870", "61", "12657", "4396", "443", "2641", "81", "4087"],
        ["Hà Nam", "35403", "35403", "57", "17450", "3396", None, "11010", None, "2039"],
        ["Nam Định", "78602", "51700", None, "7146", "1681", None, "593", None, "1185"],
        ["Thái Bình", "83164", "33500", "70", "20770", "6180", "940", "7830", None, "5650"],
        ["Ninh Bình", "39811", "35027", "56", "16327", "3253", "1443", "8939", "272", "2396"],
        ["Đông Bắc", "328842", "235483", None, "60757", "36211", "10155", "1005", "1566", "11697"],
        ["Hà Giang", "25600", "21006", None, None, None, None, None, None, None],
        ["Cao Bằng", "25516", "13283", None, None, None, None, None, None, None],
        ["Lào Cai", "19570", "10240", "42", "290", None, None, None, None, "290"],
        ["Bắc Cạn", "14002", "14002", "42", "602", "378", None, None, None, "224"],
        ["Lạng Sơn", "31200", "4870", None, None, None, None, None, None, None],
        ["Tuyên Quang", "25816", "25816", "57", "7058", "5123", "1123", "613", "51", "148"],
        ["Yên Bái", "23896", "23896", "40", "7886", "6382", "677", "6", None, "784"],
        ["Thái Nguyên", "41500", "28820", None, "8204", "5658", "1500", "26", None, "1020"],
        ["Phú Thọ", "34000", "32123", "48", "15069", "10912", "1340", "255", None, "2563"],
        ["Bắc Giang", "59442", "44702", "49", "17732", "6930", "4169", "106", "1515", "4926"],
        ["Quảng Ninh", "28300", "16725", None, "3917", "829", "1346", None, None, "1742"],
        ["Tây Bắc", "122557", "52726", None, "5025", "2153", "838", "522", "0", "1512"],
        ["Lai Châu", "24682", "15000", "33", "239", "210", None, "29", None, None],
        ["Điện Biên", "37025", "12686", "32", "43", "23", "20", None, None, None],
        ["Sơn La", "36436", "5678", "27", "893", "400", None, None, None, "493"],
        ["Hoà Bình", "24414", "19362", "50", "3850", "1520", "818", "493", None, "1019"],
        ["Bắc Trung Bộ", "182592", "155836", None, "88690", "48788", "12094", "3635", "4166", "19489"],
        ["Thanh Hoá", "136836", "136836", "53", "42672", "20788", "4594", "3635", "1666", "11989"],
        ["Nghệ An", "33156", "18000", "38", "45500", "28000", "7500", None, "2500", "7500"],
        ["Hà Tĩnh", "6500", None, None, None, None, None, None, None, None],
        ["Quảng Bình", "1000", "1000", None, "518", None, None, None, None, None],
        ["Quảng Trị", "4500", None, None, None, None, None, None, None, None],
        ["Thừa Thiên Huế", "600", None, None, None, None, None, None, None, None],
    ]
    for row in pl2_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 10, "period_type": "Cumulative", "report_date": "2009-10-15"}
        
        # 1. Lúa Mùa
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vgc/10.0/100.0, "unit": "1000_ha", "data_type": "Actual"})) # div 1000
        vth = normalize_number(row[2])
        if vth: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": vth/10.0/100.0, "unit": "1000_ha", "data_type": "Actual"}))
        vns = normalize_number(row[3])
        if vns: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Yield", "value": vns, "unit": "quintal_per_ha", "data_type": "Actual"}))
        
        # 2. Cây vụ đông
        items = [("Cây vụ đông", "Tổng số"), ("Ngô", "Vụ đông"), ("Khoai lang", "Vụ đông"), ("Đậu tương", "Vụ đông"), ("Lạc", "Vụ đông"), ("Rau, đậu các loại", "Vụ đông")]
        for idx, it in enumerate(items):
            va = normalize_number(row[idx+4])
            if va is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": it[0], "sub_item": it[1]}, {"attribute": "Area_Planted", "value": va/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl3_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL3", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL3.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    # Loc, Mùa_GC, ĐX_GC, Màu_Total, Ngô, K.lang, Sắn, Khác
    pl3_data = [
        ["Miền Nam", "759524", "221623", "687237", "345748", "30087", "305893", "14375"],
        ["D.H Nam Trung Bộ", "87820", "26712", "104342", "38545", "4723", "60433", "641"],
        ["TP Đà Nẵng", "2225", None, "1187", "664", "437", "86", None],
        ["Quảng Nam", "45128", None, "28851", "12051", "3700", "13100", None],
        ["Quảng Ngãi", "5900", None, "21875", "7818", "200", "13857", None],
        ["Bình Định", "25505", None, "18265", "7712", None, "10553", None],
        ["Phú Yên", "7262", "26712", "22634", "6000", "226", "16125", "283"],
        ["Khánh Hoà", "1800", None, "11530", "4300", "160", "6712", "358"],
        ["Tây Nguyên", "131280", "0", "342862", "208881", "12185", "121796", "0"],
        ["Kon Tum", "16700", None, "43637", "7630", "935", "35072", None],
        ["Gia Lai", "46843", None, "101976", "49116", "1165", "51695", None],
        ["Đắc Lắc", "44167", None, "142344", "113937", "6471", "21936", None],
        ["Đắc Nông", "7000", None, "34975", "21575", "2100", "11300", None],
        ["Lâm Đồng", "16570", None, "19930", "16623", "1514", "1793", None],
        ["Đông Nam Bộ", "132938", "50539", "198721", "70449", "2246", "121158", "4868"],
        ["TP Hồ Chí Minh", "13500", "6967", "1100", "1100", None, None, None],
        ["Ninh Thuận", "6800", None, "10900", "7900", None, "3000", None],
        ["Bình Phước", "9900", None, "31808", "6672", "867", "24171", "98"],
        ["Tây Ninh", "55886", "43572", "49731", "7207", None, "42524", None],
        ["Bình Dương", "4230", None, "7351", "242", "385", "2447", "4277"],
        ["Đồng Nai", "29780", None, "41258", "25337", "374", "15429", "118"],
        ["Bình Thuận", "300", None, "31141", "4671", "391", "25704", "375"],
        ["Bà Rịa-V.Tàu", "12542", None, "25432", "17320", "229", "7883", None],
        ["ĐBS Cửu Long", "407486", "144372", "41312", "27873", "10933", "2506", "8866"],
        ["Long An", "8233", "41990", "900", "900", None, None, None],
        ["Đồng Tháp", None, None, "6278", "4234", "1187", None, "857"],
        ["An Giang", "2100", None, "6799", "6179", "120", "500", None],
        ["Tiền Giang", None, None, "6426", "4654", None, "153", "1619"],
        ["Vĩnh Long", None, None, "12375", "1266", "5211", "156", "5742"],
        ["Bến Tre", "33806", None, "1394", "818", "149", "299", "128"],
        ["Kiên Giang", "56130", "15428", "700", None, "700", None, None],
        ["Cần Thơ", None, None, "629", "629", None, None, None],
        ["Hậu Giang", "45552", "7022", "2071", "1551", None, None, "520"],
        ["Trà Vinh", "91634", None, "7279", "4871", "1606", "802", None],
        ["Sóc Trăng", "25899", "74897", "4727", "2171", "1960", "596", None],
        ["Bạc Liêu", "67933", "5035", "600", "600", None, None, None],
        ["Cà Mau", "76199", None, "0", None, None, None, None],
    ]
    for row in pl3_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 10, "period_type": "Cumulative", "report_date": "2009-10-15"}
        
        # 1. Lúa Mùa
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vgc/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa Đông Xuân
        vdx = normalize_number(row[2])
        if vdx: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": vdx/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Màu
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for idx, it in enumerate(items):
            va = normalize_number(row[idx+3])
            if va is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": it[0], "sub_item": it[1]}, {"attribute": "Area_Planted", "value": va/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/10"
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    save_json(parse_pl1_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL1.json"))
    save_json(parse_pl2_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL2.json"))
    save_json(parse_pl3_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL3.json"))
    print("Successfully parsed PL1, PL2, PL3 for Oct 2009 with Region Mapping.")
