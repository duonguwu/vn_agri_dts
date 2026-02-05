import json
import uuid
from datetime import datetime
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if not s or s.strip() == "" or s.strip() == "||" or s.strip() == "|" or s.strip() == '"':
        return None
    s = s.strip().replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    if s == "" or s == "-":
        return None
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl4_03():
    # Phụ lục 4: Thu hoạch lúa và trồng màu miền Nam
    metadata = {"year": 2009, "month": 3, "appendix_number": "PL4", "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL4.md"}
    records = []
    # Columns mapping
    # 0: Loc, 1: Lúa DX Planted, 2: Lúa DX Harvested, 3: Lúa HT Planted, 4: Màu Tổng, 5: Ngô, 6: Khoai Lang, 7: Sắn, 8: Có củ khác
    # Unit: Ha -> 1000_ha
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    
    rows = [
        ["Miền Nam", "1883381", "796171", "102321", "121606", "55875", "8059", "47781", "9891"],
        ["D.H Nam Trg Bộ", "172466", "1355", None, "38362", "13070", "4267", "20667", "358"],
        ["TP Đà Nẵng", "4006", None, None, "575", "362", "143", "70", None],
        ["Quảng Nam", "40800", None, None, "8400", "4700", "3700", None, None],
        ["Quảng Ngãi", "36243", "1355", None, "14941", "3460", "241", "11240", None],
        ["Bình Định", "46898", None, None, "9693", "1797", None, "7896", None],
        ["Phú Yên", "25649", None, None, "3503", "1859", "183", "1461", None],
        ["Khánh Hoà", "18870", None, None, "1250", "892", None, None, "358"],
        ["Tây Nguyên", "67271", "398", None, "17670", "10756", "1947", "4967", None],
        ["Kon Tum", "6775", None, None, "600", "600", None, None, None],
        ["Gia Lai", "23332", None, None, "9321", "4591", "263", "4467", None],
        ["Đắc Lắc", "23435", None, None, "3230", "2160", "570", "500", None],
        ["Đắc Nông", "3836", None, None, "3328", "2577", "751", None, None],
        ["Lâm Đồng", "9893", "398", None, "1191", "828", "363", None, None],
        ["Đông Nam Bộ", "100446", "19364", None, "45710", "19171", "542", "21345", "4652"],
        ["TP Hồ Chí Minh", "6700", None, None, "1049", "1049", None, None, None],
        ["Ninh Thuận", "11000", None, None, "2300", "2300", None, None, None],
        ["Bình Phước", "3000", None, None, None, None, None, None, None],
        ["Tây Ninh", "42016", "1764", None, "22639", "4993", None, "17646", None],
        ["Bình Dương", "2529", None, None, "5605", "142", "72", "1114", "4277"],
        ["Đồng Nai", "10100", None, None, "9200", "7000", "100", "2100", None],
        ["Bình Thuận", "20001", "12500", None, "3850", "2690", "300", "485", "375"],
        ["Bà Rịa-V.Tàu", "5100", "5100", None, "1067", "997", "70", None, None],
        ["ĐBS Cửu Long", "1543198", "775054", "102321", "19864", "12878", "1303", "802", "4881"],
        ["Long An", "247006", "97500", "13800.0", "3497", "3497", None, None, None],
        ["Đồng Tháp", "207347", "72938", "19662.0", "1507", "1399", "108", None, None],
        ["An Giang", "234228", "84127", "600.0", "1700", "1700", None, None, None],
        ["Tiền Giang", "82526", "78727", "16500.0", None, "1890", "12", "178", "1456"],
        ["Vĩnh Long", "67937", "61186", "7541.0", "3461", "678", "90", None, "2693"],
        ["Bến Tre", "21218", "757", None, "694", "382", "100", None, "212"],
        ["Kiên Giang", "277144", "148694", None, None, None, None, None, None],
        ["Cần Thơ", "90044", "53687", "9662.0", "269", "269", None, None, None],
        ["Hậu Giang", "81171", "22775", "602.0", None, "505", None, None, "520"],
        ["Trà Vinh", "53748", "42050", "5799.0", "918", "660", "137", "121", None],
        ["Sóc Trăng", "138659", "101427", "28155.0", "3257", "1898", "856", "503", None],
        ["Bạc Liêu", "42170", "11186", None, None, None, None, None, None],
    ]
    
    for row in rows:
        loc = row[0]
        geo_level = "Regional" if loc in regional else "Provincial"
        
        # 1: Lúa DX Planted
        val = normalize_number(row[1])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                "geo_context": {"geo_level": geo_level, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
        # 2: Lúa DX Harvested
        val = normalize_number(row[2])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                "geo_context": {"geo_level": geo_level, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Đông Xuân"},
                "metric_context": {"attribute": "Area_Harvested", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
        # 3: Lúa HT Planted (often cumulative)
        val = normalize_number(row[3])
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo_level, "location_name": loc},
                "item_context": {"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                "metadata": metadata
            })
        # Màu (Indices 4-8)
        mau_cols = [("Gieo trồng các cây màu lương thực", "Tổng số"), ("Ngô", None), ("Khoai lang", None), ("Sắn", None), ("Cây có củ khác", None)]
        for i in range(4, 9):
            val = normalize_number(row[i])
            if val:
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
                    "geo_context": {"geo_level": geo_level, "location_name": loc},
                    "item_context": {"sector": "Cultivation", "commodity": mau_cols[i-4][0], "sub_item": mau_cols[i-4][1]},
                    "metric_context": {"attribute": "Area_Planted", "value": val / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                    "metadata": metadata
                })

    return {"metadata": metadata, "records": records}


