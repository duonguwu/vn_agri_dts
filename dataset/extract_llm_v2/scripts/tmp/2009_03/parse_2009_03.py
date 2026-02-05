import json
import uuid
from datetime import datetime
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if not s:
        return None
    # Remove markdown formatting, <br> tags, and thousands separators
    clean = s.replace("**", "").replace("_", "").replace("<br>", "").replace(",", "").replace("~~", "").strip()
    if clean == "" or clean == "-" or clean == '"':
        return None
    try:
        return float(clean)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl1():
    metadata = {
        "year": 2009,
        "month": 3,
        "appendix_number": "PL1",
        "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL1.md",
        "extraction_timestamp": datetime.now().isoformat(),
        "estimated_tokens": 0,
        "attempts": 1
    }
    
    records = []
    source_file = metadata["source_file"]
    appendix_number = metadata["appendix_number"]
    appendix_title = "TỔNG HỢP KẾT QUẢ SẢN XUẤT NÔNG NGHIỆP"
    
    # Mapping based on rows in PL1
    # 1. Gieo cấy lúa đông xuân cả nước
    # [Location, Unit, Prev_Year_Val, Curr_Year_Val, %_vs_Plan, %_vs_Prev]
    lúa_dx_rows = [
        ["Cả nước", "1000_ha", "2931.7", "2981.0", None, "101.7", "National"],
        ["Miền Bắc", "1000_ha", "1064.1", "1097.6", None, "103.2", "Regional"],
        ["Đồng bằng sông Hồng", "1000_ha", "536.0", "553.6", None, "103.3", "Regional"],
        ["Bắc Trung bộ", "1000_ha", "328.3", "334.2", None, "101.8", "Regional"],
        ["Miền Nam", "1000_ha", "1867.6", "1883.4", None, "100.8", "Regional"],
        ["Đồng bằng sông Cửu Long", "1000_ha", "1517.6", "1543.2", None, "101.7", "Regional"],
    ]
    
    for row in lúa_dx_rows:
        loc, unit, prev_val, curr_val, vs_plan, vs_prev, geo_level = row
        # Current Value record
        c_val = normalize_number(curr_val)
        if c_val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                "geo_context": {"geo_level": geo_level, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": c_val, "unit": unit, "data_type": "Actual"},
                "comparison_context": {"comparison_type": "YoY", "comparison_value": normalize_number(vs_prev)} if vs_prev else None,
                "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
            })
        # Previous Year record
        p_val = normalize_number(prev_val)
        if p_val:
             records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 3, "period_type": "Cumulative", "report_date": "2008-03-15"},
                "geo_context": {"geo_level": geo_level, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": p_val, "unit": unit, "data_type": "Actual"},
                "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
            })

    # 2. Thu hoạch lúa đông xuân miền Nam
    thu_hoach_rows = [
        ["Miền Nam", "1000_ha", "992.0", "796.2", "42.3", "80.3", "Regional"],
        ["Đồng bằng sông Cửu Long", "1000_ha", "957.8", "775.1", "50.2", "80.9", "Regional"],
    ]
    for row in thu_hoach_rows:
        loc, unit, prev_val, curr_val, vs_plan, vs_prev, geo_level = row
        c_val = normalize_number(curr_val)
        if c_val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                "geo_context": {"geo_level": geo_level, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Harvested", "value": c_val, "unit": unit, "data_type": "Actual"},
                "comparison_context": {"comparison_type": "YoY", "comparison_value": normalize_number(vs_prev)} if vs_prev else None,
                "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
            })

    # 3. Gieo cấy lúa hè thu ở ĐBSCL
    lúa_ht = ["Đồng bằng sông Cửu Long", "1000_ha", "112.6", "102.3", None, "90.9", "Regional"]
    c_val = normalize_number(lúa_ht[3])
    if c_val:
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "Regional", "location_name": lúa_ht[0]},
            "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
            "metric_context": {"attribute": "Area_Planted", "value": c_val, "unit": unit, "data_type": "Actual"},
            "comparison_context": {"comparison_type": "YoY", "comparison_value": normalize_number(lúa_ht[5])},
            "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
        })

    # 4. Gieo trồng màu
    mau_rows = [
        ["Gieo trồng màu", None, "583.0", "533.4", None, "91.5"],
        ["Ngô", None, "382.5", "342.3", None, "89.5"],
        ["Khoai lang", None, "92.6", "80.5", None, "86.9"],
        ["Sắn", None, "105.4", "108.1", None, "102.6"],
    ]
    for row in mau_rows:
        item, sub, prev, curr, v_plan, v_prev = row
        c_val = normalize_number(curr)
        if c_val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": "Area_Planted", "value": c_val, "unit": "1000_ha", "data_type": "Actual"},
                "comparison_context": {"comparison_type": "YoY", "comparison_value": normalize_number(v_prev)},
                "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
            })

    # 5. Cây CN ngắn ngày
    cn_rows = [
        ["Cây công nghiệp ngắn ngày", None, "334.5", "320.1", None, "95.7"],
        ["Đậu tương", None, "89.9", "77.7", None, "86.4"],
        ["Lạc", None, "168.1", "162.6", None, "96.7"],
        ["Mía", "Trồng mới", "50.2", "54.1", None, "107.8"],
        ["Thuốc lá", None, "16.5", "15.8", None, "95.6"],
    ]
    for row in cn_rows:
        item, sub, prev, curr, v_plan, v_prev = row
        c_val = normalize_number(curr)
        if c_val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Cultivation", "commodity": item, "sub_item": sub},
                "metric_context": {"attribute": "Area_Planted", "value": c_val, "unit": "1000_ha", "data_type": "Actual"},
                "comparison_context": {"comparison_type": "YoY", "comparison_value": normalize_number(v_prev)},
                "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
            })
            
    # 6. Rau đậu
    rau_dau = ["Rau, đậu các loại", None, "339.6", "360.3", None, "106.1"]
    c_val = normalize_number(rau_dau[3])
    if c_val:
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Cultivation", "commodity": rau_dau[0], "sub_item": None},
            "metric_context": {"attribute": "Area_Planted", "value": c_val, "unit": "1000_ha", "data_type": "Actual"},
            "comparison_context": {"comparison_type": "YoY", "comparison_value": normalize_number(rau_dau[5])},
            "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
        })

    return {"metadata": metadata, "records": records}


