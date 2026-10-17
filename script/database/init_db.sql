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
    email_lien_he VARCHAR(100),
    danh_sach_nganh TEXT
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
    mat_khau_hash VARCHAR(255) NULL,
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
    lop VARCHAR(50),
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
    thoi_gian_checkin DATETIME NULL,
    thoi_gian_checkout DATETIME NULL,
    gio_check_in TIME NULL,
    gio_check_out TIME NULL,
    trang_thai VARCHAR(50) DEFAULT 'DungGio' COMMENT 'DungGio, DiMuon, VeSom, HoanThanh',
    phuong_thuc VARCHAR(50) DEFAULT 'Web' COMMENT 'QR, The, Web',
    ghi_chu VARCHAR(255) NULL,
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 11b. BẢNG CA LÀM VIỆC (Work Shifts / Schedules)
CREATE TABLE IF NOT EXISTS ca_lam_viec (
    ma_ca INT AUTO_INCREMENT PRIMARY KEY,
    ten_ca VARCHAR(100) NOT NULL,
    gio_bat_dau TIME NOT NULL,
    gio_ket_thuc TIME NOT NULL,
    cac_ngay_trong_tuan VARCHAR(255) NOT NULL,
    ngay_dien_ra DATE NULL,
    chuyen_nganh VARCHAR(100) NULL,
    lop VARCHAR(50) NULL,
    ma_chuong_trinh INT NULL,
    ghi_chu VARCHAR(255) NULL,
    trang_thai VARCHAR(50) DEFAULT 'HoatDong' COMMENT 'HoatDong, TamNgung',
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_chuong_trinh) REFERENCES chuong_trinh_thuc_tap(ma_chuong_trinh) ON DELETE SET NULL
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

