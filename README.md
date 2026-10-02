# Hệ Thống Quản Lý Thực Tập Sinh - Backend API (FastAPI)

> **Người thực hiện:** Nguyễn Văn Hiếu  
> **Vai trò:** Backend Developer  
> **Nhiệm vụ (Story Point: 2 - Ưu tiên: Cao):**  
> Thiết kế model `hop_dong`, viết endpoint `POST /api/v1/contracts` lưu `ma_so_hop_dong`, `ngay_ky`, `muc_phu_cap_co_ban` (kèm khóa ngoại `ma_ho_so` và liên kết file hợp đồng) để bàn giao cho đội ngũ Frontend và Tester.

---

## 1. Cấu trúc thư mục dự án

```text
├── app/
│   ├── __init__.py
│   ├── main.py                  # Khởi chạy FastAPI, cấu hình CORS, OpenAPI Docs
│   ├── core/
│   │   ├── config.py            # Cấu hình hệ thống, Database URL, CORS
│   │   └── database.py          # Kết nối SQLAlchemy, SessionLocal, Base
│   ├── models/
│   │   ├── __init__.py
│   │   └── hop_dong.py          # SQLAlchemy Model: hop_dong
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── hop_dong.py          # Pydantic Schemas validate dữ liệu vào/ra
│   └── api/
│       ├── __init__.py
│       ├── api.py               # Gom nhóm Router v1
│       └── endpoints/
│           ├── __init__.py
│           └── contracts.py     # Endpoint POST /api/v1/contracts và các API liên quan
├── tests/
│   ├── __init__.py
│   └── test_contracts.py        # Bộ kiểm thử tự động pytest
├── .env.example                 # File mẫu biến môi trường
├── .gitignore                   # Loại trừ file rác, venv, db khi push Git
├── requirements.txt             # Danh sách thư viện Python
├── run.py                       # Script khởi động nhanh server
└── README.md                    # Tài liệu hướng dẫn chi tiết
```

---

## 2. Thiết kế Cơ sở Dữ liệu: Model `hop_dong`

Bảng `hop_dong` được định nghĩa trong file `app/models/hop_dong.py`:

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto Increment | Khóa chính định danh hợp đồng |
| `ma_so_hop_dong` | `VARCHAR(50)` | UNIQUE, NOT NULL, INDEX | Mã số hợp đồng (duy nhất, không trùng) |
| `ngay_ky` | `DATE` | NOT NULL | Ngày ký kết hợp đồng |
| `muc_phu_cap_co_ban` | `NUMERIC(14, 2)` | NOT NULL | Mức phụ cấp cơ bản (VNĐ, >= 0) |
| `ma_ho_so` | `VARCHAR(50)` | NULLABLE, INDEX | Khóa ngoại liên kết hồ sơ thực tập sinh |
| `file_url` | `VARCHAR(500)` | NULLABLE | Đường dẫn file hợp đồng scan/pdf đính kèm |
| `trang_thai` | `VARCHAR(50)` | NOT NULL, DEFAULT 'Chờ xác nhận' | Trạng thái (`Chờ xác nhận`, `Đã xác nhận`) |
| `ghi_chu` | `TEXT` | NULLABLE | Ghi chú thêm |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT NOW | Thời điểm tạo bản ghi |
| `updated_at` | `DATETIME` | NOT NULL, DEFAULT NOW | Thời điểm cập nhật cuối |

---

## 3. Tài liệu API Endpoint cho Frontend (`mấy ae forten`)

### 3.1. Tạo mới hợp đồng (Nhiệm vụ chính)

- **URL:** `/api/v1/contracts`
- **Method:** `POST`
- **Content-Type:** `application/json`

#### Request Body mẫu:
```json
{
  "ma_so_hop_dong": "HD-2026-TTS-001",
  "ngay_ky": "2026-10-02",
  "muc_phu_cap_co_ban": 3500000.0,
  "ma_ho_so": "HS-2026-001",
  "file_url": "https://storage.example.com/contracts/hd-001.pdf",
  "ghi_chu": "Hợp đồng thực tập 3 tháng phòng Công nghệ"
}
```

