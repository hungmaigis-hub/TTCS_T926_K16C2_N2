# 🎓 Intern Management System – Backend API

> **Nhóm:** TTCS_T926_K16C2_N2  
> **Backend dev:** Nguyễn Văn Hiếu  
> **Framework:** FastAPI + MySQL (SQLAlchemy)  
> **Python:** ≥ 3.11

---

## 📁 Cấu trúc thư mục

```
├── app/
│   ├── main.py                  # Entry point FastAPI
│   ├── config.py                # Cấu hình từ .env
│   ├── database.py              # Kết nối DB, session factory
│   ├── models/
│   │   ├── nguoi_dung.py        # ORM: bảng nguoi_dung
│   │   └── ho_so_thuc_tap.py   # ORM: bảng ho_so_thuc_tap
│   ├── schemas/
│   │   └── intern.py            # Pydantic schemas (request/response)
│   ├── services/
│   │   └── intern_service.py    # Business logic (assign mentor)
│   └── routers/
│       └── intern_router.py     # FastAPI router – /api/v1/interns
├── database/
│   └── init_db.sql              # Script tạo bảng + seed data MySQL
├── tests/
│   └── test_assign_mentor.py    # Pytest test suite (15 test cases)
├── .env.example                 # Template biến môi trường
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚡ Cài đặt & Chạy

### 1. Clone & cài dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate

# Cài packages
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

```bash
# Copy file mẫu
copy .env.example .env          # Windows
cp .env.example .env             # macOS/Linux

# Chỉnh sửa .env – điền thông tin MySQL của bạn
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=intern_management
```

### 3. Khởi tạo CSDL MySQL

```bash
# Chạy script SQL để tạo bảng + seed data mẫu
mysql -u root -p < database/init_db.sql
```

### 4. Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ khởi động tại: **http://localhost:8000**

| URL | Mô tả |
|-----|-------|
| http://localhost:8000/docs | **Swagger UI** (test trực tiếp) |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/health | Health check |

---

## 🔑 Endpoint chính

### `PATCH /api/v1/interns/{id}/mentor`

**Gán hoặc thay đổi Mentor cho hồ sơ thực tập sinh.**

#### Request

| Phần | Chi tiết |
|------|----------|
| Method | `PATCH` |
| URL | `/api/v1/interns/{id}/mentor` |
| Path param | `id` – mã hồ sơ thực tập (`ma_ho_so`) |
| Content-Type | `application/json` |

**Body:**
```json
{
  "ma_mentor": "MENTOR01"
}
```

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `ma_mentor` | `string \| null` | ✅ | Mã mentor cần gán. Truyền `null` để hủy gán. |

#### Validation

| Điều kiện | Lỗi |
|-----------|-----|
| Hồ sơ `{id}` không tồn tại | `404 INTERN_NOT_FOUND` |
| `ma_mentor` không tồn tại trong bảng `nguoi_dung` | `404 MENTOR_NOT_FOUND` |
| Người dùng tồn tại nhưng `vai_tro ≠ 'Mentor'` | `422 INVALID_MENTOR_ROLE` |
| Tài khoản Mentor bị vô hiệu hóa (`kich_hoat = 0`) | `403 MENTOR_INACTIVE` |

#### Response 200 – Thành công

```json
{
  "success": true,
  "message": "Gán Mentor 'Lê Văn Phúc' cho hồ sơ 'HS001' thành công.",
  "data": {
    "ho_so": {
      "ma_ho_so": "HS001",
      "ho_ten": "Trần Văn An",
      "email": "an.tran@uni.edu.vn",
      "vi_tri_thuc_tap": "Backend Developer",
      "trang_thai": "DaDuyet"
    },
    "mentor": {
      "ma_mentor": "MENTOR01",
      "ho_ten": "Lê Văn Phúc",
      "email": "phuc.le@company.com",
      "so_dien_thoai": "0901111001"
    },
    "ngay_cap_nhat": "2024-10-07T11:39:49.123456"
  }
}
```

#### Response 404 – Hồ sơ không tồn tại

```json
{
  "detail": {
    "error_code": "INTERN_NOT_FOUND",
    "message": "Không tìm thấy hồ sơ thực tập với mã 'HS999'.",
    "field": "id"
  }
}
```

#### Response 404 – Mentor không tồn tại

```json
{
  "detail": {
    "error_code": "MENTOR_NOT_FOUND",
    "message": "Không tìm thấy người dùng với mã 'MENTOR99' trong hệ thống.",
    "field": "ma_mentor"
  }
}
```

#### Response 422 – Sai vai trò

```json
{
  "detail": {
    "error_code": "INVALID_MENTOR_ROLE",
    "message": "Người dùng 'HR01' có vai trò 'HR', không phải 'Mentor'. Chỉ người dùng có vai trò 'Mentor' mới được gán.",
    "field": "ma_mentor"
  }
}
```

#### Response 403 – Mentor bị vô hiệu hóa

```json
{
  "detail": {
    "error_code": "MENTOR_INACTIVE",
    "message": "Tài khoản của Mentor 'MENTOR04' đã bị vô hiệu hóa, không thể gán.",
    "field": "ma_mentor"
  }
}
```

#### Hủy gán Mentor

```json
{
  "ma_mentor": null
}
```

→ Response `200` với `"mentor": null`.

---

## 🧪 Chạy test

```bash
# Chạy toàn bộ test
pytest tests/ -v

