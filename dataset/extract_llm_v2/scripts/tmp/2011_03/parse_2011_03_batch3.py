import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
try:
    with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
        REGION_DATA = json.load(f)
except:
    REGION_DATA = {"provinces": {}, "regions": {}}

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): # 1.234,5
            s = s.replace(".", "").replace(",", ".")
        else: # 1,234.5
            s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "") # Thousands
            else: s = s.replace(",", ".") # Decimal
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
        else:
            parts = s.split(".")
            if len(parts[1]) == 3: s = s.replace(".", "")
            else: pass
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Cả nước": "Cả nước", "Đà Nẵng": "Đà Nẵng", "Đà Nẵ\nng": "Đà Nẵng",
        "Tiền Giang": "Tiền Giang", "Kiên Giang": "Kiên Giang", 
        "Ni h Th ậ\nnun": "Ninh Thuận", "Bà Rịa - Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "TP.Hồ Chí Minh": "Hồ Chí Minh"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.strip()
    norm_loc = alias_map.get(loc_clean, loc_clean)
    
    if norm_loc in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][norm_loc]["region_id"]
        geo_context["region_name_vn"] = REGION_DATA["provinces"][norm_loc]["region_name"]
        geo_context["location_name"] = norm_loc
    elif norm_loc in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][norm_loc]
        geo_context["region_name_vn"] = norm_loc
        geo_context["location_name"] = norm_loc
    elif norm_loc == "Cả nước":
        geo_context["region_id"] = "NATIONAL"; geo_context["region_name_vn"] = "Cả nước"
    elif norm_loc == "Miền Nam":
        geo_context["region_id"] = "SOUTH"; geo_context["region_name_vn"] = "Miền Nam"
    elif norm_loc == "Miền Bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6():
    # Forestry
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL6", "source_file": "2011_03_Phuluc_03_2011_PL6.md"}
    records = []
    
    t_3m_11 = {"year": 2011, "month": 3, "period_type": "Cumulative", "report_date": "2011-03-31"}
    t_3m_last = {"year": 2010, "month": 3, "period_type": "Cumulative", "report_date": "2010-03-31"} # Comparsion to same period last year
    
    # Item structure: [Item Name, Unit, Last Year, This Year (Est)]
    
    data = [
        ("Trồng rừng tập trung", "1000 ha", 15.5, 11.8), # Item 1
        ("Rừng phòng hộ, đặc dụng", "1000 ha", 2.3, 1.2),
        ("Rừng sản xuất", "1000 ha", 13.2, 10.5),
        ("Chăm sóc rừng trồng", "1000 ha", 72.5, 87.4),
        ("Trồng cây phân tán", "Million_Trees", 59.7, 60.3), # Tr.cay
        ("Khoanh nuôi tái sinh", "1000 ha", 605, 607.0),
        ("Khoán bảo vệ rừng", "1000 ha", 1720, 1755.0),
        ("Khai thác gỗ", "1000 m3", 761, 956.5)
    ]
    
    for row in data:
        item = row[0]
        unit_raw = row[1]
        val_last = row[2]
        val_curr = row[3]
        
        unit = "1000_ha"
        if unit_raw == "Million_Trees": unit = "million_trees"
        elif unit_raw == "1000 m3": unit = "1000_m3"
        
        records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Output", "value": float(val_curr), "unit": unit, "data_type": "Estimate"}))
        records.append(create_record({"year": 2010, "month": 3, "appendix_number": "PL6", "source_file": "2011_03_Phuluc_03_2011_PL6.md"}, t_3m_last, "Cả nước", "National", {"sector": "Forestry", "commodity": item}, {"attribute": "Output", "value": float(val_last), "unit": unit, "data_type": "Actual"}))

    return records

def parse_pl7():
    # Fishery Summary
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL7", "source_file": "2011_03_Phuluc_03_2011_PL7.md"}
    records = []
    
    # [Item, Est Mar 11, Est 3M 11, Act 3M 10]
    # Unit 1000 ton
    data = [
        ("Tổng sản lượng", 308, 1098.4, 1067),
        ("Sản lượng khai thác", 159, 601.4, 590),
        ("Khai thác biển", 138.9, 560.9, 560),
        ("Khai thác nội địa", 20.1, 40.5, 30),
        ("Sản lượng nuôi trồng", 149, 497, 477)
    ]
    
    t_mar_11 = {"year": 2011, "month": 3, "period_type": "Monthly", "report_date": "2011-03-31"}
    t_3m_11 = {"year": 2011, "month": 3, "period_type": "Cumulative", "report_date": "2011-03-31"}
    t_3m_10 = {"year": 2010, "month": 3, "period_type": "Cumulative", "report_date": "2010-03-31"}
    
    for row in data:
        item = row[0]
        # Mar 11
        if row[1] is not None: records.append(create_record(metadata, t_mar_11, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[1]), "unit": "1000_ton", "data_type": "Estimate"}))
        # 3M 11
        if row[2] is not None: records.append(create_record(metadata, t_3m_11, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[2]), "unit": "1000_ton", "data_type": "Estimate"}))
        # 3M 10
        if row[3] is not None: records.append(create_record({"year": 2010, "month": 3, "appendix_number": "PL7", "source_file": "2011_03_Phuluc_03_2011_PL7.md"}, t_3m_10, "Cả nước", "National", {"sector": "Fishery", "commodity": item}, {"attribute": "Production", "value": float(row[3]), "unit": "1000_ton", "data_type": "Actual"}))

    return records

