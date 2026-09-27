# Hướng Dẫn Tích Hợp API - Frontend & Backend

Tài liệu đặc tả các giao thức kết nối, định dạng dữ liệu (Payload) và danh sách Endpoints giữa phân hệ **Frontend** và hệ thống **Backend FastAPI**.

---

## 🌐 Cấu hình chung

- **Base URL Backend**: `http://127.0.0.1:8000`
- **Tiền tố phiên bản API**: `/api/v1`
- **Định dạng truyền nhận**: `application/json` (UTF-8)

---

## 📋 Danh sách Endpoints đã tích hợp

### 1. Truy xuất chi tiết hồ sơ thực tập sinh
- **Method**: `GET`
- **Endpoint**: `/api/v1/interns/{id}`
- **Tham số**:
  - `id` *(Path parameter)*: Mã hồ sơ thực tập sinh (ID)
- **Tệp Frontend sử dụng**: `frontend/js/xet_duyet_ho_so.js`
- **Response mẫu (HTTP 200)**:
```json
{
  "status_code": 200,
  "message": "Lấy thông tin chi tiết thực tập sinh thành công",
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
    "trang_thai_xet_duyet": "ChoDuyet",
    "trang_thai_thuc_tap": "DangThucTap"
  }
}
```

---

### 2. Cập nhật thông tin thực tập sinh
- **Method**: `PUT`
- **Endpoint**: `/api/v1/interns/{id}`
- **Tham số**:
  - `id` *(Path parameter)*: Mã hồ sơ thực tập sinh
- **Request Body**:
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
- **Phản hồi**: HTTP 200 nếu thành công; HTTP 400 nếu trùng email/SĐT; HTTP 422 nếu sai định dạng.

---

### 3. Lấy danh sách tài liệu đính kèm của hồ sơ
- **Method**: `GET`
- **Endpoint**: `/api/v1/documents/{ho_so_id}`
- **Tham số**:
  - `ho_so_id` *(Path parameter)*: Mã hồ sơ thực tập
- **Tệp Frontend sử dụng**: `frontend/js/xet_duyet_ho_so.js`
- **Response mẫu (HTTP 200)**:
```json
{
  "status_code": 200,
  "message": "Lấy danh sách tài liệu thành công",
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

### 4. Cập nhật trạng thái phê duyệt tài liệu
- **Method**: `PATCH`
- **Endpoint**: `/api/v1/documents/{id}/status`
- **Tham số**:
  - `id` *(Path parameter)*: Mã tài liệu
- **Request Body**:
```json
{
  "trang_thai_duyet": "DaDuyet",
  "ghi_chu": "Hồ sơ hợp lệ, đủ điều kiện tiếp nhận"
}
```
- **Giá trị trạng thái hợp lệ**: `ChoDuyet`, `DaDuyet`, `TuChoi`.
- **Tệp Frontend sử dụng**: `frontend/js/xet_duyet_ho_so.js`

---

## 🛡️ Cơ chế Fallback và Xử lý Lỗi

Phía Frontend cài đặt lớp xử lý an toàn tự động:
1. **Kiểm tra tín hiệu sống (Healthcheck / Timeout)**:
   - Nếu gọi API thất bại hoặc quá thời gian chờ (Server chưa khởi chạy hoặc lỗi mạng), hàm tự động chuyển sang chế độ **Mock Data**.
2. **Hiển thị thông báo trạng thái trực quan**:
   - Giao diện có huy hiệu kết nối (Badge) tại góc màn hình thông báo:
     - 🟢 *Đã kết nối API Backend*: Đang lấy dữ liệu thực từ CSDL.
     - 🟡 *Chế độ Thử nghiệm (Offline)*: Đang sử dụng dữ liệu mẫu cho phép thử nghiệm mượt mà.
