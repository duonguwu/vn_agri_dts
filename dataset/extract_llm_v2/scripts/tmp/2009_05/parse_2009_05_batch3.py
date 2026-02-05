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

def parse_pl6_05():
    # PL6a: Summary
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL6a", "source_file": "2009_05_PHULUC_T05_2009_PL6a.md"}
    records = []
    
    rows = [
        ["1", "Trồng rừng tập trung", "1000_ha", "Forest_Area_Planted", "227.3", "37.4", "48.9"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000_ha", "Forest_Area_Planted", "60.0", "7.3", "8.6"],
        ["1.2", "Rừng sản xuất", "1000_ha", "Forest_Area_Planted", "167.3", "30.1", "40.3"],
        ["2", "Chăm sóc rừng trồng", "1000_ha", "Forest_Area_Cared", "149.7", "152.5", "120.3"],
        ["3", "Trồng cây nhân dân", "million_trees", "Other", "200", "19.5", "89.5"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000_ha", "Other", "506", "640", "620.5"],
        ["5", "Khoán bảo vệ rừng", "1000_ha", "Forest_Area_Protected", "1524", "2069.7", "1840.7"],
        ["6", "Khai thác gỗ", "1000_m3", "Wood_Volume", "4380", "625", "920.0"],
    ]

    for r in rows:
        tt, item, unit, attr, plan, prev, curr = r
        # Plan
        if normalize_number(plan):
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": normalize_number(plan), "unit": unit, "data_type": "Plan"},
                "metadata": metadata
            })
        # Month 5 Est/Actual
        if normalize_number(curr):
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Monthly"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": normalize_number(curr), "unit": unit, "data_type": "Estimated"},
                "metadata": metadata
            })
    return {"metadata": metadata, "records": records}