-- 13. BẢNG ĐƠN XIN NGHỈ (Leave Requests API)
CREATE TABLE IF NOT EXISTS don_xin_nghi (
    ma_don INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    tu_ngay DATE NOT NULL,
    den_ngay DATE NOT NULL,
    ly_do VARCHAR(255) NOT NULL,
    trang_thai VARCHAR(50) DEFAULT 'Chờ duyệt' COMMENT 'Chờ duyệt, Đã duyệt, Từ chối',
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 14. BẢNG PHỤ CẤP THỰC TẬP (Allowance)
CREATE TABLE IF NOT EXISTS phu_cap (
    ma_phu_cap INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    thang INT NULL,
    nam INT NULL,
    thang_nam VARCHAR(7) NOT NULL COMMENT 'YYYY-MM',
    so_tien DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ngay_chi_tra DATE NULL,
    trang_thai VARCHAR(50) DEFAULT 'ChuaChiTra' COMMENT 'ChuaChiTra, DaChiTra, ChoDuyet',
    trang_thai_chi_tra VARCHAR(50) DEFAULT 'ChuaChiTra' COMMENT 'DaChiTra, ChuaChiTra',
    ghi_chu VARCHAR(255) NULL,
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 15. BẢNG YÊU CẦU HỖ TRỢ (Support Requests)
CREATE TABLE IF NOT EXISTS yeu_cau_ho_tro (
    ma_yeu_cau INT AUTO_INCREMENT PRIMARY KEY,
    ma_ho_so INT NOT NULL,
    loai_yeu_cau VARCHAR(50) NOT NULL COMMENT 'XinChungNhan, GiayXacNhan, Khac',
    noi_dung TEXT NOT NULL,
    phan_hoi_hr TEXT NULL,
    trang_thai VARCHAR(50) DEFAULT 'ChoXuLy' COMMENT 'ChoXuLy, DaXuLy',
    FOREIGN KEY (ma_ho_so) REFERENCES ho_so_thuc_tap(ma_ho_so) ON DELETE CASCADE
);

-- 16. BẢNG THÔNG BÁO (Notifications)
CREATE TABLE IF NOT EXISTS thong_bao (
    ma_thong_bao INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    tieu_de VARCHAR(200) NOT NULL,
    noi_dung TEXT NOT NULL,
    kenh VARCHAR(50) DEFAULT 'App' COMMENT 'Email, App',
    da_doc BOOLEAN DEFAULT FALSE,
    thoi_gian_gui DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES nguoi_dung(ma_nguoi_dung) ON DELETE CASCADE
);

-- 17. BẢNG NHẬT KÝ HỆ THỐNG (Audit Log)
CREATE TABLE IF NOT EXISTS nhat_ky_he_thong (
    ma_nhat_ky INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT NULL,
    hanh_dong VARCHAR(255) NOT NULL,
    dia_chi_ip VARCHAR(45) NULL,
    thoi_gian DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES nguoi_dung(ma_nguoi_dung) ON DELETE SET NULL
);

-- 18. BẢNG QUYỀN HẠN (RBAC Permissions)
CREATE TABLE IF NOT EXISTS quyen_han (
    ma_quyen_han INT AUTO_INCREMENT PRIMARY KEY,
    ma_quyen VARCHAR(100) NOT NULL UNIQUE,
    ten_quyen VARCHAR(150) NOT NULL,
    mo_ta VARCHAR(255) NULL,
    nhom_quyen VARCHAR(50) NOT NULL DEFAULT 'HeThong',
    INDEX idx_quyen_han_ma_quyen (ma_quyen)
);

-- 19. BẢNG VAI TRÒ - QUYỀN HẠN (RBAC Role-Permission Mapping)
CREATE TABLE IF NOT EXISTS vai_tro_quyen_han (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vai_tro VARCHAR(50) NOT NULL,
    ma_quyen_han INT NOT NULL,
    UNIQUE KEY uq_vai_tro_quyen_han (vai_tro, ma_quyen_han),
    INDEX idx_vai_tro (vai_tro),
    FOREIGN KEY (ma_quyen_han) REFERENCES quyen_han(ma_quyen_han) ON DELETE CASCADE
);

-- DỮ LIỆU MẪU (SEED DATA) ĐỂ TEST API
INSERT INTO phong_ban (ma_phong_ban, ten_phong_ban, mo_ta) 
VALUES (1, 'Trung tâm Phần mềm', 'Phòng kỹ thuật & phát triển hệ thống')
ON DUPLICATE KEY UPDATE ten_phong_ban = VALUES(ten_phong_ban);

INSERT INTO truong_dai_hoc (ma_truong, ten_truong, dia_chi, nguoi_lien_he, email_lien_he, danh_sach_nganh)
VALUES 
(1, 'Đại học Thái Nguyên (TNU)', 'Phường Tân Thịnh, TP. Thái Nguyên, Thái Nguyên', 'Ban Đào tạo TNU', 'daotao@tnu.edu.vn', '["Công nghệ thông tin", "Kỹ thuật phần mềm", "Khoa học máy tính", "An toàn thông tin", "Khoa học dữ liệu & Trí tuệ nhân tạo", "Hệ thống thông tin quản lý"]'),
(2, 'Đại học Bách Khoa Hà Nội (HUST)', 'Số 1 Đại Cồ Việt, Q. Hai Bà Trưng, Hà Nội', 'Phòng Đào tạo HUST', 'daotao@hust.edu.vn', '["Khoa học máy tính", "Kỹ thuật phần mềm", "Khoa học Dữ liệu và Trí tuệ nhân tạo", "An toàn không gian số", "Kỹ thuật Cơ điện tử", "Kỹ thuật Điều khiển & Tự động hóa", "Kỹ thuật Điện tử - Viễn thông", "Kỹ thuật máy tính"]'),
(3, 'Trường ĐH Công nghệ Thông tin và Truyền thông - ĐH Thái Nguyên (ICTU)', 'Đường Z115, Xã Quyết Thắng, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo ICTU', 'tuyensinh@ictu.edu.vn', '["Công nghệ phần mềm", "Kỹ thuật phần mềm", "Công nghệ thông tin", "Khoa học máy tính", "Trí tuệ nhân tạo & Dữ liệu lớn", "An toàn thông tin", "Mạng máy tính & Truyền thông dữ liệu", "Hệ thống thông tin quản lý", "Thiết kế đồ họa kỹ thuật số", "Công nghệ truyền thông đa phương tiện", "Thương mại điện tử & Kinh tế số", "Công nghệ kỹ thuật máy tính", "Kỹ thuật điều khiển & Tự động hóa", "Kỹ thuật điện tử, viễn thông"]'),
(4, 'Trường ĐH Kỹ thuật Công nghiệp - ĐH Thái Nguyên (TNUT)', 'Số 666 Đường 3/2, P. Tích Lương, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo TNUT', 'daotao@tnut.edu.vn', '["Kỹ thuật Cơ điện tử", "Kỹ thuật Điều khiển & Tự động hóa", "Kỹ thuật Cơ khí chế tạo máy", "Kỹ thuật Ô tô", "Kỹ thuật Điện tử - Viễn thông", "Kỹ thuật Điện tử & Tin học công nghiệp", "Kỹ thuật Xây dựng", "Kỹ thuật Quản lý công nghiệp"]'),
(5, 'Trường ĐH Kinh tế và Quản trị Kinh doanh - ĐH Thái Nguyên (TUEBA)', 'Phường Thịnh Đán, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo TUEBA', 'daotao@tueba.edu.vn', '["Thương mại điện tử", "Quản trị kinh doanh", "Marketing số & Truyền thông", "Kế toán doanh nghiệp", "Kiểm toán", "Tài chính - Ngân hàng", "Kinh doanh quốc tế & Logistics", "Kinh tế đầu tư", "Quản trị nhân lực", "Luật kinh tế"]'),
(6, 'Trường ĐH Khoa học - ĐH Thái Nguyên (TNUS)', 'Phường Tân Thịnh, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo TNUS', 'daotao@tnus.edu.vn', '["Công nghệ thông tin ứng dụng", "Khoa học Dữ liệu & Thống kê", "Toán tin ứng dụng", "Công nghệ Sinh học", "Quản lý Tài nguyên & Môi trường", "Báo chí & Truyền thông đa phương tiện", "Ngôn ngữ Anh", "Quản trị Dịch vụ Du lịch & Lữ hành"]'),
(7, 'Trường ĐH Sư phạm - ĐH Thái Nguyên (TNUE)', 'Số 20 Lương Ngọc Quyến, P. Quang Trung, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo TNUE', 'daotao@tnue.edu.vn', '["Sư phạm Tin học", "Sư phạm Toán học", "Sư phạm Vật lý", "Sư phạm Hóa học", "Sư phạm Tiếng Anh", "Sư phạm Ngữ văn", "Tâm lý học giáo dục", "Giáo dục Tiểu học", "Giáo dục Mầm non"]'),
(8, 'Trường ĐH Y - Dược - ĐH Thái Nguyên (TUMP)', 'Số 284 Lương Ngọc Quyến, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo TUMP', 'daotao@tump.edu.vn', '["Y khoa", "Dược học", "Răng - Hàm - Mặt", "Điều dưỡng", "Y học dự phòng", "Kỹ thuật Xét nghiệm y học", "Kỹ thuật Hình ảnh y học"]'),
(9, 'Trường ĐH Nông Lâm - ĐH Thái Nguyên (TUAF)', 'Xã Quyết Thắng, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo TUAF', 'daotao@tuaf.edu.vn', '["Công nghệ Thực phẩm", "Quản lý Đất đai", "Bất động sản & Địa chính", "Thú y", "Chăn nuôi công nghệ cao", "Khoa học Cây trồng", "Khoa học Môi trường", "Lâm nghiệp đô thị", "Kinh tế Nông nghiệp"]'),
(10, 'Trường Cao đẳng Kinh tế - Kỹ thuật Thái Nguyên (VETC)', 'Phường Thịnh Đán, TP. Thái Nguyên, Thái Nguyên', 'Phòng Tuyển sinh VETC', 'daotao@vetc.edu.vn', '["Tin học ứng dụng", "Công nghệ Kỹ thuật Điện - Điện tử", "Công nghệ Ô tô", "Cơ khí chế tạo máy", "Kế toán doanh nghiệp", "Quản trị mạng máy tính", "Thú y ứng dụng"]'),
(11, 'Trường Cao đẳng Công nghiệp Thái Nguyên (TNIC)', 'Số 293 Đường Gia Sàng, P. Gia Sàng, TP. Thái Nguyên, Thái Nguyên', 'Phòng Tuyển sinh TNIC', 'tuyensinh@tnic.edu.vn', '["Công nghệ Thông tin (Lập trình ứng dụng & Web)", "Điện công nghiệp", "Cắt gọt kim loại (CNC)", "Hàn công nghệ cao", "Công nghệ Ô tô", "Tự động hóa công nghiệp", "Kế toán doanh nghiệp"]'),
(12, 'Trường Cao đẳng Y tế Thái Nguyên', 'Số 478 Đường Thống Nhất, P. Tân Thịnh, TP. Thái Nguyên, Thái Nguyên', 'Phòng Tuyển sinh & Đào tạo', 'cdytthainguyen@gmail.com', '["Dược", "Điều dưỡng", "Hộ sinh", "Kỹ thuật Xét nghiệm y học", "Kỹ thuật Phục hồi chức năng"]'),
(13, 'Trường Cao đẳng Văn hóa Nghệ thuật Việt Bắc', 'Phường Đồng Quang, TP. Thái Nguyên, Thái Nguyên', 'Phòng Đào tạo', 'vhntvietbac@gmail.com', '["Thiết kế đồ họa", "Mỹ thuật ứng dụng", "Quản lý văn hóa", "Hướng dẫn du lịch", "Nghệ thuật biểu diễn múa & âm nhạc"]')
ON DUPLICATE KEY UPDATE ten_truong = VALUES(ten_truong), dia_chi = VALUES(dia_chi), danh_sach_nganh = VALUES(danh_sach_nganh);

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

INSERT INTO ca_lam_viec (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, cac_ngay_trong_tuan, ghi_chu, trang_thai)
VALUES
(1, 'Ca Sáng', '08:00:00', '12:00:00', 'Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6', 'Ca làm việc buổi sáng', 'HoatDong'),
(2, 'Ca Chiều', '13:30:00', '17:30:00', 'Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6', 'Ca làm việc buổi chiều', 'HoatDong'),
(3, 'Ca Hành Chính', '08:00:00', '17:30:00', 'Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6', 'Ca làm việc cả ngày', 'HoatDong')
ON DUPLICATE KEY UPDATE ten_ca = VALUES(ten_ca), gio_bat_dau = VALUES(gio_bat_dau), gio_ket_thuc = VALUES(gio_ket_thuc);

INSERT INTO phu_cap (ma_phu_cap, ma_ho_so, thang, nam, thang_nam, so_tien, ngay_chi_tra, trang_thai, trang_thai_chi_tra)
VALUES
(1, 1, 9, 2026, '2026-09', 3000000.00, '2026-09-30', 'DaChiTra', 'DaChiTra'),
(2, 1, 10, 2026, '2026-10', 3000000.00, '2026-10-31', 'DaChiTra', 'DaChiTra'),
(3, 1, 11, 2026, '2026-11', 3500000.00, NULL, 'ChuaChiTra', 'ChuaChiTra'),
(4, 2, 9, 2026, '2026-09', 2500000.00, '2026-09-30', 'DaChiTra', 'DaChiTra'),
(5, 2, 10, 2026, '2026-10', 2500000.00, NULL, 'ChuaChiTra', 'ChuaChiTra')
ON DUPLICATE KEY UPDATE so_tien = VALUES(so_tien), trang_thai = VALUES(trang_thai), trang_thai_chi_tra = VALUES(trang_thai_chi_tra);

INSERT INTO yeu_cau_ho_tro (ma_yeu_cau, ma_ho_so, loai_yeu_cau, noi_dung, phan_hoi_hr, trang_thai)
VALUES
(1, 1, 'XinChungNhan', 'Em xin giấy chứng nhận thực tập để nộp về trường', NULL, 'ChoXuLy'),
(2, 2, 'GiayXacNhan', 'Em xin xác nhận số giờ thực tập tháng 9', NULL, 'ChoXuLy')
ON DUPLICATE KEY UPDATE loai_yeu_cau = VALUES(loai_yeu_cau), noi_dung = VALUES(noi_dung);

-- 20. SEED QUYỀN HẠN MẪU CHO RBAC
INSERT INTO quyen_han (ma_quyen_han, ma_quyen, ten_quyen, mo_ta, nhom_quyen)
VALUES
(1, 'intern:read', 'Xem danh sách và hồ sơ thực tập sinh', 'Cho phép truy cập thông tin chi tiết và danh sách sinh viên thực tập', 'ThucTapSinh'),
(2, 'intern:create', 'Thêm mới thực tập sinh', 'Cho phép tạo mới hoặc import hồ sơ thực tập sinh vào hệ thống', 'ThucTapSinh'),
(3, 'intern:update', 'Cập nhật thông tin thực tập sinh', 'Cho phép sửa hồ sơ, phân công mentor hoặc đổi trạng thái thực tập', 'ThucTapSinh'),
(4, 'intern:delete', 'Xóa hồ sơ thực tập sinh', 'Cho phép xóa hoặc đưa hồ sơ vào trạng thái thôi học', 'ThucTapSinh'),
(5, 'task:read', 'Xem danh sách công việc và nhiệm vụ', 'Cho phép tra cứu công việc được giao hoặc danh sách task của nhóm', 'NhiemVu'),
(6, 'task:create', 'Giao nhiệm vụ cho thực tập sinh', 'Cho phép tạo task mới và phân công người thực hiện', 'NhiemVu'),
(7, 'task:update', 'Cập nhật tiến độ nhiệm vụ', 'Cho phép đổi trạng thái tiến độ công việc hoặc duyệt hoàn thành', 'NhiemVu'),
(8, 'report:read', 'Xem báo cáo thực tập tuần', 'Cho phép đọc nội dung báo cáo nộp định kỳ của sinh viên', 'BaoCao'),
(9, 'report:feedback', 'Đánh giá và nhận xét báo cáo tuần', 'Cho phép gửi phản hồi nhận xét và chấm điểm báo cáo tuần', 'BaoCao'),
(10, 'evaluation:create', 'Đánh giá kết quả cuối kỳ thực tập', 'Cho phép lập bảng điểm và nhận xét tổng kết cho sinh viên', 'BaoCao'),
(11, 'attendance:scan', 'Quét mã điểm danh và chấm công', 'Cho phép ghi nhận check-in, check-out và điểm danh trực tiếp', 'ChamCong'),
(12, 'leave:approve', 'Xét duyệt đơn xin nghỉ phép', 'Cho phép phê duyệt hoặc từ chối đơn xin nghỉ phép của thực tập sinh', 'ChamCong'),
(13, 'meeting:create', 'Tạo và chủ trì lịch họp', 'Cho phép lên lịch họp trực tuyến/trực tiếp và mời người tham gia', 'LichHop'),
(14, 'support:process', 'Tiếp nhận và xử lý yêu cầu hỗ trợ', 'Cho phép phản hồi, xử lý giấy xác nhận, chứng nhận thực tập', 'HoTro'),
(15, 'role:manage', 'Quản trị vai trò và phân quyền hệ thống', 'Cho phép xem danh mục quyền, phân quyền vai trò cho người dùng', 'HeThong'),
(16, 'system:config', 'Cấu hình tham số hệ thống và tích hợp HRM', 'Cho phép quản trị thiết lập hệ thống và kết nối ngoại vi', 'HeThong')
ON DUPLICATE KEY UPDATE ten_quyen = VALUES(ten_quyen), mo_ta = VALUES(mo_ta), nhom_quyen = VALUES(nhom_quyen);

-- 21. SEED PHÂN QUYỀN MẶC ĐỊNH CHO CÁC VAI TRÒ
INSERT INTO vai_tro_quyen_han (vai_tro, ma_quyen_han)
VALUES
-- Admin sở hữu toàn bộ các quyền
('Admin', 1), ('Admin', 2), ('Admin', 3), ('Admin', 4), ('Admin', 5), ('Admin', 6), ('Admin', 7), ('Admin', 8),
('Admin', 9), ('Admin', 10), ('Admin', 11), ('Admin', 12), ('Admin', 13), ('Admin', 14), ('Admin', 15), ('Admin', 16),
-- HR
('HR', 1), ('HR', 2), ('HR', 3), ('HR', 4), ('HR', 11), ('HR', 12), ('HR', 13), ('HR', 14), ('HR', 15),
-- Mentor
('Mentor', 1), ('Mentor', 5), ('Mentor', 6), ('Mentor', 7), ('Mentor', 8), ('Mentor', 9), ('Mentor', 10), ('Mentor', 13),
-- ThucTapSinh
('ThucTapSinh', 5), ('ThucTapSinh', 7), ('ThucTapSinh', 8),
-- NhaTruong
('NhaTruong', 1), ('NhaTruong', 8)
ON DUPLICATE KEY UPDATE vai_tro = VALUES(vai_tro);

-- 22. BẢNG THÔNG BÁO (Sprint 4 - Nguyễn Văn Hiếu)
CREATE TABLE IF NOT EXISTS thong_bao (
    ma_thong_bao INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_nhan VARCHAR(50) NOT NULL,
    tieu_de VARCHAR(255) NOT NULL,
    noi_dung TEXT NOT NULL,
    loai_thong_bao VARCHAR(50) NOT NULL DEFAULT 'CHUNG',
    da_doc BOOLEAN NOT NULL DEFAULT FALSE,
    ngay_tao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_thong_bao_nguoi_nhan (ma_nguoi_nhan),
    INDEX idx_thong_bao_da_doc (da_doc),
    INDEX idx_thong_bao_ngay_tao (ngay_tao)
);

-- 23. BẢNG NHẬT KÝ HOẠT ĐỘNG (Sprint 4 - Nguyễn Văn Hiếu)
CREATE TABLE IF NOT EXISTS nhat_ky_hoat_dong (
    ma_nhat_ky INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung VARCHAR(50) NULL,
    hanh_dong VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    phuong_thuc VARCHAR(10) NOT NULL,
    dia_chi_ip VARCHAR(50) NULL,
    mo_ta TEXT NULL,
    thoi_gian DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nhat_ky_nguoi_dung (ma_nguoi_dung),
    INDEX idx_nhat_ky_thoi_gian (thoi_gian),
    INDEX idx_nhat_ky_hanh_dong (hanh_dong),
    INDEX idx_nhat_ky_endpoint (endpoint)
);