# Chạy với report chi tiết
pytest tests/ -v --tb=short

# Chạy 1 class test cụ thể
pytest tests/test_assign_mentor.py::TestAssignMentorSuccess -v
```

**15 test cases** bao gồm:
- ✅ Gán mentor mới
- ✅ Thay đổi mentor
- ✅ Hủy gán (null)
- ✅ Gán lại cùng mentor (idempotent)
- ✅ Response có `ngay_cap_nhat`
- ❌ Hồ sơ không tồn tại (404)
- ❌ Mentor không tồn tại (404)
- ❌ Sai vai trò – HR (422)
- ❌ Sai vai trò – ThucTapSinh (422)
- ❌ Mentor bị vô hiệu hóa (403)
- ❌ Body rỗng (422)
- ✅ Whitespace treated as null

---

## 🗄️ Schema CSDL

### Bảng `nguoi_dung`

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `ma_nguoi_dung` | VARCHAR(20) PK | Mã định danh |
| `ho_ten` | VARCHAR(100) | Họ tên |
| `email` | VARCHAR(150) UNIQUE | Email đăng nhập |
| `mat_khau_hash` | VARCHAR(255) | Mật khẩu băm |
| `so_dien_thoai` | VARCHAR(15) | SĐT |
| `vai_tro` | ENUM | `HR` / `Mentor` / `ThucTapSinh` / `Admin` |
| `kich_hoat` | TINYINT(1) | 1=active, 0=inactive |
| `ngay_tao` | DATETIME | |
| `ngay_cap_nhat` | DATETIME | |

### Bảng `ho_so_thuc_tap`

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `ma_ho_so` | VARCHAR(20) PK | Mã hồ sơ |
| `ma_sinh_vien` | VARCHAR(20) FK | → nguoi_dung |
| `ho_ten` | VARCHAR(100) | |
| `email` | VARCHAR(150) | |
| `vi_tri_thuc_tap` | VARCHAR(100) | |
| `ngay_bat_dau` | DATE | |
| `ngay_ket_thuc` | DATE | |
| `trang_thai` | ENUM | ChoDuyet/DaDuyet/TuChoi/DangThucTap/HoanThanh |
| **`ma_mentor`** | **VARCHAR(20) FK** | **→ nguoi_dung (vai_tro='Mentor')** |
| `ngay_tao` | DATETIME | |
| `ngay_cap_nhat` | DATETIME | |

---

## 🔧 Dành cho Frontend

Khi gọi API từ React/Vue/Next.js:

```javascript
// Gán mentor
const assignMentor = async (maHoSo, maMentor) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/interns/${maHoSo}/mentor`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ma_mentor: maMentor }),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    // error.detail.error_code → xử lý từng loại lỗi
    // error.detail.message   → hiển thị cho người dùng
    throw error;
  }

  return response.json();
};

// Hủy gán mentor
const unassignMentor = (maHoSo) => assignMentor(maHoSo, null);
```

**Các `error_code` cần xử lý ở FE:**

| `error_code` | HTTP | Hiển thị |
|--------------|------|---------|
| `INTERN_NOT_FOUND` | 404 | "Hồ sơ không tồn tại" |
| `MENTOR_NOT_FOUND` | 404 | "Mentor không tồn tại trong hệ thống" |
| `INVALID_MENTOR_ROLE` | 422 | "Người này không phải Mentor" |
| `MENTOR_INACTIVE` | 403 | "Tài khoản Mentor đã bị vô hiệu hóa" |

---

## 📝 Ghi chú kỹ thuật

- **Transaction an toàn:** Mọi thao tác DB đều trong try/except + rollback khi lỗi.
- **Logging:** Ghi log đầy đủ ở INFO/WARNING/ERROR để dễ debug.
- **CORS:** Đã cấu hình cho phép `localhost:3000` (React) và `localhost:5173` (Vite).
- **DEBUG mode:** Tự động `CREATE TABLE IF NOT EXISTS` khi khởi động (dev only).
- **Production:** Dùng Alembic migration thay vì `create_all`.

---

*Cập nhật lần cuối: 07/10/2024*
