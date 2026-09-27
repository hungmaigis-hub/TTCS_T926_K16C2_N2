# Frontend - Hệ Thống Quản Lý Thực Tập Sinh (Internship Management)

Phân hệ giao diện người dùng (Frontend) của hệ thống quản lý thực tập sinh, được xây dựng theo kiến trúc Web hiện đại, phân quyền trực quan cho từng đối tượng người dùng và kết nối đồng bộ với hệ thống Backend FastAPI.

---

##  Công nghệ sử dụng

- **HTML5 Semantic**: Cấu trúc mã nguồn chuẩn SEO, ngữ nghĩa rõ ràng, dễ tiếp cận.
- **Tailwind CSS & CSS3**: Thiết kế giao diện hiện đại, hỗ trợ Responsive đa thiết bị (Mobile, Tablet, Desktop), hệ thống màu sắc hài hòa, hiệu ứng chuyển động mượt mà.
- **Vanilla JavaScript (ES6+)**: Xử lý logic thuần không phụ thuộc framework nặng, sử dụng Fetch API, Async/Await, Module hóa logic xử lý.
- **Krpano Viewer Engine (`tour.js`)**: Trình chiếu toàn cảnh thực tế ảo 360 độ với 74 điểm toàn cảnh quanh khuôn viên trường ICTU.
- **Biểu tượng & Phông chữ**: FontAwesome 6.4.0, Google Fonts (Inter, Plus Jakarta Sans).

---

##  Cấu trúc thư mục

```text
frontend/
├── css/                  # Bảng kiểu dáng CSS dùng chung và theo trang
│   ├── common.css        # Hệ thống biến giao diện, Dark/Light theme, modal chung
│   ├── style.css         # Phong cách toàn cục hệ thống
│   ├── dangnhap.css      # Giao diện xác thực đăng nhập/đăng ký
│   └── thamquan.css      # Giao diện điều khiển tour 360 độ
├── html/                 # Cấu trúc trang HTML phân theo nhóm người dùng
│   ├── index.html        # Trang điều hướng gốc hệ thống
│   ├── public/           # Các trang công khai cho mọi đối tượng
│   │   ├── index.html    # Landing page giới thiệu trường và chương trình thực tập
│   │   ├── dangnhap.html # Trang đăng nhập hệ thống (phân quyền vai trò)
│   │   ├── dangky.html   # Trang đăng ký tài khoản & nộp CV trực tuyến
│   │   └── thamquan.html # Tour tham quan thực tế ảo 360 độ trường ICTU
│   ├── quanly/           # Phân hệ dành cho HR, Mentor, Ban quản lý
│   │   ├── dashboard.html       # Bảng điều khiển thống kê tổng quan
│   │   ├── them_ho_so.html      # Thêm mới hồ sơ thực tập sinh
│   │   ├── xet_duyet_ho_so.html # Xét duyệt hồ sơ, xem và phê duyệt tài liệu CV/Đơn
│   │   ├── danh_gia.html        # Đánh giá năng lực & thái độ thực tập sinh
│   │   └── lich_thuc_tap.html   # Lịch trình & phân bổ thực tập sinh
│   └── sinhvien/         # Phân hệ dành riêng cho Sinh viên thực tập
│       ├── dashboard.html       # Bảng điều khiển sinh viên, tiến độ cá nhân
│       ├── hop_dong.html        # Xem nội dung và ký cam kết hợp đồng
│       ├── nhiem_vu.html        # Danh sách công việc và cập nhật tiến độ
│       └── tai_tai_lieu.html    # Nộp và theo dõi trạng thái duyệt tài liệu
├── js/                   # Mã nguồn logic JavaScript
│   ├── common.js         # Tiện ích chung, modal thông báo cập nhật, sidebar
│   ├── index.js          # Logic trang điều hướng gốc
│   ├── trangindex.js     # Logic landing page công khai
│   ├── dangnhap.js       # Logic xác thực và chuyển hướng vai trò
│   ├── dangky.js         # Xử lý form đăng ký tài khoản
│   ├── thamquan.js       # Trình điều khiển Tour 360 độ, chuyển cảnh, radar
│   ├── them_ho_so.js     # Validate và gửi dữ liệu thêm mới thực tập sinh
│   ├── xet_duyet_ho_so.js # Kết nối API duyệt hồ sơ, xem file và duyệt tài liệu
│   ├── danh_gia.js       # Xử lý tiêu chí đánh giá thực tập sinh
│   ├── lich_thuc_tap.js  # Lọc và hiển thị lịch thực tập
│   ├── hop_dong.js       # Xác nhận và ký kết hợp đồng điện tử
│   ├── nhiem_vu.js       # Quản lý danh sách nhiệm vụ và kéo thanh tiến độ
│   ├── tai_tai_lieu.js   # Quản lý upload và xem trước tài liệu
│   ├── tailwind.config.js # Cấu hình TailwindCSS
│   └── lib/              # Thư viện ngoài
│       └── tour.js       # Krpano HTML5 Viewer Engine (đã tối ưu hóa)
├── image/                # Tài nguyên đồ họa, logo, ảnh chụp toàn cảnh 360
│   ├── ictu_logo.png     # Logo trường Đại học CNTT & Truyền thông
│   └── tour/             # Dữ liệu ảnh và tọa độ 74 điểm tour 360
├── README.md             # Tài liệu kiến trúc và hướng dẫn Frontend
├── CHANGELOG.md          # Nhật ký phát triển Frontend
└── API_INTEGRATION.md    # Hướng dẫn kết nối và đặc tả API Backend
```

