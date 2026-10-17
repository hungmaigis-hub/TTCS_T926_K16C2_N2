"""
Bộ Test Case tự động kiểm thử endpoint POST /api/v1/admin/users
Đáp ứng chính xác 100% 4 yêu cầu của Tester (Lê Quang Huy):
1. Gửi thông tin tài khoản người dùng mới tạo tài khoản thành công: 201 Created.
2. Gửi dữ liệu thiếu trường yêu cầu hoặc vai trò không hợp lệ: 422 Unprocessable Entity.
3. Gửi thông tin trùng lặp username/email: 400 Bad Request (hoặc 409 Conflict).
4. Tài khoản không phải là Admin thao tác: 403 Forbidden.

Phụ trách Backend: Nguyễn Văn Hiếu
Phụ trách Tester: Lê Quang Huy
"""

import pytest
from app.models.nguoi_dung import NguoiDung
from app.core.security import verify_password
from app.schemas.user import UserRole


# ==============================================================================
# TEST CASE 1: TẠO TÀI KHOẢN THÀNH CÔNG (201 CREATED) & BĂM MẬT KHẨU BẰNG BCRYPT
# ==============================================================================

def test_admin_create_user_success_201(client, admin_headers, db_session):
    """
    Kịch bản: Admin gửi payload hợp lệ tạo tài khoản mới.
    Kỳ vọng:
    - Mã phản hồi: 201 Created.
    - Dữ liệu trả về chứa thông tin người dùng mới (không lộ mật khẩu).
    - Mật khẩu trong DB được băm an toàn bằng bcrypt.
    """
    payload = {
        "ho_ten": "Nguyễn Văn Mentor",
        "email": "mentor.nguyen@ttcs.edu.vn",
        "ten_dang_nhap": "mentor_nguyen",
        "mat_khau": "MatKhauBaoMat@2026",
        "vai_tro": "Mentor"
    }

    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)

    # 1. Kiểm tra Status Code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()

    # 2. Kiểm tra các trường trả về
    assert data["ten_dang_nhap"] == "mentor_nguyen"
    assert data["email"] == "mentor.nguyen@ttcs.edu.vn"
    assert data["ho_ten"] == "Nguyễn Văn Mentor"
    assert data["vai_tro"] == "Mentor"
    assert data["trang_thai"] is True
    assert "ma_nguoi_dung" in data

    # 3. Đảm bảo an toàn thông tin: KHÔNG lộ plain password hay hashed password trong response
    assert "mat_khau" not in data
    assert "mat_khau_hash" not in data
    assert "password" not in data

    # 4. Kiểm tra trong Cơ sở dữ liệu: Mật khẩu PHẢI được băm bằng bcrypt
    user_in_db = db_session.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "mentor_nguyen").first()
    assert user_in_db is not None
    assert user_in_db.mat_khau_hash != "MatKhauBaoMat@2026"
    assert user_in_db.mat_khau_hash.startswith("$2b$") or user_in_db.mat_khau_hash.startswith("$2a$")
    assert verify_password("MatKhauBaoMat@2026", user_in_db.mat_khau_hash) is True


