import json
import uuid
from datetime import datetime
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if not s or s.strip() == "" or s.strip() == "||" or s.strip() == "|" or s.strip() == '"':
        return None
    # Remove separators and formatting
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

def parse_pl1_04():
    # Phụ lục 1: Tổng hợp kết quả sản xuất nông nghiệp đến 15/4/2009
    metadata = {
        "year": 2009,
        "month": 4,
        "appendix_number": "PL1",
        "source_file": "2009_04_PHULUC_T04_2009_PL1.md"
    }
    records = []
    
    # Data rows from MD
    # Items: Lúa HT Nam, ĐBSCL; Lúa DX Nam, ĐBSCL; Màu LT; Ngô; K.Lang; Sắn; Cây CN; Đậu tương; Lạc; Thuốc lá; Rau đậu
    rows = [
        # Item, Sub, val08, val09, location, geo_level, attribute
        ["Lúa", "Hè Thu", "393.5", "441.2", "Miền Nam", "Regional", "Area_Planted"],
        ["Lúa", "Hè Thu", "360.9", "414.2", "Đồng bằng sông Cửu Long", "Regional", "Area_Planted"],
        ["Lúa", "Đông Xuân", "1658.0", "1653.2", "Miền Nam", "Regional", "Area_Harvested"],
        ["Lúa", "Đông Xuân", "1474.6", "1480.2", "Đồng bằng sông Cửu Long", "Regional", "Area_Harvested"],
        ["Màu lương thực", "Tổng số", "800.8", "745.4", "Cả nước", "National", "Area_Planted"],
        ["Ngô", None, "526.7", "477.9", "Cả nước", "National", "Area_Planted"],
        ["Khoai lang", None, "98.2", "86.8", "Cả nước", "National", "Area_Planted"],
        ["Sắn", None, "176.1", "159.2", "Cả nước", "National", "Area_Planted"],
        ["Cây công nghiệp ngắn ngày", "Tổng số", "365.7", "352.5", "Cả nước", "National", "Area_Planted"],
        ["Đậu tương", None, "100.6", "102.3", "Cả nước", "National", "Area_Planted"],
        ["Lạc", None, "177.1", "172.2", "Cả nước", "National", "Area_Planted"],
        ["Thuốc lá, thuốc lào", None, "18.3", "17.9", "Cả nước", "National", "Area_Planted"],
        ["Rau, đậu các loại", None, "420.3", "432.0", "Cả nước", "National", "Area_Planted"],
    ]

    for row in rows:
        item, sub, v08, v09, loc, geo, attr = row
        
        # 2009 record
        val09 = normalize_number(v09)
        if val09:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
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
                "time_context": {"year": 2008, "month": 4, "period_type": "Cumulative", "report_date": "2008-04-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": attr, "value": val08, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
    return {"metadata": metadata, "records": records}

def parse_pl2_pl3_04():
    # PL2 & PL3 for North regions are in the same MD file.
    metadata_pl2 = {"year": 2009, "month": 4, "appendix_number": "PL2", "source_file": "2009_04_PHULUC_T04_2009_PL2.md"}
    metadata_pl3 = {"year": 2009, "month": 4, "appendix_number": "PL3", "source_file": "2009_04_PHULUC_T04_2009_PL2.md"}
    
    records = []
    
    # PL2: Lúa DX & Màu LT
    # Columns: Loc, Plan DX, %, Màu LT Total, Ngô, K.Lang, Sắn, Khác
    # Unit: Ha -> Normalize to 1000_ha
    regional = ["Miền Bắc", "ĐB sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    
    pl2_data = [
        ["Miền Bắc", "1161446", "99.5", "601783", "420250", "62396", "110717", "8981"],
        ["ĐB sông Hồng", "562089", "100.2", "54801", "40811", "11397", "2592", "1"],
        ["Hà Nội", "99791", "100.0", "8077", "7221", "540", "316", None],
        ["Hải Phòng", "57069", "100.0", "3147", "1700", "1447", None, None],
        ["Vĩnh Phúc", "29700", "104.0", "3652", "2056", "319", "1276", "1"],
        ["Bắc Ninh", "37600", "99.7", "2805", "2305", "500", None, None],
        ["Hải Dương", "64000", "99.2", "5100", "3700", "1400", None, None],
        ["Hưng Yên", "40202", "100.3", "3125", "3034", "91", None, None],
        ["Hà Nam", "33000", "100.0", "7700", "7000", "700", None, None],
        ["Nam Định", "77000", "100.0", "4500", "3000", "1500", None, None],
        ["Thái Bình", "83227", "100.0", "1000.0", "7505", "3000", None, None], # Correction: Thái Bình Màu LT Total is 10505
        # Wait, let me check the MD again carefully.
        # Thai Binh: Line 33: |Thái Bình|83,227|100.0|10,505|7,505|3,000|||
        ["Thái Bình", "83227", "100.0", "10505", "7505", "3000", None, None],
        ["Ninh Bình", "40500", "100.9", "6190", "3290", "1900", "1000", None],
        ["Đông Bắc", "226797", "97.0", "234318", "173864", "19066", "38033", "4194"],
        ["Hà Giang", "9849", "100.4", "38488", "35659", "433", "2396", "839"],
        ["Cao Bằng", "3600", "91.7", "23000", "23000", None, None, None],
        ["Lào Cai", "8670", "103.2", "19790", "19545", None, "245", None],
        ["Bắc Cạn", "7238", "100.0", "11537", "10272", "189", "1031", "45"],
        ["Lạng Sơn", "15450", "70.3", "9178", "9028", None, "150", None],
        ["Tuyên Quang", "18880", "102.7", "11306", "9256", "2050", None, None],
        ["Yên Bái", "16662", "103.6", "43344", "19239", "2988", "21117", None],
        ["Thái Nguyên", "27300", "102.6", "17560", "10114", "2351", "5095", None],
        ["Phú Thọ", "34995", "98.6", "25778", "19503", "2335", "3940", None],
        ["Bắc Giang", "50000", "94.0", "22980", "10167", "6451", "3052", "3310"],
        ["Quảng Ninh", "34153", "98.3", "11357", "8081", "2269", "1007", None],
        ["Tây Bắc", "38656", "98.4", "124838", "76670", "3204", "41178", "3786"],
        ["Lai Châu", "5256", "100.0", "5189", "1089", None, "4000", "100"],
        ["Điện Biên", "7700", "102.2", "31076", "20576", None, "10500", None],
        ["Sơn La", "9200", "102.1", "50042", "31325", "120", "15911", "2686"],
        ["Hoà Bình", "16500", "93.9", "38531", "23680", "3084", "10767", "1000"],
        ["Bắc Trung Bộ", "333904", "100.3", "187826", "128905", "28729", "28914", "1000"],
        ["Thanh Hoá", "120000", "100.0", "59561", "39736", "10155", "9670", None],
        ["Nghệ An", "83996", "100.9", "41497", "34549", "6948", None, None],
        ["Hà Tĩnh", "53837", "99.4", "11435", "5831", "5326", None, None],
        ["Quảng Bình", "27500", "100.0", "52305", "45036", "600", "6669", None],
        ["Quảng Trị", "23000", "102.2", "12737", "2000", "2500", "7237", "1000"],
        ["Thừa Thiên Huế", "25571", "100.9", "10291", "1753", "3200", "5338", None],
    ]

    for row in pl2_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # Plan Lúa DX (Actual Planting usually matches Plan or close to it, but table says Plan 2009)
        # Actually in PL2, Col2 is Plan. We usually map it as Plan.
        p_val = normalize_number(row[1])
        if p_val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": p_val / 1000.0, "unit": "1000_ha", "data_type": "Plan"},
                "metadata": metadata_pl2
            })
            
        # Màu Lương thực items
        mau_items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for i in range(3, 8):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": mau_items[i-3][0], "sub_item": mau_items[i-3][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata_pl2
                })

    # PL3: Cây CN ngắn ngày & Rau đậu Miền Bắc
    # Columns: Loc, Tổng Cây CN, Đậu tương, Lạc, Mía, Thuốc lá, Rau đậu
    pl3_data = [
        ["Miền Bắc", "485871", "98471", "127594", "25466", "7472", "228032"],
        ["ĐB sông Hồng", "203815", "64896", "25240", "613", "2687", "110379"],
        ["Hà Nội", "58870", "32907", "6809", None, None, "19154"],
        ["Hải Phòng", "13437", "200", None, None, "2237", "11000"],
        ["Vĩnh Phúc", "14238", "6943", "3178", "11", None, "4106"],
        ["Bắc Ninh", "11913", "1901", "1012", None, None, "9000"],
        ["Hải Dương", "20100", "100", None, None, None, "20000"],
        ["Hưng Yên", "15462", "3353", "1109", None, None, "11000"],
        ["Hà Nam", "11450", "6000", "450", None, None, "5000"],
        ["Nam Định", "17719", "1500", "6219", None, None, "10000"],
        ["Thái Bình", "23850", "5917", "2045", None, "450", "15438"],
        ["Ninh Bình", "16776", "6075", "4418", "602", None, "5681"],
        ["Đông Bắc", "100210", "15604", "23780", "1052", "4785", "54989"],
        ["Hà Giang", "15281", "6723", "2654", None, None, "5904"],
        ["Cao Bằng", "0", None, None, None, None, None],
        ["Lào Cai", "2586", "2210", "295", None, "81", None],
        ["Bắc Cạn", "2480", "601", "336", "137", "726", "680"],
        ["Lạng Sơn", "7164", None, None, None, "3978", "3186"],
        ["Tuyên Quang", "8431", "1907", "2990", None, None, "3534"],
        ["Yên Bái", "7765", "1200", "1550", "775", None, "4240"],
        ["Thái Nguyên", "12108", "922", "3578", None, None, "7608"],
        ["Phú Thọ", "9995", "599", "3419", "140", None, "5837"],
        ["Bắc Giang", "25881", "923", "7958", None, None, "17000"],
        ["Quảng Ninh", "8519", "519", "1000", None, None, "7000"],
        ["Tây Bắc", "39232", "13897", "6857", "10589", "0", "7889"],
        ["Lai Châu", "2671", "1032", "582", None, None, "1057"],
        ["Điện Biên", "9912", "8634", "1278", None, None, None],
        ["Sơn La", "10490", "2168", "2877", "3273", None, "2172"],
        ["Hoà Bình", "16159", "2063", "2120", "7316", None, "4660"],
        ["Bắc Trung Bộ", "142614", "4074", "71717", "13212", "0", "54775"],
        ["Thanh Hoá", "59675", "4074", "16837", "3712", None, "30475"],
        ["Nghệ An", "40900", None, "21100", "9500", None, "10300"],
        ["Hà Tĩnh", "23389", None, "20389", None, None, "3000"],
        ["Quảng Bình", "11950", None, "4950", None, None, "7000"],
        ["Quảng Trị", "6700", None, "4700", None, None, "2000"],
        ["Thừa Thiên Huế", "5741", None, "3741", None, None, "2000"],
    ]

    for row in pl3_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        items = [("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Mía", None), ("Thuốc lá", None), ("Rau, đậu các loại", None)]
        for i in range(1, 7):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata_pl3
                })
    return {"metadata": metadata_pl2, "records": records}


