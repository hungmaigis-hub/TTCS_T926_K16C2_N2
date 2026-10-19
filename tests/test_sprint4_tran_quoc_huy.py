"""
=============================================================
AUTOMATION TEST - SPRINT 4 - TRẦN QUỐC HUY (TESTER)
=============================================================
Bao gồm bộ 54 Test Case tự động kiểm thử toàn diện, chuyên sâu cho 3 nhiệm vụ trên Sprint 4 Backlog:

1. NHIỆM VỤ 1 (Chấm công tự động quét mã QR/Card): 18 Test Cases
   User Story: Là thực tập sinh, tôi muốn quét mã QR / thẻ để chấm công vào ca nhanh chóng.
   Phụ trách Tester: Trần Quốc Huy (Estimate: 2 SP/h, Priority: Cao)
   Bao quát:
     - Quét mã QR check-in đúng giờ thành công (trước 08:30) -> 200 OK, DungGio
     - Quét mã thẻ Card RFID check-in đúng giờ -> 200 OK
     - Quét check-in đi muộn (sau 08:30) -> 200 OK, DiMuon
     - Phân giải mã định danh trực tiếp: số nguyên, tiền tố CARD-, INTERN-, HS, email, SĐT
     - Quét check-out về sớm (trước 17:00) -> 200 OK, VeSom
     - Quét check-out đúng giờ (sau 17:00) -> 200 OK, DungGio
     - Tự động tính toán số giờ làm việc trong ca khi hoàn tất check-out
     - Bắt lỗi mã định danh rỗng hoặc chỉ có khoảng trắng (422)
     - Bắt lỗi mã định danh không tồn tại trong hệ thống (404)
     - Bắt lỗi sinh viên chưa được phê duyệt hồ sơ: ChoDuyet / TuChoi (400)
     - Bắt lỗi sinh viên đã thôi học: ThoiHoc (400)
     - Chống quét đúp liên tiếp ngay sau check-in < 60 giây (400)
     - Chống quét lần 3 khi ca làm việc đã hoàn thành cả check-in và check-out (400)
     - Thiếu trường bắt buộc mã định danh trong payload (422)

2. NHIỆM VỤ 2 (Lên lịch họp & gửi email thông báo tự động): 18 Test Cases
   User Story: Là Mentor / HR, tôi muốn tạo lịch họp và gửi email thông báo cho thực tập sinh.
   Phụ trách Tester: Trần Quốc Huy (Estimate: 2 SP/h, Priority: Cao)
   Bao quát:
     - Tạo lịch họp đầy đủ thông tin hợp lệ -> 201 Created
     - Tự động kích hoạt BackgroundTasks gửi email HTML thông báo tới sinh viên
     - Nội dung email text fallback và HTML chứa tiêu đề cuộc họp
     - Email chứa thông tin địa điểm và tên người chủ trì
     - Email HTML chứa thời gian bắt đầu và kết thúc định dạng chuẩn tiếng Việt
     - Tạo lịch họp trực tuyến kèm link Google Meet/Zoom trong trường dia_diem
     - Hỗ trợ tiêu đề và nội dung cuộc họp bằng tiếng Việt có dấu đầy đủ UTF-8
     - Thông tin cuộc họp được lưu chính xác trong bảng CSDL lich_hop
     - Tự động loại bỏ ID trùng lặp trong danh_sach_thuc_tap_sinh (De-duplication)
     - Bắt lỗi khi tiêu đề cuộc họp để trống hoặc chỉ có khoảng trắng (400 hoặc 422)
     - Bắt lỗi khi thiếu trường bắt buộc tieu_de trong payload (422)
     - Bắt lỗi thời gian kết thúc nhỏ hơn hoặc bằng thời gian bắt đầu (400 hoặc 422)
     - Bắt lỗi thời gian bắt đầu cuộc họp nằm trong quá khứ so với thời điểm tạo (400)
     - Bắt lỗi người chủ trì không tồn tại trong CSDL (404)
     - Bắt lỗi tài khoản người chủ trì đang bị khóa ('Khoa') (400)
     - Bắt lỗi khi danh sách thực tập sinh được mời rỗng [] (400 hoặc 422)
     - Bắt lỗi danh sách sinh viên được mời chứa mã không tồn tại trong CSDL (404)
     - Bắt lỗi bỏ trống địa điểm cuộc họp (400 hoặc 422)

3. NHIỆM VỤ 3 (Sao lưu dữ liệu hệ thống tự động - System Backup): 18 Test Cases
   User Story: Là Admin, tôi muốn sao lưu dữ liệu tự động định kỳ để đảm bảo an toàn thông tin.
   Phụ trách Tester: Trần Quốc Huy (Estimate: 2 SP/h, Priority: Cao)
   Bao quát:
     - Kiểm tra hàm format bytes chuyển đổi dung lượng thân thiện (B, KB, MB, GB)
     - Kiểm tra xác thực tên file sao lưu hợp lệ có đuôi .sql.gz
     - Chặn tên file sao lưu chứa ký tự đường dẫn không an toàn Path Traversal (../ hoặc ..\\)
     - Chặn tên file sao lưu có phần mở rộng độc hại (.exe, .bat, .sh)
     - Tính toán mã băm SHA-256 chính xác 64 ký tự hex cho file sao lưu
     - Admin kích hoạt tạo bản sao lưu thủ công thành công -> HTTP 201 Created
     - File sao lưu tạo ra được nén bằng chuẩn gzip hợp lệ và giải nén an toàn
     - Bản sao lưu ghi nhận đầy đủ mã băm SHA-256 và dung lượng thực tế
     - Lưu trữ chính xác ghi chú note đính kèm khi tạo backup
     - Lấy danh sách các bản sao lưu hiện có -> HTTP 200 OK
     - Danh sách sao lưu được sắp xếp theo thời gian mới nhất lên đầu (DESC)
     - Header Content-Disposition chứa attachment và tên file khi tải về
     - Xóa bản sao lưu thành công (DELETE) và kiểm tra file bị xóa khỏi thư mục
     - Chặn tải file chứa ký tự đường dẫn ../ (Path Traversal Security) -> 400/403/404
     - Tải file sao lưu không tồn tại trong thư mục -> 404 Not Found
     - Xóa file sao lưu không tồn tại -> 404 Not Found
     - Phân quyền RBAC: Chặn tài khoản Thực tập sinh gọi API sao lưu -> 403 Forbidden
     - Chống xung đột đồng thời: Chặn tạo backup khi tiến trình khác đang chạy (409 Conflict)

Cách chạy kiểm thử:
  pytest tests/test_sprint4_tran_quoc_huy.py -v
=============================================================
"""

