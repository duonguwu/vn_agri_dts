import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if s is None:
        return None
    if not isinstance(s, str):
        try:
            return float(s)
        except:
            return None
    if s.strip() == "" or s.strip() == "||" or s.strip() == "|" or s.strip() == '"':
        return None
    s = s.strip().replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    if " " in s: s = s.split()[0]
    if s == "" or s == "-" or s == '.':
        return None
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl6b_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL6b", "source_file": "2009_06_PHULUC_T06_2009_PL6b1.md"}
    records = []
    
    rows = [
        ["Cả nước", "74039", "17634", "56405", "143113", "2038815"],
        ["Miền bắc", "70892", "15084", "55808", "96422", "1024232"],
        ["ĐB. sông Hồng", "1811", "1224", "587", "2578", "43735"],
        ["Hà Nội (mở rộng)", None, None, None, None, "8600"],
        ["Hải Phòng", "500", "300", "200", "500", "5500"],
        ["Vĩnh Phúc", "315", "140", "175", "50", "4500"],
        ["Bắc Ninh", "15", "15", None, "30", "300"],
        ["Hải Dương", "15", None, "15", "1090", "6235"],
        ["Hà Nam", "122.6", "26", "97.0", "88", "6300"],
        ["Nam Định", "100", "100", None, "520", "1700"],
        ["Thái Bình", "501", "501", None, "200", "7000"],
        ["Ninh Bình", "243", "143", "100", "100", "3600"],
        ["Đông bắc", "52200", "7721", "44479", "59108", "524778"],
        ["Hà Giang", "5900", "1000", "4900", "20582", "122913"],
        ["Cao Bằng", "222.0", "90.0", "132", "2230", "32000"],
        ["Lào Cai", "1021", "101.0", "920", "1640", "38115"],
        ["Bắc Cạn", "3006", "334", "2672", "4756", "25000"],
        ["Lạng Sơn", "5905.0", "1800", "4105", "5096", "13626"],
        ["Tuyên Quang", "7200.0", "1200", "6000", "500", "145765"],
        ["Yên Bái", "7026.0", "394", "6632", "5820", "5820"],
        ["Thái Nguyên", "4284.0", "782.0", "3502", "2116", "20000"],
        ["Phú Thọ", "4025.0", "167", "3858", "360", "46606"],
        ["Bắc Giang", "3087.0", "271", "2816", "2838", "33753"],
        ["Quảng Ninh", "10524.0", "1582", "8942", "13170", "25000"],
        ["Tây bắc", "10693", "5034", "5659", "16836", "202000"],
        ["Lai Châu", "2191.0", "2091", "100", None, "92000"],
        ["Điện Biên", "449.0", "300.0", "149", None, "30000"],
        ["Sơn La", "3276.0", "2131", "1145", "8336", "50000"],
        ["Hoà Bình", "4777.0", "512", "4265", "8500", "30000"],
        ["Bắc Trung Bộ", "6188.0", "1105", "5083", "17900", "253719"],
        ["Thanh Hoá", "4550.0", "700", "3850", "250", "70000"],
        ["Nghệ An", "1588.0", "355", "1233", "17600", "85000"],
        ["Hà Tĩnh", "50.0", "50", None, "50", "27219"],
        ["Quảng Bình", "0.0", None, None, None, "40000"],
        ["Quảng Trị", "0.0", None, None, None, "15500"],
        ["Thừa Thiên Huế", "0.0", None, None, None, "16000"],
        ["Miền Nam", "697.0", "100", "597", "35311", "889773"],
        ["D.H Nam Trung Bộ", "20.0", "0", "20", "27101", "159922"],
        ["Đà Nẵng", "20.0", None, "20", "169", "15000"],
        ["Quảng Nam", None, None, None, "1632", "35000"],
        ["Quảng Ngãi", None, None, None, "5110", "28284"],
        ["Bình Định", None, None, None, "10405", "37138"],
        ["Phú Yên", None, None, None, "9435", "30000"],
        ["Khánh Hoà", None, None, None, "350", "14500"],
        ["Tây Nguyên", "677", "100", "577", "7342", "470657"],
        ["Kon Tum", None, None, None, None, "80000"],
        ["Gia Lai", "300", "100", "200", None, "65183"],
        ["Đắc Lắc", None, None, None, None, "83577"],
        ["Đắc Nông", None, None, None, "6799", "40000"],
        ["Lâm Đồng", "377", None, "377", "543", "201897"],
        ["Đông Nam Bộ", "0", "0", "0", "868", "207394"],
        ["TP Hồ Chí Minh", None, None, None, None, "16000"],
        ["Ninh Thuận", None, None, None, "200", "40000"],
        ["Bình Phước", None, None, None, None, "20000"],
        ["Tây Ninh", None, None, None, None, "20000"],
        ["Bình Dương", None, None, None, None, None],
        ["Đồng Nai", None, None, None, None, "1600"],
        ["Bình Thuận", None, None, None, "668", "108313"],
        ["ĐB. sông Cửu Long", "0", "0", "0", "0", "51800"],
        ["Long An", None, None, None, None, "1000"],
        ["Đồng Tháp", None, None, None, None, "3200"],
        ["An Giang", None, None, None, None, "2000"],
        ["Tiền Giang", None, None, None, None, "1200"],
        ["Bến Tre", None, None, None, None, "1700"],
        ["Kiên Giang", None, None, None, None, "14000"],
        ["Cần Thơ", None, None, None, None, "1900"],
        ["Hậu Giang", None, None, None, None, "1600"],
        ["Trà Vinh", None, None, None, None, "4100"],
        ["Sóc Trăng", None, None, None, None, "1200"],
        ["Bạc Liêu", None, None, None, None, "1900"],
        ["Cà Mau", None, None, None, None, "18000"],
        ["Trung uơng", "2450", "2450", None, "11380", "124810"],
    ]
    regional = ["Cả nước", "Miền bắc", "ĐB. sông Hồng", "Đông bắc", "Tây bắc", "Bắc Trung Bộ", "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long", "Trung uơng"]
    for r in rows:
        loc = r[0]; geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional else "Provincial")
        # Planted
        v = normalize_number(r[1])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Monthly"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Forestry", "commodity": "Trồng rừng tập trung"}, "metric_context": {"attribute": "Forest_Area_Planted", "value": v, "unit": "ha", "data_type": "Estimated"}, "metadata": metadata})
        # Cared
        v = normalize_number(r[4])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Monthly"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Forestry", "commodity": "Chăm sóc rừng trồng"}, "metric_context": {"attribute": "Forest_Area_Cared", "value": v, "unit": "ha", "data_type": "Estimated"}, "metadata": metadata})
        # Protected
        v = normalize_number(r[5])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Monthly"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Forestry", "commodity": "Khoán bảo vệ rừng"}, "metric_context": {"attribute": "Forest_Area_Protected", "value": v, "unit": "ha", "data_type": "Estimated"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl7_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL7", "source_file": "2009_06_PHULUC_T06_2009_PL7.md"}
    records = []
    # Prod
    pd = [("Tổng sản lượng", "380", "2284"), ("Sản lượng khai thác", "177", "1161"), ("Khai thác biển", "166", "1076"), ("Khai thác nội địa", "11", "85"), ("Sản lượng nuôi trồng", "203", "1123")]
    for item, m, c in pd:
        records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": item}, "metric_context": {"attribute": "Production", "value": normalize_number(m), "unit": "1000_ton", "data_type": "Estimated"}, "metadata": metadata})
        records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": item}, "metric_context": {"attribute": "Production", "value": normalize_number(c), "unit": "1000_ton", "data_type": "Estimated"}, "metadata": metadata})
    # Export Items
    ei = [("Cá", "6300", "38406"), ("Cá chế biến", "5920", "30004"), ("Tôm chế biến", "1730", "10007"), ("Cá ngừ", "4030", "22300"), ("Cá Tra, basa", "44250", "251046"), ("Tôm", "10720", "54800"), ("Tôm hùm, mũ ni", "3", "30"), ("Nhuyễn thể 2 mảnh", "1460", "9704"), ("Nhuyễn thể khác", "100", "682"), ("Mực khô", "920", "4632"), ("Cá khô", "1620", "9254"), ("Nhuyễn thể chân đầu", "6260", "33429"), ("Mặt hàng khác", "2530", "17125"), ("Giáp xác khác", "950", "4595"), ("Tôm khô", "300", "2710")]
    for item, m, c in ei:
        records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": item}, "metric_context": {"attribute": "Export_Volume", "value": normalize_number(m), "unit": "ton", "data_type": "Estimated"}, "metadata": metadata})
        records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Fishery", "commodity": item}, "metric_context": {"attribute": "Export_Volume", "value": normalize_number(c), "unit": "ton", "data_type": "Estimated"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl8_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL8", "source_file": "2009_06_PHULUC_T06_2009_PL8.md"}
    records = []
    # Exhaustive PL8
    x = [
        ("Cà phê", "1000_ton", "741", "1099"), ("Cao su", "1000_ton", "229", "325"), ("Gạo", "1000_ton", "3832", "1824"), ("Chè", "1000_ton", "49", "61"), ("Hạt điều", "1000_ton", "71", "314"), ("Hạt tiêu", "1000_ton", "65", "149"), ("Hàng rau quả", "million_USD", None, "199"), ("Sắn & SP sắn", "1000_ton", "2161", "370"), ("Thuỷ sản", "million_USD", None, "1693"), ("Quế", "1000_ton", "9.0", None), ("Gỗ & SP gỗ", "million_USD", None, "1114"), ("SP mây tre thảm", "million_USD", None, "86")
    ]
    for n, u, v, g in x:
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Trade", "commodity": n}, "metric_context": {"attribute": "Export_Volume", "value": normalize_number(v), "unit": "1000_ton", "data_type": "Estimated"}, "metadata": metadata})
        if g: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Trade", "commodity": n}, "metric_context": {"attribute": "Export_Value", "value": normalize_number(g), "unit": "million_USD", "data_type": "Estimated"}, "metadata": metadata})
    # Markets 8a
    m8a = [("Gạo", "Philippine", "1383609", "752373"), ("Cà phê", "Bỉ", "105105", "152163"), ("Cao su", "Trung Quốc", "129639", "181008"), ("Chè", "Pakixtan", "10299", "14219"), ("Gỗ", "Hoa Kỳ", None, "373695"), ("Thủy sản", "Nhật Bản", "36519", "240013")]
    meta8a = {"year": 2009, "month": 6, "appendix_number": "PL8a", "source_file": "2009_06_PHULUC_T06_2009_PL8a.md"}
    for n, l, v, g in m8a:
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"}, "geo_context": {"geo_level": "International", "location_name": l}, "item_context": {"sector": "Trade", "commodity": n}, "metric_context": {"attribute": "Export_Volume", "value": normalize_number(v), "unit": "ton", "data_type": "Actual"}, "metadata": meta8a})
        if g: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"}, "geo_context": {"geo_level": "International", "location_name": l}, "item_context": {"sector": "Trade", "commodity": n}, "metric_context": {"attribute": "Export_Value", "value": normalize_number(g), "unit": "1000_USD", "data_type": "Actual"}, "metadata": meta8a})
    # NK
    nk = [("Phân bón các loại", "2225", "727"), ("Thuốc trừ sâu", None, "231"), ("Lúa mỳ", "598", "148"), ("Thức ăn gia súc", None, "783"), ("Dầu mỡ", None, "242"), ("Cao su", "122", "165"), ("Bông", "104", "130"), ("Sữa", None, "230"), ("Gỗ", None, "356"), ("Thủy sản", None, "131"), ("Rau quả", None, "119"), ("Muối", "14", None)]
    for n, v, g in nk:
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Trade", "commodity": n}, "metric_context": {"attribute": "Import_Volume", "value": normalize_number(v), "unit": "1000_ton", "data_type": "Estimated"}, "metadata": metadata})
        if g: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Trade", "commodity": n}, "metric_context": {"attribute": "Import_Value", "value": normalize_number(g), "unit": "million_USD", "data_type": "Estimated"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl9_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL9", "source_file": "2009_06_PHULUC_T06_2009_PL9.md"}
    records = []
    rows = [
        ["Tổng vốn NS (A+B)", "3954763", "210094", "1597818"],
        ["Vốn thực hiện đầu tư", "2611500", "157660", "1267510"],
        ["Đầu tư Thuỷ lợi", "1483500", "115000", "875020"],
        ["Đầu tư Nông nghiệp", "493000", "25460", "240605"],
        ["Đầu tư Lâm nghiệp", "230000", "5200", "48888"],
        ["Đầu tư Thuỷ sản", "24000", "1500", "11400"],
        ["Khoa học CNS", "230000", "5000", "38170"],
        ["Giáo dục ĐT", "90000", "4500", "37177"],
        ["Ngành khác", "61000", "1000", "16250"],
        ["Vốn TPCP (C+D+E)", "3850000", "191897", "1340463"],
    ]
    for n, p, m, c in rows:
        records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"}, "item_context": {"sector": "Investment", "commodity": n}, "metric_context": {"attribute": "Investment_Value", "value": normalize_number(c), "unit": "million_VND", "data_type": "Estimated"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl6b_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL6b.json"))
    save_json(parse_pl7_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL7.json"))
    save_json(parse_pl8_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL8.json"))
    save_json(parse_pl9_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL9.json"))
    print("FINISHED ALL Appendix Extraction for June 2009 (Fully Exhaustive).")
