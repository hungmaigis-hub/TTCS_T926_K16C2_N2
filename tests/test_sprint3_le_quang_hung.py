"""
=============================================================
AUTOMATION TEST - SPRINT 3 - LÊ QUANG HƯNG
=============================================================
Bao gồm các Test Key tương ứng với nhiệm vụ Tester trên Backlog:
  - TC-27: Thực tập sinh gửi yêu cầu hỗ trợ
           + Gửi yêu cầu đầy đủ thông tin hợp lệ (201 Created)
           + Bắt lỗi khi bỏ trống tiêu đề hoặc nội dung (422)
           + Bắt lỗi mã hồ sơ sinh viên không tồn tại trong hệ thống (404)
  - TC-08: HR gán Mentor cho thực tập sinh
           + Gán mentor thành công cho sinh viên (200 OK)
           + Kiểm tra đổi sang mentor khác (200 OK)
           + Bắt lỗi khi mã mentor không tồn tại trong hệ thống (404)
           + Bắt lỗi khi gán người dùng không có vai trò Mentor (400/422)
  - TC-35: HR xem tỷ lệ hoàn thành chương trình thực tập
           + Kiểm tra độ chính xác công thức: (hoan_thanh / tong_so) * 100
           + Kiểm tra xử lý an toàn không bị lỗi chia cho 0 khi DB chưa có sinh viên (200 OK)

Cách chạy kiểm thử:
  pytest tests/test_sprint3_le_quang_hung.py -v
=============================================================
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.nguoi_dung import NguoiDung
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.models.yeu_cau_ho_tro import YeuCauHoTro

# SQLite in-memory test database cho Sprint 3
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sprint3.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
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
    """Tạo bảng và dữ liệu mẫu trước mỗi test case, dọn dẹp sau khi chạy."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()
    try:
        # Seed Người dùng
        users = [
            NguoiDung(
                ma_nguoi_dung="HR01",
                ho_ten="Nguyễn Thị Hoa",
                email="hoa@company.com",
                mat_khau_hash="hash_hr01",
                so_dien_thoai="0900000001",
                vai_tro="HR",
                kich_hoat=True,
            ),
            NguoiDung(
                ma_nguoi_dung="MENTOR01",
                ho_ten="Lê Văn Phúc",
                email="phuc@company.com",
                mat_khau_hash="hash_m01",
                so_dien_thoai="0901111001",
                vai_tro="Mentor",
                kich_hoat=True,
            ),
            NguoiDung(
                ma_nguoi_dung="MENTOR02",
                ho_ten="Nguyễn Thị Lan",
                email="lan@company.com",
                mat_khau_hash="hash_m02",
                so_dien_thoai="0901111002",
                vai_tro="Mentor",
                kich_hoat=True,
            ),
            NguoiDung(
                ma_nguoi_dung="MENTOR_INACTIVE",
                ho_ten="Vũ Thanh Tùng",
                email="tung@company.com",
                mat_khau_hash="hash_inactive",
                so_dien_thoai="0901111003",
                vai_tro="Mentor",
                kich_hoat=False,
            ),
            NguoiDung(
                ma_nguoi_dung="TTS001",
                ho_ten="Trần Văn An",
                email="an@uni.edu.vn",
                mat_khau_hash="hash_tts001",
                so_dien_thoai="0902222001",
                vai_tro="ThucTapSinh",
                kich_hoat=True,
            ),
        ]
        db.add_all(users)
        db.flush()

        # Seed Hồ sơ thực tập sinh mẫu
        ho_sos = [
            HoSoThucTap(
                ma_ho_so="HS001",
                ma_sinh_vien="TTS001",
                ho_ten="Trần Văn An",
                email="an@uni.edu.vn",
                vi_tri_thuc_tap="Backend Developer",
                trang_thai="DaDuyet",
                ma_mentor=None,
            ),
            HoSoThucTap(
                ma_ho_so="HS002",
                ma_sinh_vien="TTS001",
                ho_ten="Trần Văn An",
                email="an@uni.edu.vn",
                vi_tri_thuc_tap="Frontend Developer",
                trang_thai="DangThucTap",
                ma_mentor="MENTOR01",
            ),
        ]
        db.add_all(ho_sos)
        db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)


# ==============================================================
# TC-27 | User Story 27
# User Story: Là thực tập sinh, tôi muốn gửi yêu cầu hỗ trợ
#             (ví dụ: chứng nhận, giấy tờ) để được giải quyết
# ==============================================================

