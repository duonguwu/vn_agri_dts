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
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl8_08():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL8", "source_file": "2009_08_PHULUC_T08_2009_PL8.md"}
    records = []
    xk_rows = [
        ["Tổng kim ngạch XK", None, "1350", None, "10219"], ["Nông sản chính", None, "630", None, "5585"],
        ["Cà phê", "55", "78", "843", "1247"], ["Cao su", "83", "122", "417", "602"], ["Gạo", "500", "205", "4717", "2153"],
        ["Chè", "16", "23", "84", "109"], ["Hạt điều", "20", "100", "115", "532"], ["Hạt tiêu", "13", "34", "95", "228"],
        ["Hàng rau quả", None, "40", None, "285"], ["Sắn và SP từ sắn", "142", "28", None, "429"],
        ["Thuỷ sản", None, "450", None, "2647"], ["Lâm sản chính", None, "250", None, "1705"],
        ["Quế", "12", "12", "14", "14"], ["Gỗ & sản phẩm gỗ", None, "232", None, "1576"], ["SP mây, tre, cói, thảm", None, "16", None, "115"],
        ["Các mặt hàng nông lâm sản khác", None, "20", None, "282"],
    ]
    nk_rows = [
        ["Tổng kim ngạch NK", None, "1000", None, "6639"], ["Các mặt hàng NK chính", None, "700", None, "4459"],
        ["Phân bón các loại", "250", "93", "2728", "904"], ["Ure", "70", "20", "838", "251"], ["SA", "55", "7", "717", "102"],
        ["DAP", "70", "25", "650", "252"], ["NPK", "10", "4", "195", "81"], ["Phân bón khác", "45", "37", "326", "217"],
        ["Thuốc trừ sâu & nguyên liệu", None, "44", None, "318"], ["Lúa mỳ", "110", "30", "881", "223"],
        ["Thức ăn gia súc và NL", None, "247", None, "1314"], ["Dầu mỡ động, thực vật", None, "60", None, "349"],
        ["Cao su", "28", "37", "178", "238"], ["Bông các loại", "41", "50", "190", "233"], ["Sữa & sản phẩm sữa", None, "42", None, "311"],
        ["Gỗ & sản phẩm gỗ", None, "93", None, "547"], ["Muối", "4", None, "21", None],
    ]
    for rows, sector in [(xk_rows, "Trade"), (nk_rows, "Trade")]:
        attr_l = "Export_Volume" if rows == xk_rows else "Import_Volume"
        attr_v = "Export_Value" if rows == xk_rows else "Import_Value"
        for r in rows:
            item = r[0]
            l8 = normalize_number(r[1]); v8 = normalize_number(r[2]); l8c = normalize_number(r[3]); v8c = normalize_number(r[4])
            if l8: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_l, "value": l8, "unit": "1000_ton", "data_type": "Actual"}, "metadata": metadata})
            if v8: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_v, "value": v8, "unit": "million_USD", "data_type": "Actual"}, "metadata": metadata})
            if l8c: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_l, "value": l8c, "unit": "1000_ton", "data_type": "Actual"}, "metadata": metadata})
            if v8c: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": sector, "commodity": item}, "metric_context": {"attribute": attr_v, "value": v8c, "unit": "million_USD", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl8a_08():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL8a", "source_file": "2009_08_PHULUC_T08_2009_PL8a.md"}
    records = []
    # Title says 7 months 2009.
    comm_data = {
        "Cà phê": [["BỈ", 114595, 165967], ["ĐỨC", 85284, 127236], ["HOA KỲ", 84056, 126993], ["ITALIA", 73584, 110066], ["TÂY BAN NHA", 49575, 73513], ["NHẬT BẢN", 42143, 67229], ["HÀ LAN", 29215, 41959], ["PHÁP", 20342, 30063], ["HÀN QUỐC", 19482, 29313], ["ANH", 17495, 26158]],
        "Cao su": [["TRUNG QUỐC", 229125, 328057], ["MALAIXIA", 14839, 20670], ["HÀN QUỐC", 15657, 20602], ["ĐÀI LOAN", 11110, 17180], ["ĐỨC", 8499, 13643], ["NGA", 5820, 9384], ["HOA KỲ", 6842, 9248], ["NHẬT BẢN", 4562, 7240], ["THỔ NHĨ KỲ", 4709, 7003], ["ẤN ĐỘ", 3759, 5370]],
        "Chè": [["PAKISTAN", 16713, 23712], ["NGA", 10845, 12855], ["ĐÀI LOAN", 10718, 12633], ["TRUNG QUỐC", 4222, 4410], ["ẤN ĐỘ", 3820, 4153], ["INĐÔNÊXIA", 2744, 2418], ["HOA KỲ", 2565, 2380], ["ĐỨC", 1168, 1477], ["BALAN", 806, 895], ["PHILIPPIN", 197, 574]],
        "Gạo": [["PHILIPPIN", 1573076, 852315], ["MALAIXIA", 410146, 180000], ["CU BA", 352325, 149761], ["XINH GA PO", 190368, 78825], ["IRẮC", 168000, 67540], ["ĐÀI LOAN", 104229, 42413], ["NGA", 52999, 22871], ["NAM PHI", 31273, 13559], ["UCRAINA", 27316, 11642], ["HỒNG KÔNG", 24651, 10436]],
        "Gỗ & sản phẩm gỗ": [[k, None, v] for k, v in [["HOA KỲ", 566418], ["NHẬT BẢN", 205251], ["ANH", 93295], ["TRUNG QUỐC", 75558], ["HÀN QUỐC", 47224], ["ĐỨC", 46023], ["HÀ LAN", 35638], ["PHÁP", 34371], ["ÔXTRÂYLIA", 32807], ["CANAĐA", 23583]]],
        "Hàng hải sản": [["NHẬT BẢN", 57215, 379800], ["HOA KỲ", 64860, 371397], ["HÀN QUỐC", 53106, 158014], ["ĐỨC", 33867, 112581], ["TÂY BAN NHA", 38823, 95811], ["ITALIA", 22380, 62393], ["HÀ LAN", 18805, 61657], ["ÔXTRÂYLIA", 12551, 61027], ["BỈ", 13820, 54253], ["Trung Quèc", 13830, 52075]],
        "Hạt điều": [["HOA KỲ", 30260, 137279], ["TRUNG QUỐC", 19141, 80830], ["HÀ LAN", 13320, 67308], ["ÔXTRÂYLIA", 5911, 27613], ["ANH", 4104, 19607], ["CANAĐA", 2383, 11409], ["NGA", 2034, 9430], ["ĐỨC", 1554, 7470], ["THÁI LAN", 1246, 5463], ["ARẬP THỐNG NHẤT", 1071, 4195]],
        "Hạt tiêu": [["HOA KỲ", 8117, 22660], ["ĐỨC", 7110, 17609], ["ARẬP THỐNG NHẤT", 6454, 13057], ["HÀ LAN", 4646, 11745], ["ẤN ĐỘ", 4351, 9727], ["AI CẬP", 4760, 9629], ["PAKISTAN", 4706, 9484], ["TÂY BAN NHA", 3168, 7523], ["XINH GA PO", 3600, 7056], ["NGA", 3028, 6140]],
        "Sản phẩm mây, tre, cói": [[k, None, v] for k, v in [["ĐỨC", 16057], ["HOA KỲ", 14338], ["NHẬT BẢN", 14278], ["ĐÀI LOAN", 4891], ["ITALIA", 4664], ["TÂY BAN NHA", 4392], ["PHÁP", 3933], ["ANH", 3092], ["HÀ LAN", 2952], ["BỈ", 2897]]],
        "Hàng rau quả": [[k, None, v] for k, v in [["TRUNG QUỐC", 24281], ["NGA", 21176], ["NHẬT BẢN", 17565], ["HÀ LAN", 10279], ["ĐÀI LOAN", 9963], ["HOA KỲ", 8894], ["INĐÔNÊXIA", 6433], ["HÀN QUỐC", 5701], ["XINH GA PO", 5595], ["THÁI LAN", 5004]]],
    }
    for comm, m_list in comm_data.items():
        for m in m_list:
            c, vol, val = m
            if vol: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": c}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Export_Volume", "value": float(vol), "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
            if val: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": c}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Export_Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl8b_08():
    metadata = {"year": 2009, "month": 7, "appendix_number": "PL8b", "source_file": "2009_08_PHULUC_T08_2009_PL8b.md"}
    records = []
    # Title says 7 months 2009
    comm_data = {
        "Bông các loại": [["HOA KỲ", 87079, 108981], ["ẤN ĐỘ", 9338, 12085], ["BRAXIN", 5938, 7851], ["INĐÔNÊXIA", 2506, 2482], ["TRUNG QUỐC", 1229, 1812], ["THỤY SỸ", 1219, 1519], ["ĐÀI LOAN", 624, 718], ["ITALIA", 947, 648], ["HÀN QUỐC", 373, 589], ["ANH", 97, 122]],
        "Cao su": [["THÁI LAN", 35937, 45713], ["HÀN QUỐC", 25570, 33963], ["CAMPUCHIA", 23068, 33015], ["ĐÀI LOAN", 10939, 16726], ["INĐÔNÊXIA", 12227, 16041], ["NHẬT BẢN", 7535, 15905], ["TRUNG QUỐC", 4416, 7478], ["NGA", 3592, 7267], ["MALAIXIA", 4867, 5133], ["HOA KỲ", 4734, 4276]],
        "Dầu mỡ động thực vật": [[k, None, v] for k, v in [["MALAIXIA", 126793], ["INĐÔNÊXIA", 90776], ["THÁI LAN", 21789], ["ACHENTINA", 19504], ["HOA KỲ", 14470], ["CHILÊ", 3902], ["XINH GA PO", 1576], ["HÀN QUỐC", 1528], ["ÔXTRÂYLIA", 1110], ["TRUNG QUỐC", 562]]],
        "Gỗ & sản phẩm gỗ": [[k, None, v] for k, v in [["MALAIXIA", 70396], ["LÀO", 59130], ["TRUNG QUỐC", 56305], ["HOA KỲ", 48810], ["NIUZILÂN", 28334], ["THÁI LAN", 24865], ["CAMPUCHIA", 22553], ["BRAXIN", 13862], ["ÔXTRÂYLIA", 8379], ["ĐÀI LOAN", 8135]]],
        "Lúa mì": [["ÔXTRÂYLIA", 646180, 167805], ["UCRAINA", 77758, 12868], ["HOA KỲ", 10084, 2876], ["NGA", 9652, 2202], ["CANAĐA", 2000, 722], ["TRUNG QUỐC", 198, 97]],
        "Phân bón các loại": [["TRUNG QUỐC", 885367, 286891], ["NGA", 284421, 82269], ["PHILIPPIN", 192960, 77326], ["UCRAINA", 202277, 58562], ["HOA KỲ", 102012, 42117], ["HÀN QUỐC", 153571, 35275], ["CANAĐA", 45229, 31221], ["ĐÀI LOAN", 83372, 13563], ["ẤN ĐỘ", 26600, 11299], ["NHẬT BẢN", 79044, 11051]],
        "Sữa & sản phẩm sữa": [[k, None, v] for k, v in [["NIUZILÂN", 67733], ["HÀ LAN", 43052], ["ĐAN MẠCH", 32364], ["HOA KỲ", 21677], ["THÁI LAN", 19094], ["MALAIXIA", 15157], ["ÔXTRÂYLIA", 10320], ["BALAN", 7824], ["TÂY BAN NHA", 6733], ["PHÁP", 5949]]],
        "Thức ăn gia súc & nguyên liệu": [[k, None, v] for k, v in [["ACHENTINA", 294179], ["ẤN ĐỘ", 285112], ["TRUNG QUỐC", 97908], ["HOA KỲ", 97639], ["INĐÔNÊXIA", 27052], ["THÁI LAN", 24902], ["ITALIA", 18428], ["ĐÀI LOAN", 15829], ["ARẬP THỐNG NHẤT", 12328], ["HÀN QUỐC", 11750]]],
        "Thuốc trừ sâu & nguyên liệu": [[k, None, v] for k, v in [["TRUNG QUỐC", 112302], ["ẤN ĐỘ", 27104], ["THỤY SỸ", 21364], ["ĐỨC", 19408], ["HÀN QUỐC", 14458], ["NHẬT BẢN", 12737], ["THÁI LAN", 12560], ["XINH GA PO", 8903], ["INĐÔNÊXIA", 8568], ["HOA KỲ", 6681]]],
    }
    for comm, m_list in comm_data.items():
        for m in m_list:
            c, vol, val = m
            if vol: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": c}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Import_Volume", "value": float(vol), "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
            if val: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 7, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": c}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Import_Value", "value": float(val), "unit": "1000_USD", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


