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

-- 6. BẢNG TÀI LIỆU HỒ SƠ
CREATE TABLE IF NOT EXISTS tai_lieu_ho_so (
    ma_tai_lieu INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    loai_tai_lieu VARCHAR(50) NOT NULL COMMENT 'CV, DonXinThucTap, GiayGioiThieu',
    duong_dan_file VARCHAR(255) NOT NULL,
    trang_thai_duyet VARCHAR(50) DEFAULT 'ChoDuyet' COMMENT 'ChoDuyet, DaDuyet, TuChoi',
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 7. BẢNG HỢP ĐỒNG THỰC TẬP
CREATE TABLE IF NOT EXISTS hop_dong (
    ma_hop_dong INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    duong_dan_file VARCHAR(255) NOT NULL,
    ngay_tai_len DATE DEFAULT (CURRENT_DATE),
    ngay_ky DATE,
    trang_thai VARCHAR(50) DEFAULT 'ChuaXacNhan' COMMENT 'ChuaXacNhan, DaXacNhan',
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 8. BẢNG NHIỆM VỤ (Tasks)
CREATE TABLE IF NOT EXISTS nhiem_vu (
    ma_nhiem_vu INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    ten_nhiem_vu VARCHAR(150) NOT NULL,
    mo_ta TEXT,
    han_hoan_thanh DATE NOT NULL,
    tien_do_phantram INT DEFAULT 0,
    trang_thai VARCHAR(50) DEFAULT 'Chưa bắt đầu',
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 9. BẢNG BÁO CÁO TUẦN (Weekly Reports)
CREATE TABLE IF NOT EXISTS bao_cao_tuan (
    ma_bao_cao INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    ma_nhiem_vu INT,
    tuan_so INT NOT NULL,
    noi_dung_cong_viec TEXT NOT NULL,
    ket_qua_dat_duoc TEXT,
    phan_hoi_mentor TEXT,
    thoi_gian_nop DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE,
    FOREIGN KEY (ma_nhiem_vu) REFERENCES nhiem_vu(ma_nhiem_vu) ON DELETE SET NULL
);

-- 10. BẢNG ĐÁNH GIÁ (Evaluations)
CREATE TABLE IF NOT EXISTS danh_gia (
    ma_danh_gia INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    ma_nguoi_danh_gia INT NOT NULL,
    loai_danh_gia VARCHAR(50) NOT NULL COMMENT 'GiuaKy, CuoiKy',
    diem_ky_nang FLOAT NOT NULL,
    diem_thai_do FLOAT NOT NULL,
    nhan_xet_chi_tiet TEXT,
    de_xuat_tuyen_chinh_thuc BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE,
    FOREIGN KEY (ma_nguoi_danh_gia) REFERENCES nguoi_dung(ma_nguoi_dung) ON DELETE RESTRICT
);

-- 11. BẢNG CHẤM CÔNG (Attendance Log)
CREATE TABLE IF NOT EXISTS cham_cong (
    ma_cham_cong INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    ngay_cham_cong DATE NOT NULL,
    gio_check_in TIME,
    gio_check_out TIME,
    phuong_thuc VARCHAR(50) DEFAULT 'Web' COMMENT 'QR, The, Web',
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 12. BẢNG ĐƠN NGHỈ PHÉP (Leave Requests)
CREATE TABLE IF NOT EXISTS don_nghi_phep (
    ma_don INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    ngay_nghi DATE NOT NULL,
    ly_do VARCHAR(255) NOT NULL,
    trang_thai VARCHAR(50) DEFAULT 'ChoDuyet' COMMENT 'ChoDuyet, DaDuyet, TuChoi',
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
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

INSERT INTO tai_lieu_ho_so (ma_tai_lieu, ma_ho_so, loai_tai_lieu, duong_dan_file, trang_thai_duyet)
VALUES 
(1, 1, 'CV', 'uploads/cv_nguyen_van_a.pdf', 'ChoDuyet'),
(2, 1, 'DonXinThucTap', 'uploads/don_xin_nguyen_van_a.pdf', 'DaDuyet')
ON DUPLICATE KEY UPDATE loai_tai_lieu = VALUES(loai_tai_lieu), trang_thai_duyet = VALUES(trang_thai_duyet);

INSERT INTO hop_dong (ma_hop_dong, ma_ho_so, duong_dan_file, ngay_tai_len, ngay_ky, trang_thai)
VALUES 
(1, 1, 'uploads/hop_dong_nguyen_van_a.pdf', '2026-09-20', NULL, 'ChuaXacNhan'),
(2, 2, 'uploads/hop_dong_tran_thi_b.pdf', '2026-09-20', '2026-09-25', 'DaXacNhan')
ON DUPLICATE KEY UPDATE trang_thai = VALUES(trang_thai);

INSERT INTO nhiem_vu (ma_nhiem_vu, ma_ho_so, ten_nhiem_vu, mo_ta, han_hoan_thanh, tien_do_phantram, trang_thai)
VALUES 
(1, 1, 'Nghiên cứu kiến trúc Microservices & Docker', 'Cấu hình Docker Compose và pass review Tech Lead', '2026-10-15', 30, 'Đang thực hiện'),
(2, 1, 'Xây dựng API quản lý lịch trình và nhiệm vụ', 'Thiết kế endpoint GET /api/v1/interns/my-schedule', '2026-10-20', 0, 'Chưa bắt đầu'),
(3, 2, 'Thiết kế giao diện Dashboard quản lý', 'Cắt HTML/CSS responsive cho bảng điều khiển', '2026-10-20', 100, 'Hoàn thành')
ON DUPLICATE KEY UPDATE ten_nhiem_vu = VALUES(ten_nhiem_vu), tien_do_phantram = VALUES(tien_do_phantram), trang_thai = VALUES(trang_thai);

INSERT INTO bao_cao_tuan (ma_bao_cao, ma_ho_so, ma_nhiem_vu, tuan_so, noi_dung_cong_viec, ket_qua_dat_duoc, phan_hoi_mentor, thoi_gian_nop)
VALUES
(1, 1, 1, 1, 'Tìm hiểu Docker và triển khai container hóa cho ứng dụng FastAPI', 'Hoàn thành file Dockerfile và docker-compose.yml', 'Tốt, tiếp tục nghiên cứu Microservices', '2026-09-10 17:00:00'),
(2, 1, 2, 2, 'Thiết kế endpoint GET /api/v1/interns/my-schedule', 'Hoàn thiện endpoint và test case đạt 100%', NULL, '2026-09-17 16:30:00')
ON DUPLICATE KEY UPDATE noi_dung_cong_viec = VALUES(noi_dung_cong_viec);

INSERT INTO danh_gia (ma_danh_gia, ma_ho_so, ma_nguoi_danh_gia, loai_danh_gia, diem_ky_nang, diem_thai_do, nhan_xet_chi_tiet, de_xuat_tuyen_chinh_thuc)
VALUES
(1, 1, 3, 'GiuaKy', 8.5, 9.0, 'Tiếp thu nhanh, hoàn thành tốt nhiệm vụ được giao', FALSE),
(2, 1, 3, 'CuoiKy', 9.0, 9.5, 'Kỹ năng chuyên môn xuất sắc, có tinh thần trách nhiệm cao', TRUE),
(3, 2, 3, 'GiuaKy', 7.5, 8.0, 'Thực hiện công việc đúng tiến độ, cần chủ động hơn trong giao tiếp', FALSE),
(4, 2, 3, 'CuoiKy', 8.0, 8.5, 'Tiến bộ rõ rệt, đáp ứng tốt yêu cầu dự án', FALSE)
ON DUPLICATE KEY UPDATE diem_ky_nang = VALUES(diem_ky_nang), diem_thai_do = VALUES(diem_thai_do), de_xuat_tuyen_chinh_thuc = VALUES(de_xuat_tuyen_chinh_thuc);

INSERT INTO cham_cong (ma_cham_cong, ma_ho_so, ngay_cham_cong, gio_check_in, gio_check_out, phuong_thuc)
VALUES
(1, 1, '2026-09-02', '08:15:00', '17:30:00', 'Web'),
(2, 1, '2026-09-03', '08:45:00', '17:35:00', 'Web'),
(3, 1, '2026-09-04', '08:20:00', '17:30:00', 'QR'),
(4, 2, '2026-09-02', '08:10:00', '17:30:00', 'Web'),
(5, 2, '2026-09-03', '08:50:00', '17:40:00', 'The')
ON DUPLICATE KEY UPDATE ngay_cham_cong = VALUES(ngay_cham_cong), gio_check_in = VALUES(gio_check_in), gio_check_out = VALUES(gio_check_out);

INSERT INTO don_nghi_phep (ma_don, ma_ho_so, ngay_nghi, ly_do, trang_thai)
VALUES
(1, 1, '2026-09-05', 'Bị ốm đột xuất có giấy khám bệnh', 'DaDuyet'),
(2, 1, '2026-09-12', 'Việc bận gia đình', 'ChoDuyet'),
(3, 2, '2026-09-08', 'Đi thi học phần ở trường', 'DaDuyet')
ON DUPLICATE KEY UPDATE ngay_nghi = VALUES(ngay_nghi), ly_do = VALUES(ly_do), trang_thai = VALUES(trang_thai);


