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
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    try:
        if "\n" in s: s = s.split("\n")[0]
        return float(s)
    except: return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    if loc_name in REGION_DATA["provinces"]:
        geo_context["region_id"] = REGION_DATA["provinces"][loc_name]["region_id"]
        geo_context["region_name"] = REGION_DATA["provinces"][loc_name]["region_name"]
    elif loc_name in REGION_DATA["regions"]:
        geo_context["region_id"] = REGION_DATA["regions"][loc_name]
        geo_context["region_name"] = loc_name
    
    record = {
        "record_id": generate_id(),
        "time_context": time,
        "geo_context": geo_context,
        "item_context": item,
        "metric_context": metric,
        "metadata": metadata
    }
    if comp: record["comparison_context"] = comp
    return record

def parse_pl6_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL6", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL6.md"}
    records = []
    regional = ["Miền bắc", "Miền Nam", "ĐB. sông Hồng", "Đông bắc", "Tây bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]
    
    # Loc, TR_Total, TR_PHDD, TR_Kinhte, Chamsoc, Khoanhnuoi, KhoanBV
    pl6_data = [
        ["Cả nước", "172232", "40430", "131802", "218962", "754367", "2516421"],
        ["Miền bắc", "138721", "28393", "110328", "148542", "634821", "1253844"],
        ["ĐB. sông Hồng", "2314", "1564", "750", "3643", "14838", "43735"],
        ["Hà Nội (mở rộng)", None, None, None, None, None, "8600"],
        ["Hải Phòng", "542", "342", "200", "500", "720", "5500"],
        ["Vĩnh Phúc", "346", "146", "200", "973", "561", "4500"],
        ["Bắc Ninh", "15", "15", None, "30", "33", "300"],
        ["Hải Dương", "15", None, "15", "1090", "11", "6235"],
        ["Hà Nam", "122.6", "26", "97.0", "230", "1679", "6300"],
        ["Nam Định", "268", "268", None, "520", None, "1700"],
        ["Thái Bình", "625", "625", None, "200", None, "7000"],
        ["Ninh Bình", "380", "143", "238", "100", "11834", "3600"],
        ["Đông bắc", "92046", "16718", "75328", "96067", "129093", "653328"],
        ["Hà Giang", "13900", "2900", "11000", "20582", "37730", "122913"],
        ["Cao Bằng", "1560", "445", "1115", "2230", "25507", "32000"],
        ["Lào Cai", "4752", "631", "4121", "1640", "5145", "87517"],
        ["Bắc Cạn", "5279", "713", "4566", "9975", "9248", "25000"],
        ["Lạng Sơn", "7263", "2388", "4875", "8540", "9801", "24081"],
        ["Tuyên Quang", "14602", "2000", "12602", "3354", "7886", "229639"],
        ["Yên Bái", "14034", "2640", "11394", "6009", "19670", "19670"],
        ["Thái Nguyên", "5506", "1017", "4489", "2116", "4600", "20033"],
        ["Phú Thọ", "5031", "244", "4787", "2812", "1400", "46606"],
        ["Bắc Giang", "4045", "616", "3429", "2838", "2125", "33753"],
        ["Quảng Ninh", "16074", "3124", "12950", "35971", "5981", "31370"],
        ["Tây bắc", "19677", "5390", "14287", "19644", "359549", "279907"],
        ["Lai Châu", "6240", "1111", "5129", "1108", "108721", "137339"],
        ["Điện Biên", "769", "329", "440", "1000", "1000", "30000"],
        ["Sơn La", "4412", "2931", "1481", "8336", "178800", "82568"],
        ["Hoà Bình", "8256", "1019", "7237", "9200", "4500", "30000"],
        ["Bắc Trung Bộ", "24684", "4721", "19963", "29188", "131341", "276874"],
        ["Thanh Hoá", "12000", "2280", "9720", "5062", "30000", "70000"],
        ["Nghệ An", "8590", "868", "7722", "17600", "74044", "85000"],
        ["Hà Tĩnh", "50", "50", None, "50", "9269", "27219"],
        ["Quảng Bình", "0", None, None, "712", "10476", "55337"],
        ["Quảng Trị", "3425", "1223", "2202", "3098", "1319", "23318"],
        ["Thừa Thiên Huế", "619", "300", "319", "2666", "6233", "16000"],
        ["Miền Nam", "30195", "8721", "21474", "55971", "115243", "1137767"],
        ["D.H Nam Trung Bộ", "3204", "741", "2463", "32622", "75840", "162142"],
        ["Đà Nẵng", "22", None, "22", "169", "121", "15000"],
        ["Quảng Nam", None, None, None, "1632", "21527", "37220"],
        ["Quảng Ngãi", "1400", "400", "1000", "9801", "1241", "28284"],
        ["Bình Định", "501", "40", "461", "10405", "47551", "37138"],
        ["Phú Yên", "100", "100", None, "9435", "3073", "30000"],
        ["Khánh Hoà", "1181", "201", "980", "1180", "2327", "14500"],
        ["Tây Nguyên", "10870", "1945", "8925", "9019", "9799", "640076"],
        ["Kon Tum", "2294", "705", "1589", "798", "2016", "80000"],
        ["Gia Lai", "869", "669", "200", None, "2254", "99130"],
        ["Đắc Lắc", "5026", "303", "4723", "879", "3944", "83577"],
        ["Đắc Nông", "1982", "82", "1900", "6799", "1585", "40000"],
        ["Lâm Đồng", "699", "186", "513", "543", None, "337369"],
        ["Đông Nam Bộ", "10006", "3835", "6171", "7490", "28040", "260159"],
        ["TP Hồ Chí Minh", "1120", "247", "873", "371", "56", "31274"],
        ["Ninh Thuận", "1400", "1400", "0", "1000", "5000", "53000"],
        ["Bình Phước", "350", "350", None, "174", None, "20774"],
        ["Tây Ninh", "875", "700", "175", "248", "10380", "42810"],
        ["Đồng Nai", "350", "350", None, "500", "1099", "1600"],
        ["Bình Thuận", "5688", "655", "5033", "4606", "10520", "109220"],
        ["Bà Rịa-Vũng Tàu", "223", "133", "90", "591", "985", "985"],
        ["ĐB. sông Cửu Long", "6115", "2200", "3915", "6840", "1564", "75390"],
        ["Tiền Giang", "168", "168", None, "93", None, "1200"],
        ["Bến Tre", "75", "75", None, "248", "14", "2974"],
        ["Kiên Giang", "120", "120", None, "234", "1500", "14000"],
        ["Hậu Giang", "500", None, "500", "179", None, "1600"],
        ["Trà Vinh", "684", "134", "550", "488", "40", "4100"],
        ["Sóc Trăng", "466", "466", None, None, None, "1200"],
        ["Bạc Liêu", "495", "200", "295", None, None, "1900"],
        ["Cà Mau", "1633", "517", "1116", "5598", "10", "40256"],
        ["Trung uơng", "3316", "3316", None, "14449", "4303", "124810"],
    ]
    for row in pl6_data:
        loc = row[0]; geo = "National" if loc == "Cả nước" else ("Regional" if loc in regional else "Provincial")
        t = {"year": 2009, "month": 10, "period_type": "Cumulative"}
        items = [("Trồng rừng tập trung", "Tổng số"), ("Trồng rừng tập trung", "Rừng PHĐD"), ("Trồng rừng tập trung", "Rừng Kinh tế"), ("Chăm sóc rừng", None), ("Khoanh nuôi tái sinh", None), ("Khoán bảo vệ rừng", None)]
        attrs = ["Forest_Area_Planted", "Forest_Area_Planted", "Forest_Area_Planted", "Area_Maintained", "Area_Regenerated", "Area_Protected"]
        for idx in range(6):
            va = normalize_number(row[idx+1])
            if va is not None:
                records.append(create_record(metadata, t, loc, geo, {"sector": "Forestry", "commodity": items[idx][0], "sub_item": items[idx][1]}, {"attribute": attrs[idx], "value": va/1000.0, "unit": "1000_ha", "data_type": "Actual"}))
    return {"metadata": metadata, "records": records}


def parse_pl7_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL7", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL6.md"}
    records = []
    # 0:TT, 1:Item, 2:Unit, 3:Plan, 4:TH_9T, 5:ƯTH_T10, 6:TH_10T, 7:TH_10T_08, 8:%_Plan, 9:%_YoY
    prod_rows = [
        ["I", "Tổng sản lượng", "1000 Tấn", "4600", "3623", "355", "3978", "3819", "86.5", "104.2"],
        ["1", "Sản lượng khai thác", "1000 Tấn", "2200", "1678", "155", "1833", "1752", "83.3", "104.6"],
        ["1.1", "Khai thác biển", "1000 Tấn", "2000", "1542", "140", "1682", "1597", "84.1", "105.3"],
        ["1.2", "Khai thác nội địa", "1000 Tấn", "200", "136", "15", "151", "155", "75.5", "97.4"],
        ["2", "Sản lượng nuôi trồng", "1000 Tấn", "2400", "1945", "200", "2145", "2067", "89.4", "103.8"],
    ]
    for r in prod_rows:
        item, unit, plan, v9, v10, v10c, v10c08, cp, cy = r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]
        g = "Cả nước"; gl = "National"
        i = {"sector": "Fishery", "commodity": item}
        
        if normalize_number(v10):
            records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Monthly"}, g, gl, i, {"attribute": "Production", "value": normalize_number(v10), "unit": unit, "data_type": "Actual"}))
        if normalize_number(v10c):
            comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cy), "comparison_unit": "percentage", "reference_period": "2008"}
            records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Cumulative"}, g, gl, i, {"attribute": "Production", "value": normalize_number(v10c), "unit": unit, "data_type": "Actual"}, comp))
        if normalize_number(plan):
            records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, g, gl, i, {"attribute": "Production", "value": normalize_number(plan), "unit": unit, "data_type": "Plan"}))
            
    return {"metadata": metadata, "records": records}


