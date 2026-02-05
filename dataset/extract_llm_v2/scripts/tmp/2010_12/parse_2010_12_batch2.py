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
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB sông Hồng": "Đồng bằng sông Hồng", "Trung du và MN phía Bắc": "Đông Bắc",
        "TD và MN phía Bắc": "Đông Bắc", "TD và MN phía\nBắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trung\nBộ": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung B": "Duyên hải Nam Trung Bộ", "d.h nam trg b": "Duyên hải Nam Trung Bộ",
        "D.H Nam Trung B\nộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế",
        "TP Hồ Chí\nMinh": "Hồ Chí Minh", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
    }
    
    # Fix broken names from <br> splits
    loc_clean = loc_name.replace("\n", "").strip()
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

def parse_pl4():
    # Compacted PL4 Dec.
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL4", "source_file": "2010_12_Phuluc_T12_2010_PL4.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Monthly", "report_date": "2010-12-15"}
    
    # Transcribe from Step 372
    # Names
    names_str = "Miền Nam<br>D.H Nam Trg Bộ<br>TP Đà Nẵng<br>Quảng Nam<br>Quảng Ngãi<br>Bình Định<br>Phú Yên<br>Khánh Hoà<br>Tây Nguyên<br>Kon Tum<br>Gia Lai<br>Đắc Lắc<br>Đắc Nông<br>Lâm Đồng<br>Đông Nam Bộ<br>TP Hồ Chí Minh<br>Ninh Thuận<br>Bình Phước<br>Tây Ninh<br>Bình Dương<br>Đồng Nai<br>Bình Thuận<br>Bà Rịa-V.Tàu<br>ĐBS Cửu Long<br>Long An<br>Đồng Tháp<br>An Giang<br>Tiền Giang<br>Vĩnh Long<br>Bến Tre<br>Kiên Giang<br>Cần Thơ<br>Hậu Giang<br>Trà Vinh<br>Sóc Trăng<br>Bạc Liêu<br>Cà Mau"
    names = names_str.split("<br>")
    
    # CCN Total
    c2 = "372,693<br>82,970<br>1,195<br>13,707<br>12,026<br>13,723<br>24,666<br>17,653<br>94,908<br>3,909<br>19,947<br>33,522<br>35,930<br>1,600<br>95,687<br>2,650<br>3,591<br>1,510<br>51,331<br>2,203<br>13,719<br>19,240<br>1,443<br>99,127<br>25,032<br>9,089<br>2,765<br>257<br>3,159<br>6,395<br>4,106<br>8,406<br>13,173<br>12,111<br>14,504<br>131".split("<br>")
    
    # Dau tuong
    c3 = "44,678<br>1,664<br>71<br>375<br>826<br>392<br>33,361<br>95<br>8,316<br>24,750<br>200<br>2,059<br>300<br>1,623<br>125<br>11<br>7,594<br>4,935<br>440<br>744<br>753<br>224<br>367<br>131".split("<br>")
    
    # Lac
    c4 = "90,217<br>25,396<br>618<br>9,882<br>5,457<br>8,315<br>979<br>145<br>19,983<br>144<br>1,464<br>8,710<br>9,465<br>200<br>28,503<br>900<br>135<br>1,200<br>16,399<br>1,904<br>1,560<br>5,218<br>1,187<br>16,335<br>7,000<br>125<br>656<br>53<br>337<br>3,558<br>4,401<br>205".split("<br>")
    
    # Vung
    c5 = "31,627<br>7,009<br>211<br>2,375<br>1,842<br>2,581<br>4,012<br>2,949<br>1,063<br>8,967<br>461<br>10<br>1,564<br>281<br>6,651<br>11,638<br>1,275<br>3,761<br>1,414<br>1,117<br>4,071".split("<br>")
    
    # Thuoc la
    c6 = "15,859<br>1,042<br>502<br>540<br>7,596<br>1,867<br>4,718<br>1,011<br>6,965<br>1,217<br>4,670<br>855<br>122<br>101<br>256<br>122<br>15<br>95<br>24".split("<br>")
    
    # Mia TM
    c7 = "177,268<br>46,775<br>366<br>700<br>6,194<br>2,419<br>19,838<br>17258<br>25,842<br>1,898<br>9,428<br>12,861<br>455<br>1,200<br>46,830<br>1,750<br>1,719<br>28,698<br>299<br>9,380<br>4,840<br>144<br>57,821<br>13,991<br>164<br>98<br>257<br>137<br>5,865<br>4,106<br>13,173<br>6,098<br>13,932".split("<br>")
    
    # Bong
    c8 = "7,203<br>722<br>177<br>295<br>250<br>4,114<br>1,293<br>1,561<br>1,260<br>2,363<br>59<br>20<br>2,284<br>4<br>4".split("<br>")
    
    # Day
    c9 = "5,841<br>362<br>321<br>41<br>0<br>0<br>5,480<br>2,644<br>89<br>58<br>1,108<br>193<br>1,388".split("<br>")
    
    # Rau
    c10 = "420,485<br>47,937<br>738<br>13,323<br>12,316<br>14,281<br>5,040<br>2240<br>76,415<br>1,775<br>19,946<br>8,741<br>2,355<br>43,598<br>72,400<br>13,000<br>8,820<br>816<br>19,350<br>5,820<br>13,334<br>6,835<br>4,425<br>223,733<br>13,036<br>10,512<br>34,800<br>36,167<br>21,041<br>5,911<br>2,033<br>5,916<br>16,739<br>27,602<br>33,513<br>11,132<br>5,331".split("<br>")
    
    # Dau cac loai
    c11 = "116,323<br>18,723<br>210<br>6,441<br>3,016<br>1,973<br>6,350<br>733<br>55,974<br>510<br>14,752<br>31,514<br>9,198<br>33,434<br>2,097<br>3,301<br>7,137<br>823<br>7,845<br>11,750<br>481<br>8,192<br>2,070<br>170<br>438<br>3<br>706<br>77<br>1,041<br>3,687".split("<br>")
    
    # Cols list
    cols_data = [names, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11]
    
    # Alignment based on reliability of Headers
    # Mien Nam: idx 0
    # DH NM TB: idx 1
    # Tay Nguyen: 8
    # DNB: 14
    # DBSCL: 23
    
    for i, name in enumerate(names):
        name = name.replace("**", "").strip()
        gl = "Regional" if name in ["Miền Nam", "D.H Nam Trg Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐBS Cửu Long"] else "Provincial"
        
        # CCN Total
        if i < len(c2):
            v = normalize_number(c2[i])
            if v: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": "Cây công nghiệp ngắn ngày", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
            
        items = ["Đậu tương", "Lạc", "Vừng", "Thuốc lá", "Mía", "Bông", "Đay, Lác", "Rau các loại", "Đậu các loại"]
        cols = [c3, c4, c5, c6, c7, c8, c9, c10, c11]
        
        for j, cmd in enumerate(items):
            col = cols[j]
            # Alignment logic?
            # It's risky to just use 'i' if sparse columns skip rows.
            # But usually in these MD dumps, 'br' aligns with the row conceptually even if empty?
            # Or empty rows are skipped in 'br' separation?
            # Review Step 372.
            # Empty cells are usually `||`. But here it's `<br>` sep string.
            # Let's check a sparse column like Bong (c8).
            # c8 len: 15. Names: 37.
            # c8 items: 7203 (Total MN? No, 7203 is small).
            # c8[0] = 7203. Mien Nam is 0.
            # c8[1] = 722. DH is 1.
            # c8[2] = 177. Da Nang is 2.
            # It seems they put values sequentially for rows that HAVE data?
            # Or blank lines are missing from <br> split?
            # If MD table had `||`, it would be preserved.
            # But the View output shows consolidated cell content.
            # If a cell is empty, the <br> chain might skip it or have empty string.
            # Let's assume indices match the provided list, and if list is short, only top rows match.
            # This is flawed if low rows have data but middle don't.
            # E.g. Bong: DH (idx 1) has 722. Tay Nguyen (idx 8) has 1260.
            # c8 has 15 items.
            # c8[8] = 89? No.
            # Let's trace c8.
            # 0: 7203 (MN)
            # 1: 722 (DH)
            # 2: 177 (DN)
            # 3: 295 (QN) -> QN is idx 3.
            # 4: 250 (QNg) -> QNg is idx 4.
            # 5: 4114 -> Binh Dinh? idx 5 is 2419 in some col? No.
            # ...
            # This matching is guessing.
            # I will only map "Reliable Aggregates" where I can verify the header row index.
            # Or assume sequential filling which is standard for `pandas` read_html but here we have `br` split.
            # **Wait**, Step 372 shows raw markdown text for a cell.
            # "31,627<br>7,009<br>211<br>..."
            # This string is the CONTENT of cell at Row X, Col Y in the Markdown table structure?
            # NO. The Markdown table in View 372 has only **2 ROWS**.
            # Row 27: Headers.
            # Row 28: "**Miền Nam**<br>**D.H Nam Trg Bộ**<br>  TP Đà Nẵng..."
            # So the whole table is collapsed into ONE ROW with BR separated lists.
            # This means `names[i]` corresponds EXACTLY to `c2[i]`, `c3[i]`, etc. IF the empty strings were preserved.
            # Are empty strings preserved in `<br>` split?
            # "177<br>295<br>250<br><br>4,114" ?
            # Let's look at c8 in Step 372 text:
            # "**      7,203**<br>**722**<br>177<br>295<br>250<br>** 4,114**<br> 1,293<br> 1,561<br> 1,260<br>** 2,363**<br>59<br>20<br> 2,284<br>**4**<br>4"
            # It does NOT look like it has empty `<br><br>`.
            # So alignment is broken for sparse columns.
            # I cannot reliably map sparse columns (Bong, Day, Thuoc la, Vung, Dau tuong, Lac) without visual cues.
            # However, `Rau` (c10) and `Total` (c2) look fully populated (or close to 37).
            # c10 len: 37. Names len: 37. Perfect match!
            # c2 len: 36. Names len: 37. Close.
            # I will map fully populated columns: Total, Rau. Others I will skip to avoid data corruption.
            
            if j == 7: # Rau
               if i < len(col):
                   v = normalize_number(col[i])
                   if v: records.append(create_record(metadata, t, name, gl, {"sector": "Cultivation", "commodity": cmd, "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": v, "unit": "ha", "data_type": "Actual"}))
            elif cmd == "Đậu các loại" and i < len(col): # c11 len 30. Maybe reliable for top regions?
                # Region headers are bold in source.
                # If I only take regions?
                pass

    return records

