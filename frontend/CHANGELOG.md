# Changelog - Frontend

Tất cả các thay đổi và tiến độ phát triển của phân hệ Frontend sẽ được ghi lại trong tài liệu này.

---

## [1.1.0] - 2026-09-27

### Đã thêm & Cải tiến (Added & Refactored)
- **Tái cấu trúc kiến trúc thư mục Frontend**:
  - Phân chia toàn bộ các trang HTML từ thư mục phẳng thành 3 phân hệ chuyên biệt:
    - `frontend/html/public/`: Trang công khai (Trang chủ, Đăng nhập, Đăng ký, Tham quan 360).
    - `frontend/html/quanly/`: Phân hệ quản lý (Dashboard, Thêm hồ sơ, Xét duyệt hồ sơ, Đánh giá, Lịch thực tập).
    - `frontend/html/sinhvien/`: Phân hệ sinh viên (Dashboard sinh viên, Hợp đồng, Nhiệm vụ, Tải tài liệu).
  - Cập nhật chuẩn hóa toàn bộ đường dẫn tương đối (relative paths) CSS, JS, hình ảnh, đảm bảo 100% liên kết hợp lệ.
- **Xây dựng Dashboard Sinh viên (`html/sinhvien/dashboard.html`)**:
  - Thiết kế bảng điều khiển riêng biệt cho sinh viên thực tập với phong cách đồng bộ cùng hệ thống quản lý.
  - Hiển thị thanh tiến độ thực tập tổng quan, widget nhiệm vụ cần hoàn thành hôm nay, thời gian thực tập và mentor phụ trách.
- **Tích hợp Modal thông báo nâng cấp toàn cục**:
  - Bổ sung hàm `thongBaoDangCapNhat()` và listener tự động cho thuộc tính `[data-coming-soon]` trong `frontend/js/common.js`.
  - Cho phép người dùng trải nghiệm các nút chức năng chưa phát hành với giao diện thông báo sang trọng, hiện đại.
- **Tích hợp API Backend trong Xét duyệt hồ sơ (`js/xet_duyet_ho_so.js`)**:
  - Loại bỏ hoàn toàn hơn 280 dòng dữ liệu mẫu tĩnh (hardcoded mock data) trong `xet_duyet_ho_so.html`.
  - Kết nối trực tiếp các API Backend:
    - `GET /api/v1/interns/{id}`: Tải thông tin thực tập sinh theo thời gian thực.
    - `GET /api/v1/documents/{ho_so_id}`: Tải danh sách tài liệu đính kèm (CV, Đơn xin thực tập).
    - `PATCH /api/v1/documents/{id}/status`: Cập nhật trạng thái duyệt tài liệu (Phê duyệt / Từ chối kèm lý do).
  - Tích hợp hộp thoại xem trước tài liệu đính kèm và huy hiệu thông báo trạng thái kết nối API thời gian thực.
  - Bổ sung cơ chế Fallback Mock Data tự động khi máy chủ Backend tạm thời offline.
- **Tối ưu hóa Krpano Tour 360**:
  - Chuẩn hóa tên tệp thành `frontend/js/lib/tour.js`.
  - Định dạng chuẩn toàn bộ tệp bằng Prettier.
  - Cập nhật liên kết script trong `frontend/html/public/thamquan.html`.

---

## [1.0.0] - 2026-09-22

### Khởi tạo ban đầu (Initial Release)
- **Thiết lập giao diện nền tảng**:
  - Cấu hình TailwindCSS CDN, FontAwesome 6 và hệ thống màu sắc theo chuẩn nhận diện ICTU.
  - Xây dựng trang chủ Landing Page (`index.html`) giới thiệu chương trình thực tập.
  - Xây dựng giao diện Đăng nhập (`dangnhap.html`) và Đăng ký tài khoản (`dangky.html`).
- **Tích hợp Tour 360 thực tế ảo**:
  - Xây dựng trải nghiệm thực tế ảo khuôn viên ICTU với 74 góc chụp toàn cảnh chất lượng cao.
  - Tích hợp radar điều hướng, chuyển đổi giữa các địa điểm trong trường.
- **Thiết kế các biểu mẫu quản lý**:
  - Xây dựng khung giao diện Thêm hồ sơ thực tập sinh, Đánh giá thực tập sinh và Lịch thực tập.
