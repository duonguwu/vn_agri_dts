import pandas as pd
import numpy as np

# Danh sách các tỉnh theo vùng (để phục vụ Plan B: Regional Breakdown)
REGIONS_PROVINCES = {
    "Mekong_Delta": [
        "An Giang", "Tiền Giang", "Bến Tre", "Đồng Tháp", "Vĩnh Long", 
        "Cần Thơ", "Hậu Giang", "Trà Vinh", "Sóc Trăng", "Bạc Liêu", 
        "Cà Mau", "Kiên Giang", "Long An"
    ],
    "Red_River_Delta": [
        "Hà Nội", "Hải Phòng", "Vĩnh Phúc", "Bắc Ninh", "Hải Dương", 
        "Hưng Yên", "Thái Bình", "Hà Nam", "Nam Định", "Ninh Bình"
    ],
    "Northern": [
        "Lào Cai", "Yên Bái", "Điện Biên", "Hòa Bình", "Lai Châu", 
        "Sơn La", "Hà Giang", "Cao Bằng", "Bắc Kạn", "Lạng Sơn", 
        "Tuyên Quang", "Thái Nguyên", "Phú Thọ", "Bắc Giang"
    ],
    "Central_Highlands": [
        "Kon Tum", "Gia Lai", "Đắk Lắk", "Đắk Nông", "Lâm Đồng"
    ]
}

def augment_plan_b(df):
    """
    Kế hoạch B: Spatial Granularity (Tách dữ liệu từ Vùng ra Tỉnh)
    Mỗi dòng Regional sẽ được tách thành n dòng Provincial.
    """
    new_rows = []
    for _, row in df.iterrows():
        if row['geo_level'] == 'Regional' and row['region_id'] in REGIONS_PROVINCES:
            provinces = REGIONS_PROVINCES[row['region_id']]
            # Chia đều giá trị cho các tỉnh (đây là giả định để tăng số dòng)
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
    return pd.DataFrame(new_rows)

def augment_plan_a(df):
    """
    Kế hoạch A: Metric Expansion & Temporal Granularity
    1. Metric Expansion: Nếu có Area và Output, tạo thêm row Yield.
    2. Temporal Expansion: Từ 1 tháng chốt năm, tạo data giả định cho các tháng trước.
    """
    # 1. Metric Expansion (tạm thời skip vì sample không đủ cặp Area/Output cho cùng 1 item/location)
    
    # 2. Temporal Expansion: Giả định mỗi record năm 2008 được phân bổ cho 12 tháng
    new_rows = []
    for _, row in df.iterrows():
        for m in range(1, 13):
            new_row = row.copy()
            new_row['month'] = m
            new_row['record_id'] = f"{row['record_id']}_M{m}"
            # Giả định giá trị phân bổ theo tháng (ví dụ 1/12)
            if row['attribute'] in ['Output', 'Export_Volume', 'Export_Value']:
                new_row['value'] = row['value'] / 12
                new_row['data_type'] = 'Estimated'
            new_rows.append(new_row)
    
    return pd.DataFrame(new_rows)

def main():
    # Load sample data
    input_file = '/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/sample_2008_long.csv'
    df = pd.read_csv(input_file)
    print(f"Số dòng ban đầu: {len(df)}")

    # Áp dụng Kế hoạch B (Chi tiết hóa không gian)
    df_b = augment_plan_b(df)
    print(f"Số dòng sau Kế hoạch B: {len(df_b)}")

    # Áp dụng Kế hoạch A (Chi tiết hóa thời gian)
    df_final = augment_plan_a(df_b)
    print(f"Số dòng sau Kế hoạch A: {len(df_final)}")

    # Lưu kết quả
    output_file = '/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/augmented_sample_500.csv'
    df_final.to_csv(output_file, index=False)
    print(f"Đã lưu {len(df_final)} dòng vào {output_file}")

if __name__ == "__main__":
    main()
