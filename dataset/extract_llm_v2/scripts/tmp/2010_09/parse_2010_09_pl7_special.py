import re
import json
import os
import uuid

def generate_id():
    return str(uuid.uuid4())

# Load region map
REGION_MAP_PATH = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/region_map.json"
try:
    with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
        REGION_DATA = json.load(f)
except:
    REGION_DATA = {"provinces": {}, "regions": {}}

def create_record(metadata, time, loc_name, geo_level, item, metric, comp=None):
    geo_context = {"geo_level": geo_level, "location_name": loc_name}
    alias_map = {
        "Đồng bằng sông Cửu Long": "Đồng bằng sông Cửu Long", "ĐBS Cửu Long": "Đồng bằng sông Cửu Long", "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
        "ĐB. sông Hồng": "Đồng bằng sông Hồng", "Đồng bằng sông Hồng": "Đồng bằng sông Hồng",
        "Trung du và MN phía Bắc": "Đông Bắc", "TD và MN phía Bắc": "Đông Bắc",
        "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ", "d.h nam trg bộ": "Duyên hải Nam Trung Bộ", "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
        "Tây Nguyên": "Tây Nguyên", "Đông Nam Bộ": "Đông Nam Bộ",
        "Bắc Trung Bộ": "Bắc Trung Bộ", "Miền Trung - Tây Nguyên": "Miền Trung",
        "TP Hồ Chí Minh": "Hồ Chí Minh", "TP Đà Nẵng": "Đà Nẵng",
        "Bà Rịa-V.Tàu": "Bà Rịa - Vũng Tàu", "Thừa Thiên Huế": "Thừa Thiên Huế", "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu"
    }
    norm_loc = alias_map.get(loc_name.strip(), loc_name.strip())
    
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
    elif norm_loc == "Miền bắc":
        geo_context["region_id"] = "NORTH"; geo_context["region_name_vn"] = "Miền Bắc"
    
    record = {"record_id": generate_id(), "time_context": time, "geo_context": geo_context, "item_context": item, "metric_context": metric, "metadata": metadata}
    if comp: record["comparison_context"] = comp
    return record

def clean_value(s):
    if not s: return None
    s = s.replace("**", "").replace("*", "").replace("_", "").replace(",", "").strip()
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_md_list(text):
    if not text: return []
    items = text.split("<br>")
    cleaned = []
    for item in items:
        # Check if item is bold (Header)
        is_bold = "**" in item
        val = clean_value(item)
        cleaned.append({"raw": item, "val": val, "is_bold": is_bold})
    return cleaned

def align_planted_forest(names_raw, totals_raw, phdd_raw, kinhte_raw):
    # Prepare lists
    names = [x.replace("**", "").replace("_","").strip() for x in names_raw.split("<br>")]
    # Filter only valid names (remove Roman numerals rows if they are just markers, but here names list seems to include Region names which we want)
    # The names list in markdown Row 21 is: Cả nước, Miền bắc, ĐB. sông Hồng, Hà Nội...
    # We want to keep them all.
    
    totals = parse_md_list(totals_raw)
    phdd = parse_md_list(phdd_raw)
    kinhte = parse_md_list(kinhte_raw)
    
    aligned_data = [] # List of dicts: {name, total, phdd, kinhte}
    
    # pointers
    p_phdd = 0
    p_kinhte = 0
    
    # We iterate through Totals because Total usually exists for every row (Name)
    # Check if names count == totals count (Basic validation)
    # In row 21: Names seem to align with Totals 1-to-1 based on visual density.
    
    limit = min(len(names), len(totals))
    
    for i in range(limit):
        name = names[i]
        total_obj = totals[i]
        t_val = total_obj["val"]
        
        row_res = {"name": name, "total": t_val, "phdd": None, "kinhte": None, "is_bold": total_obj["is_bold"]}
        
        if t_val is None:
            aligned_data.append(row_res)
            continue
            
        # Try to find matching PHDD + KinhTe
        # Candidates
        cand_phdd = phdd[p_phdd]["val"] if p_phdd < len(phdd) else 0
        cand_kinhte = kinhte[p_kinhte]["val"] if p_kinhte < len(kinhte) else 0
        
        # Combinations to check
        # 1. Total = PHDD + KT
        if abs(t_val - ((cand_phdd or 0) + (cand_kinhte or 0))) < 1.0:
            row_res["phdd"] = cand_phdd
            row_res["kinhte"] = cand_kinhte
            if cand_phdd is not None: p_phdd += 1
            if cand_kinhte is not None: p_kinhte += 1
            
        # 2. Total = PHDD (KT missing/0)
        elif abs(t_val - (cand_phdd or 0)) < 1.0:
            row_res["phdd"] = cand_phdd
            row_res["kinhte"] = 0
            if cand_phdd is not None: p_phdd += 1
            
        # 3. Total = KT (PHDD missing/0)
        elif abs(t_val - (cand_kinhte or 0)) < 1.0:
            row_res["phdd"] = 0
            row_res["kinhte"] = cand_kinhte
            if cand_kinhte is not None: p_kinhte += 1
            
        # 4. Total exists but no components match (maybe both blank?) -> Assume component data missing
        else:
            # Fallback: If this is a Bold Row (Region), and the next values in PHDD/KT are also Bold, forcably align them?
            if total_obj["is_bold"]:
                # Check formatting of candidates
                is_phdd_bold = phdd[p_phdd]["is_bold"] if p_phdd < len(phdd) else False
                is_kt_bold = kinhte[p_kinhte]["is_bold"] if p_kinhte < len(kinhte) else False
                
                if is_phdd_bold: 
                    row_res["phdd"] = cand_phdd; p_phdd += 1
                if is_kt_bold: 
                    row_res["kinhte"] = cand_kinhte; p_kinhte += 1
            
        aligned_data.append(row_res)
        
    return aligned_data

