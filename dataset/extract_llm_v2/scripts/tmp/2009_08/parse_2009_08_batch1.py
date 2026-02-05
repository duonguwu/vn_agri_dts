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
    s = s.strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|":
        return None
    # Remove separators and formatting
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl1_08():
    # Phụ lục 1: Tổng hợp kết quả sản xuất nông nghiệp đến 15/8/2009
    metadata = {
        "year": 2009,
        "month": 8,
        "appendix_number": "PL1",
        "source_file": "2009_08_PHULUC_T08_2009_PL1.md"
    }
    records = []
    
    # Data rows from MD
    # Format: [Item, Sub, val08, val09, location, geo_level, attribute]
    rows = [
        ["Lúa", "Hè Thu", "1219.0", "1223.8", "Miền Nam", "Regional", "Area_Harvested"],
        ["Lúa", "Hè Thu", "1113.8", "1117.0", "Đồng bằng sông Cửu Long", "Regional", "Area_Harvested"],
        ["Lúa", "Mùa", "1457.9", "1464.2", "Cả nước", "National", "Area_Planted"],
        ["Lúa", "Mùa", "1178.3", "1170.6", "Miền Bắc", "Regional", "Area_Planted"],
        ["Lúa", "Mùa", "279.6", "293.7", "Miền Nam", "Regional", "Area_Planted"],
        ["Màu lương thực", "Tổng số", "1453.2", "1387.6", "Cả nước", "National", "Area_Planted"],
        ["Ngô", None, "861.9", "831.9", "Cả nước", "National", "Area_Planted"],
        ["Khoai lang", None, "129.6", "117.3", "Cả nước", "National", "Area_Planted"],
        ["Sắn", None, "435.3", "411.9", "Cả nước", "National", "Area_Planted"],
        ["Cây công nghiệp ngắn ngày", "Tổng số", "608.9", "622.5", "Cả nước", "National", "Area_Planted"],
        ["Lạc", None, "226.4", "235.6", "Cả nước", "National", "Area_Planted"],
        ["Đậu tương", None, "164.7", "167.8", "Cả nước", "National", "Area_Planted"],
        ["Thuốc lá", None, "19.2", "20.5", "Cả nước", "National", "Area_Planted"],
        ["Mía", "Trồng mới", None, None, "Cả nước", "National", "Area_Planted"], # Placeholder from MD 3.2 logic
        ["Rau, đậu các loại", "Tổng số", "615.7", "614.4", "Cả nước", "National", "Area_Planted"],
    ]

    for row in rows:
        item, sub, v08, v09, loc, geo, attr = row
        
        # 2009 record
        val09 = normalize_number(v09)
        if val09:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": attr, "value": val09, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
        
        # 2008 record
        val08 = normalize_number(v08)
        if val08:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 8, "period_type": "Cumulative", "report_date": "2008-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": attr, "value": val08, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
    return {"metadata": metadata, "records": records}

