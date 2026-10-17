# BÁO CÁO THIẾT KẾ VÀ TRIỂN KHAI BACKEND (FastAPI)
## Phân hệ Quản trị Hệ thống - Nhật Ký Hoạt Động (Audit Log Service)

**Tác giả (Backend Developer):** Nguyễn Văn Hiếu  
**Dự án:** Hệ thống Quản lý Thực tập sinh  
**Nhiệm vụ trong Sprint (Row 42):**
> **Backend (FastAPI):** Thiết kế model `nhat_ky_hoat_dong` (`ma_nhat_ky`, `ma_nguoi_dung`, `hanh_dong`, `endpoint`, `phuong_thuc`, `dia_chi_ip`, `mo_ta`, `thoi_gian`). Xây dựng Middleware tự động ghi log các thao tác nghiệp vụ và viết endpoint `GET /api/v1/admin/audit-logs` hỗ trợ tìm kiếm, lọc theo ngày và phân trang.

---

## 1. Cấu trúc Thư mục Dự án

```text
├── app/
│   ├── __init__.py
│   ├── main.py                          # Khởi tạo FastAPI app, CORS, Middleware, Lifespan seed data
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # Cấu hình hệ thống (JWT, Database URL, Exclude Paths)
│   │   ├── database.py                  # Cấu hình SQLAlchemy Engine, SessionLocal, Base, get_db
│   │   ├── security.py                  # Băm mật khẩu (bcrypt), mã hóa & giải mã JWT Token
│   │   └── dependencies.py              # Dependencies: get_current_user, require_admin (RBAC)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── nguoi_dung.py                # Model NguoiDung (Admin, HR, Mentor, ThucTapSinh)
│   │   └── nhat_ky_hoat_dong.py         # Model NhatKyHoatDong (8 trường theo yêu cầu chuẩn)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py                    # Schema phân trang chung (PaginationParams, PaginatedResponse)
│   │   ├── nguoi_dung.py                # Schema người dùng, đăng nhập, TokenResponse
│   │   └── nhat_ky_hoat_dong.py         # Schema AuditLogResponse, PaginatedAuditLogResponse
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── audit_log.py                 # AuditLogMiddleware tự động ghi log thao tác nghiệp vụ
│   ├── services/
│   │   ├── __init__.py
│   │   └── audit_log_service.py         # Xử lý truy vấn, tìm kiếm đa trường, lọc theo ngày, phân trang
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── api.py                   # Gom nhóm router v1
│           └── endpoints/
│               ├── __init__.py
│               ├── audit_logs.py        # Endpoint GET /api/v1/admin/audit-logs
│               ├── auth.py              # Endpoint POST /api/v1/auth/login
│               └── users.py             # Endpoint POST /api/v1/admin/users (kích hoạt auto log)
├── frontend_demo/
│   └── audit_logs.html                  # Giao diện HTML + Fetch API chuẩn mẫu cho Frontend & Tester
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures: In-memory SQLite DB, TestClient, Admin/User tokens
│   ├── test_models.py                   # Test cấu trúc Model & quan hệ ORM
│   ├── test_middleware.py               # Test Middleware tự động ghi log thao tác
│   └── test_audit_logs_api.py           # Test quyền hạn, tìm kiếm, lọc ngày, phân trang API
├── requirements.txt                     # Danh sách thư viện phụ thuộc
└── README.md                            # Tài liệu hướng dẫn chi tiết
```

---

## 2. Chi tiết Thiết kế Model `nhat_ky_hoat_dong`

Tập tin: `app/models/nhat_ky_hoat_dong.py`

| Tên trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `ma_nhat_ky` | `Integer` | Khóa chính, Tự tăng, Index | Định danh duy nhất cho bản ghi nhật ký |
| `ma_nguoi_dung` | `Integer` | Khóa ngoại (`nguoi_dung`), `nullable=True`, Index | ID người thực hiện thao tác (cho phép null nếu là khách / hệ thống) |
| `hanh_dong` | `String(100)` | `nullable=False`, Index | Tên hành động nghiệp vụ (Vd: `TAO_NGUOI_DUNG`, `DANG_NHAP`, ...) |
| `endpoint` | `String(255)` | `nullable=False`, Index | Đường dẫn URL của API được gọi (Vd: `/api/v1/admin/users`) |
| `phuong_thuc` | `String(10)` | `nullable=False`, Index | Phương thức HTTP (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) |
| `dia_chi_ip` | `String(50)` | `nullable=True` | Địa chỉ IP của Client gửi yêu cầu |
| `mo_ta` | `Text` | `nullable=True` | Mô tả chi tiết kết quả hoặc mã trạng thái HTTP |
| `thoi_gian` | `DateTime` | `default=utcnow`, Index, `nullable=False` | Mốc thời gian ghi nhận hành động |

