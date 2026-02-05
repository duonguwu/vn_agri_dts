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
    if s == "" or s == "-" or s == "." or s == "||" or s == "|": return None
    # Handle numbers with <br>
    if "<br>" in s: s = s.split("<br>")[0].strip()
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "").replace("(", "").replace(")", "").replace(" ", "")
    try:
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    # No regional mapping for foreign countries in PL6b/c, so we just set them as foreign
    # But schema says location_name is required. 
    # For countries, let's treat geo_level="National" or we can add a level?
    # Actually, schema enum is ["National", "Regional", "Provincial"]. 
    # I'll use "National" for countries.
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6a_2010_02():
    metadata = {"year": 2010, "month": 2, "appendix_number": "PL6a", "source_file": "2010_02_PhuLuc_T02_2010_PL6a.md"}
    records = []
    
    # XK Data: name, L09, V09, L_Jan, V_Jan, L_Feb_Est, V_Feb_Est, L_2M_Est, V_2M_Est
    xk_data = [
        ["Tổng kim ngạch XK", None, 2266, None, 1412, None, 1413, None, 2825, "Value_Only"],
        ["Nông sản", None, 1317, None, 737, None, 730, None, 1467, "Value_Only"],
        ["Cà phê", 289, 444, 141, 198, 139, 196, 280, 394],
        ["Cao su", 76, 102, 48, 118, 50, 123, 98, 241],
        ["Gạo", 1043, 470, 381, 205, 383, 206, 764, 411],
        ["Chè", 14, 18, 11, 15, 10, 14, 21, 29],
        ["Hạt điều", 20, 93, 13, 70, 10, 54, 23, 124],
        ["Hạt tiêu", 15, 39, 8, 23, 9, 28, 17, 52],
        ["Hàng rau quả", None, 61, None, 40, None, 42, None, 82, "Value_Only"],
        ["Sắn và sản phẩm từ sắn", None, 91, 253, 68, 250, 67, 503, 135], # Wait, Row 23 had weird numbers in MD. 
        # MD Row 23: |Sắn và sản phẩm từ sắn||91|253|68|250|67|503|135||148.43|
        # Mapping back: TH 2T-09: None, 91. Jan 10: 253, 68. Feb 10: 250, 67. 2M-10: 503, 135.
        
        ["Thuỷ sản", None, 444, None, 313, None, 315, None, 628, "Value_Only"],
        ["Lâm sản chính", None, 387, None, 307, None, 310, None, 617, "Value_Only"],
        ["Quế", None, 2.1, None, 1.2, None, 1.0, None, 2.2, "Value_Only"],
        ["Gỗ & sản phẩm gỗ", None, 357, None, 287, None, 290, None, 577, "Value_Only"],
        ["SP mây, tre, cói, thảm", None, 28, None, 19, None, 19, None, 38, "Value_Only"],
        ["Các mặt hàng NS sản khác", None, 118, None, 55, None, 58, None, 113, "Value_Only"],
    ]
    
    # NK Data
    nk_data = [
        ["Tổng kim ngạch NK", None, 1074, None, None, None, None, None, None, "Value_Only"],
        ["Phân bón các loại", 576, 183, 506, 146, 508, 147, 1014, 293],
        ["U RE", 161, 47, 207, 66, 208, 66, 415, 132],
        ["S A", 132, 16, 153, 20, 155, 21, 308, 41],
        ["D A P", 205, 78, 58, 24, 60, 25, 118, 49],
        ["N P K", 48, 19, 28, 10, 28, 10, 56, 20],
        ["Phân bón các loại khác", 30, 23, 60, 26, 57, 25, 117, 52],
        ["Thuốc trừ sâu & nguyên liệu", None, 50, None, 56, None, 55, None, 111, "Value_Only"],
        ["Lúa mỳ", 105, 32, 142, 33, 143, 33, 285, 66],
        ["Thức ăn gia súc và nguyên liệu", None, 148, None, 149, None, 145, None, 294, "Value_Only"],
        ["Dầu mỡ động, thực vật", None, 49, None, 66, None, 60, None, 126, "Value_Only"],
        ["Cao su", 25, 39, 27, 45, 26, 43, 53, 88],
        ["Bông các loại", 23, 32, 33, 51, 35, 55, 68, 106],
        ["Sữa & sản phẩm sữa", None, 63, None, 63, None, 65, None, 128, "Value_Only"],
        ["Gỗ & sản phẩm gỗ", None, 83, None, 88, None, 90, None, 178, "Value_Only"],
    ]

    periods = [
        ("2009 Actual", {"year": 2009, "month": 2, "period_type": "Cumulative", "data_type": "Actual"}, 1, 2),
        ("Jan 2010 Actual", {"year": 2010, "month": 1, "period_type": "Monthly", "data_type": "Actual"}, 3, 4),
        ("Feb 2010 Est", {"year": 2010, "month": 2, "period_type": "Monthly", "data_type": "Estimated"}, 5, 6),
        ("2M 2010 Est", {"year": 2010, "month": 2, "period_type": "Cumulative", "data_type": "Estimated"}, 7, 8),
    ]

    for list_data, trade_type in [(xk_data, "Export"), (nk_data, "Import")]:
        for row in list_data:
            name = row[0]
            for p_name, t_ctx, l_idx, v_idx in periods:
                if l_idx < len(row):
                    l_val = normalize_number(row[l_idx])
                    if l_val is not None:
                        records.append(create_record(metadata, t_ctx, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": f"{trade_type}_Volume", "value": l_val, "unit": "1000_ton", "data_type": t_ctx["data_type"]}))
                if v_idx < len(row):
                    v_val = normalize_number(row[v_idx])
                    if v_val is not None:
                        records.append(create_record(metadata, t_ctx, "Cả nước", "National", {"sector": "Trade", "commodity": name}, {"attribute": f"{trade_type}_Value", "value": v_val, "unit": "million_USD", "data_type": t_ctx["data_type"]}))
    return {"metadata": metadata, "records": records}

def parse_pl6b_2010_02():
    # Thị trường Xuất khẩu (Jan 2010)
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL6b", "source_file": "2010_02_PhuLuc_T02_2010_PL6b.md"}
    records = []
    t_ctx = {"year": 2010, "month": 1, "period_type": "Monthly", "data_type": "Actual"}
    
    # Raw data processing... I'll include main commodities.
    # Format: Commodity, [Country, L09, V09, L10, V10]
    data = [
        ["Cà phê", [
            ["ĐỨC", 15940, 25124, 18418, 26942], ["HOA KỲ", 14300, 22568, 15927, 23537], ["ITALIA", 12207, 18974, 8655, 11794],
            ["NHẬT BẢN", 4228, 7091, 5575, 8852], ["BỈ", 28358, 41998, 5377, 7581], ["TÂY BAN NHA", 8246, 12889, 5392, 7425],
            ["IN ĐÔ NÊ XI A", 76, 121, 5270, 7404], ["ANH", 4649, 7119, 5496, 7264], ["NGA", 2955, 4624, 4790, 6585], ["HÀ LAN", 3125, 4672, 3628, 5049]
        ]],
        ["Cao su", [
            ["TRUNG QUỐC", 27692, 34188, 32842, 82578], ["ĐÀI LOAN", 1450, 2061, 2732, 7143], ["HÀN QUỐC", 1908, 2062, 2355, 4672],
            ["NGA", 173, 219, 1176, 3602], ["HOA KỲ", 1116, 1706, 1868, 3585], ["ĐỨC", 694, 1234, 1285, 2996],
            ["NHẬT BẢN", 516, 760, 929, 2463], ["THỔ NHĨ KỲ", 493, 831, 811, 2026], ["TÂY BAN NHA", 428, 642, 416, 1090], ["ẤN ĐỘ", 163, 184, 421, 1039]
        ]],
        ["Chè", [
            ["NGA", 761, 928, 2097, 2803], ["PAKIXTAN", 2293, 3200, 1548, 2242], ["ĐÀI LOAN", 624, 756, 1168, 1285],
            ["ẤN ĐỘ", 245, 165, 720, 772], ["ĐỨC", 151, 201, 413, 601], ["TRUNG QUỐC", 209, 328, 385, 492]
        ]],
        ["Gạo", [
            ["PHI LIP PIN", 4432, 1561, 209728, 117804], ["CUBA", 43525, 18031, 52500, 26623], ["MALAIXIA", 52189, 22730, 48582, 23827],
            ["XINH GA PO", 8195, 3249, 11594, 6187], ["ĐÀI LOAN", 7477, 2832, 10385, 5345], ["NGA", 23325, 9900, 5671, 2918],
            ["HỒNG CÔNG", 243, 97, 3033, 1730], ["IN ĐÔ NÊ XI A", 7200, 2750, 2150, 1438], ["UCRAINA", 1000, 443, 1890, 980], ["Ô X TRÂY LIA", 373, 253, 389, 257]
        ]],
        ["Gỗ & sản phẩm gỗ", [
            ["HOA KỲ", 0, 69458, 0, 113915], ["NHẬT BẢN", 0, 24714, 0, 35614], ["TRUNG QUỐC", 0, 2991, 0, 21763],
            ["ANH", 0, 12832, 0, 17322], ["ĐỨC", 0, 13060, 0, 15776], ["PHÁP", 0, 12294, 0, 11712]
        ]],
        ["Hàng thủy sản", [
            ["NHẬT BẢN", 0, 40157, 0, 50161], ["HOA KỲ", 0, 31237, 0, 47860], ["HÀN QUỐC", 0, 17298, 0, 25830],
            ["TRUNG QUỐC", 0, 6242, 0, 14707], ["ĐỨC", 0, 14099, 0, 14671], ["TÂY BAN NHA", 0, 9240, 0, 10170]
        ]],
        ["Hạt điều", [
            ["HOA KỲ", 3511, 16245, 3201, 18006], ["TRUNG QUỐC", 3242, 14083, 2344, 12134], ["HÀ LAN", 1497, 7479, 1438, 7960]
        ]],
        ["Hạt tiêu", [
            ["HOA KỲ", 759, 2332, 1218, 3776], ["ĐỨC", 449, 1302, 1116, 3511], ["ẤN ĐỘ", 216, 486, 438, 1120]
        ]]
    ]
    # Note: 1000 tons and million USD normalization. Units in MD are Tons and 1000 USD.
    for cmd, countries in data:
        for country, l09, v09, l10, v10 in countries:
            # 2010
            if l10: records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Export_Volume", "value": l10/1000.0, "unit": "1000_ton", "data_type": "Actual"}))
            if v10: records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Export_Value", "value": v10/1000.0, "unit": "million_USD", "data_type": "Actual"}))
            # 2009
            t_ctx_09 = {"year": 2009, "month": 1, "period_type": "Monthly", "data_type": "Actual"}
            if l09: records.append(create_record(metadata, t_ctx_09, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Export_Volume", "value": l09/1000.0, "unit": "1000_ton", "data_type": "Actual"}))
            if v09: records.append(create_record(metadata, t_ctx_09, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Export_Value", "value": v09/1000.0, "unit": "million_USD", "data_type": "Actual"}))
            
    return {"metadata": metadata, "records": records}

def parse_pl6c_2010_02():
    # Nguồn Nhập khẩu (Jan 2010)
    metadata = {"year": 2010, "month": 1, "appendix_number": "PL6c", "source_file": "2010_02_PhuLuc_T02_2010_PL6c.md"}
    records = []
    t_ctx = {"year": 2010, "month": 1, "period_type": "Monthly", "data_type": "Actual"}
    
    data = [
        ["Phân bón các loại", [
            ["TRUNG QUỐC", 77431, 29090, 162229, 51074], ["NGA", 7004, 691, 68644, 16828], ["HÀN QUỐC", 6250, 797, 62170, 14264],
            ["MALAIXIA", 0, 0, 27878, 8919], ["NHẬT BẢN", 0, 0, 52420, 7373], ["CA NA ĐA", 3000, 2219, 12000, 4762],
            ["PHI LIP PIN", 10600, 4566, 12120, 3286]
        ]],
        ["Bông các loại", [
            ["HOA KỲ", 8176, 11726, 11920, 19077], ["ẤN ĐỘ", 480, 773, 6940, 10935], ["BRAXIN", 1134, 1692, 1677, 2870]
        ]],
        ["Cao su", [
            ["CAMPUCHIA", 3953, 5120, 4182, 12070], ["HÀN QUỐC", 1227, 2233, 5203, 8391], ["THÁI LAN", 1569, 2706, 4342, 5796]
        ]],
        ["Lúa mì", [
            ["Ô X TRÂY LIA", 31155, 9902, 70573, 17244], ["UCRAINA", 0, 0, 69175, 15481]
        ]],
        ["Gỗ & sản phẩm gỗ", [
            ["TRUNG QUỐC", 0, 6641, 0, 14735], ["MALAIXIA", 0, 4476, 0, 12852], ["HOA KỲ", 0, 5328, 0, 12208]
        ]],
        ["Sữa và sản phẩm sữa", [
            ["HÀ LAN", 0, 13043, 0, 15635], ["NIU ZI LÂN", 0, 3193, 0, 14783], ["HOA KỲ", 0, 3612, 0, 8391]
        ]],
        ["Thức ăn gia súc và nguyên liệu", [
            ["ẤN ĐỘ", 0, 34643, 0, 63112], ["HOA KỲ", 0, 2792, 0, 26955], ["TRUNG QUỐC", 0, 3224, 0, 11770]
        ]],
        ["Thuốc trừ sâu và nguyên liệu", [
            ["TRUNG QUỐC", 0, 7050, 0, 26841], ["ẤN ĐỘ", 0, 1009, 0, 5922], ["THỤY SỸ", 0, 0, 0, 5544]
        ]]
    ]
    for cmd, countries in data:
        for country, l09, v09, l10, v10 in countries:
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Import_Volume", "value": l10/1000.0, "unit": "1000_ton", "data_type": "Actual"}))
            records.append(create_record(metadata, t_ctx, country, "National", {"sector": "Trade", "commodity": cmd}, {"attribute": "Import_Value", "value": v10/1000.0, "unit": "million_USD", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/02"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl6a_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL6a.json"))
    save_json(parse_pl6b_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL6b.json"))
    save_json(parse_pl6c_2010_02(), os.path.join(out_dir, "2010_02_PhuLuc_T02_2010_PL6c.json"))
    print("Successfully parsed PL6a, PL6b, PL6c for Feb 2010.")
