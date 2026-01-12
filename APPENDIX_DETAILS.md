# Phân Tích Chi Tiết Từng File Phụ Lục (2008-2022)

Tài liệu này đi sâu vào chi tiết nội dung từng file trong thư mục `markdown_output`. Mục tiêu là xác định chính xác các bảng dữ liệu (Tables), chủ đề (Themes) và các trường thông tin (Data Points) có sẵn để phục vụ việc map vào schema chung.

---

## Năm 2008
### 📂 `markdown_output/2008/Phuluc_12_2008.md`
**Loại**: Phụ lục bảng biểu chi tiết (Format Cổ điển)

**Chủ đề chính**:
1.  **Trồng trọt**: Số liệu chi tiết về Lúa (Đông xuân, Hè thu, Mùa) và các cây màu.
2.  **Chăn nuôi**: Tổng đàn và sản lượng thịt hơi.
3.  **Lâm nghiệp**: Trồng rừng và khai thác.
4.  **Thủy sản**: Nuôi trồng và Khai thác.
5.  **Xuất khẩu**: Kim ngạch và khối lượng các mặt hàng chính.

**Chi tiết các bảng dữ liệu (Tables)**:

| Tiêu đề Bảng / Nội dung | Granularity (Chi tiết) | Các cột (Columns) | Ghi chú |
| :--- | :--- | :--- | :--- |
| **1. Tiến độ sản xuất lúa** | Tỉnh/Thành phố | Diện tích gieo cấy (Nghìn ha), Diện tích thu hoạch, Năng suất (Tạ/ha), Sản lượng (Nghìn tấn) | Chia theo vụ: Đông Xuân, Hè Thu, Mùa |
| **2. Cây trồng khác (Màu)** | Tỉnh/Thành phố | Diện tích (Ngô, Khoai lang, Sắn, Lạc, Đậu tương, Rau...) | Số liệu gieo trồng hoặc thu hoạch |
| **3. Chăn nuôi** | Vùng / Tỉnh | Tổng đàn (Trâu, Bò, Lợn, Gia cầm) | Đơn vị: Nghìn con |
| **4. Lâm nghiệp** | Tỉnh | Diện tích trồng rừng tập trung, Sản lượng gỗ khai thác | Đơn vị: Ha, m3 |
| **5. Thủy sản** | Tỉnh | Tổng sản lượng, Sản lượng Cá, Tôm | Đơn vị: Tấn |

**Đánh giá độ khả thi**: 
- **Cao**. Bảng biểu rõ ràng, tuy nhiên cần xử lý header phức tạp (merge cell).

---

## Năm 2009
### 📂 `markdown_output/2009/Phuluc_T12_2009.md`
**Loại**: Phụ lục bảng biểu (Tiếp nối format 2008)

**Chi tiết**:
- Cấu trúc tương tự 2008.
- **Điểm mới**: Có thể xuất hiện thêm số liệu so sánh (%) so với cùng kỳ năm trước ngay trong bảng.

---

---

## Năm 2012
### 📂 `markdown_output/2012/Phuluc_12_2012.md`
**Loại**: Phụ lục bảng biểu chi tiết (Format Chuyển tiếp)

**Chủ đề chính & Bảng dữ liệu**:
1.  **Tổng hợp SX Nông nghiệp**: Số liệu so sánh cùng kỳ (Gieo cấy lúa, Thu hoạch lúa mùa, Cây vụ đông).
2.  **Cây vụ đông Miền Bắc**: Chi tiết đến Tỉnh các loại cây: Ngô, Khoai lang, Khoai tây, Lạc, Đậu tương, Rau đậu.
3.  **Lúa & Màu Miền Nam**: Lúa mùa, Xuống giống Đông Xuân, Cây màu.
4.  **Cây hàng năm (Cả nước)**: So sánh 2011 vs 2012 (Diện tích, Năng suất, Sản lượng) cho Lúa, Ngô, Khoai, Sắn, Mía, Thuốc lá, Lạc, Đậu tương...
5.  **Cây lâu năm**: Chè, Cà phê, Cao su, Hồ tiêu, Điều... (DT gieo trồng, DT cho sản phẩm, Năng suất, Sản lượng).
6.  **Lâm nghiệp**: Trồng rừng, Chăm sóc, Khai thác gỗ/củi, Giá trị sản xuất (giá 1994 và 2010).
7.  **Xuất Nhập khẩu**: Chi tiết theo mặt hàng và thị trường (Top 10 thị trường cho Gạo, Cà phê, Cao su...).

