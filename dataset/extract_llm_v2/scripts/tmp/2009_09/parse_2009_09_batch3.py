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

def parse_pl6a_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL6a", "source_file": "2009_09_PHULUC_T09_2009_PL6a.md"}
    records = []
    # Rows: 1:Item, 2:Unit, 3:Plan, 4:CK_08, 5:TH_09, 6:%_YoY, 7:%_Plan, 8:Attr
    rows = [
        ["Trồng rừng tập trung", "1000 ha", "227.3", "139.5", "146.7", "105.1", "64.5", "Forest_Area_Planted"],
        ["Rừng phòng hộ, đặc dụng", "1000 ha", "60.0", "23.9", "33.7", "141.0", "56.2", "Forest_Area_Planted"],
        ["Rừng sản xuất", "1000 ha", "167.3", "115.6", "113.0", "97.7", "67.5", "Forest_Area_Planted"],
        ["Chăm sóc rừng trồng", "1000 ha", "149.7", "225.6", "197.9", "87.7", "132.2", "Area_Maintained"],
        ["Trồng cây nhân dân", "Tr.cây", "200", "165.1", "163", "98.7", "81.5", "Trees_Planted"],
        ["Khoanh nuôi tái sinh", "1000 ha", "506", "650.4", "720", "110.7", "142.2", "Area_Regenerated"],
        ["Khoán bảo vệ rừng", "1000 ha", "1524", "2727.5", "2286.7", "83.8", "150.0", "Area_Protected"],
        ["Khai thác gỗ", "1000 m3", "4380", "2435", "2581", "106.0", "58.9", "Wood_Volume"],
    ]
    for r in rows:
        item, unit, plan, v08, v09, c_yoy, c_plan, attr = r
        t09 = {"year": 2009, "month": 9, "period_type": "Cumulative"}
        loc, gl = "Cả nước", "National"
        i = {"sector": "Forestry", "commodity": item}
        
        # 2009 Record
        val09 = normalize_number(v09)
        if val09:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, t09, loc, gl, i, {"attribute": attr, "value": val09, "unit": unit, "data_type": "Actual"}, comp))
            
        # Plan Record
        val_p = normalize_number(plan)
        if val_p:
            records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, loc, gl, i, {"attribute": attr, "value": val_p, "unit": unit, "data_type": "Plan"}))
            
        # 2008 Record
        val08 = normalize_number(v08)
        if val08:
            records.append(create_record(metadata, {"year": 2008, "month": 9, "period_type": "Cumulative"}, loc, gl, i, {"attribute": attr, "value": val08, "unit": unit, "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl6b_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL6b", "source_file": "2009_09_PHULUC_T09_2009_PL6b.md"}
    records = []
    regional = ["Miền bắc", "Miền Nam", "ĐB. sông Hồng", "Đông bắc", "Tây bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    # Loc, TR_Total, TR_PHDD, TR_KinhTe, Chăm sóc, Khoanh nuôi, Khoán BV
    pl6b_data = [
        ["Cả nước", "146667", "33703", "112964", "197939", "719751", "2286713"],
        ["Miền bắc", "125406", "25406", "100000", "143650", "610665", "1254729"],
        ["ĐB. sông Hồng", "2241", "1516", "725", "2720", "14633", "43735"],
        ["Hà Nội (mở rộng)", None, None, None, None, None, "8600"],
        ["Hải Phòng", "500", "300", "200", "500", "720", "5500"],
        ["Vĩnh Phúc", "315", "140", "175", "50", "356", "4500"],
        ["Bắc Ninh", "15", "15", None, "30", "33", "300"],
        ["Hải Dương", "15", None, "15", "1090", "11", "6235"],
        ["Hà Nam", "122.6", "26", "97.0", "230", "1679", "6300"],
        ["Nam Định", "268", "268", None, "520", None, "1700"],
        ["Thái Bình", "625", "625", None, "200", None, "7000"],
        ["Ninh Bình", "380", "143", "238", "100", "11834", "3600"],
        ["Đông bắc", "90318", "16075", "74243", "94946", "130883", "662031"],
        ["Hà Giang", "13900", "2900", "11000", "20582", "37730", "122913"],
        ["Cao Bằng", "7100", "277", "433", "2230", "25507", "32000"],
        ["Lào Cai", "3867", "417", "3450", "1640", "5145", "97267"],
        ["Bắc Cạn", "5148", "704", "4444", "9975", "9248", "25000"],
        ["Lạng Sơn", "9193", "2383", "6810", "7608", "7572", "23034"],
        ["Tuyên Quang", "14272", "2000", "12272", "3354", "7886", "229639"],
        ["Yên Bái", "12650", "2393", "10257", "5820", "19670", "19670"],
        ["Thái Nguyên", "5506", "1017", "4489", "2116", "4600", "20033"],
        ["Phú Thọ", "5031", "244", "4787", "2812", "1400", "46606"],
        ["Bắc Giang", "3967", "616", "3351", "2838", "2125", "33753"],
        ["Quảng Ninh", "16074", "3124", "12950", "35971", "10000", "31370"],
        ["Tây bắc", "19677", "5390", "14287", "19336", "357127", "279907"],
        ["Lai Châu", "6240", "1111", "5129", "1108", "108721", "137339"],
        ["Điện Biên", "769", "329", "440", "692", "692", "30000"],
        ["Sơn La", "4412", "2931", "1481", "8336", "178800", "82568"],
        ["Hoà Bình", "8256", "1019", "7237", "9200", "4500", "30000"],
        ["Bắc Trung Bộ", "13170", "2425", "10745", "26648", "108022", "269056"],
        ["Thanh Hoá", "9087", "2020", "7067", "5620", "30000", "70000"],
        ["Nghệ An", "4033", "355", "3678", "17600", "52044", "85000"],
        ["Hà Tĩnh", "50", "50", None, "50", "9269", "27219"],
        ["Quảng Bình", "0", None, None, "712", "10476", "55337"],
        ["Quảng Trị", "0", None, None, None, None, "15500"],
        ["Thừa Thiên Huế", "0", None, None, "2666", "6233", "16000"],
        ["Miền Nam", "18105", "5141", "12964", "42909", "106820", "907174"],
        ["D.H Nam Trung Bộ", "122", "20", "102", "32237", "75840", "162142"],
        ["Đà Nẵng", "22", None, "22", "169", "121", "15000"],
        ["Quảng Nam", None, None, None, "1632", "21527", "37220"],
        ["Quảng Ngãi", None, None, None, "9801", "1241", "28284"],
        ["Bình Định", "100", "20", "80", "10405", "47551", "37138"],
        ["Phú Yên", None, None, None, "9435", "3073", "30000"],
        ["Khánh Hoà", None, None, None, "795", "2327", "14500"],
        ["Tây Nguyên", "9055", "1263", "7792", "9019", "8039", "470657"],
        ["Kon Tum", "2264", "675", "1589", "798", "2016", "80000"],
        ["Gia Lai", "300", "100", "200", None, "1494", "65183"],
        ["Đắc Lắc", "3960", "220", "3740", "879", "2944", "83577"],
        ["Đắc Nông", "1832", "82", "1750", "6799", "1585", "40000"],
        ["Lâm Đồng", "699", "186", "513", "543", None, "201897"],
        ["Đông Nam Bộ", "6290", "2578", "3712", "1459", "22941", "221301"],
        ["TP Hồ Chí Minh", "1120", "247", "873", None, "56", "16000"],
        ["Ninh Thuận", None, None, None, "200", "1000", "53000"],
        ["Bình Phước", "350", "350", None, None, None, "20000"],
        ["Tây Ninh", "843", "843", None, None, "10380", "20000"],
        ["Đồng Nai", "350", "350", None, None, None, "1600"],
        ["Bình Thuận", "3404", "655", "2749", "668", "10520", "109220"],
        ["B bà Rịa-Vũng Tàu", "223", "133", "90", "591", "985", "985"],
        ["ĐB. sông Cửu Long", "2638", "1280", "1358", "194", "0", "53074"],
        ["Tiền Giang", "105", "105", None, None, None, "1200"],
        ["Bến Tre", "75", "75", None, "194", None, "2974"],
        ["Kiên Giang", None, None, None, None, None, "14000"],
        ["Cần Thơ", None, None, None, None, None, "1900"],
        ["Hậu Giang", None, None, None, None, None, "1600"],
        ["Trà Vinh", "684", "134", "550", None, None, "4100"],
        ["Sóc Trăng", "466", "466", None, None, None, "1200"],
        ["Bạc Liêu", "495", "200", "295", None, None, "1900"],
        ["Cà Mau", "813", "300", "513", None, None, "18000"],
        ["Trung uơng", "3156", "3156", None, "11380", "2266", "124810"],
    ]
    for row in pl6b_data:
        loc = row[0]
        geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional else "Provincial")
        t = {"year": 2009, "month": 9, "period_type": "Cumulative"}
        items = [
            ("Trồng rừng tập trung", "Tổng số"), ("Trồng rừng tập trung", "Rừng PHĐD"), ("Trồng rừng tập trung", "Rừng Kinh tế"),
            ("Chăm sóc rừng", None), ("Khoanh nuôi tái sinh", None), ("Khoán bảo vệ rừng", None)
        ]
        attrs = ["Forest_Area_Planted", "Forest_Area_Planted", "Forest_Area_Planted", "Area_Maintained", "Area_Regenerated", "Area_Protected"]
        
        for idx in range(6):
            v = normalize_number(row[idx+1])
            if v is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Forestry", "commodity": items[idx][0], "sub_item": items[idx][1]}, {"attribute": attrs[idx], "value": v/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


def parse_pl7_09():
    metadata = {"year": 2009, "month": 9, "appendix_number": "PL7", "source_file": "2009_09_PHULUC_T09_2009_PL6b.md"}
    records = []
    # Prod Rows: 0:TT, 1:Item, 2:Unit, 3:Plan, 4:TH_8T, 5:ƯTH_T9, 6:TH_9T, 7:TH_9T_08, 8:%_Plan, 9:%_YoY
    prod_rows = [
        ["I", "Tổng sản lượng", "1000 Tấn", "4600", "3200", "423", "3623", "3409", "78.8", "106.3"],
        ["1", "Sản lượng khai thác", "1000 Tấn", "2200", "1502", "176", "1678", "1582", "76.3", "106.1"],
        ["1.1", "Khai thác biển", "1000 Tấn", "2000", "1381", "161", "1542", "1437", "77.1", "107.3"],
        ["1.2", "Khai thác nội địa", "1000 Tấn", "200", "121", "15", "136", "145", "68.0", "93.8"],
        ["2", "Sản lượng nuôi trồng", "1000 Tấn", "2400", "1698", "247", "1945", "1827", "81.0", "106.5"],
        ["II", "Giá trị k/ngạch xuất khẩu TS", "Triêụ USD", "4500", "2616", "430", "3046", "3350", "67.7", "90.9"],
    ]
    for r in prod_rows:
        item, unit, plan, v8, v9, v9c, v9c08, c_plan, c_yoy = r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]
        loc, gl = "Cả nước", "National"
        i = {"sector": "Fishery", "commodity": item}
        attr = "Production" if "Sản lượng" in item or "I" in r[0] else "Export_Value"
        
        # Monthly Sep
        if normalize_number(v9):
            records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Monthly"}, loc, gl, i, {"attribute": attr, "value": normalize_number(v9), "unit": unit, "data_type": "Actual"}))
        # Cumulative 9T
        if normalize_number(v9c):
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Cumulative"}, loc, gl, i, {"attribute": attr, "value": normalize_number(v9c), "unit": unit, "data_type": "Actual"}, comp))
        # Plan
        if normalize_number(plan):
            records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, loc, gl, i, {"attribute": attr, "value": normalize_number(plan), "unit": unit, "data_type": "Plan"}))

    # Export Item list
    exp_items = [
        ("Cá", "56890", "8400", "65290", "67760", "96.36"),
        ("Cá chế biến", "43401", "6650", "50051", "62775", "79.73"),
        ("Tôm chế biến", "16486", "2740", "19226", "17900", "107.41"),
        ("Cá ngừ", "33138", "4345", "37483", "42391", "88.42"),
        ("Cá tra, basa", "381203", "58680", "439883", "485463", "90.61"),
        ("Tôm", "103387", "18850", "122237", "117708", "103.85"),
        ("Trôm hùm, tôm mũ ni", "82", "15", "97", "108", "89.81"),
        ("Nhuyễn thể hai mảnh vỏ", "14531", "1420", "15951", "12850", "124.13"),
        ("Nhuyễn thể khác", "1197", "120", "1317", "989", "133.06"),
        ("Mực khô", "6960", "960", "7920", "8285", "95.60"),
        ("Cá khô", "16268", "2910", "19178", "21570", "88.91"),
        ("Nhuyễn thể chân đầu", "50653", "6870", "57523", "65888", "87.30"),
        ("Mặt hàng khác", "21794", "1730", "23524", "19658", "119.66"),
        ("Giáp xác khác", "7080", "1290", "8370", "11068", "75.63"),
        ("Tôm khô", "3029", "270", "3299", "1925", "171.34"),
    ]
    for r in exp_items:
        it, v8, v9, v9c, v08, cp = r
        loc, gl = "Cả nước", "National"
        i = {"sector": "Fishery", "commodity": it}
        # Only cumulative shown here
        if normalize_number(v9c):
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, {"year": 2009, "month": 9, "period_type": "Cumulative"}, loc, gl, i, {"attribute": "Export_Volume", "value": normalize_number(v9c), "unit": "ton", "data_type": "Actual"}, comp))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/09"
    save_json(parse_pl6a_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL6a.json"))
    save_json(parse_pl6b_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL6b.json"))
    save_json(parse_pl7_09(), os.path.join(out_dir, "2009_09_PHULUC_T09_2009_PL7.json"))
    print("Successfully parsed PL6a, 6b, 7 for Sep 2009 with region map integration.")
