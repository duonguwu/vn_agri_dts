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
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl1_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL1", "source_file": "2009_07_PHULUC_T07_2009_PL1.md"}
    records = []
    
    # 1. Thu hoạch lúa hè thu miền Nam
    # Columns: Item, Sub, val08, val09, location, geo_level, attribute, unit
    rows = [
        ["Lúa", "Hè Thu", "570.0", "578.1", "Miền Nam", "Regional", "Area_Harvested", "1000_ha"],
        ["Lúa", "Hè Thu", "547.9", "557.2", "Đồng bằng sông Cửu Long", "Regional", "Area_Harvested", "1000_ha"],
        ["Lúa", "Mùa", "1090.4", "1140.7", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Lúa", "Mùa", "902.2", "927.8", "Miền Bắc", "Regional", "Area_Planted", "1000_ha"],
        ["Lúa", "Mùa", "434.5", "450.4", "Đồng bằng sông Hồng", "Regional", "Area_Planted", "1000_ha"],
        ["Lúa", "Mùa", "188.2", "212.9", "Miền Nam", "Regional", "Area_Planted", "1000_ha"],
        ["Lúa", "Mùa", "63.8", "63.7", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted", "1000_ha"],
        ["Màu lương thực", "Tổng số", "1392.6", "1359.0", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Ngô", None, "821.2", "780.0", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Khoai lang", None, "115.7", "113.5", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Sắn", None, "429.6", "424.5", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Cây công nghiệp ngắn ngày", "Tổng số", "562.7", "553.6", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Lạc", None, "212.5", "200.4", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Đậu tương", None, "150.7", "145.8", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Thuốc lá", None, "19.2", "24.5", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Mía", "Trồng mới", "150.3", "147.8", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Rau, đậu các loại", None, "534.9", "559.8", "Cả nước", "National", "Area_Planted", "1000_ha"],
    ]

    for row in rows:
        item, sub, v08, v09, loc, geo, attr, unit = row
        val09 = normalize_number(v09)
        if val09:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": attr, "value": val09, "unit": unit, "data_type": "Actual"},
                "metadata": metadata
            })
        val08 = normalize_number(v08)
        if val08:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 7, "period_type": "Cumulative", "report_date": "2008-07-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": attr, "value": val08, "unit": unit, "data_type": "Actual"},
                "metadata": metadata
            })
    return {"metadata": metadata, "records": records}

def parse_pl2_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL2", "source_file": "2009_07_PHULUC_T07_2009_PL2.md"}
    records = []
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    # Rows: Loc, Lúa Mùa, Màu LT Total, Ngô, K.Lang, Sắn, Khác
    pl2_data = [
        ["Miền Bắc", "927750", "734366", "496211", "96351", "132477", "9327"],
        ["ĐB sông Hồng", "450403", "75842", "51075", "20267", "4500", "0"],
        ["Hà Nội", "90710", "8268", "2768", "4500", "1000", None],
        ["Hải Phòng", "29000", "7600", "4700", "2900", None, None],
        ["Vĩnh Phúc", "28300", "7659", "5602", "557", "1500", None],
        ["Bắc Ninh", "28820", "5000", "4000", "1000", None, None],
        ["Hải Dương", "61133", "5200", "3750", "1450", None, None],
        ["Hưng Yên", "34564", "9500", "8000", "1500", None, None],
        ["Hà Nam", "35403", "4855", "4055", "800", None, None],
        ["Nam Định", "33650", "6000", "4000", "2000", None, None],
        ["Thái Bình", "72050", "12500", "9000", "3500", None, None],
        ["Ninh Bình", "36773", "9260", "5200", "2060", "2000", None],
        ["Đông Bắc", "219431", "278597", "202345", "31297", "41374", "3581"],
        ["Hà Giang", "15000", "40273", "39000", "433", None, "840"],
        ["Cao Bằng", "10176", "32894", "32694", "100", "100", None],
        ["Lào Cai", "11704", "30486", "21436", "350", "8000", "700"],
        ["Bắc Cạn", "4890", "15221", "13482", "256", "1345", "138"],
        ["Lạng Sơn", "13000", "19500", "15000", "1000", "3000", "500"],
        ["Tuyên Quang", "23636", "14000", "10000", "4000", None, None],
        ["Yên Bái", "19437", "28530", "12530", "2000", "14000", None],
        ["Thái Nguyên", "33937", "28046", "17000", "7000", "4046", None],
        ["Phú Thọ", "30000", "32694", "24509", "3165", "5020", None],
        ["Bắc Giang", "46651", "24130", "10986", "7778", "4763", "603"],
        ["Quảng Ninh", "11000", "12823", "5708", "5215", "1100", "800"],
        ["Tây Bắc", "81151", "175592", "125825", "5365", "40162", "4240"],
        ["Lai Châu", "22000", "5000", None, None, "5000", None],
        ["Điện Biên", "35000", "7500", None, None, "7500", None],
        ["Sơn La", "9475", "119025", "100825", "200", "15000", "3000"],
        ["Hoà Bình", "14676", "44067", "25000", "5165", "12662", "1240"],
        ["Bắc Trung Bộ", "176765", "204335", "116966", "39422", "46441", "1506"],
        ["Thanh Hoá", "130825", "61055", "42500", "11555", "7000", None],
        ["Nghệ An", "39110", "82058", "55713", "10141", "16204", None],
        ["Hà Tĩnh", "6230", "22326", "9000", "11326", "2000", None],
        ["Quảng Bình", None, "12700", "5000", "700", "7000", None],
        ["Quảng Trị", None, "14743", "3000", "2500", "8237", "1006"],
        ["Thừa Thiên Huế", "600", "11453", "1753", "3200", "6000", "500"],
    ]

    for row in pl2_data:
        loc = row[0]
        geo = "Regional" if loc in regional_list else "Provincial"
        
        # Lúa Mùa
        v = normalize_number(row[1])
        if v is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"},
                "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Màu LT mapping
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for i in range(2, 7):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-2][0], "sub_item": items[i-2][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}

