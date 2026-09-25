# Changelog - Backend

Tất cả các thay đổi của module Backend sẽ được ghi lại trong tài liệu này.

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