def parse_pl8():
    # Detailed Fishery by Province (PL8)
    metadata = {"year": 2011, "month": 3, "appendix_number": "PL8", "source_file": "2011_03_Phuluc_03_2011_PL8.md"}
    records = []
    t = {"year": 2011, "month": 3, "period_type": "Cumulative", "report_date": "2011-03-31"} # Likely cumulative 3 months based on PL7 context and values
    
    # [Province, Total, Nuoi Trong - Total, Nuoi Trong - Ngọt, Nuoi Trong - Man/Lo, Khai Thac - Total, KT Bien, KT Noi Dia]
    # Unit: Ton -> convert to 1000_ton or keep ton? Summary is 1000 ton. Provinces are Ton.
    # I will convert to 1000_ton for consistency.
    
    data = [
        ["Quảng Ninh", 16357, 5427, 886, 4541, 10930, 10589, 341],
        ["Hải Phòng", 18700, 9440, None, 9440, 9260, 8960, 300],
        ["Thái Bình", 15400, 7500, 4500, 3000, 7900, 7500, 400],
        ["Nam Định", 13156, 7886, 4874, 3012, 5270, 4961, 309],
        ["Ninh Bình", 6208, 4808, 4558, 250, 1400, 1400, None],
        ["Thanh Hoá", 31099, 7079, 5249, 1830, 24020, 23069, 951],
        ["Nghệ An", 20942, 6869, 6335, 534, 14073, 12901, 1172],
        ["Hà Tĩnh", 3455, 185, 60, 125, 3270, 3130, 140],
        ["Quảng Bình", 4662, 0, None, None, 4662, 4325, 337],
        ["Quảng Trị", 3675, 375, None, 375, 3300, 3000, 300],
        ["Thừa Thiên Huế", 6193, 60, 24, 36, 6133, 5398, 735],
        ["Đà Nẵ\nng", 9590, 90, 90, None, 9500, 9500, None],
        ["Quảng Nam", 10900, 0, None, None, 10900, 10800, 100],
        ["Quảng Ngãi", 19117, 530, 150, 380, 18587, 18465, 122],
        ["Bình Định", 33000, 0, None, None, 33000, 33000, None],
        ["Phú Yên", 11786, 36, 25, 11, 11750, 11750, None],
        ["Khánh Hoà", 22580, 4680, None, 4680, 17900, 17800, 100],
        ["Ni h Th ậ\nnun", 11943, 643, 65, 578, 11300, 11255, 45],
        ["Bình Thuận", 30796, 4156, 2202, 1954, 26640, 26340, 300],
        ["Tây Ninh", 2550, 1500, 1500, None, 1050, None, 1050],
        ["Bà Rịa - Vũng Tàu", 60981, 2395, 187, 2208, 58586, 58586, None],
        ["TP.Hồ Chí Minh", 10232, 5087, 2365, 2722, 5145, 5145, None],
        ["Long An", 5598, 98, None, 98, 5500, 3000, 2500],
        ["Tiền Giang", 48861, 28162, 20502, 7660, 20699, 19896, 803],
        ["Bến Tre", 54850, 29850, 26100, 3750, 25000, 25000, None],
        ["Trà Vinh", 22412, 6627, 3036, 3591, 15785, 13397, 2388],
        ["Vĩnh Long", 22497, 20447, 20447, None, 2050, None, 2050],
        ["Đồng Tháp", 96411, 95181, 95181, None, 1230, None, 1230],
        ["An Giang", 100000, 90000, 90000, None, 10000, None, 10000],
        ["Kiên Giang", 101783, 16275, 16275, None, 85508, 84708, 800],
        ["Cần Thơ", 16417, 15717, 15717, None, 700, None, 700],
        ["Hậu Giang", 8500, 8000, 8000, None, 500, None, 500],
        ["Sóc Trăng", 10850, 502, 500, 2, 10348, 8938, 1410],
        ["Bạc Liêu", 42321, 21115, None, 21115, 21206, 20010, 1196],
        ["Cà Mau", 98500, 56500, 5204, 51296, 42000, 42000, None]
    ]
    
    for row in data:
        loc = row[0]
        # Total
        if row[1] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Tổng sản lượng"}, {"attribute": "Production", "value": float(row[1])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        # Aquaculture
        if row[2] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng", "sub_item": "Tổng số"}, {"attribute": "Production", "value": float(row[2])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[3] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng", "sub_item": "Nước ngọt"}, {"attribute": "Production", "value": float(row[3])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[4] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng", "sub_item": "Nước mặn, lợ"}, {"attribute": "Production", "value": float(row[4])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        # Catching
        if row[5] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác", "sub_item": "Tổng số"}, {"attribute": "Production", "value": float(row[5])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[6] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác", "sub_item": "Khai thác biển"}, {"attribute": "Production", "value": float(row[6])/1000, "unit": "1000_ton", "data_type": "Estimate"}))
        if row[7] is not None: records.append(create_record(metadata, t, loc, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác", "sub_item": "Khai thác nội địa"}, {"attribute": "Production", "value": float(row[7])/1000, "unit": "1000_ton", "data_type": "Estimate"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl6()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL6.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl7()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL7.json"))
    save_json({"metadata": {"year": 2011, "month": 3}, "records": parse_pl8()}, os.path.join(out_dir, "2011_03_Phuluc_03_2011_PL8.json"))
    # PL9 Skipped (Sugar Factories)
    print("Successfully parsed PL6, PL7, PL8 for March 2011 (Forestry & Fishery). PL9 skipped.")
