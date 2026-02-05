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
    alias_map = {
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "ĐB Sông Cửu Long": "Đồng bằng sông Cửu Long"
    }
    norm_loc = alias_map.get(loc_name, loc_name)
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name"] = "Cả nước"
    elif norm_loc == "Miền Nam":
        geo_context["region_id"] = "SOUTH"; geo_context["region_name"] = "Miền Nam"

    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl4_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL4", "source_file": "2010_01_PhuLuc_T01_2010_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    pl4_data = [
        ["Miền Nam", "777968", "646965", "1807103", "111042", "47904", "23269", "6281", "14652", "3913"],
        ["D.H Nam Trung Bộ", "93553", "93553", "164700", "0", "14590", "8587", "5636", "367", "0"],
        ["TP Đà Nẵng", "4004", "4004", "4000", None, "340", "116", "209", "15", None],
        ["Quảng Nam", "45128", "45128", "38800", None, "11294", "6036", "5258", None, None],
        ["Quảng Ngãi", "5900", "5900", "35524", None, None, None, None, None, None],
        ["Bình Định", "25505", "25505", "46787", None, "2020", "1668", None, "352", None],
        ["Phú Yên", "7016", "7016", "25618", None, "936", "767", "169", None, None],
        ["Khánh Hoà", "6000", "6000", "13971", None, None, None, None, None, None],
        ["Tây Nguyên", "131280", "123437", "55272", "0", "3511", "3183", "299", "29", "0"],
        ["Kon Tum", "16700", "16700", "3984", None, "405", "405", None, None, None],
        ["Gia Lai", "46843", "39000", "13101", None, "1509", "1300", "180", "29", None],
        ["Đắc Lắc", "44167", "44167", "24331", None, None, None, None, None, None],
        ["Đắc Nông", "7000", "7000", "3930", None, "1597", "1478", "119", None, None],
        ["Lâm Đồng", "16570", "16570", "9926", None, None, None, None, None, None],
        ["Đông Nam Bộ", "175342", "164354", "91821", "0", "21529", "3883", "246", "13698", "3702"],
        ["TP Hồ Chí Minh", "15500", "12059", "4293", None, None, None, None, None, None],
        ["Ninh Thuận", "8970", "8970", "10181", None, None, None, None, None, None],
        ["Bình Phước", "9900", "9900", "3005", None, None, None, None, None, None],
        ["Tây Ninh", "57720", "51377", "39686", None, "16749", "3012", None, "10446", "3291"],
        ["Bình Dương", "4230", "3921", "900", None, "1627", None, "171", "1045", "411"],
        ["Đồng Nai", "29780", "29780", "11214", None, "1624", None, None, "1624", None],
        ["Bình Thuận", "36700", "36700", "17953", None, "512", None, None, "512", None],
        ["Bà Rịa-V.Tàu", "12542", "11647", "4589", None, "1017", "871", "75", "71", None],
        ["ĐBS Cửu Long", "377793", "265621", "1495310", "111042", "8274", "7616", "100", "558", "211"],
        ["Long An", "13071", "11405", "195219", "37541", "3646", "3646", None, None, None],
        ["Đồng Tháp", None, None, "207732", "400", "626", "415", None, None, "211"],
        ["An Giang", "7637", "6008", "234091", None, "1340", "1220", "30", "90", None],
        ["Tiền Giang", None, None, "82272", None, "1376", "1176", None, "200", None],
        ["Vĩnh Long", None, None, "66974", "2000", "240", "92", None, "148", None],
        ["Bến Tre", "36245", "34855", "19808", None, "540", "350", "70", "120", None],
        ["Kiên Giang", "62782", "47872", "283898", "15307", None, None, None, None, None],
        ["Cần Thơ", None, None, "89564", None, "117", "117", None, None, None],
        ["Hậu Giang", None, None, "83846", "7037", None, None, None, None, None],
        ["Trà Vinh", "91634", "85076", "57116", None, None, None, None, None, None],
        ["Sóc Trăng", "21804", "18405", "139240", "48757", "600", "600", None, None, None],
        ["Bạc Liêu", "68421", "39000", "35550", None, None, None, None, None, None],
        ["Cà Mau", "76199", "23000", None, None, None, None, None, None, None],
    ]
    for row in pl4_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2010, "month": 1, "period_type": "Cumulative", "report_date": "2010-01-15"}
        
        # 1. Lúa Mùa 2009 (Metadata says year 2010 report, but this is season 2009 finishing)
        vgc = normalize_number(row[1])
        if vgc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa 2009"}, {"attribute": "Area_Planted", "value": vgc / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        vth = normalize_number(row[2])
        if vth: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa 2009"}, {"attribute": "Area_Harvested", "value": vth / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        
        # 2. Lúa Đông Xuân 2009/10
        vdx_gc = normalize_number(row[3])
        if vdx_gc: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Planted", "value": vdx_gc / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
        vdx_th = normalize_number(row[4])
        if vdx_th: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"}, {"attribute": "Area_Harvested", "value": vdx_th / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))

        # 3. Màu lương thực Southern items
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", "Cây khác")]
        for idx, (c, s) in enumerate(items):
            v_alt = normalize_number(row[idx+5])
            if v_alt is not None: records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": c, "sub_item": s}, {"attribute": "Area_Planted", "value": v_alt / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl5_10_01():
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL5", "source_file": "2010_01_PhuLuc_T01_2010_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Rows: loc, CN_Total, Soybean, Peanut, Sesame, Tobacco, Sugarcane, Cotton, Jute, Vegetables, Legumes
    pl5_data = [
        ["Miền Nam", "37823", "967", "17128", "1551", "8839", "8957", "315", "694", "67539", "11433"],
        ["D.H Nam Trg Bộ", "8207", "437", "6933", "15", "0", "459", "223", "29", "13771", "13771"],
        ["TP Đà Nẵng", "431", None, "431", None, None, None, None, None, "282", None],
        ["Quảng Nam", "788", None, "600", None, None, None, "188", None, "6500", None],
        ["Quảng Ngãi", None, None, None, None, None, None, None, None, "1392", None],
        ["Bình Định", "5720", "252", "5468", None, None, None, None, None, "4364", "555"],
        ["Phú Yên", "1158", "185", "324", "15", None, "459", "35", "29", "1033", "594"],
        ["Khánh Hoà", "110", None, "110", None, None, None, None, None, "200", None],
        ["Tây Nguyên", "10156", "0", "110", "0", "5298", "4447", "0", "0", "6752", "2960"],
        ["Kon Tum", "4318", None, "58", None, "2145", "2115", None, None, "582", "119"],
        ["Gia Lai", "5329", None, "52", None, "2999", "2278", None, None, "4000", "1714"],
        ["Đắc Lắc", "509", None, None, None, "154", "54", None, None, "1753", "1072"],
        ["Đắc Nông", None, None, None, None, None, None, None, None, "417", "55"],
        ["Đông Nam Bộ", "15796", "165", "8018", "1037", "3513", "3118", "92", "0", "17774", "4294"],
        ["TP Hồ Chí Minh", None, None, None, None, None, None, None, None, "3481", None],
        ["Tây Ninh", "13055", None, "6955", "902", "2723", "2622", None, None, "5141", "1956"],
        ["Bình Dương", "398", None, "99", None, None, "299", None, None, "900", "30"],
        ["Đồng Nai", "1294", "165", "98", "84", "771", "99", "77", None, "3444", "135"],
        ["Bình Thuận", "874", None, "789", "51", "19", None, "15", None, "1587", "1992"],
        ["Bà Rịa-V.Tàu", "175", None, "77", None, None, "98", None, None, "3221", "181"],
        ["ĐBS Cửu Long", "3664", "365", "2067", "499", "28", "933", "0", "665", "29242", "3030"],
        ["Long An", "347", None, None, "347", None, None, None, None, None, None],
        ["Đồng Tháp", "264", "158", None, None, "10", "11", None, "85", "3681", None],
        ["An Giang", "337", "100", "73", "145", "1", "18", None, None, "5441", "600"],
        ["Vĩnh Long", "228", "88", None, None, None, "4", None, "136", "2001", "1900"],
        ["Bến Tre", "110", None, "110", None, None, None, None, None, "2050", "40"],
        ["Cần Thơ", "56", "19", "13", "7", "17", None, None, None, "1185", "113"],
        ["Hậu Giang", "900", None, None, None, None, "900", None, None, "5120", "77"],
        ["Trà Vinh", "1162", None, "1871", None, None, None, None, "444", "6661", "300"],
        ["Sóc Trăng", "260", None, None, None, None, None, None, None, "3103", None],
    ]
    for row in pl5_data:
        loc = row[0]; geo = "Regional" if loc in regional else "Provincial"
        t = {"year": 2010, "month": 1, "period_type": "Cumulative", "report_date": "2010-01-15"}
        
        items = [
            ("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None),
            ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None),
            ("Rau các loại", None), ("Đậu các loại", None)
        ]
        for idx in range(1, 11):
            if idx >= len(row): continue
            v = normalize_number(row[idx])
            if v is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Cultivation", "commodity": items[idx-1][0], "sub_item": items[idx-1][1]}, {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


