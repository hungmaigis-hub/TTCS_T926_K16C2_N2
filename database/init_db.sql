-- ============================================================
-- Database: intern_management
-- Script khởi tạo CSDL cho hệ thống quản lý thực tập sinh
-- Nhóm: TTCS_T926_K16C2_N2
-- ============================================================

CREATE DATABASE IF NOT EXISTS intern_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE intern_management;

-- ============================================================
-- Bảng: nguoi_dung
-- Lưu tất cả tài khoản người dùng: HR, Mentor, ThucTapSinh, Admin
-- ============================================================
CREATE TABLE IF NOT EXISTS nguoi_dung (
    ma_nguoi_dung   VARCHAR(20)     NOT NULL,
    ho_ten          VARCHAR(100)    NOT NULL            COMMENT 'Họ và tên đầy đủ',
    email           VARCHAR(150)    NOT NULL            COMMENT 'Email đăng nhập (unique)',
    mat_khau_hash   VARCHAR(255)    NOT NULL            COMMENT 'Mật khẩu đã băm bcrypt',
    so_dien_thoai   VARCHAR(15)     NULL                COMMENT 'Số điện thoại',
    vai_tro         ENUM('HR','Mentor','ThucTapSinh','Admin')
                                    NOT NULL            COMMENT 'Vai trò trong hệ thống',
    kich_hoat       TINYINT(1)      NOT NULL DEFAULT 1  COMMENT '1=đang hoạt động, 0=vô hiệu hóa',
    ngay_tao        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME        NULL     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (ma_nguoi_dung),
    UNIQUE KEY uq_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Bảng người dùng hệ thống';

-- ============================================================
-- Bảng: ho_so_thuc_tap
-- Hồ sơ thực tập của sinh viên – trường ma_mentor là FK sang nguoi_dung
-- ============================================================
CREATE TABLE IF NOT EXISTS ho_so_thuc_tap (
    ma_ho_so            VARCHAR(20)     NOT NULL,
    ma_sinh_vien        VARCHAR(20)     NOT NULL            COMMENT 'FK → nguoi_dung (vai trò ThucTapSinh)',
    ho_ten              VARCHAR(100)    NOT NULL,
    email               VARCHAR(150)    NULL,
    so_dien_thoai       VARCHAR(15)     NULL,
    truong_dai_hoc      VARCHAR(200)    NULL,
    nganh_hoc           VARCHAR(100)    NULL,
    gioi_thieu_ban_than TEXT            NULL,
    vi_tri_thuc_tap     VARCHAR(100)    NULL,
    ngay_bat_dau        DATE            NULL,
    ngay_ket_thuc       DATE            NULL,
    trang_thai          ENUM('ChoDuyet','DaDuyet','TuChoi','DangThucTap','HoanThanh')
                                        NOT NULL DEFAULT 'ChoDuyet',
    ghi_chu             TEXT            NULL,

    -- Trường chính cần PATCH
    ma_mentor           VARCHAR(20)     NULL                COMMENT 'FK → nguoi_dung (vai trò Mentor)',

    ngay_tao            DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat       DATETIME        NULL     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (ma_ho_so),
    CONSTRAINT fk_hstt_sinh_vien
        FOREIGN KEY (ma_sinh_vien) REFERENCES nguoi_dung(ma_nguoi_dung)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_hstt_mentor
        FOREIGN KEY (ma_mentor) REFERENCES nguoi_dung(ma_nguoi_dung)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_ma_mentor  (ma_mentor),
    INDEX idx_ma_sinh_vien (ma_sinh_vien)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Bảng hồ sơ thực tập sinh';


-- ============================================================
-- Dữ liệu mẫu (seed data) – dùng để test
-- ============================================================

-- Xóa dữ liệu cũ (thứ tự quan trọng vì FK)
DELETE FROM ho_so_thuc_tap;
DELETE FROM nguoi_dung;

-- Tạo người dùng mẫu
-- Mật khẩu hash bên dưới tương ứng với "Password@123" (bcrypt)
INSERT INTO nguoi_dung (ma_nguoi_dung, ho_ten, email, mat_khau_hash, so_dien_thoai, vai_tro, kich_hoat) VALUES
-- Admin
('ADMIN01',  'Quản Trị Viên',      'admin@company.com',       '$2b$12$examplehash...admin',   '0900000001', 'Admin',       1),

-- HR
('HR01',     'Nguyễn Thị Hoa',    'hoa.nguyen@company.com',  '$2b$12$examplehash...hr01',    '0900000002', 'HR',          1),
('HR02',     'Trần Minh Đức',     'duc.tran@company.com',    '$2b$12$examplehash...hr02',    '0900000003', 'HR',          1),

-- Mentor đang hoạt động
('MENTOR01', 'Lê Văn Phúc',       'phuc.le@company.com',     '$2b$12$examplehash...m01',     '0901111001', 'Mentor',      1),
('MENTOR02', 'Nguyễn Thị Lan',    'lan.nguyen@company.com',  '$2b$12$examplehash...m02',     '0901111002', 'Mentor',      1),
('MENTOR03', 'Phạm Quốc Huy',     'huy.pham@company.com',    '$2b$12$examplehash...m03',     '0901111003', 'Mentor',      1),

-- Mentor bị vô hiệu hóa (để test case 403)
('MENTOR04', 'Vũ Thanh Tùng',     'tung.vu@company.com',     '$2b$12$examplehash...m04',     '0901111004', 'Mentor',      0),

-- Thực tập sinh
('TTS001',   'Trần Văn An',       'an.tran@uni.edu.vn',      '$2b$12$examplehash...tts001',  '0902222001', 'ThucTapSinh', 1),
('TTS002',   'Nguyễn Thị Bình',   'binh.nguyen@uni.edu.vn',  '$2b$12$examplehash...tts002',  '0902222002', 'ThucTapSinh', 1),
('TTS003',   'Phạm Văn Cường',    'cuong.pham@uni.edu.vn',   '$2b$12$examplehash...tts003',  '0902222003', 'ThucTapSinh', 1);


-- Hồ sơ thực tập mẫu
INSERT INTO ho_so_thuc_tap
    (ma_ho_so, ma_sinh_vien, ho_ten, email, so_dien_thoai, truong_dai_hoc,
     nganh_hoc, vi_tri_thuc_tap, ngay_bat_dau, ngay_ket_thuc, trang_thai, ma_mentor)
VALUES
-- HS001: chưa có mentor
('HS001', 'TTS001', 'Trần Văn An',     'an.tran@uni.edu.vn',    '0902222001',
 'Đại học Bách Khoa HCM', 'Công nghệ thông tin', 'Backend Developer',
 '2024-10-01', '2025-01-01', 'DaDuyet', NULL),

-- HS002: đã có mentor (MENTOR01)
('HS002', 'TTS002', 'Nguyễn Thị Bình', 'binh.nguyen@uni.edu.vn','0902222002',
 'Đại học FPT',           'Kỹ thuật phần mềm',  'Frontend Developer',
 '2024-10-01', '2025-01-01', 'DangThucTap', 'MENTOR01'),

-- HS003: đang chờ duyệt
('HS003', 'TTS003', 'Phạm Văn Cường',  'cuong.pham@uni.edu.vn', '0902222003',
 'Đại học Khoa học TN HCM','Hệ thống thông tin', 'Data Analyst',
 '2024-11-01', '2025-02-01', 'ChoDuyet', NULL);
