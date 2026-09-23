# Backend - Internship Management API

Hệ thống Backend xây dựng bằng **FastAPI** và **SQLAlchemy**, kết nối cơ sở dữ liệu **MySQL**, phục vụ API quản lý thực tập sinh cho Web.

---

## 📁 Cấu trúc thư mục

```text
backend/
├── database/
│   ├── database.py       # Cấu hình kết nối MySQL & cấp phát session (get_db)
│   └── models.py         # SQLAlchemy Model (bảng interns & hàm to_dict)
├── .env                  # Biến môi trường cá nhân (không push lên Git)
├── .env.example          # File mẫu cấu hình biến môi trường
├── CHANGELOG.md          # Nhật ký thay đổi tính năng Backend
├── main.py               # File chạy chính FastAPI & định nghĩa các API routes
├── schemas.py            # Pydantic Schemas định nghĩa & validate dữ liệu đầu vào
├── tests/
│   └── test_get_put.py   # Bộ Unit Test tự động cho các API (GET & PUT)
├── README.md             # Tài liệu hướng dẫn sử dụng Backend
└── requirements.txt      # Danh sách thư viện Python cần cài đặt
```

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy (Dành cho thành viên nhóm)

### 1. Cài đặt thư viện
Mở terminal tại thư mục `backend/` và chạy lệnh:
```bash
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
1. Sao chép file `.env.example` thành file `.env`:
   ```bash
   cp .env.example .env
   ```
2. Mở file `.env` và điền thông tin kết nối MySQL của bạn (nếu mật khẩu khác mặc định):
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=intern_management
   ```

### 3. Khởi tạo Cơ sở dữ liệu (Database)
Nếu máy bạn chưa có CSDL và bảng `interns`, đứng từ thư mục gốc của dự án và chạy:
```bash
python script/init_db.py
```
*(Script sẽ tự động tạo database `intern_management`, bảng `interns` và nạp sẵn 3 thực tập sinh mẫu).*

### 4. Khởi chạy Server
Tại thư mục `backend/`, chạy lệnh:
```bash
uvicorn main:app --reload
```
* Server chạy tại: `http://127.0.0.1:8000`
* Xem tài liệu API trực quan & test trực tiếp (Swagger UI): `http://127.0.0.1:8000/docs`

### 5. Chạy Kiểm thử tự động (Unit Test)
Tại thư mục `backend/`, chạy lệnh:
```bash
pytest -v
```
*(Thực thi 15 unit test: trường hợp đúng, sai định dạng, kiểm thử biên, ngoại lệ null và trùng lặp CSDL).*

---

## 📡 Tài liệu API (API Documentation)

### 1. Lấy thông tin chi tiết một thực tập sinh
* **URL:** `/api/interns/{id}`
* **Method:** `GET`
* **URL Params:** `id=[integer]` (Bắt buộc)

#### Response mẫu:

* **Thành công (HTTP 200 OK):**
```json
{
  "status_code": 200,
  "message": "Thông tin thực tập sinh",
  "data": {
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "vana@example.com",
    "phone": "0912345678",
    "university": "Đại học Thái Nguyên",
    "major": "Công nghệ thông tin",
    "status": "Đang thực tập",
    "start_date": "2026-09-01",
    "end_date": "2026-12-01",
    "created_at": "2026-09-22T23:00:00"
  }
}
```

* **Không tìm thấy (HTTP 404 Not Found):**
```json
{
  "detail": "Không tìm thấy thực tập sinh ID: 99"
}
```

* **ID sai định dạng (HTTP 422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["path", "id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

### 2. Cập nhật thông tin thực tập sinh
* **URL:** `/api/interns/{id}`
* **Method:** `PUT`
* **URL Params:** `id=[integer]` (Bắt buộc)
* **Request Body (JSON):**
```json
{
  "full_name": "Nguyễn Văn A",
  "email": "vana_update@example.com",
  "phone": "0912345678",
  "university": "Đại học Thái Nguyên",
  "major": "Công nghệ thông tin",
  "status": "Đang thực tập",
  "start_date": "2026-09-01",
  "end_date": "2026-12-01"
}
```

> **Quy tắc Validate phía Server:**
> - `full_name`: Bắt buộc, tối đa 50 ký tự, không được để trống hoặc chỉ chứa khoảng trắng, chỉ chứa chữ cái tiếng Việt.
> - `email`: Bắt buộc, tối đa 100 ký tự, đúng định dạng email, không được trùng với thực tập sinh khác trong database.
> - `phone`: Không bắt buộc nhập; nếu nhập thì phải đúng 10 số và không được trùng với thực tập sinh khác trong database.
> - `start_date`, `end_date`: Nếu có cả hai ngày thì ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.

#### Response mẫu:

* **Thành công (HTTP 200 OK):**
```json
{
  "status_code": 200,
  "message": "Cập nhật thông tin thực tập sinh thành công",
  "data": {
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "email": "vana_update@example.com",
    "phone": "0912345678",
    "university": "Đại học Thái Nguyên",
    "major": "Công nghệ thông tin",
    "status": "Đang thực tập",
    "start_date": "2026-09-01",
    "end_date": "2026-12-01",
    "created_at": "2026-09-22T23:00:00"
  }
}
```

* **Trùng email với thực tập sinh khác (HTTP 400 Bad Request):**
```json
{
  "detail": "Email này đã được sử dụng"
}
```

* **Không tìm thấy thực tập sinh (HTTP 404 Not Found):**
```json
{
  "detail": "Không tìm thấy thực tập sinh ID: 99"
}
```

* **Dữ liệu không hợp lệ / Thiếu trường bắt buộc (HTTP 422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "full_name"],
      "msg": "Value error, Họ tên không được để trống hoặc chỉ chứa khoảng trắng"
    }
  ]
}
```

