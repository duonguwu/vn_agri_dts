# Phân Tích và Phân Chia Dataset - Báo cáo Nông Nghiệp Việt Nam 2008-2022

## Tổng quan

Dự án phân tích **28 file báo cáo** từ **15 năm** (2008-2022) của Bộ Nông nghiệp và Phát triển Nông thôn để xây dựng dataset có cấu trúc phục vụ Data Mining.

**Mục tiêu cuối cùng**: Dataset 50,000+ dòng cho phân tích xu hướng, dự đoán và khai thác dữ liệu.

---

## I. KHẢO SÁT DỮ LIỆU

### 1. Phân bổ file theo năm

| Năm | Số file | Ghi chú |
|-----|---------|---------|
| 2008 | 1 | Tháng 12 |
| 2009 | 3 | Tháng 10, 11, 12 |
| 2010-2018 | 1/năm | Các tháng khác nhau |
| 2019 | 3 | Tháng 8, 9, 10 |
| 2020-2021 | 1/năm | Tháng 11, tháng 7 |
| 2022 | 10 | Tháng 2-11 (đầy đủ nhất) |
| **Tổng** | **28 file** | **15 năm** |

### 2. Sự thay đổi format qua các giai đoạn

#### **Giai đoạn 1: 2008-2010** - "Format cổ điển"
- **Đặc điểm**: 
  - Giá so sánh năm 1994 (giá cố định)
  - Format văn bản dài, mô tả chi tiết
  - Bảng biểu phức tạp
  - Trọng tâm: sản lượng tuyệt đối
  
- **Nội dung chính**:
  - Sản xuất nông nghiệp (lúa, ngô, cây hàng năm, cây lâu năm)
  - Chăn nuôi (trâu, bò, lợn, gia cầm) + dịch bệnh chi tiết
  - Lâm nghiệp (trồng rừng, khai thác gỗ, vi phạm lâm luật)
  - Thủy sản (khai thác, nuôi trồng)
  - Xuất nhập khẩu (kim ngạch, thị trường)
  - Giá cả thị trường từng mặt hàng

#### **Giai đoạn 2: 2011-2015** - "Chuyển đổi format"
- **Đặc điểm**:
  - Thêm chỉ số tăng trưởng (%)
  - Bắt đầu tập trung phân tích so sánh
  - Format ngắn gọn hơn
  
#### **Giai đoạn 3: 2016-2020** - "Format hiện đại"
- **Đặc điểm**:
  - Tăng trưởng % là chỉ số chính
  - Nhiều phân tích thị trường
  - Xuất khẩu theo từng thị trường cụ thể (Mỹ, EU, Trung Quốc, Nhật)
  - Giá xuất khẩu trung bình (USD/tấn)

#### **Giai đoạn 4: 2021-2022** - "Format COVID"
- **Đặc điểm**:
  - Thêm yếu tố COVID-19
  - Tập trung vào giá xăng dầu, chi phí đầu vào
  - Format ngắn gọn, súc tích hơn nhiều
  - Trọng tâm: xuất nhập khẩu và doanh nghiệp

---

## II. PHÂN TÍCH CHỦ ĐỀ DATA

### 1. Các chủ đề dữ liệu chính

#### **Theme 1: SẢN XUẤT TRỒNG TRỌT**

**Dữ liệu có thể vét cạn**:
- Diện tích gieo trồng (ha) theo: Lúa (Đông xuân, Hè thu, Mùa), Ngô, Khoai lang, Lạc, Đậu tương, Rau các loại
- Năng suất (tạ/ha) từng loại cây
- Sản lượng (nghìn tấn/tấn)
- Tiến độ gieo trồng theo tháng, vùng miền
- Dịch bệnh: Rầy nâu, đạo ôn, khô vằn, sâu cuốn lá - diện tích nhiễm (ha)

**Cấu trúc Long Dataset** (mỗi dòng = 1 quan sát):
```
Date | Region | Crop | Season | Metric | Value | Unit
2008-12 | ĐBSCL | Lúa | Đông Xuân | Diện tích | 3012.5 | nghìn ha
2008-12 | ĐBSCL | Lúa | Đông Xuân | Năng suất | 60.8 | tạ/ha
2008-12 | ĐBSCL | Lúa | Đông Xuân | Sản lượng | 18324.3 | nghìn tấn
```

**Số dòng ước tính**: 
- 15 năm × 12 tháng × 8 loại cây × 6 miền × 3 metrics = ~25,000 dòng

#### **Theme 2: CHĂN NUÔI & THÚ Y**

