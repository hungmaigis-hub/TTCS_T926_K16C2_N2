# Hệ Thống Quản Lý Thực Tập Sinh - Module Tiếp Nhận Yêu Cầu Hỗ Trợ (Backend FastAPI)

> **Người thực hiện (Backend Developer):** Nguyễn Văn Hiếu  
> **Công nghệ:** Python 3.10+, FastAPI, SQLAlchemy, Pydantic v2, SQLite / PostgreSQL, Pytest  
> **Mục tiêu:** Cung cấp API tiếp nhận yêu cầu hỗ trợ của thực tập sinh/sinh viên, tự động gán thời gian tạo và kiểm tra hồ sơ hợp lệ, sẵn sàng bàn giao cho team Frontend tích hợp.

---

## 📌 1. Giới thiệu & Nghiệp vụ

Module xử lý chức năng thuộc Epic **Quản lý hỗ trợ & quyền lợi**:
- **User Story 27:** *"Là thực tập sinh, tôi muốn gửi yêu cầu hỗ trợ (ví dụ: chứng nhận, giấy tờ) để được giải quyết."*
- **User Story 28:** *"Là HR, tôi muốn duyệt và phản hồi yêu cầu hỗ trợ để hỗ trợ thực tập sinh kịp thời."*

### Điểm nổi bật của Backend:
- **Model `yeu_cau_ho_tro` (SQLAlchemy):** Thiết kế chuẩn hóa với các trường `ma_yeu_cau`, `ma_ho_so`, `loai_yeu_cau`, `tieu_de`, `noi_dung`, `trang_thai = "ChoXuLy"`, `ngay_tao`.
- **Model `ho_so` (SQLAlchemy):** Quản lý hồ sơ sinh viên để kiểm tra tính hợp lệ trước khi tiếp nhận yêu cầu.
- **Tự động hóa:** Tự động gán thời gian tạo `ngay_tao` và trạng thái mặc định `trang_thai = "ChoXuLy"`.
- **Kiểm soát tính hợp lệ:**
  - Nếu mã hồ sơ không tồn tại -> Trả về `404 Not Found`.
  - Nếu hồ sơ bị khóa (`Khoa`, `BiHuy`) -> Trả về `400 Bad Request`.
- **CORS mở:** Đã cấu hình sẵn CORS middleware để anh em Frontend gọi API từ localhost (React, Vue, Vite, Next.js) không bị lỗi chặn CORS.
- **Tự động Seed dữ liệu:** Khi khởi chạy server lần đầu, hệ thống tự nạp sẵn 3 hồ sơ mẫu (`HS001`, `HS002`, `HS003`) để test ngay.

---

## 📂 2. Cấu trúc thư mục dự án

```text
├── app/
│   ├── __init__.py
│   ├── main.py                  # Khởi chạy FastAPI, cấu hình CORS, lifespan init DB
│   ├── core/
│   │   ├── config.py            # Cấu hình biến môi trường, tiền tố API /api/v1
│   │   └── database.py          # Khởi tạo SQLAlchemy Engine, SessionLocal, Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ho_so.py             # Model HoSo (Hồ sơ sinh viên)
│   │   └── yeu_cau_ho_tro.py    # Model YeuCauHoTro (Đúng yêu cầu đề bài)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ho_so.py             # Pydantic schemas cho HoSo
│   │   └── yeu_cau_ho_tro.py    # Pydantic schemas cho YeuCauHoTro (Create & Response)
│   ├── api/
│   │   ├── deps.py              # Dependency get_db session
│   │   └── v1/
│   │       ├── api.py           # Gom các router v1
│   │       └── endpoints/
│   │           ├── support_requests.py  # Endpoint POST, GET /api/v1/support-requests
│   │           └── student_profiles.py  # Endpoint tra cứu hồ sơ sinh viên
│   └── db/
│       └── init_db.py           # Tạo bảng tự động và seed dữ liệu mẫu sinh viên
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixture SQLite in-memory test & TestClient
│   └── test_support_requests.py # Bộ unit tests tự động
├── .env.example                 # Mẫu cấu hình môi trường
├── .gitignore                   # Cấu hình bỏ qua tệp rác khi commit Git
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn & Bàn giao Frontend
```

---

## 🚀 3. Hướng dẫn cài đặt & Khởi chạy

### Bước 1: Mở Terminal tại thư mục dự án và tạo môi trường ảo

```bash
# Tạo môi trường ảo (Virtual Environment)
python -m venv venv

# Kích hoạt môi trường ảo:
# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Hoặc trên Command Prompt (cmd):
.\venv\Scripts\activate.bat
```

### Bước 2: Cài đặt các thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Khởi chạy Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 4: Mở tài liệu API tương tác trực tiếp
- **Swagger UI (Khuyên dùng để test):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📋 4. Đặc tả API dành cho anh em Frontend

### Dữ liệu hồ sơ có sẵn để Frontend dùng test:
| Mã hồ sơ (`ma_ho_so`) | Họ và tên | Trạng thái | Ghi chú để test |
|---|---|---|---|
| `HS001` | Nguyễn Văn Hiếu | `DangThucTap` | ✅ Hợp lệ (Dùng test thành công) |
| `HS002` | Trần Thị Mai | `DaTiepNhan` | ✅ Hợp lệ (Dùng test thành công) |
| `HS003` | Lê Hoàng Nam | `Khoa` | ❌ Bị khóa (Dùng test lỗi 400 Bad Request) |

