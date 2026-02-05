import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|": return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_national_record(metadata, time, item, metric, comp=None):
    return {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": {"geo_level": "National", "location_name": "Cả nước", "region_id": "NATIONAL", "region_name": "Cả nước"},
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata,
        "comparison_context": comp
    } if comp else {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": {"geo_level": "National", "location_name": "Cả nước", "region_id": "NATIONAL", "region_name": "Cả nước"},
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata
    }

def parse_pl4_12():
    metadata = {"year": 2009, "month": 12, "appendix_number": "PL4", "source_file": "2009_12_Phuluc_T12_2009_PL4.md"}
    records = []
    # Items: Bông, Đay, Cói, Lạc, Đậu tương, Rau các loại, Đậu các loại
    # Structure: [Item, Unit, val08, val09, comp]
    # Since area/yield/production are stacked, I'll map them carefully.
    data = [
        ["Bông", "1000 ha", 5.8, 8.0, 137.9, "Area_Planted"],
        ["Bông", "tạ/ha", 13.8, 12.5, 90.6, "Yield"],
        ["Bông", "1000 tấn", 8.0, 10.0, 125.0, "Production"],
        ["Đay", "1000 ha", 3.3, 1.9, 57.6, "Area_Planted"],
        ["Đay", "tạ/ha", 23.6, 28.9, 122.7, "Yield"],
        ["Đay", "1000 tấn", 7.8, 5.5, 70.5, "Production"],
        ["Cói", "1000 ha", 11.7, 10.3, 88.0, "Area_Planted"],
        ["Cói", "tạ/ha", 72.5, 73.5, 101.4, "Yield"],
        ["Cói", "1000 tấn", 84.8, 75.7, 89.3, "Production"],
        ["Lạc", "1000 ha", 255.3, 249.2, 97.6, "Area_Planted"],
        ["Lạc", "tạ/ha", 20.8, 21.1, 101.3, "Yield"],
        ["Lạc", "1000 tấn", 530.2, 525.1, 99.0, "Production"],
        ["Đậu tương", "1000 ha", 192.1, 146.2, 76.1, "Area_Planted"],
        ["Đậu tương", "tạ/ha", 13.9, 14.6, 105.1, "Yield"],
        ["Đậu tương", "1000 tấn", 267.6, 213.6, 79.8, "Production"],
        ["Rau các loại", "1000 ha", 722.2, 734.5, 101.7, "Area_Planted"],
        ["Rau các loại", "tạ/ha", 159.4, 162.0, 101.6, "Yield"],
        ["Rau các loại", "1000 tấn", 11512.6, 11896.9, 103.3, "Production"],
        ["Đậu các loại", "1000 ha", 197.5, 191.2, 96.8, "Area_Planted"],
        ["Đậu các loại", "tạ/ha", 9.5, 10.0, 105.9, "Yield"],
        ["Đậu các loại", "1000 tấn", 186.9, 191.6, 102.5, "Production"],
    ]
    for r in data:
        item, unit, v08, v09, comp, attr = r
        i_ctx = {"sector": "Cultivation", "commodity": item}
        t09 = {"year": 2009, "month": 12, "period_type": "Annual"}
        t08 = {"year": 2008, "month": 12, "period_type": "Annual"}
        
        c09 = {"comparison_type": "YoY", "comparison_value": (comp), "comparison_unit": "percentage", "reference_period": "2008"}
        records.append(create_national_record(metadata, t09, i_ctx, {"attribute": attr, "value": float(v09), "unit": unit, "data_type": "Actual"}, c09))
        records.append(create_national_record(metadata, t08, i_ctx, {"attribute": attr, "value": float(v08), "unit": unit, "data_type": "Actual"}))
        
    return {"metadata": metadata, "records": records}