def parse_pl5_03():
    # Phụ lục 5: Cây CN ngắn ngày & Rau đậu Miền Nam
    metadata = {"year": 2009, "month": 3, "appendix_number": "PL5", "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    items = [
        ("Cây công nghiệp ngắn ngày", "Tổng số"),
        ("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None),
        ("Rau các loại", None), ("Đậu các loại", None)
    ]
    
    rows = [
        ["Miền Nam", "109592", "3865", "42660", "2022", "9987", "50337", "243", "478", "133356", "21547<br>7082"],
        ["D.H Nam Trg Bộ", "25008", "687", "19020", "111", "370", "4581", "211", "28", "15143", "15143"],
        ["TP Đà Nẵng", "816", None, "639", None, None, "177", None, None, "300", "80"],
        ["Quảng Nam", "8100", None, "8100", None, None, None, None, None, "3500", "3500"],
        ["Quảng Ngãi", "3319", None, "3169", None, None, "150", None, None, "3905", "1147"],
        ["Bình Định", "6741", "371", "6370", None, None, None, None, None, "5452", "617"],
        ["Phú Yên", "5832", "316", "542", "111", "370", "4254", "211", "28", "1886", "1238"],
        ["Khánh Hoà", "200", None, "200", None, None, None, None, None, "100", "500"],
        ["Tây Nguyên", "13371", "0", "260", "0", "5483", "7628", None, None, "30829", "4557"],
        ["Kon Tum", "2297", None, "14", None, "2158", "125", None, None, "630", "57"],
        ["Gia Lai", "9684", None, "204", None, "3325", "6155", None, None, "7185", "2177"],
        ["Đắc Lắc", "42", None, "42", None, None, None, None, None, "1865", "1589"],
        ["Đắc Nông", "0", None, None, None, None, None, None, None, "7461", "201"],
        ["Lâm Đồng", "1348", None, None, None, None, "1348", None, None, "13688", "533"],
        ["Đông Nam Bộ", "26930", "563", "15334", "573", "3957", "6471", "32", None, "21372", "7074"],
        ["TP Hồ Chí Minh", "2914", None, "714", None, None, "2200", None, None, "3855", None],
        ["Ninh Thuận", "842", None, None, None, "500", "310", "32", None, "2920", "500"],
        ["Bình Phước", "60", None, "60", None, None, None, None, None, None, None],
        ["Tây Ninh", "20439", None, "13368", "504", "2877", "3690", None, None, "5482", "2199"],
        ["Bình Dương", "453", None, "182", None, None, "271", None, None, "1100", "17"],
        ["Đồng Nai", "1115", "321", "145", "69", "580", None, None, None, "3542", "2000"],
        ["Bình Thuận", "1042", "242", "800", None, None, None, None, None, "1400", "2220"],
        ["Bà Rịa-V.Tàu", "65", None, "65", None, None, None, None, None, "3073", "138"],
        ["ĐBS Cửu Long", "58664", "2615", "8046", "1338", "177", "31657", None, "450", "66012", "2834"],
        ["Long An", "20720", None, "5361", "978", None, None, "14381", None, "3196", None],
        ["Đồng Tháp", "307", "272", "35", None, None, None, None, None, "3195", None],
        ["An Giang", "512", "140", "191", "157", "6", "18", None, None, "11700", "1090"],
        ["Tiền Giang", None, None, None, None, None, None, None, None, "13072", None],
        ["Vĩnh Long", "1045", "681", "28", "198", None, "138", None, None, "8538", "231"],
        ["Bến Tre", "7047", None, "265", None, None, "6782", None, None, "1950", "80"],
        ["Kiên Giang", "0", None, None, None, None, None, None, None, None, None],
        ["Cần Thơ", "1269", "1250", "3", "5", "11", None, None, None, "1451", "136"],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "4521", None],
        ["Trà Vinh", "4230", None, "2088", None, None, "1692", None, "450", "6325", "426"],
        ["Sóc Trăng", "10081", "272", "75", None, "160", "9574", None, None, "12064", "871"],
    ]

    for row in rows:
        loc = row[0]
        geo_level = "Regional" if loc in regional else "Provincial"
        for i in range(1, 11):
            cell = str(row[i]) if row[i] else None
            if not cell: continue
            
            # Split <br> values
            cell_vals = cell.split("<br>")
            for cv in cell_vals:
                num = normalize_number(cv)
                if num is not None:
                    records.append({
                        "record_id": generate_id(),
                        "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative", "report_date": "2009-03-15"},
                        "geo_context": {"geo_level": geo_level, "location_name": loc},
                        "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                        "metric_context": {"attribute": "Area_Planted", "value": num / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                        "metadata": metadata
                    })
    return {"metadata": metadata, "records": records}