**Dữ liệu có thể vét cạn**:
- Tổng đàn (nghìn con): Trâu, Bò, Lợn, Gà, Vịt, Ngan
- Sản lượng thịt xuất chuồng (nghìn tấn)
- Giá gia súc/gia cầm (đồng/kg hoặc đồng/con)
- Dịch bệnh: Cúm gia cầm, Lợn tai xanh, Dịch tả lợn châu Phi (DTLCP), Lở mồm long móng
  - Số ổ dịch, tỉnh/huyện/xã
  - Số con tiêu hủy

**Cấu trúc Long Dataset**:
```
Date | Animal | Metric | Value | Unit
2008-12 | Lợn | Tổng đàn | 26701.6 | nghìn con
2019-08 | Lợn | Tiêu hủy do DTLCP | 4426.236 | nghìn con
2022-02 | Gà | Giá hơi | 24000-25000 | đồng/kg
```

**Số dòng ước tính**: 
- 15 năm × 12 tháng × 6 loại × 4 metrics = ~4,000 dòng
- Dịch bệnh: ~2,000 dòng

#### **Theme 3: XUẤT NHẬP KHẨU**

**Dữ liệu có thể vét cạn**:
- **Xuất khẩu**:
  - Kim ngạch (triệu USD) theo mặt hàng: Gạo, Cà phê, Cao su, Tiêu, Hạt điều, Chè, Thủy sản, Gỗ
  - Khối lượng (nghìn tấn)
  - Giá xuất khẩu bình quân (USD/tấn)
  - Thị trường: Mỹ, EU, Trung Quốc, Nhật, Hàn Quốc (% thị phần)
  
- **Nhập khẩu**:
  - Phân bón, Thuốc BVTV, Thức ăn chăn nuôi
  - Khối lượng + giá trị

**Cấu trúc Long Dataset**:
```
Date | Product | Market | Direction | Metric | Value | Unit
2019-08 | Gạo | Philippines | Xuất khẩu | Khối lượng | 1460 | nghìn tấn
2019-08 | Gạo | Philippines | Xuất khẩu | Kim ngạch | 589.4 | triệu USD
2019-08 | Gạo | Philippines | Xuất khẩu | Giá TB | 433 | USD/tấn
```

**Số dòng ước tính**: 
- 15 năm × 12 tháng × 10 mặt hàng × 5 thị trường × 3 metrics = ~27,000 dòng

#### **Theme 4: GIÁ CẢ THỊ TRƯỜNG**

**Dữ liệu có thể vét cạn**:
- Giá nông sản trong nước: Lúa, Gạo, Cà phê, Cao su, Tiêu, Điều (đồng/kg)
- Giá thịt hơi: Lợn, Gà, Bò (đồng/kg)
- Giá thủy sản: Cá tra, Tôm sú, Tôm thẻ (đồng/kg)
- Giá rau quả: Thanh long, Nhãn, Dưa hấu (đồng/kg)
- Theo vùng miền: Miền Bắc, Miền Trung, Miền Nam

**Cấu trúc Long Dataset**:
```
Date | Region | Product | Price | Unit
2019-08 | Đồng Nai | Lợn hơi | 36000-38000 | đồng/kg
2019-08 | An Giang | Lúa IR50404 | 4200 | đồng/kg
```

**Số dòng ước tính**: 
- 15 năm × 12 tháng × 20 sản phẩm × 3 vùng = ~10,800 dòng

---

## III. ĐỀ XUẤT PHÂN CHIA 4 DATASET

### Nguyên tắc phân chia:
1. Chia đều khối lượng công việc (mỗi người ~12,500 dòng)
2. Mỗi dataset tương đối độc lập
3. Dễ merge sau này (chung cấu trúc)

---

### **DATASET 1: PRODUCTION (Sản xuất Trồng trọt)**

**Người chịu trách nhiệm**: Thành viên 1

**Phạm vi**:
- Trồng trọt: Lúa, Ngô, các cây hàng năm, cây lâu năm
- Lâm nghiệp: Trồng rừng, khai thác gỗ
- Diêm nghiệp: Sản xuất muối

**Dữ liệu trích xuất**:
- Diện tích (ha)
- Năng suất (tạ/ha)
- Sản lượng (tấn)
- Theo thời gian (tháng/năm), vùng miền, mùa vụ

