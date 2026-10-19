# -*- coding: utf-8 -*-
"""
=============================================================
AUTOMATION TEST - SPRINT 3 - TRẦN QUỐC HUY
=============================================================
Mã sinh viên: ICTU - K16C2
Thành viên: Trần Quốc Huy

Bao gồm các Test Key tương ứng với nhiệm vụ Tester trên Backlog Sprint 3:
  - TC-26 (Dòng 6): Xem lịch sử nhận phụ cấp
           + Endpoint: GET /api/v1/interns/{id}/allowances
           + Lấy thành công danh sách phụ cấp & kiểm tra tính toán tổng tiền (200 OK)
           + Tính đúng tổng tiền đã nhận và các khoản đang chờ giải ngân
           + Trả về danh sách rỗng an toàn khi TTS chưa có phụ cấp (200 OK)
           + Bắt lỗi mã hồ sơ TTS không tồn tại (404 Not Found)
           + Bắt lỗi kiểu dữ liệu mã hồ sơ không hợp lệ (422 Unprocessable Entity)
           + Kiểm tra sắp xếp các khoản phụ cấp theo tháng giảm dần
  - TC-40 (Dòng 15): Thêm mới Mentor (Người hướng dẫn)
           + Endpoint: POST /api/v1/mentors
           + Thêm mới Mentor thành công với đầy đủ thông tin (201 Created)
           + Thêm mới Mentor thành công chỉ với các trường tối thiểu (201 Created)
           + Kiểm tra mật khẩu được hash an toàn (bcrypt) và đăng nhập thành công
           + Bắt lỗi trùng email đã tồn tại trong hệ thống (400 Bad Request)
           + Bắt lỗi trùng số điện thoại đã tồn tại (400 Bad Request)
           + Bắt lỗi mã phòng ban không tồn tại (400 Bad Request)
           + Bắt lỗi bỏ trống họ tên / họ tên chỉ khoảng trắng (422)
           + Bắt lỗi họ tên chứa số hoặc ký tự đặc biệt (422)
           + Bắt lỗi định dạng email không hợp lệ (422)
           + Bắt lỗi mật khẩu quá ngắn dưới 6 ký tự (422)
           + Bắt lỗi số điện thoại sai định dạng Việt Nam (422)
  - TC-34 (Dòng 24): Báo cáo thống kê thực tập sinh theo trường/khoa/chuyên ngành
           + Endpoint: GET /api/v1/reports/interns-by-faculty
           + Lấy báo cáo thống kê mặc định thành công (200 OK)
           + Kiểm tra tính toán chính xác tổng sinh viên và tỷ lệ phần trăm (100%)
           + Lọc theo ma_truong hợp lệ thành công (200 OK)
           + Bắt lỗi ma_truong không tồn tại trong hệ thống (404 Not Found)
           + Bắt lỗi ma_truong sai định dạng / âm / bằng 0 (422)
           + Tìm kiếm theo từ khóa ten_truong và chuyen_nganh (200 OK)
           + Lọc theo trạng thái xét duyệt và trạng thái thực tập (200 OK)
           + Bắt lỗi truyền trạng thái không hợp lệ (400 Bad Request)
           + Xử lý an toàn khi DB chưa có sinh viên nào, tránh ZeroDivisionError (200 OK)

Cách chạy kiểm thử:
  pytest tests/test_sprint3_tran_quoc_huy.py -v
=============================================================
"""

import sys
import uuid
from pathlib import Path
from datetime import date, datetime, time

# Đảm bảo import được module từ thư mục backend
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.session import Base, get_db
from database.models import (
    PhongBan,
    TruongDaiHoc,
    ChuongTrinhThucTap,
    NguoiDung,
    HoSoThucTap,
    PhuCap,
)
from main import app
from security import get_password_hash, verify_password

