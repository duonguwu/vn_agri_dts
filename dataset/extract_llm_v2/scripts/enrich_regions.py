import json
import os
import glob

# Đường dẫn cấu hình
BASE_DIR = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2"
REGION_MAP_PATH = os.path.join(BASE_DIR, "region_map.json")
DATA_DIR = os.path.join(BASE_DIR, "extracted_data")

def load_region_map():
    with open(REGION_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def enrich_file(file_path, region_data):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "records" not in data:
            return False

        updated = False
        for record in data["records"]:
            geo = record.get("geo_context", {})
            loc_name = geo.get("location_name")
            
            if not loc_name:
                continue
            
            # 1. Kiểm tra nếu là Tỉnh
            if loc_name in region_data["provinces"]:
                p_info = region_data["provinces"][loc_name]
                geo["region_id"] = p_info["region_id"]
                geo["region_name"] = p_info["region_name"]
                updated = True
            
            # 2. Kiểm tra nếu bản thân location_name đã là tên Vùng
            elif loc_name in region_data["regions"]:
                geo["region_id"] = region_data["regions"][loc_name]
                geo["region_name"] = loc_name
                updated = True
                
            # 3. Xử lý một số tên viết tắt phổ biến trong data cũ
            else:
                alias_map = {
                    "ĐB sông Hồng": "Đồng bằng sông Hồng",
                    "ĐB. sông Hồng": "Đồng bằng sông Hồng",
                    "ĐBS Cửu Long": "Đồng bằng sông Cửu Long",
                    "ĐB. sông Cửu Long": "Đồng bằng sông Cửu Long",
                    "D.H Nam Trung Bộ": "Duyên hải Nam Trung Bộ",
                    "D.H Nam Trg Bộ": "Duyên hải Nam Trung Bộ",
                    "Bắc Trung bộ": "Bắc Trung Bộ"
                }
                if loc_name in alias_map:
                    real_name = alias_map[loc_name]
                    geo["region_id"] = region_data["regions"].get(real_name)
                    geo["region_name"] = real_name
                    updated = True

        if updated:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

if __name__ == "__main__":
    reg_data = load_region_map()
    json_files = glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)
    
    count = 0
    for f_path in json_files:
        if enrich_file(f_path, reg_data):
            print(f"Enriched: {os.path.relative_path(f_path, DATA_DIR) if hasattr(os, 'relative_path') else f_path}")
            count += 1
            
    print(f"\nDone! Enriched {count} files with region information.")
