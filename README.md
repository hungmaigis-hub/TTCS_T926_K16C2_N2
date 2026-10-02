# Backend (FastAPI): Quản lý Thực tập sinh — NV15: Phân công Mentor

- **Người thực hiện (Assignee)**: Nguyễn Văn Hiếu (Backend)
- **Nhiệm vụ**: Viết endpoint `PATCH /api/v1/interns/{id}/assign-mentor` cập nhật trường `ma_mentor` trong `ho_so_thuc_tap`.
- **Dành cho Frontend**: Cung cấp API để hiển thị danh sách thực tập sinh, dropdown `<select>` chọn Mentor và nút Lưu phân công mentor.

---

## 1. Cài đặt và Khởi chạy

### Cài thư viện:
```bash
pip install -r requirements.txt
```

### Chạy ứng dụng FastAPI:
```bash
uvicorn app.main:app --reload --port 8000
```
- Swagger UI (Xem & Test API trực quan): [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

*(Lưu ý: Hệ thống đã tích hợp sẵn data seed mẫu gồm các mentor và thực tập sinh, chạy lên là có sẵn data để test).*

---

## 2. Tài liệu API dành cho Frontend & Tester

### 🎯 API 1 (Nhiệm vụ chính NV15): Gán Mentor cho thực tập sinh
- **Method**: `PATCH`
- **URL**: `/api/v1/interns/{id}/assign-mentor`
- **Path Param**: `id` (int, ví dụ: `1`, `2`, ...)
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "ma_mentor": "MTR001"
}
```

#### Response thành công (`200 OK`):
```json
{
  "message": "Gán mentor cho thực tập sinh thành công",
  "data": {
    "id": 1,
    "ma_thuc_tap_sinh": "TTS2024001",
    "ho_ten": "Lê Hoàng Huy",
    "email": "huy.le@university.edu.vn",
    "truong_dai_hoc": "Đại học Quốc gia",
    "chuyen_nganh": "Công nghệ Thông tin",
    "vi_tri_thuc_tap": "Frontend Intern",
    "ma_phong_ban": "PB01",
    "ma_mentor": "MTR001",
    "trang_thai": "dang_thuc_tap",
    "ngay_cap_nhat": "2026-10-02T13:45:00"
  }
}
```

#### Các mã lỗi cần xử lý:
- `404 Not Found`: Khi không tìm thấy hồ sơ thực tập sinh theo `id` hoặc không tìm thấy mentor theo `ma_mentor`.
```json
{ "detail": "Không tìm thấy hồ sơ thực tập sinh có id = 999" }
```
- `400 Bad Request`: Khi người dùng được chọn không có vai trò Mentor hoặc tài khoản không hoạt động.
```json
{ "detail": "Người dùng 'Nguyễn Văn Test' không có vai trò Mentor (Role hiện tại: Employee)." }
```

---

### 📋 API 2: Lấy danh sách Mentor (Đổ vào `<select>` dropdown trên Frontend)
- **Method**: `GET`
- **URL**: `/api/v1/interns/mentors`
- **Response**: Trả về danh sách mentor hợp lệ (`role = "Mentor"` & `is_active = true`).

---

### 📋 API 3: Lấy danh sách Thực tập sinh (Render ra bảng danh sách)
- **Method**: `GET`
- **URL**: `/api/v1/interns`

---

## 3. Code mẫu JavaScript (fetch) cho các bạn Frontend

```javascript
// Hàm gọi API khi người dùng chọn mentor và bấm Lưu
async function handleAssignMentor(internId, selectedMaMentor) {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/interns/${internId}/assign-mentor`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ma_mentor: selectedMaMentor,
      }),
    });

    const result = await response.json();
    if (!response.ok) {
      alert("Lỗi: " + result.detail);
      return;
    }

    alert(result.message);
    // Reload lại bảng hoặc cập nhật giao diện
  } catch (error) {
    console.error("Lỗi kết nối API:", error);
    alert("Không thể kết nối đến máy chủ");
  }
}
```

---

## 4. Hướng dẫn Đẩy Code Lên GitHub (Git Push)

Mở terminal trong thư mục dự án và chạy các lệnh:
```bash
git add .
git commit -m "feat(backend): hoan thanh endpoint PATCH /api/v1/interns/{id}/assign-mentor (NV15)"
git push origin <ten-branch-cua-ban>
```
