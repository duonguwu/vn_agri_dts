import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if not s or s.strip() == "" or s.strip() == "||" or s.strip() == "|" or s.strip() == '"':
        return None
    s = str(s).strip().replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    if s == "" or s == "-" or s == '.':
        return None
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl6b1_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL6b1", "source_file": "2009_07_PHULUC_T07_2009_PL6b1.md"}
    records = []
    # Items: TT, Name, Unit, Plan, TH CK, TH T7
    # Forest_Area_Planted, Wood_Volume...
    summary_data = [
        ["1", "Trồng rừng tập trung", "1000_ha", "227.3", "91.5", "92.4", "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000_ha", "60.0", "18.3", "21.3", "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000_ha", "167.3", "73.2", "71.1", "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000_ha", "149.7", "201.5", "147.9", "Other"],
        ["3", "Trồng cây nhân dân", "million_trees", "200", "125.6", "123.6", "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000_ha", "506", "643", "623.2", "Other"],
        ["5", "Khoán bảo vệ rừng", "1000_ha", "1524", "2330.0", "2117.8", "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000_m3", "4380", "1684", "1967.6", "Wood_Volume"],
    ]
    for row in summary_data:
        v = normalize_number(row[5])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Forestry", "commodity": row[1]}, "metric_context": {"attribute": row[6], "value": v, "unit": row[2], "data_type": "Actual"}, "metadata": metadata})
        plan = normalize_number(row[3])
        if plan: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 12, "period_type": "Annual"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Forestry", "commodity": row[1]}, "metric_context": {"attribute": row[6], "value": plan, "unit": row[2], "data_type": "Plan"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}

