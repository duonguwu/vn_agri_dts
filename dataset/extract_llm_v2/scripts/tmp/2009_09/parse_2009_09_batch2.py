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

def parse_pl4_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL4", "source_file": "2009_09_PHULUC_T09_2009_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Rows: 0:Loc, 1:HT_GC, 2:HT_TH, 3:%, 4:Mùa_GC, 5:Màu_Total, 6:Ngô, 7:K.Lang, 8:Sắn, 9:Khác
    pl4_data = [
        ["Miền Nam", "2038338", "1785648", "87.6", "491617", "627801", "300817", "24153", "288456", "14375"],
        ["D.H Nam Trg Bộ", "114881", "109634", "95.4", "75783", "101070", "38085", "4723", "57621", "641"],
        ["TP Đà Nẵng", None, None, None, "3755", "1187", "664", "437", "86", None],
        ["Quảng Nam", None, None, None, "44128", "27751", "12051", "3700", "12000", None],
        ["Quảng Ngãi", "31641", "31641", "100.0", "600", "21875", "7818", "200", "13857", None],
        ["Bình Định", "41550", "36303", "87.4", "25505", "18093", "7540", None, "10553", None],
        ["Phú Yên", "23920", "23920", "100.0", "1795", "22346", "5712", "226", "16125", "283"],
        ["Khánh Hoà", "17770", "17770", "100.0", None, "9818", "4300", "160", "5000", "358"],
        ["Tây Nguyên", "6175", "6175", "100.0", "149524", "288138", "159191", "9911", "119036", "0"],
        ["Kon Tum", None, None, None, "15414", "42612", "7388", "152", "35072", None],
        ["Gia Lai", None, None, None, "39527", "91684", "40820", "857", "50007", None],
        ["Đắc Lắc", None, None, None, "43773", "100467", "74315", "5288", "20864", None],
        ["Đắc Nông", None, None, None, "35120", "33975", "20575", "2100", "11300", None],
        ["Lâm Đồng", "6175", "6175", "100.0", "15690", "19400", "16093", "1514", "1793", None],
        ["Đông Nam Bộ", "159557", "152204", "95.4", "77665", "193532", "77171", "1700", "109793", "4868"],
        ["TP Hồ Chí Minh", "6967", "6967", "100.0", "10000", "1100", "1100", None, None, None],
        ["Ninh Thuận", "12400", "12000", "96.8", "6800", "7900", "7900", None, None, None],
        ["Bình Phước", "13700", "13000", "94.9", "9500", "31237", "6672", "867", "23600", "98"],
        ["Tây Ninh", "52991", "52991", "100.0", "36543", "42117", "7072", None, "35045", None],
        ["Bình Dương", "2192", "2192", "100.0", "1982", "6724", "130", "1", "2316", "4277"],
        ["Đồng Nai", "25196", "19800", "78.6", "1705", "41258", "25337", "374", "15429", "118"],
        ["Bình Thuận", "38357", "37500", "97.8", None, "37764", "11640", "229", "25520", "375"],
        ["Bà Rịa-V.Tàu", "7754", "7754", "100.0", "11135", "25432", "17320", "229", "7883", None],
        ["ĐBS Cửu Long", "1757725", "1517635", "86.3", "188645", "45061", "26370", "7819", "2006", "8866"],
        ["Long An", "201140", "201103", "100.0", "13286", "900", "900", None, None, None],
        ["Đồng Tháp", "195730", "195730", "100.0", None, "6232", "4188", "1187", None, "857"],
        ["An Giang", "230884", "230071", "99.6", None, "6299", "6179", "120", None, None],
        ["Tiền Giang", "117084", "90415", "77.2", None, "6156", "4146", "238", "153", "1619"],
        ["Vĩnh Long", "63003", "63003", "100.0", None, "8886", "911", "2077", "156", "5742"],
        ["Bến Tre", "24212", "24212", "100.0", "33105", "1394", "818", "149", "299", "128"],
        ["Kiên Giang", "274836", "231464", "84.2", "38425", "700", None, "700", None, None],
        ["Cần Thơ", "120976", "120976", "100.0", None, "629", "629", None, None, None],
        ["Hậu Giang", "186453", "77888", "41.8", None, "2071", "1551", None, None, "520"],
        ["Trà Vinh", "82431", "81334", "98.7", "73330", "6467", "4277", "1388", "802", None],
        ["Sóc Trăng", "169071", "152807", "90.4", "11367", "4727", "2171", "1960", "596", None],
        ["Bạc Liêu", "55777", "16041", "28.8", "11242", "600", "600", None, None, None],
        ["Cà Mau", "36128", "32591", "90.2", "7890", "0", None, None, None, None],
    ]

    for row in pl4_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2009, "month": 9, "period_type": "Cumulative", "report_date": "2009-09-15"}
        
        # 1. Lúa HT Gieo cấy
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Planted", "value": vgc/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 2. Lúa HT Thu hoạch với comparison vs_Plan (TH/GC)
        vth = normalize_number(row[2])
        if vth:
            comp = None
            if normalize_number(row[3]):
                comp = {"comparison_type": "vs_Plan", "comparison_value": normalize_number(row[3]), "comparison_unit": "percentage", "reference_period": "Current_Planting"}
            records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"}, {"attribute": "Area_Harvested", "value": vth/1000.0, "unit": "1000_ha", "data_type": "Actual"}, comp))
        # 3. Lúa Mùa Gieo cấy
        vmgc = normalize_number(row[4])
        if vmgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"}, {"attribute": "Area_Planted", "value": vmgc/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        # 4. Màu items
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for idx, (c, s) in enumerate(items):
            va = normalize_number(row[idx+5])
            if va is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": va/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


