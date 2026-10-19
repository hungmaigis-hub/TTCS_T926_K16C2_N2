"""
Test Suite kiểm thử toàn diện cho hệ thống Phân quyền theo vai trò (RBAC):
- Bảng quyen_han & vai_tro_quyen_han
- Dependency require_permissions trong FastAPI
- Endpoint PUT /api/v1/admin/roles/{role}/permissions
- Endpoint GET /api/v1/admin/roles/{role}/permissions
- Endpoint GET /api/v1/admin/permissions
"""
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app
from database.models import NguoiDung, QuyenHan, VaiTroQuyenHan
from tests.conftest import TestSessionLocal

client = TestClient(app)


def test_get_all_permissions_success():
    """Kiểm tra truy vấn danh mục toàn bộ quyền hạn hệ thống"""
    response = client.get(
        "/api/v1/admin/permissions",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["total"] >= 16
    codes = [item["ma_quyen"] for item in data["data"]]
    assert "intern:read" in codes
    assert "role:manage" in codes
    assert "attendance:scan" in codes


def test_get_role_permissions_success():
    """Kiểm tra truy vấn danh sách quyền hạn của vai trò Mentor"""
    response = client.get(
        "/api/v1/admin/roles/Mentor/permissions",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "Mentor"
    assert data["total_permissions"] > 0
    codes = [p["ma_quyen"] for p in data["permissions"]]
    assert "intern:read" in codes or "task:read" in codes


def test_update_role_permissions_by_codes():
    """Kiểm tra cập nhật quyền hạn cho vai trò bằng danh sách mã quyền chuỗi"""
    new_perms = ["intern:read", "task:read", "meeting:create"]
    response = client.put(
        "/api/v1/admin/roles/Mentor/permissions",
        headers={"X-User-Email": "admin@example.com"},
        json={"permissions": new_perms}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["role"] == "Mentor"
    assert data["total_permissions"] == 3
    result_codes = {p["ma_quyen"] for p in data["permissions"]}
    assert result_codes == set(new_perms)

    # Kiểm tra lại bằng GET
    get_res = client.get(
        "/api/v1/admin/roles/Mentor/permissions",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["total_permissions"] == 3


def test_update_role_permissions_by_ids():
    """Kiểm tra cập nhật quyền hạn cho vai trò bằng danh sách ID số nguyên"""
    db = TestSessionLocal()
    perm_records = db.query(QuyenHan).limit(2).all()
    target_ids = [p.ma_quyen_han for p in perm_records]
    db.close()

    response = client.put(
        "/api/v1/admin/roles/ThucTapSinh/permissions",
        headers={"X-User-Email": "admin@example.com"},
        json={"permissions": target_ids}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "ThucTapSinh"
    assert data["total_permissions"] == len(target_ids)
    res_ids = {p["ma_quyen_han"] for p in data["permissions"]}
    assert res_ids == set(target_ids)


def test_update_role_permissions_invalid_code():
    """Kiểm tra cập nhật với mã quyền không hợp lệ bị từ chối 400"""
    response = client.put(
        "/api/v1/admin/roles/Mentor/permissions",
        headers={"X-User-Email": "admin@example.com"},
        json={"permissions": ["invalid:code:does_not_exist_xyz"]}
    )
    assert response.status_code == 400
    assert "không tồn tại" in response.json()["detail"]


def test_require_permissions_without_credentials():
    """Kiểm tra gọi endpoint khi không cung cấp thông tin xác thực bị chặn 401"""
    response = client.get("/api/v1/admin/permissions")
    assert response.status_code == 401
    assert "Yêu cầu đăng nhập hoặc cung cấp thông tin xác thực" in response.json()["detail"]


def test_require_permissions_locked_account():
    """Kiểm tra tài khoản bị khóa bị từ chối truy cập 403"""
    response = client.get(
        "/api/v1/admin/permissions",
        headers={"X-User-Email": "locked@example.com"}
    )
    assert response.status_code == 403
    assert "đã bị khóa" in response.json()["detail"]


def test_require_permissions_missing_permission():
    """Kiểm tra tài khoản không có quyền role:manage bị từ chối 403"""
    # Sinh viên (vana@example.com) không có quyền role:manage
    response = client.get(
        "/api/v1/admin/permissions",
        headers={"X-User-Email": "vana@example.com"}
    )
    assert response.status_code == 403
    assert "Quyền truy cập bị từ chối" in response.json()["detail"]


def test_require_permissions_admin_bypass():
    """Kiểm tra tài khoản Admin có toàn quyền bypass thành công 200"""
    response = client.get(
        "/api/v1/admin/permissions",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert response.status_code == 200


def test_require_permissions_via_user_id():
    """Kiểm tra xác thực qua header X-User-Id thành công"""
    response = client.get(
        "/api/v1/admin/permissions",
        headers={"X-User-Id": "5"}
    )
    assert response.status_code == 200


def test_prevent_admin_role_permission_modification():
    """Kiểm tra hệ thống chặn không cho phép sửa đổi hoặc tước bỏ quyền hạn của vai trò Admin"""
    response = client.put(
        "/api/v1/admin/roles/Admin/permissions",
        headers={"X-User-Email": "admin@example.com"},
        json={"permissions": ["intern:read"]}
    )
    assert response.status_code == 400
    assert "Superadmin tối cao" in response.json()["detail"]

