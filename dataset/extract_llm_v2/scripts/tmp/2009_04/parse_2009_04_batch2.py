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
    if s == "" or s == "-" or s == '.':
        return None
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl5_04():
    # PL5: Cây CN ngắn ngày & Rau đậu Miền Nam (15/04/2009)
    metadata = {"year": 2009, "month": 4, "appendix_number": "PL5", "source_file": "2009_04_PHULUC_T04_2009_PL5.md"}
    records = []
    regional = ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"]
    items = [
        ("Cây công nghiệp ngắn ngày", "Tổng số"), ("Đậu tương", None), ("Lạc", None), ("Vừng", None), ("Thuốc lá", None), 
        ("Mía", "Trồng mới"), ("Bông", None), ("Đay, Lác", None), ("Rau các loại", None), ("Đậu các loại", None)
    ]
    
    # Extracting all data from MD
    raw_data = [
        ["Miền Nam", "122868", "3865", "44646", "2584", "10425", "60627", "243", "478", "141870", "22834<br>7082"],
        ["D.H Nam Trg Bộ", "25008", "687", "19020", "111", "370", "4581", "211", "28", "15143", "15143"],
        ["TP Đà Nẵng", "816", None, "639", None, None, "177", None, None, "300", "80"],
        ["Quảng Nam", "8100", None, "8100", None, None, None, None, None, "3500", "3500"],
        ["Quảng Ngãi", "3319", None, "3169", None, None, "150", None, None, "3905", "1147"],
        ["Bình Định", "6741", "371", "6370", None, None, None, None, None, "5452", "617"],
        ["Phú Yên", "5832", "316", "542", "111", "370", "4254", "211", "28", "1886", "1238"],
        ["Khánh Hoà", "200", None, "200", None, None, None, None, None, "100", "500"],
        ["Tây Nguyên", "14713", "0", "260", "0", "5921", "8532", None, None, "29073", "4931"],
        ["Kon Tum", "2404", None, "14", None, "2158", "232", None, None, "630", "57"],
        ["Gia Lai", "10504", None, "204", None, "3457", "6843", None, None, "5000", "2420"],
        ["Đắc Lắc", "457", None, "42", None, "306", "109", None, None, "2294", "1720"],
        ["Đắc Nông", "0", None, None, None, None, None, None, None, "7461", "201"],
        ["Lâm Đồng", "1348", None, None, None, None, "1348", None, None, "13688", "533"],
        ["Đông Nam Bộ", "25960", "563", "17194", "956", "3957", "3258", "32", None, "25895", "7939"],
        ["TP Hồ Chí Minh", "2920", None, "720", None, None, "2200", None, None, "5111", None],
        ["Ninh Thuận", "842", None, None, None, "500", "310", "32", None, "2920", "500"],
        ["Bình Phước", "60", None, "60", None, None, None, None, None, None, None],
        ["Tây Ninh", "19337", None, "15096", "887", "2877", "477", None, None, "7825", "3017"],
        ["Bình Dương", "579", None, "308", None, None, "271", None, None, "2024", "64"],
        ["Đồng Nai", "1115", "321", "145", "69", "580", None, None, None, "3542", "2000"],
        ["Bình Thuận", "1042", "242", "800", None, None, None, None, None, "1400", "2220"],
        ["Bà Rịa-V.Tàu", "65", None, "65", None, None, None, None, None, "3073", "138"],
        ["ĐBS Cửu Long", "71568", "2615", "8172", "1517", "177", "44256", None, "450", "71759", "2882"],
        ["Long An", "35280", None, "5361", "1157", None, "14381", "14381", None, "3312", None],
        ["Đồng Tháp", "307", "272", "35", None, None, None, None, None, "3195", None],
        ["An Giang", "512", "140", "191", "157", "6", "18", None, None, "11700", "1090"],
        ["Tiền Giang", None, None, None, None, None, None, None, None, "18571", None],
        ["Vĩnh Long", "1045", "681", "28", "198", None, "138", None, None, "8538", "231"],
        ["Bến Tre", "5391", None, "391", None, None, "5000", None, None, "2082", "128"],
        ["Cần Thơ", "1269", "1250", "3", "5", "11", None, None, None, "1451", "136"],
        ["Hậu Giang", "13453", None, None, None, None, "13453", None, None, "4521", None],
        ["Trà Vinh", "4230", None, "2088", None, None, "1692", None, "450", "6325", "426"],
        ["Sóc Trăng", "10081", "272", "75", None, "160", "9574", None, None, "12064", "871"],
    ]

    for row in raw_data:
        loc = row[0]
        geo = "Regional" if loc in regional else "Provincial"
        for i in range(1, 11):
            cell = str(row[i]) if row[i] else None
            if not cell: continue
            
            # Handle <br>
            cell_vals = cell.split("<br>")
            for cv in cell_vals:
                num = normalize_number(cv)
                if num is not None:
                    records.append({
                        "record_id": generate_id(),
                        "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative", "report_date": "2009-04-15"},
                        "geo_context": {"geo_level": geo, "location_name": loc},
                        "item_context": {"sector": "Cultivation", "commodity": items[i-1][0], "sub_item": items[i-1][1]},
                        "metric_context": {"attribute": "Area_Planted", "value": num / 1000.0, "unit": "1000_ha", "data_type": "Actual"},
                        "metadata": metadata
                    })
    return {"metadata": metadata, "records": records}