class TestTC27_SupportRequests:

    def test_27_1_gui_yeu_cau_day_du_thong_tin_hop_le_201_created(self):
        """Gửi yêu cầu hỗ trợ với đầy đủ thông tin hợp lệ -> 201 Created"""
        payload = {
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "Xin cấp giấy xác nhận thực tập",
            "noi_dung": "Em cần xin giấy xác nhận hoàn thành thực tập để nộp về trường."
        }
        response = client.post("/api/v1/support-requests", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["ma_ho_so"] == "HS001"
        assert data["loai_yeu_cau"] == "GiayTo"
        assert data["tieu_de"] == "Xin cấp giấy xác nhận thực tập"
        assert data["trang_thai"] == "ChoXuLy"
        assert "ma_yeu_cau" in data
        assert "ngay_tao" in data

    def test_27_2_bat_loi_bo_trong_tieu_de_tra_422(self):
        """Bắt lỗi khi tiêu đề rỗng, chỉ chứa khoảng trắng hoặc thiếu trường -> 422"""
        # 1. Tiêu đề rỗng chuỗi ""
        r1 = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "",
            "noi_dung": "Nội dung hợp lệ"
        })
        assert r1.status_code == 422

        # 2. Tiêu đề chỉ toàn khoảng trắng "   "
        r2 = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "   ",
            "noi_dung": "Nội dung hợp lệ"
        })
        assert r2.status_code == 422

        # 3. Thiếu hẳn trường tieu_de trong body JSON
        r3 = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "noi_dung": "Nội dung hợp lệ"
        })
        assert r3.status_code == 422

    def test_27_3_bat_loi_bo_trong_noi_dung_tra_422(self):
        """Bắt lỗi khi nội dung rỗng, chỉ chứa khoảng trắng hoặc thiếu trường -> 422"""
        # 1. Nội dung rỗng chuỗi ""
        r1 = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "Tiêu đề hợp lệ",
            "noi_dung": ""
        })
        assert r1.status_code == 422

        # 2. Nội dung chỉ toàn khoảng trắng "   "
        r2 = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "Tiêu đề hợp lệ",
            "noi_dung": "   "
        })
        assert r2.status_code == 422

        # 3. Thiếu hẳn trường noi_dung trong body JSON
        r3 = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "Tiêu đề hợp lệ"
        })
        assert r3.status_code == 422

    def test_27_4_bat_loi_ma_ho_so_khong_ton_tai_tra_404(self):
        """Bắt lỗi khi gửi mã hồ sơ sinh viên không tồn tại trong hệ thống -> 404"""
        payload = {
            "ma_ho_so": "HS_KHONG_TON_TAI_999",
            "loai_yeu_cau": "KyThuat",
            "tieu_de": "Lỗi tài khoản",
            "noi_dung": "Không thể đăng nhập vào Git nội bộ."
        }
        response = client.post("/api/v1/support-requests", json=payload)
        assert response.status_code == 404
        assert "không tồn tại" in response.json()["detail"]

    @pytest.mark.xfail(reason="BUG-04: Backend chưa validate enum và chấp nhận loai_yeu_cau rỗng (HTTP 201 thay vì 422)")
    def test_27_5_kiem_tra_chan_loai_yeu_cau_rong_hoac_ngoai_danh_muc(self):
        """Kiểm tra chặn loại yêu cầu rỗng hoặc ngoài danh mục enum -> Kỳ vọng 422 (Hiện tại lỗi: Backend trả về 201)"""
        payload = {
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "",
            "tieu_de": "Yêu cầu hỗ trợ",
            "noi_dung": "Nội dung cần hỗ trợ"
        }
        response = client.post("/api/v1/support-requests", json=payload)
        # Kỳ vọng: 422 Unprocessable Entity
        assert response.status_code == 422

    @pytest.mark.xfail(reason="BUG-05: Backend lưu trữ trực tiếp thẻ script vào DB, tiềm ẩn lỗ hổng Stored XSS")
    def test_27_6_kiem_tra_chan_ma_doc_xss_script_injection(self):
        """Kiểm tra mã độc HTML/Script Injection trong nội dung hỗ trợ -> Kỳ vọng Sanitize hoặc 400 (Hiện tại lỗi: lưu raw script)"""
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post("/api/v1/support-requests", json={
            "ma_ho_so": "HS001",
            "loai_yeu_cau": "GiayTo",
            "tieu_de": "Kiểm tra bảo mật",
            "noi_dung": xss_payload
        })
        # Backend không được lưu nguyên thẻ script độc hại vào DB
        saved_content = response.json().get("noi_dung", "")
        assert "<script>" not in saved_content


# ==============================================================
# TC-08 | User Story: Gán Mentor cho thực tập sinh
# User Story: Là HR, tôi muốn gán mentor cho thực tập sinh
#             để họ được hướng dẫn
# ==============================================================