**Cấu trúc**:
```csv
Date, Region, ProductType, Product, Season, Metric, Value, Unit
2008-12, ĐBSCL, Lúa, Lúa, Đông Xuân, Diện tích, 3012500, ha
2008-12, ĐBSCL, Lúa, Lúa, Đông Xuân, Năng suất, 6.08, tấn/ha
```

**Ước tính**: ~12,000 dòng

---

### **DATASET 2: LIVESTOCK (Chăn nuôi & Dịch bệnh)**

**Người chịu trách nhiệm**: Thành viên 2

**Phạm vi**:
- Chăn nuôi: Đàn gia súc, gia cầm
- Sản lượng thịt, trứng, sữa
- Dịch bệnh động vật: Cúm gia cầm, DTLCP, Lở mồm long móng, Tai xanh

**Dữ liệu trích xuất**:
- Tổng đàn (con)
- Sản lượng thịt (tấn)
- Số ổ dịch, số con tiêu hủy

**Cấu trúc**:
```csv
Date, Region, AnimalType, Metric, Value, Unit
2019-08, Toàn quốc, Lợn, Tổng đàn, 26701600, con
2019-08, Toàn quốc, Lợn DTLCP, Tiêu hủy, 4426236, con
2019-08, Toàn quốc, Lợn DTLCP, Số ổ dịch, 6959, ổ
```

**Ước tính**: ~13,000 dòng

---

### **DATASET 3: TRADE (Xuất Nhập khẩu)**

**Người chịu trách nhiệm**: Thành viên 3

**Phạm vi**:
- Xuất khẩu: Gạo, Cà phê, Cao su, Tiêu, Điều, Chè, Thủy sản, Gỗ
- Nhập khẩu: Phân bón, Thuốc BVTV, Thức ăn chăn nuôi
- Theo thị trường: Mỹ, EU, Trung Quốc, Nhật, ASEAN

**Dữ liệu trích xuất**:
- Khối lượng (tấn)
- Kim ngạch (USD)
- Giá bình quân (USD/tấn)
- Thị phần (%)

**Cấu trúc**:
```csv
Date, Product, Market, Direction, Metric, Value, Unit
2019-08, Gạo, Philippines, Export, Volume, 1460000, tấn
2019-08, Gạo, Philippines, Export, Value, 589400000, USD
2019-08, Gạo, Philippines, Export, Price, 433, USD/tấn
2019-08, Gạo, Philippines, Export, MarketShare, 34.5, %
```

**Ước tính**: ~14,000 dòng

---

### **DATASET 4: MARKET PRICE (Giá cả Thị trường)**

**Người chịu trách nhiệm**: Thành viên 4

**Phạm vi**:
- Giá nông sản: Lúa, Gạo, Cà phê, Cao su, Tiêu
- Giá chăn nuôi: Lợn hơi, Gà, Bò
- Giá thủy sản: Cá tra, Tôm
- Giá rau quả: Thanh long, Nhãn, Xoài
- Theo vùng/tỉnh

**Dữ liệu trích xuất**:
- Giá trong nước (VND/kg)
- Giá thế giới (USD/tấn)
- Theo thời điểm, địa phương

**Cấu trúc**:
```csv
Date, Region, Province, Product, PriceType, Value, Unit
2019-08, Miền Nam, Đồng Nai, Lợn hơi, Domestic, 36000, VND/kg
2019-08, Đồng bằng sông Cửu Long, An Giang, Lúa IR50404, Domestic, 4200, VND/kg
2019-08, World, , Cà phê Robusta, International, 1297, USD/tấn
```

**Ước tính**: ~11,000 dòng

---

## IV. LONG DATASET - Ý NGHĨA MỖI DÒNG

### Ví dụ cụ thể 1 dòng cho mỗi dataset:

#### **Dataset 1: Production**
```
2019-08-15, Đồng bằng sông Cửu Long, Crop, Lúa, Hè Thu, Sản lượng, 10950000, tấn
```
**Ý nghĩa**: Vào giữa tháng 8/2019, vùng Đồng bằng sông Cửu Long thu hoạch được 10.95 triệu tấn lúa Hè Thu.

#### **Dataset 2: Livestock**
```
2019-08-20, 62 tỉnh, Disease, Lợn DTLCP, Số con tiêu hủy, 4426236, con
```
**Ý nghĩa**: Đến ngày 20/8/2019, dịch tả lợn châu Phi đã lan ra 62 tỉnh, tổng số lợn bị tiêu hủy là 4.426.236 con.

#### **Dataset 3: Trade**
```
2019-08-31, Gạo, Philippines, Export, Kim ngạch, 589400000, USD
```
**Ý nghĩa**: Tháng 8/2019, Việt Nam xuất khẩu gạo sang Philippines đạt kim ngạch 589.4 triệu USD.

