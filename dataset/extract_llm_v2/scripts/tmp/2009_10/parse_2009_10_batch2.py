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

def parse_pl4_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL4", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    # Loc, CCN_Total, Đậu tương, Lạc, Vừng, Thuốc lá, Mía, Bông, Đay/Lác, Rau, Đậu
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
        ["Long An", "24797", None, "6966", "1752", None, "14381", None, "1698", "6510", None],
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
        t = {"year": 2009, "month": 10, "period_type": "Cumulative"}
        items = [
            ("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None),
            ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None),
            ("Rau các loại", None), ("Đậu các loại", None)
        ]
        for idx in range(10):
            va = normalize_number(row[idx+1])
            if va is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": items[idx][0], "sub_item": items[idx][1]}, {"attribute": "Area_Planted", "value": va/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


def parse_pl5_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL5", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL5.md"}
    records = []
    # Rows: Item, Unit, Plan, v08, v09, c_yoy, c_plan, Attr
    rows = [
        ["Trồng rừng tập trung", "1000 ha", "227.3", "157.1", "172.2", "109.6", "75.8", "Forest_Area_Planted"],
        ["Rừng phòng hộ, đặc dụng", "1000 ha", "60.0", "25.4", "40.4", "159.2", "67.4", "Forest_Area_Planted"],
        ["Rừng sản xuất", "1000 ha", "167.3", "131.8", "131.8", "100.0", "78.8", "Forest_Area_Planted"],
        ["Chăm sóc rừng trồng", "1000 ha", "149.7", "243.8", "219.0", "89.8", "146.3", "Area_Maintained"],
        ["Trồng cây nhân dân", "Tr.cây", "200", "172.0", "170.0", "98.8", "85.0", "Trees_Planted"],
        ["Khoanh nuôi tái sinh", "1000 ha", "506", "649.4", "754.4", "116.2", "149.1", "Area_Regenerated"],
        ["Khoán bảo vệ rừng", "1000 ha", "1524", "2127.0", "2516.4", "118.3", "165.1", "Area_Protected"],
        ["Khai thác gỗ", "1000 m3", "4380", "2760.9", "2955.0", "107.0", "67.5", "Wood_Volume"],
    ]
    for r in rows:
        item, unit, plan, v08, v09, c_yoy, c_plan, attr = r
        t09 = {"year": 2009, "month": 10, "period_type": "Cumulative"}
        g = "Cả nước"; gl = "National"
        i = {"sector": "Forestry", "commodity": item}
        
        # 2009 record
        val09 = normalize_number(v09)
        if val09:
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(c_yoy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, t09, g, gl, i, {"attribute": attr, "value": val09, "unit": unit, "data_type": "Actual"}, comp))
        
        # Plan record
        val_p = normalize_number(plan)
        if val_p:
            records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, g, gl, i, {"attribute": attr, "value": val_p, "unit": unit, "data_type": "Plan"}))
            
        # 2008 record
        val08 = normalize_number(v08)
        if val08:
            records.append(create_record(metadata, {"year": 2008, "month": 10, "period_type": "Cumulative"}, g, gl, i, {"attribute": attr, "value": val08, "unit": unit, "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/10"
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    save_json(parse_pl4_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL4.json"))
    save_json(parse_pl5_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL5.json"))
    print("Successfully parsed PL4, PL5 for Oct 2009 with Region Mapping.")