def parse_pl8_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL8", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL8.md"}
    records = []
    # Simplified extraction of National Trade
    xk_rows = [
        ["Tổng kim ngạch XK", None, "1280", None, "12674", None, "91.12"],
        ["Nông sản chính", None, "550", None, "6599", None, "89.62"],
        ["Cà phê", "50", "74", "938", "1388", "116.84", "82.60"],
        ["Cao su", "70", "120", "549", "840", "106.43", "61.15"],
        ["Gạo", "400", "150", "5367", "2387", "133.23", "92.35"],
        ["Chè", "15", "20", "111", "145", "123.26", "114.54"],
        ["Hạt điều", "15", "76", "144", "675", "104.32", "86.68"],
        ["Hạt tiêu", "12", "36", "120", "300", "151.67", "108.22"],
        ["Hàng rau quả", None, "40", None, "361", None, "115.20"],
        ["Sắn và SP từ sắn", "150", "34", None, "503", "219.35", None],
        ["Thuỷ sản", None, "430", None, "3469", None, "90.38"],
        ["Lâm sản chính", None, "237", None, "2147", None, "85.92"],
    ]
    nk_rows = [
        ["Tổng kim ngạch NK", None, "900", None, "8373", None, "94.52"],
        ["Các mặt hàng nhập khẩu chính", None, "563", None, "5518", None, "85.83"],
        ["Phân bón các loại", "500", "130", "3867", "1184", "137.37", "84.88"],
    ]
    for rows, sector in [(xk_rows, "Export"), (nk_rows, "Import")]:
        attr_vol = "Export_Volume" if sector == "Export" else "Import_Volume"
        attr_val = "Export_Value" if sector == "Export" else "Import_Value"
        for r in rows:
            item = r[0]; v10_vol, v10_val, v10c_vol, v10c_val, cp_vol, cp_val = r[1], r[2], r[3], r[4], r[5], r[6]
            g = "Cả nước"; gl = "National"
            i = {"sector": "Trade", "commodity": item}
            if normalize_number(v10_vol):
                records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Monthly"}, g, gl, i, {"attribute": attr_vol, "value": normalize_number(v10_vol), "unit": "1000_ton", "data_type": "Actual"}))
            if normalize_number(v10_val):
                records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Monthly"}, g, gl, i, {"attribute": attr_val, "value": normalize_number(v10_val), "unit": "million_USD", "data_type": "Actual"}))
            if normalize_number(v10c_vol):
                comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp_vol), "comparison_unit": "percentage", "reference_period": "2008"} if cp_vol else None
                records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Cumulative"}, g, gl, i, {"attribute": attr_vol, "value": normalize_number(v10c_vol), "unit": "1000_ton", "data_type": "Actual"}, comp))
            if normalize_number(v10c_val):
                comp = {"comparison_type": "YoY", "comparison_value": normalize_number(cp_val), "comparison_unit": "percentage", "reference_period": "2008"} if cp_val else None
                records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Cumulative"}, g, gl, i, {"attribute": attr_val, "value": normalize_number(v10c_val), "unit": "million_USD", "data_type": "Actual"}, comp))
    return {"metadata": metadata, "records": records}