def parse_pl6_pl7_03():
    # March PL6 has Forestry AND Thủy sản (as PL7) in the same MD file.
    metadata_base = {"year": 2009, "month": 3}
    records = []
    
    # 1. Forestry (PL6 part)
    # [TT, Item, Unit, Attr, Plan, Prev_Cum_YearSameMonth, Curr_Month]
    rows_f = [
        ["1", "Trồng rừng tập trung", "1000_ha", "Forest_Area_Planted", "227.3", "12.2", "16.8"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000_ha", "Forest_Area_Planted", "60.0", "1.2", "2.7"],
        ["1.2", "Rừng sản xuất", "1000_ha", "Forest_Area_Planted", "167.3", "11.0", "14.1"],
        ["2", "Chăm sóc rừng trồng", "1000_ha", "Other", "149.7", "71.0", "72.0"],
        ["3", "Trồng cây nhân dân", "million_trees", "Other", "200", "15.1", "59.2"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000_ha", "Other", "506", "611", "609"],
        ["5", "Khoán bảo vệ rừng từ nguồn vốn nhà nước", "1000_ha", "Forest_Area_Protected", "1524", "2007.5", "1730"],
        ["6", "Khai thác gỗ", "1000_m3", "Wood_Volume", "4380", "484", "494"],
    ]
    
    for r in rows_f:
        tt, item, unit, attr, plan, prev, curr = r
        m6 = {"source_file": "2009_03_PHULUC_T03_2009_FINAL_PL6.md", "appendix_number": "PL6"}
        m6.update(metadata_base)
        
        # Plan
        if normalize_number(plan):
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": normalize_number(plan), "unit": unit, "data_type": "Plan"},
                "metadata": m6
            })
        # Prev Mar 2008
        if normalize_number(prev):
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 3, "period_type": "Monthly"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": normalize_number(prev), "unit": unit, "data_type": "Actual"},
                "metadata": m6
            })
        # Curr Mar 2009
        if normalize_number(curr):
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 3, "period_type": "Monthly"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": normalize_number(curr), "unit": unit, "data_type": "Estimated"},
                "metadata": m6
            })

    # 2. Fishery (PL7 part in same file)
    # [TT, Item, Unit, Attr, 2mo_09, Curr_Mar_09, 3mo_09, 3mo_08_Plan??] 
    # Actually columns in PL7 part are: 4: Plan 2009, 5: 2 months, 6: Month 3, 7: 3 months
    rows_ts = [
        ["I", "Tổng sản lượng", "1000_ton", "Production", "4600", "683", "345", "1028"],
        ["1", "Sản lượng khai thác", "1000_ton", "Production", "2200", "398", "215", "613"],
        ["1.1", "Khai thác biển", "1000_ton", "Production", "2000", "368", "200", "568"],
        ["1.2", "Khai thác nội địa", "1000_ton", "Production", "200", "30", "15", "45"],
        ["2", "Sản lượng nuôi trồng", "1000_ton", "Production", "2400", "285", "130", "415"],
        ["II", "Giá trị kim ngạch xuất khẩu TS", "million_USD", "Export_Value", "4500", "444", "300", "744"],
    ]
    
    m7 = {"source_file": "2009_03_PHULUC_T03_2009_FINAL_PL6.md", "appendix_number": "PL7"}
    m7.update(metadata_base)
    
    for r in rows_ts:
        tt, item, unit, attr, plan, cum2, curr3, cum3 = r
        # Plan
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(plan), "unit": unit, "data_type": "Plan"},
            "metadata": m7
        })
        # Month 3
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 3, "period_type": "Monthly"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(curr3), "unit": unit, "data_type": "Estimated"},
            "metadata": m7
        })
        # Cum 3
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(cum3), "unit": unit, "data_type": "Estimated"},
            "metadata": m7
        })
        
    return {"metadata": m6, "records": records}


