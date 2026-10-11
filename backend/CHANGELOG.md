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

- **Pydantic Schemas (`schemas.py`)**:
  - `MentorWorkloadItem`: Schema biểu diễn khối lượng công việc của từng Mentor bao gồm thông tin cá nhân, phòng ban và số lượng thực tập sinh đang phụ trách.
  - `MentorWorkloadSummary`: Khối KPI tổng quan tự động thống kê tổng số mentor, tổng số TTS được hướng dẫn, trung bình TTS/mentor, mentor phụ trách nhiều nhất và số mentor chưa có sinh viên.
  - `MentorWorkloadData` & `MentorWorkloadResponse`: Response bọc chuẩn RESTful trả về cho Client.
- **Endpoint Thống Kê Khối Lượng Công Việc Mentor (`GET /api/v1/mentors/workload`)**:
  - Thêm route tại [main.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/main.py) thực hiện truy vấn kết hợp giữa `nguoi_dung` (`vai_tro = "Mentor"`), `ho_so_thuc_tap` và `phong_ban` bằng kỹ thuật `outerjoin` và `group_by`.
  - Đếm chính xác số lượng thực tập sinh bằng `func.count(HoSoThucTap.ma_ho_so)` đảm bảo các Mentor chưa có sinh viên vẫn hiển thị đầy đủ với `so_luong_thuc_tap_sinh = 0`.
  - Hỗ trợ các bộ lọc linh hoạt: `ma_phong_ban` (kiểm tra tồn tại HTTP 404), `trang_thai` (validate HTTP 400), `tu_khoa` (tìm kiếm không phân biệt hoa thường theo họ tên hoặc email).
- **Cơ sở dữ liệu & Tài liệu thiết kế**:
  - Cập nhật ghi chú quan hệ và vai trò thực thể `NGUOI_DUNG` (Mentor Workload) trong [DATABASE_DESIGN.md](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/database/DATABASE_DESIGN.md).
  - Bổ sung Mentor mẫu chưa có sinh viên vào fixture SQLite trong [conftest.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/tests/conftest.py) phục vụ kiểm thử `outerjoin`.
- **Kiểm thử tự động**:
  - Tạo mới bộ test [tests/test_mentor_workload.py](file:///d:/CodeGym/TTCS_T926_K16C2_N2/backend/tests/test_mentor_workload.py) gồm 7 test cases bao phủ gọi mặc định, mentor có sinh viên, mentor 0 sinh viên (outerjoin), lọc theo phòng ban (200 & 404), lọc từ khóa, lọc trạng thái (200 & 400) và tính toán KPI summary -> **7/7 PASS 100%**.
  - Kiểm tra hồi quy toàn bộ cụm Mentor -> **18/18 PASS 100%**.


---

## [1.22.0] - 2026-10-09

### Đã hoàn thành (Added & Enhanced)
- **Pydantic Schemas (`FacultyReportResponse`, `FacultyReportData`, `FacultyReportSummary`, `FacultyUniversityStat`, `FacultyMajorStat`, `FacultyInternBreakdownItem`)**:
  - Khai báo schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py).
  - Chuẩn hóa cấu trúc gom nhóm hai chiều (Trường × Chuyên ngành), phân cấp theo trường đại học, phân cấp theo chuyên ngành, danh sách phẳng chi tiết và khối thống kê tổng hợp.
- **Endpoint Thống Kê Sinh Viên Theo Trường & Chuyên Ngành (`GET /api/v1/reports/interns-by-faculty`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) kết hợp bảng `truong_dai_hoc` và `ho_so_thuc_tap` qua `ma_truong`.
  - Thực hiện gom nhóm hai chiều theo `ten_truong` và `chuyen_nganh`, tính toán tổng số lượng sinh viên và tỷ lệ % phân bổ.
  - Hỗ trợ các bộ lọc linh hoạt: `ma_truong`, `ten_truong`, `chuyen_nganh`, `ma_chuong_trinh`, `trang_thai_xet_duyet`, `trang_thai_thuc_tap`.
  - Bắt trọn vẹn ngoại lệ theo chuẩn RESTful: `HTTP 404` (khi mã trường hoặc mã chương trình không tồn tại), `HTTP 400` (khi sai trạng thái xét duyệt hoặc thực tập).
