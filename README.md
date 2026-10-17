
# Giao diện Quản trị Nhật ký Hoạt động (Audit Logs Management)

Hệ thống giao diện bảng HTML5 / CSS3 / Vanilla JavaScript hiện đại, trực quan, chuyên nghiệp dành cho trang quản trị hệ thống (Admin Portal).

---

## 📁 Cấu trúc thư mục

```
audit-logs/
├── index.html       # Giao diện HTML gồm Form bộ lọc, Bảng hiển thị, Phân trang và Modal
├── style.css        # Toàn bộ CSS giao diện bảng, huy hiệu trạng thái, hiệu ứng chuyển trang
├── app.js           # JavaScript Fetch API GET /api/v1/admin/audit-logs, bộ lọc & Mock fallback
└── README.md        # Hướng dẫn chi tiết & tài liệu kỹ thuật
```

---

## 🚀 Tính năng nổi bật

1. **Bộ lọc đa tiêu chí (Smart Filters)**:
   - **Người dùng**: Tìm kiếm theo tên, email hoặc mã User ID.
   - **Hành động (Action)**: `LOGIN`, `LOGOUT`, `CREATE`, `UPDATE`, `DELETE`, `EXPORT`, `PERMISSION_CHANGE`.
   - **Khoảng thời gian (Date Range)**: Lọc từ ngày (`from_date`) đến ngày (`to_date`).
   - **Trạng thái**: `SUCCESS`, `FAILED`, `WARNING`.
   - Lựa chọn kích thước trang linh hoạt: 10, 20, 50 dòng/trang.

2. **Giao thức Fetch API chuẩn RESTful**:
   - Gửi yêu cầu HTTP GET tới `/api/v1/admin/audit-logs` với chuỗi `URLSearchParams`.
   - Đính kèm headers `Accept: application/json` và `Authorization: Bearer <token>`.
   - Quản lý trạng thái: Skeleton loading, Empty state (không tìm thấy kết quả), Error handling & Retry.

3. **Phân trang thông minh (Smart Pagination)**:
   - Hiển thị số bản ghi: `Đang hiển thị X - Y trong tổng Z bản ghi`.
   - Nút chuyển: Trang đầu, Trang trước, Trang sau, Trang cuối.
   - Nút số trang thông minh dạng rút gọn (VD: `1`, `...`, `4`, `[5]`, `6`, `...`, `15`).

4. **Huy hiệu trực quan (Visual Badges) & Modal xem chi tiết**:
   - Màu sắc riêng biệt cho từng hành động và trạng thái.
   - Avatar người dùng tự động sinh màu pastel theo tên.
   - Xem chi tiết từng lượt thao tác: IP, User Agent, JSON payload thay đổi (old_value, new_value).

5. **Chế độ Mock Fallback thông minh**:
   - Khi chưa khởi động backend server, hệ thống tự động sinh 45 bản ghi mẫu giả lập ngay trên trình duyệt để kiểm thử toàn diện thao tác lọc và phân trang mà không bị lỗi.

---

## 📡 Đặc tả API Endpoint