---

##  Phân hệ & Chức năng chi tiết

### 1. Phân hệ Công khai (Public)
- **Trang chủ (`html/public/index.html`)**: Giới thiệu về trường, các chương trình thực tập nổi bật, quy trình tuyển dụng và nút kêu gọi hành động (CTA).
- **Đăng nhập (`html/public/dangnhap.html`)**: Hỗ trợ phân loại vai trò đăng nhập (Sinh viên thực tập, Cán bộ quản lý HR, Mentor hướng dẫn) và chuyển hướng tới đúng Dashboard tương ứng.
- **Đăng ký (`html/public/dangky.html`)**: Biểu mẫu cho ứng viên đăng ký tài khoản, khai báo thông tin cá nhân và tải lên CV ứng tuyển.
- **Tham quan 360 (`html/public/thamquan.html`)**: Trải nghiệm thực tế ảo khuôn viên ICTU với bản đồ radar mini, danh sách các tòa nhà (Tòa C6, Samsung Lab, Sic Lab, Sân bóng, Thư viện,...), điều hướng chuyển cảnh góc nhìn 360 độ sống động.

### 2. Phân hệ Quản lý (HR & Ban Quản lý)
- **Dashboard Quản lý (`html/quanly/dashboard.html`)**: Thống kê số lượng thực tập sinh, biểu đồ trạng thái tiếp nhận, danh sách sinh viên mới cần phê duyệt.
- **Thêm hồ sơ (`html/quanly/them_ho_so.html`)**: Form tiếp nhận hồ sơ thực tập sinh mới với kiểm tra ràng buộc dữ liệu.
- **Xét duyệt hồ sơ (`html/quanly/xet_duyet_ho_so.html`)**:
  - Tích hợp trực tiếp với API Backend (`GET /api/v1/interns/{id}`, `GET /api/v1/documents/{ho_so_id}`).
  - Hộp thoại xem tài liệu đính kèm (CV, đơn xin thực tập) và cập nhật trạng thái phê duyệt từng tài liệu qua `PATCH /api/v1/documents/{id}/status`.
  - Huy hiệu hiển thị trạng thái kết nối Backend API thời gian thực và tự động chuyển đổi sang Mock Data nếu server offline.
- **Đánh giá thực tập sinh (`html/quanly/danh_gia.html`)**: Bộ tiêu chí chấm điểm kỹ năng chuyên môn, thái độ làm việc và nhận xét tổng kết.
- **Lịch thực tập (`html/quanly/lich_thuc_tap.html`)**: Theo dõi tiến độ thời gian theo tuần của từng thực tập sinh.

### 3. Phân hệ Sinh viên thực tập (Interns)
- **Dashboard Sinh viên (`html/sinhvien/dashboard.html`)**: Tổng quan thông tin thực tập cá nhân, tiến độ hoàn thành, nhiệm vụ hôm nay và thông báo mới từ mentor.
- **Hợp đồng thực tập (`html/sinhvien/hop_dong.html`)**: Xem chi tiết điều khoản hợp đồng thực tập, chế độ đãi ngộ và xác nhận cam kết trực tuyến.
- **Nhiệm vụ (`html/sinhvien/nhiem_vu.html`)**: Danh sách công việc được giao, hỗ trợ thanh trượt điều chỉnh tiến độ trực tiếp và lưu kết quả.
- **Tải tài liệu (`html/sinhvien/tai_tai_lieu.html`)**: Nộp bổ sung các tài liệu theo yêu cầu và theo dõi phản hồi phê duyệt từ HR.

---

##  Hướng dẫn Khởi chạy Frontend

### 1. Khởi chạy bằng Live Server (Khuyên dùng)
1. Cài đặt tiện ích mở rộng **Live Server** trong VS Code / Antigravity IDE.
2. Bấm chuột phải vào file `frontend/html/index.html` hoặc `frontend/html/public/index.html`.
3. Chọn **Open with Live Server** (Mặc định chạy tại địa chỉ `http://127.0.0.1:5500`).

### 2. Khởi chạy bằng Node.js HTTP Server
Nếu có sẵn Node.js, bạn có thể chạy một local server nhanh:
```bash
npx serve frontend
```

### 3. Cấu hình kết nối Backend API
Hệ thống Frontend mặc định kết nối với API Backend tại:
```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
```
- Khi Backend đang chạy: Dữ liệu thực tế từ cơ sở dữ liệu MySQL sẽ được hiển thị.
- Khi Backend chưa bật: Hệ thống sẽ kích hoạt cơ chế **Fallback Mock Data**, đảm bảo giao diện luôn hoạt động ổn định để demo và kiểm thử.

---

## Tiêu chuẩn thiết kế & Quy ước mã nguồn

1. **Liên kết nội bộ chuẩn xác 100%**: Tất cả đường dẫn CSS, JS, hình ảnh và liên kết chuyển trang đều sử dụng đường dẫn tương đối chuẩn xác, không có liên kết gãy.
2. **Modal thông báo nâng cấp toàn cục**: Tích hợp hàm `thongBaoDangCapNhat()` cho các tính năng chưa mở trong Sprint 1, mang lại trải nghiệm chuyên nghiệp cho người dùng.
3. **Mã nguồn sạch**: Toàn bộ mã nguồn JavaScript và HTML đều tuân thủ nguyên tắc định dạng nhất quán qua Prettier.