---

## 3. Cơ chế Hoạt động của `AuditLogMiddleware`

Tập tin: `app/middleware/audit_log.py`

1. **Lọc yêu cầu tự động:**
   - Tự động bỏ qua các URL tài nguyên tĩnh hoặc endpoint hệ thống: `/docs`, `/redoc`, `/openapi.json`, `/ping`, `/health` và method `OPTIONS` (CORS preflight).
2. **Nhận diện Người dùng:**
   - Tự động giải mã Bearer JWT token từ header `Authorization` để xác định `ma_nguoi_dung`.
   - Hỗ trợ header `X-Test-User-Id` để kiểm thử nhanh trong môi trường development/testing.
3. **Thu thập thông tin Client:**
   - Tự động lấy địa chỉ IP chuẩn qua `x-forwarded-for` (nếu chạy sau Reverse Proxy/Nginx) hoặc `request.client.host`.
4. **Phân loại hành động nghiệp vụ:**
   - Tự động ghi log các thao tác làm thay đổi dữ liệu: `POST`, `PUT`, `DELETE`, `PATCH`.
   - Ghi log các truy vấn giám sát nhạy cảm của Admin (`GET /api/v1/admin/audit-logs`).
   - Tự động suy luận mã hành động nghiệp vụ chuẩn hóa:
     * `POST /api/v1/admin/users` $\rightarrow$ `TAO_NGUOI_DUNG`
     * `POST /api/v1/auth/login` $\rightarrow$ `DANG_NHAP`
     * `POST /api/v1/support-requests` $\rightarrow$ `TAO_YEU_CAU_HO_TRO`
     * v.v.
   - Cho phép các route ghi đè mô tả nghiệp vụ cụ thể qua `request.state.audit_action` và `request.state.audit_description`.
5. **Đảm bảo tính sẵn sàng (Resilience):**
   - Quá trình ghi database diễn ra độc lập trong khối `try/except`. Nếu database ghi log gặp sự cố, hệ thống sẽ ghi log lỗi ra console và **không làm gián đoạn phản hồi (Response) của người dùng cuối**.

---

## 4. Tài liệu API `GET /api/v1/admin/audit-logs` (Dành cho Frontend & Tester)

### 4.1. Thông tin Endpoint
- **URL:** `/api/v1/admin/audit-logs`
- **Method:** `GET`
- **Quyền hạn:** `Admin` (Bắt buộc Authorization: `Bearer <token>` của tài khoản Admin)

### 4.2. Tham số Query Parameters (Request Query)

| Tham số | Kiểu dữ liệu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `search` | `string` | `None` | Từ khóa tìm kiếm tự do (tìm trong mô tả, hành động, endpoint, IP, tên đăng nhập, họ tên) |
| `tu_ngay` | `datetime` | `None` | Lọc từ ngày (Định dạng ISO: `2026-10-01T00:00:00` hoặc `2026-10-01`) |
| `den_ngay` | `datetime` | `None` | Lọc đến ngày (Định dạng ISO: `2026-10-17T23:59:59` hoặc `2026-10-17`) |
| `ma_nguoi_dung` | `integer` | `None` | Lọc chính xác theo mã người dùng (`ma_nguoi_dung`) |
| `hanh_dong` | `string` | `None` | Lọc theo tên hành động (Vd: `TAO_NGUOI_DUNG`, `DANG_NHAP`) |
| `phuong_thuc` | `string` | `None` | Lọc theo phương thức HTTP (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) |
| `page` | `integer` | `1` | Số trang hiện tại (bắt đầu từ 1, `ge=1`) |
| `page_size` | `integer` | `20` | Số lượng bản ghi mỗi trang (tối đa 100, `ge=1, le=100`) |

### 4.3. Cấu trúc Dữ liệu Phản hồi (Response Body) - HTTP 200