def parse_pl2():
    metadata = {
        "year": 2009,
        "month": 3,
        "appendix_number": "PL2",
        "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL2.md",
        "extraction_timestamp": datetime.now().isoformat(),
        "estimated_tokens": 0,
        "attempts": 1
    }
    records = []
    source_file = metadata["source_file"]
    appendix_number = metadata["appendix_number"]
    appendix_title = "GIEO CẤY LÚA ĐÔNG XUÂN VÀ MÀU LƯƠNG THỰC VỤ ĐÔNG XUÂN (Miền Bắc)"
    
    # [Loc, Lúa DX, Màu, Ngô, Khoai lang, Sắn]
    # Unit: ha. Normalize to 1000_ha.
    data = [
        ["Miền Bắc", "1,097,635", "274,166", "188,046", "22,459", "67,325"],
        ["Đồng bằng sông Hồng", "553,631", "37,647", "27,847", "4,652", "1,721"],
        ["Hà Nội", "99,791", "8,076", "7,221", "539", "316"],
        ["Hải Phòng", "49,688", "2,796", "1,700", None, None],
        ["Vĩnh Phúc", "30,782", "3,069", "2,052", "312", "705"],
        ["Bắc Ninh", "37,234", "1,004", "1,004", None, None],
        ["Hải Dương", "63,500", "4,500", "3,600", "1,250", None],
        ["Hưng Yên", "38,500", "6,487", "2,715", "91", None],
        ["Hà Nam", "32,500", "3,000", "3,000", "600", "400"],
        ["Nam Định", "77,650", "4,600", "2,900", "1,700", None],
        ["Thái Bình", "83,227", "2,155", "2,155", None, None],
        ["Ninh Bình", "40,759", "1,960", "1,500", "160", "300"],
        ["Đông Bắc", "176,438", "84,340", "58,495", "5,648", "20,197"],
        ["Hà Giang", "5,899", "7,544", "7,544", None, None],
        ["Cao Bằng", "400", "12,814", "12,704", "90", "20"],
        ["Lào Cai", "7,086", "4,432", "4,432", None, None],
        ["Bắc Cạn", "7,054", "7,519", "7,274", None, "245"],
        ["Lạng Sơn", "300", "295", "145", None, "150"],
        ["Tuyên Quang", "19,000", "6,604", "3,104", None, "3,500"],
        ["Yên Bái", "16,985", "27,350", "12,450", "2,150", "12,750"],
        ["Thái Nguyên", "27,967", "8,298", "4,769", "1,004", "2,525"],
        ["Phú Thọ", "34,500", "2,638", "2,503", "135", None],
        ["Bắc Giang", "45,000", "167", "167", None, None],
        ["Quảng Ninh", "12,247", "6,679", "3,403", "2,269", "1,007"],
        ["Tây Bắc", "33,360", "29,702", "5,998", "804", "22,900"],
        ["Lai Châu", "5,000", "3,374", "374", None, "3,000"],
        ["Điện Biên", "7,872", "9,076", "576", None, "8,500"],
        ["Sơn La", "6,488", "4,768", "1,368", None, "3,400"],
        ["Hoà Bình", "14,000", "12,484", "3,680", "804", "8,000"],
        ["Bắc Trung Bộ", "334,206", "122,477", "95,706", "11,355", "22,507"],
        ["Thanh Hoá", "119,149", "43,091", "29,736", "9,155", "4,200"],
        ["Nghệ An", "84,719", "16,749", "14,549", "2,200", None],
        ["Hà Tĩnh", "53,537", "2,832", "2,832", None, None],
        ["Quảng Bình", "27,500", "51,705", "45,036", None, "6,669"],
        ["Quảng Trị", "23,504", "8,100", "1,800", None, "6,300"],
        ["Thừa Thiên Huế", "25,797", "0", "1,753", None, "5,338"],
    ]
    
    regional = ["Miền Bắc", "Đông bằng sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    items = [
        ("Lúa", "Đông Xuân"),
        ("Màu lương thực", "Tổng số"),
        ("Ngô", None),
        ("Khoai lang", None),
        ("Sắn", None)
    ]

    for row in data:
        loc = row[0]
        geo_level = "Regional" if loc in regional else "Provincial"
        for i in range(1, 6):
            val = normalize_number(row[i])
            if val is not None:
                 records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                    "geo_context": {"geo_level": geo_level, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
                })
    return {"metadata": metadata, "records": records}


