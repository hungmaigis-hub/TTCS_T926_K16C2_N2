import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient
from main import app

# Khởi tạo client giả lập để gửi request test đến API mà không cần bật server
client = TestClient(app)

# ==============================================================
# UNIT TEST CHO API GET /api/v1/interns/{id}
# ==============================================================

def test_get_intern_success():
    """Kiểm tra lấy thành công thông tin thực tập sinh có sẵn (ID 1)"""
    response = client.get("/api/v1/interns/1")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert "data" in res_data
    assert res_data["data"]["ma_ho_so"] == 1
    assert "ho_ten" in res_data["data"]
    assert "email" in res_data["data"]

def test_get_intern_not_found():
    """Kiểm tra khi tìm ID không tồn tại -> Trả về 404"""
    response = client.get("/api/v1/interns/99999")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_get_intern_invalid_id():
    """Kiểm tra khi ID không phải là số -> Trả về 422"""
    response = client.get("/api/v1/interns/abc")
    assert response.status_code == 422


# ==============================================================
# UNIT TEST CHO API PUT /api/v1/interns/{id}
# ==============================================================

def test_update_intern_success():
    """Kiểm tra cập nhật thành công với dữ liệu hợp lệ"""
    payload = {
        "ho_ten": "Nguyễn Văn A Updated",
        "email": "vana@example.com",
        "so_dien_thoai": "0912345678",
        "chuyen_nganh": "Khoa học máy tính",
        "ma_truong": 1,
        "trang_thai_thuc_tap": "DangThucTap"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["message"] == "Cập nhật thông tin thực tập sinh thành công"
    assert res_data["data"]["ho_ten"] == "Nguyễn Văn A Updated"
    assert res_data["data"]["chuyen_nganh"] == "Khoa học máy tính"

def test_update_intern_not_found():
    """Kiểm tra cập nhật với ID không tồn tại -> Trả về 404"""
    payload = {
        "ho_ten": "Người Vô Danh",
        "email": "nodata@example.com"
    }
    response = client.put("/api/v1/interns/99999", json=payload)
    assert response.status_code == 404

def test_update_intern_duplicate_email():
    """Kiểm tra đổi email thành email của thực tập sinh khác (user 2: thib@example.com) -> Trả về 400"""
    payload = {
        "ho_ten": "Nguyễn Văn A",
        "email": "thib@example.com"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email này đã được sử dụng"

def test_update_intern_duplicate_phone():
    """Kiểm tra đổi SĐT thành SĐT của thực tập sinh khác (user 2: 0987654321) -> Trả về 400"""
    payload = {
        "ho_ten": "Nguyễn Văn A",
        "email": "vana@example.com",
        "so_dien_thoai": "0987654321"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Số điện thoại này đã được sử dụng"

def test_update_intern_empty_required_field():
    """Kiểm tra bỏ trống trường bắt buộc hoặc chỉ nhập khoảng trắng -> Trả về 422"""
    payload = {
        "ho_ten": "   ",
        "email": "vana@example.com"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 422

def test_update_intern_invalid_university_id():
    """Kiểm tra truyền mã trường đại học không tồn tại -> Trả về 400"""
    payload = {
        "ho_ten": "Nguyễn Văn A",
        "email": "vana@example.com",
        "ma_truong": 99999
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Mã trường đại học không tồn tại trong hệ thống"

# ==============================================================
# NGOẠI LỆ, TEST BIÊN, CASE SAI ĐỊNH DẠNG
# ==============================================================

def test_put_field_is_null():
    """Truyền null vào trường bắt buộc -> Trả về 422"""
    payload = {
        "ho_ten": None,
        "email": None
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 422

def test_put_invalid_email_format():
    """Email sai định dạng cú pháp -> Trả về 422"""
    payload = {
        "ho_ten": "Nguyễn Văn A",
        "email": "email_khong_hop_le"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 422

def test_put_invalid_phone_format():
    """SĐT không đủ 10 số hoặc chứa chữ cái -> Trả về 422"""
    payload = {
        "ho_ten": "Nguyễn Văn A",
        "email": "vana@example.com",
        "so_dien_thoai": "091234abcd"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 422

def test_put_boundary_name_too_long():
    """Họ tên vượt quá độ dài tối đa 100 ký tự -> Trả về 422"""
    payload = {
        "ho_ten": "A" * 105,
        "email": "vana@example.com"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 422
    
def test_put_keep_own_email_and_phone():
    """Giữ nguyên email và SĐT của chính mình -> Hợp lệ (200)"""
    payload = {
        "ho_ten": "Nguyễn Văn A",
        "email": "vana@example.com",
        "so_dien_thoai": "0912345678"
    }
    response = client.put("/api/v1/interns/1", json=payload)
    assert response.status_code == 200