# Changelog - Backend

Tất cả các thay đổi của module Backend sẽ được ghi lại trong tài liệu này.

---

## [1.23.0] - 2026-10-10

### Đã hoàn thành (Added & Enhanced)
- **Model YeuCauHoTro (`yeu_cau_ho_tro.py`)**:
  - Tạo mới ORM Model [YeuCauHoTro](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/models/yeu_cau_ho_tro.py) ánh xạ bảng `yeu_cau_ho_tro` (`ma_yeu_cau`, `ma_ho_so`, `loai_yeu_cau`, `noi_dung`, `phan_hoi_hr`, `trang_thai`).
  - Thiết lập quan hệ hai chiều `ho_so` và `danh_sach_yeu_cau_ho_tro` trong [ho_so.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/models/ho_so.py).
  - Export tại [database/models/__init__.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/models/__init__.py).
- **Dịch vụ Email Thông báo (`email_service.py`)**:
  - Bổ sung hàm `send_support_request_email` gửi email thông báo kết quả xử lý yêu cầu (kèm trích dẫn phản hồi của HR) cho sinh viên qua SMTP.
- **Pydantic Schemas (`schemas.py`)**:
  - `SupportRequestStatusUpdate`: Tiếp nhận trạng thái cập nhật (chỉ cho phép `DaXuLy` hoặc `TuChoi`) và trường phản hồi `phan_hoi_hr`.
  - `SupportRequestItemData` & `SupportRequestResponse`: Schema response chuẩn RESTful (HTTP 200 OK).
- **Endpoint Cập Nhật Yêu Cầu Hỗ Trợ (`PATCH /api/v1/support-requests/{id}`)**:
  - Thêm route tại [main.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/main.py) cho phép HR cập nhật trạng thái yêu cầu (`DaXuLy` hoặc `TuChoi`), lưu ghi chú phản hồi vào `phan_hoi_hr`.
  - Tích hợp `fastapi.BackgroundTasks` tự động gửi email thông báo cho sinh viên mà không làm nghẽn tiến trình API.
  - Bắt trọn vẹn ngoại lệ: `HTTP 404 Not Found` (khi ID yêu cầu không tồn tại), `HTTP 400 Bad Request` / `422 Unprocessable Entity` (khi trạng thái không hợp lệ).
- **Đồng bộ CSDL & Thiết kế**:
  - Cập nhật sơ đồ Mermaid ERD và Bảng 2.14 trong [DATABASE_DESIGN.md](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/DATABASE_DESIGN.md).
  - Bổ sung seed data cho bảng `yeu_cau_ho_tro` trong [init_db.sql](file:///d:/CodeGym/TTCS_T926_K16C2_N2/script/database/init_db.sql).
  - Cập nhật fixture SQLite trong [conftest.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/tests/conftest.py).
- **Kiểm thử tự động**:
  - Tạo mới bộ test [test_support_requests.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/tests/test_support_requests.py) gồm 6 test cases bao phủ cập nhật trạng thái DaXuLy, TuChoi, gửi email nền, bắt lỗi 404/422 -> **6/6 PASS 100%**.
  - Kiểm thử hồi quy toàn bộ cụm email -> **12/12 PASS 100%**.

---

## [1.22.0] - 2026-10-09

### Đã hoàn thành (Added & Enhanced)
- **Pydantic Schemas (`FacultyReportResponse`, `FacultyReportData`, `FacultyReportSummary`, `FacultyUniversityStat`, `FacultyMajorStat`, `FacultyInternBreakdownItem`)**:
  - Khai báo schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py).
  - Chuẩn hóa cấu trúc gom nhóm hai chiều (Trường × Chuyên ngành), phân cấp theo trường đại học, phân cấp theo chuyên ngành, danh sách phẳng chi tiết và khối `summary` KPI tổng quan.
- **Endpoint Thống Kê Sinh Viên Theo Trường & Chuyên Ngành (`GET /api/v1/reports/interns-by-faculty`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) kết hợp bảng `truong_dai_hoc` và `ho_so_thuc_tap` qua `ma_truong`.
  - Thực hiện gom nhóm hai chiều theo `ten_truong` và `chuyen_nganh`, tính toán tổng số lượng sinh viên và tỷ lệ % phân bổ.
  - Hỗ trợ các bộ lọc linh hoạt: `ma_truong`, `ten_truong`, `chuyen_nganh`, `ma_chuong_trinh`, `trang_thai_xet_duyet`, `trang_thai_thuc_tap`.
  - Bắt trọn vẹn ngoại lệ theo chuẩn RESTful: `HTTP 404` (khi mã trường hoặc mã chương trình không tồn tại), `HTTP 400` (khi sai trạng thái xét duyệt hoặc thực tập), `HTTP 422` (khi tham số vi phạm validation).
- **Kiểm thử tự động (Unit Test & Regression Test)**:
  - Tạo mới bộ test [tests/test_report_interns_by_faculty.py](file:///d:/clone/ttcs/backend/tests/test_report_interns_by_faculty.py) gồm 13 test cases bao phủ gọi mặc định, lọc theo từng tiêu chí, bắt lỗi 400/404/422, gom nhóm nhiều sinh viên tính % và trường hợp dữ liệu rỗng -> **13/13 PASS 100%**.
  - Kiểm tra hồi quy toàn bộ cụm report -> **54/54 PASS 100%**.

---

## [1.21.0] - 2026-10-07

### Đã hoàn thành (Added & Enhanced)
- **Pydantic Schemas (`MentorCreate`, `MentorItemData`, `MentorResponse`)**:
  - Khai báo schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py).
  - Tự động validate họ tên, chuẩn hóa email, ràng buộc mật khẩu (tối thiểu 6 ký tự), kiểm tra định dạng số điện thoại Việt Nam và hỗ trợ mã phòng ban.
- **Endpoint Tạo Tài Khoản Người Hướng Dẫn (`POST /api/v1/mentors`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) tiếp nhận thông tin người hướng dẫn, tạo tài khoản vào bảng `nguoi_dung` với `vai_tro = "Mentor"`, `trang_thai = "HoatDong"`.
  - Băm mật khẩu bảo mật bằng bcrypt thông qua `security.get_password_hash`.
  - Kiểm tra chống trùng lặp email và số điện thoại trong hệ thống (`HTTP 400 Bad Request`).
  - Kiểm tra tính tồn tại của phòng ban liên kết theo `ma_phong_ban` (`HTTP 400 Bad Request` nếu không tồn tại).
  - Trả về mã `HTTP 201 Created` kèm thông tin tài khoản (ẩn mật khẩu băm).
