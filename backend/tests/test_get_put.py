import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient
from main import app

# Khởi tạo client giả lập để gửi request test đến API mà không cần bật server
client = TestClient(app)

# Unit test cho api get

def test_get_intern_success():
    """Kiểm tra lấy thành công thông tin thực tập sinh có sẵn (ID 1)"""
    response = client.get("/api/interns/1")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert "data" in res_data
    assert res_data["data"]["id"] == 1

def test_get_intern_not_found():
    """Kiểm tra khi tìm ID không tồn tại -> Trả về 404"""
    response = client.get("/api/interns/99999")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_get_intern_invalid_id():
    """Kiểm tra khi ID không phải là số -> Trả về 422"""
    response = client.get("/api/interns/abc")
    assert response.status_code == 422


# Unit test cho api put --------------------------------------------

def test_update_intern_success():
    """Kiểm tra cập nhật thành công với dữ liệu hợp lệ"""
    payload = {
        "full_name": "Nguyễn Văn A Updated",
        "email": "vana@example.com",
        "phone": "0912345678",
        "university": "Đại học Thái Nguyên",
        "major": "Khoa học máy tính",
        "status": "Đang thực tập",
        "start_date": "2026-09-01",
        "end_date": "2026-12-30"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["message"] == "Cập nhật thông tin thực tập sinh thành công"
    assert res_data["data"]["full_name"] == "Nguyễn Văn A Updated"

def test_update_intern_not_found():
    """Kiểm tra cập nhật với ID không tồn tại -> Trả về 404"""
    payload = {
        "full_name": "Người Vô Danh",
        "email": "nodata@example.com"
    }
    response = client.put("/api/interns/99999", json=payload)
    assert response.status_code == 404

def test_update_intern_duplicate_email():
    """Kiểm tra đổi email thành email của thực tập sinh khác (ID 2: thib@example.com) -> Trả về 400"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "thib@example.com"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email này đã được sử dụng"

def test_update_intern_duplicate_phone():
    """Kiểm tra đổi SĐT thành SĐT của thực tập sinh khác (ID 2: 0987654321) -> Trả về 400"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "vana@example.com",
        "phone": "0987654321"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Số điện thoại này đã được sử dụng"

def test_update_intern_empty_required_field():
    """Kiểm tra bỏ trống trường bắt buộc hoặc chỉ nhập khoảng trắng -> Trả về 422"""
    payload = {
        "full_name": "   ",
        "email": "vana@example.com"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 422

def test_update_intern_invalid_date_logic():
    """Kiểm tra logic ngày kết thúc < ngày bắt đầu -> Trả về 422"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "vana@example.com",
        "start_date": "2026-12-01",
        "end_date": "2026-09-01"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 422
# ngoại lệ, test biên, case sai, case logic
def test_put_field_is_null():
    """Truyền null vào trường bắt buộc -> Trả về 422"""
    payload = {
        "full_name": None,
        "email": None
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 422
def test_put_invalid_email_format():
    """Email sai định dạng cú pháp -> Trả về 422"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "email_khong_hop_le"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 422
def test_put_invalid_phone_format():
    """sdt không đủ 10 số (chỉ có 8 số hoặc có chữ) -> Trả về 422"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "vana@example.com",
        "phone": "091234abcd"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 422
def test_put_boundary_same_dates():
    """start_date và end_date cùng 1 ngày -> Hợp lệ (200)"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "vana@example.com",
        "start_date": "2026-09-01",
        "end_date": "2026-09-01"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 200
def test_put_boundary_name_too_long():
    """Họ tên vượt quá độ dài tối đa 100 ký tự -> Trả về 422"""
    payload = {
        "full_name": "A" * 105,
        "email": "vana@example.com"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 422
    
def test_put_keep_own_email_and_phone():
    """Giữ nguyên email và SĐT của chính mình -> Hợp lệ (200)"""
    payload = {
        "full_name": "Nguyễn Văn A",
        "email": "vana@example.com",
        "phone": "0912345678"
    }
    response = client.put("/api/interns/1", json=payload)
    assert response.status_code == 200