### Request
```http
GET /api/v1/admin/audit-logs?user=nguyen&action=UPDATE&from_date=2026-10-01&to_date=2026-10-16&page=1&limit=10
Accept: application/json
Authorization: Bearer <your_jwt_token>
=======

# Module Quản Lý Thông Báo (Notification Service) - FastAPI & SQLAlchemy

> **Dự án**: Hệ thống Quản lý Thực tập sinh  
> **Người thực hiện**: Nguyễn Văn Hiếu  
> **Vai trò**: Backend Developer  
> **Đối tác phối hợp**:
> - Frontend Developer: Đỗ Hoàng (Xây dựng icon chuông, badge số lượng, dropdown thông báo)
> - QA / Tester: Lê Quang Huy (Viết test case tự động kiểm thử phân quyền 200/404/403)

---

## 1. Thiết Kế Database Model `thong_bao` (SQLAlchemy)

Bảng cơ sở dữ liệu `thong_bao` được định nghĩa tại `app/models/thong_bao.py` với đầy đủ các trường theo đặc tả:

| Tên trường | Kiểu dữ liệu | Thuộc tính | Mô tả |
| :--- | :--- | :--- | :--- |
| `ma_thong_bao` | `Integer` | `primary_key=True, autoincrement=True, index=True` | Khóa chính của thông báo |
| `ma_nguoi_nhan` | `Integer` | `ForeignKey("nguoi_dung.ma_nguoi_dung"), nullable=False, index=True` | Khóa ngoại trỏ đến người nhận |
| `tieu_de` | `String(255)` | `nullable=False` | Tiêu đề ngắn gọn của thông báo |
| `noi_dung` | `Text` | `nullable=False` | Nội dung chi tiết thông báo |
| `loai_thong_bao`| `String(50)` | `nullable=False, default="CHUNG", index=True` | Phân loại: `LICH_TRINH`, `CONG_VIEC`, `HE_THONG`, `CHUNG` |
| `da_doc` | `Boolean` | `nullable=False, default=False, index=True` | Trạng thái: `False` (chưa đọc), `True` (đã đọc) |
| `ngay_tao` | `DateTime` | `nullable=False, default=datetime.utcnow, index=True` | Thời điểm tạo thông báo |

```python
# Trích đoạn code SQLAlchemy Model (app/models/thong_bao.py):
class ThongBao(Base):
    __tablename__ = "thong_bao"

    ma_thong_bao = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_nguoi_nhan = Column(Integer, ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="CASCADE"), nullable=False, index=True)
    tieu_de = Column(String(255), nullable=False)
    noi_dung = Column(Text, nullable=False)
    loai_thong_bao = Column(String(50), nullable=False, default="CHUNG", index=True)
    da_doc = Column(Boolean, default=False, nullable=False, index=True)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    nguoi_nhan = relationship("NguoiDung", back_populates="thong_bao_list")
```

---

## 2. Chi Tiết Các Endpoint API

Base URL: `http://localhost:8000/api/v1`

### 2.1. Lấy thông báo cá nhân (`GET /api/v1/notifications/my`)
- **Mục đích**: Lấy danh sách thông báo của người dùng đang đăng nhập (sắp xếp giảm dần theo ngày tạo mới nhất).
- **Headers**:
  - `Authorization: Bearer <access_token>` hoặc `X-User-Id: <ma_nguoi_nhan>` (hỗ trợ kiểm thử nhanh giữa Frontend/Tester).
- **Query Parameters**:
  - `unread_only` (*boolean, optional*): Nếu `true`, chỉ trả về thông báo chưa đọc.
  - `skip` (*int, default = 0*): Phân trang.
  - `limit` (*int, default = 50*): Số lượng bản ghi tối đa.
- **Phản hồi mẫu (`200 OK`)**:
```json
{
  "items": [
    {
      "ma_thong_bao": 1,
      "id": 1,
      "ma_nguoi_nhan": 1,
      "tieu_de": "Lịch họp tiếp nhận thực tập sinh K16C2",
      "noi_dung": "Buổi gặp mặt và phổ biến quy chế thực tập diễn ra vào 08:30 ngày 20/10 tại phòng họp 302.",
      "loai_thong_bao": "LICH_TRINH",
      "da_doc": false,
      "ngay_tao": "2026-10-17T06:30:00"
    }
  ],
  "total": 5,
  "unread_count": 4,
  "limit": 50,
  "skip": 0
}
```
> **Lưu ý cho Frontend (Đỗ Hoàng)**: Trường `unread_count` trả về trực tiếp số lượng thông báo chưa đọc để render vào **badge đỏ** trên icon chuông mà không cần duyệt mảng ở client!

---