def parse_pl2_08():
    # Phụ lục 2: Các tỉnh miền Bắc gieo cấy lúa và trồng màu lương thực đến 15/8/2009
    metadata = {
        "year": 2009,
        "month": 8,
        "appendix_number": "PL2",
        "source_file": "2009_08_PHULUC_T08_2009_PL2.md"
    }
    records = []
    
    # Columns: Loc, Lúa Mùa Total, Lúa Mùa Nương, Lúa Hè Thu Nương (?), Màu LT Total, Ngô, Khoai lang, Sắn, Khác
    # Unit: Ha -> Normalize to 1000_ha
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    # Data from MD
    pl2_data = [
        ["Miền Bắc", "1170558", "45904", "160267", "776555", "555276", "95079", "115984", "10216"],
        ["ĐB sông Hồng", "546493", "0", "0", "94762", "69432", "20830", "4500", "0"],
        ["Hà Nội", "98454", None, None, "25835", "21100", "4235", "500", None],
        ["Hải Phòng", "43000", None, None, "8000", "5000", "3000", None, None],
        ["Vĩnh Phúc", "28986", None, None, "9414", "6549", "865", "2000", None],
        ["Bắc Ninh", "37338", None, None, "5000", "4000", "1000", None, None],
        ["Hải Dương", "62774", None, None, "4500", "3000", "1500", None, None],
        ["Hưng Yên", "40671", None, None, "7550", "6000", "1550", None, None],
        ["Hà Nam", "35403", None, None, "5555", "4655", "900", None, None],
        ["Nam Định", "78602", None, None, "6216", "4116", "2100", None, None],
        ["Thái Bình", "83164", None, None, "13362", "9812", "3550", None, None],
        ["Ninh Bình", "38101", None, None, "9330", "5200", "2130", "2000", None],
        ["Đông Bắc", "319224", "5083", "0", "282276", "204458", "34918", "39484", "3416"],
        ["Hà Giang", "25600", None, None, "41273", "40000", "433", None, "840"],
        ["Cao Bằng", "25239", "669", None, "12551", "12351", "100", "100", None],
        ["Lào Cai", "16025", "498", None, "28645", "25014", "296", "2800", "535"],
        ["Bắc Cạn", "13234", "136", None, "17531", "15482", "356", "1555", "138"],
        ["Lạng Sơn", "31200", None, None, "22700", "17000", "1200", "4000", "500"],
        ["Tuyên Quang", "25225", None, None, "14000", "10000", "4000", None, None],
        ["Yên Bái", "23257", "3780", None, "34944", "17330", "2614", "15000", None],
        ["Thái Nguyên", "41053", None, None, "32948", "20961", "7941", "4046", None],
        ["Phú Thọ", "34000", None, None, "33320", "25000", "3200", "5120", None],
        ["Bắc Giang", "56116", None, None, "27144", "12000", "8778", "5763", "603"],
        ["Quảng Ninh", "28275", None, None, "17220", "9320", "6000", "1100", "800"],
        ["Tây Bắc", "112241", "40821", "0", "218237", "179405", "5532", "29000", "4300"],
        ["Lai Châu", "26117", "8965", None, "15000", "15000", None, None, None],
        ["Điện Biên", "35184", "19836", None, "30000", "30000", None, None, None],
        ["Sơn La", "26730", "12020", None, "123672", "104405", "267", "16000", "3000"],
        ["Hoà Bình", "24210", None, None, "49565", "30000", "5265", "13000", "1300"],
        ["Bắc Trung Bộ", "192600", None, "160267", "181280", "101981", "33799", "43000", "2500"],
        ["Thanh Hoá", "135000", None, None, "59535", "40736", "11799", "7000", None],
        ["Nghệ An", "45000", None, "59000", "57600", "41100", "4500", "12000", None],
        ["Hà Tĩnh", "6500", None, "41910", "22145", "10145", "10000", "2000", None],
        ["Quảng Bình", "1000", None, "16435", "13000", "5000", "1000", "7000", None],
        ["Quảng Trị", "4500", None, "19000", "16500", "3000", "2500", "9000", "2000"],
        ["Thừa Thiên Huế", "600", None, "23922", "12500", "2000", "4000", "6000", "500"],
    ]

    for row in pl2_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # Lúa Mùa Total
        val_mua = normalize_number(row[1])
        if val_mua:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"},
                "metric_context": {"attribute": "Area_Planted", "value": val_mua / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Lúa Mùa Nương
        val_nuong = normalize_number(row[2])
        if val_nuong:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa nương"},
                "metric_context": {"attribute": "Area_Planted", "value": val_nuong / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # Lúa Hè Thu
        val_ht = normalize_number(row[3])
        if val_ht:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": val_ht / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # Màu lương thực items
        # Ngô: index 5, Khoai lang: index 6, Sắn: index 7, Khác: index 8
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for i in range(4, 9):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-4][0], "sub_item": items[i-4][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })

    return {"metadata": metadata, "records": records}