**Ghi chú**: 
- Dữ liệu Xuất khẩu/Nhập khẩu rất chi tiết theo quốc gia (Lượng & Giá trị).
- Có bảng "Thị phần" xuất khẩu.

---

## Năm 2013
### 📂 `markdown_output/2013/Phuluc_10_2013_fe.md`
**Loại**: Phụ lục bảng biểu (Format tương tự 2012)

**Chi tiết đáng chú ý**:
- **Bảng 1**: Tổng hợp tiến độ (Thu hoạch lúa mùa MB, Gieo cấy Thu Đông ĐBSCL...).
- **Bảng 2**: Chi tiết vụ Đông Miền Bắc theo Tỉnh (Ngô, Khoai, Đậu tương...).
- **Bảng 3**: Lúa & Màu Miền Nam (Hè Thu, Thu Đông, Mùa).
- **Xuất nhập khẩu**: Tiếp tục duy trì bảng chi tiết thị trường (Top 10) và kim ngạch.
- **Lâm nghiệp**: Số liệu 10 tháng đầu năm.

---

## Năm 2014
### 📂 `markdown_output/2014/phuluc_10_2014_f.md`
**Loại**: Phụ lục bảng biểu

**Điểm mới / Chi tiết**:
- **Thủy sản**: Có thêm bảng chi tiết "Diện tích và Sản lượng Tôm" (Tôm càng xanh, Tôm sú, Tôm thẻ) và "Cá Tra" tại ĐBSCL. -> **Quan trọng cho Dataset Thủy sản**.
- **Cây công nghiệp & Rau đậu vụ Đông Xuân (Miền Nam)**: Chi tiết diện tích theo tỉnh.
- **Xuất nhập khẩu**: Vẫn chi tiết theo thị trường.

**Data Points cốt lõi**:
- Diện tích/Năng suất/Sản lượng (Lúa, Màu, Cây CN).
- Tổng đàn (Chăn nuôi - *Cần check kỹ xem có bảng chăn nuôi riêng không vì file này tập trung nhiều vào Trồng trọt/Lâm nghiệp/Thủy sản/XNK*).
- Kim ngạch/Lượng XNK theo thị trường.

---

## Năm 2015
### 📂 `markdown_output/2015/phuluc_T12_2015-f.md`
**Loại**: Phụ lục bảng biểu chi tiết

**Điểm mới / Chi tiết**:
- **Dịch hại (Sâu bệnh)**: Xuất hiện bảng chi tiết "Diện tích và phân bố dịch hại trên cây lúa" (Rầy nâu, Đạo ôn, Bạc lá...) phân theo vùng (chủ yếu ĐBSCL). -> **Dataset Dịch bệnh**.
- **Lâm nghiệp**: Chi tiết Diện tích trồng mới, Chăm sóc, Khoán bảo vệ theo Tỉnh.
- **Chăn nuôi**: Số liệu tại thời điểm 1/10 (Tổng đàn & Sản lượng).

**Data Points cốt lõi**:
- Giá trị sản xuất (Nông/Lâm/Thủy sản).
- Tiến độ & Sản lượng cây trồng (Lúa, Màu, Cây CN).
- Diện tích nhiễm sâu bệnh (Ha).
- Lâm nghiệp (Ha trồng mới, m3 gỗ).

---

## Năm 2016
### 📂 `markdown_output/2016/Phuluc_T12_2016.md`
**Loại**: Phụ lục bảng biểu chi tiết

**Chi tiết**:
- Cấu trúc ổn định, giống 2015.
- **Giá trị sản xuất**: Ghi rõ theo giá so sánh 2010.
- **Dịch hại**: Tiếp tục theo dõi chi tiết trên lúa (Tháng 12).