def parse_pl3_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL3", "source_file": "2009_07_PHULUC_T07_2009_PL3.md"}
    records = []
    regional_list = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    # Rows: Loc, Cây CN ngắn ngày Total, Đậu tương, Lạc, Mía, Thuốc lá, Rau đậu các loại
    pl3_data = [
        ["Miền Bắc", "300001", "122261", "134234", "34575", "8931", "282107"],
        ["ĐB sông Hồng", "113893", "79812", "30973", "858", "2250", "124941"],
        ["Hà Nội", "45069", "37596", "7473", None, None, "25136"],
        ["Hải Phòng", "2550", "200", "100", None, "2250", "12400"],
        ["Vĩnh Phúc", "15068", "8637", "6381", "50", None, "5394"],
        ["Bắc Ninh", "3519", "2466", "1053", None, None, "5730"],
        ["Hải Dương", "1200", "200", "1000", None, None, "24000"],
        ["Hưng Yên", "5188", "3561", "1627", None, None, "12000"],
        ["Hà Nam", "9500", "9000", "500", None, None, "5600"],
        ["Nam Định", "9239", "3000", "6239", None, None, "13000"],
        ["Thái Bình", "10177", "8077", "2100", None, None, "16000"],
        ["Ninh Bình", "12383", "7075", "4500", "808", None, "5681"],
        ["Đông Bắc", "52081", "22556", "20887", "2140", "6498", "62359"],
        ["Hà Giang", "12096", "7543", "4553", None, None, "9490"],
        ["Cao Bằng", "4552", "1084", "314", "1975", "1179", "1963"],
        ["Lào Cai", "3083", "2353", "648", None, "82", "3594"],
        ["Bắc Cạn", "2992", "1729", "362", "165", "736", "1476"],
        ["Lạng Sơn", "6483", "800", "1182", None, "4501", "5732"],
        ["Tuyên Quang", "3457", "3000", "457", None, None, "4534"],
        ["Yên Bái", "2801", "1238", "1563", None, None, "4429"],
        ["Thái Nguyên", "5203", "1415", "3788", None, None, "10844"],
        ["Phú Thọ", "6056", "1056", "5000", None, None, "8289"],
        ["Bắc Giang", "2108", "1678", "430", None, None, "2508"],
        ["Quảng Ninh", "3250", "660", "2590", None, None, "9500"],
        ["Tây Bắc", "31828", "15346", "8137", "8345", "0", "11657"],
        ["Lai Châu", "2232", "1232", "1000", None, None, "1500"],
        ["Điện Biên", "11250", "9650", "1600", None, None, None],
        ["Sơn La", "2300", "1678", "622", None, None, "2556"],
        ["Hoà Bình", "16046", "2786", "4915", "8345", None, "7601"],
        ["Bắc Trung Bộ", "102199", "4547", "74237", "23232", "183", "83150"],
        ["Thanh Hoá", "34596", "4047", "16837", "13712", None, "35600"],
        ["Nghệ An", "32000", "500", "22000", "9500", None, "20550"],
        ["Hà Tĩnh", "21400", None, "21400", None, None, "13000"],
        ["Quảng Bình", "5000", None, "5000", None, None, "7000"],
        ["Quảng Trị", "5123", None, "5000", "20", "103", "2000"],
        ["Thừa Thiên Huế", "4080", None, "4000", None, "80", "5000"],
    ]

    for row in pl3_data:
        loc = row[0]
        geo = "Regional" if loc in regional_list else "Provincial"
        items = [("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Mía", "Trồng mới"), ("Thuốc lá", None), ("Rau, đậu các loại", None)]
        for i in range(1, 7):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/07"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl1_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL1.json"))
    save_json(parse_pl2_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL2.json"))
    save_json(parse_pl3_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL3.json"))
    print("Successfully parsed PL1, PL2, PL3 for July 2009.")