def parse_pl6_pl7_04():
    # PL6 (Forestry) & PL7 (Fishery) in March 2009
    metadata_base = {"year": 2009, "month": 4}
    records = []
    
    # 1. Forestry (PL6)
    # TT, Chỉ tiêu, Plan, C.kỳ, Tháng 4
    rows_f = [
        ["1", "Trồng rừng tập trung", "1000_ha", "Forest_Area_Planted", "227.3", "19.1", "20.3"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000_ha", "Forest_Area_Planted", "60.0", "2.1", "3.0"],
        ["1.2", "Rừng sản xuất", "1000_ha", "Forest_Area_Planted", "167.3", "17.1", "17.3"],
        ["2", "Chăm sóc rừng trồng", "1000_ha", "Other", "149.7", "90.0", "78.0"],
        ["3", "Trồng cây nhân dân", "million_trees", "Other", "200", "23.0", "76.2"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000_ha", "Other", "506", "628", "613.0"],
        ["5", "Khoán bảo vệ rừng từ nguồn vốn nhà nước", "1000_ha", "Forest_Area_Protected", "1524", "1960.5", "1780.0"],
        ["6", "Khai thác gỗ", "1000_m3", "Wood_Volume", "4380", "487", "606.0"],
    ]
    m6 = {"source_file": "2009_04_PHULUC_T04_2009_PL6.md", "appendix_number": "PL6"}
    m6.update(metadata_base)
    
    for r in rows_f:
        tt, item, unit, attr, plan, prev, curr = r
        # Plan
        nv_p = normalize_number(plan)
        if nv_p:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": nv_p, "unit": unit, "data_type": "Plan"},
                "metadata": m6
            })
        # Month 4 Actual
        nv_c = normalize_number(curr)
        if nv_c:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 4, "period_type": "Monthly"},
                "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
                "item_context": {"sector": "Forestry", "commodity": item},
                "metric_context": {"attribute": attr, "value": nv_c, "unit": unit, "data_type": "Estimated"},
                "metadata": m6
            })

    # 2. Fishery (PL7)
    # TT, Item, Unit, Plan 2009, 3mo_09, Est_Apr_09, 4mo_09, 4mo_08_Plan??
    rows_ts = [
        ["I", "Tổng sản lượng", "1000_ton", "Production", "4600", "1020", "344", "1364", "1301"],
        ["1", "Sản lượng khai thác", "1000_ton", "Production", "2200", "605", "204", "809", "738"],
        ["1.1", "Khai thác biển", "1000_ton", "Production", "2000", "560", "190", "750", "674"],
        ["1.2", "Khai thác nội địa", "1000_ton", "Production", "200", "45", "14", "59", "64"],
        ["2", "Sản lượng nuôi trồng", "1000_ton", "Production", "2400", "415", "140", "555", "563"],
        ["II", "Giá trị kim ngạch xuất khẩu TS", "million_USD", "Export_Value", "4500", "748", "300", "1048", "1140"],
    ]
    m7 = {"source_file": "2009_04_PHULUC_T04_2009_PL6.md", "appendix_number": "PL7"}
    m7.update(metadata_base)
    
    for r in rows_ts:
        tt, item, unit, attr, plan, cum3, curr4, cum4, prev_cum4 = r
        # Plan
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(plan), "unit": unit, "data_type": "Plan"},
            "metadata": m7
        })
        # Month 4 Est
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 4, "period_type": "Monthly"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(curr4), "unit": unit, "data_type": "Estimated"},
            "metadata": m7
        })
        # Cum 4 Est
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(cum4), "unit": unit, "data_type": "Estimated"},
            "metadata": m7
        })
        # Cum 4 Prev Year
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2008, "month": 4, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Cả nước"},
            "item_context": {"sector": "Fishery", "commodity": item},
            "metric_context": {"attribute": attr, "value": normalize_number(prev_cum4), "unit": unit, "data_type": "Actual"},
            "metadata": m7
        })
    return {"metadata": m6, "records": records}