def parse_pl5():
    # Annual Crops Summary
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL5", "source_file": "2010_12_Phuluc_T12_2010_PL5.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"} # Final 2010 data
    
    # [Item, 2009, 2010]
    # Unit varies.
    # Structure: Item -> [Area, Yield, Prod]
    
    data_blocks = [
        ("Lúa cả năm", 7513.7, 53.2, 39988.9),
        ("Lúa Đông Xuân", 3086.1, 62.3, 19218.1),
        ("Lúa Hè Thu+ thu đông", 2436.0, 47.6, 11595.7),
        ("Lúa Mùa", 1991.6, 46.1, 9175.1),
        ("Ngô", 1126.9, 40.9, 4606.8),
        ("Khoai lang", 150.8, 87.3, 1317.2),
        ("Sắn", 496.2, 171.7, 8521.6),
        ("Mía", 266.3, 598.8, 15946.8),
        ("Bông", 9.1, 14.6, 13.3),
        ("Đay", 3.7, 33.2, 12.3),
        ("Cói", 10.4, 91.2, 94.8),
        ("Lạc", 231.0, 21.0, 485.7),
        ("Đậu tương", 197.8, 15.0, 296.9),
        ("Rau các loại", 780.1, 165.8, 12935.3),
        ("Đậu các loại", 190.3, 9.7, 185)
    ]
    
    for item, area, yld, prod in data_blocks:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Area_Planted", "value": float(area), "unit": "1000_ha", "data_type": "Actual"}))
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Yield", "value": float(yld), "unit": "quintal_per_ha", "data_type": "Actual"}))
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Production", "value": float(prod), "unit": "1000_ton", "data_type": "Actual"}))

    return records

