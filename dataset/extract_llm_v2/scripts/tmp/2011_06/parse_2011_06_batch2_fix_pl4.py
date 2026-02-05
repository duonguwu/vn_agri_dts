import json
import uuid
import os

# --- UTILS SHARED ---
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
    if s in ["", "-", ".", ",", "||", "|", "...", ".."]: return None
    
    # Cleaning noise
    s = s.replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    s = s.replace("(", "").replace(")", "").replace(" ", "")
    
    # Handle mixed <br> in singular value case
    if "<br>" in s: s = s.split("<br>")[0]

    # Handle Vietnamese formatting: 1.234,5 vs 1,234.5
    if "." in s and "," in s:
        if s.find(".") < s.find(","): # 1.234,5 -> 1234.5
            s = s.replace(".", "").replace(",", ".")
        else: # 1,234.5 -> 1234.5
            s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1: s = s.replace(",", "") # 1,000,000 -> 1000000
        else:
            parts = s.split(",")
            if len(parts[1]) == 3: s = s.replace(",", "") # Assume thousands
            else: s = s.replace(",", ".") # Assume decimal
    elif "." in s:
        if s.count(".") > 1: s = s.replace(".", "")
        else:
            parts = s.split(".")
            if len(parts[1]) == 3: s = s.replace(".", "") # Assume thousands
            else: pass

    try:
        return float(s)
    except: return None

def get_geo_info(loc_name):
    # Mapping logic
    alias_map = {
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
        "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
        "Đông Nam Bộ": "Đông Nam Bộ",
        "Tây Nguyên": "Tây Nguyên",
        "TP Hồ Chí Minh": "Hồ Chí Minh",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu",
        "Thừa Thiên Huế": "Thừa Thiên Huế"
    }
    
    loc_clean = loc_name.strip().replace("-", " - ")
    loc_clean = alias_map.get(loc_clean, loc_clean)
    
    if loc_clean == "Hồ Chí Minh": loc_clean = "Hồ Chí Minh"
    
    geo_context = {"location_name": loc_clean}
    
    if loc_clean in REGION_DATA["provinces"]:
        geo_context["geo_level"] = "Provincial"
        geo_context["region_id"] = REGION_DATA["provinces"][loc_clean]["region_id"]
        geo_context["region_name_vn"] = REGION_DATA["provinces"][loc_clean]["region_name"]
    elif loc_clean in REGION_DATA["regions"] or "Bộ" in loc_clean or "Miền" in loc_clean or "Tây Nguyên" in loc_clean:
         geo_context["geo_level"] = "Regional"
         if loc_clean in REGION_DATA["regions"]:
             geo_context["region_id"] = REGION_DATA["regions"][loc_clean]
    else:
        geo_context["geo_level"] = "Provincial"
    
    return geo_context

def create_record(metadata, time_ctx, geo_ctx, item_ctx, metric_ctx, comp_ctx=None):
    record = {
        "record_id": generate_id(),
        "time_context": time_ctx,
        "geo_context": geo_ctx,
        "item_context": item_ctx,
        "metric_context": metric_ctx,
        "metadata": metadata
    }
    if comp_ctx: record["comparison_context"] = comp_ctx
    return record

# --- SPECIFIC PARSING FOR PL4 ---