```json
{
  "items": [
    {
      "ma_nhat_ky": 105,
      "ma_nguoi_dung": 1,
      "ten_dang_nhap": "admin",
      "ho_ten": "Quản Trị Viên Hệ Thống",
      "vai_tro": "Admin",
      "hanh_dong": "TAO_NGUOI_DUNG",
      "endpoint": "/api/v1/admin/users",
      "phuong_thuc": "POST",
      "dia_chi_ip": "192.168.1.55",
      "mo_ta": "[201] Admin 'admin' tạo mới người dùng 'mentor_an' với vai trò 'Mentor'",
      "thoi_gian": "2026-10-17T07:35:12"
    }
  ],
  "total": 48,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### 4.4. Mã lỗi HTTP thường gặp
- `401 Unauthorized`: Chưa cung cấp Bearer token hoặc token đã hết hạn.
- `403 Forbidden`: Người dùng không có vai trò `Admin` (Vd: Sinh viên thực tập cố truy cập API này).

---

## 5. Hướng dẫn Dành cho Frontend Developer (Lê Hoàng Huy)

1. **Xem trang giao diện mẫu hoàn chỉnh:**
   - Đã xây dựng sẵn file: [`frontend_demo/audit_logs.html`](file:///d:/New%20folder%20(Backend%20(FastAPI)%20Thi%E1%BA%BFt%20k%E1%BA%BF%20model%20nhat_ky_hoat_dong%20(ma_nhat_ky,%20ma_nguoi_dung,%20hanh_dong,%20endpoint,%20phuong_thuc,%20dia_chi_ip,%20mo_ta,%20thoi_gian).%20X%C3%A2y%20d%E1%BB%B1ng%20Middleware%20t%E1%BB%B1%20%C4%91%E1%BB%99ng%20ghi%20log%20c%C3%A1c%20thao%20t%C3%A1c%20nghi%E1%BB%87p%20v%E1%BB%A5%20v%C3%A0%20vi%E1%BA%BFt%20endpoint%20GET%20apiv1a2)/frontend_demo/audit_logs.html)
   - Truy cập trực tiếp qua trình duyệt tại: `http://127.0.0.1:8000/demo`
2. **Cách viết Fetch API chuẩn để lấy dữ liệu:**
   ```javascript
   const token = localStorage.getItem("access_token");
   const response = await fetch(
     `http://127.0.0.1:8000/api/v1/admin/audit-logs?page=${page}&page_size=20&search=${encodeURIComponent(keyword)}`,
     {
       method: "GET",
       headers: {
         "Authorization": `Bearer ${token}`,
         "Content-Type": "application/json"
       }
     }
   );
   const data = await response.json();
   console.log("Danh sách log:", data.items);
   console.log("Tổng số trang:", data.total_pages);
   ```

---

## 6. Hướng dẫn Dành cho Tester (Lê Quốc Huy)

Bộ test case tự động đã được lập trình đầy đủ bằng `pytest` tại thư mục `tests/`:

1. **`test_models.py`:**
   - Kiểm tra đầy đủ 8 trường dữ liệu của model `nhat_ky_hoat_dong`.
   - Kiểm tra quan hệ ORM với `NguoiDung`.
   - Kiểm tra lưu log vô danh (`ma_nguoi_dung = None`).
2. **`test_middleware.py`:**
   - Kiểm tra tự động ghi log khi gọi `POST /api/v1/admin/users`.
   - Kiểm tra trích xuất chính xác IP, Endpoint, Method, Action, Description.
   - Kiểm tra không ghi log với `/ping`.
   - Kiểm tra ghi log với request lỗi `400 Bad Request`.
3. **`test_audit_logs_api.py`:**
   - Kiểm tra chặn `401 Unauthorized` khi thiếu token.
   - Kiểm tra chặn `403 Forbidden` khi tài khoản không phải `Admin`.
   - Kiểm tra phân trang chính xác (`page`, `page_size`, `total_pages`).
   - Kiểm tra tìm kiếm theo từ khóa (`search`).
   - Kiểm tra lọc theo mốc thời gian (`tu_ngay`, `den_ngay`).
   - Kiểm tra lọc theo `ma_nguoi_dung`, `hanh_dong`, `phuong_thuc`.

### Lệnh chạy kiểm thử tự động:
```powershell
# Chạy toàn bộ test suite
pytest -v

# Chạy riêng kiểm thử Middleware
pytest tests/test_middleware.py -v

# Chạy riêng kiểm thử API Audit Logs
pytest tests/test_audit_logs_api.py -v
```

---

## 7. Tài khoản Kiểm thử Mặc định (Được tạo tự động khi khởi động)

| Tài khoản (Username) | Mật khẩu | Vai trò (Role) | Mục đích |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | `Admin` | Truy cập toàn quyền vào API `GET /api/v1/admin/audit-logs` |
| `mentor_hung` | `mentor123` | `Mentor` | Kiểm thử chặn quyền 403 Forbidden |
| `intern_hieu` | `intern123` | `ThucTapSinh` | Kiểm thử chặn quyền 403 Forbidden |