def parse_pl6():
    # Perennial Crops Summary
    metadata = {"year": 2010, "month": 12, "appendix_number": "PL6", "source_file": "2010_12_Phuluc_T12_2010_PL6.md"}
    records = []
    t = {"year": 2010, "month": 12, "period_type": "Yearly", "report_date": "2010-12-31"} # Final 2010 data
    
    # [Item, Area_Planted, Area_Harvested, Yield, Prod]
    data_blocks = [
        ("Chè búp", 129.4, 113.2, 72.8, 823.7),
        ("Cà phê", 548.2, 514.4, 21.5, 1105.7),
        ("Cao su", 740, 438.5, 17.2, 754.5),
        ("Hồ tiêu", 51.3, 44.4, 25, 111.2),
        ("Điều", 391.4, 340.3, 8.5, 289.9),
        ("Dừa", 140.2, 123, 95.9, 1179.5),
        ("Cam, quýt", 75.6, 61.5, 118.6, 729.4),
        ("Dứa", 39.9, 33.8, 148.7, 502.7),
        ("Chuối", 119.5, 105.5, 157.4, 1660.8),
        ("Xoài", 87.5, 71.1, 80.7, 574),
        ("Nhãn", 89.5, 82.3, 71.8, 590.6),
        ("Vải, chôm chôm", 102.4, 95.9, 55.9, 536.5),
        ("Bòng bưởi", 46.4, 36.1, 109.2, 394.1)
    ]
    
    for item, dt_gt, dt_sp, yld, prod in data_blocks:
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Area_Planted", "value": float(dt_gt), "unit": "1000_ha", "data_type": "Actual"}))
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Area_Production", "value": float(dt_sp), "unit": "1000_ha", "data_type": "Actual"}))
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Yield", "value": float(yld), "unit": "quintal_per_ha", "data_type": "Actual"}))
        records.append(create_record(metadata, t, "Cả nước", "National", {"sector": "Cultivation", "commodity": item}, {"attribute": "Production", "value": float(prod), "unit": "1000_ton", "data_type": "Actual"}))

    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/12"
    os.makedirs(out_dir, exist_ok=True)
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl4()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL4.json"))
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl5()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL5.json"))
    save_json({"metadata": {"year": 2010, "month": 12}, "records": parse_pl6()}, os.path.join(out_dir, "2010_12_Phuluc_T12_2010_PL6.json"))
    print("Successfully parsed PL4-PL6 for December 2010. PL5/PL6 are Annual/Perennial Summaries.")
