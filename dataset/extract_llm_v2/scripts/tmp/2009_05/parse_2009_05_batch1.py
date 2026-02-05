import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if not s or s.strip() == "" or s.strip() == "||" or s.strip() == "|" or s.strip() == '"':
        return None
    s = s.strip().replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    if s == "" or s == "-" or s == '.':
        return None
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl1_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL1", "source_file": "2009_05_PHULUC_T05_2009_PL1.md"}
    records = []
    
    rows = [
        # Item, Sub, v08, v09, location, geo, attribute
        ["Lúa", "Hè Thu", "1348.0", "1344.6", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Hè Thu", "1182.2", "1191.7", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "1831.1", "1844.1", "Miền Nam", "Regional", "Area_Harvested"],
        ["Lúa", "Đông Xuân", "160.0", "159.8", "Duyên hải miền Trung", "Regional", "Area_Harvested"],
        ["Lúa", "Đông Xuân", "54.5", "50.7", "Tây Nguyên", "Regional", "Area_Harvested"],
        ["Lúa", "Đông Xuân", "105.8", "89.9", "Đông Nam bộ", "Regional", "Area_Harvested"],
        ["Lúa", "Đông Xuân", "1510.7", "1543.7", "Đồng bằng sông Cửu Long", "Regional", "Area_Harvested"],
        ["Màu lương thực", "Tổng số", "1093.3", "1089.5", "Cả nước", "National", "Area_Planted"],
        ["Ngô", None, "710.3", "715.0", "Cả nước", "National", "Area_Planted"],
        ["Khoai lang", None, "103.8", "99.4", "Cả nước", "National", "Area_Planted"],
        ["Sắn", None, "254.7", "250.9", "Cả nước", "National", "Area_Planted"],
        ["Cây công nghiệp ngắn ngày", "Tổng số", "459.0", "465.4", "Cả nước", "National", "Area_Planted"],
        ["Lạc", None, "189.8", "194.5", "Cả nước", "National", "Area_Planted"],
        ["Đậu tương", None, "110.5", "129.8", "Cả nước", "National", "Area_Planted"],
        ["Thuốc lá, thuốc lào", None, "19.1", "19.6", "Cả nước", "National", "Area_Planted"],
        ["Mía", "Trồng mới", "99.9", "102.3", "Cả nước", "National", "Area_Planted"],
        ["Rau, đậu các loại", None, "495.5", "501.2", "Cả nước", "National", "Area_Planted"],
    ]
    
    for row in rows:
        item, sub, v08, v09, loc, geo, attr = row
        for y, v in [(2008, v08), (2009, v09)]:
            val = normalize_number(v)
            if val is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": y, "month": 5, "period_type": "Cumulative", "report_date": f"{y}-05-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                    "metric_context": {"attribute": attr, "value": val, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}

def parse_pl2_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL2", "source_file": "2009_05_PHULUC_T05_2009_PL2.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    rows = [
        ["Miền Bắc", "1154389", None, "19009", "775951", "541118", "87671", "137021"],
        ["ĐB sông Hồng", "564303", "58.9", "0", "83167", "61871", "17202", "4092"],
        ["Hà Nội", "99791", "97.6", None, "22577", "17221", "4540", "816"],
        ["Hải Phòng", "57069", "0.0", None, "3147", "1700", "1447", None],
        ["Vĩnh Phúc", "31020", "16.2", None, "5720", "4118", "324", "1276"],
        ["Bắc Ninh", "37234", "100.0", None, "4003", "3503", "500", None],
        ["Hải Dương", "63500", "0.0", None, "5100", "3700", "1400", None],
        ["Hưng Yên", "40323", "0.0", None, "9125", "8034", "1091", None],
        ["Hà Nam", "33000", "0.0", None, "7700", "7000", "700", None],
        ["Nam Định", "77650", "100.0", None, "5000", "3000", "2000", None],
        ["Thái Bình", "83277", "88.3", None, "11705", "8505", "3200", None],
        ["Ninh Bình", "41439", "100.0", None, "9090", "5090", "2000", "2000"],
        ["Đông Bắc", "215173", None, "0", "280335", "207041", "29120", "39158"],
        ["Hà Giang", "9885", None, None, "42488", "39659", "433", "2396"],
        ["Cao Bằng", "3300", None, None, "23500", "23500", None, None],
        ["Lào Cai", "8995", None, None, "27345", "20833", "341", "5500"],
        ["Bắc Cạn", "7393", None, None, "13847", "12201", "238", "1218"],
        ["Lạng Sơn", "14225", None, None, "18526", "13874", "884", "3768"],
        ["Tuyên Quang", "19778", "100.0", None, "19507", "16174", "3333", None],
        ["Yên Bái", "17361", "0.0", None, "34176", "19239", "2988", "11349"],
        ["Thái Nguyên", "28636", None, None, "25600", "16673", "3832", "5095"],
        ["Phú Thọ", "36925", "100.0", None, "32614", "24509", "3165", "4940"],
        ["Bắc Giang", "51457", None, None, "28363", "12298", "8691", "3819"],
        ["Quảng Ninh", "17218", None, None, "14369", "8081", "5215", "1073"],
        ["Tây Bắc", "38855", None, "18446", "223043", "163670", "5027", "50223"],
        ["Lai Châu", "5256", None, None, "16189", "11089", None, "5000"],
        ["Điện Biên", "7872", "100.0", "13846", "41076", "30576", None, "10500"],
        ["Sơn La", "9417", None, "4600", "123312", "98325", "141", "22061"],
        ["Hoà Bình", "16310", "100.0", None, "42466", "23680", "4886", "12662"],
        ["Bắc Trung Bộ", "336058", None, "563", "189406", "108536", "36322", "43548"],
        ["Thanh Hoá", "120000", "0.0", None, "56291", "40736", "10555", "5000"],
        ["Nghệ An", "85720", None, None, "76058", "50713", "9141", "16204"],
        ["Hà Tĩnh", "53537", None, None, "21157", "8831", "10326", "2000"],
        ["Quảng Bình", "27500", None, None, "11772", "4503", "600", "6669"],
        ["Quảng Trị", "23504", None, None, "13737", "2000", "2500", "8237"],
        ["Thừa Thiên Huế", "25797", "0.0", "563", "10391", "1753", "3200", "5438"],
    ]
    
    for row in rows:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # Lúa Đông Xuân
        val = normalize_number(row[1])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": "2009-05-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Lúa Hè Thu/Mùa
        val_ht = normalize_number(row[3])
        if val_ht is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": "2009-05-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": val_ht / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Màu
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None)]
        for i in range(4, 8):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": "2009-05-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-4][0], "sub_item": items[i-4][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}

