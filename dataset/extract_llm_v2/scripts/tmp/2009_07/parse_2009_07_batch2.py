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
        # Handle cases like "43,440\n9,211" if they occur in raw markdown
        if "\n" in s:
            s = s.split("\n")[0] # Take the first one if multi-row data in one cell
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl4_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL4", "source_file": "2009_07_PHULUC_T07_2009_PL4.md"}
    records = []
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Rows: Loc, Lúa HT Planted, Lúa HT Harvested, Lúa Mùa Planted, Màu LT Total, Ngô, K.Lang, Sắn, Khác
    pl4_data = [
        ["Miền Nam", "1866288", "578121", "212930", "586372", "262709", "17144", "292060", "14459"],
        ["D.H Nam Trg Bộ", "158260", "20323", "13297", "85254", "20942", "4723", "58948", "641"],
        ["TP Đà Nẵng", "3751", None, None, "1187", "664", "437", "86", None],
        ["Quảng Nam", "40500", None, None, "22300", "5600", "3700", "13000", None],
        ["Quảng Ngãi", "31641", None, None, "18915", "3206", "200", "15509", None],
        ["Bình Định", "41098", "20122", "12867", "15507", "4954", None, "10553", None],
        ["Phú Yên", "23500", "201", "430", "17707", "3398", "226", "13800", "283"],
        ["Khánh Hoà", "17770", None, None, "9638", "3120", "160", "6000", "358"],
        ["Tây Nguyên", "6175", "0", "135809", "270269", "151285", "4962", "114022", "0"],
        ["Kon Tum", None, None, "15414", "42612", "7388", "152", "35072", None],
        ["Gia Lai", None, None, "30300", "82801", "35588", "572", "46641", None],
        ["Đắc Lắc", None, None, "43148", "93792", "74315", "968", "18509", None],
        ["Đắc Nông", None, None, "35120", "33975", "20575", "2100", "11300", None],
        ["Lâm Đồng", "6175", None, "11827", "17089", "13419", "1170", "2500", None],
        ["Đông Nam Bộ", "148364", "615", "100", "189522", "66603", "852", "117199", "4868"],
        ["TP Hồ Chí Minh", "6967", "500", "100", "1067", "1067", None, None, None],
        ["Ninh Thuận", "12400", None, None, "6407", "6407", None, None, None],
        ["Bình Phước", "11986", None, None, "30412", "6150", "164", "24000", "98"],
        ["Tây Ninh", "47094", "115", None, "43896", "5896", None, "38000", None],
        ["Bình Dương", "1437", None, None, "6637", "43", "1", "2316", "4277"],
        ["Đồng Nai", "24574", None, None, "41590", "25337", "135", "16000", "118"],
        ["Bình Thuận", "36400", None, None, "40918", "11171", "372", "29000", "375"],
        ["Bà Rịa-V.Tàu", "7506", None, None, "18595", "10532", "180", "7883", None],
        ["ĐBS Cửu Long", "1553489", "557183", "63724", "41327", "23879", "6607", "1891", "8950"],
        ["Long An", "194579", "51977", None, "3762", "3762", None, None, None],
        ["Đồng Tháp", "195845", "101136", None, "5217", "3295", "1065", None, "857"],
        ["An Giang", "230884", "123522", None, "6299", "6179", "120", None, None],
        ["Tiền Giang", "76000", "30717", None, "5628", "3371", "238", "400", "1619"],
        ["Vĩnh Long", "63003", "55727", None, "8886", "911", "2077", "156", "5742"],
        ["Bến Tre", "24157", None, "35000", "924", "420", "175", "117", "212"],
        ["Kiên Giang", "271841", "22072", None, "700", None, "700", None, None],
        ["Cần Thơ", "84129", "72129", None, "629", "629", None, None, None],
        ["Hậu Giang", "72856", "47296", None, "1548", "1028", None, None, "520"],
        ["Trà Vinh", "82431", "18195", None, "6181", "4068", "1311", "802", None],
        ["Sóc Trăng", "167000", "34412", "26941", "1553", "216", "921", "416", None],
        ["Bạc Liêu", "55777", None, "1783", "0", None, None, None, None],
        ["Cà Mau", "34987", None, None, "0", None, None, None, None],
    ]

    for row in pl4_data:
        loc = row[0]
        geo = "Regional" if loc in regional_list else "Provincial"
        
        # Lúa HT Gieo cấy
        v = normalize_number(row[1])
        if v is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Lúa HT Thu hoạch
        v = normalize_number(row[2])
        if v is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Harvested", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # Lúa Mùa Gieo cấy
        v = normalize_number(row[3])
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
        for i in range(4, 9):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative", "report_date": "2009-07-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-4][0], "sub_item": items[i-4][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}