def parse_pl6b2_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL6b2", "source_file": "2009_07_PHULUC_T07_2009_PL6b1.md"}
    records = []
    regional = ["Miền bắc", "ĐB. sông Hồng", "Đông bắc", "Tây bắc", "Bắc Trung Bộ", "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", " Đông Nam Bộ", " ĐB. sông Cửu Long"]
    
    # Loc, Trồng rừng (Tổng), PHĐD, Kinh tế, Chăm sóc (Ha), Khoán BV (Ha)
    pl6b2_raw = [
        ["Cả nước", "92386", "21331", "71055", "147945", "2117848"],
        ["Miền bắc", "87298", "17625", "69673", "99930", "1103265"],
        ["ĐB. sông Hồng", "1811", "1224", "587", "2578", "43735"],
        ["Hà Nội (mở rộng)", None, None, None, None, "8600"],
        ["Hải Phòng", "500", "300", "200", "500", "5500"],
        ["Vĩnh Phúc", "315", "140", "175", "50", "4500"],
        ["Bắc Ninh", "15", "15", None, "30", "300"],
        ["Hải Dương", "15", None, "15", "1090", "6235"],
        ["Hưng Yên", None, None, None, None, None],
        ["Hà Nam", "122.6", "26", "97.0", "88", "6300"],
        ["Nam Định", "100", "100", None, "520", "1700"],
        ["Thái Bình", "501", "501", None, "200", "7000"],
        ["Ninh Bình", "243", "143", "100", "100", "3600"],
        ["Đông bắc", "67060", "9629", "57431", "61674", "533279"],
        ["Hà Giang", "5900", "1000", "4900", "20582", "122913.0"],
        ["Cao Bằng", "415.0", "150.0", "265", "2230", "32000"],
        ["Lào Cai", "1530", "130.0", "1400", "1640", "38115"],
        ["Bắc Cạn", "3488", "531", "2957", "4756", "25000"],
        ["Lạng Sơn", "9193.0", "2100", "7093", "6500", "15757"],
        ["Tuyên Quang", "12478.0", "1200", "11278", "1300", "145765"],
        ["Yên Bái", "9215.0", "708", "8507", "5820", "5820"],
        ["Thái Nguyên", "4962.0", "963.0", "3999", "2116", "20000"],
        ["Phú Thọ", "4025.0", "167", "3858", "722", "46606"],
        ["Bắc Giang", "3634.0", "510", "3124", "2838", "33753"],
        ["Quảng Ninh", "12220.0", "2170", "10050", "13170", "31370"],
        ["Tây bắc", "11289", "5667", "5622", "17778", "272532"],
        ["Lai Châu", "2191.0", "2091", "100", "942", "129964"],
        ["Điện Biên", "449.0", "300.0", "149", None, "30000"],
        ["Sơn La", "3872.0", "2764", "1108", "8336", "82568"],
        ["Hoà Bình", "4777.0", "512", "4265", "8500", "30000"],
        ["Bắc Trung Bộ", "7138.0", "1105", "6033", "17900", "253719"],
        ["Thanh Hoá", "5500.0", "700", "4800", "250", "70000"],
        ["Nghệ An", "1588.0", "355", "1233", "17600", "85000"],
        ["Hà Tĩnh", "50.0", "50", None, "50", "27219"],
        ["Quảng Bình", "0.0", None, None, None, "40000"],
        ["Quảng Trị", "0.0", None, None, None, "15500"],
        ["Thừa Thiên Huế", "0.0", None, None, None, "16000"],
        ["Miền Nam", "2638.0", "1256", "1382", "36635", "889773"],
        ["D.H Nam Trung Bộ", "20.0", "0", "20", "27546", "159922"],
        ["Đà Nẵng", "20.0", None, "20", "169", "15000"],
        ["Quảng Nam", None, None, None, "1632", "35000"],
        ["Quảng Ngãi", None, None, None, "5110", "28284"],
        ["Bình Định", None, None, None, "10405", "37138"],
        ["Phú Yên", None, None, None, "9435", "30000"],
        ["Khánh Hoà", None, None, None, "795", "14500"],
        ["Tây Nguyên", "1457", "200", "1257", "8221", "470657"],
        ["Kon Tum", None, None, None, None, "80000"],
        ["Gia Lai", "300", "100", "200", None, "65183"],
        ["Đắc Lắc", "780", "100", "680", "879", "83577"],
        ["Đắc Nông", None, None, None, "6799", "40000"],
        ["Lâm Đồng", "377", None, "377", "543", "201897"],
        [" Đông Nam Bộ", "1081", "976", "105", "868", "207394"],
        ["TP Hồ Chí Minh", None, None, None, None, "16000"],
        ["Ninh Thuận", None, None, None, "200", "40000"],
        ["Bình Phước", None, None, None, None, "20000"],
        ["Tây Ninh", "843.0", "843.0", None, None, "20000"],
        ["Bình Dương", None, None, None, None, None],
        ["Đồng Nai", None, None, None, None, "1600"],
        ["Bình Thuận", "105", None, "105", "668", "108313"],
        ["Bà Rịa-Vũng Tàu", "133.0", "133.0", None, None, None],
        [" ĐB. sông Cửu Long", "80", "80", "0", "0", "51800"],
        ["Long An", None, None, None, None, "1000"],
        ["Đồng Tháp", None, None, None, None, "3200"],
        ["An Giang", None, None, None, None, "2000"],
        ["Tiền Giang", None, None, None, None, "1200"],
        ["Vĩnh Long", None, None, None, None, None],
        ["Bến Tre", None, None, None, None, "1700"],
        ["Kiên Giang", None, None, None, None, "14000"],
        ["Cần Thơ", None, None, None, None, "1900"],
        ["Hậu Giang", None, None, None, None, "1600"],
        ["Trà Vinh", "80", "80", None, None, "4100"],
        ["Sóc Trăng", None, None, None, None, "1200"],
        ["Bạc Liêu", None, None, None, None, "1900"],
        ["Cà Mau", None, None, None, None, "18000"],
    ]
    for row in pl6b2_raw:
        loc = row[0]
        geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional else "Provincial")
        items = [("Trồng rừng (tổng)", "Forest_Area_Planted"), ("Trồng rừng PHĐD", "Forest_Area_Planted"), ("Trồng rừng Kinh tế", "Forest_Area_Planted"), ("Chăm sóc rừng", "Other"), ("Khoán bảo vệ rừng", "Forest_Area_Protected")]
        for i in range(1, 4):
            v = normalize_number(row[i])
            if v is not None: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Forestry", "commodity": items[i-1][0]}, "metric_context": {"attribute": items[i-1][1], "value": v / 1000.0 if i < 4 else v, "unit": "1000_ha" if i < 4 else "ha", "data_type": "Actual"}, "metadata": metadata})
        # Special handling for unit conversion in Col 4, 5 (Chăm sóc, Khoán) - table says Ha
        for i in range(4, 6):
            v = normalize_number(row[i])
            if v is not None: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Forestry", "commodity": items[i-1][0]}, "metric_context": {"attribute": items[i-1][1], "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}