- **Kiểm thử tự động (Unit Test & Regression Test)**:
  - Tạo mới bộ test [tests/test_report_interns_by_faculty.py](file:///d:/clone/ttcs/backend/tests/test_report_interns_by_faculty.py) gồm 13 test cases bao phủ gọi mặc định, lọc theo trường, chuyên ngành, kiểm tra phân cấp hai chiều, xác thực lỗi.
  - Kiểm tra hồi quy toàn bộ cụm report -> **54/54 PASS 100%**.

---

## [1.21.0] - 2026-10-07

### Đã hoàn thành (Added & Enhanced)
- **Pydantic Schemas (`MentorCreate`, `MentorItemData`, `MentorResponse`)**:
  - Khai báo schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py).
  - Tự động validate họ tên, chuẩn hóa email, ràng buộc mật khẩu (tối thiểu 6 ký tự), kiểm tra định dạng số điện thoại Việt Nam và hỗ trợ mã phòng ban.
- **Endpoint Tạo Tài Khoản Người Hướng Dẫn (`POST /api/v1/mentors`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) tiếp nhận thông tin người hướng dẫn, tạo tài khoản vào bảng `nguoi_dung` với `vai_tro = "Mentor"`, trạng thái `HoatDong`.
  - Băm mật khẩu bảo mật bằng bcrypt thông qua `security.get_password_hash`.
  - Kiểm tra chống trùng lặp email và số điện thoại trong hệ thống (`HTTP 400 Bad Request`).
  - Kiểm tra tính tồn tại của phòng ban liên kết theo `ma_phong_ban` (`HTTP 400 Bad Request` nếu không tồn tại).
  - Trả về mã `HTTP 201 Created` kèm thông tin tài khoản (ẩn mật khẩu băm).
