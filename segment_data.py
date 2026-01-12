
import os
import re
import json

def get_sector(title):
    title = title.lower()
    if any(k in title for k in ["lúa", "gieo cấy", "trồng trọt", "cây vụ đông", "màu lương thực", "ngắn ngày", "hàng năm", "rau", "đậu", "ngô", "khoai", "sắn"]):
        return "Cultivation"
    if any(k in title for k in ["chăn nuôi", "lợn", "heo", "gia cầm", "bò", "trâu"]):
        return "Livestock"
    if any(k in title for k in ["thủy sản", "thuỷ sản", "nuôi trồng", "khai thác thủy sản"]):
        return "Fishery"
    if any(k in title for k in ["lâm nghiệp", "trồng rừng", "gỗ"]):
        return "Forestry"
    if any(k in title for k in ["xuất khẩu", "nhập khẩu", "xnk", "thị trường"]):
        return "Trade"
    if any(k in title for k in ["dịch hại", "sâu bệnh", "sinh vật gây hại"]):
        return "Pest"
    return "Other"

def segment_file(filepath):
    filename = os.path.basename(filepath)
    # Extract year and month from filename or path
    year_match = re.search(r'20\d{2}', filepath)
    month_match = re.search(r'[tT_](\d{2})', filename)
    
    year = year_match.group(0) if year_match else "Unknown"
    month = month_match.group(1) if month_match else "Unknown"
    
    # # Correct the 2019 file in 2010 folder issue
    # if "T10_2019" in filename:
    #     year = "2019"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by Phase: _**Phụ lục [number]**_ or # **Phụ lục [number]** or # PHỤ LỤC ...
    # Using a more flexible regex for Appendix headers
    pattern = r'(_\*\*Phụ lục [0-9a-z]+\*\*_|# \*\*Phụ lục [0-9a-z]+\*\*|# \*\*PHỤ LỤC [0-9a-z]+\*\*|# PHỤ LỤC [0-9a-z]+)'
    parts = re.split(pattern, content, flags=re.IGNORECASE)
    
    if len(parts) < 2:
        return []

    segments = []
    # parts[0] is usually preamble
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i+1].strip()
        
        # Get first couple of non-empty lines from body as title
        lines = [l.strip() for l in body.split('\n') if l.strip() and not l.strip().startswith('|')]
        title = " ".join(lines[:2]) if lines else "Untitled"
        
        phuluc_id_match = re.search(r'phụ lục ([0-9a-z]+)', header, re.IGNORECASE)
        phuluc_id = phuluc_id_match.group(1) if phuluc_id_match else f"segment_{i//2}"
        
        sector = get_sector(title)
        
        if sector == "Other" and i == 1: # Usually the first summary table is agriculture context
             sector = "Cultivation" # Default for "Tổng hợp kết quả sản xuất nông nghiệp"

        segment_filename = f"{year}_{month}_{filename.replace('.md', '')}_PL{phuluc_id}.md"
        dest_dir = f"segments/{year}"
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, segment_filename)
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(f"{header}\n\n{body}")
            
        segments.append({
            "year": int(year) if year.isdigit() else year,
            "month": int(month) if month.isdigit() else month,
            "phuluc": phuluc_id,
            "sector": sector,
            "title": title[:100],
            "file_path": dest_path
        })
    return segments

def main():
    root_dir = "markdown_output/2015"
    all_segments = []
    
    if os.path.exists(root_dir):
        files = [f for f in os.listdir(root_dir) if f.endswith('.md')]
        for filename in files:
            full_path = os.path.join(root_dir, filename)
            print(f"Processing {filename}...")
            all_segments.extend(segment_file(full_path))
    
    with open('segments_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(all_segments, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully created {len(all_segments)} segments for 2011.")

if __name__ == "__main__":
    main()
