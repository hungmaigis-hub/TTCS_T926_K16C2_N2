CREATE DATABASE IF NOT EXISTS intern_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE intern_management;

-- 1. BẢNG PHÒNG BAN
CREATE TABLE IF NOT EXISTS phong_ban (
    ma_phong_ban INT AUTO_INCREMENT PRIMARY KEY,
    ten_phong_ban VARCHAR(100) NOT NULL,
    mo_ta VARCHAR(255)
);

-- 2. BẢNG TRƯỜNG ĐẠI HỌC
CREATE TABLE IF NOT EXISTS truong_dai_hoc (
    ma_truong INT AUTO_INCREMENT PRIMARY KEY,
    ten_truong VARCHAR(200) NOT NULL,
    dia_chi VARCHAR(255),
    nguoi_lien_he VARCHAR(100),
    email_lien_he VARCHAR(100)
);

-- 3. BẢNG CHƯƠNG TRÌNH THỰC TẬP
CREATE TABLE IF NOT EXISTS chuong_trinh_thuc_tap (
    ma_chuong_trinh INT AUTO_INCREMENT PRIMARY KEY,
    ma_phong_ban INT NOT NULL,
    ten_chuong_trinh VARCHAR(150) NOT NULL,
    ngay_bat_dau DATE NOT NULL,
    ngay_ket_thuc DATE NOT NULL,
    mo_ta TEXT,
    FOREIGN KEY (ma_phong_ban) REFERENCES phong_ban(ma_phong_ban) ON DELETE CASCADE
);

-- 4. BẢNG NGƯỜI DÙNG (Tài khoản)
CREATE TABLE IF NOT EXISTS nguoi_dung (
    ma_nguoi_dung INT AUTO_INCREMENT PRIMARY KEY,
    ma_phong_ban INT,
    ho_ten VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    so_dien_thoai VARCHAR(20) UNIQUE,
    vai_tro VARCHAR(50) DEFAULT 'ThucTapSinh',
    trang_thai VARCHAR(50) DEFAULT 'HoatDong',
    FOREIGN KEY (ma_phong_ban) REFERENCES phong_ban(ma_phong_ban) ON DELETE SET NULL
);

-- 5. BẢNG HỒ SƠ THỰC TẬP (Thực thể trung tâm)
CREATE TABLE IF NOT EXISTS ho_so_thuc_tap (
    ma_ho_so INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    ma_truong INT,
    ma_chuong_trinh INT,
    ma_mentor INT,
    chuyen_nganh VARCHAR(100),
    trang_thai_xet_duyet VARCHAR(50) DEFAULT 'ChoDuyet',
    trang_thai_thuc_tap VARCHAR(50) DEFAULT 'DangThucTap',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES nguoi_dung(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_truong) REFERENCES truong_dai_hoc(ma_truong) ON DELETE SET NULL,
    FOREIGN KEY (ma_chuong_trinh) REFERENCES chuong_trinh_thuc_tap(ma_chuong_trinh) ON DELETE SET NULL,
    FOREIGN KEY (ma_mentor) REFERENCES nguoi_dung(ma_nguoi_dung) ON DELETE SET NULL
);

-- DỮ LIỆU MẪU (SEED DATA) ĐỂ TEST API
INSERT INTO phong_ban (ma_phong_ban, ten_phong_ban, mo_ta) 
VALUES (1, 'Trung tâm Phần mềm', 'Phòng kỹ thuật & phát triển hệ thống')
ON DUPLICATE KEY UPDATE ten_phong_ban = VALUES(ten_phong_ban);

INSERT INTO truong_dai_hoc (ma_truong, ten_truong, dia_chi, nguoi_lien_he, email_lien_he)
VALUES 
(1, 'Đại học Thái Nguyên', 'Thái Nguyên', 'Thầy Nguyễn Văn X', 'lienhe@tnu.edu.vn'),
(2, 'Đại học Bách Khoa Hà Nội', 'Hà Nội', 'Cô Trần Thị Y', 'lienhe@hust.edu.vn')
ON DUPLICATE KEY UPDATE ten_truong = VALUES(ten_truong);

INSERT INTO chuong_trinh_thuc_tap (ma_chuong_trinh, ma_phong_ban, ten_chuong_trinh, ngay_bat_dau, ngay_ket_thuc, mo_ta)
VALUES (1, 1, 'Thực tập sinh Khóa Mùa Thu 2026', '2026-09-01', '2026-12-30', 'Chương trình đào tạo kỹ sư phần mềm thực chiến')
ON DUPLICATE KEY UPDATE ten_chuong_trinh = VALUES(ten_chuong_trinh);

INSERT INTO nguoi_dung (ma_nguoi_dung, ma_phong_ban, ho_ten, email, so_dien_thoai, vai_tro, trang_thai)
VALUES 
(1, 1, 'Nguyễn Văn A', 'vana@example.com', '0912345678', 'ThucTapSinh', 'HoatDong'),
(2, 1, 'Trần Thị B', 'thib@example.com', '0987654321', 'ThucTapSinh', 'HoatDong'),
(3, 1, 'Nguyễn Hướng Dẫn', 'mentor@example.com', '0905123456', 'Mentor', 'HoatDong')
ON DUPLICATE KEY UPDATE ho_ten = VALUES(ho_ten), email = VALUES(email), so_dien_thoai = VALUES(so_dien_thoai);

INSERT INTO ho_so_thuc_tap (ma_ho_so, ma_nguoi_dung, ma_truong, ma_chuong_trinh, ma_mentor, chuyen_nganh, trang_thai_xet_duyet, trang_thai_thuc_tap)
VALUES 
(1, 1, 1, 1, 3, 'Công nghệ thông tin', 'DaDuyet', 'DangThucTap'),
(2, 2, 2, 1, 3, 'Khoa học máy tính', 'DaDuyet', 'DangThucTap')
ON DUPLICATE KEY UPDATE chuyen_nganh = VALUES(chuyen_nganh);