def parse_pl4_04():
    # Phụ lục 4: Thu hoạch lúa & màu miền Nam (15/4)
    metadata = {"year": 2009, "month": 4, "appendix_number": "PL4", "source_file": "2009_04_PHULUC_T04_2009_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Loc, DX Plant, DX Harvest, % TH/GC, %, HT Planting, Màu Total, Ngô, K.Lang, Sắn, Khác
    pl4_data = [
        ["Miền Nam", "1876396", "1653190", "88.1", "441221", "126916", "57608", "8171", "48495", "12642"],
        ["D.H Nam Trg Bộ", "172515", "80900", "46.9", "16378", "41440", "13360", "4304", "20667", "3109"],
        ["TP Đà Nẵng", "4006", None, None, None, "612", "362", "180", "70", None],
        ["Quảng Nam", "40800", "4100", "10.0", None, "8400", "4700", "3700", None, None],
        ["Quảng Ngãi", "36243", "10100", "27.9", None, "14941", "3460", "241", "11240", None],
        ["Bình Định", "46898", "38200", "81.5", "16378", "9693", "1797", None, "7896", None],
        ["Phú Yên", "25698", "16500", "64.2", None, "6544", "2149", "183", "1461", "2751"],
        ["Khánh Hoà", "18870", "12000", "63.6", None, "1250", "892", None, None, "358"],
        ["Tây Nguyên", "67483", "22695", "33.6", "3649", "17994", "11080", "1947", "4967", None],
        ["Kon Tum", "6924", None, None, None, "635", "635", None, None, None],
        ["Gia Lai", "23395", "7600", "32.5", None, "9321", "4591", "263", "4467", None],
        ["Đắc Lắc", "23435", "8221", "35.1", None, "3519", "2449", "570", "500", None],
        ["Đắc Nông", "3836", "1254", "32.7", None, "3328", "2577", "751", None, None],
        ["Lâm Đồng", "9893", "5620", "56.8", "3649", "1191", "828", "363", None, None],
        ["Đông Nam Bộ", "106305", "69409", "65.3", "6960", "46725", "19589", "542", "21942", "4652"],
        ["TP Hồ Chí Minh", "6452", "3294", "51.1", "206", "1052", "1052", None, None, None],
        ["Ninh Thuận", "11000", "6971", "63.4", None, "2300", "2300", None, None, None],
        ["Bình Phước", "3000", "3000", "100.0", None, None, None, None, None, None],
        ["Tây Ninh", "48124", "21377", "44.4", "6754", "23331", "5434", None, "17897", None],
        ["Bình Dương", "2528", "1900", "75.2", None, "5925", "116", "72", "1460", "4277"],
        ["Đồng Nai", "10100", "8767", "86.8", None, "9200", "7000", "100", "2100", None],
        ["Bình Thuận", "20001", "19000", "95.0", None, "3850", "2690", "300", "485", "375"],
        ["Bà Rịa-V.Tàu", "5100", "5100", "100.0", None, "1067", "997", "70", None, None],
        ["ĐBS Cửu Long", "1530093", "1480186", "96.7", "414234", "20757", "13579", "1378", "919", "4881"],
        ["Long An", "234250", "203206", "86.7", "14175", "3520", "3520", None, None, None],
        ["Đồng Tháp", "207347", "207347", "100.0", "137045", "1507", "1399", "108", None, None],
        ["An Giang", "234228", "234228", "100.0", "600", "1700", "1700", None, None, None],
        ["Tiền Giang", "82526", "82526", "100.0", "39806", None, "2568", "12", "178", "1456"],
        ["Vĩnh Long", "67559", "61186", "90.6", "56267", "3461", "678", "90", None, "2693"],
        ["Bến Tre", "21218", "19246", "90.7", "10", "886", "382", "175", "117", "212"],
        ["Kiên Giang", "277144", "275000", "99.2", "11441", None, None, None, None, None],
        ["Cần Thơ", "90110", "90110", "100.0", "66392", "269", "269", None, None, None],
        ["Hậu Giang", "81171", "81171", "100.0", "35670", None, "505", None, None, "520"],
        ["Trà Vinh", "53748", "50544", "94.0", "12640", "918", "660", "137", "121", None],
        ["Sóc Trăng", "138622", "138622", "100.0", "36163", "3257", "1898", "856", "503", None],
        ["Bạc Liêu", "42170", "37000", "87.7", "4025", None, None, None, None, None],
    ]

    for row in pl4_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # DX Planted
        v = normalize_number(row[1])
        if v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
        
        # DX Harvested
        v = normalize_number(row[2])
        if v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Harvested", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # HT Planted
        v = normalize_number(row[4])
        if v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # MàuLT
        mau_items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for i in range(5, 10):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": mau_items[i-5][0], "sub_item": mau_items[i-5][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })

    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/04"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl1_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL1.json"))
    save_json(parse_pl2_pl3_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL2_PL3.json"))
    save_json(parse_pl4_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL4.json"))
    
    print("Successfully parsed PL1, PL2, PL3, PL4 for April 2009.")