def parse_pl3_08():
    # Phụ lục 3: Các tỉnh miền Bắc gieo trồng cây công nghiệp ngắn ngày và rau đậu đến 15/8/2009
    metadata = {
        "year": 2009,
        "month": 8,
        "appendix_number": "PL3",
        "source_file": "2009_08_PHULUC_T08_2009_PL3.md"
    }
    records = []
    
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    # Data from MD
    # Rows: Loc, Cây CN ngắn ngày Total, Đậu tương, Lạc, Mía, Thuốc lá, Rau đậu các loại
    pl3_data = [
        ["Miền Bắc", "346359", "141421", "159491", "34923", "9594", "336718"],
        ["ĐB sông Hồng", "109271", "73620", "32530", "871", "2250", "136806"],
        ["Hà Nội", "43073", "35500", "7573", None, None, "25136"],
        ["Hải Phòng", "2600", "200", "150", None, "2250", "15400"],
        ["Vĩnh Phúc", "8157", "1268", "6826", "63", None, "6684"],
        ["Bắc Ninh", "4507", "3295", "1212", None, None, "10730"],
        ["Hải Dương", "1205", "205", "1000", None, None, "25000"],
        ["Hưng Yên", "5230", "3600", "1630", None, None, "12000"],
        ["Hà Nam", "10877", "9877", "1000", None, None, "6175"],
        ["Nam Định", "10039", "3500", "6539", None, None, "13000"],
        ["Thái Bình", "10200", "8100", "2100", None, None, "16000"],
        ["Ninh Bình", "13383", "8075", "4500", "808", None, "6681"],
        ["Đông Bắc", "83310", "31862", "41813", "2475", "7160", "80091"],
        ["Hà Giang", "13093", "8540", "4553", None, None, "9490"],
        ["Cao Bằng", "9108", "5147", "922", "1460", "1579", "2854"],
        ["Lào Cai", "7295", "6565", "648", None, "82", "3594"],
        ["Bắc Cạn", "3373", "2010", "462", "165", "736", "2476"],
        ["Lạng Sơn", "7133", "850", "1582", "200", "4501", "6732"],
        ["Tuyên Quang", "6457", "3000", "3457", None, None, "4534"],
        ["Yên Bái", "3280", "717", "2563", None, None, "6429"],
        ["Thái Nguyên", "5313", "717", "4596", None, None, "12685"],
        ["Phú Thọ", "11338", "1238", "10000", "100", None, "8289"],
        ["Bắc Giang", "13020", "2078", "10430", "250", "262", "12508"],
        ["Quảng Ninh", "3900", "1000", "2600", "300", None, "10500"],
        ["Tây Bắc", "38765", "21095", "8395", "8345", "0", "15681"],
        ["Lai Châu", "2532", "1532", "1000", None, None, "1500"],
        ["Điện Biên", "13435", "10965", "1600", None, None, "0"],
        ["Sơn La", "5867", "5012", "795", None, None, "3580"],
        ["Hoà Bình", "16931", "3586", "5000", "8345", None, "10601"],
        ["Bắc Trung Bộ", "115013", "14844", "76753", "23232", "184", "104140"],
        ["Thanh Hoá", "34596", "4047", "16837", "13712", None, "45600"],
        ["Nghệ An", "34100", "600", "24000", "9500", None, "29550"],
        ["Hà Tĩnh", "32113", "10197", "21916", None, None, "14990"],
        ["Quảng Bình", "5000", None, "5000", None, None, "7000"],
        ["Quảng Trị", "5123", None, "5000", "20", "103", "2000"],
        ["Thừa Thiên Huế", "4081", None, "4000", None, "81", "5000"],
    ]

    for row in pl3_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # Items list
        items = [
            ("Cây công nghiệp ngắn ngày", "Tổng số"),
            ("Đậu tương", None),
            ("Lạc", None),
            ("Mía", "Trồng mới"),
            ("Thuốc lá", None),
            ("Rau, đậu các loại", None)
        ]
        
        for i in range(1, 7):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })

    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    # Create Batch 1 JSONs
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/08"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl1_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL1.json"))
    save_json(parse_pl2_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL2.json"))
    save_json(parse_pl3_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL3.json"))
    print("Successfully parsed PL1, PL2, PL3 for August 2009.")