def parse_pl3_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL3", "source_file": "2009_05_PHULUC_T05_2009_PL3.md"}
    records = []
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    rows = [
        ["Miền Bắc", "294708", "107862", "134834", "32562", "8445", "246829"],
        ["ĐB sông Hồng", "111222", "68155", "28659", "708", "2687", "105232"],
        ["Hà Nội", "39716", "32907", "6809", None, None, "19154"],
        ["Hải Phòng", "13450", "200", None, None, "2237", "10353"],
        ["Vĩnh Phúc", "14218", "7837", "6381", None, None, "3876"],
        ["Bắc Ninh", "3319", "2266", "1053", None, None, "1730"],
        ["Hải Dương", "100", "100", None, None, None, "20000"],
        ["Hưng Yên", "4562", "3353", "1209", None, None, "11000"],
        ["Hà Nam", "8500", "8000", "500", None, None, "5000"],
        ["Nam Định", "7739", "1500", "6239", None, None, "13000"],
        ["Thái Bình", "8417", "5917", "2050", None, "450", "15438"],
        ["Ninh Bình", "11201", "6075", "4418", "708", None, "5681"],
        ["Đông Bắc", "54544", "19119", "29380", "287", "5758", "72534"],
        ["Hà Giang", "10377", "6723", "3654", None, None, "8904"],
        ["Cao Bằng", "0", None, None, None, None, None],
        ["Lào Cai", "2952", "2267", "604", None, "81", "3322"],
        ["Bắc Cạn", "1819", "601", "345", "137", "736", "998"],
        ["Lạng Sơn", "6219", "736", "982", None, "4501", "5731"],
        ["Tuyên Quang", "5969", "2979", "2990", None, None, "3534"],
        ["Yên Bái", "2779", "1229", "1550", None, None, "3850"],
        ["Thái Nguyên", "5159", "1157", "3588", "150", "264", "10009"],
        ["Phú Thọ", "5870", "1056", "4814", None, None, "8289"],
        ["Bắc Giang", "10274", "1763", "8335", None, "176", "21777"],
        ["Quảng Ninh", "3126", "608", "2518", None, None, "6120"],
        ["Tây Bắc", "31436", "16514", "6577", "8345", "0", "9038"],
        ["Lai Châu", "1632", "1032", "600", None, None, "1257"],
        ["Điện Biên", "11212", "9634", "1578", None, None, None],
        ["Sơn La", "3546", "3062", "484", None, None, "2180"],
        ["Hoà Bình", "15046", "2786", "3915", "8345", None, "5601"],
        ["Bắc Trung Bộ", "97506", "4074", "70218", "23222", "0", "60025"],
        ["Thanh Hoá", "34623", "4074", "16837", "13712", None, "35475"],
        ["Nghệ An", "29101", None, "19601", "9500", None, "8550"],
        ["Hà Tĩnh", "20389", None, "20389", None, None, "3000"],
        ["Quảng Bình", "4950", None, "4950", None, None, "7000"],
        ["Quảng Trị", "4593", None, "4700", "10", None, "2000"],
        ["Thừa Thiên Huế", "3850", None, "3741", None, None, "4000"],
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
                    "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": "2009-05-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/05"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl1_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL1.json"))
    save_json(parse_pl2_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL2.json"))
    save_json(parse_pl3_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL3.json"))
    
    print("Successfully parsed PL1, PL2, PL3 for May 2009.")
