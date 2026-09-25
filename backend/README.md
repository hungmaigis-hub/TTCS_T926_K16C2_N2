# Backend - Internship Management API

Hệ thống Backend xây dựng bằng **FastAPI** và **SQLAlchemy**, kết nối cơ sở dữ liệu **MySQL**, phục vụ API quản lý thực tập sinh cho Web.

---

## 📁 Cấu trúc thư mục

```text
backend/
├── database/
│   ├── session.py        # Cấu hình kết nối MySQL & cấp phát session (get_db, Base)
│   ├── models/           # Package ORM Models (tách file theo thực thể)
│   │   ├── __init__.py
│   │   ├── phong_ban.py      # Model PhongBan
│   │   ├── truong_dai_hoc.py # Model TruongDaiHoc
│   │   ├── chuong_trinh.py   # Model ChuongTrinhThucTap
│   │   ├── nguoi_dung.py     # Model NguoiDung
│   │   ├── ho_so.py          # Model HoSoThucTap
│   │   └── tai_lieu.py       # Model TaiLieuHoSo
│   └── DATABASE_DESIGN.md # Tài liệu tham chiếu thiết kế CSDL
├── .env                  # Biến môi trường cá nhân (không push lên Git)
├── .env.example          # File mẫu cấu hình biến môi trường
├── CHANGELOG.md          # Nhật ký thay đổi tính năng Backend
├── main.py               # File chạy chính FastAPI & định nghĩa các API routes
├── schemas.py            # Pydantic Schemas định nghĩa & validate dữ liệu đầu vào
├── tests/
│   ├── test_get_put.py   # Bộ Unit Test API thông tin thực tập sinh (GET & PUT)
│   └── test_documents.py # Bộ Unit Test API tài liệu hồ sơ (GET & PATCH)
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
*(Script sẽ tạo các bảng `phong_ban`, `truong_dai_hoc`, `chuong_trinh_thuc_tap`, `nguoi_dung`, `ho_so_thuc_tap`, `tai_lieu_ho_so` và nạp sẵn dữ liệu test).*

### 4. Khởi chạy Server
Tại thư mục `backend/`, chạy lệnh:
```bash
uvicorn main:app --reload
```
* **Server chạy tại:** `http://127.0.0.1:8000`
* **Trang tài liệu tương tác (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 🧪 Hướng dẫn Test thủ công (Manual Testing)

Bạn có thể test trực tiếp các API mà không cần chạy code tự động bằng 3 cách sau:

### Cách 1: Test trực quan trên Trình duyệt bằng Swagger UI (Khuyên dùng)
1. Bật server bằng lệnh `uvicorn main:app --reload`.
2. Mở trình duyệt và truy cập: **`http://127.0.0.1:8000/docs`**
3. **Test API Documents:**
   - **`GET /api/v1/documents/{ho_so_id}`**: Bấm `Try it out` -> Nhập `ho_so_id = 1` -> Bấm `Execute` để xem danh sách tài liệu. Thử `ho_so_id = 99999` để kiểm tra lỗi 404.
   - **`PATCH /api/v1/documents/{id}/status`**: Bấm `Try it out` -> Nhập `id = 1` -> Dán body `{"trang_thai_duyet": "DaDuyet"}` -> Bấm `Execute`. Thử truyền `"KhongHopLe"` để kiểm tra lỗi 422.

---

### Cách 2: Test bằng lệnh cURL trong Terminal

#### 1. Lấy danh sách tài liệu theo hồ sơ:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/documents/1" -H "accept: application/json"
```

#### 2. Cập nhật trạng thái duyệt tài liệu:
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/documents/1/status" \
  -H "Content-Type: application/json" \
  -d "{\"trang_thai_duyet\": \"DaDuyet\"}"
```

---

## 🤖 Chạy Toàn bộ Kiểm thử tự động (Pytest)
Tại thư mục `backend/`, chạy lệnh:
```bash
pytest -v
```
*(Thực thi trọn bộ 35 unit test: bao gồm đầy đủ test biên, case đúng, case sai giá trị, case ngoại lệ null và ID không tồn tại).*

---

## 📡 Tài liệu API (API Specification)

### 1. Lấy thông tin chi tiết một thực tập sinh
* **URL:** `/api/v1/interns/{id}`
* **Method:** `GET`
* **URL Params:** `id=[integer]` (Mã hồ sơ thực tập)

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

---

### 3. Lấy danh sách tài liệu theo mã hồ sơ thực tập
* **URL:** `/api/v1/documents/{ho_so_id}`
* **Method:** `GET`
* **URL Params:** `ho_so_id=[integer]` (Mã hồ sơ thực tập)

#### Response mẫu (HTTP 200 OK):
```json
{
  "status_code": 200,
  "message": "Danh sách tài liệu của hồ sơ thực tập",
  "data": [
    {
      "ma_tai_lieu": 1,
      "ma_ho_so": 1,
      "loai_tai_lieu": "CV",
      "duong_dan_file": "uploads/cv_nguyen_van_a.pdf",
      "trang_thai_duyet": "ChoDuyet"
    },
    {
      "ma_tai_lieu": 2,
      "ma_ho_so": 1,
      "loai_tai_lieu": "DonXinThucTap",
      "duong_dan_file": "uploads/don_xin_nguyen_van_a.pdf",
      "trang_thai_duyet": "DaDuyet"
    }
  ]
}
```

---

### 4. Cập nhật trạng thái duyệt tài liệu
* **URL:** `/api/v1/documents/{id}/status`
* **Method:** `PATCH`
* **URL Params:** `id=[integer]` (Mã tài liệu)
* **Request Body (JSON):**
```json
{
  "trang_thai_duyet": "DaDuyet"
}
```

> **Quy tắc Validate:**
> - `trang_thai_duyet`: Bắt buộc, chỉ nhận một trong 3 giá trị: `"ChoDuyet"`, `"DaDuyet"`, `"TuChoi"`. Nếu truyền bất kỳ giá trị nào khác, rỗng hoặc `null` sẽ tự động trả về `HTTP 422 Unprocessable Entity`.