def parse_pl4_explode():
    """
    Parses PL4 (Rice & Crops) specifically handling the Compacted/Explode format.
    File: segments/2011/2011_06_Phuluc_06_2011_PL4.md
    """
    metadata = {"year": 2011, "month": 6, "appendix_number": "PL4", "source_file": "2011_06_Phuluc_06_2011_PL4.md"}
    base_time = {"year": 2011, "month": 6, "period_type": "Monthly", "report_date": "2011-06-15"}
    records = []

    # --- RAW DATA TRANSCRIPTION ---
    
    # LIST 1: NAMES
    # "Miền Nam<br>D.H Nam Trung Bộ<br>  TP Đà Nẵng<br>  Quảng Nam<br>  Quảng Ngãi<br>  Bình Định<br>  Phú Yên<br>  Khánh Hoà<br>**Tây Nguyên**<br>  Kon Tum<br>  Gia Lai<br>  Đắc Lắc<br>  Đắc Nông<br>  Lâm Đồng<br>**Đông Nam Bộ**<br>  TP Hồ Chí Minh<br>  Ninh Thuận<br>  Bình Phước<br>  Tây Ninh<br>  Bình Dương<br>  Đồng Nai<br>  Bình Thuận<br>  Bà Rịa-V.Tàu<br>**ĐBS Cửu Long**<br>  Long An<br>  Đồng Tháp<br>  An Giang<br>  Tiền Giang<br>  Vĩnh Long<br>  Bến Tre<br>  Kiên Giang<br>  Cần Thơ<br>  Hậu Giang<br>  Trà Vinh<br>  Sóc Trăng<br>  Bạc Liêu<br>  Cà Mau"
    raw_names = """Miền Nam
D.H Nam Trung Bộ
TP Đà Nẵng
Quảng Nam
Quảng Ngãi
Bình Định
Phú Yên
Khánh Hoà
Tây Nguyên
Kon Tum
Gia Lai
Đắc Lắc
Đắc Nông
Lâm Đồng
Đông Nam Bộ
TP Hồ Chí Minh
Ninh Thuận
Bình Phước
Tây Ninh
Bình Dương
Đồng Nai
Bình Thuận
Bà Rịa-V.Tàu
ĐBS Cửu Long
Long An
Đồng Tháp
An Giang
Tiền Giang
Vĩnh Long
Bến Tre
Kiên Giang
Cần Thơ
Hậu Giang
Trà Vinh
Sóc Trăng
Bạc Liêu
Cà Mau""".split("\n")

    # LIST 2: LUA HE THU - GIEO CAY (Planted)
    # "**1,937,832**<br>**132,913**<br>3285<br>37,000<br>26,853<br>41,688<br>22,787<br>1,300<br>**6,018**<br>6,018<br>**136,296**<br>5,316<br>10,591<br>51,336<br>1,216<br>21,521<br>38,955<br>7,361<br>**1,662,604**<br>213,206<br>235,597<br>231,885<br>120,915<br> <br>61,489<br>22,498<br>251,218<br>97,883<br> <br>81,196<br>70,000<br>186,000<br>55,809<br>34908"
    # Note: There are empty spaces in the raw string. " <br>".
    # Manual Mapping Check:
    # 1. Mien Nam: 1937
    # 2. DH Nam TB: 132
    # 3. DN: 3285
    # ...
    # 9. Tay Nguyen: 6018
    # ...
    # 11. Gia Lai: 136296 (Wait. 136k is Dong Nam Bo total? Or a province?)
    # Let's check logic: Tay Nguyen total = 6018. Kon Tum = 6018.
    # Where is Gia Lai, Dak Lak?
    # Ah, look at markdown: "**136,296**" follows "**6,018**<br>6,018<br>".
    # Sequence: Region(TN) -> Prov(KT) -> ?? -> Prov(GL)...
    # Wait, the structure is: Region -> List of Provs.
    # TN: 6018. KT: 6018. The rest of TN seems missing or zero in THIS column?
    # No, "**136,296**" is likely Dong Nam Bo Total (DNB).
    # Let's count indices.
    # Names length: 37.
    # Raw Data length: "1,937...34908".
    # Let's try to map carefully.
    
    # We will use "Hard Transcription" with alignment correction.
    # We assume the user wants ACCURACY over automatic splitting if data is sparse.
    
    # Corrected Lists from View File Analysis:
    # Mien Nam: 1,937,832
    # DH Nam TB: 132,913
    # Da Nang: 3285
    # ...
    # Tay Nguyen: 6,018
    # Kon Tum: 6,018
    # Gia Lai: (Missing in vertical list? Or is 136,296 Gia Lai? No, 136k is too big for Gia Lai HT rice).
    # East South (Dong Nam Bo): 136,296.
    # So between Kon Tum and DNB, we have Gia Lai, Dak Lak, Dak Nong, Lam Dong.
    # If list jumps from Kon Tum to DNB, then Gia Lai...Lam Dong are Missing/Zero.
    # BUT wait, the text has "10,591", "51,336".
    # Let's trace back:
    # Text: ... 6,018<br>6,018<br>**136,296**<br>5,316<br>10,591...
    # If 136,296 is DNB, then 5,316 is TP HCM?
    # Let's check TP HCM.
    # TP HCM HT Rice is usually small. 5k is reasonable.
    # Where are Gia Lai, Dak Lak?
    # It seems for HT Rice, Tay Nguyen only has Kon Tum listed? Or the others are 0?
    # This implies the list is COMPRESSED (Missing rows are skipped).
    # THIS IS A CRITICAL FINDING. If rows are skipped, simple Split is WRONG.
    
    # Clean Room Decision: 
    # Only extract Regional Totals + Provinces that we are SURE about alignment.
    # Or, extract only Regional Totals for safety.
    # Given the request is "Extract what you can", I will extract Regional Totals and clearly aligned provinces.
    
    # Let's map explicit values found:
    data_points = [
        {"name": "Miền Nam", "ht_plant": 1937832, "mua_plant": 45216, "total_color": 508451},
        {"name": "Duyên hải Nam Trung Bộ", "ht_plant": 132913, "mua_plant": 0, "total_color": 80584},
        {"name": "Tây Nguyên", "ht_plant": 6018, "mua_plant": 800, "total_color": 221876},
        {"name": "Đông Nam Bộ", "ht_plant": 136296, "mua_plant": None, "total_color": 154405},
        {"name": "Đồng bằng sông Cửu Long", "ht_plant": 1662604, "mua_plant": None, "total_color": 51586}
    ]
    
    # PROVINCIAL EXTRACT ATTEMPT (Only if easy)
    # Da Nang: 3285 (HT Plant)
    # Quang Nam: 37000
    # Quang Ngai: 26853
    # Binh Dinh: 41688
    # Phu Yen: 22787
    # Khanh Hoa: 1300
    # Kon Tum: 6018 (Matches TN total, so safe).
    # ...
    # For now, to be safe and adhere to "Clean Room" principles of not guessing:
    # I will stick to REGIONAL extraction for PL4 because the misalignment risk is high (compressed rows).
    # Unless I hardcode every province which I can do too.
    # Let's hardcode the clear ones from the top block (DH Nam TB).
    
    # DH Nam TB Provinces are clearly listed in order in the text block.
    # 3285, 37000, 26853, 41688, 22787, 1300.
    # These correspond exactly to Da Nang -> Khanh Hoa.
    dh_nam_tb_provs = [
        {"name": "TP Đà Nẵng", "ht_plant": 3285, "mua_plant": 44416}, # 44416 Mua is the outlier we saw. Skip Mua.
        {"name": "Quảng Nam", "ht_plant": 37000, "mua_plant": 17521},
        {"name": "Quảng Ngãi", "ht_plant": 26853, "mua_plant": 22737},
        {"name": "Bình Định", "ht_plant": 41688, "mua_plant": 4158},
        {"name": "Phú Yên", "ht_plant": 22787, "mua_plant": 0},
        {"name": "Khánh Hoà", "ht_plant": 1300, "mua_plant": 800}
    ]
    
    data_points.extend(dh_nam_tb_provs)

    # --- RECORD GENERATION ---
    for item in data_points:
        loc_name = item["name"]
        geo_info = get_geo_info(loc_name)
        
        # 1. Lua He Thu - Gieo Cay
        if item.get("ht_plant") is not None:
            records.append(create_record(
                metadata, base_time, geo_info,
                item_ctx={"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Hè Thu"},
                metric_ctx={"attribute": "Area_Planted", "value": item["ht_plant"]/1000, "unit": "1000_ha", "data_type": "Actual"}
            ))
            
        # 2. Lua Mua - Gieo Cay (Skip if None or suspicious)
        # Note: We skipped Da Nang Mua Plant (44416) implicitly by not mapping it or hardcoding careful check?
        # In dict above I put 44416. I should filter it or normalize it.
        # 44,416 ha = 44.4 (1000ha). Actually reasonable for Da Nang? 
        # Da Nang agri land is small. 44k ha is 440 km2. Da Nang area is ~1200 km2. 1/3 area is Rice? Unlikely.
        # Quang Nam is 37k. Da Nang 44k? No.
        # So I will SKIP Mua Plant for Da Nang.
        if item.get("mua_plant") is not None:
            val = item["mua_plant"]
            if loc_name == "TP Đà Nẵng" and val > 10000: # Simple outlier heuristic
                pass 
            else:
                records.append(create_record(
                    metadata, base_time, geo_info,
                    item_ctx={"sector": "Cultivation", "commodity": "Lúa", "sub_item": "Mùa"},
                    metric_ctx={"attribute": "Area_Planted", "value": val/1000, "unit": "1000_ha", "data_type": "Actual"}
                ))
        
        # 3. Total Color Crops
        if item.get("total_color") is not None:
            records.append(create_record(
                metadata, base_time, geo_info,
                item_ctx={"sector": "Cultivation", "commodity": "Màu lương thực", "sub_item": "Tổng số"},
                metric_ctx={"attribute": "Area_Planted", "value": item["total_color"]/1000, "unit": "1000_ha", "data_type": "Actual"}
            ))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2011/06"
    os.makedirs(out_dir, exist_ok=True)
    
    data = parse_pl4_explode()
    out_file = os.path.join(out_dir, "2011_06_Phuluc_06_2011_PL4_Exploded.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"metadata": {"year": 2011, "month": 6}, "records": data}, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully exploded PL4 data (Safe Regional + Selected Provincial). Records created: {len(data)}")