def parse_pl6_10_01():
    # This is 2009 Forestry Final Estimate
    metadata = {"year": 2009, "month": 12, "appendix_number": "PL6", "source_file": "2010_01_PhuLuc_T01_2010_PL6.md"}
    records = []
    # TT, Item, Unit, Plan, TH CK (2008), ƯTH 12T (2009)
    rows = [
        ["1", "Trồng rừng tập trung", "1000 ha", "227.3", "234.2", "247.4", "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000 ha", "60.0", "40.8", "50.0", "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000 ha", "167.3", "193.4", "197.4", "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000 ha", "149.7", "290.4", "251.2", "Other"],
        ["3", "Trồng cây nhân dân", "Tr.cây", "200", "183.7", "180.4", "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000 ha", "506", "657.1", "767.8", "Other"],
        ["5", "Khoán bảo vệ rừng", "1000 ha", "1524", "2136.9", "2544.4", "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000 m3", "4380", "3512.3", "3766.7", "Wood_Volume"],
    ]
    for r in rows:
        tt, item, unit, plan, v08, v09, attr = r
        loc, gl = "Cả nước", "National"
        t09 = {"year": 2009, "month": 12, "period_type": "Annual"}
        t08 = {"year": 2008, "month": 12, "period_type": "Annual"}
        
        records.append(create_record(metadata, t09, loc, gl, {"sector": "Forestry", "commodity": item}, {"attribute": attr, "value": normalize_number(v09), "unit": unit, "data_type": "Actual"}))
        records.append(create_record(metadata, t08, loc, gl, {"sector": "Forestry", "commodity": item}, {"attribute": attr, "value": normalize_number(v08), "unit": unit, "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/01"
    save_json(parse_pl4_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL4.json"))
    save_json(parse_pl5_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL5.json"))
    save_json(parse_pl6_10_01(), os.path.join(out_dir, "2010_01_PhuLuc_T01_2010_PL6.json"))
    print("Successfully parsed PL4, PL5, PL6 for Jan 2010.")
