 import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import date, datetime, time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.session import Base
from database.models import (
    PhongBan, TruongDaiHoc, ChuongTrinhThucTap, NguoiDung,
    HoSoThucTap, TaiLieuHoSo, HopDong, NhiemVu,
    BaoCaoTuan, DanhGia, ChamCong, DonNghiPhep, DonXinNghi
)
from security import get_password_hash

DB_PATHS = ["internship.db", "backend/internship.db"]

for db_path in DB_PATHS:
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Xóa dữ liệu cũ để nạp mới dữ liệu thật sạch
        session.query(DonXinNghi).delete()
        session.query(DonNghiPhep).delete()
        session.query(ChamCong).delete()
        session.query(DanhGia).delete()
        session.query(BaoCaoTuan).delete()
        session.query(NhiemVu).delete()
        session.query(HopDong).delete()
        session.query(TaiLieuHoSo).delete()
        session.query(HoSoThucTap).delete()
        session.query(NguoiDung).delete()
        session.query(ChuongTrinhThucTap).delete()
        session.query(TruongDaiHoc).delete()
        session.query(PhongBan).delete()
        session.commit()

        # 1. PHÒNG BAN THỰC TẾ
        pb1 = PhongBan(ma_phong_ban=1, ten_phong_ban="Trung tâm Phát triển Phần mềm ICTU", mo_ta="Nghiên cứu & phát triển các giải pháp phần mềm trường học và doanh nghiệp")
        pb2 = PhongBan(ma_phong_ban=2, ten_phong_ban="Trung tâm Dữ liệu & Trí tuệ Nhân tạo", mo_ta="Phòng thí nghiệm AI, Big Data & IoT")
        session.add_all([pb1, pb2])

        # 2. TRƯỜNG ĐẠI HỌC THỰC TẾ
        t1 = TruongDaiHoc(ma_truong=1, ten_truong="Trường Đại học Công nghệ Thông tin & Truyền thông (ICTU)", dia_chi="Đường Z115, Quyết Thắng, TP. Thái Nguyên", nguoi_lien_he="Thầy Lê Quốc Trung", email_lien_he="lqtrung@ictu.edu.vn")
        t2 = TruongDaiHoc(ma_truong=2, ten_truong="Đại học Bách Khoa Hà Nội", dia_chi="Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội", nguoi_lien_he="Cô Trần Thị Yến", email_lien_he="contact@hust.edu.vn")
        session.add_all([t1, t2])

        # 3. CHƯƠNG TRÌNH THỰC TẬP THỰC TẾ
        ct1 = ChuongTrinhThucTap(ma_chuong_trinh=1, ma_phong_ban=1, ten_chuong_trinh="Thực tập sinh Kỹ sư Phần mềm K16 - 2026", ngay_bat_dau=date(2026, 9, 1), ngay_ket_thuc=date(2026, 12, 31), mo_ta="Chương trình đào tạo thực chiến Fullstack Web & Automation Testing")
        ct2 = ChuongTrinhThucTap(ma_chuong_trinh=2, ma_phong_ban=2, ten_chuong_trinh="Thực tập sinh Trí tuệ Nhân tạo & Data Analyst", ngay_bat_dau=date(2026, 10, 1), ngay_ket_thuc=date(2027, 1, 15), mo_ta="Đào tạo Machine Learning và phân tích dữ liệu chuyên sâu")
        session.add_all([ct1, ct2])

        # 4. NGƯỜI DÙNG THẬT
        pw_hash = get_password_hash("123456")
        u1 = NguoiDung(ma_nguoi_dung=1, ma_phong_ban=1, ho_ten="Trần Quốc Huy", email="tranquochuy@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0981234567", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u2 = NguoiDung(ma_nguoi_dung=2, ma_phong_ban=1, ho_ten="Nguyễn Văn An", email="nguyenvanan@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0912345678", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u3 = NguoiDung(ma_nguoi_dung=3, ma_phong_ban=1, ho_ten="KTS. Lê Quang Hưng", email="mentor.hung@viettel.vn", mat_khau_hash=pw_hash, so_dien_thoai="0905123456", vai_tro="Mentor", trang_thai="HoatDong")
        u4 = NguoiDung(ma_nguoi_dung=4, ma_phong_ban=1, ho_ten="Ban Quản trị Thực tập HR", email="hr@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0933445566", vai_tro="NhaTruong", trang_thai="HoatDong")
        session.add_all([u1, u2, u3, u4])

        # 5. HỒ SƠ THỰC TẬP THẬT
        hs1 = HoSoThucTap(ma_ho_so=1, ma_nguoi_dung=1, ma_truong=1, ma_chuong_trinh=1, ma_mentor=3, chuyen_nganh="Kỹ thuật Phần mềm", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="DangThucTap")
        hs2 = HoSoThucTap(ma_ho_so=2, ma_nguoi_dung=2, ma_truong=1, ma_chuong_trinh=1, ma_mentor=3, chuyen_nganh="Khoa học Máy tính", trang_thai_xet_duyet="ChoDuyet", trang_thai_thuc_tap="ChuaThucTap")
        session.add_all([hs1, hs2])

        # 6. TÀI LIỆU HỒ SƠ THẬT
        tl1 = TaiLieuHoSo(ma_tai_lieu=1, ma_ho_so=1, loai_tai_lieu="CV", duong_dan_file="uploads/cv_tran_quoc_huy.pdf", trang_thai_duyet="ChoDuyet")
        tl2 = TaiLieuHoSo(ma_tai_lieu=2, ma_ho_so=1, loai_tai_lieu="DonXinThucTap", duong_dan_file="uploads/don_xin_tran_quoc_huy.pdf", trang_thai_duyet="DaDuyet")
        session.add_all([tl1, tl2])

        # 7. HỢP ĐỒNG THẬT
        hd1 = HopDong(ma_hop_dong=1, ma_ho_so=1, duong_dan_file="uploads/hop_dong_tran_quoc_huy.pdf", ngay_tai_len=date(2026, 9, 20), ngay_ky=date(2026, 9, 22), trang_thai="DaXacNhan")
        session.add(hd1)

        # 8. NHIỆM VỤ THẬT
        nv1 = NhiemVu(ma_nhiem_vu=1, ma_ho_so=1, ten_nhiem_vu="Xây dựng bộ kiểm thử tự động Automation Test", mo_ta="Viết và thực thi 8 nhóm test case theo Product Backlog", han_hoan_thanh=date(2026, 11, 15), tien_do_phantram=80, trang_thai="Đang thực hiện")
        nv2 = NhiemVu(ma_nhiem_vu=2, ma_ho_so=1, ten_nhiem_vu="Thiết kế và nộp báo cáo tiến độ tuần", mo_ta="Tổng kết kết quả thực tập tuần gửi Mentor doanh nghiệp", han_hoan_thanh=date(2026, 11, 30), tien_do_phantram=50, trang_thai="Đang thực hiện")
        session.add_all([nv1, nv2])

        # 9. BÁO CÁO TUẦN THẬT
        bc1 = BaoCaoTuan(ma_bao_cao=1, ma_ho_so=1, ma_nhiem_vu=1, tuan_so=1, noi_dung_cong_viec="Nghiên cứu kiến trúc dự án và thiết kế test suites", ket_qua_dat_duoc="Hoàn thiện cấu trúc thư mục tests và kịch bản test", phan_hoi_mentor="Tốt, cần bổ sung thêm các case biên validate")
        session.add(bc1)

        # 10. ĐÁNH GIÁ THẬT
        dg1 = DanhGia(ma_danh_gia=1, ma_ho_so=1, ma_nguoi_danh_gia=3, loai_danh_gia="GiuaKy", diem_ky_nang=9.0, diem_thai_do=9.5, nhan_xet_chi_tiet="Sinh viên nắm bắt nhanh, tư duy logic tốt, có tinh thần trách nhiệm", de_xuat_tuyen_chinh_thuc=True)
        session.add(dg1)

        # 11. CHẤM CÔNG THẬT
        cc1 = ChamCong(ma_cham_cong=1, ma_ho_so=1, ngay_cham_cong=date.today(), thoi_gian_checkin=datetime.now(), thoi_gian_checkout=None, gio_check_in=time(8, 15), gio_check_out=None, trang_thai="DungGio", phuong_thuc="Web", ghi_chu="Check-in đúng giờ tại phòng lab")
        session.add(cc1)

        # 12. ĐƠN NGHỈ PHÉP THẬT
        dn1 = DonXinNghi(ma_don=1, ma_ho_so=1, tu_ngay=date(2026, 11, 20), den_ngay=date(2026, 11, 21), ly_do="Tham gia hội nghị khoa học sinh viên trường ICTU", trang_thai="Chờ duyệt")
        session.add(dn1)

        session.commit()
        print(f"-> Nạp dữ liệu thật thành công vào {db_path}!")
    except Exception as e:
        session.rollback()
        print(f"Lỗi khi nạp dữ liệu vào {db_path}: {e}")
    finally:
        session.close()

print("HOÀN TẤT NẠP DỮ LIỆU THỰC TẾ CHO HỆ THỐNG!")