def parse_pl8_04():
    # PL8: Trade Apr 09
    metadata = {"year": 2009, "month": 4, "appendix_number": "PL8", "source_file": "2009_04_PHULUC_T04_2009_PL8.md"}
    records = []
    
    # Simple direct data from MD
    data = [
        # Sector, Item, v08_4, g08_4, v09_3, g09_3, v09_m, g09_m, v09_4, g09_4
        ["Export", "Tổng kim ngạch XK", None, "4812", None, "3671", None, "1500", None, "5171"],
        ["Export", "Nông sản chính", None, "2564", None, "2145", None, "856", None, "3001"],
        ["Export", "Cà phê", "423", "854", "430", "649", "140", "204", "570", "853"],
        ["Export", "Cao su", "161", "388", "118", "163", "48", "67", "166", "230"],
        ["Export", "Gạo", "1674", "816", "1782", "812", "750", "350", "2532", "1162"],
        ["Export", "Chè", "27", "35", "23", "29", "9", "11", "32", "40"],
        ["Export", "Hạt điều", "42", "208", "31", "139", "13", "54", "44", "193"],
        ["Export", "Hạt tiêu", "25", "89", "27", "65", "12", "26", "39", "91"],
        ["Export", "Thuỷ sản", None, "1140", None, "748", None, "300", None, "1048"],
        ["Import", "Tổng kinh ngạch NK", None, "3751", None, "1883", None, "920", None, "2803"],
        ["Import", "Phân bón các loại", "1661", "701", "1098", "343", "600", "187", "1698", "530"],
    ]

    for r in data:
        sec, item, v08_4, g08_4, v09_3, g09_3, v09_m, g09_m, v09_4, g09_4 = r
        periods = [
            (2008, 4, "Cumulative", v08_4, g08_4, "Actual"),
            (2009, 3, "Cumulative", v09_3, g09_3, "Actual"),
            (2009, 4, "Monthly", v09_m, g09_m, "Estimated"),
            (2009, 4, "Cumulative", v09_4, g09_4, "Estimated")
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


def parse_pl9_04():
    # Phụ lục 9: Đầu tư XDCB tháng 4
    metadata = {"year": 2009, "month": 4, "appendix_number": "PL9", "source_file": "2009_04_PHULUC_T04_2009_PL9.md"}
    records = []
    # Items: Tổng mức đầu tư, Thuỷ lợi, Nông nghiệp, Lâm nghiệp, Thuỷ sản...
    # Cols: 1: Plan, 2: TH 3T (Actual), 3: TH T4 (Est), 4: TH 4T (Est)
    rows = [
        ["Tổng mức đầu tư", "2954763", "629072", "172735", "801807"],
        ["Đầu tư Thuỷ lợi", "1483500", "385050", "115000", "500050"],
        ["Đầu tư Nông nghiệp", "493000", "144650", "25985", "170635"],
        ["Đầu tư Lâm nghiệp", "230000", "20327", "6500", "26827"],
        ["Đầu tư Thuỷ sản", "24000", "4100", "1500", "5600"],
    ]
    for r in rows:
        item, plan, actual3, est4, cum4 = r
        # Plan
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(plan), "unit": "million_VND", "data_type": "Plan"},
            "metadata": metadata
        })
        # Month 4 Est
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 4, "period_type": "Monthly"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(est4), "unit": "million_VND", "data_type": "Estimated"},
            "metadata": metadata
        })
        # Cum 4 Est
        records.append({
            "record_id": generate_id(),
            "time_context": {"year": 2009, "month": 4, "period_type": "Cumulative"},
            "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
            "item_context": {"sector": "Investment", "commodity": item},
            "metric_context": {"attribute": "Investment_Value", "value": normalize_number(cum4), "unit": "million_VND", "data_type": "Estimated"},
            "metadata": metadata
        })
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/04"
    os.makedirs(out_dir, exist_ok=True)
    
    save_json(parse_pl5_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL5.json"))
    save_json(parse_pl6_pl7_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL6_PL7.json"))
    save_json(parse_pl8_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL8.json"))
    save_json(parse_pl9_04(), os.path.join(out_dir, "2009_04_PHULUC_T04_2009_PL9.json"))
    
    print("Successfully parsed PL5, PL6, PL7, PL8, PL9 for April 2009.")