def parse_pl6b_05():
    # PL6b: Provincial Forestry
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL6b", "source_file": "2009_05_PHULUC_T05_2009_PL6b.md"}
    records = []
    regional = ["Cả nước", "Miền bắc", "ĐB. sông Hồng", "Đông bắc", "Tây bắc", "Bắc Trung Bộ", "Miền Nam", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    rows = [
        ["Cả nước", "48851", "8556", "40295", "1840736"],
        ["Miền bắc", "48454", "8556", "39898", "1024232"],
        ["ĐB. sông Hồng", "1486", "1014", "472", "43735"],
        ["Hà Nội", None, None, None, "8600"],
        ["Hải Phòng", "500", "300", "200", "5500"],
        ["Vĩnh Phúc", "90", "30", "60", "4500"],
        ["Bắc Ninh", "15", "15", None, "300"],
        ["Hải Dương", "15", None, "15", "6235"],
        ["Hà Nam", "122.6", "26", "97.0", "6300"],
        ["Nam Định", None, None, None, "1700"],
        ["Thái Bình", "501", "501", None, "7000"],
        ["Ninh Bình", "243", "143", "100", "3600"],
        ["Đông bắc", "32405", "3465", "28940", "524778"],
        ["Hà Giang", "5850", "1000", "4850", "122913"],
        ["Cao Bằng", "119.0", "58.0", "61", "32000"],
        ["Lào Cai", "719", "61.0", "658", "38115"],
        ["Bắc Cạn", "1700", "50", "1650", "25000"],
        ["Lạng Sơn", "1836.0", "398.0", "1438.0", "13626"],
        ["Tuyên Quang", "2897.0", "168", "2729.0", "22000"],
        ["Yên Bái", "6610.0", "182", "6428", "145765"],
        ["Thái Nguyên", "1887.0", "275.0", "1612.0", "20000"],
        ["Phú Thọ", "3988.0", "130", "3858", "46606"],
        ["Bắc Giang", "1529.0", "123", "1406", "33753"],
        ["Quảng Ninh", "5270.0", "1020", "4250", "25000"],
        ["Tây bắc", "8375", "2972", "5403", "202000"],
        ["Lai Châu", "2191.0", "2091", "100", "92000"],
        ["Điện Biên", "449.0", "300.0", "149", "30000"],
        ["Sơn La", "3276.0", "80", "3196", "50000"],
        ["Hoà Bình", "2459.0", "501", "1958", "30000"],
        ["Bắc Trung Bộ", "6188.0", "1105", "5083", "253719"],
        ["Thanh Hoá", "4550.0", "700", "3850", "70000"],
        ["Nghệ An", "1588.0", "355", "1233", "85000"],
        ["Hà Tĩnh", "50.0", "50", None, "27219"],
        ["Quảng Bình", "0.0", None, None, "40000"],
        ["Quảng Trị", "0.0", None, None, "15500"],
        ["Thừa Thiên Huế", "0.0", None, None, "16000"],
        ["Miền Nam", "397.0", "0", "397", "691694"],
        ["D.H Nam Trung Bộ", "20.0", "0", "20", "142500"],
        ["Đà Nẵng", "20.0", None, "20", "15000"],
        ["Quảng Nam", None, None, None, "35000"],
        ["Quảng Ngãi", None, None, None, "28000"],
        ["Bình Định", None, None, None, "20000"],
        ["Phú Yên", None, None, None, "30000"],
        ["Khánh Hoà", None, None, None, "14500"],
        ["Tây Nguyên", "377", "0", "377", "290000"],
        ["Kon Tum", None, None, None, "80000"],
        ["Gia Lai", None, None, None, "40000"],
        ["Đắc Lắc", None, None, None, "50000"],
        ["Đắc Nông", None, None, None, "40000"],
        ["Lâm Đồng", "377", None, "377", "80000"],
        ["Đông Nam Bộ", "0", "0", "0", "207394"],
        ["TP Hồ Chí Minh", None, None, None, "16000"],
        ["Ninh Thuận", None, None, None, "40000"],
        ["Bình Phước", None, None, None, "20000"],
        ["Tây Ninh", None, None, None, "20000"],
        ["Đồng Nai", None, None, None, "1600"],
        ["Bình Thuận", None, None, None, "108313"],
        ["Bà Rịa-Vũng Tàu", None, None, None, "1481"],
        ["ĐB. sông Cửu Long", "0", "0", "0", "51800"],
        ["Long An", None, None, None, "1000"],
        ["Đồng Tháp", None, None, None, "3200"],
        ["An Giang", None, None, None, "2000"],
        ["Tiền Giang", None, None, None, "1200"],
        ["Bến Tre", None, None, None, "1700"],
        ["Kiên Giang", None, None, None, "14000"],
        ["Cần Thơ", None, None, None, "1900"],
        ["Hậu Giang", None, None, None, "1600"],
        ["Trà Vinh", None, None, None, "4100"],
        ["Sóc Trăng", None, None, None, "1200"],
        ["Bạc Liêu", None, None, None, "1900"],
        ["Cà Mau", None, None, None, "18000"],
    ]
    
    for row in rows:
        loc = row[0]
        geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional else "Provincial")
        
        # Trồng rừng tập trung (Total)
        val = normalize_number(row[1])
        if val is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Monthly"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Forestry", "commodity": "Trồng rừng tập trung"},
                "metric_context": {"attribute": "Forest_Area_Planted", "value": float(val), "unit": "ha", "data_type": "Estimated"},
                "metadata": metadata
            })
            
        # Khoán bảo vệ rừng
        val_prot = normalize_number(row[4])
        if val_prot is not None:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Monthly"},
                "geo_context": {"geo_level": geo, "location_name": loc},
                "item_context": {"sector": "Forestry", "commodity": "Khoán bảo vệ rừng"},
                "metric_context": {"attribute": "Forest_Area_Protected", "value": float(val_prot), "unit": "ha", "data_type": "Estimated"},
                "metadata": metadata
            })
    return {"metadata": metadata, "records": records}


