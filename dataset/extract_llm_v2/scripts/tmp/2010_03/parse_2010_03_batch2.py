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
    
    # Handle numbers with <br>
    if "<br>" in s: s = s.split("<br>")[0].strip()
    
    # Unified normalization for VN format: 1.234,5 or 1234,5
    # Step 1: If there's a dot and a comma, replace dot with nothing, then comma with dot.
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    # Step 2: If there's only a comma, check if it's thousands or decimal.
    elif "," in s:
        # In these reports, if comma exists without dot, it's usually a decimal.
        # Example: 16,8 or 206,7.
        # But if it's 1,234,567...
        if s.count(",") > 1:
            s = s.replace(",", "")
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: # Maybe 1,234 ? 
                # But in agriculture, 1,234 ha is often 1.234 ha in VN.
                # Let's assume comma is decimal for small values or if it makes sense.
                # Actually, 1,730,0 in the MD suggests comma is decimal.
                s = s.replace(",", ".")
            else:
                s = s.replace(",", ".")
    # Step 3: dots only
    elif "." in s:
        if s.count(".") > 1: # 1.098.554
            s = s.replace(".", "")
        else:
            # Check context or pattern. 3 digits after dot -> likely thousands.
            parts = s.split(".")
            if len(parts[1]) == 3:
                s = s.replace(".", "")
            else:
                pass # Keep as decimal dot
                
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

