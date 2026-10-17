# DỰ ÁN QUẢN LÝ THỰC TẬP SINH (TTCS)
## PHÂN HỆ: QUẢN TRỊ HỆ THỐNG - TÀI KHOẢN & PHÂN QUYỀN

---

### THÔNG TIN NHIỆM VỤ DỰ ÁN
- **Người thực hiện Backend (FastAPI)**: **Nguyễn Văn Hiếu** (Đã hoàn thành sâu sát, chuẩn mực toàn bộ backend, validation, băm mật khẩu bcrypt, kiểm tra trùng lặp và phân quyền RBAC).
- **Người phối hợp Frontend (HTML/JS)**: **Lê Văn Hùng** (Sử dụng Fetch API gửi dữ liệu lên endpoint `POST /api/v1/admin/users`, hiển thị thông báo thành công hoặc lỗi).
- **Người phối hợp Tester (Kiểm thử)**: **Lê Quang Huy** (Chạy bộ kiểm thử tự động với 4 kịch bản tiêu chuẩn).

---

## 1. YÊU CẦU ĐỀ BÀI & GIẢI PHÁP ĐÃ THỰC HIỆN

### Đề bài:
> "Viết endpoint `POST /api/v1/admin/users` cho phép Admin tạo tài khoản người dùng, băm mật khẩu bằng bcrypt, gán vai trò tương ứng (Admin, HR, Mentor, ThucTapSinh) và kiểm tra chống trùng lặp username/email trong bảng `nguoi_dung`."

### Giải pháp kỹ thuật chuyên sâu:
1. **Endpoint**: `POST /api/v1/admin/users`
2. **Bảo mật mật khẩu**: Sử dụng thuật toán **bcrypt** tiêu chuẩn (`rounds=12`) để băm mật khẩu trước khi lưu trữ vào trường `mat_khau_hash`. Tuyệt đối không lưu mật khẩu thô và không trả về mật khẩu trong response.
3. **Gán vai trò hợp lệ**: Hệ thống sử dụng Enum `UserRole` gồm đúng 4 vai trò:
   - `Admin`: Quản trị viên hệ thống.
   - `HR`: Nhân viên nhân sự.
   - `Mentor`: Người hướng dẫn thực tập.
   - `ThucTapSinh`: Thực tập sinh tham gia chương trình.
4. **Kiểm tra chống trùng lặp (Duplicate Checking)**:
   - Kiểm tra `ten_dang_nhap` (username): Nếu đã tồn tại -> Trả về mã **HTTP 400 Bad Request** kèm thông báo `"Tên đăng nhập đã tồn tại trong hệ thống"`.
   - Kiểm tra `email`: Nếu đã tồn tại -> Trả về mã **HTTP 400 Bad Request** kèm thông báo `"Email đã tồn tại trong hệ thống"`.
5. **Phân quyền truy cập (RBAC)**:
   - Sử dụng Dependency `get_current_admin`: Chỉ có tài khoản có vai trò `Admin` mới được phép thao tác.
   - Nếu tài khoản có vai trò khác (`HR`, `Mentor`, `ThucTapSinh`) gọi endpoint -> Trả về mã **HTTP 403 Forbidden**.
   - Nếu không có token xác thực -> Trả về mã **HTTP 401 Unauthorized**.
6. **Mã trạng thái phản hồi chuẩn RESTful**:
   - **201 Created**: Tạo tài khoản thành công.
   - **400 Bad Request**: Trùng lặp username hoặc email.
   - **422 Unprocessable Entity**: Dữ liệu gửi lên thiếu trường bắt buộc hoặc vai trò không hợp lệ.
   - **403 Forbidden**: Người thao tác không có vai trò Admin.
   - **401 Unauthorized**: Không có hoặc sai token xác thực.

---

## 2. CẤU TRÚC THƯ MỤC CHUẨN MODULAR ENTERPRISE

```text
├── app/
│   ├── __init__.py
│   ├── main.py                  # Khởi tạo FastAPI, CORS, Lifespan, Seed Admin mặc định
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Cấu hình Settings, JWT Secret, DB URL
│   │   ├── database.py          # SQLAlchemy Engine, SessionLocal, get_db dependency
│   │   └── security.py          # Hàm băm mật khẩu bcrypt và xử lý JWT Token
│   ├── models/
│   │   ├── __init__.py
│   │   └── nguoi_dung.py        # SQLAlchemy Model bảng `nguoi_dung`
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py              # Pydantic Schemas: UserCreate, UserResponse, UserRole enum
│   └── api/
│       ├── __init__.py
│       ├── deps.py              # Dependency kiểm tra quyền Admin & get_current_user
│       └── v1/
│           ├── __init__.py
│           ├── api.py           # Gom API Router v1
│           └── endpoints/
│               ├── __init__.py
│               ├── admin.py     # Endpoint POST /api/v1/admin/users
│               └── auth.py      # Endpoint POST /api/v1/auth/login
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # TestClient, in-memory SQLite fixture, mock tokens
│   └── test_admin_create_user.py# Bộ kiểm thử tự động đáp ứng 100% kịch bản Tester
├── demo_frontend.html           # Giao diện HTML + Fetch API hoàn chỉnh cho Frontend
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn chi tiết
```