def parse_pl5_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL5", "source_file": "2009_07_PHULUC_T07_2009_PL5.md"}
    records = []
    regional_list = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Rows: Loc, Cây CN ngắn ngày Total, Đậu tương, Lạc, Vừng, Thuốc lá, Mía, Bông, Đay/Lác, Rau các loại, Đậu các loại
    pl5_data = [
        ["Miền Nam", "242138", "23573", "66208", "21591", "15547", "113273", "1454", "492", "234258", "43440"],
        ["D.H Nam Trg Bộ", "66795", "1067", "22163", "4419", "713", "38114", "277", "42", "25214", "25214"],
        ["TP Đà Nẵng", "1235", None, "722", "238", None, "275", None, None, "837", "80"],
        ["Quảng Nam", "9210", None, "8100", None, "330", "780", None, None, "6900", "3500"],
        ["Quảng Ngãi", "5988", None, "3787", None, None, "2201", None, None, "5433", "1521"],
        ["Bình Định", "13624", "751", "8792", "1774", None, "2307", None, None, "9254", "1630"],
        ["Phú Yên", "19512", "316", "562", "2407", "383", "15525", "277", "42", "2690", "1980"],
        ["Khánh Hoà", "17226", None, "200", None, None, "17026", None, None, "100", "500"],
        ["Tây Nguyên", "32009", "14136", "3484", "1965", "5695", "6729", None, None, "41635", "17273"],
        ["Kon Tum", "2404", None, "14", None, "2158", "232", None, None, "630", "57"],
        ["Gia Lai", "5722", None, "815", "982", "3457", "468", None, None, "7605", "8138"],
        ["Đắc Lắc", "12759", "4438", "2655", "983", "80", "4603", None, None, "2350", "8579"],
        ["Đắc Nông", "9776", "9698", None, None, None, "78", None, None, "1550", "201"],
        ["Lâm Đồng", "1348", None, None, None, None, "1348", None, None, "29500", "298"],
        ["Đông Nam Bộ", "56128", "563", "25427", "6135", "8946", "15013", "44", None, "42255", "13133"],
        ["TP Hồ Chí Minh", "2978", None, "778", None, None, "2200", None, None, "8384", None],
        ["Ninh Thuận", "1367", None, "200", "35", "480", "620", "32", None, "6900", "500"],
        ["Bình Phước", "143", None, "132", "11", None, None, None, None, "701", "145"],
        ["Tây Ninh", "32670", None, "16167", "1007", "7748", "7748", None, None, "10692", "4990"],
        ["Bình Dương", "81", None, "81", None, None, None, None, None, "2024", "64"],
        ["Đồng Nai", "8941", "321", "4156", "69", "580", "3815", None, None, "9110", "3759"],
        ["Bình Thuận", "9274", "242", "3487", "5013", "35", "485", "12", None, "2216", "3178"],
        ["Bà Rịa-V.Tàu", "674", None, "426", None, "103", "145", None, None, "2228", "497"],
        ["ĐBS Cửu Long", "87087", "7807", "15134", "9072", "193", "53417", "1133", "450", "125154", "3823"],
        ["Long An", "23099", None, "6966", "1752", None, "14381", None, None, "6510", None],
        ["Đồng Tháp", "8484", "5434", "166", "2737", "16", "131", None, None, "8602", None],
        ["An Giang", "842", "183", "215", "420", "6", "18", None, None, "8433", "1090"],
        ["Tiền Giang", None, None, None, None, None, "119", None, None, "25200", None],
        ["Vĩnh Long", "1615", "1189", "28", "331", None, "67", None, None, "15942", "370"],
        ["Bến Tre", "7360", None, "391", None, None, "6969", None, None, "2082", "128"],
        ["Kiên Giang", "0", None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", "8177", "747", "3587", "3832", "11", None, None, None, "5898", "201"],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "6068", None],
        ["Trà Vinh", "10752", None, "3627", None, None, "5542", "1133", "450", "17979", "841"],
        ["Sóc Trăng", "13305", "254", "154", None, "160", "12737", None, None, "22940", "1193"],
        ["Bạc Liêu", None, None, None, None, None, None, None, None, "5500", None],
        ["Cà Mau", None, None, None, None, None, None, None, None, None, None],
    ]

    for row in pl5_data:
        loc = row[0]
        geo = "Regional" if loc in regional_list else "Provincial"
        items = [
            ("Cây công nghiệp ngắn ngày", "Tổng số"), 
            ("Đậu tương", None), 
            ("Lạc", None), 
            ("Vừng", None), 
            ("Thuốc lá", None), 
            ("Mía", "Trồng mới"), 
            ("Bông", None), 
            ("Đay, Lác", None), 
            ("Rau các loại", None), 
            ("Đậu các loại", None)
        ]
        for i in range(1, 11):
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
    save_json(parse_pl4_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL4.json"))
    save_json(parse_pl5_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL5.json"))
    print("Successfully parsed PL4, PL5 for July 2009.")