---

### Endpoint 1: Gửi yêu cầu hỗ trợ (POST)
- **URL:** `/api/v1/support-requests`
- **Method:** `POST`
- **Content-Type:** `application/json`

#### Request Body:
```json
{
  "ma_ho_so": "HS001",
  "loai_yeu_cau": "Giấy tờ thực tập",
  "tieu_de": "Xin giấy xác nhận hoàn thành thực tập",
  "noi_dung": "Em cần giấy xác nhận hoàn thành 3 tháng thực tập để nộp về khoa CNTT trường Đại học Bách Khoa."
}
```
*(Lưu ý: Frontend không cần gửi `trang_thai` hay `ngay_tao`, Backend tự động gán).*

#### Response thành công (`201 Created`):
```json
{
  "ma_yeu_cau": 1,
  "ma_ho_so": "HS001",
  "loai_yeu_cau": "Giấy tờ thực tập",
  "tieu_de": "Xin giấy xác nhận hoàn thành thực tập",
  "noi_dung": "Em cần giấy xác nhận hoàn thành 3 tháng thực tập để nộp về khoa CNTT trường Đại học Bách Khoa.",
  "trang_thai": "ChoXuLy",
  "ngay_tao": "2026-10-07T07:45:00.000000"
}
```

#### Các trường hợp lỗi:
- **`404 Not Found`** - Khi `ma_ho_so` không có trong hệ thống:
  ```json
  {
    "detail": "Hồ sơ sinh viên với mã 'HS999' không tồn tại trong hệ thống."
  }
  ```
- **`400 Bad Request`** - Khi hồ sơ bị khóa / không hợp lệ:
  ```json
  {
    "detail": "Hồ sơ sinh viên 'HS003' đang ở trạng thái 'Khoa', không hợp lệ để gửi yêu cầu hỗ trợ."
  }
  ```
- **`422 Unprocessable Entity`** - Khi gửi thiếu trường bắt buộc hoặc dữ liệu sai định dạng:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "tieu_de"],
        "msg": "Field required",
        "type": "missing"
      }
    ]
  }
  ```

---

### Endpoint 2: Lấy danh sách yêu cầu hỗ trợ (GET)
- **URL:** `/api/v1/support-requests`
- **Method:** `GET`
- **Query Parameters (Tùy chọn):**
  - `ma_ho_so`: Lọc theo sinh viên (ví dụ: `?ma_ho_so=HS001`)
  - `trang_thai`: Lọc theo trạng thái (ví dụ: `?trang_thai=ChoXuLy`)
  - `skip`: Bỏ qua n bản ghi (phân trang, mặc định `0`)
  - `limit`: Số bản ghi tối đa (mặc định `50`)
- **Response (`200 OK`):**
  ```json
  [
    {
      "ma_yeu_cau": 1,
      "ma_ho_so": "HS001",
      "loai_yeu_cau": "Giấy tờ thực tập",
      "tieu_de": "Xin giấy xác nhận hoàn thành thực tập",
      "noi_dung": "...",
      "trang_thai": "ChoXuLy",
      "ngay_tao": "2026-10-07T07:45:00.000000"
    }
  ]
  ```

---

### Endpoint 3: Chi tiết một yêu cầu hỗ trợ (GET)
- **URL:** `/api/v1/support-requests/{ma_yeu_cau}`
- **Method:** `GET`
- **Response (`200 OK`):** Trả về chi tiết đối tượng yêu cầu.

---

## 🧪 5. Kiểm thử tự động (Unit Tests)

Dự án đã tích hợp bộ kiểm thử tự động toàn diện bằng `pytest` với cơ sở dữ liệu SQLite in-memory:

```bash
pytest tests/ -v
```

**Các kịch bản kiểm thử đã bao phủ:**
1. ✅ Tạo yêu cầu hỗ trợ thành công với hồ sơ hợp lệ (gán `ChoXuLy` & `ngay_tao`).
2. ✅ Bắt lỗi `404 Not Found` khi mã hồ sơ không tồn tại.
3. ✅ Bắt lỗi `400 Bad Request` khi hồ sơ bị khóa.
4. ✅ Bắt lỗi `422 Unprocessable Entity` khi thiếu trường thông tin.
5. ✅ Lấy danh sách yêu cầu hỗ trợ kèm bộ lọc.
6. ✅ Tra cứu chi tiết yêu cầu hỗ trợ theo ID.

---

## 💻 6. Hướng dẫn Push Code lên GitHub cho Nguyễn Văn Hiếu

Để đưa mã nguồn lên GitHub cho anh em Frontend kéo về làm tiếp:

```bash
# 1. Khởi tạo Git repository (nếu chưa khởi tạo)
git init

# 2. Thêm tất cả các file vào khu vực chờ commit
git add .

# 3. Commit mã nguồn với thông điệp rõ ràng
git commit -m "feat(backend): thiet ke model yeu_cau_ho_tro va viet endpoint POST /api/v1/support-requests"

# 4. Đổi tên nhánh chính sang main (hoặc master tùy repo của bạn)
git branch -M main

# 5. Liên kết tới kho lưu trữ GitHub của bạn (thay thế URL repo của bạn)
git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

# 6. Đẩy code lên GitHub
git push -u origin main
```

---

*Tác giả: Nguyễn Văn Hiếu - Backend Developer.*