def parse_pl5_pl6_12():
    # Both in file PL5.md
    metadata5 = {"year": 2009, "month": 12, "appendix_number": "PL5", "source_file": "2009_12_Phuluc_T12_2009_PL5.md"}
    metadata6 = {"year": 2009, "month": 12, "appendix_number": "PL6", "source_file": "2009_12_Phuluc_T12_2009_PL5.md"}
    records = []
    
    # PL5 - Perennial
    pl5_rows = [
        ["Chuối", "Area_Planted", "112.0", "114.0", "101.7"],
        ["Chuối", "Area_Harvested", "98.1", "99.4", "101.4"],
        ["Chuối", "Yield", "157.7", "153.0", "97.0"],
        ["Chuối", "Production", "1547.2", "1520.9", "98.3"],
        ["Xoài", "Area_Planted", "86.1", "87.8", "102.0"],
        ["Xoài", "Area_Harvested", "66.6", "66.9", "100.5"],
        ["Xoài", "Yield", "81.4", "81.0", "99.6"],
        ["Xoài", "Production", "542.0", "542.6", "100.1"],
        ["Nhãn", "Area_Planted", "95.7", "93.3", "97.5"],
        ["Nhãn", "Area_Harvested", "85.3", "84.9", "99.5"],
        ["Nhãn", "Yield", "75.3", "72.4", "96.1"],
        ["Nhãn", "Production", "642.4", "614.5", "95.7"],
        ["Vải, chôm chôm", "Area_Planted", "108.5", "105.8", "97.5"],
        ["Vải, chôm chôm", "Area_Harvested", "100.3", "97.5", "97.2"],
        ["Vải, chôm chôm", "Yield", "68.4", "58.4", "85.4"],
        ["Vải, chôm chôm", "Production", "686.3", "569.6", "83.0"],
        ["Bòng bưởi", "Area_Planted", "43.6", "45.2", "103.7"],
        ["Bòng bưởi", "Area_Harvested", "31.8", "33.9", "106.8"],
        ["Bòng bưởi", "Yield", "114.1", "116.0", "101.6"],
        ["Bòng bưởi", "Production", "362.9", "393.7", "108.5"],
        ["Nho", "Area_Planted", "1.2", "1.2", "102.4"],
        ["Nho", "Area_Harvested", "1.2", "1.1", "94.9"],
        ["Nho", "Yield", "219.2", "216.0", "98.6"],
        ["Nho", "Production", "26.3", "24.6", "93.5"],
    ]
    for r in pl5_rows:
        item, attr, v08, v09, cp = r
        unit = "1000 ha" if "Area" in attr else ("tạ/ha" if "Yield" == attr else "1000 tấn")
        i_ctx = {"sector": "Cultivation", "commodity": item}
        t09 = {"year": 2009, "month": 12, "period_type": "Annual"}
        t08 = {"year": 2008, "month": 12, "period_type": "Annual"}
        comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "2008"}
        records.append(create_national_record(metadata5, t09, i_ctx, {"attribute": attr, "value": normalize_number(v09), "unit": unit, "data_type": "Actual"}, comp))
        records.append(create_national_record(metadata5, t08, i_ctx, {"attribute": attr, "value": normalize_number(v08), "unit": unit, "data_type": "Actual"}))

    # PL6 - Livestock (Inventory as of Oct 1)
    pl6_rows = [
        ["Trâu", "Inventory", "2897734", "2886602", "99.62", "Con"],
        ["Trâu", "Draft_Power", "1134770", "1080963", "95.26", "Con"],
        ["Trâu", "Meat_Production", "71543", "74960", "104.78", "Tấn"],
        ["Bò", "Inventory", "6337746", "6103322", "96.30", "Con"],
        ["Bò", "Draft_Power", "1213519", "1024351", "84.41", "Con"],
        ["Bò", "Meat_Production", "226696", "257779", "113.71", "Tấn"],
        ["Bò sữa", "Inventory", "107983", "115518", "106.98", "Con"],
        ["Sữa tươi", "Production", "262160", "278190", "106.11", "Tấn"],
        ["Lợn", "Inventory", "26701598", "27627729", "103.47", "Con"],
        ["Lợn nái", "Inventory", "3950192", "4169478", "105.55", "Con"],
        ["Lợn thịt", "HeadCount", "42914423", "45895379", "106.95", "Con"],
        ["Thịt lợn", "Production", "2806453", "2931420", "104.45", "Tấn"],
        ["Gia cầm", "Inventory", "248320.1", "280180.5", "112.83", "1000_con"],
        ["Gà", "Inventory", "176036", "199999.5", "113.61", "1000_con"],
        ["Thịt gia cầm", "Production", "448242", "502750", "112.16", "Tấn"],
        ["Trứng gia cầm", "Production", "4976875", "5419423", "108.89", "1000_eggs"],
    ]
    for r in pl6_rows:
        item, attr, v08, v09, cp, unit = r
        i_ctx = {"sector": "Livestock", "commodity": item}
        t09 = {"year": 2009, "month": 10, "day": 1, "period_type": "Point_In_Time"}
        t08 = {"year": 2008, "month": 10, "day": 1, "period_type": "Point_In_Time"}
        comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "2008"}
        records.append(create_national_record(metadata6, t09, i_ctx, {"attribute": attr, "value": normalize_number(v09), "unit": unit, "data_type": "Actual"}, comp))
        records.append(create_national_record(metadata6, t08, i_ctx, {"attribute": attr, "value": normalize_number(v08), "unit": unit, "data_type": "Actual"}))
        
    return {"metadata": metadata5, "records": records}


