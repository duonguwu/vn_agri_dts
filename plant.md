📋 Kế hoạch Trích xuất Dataset (Agri-Data Mining)
Giai đoạn 1: Chuẩn bị & Chia nhỏ (Segmentation)

Phân loại Table: Xác định các loại bảng theo "Theme" (Trồng trọt, Chăn nuôi, Thủy sản, Lâm nghiệp, XNK) trong từng file Phụ lục.
Chia nhỏ dữ liệu: Do các file Markdown khá dài (nhiều phụ lục), mình sẽ chia nhỏ theo từng Phụ lục (Phụ lục 1, Phụ lục 2,...) để gửi cho LLM xử lý tránh quá tải ngữ cảnh (context window) và nhầm lẫn hàng/cột.

Giai đoạn 2: Trích xuất bằng LLM (Extraction)

Sử dụng Strategy A (cho 2008-2019): Tập trung vào việc làm phẳng (flatten) các tiêu đề phân cấp.
Ví dụ: Dòng "Hà Nội" thuộc cụm "Đồng bằng sông Hồng" sẽ được gán location_name: "Hà Nội" và region_id: "Red_River_Delta".
Áp dụng Quy tắc chuẩn hóa ngay khi Prompt:
Đổi dấu phân cách thập phân (, thành .).
Nhân hệ số cho đơn vị (1000 ha -> ha, triệu USD -> USD).
Xử lý giá trị trống: Chuyển - hoặc " thành null.

Giai đoạn 3: Hậu xử lý & Kiểm soát chất lượng (Post-processing)

Hợp nhất (Merging): Gộp các tệp JSON kết quả thành một Dataset duy nhất.
Kiểm tra tính nhất quán (Sanity Check):
Kiểm tra xem tổng các Tỉnh có bằng dữ liệu Vùng/Cả nước không.
Chuẩn hóa tên Tỉnh bằng script Python (ví dụ: "T.P Hồ Chí Minh" -> "TP Hồ Chí Minh").
Tạo Record ID: Sinh mã duy nhất theo công thức YEAR_MONTH_LOC_ITEM_METRIC để tránh trùng lặp.

Giai đoạn 4: Xuất bản Dataset

Format: Chuyển đổi từ JSON sang CSV (dạng bảng dọc - Long Format) để sẵn sàng cho các bài toán Data Mining như dự báo chuỗi thời gian hay phân cụm.