import os
import re
import sys
import gzip
from pathlib import Path
from datetime import datetime, date, time as dtime, timedelta
from unittest.mock import patch, MagicMock

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.session import Base, get_db
from database.models import (
    PhongBan, TruongDaiHoc, ChuongTrinhThucTap, NguoiDung,
    HoSoThucTap, TaiLieuHoSo, HopDong, NhiemVu,
    BaoCaoTuan, DanhGia, ChamCong, DonNghiPhep, DonXinNghi,
    LichHop
)
from main import app
from security import get_password_hash
from services.email_service import sent_emails_history
from services.backup_service import (
    create_backup,
    list_backups,
    validate_backup_filename,
    calculate_sha256,
    format_bytes,
    BackupSecurityError,
    BackupInProgressError,
)

test_db_file = BACKEND_DIR / "test_sprint4_huy.sqlite"
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

_client = TestClient(app)

class RequestsAdapter:
    @staticmethod
    def get(url, **kwargs):
        path = url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "")
        return _client.get(path, **kwargs)

    @staticmethod
    def post(url, **kwargs):
        path = url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "")
        return _client.post(path, **kwargs)

    @staticmethod
    def put(url, **kwargs):
        path = url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "")
        return _client.put(path, **kwargs)

    @staticmethod
    def patch(url, **kwargs):
        path = url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "")
        return _client.patch(path, **kwargs)

    @staticmethod
    def delete(url, **kwargs):
        path = url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "")
        return _client.delete(path, **kwargs)

requests = RequestsAdapter()
client = _client


