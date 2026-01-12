import json
import csv
import os

def flatten_json_to_csv(json_file, csv_file):
    # Đọc dữ liệu JSON
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} không tồn tại.")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("Warning: Dữ liệu JSON rỗng.")
        return

    # Định nghĩa các cột cho file CSV (theo schema_final.json)
    headers = [
        'record_id', 
        'year', 'month', 
        'geo_level', 'location_name', 'region_id',
        'sector', 'commodity', 'sub_item',
        'attribute', 'value', 'unit', 'data_type',
        'source_file'
    ]

    # Ghi file CSV
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for record in data:
            # Làm phẳng cấu trúc lồng nhau
            flat_row = {
                'record_id': record.get('record_id'),
                'year': record.get('time_context', {}).get('year'),
                'month': record.get('time_context', {}).get('month'),
                'geo_level': record.get('geo_context', {}).get('geo_level'),
                'location_name': record.get('geo_context', {}).get('location_name'),
                'region_id': record.get('geo_context', {}).get('region_id'),
                'sector': record.get('item_context', {}).get('sector'),
                'commodity': record.get('item_context', {}).get('commodity'),
                'sub_item': record.get('item_context', {}).get('sub_item'),
                'attribute': record.get('metric_context', {}).get('attribute'),
                'value': record.get('metric_context', {}).get('value'),
                'unit': record.get('metric_context', {}).get('unit'),
                'data_type': record.get('metric_context', {}).get('data_type'),
                'source_file': record.get('metadata', {}).get('source_file')
            }
            writer.writerow(flat_row)

    print(f"✅ Đã chuyển đổi thành công {len(data)} bản ghi sang: {csv_file}")

if __name__ == "__main__":
    input_json = 'extracted_data_2009.json'
    output_csv = 'extracted_data_2009.csv'
    flatten_json_to_csv(input_json, output_csv)
