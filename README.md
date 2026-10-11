# 🚀 HỆ THỐNG QUẢN LÝ THỰC TẬP SINH (TTCS_T926_K16C2_N2)

## 📌 Phân Hệ Backend: API Phân Công Mentor (Assign Mentor)

### 👤 Thông tin thành viên & Phân công nhiệm vụ
- **Họ và tên:** **Nguyễn Văn Hiếu**
- **Vai trò:** Backend Developer (FastAPI)
- **Nhiệm vụ theo Kế hoạch dự án:** Viết endpoint `PATCH /api/v1/interns/{id}/assign-mentor` cập nhật trường `ma_mentor` trong `ho_so_thuc_tap`.
- **User Story tương ứng (Theo Kế hoạch - Mục tiêu Quản lý Mentor & Phòng ban):**
  - **US 30:** *"Là HR, tôi muốn gán mentor cho thực tập sinh để họ được hướng dẫn."*
  - **US 12:** *"Là HR, tôi muốn phân công thực tập sinh cho mentor để họ được hướng dẫn."*
  - **US 31:** *"Là HR, tôi muốn xem số lượng thực tập sinh mỗi mentor quản lý để cân bằng khối lượng công việc."*
- **Nhánh Git (Feature Branch):** `feature/NV15-hieu-backend`
- **Repository:** `https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git`

---

## 🏗️ Cấu Trúc Thư Mục Dự Án (Project Structure)

```text
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── interns.py       # [Trọng tâm] Chứa API PATCH assign-mentor & quản lý TTS
│   │       │   └── mentors.py       # API lấy danh sách Mentor cho Frontend chọn
│   │       └── api.py               # Gom các router của API v1
│   ├── core/
│   │   ├── config.py                # Cấu hình hệ thống & CORS
│   │   └── database.py              # Kết nối SQLAlchemy ORM & SQLite
│   ├── models/
│   │   ├── ho_so_thuc_tap.py        # Model bảng ho_so_thuc_tap (có trường ma_mentor)
│   │   └── mentor.py                # Model bảng mentors
│   ├── schemas/
│   │   ├── intern.py                # Pydantic schemas cho AssignMentorRequest, Response
│   │   └── mentor.py                # Pydantic schemas cho Mentor
│   ├── services/
│   │   └── intern_service.py        # Business logic gán mentor, kiểm tra ràng buộc
│   └── main.py                      # Khởi chạy FastAPI app, cấu hình CORS, Swagger UI
├── tests/
│   └── test_assign_mentor.py        # Bộ unit test toàn diện (pytest)
├── demo_frontend.html               # Giao diện HTML/JS mẫu cho Frontend test trực tiếp API
├── seed_data.py                     # Script tạo sẵn dữ liệu mẫu thực tế
├── requirements.txt                 # Khai báo các thư viện phụ thuộc
├── .gitignore                       # Bỏ qua file rác, file tạm, cache, DB
└── README.md                        # Hướng dẫn chi tiết dự án & hướng dẫn Git
```

---

## 📡 Chi Tiết Đặc Tả API (API Specification)

### 🎯 1. Endpoint Trọng Tâm: `PATCH /api/v1/interns/{id}/assign-mentor`

- **Mục đích:** Cập nhật trường `ma_mentor` trong bảng `ho_so_thuc_tap` cho thực tập sinh có ID tương ứng.
- **Phương thức:** `PATCH`
- **URL Path:** `/api/v1/interns/{id}/assign-mentor`
- **Path Parameters:**
  - `id` (integer, bắt buộc): ID của hồ sơ thực tập sinh cần gán mentor.

#### 📥 Request Body (JSON):
```json
{
  "ma_mentor": 1,
  "ghi_chu": "Phân công hướng dẫn dự án Backend FastAPI"
}
```
> **Lưu ý đặc biệt:** Nếu muốn **Hủy phân công** (Unassign), truyền `"ma_mentor": null`:
```json
{
  "ma_mentor": null,
  "ghi_chu": "Hủy gán mentor"
}
```

#### 📤 Phản Hồi Thành Công (HTTP 200 OK):
```json
{
  "success": true,
  "message": "Phân công mentor thành công",
  "data": {
    "id": 1,
    "ma_sv": "DTC245180138",
    "ho_ten": "Nguyễn Văn Hiếu",
    "email": "dtc245180138@ictu.edu.vn",
    "so_dien_thoai": "0988776655",
    "truong_hoc": "Đại học Công nghệ Thông tin & Truyền thông (ICTU)",
    "chuyen_nganh": "Kỹ thuật phần mềm",
    "ma_mentor": 1,
    "mentor": {
      "id": 1,
      "ma_can_bo": "MEN01",
      "ho_ten": "Nguyễn Minh Tuấn",
      "email": "tuan.nguyen@company.com",
      "phong_ban": "Phòng Kỹ thuật Phần mềm",
      "chuc_vu": "Tech Lead Backend",
      "chuyen_mon": "FastAPI, Python, Microservices, SQL"
    },
    "trang_thai": "DangThucTap",
    "ngay_bat_dau": "2026-09-01",
    "ngay_ket_thuc": "2026-12-31",
    "ghi_chu_phan_cong": "Phân công hướng dẫn dự án Backend FastAPI",
    "ngay_gan_mentor": "2026-10-11T04:30:00",
    "created_at": "2026-10-11T04:00:00",
    "updated_at": "2026-10-11T04:30:00"
  }
}
```

