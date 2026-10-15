import os
import sys
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
try:
    from tests.conftest import TestSessionLocal
    SessionLocal = TestSessionLocal
except Exception:
    from database.session import SessionLocal
from database.models import NguoiDung, HoSoThucTap, PhongBan, TruongDaiHoc
from security import verify_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_hrm_test_data():
    """Dọn dẹp dữ liệu test sinh ra trong quá trình kiểm thử"""
    test_prefix = "hrm_test_"
    yield
    db = SessionLocal()
    try:
        # Tìm và xóa các người dùng test
        test_users = db.query(NguoiDung).filter(NguoiDung.email.like(f"{test_prefix}%")).all()
        user_ids = [u.ma_nguoi_dung for u in test_users]
        if user_ids:
            db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung.in_(user_ids)).delete(synchronize_session=False)
            db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung.in_(user_ids)).delete(synchronize_session=False)

        # Xóa các phòng ban test
        db.query(PhongBan).filter(PhongBan.ten_phong_ban.like(f"{test_prefix}%")).delete(synchronize_session=False)
        # Xóa các trường test
        db.query(TruongDaiHoc).filter(TruongDaiHoc.ten_truong.like(f"{test_prefix}%")).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def test_sync_employees_create_new():
    """Kiểm tra tạo mới nhân viên (Mentor và HR) chưa có trong hệ thống"""
    uid = uuid.uuid4().hex[:6]
    mentor_email = f"hrm_test_mentor_{uid}@company.com"
    hr_email = f"hrm_test_hr_{uid}@company.com"
    dept_name = f"hrm_test_dept_{uid}"

    payload = {
        "source": "SAP_HRM",
        "employees": [
            {
                "email": mentor_email,
                "ho_ten": "Nguyễn Văn Mentor",
                "so_dien_thoai": f"091{int(uid, 16) % 10000000:07d}",
                "vai_tro": "Mentor",
                "ten_phong_ban": dept_name,
                "trang_thai": "HoatDong"
            },
            {
                "email": hr_email,
                "ho_ten": "Trần Thị HR",
                "so_dien_thoai": f"092{int(uid, 16) % 10000000:07d}",
                "vai_tro": "HR",
                "ten_phong_ban": dept_name,
                "trang_thai": "HoatDong"
            }
        ],
        "interns": []
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status_code"] == 200
    assert data["summary"]["total_received"] == 2
    assert data["summary"]["employees_created"] == 2
    assert data["summary"]["employees_updated"] == 0
    assert data["summary"]["failed_count"] == 0

    # Kiểm tra trong CSDL
    db = SessionLocal()
    try:
        user_m = db.query(NguoiDung).filter(NguoiDung.email == mentor_email).first()
        assert user_m is not None
        assert user_m.ho_ten == "Nguyễn Văn Mentor"
        assert user_m.vai_tro == "Mentor"
        assert verify_password("123456", user_m.mat_khau_hash)

        user_h = db.query(NguoiDung).filter(NguoiDung.email == hr_email).first()
        assert user_h is not None
        assert user_h.vai_tro == "HR"
    finally:
        db.close()


def test_sync_employees_update_existing():
    """Kiểm tra cập nhật thông tin nhân viên khi email đã tồn tại"""
    uid = uuid.uuid4().hex[:6]
    email = f"hrm_test_emp_update_{uid}@company.com"

    # 1. Thêm nhân viên ban đầu
    db = SessionLocal()
    try:
        u = NguoiDung(
            ho_ten="Tên Cũ",
            email=email,
            so_dien_thoai="0901111111",
            vai_tro="Mentor",
            trang_thai="HoatDong"
        )
        db.add(u)
        db.commit()
    finally:
        db.close()

    # 2. Gửi request đồng bộ từ HRM với thông tin mới
    payload = {
        "source": "WORKDAY",
        "employees": [
            {
                "email": email,
                "ho_ten": "Tên Mới Đã Cập Nhật",
                "so_dien_thoai": "0909999999",
                "vai_tro": "HR",
                "trang_thai": "HoatDong"
            }
        ],
        "interns": []
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["employees_created"] == 0
    assert data["summary"]["employees_updated"] == 1

    # Kiểm tra CSDL
    db = SessionLocal()
    try:
        updated = db.query(NguoiDung).filter(NguoiDung.email == email).first()
        assert updated.ho_ten == "Tên Mới Đã Cập Nhật"
        assert updated.so_dien_thoai == "0909999999"
        assert updated.vai_tro == "HR"
    finally:
        db.close()


def test_sync_interns_create_new():
    """Kiểm tra đồng bộ tạo mới sinh viên và tạo kèm hồ sơ thực tập"""
    uid = uuid.uuid4().hex[:6]
    intern_email = f"hrm_test_intern_{uid}@student.edu.vn"
    school_name = f"hrm_test_school_{uid}"

    payload = {
        "source": "HRM_PORTAL",
        "employees": [],
        "interns": [
            {
                "email": intern_email,
                "ho_ten": "Lê Văn Sinh Viên",
                "so_dien_thoai": f"093{int(uid, 16) % 10000000:07d}",
                "chuyen_nganh": "Kỹ thuật Phần mềm",
                "lop": "KTPM-K19A",
                "ten_truong": school_name,
                "trang_thai_thuc_tap": "DangThucTap",
                "trang_thai_xet_duyet": "DaDuyet"
            }
        ]
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["interns_created"] == 1
    assert data["summary"]["interns_updated"] == 0

    # Kiểm tra trong CSDL
    db = SessionLocal()
    try:
        intern_u = db.query(NguoiDung).filter(NguoiDung.email == intern_email).first()
        assert intern_u is not None
        assert intern_u.vai_tro == "ThucTapSinh"

        profile = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == intern_u.ma_nguoi_dung).first()
        assert profile is not None
        assert profile.chuyen_nganh == "Kỹ thuật Phần mềm"
        assert profile.lop == "KTPM-K19A"
        assert profile.trang_thai_thuc_tap == "DangThucTap"
    finally:
        db.close()


def test_sync_intern_with_mentor_email_resolution():
    """Kiểm tra tự động phân giải mentor_email để gán ma_mentor chính xác"""
    uid = uuid.uuid4().hex[:6]
    mentor_email = f"hrm_test_lead_mentor_{uid}@company.com"
    intern_email = f"hrm_test_guided_intern_{uid}@student.edu.vn"

    db = SessionLocal()
    try:
        mentor = NguoiDung(
            ho_ten="Mentor Trưởng",
            email=mentor_email,
            vai_tro="Mentor",
            trang_thai="HoatDong"
        )
        db.add(mentor)
        db.commit()
        db.refresh(mentor)
        mentor_id = mentor.ma_nguoi_dung
    finally:
        db.close()

    payload = {
        "employees": [],
        "interns": [
            {
                "email": intern_email,
                "ho_ten": "Sinh Viên Được Gán Mentor",
                "chuyen_nganh": "Hệ thống Thông tin",
                "mentor_email": mentor_email
            }
        ]
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200

    db = SessionLocal()
    try:
        intern_u = db.query(NguoiDung).filter(NguoiDung.email == intern_email).first()
        profile = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == intern_u.ma_nguoi_dung).first()
        assert profile.ma_mentor == mentor_id
    finally:
        db.close()


def test_sync_mixed_payload():
    """Kiểm tra đồng bộ hỗn hợp cả nhân viên và sinh viên thực tập trong một request"""
    uid = uuid.uuid4().hex[:6]
    m_email = f"hrm_test_m_{uid}@comp.com"
    i_email = f"hrm_test_i_{uid}@stud.com"

    payload = {
        "employees": [
            {"email": m_email, "ho_ten": "Mentor Hỗn Hợp", "vai_tro": "Mentor"}
        ],
        "interns": [
            {"email": i_email, "ho_ten": "Intern Hỗn Hợp", "chuyen_nganh": "CNTT"}
        ]
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["total_received"] == 2
    assert data["summary"]["employees_created"] == 1
    assert data["summary"]["interns_created"] == 1
    assert len(data["details"]) == 2


def test_sync_empty_payload():
    """Kiểm tra gửi payload rỗng không gây crash hệ thống"""
    payload = {
        "employees": [],
        "interns": []
    }
    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["total_received"] == 0
    assert data["summary"]["failed_count"] == 0


def test_sync_invalid_email_format():
    """Kiểm tra bắt lỗi 422 khi định dạng email không hợp lệ"""
    payload = {
        "employees": [
            {"email": "not-an-email", "ho_ten": "Sai Email"}
        ],
        "interns": []
    }
    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 422


def test_sync_secret_key_validation(monkeypatch):
    """Kiểm tra xác thực header X-HRM-Secret-Key"""
    secret = "test-super-secret-key-12345"
    monkeypatch.setenv("HRM_WEBHOOK_SECRET", secret)

    payload = {"employees": [], "interns": []}

    # 1. Không gửi header -> 401
    res1 = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res1.status_code == 401

    # 2. Gửi sai secret -> 401
    res2 = client.post("/api/v1/integrations/hrm/sync", json=payload, headers={"X-HRM-Secret-Key": "wrong-secret"})
    assert res2.status_code == 401

    # 3. Gửi đúng secret -> 200 OK
    res3 = client.post("/api/v1/integrations/hrm/sync", json=payload, headers={"X-HRM-Secret-Key": secret})
    assert res3.status_code == 200


def test_sync_whitespace_and_case_insensitivity():
    """Kiểm tra email viết hoa và họ tên thừa khoảng trắng được chuẩn hóa"""
    uid = uuid.uuid4().hex[:6]
    raw_email = f"  HRM_TEST_CASE_{uid}@COMPANY.COM  "
    expected_email = f"hrm_test_case_{uid}@company.com"

    payload = {
        "employees": [
            {
                "email": raw_email,
                "ho_ten": "  Nguyễn   Văn   Chuẩn   Hóa  ",
                "vai_tro": "Mentor"
            }
        ],
        "interns": []
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["employees_created"] == 1

    db = SessionLocal()
    try:
        user = db.query(NguoiDung).filter(NguoiDung.email == expected_email).first()
        assert user is not None
        assert user.ho_ten == "Nguyễn   Văn   Chuẩn   Hóa"
    finally:
        db.close()


def test_sync_intern_update_existing_profile():
    """Kiểm tra cập nhật hồ sơ thực tập khi sinh viên và hồ sơ đã có sẵn trong CSDL"""
    uid = uuid.uuid4().hex[:6]
    intern_email = f"hrm_test_existing_profile_{uid}@student.edu.vn"

    db = SessionLocal()
    try:
        u = NguoiDung(
            ho_ten="Sinh Viên Đã Có Hồ Sơ",
            email=intern_email,
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add(u)
        db.commit()
        db.refresh(u)

        hs = HoSoThucTap(
            ma_nguoi_dung=u.ma_nguoi_dung,
            chuyen_nganh="Ngành Cũ",
            lop="Lớp Cũ",
            trang_thai_thuc_tap="DangThucTap",
            trang_thai_xet_duyet="ChoDuyet"
        )
        db.add(hs)
        db.commit()
    finally:
        db.close()

    payload = {
        "employees": [],
        "interns": [
            {
                "email": intern_email,
                "ho_ten": "Sinh Viên Đã Có Hồ Sơ",
                "chuyen_nganh": "Ngành Mới Cập Nhật",
                "lop": "Lớp Mới Cập Nhật",
                "trang_thai_thuc_tap": "HoanThanh",
                "trang_thai_xet_duyet": "DaDuyet"
            }
        ]
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["interns_created"] == 0
    assert data["summary"]["interns_updated"] == 1

    db = SessionLocal()
    try:
        u = db.query(NguoiDung).filter(NguoiDung.email == intern_email).first()
        hs = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == u.ma_nguoi_dung).first()
        assert hs.chuyen_nganh == "Ngành Mới Cập Nhật"
        assert hs.lop == "Lớp Mới Cập Nhật"
        assert hs.trang_thai_thuc_tap == "HoanThanh"
        assert hs.trang_thai_xet_duyet == "DaDuyet"
    finally:
        db.close()


def test_sync_employee_with_auto_create_department():
    """Kiểm tra tự động tạo mới phòng ban nếu tên phòng ban chưa có trong CSDL"""
    uid = uuid.uuid4().hex[:6]
    email = f"hrm_test_dept_auto_{uid}@company.com"
    dept_name = f"hrm_test_new_department_{uid}"

    payload = {
        "employees": [
            {
                "email": email,
                "ho_ten": "Nhân viên phòng mới",
                "ten_phong_ban": dept_name,
                "vai_tro": "HR"
            }
        ],
        "interns": []
    }

    res = client.post("/api/v1/integrations/hrm/sync", json=payload)
    assert res.status_code == 200

    db = SessionLocal()
    try:
        dept = db.query(PhongBan).filter(PhongBan.ten_phong_ban == dept_name).first()
        assert dept is not None
        user = db.query(NguoiDung).filter(NguoiDung.email == email).first()
        assert user.ma_phong_ban == dept.ma_phong_ban
    finally:
        db.close()

