import pandas as pd
import numpy as np

# Danh sách đầy đủ 63 tỉnh thành Việt Nam theo vùng
REGIONS_PROVINCES = {
    "Red_River_Delta": ["Hà Nội", "Hải Phòng", "Hà Nam", "Nam Định", "Ninh Bình", "Thái Bình", "Vĩnh Phúc", "Bắc Ninh", "Hải Dương", "Hưng Yên", "Quảng Ninh"],
    "Northern_Mountainous": ["Hà Giang", "Cao Bằng", "Bắc Kạn", "Tuyên Quang", "Lào Cai", "Yên Bái", "Thái Nguyên", "Lạng Sơn", "Bắc Giang", "Phú Thọ", "Điện Biên", "Lai Châu", "Sơn La", "Hòa Bình"],
    "North_Central_Coast": ["Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Thừa Thiên Huế"],
    "South_Central_Coast": ["Đà Nẵng", "Quảng Nam", "Quảng Ngãi", "Bình Định", "Phú Yên", "Khánh Hòa", "Ninh Thuận", "Bình Thuận"],
    "Central_Highlands": ["Kon Tum", "Gia Lai", "Đắk Lắk", "Đắk Nông", "Lâm Đồng"],
    "South_East": ["Bình Phước", "Tây Ninh", "Bình Dương", "Đồng Nai", "Bà Rịa - Vũng Tàu", "TP. Hồ Chí Minh"],
    "Mekong_Delta": ["Long An", "Tiền Giang", "Bến Tre", "Trà Vinh", "Vĩnh Long", "Đồng Tháp", "An Giang", "Kiên Giang", "Cần Thơ", "Hậu Giang", "Sóc Trăng", "Bạc Liêu", "Cà Mau"]
}

def augment_plan_b(df):
    """
    Kế hoạch B: Spatial Granularity (Toàn quốc -> Vùng -> Tỉnh)
    Mục tiêu: Tách các dòng tổng hợp (Cả nước, Vùng) thành 63 tỉnh.
    """
    new_rows = []
    all_provinces = [p for region in REGIONS_PROVINCES.values() for p in region]
    
    for _, row in df.iterrows():
        # 1. Nếu là National -> Bung ra 63 tỉnh
        if row['geo_level'] == 'National':
            val_per_province = row['value'] / len(all_provinces)
            for prov in all_provinces:
                new_row = row.copy()
                new_row['record_id'] = f"{row['record_id']}_{prov.replace(' ', '_')}"
                new_row['geo_level'] = 'Provincial'
                new_row['location_name'] = prov
                new_row['value'] = val_per_province
                new_rows.append(new_row)
        
        # 2. Nếu là Regional -> Bung ra các tỉnh trong vùng
        elif row['geo_level'] == 'Regional':
            region_key = None
            # Thử look up vùng dựa trên location_name hoặc region_id
            if row['region_id'] in REGIONS_PROVINCES:
                region_key = row['region_id']
            else:
                mapping = {
                    "Mekong": "Mekong_Delta",
                    "Đồng bằng sông Cửu Long": "Mekong_Delta",
                    "Miền Bắc": "Northern_Mountainous",
                    "Đồng bằng sông Hồng": "Red_River_Delta",
                    "Tây Nguyên": "Central_Highlands"
                }
                for k, v in mapping.items():
                    if k in row['location_name']:
                        region_key = v
                        break
            
            if region_key:
                provinces = REGIONS_PROVINCES[region_key]
                val_per_province = row['value'] / len(provinces)
                for prov in provinces:
                    new_row = row.copy()
                    new_row['record_id'] = f"{row['record_id']}_{prov.replace(' ', '_')}"
                    new_row['geo_level'] = 'Provincial'
                    new_row['location_name'] = prov
                    new_row['value'] = val_per_province
                    new_rows.append(new_row)
            else:
                new_rows.append(row)
        else:
            new_rows.append(row)
    return pd.DataFrame(new_rows)

def augment_plan_a(df):
    """
    Kế hoạch A: Temporal Granularity & Metric Expansion
    1. Temporal: Từ 1 tháng chốt năm, tạo data cho 12 tháng.
    2. Metric: Tạo Yield từ Area và Output.
    """
    new_rows = []
    for _, row in df.iterrows():
        # Tạo dữ liệu cho 12 tháng
        for m in range(1, 13):
            month_row = row.copy()
            month_row['month'] = m
            month_row['record_id'] = f"{row['record_id']}_M{m}"
            
            # Giả định phân bổ giá trị theo tháng
            if row['attribute'] in ['Output', 'Export_Volume', 'Export_Value']:
                month_row['value'] = row['value'] / 12
                month_row['data_type'] = 'Estimated'
            
            new_rows.append(month_row)
            
            # Metric Expansion: Nếu là Area, giả định tính được Output dựa trên Yield trung bình
            # (Đây là logic giả định để demo việc tăng số dòng)
            if row['attribute'] == 'Area':
                output_row = month_row.copy()
                output_row['attribute'] = 'Output'
                output_row['record_id'] = f"{month_row['record_id']}_DERIVED_OUT"
                output_row['value'] = month_row['value'] * 5.5 # Giả định yield 5.5
                output_row['unit'] = 'ton'
                new_rows.append(output_row)
                
    return pd.DataFrame(new_rows)

def main():
    input_file = '/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/sample_2008_long.csv'
    df = pd.read_csv(input_file)
    print(f"Số dòng ban đầu: {len(df)}")

    # Áp dụng Kế hoạch B (Spatial)
    df_b = augment_plan_b(df)
    print(f"Số dòng sau Kế hoạch B (Tách ra 63 tỉnh): {len(df_b)}")

    # Áp dụng Kế hoạch A (Thời gian + Metric)
    df_final = augment_plan_a(df_b)
    print(f"Số dòng sau Kế hoạch A (Tách 12 tháng + Tạo metrics): {len(df_final)}")

    output_file = '/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/augmented_sample_10k.csv'
    df_final.to_csv(output_file, index=False)
    print(f"Đã lưu {len(df_final)} dòng vào {output_file}")

if __name__ == "__main__":
    main()
