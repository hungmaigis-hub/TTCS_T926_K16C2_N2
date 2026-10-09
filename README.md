# Dashboard Quản Lý Sinh Viên - KPI & Tỷ Lệ Hoàn Thành Thời Gian Thực

Giao diện Frontend (HTML5, CSS3, Vanilla JavaScript) thiết kế hiện đại hiển thị các khối thẻ thông số KPI số lượng sinh viên theo từng trạng thái và vòng tròn phần trăm tiến độ hoàn thành (Circular Progress Bar SVG). Hệ thống sử dụng Fetch API gọi endpoint `GET /api/v1/reports/completion-rate` với cơ chế cập nhật tự động theo thời gian thực (Real-time Polling).

---

## 1. Cấu Trúc Thành Phần Giao Diện

### A. Khối Thẻ Nổi Bật (Hero Card) - Vòng Tròn Phần Trăm Hoàn Thành:
- **Vòng tròn SVG (Circular Progress Bar)**: Thiết kế bằng vector SVG với hiệu ứng Gradient màu hiện đại (Indigo -> Cyan -> Emerald), viền phát sáng (Glow effect), chuyển động quay mượt mà qua thuộc tính `stroke-dashoffset`.
- **Số phần trăm ở tâm**: Hiển thị tỷ lệ hoàn thành kèm hiệu ứng số nhảy mượt mà (Count-up animation).
- **Phân tích chỉ số kỳ học**: So sánh tỷ lệ thực tế với KPI Target, số lượng tốt nghiệp đúng hạn, gia hạn luận văn và cảnh báo học vụ.

### B. Các Khối Thẻ Thống Số KPI Trạng Thái Sinh Viên:
1. **Tổng Sinh Viên (Total Students)**: Quy mô toàn trường, thống kê xu hướng tăng trưởng so với kỳ trước (`+4.8%`).
2. **Đang Theo Học (Active Students)**: Số lượng đang có lịch học/học phần hoạt động bình thường kèm thanh tỷ lệ % trực quan.
3. **Đã Hoàn Thành / Tốt Nghiệp (Completed Students)**: Số lượng sinh viên đã đủ điều kiện tốt nghiệp và nhận văn bằng.
4. **Bảo Lưu / Chờ Xử Lý (On Leave Students)**: Thống kê số lượng sinh viên tạm dừng tiến độ hoặc đang xét duyệt bảo lưu.
5. **Thôi Học / Cảnh Báo (Dropped / Warning)**: Cảnh báo học vụ, nguy cơ buộc thôi học cần cố vấn học tập can thiệp.

---

## 2. Đặc Tả API Backend Contract

### Endpoint:
```http
GET /api/v1/reports/completion-rate
```

### Response Định Dạng Chuẩn JSON:
```json
{
  "success": true,
  "timestamp": "2026-10-09T20:15:00.000Z",
  "data": {
    "totalStudents": 12500,
    "active": 9850,
    "completed": 2100,
    "onLeave": 380,
    "dropped": 170,
    "completionRate": 84.5,
    "targetRate": 85.0,
    "trend": {
      "totalChange": "+4.8%",
      "completionRateChange": "+2.5%"
    },
    "details": {
      "onTimeGraduation": 1850,
      "delayedGraduation": 250,
      "academicWarning": 110
    }
  }
}
```

---

## 3. Tính Năng JavaScript Fetch API & Real-time
- **Fetch API không đồng bộ (`async/await`)**: Tự động gửi request với `Cache-Control: no-cache` để đảm bảo luôn nhận dữ liệu mới nhất.
- **Cơ chế Cập nhật Tự động (Polling Interval)**: Có thể tùy chỉnh tần suất gọi API (mỗi 5s, 10s, 30s hoặc Tắt).
- **Count-Up Animation (`requestAnimationFrame`)**: Khi dữ liệu cập nhật, các con số không bị giật mà tăng/giảm mượt mà.
- **Chế độ kiểm thử Demo (Mock Mode)**: Khi mở trực tiếp file `index.html` trong trình duyệt mà chưa có server backend chạy, hệ thống tự động phát hiện và cung cấp dữ liệu giả lập có biến động thời gian thực để test trơn tru ngay lập tức.
- **Badge trạng thái kết nối Live**: Hiển thị chấm tròn nhấp nháy xanh (Pulse dot) và thời điểm cập nhật lần cuối (`HH:mm:ss`).