def parse_pl4_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL4", "source_file": "2010_03_PhuLuc_T03_2010_PL4.md"}
    records = []
    # TT, Name, Unit, Plan, CK, Est_3M, %_CK, %_KH, Attr
    raw = [
        ["1", "Trồng rừng tập trung", "1000 ha", "206,7", "16,8", "15,5", "92,3", "7,5", "Forest_Area_Planted"],
        ["1.1", "Rừng phòng hộ, đặc dụng", "1000 ha", "64,8", "2,7", "2,3", "85,2", "3,6", "Forest_Area_Planted"],
        ["1.2", "Rừng sản xuất", "1000 ha", "141,9", "14,1", "13,2", "93,6", "9,3", "Forest_Area_Planted"],
        ["2", "Chăm sóc rừng trồng", "1000 ha", "149,7", "72,0", "72,5", "100,7", "48,4", "Other"],
        ["3", "Trồng cây phân tán", "Tr.cây", "200", "59,2", "59,7", "100,8", "29,9", "Other"],
        ["4", "Khoanh nuôi tái sinh, trồng dặm", "1000 ha", "668,8", "609,0", "605,0", "99,3", "90,5", "Other"],
        ["5", "Khoán bảo vệ rừng", "1000 ha", "1.506", "1.730,0", "1.720", "99,4", "114,2", "Forest_Area_Protected"],
        ["6", "Khai thác gỗ", "1000 m3", "4.700", "494,0", "761,0", "154,0", "16,2", "Wood_Volume"],
    ]
    t10 = {"year": 2010, "month": 3, "period_type": "Cumulative", "data_type": "Estimated"}
    t09 = {"year": 2009, "month": 3, "period_type": "Cumulative", "data_type": "Actual"}
    t_plan = {"year": 2010, "month": 12, "period_type": "Annual", "data_type": "Plan"}
    
    for r in raw:
        name, unit, plan, v09, v10, c_ck, c_kh, attr = r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]
        loc, gl = "Cả nước", "National"
        metadata_copy = metadata.copy()
        records.append(create_record(metadata_copy, t10, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": normalize_number(v10), "unit": unit.replace(" ", "_"), "data_type": "Estimated"}))
        records.append(create_record(metadata_copy, t09, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": normalize_number(v09), "unit": unit.replace(" ", "_"), "data_type": "Actual"}))
        records.append(create_record(metadata_copy, t_plan, loc, gl, {"sector": "Forestry", "commodity": name}, {"attribute": attr, "value": normalize_number(plan), "unit": unit.replace(" ", "_"), "data_type": "Plan"}))
    return records

def parse_pl5_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL5", "source_file": "2010_03_PhuLuc_T03_2010_PL5.md"}
    records = []
    # Chỉ tiêu, ĐVT, KH, 2M, 3M_Est, 3M_CK
    raw = [
        ["Tổng sản lượng", "1000 Tấn", 5050, 757, 340, 1097, 1028, "Production", None],
        ["Sản lượng khai thác", "1000 Tấn", 2400, 410, 210, 620, 613, "Production", "Khai thác"],
        ["Khai thác biển", "1000 Tấn", 2180, 390, 200, 590, 568, "Production", "Khai thác biển"],
        ["Khai thác nội địa", "1000 Tấn", 220, 20, 10, 30, 45, "Production", "Khai thác nội địa"],
        ["Sản lượng nuôi trồng", "1000 Tấn", 2650, 347, 130, 477, 415, "Production", "Nuôi trồng"],
    ]
    loc, gl = "Cả nước", "National"
    for r in raw:
        name, unit, plan, v_2m, v_mar, v_3m, v_3m_09, attr, sub = r
        t_plan = {"year": 2010, "month": 12, "period_type": "Annual", "data_type": "Plan"}
        t_mar = {"year": 2010, "month": 3, "period_type": "Monthly", "data_type": "Estimated"}
        t_3m = {"year": 2010, "month": 3, "period_type": "Cumulative", "data_type": "Estimated"}
        t_3m_09 = {"year": 2009, "month": 3, "period_type": "Cumulative", "data_type": "Actual"}
        
        sector = "Fishery"
        records.append(create_record(metadata, t_plan, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": float(plan), "unit": "1000_ton", "data_type": "Plan"}))
        records.append(create_record(metadata, t_mar, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": float(v_mar), "unit": "1000_ton", "data_type": "Estimated"}))
        records.append(create_record(metadata, t_3m, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": float(v_3m), "unit": "1000_ton", "data_type": "Estimated"}))
        records.append(create_record(metadata, t_3m_09, loc, gl, {"sector": sector, "commodity": name, "sub_item": sub}, {"attribute": attr, "value": float(v_3m_09), "unit": "1000_ton", "data_type": "Actual"}))
    return records

def parse_pl6a_2010_03():
    metadata = {"year": 2010, "month": 3, "appendix_number": "PL6a", "source_file": "2010_03_PhuLuc_T03_2010_PL6a.md"}
    records = []
    # Name, L_Feb, V_Feb, L_2M, V_2M, L_Mar_Est, V_Mar_Est, L_3M_Est, V_3M_Est
    xk_data = [
        ["Tổng kim ngạch XK", None, 975, None, 2386, None, 1100, None, 3486],
        ["Nông sản chính", None, 515, None, 1278, None, 631, None, 1909],
        ["Cà phê", 77, 110, 220, 312, 106, 154, 326, 466],
        ["Cao su", 22, 56, 76, 193, 32, 58, 108, 251],
        ["Gạo", 353, 205, 733, 410, 450, 240, 1183, 650],
        ["Chè", 7, 9, 17, 24, 7, 9, 24, 33],
        ["Hạt điều", 7, 36, 20, 107, 8, 41, 28, 148],
        ["Hạt tiêu", 6, 20, 14, 43, 9, 23, 23, 66],
        ["Hàng rau quả", None, 32, None, 74, None, 33, None, 107],
        ["Sắn và sản phẩm từ sắn", 186, 47, 439, 115, 430, 73, None, 188],
        ["Thuỷ sản", None, 228, None, 541, None, 230, None, 771],
        ["Lâm sản chính", None, 184, None, 501, None, 205, None, 706],
        ["Quế", None, 1, None, 3, 3, 3, None, 5],
        ["Gỗ & sản phẩm gỗ", None, 172, None, 466, None, 189, None, 655],
        ["SP mây, tre, cói, thảm", None, 12, None, 32, None, 14, None, 46],
        ["Các mặt hàng nông lâm sản khác", None, 47, None, 67, None, 34, None, 101],
    ]
    # NK data
    nk_data = [
        ["Tổng kim ngạch NK", None, 860, None, 1884, None, 830, None, 2714],
        ["Phân bón các loại", 243, 85, 748, 231, 380, 122, 1128, 353],
        ["Thuốc trừ sâu & nguyên liệu", None, 39, None, 95, None, 40, None, 135],
        ["Lúa mỳ", 94, 23, 243, 58, 124, 30, 367, 88],
        ["Thức ăn gia súc và nguyên liệu", None, 192, None, 353, None, 160, None, 513],
        ["Dầu mỡ động, thực vật", None, 30, None, 86, None, 36, None, 122],
        ["Cao su", 19, 38, 46, 83, 20, 33, 66, 116],
        ["Bông các loại", 24, 39, 57, 90, 17, 26, 74, 116],
        ["Sữa & sản phẩm sữa", None, 41, None, 105, None, 44, None, 149],
        ["Gỗ & sản phẩm gỗ", None, 47, None, 135, None, 50, None, 185],
    ]

    periods = [
        ("Feb 2010 Actual", {"year": 2010, "month": 2, "period_type": "Monthly", "data_type": "Actual"}, 1, 2),
        ("2M 2010 Actual", {"year": 2010, "month": 2, "period_type": "Cumulative", "data_type": "Actual"}, 3, 4),
        ("Mar 2010 Est", {"year": 2010, "month": 3, "period_type": "Monthly", "data_type": "Estimated"}, 5, 6),
        ("3M 2010 Est", {"year": 2010, "month": 3, "period_type": "Cumulative", "data_type": "Estimated"}, 7, 8),
    ]

    for list_data, trade_type in [(xk_data, "Export"), (nk_data, "Import")]:
        for row in list_data:
            name = row[0]
            for p_name, t_ctx, l_idx, v_idx in periods:
                if l_idx < len(row):
                    l_val = normalize_number(row[l_idx])
                    if l_val is not None: records.append(create_record(metadata, t_ctx, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": f"{trade_type}_Volume", "value": l_val, "unit": "1000_ton", "data_type": t_ctx["data_type"]}))
                if v_idx < len(row):
                    v_val = normalize_number(row[v_idx])
                    if v_val is not None: records.append(create_record(metadata, t_ctx, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": f"{trade_type}_Value", "value": v_val, "unit": "million_USD", "data_type": t_ctx["data_type"]}))
    return records


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/03"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl4_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl5_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL5.json"))
    save_json({"metadata": {"year": 2010, "month": 3}, "records": parse_pl6a_2010_03()}, os.path.join(out_dir, "2010_03_PhuLuc_T03_2010_PL6a.json"))
    print("Successfully parsed PL4, PL5, PL6a for March 2010.")
