import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|":
        return None
    # Remove separators and formatting
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        if "\n" in s:
            s = s.split("\n")[0]
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl5_08():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL5", "source_file": "2009_08_PHULUC_T08_2009_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Rows: Loc, Cây CN total, Đậu tương, Lạc, Vừng, Thuốc lá, Mía mới, Bông, Đay/Lác, Rau các loại, Đậu các loại
    pl5_data = [
        ["Miền Nam", "253391", "26418", "76110", "24986", "10908", "113273", "1204", "492", "234258", "43440"],
        ["D.H Nam Trg Bộ", "71884", "1267", "24252", "6622", "713", "38114", "874", "42", "25214", "25214"],
        ["TP Đà Nẵng", "1235", None, "722", "238", None, "275", None, None, "837", "80"],
        ["Quảng Nam", "13423", None, "9860", "2203", "330", "780", "250", None, "6900", "3500"],
        ["Quảng Ngãi", "5988", None, "3787", None, None, "2201", None, None, "5433", "1521"],
        ["Bình Định", "13824", "951", "8792", "1774", None, "2307", None, None, "9254", "1630"],
        ["Phú Yên", "19929", "316", "891", "2407", "383", "15525", "365", "42", "2690", "1980"],
        ["Khánh Hoà", "17485", None, "200", None, None, "17026", "259", None, "100", "500"],
        ["Tây Nguyên", "38512", "15858", "7722", "1965", "5695", "6729", None, None, "41635", "17273"],
        ["Kon Tum", "2555", None, "165", None, "2158", "232", None, None, "630", "57"],
        ["Gia Lai", "5722", None, "815", "982", "3457", "468", None, None, "7605", "8138"],
        ["Đắc Lắc", "15190", "5960", "3564", "983", "80", "4603", None, None, "2350", "8579"],
        ["Đắc Nông", "13497", "9698", "3178", None, None, "78", "543", None, "1550", "201"],
        ["Lâm Đồng", "1548", "200", None, None, None, "1348", None, None, "29500", "298"],
        ["Đông Nam Bộ", "57099", "1120", "29002", "7327", "4307", "15013", "330", None, "42255", "13133"],
        ["TP Hồ Chí Minh", "2978", None, "778", None, None, "2200", None, None, "8384", None],
        ["Ninh Thuận", "1367", None, "200", "35", "480", "620", "32", None, "6900", "500"],
        ["Bình Phước", "593", "287", "132", "11", None, None, "163", None, "701", "145"],
        ["Tây Ninh", "31031", None, "19167", "1007", "3109", "7748", None, None, "10692", "4990"],
        ["Bình Dương", "81", None, "81", None, None, None, None, None, "2024", "64"],
        ["Đồng Nai", "9325", "582", "4156", "69", "580", "3815", "123", None, "9110", "3759"],
        ["Bình Thuận", "10375", "242", "3487", "6114", "35", "485", "12", None, "2216", "3178"],
        ["Bà Rịa-V.Tàu", "1349", "9", "1001", "91", "103", "145", None, None, "2228", "497"],
        ["ĐBS Cửu Long", "87453", "8173", "15134", "9072", "193", "53417", None, "450", "125154", "3823"],
        ["Long An", "23099", None, "6966", "1752", None, "14381", None, None, "6510", None],
        ["Đồng Tháp", "8484", "5434", "166", "2737", "16", "131", None, None, "8602", None],
        ["An Giang", "1205", "546", "215", "420", "6", "18", None, None, "8433", "1090"],
        ["Tiền Giang", None, None, None, None, None, "119", None, None, "25200", None],
        ["Vĩnh Long", "1615", "1189", "28", "331", None, "67", None, None, "15942", "370"],
        ["Bến Tre", "7360", None, "391", None, None, "6969", None, None, "2082", "128"],
        ["Kiên Giang", "0", None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", "8177", "747", "3587", "3832", "11", None, None, None, "5898", "201"],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "6068", None],
        ["Trà Vinh", "10752", None, "3627", None, None, "5542", "1133", "450", "17979", "841"],
        ["Sóc Trăng", "13308", "257", "154", None, "160", "12737", None, None, "22940", "1193"],
        ["Bạc Liêu", None, None, None, None, None, None, None, None, "5500", None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]

    for row in pl5_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        items = [
            ("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None),
            ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None),
            ("Rau các loại", None), ("Đậu các loại", None)
        ]
        indices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for i, idx in enumerate(indices):
            v = normalize_number(row[idx])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i][0], "sub_item": items[i][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}

def parse_pl6a_08():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL6a", "source_file": "2009_08_PHULUC_T08_2009_PL6a.md"}
    records = []
    # TT, Item, Unit, Plan, TH CK, TH T8
    rows = [
        ["1", "Trồng rừng tập trung", "1000_ha", "227.3", "107.4", "117.5", "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000_ha", "60.0", "23.5", "27.6", "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000_ha", "167.3", "83.9", "89.9", "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000_ha", "149.7", "206.0", "174.6", "Other"],
        ["3", "Trồng cây nhân dân", "million_trees", "200", "138.7", "137", "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000_ha", "506", "647", "677", "Other"],
        ["5", "Khoán bảo vệ rừng", "1000_ha", "1524", "2484.6", "2125.2", "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000_m3", "4380", "2053", "2352", "Wood_Volume"],
    ]
    for row in rows:
        tt, item, unit, plan, ck, t8, attr = row
        v_t8 = normalize_number(t8)
        if v_t8: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Forestry", "commodity": item}, "metric_context": {"attribute": attr, "value": v_t8, "unit": unit, "data_type": "Actual"}, "metadata": metadata})
        v_plan = normalize_number(plan)
        if v_plan: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 12, "period_type": "Annual"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Forestry", "commodity": item}, "metric_context": {"attribute": attr, "value": v_plan, "unit": unit, "data_type": "Plan"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}

def parse_pl6b_08():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL6b", "source_file": "2009_08_PHULUC_T08_2009_PL6b.md"}
    records = []
    regional = ["Miền bắc", "Miền Nam", "ĐB. sông Hồng", "Đông bắc", "Tây bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    # Unit in table for detail columns: Ha -> 1000_ha
    pl6b_raw = [
        ["Cả nước", "117546", "27650", "89896", "174628", "677016", "2125158"],
        ["Miền bắc", "105746", "22146", "83600", "125815", "573084", "1110575"],
        ["ĐB. sông Hồng", "1811", "1224", "587", "2578", "14633", "43735"],
        ["Hà Nội (mở rộng)", None, None, None, None, None, "8600"],
        ["Hải Phòng", "500", "300", "200", "500", "720", "5500"],
        ["Vĩnh Phúc", "315", "140", "175", "50", "356", "4500"],
        ["Bắc Ninh", "15", "15", None, "30", "33", "300"],
        ["Hải Dương", "15", None, "15", "1090", "11", "6235"],
        ["Hưng Yên", None, None, None, None, None, None],
        ["Hà Nam", "122.6", "26", "97.0", "88", "1679", "6300"],
        ["Nam Định", "100", "100", None, "520", None, "1700"],
        ["Thái Bình", "501", "501", None, "200", None, "7000"],
        ["Ninh Bình", "243", "143", "100", "100", "11834", "3600"],
        ["Đông bắc", "80492", "13100", "67392", "86167", "130883", "540589"],
        ["Hà Giang", "12588", "2000", "10588", "20582", "37730", "122913"],
        ["Cao Bằng", "415.0", "150", "265", "2230", "25507", "32000"],
        ["Lào Cai", "2511", "184", "2327", "1640", "5145", "38115"],
        ["Bắc Cạn", "4322", "703", "3619", "4756", "9248", "25000"],
        ["Lạng Sơn", "9193", "2100", "7093", "7608", "7572", "23034"],
        ["Tuyên Quang", "13537", "1338", "12199", "1884", "7886", "22000"],
        ["Yên Bái", "11694", "2240", "9454", "5820", "19670", "19670"],
        ["Thái Nguyên", "5506", "1017", "4489", "2116", "4600", "20033"],
        ["Phú Thọ", "4025", "167", "3858", "722", "1400", "46606"],
        ["Bắc Giang", "3634", "510", "3124", "2838", "2125", "33753"],
        ["Quảng Ninh", "13067", "2691", "10376", "35971", "10000", "31370"],
        ["Tây bắc", "15088", "6203", "8885", "19170", "346529", "272532"],
        ["Lai Châu", "2191", "2091", "100", "942", "98123", "129964"],
        ["Điện Biên", "769", "329", "440", "692", "692", "30000"],
        ["Sơn La", "3872", "2764", "1108", "8336", "178800", "82568"],
        ["Hoà Bình", "8256", "1019", "7237", "9200", "4500", "30000"],
        ["Bắc Trung Bộ", "8355", "1619", "6736", "17900", "81039", "253719"],
        ["Thanh Hoá", "6717", "1214", "5503", "250", "19726", "70000"],
        ["Nghệ An", "1588", "355", "1233", "17600", "52044", "85000"],
        ["Hà Tĩnh", "50", "50", None, "50", "9269", "27219"],
        ["Quảng Bình", "0.0", None, None, None, None, "40000"],
        ["Quảng Trị", "0.0", None, None, None, None, "15500"],
        ["Thừa Thiên Huế", "0.0", None, None, None, None, "16000"],
        ["Miền Nam", "9350", "3054", "6296", "37433", "101666", "889773"],
        ["D.H Nam Trung Bộ", "20", "0", "20", "27546", "75840", "159922"],
        ["Đà Nẵng", "20", None, "20", "169", "121", "15000"],
        ["Quảng Nam", None, None, None, "1632", "21527", "35000"],
        ["Quảng Ngãi", None, None, None, "5110", "1241", "28284"],
        ["Bình Định", None, None, None, "10405", "47551", "37138"],
        ["Phú Yên", None, None, None, "9435", "3073", "30000"],
        ["Khánh Hoà", None, None, None, "795", "2327", "14500"],
        ["Tây Nguyên", "6827", "1151", "5676", "9019", "6545", "470657"],
        ["Kon Tum", "2264", "675", "1589", "798", "2016", "80000"],
        ["Gia Lai", "300", "100", "200", None, None, "65183"],
        ["Đắc Lắc", "3700", "190", "3510", "879", "2944", "83577"],
        ["Đắc Nông", None, None, None, "6799", "1585", "40000"],
        ["Lâm Đồng", "563", "186", "377", "543", None, "201897"],
        ["Đông Nam Bộ", "1389", "1284", "105", "868", "19281", "207394"],
        ["TP Hồ Chí Minh", None, None, None, None, "56", "16000"],
        ["Ninh Thuận", None, None, None, "200", "600", "40000"],
        ["Bình Phước", None, None, None, None, None, "20000"],
        ["Tây Ninh", "843", "843", None, None, "10380", "20000"],
        ["Bình Dương", None, None, None, None, None, None],
        ["Đồng Nai", "308", "308", None, None, None, "1600"],
        ["Bình Thuận", "105", None, "105", "668", "7260", "108313"],
        ["Bà Rịa-Vũng Tàu", "133", "133", None, None, "985", "985"],
        ["ĐB. sông Cửu Long", "1114", "619", "495", "0", "0", "51800"],
        ["Long An", None, None, None, None, None, "1000"],
        ["Đồng Tháp", None, None, None, None, None, "3200"],
        ["An Giang", None, None, None, None, None, "2000"],
        ["Tiền Giang", None, None, None, None, None, "1200"],
        ["Vĩnh Long", None, None, None, None, None, None],
        ["Bến Tre", "73", "73", None, None, None, "1700"],
        ["Kiên Giang", None, None, None, None, None, "14000"],
        ["Cần Thơ", None, None, None, None, None, "1900"],
        ["Hậu Giang", None, None, None, None, None, "1600"],
        ["Trà Vinh", "80", "80", None, None, None, "4100"],
        ["Sóc Trăng", "466", "466", None, None, None, "1200"],
        ["Bạc Liêu", "495", None, "495", None, None, "1900"],
        ["Cà Mau", None, None, None, None, None, "18000"],
        ["Trung uơng", "2450", "2450", None, "11380", "2266", "124810"],
    ]
    for row in pl6b_raw:
        loc = row[0]
        geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional else "Provincial")
        items = [("Trồng rừng tập trung (tổng)", "Forest_Area_Planted"), ("Trồng rừng PHĐD", "Forest_Area_Planted"), ("Trồng rừng Kinh tế", "Forest_Area_Planted"), ("Chăm sóc rừng", "Other"), ("Khoanh nuôi tái sinh", "Other"), ("Khoán bảo vệ rừng", "Forest_Area_Protected")]
        for i in range(1, 7):
            v = normalize_number(row[i])
            if v is not None: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Monthly"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Forestry", "commodity": items[i-1][0]}, "metric_context": {"attribute": items[i-1][1], "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}

def parse_pl7_08():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL7", "source_file": "2009_08_PHULUC_T08_2009_PL6b.md"}
    records = []
    prod_rows = [
        ["I", "Tổng sản lượng", "1000_ton", "4600", "2662", "338", "3000"],
        ["1", "Sản lượng khai thác", "1000_ton", "2200", "1344", "158", "1502"],
        ["1.1", "Khai thác biển", "1000_ton", "2000", "1240", "140", "1380"],
        ["1.2", "Khai thác nội địa", "1000_ton", "200", "104", "18", "122"],
        ["2", "Sản lượng nuôi trồng", "1000_ton", "2400", "1318", "180", "1498"],
        ["II", "Giá trị k/ngạch xuất khẩu TS", "million_USD", "4500", "1762", "400", "2162"],
    ]
    for row in prod_rows:
        v_t8 = normalize_number(row[5]); v_8t = normalize_number(row[6])
        attr = "Production" if "Sản lượng" in row[1] or "I" in row[0] else "Export_Value"
        if v_t8: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": row[1]}, "metric_context": {"attribute": attr, "value": v_t8, "unit": row[2], "data_type": "Actual"}, "metadata": metadata})
        if v_8t: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": row[1]}, "metric_context": {"attribute": attr, "value": v_8t, "unit": row[2], "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/08"
    save_json(parse_pl5_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL5.json"))
    save_json(parse_pl6a_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL6a.json"))
    save_json(parse_pl6b_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL6b.json"))
    save_json(parse_pl7_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL7.json"))
    print("Batch 3: Corrected with full data for Aug 2009.")
