# Backend - Internship Management API

Hệ thống Backend xây dựng bằng **FastAPI** và **SQLAlchemy**, kết nối cơ sở dữ liệu **MySQL**, phục vụ API quản lý thực tập sinh cho Web.

---

## 📁 Cấu trúc thư mục

```text
backend/
├── database/
│   ├── session.py        # Cấu hình kết nối MySQL & cấp phát session (get_db, Base)
│   ├── models.py         # SQLAlchemy Models (NguoiDung, HoSoThucTap, Truong,...)
│   └── DATABASE_DESIGN.md # Tài liệu tham chiếu thiết kế CSDL
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

## 🚀 Hướng dẫn cài đặt & Khởi chạy

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
2. Mở file `.env` và điền thông tin kết nối MySQL của bạn:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=intern_management
   ```

### 3. Khởi tạo Cơ sở dữ liệu (Database & Seed Data)
Đứng từ thư mục gốc của dự án (`ttcs/`) và chạy script tạo bảng & nạp dữ liệu mẫu:
```bash
python script/init_db.py
```
*(Script sẽ tạo các bảng `phong_ban`, `truong_dai_hoc`, `chuong_trinh_thuc_tap`, `nguoi_dung`, `ho_so_thuc_tap` và nạp sẵn dữ liệu test).*

### 4. Khởi chạy Server
Tại thư mục `backend/`, chạy lệnh:
```bash
uvicorn main:app --reload
```
* **Server chạy tại:** `http://127.0.0.1:8000`
* **Trang tài liệu tương tác (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 🧪 Hướng dẫn Test thủ công (Không tự động / Manual Testing)

Bạn có thể test trực tiếp các API mà không cần chạy code tự động bằng 3 cách sau:

### Cách 1: Test trực quan trên Trình duyệt bằng Swagger UI (Khuyên dùng - Nhanh nhất)
1. Bật server bằng lệnh `uvicorn main:app --reload`.
2. Mở trình duyệt và truy cập: **`http://127.0.0.1:8000/docs`**
3. **Test API GET (Lấy chi tiết thực tập sinh):**
   - Bấm vào mục **`GET /api/v1/interns/{id}`**.
   - Bấm nút **`Try it out`** ở góc phải.
   - Nhập `id`: `1` (hoặc `2`).
   - Bấm **`Execute`** và xem kết quả HTTP 200 ở khung bên dưới.
   - Thử nhập `id`: `9999` để kiểm tra phản hồi lỗi `404 Not Found`.
4. **Test API PUT (Cập nhật hồ sơ thực tập sinh):**
   - Bấm vào mục **`PUT /api/v1/interns/{id}`**.
   - Bấm nút **`Try it out`**.
   - Nhập `id`: `1`.
   - Trong ô **Request body**, dán JSON cập nhật mẫu:
     ```json
     {
       "ho_ten": "Nguyễn Văn A Cập Nhật",
       "email": "vana@example.com",
       "so_dien_thoai": "0912345678",
       "chuyen_nganh": "Công nghệ thông tin",
       "ma_truong": 1,
       "trang_thai_thuc_tap": "DangThucTap"
     }
     ```
   - Bấm **`Execute`** và kiểm tra kết quả phản hồi 200.
   - Thử đổi `email` thành `thib@example.com` (email của user 2) để test lỗi trùng lặp `400 Bad Request`.

---

### Cách 2: Test bằng Postman hoặc Thunder Client (VS Code)

#### 1. Test GET:
* **Method:** `GET`
* **URL:** `http://localhost:8000/api/v1/interns/1`
* Bấm **Send**.

#### 2. Test PUT:
* **Method:** `PUT`
* **URL:** `http://localhost:8000/api/v1/interns/1`
* **Headers:** Thêm `Content-Type: application/json`
* **Body** (chọn `raw` -> `JSON`):
  ```json
  {
    "ho_ten": "Nguyễn Văn A",
    "email": "vana@example.com",
    "so_dien_thoai": "0912345678",
    "chuyen_nganh": "Kỹ thuật phần mềm",
    "ma_truong": 2,
    "trang_thai_thuc_tap": "DangThucTap"
  }
  ```
* Bấm **Send**.

---

### Cách 3: Test bằng lệnh cURL trong Terminal

#### 1. Lệnh gọi GET:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/interns/1" -H "accept: application/json"
```

#### 2. Lệnh gọi PUT:
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/interns/1" \
  -H "Content-Type: application/json" \
  -d "{\"ho_ten\": \"Nguyễn Văn A\", \"email\": \"vana@example.com\", \"so_dien_thoai\": \"0912345678\", \"chuyen_nganh\": \"Công nghệ phần mềm\", \"ma_truong\": 1, \"trang_thai_thuc_tap\": \"DangThucTap\"}"
```

---

## 🤖 Chạy Kiểm thử tự động (Unit Test với Pytest)
Khi cần chạy kiểm thử toàn bộ 14 test case tự động:
```bash
pytest backend/tests/test_get_put.py -v
```

---

## 📡 Tài liệu API (API Specification)

### 1. Lấy thông tin chi tiết một thực tập sinh
* **URL:** `/api/v1/interns/{id}`
* **Method:** `GET`
* **URL Params:** `id=[integer]` (Mã hồ sơ thực tập)

#### Response mẫu (HTTP 200 OK):
```json
{
  "status_code": 200,
  "message": "Thông tin thực tập sinh",
  "data": {
    "ma_ho_so": 1,
    "ma_nguoi_dung": 1,
    "ho_ten": "Nguyễn Văn A",
    "email": "vana@example.com",
    "so_dien_thoai": "0912345678",
    "chuyen_nganh": "Công nghệ thông tin",
    "ma_truong": 1,
    "ten_truong": "Đại học Thái Nguyên",
    "ma_chuong_trinh": 1,
    "ten_chuong_trinh": "Thực tập sinh Khóa Mùa Thu 2026",
    "ngay_bat_dau": "2026-09-01",
    "ngay_ket_thuc": "2026-12-30",
    "ma_mentor": 3,
    "ten_mentor": "Nguyễn Hướng Dẫn",
    "trang_thai_xet_duyet": "DaDuyet",
    "trang_thai_thuc_tap": "DangThucTap"
  }
}
```

---

### 2. Cập nhật thông tin thực tập sinh
* **URL:** `/api/v1/interns/{id}`
* **Method:** `PUT`
* **URL Params:** `id=[integer]` (Mã hồ sơ thực tập)
* **Request Body (JSON):**
```json
{
  "ho_ten": "Nguyễn Văn A",
  "email": "vana@example.com",
  "so_dien_thoai": "0912345678",
  "chuyen_nganh": "Kỹ thuật phần mềm",
  "ma_truong": 1,
  "trang_thai_thuc_tap": "DangThucTap"
}
```

> **Quy tắc Validate:**
> - `ho_ten`: Bắt buộc, tối đa 100 ký tự, không được để trống hoặc chỉ chứa khoảng trắng, chỉ chứa chữ cái tiếng Việt.
> - `email`: Bắt buộc, đúng cú pháp email, không được trùng với tài khoản khác trong hệ thống.
> - `so_dien_thoai`: Tùy chọn; nếu nhập phải đúng 10 số (bắt đầu bằng `0` hoặc `+84`), không được trùng với tài khoản khác.
> - `ma_truong`: Tùy chọn; nếu nhập phải tồn tại trong bảng `truong_dai_hoc`.