#### **Dataset 4: Market Price**
```
2019-08-25, Miền Nam, An Giang, Lúa IR50404, Domestic, 4200, VND/kg
```
**Ý nghĩa**: Ngày 25/8/2019, giá lúa giống IR50404 tại An Giang là 4,200 đồng/kg.

---

## V. CHIẾN LƯỢC XÂY DỰNG 50K DÒNG

### 1. Phân bổ số dòng ước tính

| Dataset | Ước tính | % | Ghi chú |
|---------|----------|---|---------|
| Production | 12,000 | 24% | Nhiều loại cây, vùng miền, metrics |
| Livestock | 13,000 | 26% | Nhiều dịch bệnh, theo tháng |
| Trade | 14,000 | 28% | Nhiều thị trường, sản phẩm |
| Market Price | 11,000 | 22% | Giá theo tháng, vùng |
| **Tổng** | **50,000** | **100%** | |

### 2. Cách đạt được 50K dòng

#### **Chiến lược "Điền đầy" dữ liệu**:

1. **Temporal Granularity** (Chi tiết hóa thời gian):
   - Hiện tại: Báo cáo theo tháng (~28 báo cáo)
   - Khai thác: Mỗi báo cáo tháng chứa dữ liệu lũy kế, vụ mùa, dự báo
   - **Mở rộng**: Từ 1 giá trị tháng → 3-4 giá trị (đầu tháng, cuối tháng, lũy kế)

2. **Spatial Granularity** (Chi tiết hóa không gian):
   - Hiện tại: Dữ liệu theo vùng (ĐBSCL, ĐBSH, Miền Bắc...)
   - **Mở rộng**: Tách ra theo tỉnh (63 tỉnh)
   - Ví dụ: "ĐBSCL: 10.95 triệu tấn" → "An Giang: 2.74 triệu tấn, Đồng Tháp: 3.19 triệu tấn..."

3. **Metric Expansion** (Mở rộng chỉ số):
   - Từ 1 số liệu → Tính toán thêm các chỉ số phụ
   - Ví dụ: Có "Diện tích" và "Sản lượng" → Tính "Năng suất"
   - Có "Kim ngạch" và "Khối lượng" → Tính "Giá bình quân"

4. **Cross-Referencing** (Tham chiếu chéo):
   - Dữ liệu từ bảng biểu khác nhau trong cùng 1 báo cáo
   - Ví dụ: "Xuất khẩu gạo theo thị trường" + "Giá gạo xuất khẩu" → 2 dòng riêng

### 3. Công thức tính số dòng

```
Số dòng = Số năm × Số tháng × Số sản phẩm × Số vùng × Số metrics

Ví dụ Dataset 1 (Production):
= 15 năm × 10 tháng (trung bình có data) × 8 loại cây × 6 vùng × 3 metrics
= 21,600 dòng (có thể lọc xuống ~12,000)
```

---

## VI. TĂNG CƯỜNG DỮ LIỆU (DATA AUGMENTATION)

### 1. Filled Missing Data (Điền dữ liệu thiếu)

**Phương pháp**:
- **Forward Fill**: Nếu tháng 2 thiếu dữ liệu → dùng data tháng 1
- **Interpolation**: Nếu có tháng 1 và tháng 3 → tính trung bình cho tháng 2
- **Seasonal Pattern**: Lúa Đông Xuân thường thu hoạch tháng 4-5 → điền vào các năm thiếu

**Ví dụ**:
```
Năm 2010: Chỉ có báo cáo tháng 12
→ Interpolate từ 2009 và 2011 để ước tính tháng 1-11/2010
```

### 2. Derived Metrics (Tính toán metrics từ dữ liệu có)

**Công thức**:
- Năng suất = Sản lượng / Diện tích
- Tốc độ tăng trưởng (%) = (Năm nay - Năm trước) / Năm trước × 100
- Tỷ trọng thị phần (%) = Kim ngạch thị trường X / Tổng kim ngạch

**Ví dụ**:
```
Có: Sản lượng gạo = 4.67 triệu tấn, Kim ngạch = 2.869 tỷ USD
→ Tính: Giá bình quân = 2,869,000,000 / 4,670,000 = 614 USD/tấn
```

### 3. Regional Breakdown (Tách dữ liệu theo vùng)