def parse_pl9_08():
    metadata = {"year": 2009, "month": 8, "appendix_number": "PL9", "source_file": "2009_08_PHULUC_T08_2009_PL9.md"}
    records = []
    rows = [
        ["I", "Vốn thực hiện đầu tư", "2611500", "1761861", "167250", "1929111"],
        ["1", "Đầu tư Thuỷ lợi", "1483500", "1277909", "124500", "1402409"],
        ["2", "Đầu tư Nông nghiệp", "493000", "251931", "22100", "274031"],
        ["3", "Đầu tư Lâm nghiệp", "230000", "71486", "6300", "77786"],
        ["4", "Đầu tư Thuỷ sản", "24000", "16500", "1500", "18000"],
        ["5", "Khoa học - Công nghệ", "230000", "69643", "5000", "74643"],
        ["6", "Giáo dục - Đào tạo", "90000", "44042", "5350", "49392"],
        ["7", "Các ngành khác", "61000", "30350", "2500", "32850"],
        ["II", "Chương trình mục tiêu", "40263", "9000", "1500", "10500"],
        ["III", "Vốn đầu tư theo nhiệm vụ cụ thể", "208000", "80944", "7500", "88444"],
        ["IV", "Bổ sung dự trữ Quốc gia", "65000", "65000", None, "65000"],
        ["V", "Vốn chuẩn bị đầu tư", "30000", "13500", "2850", "16350"],
        ["B", "Vốn ứng trước cho dự án cấp bách", "1000000", "343269", "52480", "395749"],
        ["C", "Vốn TPCP quyết định 171", "3250000", "1621245", "165000", "1786245"],
        ["D", "Các dự án cấp bách bổ sung", "200000", "66905", "15400", "82305"],
        ["E", "Các dự án thuỷ lợi ĐBS Hồng", "400000", "52955", "12800", "65755"],
    ]
    for r in rows:
        item = r[1]
        v_kh = normalize_number(r[2]); v_p = normalize_number(r[4]); v_c = normalize_number(r[5])
        if v_kh: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 12, "period_type": "Annual"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Investment", "commodity": item}, "metric_context": {"attribute": "Investment_Amount", "value": v_kh, "unit": "million_VND", "data_type": "Plan"}, "metadata": metadata})
        if v_p: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Monthly"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Investment", "commodity": item}, "metric_context": {"attribute": "Investment_Amount", "value": v_p, "unit": "million_VND", "data_type": "Actual"}, "metadata": metadata})
        if v_c: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 8, "period_type": "Cumulative"}, "geo_context": {"geo_level": "National", "location_name": "Cả nước"}, "item_context": {"sector": "Investment", "commodity": item}, "metric_context": {"attribute": "Investment_Amount", "value": v_c, "unit": "million_VND", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/08"
    save_json(parse_pl8_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL8.json"))
    save_json(parse_pl8a_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL8a.json"))
    save_json(parse_pl8b_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL8b.json"))
    save_json(parse_pl9_08(), os.path.join(out_dir, "2009_08_PHULUC_T08_2009_PL9.json"))
    print("Batch 4: Trade & Investment for Aug 2009.")