#### ⚠️ Các Mã Lỗi Xử Lý (Error Responses):
1. **HTTP 404 Not Found (Không tìm thấy thực tập sinh):**
   ```json
   { "detail": "Không tìm thấy hồ sơ thực tập sinh với ID = 999" }
   ```
2. **HTTP 404 Not Found (Không tìm thấy mentor):**
   ```json
   { "detail": "Không tìm thấy mentor với ID = 999" }
   ```
3. **HTTP 400 Bad Request (Mentor không khả dụng):**
   ```json
   { "detail": "Mentor 'Vũ Hải Đăng' hiện không khả dụng (Trạng thái: TamNghi)" }
   ```
4. **HTTP 400 Bad Request (Mentor quá tải số lượng):**
   ```json
   { "detail": "Mentor 'Nguyễn Minh Tuấn' đã đạt giới hạn tối đa (5 thực tập sinh)" }
   ```

---

### 🌐 2. Các API Hỗ Trợ Đội Ngũ Frontend (Supporting APIs)

| Phương thức | Endpoint | Chức năng | Phục vụ Frontend |
|---|---|---|---|
| `GET` | `/api/v1/interns` | Lấy danh sách thực tập sinh | Render bảng danh sách sinh viên |
| `GET` | `/api/v1/interns/{id}` | Lấy chi tiết thực tập sinh | Xem thông tin chi tiết / profile |
| `GET` | `/api/v1/mentors` | Lấy danh sách tất cả mentor | Đổ dữ liệu vào Dropdown / Select chọn Mentor |
| `GET` | `/docs` | Swagger UI tương tác | Test trực tiếp API trên trình duyệt |

---

## 🛠️ Hướng Dẫn Cài Đặt & Chạy Thử (Quick Start)

### 1. Cài đặt môi trường ảo & Thư viện
```bash
python -m venv venv
# Trên Windows:
venv\Scripts\activate
# Cài đặt thư viện:
pip install -r requirements.txt
```

### 2. Khởi tạo dữ liệu mẫu (Seed Data)
```bash
python seed_data.py
```

### 3. Chạy Server FastAPI
```bash
uvicorn app.main:app --reload
```
Server chạy tại: `http://127.0.0.1:8000`
- Swagger UI tài liệu: `http://127.0.0.1:8000/docs`
- Redoc tài liệu: `http://127.0.0.1:8000/redoc`

### 4. Chạy Unit Test
```bash
pytest -v
```

### 5. Thử nghiệm với giao diện mẫu (Dành cho Frontend)
Mở trực tiếp file `demo_frontend.html` bằng trình duyệt (Chrome / Edge / Firefox) để trải nghiệm giao diện test thực tế, bấm chọn sinh viên, gán mentor và xem dữ liệu phản hồi!

---

## 🌿 HƯỚNG DẪN PUSH CODE LÊN GITHUB (DÀNH CHO NGUYỄN VĂN HIẾU)

Để nộp bài chuẩn quy trình nhóm và đẩy lên nhánh `feature/NV15-hieu-backend` cho anh em Frontend kéo về:

Mở **Terminal (PowerShell)** tại thư mục dự án và chạy các lệnh sau:

```powershell
# 1. Thêm toàn bộ file mới vào Git
git add .

# 2. Tạo commit theo quy chuẩn conventional commit
git commit -m "feat(backend): hoan thanh endpoint PATCH /api/v1/interns/{id}/assign-mentor (NV15 - Nguyen Van Hieu)"

# 3. Tạo và chuyển sang nhánh riêng của bạn (nếu chưa ở nhánh này)
git checkout -B feature/NV15-hieu-backend

# 4. Kiểm tra remote origin đã trỏ về đúng repo nhóm
git remote set-url origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

# 5. Đẩy nhánh lên GitHub
git push -u origin feature/NV15-hieu-backend
```

---

## 🤝 Dành Cho Đồng Đội Frontend Kéo Về Làm Việc

Khi anh em Frontend muốn lấy nhánh của Hiếu về máy để ghép API vào giao diện:
```powershell
git fetch origin
git checkout feature/NV15-hieu-backend
```
Các bạn Frontend chỉ cần mở file `demo_frontend.html` hoặc xem trực tiếp tại Swagger `/docs` để lấy chính xác định dạng Request/Response!
