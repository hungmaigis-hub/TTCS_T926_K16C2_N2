# Backend - Internship Management API

Hệ thống Backend xây dựng bằng **FastAPI** và **SQLAlchemy**, kết nối cơ sở dữ liệu **MySQL**, phục vụ API quản lý thực tập sinh cho Web.

---

## 📁 Cấu trúc thư mục

```text
backend/
├── database/
│   ├── session.py              # Cấu hình kết nối MySQL & cấp phát session (get_db, Base)
│   ├── models/                 # Package ORM Models (tách file theo thực thể)
│   │   ├── __init__.py
│   │   ├── phong_ban.py        # Model PhongBan
│   │   ├── truong_dai_hoc.py   # Model TruongDaiHoc
│   │   ├── chuong_trinh.py     # Model ChuongTrinhThucTap
│   │   ├── nguoi_dung.py       # Model NguoiDung
│   │   ├── ho_so.py            # Model HoSoThucTap
│   │   └── tai_lieu.py         # Model TaiLieuHoSo
│   └── DATABASE_DESIGN.md       # Tài liệu tham chiếu thiết kế CSDL
├── services/
│   ├── __init__.py
│   └── email_service.py        # Dịch vụ gửi email thông báo kết quả duyệt (SMTP/Mock)
├── .env                        # Biến môi trường cá nhân (không push lên Git)
├── .env.example                # File mẫu cấu hình biến môi trường
├── CHANGELOG.md                # Nhật ký thay đổi tính năng Backend
├── main.py                     # File chạy chính FastAPI & định nghĩa các API routes
├── schemas.py                  # Pydantic Schemas định nghĩa & validate dữ liệu đầu vào
├── uploads/                # Thư mục lưu trữ file tài liệu đính kèm trên server
├── tests/
│   ├── conftest.py             # Cấu hình test fixtures & SQLite fallback
│   ├── test_create_intern.py   # Bộ Unit Test API tạo hồ sơ thực tập sinh (POST)
│   ├── test_get_put.py         # Bộ Unit Test API thông tin thực tập sinh (GET & PUT)
│   ├── test_upload_document.py # Bộ Unit Test API tải lên tài liệu hồ sơ (POST)
│   ├── test_documents.py       # Bộ Unit Test API tài liệu hồ sơ (GET & PATCH)
│   ├── test_email_notification.py # Bộ Unit Test gửi email trong nền sau khi duyệt
│   └── test_programs.py        # Bộ Unit Test API tạo chương trình thực tập (POST)
├── README.md                   # Tài liệu hướng dẫn sử dụng Backend
└── requirements.txt            # Danh sách thư viện Python cần cài đặt
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
2. Mở file `.env` và điền thông tin kết nối MySQL & Email của bạn:
   ```env
   # Database MySQL
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=intern_management

   # Cấu hình Gửi Email (SMTP)
   # Nếu để MAIL_ENABLED=false, hệ thống sẽ chạy ở chế độ mô phỏng (log console), an toàn cho Dev & Test
   MAIL_ENABLED=false
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SMTP_FROM_EMAIL=no-reply@internship.local
   SMTP_FROM_NAME=Hệ thống Quản lý Thực tập sinh
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
1. Bật server bằng lệnh `uvicorn main:app --reload` (hoặc `python -m uvicorn main:app --reload`).
2. Mở trình duyệt và truy cập: **`http://127.0.0.1:8000/docs`**
3. **Test API Xác nhận Hợp đồng & Kích hoạt Thực tập:**
   - **`PATCH /api/v1/contracts/{id}/confirm`**: Bấm `Try it out` -> Nhập `id = 1` -> Dán body:
     ```json
     {
       "trang_thai": "DaXacNhan",
       "trang_thai_thuc_tap": "DangThucTap",
       "ghi_chu": "Mã xác thực OTP: ICTU-SIGNED-9921-OK"
     }
     ```
     -> Bấm `Execute`. Kiểm tra `trang_thai` đổi thành `DaXacNhan` và hồ sơ đổi sang `DangThucTap`.
