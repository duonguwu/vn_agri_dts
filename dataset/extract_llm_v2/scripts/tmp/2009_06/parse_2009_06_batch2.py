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

def parse_pl4_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL4", "source_file": "2009_06_PHULUC_T06_2009_PL4.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg B", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    rows = [
        ["Miền Nam", "1902663", "1880348", "1887170", "460331", "233540", "16664", "196525", "13602"],
        ["D.H Nam Trg B", "173456", "169079", "142113", "88288", "28276", "4723", "54648", "641"],
        ["TP Đà Nẵng", "4004", "4004", "3751", "1187", "664", "437", "86", None],
        ["Quảng Nam", "40800", "40800", "34500", "27700", "13000", "3700", "11000", None],
        ["Quảng Ngãi", "36564", "35000", "29364", "20469", "4760", "200", "15509", None],
        ["Bình Định", "47475", "47475", "41098", "15507", "4954", None, "10553", None],
        ["Phú Yên", "25743", "23000", "23500", "16407", "3398", "226", "12500", "283"],
        ["Khánh Hoà", "18870", "18800", "9900", "7018", "1500", "160", "5000", "358"],
        ["Tây Nguyên", "72254", "63721", "40593", "193852", "128112", "4545", "61195", None],
        ["Kon Tum", "6924", "6924", None, "635", "635", None, None, None],
        ["Gia Lai", "23395", "16000", "10870", "57482", "23109", "350", "34023", None],
        ["Đắc Lắc", "28242", "28242", "17988", "87080", "71408", "925", "14747", None],
        ["Đắc Nông", "3836", "2698", "6500", "33975", "20575", "2100", "11300", None],
        ["Lâm Đồng", "9857", "9857", "5235", "14680", "12385", "1170", "1125", None],
        ["Đông Nam Bộ", "109977", "103753", "123267", "136981", "52024", "948", "79141", "4868"],
        ["TP Hồ Chí Minh", "6452", "6452", "6500", "1400", "1400", None, None, None],
        ["Ninh Thuận", "11000", "11000", "12400", "6407", "6407", None, None, None],
        ["Bình Phước", "3000", "3000", None, "11959", "397", "164", "11300", "98"],
        ["Tây Ninh", "42124", "35900", "47094", "34104", "5896", None, "28208", None],
        ["Bình Dương", "2612", "2612", "2193", "5950", "116", "97", "1460", "4277"],
        ["Đồng Nai", "15874", "15874", "24574", "35590", "20337", "135", "15000", "118"],
        ["Bình Thuận", "23787", "23787", "23000", "22976", "6939", "372", "15290", "375"],
        ["Bà Rịa-V.Tàu", "5128", "5128", "7506", "18595", "10532", "180", "7883", None],
        ["ĐBS Cửu Long", "1546976", "1543795", "1581197", "41210", "25128", "6448", "1541", "8093"],
        ["Long An", "248968", "248485", "194579", "3762", "3762", None, None, None],
        ["Đồng Tháp", "207203", "207203", "212093", "3902", "3154", "748", None, None],
        ["An Giang", "234098", "233545", "232803", "6299", "6179", "120", None, None],
        ["Tiền Giang", "82747", "82747", "115792", "5381", "3371", "238", "153", "1619"],
        ["Vĩnh Long", "67560", "67559", "63753", "9062", "857", "2307", "156", "5742"],
        ["Bến Tre", "21130", "21130", "24157", "898", "394", "175", "117", "212"],
        ["Kiên Giang", "277144", "275000", "243382", "700", None, "700", None, None],
        ["Cần Thơ", "90110", "90110", "84129", "571", "571", None, None, None],
        ["Hậu Giang", "81171", "81171", "72856", "1548", "1028", None, None, "520"],
        ["Trà Vinh", "56053", "56053", "80642", "5444", "3588", "1157", "699", None],
        ["Sóc Trăng", "138622", "138622", "167000", "3643", "2224", "1003", "416", None],
        ["Bạc Liêu", "42170", "42170", "55024", None, None, None, None, None],
        ["Cà Mau", None, None, "34987", None, None, None, None, None],
    ]
    for row in rows:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        for idx, attr, sub in [(1, "Area_Planted", "Đông Xuân"), (2, "Area_Harvested", "Đông Xuân"), (3, "Area_Planted", "Hè Thu")]:
            val = normalize_number(row[idx])
            if val: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": sub}, "metric_context": {"attribute": attr, "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"}, "metadata": metadata})
        itms = [("Màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Khác", None)]
        for i in range(4, 9):
            val = normalize_number(row[i])
            if val: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Cultivation", "commodity": itms[i-4][0], "sub_item": itms[i-4][1]}, "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl5_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL5", "source_file": "2009_06_PHULUC_T06_2009_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    itms = [("Cây CN ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None), ("Rau các loại", None), ("Đậu các loại", None)]
    raw = [
        ["Miền Nam", "240257", "23222", "64720", "19813", "15818", "115871", "321", "492", "212995", "37074"],
        ["D.H Nam Trg Bộ", "66280", "1067", "22163", "3904", "713", "38114", "277", "42", "25214", "25214"],
        ["TP Đà Nẵng", "1235", None, "722", "238", None, "275", None, None, "837", "80"],
        ["Quảng Nam", "9210", None, "8100", None, "330", "780", None, None, "6900", "3500"],
        ["Quảng Ngãi", "5988", None, "3787", None, None, "2201", None, None, "5433", "1521"],
        ["Bình Định", "13109", "751", "8792", "1259", None, "2307", None, None, "9254", "1630"],
        ["Phú Yên", "19512", "316", "562", "2407", "383", "15525", "277", "42", "2690", "1980"],
        ["Khánh Hoà", "17226", None, "200", None, None, "17026", None, None, "100", "500"],
        ["Tây Nguyên", "38790", "13952", "2837", "2982", "5966", "13053", None, None, "37363", "10889"],
        ["Kon Tum", "2404", None, "14", None, "2158", "232", None, None, "630", "57"],
        ["Gia Lai", "12548", None, "248", "2000", "3457", "6843", None, None, "7805", "2706"],
        ["Đắc Lắc", "12714", "4254", "2575", "982", "351", "4552", None, None, "4378", "7529"],
        ["Đắc Nông", "9776", "9698", None, None, None, "78", None, None, "1550", "201"],
        ["Lâm Đồng", "1348", None, None, None, None, "1348", None, None, "23000", "396"],
        ["Đông Nam Bộ", "55335", "563", "26097", "4401", "8946", "15284", "44", None, "41297", "13133"],
        ["TP Hồ Chí Minh", "3300", None, "1100", None, None, "2200", None, None, "7426", None],
        ["Ninh Thuận", "1362", None, "200", "30", "480", "620", "32", None, "6900", "500"],
        ["Bình Phước", "144", None, "132", "12", None, None, None, None, "701", "145"],
        ["Tây Ninh", "32615", None, "16167", "952", "7748", "7748", None, None, "10692", "4990"],
        ["Bình Dương", "700", None, "429", None, None, "271", None, None, "2024", "64"],
        ["Đồng Nai", "8872", "321", "4156", None, "580", "3815", None, None, "9110", "3759"],
        ["Bình Thuận", "7668", "242", "3487", "3407", "35", "485", "12", None, "2216", "3178"],
        ["Bà Rịa-V.Tàu", "674", None, "426", None, "103", "145", None, None, "2228", "497"],
        ["ĐBS Cửu Long", "79733", "7640", "13623", "8526", "193", "49420", None, "450", "109121", "3841"],
        ["Long An", "22806", None, "6966", "1459", None, "14381", None, None, "6510", None],
        ["Đồng Tháp", "8743", "5415", "250", "2931", "16", "131", None, None, "7824", "438"],
        ["An Giang", "422", "183", "215", None, "6", "18", None, None, "8433", "1090"],
        ["Vĩnh Long", "1541", "1115", "28", "331", None, "67", None, None, "12759", "365"],
        ["Bến Tre", "7360", None, "391", None, None, "6969", None, None, "2082", "128"],
        ["Cần Thơ", "8124", "721", "3587", "3805", "11", None, None, None, "5480", "201"],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "6068", None],
        ["Trà Vinh", "4230", None, "2088", None, None, "1692", None, "450", "6325", "426"],
        ["Sóc Trăng", "13054", "206", "98", None, "160", "12590", None, None, "22940", "1193"],
        ["Bạc Liêu", None, None, None, None, None, None, None, None, "5500", None],
    ]
    for r in raw:
        loc = r[0]; geo = "Regional" if loc in regional else "Provincial"
        for i in range(1, 11):
            val = normalize_number(r[i])
            if val: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Cultivation", "commodity": itms[i-1][0], "sub_item": itms[i-1][1]}, "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl6a_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL6a", "source_file": "2009_06_PHULUC_T06_2009_PL5.md"}
    records = []
    # Header: [Loc, PigTotal, Nái, Thịt, Đực, SlConXChuong, SLThitHoi, GiaCamTotal, Gà, GàCN, GàĐẻ, Vịt, Ngan, SLThitHoiGC, Trứng]
    # Indices: 0:Loc, 1:PigTotal, 2:Sow, 3:MeatPig, 6:PigMeatProd(T), 7:PoultryTotal(1000), 8:Chicken, 13:PoultryMeatProd(T), 14:Eggs(1000)
    data = [
        ["Cả nước", "26497537", "4088194", "22311607", "1708909", "256615", "185288", "64502", "282804", "3062237"],
        ["ĐB Sông Hồng", "7169754", "1180258", "5977381", "537713", "66323", "48726", "13723", "90535", "962641"],
        ["Hà Nội", "1600118", "206583", "1390709", "154783", "14872", "10963", "3228", "24923", "266666"],
        ["Vĩnh Phúc", "526043", "86548", "438131", "32289", "6273", "5302", "797", "10579", "81906"],
        ["Bắc Ninh", "443226", "70143", "372548", "34193", "3952", "3084", "868", "5708", "57783"],
        ["Quảng Ninh", "330833", "33851", "295368", "21631", "1951", "1453", "498", "2474", "18228"],
        ["Hải Dương", "624799", "115553", "508539", "39274", "6909", "5535", "1374", "7556", "60250"],
        ["Hải Phòng", "497881", "83100", "414405", "35656", "4965", "3916", "733", "9126", "87056"],
        ["Hưng Yên", "575431", "59390", "515248", "45706", "5739", "3650", "1401", "9937", "80560"],
        ["Hà Nam", "448760", "70653", "377300", "27380", "4740", "2495", "1561", "2322", "79550"],
        ["Nam Định", "699995", "142283", "556401", "54999", "5486", "4086", "1400", "5929", "88933"],
        ["Thái Bình", "1045000", "217027", "827141", "66453", "8064", "5892", "1218", "7645", "90446"],
        ["Ninh Bình", "377668", "95127", "281591", "25349", "3372", "2350", "645", "4336", "51263"],
        ["Miền núi và Trung du", "5915238", "867747", "4997341", "242980", "56459", "47427", "7317", "44865", "288599"],
        ["Hà Giang", "380201", "62623", "303201", "7849", "2817", "2301", "366", "2193", "12289"],
        ["Cao Bằng", "308210", "37736", "270175", "12509", "1854", "1517", "337", "1961", "13603"],
        ["Bắc Cạn", "138415", "15369", "122457", "6114", "1242", "1007", "172", "919", "4999"],
        ["Tuyên Quang", "451121", "47380", "400106", "16097", "4573", "3810", "763", "3369", "49858"],
        ["Lào Cai", "377564", "63345", "307552", "10589", "2662", "2283", "245", "1520", "13675"],
        ["Yên Bái", "397094", "49845", "344175", "9769", "2830", "2392", "325", "1190", "27351"],
        ["Thái Nguyên", "547686", "95897", "451400", "33341", "5550", "4575", "975", "4899", "40021"],
        ["Lạng Sơn", "335005", "21877", "312799", "21646", "3327", "2743", "527", "3092", "12154"],
        ["Bắc Giang", "1029626", "172639", "856028", "61059", "12599", "10970", "1208", "8874", "11740"],
        ["Phú Thọ", "626274", "76091", "549284", "32504", "8905", "7434", "897", "8883", "48579"],
        ["Điện Biên", "261515", "65051", "193569", "4373", "1828", "1366", "462", "689", "9880"],
        ["Lai Châu", "189262", "41029", "142086", "2251", "905", "674", "231", "505", "3309"],
        ["Sơn La", "449568", "87424", "358364", "9227", "4310", "3689", "418", "2846", "19599"],
        ["Hoà Bình", "423697", "31441", "386145", "15652", "3057", "2666", "391", "3925", "21542"],
        ["Bắc Trung Bộ & DHMT", "5802565", "960108", "4833374", "321049", "57142", "41343", "15197", "49912", "510248"],
        ["Thanh Hoá", "992706", "167328", "824844", "70556", "13783", "9893", "3890", "12185", "18095"],
        ["Nghệ An", "1192087", "262986", "928026", "68379", "13904", "11524", "2112", "12197", "114406"],
        ["Hà Tĩnh", "373528", "37460", "335680", "21385", "4883", "3824", "922", "2959", "76715"],
        ["Quảng Bình", "376168", "43224", "332375", "18047", "2269", "1674", "595", "2692", "24767"],
        ["Quảng Trị", "231969", "51626", "180051", "10543", "1404", "1029", "375", "1105", "3477"],
        ["Thừa Thiên Huế", "238972", "26982", "211802", "10310", "1760", "1134", "626", "1507", "12275"],
        ["TP Đà Nẵng", "67788", "6347", "61257", "3495", "459", "375", "84", "402", "2510"],
        ["Quảng Nam", "589072", "74985", "513346", "22271", "3362", "2677", "630", "2408", "12147"],
        ["Quảng Ngãi", "512456", "93964", "417871", "16825", "2954", "2149", "709", "1978", "28568"],
        ["Bình Định", "664817", "130599", "531765", "38448", "4827", "2966", "1861", "3950", "118521"],
    ]
    regional_names = ["Cả nước", "ĐB Sông Hồng", "Miền núi và Trung du", "Bắc Trung Bộ & DHMT"]
    for r in data:
        loc = r[0]; geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional_names else "Provincial")
        # Pigs
        v = normalize_number(r[1])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 4, "period_type": "Point_In_Time", "report_date": "2009-04-01"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Livestock", "commodity": "Lợn", "sub_item": "Tổng số"}, "metric_context": {"attribute": "Head_Count", "value": v, "unit": "head", "data_type": "Actual"}, "metadata": metadata})
        v = normalize_number(r[6])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 4, "period_type": "Point_In_Time", "report_date": "2009-04-01"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Livestock", "commodity": "Lợn", "sub_item": "Thịt hơi xuất chuồng"}, "metric_context": {"attribute": "Production", "value": v, "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
        # Poultry (r[7] is total in 1000 head, r[9] is eggs in 1000 pcs)
        v = normalize_number(r[7])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 4, "period_type": "Point_In_Time", "report_date": "2009-04-01"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Livestock", "commodity": "Gia cầm", "sub_item": "Tổng số"}, "metric_context": {"attribute": "Head_Count", "value": v * 1000, "unit": "head", "data_type": "Actual"}, "metadata": metadata})
        v = normalize_number(r[9])
        if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 4, "period_type": "Point_In_Time", "report_date": "2009-04-01"}, "geo_context": {"geo_level": geo, "location_name": loc}, "item_context": {"sector": "Livestock", "commodity": "Gia cầm", "sub_item": "Sản lượng trứng"}, "metric_context": {"attribute": "Production", "value": v, "unit": "1000_eggs", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl4_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL4.json"))
    save_json(parse_pl5_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL5.json"))
    save_json(parse_pl6a_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL6a.json"))
    print("FINISHED Batch 2 Exhaustive (PL4, PL5, PL6a Census).")
