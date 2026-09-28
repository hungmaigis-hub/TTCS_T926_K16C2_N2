# Changelog - Backend

Tất cả các thay đổi của module Backend sẽ được ghi lại trong tài liệu này.

---

## [1.9.0] - 2026-09-28

### Đã hoàn thành (Added & Enhanced)
- **Model SQLAlchemy Nhiệm vụ thực tập (`NhiemVu`)**:
  - Xây dựng model `backend/database/models/nhiem_vu.py` theo đúng đặc tả thiết kế CSDL (bảng `nhiem_vu`: `ma_nhiem_vu`, `ma_ho_so`, `ten_nhiem_vu`, `mo_ta`, `han_hoan_thanh`, `tien_do_phantram`, `trang_thai`).
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
  - Nâng tổng số test cases của toàn hệ thống lên **123/123 PASS 100%**.

---

## [1.8.0] - 2026-09-27

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