---

## Năm 2017
### 📂 `markdown_output/2017/Phuluc_T12_2017.md`
**Loại**: Phụ lục bảng biểu chi tiết

**Điểm mới / Chi tiết**:
- **Thủy sản**: Bổ sung các phụ lục chi tiết (PL 13, 14):
    - Sản lượng nuôi trồng thủy sản chi tiết theo Tỉnh (Cả nước & Top tỉnh trọng điểm).
    - Diện tích & Sản lượng Tôm (Tôm sú, Tôm thẻ...).
- **Dịch hại**: Cập nhật đến cuối tháng 12/2017.

**Data Points cốt lõi**:
- Sản lượng Thủy sản chi tiết Tỉnh (Quan trọng cho Dataset Thủy sản).
- Các chỉ số Trồng trọt, Chăn nuôi, Lâm nghiệp duy trì như 2015-2016.

---

## Năm 2018
### 📂 `markdown_output/2018/Phuluc_T10_2018.md`
**Loại**: Phụ lục kết quả sản xuất trồng trọt, dịch hại và lâm nghiệp (Số liệu tháng 10)

**Chủ đề chính & Bảng dữ liệu**:
1.  **Sản xuất lúa**: Tổng hợp diện tích, năng suất, sản lượng cho các vụ: Đông xuân, Hè thu, Vụ mùa, Thu đông. Lũy kế 10 tháng.
2.  **Chi tiết vụ Mùa/Hè thu phía Bắc**: Theo tỉnh, bao gồm cả lúa nương.
3.  **Chi tiết Miền Nam**: Tiến độ thu hoạch lúa Hè thu và xuống giống lúa Mùa, Thu đông theo tỉnh.
4.  **Cây màu/Cây công nghiệp hàng ngắn ngày**: Diện tích Ngô, Khoai lang, Sắn, Lạc, Đậu tương... theo tỉnh (Miền Bắc & Miền Nam riêng).
5.  **Dịch hại (Pests)**: Diện tích nhiễm và phân bố của các đối tượng dịch hại lúa (Đạo ôn, Rầy nâu, Bạc lá, Chuột...).
6.  **Lâm nghiệp**: Các chỉ tiêu trồng rừng mới, chăm sóc, khoán bảo vệ phân theo mục đích sử dụng và chi tiết đến từng Tỉnh.

**Ghi chú**: 
- Số liệu rất chi tiết về tiến độ thu hoạch và gieo cấy theo vụ.
- Bảng dịch hại cung cấp phân bố tập trung theo mã tỉnh.

---

## Năm 2019
### 📂 `markdown_output/2019/Phuluc_T07_2019.md` & `Phuluc_T10_2019.md`
**Loại**: Phụ lục báo cáo định kỳ tháng 7 và tháng 10.

**Chi tiết đáng chú ý**:
- **Trồng trọt**: 
    - Phụ lục T07 tập trung vào tiến độ gieo cấy lúa Mùa phía Bắc và thu hoạch lúa Hè thu Miền Nam.
    - Phụ lục T10 cung cấp số liệu lũy kế 10 tháng, so sánh chi tiết năng suất và sản lượng lúa.
- **Cây hàng năm khác**: Sắn, Lạc, Đậu tương, Rau đậu được chi tiết diện tích gieo trồng đến cấp tỉnh.
- **Dịch hại**: Tiếp tục duy trì bảng theo dõi diện tích nhiễm dịch hại trên lúa.
- **Lâm nghiệp**: Số liệu 7 và 10 tháng về diện tích rừng tập trung theo mục đích sử dụng (Phòng hộ, Đặc dụng, Sản xuất) theo tỉnh.

**Data Points cốt lõi**:
- Tiến độ & Kết quả sản xuất lương thực (Lúa, Ngô).
- Cơ cấu diện tích cây công nghiệp ngắn ngày.
- Tình hình dịch hại cây trồng.
- Hiện trạng trồng rừng địa phương.

---

## Năm 2020
### 📂 `markdown_output/2020/Baocao_T11_2020.md`
**Loại**: Báo cáo tổng hợp tháng 11 (bao gồm bảng số liệu tích hợp).

