import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
    REGION_DATA = json.load(f)

def normalize_number(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if s == "" or s == "-" or s == "." or s == "," or s == "||" or s == "|": return None
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    # VN format handling
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        # Check if it's thousands or decimal
        parts = s.split(",")
        if len(parts) > 1 and len(parts[-1]) == 3: # 22,931
            # But in some cases 203,924 might be 203.924
            # Let's assume comma is decimal if there is only one and it looks like it
            # Agriculture data often uses dots for thousands and commas for decimals
            # In March reports, they use it mixedly.
            # I'll try to convert to float directly if it has one comma.
            # If float(s.replace(',','.')) is reasonable, use it.
            s = s.replace(",", ".")
        else:
            s = s.replace(",", ".")
    elif "." in s:
        # 1.098.554
        if s.count(".") > 1:
            s = s.replace(".", "")
        else:
            parts = s.split(".")
            if len(parts[1]) == 3: # 22.931
                s = s.replace(".", "")
            else:
                pass
                
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6b_2010_03_from_pl6a():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL6b", "source_file": "2010_03_PhuLuc_T03_2010_PL6a.md"}
    records = []
    # This is for Jan-Feb 2010 (2 months)
    t_ctx = {"year": 2010, "month": 2, "period_type": "Cumulative", "data_type": "Actual"}
    
    # Main Commodities and Markets
    data = [
        ["Cà phê", [
            ["ĐỨC", 35184, 54952], ["HOA KỲ", 27613, 43382], ["ITALIA", 27470, 43033], ["NHẬT BẢN", 11712, 19739]
        ]],
        ["Cao su", [
            ["TRUNG QUỐC", 52104, 68079], ["HÀN QUỐC", 4665, 5790], ["ĐÀI LOAN", 2789, 4082]
        ]],
        ["Gạo", [
            ["PHI LIP PIN", 381662, 206440], ["MALAIXIA", 54252, 23560], ["CUBA", 67925, 27335]
        ]]
    ]
    for cmd, countries in data:
        for country, l10, v10 in countries:
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Export_Volume", "value": l10/1000.0, "unit": "1000_ton", "data_type": "Actual"}))
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Export_Value", "value": v10/1000.0, "unit": "million_USD", "data_type": "Actual"}))
    return records

def parse_pl6c_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL6c", "source_file": "2010_03_PhuLuc_T03_2010_PL6c.md"}
    records = []
    t_ctx = {"year": 2010, "month": 2, "period_type": "Cumulative", "data_type": "Actual"}
    
    data = [
        ["Phân bón các loại", [
            ["TRUNG QUỐC", 257547, 82136], ["NGA", 97432, 24221], ["PHI LIP PIN", 53735, 19043]
        ]],
        ["Bông các loại", [
            ["ẤN ĐỘ", 16671, 26943], ["HOA KỲ", 14694, 23958]
        ]]
    ]
    for cmd, countries in data:
        for country, l10, v10 in countries:
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Import_Volume", "value": l10/1000.0, "unit": "1000_ton", "data_type": "Actual"}))
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Import_Value", "value": v10/1000.0, "unit": "million_USD", "data_type": "Actual"}))
    return records

def parse_pl7_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL7", "source_file": "2010_03_PhuLuc_T03_2010_PL7.md"}
    records = []
    # TT, Name, KH, 2T, Mar_Est, 3T_Est
    raw = [
        ["Vốn ngân sách giao đầu năm", 3186262, 343225, 154950, 498175],
        ["Đầu tư Thuỷ lợi", 1735000, 259400, 115000, 374400],
        ["Đầu tư Nông nghiệp", 415300, 28060, 11500, 39560],
        ["Đầu tư Lâm nghiệp", 260000, 15000, 9250, 24250],
        ["Đầu tư Thuỷ sản", 25000, 1100, 500, 1600],
        ["Khoa học - Công nghệ", 137800, 11840, 6500, 18340],
        ["Giáo dục - Đào tạo", 86900, 9200, 4500, 13700],
        ["Vốn trái phiếu Chính phủ", 4000000, 214636, 112500, 327136],
        ["Tổng vốn đầu tư : = A + B", 7186262, 557861, 267450, 825311],
    ]
    loc, gl = "Cả nước", "National"
    for r in raw:
        name, plan, v_2t, v_mar, v_3t = r
        t_plan = {"year": 2010, "month": 12, "period_type": "Annual", "data_type": "Plan"}
        t_2t = {"year": 2010, "month": 2, "period_type": "Cumulative", "data_type": "Actual"}
        t_mar = {"year": 2010, "month": 3, "period_type": "Monthly", "data_type": "Estimated"}
        t_3t = {"year": 2010, "month": 3, "period_type": "Cumulative", "data_type": "Estimated"}
        
        sector = "Investment"
        records.append(create_record(metadata, t_plan, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": float(plan), "unit": "million_VND", "data_type": "Plan"}))
        records.append(create_record(metadata, t_2t, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": float(v_2t), "unit": "million_VND", "data_type": "Actual"}))
        records.append(create_record(metadata, t_mar, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": float(v_mar), "unit": "million_VND", "data_type": "Estimated"}))
        records.append(create_record(metadata, t_3t, loc, gl, {"sector": sector, "commodity": name}, {"attribute": "Investment_Amount", "value": float(v_3t), "unit": "million_VND", "data_type": "Estimated"}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl6b_2010_03_from_pl6a()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL6b.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl6c_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL6c.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl7_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL7.json"))
    print("Successfully parsed PL6b, PL6c, PL7 for March 2010.")