@pytest.mark.parametrize("role", ["Admin", "HR", "Mentor", "ThucTapSinh"])
def test_admin_create_user_all_valid_roles_201(client, admin_headers, role):
    """
    Kiểm thử Admin có thể gán đúng cả 4 vai trò hợp lệ: Admin, HR, Mentor, ThucTapSinh.
    """
    payload = {
        "ho_ten": f"Người dùng vai trò {role}",
        "email": f"user_{role.lower()}@ttcs.edu.vn",
        "ten_dang_nhap": f"user_{role.lower()}",
        "mat_khau": "MatKhauChuan@123",
        "vai_tro": role
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["vai_tro"] == role


def test_admin_create_user_with_english_field_aliases_201(client, admin_headers):
    """
    Kiểm thử độ linh hoạt: Hỗ trợ cả frontend gửi tên trường tiếng Anh
    (full_name, username, password, role) vẫn được xử lý chuẩn xác trả về 201.
    """
    payload = {
        "full_name": "Lê Văn Intern",
        "email": "intern.le@ttcs.edu.vn",
        "username": "intern_le",
        "password": "PasswordIntern@123",
        "role": "ThucTapSinh"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["ten_dang_nhap"] == "intern_le"
    assert response.json()["vai_tro"] == "ThucTapSinh"


# ==============================================================================
# TEST CASE 2: THIẾU TRƯỜNG BẮT BUỘC HOẶC VAI TRÒ KHÔNG HỢP LỆ (422 UNPROCESSABLE ENTITY)
# ==============================================================================

def test_create_user_missing_email_422(client, admin_headers):
    """Gửi dữ liệu thiếu trường email -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Nguyễn Văn Thiếu Email",
        "ten_dang_nhap": "thieu_email",
        "mat_khau": "Password@123",
        "vai_tro": "Mentor"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_create_user_missing_username_422(client, admin_headers):
    """Gửi dữ liệu thiếu trường ten_dang_nhap (username) -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Nguyễn Văn Thiếu User",
        "email": "thieu_user@ttcs.edu.vn",
        "mat_khau": "Password@123",
        "vai_tro": "HR"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_create_user_missing_password_422(client, admin_headers):
    """Gửi dữ liệu thiếu trường mat_khau (password) -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Nguyễn Văn Thiếu Pass",
        "email": "thieu_pass@ttcs.edu.vn",
        "ten_dang_nhap": "thieu_pass",
        "vai_tro": "ThucTapSinh"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_create_user_missing_full_name_422(client, admin_headers):
    """Gửi dữ liệu thiếu trường ho_ten (họ và tên) -> 422 Unprocessable Entity"""
    payload = {
        "email": "thieu_hoten@ttcs.edu.vn",
        "ten_dang_nhap": "thieu_hoten",
        "mat_khau": "Password@123",
        "vai_tro": "Mentor"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_create_user_missing_role_422(client, admin_headers):
    """Gửi dữ liệu thiếu trường vai_tro -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Nguyễn Văn Thiếu Role",
        "email": "thieu_role@ttcs.edu.vn",
        "ten_dang_nhap": "thieu_role",
        "mat_khau": "Password@123"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_create_user_invalid_role_422(client, admin_headers):
    """
    Gửi vai trò không nằm trong danh sách (Admin, HR, Mentor, ThucTapSinh),
    ví dụ 'SuperAdmin', 'GiamDoc', 'SinhVien' -> 422 Unprocessable Entity.
    """
    payload = {
        "ho_ten": "Người Dùng Sai Role",
        "email": "sai_role@ttcs.edu.vn",
        "ten_dang_nhap": "sai_role",
        "mat_khau": "Password@123",
        "vai_tro": "SuperAdmin"  # Không hợp lệ
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_create_user_invalid_email_format_422(client, admin_headers):
    """Gửi email sai định dạng (không có @ hoặc domain) -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Email Sai Định Dạng",
        "email": "email_khong_hop_le",
        "ten_dang_nhap": "invalid_email_user",
        "mat_khau": "Password@123",
        "vai_tro": "ThucTapSinh"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 422


# ==============================================================================
# TEST CASE 3: CHỐNG TRÙNG LẶP USERNAME / EMAIL (400 BAD REQUEST)
# ==============================================================================

def test_create_user_duplicate_username_400(client, admin_headers):
    """
    Kịch bản: Tạo tài khoản thứ 2 có trùng `ten_dang_nhap` (username).
    Kỳ vọng: Trả về mã 400 Bad Request kèm thông báo lỗi rõ ràng.
    """
    # 1. Tạo user ban đầu
    user_initial = {
        "ho_ten": "Tài Khoản Gốc",
        "email": "original@ttcs.edu.vn",
        "ten_dang_nhap": "user_trung_lap",
        "mat_khau": "MatKhau1@123",
        "vai_tro": "Mentor"
    }
    res1 = client.post("/api/v1/admin/users", json=user_initial, headers=admin_headers)
    assert res1.status_code == 201

    # 2. Cố gắng tạo user mới có CÙNG tên đăng nhập (dù email khác)
    user_duplicate = {
        "ho_ten": "Tài Khoản Thứ Hai",
        "email": "other_email@ttcs.edu.vn",
        "ten_dang_nhap": "user_trung_lap",  # Trùng username
        "mat_khau": "MatKhau2@123",
        "vai_tro": "HR"
    }
    res2 = client.post("/api/v1/admin/users", json=user_duplicate, headers=admin_headers)

    assert res2.status_code in [400, 409], f"Expected 400 or 409, got {res2.status_code}"
    error_detail = res2.json().get("detail", "")
    assert "Tên đăng nhập" in error_detail or "tồn tại" in error_detail


def test_create_user_duplicate_email_400(client, admin_headers):
    """
    Kịch bản: Tạo tài khoản thứ 2 có trùng `email`.
    Kỳ vọng: Trả về mã 400 Bad Request kèm thông báo lỗi rõ ràng.
    """
    # 1. Tạo user ban đầu
    user_initial = {
        "ho_ten": "Tài Khoản Email Gốc",
        "email": "email_trung_lap@ttcs.edu.vn",
        "ten_dang_nhap": "user_email_1",
        "mat_khau": "MatKhau1@123",
        "vai_tro": "Mentor"
    }
    res1 = client.post("/api/v1/admin/users", json=user_initial, headers=admin_headers)
    assert res1.status_code == 201

    # 2. Cố gắng tạo user mới có CÙNG email (dù username khác)
    user_duplicate = {
        "ho_ten": "Tài Khoản Trùng Email",
        "email": "email_trung_lap@ttcs.edu.vn",  # Trùng email
        "ten_dang_nhap": "user_email_2",
        "mat_khau": "MatKhau2@123",
        "vai_tro": "ThucTapSinh"
    }
    res2 = client.post("/api/v1/admin/users", json=user_duplicate, headers=admin_headers)

    assert res2.status_code in [400, 409], f"Expected 400 or 409, got {res2.status_code}"
    error_detail = res2.json().get("detail", "")
    assert "Email" in error_detail or "tồn tại" in error_detail


# ==============================================================================
# TEST CASE 4: PHÂN QUYỀN RBAC - TÀI KHOẢN KHÔNG PHẢI ADMIN THAO TÁC (403 FORBIDDEN)
# ==============================================================================

def test_create_user_forbidden_by_hr_403(client, hr_headers):
    """Tài khoản có vai trò HR cố tình tạo user -> 403 Forbidden"""
    payload = {
        "ho_ten": "Test User",
        "email": "test_by_hr@ttcs.edu.vn",
        "ten_dang_nhap": "test_by_hr",
        "mat_khau": "MatKhau@123",
        "vai_tro": "ThucTapSinh"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=hr_headers)
    assert response.status_code == 403
    assert "Chỉ có Quản trị viên (Admin)" in response.json().get("detail", "")


def test_create_user_forbidden_by_mentor_403(client, mentor_headers):
    """Tài khoản có vai trò Mentor cố tình tạo user -> 403 Forbidden"""
    payload = {
        "ho_ten": "Test User",
        "email": "test_by_mentor@ttcs.edu.vn",
        "ten_dang_nhap": "test_by_mentor",
        "mat_khau": "MatKhau@123",
        "vai_tro": "ThucTapSinh"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=mentor_headers)
    assert response.status_code == 403


def test_create_user_forbidden_by_intern_403(client, intern_headers):
    """Tài khoản có vai trò ThucTapSinh cố tình tạo user -> 403 Forbidden"""
    payload = {
        "ho_ten": "Test User",
        "email": "test_by_intern@ttcs.edu.vn",
        "ten_dang_nhap": "test_by_intern",
        "mat_khau": "MatKhau@123",
        "vai_tro": "ThucTapSinh"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers=intern_headers)
    assert response.status_code == 403


def test_create_user_forbidden_via_header_mock_403(client):
    """Kiểm thử qua header mock X-User-Role: HR -> 403 Forbidden"""
    payload = {
        "ho_ten": "Test User",
        "email": "mock_test@ttcs.edu.vn",
        "ten_dang_nhap": "mock_test_user",
        "mat_khau": "MatKhau@123",
        "vai_tro": "Mentor"
    }
    response = client.post("/api/v1/admin/users", json=payload, headers={"X-User-Role": "HR"})
    assert response.status_code == 403


# ==============================================================================
# TEST CASE BỔ SUNG: KHÔNG XÁC THỰC / THIẾU TOKEN (401 UNAUTHORIZED)
# ==============================================================================

def test_create_user_unauthorized_without_token_401(client):
    """Không gửi kèm token xác thực hoặc header -> 401 Unauthorized"""
    payload = {
        "ho_ten": "User Khong Auth",
        "email": "no_auth@ttcs.edu.vn",
        "ten_dang_nhap": "no_auth_user",
        "mat_khau": "MatKhau@123",
        "vai_tro": "Mentor"
    }
    response = client.post("/api/v1/admin/users", json=payload)
    assert response.status_code == 401
