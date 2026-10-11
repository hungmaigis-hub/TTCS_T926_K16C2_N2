import uuid
import pytest
from fastapi.testclient import TestClient

from main import app
from security import verify_password
from tests.conftest import TestSessionLocal
from database.models import NguoiDung

client = TestClient(app)


def test_create_mentor_success_full():
    uid = uuid.uuid4().hex[:6]
    test_email = f"mentor_{uid}@example.com"
    test_phone = f"093{int(uid, 16) % 10000000:07d}"

    payload = {
        "ho_ten": "Trần Hướng Dẫn",
        "email": test_email,
        "mat_khau": "MatKhau123",
        "so_dien_thoai": test_phone,
        "ma_phong_ban": 1
    }

    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["status_code"] == 201
    assert body["message"] == "Tạo tài khoản người hướng dẫn thành công"

    data = body["data"]
    assert data["ho_ten"] == "Trần Hướng Dẫn"
    assert data["email"] == test_email
    assert data["so_dien_thoai"] == test_phone
    assert data["ma_phong_ban"] == 1
    assert data["ten_phong_ban"] == "Trung tâm Phần mềm"
    assert data["vai_tro"] == "Mentor"
    assert data["trang_thai"] == "HoatDong"
    assert "mat_khau_hash" not in data


def test_create_mentor_success_minimal():
    uid = uuid.uuid4().hex[:6]
    test_email = f"mentor_min_{uid}@example.com"

    payload = {
        "ho_ten": "Hoàng Văn Mentor",
        "email": test_email,
        "mat_khau": "Secret123456"
    }

    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 201

    data = response.json()["data"]
    assert data["email"] == test_email
    assert data["so_dien_thoai"] is None
    assert data["ma_phong_ban"] is None
    assert data["ten_phong_ban"] is None
    assert data["vai_tro"] == "Mentor"


def test_create_mentor_password_hashed_and_login():
    uid = uuid.uuid4().hex[:6]
    test_email = f"mentor_auth_{uid}@example.com"
    plain_password = "SecurePassword2026"

    payload = {
        "ho_ten": "Lê Văn Hướng Dẫn",
        "email": test_email,
        "mat_khau": plain_password,
        "ma_phong_ban": 1
    }

    create_res = client.post("/api/v1/mentors", json=payload)
    assert create_res.status_code == 201
    mentor_id = create_res.json()["data"]["ma_nguoi_dung"]

    # Kiểm tra trực tiếp bản ghi trong database
    db = TestSessionLocal()
    try:
        user = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == mentor_id).first()
        assert user is not None
        assert user.mat_khau_hash != plain_password
        assert verify_password(plain_password, user.mat_khau_hash) is True
    finally:
        db.close()

    # Thử đăng nhập qua endpoint /api/v1/auth/login
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "mat_khau": plain_password
    })
    assert login_res.status_code == 200
    assert login_res.json()["data"]["vai_tro"] == "Mentor"


def test_create_mentor_duplicate_email():
    payload = {
        "ho_ten": "Nguyễn Trùng Email",
        "email": "mentor@example.com",
        "mat_khau": "MatKhau123"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 400
    assert "Email này đã được sử dụng" in response.json()["detail"]


def test_create_mentor_duplicate_phone():
    uid = uuid.uuid4().hex[:6]
    payload = {
        "ho_ten": "Nguyễn Trùng SĐT",
        "email": f"unique_{uid}@example.com",
        "mat_khau": "MatKhau123",
        "so_dien_thoai": "0905123456"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 400
    assert "Số điện thoại này đã được sử dụng" in response.json()["detail"]


def test_create_mentor_invalid_department():
    uid = uuid.uuid4().hex[:6]
    payload = {
        "ho_ten": "Nguyễn Văn Sai Phòng",
        "email": f"dept_{uid}@example.com",
        "mat_khau": "MatKhau123",
        "ma_phong_ban": 99999
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 400
    assert "Mã phòng ban không tồn tại" in response.json()["detail"]


def test_create_mentor_validation_empty_name():
    payload = {
        "ho_ten": "   ",
        "email": "test@example.com",
        "mat_khau": "MatKhau123"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 422


def test_create_mentor_validation_invalid_name():
    payload = {
        "ho_ten": "Mentor 123@",
        "email": "test@example.com",
        "mat_khau": "MatKhau123"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 422


def test_create_mentor_validation_invalid_email():
    payload = {
        "ho_ten": "Mentor Test",
        "email": "invalid-email-format",
        "mat_khau": "MatKhau123"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 422


def test_create_mentor_validation_short_password():
    payload = {
        "ho_ten": "Mentor Test",
        "email": "test@example.com",
        "mat_khau": "12345"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 422


def test_create_mentor_validation_invalid_phone():
    payload = {
        "ho_ten": "Mentor Test",
        "email": "test@example.com",
        "mat_khau": "MatKhau123",
        "so_dien_thoai": "012345"
    }
    response = client.post("/api/v1/mentors", json=payload)
    assert response.status_code == 422