def parse_pl3():
    metadata = {
        "year": 2009,
        "month": 3,
        "appendix_number": "PL3",
        "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL3.md",
        "extraction_timestamp": datetime.now().isoformat(),
        "estimated_tokens": 0,
        "attempts": 1
    }
    records = []
    source_file = metadata["source_file"]
    appendix_number = metadata["appendix_number"]
    appendix_title = "DIỆN TÍCH GIEO TRỒNG CÂY VỤ ĐÔNG XUÂN (Miền Bắc)"
    
    # [Loc, Tổng CN, Đậu tương, Lạc, Mía, Thuốc lá, Rau]
    data = [
        ["Miền Bắc", "422592", "73818", "119896", "5794", "5810", "239251"],
        ["Đồng bằng sông Hồng", "182373", "56537", "25023", "291", "2687", "117835"],
        ["Hà Nội", "58870", "32907", "6809", None, None, "19154"],
        ["Hải Phòng", "13437", "200", None, None, "2237", "11000"],
        ["Vĩnh Phúc", "17225", "6049", "3166", "10", None, "8000"],
        ["Bắc Ninh", "11913", "1901", "1012", None, None, "9000"],
        ["Hải Dương", None, None, None, None, None, "20000"],
        ["Hưng Yên", "14446", "2530", "916", None, None, "11000"],
        ["Hà Nam", "6638", "200", "438", None, None, "6000"],
        ["Nam Định", "20977", "758", "6219", None, None, "14000"],
        ["Thái Bình", "22412", "5917", "2045", None, "450", "14000"],
        ["Ninh Bình", "16455", "6075", "4418", "281", None, "5681"],
        ["Đông Bắc", "92469", "9104", "20676", "1109", "3123", "58457"],
        ["Hà Giang", "8784", "2894", "2770", None, None, "3120"],
        ["Cao Bằng", "5416", "778", "56", "334", "2015", "2233"],
        ["Lào Cai", "4424", "2178", "185", None, "47", "2014"],
        ["Bắc Cạn", "1901", "518", "322", None, "711", "350"],
        ["Lạng Sơn", "7350", None, None, None, "350", "7000"],
        ["Tuyên Quang", "6218", "251", "2467", None, None, "3500"],
        ["Yên Bái", "7765", "1200", "1550", "775", None, "4240"],
        ["Thái Nguyên", "10219", "863", "3356", None, None, "6000"],
        ["Phú Thọ", "9618", "199", "3419", None, None, "6000"],
        ["Bắc Giang", "23081", "123", "5958", None, None, "17000"],
        ["Quảng Ninh", "7693", "100", "593", None, None, "7000"],
        ["Tây Bắc", "14636", "4103", "2480", "4394", "0", "3659"],
        ["Lai Châu", "1371", "1032", "282", None, None, "57"],
        ["Điện Biên", "941", "863", "78", None, None, None],
        ["Sơn La", "5360", "145", "0", "3273", None, "1942"],
        ["Hoà Bình", "6964", "2063", "2120", "1121", None, "1660"],
        ["Bắc Trung Bộ", "133114", "4074", "71717", "0", "0", "59300"],
        ["Thanh Hoá", "59675", "4074", "16837", None, None, "37000"],
        ["Nghệ An", "31400", None, "21100", None, None, "10300"],
        ["Hà Tĩnh", "23389", None, "20389", None, None, "3000"],
        ["Quảng Bình", "11950", None, "4950", None, None, "7000"],
        ["Quảng Trị", "6700", None, "4700", None, None, "2000"],
        ["Thừa Thiên Huế", "0", None, "3741", None, None, None],
    ]
    
    regional = ["Miền Bắc", "Đồng bằng sông Hồng", "Đông Bắc", "Tây Bắc", "Bắc Trung Bộ"]
    items = [
        ("Cây công nghiệp ngắn ngày", "Tổng số"),
        ("Đậu tương", None),
        ("Lạc", None),
        ("Mía", None),
        ("Thuốc lá", None),
        ("Rau, đậu các loại", None)
    ]

    for row in data:
        loc = row[0]
        geo_level = "Regional" if loc in regional else "Provincial"
        for i in range(1, 7):
            val = normalize_number(row[i])
            if val is not None:
                 records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                    "geo_context": {"geo_level": geo_level, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": {"source_file": source_file, "appendix_number": appendix_number, "appendix_title": appendix_title}
                })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/03"
    
    pl1 = parse_pl1()
    save_json(pl1, os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL1.json"))
    
    pl2 = parse_pl2()
    save_json(pl2, os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL2.json"))
    
    pl3 = parse_pl3()
    save_json(pl3, os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL3.json"))
    
    print("Successfully parsed PL1, PL2, and PL3 for March 2009.")