def parse_pl8_03():
    # Phụ lục 8: Xuất nhập khẩu tháng 3
    metadata = {"year": 2009, "month": 3, "appendix_number": "PL8", "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL8.md"}
    records = []
    # Columns: 1: TH 3mo 08, 2/3: TH 2mo 09, 4/5: Est Mar 09, 6/7: Est 3mo 09
    # Indices in logic: row[1]: 3mo08 Vol, row[2]: 3mo08 Val, row[3]: 2mo09 Vol, row[4]: 2mo09 Val...
    # Wait, markdown has: 1, 2 (3mo 08), skip, skip, 3, 4 (Mar 09), 5, 6 (3mo 09)
    # Check MD: |1|2|||3|4|5|6|
    
    # Simple manual extraction for trade items
    data = [
        # Sector, Item, 3mo08 Vol, 3mo08 Val, 2mo09 Vol, 2mo09 Val, Mar09 Vol, Mar09 Val, 3mo09 Vol, 3mo09 Val
        ["Export", "Tổng kim ngạch XK", None, "3362", None, "2266", None, "1200", None, "3466"],
        ["Export", "Nông sản chính", None, "1767", None, "1317", None, "649", None, "1966"],
        ["Export", "Cà phê", "345", "682", "289", "444", "130", "189", "419", "634"],
        ["Export", "Cao su", "124", "292", "76", "102", "39", "57", "115", "158"],
        ["Export", "Gạo", "1017", "445", "1043", "470", "560", "257", "1603", "727"],
        ["Export", "Thuỷ sản", None, "800", None, "444", None, "300", None, "744"],
        ["Import", "Tổng kinh ngạch NK", None, "2667", None, "1074", None, "640", None, "1714"],
        ["Import", "Phân bón các loại", "454", "196", "576", "183", "298", "93", "874", "276"],
    ]
    
    for r in data:
        sec, item, v08_3, g08_3, v09_2, g09_2, v09_m, g09_m, v09_3, g09_3 = r
        periods = [
            (2008, 3, "Cumulative", v08_3, g08_3, "Actual"),
            (2009, 2, "Cumulative", v09_2, g09_2, "Actual"),
            (2009, 3, "Monthly", v09_m, g09_m, "Estimated"),
            (2009, 3, "Cumulative", v09_3, g09_3, "Estimated")
        ]
        for y, m, pt, vol, val, dt in periods:
            # Volume
            if normalize_number(vol):
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": y, "month": m, "period_type": pt},
                    "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                    "item_context": {"sector": "Trade", "commodity": item},
                    "metric_context": {"attribute": f"{sec}_Volume", "value": normalize_number(vol), "unit": "1000_ton", "data_type": dt},
                    "metadata": metadata
                })
            # Value
            if normalize_number(val):
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": y, "month": m, "period_type": pt},
                    "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                    "item_context": {"sector": "Trade", "commodity": item},
                    "metric_context": {"attribute": f"{sec}_Value", "value": normalize_number(val), "unit": "million_USD", "data_type": dt},
                    "metadata": metadata
                })
    return {"metadata": metadata, "records": records}


def parse_pl9_03():
    # Phụ lục 9: Đầu tư XDCB tháng 3
    metadata = {"year": 2009, "month": 3, "appendix_number": "PL9", "source_file": "2009_03_PHULUC_T03_2009_FINAL_PL9.md"}
    records = []
    # Items: Tổng mức đầu tư, Thuỷ lợi, Nông nghiệp, Lâm nghiệp, Thuỷ sản...
    # Cols: 1: Plan, 2: TH 2T (Actual), 3: TH T3 (Est), 4: TH 3T (Est)
    rows = [
        ["Tổng mức đầu tư", "2954763", "382186", "211951", "594137"],
        ["Đầu tư Thuỷ lợi", "1483500", "230000", "125000", "355000"],
        ["Đầu tư Nông nghiệp", "493000", "83913", "60701", "144614"],
        ["Đầu tư Lâm nghiệp", "230000", "14473", "4500", "18973"],
        ["Đầu tư Thuỷ sản", "24000", "2500", "1000", "3500"],
    ]
    for r in rows:
        item, plan, actual2, est3, cum3 = r
        # Plan
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(plan), "unit": "million_VND", "data_type": "Plan"},
            "metadata": metadata
        })
        # Month 3
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 3, "period_type": "Monthly"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(est3), "unit": "million_VND", "data_type": "Estimated"},
            "metadata": metadata
        })
        # Cum 3
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 3, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(cum3), "unit": "million_VND", "data_type": "Estimated"},
            "metadata": metadata
        })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/03"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl4_03(), os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL4.json"))
    save_json(parse_pl5_03(), os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL5.json"))
    save_json(parse_pl6_pl7_03(), os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL6_PL7.json"))
    save_json(parse_pl8_03(), os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL8.json"))
    save_json(parse_pl9_03(), os.path.join(out_dir, "2009_03_PHULUC_T03_2009_FINAL_PL9.json"))
    
    print("Successfully parsed PL4 - PL9 for March 2009.")
