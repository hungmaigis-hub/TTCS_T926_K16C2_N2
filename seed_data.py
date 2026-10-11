"""
Script tạo dữ liệu mẫu (Seed Data) cho hệ thống Quản lý Thực tập sinh.
Giúp Backend tự kiểm thử và ae Frontend có dữ liệu sẵn để hiển thị ngay!
Chạy lệnh: python seed_data.py
"""
from datetime import date, datetime
from app.core.database import SessionLocal, engine, Base
from app.models.mentor import Mentor
from app.models.ho_so_thuc_tap import HoSoThucTap

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Thêm Mentor mẫu nếu chưa có
        if db.query(Mentor).count() == 0:
            print(" Đang khởi tạo danh sách Mentor...")
            mentors = [
                Mentor(
                    ma_can_bo="MEN01",
                    ho_ten="Nguyễn Minh Tuấn",
                    email="tuan.nguyen@company.com",
                    so_dien_thoai="0912345678",
                    phong_ban="Phòng Kỹ thuật Phần mềm",
                    chuc_vu="Tech Lead Backend",
                    chuyen_mon="FastAPI, Python, Microservices, SQL",
                    so_luong_toi_da=5,
                    trang_thai="HoatDong"
                ),
                Mentor(
                    ma_can_bo="MEN02",
                    ho_ten="Trần Thị Thu Hà",
                    email="ha.tran@company.com",
                    so_dien_thoai="0923456789",
                    phong_ban="Phòng Phát triển Web",
                    chuc_vu="Senior Frontend Engineer",
                    chuyen_mon="ReactJS, Vue.js, TypeScript, TailwindCSS",
                    so_luong_toi_da=5,
                    trang_thai="HoatDong"
                ),
                Mentor(
                    ma_can_bo="MEN03",
                    ho_ten="Lê Hoàng Nam",
                    email="nam.le@company.com",
                    so_dien_thoai="0934567890",
                    phong_ban="Phòng Trí tuệ Nhân tạo (AI)",
                    chuc_vu="Lead AI Engineer",
                    chuyen_mon="Machine Learning, PyTorch, Big Data",
                    so_luong_toi_da=3,
                    trang_thai="HoatDong"
                ),
                Mentor(
                    ma_can_bo="MEN04",
                    ho_ten="Phạm Quốc Bảo",
                    email="bao.pham@company.com",
                    so_dien_thoai="0945678901",
                    phong_ban="Phòng Di động (Mobile)",
                    chuc_vu="Senior Mobile Dev",
                    chuyen_mon="Flutter, Android, iOS Native",
                    so_luong_toi_da=4,
                    trang_thai="HoatDong"
                ),
                Mentor(
                    ma_can_bo="MEN05",
                    ho_ten="Vũ Hải Đăng",
                    email="dang.vu@company.com",
                    so_dien_thoai="0956789012",
                    phong_ban="Phòng Đảm bảo Chất lượng (QA)",
                    chuc_vu="QA Lead",
                    chuyen_mon="Automation Test, Selenium, Performance",
                    so_luong_toi_da=2,
                    trang_thai="TamNghi"  # Mentor đang tạm nghỉ để test validation logic!
                )
            ]
            db.add_all(mentors)
            db.commit()
            print(f" Đã thêm {len(mentors)} Mentor mẫu!")

        # 2. Thêm Hồ sơ thực tập sinh mẫu nếu chưa có
        if db.query(HoSoThucTap).count() == 0:
            print(" Đang khởi tạo danh sách Hồ sơ thực tập sinh...")
            interns = [
                HoSoThucTap(
                    ma_sv="DTC245180138",
                    ho_ten="Nguyễn Văn Hiếu",
                    email="dtc245180138@ictu.edu.vn",
                    so_dien_thoai="0988776655",
                    truong_hoc="Đại học Công nghệ Thông tin & Truyền thông (ICTU)",
                    chuyen_nganh="Kỹ thuật phần mềm",
                    ma_mentor=None,  # Chưa phân công mentor - sẵn sàng để test PATCH assign-mentor!
                    trang_thai="DangThucTap",
                    ngay_bat_dau=date(2026, 9, 1),
                    ngay_ket_thuc=date(2026, 12, 31),
                    ghi_chu_phan_cong=None
                ),
                HoSoThucTap(
                    ma_sv="DTC245180139",
                    ho_ten="Phùng Văn Thắng",
                    email="thang.pv@ictu.edu.vn",
                    so_dien_thoai="0977665544",
                    truong_hoc="Đại học Công nghệ Thông tin & Truyền thông (ICTU)",
                    chuyen_nganh="Khoa học máy tính",
                    ma_mentor=None,  # Chưa phân công
                    trang_thai="DangThucTap",
                    ngay_bat_dau=date(2026, 9, 1),
                    ngay_ket_thuc=date(2026, 12, 31)
                ),
                HoSoThucTap(
                    ma_sv="DTC245180140",
                    ho_ten="Nguyễn Tuấn Linh",
                    email="linh.nt@ictu.edu.vn",
                    so_dien_thoai="0966554433",
                    truong_hoc="Đại học Công nghệ Thông tin & Truyền thông (ICTU)",
                    chuyen_nganh="Kỹ thuật phần mềm",
                    ma_mentor=1,  # Đã phân công mentor 1 (Anh Tuấn)
                    ngay_gan_mentor=datetime(2026, 9, 5, 8, 30),
                    ghi_chu_phan_cong="Hướng dẫn dự án Quản lý nhân sự",
                    trang_thai="DangThucTap",
                    ngay_bat_dau=date(2026, 9, 1),
                    ngay_ket_thuc=date(2026, 12, 31)
                ),
                HoSoThucTap(
                    ma_sv="BK2026001",
                    ho_ten="Hà Tiến Đạt",
                    email="dat.ht@hust.edu.vn",
                    so_dien_thoai="0955443322",
                    truong_hoc="Đại học Bách Khoa Hà Nội",
                    chuyen_nganh="Hệ thống thông tin",
                    ma_mentor=2,  # Đã phân công mentor 2 (Chị Hà)
                    ngay_gan_mentor=datetime(2026, 9, 6, 9, 0),
                    ghi_chu_phan_cong="Phát triển giao diện Dashboard",
                    trang_thai="DangThucTap",
                    ngay_bat_dau=date(2026, 9, 1),
                    ngay_ket_thuc=date(2026, 12, 31)
                ),
                HoSoThucTap(
                    ma_sv="UET202602",
                    ho_ten="Trần Phương Thảo",
                    email="thao.tp@vnu.edu.vn",
                    so_dien_thoai="0944332211",
                    truong_hoc="Đại học Công nghệ - ĐHQGHN",
                    chuyen_nganh="Công nghệ thông tin",
                    ma_mentor=None,
                    trang_thai="MoiTiepNhan",
                    ngay_bat_dau=date(2026, 9, 15),
                    ngay_ket_thuc=date(2026, 12, 31)
                ),
                HoSoThucTap(
                    ma_sv="PTIT202605",
                    ho_ten="Hoàng Minh Đức",
                    email="duc.hm@ptit.edu.vn",
                    so_dien_thoai="0933221100",
                    truong_hoc="Học viện Công nghệ Bưu chính Viễn thông",
                    chuyen_nganh="Mạng máy tính",
                    ma_mentor=None,
                    trang_thai="DangThucTap",
                    ngay_bat_dau=date(2026, 9, 1),
                    ngay_ket_thuc=date(2026, 12, 31)
                )
            ]
            db.add_all(interns)
            db.commit()
            print(f" Đã thêm {len(interns)} Hồ sơ thực tập sinh mẫu!")

        print(" Khởi tạo dữ liệu mẫu thành công!")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi khởi tạo dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