4. **Test API Phê duyệt Hồ sơ Thực tập sinh:**
   - **`PATCH /api/v1/interns/{id}/approval`**: Bấm `Try it out` -> Nhập `id = 1` -> Dán body:
     ```json
     {
       "trang_thai_duyet": "DaDuyet",
       "ghi_chu": "Hồ sơ và phỏng vấn đạt yêu cầu"
     }
     ```
     -> Bấm `Execute`. Thử `trang_thai_duyet = "KhongHopLe"` để kiểm tra lỗi 422.
5. **Test API Documents:**
   - **`GET /api/v1/documents/{ho_so_id}`**: Bấm `Try it out` -> Nhập `ho_so_id = 1` -> Bấm `Execute` để xem danh sách tài liệu. Thử `ho_so_id = 99999` để kiểm tra lỗi 404.
   - **`PATCH /api/v1/documents/{id}/status`**: Bấm `Try it out` -> Nhập `id = 1` -> Dán body `{"trang_thai_duyet": "DaDuyet"}` -> Bấm `Execute`. Thử truyền `"KhongHopLe"` để kiểm tra lỗi 422.

---

### Cách 2: Test bằng lệnh cURL trong Terminal

#### 1. Xác nhận ký hợp đồng thực tập điện tử:
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/contracts/1/confirm" \
  -H "Content-Type: application/json" \
  -d "{\"trang_thai\": \"DaXacNhan\", \"trang_thai_thuc_tap\": \"DangThucTap\", \"ghi_chu\": \"OTP: ICTU-SIGNED-9921-OK\"}"
```

#### 2. Cập nhật trạng thái xét duyệt hồ sơ thực tập sinh (Phê duyệt / Từ chối):
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/interns/1/approval" \
  -H "Content-Type: application/json" \
  -d "{\"trang_thai_duyet\": \"DaDuyet\", \"ghi_chu\": \"Đạt điều kiện tiếp nhận thực tập\"}"
```

#### 3. Lấy danh sách tài liệu theo hồ sơ:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/documents/1" -H "accept: application/json"
```

#### 4. Cập nhật trạng thái duyệt tài liệu:
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
*(Thực thi trọn bộ **123 unit test**: bao gồm đầy đủ tạo hồ sơ POST, cập nhật PUT, duyệt hồ sơ PATCH, xác nhận hợp đồng PATCH kèm email BackgroundTasks, truy vấn GET, upload tài liệu POST, duyệt tài liệu PATCH, tạo chương trình POST, cập nhật tiến độ nhiệm vụ PATCH và xử lý ngoại lệ).*

---

## 📡 Tài liệu API (API Specification)

### 1. Tạo mới hồ sơ thực tập sinh
* **URL:** `/api/v1/interns`
* **Method:** `POST`
* **Status Code:** `201 Created`
* **Request Body (JSON):**
```json
{
  "ho_ten": "Lê Văn Cường",
  "email": "cuong.le@example.com",
  "so_dien_thoai": "0933112233",
  "chuyen_nganh": "Kỹ thuật phần mềm",
  "ma_truong": 1,
  "ma_chuong_trinh": 1,
  "ma_mentor": 3,
  "trang_thai_xet_duyet": "ChoDuyet",
  "trang_thai_thuc_tap": "DangThucTap"
}
```
> **Ghi chú:**
> - `ho_ten`, `email`: Bắt buộc. Họ tên chỉ gồm chữ cái tiếng Việt, email đúng chuẩn.
> - `so_dien_thoai`: Tùy chọn, đúng 10 chữ số.
> - `ma_truong`, `ma_chuong_trinh`, `ma_mentor`: Tùy chọn, hệ thống tự động kiểm tra tính tồn tại trong CSDL.
> - Hệ thống tự động tạo đồng thời tài khoản người dùng (`vai_tro='ThucTapSinh'`) và hồ sơ trong cùng một giao dịch database.

---

### 2. Lấy thông tin chi tiết một thực tập sinh
* **URL:** `/api/v1/interns/{id}`
* **Method:** `GET`
* **URL Params:** `id=[integer]` (Mã hồ sơ thực tập)

---

### 3. Cập nhật thông tin thực tập sinh
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

### 4. Cập nhật trạng thái xét duyệt hồ sơ thực tập sinh (Phê duyệt / Từ chối)
* **URL:** `/api/v1/interns/{id}/approval`
* **Method:** `PATCH`
* **Status Code:** `200 OK`
* **URL Params:** `id=[integer]` (Mã hồ sơ thực tập)
* **Request Body (JSON):**
```json
{
  "trang_thai_duyet": "DaDuyet",
  "ghi_chu": "Hồ sơ đạt tiêu chuẩn tuyển dụng, phỏng vấn tốt"
}
```
> **Quy tắc Validate & Tính năng:**
> - `trang_thai_duyet` (hoặc `trang_thai_xet_duyet`): Bắt buộc, chỉ nhận `"ChoDuyet"`, `"DaDuyet"`, hoặc `"TuChoi"`. Tự động chuẩn hóa loại bỏ khoảng trắng thừa đầu cuối.
> - `ghi_chu`: Tùy chọn, tối đa 500 ký tự (lý do từ chối hoặc nhận xét đánh giá).
> - **Gửi Email tự động:** Sau khi cập nhật CSDL thành công, hệ thống tự động kích hoạt `BackgroundTasks` gửi email thông báo kết quả (Chúc mừng nếu Đã duyệt / Nêu lý do nếu Từ chối) tới địa chỉ email của thực tập sinh.

#### Response mẫu (HTTP 200 OK):
```json
{
  "status_code": 200,
  "message": "Cập nhật trạng thái xét duyệt hồ sơ thành công",
  "data": {
    "ma_ho_so": 1,
    "ma_nguoi_dung": 1,
    "ho_ten": "Nguyễn Văn A",
    "email": "vana@example.com",
    "trang_thai_xet_duyet": "DaDuyet",
    "trang_thai_thuc_tap": "ChuaThucTap"
  }
}
```

---

### 5. Xác nhận ký hợp đồng thực tập & kích hoạt trạng thái thực tập
* **URL:** `/api/v1/contracts/{id}/confirm`
* **Method:** `PATCH`
* **Status Code:** `200 OK`
* **URL Params:** `id=[integer]` (Mã hợp đồng thực tập)
* **Request Body (JSON, tùy chọn):**
```json
{
  "trang_thai": "DaXacNhan",
  "trang_thai_thuc_tap": "DangThucTap",
  "ngay_ky": "2026-09-27",
  "ghi_chu": "Mã xác thực OTP: ICTU-SIGNED-9921-OK"
}
```
> **Quy tắc Validate & Tính năng:**
> - `trang_thai`: Tùy chọn (mặc định: `"DaXacNhan"`). Chỉ chấp nhận `"ChuaXacNhan"`, `"DaXacNhan"`.
> - `trang_thai_thuc_tap`: Tùy chọn (mặc định: `"DangThucTap"`). Tự động đồng bộ sang bảng `ho_so_thuc_tap`.
> - `ngay_ky`: Tùy chọn (mặc định tự lấy ngày hiện tại trên server).
> - `ghi_chu`: Tùy chọn, tối đa 500 ký tự (lưu mã OTP chữ ký số).
> - **Giao dịch nguyên tử (Atomic Transaction):** Cập nhật đồng thời trạng thái hợp đồng và trạng thái thực tập của sinh viên trong một commit duy nhất.
> - **Gửi Email tự động qua BackgroundTasks:** Gửi email thông báo ký kết thành công và chào mừng bắt đầu kỳ thực tập chính thức.

#### Response mẫu (HTTP 200 OK):
```json
{
  "status_code": 200,
  "message": "Xác nhận ký hợp đồng và cập nhật trạng thái thực tập thành công",
  "data": {
    "ma_hop_dong": 1,
    "ma_ho_so": 1,
    "duong_dan_file": "uploads/hop_dong_nguyen_van_a.pdf",
    "ngay_tai_len": "2026-09-20",
    "ngay_ky": "2026-09-27",
    "trang_thai": "DaXacNhan",
    "trang_thai_thuc_tap": "DangThucTap",
    "sinh_vien": {
      "ho_ten": "Nguyễn Văn A",
      "email": "vana@example.com",
      "chuyen_nganh": "Công nghệ thông tin"
    }
  }
}
```

---

### 6. Tải lên tài liệu đính kèm cho hồ sơ thực tập
* **URL:** `/api/v1/documents/upload`
* **Method:** `POST`
* **Status Code:** `201 Created`
* **Content-Type:** `multipart/form-data`
* **Form Data:**
  * `ma_ho_so`: `int` (bắt buộc) - Mã hồ sơ thực tập
  * `loai_tai_lieu`: `str` (bắt buộc) - Loại tài liệu (`CV`, `DonXinThucTap`, `GiayGioiThieu`, `BangDiem`...)
  * `file`: `UploadFile` (bắt buộc) - File tài liệu đính kèm (`.pdf`, `.docx`, `.png`, `.jpg`..., tối đa 10MB)

#### Response mẫu (HTTP 201 Created):
```json
{
  "status_code": 201,
  "message": "Tải lên tài liệu thành công",
  "data": {
    "ma_tai_lieu": 3,
    "ma_ho_so": 1,
    "loai_tai_lieu": "CV",
    "duong_dan_file": "uploads/1_CV_8f2b1a9c.pdf",
    "trang_thai_duyet": "ChoDuyet"
  }
}
```

---

### 7. Lấy danh sách tài liệu theo mã hồ sơ thực tập
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

### 8. Cập nhật trạng thái duyệt tài liệu
* **URL:** `/api/v1/documents/{id}/status`
* **Method:** `PATCH`
* **URL Params:** `id=[integer]` (Mã tài liệu)
* **Request Body (JSON):**
```json
{
  "trang_thai_duyet": "DaDuyet",
  "ghi_chu": "Tài liệu hợp lệ"
}
```

> **Quy tắc Validate:**
> - `trang_thai_duyet`: Bắt buộc, chỉ nhận một trong 3 giá trị: `"ChoDuyet"`, `"DaDuyet"`, `"TuChoi"`. Nếu truyền bất kỳ giá trị nào khác, rỗng hoặc `null` sẽ tự động trả về `HTTP 422 Unprocessable Entity`.
> - `ghi_chu`: Tùy chọn, tối đa 500 ký tự.

---

### 5. Tạo mới chương trình thực tập
* **URL:** `/api/v1/programs`
* **Method:** `POST`
* **Request Body (JSON):**
```json
{
  "ma_phong_ban": 1,
  "ten_chuong_trinh": "Chương trình Kỹ sư AI 2026",
  "mo_ta": "Đào tạo chuyên sâu AI và Machine Learning",
  "ngay_bat_dau": "2026-10-01",
  "ngay_ket_thuc": "2026-12-31"
}
```

> **Quy tắc Validate:**
> - `ma_phong_ban`: Bắt buộc, số nguyên dương > 0. Nếu mã phòng ban không tồn tại trong hệ thống sẽ trả về `HTTP 400 Bad Request`.
> - `ten_chuong_trinh`: Bắt buộc, chuỗi từ 1 đến 150 ký tự, không được để trống hoặc chỉ chứa khoảng trắng. Nếu trùng tên trong cùng phòng ban sẽ trả về `HTTP 400 Bad Request`.
> - `mo_ta`: Tùy chọn, chuỗi văn bản mô tả nội dung.
> - `ngay_bat_dau`, `ngay_ket_thuc`: Tùy chọn. Nếu không truyền, hệ thống tự động gán ngày bắt đầu là hôm nay và ngày kết thúc sau 90 ngày. Nếu truyền thì bắt buộc `ngay_ket_thuc >= ngay_bat_dau`, vi phạm sẽ trả về `HTTP 422 Unprocessable Entity`.
* **Phản hồi thành công (HTTP 201 Created):**
```json
{
  "status_code": 201,
  "message": "Tạo chương trình thực tập thành công",
  "data": {
    "ma_chuong_trinh": 2,
    "ma_phong_ban": 1,
    "ten_phong_ban": "Trung tâm Phần mềm",
    "ten_chuong_trinh": "Chương trình Kỹ sư AI 2026",
    "ngay_bat_dau": "2026-10-01",
    "ngay_ket_thuc": "2026-12-31",
    "mo_ta": "Đào tạo chuyên sâu AI và Machine Learning"
  }
}

---

### 6. Cập nhật thời gian chương trình thực tập (Timeline)
* **URL:** `/api/v1/programs/{id}/timeline`
* **Method:** `PATCH`
* **Status Code:** `200 OK`
* **URL Params:** `id=[integer]` (Mã chương trình thực tập)
* **Request Body (JSON):**
```json
{
  "ngay_bat_dau": "2026-10-01",
  "ngay_ket_thuc": "2026-12-31"
}
```

> **Quy tắc Validate & Nghiệp vụ:**
> - `ngay_bat_dau`, `ngay_ket_thuc`: Tùy chọn (cho phép cập nhật một hoặc cả hai trường).
> - Yêu cầu cung cấp ít nhất một trường trong payload, nếu rỗng sẽ trả về `HTTP 422 Unprocessable Entity`.
> - **Quy tắc thời gian bắt buộc:** `ngay_ket_thuc > ngay_bat_dau` (ngày kết thúc phải lớn hơn ngày bắt đầu).
>   - Nếu gửi cả hai ngày mà `ngay_ket_thuc <= ngay_bat_dau`: Trả về `HTTP 422 Unprocessable Entity`.
>   - Nếu chỉ gửi một ngày mà xung đột với mốc thời gian hiện tại trong CSDL: Trả về `HTTP 400 Bad Request`.
> - `id`: Nếu không tìm thấy chương trình thực tập trong hệ thống sẽ trả về `HTTP 404 Not Found`.

* **Phản hồi thành công (HTTP 200 OK):**
```json
{
  "status_code": 200,
  "message": "Cập nhật thời gian chương trình thực tập thành công",
  "data": {
    "ma_chuong_trinh": 1,
    "ma_phong_ban": 1,
    "ten_phong_ban": "Trung tâm Phần mềm",
    "ten_chuong_trinh": "Thực tập sinh Khóa Mùa Thu 2026",
    "ngay_bat_dau": "2026-10-01",
    "ngay_ket_thuc": "2026-12-31",
    "mo_ta": "Chương trình đào tạo kỹ sư phần mềm thực chiến"
  }
}
```

---

### 9. Cập nhật tiến độ nhiệm vụ thực tập sinh
* **URL:** `/api/v1/tasks/{id}/progress`
* **Method:** `PATCH`
* **Status Code:** `200 OK`
* **URL Params:** `id=[integer]` (Mã nhiệm vụ)
* **Request Body (JSON):**
```json
{
  "tien_do_phantram": 100
}
```
> **Quy tắc Validate & Tính năng:**
> - `tien_do_phantram`: Bắt buộc, số nguyên trong khoảng `0` đến `100`. Nếu vi phạm sẽ trả về `HTTP 422 Unprocessable Entity`.
> - **Tự động cập nhật trạng thái (`trang_thai`):**
>   - Đạt `100%`: Tự động chuyển `trang_thai = "Hoàn thành"`.
>   - Từ `1%` đến `99%`: Tự động chuyển `trang_thai = "Đang thực hiện"`.
>   - Bằng `0%`: Tự động chuyển `trang_thai = "Chưa bắt đầu"`.
> - Nếu mã nhiệm vụ không tồn tại: Trả về `HTTP 404 Not Found`.

#### Response mẫu (HTTP 200 OK):
```json
{
  "status_code": 200,
  "message": "Cập nhật tiến độ nhiệm vụ thành công",
  "data": {
    "ma_nhiem_vu": 1,
    "ma_ho_so": 1,
    "ten_nhiem_vu": "Nghiên cứu tài liệu kiến trúc hệ thống",
    "mo_ta": "Đọc hiểu tài liệu thiết kế CSDL và luồng xử lý API",
    "han_hoan_thanh": "2026-10-15",
    "tien_do_phantram": 100,
    "trang_thai": "Hoàn thành"
  }
}
```

---

### 10. Tạo mới đánh giá kết quả thực tập
* **URL:** `/api/v1/evaluations`
* **Method:** `POST`
* **Status Code:** `201 Created`
* **Request Body (JSON):**
```json
{
  "ma_ho_so": 1,
  "ma_nguoi_danh_gia": 3,
  "loai_danh_gia": "CuoiKy",
  "diem_ky_nang": 8.5,
  "diem_thai_do": 9.0,
  "nhan_xet": "Sinh viên tiếp thu nhanh, hoàn thành tốt các nhiệm vụ được giao.",
  "de_xuat_tuyen_dung": true
}
```

> **Quy tắc Validate & Tính năng:**
> - `ma_ho_so`: Bắt buộc, số nguyên dương > 0. Nếu không tìm thấy hồ sơ sẽ trả về `HTTP 404 Not Found`.
> - `ma_nguoi_danh_gia`: Bắt buộc, số nguyên dương > 0. Nếu người đánh giá không tồn tại trong hệ thống sẽ trả về `HTTP 400 Bad Request`.
> - `loai_danh_gia`: Bắt buộc, chỉ nhận `"GiuaKy"` hoặc `"CuoiKy"`. Giá trị khác sẽ trả về `HTTP 422 Unprocessable Entity`.
> - `diem_ky_nang`, `diem_thai_do`: Bắt buộc, số thực trong khoảng `0.0` đến `10.0`. Nếu ngoài khoảng sẽ trả về `HTTP 422 Unprocessable Entity`.
> - `nhan_xet`: Tùy chọn (hỗ trợ cả alias `nhan_xet_chi_tiet`).
> - `de_xuat_tuyen_dung`: Tùy chọn, kiểu boolean (hỗ trợ cả alias `de_xuat_tuyen_chinh_thuc`).
> - **Chống trùng lặp:** Mỗi hồ sơ chỉ có tối đa 1 đánh giá giữa kỳ và 1 đánh giá cuối kỳ. Trùng lặp sẽ trả về `HTTP 400 Bad Request`.
> - **Tự động tính toán:** Tự động tính điểm trung bình (`diem_trung_binh`) và xếp loại rèn luyện (`xep_loai`: XuatSac, Gioi, Kha, TrungBinh, Yeu).

* **Phản hồi thành công (HTTP 201 Created):**
```json
{
  "status_code": 201,
  "message": "Tạo đánh giá thực tập sinh thành công",
  "data": {
    "ma_danh_gia": 1,
    "ma_ho_so": 1,
    "ma_nguoi_danh_gia": 3,
    "ten_nguoi_danh_gia": "Nguyễn Hướng Dẫn",
    "loai_danh_gia": "CuoiKy",
    "diem_ky_nang": 8.5,
    "diem_thai_do": 9.0,
    "diem_trung_binh": 8.75,
    "xep_loai": "Gioi",
    "nhan_xet_chi_tiet": "Sinh viên tiếp thu nhanh, hoàn thành tốt các nhiệm vụ được giao.",
    "de_xuat_tuyen_chinh_thuc": true
  }
}
```

---

### 11. Điểm danh vào ca làm việc (Check-in)
* **URL:** `/api/v1/attendance/check-in`
* **Method:** `POST`
* **Status Code:** `201 Created`
* **Request Body (JSON):**
```json
{
  "ma_ho_so": 1,
  "thoi_gian_checkin": "2026-10-01T08:15:00",
  "phuong_thuc": "Web",
  "ghi_chu": "Check-in đúng giờ qua cổng Web"
}
```

> **Quy tắc Validate & Nghiệp vụ:**
> - `ma_ho_so`: Bắt buộc, số nguyên dương > 0. Nếu không tìm thấy hồ sơ sẽ trả về `HTTP 404 Not Found`.
> - `thoi_gian_checkin`: Tùy chọn (định dạng ISO 8601). Nếu không truyền hoặc truyền `null`, hệ thống tự động lấy thời gian hiện tại (`datetime.now()`).
> - `phuong_thuc`: Tùy chọn (`Web`, `QR`, `The`), mặc định là `"Web"`.
> - `ghi_chu`: Tùy chọn chuỗi ghi chú lý do.
> - **Quy tắc tính trạng thái chấm công (`trang_thai`):**
>   - Check-in trước hoặc đúng 08:30:00 $\rightarrow$ `DungGio` (Đúng giờ).
>   - Check-in sau 08:30:00 $\rightarrow$ `DiMuon` (Đi muộn).
> - **Chống trùng lặp:** Mỗi thực tập sinh chỉ được check-in 1 lần trong một ngày. Nếu đã check-in trong ngày, trả về `HTTP 400 Bad Request`.

#### Response mẫu (HTTP 201 Created):
```json
{
  "status_code": 201,
  "message": "Check-in thành công",
  "data": {
    "ma_cham_cong": 15,
    "ma_ho_so": 1,
    "ngay_cham_cong": "2026-10-01",
    "thoi_gian_checkin": "2026-10-01T08:15:00",
    "thoi_gian_checkout": null,
    "gio_check_in": "08:15:00",
    "gio_check_out": null,
    "trang_thai": "DungGio",
    "phuong_thuc": "Web",
    "ghi_chu": "Check-in đúng giờ qua cổng Web"
  }
}
```

---

### 12. Điểm danh kết thúc ca làm việc (Check-out)
* **URL:** `/api/v1/attendance/check-out`
* **Method:** `POST`
* **Status Code:** `200 OK`
* **Request Body (JSON):**
```json
{
  "ma_ho_so": 1,
  "thoi_gian_checkout": "2026-10-01T17:35:00",
  "ghi_chu": "Hoàn thành ca làm việc"
}
```

> **Quy tắc Validate & Nghiệp vụ:**
> - `ma_ho_so`: Bắt buộc, số nguyên dương > 0. Nếu không tìm thấy hồ sơ sẽ trả về `HTTP 404 Not Found`.
> - `thoi_gian_checkout`: Tùy chọn (định dạng ISO 8601). Nếu không truyền hoặc truyền `null`, hệ thống tự động lấy thời gian hiện tại (`datetime.now()`).
> - `ghi_chu`: Tùy chọn chuỗi ghi chú bổ sung khi checkout.
> - **Bắt buộc phải Check-in trước:** Nếu chưa có bản ghi check-in trong ngày tương ứng, trả về `HTTP 400 Bad Request`.
> - **Chống trùng lặp:** Nếu hồ sơ đã check-out trong ngày, trả về `HTTP 400 Bad Request`.
> - **Logic thời gian:** `thoi_gian_checkout` phải sau `thoi_gian_checkin`. Nếu checkout trước thời điểm checkin sẽ trả về `HTTP 400 Bad Request`.
> - **Cập nhật trạng thái:** Nếu trước đó trạng thái là `DungGio` nhưng thời gian check-out trước 17:00:00 $\rightarrow$ cập nhật `trang_thai = "VeSom"` (Về sớm). Nếu trước đó đã là `DiMuon` thì giữ nguyên để phản ánh đúng kỷ luật ca làm việc.

#### Response mẫu (HTTP 200 OK):
```json
{
  "status_code": 200,
  "message": "Check-out thành công",
  "data": {
    "ma_cham_cong": 15,
    "ma_ho_so": 1,
    "ngay_cham_cong": "2026-10-01",
    "thoi_gian_checkin": "2026-10-01T08:15:00",
    "thoi_gian_checkout": "2026-10-01T17:35:00",
    "gio_check_in": "08:15:00",
    "gio_check_out": "17:35:00",
    "trang_thai": "DungGio",
    "phuong_thuc": "Web",
    "ghi_chu": "Hoàn thành ca làm việc"
  }
}
```

---

### 13. Tạo đơn xin nghỉ phép (Leave Requests)
* **URL:** `/api/v1/leave-requests`
* **Method:** `POST`
* **Status Code:** `201 Created`
* **Request Body (JSON):**
```json
{
  "ma_ho_so": 1,
  "tu_ngay": "2026-10-05",
  "den_ngay": "2026-10-06",
  "ly_do": "[Nghỉ phép cá nhân] Có việc bận gia đình",
  "trang_thai": "Chờ duyệt"
}
```

> **Quy tắc Validate & Nghiệp vụ:**
> - `ma_ho_so`: Bắt buộc, số nguyên dương > 0. Nếu không tìm thấy hồ sơ thực tập sinh tương ứng sẽ trả về `HTTP 404 Not Found`.
> - `tu_ngay`: Bắt buộc, định dạng ngày `YYYY-MM-DD`. Ràng buộc `tu_ngay >= ngày hiện tại` (`date.today()`). Nếu ngày bắt đầu nghỉ trong quá khứ sẽ trả về `HTTP 422 Unprocessable Entity`.
> - `den_ngay`: Bắt buộc, định dạng ngày `YYYY-MM-DD`. Ràng buộc `den_ngay >= tu_ngay`. Nếu ngày kết thúc trước ngày bắt đầu sẽ trả về `HTTP 422 Unprocessable Entity`.
> - `ly_do`: Bắt buộc, chuỗi không được để trống hoặc chỉ chứa khoảng trắng. Nếu vi phạm trả về `HTTP 422 Unprocessable Entity`.
> - `trang_thai`: Tùy chọn, mặc định tự động gán là `"Chờ duyệt"`.
> - **Tiện ích:** API tự động tính toán tổng số ngày nghỉ `so_ngay = (den_ngay - tu_ngay).days + 1` trả về trong phản hồi.

#### Response mẫu (HTTP 201 Created):
```json
{
  "status_code": 201,
  "message": "Tạo đơn xin nghỉ thành công",
  "data": {
    "ma_don": 1,
    "ma_ho_so": 1,
    "tu_ngay": "2026-10-05",
    "den_ngay": "2026-10-06",
    "so_ngay": 2,
    "ly_do": "[Nghỉ phép cá nhân] Có việc bận gia đình",
    "trang_thai": "Chờ duyệt",
    "ngay_tao": "2026-10-01T19:39:24.000000"
  }
}
```

---

### 14. Tạo mới nhiệm vụ thực tập (Tasks Management)
* **URL:** `/api/v1/tasks`
* **Method:** `POST`
* **Status Code:** `201 Created`
* **Request Body (JSON):**
```json
{
  "ma_ho_so": 1,
  "tieu_de": "Phát triển tính năng quản lý nhiệm vụ thực tập",
  "mo_ta": "Thiết kế model CSDL, xây dựng endpoint POST và kiểm thử tự động",
  "han_hoan_thanh": "2026-10-25",
  "tien_do_phantram": 0,
  "trang_thai": "Chưa bắt đầu"
}
```

> **Quy tắc Validate & Nghiệp vụ:**
> - `ma_ho_so`: Bắt buộc, số nguyên dương > 0. Nếu không tồn tại hồ sơ thực tập tương ứng sẽ trả về `HTTP 404 Not Found`.
> - `tieu_de`: Bắt buộc, chuỗi không được để trống hoặc chỉ chứa khoảng trắng (hỗ trợ alias `ten_nhiem_vu`).
> - `han_hoan_thanh`: Bắt buộc, định dạng ngày `YYYY-MM-DD`. Nếu định dạng sai sẽ trả về `HTTP 422 Unprocessable Entity`.
> - `tien_do_phantram`: Tùy chọn, mặc định tự động gán là `0` (khoảng giá trị từ `0` đến `100`).
> - `trang_thai`: Tùy chọn, mặc định tự động gán là `"Chưa bắt đầu"`.
> - `mo_ta`: Tùy chọn, mô tả chi tiết công việc cần hoàn thành.

#### Response mẫu (HTTP 201 Created):
```json
{
  "status_code": 201,
  "message": "Tạo nhiệm vụ mới thành công",
  "data": {
    "ma_nhiem_vu": 4,
    "ma_ho_so": 1,
    "tieu_de": "Phát triển tính năng quản lý nhiệm vụ thực tập",
    "ten_nhiem_vu": "Phát triển tính năng quản lý nhiệm vụ thực tập",
    "mo_ta": "Thiết kế model CSDL, xây dựng endpoint POST và kiểm thử tự động",
    "han_hoan_thanh": "2026-10-25",
    "tien_do_phantram": 0,
    "trang_thai": "Chưa bắt đầu"
  }
}
```


