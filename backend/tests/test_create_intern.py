import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/interns (Tạo mới hồ sơ thực tập sinh)
# ==============================================================================

def test_create_intern_success_full_fields():
    """Kiểm tra tạo mới thực tập sinh thành công với đầy đủ thông tin -> 201 Created"""
    payload = {
        "ho_ten": "Lê Văn Cường",
        "email": "cuong.le@example.com",
        "so_dien_thoai": "0933112233",
        "chuyen_nganh": "Kỹ thuật phần mềm",
        "ma_truong": 1,
        "ma_chuong_trinh": 1,
        "ma_mentor": 3,
        "trang_thai_xet_duyet": "ChoDuyet",
        "trang_thai_thuc_tap": "DangThucTap"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status_code"] == 201
    assert res_data["message"] == "Tạo hồ sơ thực tập sinh thành công"
    assert "data" in res_data
    
    data = res_data["data"]
    assert data["ho_ten"] == "Lê Văn Cường"
    assert data["email"] == "cuong.le@example.com"
    assert data["so_dien_thoai"] == "0933112233"
    assert data["chuyen_nganh"] == "Kỹ thuật phần mềm"
    assert data["ma_truong"] == 1
    assert data["ten_truong"] == "Đại học Thái Nguyên"
    assert data["ma_chuong_trinh"] == 1
    assert data["ten_chuong_trinh"] == "Thực tập sinh Khóa Mùa Thu 2026"
    assert data["ma_mentor"] == 3
    assert data["ten_mentor"] == "Nguyễn Hướng Dẫn"
    assert data["trang_thai_xet_duyet"] == "ChoDuyet"
    assert data["trang_thai_thuc_tap"] == "DangThucTap"
    assert "ma_ho_so" in data
    assert "ma_nguoi_dung" in data


def test_create_intern_success_minimal_fields():
    """Kiểm tra tạo mới chỉ với trường bắt buộc (ho_ten, email), các trường khác None -> 201 Created"""
    payload = {
        "ho_ten": "Phạm Hoàng Dung",
        "email": "dung.pham@example.com"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status_code"] == 201
    
    data = res_data["data"]
    assert data["ho_ten"] == "Phạm Hoàng Dung"
    assert data["email"] == "dung.pham@example.com"
    assert data["so_dien_thoai"] is None
    assert data["chuyen_nganh"] is None
    assert data["ma_truong"] is None
    assert data["trang_thai_xet_duyet"] == "ChoDuyet"
    assert data["trang_thai_thuc_tap"] == "DangThucTap"


def test_create_intern_success_strip_whitespace():
    """Kiểm tra tự động cắt khoảng trắng thừa ở họ tên và email -> 201 Created"""
    payload = {
        "ho_ten": "   Vũ Đức Đam   ",
        "email": "   dam.vu@example.com   ",
        "so_dien_thoai": "  0988776655  "
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["ho_ten"] == "Vũ Đức Đam"
    assert data["email"] == "dam.vu@example.com"
    assert data["so_dien_thoai"] == "0988776655"


# ------------------------------------------------------------------------------
# NHÓM TEST CASES VALIDATE SCHEMA ĐẦU VÀO (HTTP 422)
# ------------------------------------------------------------------------------

def test_create_intern_missing_ho_ten():
    """Thiếu trường bắt buộc ho_ten -> 422 Unprocessable Entity"""
    payload = {
        "email": "no_name@example.com"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_empty_ho_ten():
    """Trường ho_ten để chuỗi rỗng hoặc chỉ khoảng trắng -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "    ",
        "email": "empty_name@example.com"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_ho_ten_with_numbers():
    """Trường ho_ten chứa chữ số -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Nguyễn Văn 123",
        "email": "num_name@example.com"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_missing_email():
    """Thiếu trường bắt buộc email -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Trần Văn Thiếu Email"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_invalid_email_format():
    """Định dạng email không hợp lệ -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Trần Văn A",
        "email": "invalid-email-format"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_invalid_phone_format():
    """Số điện thoại không đúng chuẩn 10 chữ số -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Trần Văn A",
        "email": "valid@example.com",
        "so_dien_thoai": "09123"  # Thiếu số
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_invalid_trang_thai_xet_duyet():
    """Trạng thái xét duyệt không nằm trong danh mục cho phép -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Trần Văn A",
        "email": "valid@example.com",
        "trang_thai_xet_duyet": "KhongHopLe"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


def test_create_intern_invalid_trang_thai_thuc_tap():
    """Trạng thái thực tập không nằm trong danh mục cho phép -> 422 Unprocessable Entity"""
    payload = {
        "ho_ten": "Trần Văn A",
        "email": "valid@example.com",
        "trang_thai_thuc_tap": "DaNghiViec"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 422


# ------------------------------------------------------------------------------
# NHÓM TEST CASES RÀNG BUỘC NGHIỆP VỤ & CSDL (HTTP 400)
# ------------------------------------------------------------------------------

def test_create_intern_duplicate_email():
    """Email đã tồn tại trong hệ thống (vana@example.com) -> 400 Bad Request"""
    payload = {
        "ho_ten": "Nguyễn Văn Trùng",
        "email": "vana@example.com"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 400
    assert "Email này đã được sử dụng" in response.json()["detail"]


def test_create_intern_duplicate_phone():
    """Số điện thoại đã tồn tại trong hệ thống (0912345678) -> 400 Bad Request"""
    payload = {
        "ho_ten": "Nguyễn Văn Trùng Phone",
        "email": "new_unique@example.com",
        "so_dien_thoai": "0912345678"
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 400
    assert "Số điện thoại này đã được sử dụng" in response.json()["detail"]


def test_create_intern_nonexistent_university():
    """Mã trường đại học không tồn tại trong CSDL -> 400 Bad Request"""
    payload = {
        "ho_ten": "Lý Văn E",
        "email": "lye@example.com",
        "ma_truong": 99999
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 400
    assert "Mã trường đại học không tồn tại" in response.json()["detail"]


def test_create_intern_nonexistent_program():
    """Mã chương trình thực tập không tồn tại trong CSDL -> 400 Bad Request"""
    payload = {
        "ho_ten": "Lý Văn E",
        "email": "lye@example.com",
        "ma_chuong_trinh": 99999
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 400
    assert "Mã chương trình thực tập không tồn tại" in response.json()["detail"]


def test_create_intern_nonexistent_mentor():
    """Mã người hướng dẫn (mentor) không tồn tại trong CSDL -> 400 Bad Request"""
    payload = {
        "ho_ten": "Lý Văn E",
        "email": "lye@example.com",
        "ma_mentor": 99999
    }
    response = client.post("/api/v1/interns", json=payload)
    assert response.status_code == 400
    assert "Mã người hướng dẫn (mentor) không tồn tại" in response.json()["detail"]