### 2.2. Đánh dấu đã đọc (`PATCH /api/v1/notifications/{id}/read`)
- **Mục đích**: Chuyển trạng thái `da_doc` thành `true` khi người dùng click vào thông báo trên dropdown.
- **Path Parameter**: `{id}` là `ma_thong_bao`.
- **Headers**: `Authorization: Bearer <token>` hoặc `X-User-Id: <user_id>`.
- **Mã phản hồi chuẩn RESTful & Security (Đúng đặc tả Tester)**:
  - **`200 OK`**: Đánh dấu thành công, trả về thông báo đã cập nhật.
    ```json
    {
      "ma_thong_bao": 1,
      "id": 1,
      "ma_nguoi_nhan": 1,
      "tieu_de": "Lịch họp tiếp nhận thực tập sinh K16C2",
      "noi_dung": "Buổi gặp mặt...",
      "loai_thong_bao": "LICH_TRINH",
      "da_doc": true,
      "ngay_tao": "2026-10-17T06:30:00"
    }
    ```
  - **`404 Not Found`**: Khi `id` không tồn tại trong hệ thống.
    ```json
    {
      "detail": "Không tìm thấy thông báo với mã 999999"
    }
    ```
  - **`403 Forbidden`**: Khi người dùng cố tình cập nhật thông báo của người khác.
    ```json
    {
      "detail": "Bạn không có quyền truy cập hoặc chỉnh sửa thông báo này"
    }
    ```
  - **`401 Unauthorized`**: Khi chưa đăng nhập hoặc token không hợp lệ.

---

### 2.3. Các Endpoint Bổ Sung (Hỗ trợ hệ thống)
- `PATCH /api/v1/notifications/read-all`: Đánh dấu đọc tất cả thông báo của người dùng.
- `POST /api/v1/notifications`: Tạo thông báo mới (phục vụ tạo lịch họp, gửi phân công công việc từ HR/Mentor).
- `POST /api/v1/auth/login`: Đăng nhập lấy Bearer JWT Token.
- `POST /api/v1/auth/register`: Đăng ký tài khoản người dùng mới.

---

## 3. Cấu Trúc Dự Án

```
├── app/
│   ├── __init__.py
│   ├── main.py                     # Khởi tạo FastAPI app, middleware CORS, include router
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Cấu hình Settings, JWT, CORS, Database URL
│   │   ├── security.py             # Hash bcrypt và tạo/giải mã JWT token
│   │   └── database.py             # SQLAlchemy Engine, SessionLocal, Base, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── nguoi_dung.py           # Model NguoiDung (User)
│   │   └── thong_bao.py            # Model ThongBao theo đặc tả
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── thong_bao.py            # Pydantic schemas (ThongBaoResponse, ThongBaoListResponse,...)
│   │   └── nguoi_dung.py           # Pydantic schemas cho NguoiDung và Token
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── crud_thong_bao.py       # Tầng truy xuất dữ liệu thông báo
│   │   └── crud_nguoi_dung.py      # Tầng truy xuất dữ liệu người dùng
│   └── api/
│       ├── __init__.py
│       ├── deps.py                 # Dependency get_db, get_current_user (JWT & X-User-Id)
│       └── v1/
│           ├── __init__.py
│           ├── api.py              # Đăng ký routes v1
│           └── endpoints/
│               ├── __init__.py
│               ├── auth.py         # Login & Register
│               └── notifications.py# GET /my, PATCH /{id}/read
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures: SQLite in-memory, TestClient, Mock Users
│   └── test_notifications.py       # 6 Test cases tự động đáp ứng 100% yêu cầu của Tester
├── seed_data.py                    # Khởi tạo dữ liệu mẫu người dùng và thông báo
├── frontend_demo.html              # Trang giao diện HTML mô phỏng Header có icon chuông & badge
├── requirements.txt                # Thư viện phụ thuộc
└── README.md                       # Tài liệu hướng dẫn
```

---

## 4. Hướng Dẫn Cài Đặt & Chạy Hệ Thống

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
=======
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

### Query Parameters

| Tham số | Kiểu | Mô tả | Mặc định |
|---|---|---|---|
| `page` | `integer` | Số trang hiện tại | `1` |
| `limit` | `integer` | Số lượng bản ghi trên một trang | `10` |
| `user` | `string` | Từ khóa tìm kiếm người dùng (tên / email / id) | `""` |
| `action` | `string` | Mã hành động (`CREATE`, `UPDATE`, `DELETE`, ...) | `""` |
| `from_date` | `string` | Ngày bắt đầu định dạng `YYYY-MM-DD` | `""` |
| `to_date` | `string` | Ngày kết thúc định dạng `YYYY-MM-DD` | `""` |
| `status` | `string` | Trạng thái thực thi (`SUCCESS`, `FAILED`) | `""` |