- **Kiểm thử tự động (Unit Test & Regression Test)**:
  - Tạo mới bộ test [tests/test_mentors.py](file:///d:/clone/ttcs/backend/tests/test_mentors.py) với 11 test cases bao phủ tạo thành công (đủ trường / tối giản), băm mật khẩu, kiểm tra trùng lặp.
  - Kiểm thử hồi quy toàn bộ test suite của Backend: **285/285 test cases PASS 100%**.

---

## [1.20.0] - 2026-10-06

### Đã hoàn thành (Added & Enhanced)
- **Thiết kế Model Phụ Cấp Thực Tập Sinh (`PhuCap`)**:
  - Tạo mới ORM model [phu_cap.py](file:///d:/clone/ttcs/backend/database/models/phu_cap.py) ánh xạ bảng `phu_cap` với các trường: `ma_phu_cap` (PK), `ma_ho_so` (FK), `thang_nam`, `so_tien`, `trang_thai_chi_tra`.
  - Thiết lập quan hệ hai chiều `ho_so` và `danh_sach_phu_cap` với model [ho_so.py](file:///d:/clone/ttcs/backend/database/models/ho_so.py).
  - Export tại [database/models/__init__.py](file:///d:/clone/ttcs/backend/database/models/__init__.py).
- **Pydantic Schemas (`AllowanceItem`, `AllowanceSummary`, `AllowanceDetailData`, `AllowanceResponse`)**:
  - Khai báo các schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py) chuẩn hóa dữ liệu tài chính cho Client.
  - Cung cấp khối `summary` tự động thống kê tổng tiền đã nhận, tổng tiền đang chờ giải ngân, tổng toàn bộ.
- **Endpoint Truy Vấn Danh Sách Phụ Cấp (`GET /api/v1/interns/{id}/allowances`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) truy vấn danh sách phụ cấp theo `ma_ho_so` (`id`).
  - Tự động kiểm tra tính tồn tại của hồ sơ thực tập sinh (`HTTP 404 Not Found` nếu không tìm thấy).
  - Tự động tính toán tổng số tiền đã nhận và các khoản đang chờ giải ngân trả về cho Client theo thứ tự tháng giảm dần.
- **Đồng bộ Cơ sở dữ liệu & Seed Data**:
  - Bổ sung lệnh INSERT dữ liệu mẫu cho bảng `phu_cap` vào [init_db.sql](file:///d:/clone/ttcs/script/database/init_db.sql).
  - Nạp thành công CSDL MySQL thực tế thông qua `script/init_db.py`.
  - Cập nhật hàm `reseed_sqlite_db()` trong [conftest.py](file:///d:/clone/ttcs/backend/tests/conftest.py).
- **Kiểm thử tự động (Unit Test & Regression Test)**:
  - Tạo mới bộ test [tests/test_intern_allowances.py](file:///d:/clone/ttcs/backend/tests/test_intern_allowances.py) với 5 test cases kiểm tra tính toán tổng tiền, danh sách rỗng, kiểm tra hồi quy.
  - Kiểm tra hồi quy với các test cases liên quan -> **PASS 100%**.

---

## [1.19.0] - 2026-10-03

### Đã hoàn thành (Added & Enhanced)
- **Thiết kế Model Ca Làm Việc (`CaLamViec`)**:
  - Tạo mới ORM model [ca_lam_viec.py](file:///d:/clone/ttcs/backend/database/models/ca_lam_viec.py) ánh xạ bảng `ca_lam_viec` với các trường: `ma_ca` (PK), `ten_ca`, `gio_bat_dau`, `gio_ket_thuc`, `cac_ngay_trong_tuan`.
  - Cung cấp phương thức `to_dict()` chuẩn hóa định dạng thời gian `HH:MM:SS` trả về cho Client.
  - Export tại [database/models/__init__.py](file:///d:/clone/ttcs/backend/database/models/__init__.py).
- **Pydantic Schemas (`ScheduleCreate`, `ScheduleData`, `ScheduleCreateResponse`)**:
  - Khai báo schema tại [schemas.py](file:///d:/clone/ttcs/backend/schemas.py).
  - Tích hợp validator `@model_validator(mode="after")` kiểm tra logic `gio_ket_thuc > gio_bat_dau` (báo lỗi HTTP 422 nếu giờ kết thúc nhỏ hơn hoặc bằng giờ bắt đầu).
  - Chuẩn hóa trường `ten_ca` (cấm chuỗi rỗng/chỉ chứa khoảng trắng) và trường `cac_ngay_trong_tuan` (hỗ trợ cả mảng `List[str]` và chuỗi `str`).
- **Endpoint Tạo Mới Ca Làm Việc (`POST /api/v1/schedules`)**:
  - Thêm route tại [main.py](file:///d:/clone/ttcs/backend/main.py) trả về mã `HTTP 201 Created` kèm thông tin ca làm việc vừa lưu vào CSDL.
- **Đồng bộ Cơ sở dữ liệu & Database Design**:
  - Cập nhật sơ đồ ERD mermaid và bổ sung mục `2.11b. CA_LAM_VIEC` vào [DATABASE_DESIGN.md](file:///d:/clone/ttcs/backend/database/DATABASE_DESIGN.md).
  - Bổ sung câu lệnh DDL `CREATE TABLE IF NOT EXISTS ca_lam_viec` và Seed data mẫu vào [init_db.sql](file:///d:/clone/ttcs/script/database/init_db.sql).
  - Cập nhật hàm `reseed_sqlite_db()` trong [conftest.py](file:///d:/clone/ttcs/backend/tests/conftest.py).
  - Thực thi nạp thành công CSDL MySQL qua script `script/init_db.py`.
- **Kiểm thử tự động (Unit Test & Integration Test)**:
  - Tạo mới bộ test [tests/test_schedules.py](file:///d:/clone/ttcs/backend/tests/test_schedules.py) với 7 test cases kiểm tra thành công, validate logic giờ, tên rỗng, thiếu trường.
  - Chạy kiểm thử hồi quy toàn diện toàn bộ test suite của Backend: **269/269 test cases PASS 100%** không có bất kỳ xung đột nào.

---

## [1.18.0] - 2026-10-02

### Đã hoàn thành (Added & Enhanced)
- **Schemas Pydantic Báo cáo tuần & Phản hồi (`schemas.py`)**:
  - `ReportItemData`: Schema biểu diễn báo cáo tuần chi tiết kèm thông tin sinh viên, Mentor phụ trách và thông tin nhiệm vụ.
  - `ReportPagination`: Thông tin phân trang chuẩn RESTful.
  - `ReportListData` & `ReportListResponse`: Schema response cho danh sách báo cáo tuần.
  - `ReportFeedbackRequest`: Request body cho phản hồi của Mentor kèm validator.
  - `ReportFeedbackResponse`: Response trả về sau khi gửi phản hồi thành công.
- **Endpoint Lấy Danh Sách Báo Cáo Tuần (`GET /api/v1/reports`)**:
  - Hỗ trợ lọc báo cáo theo sinh viên, hỗ trợ các bộ lọc linh hoạt, tìm kiếm từ khóa.
  - Hỗ trợ phân trang chuẩn RESTful.
- **Endpoint Gửi Phản Hồi Báo Cáo Tuần (`POST /api/v1/reports/{id}/feedback`)**:
  - Cho phép Mentor gửi nhận xét, cập nhật cột `phan_hoi_mentor`.
  - Kiểm tra thẩm quyền của Mentor.
- **Kiểm thử tự động (Unit Test)**:
  - Bổ sung thêm **17 test cases**, nâng tổng số test cases lên **262/262 PASS 100%**.

---

## [1.17.0] - 2026-10-01

### Đã hoàn thành (Added & Enhanced)
- **Model Nhiệm Vụ (`NhiemVu`)**:
  - Bổ sung synonym `tieu_de` ánh xạ tới cột `ten_nhiem_vu`.
  - Cập nhật hàm `to_dict()` trả về đồng thời cả `tieu_de` và `ten_nhiem_vu`.
  - Đảm bảo các giá trị mặc định: `tien_do_phantram = 0`, `trang_thai = "Chưa bắt đầu"`.
- **Pydantic Schemas (`TaskCreate`, `TaskDetailData`, `TaskCreateResponse`)**:
  - Thiết kế `TaskCreate` hỗ trợ validate chặt chẽ.
- **Endpoint Tạo Mới Nhiệm Vụ (`POST /api/v1/tasks`)**:
  - Triển khai endpoint tiếp nhận yêu cầu tạo nhiệm vụ mới.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử với **10 test cases**, toàn bộ 23/23 tests liên quan đều PASS 100%.

---

## [1.16.0] - 2026-10-01

### Đã hoàn thành (Added & Enhanced)
- **Model Đơn Xin Nghỉ Phép (`DonXinNghi`)**:
  - Tạo mới ORM model quản lý bảng `don_xin_nghi`.
  - Thiết lập quan hệ 2 chiều với `HoSoThucTap`.
  - Cập nhật script khởi tạo CSDL và ki��n trúc DATABASE_DESIGN.md.
- **Endpoint Tạo Mới Đơn Xin Nghỉ Phép (`POST /api/v1/leave-requests`)**:
  - Triển khai endpoint tiếp nhận yêu cầu xin nghỉ phép của thực tập sinh.
  - Validate dữ liệu đầu vào nghiêm ngặt.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới file kiểm thử với **10 test cases**, toàn bộ test suite đạt **235/235 tests PASS 100%**.

---

## [1.15.0] - 2026-10-01

### Đã hoàn thành (Added & Enhanced)
- **Model Điểm danh & Chấm công (`cham_cong`)**:
  - Bổ sung và chuẩn hóa các trường dữ liệu.
  - Đảm bảo 100% tương thích ngược với API báo cáo tổng hợp chấm công.
- **Endpoint Check-in Ca làm việc (`POST /api/v1/attendance/check-in`)**:
  - Ghi nhận thời gian check-in của thực tập sinh.
  - Tự động phân loại trạng thái.
- **Endpoint Check-out Ca làm việc (`POST /api/v1/attendance/check-out`)**:
  - Ghi nhận thời gian check-out của thực tập sinh.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử với **14 test cases**, toàn bộ test suite đạt **225/225 tests PASS 100%**.

---

## [1.14.0] - 2026-09-30

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Tạo Mới Đánh Giá Thực Tập Sinh (`POST /api/v1/evaluations`)**:
  - Triển khai endpoint tiếp nhận đánh giá thực tập sinh.
  - Tự động tính điểm trung bình và xếp loại.
  - Validate chặt chẽ thang điểm và loại đánh giá.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử với **14 test cases**, nâng tổng số test cases lên **190/190 PASS 100%**.

---

## [1.13.0] - 2026-09-30

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Báo cáo Tổng hợp Chấm công (`GET /api/v1/attendance/reports`)**:
  - Triển khai endpoint lọc và tổng hợp dữ liệu chấm công.
  - Hỗ trợ phân trang chuẩn.
- **Cơ sở dữ liệu & Models**:
  - Bổ sung bảng `cham_cong` và `don_nghi_phep`.
  - Tạo model ChamCong và DonNghiPhep.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo mới bộ kiểm thử với **11 test cases**, toàn bộ test suite đạt **162/162 unit tests PASS 100%**.

---

## [1.12.0] - 2026-09-30

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Cập nhật Thời gian Chương trình Thực tập (`PATCH /api/v1/programs/{id}/timeline`)**:
  - Triển khai endpoint cập nhật mốc thời gian.
  - Validate chặt chẽ logic thời gian.
- **Kiểm thử tự động (Unit Test)**:
  - Bổ sung 11 unit test cases, nâng tổng số test từ 14 lên 25 tests.
  - Toàn bộ test suite: **151/151 unit tests PASS 100%**.

---

## [1.12.0] - 2026-09-29

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/evaluations/summary` tổng hợp dữ liệu từ `ho_so_thuc_tap`, `danh_gia`, `truong_dai_hoc`...

### Đã hoàn thành (Added & Enhanced)
- **Cơ sở dữ liệu & Model ORM Đánh giá năng lực (`DanhGia`)**:
  - Bổ sung định nghĩa bảng `danh_gia` và nạp dữ liệu mẫu.
  - Tích hợp các thuộc tính tính toán tự động.
- **Pydantic Schemas tổng hợp đánh giá (`backend/schemas.py`)**:
  - Xây dựng các schema tương ứng.
- **Module Xuất File Đa định dạng (`backend/services/export_service.py`)**:
  - Xuất file Excel (.xlsx) và PDF.
- **Endpoint Tổng hợp Đánh giá (`GET /api/v1/evaluations/summary`)**:
  - Hỗ trợ các bộ lọc tìm kiếm linh hoạt.
  - Hỗ trợ tham số `format`: json, excel/xlsx, pdf.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng bộ test mới gồm **25 test cases**, toàn bộ **165/165 test cases** PASS 100%.

---

## [1.11.0] - 2026-09-28

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Nhiệm vụ thực tập (`NhiemVu`)**:
  - Tích hợp và hoàn thiện model.
  - Thiết lập quan hệ 2 chiều giữa models.
- **Endpoint Cập nhật Tiến độ Nhiệm vụ (`PATCH /api/v1/tasks/{id}/progress`)**:
  - Xây dựng endpoint chuẩn.
  - Tự động cập nhật trạng thái.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới gồm **13 test cases**.
  - Nâng tổng số test cases lên **140/140 PASS 100%**.

---

## [1.10.0] - 2026-09-28

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Thiết kế model `bao_cao_tuan`, viết endpoint `POST /api/v1/reports`...

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Báo cáo tuần (`BaoCaoTuan`)**:
  - Xây dựng model theo đặc tả Mục 2.9 DATABASE_DESIGN.md.
  - Thiết lập quan hệ hai chiều.
- **Endpoint Nộp Báo cáo Tuần (`POST /api/v1/reports`)**:
  - Xây dựng endpoint chuẩn.
  - Validate kiểm tra hồ sơ thực tập tồn tại.
- **Đồng bộ Cơ sở dữ liệu & Seed Data**:
  - Bổ sung bảng `bao_cao_tuan`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test gồm **13 test cases**.
  - Nâng tổng số test cases lên **127/127 PASS 100%**.

---

## [1.9.0] - 2026-09-28

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/interns/my-schedule` truy vấn ngày bắt đầu, ngày kết thúc và nhiệm vụ cá nhân.

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Nhiệm vụ (`NhiemVu`)**:
  - Xây dựng model theo đặc tả CSDL.
  - Thiết lập quan hệ hai chiều.
- **Endpoint Truy vấn Lịch trình & Nhiệm vụ cá nhân (`GET /api/v1/interns/my-schedule`)**:
  - Xây dựng endpoint chuẩn.
  - Xử lý thứ tự định tuyến chuẩn xác.
- **Đồng bộ Cơ sở dữ liệu & Seed Data**:
  - Bổ sung bảng `hop_dong`, `nhiem_vu`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test gồm **4 test cases**.
  - Nâng tổng số test cases lên **114/114 PASS 100%**.

---

## [1.8.0] - 2026-09-27

> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Hợp đồng thực tập (`HopDong`)**:
  - Xây dựng model theo đặc tả CSDL.
  - Thiết lập quan hệ 2 chiều.
- **Endpoint Xác nhận Ký Hợp đồng & Kích hoạt Thực tập (`PATCH /api/v1/contracts/{id}/confirm`)**:
  - Xây dựng endpoint chuẩn.
  - Giao dịch nguyên tử cập nhật trạng thái.
  - Validate whitelist nghiêm ngặt.
- **Tự động gửi Email thông báo qua BackgroundTasks**:
  - Tích hợp hàm `send_contract_confirmed_email`.
- **Tích hợp Giao diện Frontend (`frontend/js/hop_dong.js`)**:
  - Đồng bộ hàm `thucHienKyHopDong`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới gồm **11 test cases**.
  - Nâng tổng số test cases lên **96/96 PASS 100%**.

---

## [1.7.0] - 2026-09-27

> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Cập nhật trạng thái xét duyệt hồ sơ thực tập sinh (`PATCH /api/v1/interns/{id}/approval`)**:
  - Xây dựng endpoint chuẩn.
  - Validate whitelist nghiêm ngặt trạng thái.
- **Tự động gửi Email thông báo qua BackgroundTasks**:
  - Tích hợp email notification.
- **Tích hợp Frontend (`frontend/js/xet_duyet_ho_so.js`)**:
  - Cập nhật hai hàm kết nối trực tiếp vào endpoint.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới gồm **11 test cases**.
  - Nâng tổng số test cases lên **85/85 PASS 100%**.

---

## [1.6.0] - 2026-09-27

> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Tải lên tài liệu đính kèm (`POST /api/v1/documents/upload`)**:
  - Xây dựng endpoint chuẩn RESTful.
  - Kiểm tra tồn tại hồ sơ.
  - Bảo mật tệp tin chặt chẽ.
- **Phục vụ tệp tĩnh (Static Files Serving)**:
  - Mount thư mục `uploads/`.
- **Mở rộng Schema & Phụ thuộc**:
  - Bổ sung schema `DocumentUploadResponse`.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test mới gồm **11 test cases**.
  - Nâng tổng số test cases lên **74/74 PASS 100%**.

---

## [1.5.0] - 2026-09-27

> **Người thực hiện**: Nguyễn Trung Học

### Đã hoàn thành (Added & Enhanced)
- **Endpoint Tạo mới hồ sơ thực tập sinh (`POST /api/v1/interns`)**:
  - Xây dựng endpoint chuẩn RESTful.
  - Lưu trữ đồng thời tài khoản và hồ sơ.
- **Mở rộng Schema (`schemas.py`)**:
  - Xây dựng schema `InternCreate` và `InternCreateResponse`.
  - Validate nghiêm ngặt.
- **Môi trường & Kiểm thử tự động (Unit Test)**:
  - Cải tiến `backend/database/session.py`.
  - Xây dựng bộ test mới gồm **16 test cases**.
  - Nâng tổng số test cases lên **63/63 PASS 100%**.

---

## [1.4.0] - 2026-09-26

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Sử dụng `fastapi.BackgroundTasks` kết hợp thư viện email gửi mail tự động thông báo kết quả sau khi duyệt.

### Đã hoàn thành (Added & Enhanced)
- **Tích hợp gửi Email tự động trong nền (`fastapi.BackgroundTasks`)**:
  - Tích hợp vào endpoint duyệt tài liệu.
  - Tự động kích hoạt tác vụ gửi email.
- **Module Dịch vụ Email (`backend/services/email_service.py`)**:
  - Xây dựng module dịch vụ email.
  - Hỗ trợ cơ chế giả lập gửi email thông minh.
- **Mở rộng Schema (`schemas.py`)**:
  - Cập nhật `DocumentStatusUpdate`.
- **Cấu hình & Biến môi trường**:
  - Bổ sung cấu hình SMTP.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng bộ test mới gồm **12 test cases**.
  - Nâng tổng số test cases lên **47/47 PASS 100%**.

---

## [1.3.0] - 2026-09-25

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/documents/{ho_so_id}` lấy tài liệu và `PATCH /api/v1/documents/{id}/status` cập nhật `trang_thai_duyet`.

### Đã hoàn thành
- **Cấu trúc Model dạng Package (`backend/database/models/`)**:
  - Tách `models.py` thành thư mục package.
- **Tài liệu hồ sơ**:
  - Bổ sung bảng `tai_lieu_ho_so`.
  - Schema và Endpoint.
- **Kiểm thử tự động (Unit Test)**:
  - Xây dựng file test gồm **21 test cases**.
  - Toàn bộ 35/35 test cases PASS 100%**.

---

## [1.2.0] - 2026-09-25

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Viết endpoint `GET /api/v1/interns/{id}` lấy chi tiết và `PUT /api/v1/interns/{id}` cập nhật thông tin hồ sơ.

### Đã thay đổi & Cải tiến
- **Tái cấu trúc CSDL & Models**:
  - Chuyển đổi từ bảng phẳng sang mô hình quan hệ chuẩn hóa.
  - Cập nhật database/models.py.
  - Cập nhật script/database/init_db.sql.
- **Validation & Schemas**:
  - Cập nhật schemas.py.
- **API Endpoints**:
  - Chuẩn hóa tiền tố đường dẫn theo chuẩn RESTful versioning.
- **Kiểm thử tự động (Unit Test)**:
  - Cập nhật tests/test_get_put.py.
  - Toàn bộ 14/14 test cases PASS 100%**.

---

## [1.1.0] - 2026-09-23

> **Người thực hiện**: Dương Đình Hoàng  
> **Nhiệm vụ**: Backend (FastAPI): Thiết kế model `chuong_trinh_thuc_tap`, viết endpoint `POST /api/v1/programs` liên kết `ma_phong_ban`, lưu `ten_chuong_trinh`, `mo_ta`.

### Đã hoàn thành (Added)
- **Validation & Schemas**:
  - Tạo `schemas.py` định nghĩa `InternUpdate`.
- **API Endpoints**:
  - Endpoint `PUT /api/interns/{id}`.
- **Kiểm thử tự động (Unit Test)**:
  - Tạo bộ test `tests/test_get_put.py` với 15 test cases.

---

## [1.0.0] - 2026-09-22

### Đã hoàn thành (Added)
- **Cấu hình & Môi trường**:
  - Quản lý phụ thuộc dự án qua `requirements.txt`.
  - Cấu hình biến môi trường qua `.env`.
- **Database & Model**:
  - `database/database.py`: Cấu hình kết nối MySQL.
  - `database/models.py`: Định nghĩa model `Intern`.
- **API Endpoints**:
  - Endpoint `GET /api/interns/{id}`.
- **Bảo mật & Tích hợp**:
  - Kích hoạt `CORSMiddleware`.
