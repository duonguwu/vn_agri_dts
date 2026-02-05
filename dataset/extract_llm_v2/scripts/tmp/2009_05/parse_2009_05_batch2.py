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

def parse_pl4_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL4", "source_file": "2009_05_PHULUC_T05_2009_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    rows = [
        ["Miền Nam", "1892417", "1844115", "97.4", "1344584", "315376", "173906", "11772", "113889", "15809"],
        ["D.H Nam Trg Bộ", "173466", "159814", "92.1", "63680", "75655", "27220", "4507", "40819", "3109"],
        ["TP Đà Nẵng", "4014", "4014", "100.0", None, "1029", "680", "180", "169", None],
        ["Quảng Nam", "40800", "40800", "100.0", "34500", "27700", "13000", "3700", "11000", None],
        ["Quảng Ngãi", "36564", "35000", "95.7", "1555", "16241", "4760", "241", "11240", None],
        ["Bình Định", "47475", "38200", "80.5", "23375", "14847", "4314", None, "10533", None],
        ["Phú Yên", "25743", "23000", "89.3", "250", "12348", "2966", "226", "6405", "2751"],
        ["Khánh Hoà", "18870", "18800", "99.6", "4000", "3490", "1500", "160", "1472", "358"],
        ["Tây Nguyên", "65776", "50721", "77.1", "15746", "99998", "72606", "3573", "23819", None],
        ["Kon Tum", "6924", "3478", "50.2", None, "635", "635", None, None, None],
        ["Gia Lai", "23395", "16000", "68.4", "4186", "14177", "9447", "263", "4467", None],
        ["Đắc Lắc", "21728", "21728", "100.0", "4900", "46640", "37673", "847", "8120", None],
        ["Đắc Nông", "3836", "2698", "70.3", "1425", "28907", "15575", "2100", "11232", None],
        ["Lâm Đồng", "9893", "6817", "68.9", "5235", "9639", "9276", "363", None, None],
        ["Đông Nam Bộ", "106333", "89918", "84.6", "73488", "103130", "50227", "535", "47598", "4770"],
        ["TP Hồ Chí Minh", "6452", "6290", "97.5", "5552", "1359", "1359", None, None, None],
        ["Ninh Thuận", "11000", "6971", "63.4", "12400", "2300", "2300", None, None, None],
        ["Bình Phước", "3000", "3000", "100.0", None, "397", "397", None, None, None],
        ["Tây Ninh", "48124", "35900", "74.6", "17770", "24244", "5624", None, "18620", None],
        ["Bình Dương", "2528", "2528", "100.0", "553", "5925", "116", "72", "1460", "4277"],
        ["Đồng Nai", "10100", "10100", "100.0", "11465", "30574", "22256", "100", "8100", "118"],
        ["Bình Thuận", "20001", "20001", "100.0", "20814", "23509", "7544", "300", "15290", "375"],
        ["Bà Rịa-V.Tàu", "5128", "5128", "100.0", "4934", "14822", "10631", "63", "4128", None],
        ["ĐBS Cửu Long", "1546842", "1543662", "99.8", "1191670", "36593", "23853", "3157", "1653", "7930"],
        ["Long An", "248968", "248485", "99.8", "144979", "3762", "3762", None, None, None],
        ["Đồng Tháp", "207203", "207203", "100.0", "194862", "3804", "3057", "747", None, None],
        ["An Giang", "234098", "233545", "99.8", "226052", "6299", "6179", "120", None, None],
        ["Tiền Giang", "82526", "82526", "100.0", "61572", "4214", "2568", "12", "178", "1456"],
        ["Vĩnh Long", "67559", "67559", "100.0", "63432", "6888", "900", "90", "156", "5742"],
        ["Bến Tre", "21218", "21218", "100.0", "13000", "886", "382", "175", "117", "212"],
        ["Kiên Giang", "277144", "275000", "99.2", "148176", None, None, None, None, None],
        ["Cần Thơ", "90110", "90110", "100.0", "82970", "491", "491", None, None, None],
        ["Hậu Giang", "81171", "81171", "100.0", "72856", "1548", "1028", None, None, "520"],
        ["Trà Vinh", "56053", "56053", "100.0", "45259", "5444", "3588", "1157", "699", None],
        ["Sóc Trăng", "138622", "138622", "100.0", "89570", "3257", "1898", "856", "503", None],
        ["Bạc Liêu", "42170", "42170", "100.0", "40000", None, None, None, None, None],
        ["Cà Mau", None, None, None, "8942", None, None, None, None, None],
    ]
    
    for row in rows:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        report_date = "2009-05-15"
        
        # Lúa DX Planted
        val = normalize_number(row[1])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": report_date},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Lúa DX Harvested
        val = normalize_number(row[2])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": report_date},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Harvested", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Lúa HT Planted
        val = normalize_number(row[4])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": report_date},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # Màu
        items = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Màu lương thực khác", None)]
        for i in range(5, 10):
            v = normalize_number(row[i])
            if v is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": report_date},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-5][0], "sub_item": items[i-5][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}


