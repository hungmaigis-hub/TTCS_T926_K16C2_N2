# 🚀 TTCS_T926_K16C2_N2 - Hệ Thống Quản Lý Thực Tập Sinh

---

## 📌 Phân Hệ Backend (FastAPI): NV15 - Phân Công Mentor

- **Người thực hiện (Assignee):** **Nguyễn Văn Hiếu** (Backend Developer)
- **Nhiệm vụ:** Viết endpoint `PATCH /api/v1/interns/{id}/assign-mentor` cập nhật trường `ma_mentor` trong `ho_so_thuc_tap`.
- **Dành cho Frontend:** Cung cấp API để hiển thị danh sách thực tập sinh, dropdown `<select>` chọn Mentor và nút Lưu phân công mentor.
- **User Story tương ứng:**
  - **US 30:** *"Là HR, tôi muốn gán mentor cho thực tập sinh để họ được hướng dẫn."*
  - **US 12:** *"Là HR, tôi muốn phân công thực tập sinh cho mentor để họ được hướng dẫn."*
  - **US 31:** *"Là HR, tôi muốn xem số lượng thực tập sinh mỗi mentor quản lý để cân bằng khối lượng công việc."*
- **Nhánh phát triển:** `develop`

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

*(Lưu ý: Hệ thống đã tích hợp sẵn data seed mẫu gồm các mentor và thực tập sinh trong `seed_data.py`, chạy `python seed_data.py` là có sẵn data để test).*

---

## 2. Tài liệu API dành cho Frontend & Tester

### 🎯 API 1 (Nhiệm vụ chính NV15): Gán Mentor cho thực tập sinh
- **Method:** `PATCH`
- **URL:** `/api/v1/interns/{id}/assign-mentor`
- **Path Param:** `id` (int, ví dụ: `1`, `2`, ...)
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "ma_mentor": 1,
  "ghi_chu": "Phân công hướng dẫn Backend"
}
```
*(Nếu muốn hủy phân công, truyền `"ma_mentor": null`)*

#### Response thành công (`200 OK`):
```json
{
  "success": true,
  "message": "Phân công mentor thành công",
  "data": {
    "id": 1,
    "ma_sv": "DTC245180138",
    "ho_ten": "Nguyễn Văn Hiếu",
    "email": "dtc245180138@ictu.edu.vn",
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
    "ghi_chu_phan_cong": "Phân công hướng dẫn Backend",
    "ngay_gan_mentor": "2026-10-11T04:30:00"
  }
}
```

#### Các mã lỗi cần xử lý:
- `404 Not Found`: Khi không tìm thấy hồ sơ thực tập sinh theo `id` hoặc không tìm thấy mentor theo `ma_mentor`.
- `400 Bad Request`: Khi mentor được chọn đang tạm nghỉ hoặc đã đạt số lượng tối đa.

---

### 📋 API 2: Lấy danh sách Mentor (Đổ vào `<select>` dropdown trên Frontend)
- **Method:** `GET`
- **URL:** `/api/v1/mentors`
- **Response:** Trả về danh sách mentor hợp lệ kèm số lượng thực tập sinh đang hướng dẫn.

---

### 📋 API 3: Lấy danh sách Thực tập sinh (Render ra bảng danh sách)
- **Method:** `GET`
- **URL:** `/api/v1/interns`

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
        ghi_chu: "Phân công mentor"
      }),
    });

    const result = await response.json();
    if (!response.ok) {
      alert("Lỗi: " + result.detail);
      return;
    }

    alert(result.message);
  } catch (error) {
    console.error("Lỗi kết nối API:", error);
    alert("Không thể kết nối đến máy chủ");
  }
}
```

---

## 4. Kiểm thử tự động (Unit Test)
Chạy bộ test kiểm thử tất cả các trường hợp:
```bash
pytest -v
```