def parse_pl7_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL7", "source_file": "2009_07_PHULUC_T07_2009_PL6b1.md"}
    records = []
    # I. Sản lượng - TT, Name, Unit, Plan, TH 6T, Ư TH T7, TH 7T
    prod_rows = [
        ["I", "Tổng sản lượng", "1000_ton", "4600", "2285", "377", "2662"],
        ["1", "Sản lượng khai thác", "1000_ton", "2200", "1162", "182", "1344"],
        ["1.1", "Khai thác biển", "1000_ton", "2000", "1075", "165", "1240"],
        ["1.2", "Khai thác nội địa", "1000_ton", "200", "87", "17", "104"],
        ["2", "Sản lượng nuôi trồng", "1000_ton", "2400", "1123", "195", "1318"],
        ["II", "Giá trị KNK xuất khẩu TS", "million_USD", "4500", "1762", "400", "2162"],
    ]
    for row in prod_rows:
        unit = row[2]
        attr = "Production" if "Sản lượng" in row[1] or "I" in row[0] else "Export_Value"
        v_t7 = normalize_number(row[5]); v_7t = normalize_number(row[6])
        if v_t7: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": row[1]}, "metric_context": {"attribute": attr, "value": v_t7, "unit": unit, "data_type": "Actual"}, "metadata": metadata})
        if v_7t: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": row[1]}, "metric_context": {"attribute": attr, "value": v_7t, "unit": unit, "data_type": "Actual"}, "metadata": metadata})

    # III. Tổng sản phẩm XK - exhaustive list of commodities
    exp_data = [
        ["1", "Cá", "38685", "7670", "46355"], ["2", "Cá chế biến", "29694", "7260", "36954"], ["3", "Tôm chế biến", "10889", "2380", "13269"],
        ["4", "Cá ngừ", "23243", "5470", "28713"], ["5", "Cá Tra, basa", "264714", "60450", "325164"], ["6", "Tôm", "60441", "15560", "76001"],
        ["7", "Tôm hùm, tôm mũ ni", "35", "15", "50"], ["8", "Nhuyễn thể hai mảnh vỏ", "10279", "1970", "12249"], ["9", "Nhuyễn thể khác", "754", "165", "919"],
        ["10", "Mực khô", "4695", "1060", "5755"], ["11", "Cá khô", "10290", "2690", "12980"], ["12", "Nhuyễn thể chân đầu", "35311", "8250", "43561"],
        ["13", "Mặt hàng khác", "19086", "2600", "21686"], ["14", "Giáp xác khác", "4695", "1260", "5955"], ["15", "Tôm khô", "2602", "220", "2822"],
    ]
    for row in exp_data:
        v_t7 = normalize_number(row[3]); v_7t = normalize_number(row[4])
        if v_t7: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": row[1]}, "metric_context": {"attribute": "Export_Volume", "value": v_t7, "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
        if v_7t: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": row[1]}, "metric_context": {"attribute": "Export_Volume", "value": v_7t, "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/07"
    save_json(parse_pl6b1_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL6b1.json"))
    save_json(parse_pl6b2_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL6b2.json"))
    save_json(parse_pl7_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL7.json"))
    print("Updated Batch 3: Comprehensive Forestry & Fishery.")