---

## 3. HƯỚNG DẪN CÀI ĐẶT & CHẠY HỆ THỐNG

### Bước 1: Cài đặt thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### Bước 2: Khởi động Backend FastAPI Server
```bash
uvicorn app.main:app --reload
```
- Máy chủ sẽ chạy tại: `http://127.0.0.1:8000`
- Swagger UI tài liệu API tương tác: `http://127.0.0.1:8000/docs`
- ReDoc tài liệu API chi tiết: `http://127.0.0.1:8000/redoc`

*Ghi chú: Khi khởi động lần đầu, hệ thống tự động tạo cơ sở dữ liệu SQLite và tự động tạo tài khoản Admin mặc định:*
- **Tên đăng nhập**: `admin`
- **Mật khẩu**: `Admin@123456`
- **Vai trò**: `Admin`

---

## 4. CHI TIẾT ENDPOINT CHO FRONTEND (LÊ VĂN HÙNG)

### Endpoint: `POST /api/v1/admin/users`

#### Headers yêu cầu:
```http
Content-Type: application/json
Authorization: Bearer <ADMIN_JWT_TOKEN>
```
*(Lưu ý: Để Frontend kiểm thử nhanh mà không cần gọi luồng login trước, Backend có hỗ trợ header: `X-User-Role: Admin`)*

#### Dữ liệu gửi lên (Request Body):
Backend hỗ trợ linh hoạt cả tiếng Việt và tiếng Anh để tiện lợi tối đa:

```json
{
  "ho_ten": "Nguyễn Văn Mentor",
  "email": "mentor.nguyen@ttcs.edu.vn",
  "ten_dang_nhap": "mentor_nguyen",
  "mat_khau": "MatKhauChuan@2026",
  "vai_tro": "Mentor"
}
```
*(Giá trị `vai_tro` chỉ nhận 1 trong 4 giá trị: `"Admin"`, `"HR"`, `"Mentor"`, `"ThucTapSinh"`)*

#### Dữ liệu trả về khi thành công (HTTP 201 Created):
```json
{
  "ma_nguoi_dung": 2,
  "ten_dang_nhap": "mentor_nguyen",
  "email": "mentor.nguyen@ttcs.edu.vn",
  "ho_ten": "Nguyễn Văn Mentor",
  "vai_tro": "Mentor",
  "trang_thai": true,
  "ngay_tao": "2026-10-17T08:00:00.000000"
}
```

---

## 5. BỘ TEST CASES DÀNH CHO TESTER (LÊ QUANG HUY)

File kiểm thử tự động đã được lập trình sẵn tại `tests/test_admin_create_user.py` bao gồm:

| STT | Kịch bản kiểm thử | Kỳ vọng Status Code | Chi tiết kiểm tra |
|---|---|---|---|
| **1** | Gửi thông tin tài khoản mới hợp lệ | **201 Created** | Trả về thông tin user mới, mật khẩu trong database được băm bằng bcrypt, không lộ mật khẩu thô trong response. Kiểm thử thành công cho cả 4 vai trò: Admin, HR, Mentor, ThucTapSinh. |
| **2** | Gửi thiếu trường bắt buộc (thiếu email, username, mat_khau, ho_ten) | **422 Unprocessable Entity** | Trả về thông báo lỗi chi tiết vị trí trường bị thiếu. |
| **3** | Gửi vai trò không hợp lệ (ví dụ: `SuperAdmin`, `SinhVien`) | **422 Unprocessable Entity** | Pydantic Enum Validation chặn ngay lập tức. |
| **4** | Gửi email sai định dạng | **422 Unprocessable Entity** | EmailValidator chặn định dạng không có `@` hoặc domain. |
| **5** | Gửi tên đăng nhập (username) đã tồn tại | **400 Bad Request** | Backend kiểm tra bảng `nguoi_dung` và thông báo `"Tên đăng nhập đã tồn tại"`. |
| **6** | Gửi email đã tồn tại | **400 Bad Request** | Backend kiểm tra bảng `nguoi_dung` và thông báo `"Email đã tồn tại"`. |
| **7** | Tài khoản có vai trò HR, Mentor, ThucTapSinh thao tác tạo người dùng | **403 Forbidden** | RBAC Dependency từ chối truy cập vì không phải Admin. |
| **8** | Không truyền token hoặc header xác thực | **401 Unauthorized** | Hệ thống yêu cầu xác thực trước khi thực hiện. |

### Lệnh chạy kiểm thử tự động:
```bash
pytest -v tests/test_admin_create_user.py
```
Hoặc xem độ bao phủ code (Coverage):
```bash
pytest --cov=app tests/
```
