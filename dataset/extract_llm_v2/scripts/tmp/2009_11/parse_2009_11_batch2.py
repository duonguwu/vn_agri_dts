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
    elif loc_name == "Cả nước":
        geo_context["region_id"] = "NATIONAL"
        geo_context["region_name"] = "Cả nước"
    
    # Handle aliases
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ"
    }
    if loc_name in alias_map:
        real_name = alias_map[loc_name]
        geo_context["region_id"] = REGION_DATA["regions"].get(real_name)
        geo_context["region_name"] = real_name

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

def parse_pl3_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL3", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL3.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    pl3_data = [
        ["Miền Nam", "825052", "320777", "332735", "693121", "351632", "30087", "305893", "14375"],
        ["D.H Nam Trung Bộ", "92020", "92020", "65303", "104342", "38545", "4723", "60433", "641"],
        ["TP Đà Nẵng", "2225", "2225", None, "1187", "664", "437", "86", None],
        ["Quảng Nam", "45128", "45128", "3051", "28851", "12051", "3700", "13100", None],
        ["Quảng Ngãi", "5900", "5900", "9640", "21875", "7818", "200", "13857", None],
        ["Bình Định", "25505", "25505", "45900", "18265", "7712", None, "10553", None],
        ["Phú Yên", "7262", "7262", "6712", "22634", "6000", "226", "16125", "283"],
        ["Khánh Hoà", "6000", "6000", None, "11530", "4300", "160", "6712", "358"],
        ["Tây Nguyên", "131280", "115098", "2929", "348746", "214765", "12185", "121796", "0"],
        ["Kon Tum", "16700", "16700", None, "43637", "7630", "935", "35072", None],
        ["Gia Lai", "46843", "36705", None, "107860", "55000", "1165", "51695", None],
        ["Đắc Lắc", "44167", "44167", None, "142344", "113937", "6471", "21936", None],
        ["Đắc Nông", "7000", "7000", None, "34975", "21575", "2100", "11300", None],
        ["Lâm Đồng", "16570", "10526", "2929", "19930", "16623", "1514", "1793", None],
        ["Đông Nam Bộ", "175508", "81875", "40695", "198721", "70449", "2246", "121158", "4868"],
        ["TP Hồ Chí Minh", "15500", "6220", "6967", "1100", "1100", None, None, None],
        ["Ninh Thuận", "8970", "7000", "1100", "10900", "7900", None, "3000", None],
        ["Bình Phước", "9900", "5428", None, "31808", "6672", "867", "24171", "98"],
        ["Tây Ninh", "57886", "25980", "9000", "49731", "7207", None, "42524", None],
        ["Bình Dương", "4230", "600", "97", "7351", "242", "385", "2447", "4277"],
        ["Đồng Nai", "29780", "11000", "5700", "41258", "25337", "374", "15429", "118"],
        ["Bình Thuận", "36700", "24000", "15741", "31141", "4671", "391", "25704", "375"],
        ["Bà Rịa-V.Tàu", "12542", "1647", "2090", "25432", "17320", "229", "7883", None],
        ["ĐBS Cửu Long", "426244", "31784", "223808", "41312", "27873", "10933", "2506", "8866"],
        ["Long An", "12997", "2021", "61175", "900", "900", None, None, None],
        ["Đồng Tháp", None, None, "22942", "6278", "4234", "1187", None, "857"],
        ["An Giang", "7637", None, None, "6799", "6179", "120", "500", None],
        ["Tiền Giang", None, None, "175", "6426", "4654", None, "153", "1619"],
        ["Vĩnh Long", None, None, "4008", "12375", "1266", "5211", "156", "5742"],
        ["Bến Tre", "36245", None, "5", "1394", "818", "149", "299", "128"],
        ["Kiên Giang", "61560", None, "45247", "700", None, "700", None, None],
        ["Cần Thơ", None, None, "37", "629", "629", None, None, None],
        ["Hậu Giang", "45552", None, "7505", "2071", "1551", None, None, "520"],
        ["Trà Vinh", "91634", "21141", "1331", "7279", "4871", "1606", "802", None],
        ["Sóc Trăng", "25899", None, "74897", "4727", "2171", "1960", "596", None],
        ["Bạc Liêu", "68521", "8622", "6486", "600", "600", None, None, None],
        ["Cà Mau", "76199", None, None, None, None, None, None, None],
    ]
    for row in pl3_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 11, "period_type": "Cumulative", "report_date": "2009-11-15"}
        
        # 1. Lúa Mùa Gieo cấy (Year context is tricky, metadata says report year 2009)
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vgc / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa Mùa Thu hoạch
        vth = normalize_number(row[2])
        if vth: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Harvested", "value": vth / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 3. Lúa Đông Xuân Gieo cấy
        vdx = normalize_number(row[3])
        if vdx: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": vdx / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 4. Màu lương thực items - Col 4, 5, 6, 7, 8
        items = [
            ("Màu lương thực", "Tổng số"),
            ("Ngô", None),
            ("Khoai lang", None),
            ("Sắn", None),
            ("Màu lương thực khác", "Cây có củ khác")
        ]
        for idx, (c, s) in enumerate(items):
            v_alt = normalize_number(row[idx+4])
            if v_alt is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v_alt / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl4_11():
    metadata = {"year": 2009, "month": 11, "appendix_number": "PL4", "source_file": "2009_11_PHULUC_T11_2009_FINAL_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    pl4_data = [
        ["Miền Nam", "264623", "27085", "76485", "22272", "14142", "119117", "1270", "4252", "281940", "60253"],
        ["D.H Nam Trg Bộ", "79029", "1175", "26275", "6441", "439", "43729", "874", "96", "32324", "32324"],
        ["TP Đà Nẵng", "1308", None, "722", "255", "56", "275", None, None, "837", "200"],
        ["Quảng Nam", "13464", None, "9860", "2520", None, "780", "250", "54", "6900", "3500"],
        ["Quảng Ngãi", "12900", None, "5620", None, None, "7280", None, None, "8651", "5210"],
        ["Bình Định", "13943", "859", "8982", "1259", None, "2843", None, None, "13146", "1929"],
        ["Phú Yên", "19929", "316", "891", "2407", "383", "15525", "365", "42", "2690", "1980"],
        ["Khánh Hoà", "17485", None, "200", None, None, "17026", "259", None, "100", "500"],
        ["Tây Nguyên", "49559", "15858", "10031", "4209", "9113", "9805", None, None, "48975", "19623"],
        ["Kon Tum", "2880", None, "165", None, "2158", "557", None, None, "630", "57"],
        ["Gia Lai", "8987", None, "1378", "3226", "3457", "926", None, None, "10933", "8138"],
        ["Đắc Lắc", "22537", "5960", "5096", "983", "3498", "7000", None, None, "3689", "10929"],
        ["Đắc Nông", "13497", "9698", "3178", None, None, "78", "543", None, "1550", "201"],
        ["Lâm Đồng", "1658", "200", "214", None, None, "1244", None, None, "32173", "298"],
        ["Đông Nam Bộ", "44984", "1120", "24863", "2540", "4404", "11661", "396", None, "51753", "22310"],
        ["TP Hồ Chí Minh", "3110", None, "910", None, None, "2200", None, None, "11270", None],
        ["Ninh Thuận", "1367", None, "200", "35", "480", "620", "32", None, "6900", "2500"],
        ["Bình Phước", "1737", "287", "1276", "11", None, None, "163", None, "701", "2987"],
        ["Tây Ninh", "30758", None, "18092", "1143", "3276", "8247", None, None, "17870", "6351"],
        ["Bình Dương", "106", None, "106", None, None, None, None, None, "2024", "170"],
        ["Đồng Nai", "2351", "582", "579", "151", "510", "340", "189", None, "4101", "3124"],
        ["Bình Thuận", "4206", "242", "2699", "1109", "35", "109", "12", None, "4869", "4210"],
        ["Bà Rịa-V.Tàu", "1349", "9", "1001", "91", "103", "145", None, None, "4018", "2968"],
        ["ĐBS Cửu Long", "92608", "8932", "15316", "9082", "186", "53922", None, "4156", "148888", "5001"],
        ["Long An", "24797", None, "6966", "1752", None, "14381", None, None, "1698", "6510"],
        ["Đồng Tháp", "8632", "5355", "190", "2748", "9", "249", None, "81", "9239", None],
        ["An Giang", "1205", "546", "215", "420", "6", "18", None, None, "8433", "1090"],
        ["Tiền Giang", None, None, None, None, None, "119", None, None, "25200", "132"],
        ["Vĩnh Long", "2742", "1532", "28", "329", None, "199", None, "654", "20259", "370"],
        ["Bến Tre", "7628", None, "221", None, None, "6969", None, "438", "3690", "128"],
        ["Kiên Giang", "0", None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", "8182", "751", "3587", "3833", "11", None, None, None, "6342", None],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "10556", "1247"],
        ["Trà Vinh", "11972", None, "3914", None, None, "5640", "1133", "1285", "24159", "841"],
        ["Sóc Trăng", "13997", "748", "195", None, "160", "12894", None, None, "25300", "1193"],
        ["Bạc Liêu", None, None, None, None, None, None, None, None, "9200", None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]
    for row in pl4_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 11, "period_type": "Cumulative", "report_date": "2009-11-15"}
        
        items = [
            ("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None),
            ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None),
            ("Rau các loại", None), ("Đậu các loại", None)
        ]
        # Skip extra columns in PL4 (some duplicates or malformed md tables)
        for idx in range(1, 11):
            if idx >= len(row): continue
            v = normalize_number(row[idx])
            if v is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": items[idx-1][0], "sub_item": items[idx-1][1]}, {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/11"
    save_json(parse_pl3_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL3.json"))
    save_json(parse_pl4_11(), os.path.join(out_dir, "2009_11_PHULUC_T11_2009_FINAL_PL4.json"))
    print("Successfully parsed PL3, PL4 for Nov 2009 with Region Mapping.")