### Chuẩn JSON Response mong đợi

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1001,
        "timestamp": "2026-10-16T15:30:00Z",
        "user": {
          "id": 101,
          "name": "Nguyễn Văn An",
          "email": "an.nguyen@company.com",
          "role": "Super Admin"
        },
        "action": "UPDATE",
        "resource": "Hợp đồng lao động #HD-2026-89",
        "description": "Cập nhật trạng thái hợp đồng nhân sự",
        "ip_address": "192.168.1.15",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "status": "SUCCESS",
        "details": {
          "field_modified": "status",
          "old_value": "PENDING",
          "new_value": "ACTIVE"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total_records": 45,
      "total_pages": 5
=======
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


### Bước 2: Nạp dữ liệu mẫu (Seed Data)
```bash
python seed_data.py
=======
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
*Script sẽ tạo sẵn 3 người dùng (Hiếu, Hoàng, Huy) cùng 6 thông báo mẫu đủ các loại lịch trình, công việc, hệ thống.*


### Bước 3: Khởi chạy Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Tài liệu tương tác Swagger UI: `http://localhost:8000/docs`
- Tài liệu ReDoc: `http://localhost:8000/redoc`

---

## 5. Hướng Dẫn Cho Tester (Lê Quang Huy) Chạy Kiểm Thử Tự Động

Chạy bộ test suite bằng `pytest`:
```bash
pytest tests/ -v
```

Bộ test bao gồm các kịch bản đúng theo yêu cầu phân công công việc:
1. `test_get_my_notifications_unauthenticated`: Kiểm tra trả về `401 Unauthorized` khi chưa xác thực.
2. `test_get_my_notifications_returns_200_and_filters_user`: Kiểm tra trả về `200 OK`, dữ liệu hiển thị đúng người nhận, không lộ thông báo của người khác.
3. `test_mark_notification_as_read_success`: Kiểm tra click đánh dấu đổi `da_doc` thành `True` thành công (`200 OK`).
4. `test_mark_notification_not_found_404`: Kiểm tra trả về `404 Not Found` khi mã thông báo không tồn tại.
5. `test_mark_notification_forbidden_403`: Kiểm tra trả về `403 Forbidden` khi cố tình đọc thông báo của người khác.
6. `test_get_my_notifications_with_x_user_id_header`: Kiểm thử cơ chế Header linh hoạt cho môi trường dev.

---

## 6. Hướng Dẫn Cho Frontend Developer (Đỗ Hoàng) Tích Hợp

Trong file `frontend_demo.html` đã xây dựng sẵn code JavaScript mẫu bằng `fetch API`:

```javascript
const API_BASE = "http://127.0.0.1:8000/api/v1";

// 1. Lấy danh sách thông báo & số lượng chưa đọc hiển thị lên Badge:
async function loadNotifications() {
    const res = await fetch(`${API_BASE}/notifications/my`, {
        headers: {
            "Authorization": `Bearer ${token}` // Hoặc dùng "X-User-Id": "1" khi test
        }
    });
    const data = await res.json();
    
    // Cập nhật số lượng Badge trên icon chuông:
    const badge = document.getElementById("unreadBadge");
    if (data.unread_count > 0) {
        badge.innerText = data.unread_count;
        badge.style.display = "block";
    } else {
        badge.style.display = "none";
    }

    // Render danh sách data.items vào Dropdown...
}

// 2. Đánh dấu đã đọc khi người dùng click vào một thông báo trên Dropdown:
async function onNotificationClick(maThongBao) {
    const res = await fetch(`${API_BASE}/notifications/${maThongBao}/read`, {
        method: "PATCH",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    if (res.ok) {
        // Cập nhật lại UI: đổi style thành đã đọc và giảm số lượng Badge
        loadNotifications();

    }
}
```

Có thể mở file `frontend_demo.html` trực tiếp trên trình duyệt (hoặc qua Live Server) để trải nghiệm và kiểm chứng hoạt động của toàn bộ luồng.
=======
---

## 💻 Cách sử dụng
Mở file `index.html` trực tiếp trên trình duyệt web (Google Chrome, Microsoft Edge, Firefox, Brave) hoặc chạy qua bất kỳ static web server nào (Live Server, VSCode, Nginx, Apache).
=======
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

