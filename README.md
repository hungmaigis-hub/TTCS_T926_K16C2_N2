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
```

### Bước 2: Nạp dữ liệu mẫu (Seed Data)
```bash
python seed_data.py
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