**Bối cảnh & Dữ liệu nổi bật**:
- **Tác động kép**: Ảnh hưởng của dịch COVID-19 và thiên tai liên tiếp tại miền Trung.
- **Trồng trọt**: Số liệu diện tích, năng suất, sản lượng lúa chi tiết theo các trà (Mùa, Thu Đông, Đông Xuân). Lưu ý sự sụt giảm diện tích gieo cấy lúa cả nước (~352 nghìn ha).
- **Chăn nuôi**: Đàn lợn hồi phục mạnh (+12,2% so với cùng kỳ) sau dịch tả lợn châu Phi.
- **Thủy sản**: Điểm nhấn là sự tăng trưởng mạnh của tôm thẻ chân trắng (+15,2%) phục vụ xuất khẩu.
- **Đầu tư công**: Bảng chi tiết giải ngân vốn NSNN và trái phiếu chính phủ cho các dự án nông nghiệp.

---

## Năm 2021
### 📂 `markdown_output/2021/Baocao_T07_2021.md`
**Loại**: Báo cáo tình hình tháng 7 và 7 tháng đầu năm.

**Nội dung trọng tâm**:
- **COVID-19**: Tập trung vào việc duy trì chuỗi cung ứng nông sản trong điều kiện giãn cách tại các tỉnh phía Nam.
- **Trồng trọt**: Kết quả vụ Đông Xuân đạt kỷ lục về sản lượng (20,5 triệu tấn).
- **Dịch bệnh**: Xuất hiện dịch Viêm da nổi cục trên gia súc và các biến chủng cúm gia cầm A/H5N8.
- **Thị trường**: Biến động giá vật tư nông nghiệp và giá các mặt hàng xuất khẩu (Cà phê, Cao su tăng; Lúa gạo, Hồ tiêu biến động).

---

## Năm 2022
### 📂 `markdown_output/2022/Baocao_T11_2022.md`
**Loại**: Báo cáo tổng kết 11 tháng và nhiệm vụ trọng tâm tháng 12.

**Điểm mới & Xu thế**:
- **Chuyển đổi tư duy**: Nhấn mạnh việc chuyển từ "Sản xuất nông nghiệp" sang "Kinh tế nông nghiệp".
- **Xuất khẩu**: Đạt cột mốc ấn tượng (~49 tỷ USD trong 11 tháng). Thủy sản (Cá tra) tăng trưởng đột phá (+61,9%).
- **Quản lý**: Đẩy mạnh cấp mã số vùng trồng (traceability) và cơ sở đóng gói phục vụ xuất khẩu chính ngạch sang Trung Quốc và Hoa Kỳ (Bưởi tươi).
- **Lâm nghiệp**: Tỷ lệ che phủ rừng duy trì ổn định 42,02%. Thu dịch vụ môi trường rừng vượt kế hoạch.

**Data Points cốt lõi**:
- Kim ngạch xuất nhập khẩu chi tiết theo nhóm hàng.
- Tình hình chuyển đổi diện tích lúa kém hiệu quả sang cây trồng khác/thủy sản.
- Kết quả xây dựng Nông thôn mới và chương trình OCOP (vượt kế hoạch).

---

## Tổng kết chung giai đoạn 2012 - 2022
Qua việc rà soát các phụ lục và báo cáo, có thể thấy sự chuyển dịch rõ rệt:
1.  **Độ chi tiết**: Từ các bảng thống kê thô (2012-2014) sang các báo cáo tích hợp phân tích sâu hơn (2020-2022).
2.  **Lĩnh vực mới**: Bổ sung theo dõi Dịch hại lúa (từ 2015), Thủy sản chi tiết tỉnh (từ 2017) và Mã số vùng trồng/Kinh tế tuần hoàn (2022).
3.  **Khả năng khai thác**: Các tệp `markdown` cung cấp cấu trúc bảng ổn định, phù hợp để crawler dữ liệu phục vụ các bài toán Data Mining về dự báo sản lượng và phân tích thị trường.

*(Hoàn thành rà soát sơ bộ danh mục phụ lục)*