def parse_pl5_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL5", "source_file": "2009_09_PHULUC_T09_2009_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    pl5_data = [
        ["Miền Nam", "272967", "26742", "81483", "25097", "11075", "123048", "1270", "4252", "258801", "60253"],
        ["D.H Nam Trg Bộ", "78765", "1175", "26275", "6439", "713", "43193", "874", "96", "32260", "32260"],
        ["TP Đà Nẵng", "1235", None, "722", "238", None, "275", None, None, "837", "200"],
        ["Quảng Nam", "13477", None, "9860", "2203", "330", "780", "250", "54", "6900", "3500"],
        ["Quảng Ngãi", "12900", None, "5620", None, None, "7280", None, None, "8651", "5210"],
        ["Bình Định", "13739", "859", "8982", "1591", None, "2307", None, None, "13082", "1929"],
        ["Phú Yên", "19929", "316", "891", "2407", "383", "15525", "365", "42", "2690", "1980"],
        ["Khánh Hoà", "17485", None, "200", None, None, "17026", "259", None, "100", "500"],
        ["Tây Nguyên", "43673", "15858", "9021", "1965", "5695", "10591", None, None, "45647", "19623"],
        ["Kon Tum", "2880", None, "165", None, "2158", "557", None, None, "630", "57"],
        ["Gia Lai", "7180", None, "1900", "982", "3457", "841", None, None, "7605", "8138"],
        ["Đắc Lắc", "18458", "5960", "3564", "983", "80", "7871", None, None, "3689", "10929"],
        ["Đắc Nông", "13497", "9698", "3178", None, None, "78", "543", None, "1550", "201"],
        ["Lâm Đồng", "1658", "200", "214", None, None, "1244", None, None, "32173", "298"],
        ["Đông Nam Bộ", "60329", "1120", "31158", "7609", "4474", "15572", "396", None, "49107", "22310"],
        ["TP Hồ Chí Minh", "3000", None, "800", None, None, "2200", None, None, "10770", None],
        ["Ninh Thuận", "1367", None, "200", "35", "480", "620", "32", None, "6900", "2500"],
        ["Bình Phước", "1737", "287", "1276", "11", None, None, "163", None, "701", "2987"],
        ["Tây Ninh", "32818", None, "20157", "1138", "3276", "8247", None, None, "16863", "6351"],
        ["Bình Dương", "81", None, "81", None, None, None, None, None, "2024", "170"],
        ["Đồng Nai", "9602", "582", "4156", "220", "580", "3875", "189", None, "2962", "3124"],
        ["Bình Thuận", "10375", "242", "3487", "6114", "35", "485", "12", None, "4869", "4210"],
        ["Bà Rịa-V.Tàu", "1349", "9", "1001", "91", "103", "145", None, None, "4018", "2968"],
        ["ĐBS Cửu Long", "91757", "8589", "15029", "9084", "193", "53692", None, "4156", "131787", "5001"],
        ["Long An", "24797", None, "6966", "1752", None, "14381", None, "1698", "6510", None],
        ["Đồng Tháp", "8639", "5355", "190", "2748", "16", "249", None, "81", "9239", None],
        ["An Giang", "1205", "546", "215", "420", "6", "18", None, None, "8433", "1090"],
        ["Tiền Giang", None, None, None, None, None, "119", None, None, "25200", "132"],
        ["Vĩnh Long", "2269", "1189", "28", "331", None, "67", None, "654", "15942", "370"],
        ["Bến Tre", "7628", None, "221", None, None, "6969", None, "438", "3146", "128"],
        ["Kiên Giang", "0", None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", "8182", "751", "3587", "3833", "11", None, None, None, "6342", None],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "10556", "1247"],
        ["Trà Vinh", "11587", None, "3627", None, None, "5542", "1133", "1285", "17979", "841"],
        ["Sóc Trăng", "13997", "748", "195", None, "160", "12894", None, None, "22940", "1193"],
        ["Bạc Liêu", None, None, None, None, None, None, None, None, "5500", None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]
    for row in pl5_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        items = [("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None), ("Rau các loại", None), ("Đậu các loại", None)]
        for idx, (c, s) in enumerate(items):
            va = normalize_number(row[idx+1])
            if va is not None: records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Cumulative"}, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": va/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/09"
    save_json(parse_pl4_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL4.json"))
    save_json(parse_pl5_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL5.json"))
    print("Fixed Batch 2 with region map integration.")