def process_file_content(content):
    # Extract Row 21 (North) and Row 30 (South) blocks
    # Using regex to find the specific patterns based on the "Name" column start
    
    # Pattern for Row 21: Starts with "Cả nước" ends with "Thừa Thiên Huế" in the first block
    # Note: text is markdown table cells.
    
    # We will split by table row "|...|"
    lines = content.split('\n')
    data_rows = [l for l in lines if "|" in l and ("Cả nước" in l or "Miền Nam" in l)]
    
    all_aligned = []
    
    for row_line in data_rows:
        cols = row_line.split('|')
        if len(cols) < 5: continue
        
        # Col 2 in MD view is Names (index 2)
        # Col 3 is Total (index 3)
        # Col 4 is PHDD (index 4)
        # Col 5 is KinhTe (index 5)
        # Col 6 is ChamSoc (index 6)
        # Col 7 is KhoanhNuoi (index 7)
        # Col 8 is BaoVe (index 8)
        
        names_raw = cols[2]
        total_raw = cols[3]
        phdd_raw = cols[4]
        kt_raw = cols[5]
        
        # Only process if it contains <br> (block data)
        if "<br>" in names_raw:
            aligned = align_planted_forest(names_raw, total_raw, phdd_raw, kt_raw)
            all_aligned.extend(aligned)
            
    return all_aligned

def parse_pl7():
    metadata = {"year": 2010, "month": 9, "appendix_number": "PL7", "source_file": "2010_09_phuluc_T09_2010_PL7.md"}
    file_path = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2010/2010_09_phuluc_T09_2010_PL7.md"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    aligned_data = process_file_content(content)
    
    records = []
    t = {"year": 2010, "month": 9, "period_type": "Cumulative", "report_date": "2010-09-30"}
    
    for row in aligned_data:
        name = row["name"]
        # Skip garbage names often found in first col like "I", "II", numerals
        if len(name) < 3 and not name.isupper(): continue 
        if any(char.isdigit() for char in name): continue
        if "Chia ra:" in name: continue
        
        # Clean name
        clean_name = re.sub(r'^\d+\.?\s*', '', name).replace("_", "").strip()
        
        gl = "Provincial"
        if row["is_bold"] or clean_name in ["Cả nước", "Miền bắc", "Miền Nam", "ĐB. sông Hồng", "Trung du và MN phía Bắc", "Bắc Trung Bộ", "D.H Nam Trung Bộ", "Tây Nguyên", "Đông Nam Bộ", "ĐB. sông Cửu Long"]:
            gl = "Regional"
            if clean_name == "Cả nước": gl = "National"
            
        if row["total"] is not None:
            records.append(create_record(metadata, t, clean_name, gl, {"sector": "Forestry", "commodity": "Rừng tập trung", "sub_item": "Tổng số"}, {"attribute": "Area_Planted", "value": row["total"], "unit": "ha", "data_type": "Actual"}))
        if row["phdd"] is not None:
            records.append(create_record(metadata, t, clean_name, gl, {"sector": "Forestry", "commodity": "Rừng phòng hộ, đặc dụng", "sub_item": None}, {"attribute": "Area_Planted", "value": row["phdd"], "unit": "ha", "data_type": "Actual"}))
        if row["kinhte"] is not None:
            records.append(create_record(metadata, t, clean_name, gl, {"sector": "Forestry", "commodity": "Rừng kinh tế", "sub_item": None}, {"attribute": "Area_Planted", "value": row["kinhte"], "unit": "ha", "data_type": "Actual"}))
            
    return records

if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2010/09"
    os.makedirs(out_dir, exist_ok=True)
    records = parse_pl7()
    save_json({"metadata": {"year": 2010, "month": 9}, "records": records}, os.path.join(out_dir, "2010_09_phuluc_T09_2010_PL7.json"))
    print(f"Successfully specialized parsed PL7 for September 2010. Records: {len(records)}")
