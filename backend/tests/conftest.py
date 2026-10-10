import os
import sys
from datetime import date, datetime, time
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database.session import Base, get_db, engine as prod_engine
from database.models import (
    PhongBan,
    TruongDaiHoc,
    ChuongTrinhThucTap,
    NguoiDung,
    HoSoThucTap,
    TaiLieuHoSo,
    HopDong,
    NhiemVu,
    BaoCaoTuan,
    DanhGia,
    ChamCong,
    DonNghiPhep,
    DonXinNghi,
    CaLamViec,
    PhuCap,
    YeuCauHoTro,
)
from main import app

@pytest.fixture(autouse=True)
def setup_test_mail_env(monkeypatch):
    """Mặc định khi chạy test sẽ dùng chế độ giả lập để test chạy nhanh và không gửi mail rác"""
    if "MAIL_ENABLED" not in os.environ or os.environ.get("MAIL_ENABLED") == "true":
        monkeypatch.setenv("MAIL_ENABLED", "false")

import socket

def check_mysql() -> bool:
    """Kiểm tra MySQL port có mở hay không với timeout 0.5s"""
    host = os.getenv("DB_HOST", "localhost")
    try:
        port = int(os.getenv("DB_PORT", "3306"))
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except (OSError, ValueError):
        return False

MYSQL_AVAILABLE = check_mysql()
if MYSQL_AVAILABLE:
    try:
        Base.metadata.create_all(bind=prod_engine)
    except Exception:
        pass