**Phương pháp**:
- Dùng tỷ lệ phân bổ từ các năm có dữ liệu chi tiết
- Ví dụ: ĐBSCL chiếm 65% sản lượng lúa cả nước → Áp dụng cho các năm khác

**Ví dụ**:
```
Cả nước: 38.63 triệu tấn lúa
→ ĐBSCL: 38.63 × 65% = 25.1 triệu tấn
→ ĐBSH: 38.63 × 20% = 7.7 triệu tấn
```

### 4. Temporal Smoothing (Làm mượt dữ liệu theo thời gian)

**Phương pháp**:
- Moving Average: Trung bình trượt 3 tháng
- Seasonal Decomposition: Tách xu hướng, mùa vụ, nhiễu

**Ví dụ**:
```
Giá lúa tháng 1: 4,000 đ/kg
Giá lúa tháng 2: 4,500 đ/kg  
Giá lúa tháng 3: 4,200 đ/kg
→ Moving Avg tháng 2 = (4000 + 4500 + 4200) / 3 = 4,233 đ/kg
```

---

##VII. KẾ HOẠCH THỰC HIỆN

### Phase 2: LLM Parsing (2-3 tuần)

**Tuần 1-2**: Thiết kế prompt và test
- Mỗi người thiết kế prompt cho dataset của mình
- Test với 2-3 file mẫu từ các giai đoạn khác nhau
- Review và điều chỉnh

**Tuần 3**: Batch processing
- Chạy LLM parse toàn bộ 28 file
- Validate và fix lỗi
- Merge vào dataset tổng

### Phase 3: Chuẩn hóa (1 tuần)

- Xử lý NaN, outliers
- Chuẩn hóa tên sản phẩm, địa danh
- Kiểm tra logic data
- Export CSV cuối cùng

### Phase 4: Data Mining (2-3 tuần)

- EDA: Exploratory analysis
- Feature engineering
- Modeling: Classification, Clustering, Time series
- Visualization

---

## VIII. VÍ DỤ PROMPT CHO LLM

### Prompt cho Dataset 1 (Production):

```
Bạn là chuyên gia phân tích báo cáo nông nghiệp. Hãy trích xuất dữ liệu sản xuất trồng trọt từ báo cáo sau:

**Yêu cầu**:
1. Trích xuất các metrics: Diện tích, Năng suất, Sản lượng
2. Cho các loại cây: Lúa (Đông Xuân, Hè Thu, Mùa), Ngô, Khoai lang, Lạc, Đậu tương, Rau
3. Phân chia theo vùng: Miền Bắc, ĐBSH, Miền Nam, ĐBSCL
4. Chuẩn hóa đơn vị: Diện tích (ha), Năng suất (tạ/ha), Sản lượng (tấn)

**Output format** (CSV):
Date, Region, Product, Season, Metric, Value, Unit

**Lưu ý**:
- "Lúa đông xuân" = "Đông Xuân"
- "ĐBSCL" bao gồm: An Giang, Cần Thơ, Đồng Tháp, Kiên Giang, Long An, Tiền Giang, Bến Tre, Vĩnh Long, Trà Vinh, Sóc Trăng, Bạc Liêu, Cà Mau, Hậu Giang
- Chuyển đổi: 1 nghìn ha = 1000 ha, 1 ngàn tấn = 1000 tấn

**Báo cáo**:
[Paste nội dung báo cáo markdown]
```

---

## IX. KẾT LUẬN

### Tổng kết:

1. **28 file báo cáo** từ 15 năm đã được phân loại thành **4 giai đoạn format** khác nhau
2. **Đề xuất 4 dataset**: Production, Livestock, Trade, Market Price
3. **Mục tiêu 50,000 dòng** là khả thi với chiến lược kết hợp:
   - Temporal granularity (mở rộng thời gian)
   - Spatial granularity (chi tiết hóa vùng miền)
   - Metric expansion (tính toán thêm chỉ số)
   - Data augmentation (điền thiếu, làm mượt)

### Ưu điểm mô hình:

- **Modularity**: 4 dataset độc lập, dễ merge
- **Scalability**: Dễ thêm năm mới
- **Flexibility**: LLM có thể adapt với format thay đổi
- **Comprehensive**: Bao phủ toàn bộ chuỗi giá trị nông nghiệp

### Điểm lưu ý:

- Chất lượng data phụ thuộc vào LLM prompt engineering
- Cần validation kỹ để tránh hallucination
- Dữ liệu thiếu cần điền cẩn thận (không làm méo xu hướng)

---

**Tài liệu này** sẽ được dùng làm blueprint cho Phase 2: LLM Parsing.
