import pytest
from fastapi.testclient import TestClient
from main import app
from database.session import get_db
from database.models import NguoiDung, HoSoThucTap
from security import get_password_hash

client = TestClient(app)

def test_register_intern_success():
    import uuid
    uid = uuid.uuid4().hex[:6]
    test_email = f"levantest_{uid}@example.com"
    test_phone = f"098{int(uid, 16) % 10000000:07d}"
    payload = {
        "ho_ten": "Lê Văn Test",
        "email": test_email,
        "mat_khau": "MatKhau123",
        "so_dien_thoai": test_phone,
        "chuyen_nganh": "Công nghệ thông tin",
        "ma_truong": 1
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status_code"] == 201
    assert "data" in body
    assert body["data"]["email"] == test_email
    assert body["data"]["vai_tro"] == "ThucTapSinh"
    assert body["data"]["ma_ho_so"] is not None

def test_register_duplicate_email():
    payload = {
        "ho_ten": "Trùng Email",
        "email": "vana@example.com",
        "mat_khau": "MatKhau123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "Email này đã được sử dụng" in response.json()["detail"]

def test_register_duplicate_phone():
    payload = {
        "ho_ten": "Trùng SĐT",
        "email": "trungsdt@example.com",
        "mat_khau": "MatKhau123",
        "so_dien_thoai": "0912345678"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "Số điện thoại này đã được sử dụng" in response.json()["detail"]

def test_register_short_password():
    payload = {
        "ho_ten": "Mật Khẩu Ngắn",
        "email": "mkngan@example.com",
        "mat_khau": "123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

def test_register_invalid_university():
    payload = {
        "ho_ten": "Sai Trường",
        "email": "saitruong@example.com",
        "mat_khau": "MatKhau123",
        "ma_truong": 99999
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "Mã trường đại học không tồn tại" in response.json()["detail"]

def test_login_success():
    payload = {
        "email": "vana@example.com",
        "mat_khau": "123456"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert body["data"]["email"] == "vana@example.com"
    assert body["data"]["vai_tro"] == "ThucTapSinh"

def test_login_wrong_password():
    payload = {
        "email": "vana@example.com",
        "mat_khau": "SaiMatKhau123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Mật khẩu không chính xác" in response.json()["detail"]

def test_login_nonexistent_email():
    payload = {
        "email": "khongtontai@example.com",
        "mat_khau": "MatKhau123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Tài khoản không tồn tại" in response.json()["detail"]

def test_login_student_blocked_on_mentor_portal():
    payload = {
        "email": "vana@example.com",
        "mat_khau": "123456",
        "vai_tro": "mentor"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 403
    assert "không có quyền đăng nhập vào cổng Doanh nghiệp / Mentor" in response.json()["detail"]

def test_login_student_allowed_on_student_portal():
    payload = {
        "email": "vana@example.com",
        "mat_khau": "123456",
        "vai_tro": "student"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["vai_tro"] == "ThucTapSinh"
