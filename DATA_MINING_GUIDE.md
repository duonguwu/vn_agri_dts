# Hướng dẫn Khai thác Dữ liệu Nông nghiệp (Data Mining Guide)

Tài liệu này hướng dẫn cách sử dụng `schema_final.json` để xây dựng Long Dataset và các kỹ thuật Data Mining từ tập hợp báo cáo 2008-2022.

---

## 1. Cách đưa dữ liệu vào Schema (Ví dụ: Phụ lục 2008)

Dựa trên file `markdown_output/2008/Phuluc_12_2008.md`, chúng ta sẽ bóc tách bảng **Phụ lục 2: Diện tích gieo trồng cây vụ đông Miền Bắc**.

### Ví dụ 1: Dòng dữ liệu cho Hà Nội (Dòng 42 trong file gốc)
Trong bảng, Hà Nội có diện tích Ngô là 12,025 Ha.

**JSON Record (Tuân thủ schema):**
```json
{
  "record_id": "200812_HN_NGO_AREA",
  "time_context": { "year": 2008, "month": 12, "report_date": "2008-12-15" },
  "geo_context": { 
      "geo_level": "Provincial", 
      "location_name": "Hà Nội", 
      "region_id": "Red_River_Delta" 
  },
  "item_context": {
      "sector": "Cultivation",
      "commodity": "Ngô",
      "sub_item": "Cây vụ Đông"
  },
  "metric_context": {
      "attribute": "Area",
      "value": 12025.0,
      "unit": "ha",
      "data_type": "Actual"
  },
  "metadata": { "source_file": "Phuluc_12_2008.md", "table_index": 2 }
}
```

### Ví dụ 2: Dữ liệu Chăn nuôi (Phụ lục 6)
Dòng 318: Lợn (Cả nước) năm 2008 là 26,701,598 con.

```json
{
  "record_id": "200812_TQ_LON_HEADCOUNT",
  "time_context": { "year": 2008, "month": 12, "report_date": "2008-12-31" },
  "geo_context": { "geo_level": "National", "location_name": "Cả nước" },
  "item_context": { "sector": "Livestock", "commodity": "Lợn" },
  "metric_context": {
      "attribute": "Headcount",
      "value": 26701598.0,
      "unit": "heads",
      "data_type": "Estimated"
  }
}
```

---

## 2. Cách bổ sung Feature mới (Feature Engineering)

Khi đã có Long Dataset, ta có thể tạo Feature ngang để làm ML bằng cách:

1.  **Lag Features (Số liệu quá khứ):**
    - Tạo cột `Value_T-1`: Lấy giá trị của cùng tỉnh, cùng sản phẩm ở tháng trước (hoặc năm trước).
    - *Công dụng*: Dự báo chuỗi thời gian (Time Series Forecasting).

2.  **External Features (Dữ liệu ngoại biên):**
    - **Thời tiết**: Map tên tỉnh với lượng mưa/nhiệt độ của tháng đó.
    - **Giá phân bón**: Map giá phân bón nhập khẩu (Theme 3) với sản lượng trồng trọt (Theme 1).

3.  **Efficiency Metrics (Chỉ số hiệu quả):**
    - `Yield = Output / Area` (Năng suất).
    - `Value_per_Ha`: Doanh thu trên mỗi ha (nếu có giá bán).

---

## 3. Các bài toán Data Mining gợi ý

Từ Schema này, bạn có thể thực hiện 3 bài toán chính:

### A. Phân tích Xu hướng & Dự báo (Regression/Time Series)
- **Đề tài**: Dự báo sản lúa gạo ĐBSCL dựa trên diện tích gieo cấy và tình hình dịch hại trễ 1 tháng.
- **Input**: Long Dataset -> Pivot ngang (Row = Month/Province, Columns = Area, Pest_Area, Past_Output).

### B. Phân cụm (Clustering) các địa phương
- **Đề tài**: Phân nhóm các tỉnh dựa trên cơ cấu cây trồng và vật nuôi.
- **Input**: Tính tỷ trọng (Area_Lúa / Total_Area) của từng tỉnh qua các năm. Dùng K-Means để xem tỉnh nào thuần nông, tỉnh nào chuyển dịch sang thủy sản.

### C. Khai phá Luật kết hợp (Association Rules)
- **Đề tài**: "Nếu diện tích Ngô tăng, liệu sản lượng Chăn nuôi gia cầm có tăng theo sau đó không?"
- **Input**: Chuyển dữ liệu sang dạng giao dịch (Transaction) theo năm.

---

## 4. Ràng buộc (Constraints) cần lưu ý khi trích xuất
1.  **Unit Standard**: Luôn phải đổi "1000 ha" -> "ha" (nhân 1000). Không để đơn vị hỗn hợp.
2.  **Null values**: Nếu báo cáo ghi "-" hoặc trống, để `null`. Không được mặc định là `0`.
3.  **Naming Convention**: Tên sản phẩm phải thống nhất (ví dụ: "Lợn" và "Heo" phải quy về "Lợn").

*(Tài liệu này là Blueprint để triển khai giai đoạn trích xuất 50k dòng)*
