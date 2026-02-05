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

def parse_pl8b_07():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL8b", "source_file": "2009_07_PHULUC_T07_2009_PL8b.md"}
    records = []
    # Exhaustive Import Market data (6 months 2009)
    # Item: [[Country, Volume, Value], ...]
    nk_data = {
        "Bông các loại": [["Hoa Kỳ", 66475, 84244.97], ["Braxin", 4868, 6506.5], ["Ấn Độ", 3244, 4148], ["Inđônêxia", 2476, 2457], ["Trung Quốc", 1196, 1685], ["Thuỵ Sỹ", 979, 1229], ["Đài Loan", 595, 668.5], ["Hàn Quốc", 310, 473.9]],
        "Cao su": [["Thái Lan", 32454, 41654], ["Hàn Quốc", 21091, 27942], ["Campuchia", 17726, 24944], ["Đài Loan", 8842, 13475], ["Nhật Bản", 5942, 12829], ["Inđônêxia", 9584, 12298], ["Trung Quốc", 3503, 6197], ["Nga", 2850, 5888], ["Malaixia", 4320, 4754], ["Pháp", 1278, 3217]],
        "Dầu mỡ động thực vật": [[k, None, v] for k, v in [["Malaixia", 104345], ["Inđônêxia", 74799], ["Thái Lan", 19829], ["Achentina", 19478], ["Chile", 2770], ["Hoa kỳ", 1462], ["Hàn Quốc", 1329], ["Xingapo", 1247], ["Ôxtrâylia", 777], ["Trung Quốc", 510]]],
        "Lúa mì": [["Ôxtrâylia", 559236, 144806], ["Ucraina", 72301, 11839], ["Hoa kỳ", 8776, 2526], ["Nga", 1563, 392], ["Trung Quốc", 198, 97]],
        "Gỗ & sản phẩm gỗ": [[k, None, v] for k, v in [["Malaixia", 56171], ["Trung Quốc", 45434], ["Lào", 44853], ["Hoa kỳ", 39506], ["Niuzilân", 22675], ["Thái Lan", 20143], ["Campuchia", 19201], ["Braxin", 11747], ["Đài Loan", 6954], ["Ôxtrâylia", 6569]]],
        "Hàng rau quả": [[k, None, v] for k, v in [["Braxin", 1193], ["Chile", 1320], ["Hoa kỳ", 7966], ["Inđônêxia", 130], ["Malaixia", 1160], ["Ôxtrâylia", 9319], ["Thái Lan", 22942], ["Trung Quốc", 61960]]],
        "Hàng thủy sản": [[k, None, v] for k, v in [["Đài Loan", 14802], ["Nhật Bản", 10823], ["Inđônêxia", 9769], ["Hàn Quốc", 8208], ["Nauy", 7677], ["Hoa kỳ", 7203], ["Thái Lan", 6962], ["Trung Quốc", 6507], ["Ấn Độ", 4153], ["Chile", 3716]]],
        "Phân bón các loại": [["Trung Quốc", 724862, 238215], ["Nga", 269549, 77040], ["Philippin", 189860, 76075], ["Ucraina", 202277, 58561], ["Hoa kỳ", 101913, 41365], ["Hàn Quốc", 147121, 34368], ["Canađa", 44029, 30428], ["Đài Loan", 76625, 12610], ["Ấn Độ", 23701, 10257], ["Nhật Bản", 66133, 9372]],
        "Sữa và sản phẩm sữa": [[k, None, v] for k, v in [["Niuzilân", 56489], ["Hà Lan", 33485], ["Đan Mạch", 28406], ["Hoa kỳ", 19433], ["Thái Lan", 14383], ["Malaixia", 13403], ["Ôxtrâylia", 9620], ["Ba lan", 6249], ["Tây Ban Nha", 5696], ["Pháp", 5248]]],
    }
    for comm, markets in nk_data.items():
        for m in markets:
            country, l, v = m
            if l: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": country}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Import_Volume", "value": float(l), "unit": "ton", "data_type": "Actual"}, "metadata": metadata})
            if v: records.append({"record_id": generate_id(), "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"}, "geo_context": {"geo_level": "Provincial", "location_name": country}, "item_context": {"sector": "Trade", "commodity": comm}, "metric_context": {"attribute": "Import_Value", "value": float(v), "unit": "million_USD", "data_type": "Actual"}, "metadata": metadata})
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/07"
    save_json(parse_pl8b_07(), os.path.join(out_dir, "2009_07_PHULUC_T07_2009_PL8b.json"))
    print("Exhaustive Batch 5: PL8b processed.")