# Cấu hình SQLite test engine phòng khi môi trường không có MySQL đang chạy
test_db_path = backend_dir / "test_intern_db.sqlite"
test_engine = create_engine(
    f"sqlite:///{test_db_path}",
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def reseed_sqlite_db():
    """Tạo lại bảng và nạp dữ liệu mẫu ban đầu vào SQLite để test độc lập"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    try:
        pb = PhongBan(ma_phong_ban=1, ten_phong_ban="Trung tâm Phần mềm", mo_ta="Phòng kỹ thuật & phát triển hệ thống")
        session.add(pb)

        t1 = TruongDaiHoc(ma_truong=1, ten_truong="Đại học Thái Nguyên", dia_chi="Thái Nguyên", nguoi_lien_he="Thầy Nguyễn Văn X", email_lien_he="lienhe@tnu.edu.vn")
        t2 = TruongDaiHoc(ma_truong=2, ten_truong="Đại học Bách Khoa Hà Nội", dia_chi="Hà Nội", nguoi_lien_he="Cô Trần Thị Y", email_lien_he="lienhe@hust.edu.vn")
        session.add_all([t1, t2])

        ct = ChuongTrinhThucTap(ma_chuong_trinh=1, ma_phong_ban=1, ten_chuong_trinh="Thực tập sinh Khóa Mùa Thu 2026", ngay_bat_dau=date(2026, 9, 1), ngay_ket_thuc=date(2026, 12, 30), mo_ta="Chương trình đào tạo kỹ sư phần mềm thực chiến")
        session.add(ct)

        from security import get_password_hash
        pass_hash = get_password_hash("123456")
        u1 = NguoiDung(ma_nguoi_dung=1, ma_phong_ban=1, ho_ten="Nguyễn Văn A", email="vana@example.com", mat_khau_hash=pass_hash, so_dien_thoai="0912345678", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u2 = NguoiDung(ma_nguoi_dung=2, ma_phong_ban=1, ho_ten="Trần Thị B", email="thib@example.com", mat_khau_hash=pass_hash, so_dien_thoai="0987654321", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u3 = NguoiDung(ma_nguoi_dung=3, ma_phong_ban=1, ho_ten="Nguyễn Hướng Dẫn", email="mentor@example.com", mat_khau_hash=pass_hash, so_dien_thoai="0905123456", vai_tro="Mentor", trang_thai="HoatDong")
        session.add_all([u1, u2, u3])

        hs1 = HoSoThucTap(ma_ho_so=1, ma_nguoi_dung=1, ma_truong=1, ma_chuong_trinh=1, ma_mentor=3, chuyen_nganh="Công nghệ thông tin", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="ChuaThucTap")
        hs2 = HoSoThucTap(ma_ho_so=2, ma_nguoi_dung=2, ma_truong=2, ma_chuong_trinh=1, ma_mentor=3, chuyen_nganh="Khoa học máy tính", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="DangThucTap")
        session.add_all([hs1, hs2])

        tl1 = TaiLieuHoSo(ma_tai_lieu=1, ma_ho_so=1, loai_tai_lieu="CV", duong_dan_file="uploads/cv_nguyen_van_a.pdf", trang_thai_duyet="ChoDuyet")
        tl2 = TaiLieuHoSo(ma_tai_lieu=2, ma_ho_so=1, loai_tai_lieu="DonXinThucTap", duong_dan_file="uploads/don_xin_nguyen_van_a.pdf", trang_thai_duyet="DaDuyet")
        session.add_all([tl1, tl2])

        hd1 = HopDong(ma_hop_dong=1, ma_ho_so=1, duong_dan_file="uploads/hop_dong_nguyen_van_a.pdf", ngay_tai_len=date(2026, 9, 20), ngay_ky=None, trang_thai="ChuaXacNhan")
        hd2 = HopDong(ma_hop_dong=2, ma_ho_so=2, duong_dan_file="uploads/hop_dong_tran_thi_b.pdf", ngay_tai_len=date(2026, 9, 20), ngay_ky=date(2026, 9, 25), trang_thai="DaXacNhan")
        session.add_all([hd1, hd2])

        nv1 = NhiemVu(ma_nhiem_vu=1, ma_ho_so=1, ten_nhiem_vu="Nghiên cứu kiến trúc Microservices & Docker", mo_ta="Cấu hình Docker Compose", han_hoan_thanh=date(2026, 10, 15), tien_do_phantram=30, trang_thai="Đang thực hiện")
        nv2 = NhiemVu(ma_nhiem_vu=2, ma_ho_so=1, ten_nhiem_vu="Xây dựng API quản lý lịch trình và nhiệm vụ", mo_ta="Thiết kế endpoint GET /api/v1/interns/my-schedule", han_hoan_thanh=date(2026, 10, 20), tien_do_phantram=0, trang_thai="Chưa bắt đầu")
        nv3 = NhiemVu(ma_nhiem_vu=3, ma_ho_so=2, ten_nhiem_vu="Thiết kế giao diện Dashboard quản lý", mo_ta="Cắt HTML/CSS responsive cho bảng điều khiển", han_hoan_thanh=date(2026, 10, 20), tien_do_phantram=100, trang_thai="Hoàn thành")
        session.add_all([nv1, nv2, nv3])

        bc1 = BaoCaoTuan(ma_bao_cao=1, ma_ho_so=1, ma_nhiem_vu=1, tuan_so=1, noi_dung_cong_viec="Hoàn thành Docker Compose", ket_qua_dat_duoc="Chạy thành công môi trường", thoi_gian_nop=datetime(2026, 9, 10, 17, 0))
        session.add(bc1)

        dg1 = DanhGia(ma_danh_gia=1, ma_ho_so=1, ma_nguoi_danh_gia=3, loai_danh_gia="GiuaKy", diem_ky_nang=8.5, diem_thai_do=9.0, nhan_xet_chi_tiet="Tiếp thu nhanh, hoàn thành tốt nhiệm vụ", de_xuat_tuyen_chinh_thuc=False)
        dg2 = DanhGia(ma_danh_gia=2, ma_ho_so=1, ma_nguoi_danh_gia=3, loai_danh_gia="CuoiKy", diem_ky_nang=9.0, diem_thai_do=9.5, nhan_xet_chi_tiet="Kỹ năng chuyên môn xuất sắc, trách nhiệm cao", de_xuat_tuyen_chinh_thuc=True)
        dg3 = DanhGia(ma_danh_gia=3, ma_ho_so=2, ma_nguoi_danh_gia=3, loai_danh_gia="GiuaKy", diem_ky_nang=7.5, diem_thai_do=8.0, nhan_xet_chi_tiet="Thực hiện công việc đúng tiến độ", de_xuat_tuyen_chinh_thuc=False)
        dg4 = DanhGia(ma_danh_gia=4, ma_ho_so=2, ma_nguoi_danh_gia=3, loai_danh_gia="CuoiKy", diem_ky_nang=8.0, diem_thai_do=8.5, nhan_xet_chi_tiet="Tiến bộ rõ rệt, đáp ứng tốt yêu cầu", de_xuat_tuyen_chinh_thuc=False)
        session.add_all([dg1, dg2, dg3, dg4])

        cc1 = ChamCong(ma_cham_cong=1, ma_ho_so=1, ngay_cham_cong=date(2026, 9, 2), gio_check_in=time(8, 15, 0), gio_check_out=time(17, 30, 0), phuong_thuc="Web")
        cc2 = ChamCong(ma_cham_cong=2, ma_ho_so=1, ngay_cham_cong=date(2026, 9, 3), gio_check_in=time(8, 45, 0), gio_check_out=time(17, 35, 0), phuong_thuc="Web")
        cc3 = ChamCong(ma_cham_cong=3, ma_ho_so=1, ngay_cham_cong=date(2026, 9, 4), gio_check_in=time(8, 20, 0), gio_check_out=time(17, 30, 0), phuong_thuc="QR")
        cc4 = ChamCong(ma_cham_cong=4, ma_ho_so=2, ngay_cham_cong=date(2026, 9, 2), gio_check_in=time(8, 10, 0), gio_check_out=time(17, 30, 0), phuong_thuc="Web")
        cc5 = ChamCong(ma_cham_cong=5, ma_ho_so=2, ngay_cham_cong=date(2026, 9, 3), gio_check_in=time(8, 50, 0), gio_check_out=time(17, 40, 0), phuong_thuc="The")
        session.add_all([cc1, cc2, cc3, cc4, cc5])

        dnp1 = DonNghiPhep(ma_don=1, ma_ho_so=1, ngay_nghi=date(2026, 9, 5), ly_do="Bị ốm đột xuất", trang_thai="DaDuyet")
        dnp2 = DonNghiPhep(ma_don=2, ma_ho_so=1, ngay_nghi=date(2026, 9, 12), ly_do="Việc gia đình", trang_thai="ChoDuyet")
        dnp3 = DonNghiPhep(ma_don=3, ma_ho_so=2, ngay_nghi=date(2026, 9, 8), ly_do="Thi học phần", trang_thai="DaDuyet")
        session.add_all([dnp1, dnp2, dnp3])

        clv1 = CaLamViec(ma_ca=1, ten_ca="Ca Sáng", gio_bat_dau=time(8, 0, 0), gio_ket_thuc=time(12, 0, 0), cac_ngay_trong_tuan="Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6", ghi_chu="Ca làm việc buổi sáng", trang_thai="HoatDong")
        clv2 = CaLamViec(ma_ca=2, ten_ca="Ca Chiều", gio_bat_dau=time(13, 30, 0), gio_ket_thuc=time(17, 30, 0), cac_ngay_trong_tuan="Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6", ghi_chu="Ca làm việc buổi chiều", trang_thai="HoatDong")
        clv3 = CaLamViec(ma_ca=3, ten_ca="Ca Hành Chính", gio_bat_dau=time(8, 0, 0), gio_ket_thuc=time(17, 30, 0), cac_ngay_trong_tuan="Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6", ghi_chu="Ca làm việc cả ngày", trang_thai="HoatDong")
        session.add_all([clv1, clv2, clv3])

        pc1 = PhuCap(ma_phu_cap=1, ma_ho_so=1, thang_nam="2026-09", so_tien=3000000.00, trang_thai_chi_tra="DaChiTra")
        pc2 = PhuCap(ma_phu_cap=2, ma_ho_so=1, thang_nam="2026-10", so_tien=3000000.00, trang_thai_chi_tra="DaChiTra")
        pc3 = PhuCap(ma_phu_cap=3, ma_ho_so=1, thang_nam="2026-11", so_tien=3500000.00, trang_thai_chi_tra="ChuaChiTra")
        pc4 = PhuCap(ma_phu_cap=4, ma_ho_so=2, thang_nam="2026-09", so_tien=2500000.00, trang_thai_chi_tra="DaChiTra")
        pc5 = PhuCap(ma_phu_cap=5, ma_ho_so=2, thang_nam="2026-10", so_tien=2500000.00, trang_thai_chi_tra="ChuaChiTra")
        session.add_all([pc1, pc2, pc3, pc4, pc5])

        yc1 = YeuCauHoTro(ma_yeu_cau=1, ma_ho_so=1, loai_yeu_cau="XinChungNhan", noi_dung="Em xin giấy chứng nhận thực tập để nộp về trường", phan_hoi_hr=None, trang_thai="ChoXuLy")
        yc2 = YeuCauHoTro(ma_yeu_cau=2, ma_ho_so=2, loai_yeu_cau="GiayXacNhan", noi_dung="Em xin xác nhận số giờ thực tập tháng 9", phan_hoi_hr=None, trang_thai="ChoXuLy")
        session.add_all([yc1, yc2])

        session.commit()
    finally:
        session.close()

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

reseed_sqlite_db()
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def reset_db_state():
    reseed_sqlite_db()
    yield