def parse_pl9_10():
    metadata = {"year": 2009, "month": 10, "appendix_number": "PL9", "source_file": "2009_10_PHULUC_T10_2009_FINAL_PL9.md"}
    records = []
    rows = [
        ["Đầu tư Thuỷ lợi", "1483500", "1748086", "115000", "1863086", "125.59"],
        ["Đầu tư Nông nghiệp", "493000", "361720", "17500", "379220", "76.92"],
        ["Đầu tư Lâm nghiệp", "230000", "118807", "4800", "123607", "53.74"],
        ["Đầu tư Thuỷ sản", "24000", "24000", "1500", "25500", "106.25"],
    ]
    for r in rows:
        item, plan, v9, v10, v10c, cp = r
        g = "Bộ NN & PTNT"; gl = "National"
        i = {"sector": "Investment", "commodity": item}
        if normalize_number(v10):
            records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Monthly"}, g, gl, i, {"attribute": "Investment_Amount", "value": normalize_number(v10), "unit": "million_VND", "data_type": "Actual"}))
        if normalize_number(v10c):
            comp = {"comparison_type": "vs_Plan", "comparison_value": normalize_number(cp), "comparison_unit": "percentage", "reference_period": "Annual_Plan"}
            records.append(create_record(metadata, {"year": 2009, "month": 10, "period_type": "Cumulative"}, g, gl, i, {"attribute": "Investment_Amount", "value": normalize_number(v10c), "unit": "million_VND", "data_type": "Actual"}, comp))
        if normalize_number(plan):
            records.append(create_record(metadata, {"year": 2009, "month": 12, "period_type": "Annual"}, g, gl, i, {"attribute": "Investment_Amount", "value": normalize_number(plan), "unit": "million_VND", "data_type": "Plan"}))
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/10"
    save_json(parse_pl6_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL6.json"))
    save_json(parse_pl7_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL7.json"))
    save_json(parse_pl8_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL8.json"))
    save_json(parse_pl9_10(), os.path.join(out_dir, "2009_10_PHULUC_T10_2009_FINAL_PL9.json"))
    print("Successfully parsed PL6, 7, 8, 9 for Oct 2009 with Region Mapping.")