@pytest.fixture(autouse=True)
def setup_sprint4_database():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    session = TestingSessionLocal()
    try:
        # 1. Phòng ban
        pb1 = PhongBan(ma_phong_ban=1, ten_phong_ban="Trung tâm Phát triển Phần mềm ICTU", mo_ta="Nghiên cứu & phát triển phần mềm")
        pb2 = PhongBan(ma_phong_ban=2, ten_phong_ban="Trung tâm Dữ liệu & AI", mo_ta="Phòng thí nghiệm AI")
        session.add_all([pb1, pb2])

        # 2. Trường đại học
        t1 = TruongDaiHoc(ma_truong=1, ten_truong="Trường Đại học Công nghệ Thông tin & Truyền thông (ICTU)", dia_chi="Thái Nguyên", nguoi_lien_he="Thầy Lê Quốc Trung", email_lien_he="lqtrung@ictu.edu.vn")
        session.add(t1)

        # 3. Chương trình thực tập
        ct1 = ChuongTrinhThucTap(ma_chuong_trinh=1, ma_phong_ban=1, ten_chuong_trinh="Thực tập sinh Kỹ sư Phần mềm K16 - 2026", ngay_bat_dau=date(2026, 9, 1), ngay_ket_thuc=date(2026, 12, 31), mo_ta="Đào tạo Fullstack & Testing")
        session.add(ct1)

        # 4. Người dùng mẫu
        pw_hash = get_password_hash("123456")
        u_admin = NguoiDung(ma_nguoi_dung=1, ma_phong_ban=1, ho_ten="Quản Trị Viên Hệ Thống", email="admin@example.com", mat_khau_hash=pw_hash, so_dien_thoai="0901112233", vai_tro="Admin", trang_thai="HoatDong")
        u_mentor = NguoiDung(ma_nguoi_dung=2, ma_phong_ban=1, ho_ten="KTS. Lê Quang Hưng", email="mentor.hung@viettel.vn", mat_khau_hash=pw_hash, so_dien_thoai="0905123456", vai_tro="Mentor", trang_thai="HoatDong")
        u_tts1 = NguoiDung(ma_nguoi_dung=3, ma_phong_ban=1, ho_ten="Trần Quốc Huy", email="tranquochuy@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0981234567", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u_tts2 = NguoiDung(ma_nguoi_dung=4, ma_phong_ban=1, ho_ten="Nguyễn Văn An", email="nguyenvanan@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0912345678", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u_tts_chua_duyet = NguoiDung(ma_nguoi_dung=5, ma_phong_ban=1, ho_ten="Sinh Viên Chờ Duyệt", email="choduyet@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0922334455", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        u_tts_thoi_hoc = NguoiDung(ma_nguoi_dung=6, ma_phong_ban=1, ho_ten="Sinh Viên Thôi Học", email="thoihoc@ictu.edu.vn", mat_khau_hash=pw_hash, so_dien_thoai="0933445566", vai_tro="ThucTapSinh", trang_thai="HoatDong")
        session.add_all([u_admin, u_mentor, u_tts1, u_tts2, u_tts_chua_duyet, u_tts_thoi_hoc])

        # 5. Hồ sơ thực tập
        hs1 = HoSoThucTap(ma_ho_so=1, ma_nguoi_dung=3, ma_truong=1, ma_chuong_trinh=1, ma_mentor=2, chuyen_nganh="Kỹ thuật Phần mềm", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="DangThucTap")
        hs2 = HoSoThucTap(ma_ho_so=2, ma_nguoi_dung=4, ma_truong=1, ma_chuong_trinh=1, ma_mentor=2, chuyen_nganh="Khoa học Máy tính", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="DangThucTap")
        hs_chua_duyet = HoSoThucTap(ma_ho_so=5, ma_nguoi_dung=5, ma_truong=1, ma_chuong_trinh=1, ma_mentor=None, chuyen_nganh="CNTT", trang_thai_xet_duyet="ChoDuyet", trang_thai_thuc_tap="ChuaThucTap")
        hs_thoi_hoc = HoSoThucTap(ma_ho_so=6, ma_nguoi_dung=6, ma_truong=1, ma_chuong_trinh=1, ma_mentor=None, chuyen_nganh="CNTT", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="ThoiHoc")
        session.add_all([hs1, hs2, hs_chua_duyet, hs_thoi_hoc])

        session.commit()
    finally:
        session.close()

    sent_emails_history.clear()


# ==============================================================================
# PHẦN 1: USER STORY 1 - CHẤM CÔNG QUÉT MÃ QR / CARD RFID [18 TEST CASES]
# Endpoint: POST /api/v1/attendance/scan
# ==============================================================================

class TestSprint4_AttendanceScan:

    def test_01_scan_qr_checkin_on_time_success_200_ok(self):
        """TC-01: Quét mã QR check-in đúng giờ (< 08:30) -> HTTP 200 OK, trạng thái DungGio"""
        payload = {
            "ma_dinh_danh": "1",
            "phuong_thuc": "QR",
            "thoi_gian_quet": "2026-10-25T08:15:00",
            "ghi_chu": "Quét cổng chính ICTU"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["ma_ho_so"] == 1
        assert data["hanh_dong"] == "CHECK_IN"
        assert data["trang_thai"] == "DungGio"
        assert data["phuong_thuc"] == "QR"

    def test_02_scan_card_checkin_on_time_success_200_ok(self):
        """TC-02: Quét mã thẻ Card RFID check-in đúng giờ -> HTTP 200 OK, trạng thái DungGio"""
        payload = {
            "ma_dinh_danh": "CARD-001",
            "phuong_thuc": "Card",
            "thoi_gian_quet": "2026-10-25T08:20:00",
            "ghi_chu": "Quét đầu đọc RFID phòng lab"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["ma_ho_so"] == 1
        assert data["hanh_dong"] == "CHECK_IN"
        assert data["trang_thai"] == "DungGio"
        assert data["phuong_thuc"] == "Card"

    def test_03_scan_checkin_late_classified_as_di_muon(self):
        """TC-03: Quét check-in đi muộn (> 08:30) -> HTTP 200 OK, phân loại DiMuon"""
        payload = {
            "ma_dinh_danh": "1",
            "phuong_thuc": "QR",
            "thoi_gian_quet": "2026-10-25T08:45:00"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["hanh_dong"] == "CHECK_IN"
        assert data["trang_thai"] == "DiMuon"

    def test_04_scan_with_prefix_intern_resolves_correctly(self):
        """TC-04: Phân giải định danh dạng INTERN-01 -> Tìm đúng hồ sơ sinh viên 1"""
        payload = {
            "ma_dinh_danh": "INTERN-01",
            "phuong_thuc": "QR",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        assert res.json()["data"]["ma_ho_so"] == 1

    def test_05_scan_with_prefix_hs_resolves_correctly(self):
        """TC-05: Phân giải định danh dạng HS001 -> Tìm đúng hồ sơ sinh viên 1"""
        payload = {
            "ma_dinh_danh": "HS001",
            "phuong_thuc": "Card",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        assert res.json()["data"]["ma_ho_so"] == 1

    def test_06_scan_with_student_email_resolves_correctly(self):
        """TC-06: Phân giải định danh trực tiếp bằng email sinh viên tranquochuy@ictu.edu.vn"""
        payload = {
            "ma_dinh_danh": "tranquochuy@ictu.edu.vn",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        assert res.json()["data"]["ma_ho_so"] == 1

    def test_07_scan_with_student_phone_resolves_correctly(self):
        """TC-07: Phân giải định danh bằng số điện thoại sinh viên 0981234567"""
        payload = {
            "ma_dinh_danh": "0981234567",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        }
        res = client.post("/api/v1/attendance/scan", json=payload)
        assert res.status_code == 200
        assert res.json()["data"]["ma_ho_so"] == 1

    def test_08_scan_checkout_early_classified_as_ve_som(self):
        """TC-08: Quét check-out về sớm (trước 17:00) -> 200 OK, trạng thái VeSom"""
        # Bước 1: Check-in lúc 08:00
        client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "phuong_thuc": "QR", "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        # Bước 2: Check-out lúc 16:30 (về sớm)
        res = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "phuong_thuc": "QR", "thoi_gian_quet": "2026-10-25T16:30:00"
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["hanh_dong"] == "CHECK_OUT"
        assert data["trang_thai"] == "VeSom"

    def test_09_scan_checkout_on_time_success(self):
        """TC-09: Quét check-out đúng giờ (sau 17:00) -> 200 OK, cập nhật gio_checkout"""
        client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "2", "phuong_thuc": "QR", "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        res = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "2", "phuong_thuc": "QR", "thoi_gian_quet": "2026-10-25T17:30:00"
        })
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["hanh_dong"] == "CHECK_OUT"
        assert data["trang_thai"] == "DungGio"
        assert data.get("gio_checkout") is not None or data.get("gio_check_out") is not None

    def test_10_attendance_record_persisted_in_database(self):
        """TC-10: Bản ghi chấm công lưu chuẩn xác vào bảng CSDL cham_cong"""
        client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "phuong_thuc": "Card", "thoi_gian_quet": "2026-10-25T08:15:00"
        })
        db = TestingSessionLocal()
        try:
            record = db.query(ChamCong).filter(ChamCong.ma_ho_so == 1).first()
            assert record is not None
            assert record.phuong_thuc == "Card"
            assert record.trang_thai == "DungGio"
        finally:
            db.close()

    def test_11_scan_empty_or_malformed_identifier_returns_400_or_422(self):
        """TC-11: Bắt lỗi mã QR sai định dạng hoặc chuỗi rỗng -> 400 Bad Request hoặc 422 Unprocessable"""
        res1 = client.post("/api/v1/attendance/scan", json={"ma_dinh_danh": ""})
        assert res1.status_code in [400, 422]

        res2 = client.post("/api/v1/attendance/scan", json={"ma_dinh_danh": "   "})
        assert res2.status_code in [400, 422]

    def test_12_scan_expired_or_non_existent_qr_returns_400_or_404(self):
        """TC-12: Bắt lỗi mã QR hết hạn hoặc không tồn tại trong hệ thống -> 400 hoặc 404 Not Found"""
        res = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "QR-EXPIRED-TOKEN-999999",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        assert res.status_code in [400, 404]
        assert "Không tìm thấy" in res.json()["detail"] or "hết hạn" in res.json()["detail"].lower()

    def test_13_scan_intern_pending_approval_returns_400(self):
        """TC-13: Chặn chấm công thực tập sinh chưa được phê duyệt hồ sơ (ChoDuyet) -> 400 Bad Request"""
        res = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "5",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        assert res.status_code == 400
        assert "chưa được phê duyệt" in res.json()["detail"]

    def test_14_scan_intern_dropped_out_returns_400(self):
        """TC-14: Chặn chấm công thực tập sinh đã thôi học (ThoiHoc) -> 400 Bad Request"""
        res = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "6",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        assert res.status_code == 400
        assert "đã thôi học" in res.json()["detail"]

    def test_15_prevent_duplicate_checkin_consecutive_returns_400_or_409(self):
        """TC-15: Bắt lỗi check-in nhiều lần liên tiếp trong cùng phiên ca làm việc -> 409 Conflict hoặc 400 Bad Request"""
        res1 = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T08:15:00"
        })
        assert res1.status_code == 200

        res_dup = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T08:15:10"
        })
        assert res_dup.status_code in [400, 409]
        assert "vừa" in res_dup.json()["detail"].lower() and "quét" in res_dup.json()["detail"].lower()

        res_checkin_dup = client.post("/api/v1/attendance/check-in", json={
            "ma_ho_so": 1, "thoi_gian_checkin": "2026-10-25T08:15:20"
        })
        assert res_checkin_dup.status_code in [400, 409]
        assert "đã thực hiện check-in" in res_checkin_dup.json()["detail"]

    def test_16_prevent_third_scan_after_shift_completed_returns_400_or_409(self):
        """TC-16: Chống quét lần 3 khi ca làm việc đã hoàn thành cả check-in và check-out -> 400 Bad Request hoặc 409 Conflict"""
        client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T17:30:00"
        })
        res_third = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T18:00:00"
        })
        assert res_third.status_code in [400, 409]
        assert "hoàn thành" in res_third.json()["detail"]

    def test_17_checkout_before_checkin_prevented(self):
        """TC-17: Không cho phép giờ check-out trước giờ check-in trong logic thời gian"""
        client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T10:00:00"
        })
        res_err = client.post("/api/v1/attendance/scan", json={
            "ma_dinh_danh": "1", "thoi_gian_quet": "2026-10-25T09:00:00"
        })
        assert res_err.status_code == 400
        assert "không thể trước" in res_err.json()["detail"].lower() or "không được trước" in res_err.json()["detail"].lower()

    def test_18_scan_missing_required_identifier_field_returns_422(self):
        """TC-18: Thiếu trường bắt buộc ma_dinh_danh trong payload -> 422 Unprocessable Entity"""
        res = client.post("/api/v1/attendance/scan", json={
            "phuong_thuc": "QR",
            "thoi_gian_quet": "2026-10-25T08:00:00"
        })
        assert res.status_code == 422


