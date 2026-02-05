import json
import uuid
import os
import re

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
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "").replace("..", ".")
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    if "." in s and "," in s:
        if s.find(".") < s.find(","): s = s.replace(".", "").replace(",", ".")
        else: s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts[-1]) == 3: s = s.replace(",", "")
        else: s = s.replace(",", ".")
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
    
    try:
        return float(s)
    except: return None

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB. sông Hồng": "Đồng bằng sông Hồng", "Đồng bằng sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và miền núi phía Bắc": "Đông Bắc", "Trung du và miền núi": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Đông Nam Bộ": "Đông Nam Bộ", "Tây Nguyên": "Tây Nguyên",
        "Miền Bắc": "Miền Bắc", "Miền Nam": "Miền Nam", "Cả nước": "Cả nước", "Toàn quốc": "Cả nước",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP.Hồ Chí Minh": "Hồ Chí Minh", "TP. Hồ Chí Minh": "Hồ Chí Minh",
        "Bắc Kạn": "Bắc Kạn", "Bắc Cạn": "Bắc Kạn", "Bc Giang": "Bắc Giang", "Hà Nông": "Hà Nam",
        "Lâm Đng": "Lâm Đồng", "Vĩ h Lnong": "Vĩnh Long", "Trà Vinh*": "Trà Vinh", "An Giang *": "An Giang"
    }
    
    loc_clean = loc_name.strip()
    loc_clean = re.sub(r"^\d+\s", "", loc_clean)
    loc_clean = re.sub(r"^[IVX]+\s", "", loc_clean)
    loc_clean = loc_clean.replace("\n", "").replace("<br>", "").strip()
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
    else:
        geo_context["region_id"] = "COUNTRY"; geo_context["region_name_vn"] = norm_loc; geo_context["location_name"] = norm_loc
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_05_Phuluc_05_2012_PL6.md"
    metadata = {"year": 2012, "month": 5, "appendix_number": "PL6"}
    records = []
    t_5m = {"year": 2012, "month": 5, "period_type": "Cumulative", "report_date": "2012-05-31"}
    if not os.path.exists(fpath): return []
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in f:
            if "|" in line:
                row = [p.strip() for p in line.split("|")]
                if len(row) > 2 and row[0] == "" and row[-1] == "": row = row[1:-1]
                if len(row) < 5: continue
                name = row[1].replace("**", "").replace("_", "").strip()
                if "Chỉ tiêu" in name or name == "": continue
                val = normalize_number(row[4])
                unit = row[2].strip()
                if val: records.append(create_record(metadata, t_5m, "Cả nước", "National", {"sector": "Forestry", "commodity": name}, {"attribute": "Value", "value": val, "unit": unit, "data_type": "Estimate"}))
    return records

