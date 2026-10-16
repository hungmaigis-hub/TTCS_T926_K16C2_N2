# Giao diện Quản trị Nhật ký Hoạt động (Audit Logs Management)

Hệ thống giao diện bảng HTML5 / CSS3 / Vanilla JavaScript hiện đại, trực quan, chuyên nghiệp dành cho trang quản trị hệ thống (Admin Portal).

---

## 📁 Cấu trúc thư mục

```
audit-logs/
├── index.html       # Giao diện HTML gồm Form bộ lọc, Bảng hiển thị, Phân trang và Modal
├── style.css        # Toàn bộ CSS giao diện bảng, huy hiệu trạng thái, hiệu ứng chuyển trang
├── app.js           # JavaScript Fetch API GET /api/v1/admin/audit-logs, bộ lọc & Mock fallback
└── README.md        # Hướng dẫn chi tiết & tài liệu kỹ thuật
```

---

## 🚀 Tính năng nổi bật

1. **Bộ lọc đa tiêu chí (Smart Filters)**:
   - **Người dùng**: Tìm kiếm theo tên, email hoặc mã User ID.
   - **Hành động (Action)**: `LOGIN`, `LOGOUT`, `CREATE`, `UPDATE`, `DELETE`, `EXPORT`, `PERMISSION_CHANGE`.
   - **Khoảng thời gian (Date Range)**: Lọc từ ngày (`from_date`) đến ngày (`to_date`).
   - **Trạng thái**: `SUCCESS`, `FAILED`, `WARNING`.
   - Lựa chọn kích thước trang linh hoạt: 10, 20, 50 dòng/trang.

2. **Giao thức Fetch API chuẩn RESTful**:
   - Gửi yêu cầu HTTP GET tới `/api/v1/admin/audit-logs` với chuỗi `URLSearchParams`.
   - Đính kèm headers `Accept: application/json` và `Authorization: Bearer <token>`.
   - Quản lý trạng thái: Skeleton loading, Empty state (không tìm thấy kết quả), Error handling & Retry.

3. **Phân trang thông minh (Smart Pagination)**:
   - Hiển thị số bản ghi: `Đang hiển thị X - Y trong tổng Z bản ghi`.
   - Nút chuyển: Trang đầu, Trang trước, Trang sau, Trang cuối.
   - Nút số trang thông minh dạng rút gọn (VD: `1`, `...`, `4`, `[5]`, `6`, `...`, `15`).

4. **Huy hiệu trực quan (Visual Badges) & Modal xem chi tiết**:
   - Màu sắc riêng biệt cho từng hành động và trạng thái.
   - Avatar người dùng tự động sinh màu pastel theo tên.
   - Xem chi tiết từng lượt thao tác: IP, User Agent, JSON payload thay đổi (old_value, new_value).

5. **Chế độ Mock Fallback thông minh**:
   - Khi chưa khởi động backend server, hệ thống tự động sinh 45 bản ghi mẫu giả lập ngay trên trình duyệt để kiểm thử toàn diện thao tác lọc và phân trang mà không bị lỗi.

---

## 📡 Đặc tả API Endpoint

### Request
```http
GET /api/v1/admin/audit-logs?user=nguyen&action=UPDATE&from_date=2026-10-01&to_date=2026-10-16&page=1&limit=10
Accept: application/json
Authorization: Bearer <your_jwt_token>
```

### Query Parameters

| Tham số | Kiểu | Mô tả | Mặc định |
|---|---|---|---|
| `page` | `integer` | Số trang hiện tại | `1` |
| `limit` | `integer` | Số lượng bản ghi trên một trang | `10` |
| `user` | `string` | Từ khóa tìm kiếm người dùng (tên / email / id) | `""` |
| `action` | `string` | Mã hành động (`CREATE`, `UPDATE`, `DELETE`, ...) | `""` |
| `from_date` | `string` | Ngày bắt đầu định dạng `YYYY-MM-DD` | `""` |
| `to_date` | `string` | Ngày kết thúc định dạng `YYYY-MM-DD` | `""` |
| `status` | `string` | Trạng thái thực thi (`SUCCESS`, `FAILED`) | `""` |

### Chuẩn JSON Response mong đợi

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1001,
        "timestamp": "2026-10-16T15:30:00Z",
        "user": {
          "id": 101,
          "name": "Nguyễn Văn An",
          "email": "an.nguyen@company.com",
          "role": "Super Admin"
        },
        "action": "UPDATE",
        "resource": "Hợp đồng lao động #HD-2026-89",
        "description": "Cập nhật trạng thái hợp đồng nhân sự",
        "ip_address": "192.168.1.15",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "status": "SUCCESS",
        "details": {
          "field_modified": "status",
          "old_value": "PENDING",
          "new_value": "ACTIVE"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total_records": 45,
      "total_pages": 5
    }
  }
}
```

---

## 💻 Cách sử dụng
Mở file `index.html` trực tiếp trên trình duyệt web (Google Chrome, Microsoft Edge, Firefox, Brave) hoặc chạy qua bất kỳ static web server nào (Live Server, VSCode, Nginx, Apache).