def parse_pl5_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL5", "source_file": "2009_05_PHULUC_T05_2009_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    items = [
        ("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), 
        ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None), ("Rau các loại", None), ("Đậu các loại", None)
    ]
    
    raw_data = [
        ["Miền Nam", "207088", "21963", "59656", "13814", "11138", "99704", "321", "492", "181778", "32423<br>8975"],
        ["D.H Nam Trg Bộ", "58845", "1167", "21838", "3730", "713", "31078", "277", "42", "23966", "23966"],
        ["TP Đà Nẵng", "897", None, "720", None, None, "177", None, None, "501", "80"],
        ["Quảng Nam", "9210", None, "8100", None, "330", "780", None, None, "6900", "3500"],
        ["Quảng Ngãi", "3937", None, "3787", None, None, "150", None, None, "5433", "1521"],
        ["Bình Định", "12960", "851", "8479", "1323", None, "2307", None, None, "8669", "1410"],
        ["Phú Yên", "14615", "316", "552", "2407", "383", "10638", "277", "42", "2363", "1964"],
        ["Khánh Hoà", "17226", None, "200", None, None, "17026", None, None, "100", "500"],
        ["Tây Nguyên", "29526", "12498", "1662", "300", "5925", "9141", None, None, "27478", "9004"],
        ["Kon Tum", "2404", None, "14", None, "2158", "232", None, None, "630", "57"],
        ["Gia Lai", "10548", None, "248", None, "3457", "6843", None, None, "7805", "2706"],
        ["Đắc Lắc", "5450", "2800", "1400", "300", "310", "640", None, None, "2805", "5170"],
        ["Đắc Nông", "9776", "9698", None, None, None, "78", None, None, "1550", "201"],
        ["Lâm Đồng", "1348", None, None, None, None, "1348", None, None, "14688", "870"],
        ["Đông Nam Bộ", "47032", "563", "22637", "4383", "4307", "15098", "44", None, "41005", "11497"],
        ["TP Hồ Chí Minh", "3300", None, "1100", None, None, "2200", None, None, "6220", None],
        ["Ninh Thuận", "1367", None, "200", "35", "480", "620", "32", None, "6900", "500"],
        ["Bình Phước", "143", None, "132", "11", None, None, None, None, "701", "145"],
        ["Tây Ninh", "25694", None, "14079", "1007", "3109", "7499", None, None, "8796", "3523"],
        ["Bình Dương", "700", None, "429", None, None, "271", None, None, "2024", "64"],
        ["Đồng Nai", "8941", "321", "4156", "69", "580", "3815", None, None, "9110", "3759"],
        ["Bình Thuận", "6213", "242", "2115", "3261", "35", "548", "12", None, "2300", "3009"],
        ["Bà Rịa-V.Tàu", "674", None, "426", None, "103", "145", None, None, "4954", "497"],
        ["ĐBS Cửu Long", "71685", "7735", "13519", "5401", "193", "44387", None, "450", "89329", "2947"],
        ["Long An", "23099", None, "6966", "1752", None, "14381", None, None, "6510", None],
        ["Đồng Tháp", "8487", "5434", "169", "2737", "16", "131", None, None, "7938", None],
        ["An Giang", "842", "183", "215", "420", "6", "18", None, None, "8433", "1090"],
        ["Tiền Giang", None, None, None, None, None, None, None, None, "20211", None],
        ["Vĩnh Long", "1778", "1125", "28", "487", None, "138", None, None, "11200", "231"],
        ["Bến Tre", "5391", None, "391", None, None, "5000", None, None, "2082", "128"],
        ["Cần Thơ", "4324", "721", "3587", "5", "11", None, None, None, "2998", "201"],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "6068", None],
        ["Trà Vinh", "4230", None, "2088", None, None, "1692", None, "450", "6325", "426"],
        ["Sóc Trăng", "10081", "272", "75", None, "160", "9574", None, None, "12064", "871"],
        ["Bạc Liêu", None, None, None, None, None, None, None, None, "5500", None],
    ]

    for row in raw_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        for i in range(1, 11):
            cell = str(row[i]) if row[i] else None
            if not cell: continue
            cell_vals = cell.split("<br>")
            for cv in cell_vals:
                num = normalize_number(cv)
                if num is not None:
                    records.append({
                        "record_id": generate_id(),
                        "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative", "report_date": "2009-05-15"},
                        "geo_context": {"geo_level": geo, "location_name": loc},
                        "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                        "metric_context": {"attribute": "Area_Planted", "value": num / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                        "metadata": metadata
                    })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/05"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl4_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL4.json"))
    save_json(parse_pl5_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL5.json"))
    
    print("Successfully parsed PL4, PL5 for May 2009.")
