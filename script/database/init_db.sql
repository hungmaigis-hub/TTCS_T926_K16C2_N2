CREATE DATABASE IF NOT EXISTS intern_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE intern_management;

CREATE TABLE IF NOT EXISTS interns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL COMMENT 'Họ và tên',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'Email liên hệ',
    phone VARCHAR(20) COMMENT 'Số điện thoại',
    university VARCHAR(150) COMMENT 'Trường đại học',
    major VARCHAR(100) COMMENT 'Chuyên ngành',
    status VARCHAR(50) DEFAULT 'Đang thực tập' COMMENT 'Trạng thái thực tập',
    start_date DATE COMMENT 'Ngày bắt đầu',
    end_date DATE COMMENT 'Ngày kết thúc',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời gian tạo bản ghi'
);

-- Thêm 3 ts mẫu để test api

INSERT INTO interns (id, full_name, email, phone, university, major, status, start_date, end_date) 
VALUES 
(1, 'Nguyễn Văn A', 'vana@example.com', '0912345678', 'Đại học Thái Nguyên', 'Công nghệ thông tin', 'Đang thực tập', '2026-09-01', '2026-12-01'),
(2, 'Trần Thị B', 'thib@example.com', '0987654321', 'Đại học Quốc Gia', 'Khoa học máy tính', 'Đã hoàn thành', '2026-06-01', '2026-08-31'),
(3, 'Lê Hoàng C', 'hoangc@example.com', '0905123456', 'Đại học Bưu Chính', 'An toàn thông tin', 'Đang thực tập', '2026-09-15', '2026-12-15')
ON DUPLICATE KEY UPDATE id=id;