#### Response thành công (`201 Created`):
```json
{
  "id": 1,
  "ma_so_hop_dong": "HD-2026-TTS-001",
  "ngay_ky": "2026-10-02",
  "muc_phu_cap_co_ban": "3500000.00",
  "ma_ho_so": "HS-2026-001",
  "file_url": "https://storage.example.com/contracts/hd-001.pdf",
  "trang_thai": "Chờ xác nhận",
  "ghi_chu": "Hợp đồng thực tập 3 tháng phòng Công nghệ",
  "created_at": "2026-10-02T13:00:00",
  "updated_at": "2026-10-02T13:00:00"
}
```

#### Response lỗi:
- **`400 Bad Request`** (Khi mã số hợp đồng đã tồn tại trong database):
  ```json
  {
    "detail": "Mã số hợp đồng 'HD-2026-TTS-001' đã tồn tại trên hệ thống!"
  }
  ```
- **`422 Unprocessable Entity`** (Khi mức phụ cấp < 0 hoặc thiếu trường bắt buộc):
  ```json
  {
    "detail": [
      {
        "loc": ["body", "muc_phu_cap_co_ban"],
        "msg": "Input should be greater than or equal to 0",
        "type": "greater_than_equal"
      }
    ]
  }
  ```

---

### 3.2. Các API bổ trợ cho Frontend tích hợp hoàn thiện

1. **Lấy danh sách hợp đồng (hỗ trợ phân trang & tìm kiếm):**
   - **Method:** `GET /api/v1/contracts?skip=0&limit=20&ma_so_hop_dong=HD-01&ma_ho_so=HS-01`
   - Trả về: `{ "total": 10, "items": [...] }`

2. **Lấy chi tiết 1 hợp đồng:**
   - **Method:** `GET /api/v1/contracts/{id}`

3. **Thực tập sinh xác nhận hợp đồng (User Story STT 10):**
   - **Method:** `PATCH /api/v1/contracts/{id}/confirm`
   - Body: `{ "xac_nhan": true, "ghi_chu": "Tôi đã đọc và đồng ý" }`
   - Ngăn chặn người dùng ký lại nhiều lần (trả về `400` nếu đã xác nhận trước đó).

---

## 4. Hướng dẫn Cài đặt & Khởi chạy Backend

### Bước 1: Tạo môi trường ảo và cài đặt thư viện
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt môi trường (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# Hoặc Windows Command Prompt:
# venv\Scripts\activate.bat

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng FastAPI
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Hoặc chạy trực tiếp qua file:
```bash
python run.py
```

### Bước 3: Kiểm tra giao diện tài liệu Swagger UI & ReDoc
- **Swagger UI (Dành cho Frontend & Tester test trực tiếp):**  
  👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:**  
  👉 [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 5. Chạy Kiểm Thử Tự Động (Automated Testing)

Dự án đã viết sẵn 6 test case tự động bao phủ toàn bộ nghiệp vụ (thành công, trùng lặp mã hợp đồng, validate mức phụ cấp, danh sách, xác nhận hợp đồng):
```bash
pytest -v
```

---

## 6. Hướng dẫn Nộp Code lên GitHub cho Frontend Tiếp tục Làm Việc

Chạy các lệnh Git sau trong thư mục dự án để đẩy source code lên GitHub:

```bash
# 1. Khởi tạo kho lưu trữ git
git init

# 2. Thêm tất cả các file đã tạo vào staging
git add .

# 3. Tạo commit với thông tin định danh
git commit -m "feat(backend): thiet ke model hop_dong va endpoint POST /api/v1/contracts by Nguyen Van Hieu"

# 4. Đặt tên nhánh chính là main
git branch -M main

# 5. Liên kết tới repository GitHub của nhóm (thay URL bằng link repo thật của bạn)
git remote add origin https://github.com/<tai-khoan-cua-ban>/<ten-repository>.git

# 6. Đẩy mã nguồn lên GitHub
git push -u origin main
```

Sau khi push thành công, đội ngũ Frontend chỉ cần:
1. `git pull origin main` hoặc `git clone <URL>`
2. Khởi động backend tại `http://127.0.0.1:8000`
3. Gọi endpoint `POST /api/v1/contracts` để kết nối form nhập liệu hợp đồng.