def parse_pl7_12():
    metadata = {"year": 2009, "month": 12, "appendix_number": "PL7", "source_file": "2009_12_Phuluc_T12_2009_PL7.md"}
    records = []
    # TT, Item, Unit, Plan, TH CK (2008), ƯTH 12T (2009)
    rows = [
        ["1", "Trồng rừng tập trung", "1000 ha", "227.3", "234.2", "208.6", "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000 ha", "60.0", "40.8", "47.8", "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000 ha", "167.3", "193.4", "160.8", "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000 ha", "149.7", "290.4", "251.2", "Other"],
        ["3", "Trồng cây nhân dân", "Tr.cây", "200", "183.7", "180.4", "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000 ha", "506", "657.1", "767.8", "Other"],
        ["5", "Khoán bảo vệ rừng", "1000 ha", "1524", "2136.9", "2535.2", "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000 m3", "4380", "3512.3", "3766.7", "Wood_Volume"],
    ]
    for r in rows:
        tt, item, unit, plan, v08, v09, attr = r
        i_ctx = {"sector": "Forestry", "commodity": item}
        t09 = {"year": 2009, "month": 12, "period_type": "Annual"}
        t08 = {"year": 2008, "month": 12, "period_type": "Annual"}
        
        val09 = normalize_number(v09)
        if val09:
            comp = {"comparison_type": "vs_Plan", "comparison_value": (val09/normalize_number(plan)*100) if plan else None, "comparison_unit": "percentage", "reference_period": "Annual_Plan"}
            records.append(create_national_record(metadata, t09, i_ctx, {"attribute": attr, "value": val09, "unit": unit, "data_type": "Actual"}, comp))
        
        val08 = normalize_number(v08)
        if val08:
            records.append(create_national_record(metadata, t08, i_ctx, {"attribute": attr, "value": val08, "unit": unit, "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/12"
    save_json(parse_pl4_12(), os.path.join(out_dir, "2009_12_Phuluc_T12_2009_PL4.json"))
    save_json(parse_pl5_pl6_12(), os.path.join(out_dir, "2009_12_Phuluc_T12_2009_PL5.json"))
    save_json(parse_pl7_12(), os.path.join(out_dir, "2009_12_Phuluc_T12_2009_PL7.json"))
    print("Successfully parsed PL4, PL5, PL6, PL7 for Dec 2009.")
