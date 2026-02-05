import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if not s or s.strip() == "" or s.strip() == "||" or s.strip() == "|" or s.strip() == '"':
        return None
    s = s.strip().replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    # Handle thousands separator as dot for specific Vietnamese numbers if any (e.g. 20.690,6)
    if " " in s: s = s.split()[0] # basic cleanup
    if "." in s and "," in s: # e.g. 20.690,6
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    if s == "" or s == "-" or s == '.':
        return None
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl1_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL1", "source_file": "2009_06_PHULUC_T06_2009_PL1.md"}
    records = []
    
    # [Item, Sub, v08, v09, location, geo, attribute, unit]
    rows = [
        ["Lúa", "Đông Xuân", "658.8", "969.4", "Miền Bắc", "Regional", "Area_Harvested", "1000_ha"],
        ["Lúa", "Đông Xuân", "294.4", "542.7", "Đồng bằng sông Hồng", "Regional", "Area_Harvested", "1000_ha"],
        ["Lúa", "Đông Xuân", "294.1", "336.1", "Bắc Trung bộ", "Regional", "Area_Harvested", "1000_ha"],
        ["Lúa", "Hè Thu", "2044.9", "2016.8", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Lúa", "Hè Thu", "118.7", "129.6", "Miền Bắc", "Regional", "Area_Planted", "1000_ha"],
        ["Lúa", "Hè Thu", "1926.2", "1887.2", "Miền Nam", "Regional", "Area_Planted", "1000_ha"],
        ["Lúa", "Hè Thu", "1597.3", "1581.2", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted", "1000_ha"],
        ["Màu lương thực", "Tổng số", "1226.5", "1222.8", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Ngô", None, "796.1", "779.9", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Khoai lang", None, "111.5", "112.9", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Sắn", None, "295.2", "306.2", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Cây công nghiệp ngắn ngày", "Tổng số", "539.5", "563.2", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Lạc", None, "195.5", "204.5", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Đậu tương", None, "130.7", "137.9", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Thuốc lá", None, "24.9", "25.5", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Mía", "Trồng mới", "143.8", "150.7", "Cả nước", "National", "Area_Planted", "1000_ha"],
        ["Rau, đậu các loại", None, "530.4", "533.6", "Cả nước", "National", "Area_Planted", "1000_ha"],
        # Section 4: Production
        ["Tổng sản lượng lương thực", "Đông Xuân", None, "20690.6", "Cả nước", "National", "Production", "1000_ton"],
        ["Tổng sản lượng lương thực", "Đông Xuân", None, "8534.5", "Miền Bắc", "Regional", "Production", "1000_ton"],
        ["Tổng sản lượng lương thực", "Đông Xuân", None, "12156.1", "Miền Nam", "Regional", "Production", "1000_ton"],
        ["Lúa", "Đông Xuân", None, "18638.7", "Cả nước", "National", "Production", "1000_ton"],
        ["Ngô", "Đông Xuân", None, "2051.0", "Cả nước", "National", "Production", "1000_ton"],
    ]

    for row in rows:
        item, sub, v08, v09, loc, geo, attr, unit = row
        for y, v in [(2008, v08), (2009, v09)]:
            val = normalize_number(v)
            if val is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": y, "month": 6, "period_type": "Cumulative", "report_date": f"{y}-06-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                    "metric_context": {"attribute": attr, "value": val, "unit": unit, "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}


def parse_pl2_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL2", "source_file": "2009_06_PHULUC_T06_2009_PL2.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    rows = [
        ["Miền Bắc", "1143879", "84.8", "151693", "174046", "757967", "546337", "96210", "109711", "8394"],
        ["ĐB sông Hồng", "549657", "98.7", "37263", "5259", "87136", "62627", "20331", "4176", "2"],
        ["Hà Nội", "99791", "98.7", "4682", None, "22661", "17221", "4540", "900", None],
        ["Hải Phòng", "40125", "99.6", "200", None, "7567", "4700", "2867", None, None],
        ["Vĩnh Phúc", "31020", "100.0", None, "2709", "6387", "4785", "324", "1276", "2"],
        ["Bắc Ninh", "37234", "93.1", "157", None, "4503", "3503", "1000", None, None],
        ["Hải Dương", "63827", "97.1", "1805", "1900", "5100", "3700", "1400", None, None],
        ["Hưng Yên", "40323", "98.4", "3000", None, "9534", "8034", "1500", None, None],
        ["Hà Nam", "34282", "100.0", None, None, "3753", "3053", "700", None, None],
        ["Nam Định", "78339", "100.0", "919", None, "5841", "3841", "2000", None, None],
        ["Thái Bình", "83277", "100.0", "1500", "500", "12100", "8600", "3500", None, None],
        ["Ninh Bình", "41439", "98.9", "25000", "150", "9690", "5190", "2500", "2000", None],
        ["Đông Bắc", "219310", None, "1953", "6736", "268255", "203988", "30722", "30832", "2713"],
        ["Hà Giang", "9818", None, None, None, "39481", "38209", "433", None, "839"],
        ["Cao Bằng", "6575", None, None, None, "24186", "24026", "80", "80", None],
        ["Lào Cai", "9039", "27.7", "313", "5500", "30274", "21262", "341", "8000", "671"],
        ["Bắc Cạn", "7518", None, "140", "1236", "23797", "21996", "256", "1345", "200"],
        ["Lạng Sơn", "14225", None, None, None, "15300", "14000", "900", None, "400"],
        ["Tuyên Quang", "19778", "40.4", "1500", None, "20174", "16174", "4000", None, None],
        ["Yên Bái", "17238", None, None, None, "27421", "12530", "1993", "12898", None],
        ["Thái Nguyên", "28636", "40.0", None, None, "27251", "16673", "6832", "3746", None],
        ["Phú Thọ", "36925", "67.7", None, None, "27674", "24509", "3165", None, None],
        ["Bắc Giang", "52240", None, None, None, "22774", "9901", "7507", "4763", "603"],
        ["Quảng Ninh", "17318", "74.8", None, None, "9923", "4708", "5215", None, None],
        ["Tây Bắc", "38854", "68.9", "177", "32426", "207010", "169425", "5150", "28262", "4173"],
        ["Lai Châu", "5256", "41.1", None, "5000", "20774", "15524", "0", "5100", "150"],
        ["Điện Biên", "7872", "70.0", "150", "22391", "41076", "30576", "0", "10500", None],
        ["Sơn La", "9416", "34.1", "27", "5035", "102260", "99325", "150", None, "2785"],
        ["Hoà Bình", "16310", "97.5", None, None, "42900", "24000", "5000", "12662", "1238"],
        ["Bắc Trung Bộ", "336058", "100.0", "112300", "129625", "195566", "110297", "37322", "46441", "1506"],
        ["Thanh Hoá", "120000", "100.0", "112000", "10545", "58555", "41000", "10555", "7000", None],
        ["Nghệ An", "85720", "100.0", None, "30000", "77058", "50713", "10141", "16204", None],
        ["Hà Tĩnh", "53537", "100.0", None, "39000", "21157", "8831", "10326", "2000", None],
        ["Quảng Bình", "27500", "100.0", None, "15000", "12600", "5000", "600", "7000", None],
        ["Quảng Trị", "23504", "100.0", None, "13500", "14743", "3000", "2500", "8237", "1006"],
        ["Thừa Thiên Huế", "25797", "100.0", "300", "21580", "11453", "1753", "3200", "6000", "500"],
    ]
    
    for row in rows:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # 1. Lúa DX Planted
        val = normalize_number(row[1])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative", "report_date": "2009-06-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # 2. Lúa DX Harvested % -> Derived or ignore.
        
        # 3. Mau HT/Mua Planted
        val_ht = normalize_number(row[4])
        if val_ht is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative", "report_date": "2009-06-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu/Mùa"},
                "metric_context": {"attribute": "Area_Planted", "value": val_ht / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # 4. Màu LT items
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for i in range(5, 10):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative", "report_date": "2009-06-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-5][0], "sub_item": items[i-5][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}


def parse_pl3_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL3", "source_file": "2009_06_PHULUC_T06_2009_PL3.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    rows = [
        ["Miền Bắc", "448251", "114657", "139745", "34863", "9703", "263525"],
        ["ĐB sông Hồng", "105684", "73189", "29500", "758", "2237", "114242"],
        ["Hà Nội", "42000", "35000", "7000", None, None, "20154"],
        ["Hải Phòng", "2537", "200", "100", None, "2237", "12353"],
        ["Vĩnh Phúc", "15068", "8637", "6381", "50", None, "4319"],
        ["Bắc Ninh", "3519", "2466", "1053", None, None, "1730"],
        ["Hải Dương", "200", "200", "0", None, None, "23968"],
        ["Hưng Yên", "5188", "3561", "1627", None, None, "12000"],
        ["Hà Nam", "9000", "8500", "500", None, None, "5599"],
        ["Nam Định", "7889", "1550", "6239", None, None, "13000"],
        ["Thái Bình", "8100", "6000", "2100", None, None, "15438"],
        ["Ninh Bình", "12283", "7075", "4500", "708", None, "5681"],
        ["Đông Bắc", "135007", "20864", "32279", "2538", "7286", "72040"],
        ["Hà Giang", "20586", "7543", "4553", None, None, "8490"],
        ["Cao Bằng", "5881", "994", "234", "1975", "1179", "1499"],
        ["Lào Cai", "6677", "2353", "648", None, "82", "3594"],
        ["Bắc Cạn", "3442", "1165", "362", "137", "763", "1015"],
        ["Lạng Sơn", "12115", "800", "1082", None, "4501", "5732"],
        ["Tuyên Quang", "10534", "3000", "3000", None, None, "4534"],
        ["Yên Bái", "7230", "1238", "1563", None, None, "4429"],
        ["Thái Nguyên", "15168", "1157", "3588", "150", "264", "10009"],
        ["Phú Thọ", "14345", "1056", "5000", None, None, "8289"],
        ["Bắc Giang", "29291", "900", "9669", "276", "497", "17949"],
        ["Quảng Ninh", "9738", "658", "2580", None, None, "6500"],
        ["Tây Bắc", "40697", "16530", "6729", "8345", "0", "9038"],
        ["Lai Châu", "2989", "1032", "700", None, None, "1257"],
        ["Điện Biên", "11250", "9650", "1600", None, None, "0"],
        ["Sơn La", "5811", "3062", "514", None, None, "2235"],
        ["Hoà Bình", "20647", "2786", "3915", "8345", None, "5601"],
        ["Bắc Trung Bộ", "166863", "4074", "71237", "23222", "180", "68150"],
        ["Thanh Hoá", "70223", "4074", "16837", "13712", None, "35600"],
        ["Nghệ An", "45050", None, "20000", "9500", None, "15550"],
        ["Hà Tĩnh", "23400", None, "20400", None, None, "3000"],
        ["Quảng Bình", "12000", None, "5000", None, None, "7000"],
        ["Quảng Trị", "7110", None, "5000", "10", "100", "2000"],
        ["Thừa Thiên Huế", "9080", None, "4000", None, "80", "5000"],
    ]
    
    for row in rows:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        items = [("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Mía", "Trồng mới"), ("Thuốc lá", None), ("Rau, đậu các loại", None)]
        for i in range(1, 7):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative", "report_date": "2009-06-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/06"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl1_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL1.json"))
    save_json(parse_pl2_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL2.json"))
    save_json(parse_pl3_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL3.json"))
    
    print("Successfully parsed PL1, PL2, PL3 for June 2009.")
