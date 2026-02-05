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
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|":
        return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl4_08():
    metadata = {
        "year": 2009,
        "month": 8,
        "appendix_number": "PL4",
        "source_file": "2009_08_PHULUC_T08_2009_PL4.md"
    }
    records = []
    
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    # Rows: Loc, Lúa HT Gieo cấy, Lúa HT Thu hoạch, Lúa Mùa Gieo cấy, Màu LT Total, Ngô, K.Lang, Sắn, Có củ khác
    pl4_data = [
        ["Miền Nam", "2034242", "1223786", "293654", "609263", "276672", "22270", "295946", "14375"],
        ["D.H Nam Trg Bộ", "118636", "29708", "70869", "85360", "23173", "4723", "56823", "641"],
        ["TP Đà Nẵng", "3755", None, "4003", "1187", "664", "437", "86", None],
        ["Quảng Nam", None, None, "41940", "22200", "6500", "3700", "12000", None],
        ["Quảng Ngãi", "31641", "4500", None, "18915", "3206", "200", "15509", None],
        ["Bình Định", "41550", "24208", "23131", "15507", "4954", None, "10553", None],
        ["Phú Yên", "23920", "1000", "1795", "18913", "4729", "226", "13675", "283"],
        ["Khánh Hoà", "17770", None, None, "8638", "3120", "160", "5000", "358"],
        ["Tây Nguyên", "6175", "6175", "143653", "285436", "156992", "9179", "119265", "0"],
        ["Kon Tum", None, None, "15414", "42612", "7388", "152", "35072", None],
        ["Gia Lai", None, None, "32930", "91684", "40820", "857", "50007", None],
        ["Đắc Lắc", None, None, "43148", "99601", "74315", "4900", "20386", None],
        ["Đắc Nông", None, None, "35120", "33975", "20575", "2100", "11300", None],
        ["Lâm Đồng", "6175", "6175", "17041", "17564", "13894", "1170", "2500", None],
        ["Đông Nam Bộ", "153171", "70904", "19305", "193476", "68794", "1555", "118259", "4868"],
        ["TP Hồ Chí Minh", "6967", "6000", "500", "1067", "1067", None, None, None],
        ["Ninh Thuận", "12400", "900", None, "6407", "6407", None, None, None],
        ["Bình Phước", "13700", None, None, "30715", "6150", "867", "23600", "98"],
        ["Tây Ninh", "49094", "33174", "17100", "48119", "8000", None, "40119", None],
        ["Bình Dương", "1530", "1530", None, "6724", "130", "1", "2316", "4277"],
        ["Đồng Nai", "24574", None, "1705", "40590", "25337", "135", "15000", "118"],
        ["Bình Thuận", "37400", "26000", None, "41259", "11171", "372", "29341", "375"],
        ["Bà Rịa-V.Tàu", "7506", "3300", None, "18595", "10532", "180", "7883", None],
        ["ĐBS Cửu Long", "1756260", "1116999", "59827", "44991", "27713", "6813", "1599", "8866"],
        ["Long An", "201733", "149424", "1610", "3762", "3762", None, None, None],
        ["Đồng Tháp", "195730", "193638", None, "6226", "4175", "1194", None, "857"],
        ["An Giang", "230884", "222240", None, "6299", "6179", "120", None, None],
        ["Tiền Giang", "117084", "45500", None, "6156", "4146", "238", "153", "1619"],
        ["Vĩnh Long", "63003", "63003", None, "8886", "911", "2077", "156", "5742"],
        ["Bến Tre", "24225", "1626", "1010", "826", "435", "175", "88", "128"],
        ["Kiên Giang", "274836", "141582", None, "700", None, "700", None, None],
        ["Cần Thơ", "120976", "83840", None, "629", "629", None, None, None],
        ["Hậu Giang", "186453", "76862", None, "1548", "1028", None, None, "520"],
        ["Trà Vinh", "82431", "37487", "22480", "6467", "4277", "1388", "802", None],
        ["Sóc Trăng", "167000", "81292", "26941", "3492", "2171", "921", "400", None],
        ["Bạc Liêu", "55777", "16041", "4369", "0", None, None, None, None],
        ["Cà Mau", "36128", "4464", "3417", "0", None, None, None, None],
    ]

    for row in pl4_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        
        # 1. Lúa Hè Thu (Gieo cấy)
        v_gc = normalize_number(row[1])
        if v_gc is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": v_gc / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # 2. Lúa Hè Thu (Thu hoạch)
        v_th = normalize_number(row[2])
        if v_th is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Harvested", "value": v_th / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # 3. Lúa Mùa (Gieo cấy)
        v_m = normalize_number(row[3])
        if v_m is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"},
                "metric_context": {"attribute": "Area_Planted", "value": v_m / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })

        # 4. Màu lương thực items - Col 4, 5, 6, 7, 8
        items = [
            ("Màu lương thực", "Tổng số"),
            ("Ngô", None),
            ("Khoai lang", None),
            ("Sắn", None),
            ("Màu lương thực khác", None)
        ]
        for i in range(4, 9):
            v_alt = normalize_number(row[i])
            if v_alt is not None:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative", "report_date": "2009-08-15"},
                    "geo_context": {"geo_level": geo, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-4][0], "sub_item": items[i-1 if i > 4 else 0][1] if i == 4 else items[i-4][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": v_alt / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })

    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/08"
    save_json(parse_pl4_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL4.json"))
    print("Successfully parsed PL4 for August 2009.")