def parse_pl7_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL7", "source_file": "2009_05_PHULUC_T05_2009_PL7.md"}
    records = []
    rows = [
        ["I", "Tổng sản lượng", "1000_ton", "Production", "4600", "1383", "353.6", "1737", "1635"],
        ["1", "Sản lượng khai thác", "1000_ton", "Production", "2200", "803", "186", "989", "908"],
        ["1.1", "Khai thác biển", "1000_ton", "Production", "2000", "742", "170", "912", "833"],
        ["1.2", "Khai thác nội địa", "1000_ton", "Production", "200", "61", "16", "77", "75"],
        ["2", "Sản lượng nuôi trồng", "1000_ton", "Production", "2400", "581", "168", "748", "727"],
        ["II", "Giá trị kim ngạch xuất khẩu TS", "million_USD", "Export_Value", "4500", "1056", "300", "1356", "1510"],
    ]
    
    for r in rows:
        tt, item, unit, attr, plan, cum4, curr5, cum5, prev_cum5 = r
        # Plan
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(plan), "unit": unit, "data_type": "Plan"},
            "metadata": metadata
        })
        # Month 5 Est
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 5, "period_type": "Monthly"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(curr5), "unit": unit, "data_type": "Estimated"},
            "metadata": metadata
        })
        # Cum 5 Est
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(cum5), "unit": unit, "data_type": "Estimated"},
            "metadata": metadata
        })
        # Cum 5 Prev Year
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2008, "month": 5, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(prev_cum5), "unit": unit, "data_type": "Actual"},
            "metadata": metadata
        })
    return {"metadata": metadata, "records": records}


def parse_pl8_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL8", "source_file": "2009_05_PHULUC_T05_2009_PL8.md"}
    records = []
    data = [
        ["Export", "Tổng kim ngạch XK", None, "6371", None, "5037", None, "1400", None, "6437"],
        ["Export", "Gạo", "2234", "1260", "2487", "1158", "710", "350", "3197", "1508"],
        ["Import", "Tổng kinh ngạch NK", None, "4780", None, "2788", None, "900", None, "3688"],
        ["Import", "Phân bón các loại", "1985", "905", "1652", "523", "540", "180", "2192", "703"],
    ]
    for r in data:
        sec, item, v08_5, g08_5, v09_4, g09_4, v09_m, g09_m, v09_5, g09_5 = r
        periods = [
            (2008, 5, "Cumulative", v08_5, g08_5, "Actual"),
            (2009, 4, "Cumulative", v09_4, g09_4, "Actual"),
            (2009, 5, "Monthly", v09_m, g09_m, "Estimated"),
            (2009, 5, "Cumulative", v09_5, g09_5, "Estimated")
        ]
        for y, m, pt, vol, val, dt in periods:
            if normalize_number(vol):
                records.append({
                    "record_id": generate_id(),
                    "time_context": {"year": y, "month": m, "period_type": pt},
                    "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                    "item_context": {"sector": "Trade", "commodity": item},
                    "metric_context": {"attribute": f"{sec}_Volume", "value": normalize_number(vol), "unit": "1000_ton", "data_type": dt},
                    "metadata": metadata
                })
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


def parse_pl9_05():
    metadata = {"year": 2009, "month": 5, "appendix_number": "PL9", "source_file": "2009_05_PHULUC_T05_2009_PL9.md"}
    records = []
    rows = [
        ["Tổng mức đầu tư", "2954763", "994936", "181778", "1176714"],
        ["Đầu tư Thuỷ lợi", "1483500", "674643", "110000", "784643"],
        ["Đầu tư Nông nghiệp", "493000", "169953", "46278", "216231"],
        ["Đầu tư Lâm nghiệp", "230000", "23588", "4500", "28088"],
        ["Đầu tư Thuỷ sản", "24000", "7000", "2000", "9000"],
    ]
    for r in rows:
        item, plan, actual4, est5, cum5 = r
        # Plan
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(plan), "unit": "million_VND", "data_type": "Plan"},
            "metadata": metadata
        })
        # Month 5
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 5, "period_type": "Monthly"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(est5), "unit": "million_VND", "data_type": "Estimated"},
            "metadata": metadata
        })
        # Cum 5
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(cum5), "unit": "million_VND", "data_type": "Estimated"},
            "metadata": metadata
        })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/05"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl6_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL6a.json"))
    save_json(parse_pl6b_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL6b.json"))
    save_json(parse_pl7_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL7.json"))
    save_json(parse_pl8_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL8.json"))
    save_json(parse_pl9_05(), os.path.join(out_dir, "2009_05_PHULUC_T05_2009_PL9.json"))
    
    print("Successfully parsed PL6, PL7, PL8, PL9 for May 2009.")
