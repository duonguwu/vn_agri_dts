import pandas as pd

# 1. Đọc file Long Dataset mẫu
df_long = pd.read_csv('dataset/sample_2008_long.csv')

# 2. Tiến hành Pivot (Xoay ngang)
# Index: Các trường định danh
# Columns: Các thuộc tính (Metric) sẽ biến thành cột
# Values: Giá trị số
df_wide = df_long.pivot_table(
    index=['year', 'month', 'location_name', 'commodity', 'sub_item'],
    columns='attribute',
    values='value'
).reset_index()

# 3. Làm sạch tên cột và sắp xếp
df_wide.columns.name = None
df_wide = df_wide.sort_values(['location_name', 'commodity'])

# 4. Lưu ra file dataset dành cho ML
df_wide.to_csv('dataset/ml_ready_product_2008.csv', index=False)

print('--- PREVIEW DATASET DẠNG NGANG (WIDE FORMAT) ---')
print(df_wide.head(10).to_markdown())