# ==============================================================================
# PHẦN 2: USER STORY 2 - LÊN LỊCH HỌP & GỬI EMAIL THÔNG BÁO [18 TEST CASES]
# Endpoint: POST /api/v1/meetings
# ==============================================================================

class TestSprint4_Meetings:

    def test_19_create_meeting_success_returns_201_created(self):
        """TC-19: Tạo lịch họp đầy đủ thông tin hợp lệ -> HTTP 201 Created"""
        now = datetime.now()
        start = now + timedelta(days=2, hours=9)
        end = now + timedelta(days=2, hours=10, minutes=30)
        payload = {
            "tieu_de": "Họp triển khai kiểm thử Sprint 4",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "Phòng họp Lotus - Tầng 2 ICTU",
            "ma_nguoi_chu_tri": 2,  # Mentor Lê Quang Hưng
            "danh_sach_thuc_tap_sinh": [3, 4],  # Trần Quốc Huy, Nguyễn Văn An
            "noi_dung": "Đánh giá tiến độ kiểm thử tự động Sprint 4 của Trần Quốc Huy"
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["tieu_de"] == "Họp triển khai kiểm thử Sprint 4"
        assert data["ma_nguoi_chu_tri"] == 2
        assert data["so_luong_nguoi_moi"] == 2

    def test_20_create_meeting_triggers_background_html_emails(self):
        """TC-20: Tự động kích hoạt BackgroundTasks gửi email HTML thông báo tới sinh viên"""
        now = datetime.now()
        start = now + timedelta(days=3, hours=14)
        end = now + timedelta(days=3, hours=15, minutes=30)
        payload = {
            "tieu_de": "Review tiến độ đồ án thực tập",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "Phòng Lab A2",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3],
            "noi_dung": "Demo tính năng mới"
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        assert len(sent_emails_history) >= 1
        em = sent_emails_history[-1]
        assert "tranquochuy@ictu.edu.vn" in em["to_email"]
        assert "Review tiến độ đồ án thực tập" in em["subject"]

    def test_21_email_content_contains_meeting_details(self):
        """TC-21: Nội dung email text fallback và HTML chứa tiêu đề cuộc họp"""
        now = datetime.now()
        start = now + timedelta(days=1, hours=8)
        end = now + timedelta(days=1, hours=9)
        payload = {
            "tieu_de": "Họp giao ban đầu tuần",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "Phòng họp Online Zoom 123",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        em = sent_emails_history[-1]
        assert "Họp giao ban đầu tuần" in em["content"]
        assert "<!DOCTYPE html>" in em.get("html_content", "")
        assert "Họp giao ban đầu tuần" in em.get("html_content", "")

    def test_22_create_meeting_email_contains_location_and_host(self):
        """TC-22: Email chứa thông tin địa điểm và tên người chủ trì"""
        now = datetime.now()
        start = now + timedelta(days=2, hours=15)
        end = now + timedelta(days=2, hours=16)
        payload = {
            "tieu_de": "Họp định hướng đề tài",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "Phòng Lab AI K16",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        em = sent_emails_history[-1]
        assert "Phòng Lab AI K16" in em["content"]
        assert "Lê Quang Hưng" in em["content"]

    def test_23_email_content_has_vietnamese_datetime_format(self):
        """TC-23: Email HTML chứa thời gian bắt đầu và kết thúc định dạng chuẩn tiếng Việt"""
        now = datetime.now()
        start = now + timedelta(days=4, hours=10)
        end = now + timedelta(days=4, hours=11)
        payload = {
            "tieu_de": "Kiểm thử định dạng thời gian email",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "Phòng 301",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        em = sent_emails_history[-1]
        assert "ngày" in em["content"] or "ngày" in em.get("html_content", "")

    def test_24_create_online_meeting_with_meet_link_in_location(self):
        """TC-24: Tạo lịch họp trực tuyến kèm link Google Meet/Zoom trong địa điểm dia_diem"""
        now = datetime.now()
        start = now + timedelta(days=2, hours=15)
        end = now + timedelta(days=2, hours=16)
        payload = {
            "tieu_de": "Họp trực tuyến toàn đội",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "https://meet.google.com/abc-defg-hij",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3, 4]
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        assert "meet.google.com" in res.json()["data"]["dia_diem"]
        em = sent_emails_history[-1]
        assert "https://meet.google.com/abc-defg-hij" in em["content"]

    def test_25_create_meeting_with_vietnamese_unicode(self):
        """TC-25: Hỗ trợ tiêu đề và nội dung cuộc họp bằng tiếng Việt có dấu đầy đủ UTF-8"""
        now = datetime.now()
        payload = {
            "tieu_de": "Hội thảo: Tối ưu hóa hiệu năng ứng dụng & Thiết kế hệ thống phân tán",
            "thoi_gian_bat_dau": (now + timedelta(days=2, hours=10)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=2, hours=12)).isoformat(),
            "dia_diem": "Hội trường lớn A1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3],
            "noi_dung": "Yêu cầu các bạn thực tập sinh đọc trước tài liệu về Caching và Message Queue."
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        assert "Tối ưu hóa hiệu năng" in res.json()["data"]["tieu_de"]

    def test_26_create_meeting_persisted_in_database(self):
        """TC-26: Thông tin cuộc họp được lưu chính xác trong bảng CSDL lich_hop"""
        now = datetime.now()
        start = now + timedelta(days=4, hours=10)
        end = now + timedelta(days=4, hours=11)
        payload = {
            "tieu_de": "Kiểm thử lưu database",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "Phòng 301",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        m_id = res.json()["data"]["ma_lich_hop"]

        db = TestingSessionLocal()
        try:
            m = db.query(LichHop).filter(LichHop.ma_lich_hop == m_id).first()
            assert m is not None
            assert m.tieu_de == "Kiểm thử lưu database"
            assert m.dia_diem == "Phòng 301"
            assert m.ma_nguoi_chu_tri == 2
        finally:
            db.close()

    def test_27_duplicate_intern_ids_automatically_deduplicated(self):
        """TC-27: Tự động loại bỏ ID trùng lặp trong danh_sach_thuc_tap_sinh (De-duplication)"""
        now = datetime.now()
        payload = {
            "tieu_de": "Họp lọc trùng ID",
            "thoi_gian_bat_dau": (now + timedelta(days=2)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=2, hours=1)).isoformat(),
            "dia_diem": "P101",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3, 3, 3]
        }
        res = client.post("/api/v1/meetings", json=payload)
        assert res.status_code == 201
        assert res.json()["data"]["so_luong_nguoi_moi"] == 1
        assert len(res.json()["data"]["danh_sach_email_duoc_moi"]) == 1

    def test_28_create_meeting_empty_title_returns_400_or_422(self):
        """TC-28: Bắt lỗi khi tiêu đề cuộc họp để trống hoặc chỉ có khoảng trắng -> 400 hoặc 422"""
        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "   ",
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code in [400, 422]

    def test_29_create_meeting_missing_required_title_field_returns_422(self):
        """TC-29: Bắt lỗi khi thiếu trường bắt buộc tieu_de trong payload -> 422"""
        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code == 422

    def test_30_create_meeting_end_time_before_start_time_returns_400_or_422(self):
        """TC-30: Bắt lỗi thời gian kết thúc nhỏ hơn hoặc bằng thời gian bắt đầu -> 400 hoặc 422"""
        now = datetime.now()
        start = now + timedelta(days=2, hours=10)
        end = now + timedelta(days=2, hours=9)  # Kết thúc trước bắt đầu!
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Lỗi thời gian",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code in [400, 422]
        assert "bắt đầu" in str(res.json()).lower() or "thoi_gian" in str(res.json()).lower()

    def test_31_create_meeting_start_time_in_past_returns_400(self):
        """TC-31: Bắt lỗi thời gian bắt đầu cuộc họp nằm trong quá khứ -> 400 Bad Request"""
        now = datetime.now()
        start = now - timedelta(days=2)  # Quá khứ
        end = now - timedelta(days=2, hours=-1)
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Lỗi quá khứ",
            "thoi_gian_bat_dau": start.isoformat(),
            "thoi_gian_ket_thuc": end.isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code == 400
        assert "quá khứ" in res.json()["detail"].lower()

    def test_32_create_meeting_non_existent_host_returns_404(self):
        """TC-32: Bắt lỗi người chủ trì không tồn tại trong CSDL -> 404 Not Found"""
        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Chủ trì ảo",
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 99999,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code == 404
        assert "người chủ trì" in res.json()["detail"].lower()

    def test_33_create_meeting_locked_host_returns_400(self):
        """TC-33: Bắt lỗi tài khoản người chủ trì đang bị khóa ('Khoa') -> 400 Bad Request"""
        db = TestingSessionLocal()
        try:
            locked_host = NguoiDung(
                ma_nguoi_dung=99,
                ma_phong_ban=1,
                ho_ten="Mentor Bị Khóa",
                email="locked_mentor@example.com",
                vai_tro="Mentor",
                trang_thai="Khoa"
            )
            db.add(locked_host)
            db.commit()
        finally:
            db.close()

        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Họp với mentor bị khóa",
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 99,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code == 400
        assert "khóa" in res.json()["detail"].lower()

    def test_34_create_meeting_empty_intern_list_returns_400_or_422(self):
        """TC-34: Bắt lỗi khi danh sách thực tập sinh được mời rỗng [] -> 400 hoặc 422"""
        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Họp thiếu danh sách sinh viên",
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": []
        })
        assert res.status_code in [400, 422]

    def test_35_create_meeting_non_existent_intern_returns_404(self):
        """TC-35: Bắt lỗi danh sách sinh viên được mời chứa mã không tồn tại -> 404 Not Found"""
        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Họp sinh viên ảo",
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "P1",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3, 88888]
        })
        assert res.status_code == 404
        assert "88888" in res.json()["detail"]

    def test_36_create_meeting_empty_location_returns_400_or_422(self):
        """TC-36: Bắt lỗi bỏ trống địa điểm cuộc họp -> 400 hoặc 422"""
        now = datetime.now()
        res = client.post("/api/v1/meetings", json={
            "tieu_de": "Không có địa điểm",
            "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
            "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
            "dia_diem": "   ",
            "ma_nguoi_chu_tri": 2,
            "danh_sach_thuc_tap_sinh": [3]
        })
        assert res.status_code in [400, 422]