- **Kiểm thử tự động (Unit Test & Regression Test)**:
  - Tạo mới bộ test [tests/test_mentors.py](file:///d:/clone/ttcs/backend/tests/test_mentors.py) với 11 test cases bao phủ tạo thành công (đủ trường / tối giản), băm mật khẩu & đăng nhập, trùng email, trùng SĐT, sai phòng ban và các lỗi validation -> **11/11 PASS 100%**.
  - Kiểm thử hồi quy toàn bộ test suite của Backend: **285/285 test cases PASS 100%**.

---

## [1.20.0] - 2026-10-06

### Đã hoàn thành (Added & Enhanced)
- **Thiết kế Model Phụ Cấp Thực Tập Sinh (`PhuCap`)**:
  - Tạo mới ORM model [phu_cap.py](file:///d:/clone/ttcs/backend/database/models/phu_cap.py) ánh xạ bảng `phu_cap` với các trường: `ma_phu_cap` (PK), `ma_ho_so` (FK), `thang_nam` (`YYYY-MM`), `so_tien` (`Numeric(12, 2)`), `trang_thai_chi_tra` (`DaChiTra`, `ChuaChiTra`).
  - Thiết lập quan hệ hai chiều `ho_so` và `danh_sach_phu_cap` với model [ho_so.py](file:///d:/clone/ttcs/backend/database/models/ho_so.py).
  - Export tại [database/models/__init__.py](file:///d:/clone/ttcs/backend/database/models/__init__.py).
- **Pydantic Schemas (`AllowanceItem`, `AllowanceSummary`, `AllowanceDetailData`, `AllowanceResponse`)**:
  - Khai báo các schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py) chuẩn hóa dữ liệu tài chính cho Client.
  - Cung cấp khối `summary` tự động thống kê tổng tiền đã nhận (`tong_tien_da_nhan`), tổng tiền đang chờ giải ngân (`tong_tien_cho_giai_ngan`), tổng toàn bộ (`tong_tien_phu_cap`) và số lượng khoản của mỗi loại.
- **Endpoint Truy Vấn Danh Sách Phụ Cấp (`GET /api/v1/interns/{id}/allowances`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) truy vấn danh sách phụ cấp theo `ma_ho_so` (`id`).
  - Tự động kiểm tra tính tồn tại của hồ sơ thực tập sinh (`HTTP 404 Not Found` nếu không tìm thấy).
  - Tự động tính toán tổng số tiền đã nhận và các khoản đang chờ giải ngân trả về cho Client theo thứ tự tháng giảm dần.
- **Đồng bộ Cơ sở dữ liệu & Seed Data**:
  - Bổ sung lệnh INSERT dữ liệu mẫu cho bảng `phu_cap` vào [init_db.sql](file:///d:/clone/ttcs/script/database/init_db.sql).
  - Nạp thành công CSDL MySQL thực tế thông qua `script/init_db.py`.
  - Cập nhật hàm `reseed_sqlite_db()` trong [conftest.py](file:///d:/clone/ttcs/backend/tests/conftest.py).
- **Kiểm thử tự động (Unit Test & Regression Test)**:
  - Tạo mới bộ test [tests/test_intern_allowances.py](file:///d:/clone/ttcs/backend/tests/test_intern_allowances.py) với 5 test cases kiểm tra tính toán tổng tiền, danh sách rỗng, 404 not found, 422 validation -> **5/5 PASS 100%**.
  - Kiểm tra hồi quy với các test cases liên quan -> **PASS 100%**.

---

## [1.19.0] - 2026-10-03

### Đã hoàn thành (Added & Enhanced)
- **Thiết kế Model Ca Làm Việc (`CaLamViec`)**:
  - Tạo mới ORM model [ca_lam_viec.py](file:///d:/clone/ttcs/backend/database/models/ca_lam_viec.py) ánh xạ bảng `ca_lam_viec` với các trường: `ma_ca` (PK), `ten_ca`, `gio_bat_dau`, `gio_ket_thuc`, `cac_ngay_trong_tuan`, `ghi_chu`, `trang_thai`, `ngay_tao`.
  - Cung cấp phương thức `to_dict()` chuẩn hóa định dạng thời gian `HH:MM:SS` trả về cho Client.
  - Export tại [database/models/__init__.py](file:///d:/clone/ttcs/backend/database/models/__init__.py).
- **Pydantic Schemas (`ScheduleCreate`, `ScheduleData`, `ScheduleCreateResponse`)**:
  - Khai báo schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py).
  - Tích hợp validator `@model_validator(mode="after")` kiểm tra logic `gio_ket_thuc > gio_bat_dau` (báo lỗi HTTP 422 nếu giờ kết thúc nhỏ hơn hoặc bằng giờ bắt đầu).
  - Chuẩn hóa trường `ten_ca` (cấm chuỗi rỗng/chỉ chứa khoảng trắng) và trường `cac_ngay_trong_tuan` (hỗ trợ cả mảng `List[str]` và chuỗi `str`).
- **Endpoint Tạo Mới Ca Làm Việc (`POST /api/v1/schedules`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) trả về mã `HTTP 201 Created` kèm thông tin ca làm việc vừa lưu vào CSDL.
- **Đồng bộ Cơ sở dữ liệu & Database Design**:
  - Cập nhật sơ đồ ERD mermaid và bổ sung mục `2.11b. CA_LAM_VIEC (Ca làm việc / Lịch làm việc)` vào [DATABASE_DESIGN.md](file:///d:/clone/ttcs/backend/database/DATABASE_DESIGN.md).
  - Bổ sung câu lệnh DDL `CREATE TABLE IF NOT EXISTS ca_lam_viec` và Seed data mẫu vào [init_db.sql](file:///d:/clone/ttcs/script/database/init_db.sql).
  - Cập nhật hàm `reseed_sqlite_db()` trong [conftest.py](file:///d:/clone/ttcs/backend/tests/conftest.py).
  - Thực thi nạp thành công CSDL MySQL qua script `script/init_db.py`.
- **Kiểm thử tự động (Unit Test & Integration Test)**:
  - Tạo mới bộ test [tests/test_schedules.py](file:///d:/clone/ttcs/backend/tests/test_schedules.py) với 7 test cases kiểm tra thành công, validate logic giờ, tên rỗng, thiếu trường, sai format -> **7/7 PASS 100%**.
  - Chạy kiểm thử hồi quy toàn diện toàn bộ test suite của Backend: **269/269 test cases PASS 100%** không có bất kỳ xung đột nào.

---

## [1.18.0] - 2026-10-02

### Đã hoàn thành (Added & Enhanced)
- **Schemas Pydantic Báo cáo tuần & Phản hồi (`schemas.py`)**:
  - `ReportItemData`: Schema biểu diễn báo cáo tuần chi tiết kèm thông tin sinh viên (`ho_ten_sinh_vien`, `email_sinh_vien`), Mentor phụ trách (`ma_mentor`, `ho_ten_mentor`) và tên nhiệm vụ liên kết (`ten_nhiem_vu`).
  - `ReportPagination`: Thông tin phân trang chuẩn RESTful (`page`, `page_size`, `total_items`, `total_pages`).
  - `ReportListData` & `ReportListResponse`: Schema response cho danh sách báo cáo tuần (`GET /api/v1/reports`).
  - `ReportFeedbackRequest`: Request body cho phản hồi của Mentor (`POST /api/v1/reports/{id}/feedback`) kèm validator loại bỏ khoảng trắng thừa và cấm chuỗi rỗng.
  - `ReportFeedbackResponse`: Response trả về sau khi gửi phản hồi thành công.
- **Endpoint Lấy Danh Sách Báo Cáo Tuần (`GET /api/v1/reports`)**:
  - Hỗ trợ lọc báo cáo theo sinh viên mà Mentor phụ trách thông qua tham số `ma_mentor`.
  - Kiểm tra tính tồn tại của Mentor (`HTTP 404 Not Found` nếu không tìm thấy Mentor).
  - Hỗ trợ các bộ lọc linh hoạt: `ma_ho_so`, `tuan_so`, trạng thái đã nhận xét `da_phan_hoi` (true/false).
  - Hỗ trợ tìm kiếm từ khóa `tu_khoa` trong nội dung công việc, kết quả đạt được hoặc tên sinh viên.
  - Hỗ trợ phân trang chuẩn RESTful (`page`, `page_size`) với sắp xếp mặc định ưu tiên báo cáo mới nhất.
- **Endpoint Gửi Phản Hồi Báo Cáo Tuần (`POST /api/v1/reports/{id}/feedback`)**:
  - Cho phép Mentor gửi nhận xét, phản hồi hoặc ghi nhận trực tiếp vào báo cáo tuần của sinh viên (cập nhật cột `phan_hoi_mentor` trong bảng `bao_cao_tuan`).
  - Kiểm tra sự tồn tại của báo cáo (`HTTP 404 Not Found` nếu sai ID).
  - Kiểm tra thẩm quyền của Mentor: Nếu gửi kèm `ma_mentor`, kiểm tra mentor có tồn tại không và có đúng là người phụ trách sinh viên của báo cáo đó không (`HTTP 403 Forbidden` nếu không có quyền phụ trách).
- **Kiểm thử tự động (Unit Test)**:
  - Bổ sung thêm **17 test cases** vào [tests/test_weekly_reports.py](file:///d:/clone/ttcs/backend/tests/test_weekly_reports.py), nâng tổng số test cases của module báo cáo tuần lên **30/30 PASS 100%**.
  - Kiểm thử toàn diện toàn bộ test suite hệ thống: **262/262 PASS 100%**.

---

## [1.17.0] - 2026-10-01

### Đã hoàn thành (Added & Enhanced)
- **Model Nhiệm Vụ (`NhiemVu`)**:
  - Bổ sung synonym `tieu_de` ánh xạ tới cột `ten_nhiem_vu` trong SQLAlchemy ORM model [NhiemVu](file:///d:/clone/ttcs/backend/database/models/nhiem_vu.py).
  - Cập nhật hàm `to_dict()` trả về đồng thời cả `tieu_de` và `ten_nhiem_vu` để tương thích linh hoạt cho cả Client cũ và mới.
  - Đảm bảo các giá trị mặc định: `tien_do_phantram = 0`, `trang_thai = "Chưa bắt đầu"`.
- **Pydantic Schemas (`TaskCreate`, `TaskDetailData`, `TaskCreateResponse`)**:
  - Thiết kế `TaskCreate` hỗ trợ validate chặt chẽ:
    - Bắt buộc `ma_ho_so > 0`.
    - Hỗ trợ cả trường `tieu_de` và `ten_nhiem_vu` (tự động chuẩn hóa và loại bỏ khoảng trắng thừa).
    - Bắt buộc `han_hoan_thanh` (định dạng YYYY-MM-DD).
    - Validate `tien_do_phantram` trong khoảng `[0, 100]`.
    - Tự động gán mặc định `trang_thai = "Chưa bắt đầu"`.
- **Endpoint Tạo Mới Nhiệm Vụ (`POST /api/v1/tasks`)**:
  - Triển khai endpoint tiếp nhận yêu cầu tạo nhiệm vụ mới tại [main.py](file:///d:/clone/ttcs/backend/main.py).
  - Kiểm tra tính tồn tại của hồ sơ thực tập (`ho_so_thuc_tap`), trả về `HTTP 404 Not Found` nếu không tìm thấy.
  - Trả về mã phản hồi `HTTP 201 Created` kèm dữ liệu nhiệm vụ vừa được tạo.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử [test_create_task.py](file:///d:/clone/ttcs/backend/tests/test_create_task.py) với **10 test cases** kiểm thử đầy đủ các tình huống:
    - Tạo nhiệm vụ thành công với dữ liệu tối thiểu và mặc định (201 Created).
    - Tạo nhiệm vụ thành công với đầy đủ các trường (201 Created).
    - Tạo nhiệm vụ khi truyền alias `ten_nhiem_vu` (201 Created).
    - Bắt lỗi mã hồ sơ không tồn tại (404 Not Found).
    - Bắt lỗi thiếu tiêu đề hoặc tiêu đề rỗng (422 Unprocessable Entity).
    - Bắt lỗi thiếu hạn hoàn thành hoặc sai định dạng ngày (422 Unprocessable Entity).
    - Bắt lỗi mã hồ sơ <= 0 (422 Unprocessable Entity).
    - Bắt lỗi tiến độ phần trăm ngoài khoảng [0, 100] (422 Unprocessable Entity).
  - Toàn bộ 23/23 tests liên quan đến Tasks đều PASS 100%.

---

## [1.16.0] - 2026-10-01


### Đã hoàn thành (Added & Enhanced)
- **Model Đơn Xin Nghỉ Phép (`DonXinNghi`)**:
  - Tạo mới ORM model [DonXinNghi](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/models/don_xin_nghi.py) quản lý bảng `don_xin_nghi`:
    - `ma_don`: Khóa chính (Integer, PK, auto-increment).
    - `ma_ho_so`: Khóa ngoại liên kết hồ sơ thực tập sinh (`ho_so_thuc_tap.ma_ho_so`).
    - `tu_ngay`: Ngày bắt đầu nghỉ phép (Date).
    - `den_ngay`: Ngày kết thúc nghỉ phép (Date).
    - `ly_do`: Lý do chi tiết xin nghỉ (String(255)).
    - `trang_thai`: Trạng thái duyệt đơn, mặc định là `"Chờ duyệt"` (`String(50)`).
    - `ngay_tao`: Thời điểm nộp đơn (DateTime).
  - Thiết lập quan hệ 2 chiều với `HoSoThucTap` (`danh_sach_don_xin_nghi` $\leftrightarrow$ `ho_so`).
  - Cập nhật script khởi tạo CSDL [init_db.sql](file:///d:/CodeGym/TTCS_T926_K16C2_N2/script/database/init_db.sql) và kiến trúc [DATABASE_DESIGN.md](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/DATABASE_DESIGN.md).
- **Endpoint Tạo Mới Đơn Xin Nghỉ Phép (`POST /api/v1/leave-requests`)**:
  - Triển khai endpoint tiếp nhận yêu cầu xin nghỉ phép của thực tập sinh.
  - Tương thích 100% với hợp đồng payload từ Frontend (`frontend/js/nghi_phep.js`).
  - Validate dữ liệu đầu vào nghiêm ngặt:
    - Bắt lỗi `tu_ngay < date.today()` (ngày bắt đầu trong quá khứ) $\rightarrow$ `HTTP 422 Unprocessable Entity`.
    - Bắt lỗi `den_ngay < tu_ngay` (ngày kết thúc trước ngày bắt đầu) $\rightarrow$ `HTTP 422 Unprocessable Entity`.
    - Bắt lỗi mã hồ sơ không tồn tại trong CSDL $\rightarrow$ `HTTP 404 Not Found`.
    - Bắt lỗi mã hồ sơ âm hoặc bằng 0 $\rightarrow$ `HTTP 422 Unprocessable Entity`.
    - Bắt lỗi lý do rỗng hoặc chỉ chứa khoảng trắng $\rightarrow$ `HTTP 422 Unprocessable Entity`.
  - Tự động gán trạng thái mặc định `"Chờ duyệt"`.
  - Tự động tính toán tổng số ngày nghỉ (`so_ngay`) trả về trong response.
  - Trả về mã phản hồi `HTTP 201 Created` kèm thông tin đơn xin nghỉ vừa tạo.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới file kiểm thử [test_leave_requests.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/tests/test_leave_requests.py) với **10 test cases** kiểm thử toàn diện:
    - Tạo đơn nghỉ tương lai thành công (201 Created).
    - Tạo đơn nghỉ trong ngày hôm nay thành công (tu_ngay == den_ngay == today).
    - Kiểm tra trạng thái mặc định "Chờ duyệt" khi không gửi trường trạng thái.
    - Bắt lỗi ngày bắt đầu trong quá khứ (422).
    - Bắt lỗi ngày kết thúc nhỏ hơn ngày bắt đầu (422).
    - Bắt lỗi mã hồ sơ không tồn tại (404).
    - Bắt lỗi mã hồ sơ không hợp lệ (422).
    - Bắt lỗi lý do rỗng (422).
    - Kiểm tra tính tương thích 100% với payload frontend gửi lên.
    - Kiểm tra tạo nhiều đơn liên tiếp cho các thực tập sinh khác nhau.
  - Toàn bộ test suite đạt **235/235 tests PASS 100%**.

---

## [1.15.0] - 2026-10-01

### Đã hoàn thành (Added & Enhanced)
- **Model Điểm danh & Chấm công (`cham_cong`)**:
  - Bổ sung và chuẩn hóa các trường dữ liệu:
    - `thoi_gian_checkin` (DateTime, NULLABLE): Thời điểm quét/ghi nhận vào ca.
    - `thoi_gian_checkout` (DateTime, NULLABLE): Thời điểm quét/ghi nhận kết thúc ca.
    - `trang_thai` (String/Enum): Trạng thái ca làm việc (`DungGio`, `DiMuon`, `VeSom`, `NghiCoPhep`, `NghiKhongPhep`).
    - `ghi_chu` (Text/String): Ghi chú bổ sung lý do, địa điểm công tác hoặc giải trình.
  - Đảm bảo 100% tương thích ngược với API báo cáo tổng hợp chấm công (`GET /api/v1/attendance/reports`) qua các trường legacy `ngay_cham_cong`, `gio_check_in`, `gio_check_out`.
- **Endpoint Check-in Ca làm việc (`POST /api/v1/attendance/check-in`)**:
  - Ghi nhận thời gian check-in của thực tập sinh.
  - Nhận `ma_ho_so`, tùy chọn `thoi_gian_checkin` (mặc định thời điểm hiện tại), `phuong_thuc` (`Web`, `QR`, `The`), `ghi_chu`.
  - Tự động phân loại trạng thái: Đến trước hoặc đúng 08:30:00 là `DungGio`; đến sau 08:30:00 là `DiMuon`.
  - Validate mã hồ sơ hợp lệ (`HTTP 404 Not Found` nếu không tồn tại).
  - Chống trùng lặp: Từ chối check-in nhiều lần trong cùng một ngày (`HTTP 400 Bad Request`).
  - Trả về mã phản hồi `HTTP 201 Created` kèm thông tin bản ghi chi tiết.
- **Endpoint Check-out Ca làm việc (`POST /api/v1/attendance/check-out`)**:
  - Ghi nhận thời gian check-out của thực tập sinh.
  - Nhận `ma_ho_so`, tùy chọn `thoi_gian_checkout` (mặc định thời điểm hiện tại), `ghi_chu`.
  - Yêu cầu phải check-in trước khi check-out (`HTTP 400 Bad Request` nếu chưa check-in trong ngày).
  - Chống trùng lặp check-out (`HTTP 400 Bad Request` nếu đã check-out).
  - Ràng buộc logic thời gian: Không cho phép check-out trước thời điểm check-in (`HTTP 400 Bad Request`).
  - Tự động cập nhật trạng thái nếu về trước 17:00:00 sang `VeSom` (nếu trước đó đúng giờ).
  - Trả về mã phản hồi `HTTP 200 OK` kèm thông tin bản ghi chi tiết.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử `backend/tests/test_attendance_checkin_checkout.py` với **14 test cases**:
    - Check-in đúng giờ và đi muộn thành công.
    - Check-in mặc định thời gian hiện tại khi không truyền payload thời gian.
    - Chặn check-in trùng lặp trong cùng ngày.
    - Bắt lỗi hồ sơ không tồn tại (404) và mã hồ sơ không hợp lệ (422).
    - Check-out đúng giờ và về sớm thành công.
    - Bắt lỗi check-out khi chưa check-in hoặc check-out trùng lặp (400).
    - Bắt lỗi check-out có mốc thời gian sớm hơn check-in (400).
    - Luồng hoàn chỉnh Check-in $\rightarrow$ Check-out trong cùng ca.
  - Toàn bộ test suite đạt **225/225 tests PASS 100%**.

---

## [1.14.0] - 2026-09-30

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Tạo Mới Đánh Giá Thực Tập Sinh (`POST /api/v1/evaluations`)**:
  - Triển khai endpoint tiếp nhận đánh giá thực tập sinh (Giữa kỳ hoặc Cuối kỳ).
  - Lưu đầy đủ các trường: `ma_ho_so`, `ma_nguoi_danh_gia`, `loai_danh_gia`, `diem_ky_nang`, `diem_thai_do`, `nhan_xet`, `de_xuat_tuyen_dung`.
  - Hỗ trợ linh hoạt cả 2 tên trường `nhan_xet` $\leftrightarrow$ `nhan_xet_chi_tiet` và `de_xuat_tuyen_dung` $\leftrightarrow$ `de_xuat_tuyen_chinh_thuc`.
  - Tự động tính điểm trung bình (`diem_trung_binh`) và xếp loại rèn luyện (`xep_loai`: XuatSac, Gioi, Kha, TrungBinh, Yeu).
  - Validate chặt chẽ:
    - Thang điểm `diem_ky_nang` và `diem_thai_do` từ 0.0 đến 10.0 $\rightarrow$ báo lỗi `HTTP 422 Unprocessable Entity` nếu vi phạm.
    - Loại đánh giá `loai_danh_gia` chỉ nhận `GiuaKy` hoặc `CuoiKy` $\rightarrow$ báo lỗi `HTTP 422 Unprocessable Entity` nếu sai giá trị.
    - Kiểm tra khóa ngoại `ma_ho_so` tồn tại $\rightarrow$ trả về `HTTP 404 Not Found`.
    - Kiểm tra khóa ngoại `ma_nguoi_danh_gia` tồn tại $\rightarrow$ trả về `HTTP 400 Bad Request`.
    - Chống trùng lặp đánh giá cùng loại cho một hồ sơ $\rightarrow$ trả về `HTTP 400 Bad Request`.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử `backend/tests/test_create_evaluation.py` với **14 test cases** kiểm thử toàn diện:
    - Tạo đánh giá Giữa kỳ và Cuối kỳ thành công với đầy đủ thông tin (201 Created).
    - Kiểm tra tính toán điểm trung bình cộng và xếp loại rèn luyện chính xác.
    - Kiểm tra chặn trùng lặp cùng loại đánh giá cho 1 hồ sơ (400 Bad Request).
    - Cho phép 1 hồ sơ có cả đánh giá Giữa kỳ và Cuối kỳ (201 Created).
    - Bắt lỗi điểm kỹ năng / thái độ âm hoặc > 10.0 (422).
    - Bắt lỗi loại đánh giá không hợp lệ (422).
    - Bắt lỗi mã hồ sơ không tồn tại (404), người đánh giá không tồn tại (400).
    - Kiểm tra điểm số biên 0.0 (Yếu) và 10.0 (Xuất sắc).
  - Nâng tổng số test cases của toàn hệ thống lên **190/190 PASS 100%**.

---

## [1.13.0] - 2026-09-30

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Báo cáo Tổng hợp Chấm công (`GET /api/v1/attendance/reports`)**:
  - Triển khai endpoint lọc và tổng hợp dữ liệu chấm công của thực tập sinh:
    - Lọc linh hoạt theo `thang` (1-12), `nam`, `ma_phong_ban`.
    - Tối ưu hóa truy vấn thời gian SARGable (`ngay_cham_cong >= start_date AND < end_date`) giúp tận dụng index CSDL và tương thích 100% giữa MySQL và SQLite.
    - Tổng hợp các chỉ số KPI: `so_ngay_di_lam`, `so_lan_di_muon` (tùy biến mốc giờ qua `gio_chuan`, mặc định `08:30:00`), `so_ngay_nghi` (chỉ tính các đơn nghỉ phép ở trạng thái `DaDuyet`).
    - Tính toán KPI tổng quan: `tong_so_thuc_tap_sinh`, `tong_so_ngay_di_lam`, `tong_so_lan_di_muon`, `tong_so_ngay_nghi`, `ty_le_di_muon`, `trung_binh_ngay_cong`.
    - Hỗ trợ phân trang chuẩn `page`, `page_size`, `total_items`, `total_pages`.
- **Cơ sở dữ liệu & Models**:
  - Bổ sung bảng `cham_cong` và `don_nghi_phep` vào file [init_db.sql](file:///d:/clone/ttcs/script/database/init_db.sql) chuẩn theo [DATABASE_DESIGN.md](file:///d:/clone/ttcs/backend/database/DATABASE_DESIGN.md).
  - Bổ sung Seed Data mẫu cho chấm công và đơn xin nghỉ phép vào [init_db.sql](file:///d:/clone/ttcs/script/database/init_db.sql) và [init_db.py](file:///d:/clone/ttcs/script/init_db.py).
  - Tạo model [ChamCong](file:///d:/clone/ttcs/backend/database/models/cham_cong.py) và [DonNghiPhep](file:///d:/clone/ttcs/backend/database/models/don_nghi_phep.py).
  - Khai báo relationships `danh_sach_cham_cong` và `danh_sach_nghi_phep` trong [HoSoThucTap](file:///d:/clone/ttcs/backend/database/models/ho_so.py).
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới `backend/tests/test_attendance_reports.py` với 11 test cases bao phủ:
    - Báo cáo mặc định và theo tháng/năm.
    - Lọc theo phòng ban và xử lý phòng ban không tồn tại (404).
    - Lọc tháng không có dữ liệu (số liệu 0).
    - Tùy chỉnh giờ chuẩn vào làm (`gio_chuan`).
    - Lọc trạng thái đơn nghỉ phép (chỉ tính đơn `DaDuyet`).
    - Phân trang kết quả.
    - Validate dữ liệu đầu vào (tháng ngoài 1-12, năm < 2000, page/page_size <= 0 -> 422).
  - Toàn bộ test suite đạt **162/162 unit tests PASS 100%**.

---

## [1.12.0] - 2026-09-30


### Đã hoàn thành (Added & Enhanced)
- **Endpoint Cập nhật Thời gian Chương trình Thực tập (`PATCH /api/v1/programs/{id}/timeline`)**:
  - Triển khai endpoint cập nhật mốc thời gian `ngay_bat_dau` và `ngay_ket_thuc` cho chương trình thực tập theo `id` (`ma_chuong_trinh`).
  - Xây dựng schema `ProgramTimelineUpdate` và `ProgramTimelineResponse` trong `backend/schemas.py`.
  - Validate chặt chẽ logic thời gian:
    - Bắt buộc cung cấp ít nhất một trường (`ngay_bat_dau` hoặc `ngay_ket_thuc`), trả về `HTTP 422 Unprocessable Entity` nếu body rỗng `{}`.
    - Validate bắt buộc: **ngày kết thúc > ngày bắt đầu** (`ngay_ket_thuc > ngay_bat_dau`).
    - Nếu gửi cả hai ngày và `ngay_ket_thuc <= ngay_bat_dau` $\rightarrow$ Trả về `HTTP 422 Unprocessable Entity`.
    - Nếu chỉ gửi một ngày và vi phạm với ngày hiện tại trong DB $\rightarrow$ Trả về `HTTP 400 Bad Request`.
    - Trả về `HTTP 404 Not Found` nếu không tìm thấy chương trình thực tập theo `id`.
    - Trả về `HTTP 422 Unprocessable Entity` nếu `id <= 0`.
- **Kiểm thử tự động (Unit Test)**:
  - Bổ sung 11 unit test cases mới vào `backend/tests/test_programs.py` (tổng số test trong file tăng từ 14 lên 25 tests):
    - Cập nhật thành công cả 2 ngày (`ngay_ket_thuc > ngay_bat_dau`) $\rightarrow$ 200 OK.
    - Cập nhật chỉ ngày bắt đầu $\rightarrow$ 200 OK.
    - Cập nhật chỉ ngày kết thúc $\rightarrow$ 200 OK.
    - Bắt lỗi khi ngày kết thúc trước ngày bắt đầu $\rightarrow$ 422.
    - Bắt lỗi khi ngày kết thúc trùng ngày bắt đầu $\rightarrow$ 422.
    - Bắt lỗi khi ngày bắt đầu mới $\ge$ ngày kết thúc hiện tại trong DB $\rightarrow$ 400.
    - Bắt lỗi khi ngày kết thúc mới $\le$ ngày bắt đầu hiện tại trong DB $\rightarrow$ 400.
    - Bắt lỗi khi ngày kết thúc mới bằng đúng ngày bắt đầu hiện tại $\rightarrow$ 400.
    - Bắt lỗi khi gửi payload rỗng $\rightarrow$ 422.
    - Bắt lỗi khi mã chương trình không tồn tại $\rightarrow$ 404.
    - Bắt lỗi khi ID âm hoặc bằng 0 $\rightarrow$ 422.
  - Toàn bộ test suite: **151/151 unit tests PASS 100%**.

---

## [1.12.0] - 2026-09-29
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/evaluations/summary` tổng hợp dữ liệu từ `ho_so_thuc_tap`, `danh_gia`, `truong_dai_hoc`, đồng thời hỗ trợ xuất dữ liệu ra file PDF/Excel.

### Đã hoàn thành (Added & Enhanced)
- **Cơ sở dữ liệu & Model ORM Đánh giá năng lực (`DanhGia`)**:
  - Bổ sung định nghĩa bảng `danh_gia` (Mục 2.10 `DATABASE_DESIGN.md`) và nạp dữ liệu mẫu vào file `script/database/init_db.sql`.
  - Thực thi đồng bộ tạo bảng và nạp 4 bản ghi seed data vào MySQL thực tế (`intern_management`) thông qua `script/init_db.py`.
  - Xây dựng model SQLAlchemy `backend/database/models/danh_gia.py` đầy đủ thuộc tính: `ma_danh_gia`, `ma_ho_so`, `ma_nguoi_danh_gia`, `loai_danh_gia`, `diem_ky_nang`, `diem_thai_do`, `nhan_xet_chi_tiet`, `de_xuat_tuyen_chinh_thuc`.
  - Tích hợp các thuộc tính tính toán tự động: `diem_trung_binh`, `xep_loai` (Xuất sắc, Giỏi, Khá, Trung bình, Yếu) và quan hệ ORM hai chiều với `HoSoThucTap` (`danh_sach_danh_gia`).
- **Pydantic Schemas tổng hợp đánh giá (`backend/schemas.py`)**:
  - `GradeDistribution`: Phân bổ số lượng theo xếp loại.
  - `UniversityEvaluationStat`: Thống kê số lượng và điểm trung bình theo trường đại học.
  - `EvaluationSummaryStats`: Chỉ số KPI tổng thể (tổng SV, tổng ĐG, điểm kỹ năng TB, điểm thái độ TB, điểm tổng kết TB, tỷ lệ đề xuất tuyển dụng chính thức).
  - `EvaluationDetailItem`: Chi tiết từng bản đánh giá kết hợp thông tin sinh viên và trường học.
  - `EvaluationSummaryResponse`: Response chuẩn trả về cho JSON API.
- **Module Xuất File Đa định dạng (`backend/services/export_service.py`)**:
  - `export_evaluations_to_excel`: Xuất file Excel (.xlsx) 2 sheet chuyên nghiệp gồm Sheet KPI/Phân bổ/Thống kê trường và Sheet Chi tiết từng sinh viên; định dạng font, màu sắc header, border và tự động căn chỉnh độ rộng cột.
  - `export_evaluations_to_pdf`: Xuất file PDF khổ A4 ngang (Landscape) bằng ReportLab; đăng ký font TrueType Unicode tiếng Việt (Arial) đảm bảo 100% hiển thị tiếng Việt có dấu chuẩn xác; layout 2 bảng KPI & phân loại xếp loại, bảng thống kê trường và bảng chi tiết thực tập sinh.
- **Endpoint Tổng hợp Đánh giá (`GET /api/v1/evaluations/summary`)**:
  - Hỗ trợ các bộ lọc tìm kiếm linh hoạt: `ma_truong`, `loai_danh_gia` (`GiuaKy`, `CuoiKy`), `trang_thai_thuc_tap`, `de_xuat_tuyen_chinh_thuc` (`true`/`false`), và tìm kiếm từ khóa `tu_khoa` (theo họ tên, email, chuyên ngành, tên trường).
  - Hỗ trợ tham số `format`: `json` (mặc định), `excel`/`xlsx` (tải file .xlsx kèm header `Content-Disposition`), `pdf` (tải file .pdf).
  - Hỗ trợ phân trang danh sách với `page` và `page_size` khi xem dạng JSON.
- **Kiểm thử tự động (Unit Test)**:
  - Cập nhật `tests/conftest.py` bổ sung seed data cho bảng `danh_gia`.
  - Xây dựng bộ test mới `tests/test_evaluation_summary.py` gồm **25 test cases** bao phủ toàn diện:
    - Test lấy dữ liệu JSON mặc định, độ chính xác của các chỉ số KPI tính toán.
    - Test đầy đủ các trường của `items`.
    - Test các bộ lọc độc lập và kết hợp (`ma_truong`, `loai_danh_gia`, `trang_thai_thuc_tap`, `de_xuat_tuyen_chinh_thuc`).
    - Test tìm kiếm theo từ khóa (họ tên, email, chuyên ngành, trường, không khớp).
    - Test phân trang: trang 1, trang 2, ngoài giới hạn, lỗi validation 422 khi `page <= 0` hoặc `page_size > 100`.
    - Test xuất file Excel (`format=excel`, `format=xlsx`), kiểm tra header, tải và đọc cấu trúc openpyxl cả trường hợp có filter.
    - Test xuất file PDF (`format=pdf`), kiểm tra Content-Type, magic byte `%PDF` cả trường hợp có filter.
    - Test kiểm tra lỗi định dạng không hỗ trợ (`format=docx` -> 400 Bad Request).
  - Toàn bộ **165/165 test cases** của hệ thống đều **PASS 100%**.

---

## [1.11.0] - 2026-09-28


### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Nhiệm vụ thực tập (`NhiemVu`)**:
  - Tích hợp và hoàn thiện model `backend/database/models/nhiem_vu.py` theo đúng đặc tả thiết kế CSDL (bảng `nhiem_vu`: `ma_nhiem_vu`, `ma_ho_so`, `ten_nhiem_vu`, `mo_ta`, `han_hoan_thanh`, `tien_do_phantram`, `trang_thai`).
  - Thiết lập quan hệ 2 chiều giữa `NhiemVu` và `HoSoThucTap` qua `danh_sach_nhiem_vu`.
- **Endpoint Cập nhật Tiến độ Nhiệm vụ (`PATCH /api/v1/tasks/{id}/progress`)**:
  - Xây dựng endpoint chuẩn `PATCH /api/v1/tasks/{id}/progress` trả về `HTTP 200 OK`.
  - Validate giá trị `tien_do_phantram` chặt chẽ từ 0 đến 100% bằng Pydantic `Field(..., ge=0, le=100)`.
  - Tự động cập nhật `trang_thai`:
    - Đổi thành `"Hoàn thành"` khi `tien_do_phantram == 100`.
    - Đổi thành `"Đang thực hiện"` khi `0 < tien_do_phantram < 100`.
    - Đổi thành `"Chưa bắt đầu"` khi `tien_do_phantram == 0`.
  - Trả về `HTTP 404 Not Found` nếu không tìm thấy mã nhiệm vụ (`id`).
  - Trả về `HTTP 422 Unprocessable Entity` khi dữ liệu tiến độ không hợp lệ (< 0, > 100, sai kiểu dữ liệu, null, thiếu field) hoặc ID không hợp lệ (<= 0).
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới `tests/test_task_progress.py` gồm **13 test cases** kiểm thử toàn diện:
    - Cập nhật tiến độ 100% tự động đổi sang "Hoàn thành" (200).
    - Cập nhật tiến độ trong khoảng (0, 100) đổi sang "Đang thực hiện" (200).
    - Cập nhật tiến độ 0% đổi sang "Chưa bắt đầu" (200).
    - Giảm tiến độ từ 100% về 75% đổi lại "Đang thực hiện" (200).
    - Bắt lỗi 404 task không tồn tại, 422 khi tiến độ âm, vượt quá 100, sai kiểu dữ liệu, null, thiếu field, ID không hợp lệ.
  - Nâng tổng số test cases của toàn hệ thống lên **140/140 PASS 100%**.

---

## [1.10.0] - 2026-09-28
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Thiết kế model `bao_cao_tuan`, viết endpoint `POST /api/v1/reports` lưu `ma_ho_so`, `ma_nhiem_vu`, `tuan_so`, `noi_dung_cong_viec`, `ket_qua_dat_duoc` kèm gán `thoi_gian_nop = datetime.now()`.

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Báo cáo tuần (`BaoCaoTuan`)**:
  - Xây dựng model `backend/database/models/bao_cao_tuan.py` theo đúng đặc tả Mục 2.9 `DATABASE_DESIGN.md` (bảng `bao_cao_tuan`: `ma_bao_cao`, `ma_ho_so`, `ma_nhiem_vu`, `tuan_so`, `noi_dung_cong_viec`, `ket_qua_dat_duoc`, `phan_hoi_mentor`, `thoi_gian_nop`).
  - Thiết lập quan hệ hai chiều giữa `HoSoThucTap` và `BaoCaoTuan` (`danh_sach_bao_cao`).
- **Endpoint Nộp Báo cáo Tuần (`POST /api/v1/reports`)**:
  - Xây dựng endpoint chuẩn `POST /api/v1/reports` trả về `HTTP 201 Created` cho phép thực tập sinh nộp báo cáo định kỳ tuần.
  - Lưu trữ mã hồ sơ (`ma_ho_so`), mã nhiệm vụ liên kết (`ma_nhiem_vu`), tuần số (`tuan_so`), nội dung công việc và kết quả đạt được.
  - Tự động gán thời gian nộp `thoi_gian_nop = datetime.now()` tại thời điểm nộp.
  - Validate kiểm tra hồ sơ thực tập tồn tại (`HTTP 404`), kiểm tra mã nhiệm vụ tồn tại và thuộc quyền sở hữu của hồ sơ (`HTTP 400`), validate tuần số và cắt khoảng trắng thừa (`HTTP 422`).
- **Đồng bộ Cơ sở dữ liệu & Seed Data**:
  - Bổ sung bảng `bao_cao_tuan` và dữ liệu mẫu vào `script/database/init_db.sql`.
  - Tích hợp tự động tạo bảng qua `Base.metadata.create_all(bind=engine)`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test `tests/test_weekly_reports.py` gồm **13 test cases** kiểm thử toàn diện từ happy path đến các trường hợp biên.
  - Nâng tổng số test cases của toàn hệ thống lên **127/127 PASS 100%**.

---

## [1.9.0] - 2026-09-28
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/interns/my-schedule` truy vấn ngày bắt đầu, ngày kết thúc và nhiệm vụ cá nhân.

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Nhiệm vụ (`NhiemVu`)**:
  - Xây dựng model `backend/database/models/nhiem_vu.py` theo đúng thiết kế CSDL (bảng `nhiem_vu`: `ma_nhiem_vu`, `ma_ho_so`, `ten_nhiem_vu`, `mo_ta`, `han_hoan_thanh`, `tien_do_phantram`, `trang_thai`).
  - Thiết lập quan hệ hai chiều giữa `HoSoThucTap` và `NhiemVu` (`danh_sach_nhiem_vu`).
- **Endpoint Truy vấn Lịch trình & Nhiệm vụ cá nhân (`GET /api/v1/interns/my-schedule`)**:
  - Xây dựng endpoint chuẩn `GET /api/v1/interns/my-schedule` trả về `HTTP 200 OK` tổng hợp thời gian bắt đầu, kết thúc (từ `ChuongTrinhThucTap`) và danh sách nhiệm vụ cá nhân kèm tiến độ.
  - Xử lý thứ tự định tuyến (Route Precedence) chuẩn xác trước route `{id}` để tránh xung đột.
  - Bắt lỗi `HTTP 404 Not Found` khi không tìm thấy hồ sơ thực tập sinh và `HTTP 422 Unprocessable Entity` khi thiếu hoặc sai kiểu tham số `ho_so_id`.
- **Đồng bộ Cơ sở dữ liệu & Seed Data**:
  - Bổ sung bảng `hop_dong`, `nhiem_vu` và dữ liệu mẫu vào `script/database/init_db.sql`.
  - Tự động đồng bộ tạo bảng còn thiếu khi khởi động ứng dụng FastAPI (`Base.metadata.create_all(bind=engine)`).
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test `tests/test_my_schedule.py` gồm **4 test cases** kiểm thử toàn diện.
  - Nâng tổng số test cases của toàn hệ thống lên **114/114 PASS 100%**.

---

## [1.8.0] - 2026-09-27
> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Hợp đồng thực tập (`HopDong`)**:
  - Xây dựng model `backend/database/models/hop_dong.py` theo đúng đặc tả thiết kế CSDL (bảng `hop_dong`: `ma_hop_dong`, `ma_ho_so`, `duong_dan_file`, `ngay_tai_len`, `ngay_ky`, `trang_thai`).
  - Thiết lập quan hệ 2 chiều giữa `HopDong` và `HoSoThucTap`.
- **Endpoint Xác nhận Ký Hợp đồng & Kích hoạt Thực tập (`PATCH /api/v1/contracts/{id}/confirm`)**:
  - Xây dựng endpoint chuẩn `PATCH /api/v1/contracts/{id}/confirm` trả về `HTTP 200 OK`.
  - Hỗ trợ payload tùy chọn qua schema `ContractConfirmRequest` (cho phép truyền body rỗng hoặc tùy chỉnh `trang_thai`, `trang_thai_thuc_tap`, `ngay_ky`, `ghi_chu`).
  - Giao dịch nguyên tử (Atomic Database Transaction): cập nhật đồng thời trạng thái hợp đồng thành `"DaXacNhan"`, cập nhật ngày ký `ngay_ky` và chuyển trạng thái hồ sơ `trang_thai_thuc_tap` thành `"DangThucTap"`.
  - Validate whitelist nghiêm ngặt trạng thái hợp đồng và trạng thái thực tập, tự động chuẩn hóa strip khoảng trắng thừa.
  - Trả về `HTTP 404 Not Found` nếu không tìm thấy mã hợp đồng hoặc hồ sơ liên kết.
  - Trả về `HTTP 422 Unprocessable Entity` khi dữ liệu validate không hợp lệ.
- **Tự động gửi Email thông báo qua BackgroundTasks**:
  - Tích hợp hàm `send_contract_confirmed_email` trong `services/email_service.py`.
  - Gửi email thông báo ký kết thành công và chào mừng sinh viên chính thức bắt đầu kỳ thực tập với vai trò "Đang thực tập".
- **Tích hợp Giao diện Frontend (`frontend/js/hop_dong.js`)**:
  - Đồng bộ hàm `thucHienKyHopDong` với API `PATCH /api/v1/contracts/{id}/confirm`, hiển thị trực quan thông tin ký số và trạng thái thực tập từ server.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới `tests/test_contract_confirm.py` gồm **11 test cases** kiểm thử toàn diện:
    - Xác nhận hợp đồng với payload mặc định, không truyền body, truyền ngày ký tùy chọn & mã OTP (200).
    - Kiểm tra tính nguyên tử (atomic commit) trên cả hai bảng CSDL.
    - Kiểm tra email thông báo được ghi nhận qua BackgroundTasks.
    - Bắt lỗi 404 không tìm thấy hợp đồng, 422 trạng thái sai, ghi chú quá dài, ID sai kiểu dữ liệu.
  - Nâng tổng số test cases của toàn hệ thống lên **96/96 PASS 100%**.

---

## [1.7.0] - 2026-09-27
> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Cập nhật trạng thái xét duyệt hồ sơ thực tập sinh (`PATCH /api/v1/interns/{id}/approval`)**:
  - Xây dựng endpoint chuẩn `PATCH /api/v1/interns/{id}/approval` trả về `HTTP 200 OK` để xét duyệt hồ sơ thực tập sinh.
  - Hỗ trợ linh hoạt cả hai tên trường `trang_thai_duyet` (theo yêu cầu nghiệp vụ) và `trang_thai_xet_duyet` (tên cột CSDL) thông qua helper `approval_data.get_status()`.
  - Validate whitelist nghiêm ngặt trạng thái duyệt: chỉ chấp nhận `"ChoDuyet"`, `"DaDuyet"`, `"TuChoi"`. Tự động chuẩn hóa strip khoảng trắng thừa đầu cuối.
  - Hỗ trợ trường `ghi_chu` tùy chọn (tối đa 500 ký tự) cho lý do từ chối hoặc nhận xét đánh giá.
  - Trả về `HTTP 404 Not Found` nếu không tìm thấy mã hồ sơ thực tập sinh trong hệ thống.
  - Trả về `HTTP 422 Unprocessable Entity` khi thiếu trạng thái, trạng thái ngoài whitelist, hoặc ghi chú vượt quá giới hạn độ dài.
- **Tự động gửi Email thông báo qua BackgroundTasks**:
  - Khi cập nhật thành công, endpoint tự động kích hoạt `BackgroundTasks` gọi `send_profile_approval_email` gửi thư thông báo kết quả (Chúc mừng nếu Đã duyệt / Nêu lý do từ chối nếu Bị từ chối) tới địa chỉ email của thực tập sinh.
  - Quá trình gửi email diễn ra hoàn toàn bất đồng bộ trong nền, không làm chậm độ trễ phản hồi của API.
- **Tích hợp Frontend (`frontend/js/xet_duyet_ho_so.js`)**:
  - Cập nhật hai hàm `duyetHoSo` và `xacNhanTuChoiHoSo` kết nối trực tiếp vào endpoint `PATCH /api/v1/interns/{id}/approval` thay vì gọi tạm API tài liệu.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới `tests/test_intern_approval.py` gồm **11 test cases** bao phủ:
    - Duyệt hồ sơ thành công `DaDuyet`, từ chối `TuChoi`, đổi lại `ChoDuyet` (200).
    - Duyệt qua alias field `trang_thai_duyet` (200).
    - Tự động strip khoảng trắng đầu cuối (200).
    - Kiểm tra email được gửi tới đúng thực tập sinh với tiêu đề và nội dung phù hợp.
    - Bắt lỗi không tìm thấy ID (404), trạng thái không hợp lệ (422), rỗng (422), thiếu trường (422), ghi chú quá 500 ký tự (422), sai kiểu dữ liệu ID (422).
  - Nâng tổng số test cases của toàn hệ thống lên **85/85 PASS 100%**.

---

## [1.6.0] - 2026-09-27
> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Tải lên tài liệu đính kèm (`POST /api/v1/documents/upload`)**:
  - Xây dựng endpoint chuẩn `POST /api/v1/documents/upload` trả về `HTTP 201 Created` xử lý form upload đa phần (`multipart/form-data`) bằng `UploadFile`, `File` và `Form`.
  - Kiểm tra tồn tại của hồ sơ thực tập sinh `ma_ho_so` trước khi ghi file (trả về `HTTP 404 Not Found` nếu không tìm thấy).
  - Xác thực nghiêm ngặt loại tài liệu `loai_tai_lieu` không được rỗng hay chứa khoảng trắng thừa (`HTTP 422`).
  - Bảo mật tệp tin: giới hạn định dạng cho phép (.pdf, .doc, .docx, .xls, .xlsx, .png, .jpg, .jpeg), chặn file thực thi nguy hiểm (.exe, .sh, .bat...), kiểm tra dung lượng tối đa 10MB (trả về `HTTP 400 Bad Request` khi vi phạm).
  - Tự động sinh tên file ngẫu nhiên an toàn kết hợp mã hồ sơ, loại tài liệu và mã băm UUID (`{ma_ho_so}_{loai_tai_lieu}_{uuid}{ext}`) chống ghi đè và chống tấn công Path Traversal.
  - Lưu trữ file thực tế vào thư mục `backend/uploads/` trên máy chủ và ghi nhận đường dẫn tương đối vào bảng `tai_lieu_ho_so` với trạng thái mặc định `ChoDuyet`.
- **Phục vụ tệp tĩnh (Static Files Serving)**:
  - Mount thư mục `uploads/` vào route `/uploads` qua `fastapi.staticfiles.StaticFiles`, hỗ trợ xem trực tuyến và tải về tài liệu trực tiếp từ URL.
- **Mở rộng Schema & Phụ thuộc**:
  - Bổ sung schema `DocumentUploadResponse` vào `schemas.py`.
  - Khai báo bổ sung `python-multipart>=0.0.9` vào `requirements.txt`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới `tests/test_upload_document.py` gồm **11 test cases** bao phủ:
    - Upload thành công file PDF, ảnh PNG, Word DOCX (201).
    - Phục vụ tệp tĩnh qua endpoint `/uploads/<filename>` (200).
    - Bắt lỗi mã hồ sơ không tồn tại (404), đuôi file nguy hiểm .exe, .sh (400), vượt quá 10MB (400), thiếu tham số / file (422).
  - Nâng tổng số test cases của toàn hệ thống lên **74/74 PASS 100%**.

---

## [1.5.0] - 2026-09-27
> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Tạo mới hồ sơ thực tập sinh (`POST /api/v1/interns`)**:
  - Xây dựng endpoint chuẩn RESTful `POST /api/v1/interns` trả về `HTTP 201 Created`.
  - Thực hiện lưu trữ đồng thời cả tài khoản người dùng (`NguoiDung` vai trò `ThucTapSinh`) và bản ghi hồ sơ (`HoSoThucTap`) trong cùng một Database Transaction nguyên tử (Atomic).
  - Tự động kiểm tra trùng lặp email và số điện thoại với các tài khoản đã có trong hệ thống (trả về `HTTP 400 Bad Request`).
  - Kiểm tra tính tồn tại và toàn vẹn của các khóa ngoại: mã trường đại học `ma_truong`, mã chương trình thực tập `ma_chuong_trinh`, mã người hướng dẫn `ma_mentor` (trả về `HTTP 400 Bad Request` nếu không tồn tại).
- **Mở rộng Schema (`schemas.py`)**:
  - Xây dựng schema `InternCreate` và `InternCreateResponse` bằng Pydantic v2:
    - Validate nghiêm ngặt họ tên tiếng Việt (không để trống, chỉ chứa chữ cái và khoảng trắng).
    - Validate cú pháp email chuẩn RFC.
    - Validate số điện thoại định dạng 10 chữ số (hoặc đầu số quốc tế `+84`).
    - Validate danh mục trạng thái xét duyệt (`ChoDuyet`, `DaDuyet`, `TuChoi`) và trạng thái thực tập (`DangThucTap`, `HoanThanh`, `ThoiHoc`).
- **Môi trường & Kiểm thử tự động (Unit Test)**:
  - Cải tiến `backend/database/session.py` với giá trị cấu hình mặc định an toàn cho biến môi trường CSDL.
  - Tích hợp cơ chế SQLite Test Database fallback tự động trong `tests/conftest.py` giúp toàn bộ bộ test có thể chạy độc lập, tốc độ cao mà không bắt buộc phải bật MySQL Server cục bộ.
  - Xây dựng bộ test mới `tests/test_create_intern.py` gồm **16 test cases** bao phủ đầy đủ:
    - Tạo thành công đầy đủ trường và tối thiểu trường bắt buộc (201).
    - Tự động cắt khoảng trắng thừa (201).
    - Bắt lỗi validate schema, thiếu trường, sai format tên, email, sđt, trạng thái (422).
    - Bắt lỗi trùng email, trùng số điện thoại, khóa ngoại không tồn tại (400).
  - Nâng tổng số test cases của toàn hệ thống lên **63/63 PASS 100%**.

---

## [1.4.0] - 2026-09-26
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Sử dụng `fastapi.BackgroundTasks` kết hợp thư viện email gửi mail tự động thông báo kết quả sau khi duyệt.

### Đã hoàn thành (Added & Enhanced)
- **Tích hợp gửi Email tự động trong nền (`fastapi.BackgroundTasks`)**:
  - Tích hợp `fastapi.BackgroundTasks` vào endpoint duyệt tài liệu `PATCH /api/v1/documents/{id}/status`.
  - Tự động kích hoạt tác vụ gửi email thông báo kết quả duyệt cho thực tập sinh ngay sau khi trạng thái duyệt được lưu vào CSDL mà không làm nghẽn luồng xử lý chính của HTTP response.
- **Module Dịch vụ Email (`backend/services/email_service.py`)**:
  - Xây dựng module dịch vụ email sử dụng thư viện chuẩn `smtplib` và `email.mime.text` (MIMEText/Header) hỗ trợ bảo mật kết nối TLS.
  - Định dạng nội dung email dạng văn bản thuần túy (plain text) ngắn gọn, súc tích, chuyên nghiệp, thông báo rõ ràng tên thực tập sinh, tên tài liệu tiếng Việt, kết quả xét duyệt và ghi chú/lý do từ chối (nếu có).
  - Hỗ trợ cơ chế giả lập gửi email thông minh (`MAIL_ENABLED=false` hoặc môi trường dev/test) với danh sách `sent_emails_history` giúp chạy test nhanh chóng và an toàn mà không cần kết nối mạng SMTP bên ngoài.
  - Định nghĩa sẵn hàm `send_profile_approval_email` hỗ trợ mở rộng cho các luồng duyệt hồ sơ tuyển dụng.
- **Mở rộng Schema (`schemas.py`)**:
  - Cập nhật `DocumentStatusUpdate`: bổ sung trường tùy chọn `ghi_chu: Optional[str]` tối đa 500 ký tự (cho phép người duyệt gửi kèm nhận xét hoặc lý do từ chối), tự động strip khoảng trắng thừa.
- **Cấu hình & Biến môi trường**:
  - Bổ sung cấu hình SMTP vào `.env.example` và `.env`: `MAIL_ENABLED`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng bộ test mới `tests/test_email_notification.py` gồm **12 test cases**:
    - Gửi email phê duyệt `DaDuyet`, từ chối `TuChoi` kèm ghi chú, hoàn trạng thái `ChoDuyet`.
    - Kiểm tra xử lý chuỗi ghi chú (strip, rỗng, vượt quá 500 ký tự trả về 422).
    - Kiểm tra trường hợp tài liệu không tồn tại (404 không kích hoạt gửi email).
    - Kiểm tra trực tiếp các hàm trong dịch vụ email và mock quy trình kết nối SMTP với TLS.
    - Kiểm tra bắt ngoại lệ Exception khi mất mạng hay lỗi SMTP mà không làm sập server.
  - Nâng tổng số test cases của toàn hệ thống lên **47/47 PASS 100%**.

---

## [1.3.0] - 2026-09-25
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/documents/{ho_so_id}` lấy tài liệu và `PATCH /api/v1/documents/{id}/status` cập nhật `trang_thai_duyet`.

### Đã hoàn thành
- **Cấu trúc Model dạng Package (`backend/database/models/`)**:
  - Tách `models.py` thành thư mục package `models/` chuẩn modular architecture:
    - `models/phong_ban.py` (`PhongBan`)
    - `models/truong_dai_hoc.py` (`TruongDaiHoc`)
    - `models/chuong_trinh.py` (`ChuongTrinhThucTap`)
    - `models/nguoi_dung.py` (`NguoiDung`)
    - `models/ho_so.py` (`HoSoThucTap`)
    - `models/tai_lieu.py` (`TaiLieuHoSo`)
    - `models/__init__.py` xuất khẩu toàn bộ models.
- **Tài liệu hồ sơ**:
  - Bổ sung bảng `tai_lieu_ho_so` vào CSDL và nạp dữ liệu mẫu vào `script/database/init_db.sql`.
  - Schema `DocumentStatusUpdate`: Kiểm tra nghiêm ngặt `trang_thai_duyet` chỉ chấp nhận các giá trị `ChoDuyet`, `DaDuyet`, `TuChoi`, tự động cắt khoảng trắng thừa.
  - Endpoint `GET /api/v1/documents/{ho_so_id}`: Lấy danh sách tài liệu theo mã hồ sơ; trả về 404 nếu hồ sơ không tồn tại, trả về mảng rỗng nếu chưa có tài liệu.
  - Endpoint `PATCH /api/v1/documents/{id}/status`: Cập nhật trạng thái duyệt của tài liệu; trả về 404 nếu mã tài liệu không tồn tại.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test `tests/test_documents.py` gồm **21 test cases** bao phủ toàn diện:
    - Case thành công: Duyệt `DaDuyet`, từ chối `TuChoi`, đưa về `ChoDuyet`, xử lý khoảng trắng.
    - Case biên & logic: Danh sách rỗng, ID bằng 0, ID số âm, ID số thực (float).
    - Case lỗi & ngoại lệ: Không tìm thấy (404), sai kiểu dữ liệu chữ/số (422), giá trị ngoài danh mục (422), chuỗi rỗng/chỉ dấu cách (422), thiếu trường/field rỗng/null (422).
  - Toàn bộ 35/35 test cases của hệ thống đều **PASS 100%**.

---

## [1.2.0] - 2026-09-25
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/interns/{id}` lấy chi tiết và `PUT /api/v1/interns/{id}` cập nhật thông tin hồ sơ.

### Đã thay đổi & Cải tiến
- **Tái cấu trúc CSDL & Models (Database & ORM Models)**:
  - Chuyển đổi từ bảng phẳng đơn lẻ `interns` sang mô hình quan hệ chuẩn hóa 16 bảng theo thiết kế hệ thống (`DATABASE_DESIGN.md`).
  - Cập nhật `database/models.py`:
    - Loại bỏ class `Intern` cũ.
    - Xây dựng 5 Model ORM cốt lõi: `PhongBan`, `TruongDaiHoc`, `ChuongTrinhThucTap`, `NguoiDung`, `HoSoThucTap`.
    - Thiết lập khóa ngoại `ForeignKey` và các quan hệ hai chiều `relationship()` giữa `HoSoThucTap` với tài khoản thực tập sinh, mentor hướng dẫn, trường đại học và chương trình thực tập.
    - Tích hợp phương thức `to_dict()` tổng hợp dữ liệu chi tiết cho response.
  - Cập nhật `script/database/init_db.sql` và `script/init_db.py`: Định nghĩa lại DDL tạo bảng và nạp dữ liệu mẫu (Seed Data) chuẩn khóa ngoại, hỗ trợ UTF-8 console output.
- **Validation & Schemas**:
  - Cập nhật `schemas.py`:
    - Chuẩn hóa `InternUpdate` theo các trường mới: `ho_ten`, `email`, `so_dien_thoai`, `chuyen_nganh`, `ma_truong`, `trang_thai_thuc_tap`.
    - Bổ sung schema `InternDetailData` và `InternResponse` định hình cấu trúc dữ liệu trả về cho API `GET`.
    - Duy trì và kế thừa bộ validator regex nghiêm ngặt: chuẩn hóa họ tên tiếng Việt, kiểm tra định dạng email và số điện thoại 10 số.
- **API Endpoints**:
  - Chuẩn hóa tiền tố đường dẫn theo chuẩn RESTful versioning:
    - `GET /api/v1/interns/{id}`: Truy vấn chi tiết hồ sơ thực tập sinh, kết hợp tự động dữ liệu từ các bảng người dùng, trường, chương trình và mentor; trả về 404 nếu không tìm thấy.
    - `PUT /api/v1/interns/{id}`: Cập nhật thông tin thực tập sinh đồng bộ trên cả bảng `NGUOI_DUNG` và `HO_SO_THUC_TAP` trong cùng một giao dịch (Transaction), kiểm tra chống trùng email/SĐT (HTTP 400) và kiểm tra tồn tại của mã trường (HTTP 400).
- **Kiểm thử tự động (Unit Test)**:
  - Cập nhật `tests/test_get_put.py` kiểm thử toàn diện các endpoint mới `/api/v1/interns/{id}`.
  - Bổ sung test kiểm tra ràng buộc trường học không tồn tại. Toàn bộ 14/14 test cases đều vượt qua (100% Passed).

---

## [1.1.0] - 2026-09-23
> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Thiết kế model `chuong_trinh_thuc_tap`, viết endpoint `POST /api/v1/programs` liên kết `ma_phong_ban`, lưu `ten_chuong_trinh`, `mo_ta`.

### Đã hoàn thành (Added)
- **Validation & Schemas**:
  - Tạo `schemas.py` định nghĩa `InternUpdate` bằng **Pydantic**:
    - Validate bắt buộc các trường `full_name`, `email` không được để trống hoặc chỉ chứa khoảng trắng.
    - Giới hạn độ dài chuẩn CSDL (`full_name` tối đa 50 ký tự, `email` tối đa 100, `phone` đúng 10 số).
    - Validate biểu thức chính quy (Regex) họ tên tiếng Việt và định dạng email.
    - Validate số điện thoại hợp lệ (10 số).
    - Validate logic nghiệp vụ: `end_date >= start_date`.
- **API Endpoints**:
  - Endpoint `PUT /api/interns/{id}`:
    - Nhận ID qua Path parameter và thông tin cập nhật qua JSON Request Body.
    - Kiểm tra tồn tại của thực tập sinh (trả về 404 nếu không tìm thấy).
    - Kiểm tra trùng lặp email và số điện thoại với các thực tập sinh khác trong CSDL (trả về 400).
    - Lưu thay đổi vào MySQL và đồng bộ trạng thái (`commit` & `refresh`).
    - Trả về mã HTTP 200 kèm dữ liệu mới nhất.
    - Bắt lỗi validate tự động với HTTP 422.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo bộ test `tests/test_get_put.py` sử dụng `pytest` và `TestClient(app)` gồm 15 test case:
    - 3 test case cho API `GET /api/interns/{id}` (thành công 200, không tìm thấy 404, ID không hợp lệ 422).
    - 12 test case cho API `PUT /api/interns/{id}` bao gồm:
      - **Case đúng**: Cập nhật thành công (200), giữ nguyên email & SĐT của chính mình (200).
      - **Case sai**: ID không tồn tại (404), trùng email (400), trùng số điện thoại (400), sai format email (422), sai format SĐT (422), logic ngày kết thúc < ngày bắt đầu (422).
      - **Case biên**: Cùng ngày bắt đầu & kết thúc (200), họ tên vượt quá độ dài tối đa (422), bỏ trống trường bắt buộc (422).
      - **Case ngoại lệ**: Trường bắt buộc bị truyền `null` (422).
  - Bổ sung `pytest` và `httpx` vào `requirements.txt`.

---

## [1.0.0] - 2026-09-22

### Đã hoàn thành (Added)
- **Cấu hình & Môi trường**:
  - Quản lý phụ thuộc dự án qua `requirements.txt` (FastAPI, Uvicorn, SQLAlchemy, PyMySQL, Python-dotenv).
  - Cấu hình biến môi trường qua `.env` và cung cấp `.env.example` làm mẫu kết nối MySQL.
- **Database & Model**:
  - `database/database.py`: Cấu hình kết nối MySQL bằng SQLAlchemy engine và session dependency `get_db()`.
  - `database/models.py`: Định nghĩa model `Intern` ánh xạ bảng `interns`, tích hợp hàm `to_dict()` tự động serialize dữ liệu sang JSON và xử lý định dạng ngày tháng (Date/DateTime).
- **API Endpoints**:
  - Endpoint `GET /api/interns/{id}`:
    - Nhận tham số đường dẫn `{id}` (kiểu `int`).
    - Truy vấn chi tiết thông tin thực tập sinh từ CSDL MySQL.
    - Trả về mã HTTP 200 kèm dữ liệu khi tìm thấy.
    - Trả về mã HTTP 404 khi không tìm thấy bản ghi.
    - Tự động bắt lỗi HTTP 422 khi `id` truyền vào sai kiểu dữ liệu.
- **Bảo mật & Tích hợp**:
  - Kích hoạt `CORSMiddleware` cho phép kết nối từ Frontend Web / Mobile.
