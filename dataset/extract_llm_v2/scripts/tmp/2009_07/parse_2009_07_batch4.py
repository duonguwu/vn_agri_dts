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

def parse_pl8_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL8", "source_file": "2009_07_PHULUC_T07_2009_PL8.md"}
    records = []
    # Exhaustive list for Trade Summary
    # Item, T7 Lượng, T7 Giá trị, 7T Lượng, 7T Giá trị
    xk_rows = [
        ["Cà phê", "80", "115", "812", "1204"], ["Cao su", "65", "95", "316", "453"], ["Gạo", "640", "260", "4372", "2010"],
        ["Chè", "12", "14", "64", "78"], ["Hạt điều", "17", "79", "92", "411"], ["Hạt tiêu", "15", "37", "83", "195"],
        ["Hàng rau quả", None, "45", None, "255"], ["Sắn và SP từ sắn", "260", "45", None, "411"],
        ["Tổng kim ngạch XK", None, "1400", None, "9081"], ["Nông sản chính", None, "690", None, "5015"],
        ["Thuỷ sản", None, "400", None, "2162"], ["Lâm sản chính", None, "205", None, "1430"],
        ["Quế", "10", "10", "12", "12"], ["Gỗ & sản phẩm gỗ", None, "190", None, "1320"], ["SP mây, tre, cói, thảm", None, "13", None, "98"],
    ]
    # Import list
    nk_rows = [
        ["Tổng kim ngạch NK", None, "1000", None, "5676"], ["Các mặt hàng NK chính", None, "669", None, "3748"],
        ["Phân bón các loại", "300", "120", "2531", "846"], ["Ure", "66", "19", "762", "230"], ["SA", "33", "5", "650", "94"],
        ["DAP", "107", "38", "621", "241"], ["NPK", "14", "6", "189", "79"], ["Phân bón khác", "80", "52", "310", "201"],
        ["Thuốc trừ sâu & nguyên liệu", None, "44", None, "274"], ["Lúa mỳ", "165", "40", "832", "206"],
        ["Thức ăn gia súc và NL", None, "220", None, "1043"], ["Dầu mỡ động, thực vật", None, "60", None, "292"],
        ["Cao su", "21", "26", "141", "191"], ["Bông các loại", "26", "32", "136", "169"], ["Sữa & sản phẩm sữa", None, "40", None, "269"],
        ["Gỗ & sản phẩm gỗ", None, "85", None, "443"], ["Muối", "2", None, "15", None], ["Hàng rau quả", None, "25", None, "119"],
    ]
    for rows, sector in [(xk_rows, "Trade"), (nk_rows, "Trade")]:
        attr_l = "Export_Volume" if sector == "Trade" and rows == xk_rows else "Import_Volume"
        attr_v = "Export_Value" if sector == "Trade" and rows == xk_rows else "Import_Value"
        for r in rows:
             item = r[0]
             # T7 Monthly
             l7 = normalize_number(r[1]); v7 = normalize_number(r[2])
             if l7: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_l, "value": l7, "unit": "1000_ton", "data_type": "Actual"}, "metadata": metadata})
             if v7: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_v, "value": v7, "unit": "million_USD", "data_type": "Actual"}, "metadata": metadata})
             # 7T Cumulative
             l7c = normalize_number(r[3]); v7c = normalize_number(r[4])
             if l7c: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_l, "value": l7c, "unit": "1000_ton", "data_type": "Actual"}, "metadata": metadata})
             if v7c: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_v, "value": v7c, "unit": "million_USD", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl8a_07():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL8a", "source_file": "2009_07_PHULUC_T07_2009_PL8a.md"}
    records = []
    # Exhaustive market data for 6 months 2009
    comm_data = {
        "Cà phê": [["BỈ", 111043, 160860], ["ĐỨC", 79072, 118346], ["HOA KỲ", 77932, 118171], ["ITALIA", 68677, 102981], ["TÂY BAN NHA", 44975, 66911], ["NHẬT BẢN", 36149, 58237], ["HÀ LAN", 27725, 39893], ["PHÁP", 19524, 28951], ["HÀN QUỐC", 18411, 27791], ["ANH", 16610, 24845]],
        "Cao su": [["TRUNG QUỐC", 173124, 245167], ["HÀN QUỐC", 12501, 16328], ["MALAIXIA", 11076, 15389], ["ĐÀI LOAN", 7809, 11832], ["ĐỨC", 6594, 10882], ["HOA KỲ", 5142, 7222], ["NHẬT BẢN", 3961, 6215], ["NGA", 3465, 5461], ["THỔ NHĨ KỲ", 3507, 5202], ["ITALIA", 2126, 3306]],
        "Chè": [["PAKISTAN", 13025, 18136], ["NGA", 8750, 10393], ["ĐÀI LOAN", 8141, 9798], ["TRUNG QUỐC", 3258, 3486], ["ẤN ĐỘ", 2745, 2856], ["HOA KỲ", 2097, 1915], ["INĐÔNÊXIA", 2044, 1581], ["ĐỨC", 873, 1107], ["BALAN", 562, 627], ["PHILIPPIN", 132, 410]],
        "Gạo": [["PHILIPPIN", 1564504, 849030], ["MALAIXIA", 356422, 156185], ["CU BA", 271175, 114785], ["IRẮC", 168000, 67540], ["XINH GA PO", 158143, 65941], ["ĐÀI LOAN", 87466, 35579], ["NGA", 44674, 19332], ["NAM PHI", 30948, 13435], ["UCRAINA", 23716, 10089], ["HỒNG KÔNG", 19567, 8260]],
        "Gỗ & sản phẩm gỗ": [[k, None, v] for k, v in [["HOA KỲ", 465165], ["NHẬT BẢN", 172956], ["ANH", 79800], ["TRUNG QUỐC", 57547], ["ĐỨC", 41997], ["HÀN QUỐC", 39802], ["HÀ LAN", 33548], ["PHÁP", 31356], ["ÔXTRÂYLIA", 25192], ["CANAĐA", 18891]]],
        "Hàng rau quả": [[k, None, v] for k, v in [["TRUNG QUỐC", 20355], ["NGA", 18793], ["NHẬT BẢN", 15229], ["ĐÀI LOAN", 8320], ["HÀ LAN", 7738], ["HOA KỲ", 7177], ["INĐÔNÊXIA", 6174], ["XINH GA PO", 4646], ["THÁI LAN", 4342], ["HÀN QUỐC", 4303]]],
        "Hàng thủy sản": [["NHẬT BẢN", 45992, 303482], ["HOA KỲ", 51625, 292847], ["HÀN QUỐC", 43368, 127700], ["ĐỨC", 27991, 92335], ["TÂY BAN NHA", 31173, 77777], ["ITALIA", 18253, 50486], ["ÔXTRÂYLIA", 10217, 48841], ["HÀ LAN", 14545, 47012], ["UCRAINA", 26530, 46166], ["TRUNG QUỐC", 11722, 44603]],
        "Hạt điều": [["HOA KỲ", 22522, 98962], ["TRUNG QUỐC", 16472, 69467], ["HÀ LAN", 10266, 51651], ["ÔXTRÂYLIA", 4409, 20170], ["ANH", 3137, 14563], ["NGA", 1414, 6484], ["CANAĐA", 1385, 6275], ["ĐỨC", 1283, 6132], ["THÁI LAN", 989, 4355], ["ARẬP THỐNG", 999, 3828]],
        "Hạt tiêu": [["HOA KỲ", 6436, 18383], ["ĐỨC", 5872, 14317], ["ARẬP THỐNG", 5353, 10656], ["HÀ LAN", 4002, 10107], ["AI CẬP", 4299, 8608], ["PAKISTAN", 3877, 7669], ["ẤN ĐỘ", 3412, 7481], ["TÂY BAN NHA", 2799, 6528], ["XINH GA PO", 2871, 5536], ["NGA", 2461, 4873]],
        "Sản phẩm mây, tre, cói và th": [[k, None, v] for k, v in [["ĐỨC", 13418], ["NHẬT BẢN", 12111], ["HOA KỲ", 12093], ["ITALIA", 4309], ["ĐÀI LOAN", 4079], ["TÂY BAN NHA", 3616], ["PHÁP", 3408], ["ANH", 2654], ["HÀ LAN", 2481]]]
    }
    for comm, markets in comm_data.items():
        for m in markets:
            country, l, v = m
            if l: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": country}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Export_Volume", "value": float(l), "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
            if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": country}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Export_Value", "value": float(v), "unit": "million_USD", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl9_07():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL9", "source_file": "2009_07_PHULUC_T07_2009_PL9.md"}
    records = []
    pl9_rows = [
        ["I", "Vốn thực hiện đầu tư", "2611500", "1373850", "164080", "1537930"],
        ["1", "Đầu tư Thuỷ lợi", "1483500", "962313", "125000", "1087313"],
        ["2", "Đầu tư Nông nghiệp", "493000", "245010", "24500", "269510"],
        ["3", "Đầu tư Lâm nghiệp", "230000", "60600", "6180", "66780"],
        ["4", "Đầu tư Thuỷ sản", "24000", "13200", "1700", "14900"],
        ["5", "Khoa học - Công nghệ", "230000", "34200", "3000", "37200"],
        ["6", "Giáo dục - Đào tạo", "90000", "33177", "2500", "35677"],
        ["7", "Các ngành khác", "61000", "25350", "1200", "26550"],
        ["II", "Chương trình mục tiêu", "40263", "7500", "1000", "8500"],
        ["III", "Vốn ĐT theo mục tiêu cụ thể", "208000", "47244", "5000", "52244"],
        ["Preparation", "Vốn chuẩn bị đầu tư", "30000", "12000", "1500", "13500"],
        ["B", "Vốn ứng trước dự án cấp bách", "1000000", "261396", "47360", "308756"],
        ["C", "Vốn TPCP quyết định 171", "3250000", "1265401", "170000", "1435401"],
        ["D", "Các dự án cấp bách bổ sung", "200000", "38833", "5400", "44233"],
        ["E", "Các dự án thuỷ lợi ĐBS Hồng", "400000", "23508", "6800", "30308"],
    ]
    for row in pl9_rows:
        item = row[1]
        v_kh = normalize_number(row[2]); v_t7 = normalize_number(row[4]); v_7t = normalize_number(row[5])
        if v_kh: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 12, "period_type": "Annual"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Investment", "commodity": item}, "metric_context": {"attribute": "Investment_Amount", "value": v_kh, "unit": "million_VND", "data_type": "Plan"}, "metadata": metadata})
        if v_t7: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Investment", "commodity": item}, "metric_context": {"attribute": "Investment_Amount", "value": v_t7, "unit": "million_VND", "data_type": "Actual"}, "metadata": metadata})
        if v_7t: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Investment", "commodity": item}, "metric_context": {"attribute": "Investment_Amount", "value": v_7t, "unit": "million_VND", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/07"
    save_json(parse_pl8_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL8.json"))
    save_json(parse_pl8a_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL8a.json"))
    save_json(parse_pl9_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL9.json"))
    print("Exhaustive Batch 4: PL8, 8a, 9 processed.")