def parse_pl7():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_05_Phuluc_05_2012_PL7.md"
    metadata = {"year": 2012, "month": 5, "appendix_number": "PL7"}
    records = []
    t_5m = {"year": 2012, "month": 5, "period_type": "Cumulative", "report_date": "2012-05-31"}
    if not os.path.exists(fpath): return []
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in f:
            if "|" in line:
                row = [p.strip() for p in line.split("|")]
                if len(row) > 2 and row[0] == "" and row[-1] == "": row = row[1:-1]
                if len(row) < 4: continue
                name = row[1].replace("**", "").replace("n", "").strip()
                if "Tỉh/TP" in name or "Tỉnh/TP" in name or "Cả nước" in name or "Miền" in name or "ĐB" in name or name == "" or "TT" in row[0]:
                    gl = "Regional"
                    if "Cả nước" in name: gl = "National"
                else: gl = "Provincial"
                v_total = normalize_number(row[2])
                v_care = normalize_number(row[5]) if len(row) > 5 else None
                if v_total: records.append(create_record(metadata, t_5m, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng mới tập trung"}, {"attribute": "Area", "value": v_total, "unit": "ha", "data_type": "Actual"}))
                if v_care: records.append(create_record(metadata, t_5m, name, gl, {"sector": "Forestry", "commodity": "Diện tích rừng trồng được chăm sóc"}, {"attribute": "Area", "value": v_care, "unit": "ha", "data_type": "Actual"}))
    return records

def parse_pl8_9_10():
    fpath = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2012/2012_05_Phuluc_05_2012_PL8.md"
    if not os.path.exists(fpath): return []
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    records = []
    current_appendix = "PL8"
    t_m = {"year": 2012, "month": 5, "period_type": "Monthly", "report_date": "2012-05-31"}
    t_5m = {"year": 2012, "month": 5, "period_type": "Cumulative", "report_date": "2012-05-31"}
    
    for line in lines:
        # Appendix detection (out of table)
        if "Phụ lục 9" in line: current_appendix = "PL9"; continue
        if "Phụ lục 10" in line: current_appendix = "PL10"; continue
        
        if "|" in line:
            row = [p.strip() for p in line.split("|")]
            if len(row) > 2 and row[0] == "" and row[-1] == "": row = row[1:-1]
            if len(row) < 2: continue
            
            if current_appendix == "PL8":
                name = row[1].replace("**", "").replace("_", "").strip()
                if "Tổng sản lượng" in name:
                    vm = normalize_number(row[5]); v5 = normalize_number(row[6])
                    if vm: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL8"}, t_m, "Cả nước", "National", {"sector": "Fishery", "commodity": "Tổng sản lượng"}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"}))
                    if v5: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL8"}, t_5m, "Cả nước", "National", {"sector": "Fishery", "commodity": "Tổng sản lượng"}, {"attribute": "Production", "value": v5, "unit": "1000_ton", "data_type": "Estimate"}))
                elif "Sản lượng khai thác" in name or "Sản lượng nuôi trồng" in name:
                    vm = normalize_number(row[5]); v5 = normalize_number(row[6])
                    if vm: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL8"}, t_m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": vm, "unit": "1000_ton", "data_type": "Estimate"}))
                    if v5: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL8"}, t_5m, "Cả nước", "National", {"sector": "Fishery", "commodity": name}, {"attribute": "Production", "value": v5, "unit": "1000_ton", "data_type": "Estimate"}))

            elif current_appendix == "PL9":
                name = row[0].replace("**", "").replace("_", "").strip()
                if "Tỉnh/TP" in name or "Miền" in name or name == "" or name.isdigit():
                    if len(row) > 1 and not row[1].replace(".", "").isdigit(): name = row[1]
                    else: continue
                if "Miền Bắc" in name or "Miền Nam" in name: continue
                v_prod = normalize_number(row[1])
                v_nuoi = normalize_number(row[2])
                v_khai = normalize_number(row[5])
                if v_prod: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL9"}, t_m, name, "Provincial", {"sector": "Fishery", "commodity": "Tổng sản lượng"}, {"attribute": "Production", "value": v_prod, "unit": "ton", "data_type": "Actual"}))
                if v_nuoi: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL9"}, t_m, name, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng nuôi trồng"}, {"attribute": "Production", "value": v_nuoi, "unit": "ton", "data_type": "Actual"}))
                if v_khai: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL9"}, t_m, name, "Provincial", {"sector": "Fishery", "commodity": "Sản lượng khai thác"}, {"attribute": "Production", "value": v_khai, "unit": "ton", "data_type": "Actual"}))

            elif current_appendix == "PL10":
                if len(row) < 10: continue
                name = row[1].replace("**", "").replace("_", "").replace("<br>", " ").replace("~~", "").strip()
                if "Danh mục" in name or "TỔNG CỘNG" in name or "TT" in row[0]: continue
                v4 = normalize_number(row[5]); v5 = normalize_number(row[8])
                t_4m = {"year": 2012, "month": 4, "period_type": "Cumulative", "report_date": "2012-04-30"}
                if v4: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL10"}, t_4m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v4, "unit": "million_VND", "data_type": "Actual"}))
                if v5: records.append(create_record({"year": 2012, "month": 5, "appendix_number": "PL10"}, t_5m, "Cả nước", "National", {"sector": "Investment", "commodity": name}, {"attribute": "Investment_Amount", "value": v5, "unit": "million_VND", "data_type": "Estimate"}))
    return records

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2012/05"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2012, "month": 5}, "records": parse_pl6()}, os.path.join(out_dir, "2012_05_Phuluc_05_2012_PL6.json"))
    save_json({"metadata": {"year": 2012, "month": 5}, "records": parse_pl7()}, os.path.join(out_dir, "2012_05_Phuluc_05_2012_PL7.json"))
    save_json({"metadata": {"year": 2012, "month": 5}, "records": parse_pl8_9_10()}, os.path.join(out_dir, "2012_05_Phuluc_05_2012_PL8_9_10.json"))
    
    print("Successfully parsed Batch 2 (Corrected) for May 2012.")