class TestTC08_AssignMentor:

    def test_08_1_gan_mentor_thanh_cong_cho_sinh_vien_200_ok(self):
        """Gán mentor thành công cho sinh viên chưa có mentor -> 200 OK"""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mentor"]["ma_mentor"] == "MENTOR01"
        assert data["data"]["ho_so"]["ma_ho_so"] == "HS001"
        assert "ngay_cap_nhat" in data["data"]

    def test_08_2_kiem_tra_doi_sang_mentor_khac_200_ok(self):
        """Kiểm tra thay đổi sang mentor khác cho hồ sơ đã có mentor -> 200 OK"""
        response = client.patch(
            "/api/v1/interns/HS002/mentor",
            json={"ma_mentor": "MENTOR02"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mentor"]["ma_mentor"] == "MENTOR02"

    def test_08_3_bat_loi_ma_mentor_khong_ton_tai_tra_404(self):
        """Bắt lỗi khi mã mentor không tồn tại trong hệ thống -> 404 Not Found"""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR_KHONG_TON_TAI"},
        )
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "MENTOR_NOT_FOUND"

    def test_08_4_bat_loi_nguoi_dung_khong_co_vai_tro_mentor_tra_400_hoac_422(self):
        """Bắt lỗi khi gán người dùng có vai trò khác (HR, Thực tập sinh) -> 400/422"""
        # Gán tài khoản HR làm Mentor
        res_hr = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "HR01"},
        )
        assert res_hr.status_code in (400, 422)
        assert res_hr.json()["detail"]["error_code"] == "INVALID_MENTOR_ROLE"

        # Gán tài khoản Thực tập sinh làm Mentor
        res_tts = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "TTS001"},
        )
        assert res_tts.status_code in (400, 422)
        assert res_tts.json()["detail"]["error_code"] == "INVALID_MENTOR_ROLE"

    def test_08_5_bat_loi_ho_so_khong_ton_tai_tra_404(self):
        """Bắt lỗi khi mã hồ sơ sinh viên cần gán không tồn tại -> 404 Not Found"""
        response = client.patch(
            "/api/v1/interns/HS9999/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 404
        assert response.json()["detail"]["error_code"] == "INTERN_NOT_FOUND"

    def test_08_6_bat_loi_mentor_bi_vo_hieu_hoa_tra_403(self):
        """Bắt lỗi khi gán mentor đang bị vô hiệu hóa (kich_hoat = False) -> 403"""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR_INACTIVE"},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["error_code"] == "MENTOR_INACTIVE"

    def test_08_7_bat_loi_vuot_chi_tieu_5_sinh_vien_tra_400(self):
        """Bắt lỗi khi mentor đã đủ 5 sinh viên mà gán thêm sinh viên thứ 6 -> 400 Bad Request"""
        db = TestingSessionLocal()
        for i in range(10, 14):
            hs = HoSoThucTap(
                ma_ho_so=f"HS0{i}",
                ma_sinh_vien="TTS001",
                ho_ten=f"Sinh viên {i}",
                vi_tri_thuc_tap="Developer",
                trang_thai="DangThucTap",
                ma_mentor="MENTOR01",
            )
            db.add(hs)
        db.commit()
        db.close()

        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "MENTOR_QUOTA_EXCEEDED"

    @pytest.mark.xfail(reason="BUG-06: Backend vẫn cho phép gán mentor cho sinh viên có trạng thái ThoiHoc hoặc TuChoi (200 OK thay vì 400)")
    def test_08_8_chan_gan_mentor_cho_sinh_vien_da_thoi_hoc_hoac_tu_choi(self):
        """Kiểm tra chặn gán Mentor cho sinh viên có trạng thái Thôi học hoặc Bị từ chối -> Kỳ vọng 400 Bad Request (Hiện tại lỗi: trả về 200)"""
        db = TestingSessionLocal()
        hs_dropped = HoSoThucTap(
            ma_ho_so="HS_DROPOUT",
            ma_sinh_vien="TTS999",
            ho_ten="Sinh viên Thôi học",
            trang_thai="ThoiHoc",
        )
        db.add(hs_dropped)
        db.commit()
        db.close()

        response = client.patch(
            "/api/v1/interns/HS_DROPOUT/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        # Kỳ vọng: 400 Bad Request (chặn gán mentor cho sinh viên đã thôi học / từ chối)
        assert response.status_code == 400


# ==============================================================
# TC-35 | User Story: Báo cáo tỷ lệ hoàn thành thực tập
# User Story: Là HR, tôi muốn xem tỷ lệ hoàn thành chương trình
#             để đánh giá chất lượng thực tập
# ==============================================================

class TestTC35_CompletionRateReport:

    def test_35_1_xu_ly_an_toan_khong_loi_chia_cho_0_khi_db_chua_co_sinh_vien_200_ok(self):
        """Kiểm tra xử lý an toàn không bị lỗi chia cho 0 khi DB chưa có sinh viên nào -> 200 OK, tỷ lệ = 0.0%"""
        # Xóa hết hồ sơ sinh viên để kiểm tra DB rỗng
        db = TestingSessionLocal()
        db.query(HoSoThucTap).delete()
        db.commit()
        db.close()

        response = client.get("/api/v1/reports/completion-rate")
        assert response.status_code == 200
        data = response.json()
        assert data["tong_so_sinh_vien"] == 0
        assert data["so_luong_hoan_thanh"] == 0
        assert data["so_luong_dang_thuc_tap"] == 0
        assert data["so_luong_thoi_hoc"] == 0
        # Không bị crash ZeroDivisionError, trả về an toàn 0.0%
        assert data["ty_le_hoan_thanh"] == 0.0

    def test_35_2_kiem_tra_chinh_xac_cong_thuc_phan_tram_50_percent(self):
        """Kiểm tra tính đúng công thức (hoan_thanh / tong_so) * 100: (2 / 4) * 100 = 50.0%"""
        db = TestingSessionLocal()
        db.query(HoSoThucTap).delete()
        s1 = HoSoThucTap(ma_ho_so="HS101", ma_sinh_vien="SV01", ho_ten="SV A", email="a@test.com", trang_thai="HoanThanh")
        s2 = HoSoThucTap(ma_ho_so="HS102", ma_sinh_vien="SV02", ho_ten="SV B", email="b@test.com", trang_thai="HoanThanh")
        s3 = HoSoThucTap(ma_ho_so="HS103", ma_sinh_vien="SV03", ho_ten="SV C", email="c@test.com", trang_thai="DangThucTap")
        s4 = HoSoThucTap(ma_ho_so="HS104", ma_sinh_vien="SV04", ho_ten="SV D", email="d@test.com", trang_thai="ThoiHoc")
        db.add_all([s1, s2, s3, s4])
        db.commit()
        db.close()

        response = client.get("/api/v1/reports/completion-rate")
        assert response.status_code == 200
        data = response.json()
        assert data["tong_so_sinh_vien"] == 4
        assert data["so_luong_hoan_thanh"] == 2
        assert data["so_luong_dang_thuc_tap"] == 1
        assert data["so_luong_thoi_hoc"] == 1
        # Công thức: (2 / 4) * 100 = 50.0%
        assert data["ty_le_hoan_thanh"] == 50.0

    def test_35_3_kiem_tra_chinh_xac_lam_tron_2_chu_so_thap_phan(self):
        """Kiểm tra làm tròn 2 chữ số thập phân khi chia lẻ: (1 / 3) * 100 = 33.33%"""
        db = TestingSessionLocal()
        db.query(HoSoThucTap).delete()
        s1 = HoSoThucTap(ma_ho_so="HS201", ma_sinh_vien="SV01", ho_ten="SV A", email="a@test.com", trang_thai="HoanThanh")
        s2 = HoSoThucTap(ma_ho_so="HS202", ma_sinh_vien="SV02", ho_ten="SV B", email="b@test.com", trang_thai="DangThucTap")
        s3 = HoSoThucTap(ma_ho_so="HS203", ma_sinh_vien="SV03", ho_ten="SV C", email="c@test.com", trang_thai="DangThucTap")
        db.add_all([s1, s2, s3])
        db.commit()
        db.close()

        response = client.get("/api/v1/reports/completion-rate")
        assert response.status_code == 200
        data = response.json()
        assert data["tong_so_sinh_vien"] == 3
        assert data["so_luong_hoan_thanh"] == 1
        # Công thức: (1 / 3) * 100 = 33.33%
        assert data["ty_le_hoan_thanh"] == 33.33

    def test_35_4_kiem_tra_ty_le_dat_100_percent_khi_tat_ca_hoan_thanh(self):
        """Kiểm tra tỷ lệ đạt tối đa 100.0% khi tất cả sinh viên đều hoàn thành"""
        db = TestingSessionLocal()
        db.query(HoSoThucTap).delete()
        s1 = HoSoThucTap(ma_ho_so="HS301", ma_sinh_vien="SV01", ho_ten="SV A", email="a@test.com", trang_thai="HoanThanh")
        s2 = HoSoThucTap(ma_ho_so="HS302", ma_sinh_vien="SV02", ho_ten="SV B", email="b@test.com", trang_thai="HoanThanh")
        db.add_all([s1, s2])
        db.commit()
        db.close()

        response = client.get("/api/v1/reports/completion-rate")
        assert response.status_code == 200
        data = response.json()
        assert data["tong_so_sinh_vien"] == 2
        assert data["so_luong_hoan_thanh"] == 2
        # Công thức: (2 / 2) * 100 = 100.0%
        assert data["ty_le_hoan_thanh"] == 100.0