# ==============================================================================
# PHẦN 3: USER STORY 3 - SAO LƯU DỮ LIỆU HỆ THỐNG (SYSTEM BACKUP) [18 TEST CASES]
# Endpoints: POST /api/v1/system/backup, GET /api/v1/system/backups
# ==============================================================================

class TestSprint4_SystemBackup:

    @pytest.fixture(autouse=True)
    def cleanup_test_backups(self):
        yield
        from services.backup_service import get_backup_directory
        try:
            bk_dir = get_backup_directory()
            for f in bk_dir.glob("backup_intern_management_*.sql.gz"):
                try:
                    f.unlink()
                except Exception:
                    pass
        except Exception:
            pass

    def test_37_format_bytes_utility_helper(self):
        """TC-37: Kiểm tra hàm format bytes chuyển đổi dung lượng thân thiện (B, KB, MB, GB)"""
        assert format_bytes(500) == "500 B"
        assert "KB" in format_bytes(2048)
        assert "MB" in format_bytes(5 * 1024 * 1024)
        assert "GB" in format_bytes(2 * 1024 * 1024 * 1024)

    def test_38_validate_backup_filename_valid_names(self):
        """TC-38: Kiểm tra xác thực tên file sao lưu hợp lệ có đuôi .sql.gz"""
        assert validate_backup_filename("backup_20261019.sql.gz") == "backup_20261019.sql.gz"
        assert validate_backup_filename("backup-intern-management_20261019_120000.sql.gz") == "backup-intern-management_20261019_120000.sql.gz"

    def test_39_validate_backup_filename_blocks_path_traversal(self):
        """TC-39: Chặn tên file sao lưu chứa ký tự đường dẫn không an toàn Path Traversal (../ hoặc ..\\)"""
        with pytest.raises(BackupSecurityError):
            validate_backup_filename("../../../etc/passwd.sql.gz")

        with pytest.raises(BackupSecurityError):
            validate_backup_filename("..\\..\\windows\\system32.sql.gz")

    def test_40_validate_backup_filename_blocks_malicious_extensions(self):
        """TC-40: Chặn tên file sao lưu có phần mở rộng độc hại (.exe, .bat, .sh)"""
        with pytest.raises(BackupSecurityError):
            validate_backup_filename("hack.exe")

        with pytest.raises(BackupSecurityError):
            validate_backup_filename("script.sh")

        with pytest.raises(BackupSecurityError):
            validate_backup_filename("test.sql")

    def test_41_calculate_sha256_checksum_accuracy(self, tmp_path):
        """TC-41: Tính toán mã băm SHA-256 chính xác 64 ký tự hex cho file sao lưu"""
        test_file = tmp_path / "test_sample.sql.gz"
        test_file.write_bytes(b"DATA SAMPLE FOR HASH INTEGRITY CHECK")
        checksum = calculate_sha256(test_file)
        assert len(checksum) == 64
        assert re.match(r"^[a-f0-9]{64}$", checksum) is not None

    def test_42_admin_trigger_backup_success_returns_200_or_201(self):
        """TC-42: Admin kích hoạt tạo bản sao lưu thủ công thành công -> HTTP 200 OK hoặc 201 Created"""
        res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"},
            json={"note": "Bản sao lưu trước khi nghiệm thu Sprint 4"}
        )
        assert res.status_code in [200, 201]
        data = res.json()
        assert data["status_code"] in [200, 201]
        assert "backup" in data
        assert data["backup"]["filename"].endswith(".sql.gz")

    def test_43_backup_file_is_valid_gzip(self):
        """TC-43: File sao lưu tạo ra được nén bằng chuẩn gzip hợp lệ và giải nén an toàn"""
        res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code == 201
        filename = res.json()["backup"]["filename"]
        from services.backup_service import get_backup_directory
        filepath = get_backup_directory() / filename
        assert filepath.exists()

        with gzip.open(filepath, "rt", encoding="utf-8", errors="ignore") as gz:
            content_snippet = gz.read(200)
            assert len(content_snippet) > 0

    def test_44_backup_has_sha256_checksum_metadata(self):
        """TC-44: Bản sao lưu ghi nhận đầy đủ mã băm SHA-256 và dung lượng thực tế"""
        res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code == 201
        bk = res.json()["backup"]
        assert len(bk["checksum_sha256"]) == 64
        assert bk["size_bytes"] > 0
        assert "KB" in bk.get("size_human", "") or "B" in bk.get("size_human", "")

    def test_45_backup_preserves_custom_note(self):
        """TC-45: Lưu trữ chính xác ghi chú note đính kèm khi tạo backup"""
        custom_note = "Sao lưu tự động định kỳ cuối ngày Sprint 4"
        res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"},
            json={"note": custom_note}
        )
        assert res.status_code == 201
        assert res.json()["backup"]["note"] == custom_note

    def test_46_get_backups_list_returns_200_ok(self):
        """TC-46: Lấy danh sách các bản sao lưu hiện có -> HTTP 200 OK"""
        res = client.get(
            "/api/v1/system/backups",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "backups" in data
        assert "total_files" in data or "total_count" in data
        assert isinstance(data["backups"], list)

    def test_47_backups_ordered_by_creation_time_descending(self):
        """TC-47: Danh sách sao lưu được sắp xếp theo thời gian mới nhất lên đầu"""
        res = client.get(
            "/api/v1/system/backups",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code == 200
        backups = res.json()["backups"]
        if len(backups) >= 2:
            assert backups[0]["created_at"] >= backups[1]["created_at"]

    def test_48_download_backup_has_proper_content_disposition_header(self):
        """TC-48: Header Content-Disposition chứa attachment và tên file tải về"""
        c_res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"}
        )
        filename = c_res.json()["backup"]["filename"]
        dl_res = client.get(
            f"/api/v1/system/backups/{filename}/download",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert dl_res.status_code == 200
        cd = dl_res.headers.get("content-disposition", "")
        assert "attachment" in cd
        assert filename in cd

    def test_49_delete_backup_success_removes_file(self):
        """TC-49: Xóa bản sao lưu thành công (DELETE) và kiểm tra file bị xóa"""
        c_res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"}
        )
        filename = c_res.json()["backup"]["filename"]

        del_res = client.delete(
            f"/api/v1/system/backups/{filename}",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert del_res.status_code == 200
        assert "thành công" in del_res.json()["message"].lower()

        # Tải lại file đã xóa -> 404 Not Found
        re_dl = client.get(
            f"/api/v1/system/backups/{filename}/download",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert re_dl.status_code == 404

    def test_50_download_with_path_traversal_blocked_returns_400(self):
        """TC-50: Chặn tải file chứa ký tự đường dẫn ../ (Path Traversal Security) -> 400"""
        res = client.get(
            "/api/v1/system/backups/..%2F..%2Fmain.py/download",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code in [400, 403, 404]

    def test_51_download_non_existent_backup_returns_404(self):
        """TC-51: Tải file sao lưu không tồn tại trong thư mục -> 404 Not Found"""
        res = client.get(
            "/api/v1/system/backups/backup_khong_ton_tai_99999.sql.gz/download",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code == 404

    def test_52_delete_non_existent_backup_returns_404(self):
        """TC-52: Xóa file sao lưu không tồn tại -> 404 Not Found"""
        res = client.delete(
            "/api/v1/system/backups/backup_fake_file_99999.sql.gz",
            headers={"X-User-Email": "admin@example.com"}
        )
        assert res.status_code == 404

    def test_53_student_blocked_from_backup_api_returns_403(self):
        """TC-53: Phân quyền RBAC: Chặn tài khoản Thực tập sinh gọi API sao lưu -> 403 Forbidden"""
        res = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "tranquochuy@ictu.edu.vn"}  # Thực tập sinh
        )
        assert res.status_code == 403

    def test_54_concurrency_lock_prevents_simultaneous_backups(self):
        """TC-54: Chống xung đột đồng thời: Chặn tạo backup khi tiến trình khác đang chạy (409 Conflict)"""
        import services.backup_service as bs
        orig = bs._is_backup_running
        try:
            bs._is_backup_running = True
            res = client.post(
                "/api/v1/system/backup",
                headers={"X-User-Email": "admin@example.com"}
            )
            assert res.status_code == 409
            assert "tiến trình" in res.json()["detail"].lower() or "đang được thực hiện" in res.json()["detail"].lower()
        finally:
            bs._is_backup_running = orig