# Cấu hình SQLite test database độc lập cho bộ test Sprint 3 của Trần Quốc Huy
test_db_file = backend_dir / "test_sprint3_huy.sqlite"
engine_test = create_engine(
    f"sqlite:///{test_db_file}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Tạo bảng và dữ liệu mẫu chuẩn trước mỗi test case, dọn dẹp sau khi chạy."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()
    try:
        # 1. Seed Phòng ban
        pb1 = PhongBan(
            ma_phong_ban=1,
            ten_phong_ban="Trung tâm Phần mềm",
            mo_ta="Phòng phát triển hệ thống & AI"
        )
        pb2 = PhongBan(
            ma_phong_ban=2,
            ten_phong_ban="Phòng Đảm bảo Chất lượng (QA/QC)",
            mo_ta="Kiểm thử và vận hành chất lượng"
        )
        db.add_all([pb1, pb2])
        db.flush()

        # 2. Seed Trường Đại học
        t1 = TruongDaiHoc(
            ma_truong=1,
            ten_truong="Trường Đại học Công nghệ Thông tin và Truyền thông",
            dia_chi="Thái Nguyên",
            nguoi_lien_he="Thầy Nguyễn Văn X",
            email_lien_he="lienhe@ictu.edu.vn"
        )
        t2 = TruongDaiHoc(
            ma_truong=2,
            ten_truong="Đại học Bách Khoa Hà Nội",
            dia_chi="Hà Nội",
            nguoi_lien_he="Cô Trần Thị Y",
            email_lien_he="lienhe@hust.edu.vn"
        )
        t3 = TruongDaiHoc(
            ma_truong=3,
            ten_truong="Đại học Quốc Gia Hà Nội",
            dia_chi="Hà Nội",
            nguoi_lien_he="Thầy Lê Văn Z",
            email_lien_he="lienhe@vnu.edu.vn"
        )
        db.add_all([t1, t2, t3])
        db.flush()

        # 3. Seed Chương trình thực tập
        ct1 = ChuongTrinhThucTap(
            ma_chuong_trinh=1,
            ma_phong_ban=1,
            ten_chuong_trinh="Thực tập sinh Công nghệ K16 - Mùa Thu 2026",
            ngay_bat_dau=date(2026, 9, 1),
            ngay_ket_thuc=date(2026, 12, 31),
            mo_ta="Chương trình đào tạo chuyên sâu Fullstack & Automation Test"
        )
        db.add(ct1)
        db.flush()

        # 4. Seed Người dùng
        pwd_hash = get_password_hash("MatKhau@123")
        u_hr = NguoiDung(
            ma_nguoi_dung=1,
            ma_phong_ban=1,
            ho_ten="Lê Thị HR",
            email="hr@company.com",
            mat_khau_hash=pwd_hash,
            so_dien_thoai="0901234567",
            vai_tro="HR",
            trang_thai="HoatDong"
        )
        u_mentor1 = NguoiDung(
            ma_nguoi_dung=2,
            ma_phong_ban=1,
            ho_ten="Lê Quang Hưng",
            email="mentor.hung@company.com",
            mat_khau_hash=pwd_hash,
            so_dien_thoai="0905123456",
            vai_tro="Mentor",
            trang_thai="HoatDong"
        )
        u_tts1 = NguoiDung(
            ma_nguoi_dung=3,
            ma_phong_ban=1,
            ho_ten="Trần Quốc Huy",
            email="huy.tq@ictu.edu.vn",
            mat_khau_hash=pwd_hash,
            so_dien_thoai="0912345678",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        u_tts2 = NguoiDung(
            ma_nguoi_dung=4,
            ma_phong_ban=1,
            ho_ten="Nguyễn Văn A",
            email="vana@hust.edu.vn",
            mat_khau_hash=pwd_hash,
            so_dien_thoai="0987654321",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        u_tts3 = NguoiDung(
            ma_nguoi_dung=5,
            ma_phong_ban=2,
            ho_ten="Trần Thị B",
            email="thib@vnu.edu.vn",
            mat_khau_hash=pwd_hash,
            so_dien_thoai="0977112233",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        u_tts4 = NguoiDung(
            ma_nguoi_dung=6,
            ma_phong_ban=1,
            ho_ten="Hoàng Thị C",
            email="hoangc@ictu.edu.vn",
            mat_khau_hash=pwd_hash,
            so_dien_thoai="0966554433",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add_all([u_hr, u_mentor1, u_tts1, u_tts2, u_tts3, u_tts4])
        db.flush()

        # 5. Seed Hồ sơ thực tập sinh
        # HS1: Trần Quốc Huy (ICTU, Kỹ thuật phần mềm)
        hs1 = HoSoThucTap(
            ma_ho_so=1,
            ma_nguoi_dung=3,
            ma_truong=1,
            ma_chuong_trinh=1,
            ma_mentor=2,
            chuyen_nganh="Kỹ thuật phần mềm",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        # HS2: Nguyễn Văn A (HUST, Khoa học máy tính)
        hs2 = HoSoThucTap(
            ma_ho_so=2,
            ma_nguoi_dung=4,
            ma_truong=2,
            ma_chuong_trinh=1,
            ma_mentor=2,
            chuyen_nganh="Khoa học máy tính",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        # HS3: Trần Thị B (VNU, Công nghệ thông tin)
        hs3 = HoSoThucTap(
            ma_ho_so=3,
            ma_nguoi_dung=5,
            ma_truong=3,
            ma_chuong_trinh=1,
            ma_mentor=None,
            chuyen_nganh="Công nghệ thông tin",
            trang_thai_xet_duyet="ChoDuyet",
            trang_thai_thuc_tap="ChuaThucTap"
        )
        # HS4: Hoàng Thị C (ICTU, Kỹ thuật phần mềm - chưa có phụ cấp)
        hs4 = HoSoThucTap(
            ma_ho_so=4,
            ma_nguoi_dung=6,
            ma_truong=1,
            ma_chuong_trinh=1,
            ma_mentor=None,
            chuyen_nganh="Kỹ thuật phần mềm",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        db.add_all([hs1, hs2, hs3, hs4])
        db.flush()

        # 6. Seed Phụ cấp
        # HS1 (Trần Quốc Huy):
        # - Tháng 9/2026: 3.000.000 VNĐ (DaChiTra)
        # - Tháng 10/2026: 3.500.000 VNĐ (DaChiTra)
        # - Tháng 11/2026: 4.000.000 VNĐ (ChuaChiTra - chờ giải ngân)
        # Tổng đã nhận: 6.500.000, Tổng chờ giải ngân: 4.000.000, Tổng phụ cấp: 10.500.000
        pc1 = PhuCap(
            ma_phu_cap=1,
            ma_ho_so=1,
            thang=9,
            nam=2026,
            thang_nam="2026-09",
            so_tien=3000000.0,
            ngay_chi_tra=date(2026, 9, 30),
            trang_thai="DaChiTra",
            trang_thai_chi_tra="DaChiTra"
        )
        pc2 = PhuCap(
            ma_phu_cap=2,
            ma_ho_so=1,
            thang=10,
            nam=2026,
            thang_nam="2026-10",
            so_tien=3500000.0,
            ngay_chi_tra=date(2026, 10, 31),
            trang_thai="DaChiTra",
            trang_thai_chi_tra="DaChiTra"
        )
        pc3 = PhuCap(
            ma_phu_cap=3,
            ma_ho_so=1,
            thang=11,
            nam=2026,
            thang_nam="2026-11",
            so_tien=4000000.0,
            ngay_chi_tra=None,
            trang_thai="ChuaChiTra",
            trang_thai_chi_tra="ChuaChiTra"
        )

        # HS2 (Nguyễn Văn A):
        # - Tháng 9/2026: 2.500.000 VNĐ (DaChiTra)
        pc4 = PhuCap(
            ma_phu_cap=4,
            ma_ho_so=2,
            thang=9,
            nam=2026,
            thang_nam="2026-09",
            so_tien=2500000.0,
            ngay_chi_tra=date(2026, 9, 30),
            trang_thai="DaChiTra",
            trang_thai_chi_tra="DaChiTra"
        )
        db.add_all([pc1, pc2, pc3, pc4])
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)


# ==============================================================
# TC-26 | Dòng 6 (Product Backlog Sprint 3)
# User Story: Là thực tập sinh, tôi muốn xem lịch sử nhận phụ cấp
#             để theo dõi thu nhập.
# ==============================================================

class TestTC26_InternAllowances:

    def test_26_1_lay_danh_sach_phu_cap_thanh_cong_200_ok(self):
        """Lấy thành công danh sách phụ cấp của thực tập sinh (Trần Quốc Huy) -> HTTP 200 OK"""
        response = client.get("/api/v1/interns/1/allowances")
        assert response.status_code == 200

        res_body = response.json()
        assert res_body["status_code"] == 200
        assert "Lấy danh sách phụ cấp thực tập sinh thành công" in res_body["message"]
        assert "data" in res_body

        data = res_body["data"]
        assert data["ma_ho_so"] == 1
        assert data["ho_ten"] == "Trần Quốc Huy"
        assert data["email"] == "huy.tq@ictu.edu.vn"
        assert len(data["danh_sach_phu_cap"]) == 3

    def test_26_2_kiem_tra_chinh_xac_tong_tien_da_nhan_va_cho_giai_ngan(self):
        """Kiểm tra tính toán chính xác tổng tiền đã nhận và các khoản đang chờ giải ngân"""
        response = client.get("/api/v1/interns/1/allowances")
        assert response.status_code == 200

        data = response.json()["data"]
        summary = data["summary"]

        # Khoản đã nhận: 3.000.000 + 3.500.000 = 6.500.000 VNĐ (2 khoản)
        assert summary["tong_tien_da_nhan"] == 6500000.0
        assert summary["so_khoan_da_nhan"] == 2

        # Khoản chờ giải ngân: 4.000.000 VNĐ (1 khoản)
        assert summary["tong_tien_cho_giai_ngan"] == 4000000.0
        assert summary["so_khoan_cho_giai_ngan"] == 1

        # Tổng phụ cấp: 6.500.000 + 4.000.000 = 10.500.000 VNĐ
        assert summary["tong_tien_phu_cap"] == 10500000.0

        # Kiểm tra chi tiết mảng các khoản đã nhận và chờ giải ngân
        assert len(data["cac_khoan_da_nhan"]) == 2
        assert len(data["cac_khoan_cho_giai_ngan"]) == 1

    def test_26_3_tra_ve_danh_sach_rong_va_tong_tien_0_khi_tts_chua_co_phu_cap(self):
        """Kiểm tra thực tập sinh chưa có khoản phụ cấp nào trong CSDL -> 200 OK, danh sách rỗng, tổng = 0.0"""
        response = client.get("/api/v1/interns/4/allowances")
        assert response.status_code == 200

        data = response.json()["data"]
        assert data["ma_ho_so"] == 4
        assert data["ho_ten"] == "Hoàng Thị C"
        assert data["danh_sach_phu_cap"] == []
        assert data["cac_khoan_da_nhan"] == []
        assert data["cac_khoan_cho_giai_ngan"] == []

        summary = data["summary"]
        assert summary["tong_tien_da_nhan"] == 0.0
        assert summary["tong_tien_cho_giai_ngan"] == 0.0
        assert summary["tong_tien_phu_cap"] == 0.0
        assert summary["so_khoan_da_nhan"] == 0
        assert summary["so_khoan_cho_giai_ngan"] == 0

    def test_26_4_bat_loi_ma_ho_so_khong_ton_tai_tra_404_not_found(self):
        """Bắt lỗi khi mã hồ sơ thực tập sinh không tồn tại trong hệ thống -> 404 Not Found"""
        response = client.get("/api/v1/interns/99999/allowances")
        assert response.status_code == 404
        assert "Không tìm thấy thực tập sinh" in response.json()["detail"]

    def test_26_5_bat_loi_ma_ho_so_sai_dinh_dang_tra_422_unprocessable_entity(self):
        """Bắt lỗi khi mã hồ sơ truyền chuỗi ký tự thay vì số nguyên -> 422 Unprocessable Entity"""
        response = client.get("/api/v1/interns/abc_xyz/allowances")
        assert response.status_code == 422

    def test_26_6_kiem_tra_sap_xep_phu_cap_theo_thang_nam_giam_dan(self):
        """Kiểm tra các khoản phụ cấp được sắp xếp giảm dần theo thời gian (tháng gần nhất lên đầu)"""
        response = client.get("/api/v1/interns/1/allowances")
        assert response.status_code == 200

        items = response.json()["data"]["danh_sach_phu_cap"]
        thang_nams = [item["thang_nam"] for item in items]
        # Thứ tự mong đợi: 2026-11, 2026-10, 2026-09
        assert thang_nams == sorted(thang_nams, reverse=True)


# ==============================================================
# TC-40 | Dòng 15 (Product Backlog Sprint 3)
# User Story: Là HR, tôi muốn thêm mới Mentor
#             để phân công hướng dẫn thực tập sinh.
# ==============================================================

class TestTC40_CreateMentor:

    def test_40_1_them_moi_mentor_day_du_thong_tin_hop_le_201_created(self):
        """Thêm mới Mentor với đầy đủ thông tin hợp lệ -> HTTP 201 Created"""
        payload = {
            "ho_ten": "Phan Hướng Dẫn",
            "email": "phan.mentor@company.com",
            "mat_khau": "MatKhauChuan2026",
            "so_dien_thoai": "0934567890",
            "ma_phong_ban": 1
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 201

        res_body = response.json()
        assert res_body["status_code"] == 201
        assert "Tạo tài khoản người hướng dẫn thành công" in res_body["message"]

        data = res_body["data"]
        assert data["ho_ten"] == "Phan Hướng Dẫn"
        assert data["email"] == "phan.mentor@company.com"
        assert data["so_dien_thoai"] == "0934567890"
        assert data["ma_phong_ban"] == 1
        assert data["ten_phong_ban"] == "Trung tâm Phần mềm"
        assert data["vai_tro"] == "Mentor"
        assert data["trang_thai"] == "HoatDong"
        # Bảo mật: không bao giờ để lộ mật khẩu hay hash trong response
        assert "mat_khau" not in data
        assert "mat_khau_hash" not in data

    def test_40_2_them_moi_mentor_chi_truong_bat_buoc_toi_thieu_201_created(self):
        """Thêm mới Mentor chỉ với các trường bắt buộc (không có SĐT và phòng ban) -> 201 Created"""
        payload = {
            "ho_ten": "Vũ Văn Mentor",
            "email": "vu.mentor@company.com",
            "mat_khau": "MatKhau@2026"
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 201

        data = response.json()["data"]
        assert data["ho_ten"] == "Vũ Văn Mentor"
        assert data["email"] == "vu.mentor@company.com"
        assert data["so_dien_thoai"] is None
        assert data["ma_phong_ban"] is None
        assert data["ten_phong_ban"] is None
        assert data["vai_tro"] == "Mentor"

    def test_40_3_kiem_tra_mat_khau_duoc_hash_bcrypt_va_dang_nhap_thanh_cong(self):
        """Kiểm tra mật khẩu trong DB được mã hóa an toàn bcrypt và đăng nhập thành công"""
        raw_password = "MatKhauBaoMat2026"
        test_email = "mentor.auth@company.com"

        payload = {
            "ho_ten": "Hoàng Hướng Dẫn",
            "email": test_email,
            "mat_khau": raw_password,
            "ma_phong_ban": 1
        }
        create_res = client.post("/api/v1/mentors", json=payload)
        assert create_res.status_code == 201
        mentor_id = create_res.json()["data"]["ma_nguoi_dung"]

        # Kiểm tra trực tiếp trong CSDL
        db = TestingSessionLocal()
        try:
            saved_mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == mentor_id).first()
            assert saved_mentor is not None
            # Mật khẩu lưu trong DB không được trùng với plain-text
            assert saved_mentor.mat_khau_hash != raw_password
            # Verify bcrypt hash phải khớp
            assert verify_password(raw_password, saved_mentor.mat_khau_hash) is True
        finally:
            db.close()

        # Thử đăng nhập qua API xác thực
        login_res = client.post("/api/v1/auth/login", json={
            "email": test_email,
            "mat_khau": raw_password
        })
        assert login_res.status_code == 200
        assert login_res.json()["data"]["vai_tro"] == "Mentor"

    def test_40_4_bat_loi_trung_lap_email_da_ton_tai_tra_400_bad_request(self):
        """Bắt lỗi khi tạo Mentor có email đã tồn tại trong hệ thống -> 400 Bad Request"""
        # Email mentor.hung@company.com đã được seed trong fixture
        payload = {
            "ho_ten": "Người Hướng Dẫn Mới",
            "email": "mentor.hung@company.com",
            "mat_khau": "MatKhau123"
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 400
        assert "Email này đã được sử dụng" in response.json()["detail"]

    def test_40_5_bat_loi_trung_lap_so_dien_thoai_tra_400_bad_request(self):
        """Bắt lỗi khi tạo Mentor có số điện thoại đã tồn tại trong hệ thống -> 400 Bad Request"""
        # SĐT 0905123456 đã được seed cho mentor Lê Quang Hưng
        payload = {
            "ho_ten": "Người Hướng Dẫn Khác",
            "email": "mentor.unique@company.com",
            "mat_khau": "MatKhau123",
            "so_dien_thoai": "0905123456"
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 400
        assert "Số điện thoại này đã được sử dụng" in response.json()["detail"]

    def test_40_6_bat_loi_ma_phong_ban_khong_ton_tai_tra_400_bad_request(self):
        """Bắt lỗi khi chọn mã phòng ban không tồn tại trong hệ thống -> 400 Bad Request"""
        payload = {
            "ho_ten": "Người Hướng Dẫn Sai Phòng",
            "email": "mentor.sai_phong@company.com",
            "mat_khau": "MatKhau123",
            "ma_phong_ban": 99999
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 400
        assert "Mã phòng ban không tồn tại" in response.json()["detail"]

    def test_40_7_bat_loi_bo_trong_ho_ten_tra_422_unprocessable_entity(self):
        """Bắt lỗi khi họ tên rỗng, chỉ chứa khoảng trắng hoặc thiếu trường -> 422"""
        # Họ tên chỉ chứa khoảng trắng
        r1 = client.post("/api/v1/mentors", json={
            "ho_ten": "   ",
            "email": "mentor.empty_name@company.com",
            "mat_khau": "MatKhau123"
        })
        assert r1.status_code == 422

        # Thiếu hẳn trường ho_ten
        r2 = client.post("/api/v1/mentors", json={
            "email": "mentor.missing_name@company.com",
            "mat_khau": "MatKhau123"
        })
        assert r2.status_code == 422

    def test_40_8_bat_loi_ho_ten_chua_ky_tu_dac_biet_hoac_so_tra_422(self):
        """Bắt lỗi khi họ tên chứa số hoặc ký tự đặc biệt -> 422 Unprocessable Entity"""
        payload = {
            "ho_ten": "Mentor 123@#$",
            "email": "mentor.invalid_char@company.com",
            "mat_khau": "MatKhau123"
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 422

    def test_40_9_bat_loi_dinh_dang_email_sai_tra_422(self):
        """Bắt lỗi khi định dạng email không đúng chuẩn RFC -> 422 Unprocessable Entity"""
        payload = {
            "ho_ten": "Mentor Email Sai",
            "email": "khong_phai_email_hop_le",
            "mat_khau": "MatKhau123"
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 422

    def test_40_10_bat_loi_mat_khau_ngan_duoi_6_ky_tu_tra_422(self):
        """Bắt lỗi khi mật khẩu ngắn hơn 6 ký tự -> 422 Unprocessable Entity"""
        payload = {
            "ho_ten": "Mentor Mat Khau Ngan",
            "email": "mentor.short_pwd@company.com",
            "mat_khau": "12345"
        }
        response = client.post("/api/v1/mentors", json=payload)
        assert response.status_code == 422

    def test_40_11_bat_loi_so_dien_thoai_sai_dinh_dang_viet_nam_tra_422(self):
        """Bắt lỗi khi số điện thoại không đúng chuẩn 10 chữ số của Việt Nam -> 422"""
        # Số điện thoại quá ngắn
        r1 = client.post("/api/v1/mentors", json={
            "ho_ten": "Mentor SĐT Sai",
            "email": "mentor.sdt1@company.com",
            "mat_khau": "MatKhau123",
            "so_dien_thoai": "012345"
        })
        assert r1.status_code == 422

        # Số điện thoại chứa ký tự chữ cái
        r2 = client.post("/api/v1/mentors", json={
            "ho_ten": "Mentor SĐT Chữ",
            "email": "mentor.sdt2@company.com",
            "mat_khau": "MatKhau123",
            "so_dien_thoai": "0987abcdef"
        })
        assert r2.status_code == 422


# ==============================================================
# TC-34 | Dòng 24 (Product Backlog Sprint 3)
# User Story: Là HR, tôi muốn báo cáo thống kê thực tập sinh
#             theo trường/khoa/chuyên ngành để nắm bắt nguồn tuyển dụng.
# ==============================================================

class TestTC34_InternsByFacultyReport:

    def test_34_1_lay_bao_cao_thong_ke_mac_dinh_thanh_cong_200_ok(self):
        """Lấy báo cáo thống kê mặc định thành công -> HTTP 200 OK với cấu trúc chuẩn"""
        response = client.get("/api/v1/reports/interns-by-faculty")
        assert response.status_code == 200

        res_body = response.json()
        assert res_body["status_code"] == 200
        assert "Lấy báo cáo thống kê" in res_body["message"]
        assert "data" in res_body

        data = res_body["data"]
        assert "summary" in data
        assert "thong_ke_theo_truong" in data
        assert "thong_ke_theo_chuyen_nganh" in data
        assert "chi_tiet" in data

    def test_34_2_kiem_tra_tinh_toan_chinh_xac_so_luong_va_ty_le_phan_tram(self):
        """Kiểm tra độ chính xác của các chỉ số KPI summary và tỷ lệ phần trăm gom nhóm"""
        response = client.get("/api/v1/reports/interns-by-faculty")
        assert response.status_code == 200

        data = response.json()["data"]
        summary = data["summary"]

        # Tổng sinh viên = 4 (Trần Quốc Huy, Nguyễn Văn A, Trần Thị B, Hoàng Thị C)
        assert summary["tong_sinh_vien"] == 4
        # Tổng số trường = 3 (ICTU, HUST, VNU)
        assert summary["tong_so_truong"] == 3
        # Tổng số chuyên ngành = 3 (Kỹ thuật phần mềm, Khoa học máy tính, Công nghệ thông tin)
        assert summary["tong_so_chuyen_nganh"] == 3
        # Trường có nhiều sinh viên nhất: ICTU (2 sinh viên)
        assert "Công nghệ Thông tin và Truyền thông" in summary["truong_nhieu_sinh_vien_nhat"]
        # Chuyên ngành nhiều sinh viên nhất: Kỹ thuật phần mềm (2 sinh viên)
        assert summary["chuyen_nganh_nhieu_sinh_vien_nhat"] == "Kỹ thuật phần mềm"

        # Kiểm tra tổng tỷ lệ phần trăm trong chi tiết gom nhóm phải bằng 100.0%
        details = data["chi_tiet"]
        total_percent = sum(item["ty_le_phan_tram"] for item in details)
        assert round(total_percent, 1) == 100.0

    def test_34_3_loc_theo_ma_truong_hop_le_thanh_cong_200_ok(self):
        """Lọc theo ma_truong=1 (ICTU) -> chỉ trả về đúng 2 sinh viên của ICTU"""
        response = client.get("/api/v1/reports/interns-by-faculty?ma_truong=1")
        assert response.status_code == 200

        data = response.json()["data"]
        summary = data["summary"]
        assert summary["tong_sinh_vien"] == 2
        assert summary["tong_so_truong"] == 1
        assert "Công nghệ Thông tin và Truyền thông" in summary["truong_nhieu_sinh_vien_nhat"]

        by_univ = data["thong_ke_theo_truong"]
        assert len(by_univ) == 1
        assert by_univ[0]["ma_truong"] == 1
        assert by_univ[0]["tong_sinh_vien"] == 2

    def test_34_4_bat_loi_ma_truong_khong_ton_tai_tra_404_not_found(self):
        """Bắt lỗi khi truyền ma_truong không tồn tại trong hệ thống -> 404 Not Found"""
        response = client.get("/api/v1/reports/interns-by-faculty?ma_truong=99999")
        assert response.status_code == 404
        assert "Trường đại học không tồn tại" in response.json()["detail"]

    def test_34_5_bat_loi_ma_truong_am_hoac_bang_0_tra_422(self):
        """Bắt lỗi khi truyền ma_truong <= 0 hoặc sai kiểu chuỗi ký tự -> 422"""
        assert client.get("/api/v1/reports/interns-by-faculty?ma_truong=0").status_code == 422
        assert client.get("/api/v1/reports/interns-by-faculty?ma_truong=-5").status_code == 422
        assert client.get("/api/v1/reports/interns-by-faculty?ma_truong=abc").status_code == 422

    def test_34_6_tim_kiem_theo_tu_khoa_ten_truong_chinh_xac(self):
        """Kiểm tra tìm kiếm sinh viên theo từ khóa tên trường đại học"""
        # Tìm trường "Bách Khoa"
        response = client.get("/api/v1/reports/interns-by-faculty?ten_truong=Bách+Khoa")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["summary"]["tong_sinh_vien"] == 1
        assert data["thong_ke_theo_truong"][0]["ten_truong"] == "Đại học Bách Khoa Hà Nội"

        # Tìm trường không tồn tại -> trả về kết quả rỗng an toàn (200 OK)
        res_empty = client.get("/api/v1/reports/interns-by-faculty?ten_truong=Truong_Khong_Ton_Tai")
        assert res_empty.status_code == 200
        data_empty = res_empty.json()["data"]
        assert data_empty["summary"]["tong_sinh_vien"] == 0
        assert len(data_empty["thong_ke_theo_truong"]) == 0
        assert len(data_empty["chi_tiet"]) == 0

    def test_34_7_loc_theo_chuyen_nganh_chinh_xac(self):
        """Kiểm tra tìm kiếm / lọc theo chuyên ngành đào tạo"""
        # Lọc chuyên ngành "Kỹ thuật phần mềm" -> có 2 sinh viên
        response = client.get("/api/v1/reports/interns-by-faculty?chuyen_nganh=Kỹ+thuật+phần+mềm")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["summary"]["tong_sinh_vien"] == 2
        assert data["thong_ke_theo_chuyen_nganh"][0]["chuyen_nganh"] == "Kỹ thuật phần mềm"

    def test_34_8_loc_theo_trang_thai_xet_duyet_va_thuc_tap(self):
        """Kiểm tra lọc kết hợp trạng thái xét duyệt và trạng thái thực tập"""
        # Lọc trạng thái DaDuyet và DangThucTap -> 3 sinh viên (Huy, A, C)
        response = client.get("/api/v1/reports/interns-by-faculty?trang_thai_xet_duyet=DaDuyet&trang_thai_thuc_tap=DangThucTap")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["summary"]["tong_sinh_vien"] == 3

    def test_34_9_bat_loi_trang_thai_xet_duyet_khong_hop_le_tra_400(self):
        """Bắt lỗi khi truyền trạng thái xét duyệt không nằm trong danh mục hợp lệ -> 400 Bad Request"""
        response = client.get("/api/v1/reports/interns-by-faculty?trang_thai_xet_duyet=TrangThaiSai")
        assert response.status_code == 400
        assert "Trạng thái xét duyệt không hợp lệ" in response.json()["detail"]

    def test_34_10_bat_loi_trang_thai_thuc_tap_khong_hop_le_tra_400(self):
        """Bắt lỗi khi truyền trạng thái thực tập không nằm trong danh mục hợp lệ -> 400 Bad Request"""
        response = client.get("/api/v1/reports/interns-by-faculty?trang_thai_thuc_tap=TrangThaiLoi")
        assert response.status_code == 400
        assert "Trạng thái thực tập không hợp lệ" in response.json()["detail"]

    def test_34_11_xu_ly_an_toan_khong_loi_chia_cho_0_khi_db_khong_co_sinh_vien_200_ok(self):
        """Kiểm tra xử lý an toàn không bị lỗi chia cho 0 khi DB chưa có sinh viên nào -> 200 OK, tỷ lệ = 0.0%"""
        db = TestingSessionLocal()
        try:
            db.query(PhuCap).delete()
            db.query(HoSoThucTap).delete()
            db.commit()
        finally:
            db.close()

        response = client.get("/api/v1/reports/interns-by-faculty")
        assert response.status_code == 200
        data = response.json()["data"]
        summary = data["summary"]
        assert summary["tong_sinh_vien"] == 0
        assert summary["tong_so_truong"] == 0
        assert summary["tong_so_chuyen_nganh"] == 0
        assert summary["truong_nhieu_sinh_vien_nhat"] is None
        assert summary["chuyen_nganh_nhieu_sinh_vien_nhat"] is None
        assert data["thong_ke_theo_truong"] == []
        assert data["thong_ke_theo_chuyen_nganh"] == []
        assert data["chi_tiet"] == []
