# Form Quản Lý Ca Làm Việc & Phân Bổ Thực Tập Sinh

Dự án Frontend xây dựng Form HTML hoàn chỉnh để thiết lập ca làm việc, tích hợp chọn giờ bằng `input type="time"`, checkbox chọn các ngày trong tuần và Modal chọn danh sách thực tập sinh áp dụng.

---

## 🚀 Tính Năng Chính

1. **Nhập Tên Ca Làm Việc**:
   - Trường input text hỗ trợ validation (bắt buộc, tối thiểu 3 ký tự).
   - Menu gợi ý mẫu ca nhanh (Ca sáng, Ca chiều, Ca full-time, Ca tối) giúp nhập liệu tức thì.

2. **Chọn Giờ Làm Việc (`input type="time"`)**:
   - Hai input time độc lập: **Giờ bắt đầu** và **Giờ kết thúc**.
   - Tự động tính toán tổng thời lượng ca làm việc (giờ & phút) theo thời gian thực.
   - Nhận diện và hiển thị cảnh báo đối với ca làm việc qua đêm (qua 24:00).
   - Validation ngăn chặn trường hợp giờ kết thúc trùng giờ bắt đầu.

3. **Checkbox Chọn Các Ngày Trong Tuần**:
   - 7 checkbox trực quan từ Thứ 2 đến Chủ Nhật thiết kế dạng Card trực quan.
   - Phân biệt rõ ràng ngày thường (T2-T6) và ngày cuối tuần (T7, CN).
   - Bộ nút thao tác nhanh: **Thứ 2 - Thứ 6**, **Cuối tuần**, **Cả tuần**, **Bỏ chọn tất cả**.

4. **Modal Chọn Danh Sách Thực Tập Sinh Áp Dụng**:
   - Modal Bootstrap hiện đại, responsive.
   - Thanh tìm kiếm thông minh theo Họ tên, Mã TTS, Email hoặc Vị trí.
   - Bộ lọc theo Chuyên ngành/Phòng ban (Frontend, Backend, Mobile, UI/UX, QA, DevOps, HR).
   - Checkbox "Chọn tất cả" các thực tập sinh đang lọc và hiển thị số lượng theo thời gian thực.
   - Hiển thị danh sách TTS đã chọn trên Form chính dưới dạng các thẻ Tags/Chips kèm avatar và nút xóa nhanh (x).

5. **Lưu Trữ & Hiển Thị Danh Sách Ca Làm Việc**:
   - Bảng tổng hợp ca làm việc đã thiết lập.
   - Hiển thị Avatar Stack của các thực tập sinh trong ca.
   - Thao tác xóa ca làm việc với thông báo Toast tương tác.

---

## 📁 Cấu Trúc Mã Nguồn

```
shift-schedule-form/
├── index.html       # Cấu trúc Form, Modal và Bảng danh sách ca làm việc
├── style.css        # Giao diện tùy chỉnh, hiệu ứng hover, badge, tag
├── app.js           # Xử lý logic tính giờ, lọc tìm kiếm modal, validation và render
└── README.md        # Hướng dẫn chi tiết dự án
```

## 🛠️ Hướng Dẫn Khởi Chạy

Chỉ cần mở trực tiếp file `index.html` bằng trình duyệt web bất kỳ (Chrome, Edge, Firefox, Brave,...), hoặc dùng Live Server trong VS Code:

```bash
# Mở file trực tiếp trên Windows PowerShell
Start-Process "index.html"
```
