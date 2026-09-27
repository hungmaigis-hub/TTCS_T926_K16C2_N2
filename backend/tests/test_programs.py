import pytest
import sys
from pathlib import Path
from datetime import date, timedelta

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import ChuongTrinhThucTap

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_created_test_programs():
    """Dọn dẹp các chương trình được tạo trong quá trình test sau mỗi test case"""
    yield
    db = SessionLocal()
    try:
        # Xóa các chương trình test có mã lớn hơn 1 (dữ liệu mẫu ban đầu là 1)
        db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh > 1).delete()
        db.commit()
    finally:
        db.close()


# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/programs
# ==============================================================================

def test_create_program_full_success():
    """Kiểm tra tạo chương trình thực tập thành công với đầy đủ các trường thông tin -> 201 Created"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "Chương trình Kỹ sư AI Thực chiến 2026",
        "mo_ta": "Đào tạo chuyên sâu về Machine Learning và MLOps cho sinh viên năm cuối",
        "ngay_bat_dau": "2026-10-01",
        "ngay_ket_thuc": "2026-12-31"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status_code"] == 201
    assert res_data["message"] == "Tạo chương trình thực tập thành công"
    assert "data" in res_data
    
    prog = res_data["data"]
    assert prog["ma_chuong_trinh"] > 0
    assert prog["ma_phong_ban"] == 1
    assert prog["ten_phong_ban"] == "Trung tâm Phần mềm"
    assert prog["ten_chuong_trinh"] == "Chương trình Kỹ sư AI Thực chiến 2026"
    assert prog["ngay_bat_dau"] == "2026-10-01"
    assert prog["ngay_ket_thuc"] == "2026-12-31"
    assert "Machine Learning" in prog["mo_ta"]


def test_create_program_minimal_fields_success():
    """Kiểm tra tạo chương trình chỉ với trường bắt buộc (ma_phong_ban, ten_chuong_trinh) -> 201 Created"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "Chương trình Lập trình Web Căn bản"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    prog = res_data["data"]
    assert prog["ten_chuong_trinh"] == "Chương trình Lập trình Web Căn bản"
    assert prog["mo_ta"] is None
    # Tự động gán ngày bắt đầu là hôm nay và ngày kết thúc sau 90 ngày
    assert prog["ngay_bat_dau"] == date.today().isoformat()
    expected_end = (date.today() + timedelta(days=90)).isoformat()
    assert prog["ngay_ket_thuc"] == expected_end


def test_create_program_strip_whitespace():
    """Kiểm tra tên chương trình có khoảng trắng thừa ở hai đầu được tự động strip -> 201 Created"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "   Chương trình Cloud DevOps 2026   ",
        "mo_ta": "   Mô tả cũng được cắt gọn   "
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 201
    prog = response.json()["data"]
    assert prog["ten_chuong_trinh"] == "Chương trình Cloud DevOps 2026"
    assert prog["mo_ta"] == "Mô tả cũng được cắt gọn"


def test_create_program_department_not_found():
    """Kiểm tra mã phòng ban không tồn tại trong CSDL -> 400 Bad Request"""
    payload = {
        "ma_phong_ban": 99999,
        "ten_chuong_trinh": "Chương trình không hợp lệ",
        "mo_ta": "Phòng ban không tồn tại"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    assert "detail" in res_data
    assert "Mã phòng ban không tồn tại" in res_data["detail"]


def test_create_program_duplicate_name_same_department():
    """Kiểm tra tạo chương trình trùng tên trong cùng một phòng ban -> 400 Bad Request"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "Thực tập sinh Khóa Mùa Thu 2026"  # Đã có trong seed data
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    assert "detail" in res_data
    assert "đã tồn tại trong phòng ban" in res_data["detail"]


def test_create_program_invalid_dates_logic():
    """Kiểm tra logic ngày kết thúc diễn ra trước ngày bắt đầu -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "Chương trình sai ngày",
        "ngay_bat_dau": "2026-12-31",
        "ngay_ket_thuc": "2026-01-01"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_empty_name():
    """Kiểm tra tên chương trình là chuỗi rỗng -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": ""
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_only_whitespace_name():
    """Kiểm tra tên chương trình chỉ chứa khoảng trắng -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "        "
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_missing_required_ten_chuong_trinh():
    """Kiểm tra gửi thiếu trường bắt buộc ten_chuong_trinh -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": 1,
        "mo_ta": "Thiếu tên chương trình"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_missing_required_ma_phong_ban():
    """Kiểm tra gửi thiếu trường bắt buộc ma_phong_ban -> 422 Unprocessable Entity"""
    payload = {
        "ten_chuong_trinh": "Chương trình thiếu phòng ban"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_invalid_department_id_string():
    """Kiểm tra mã phòng ban là chuỗi chữ cái -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": "phong_ban_it",
        "ten_chuong_trinh": "Chương trình IT"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_negative_department_id():
    """Kiểm tra mã phòng ban là số âm -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": -1,
        "ten_chuong_trinh": "Chương trình phòng ban âm"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_zero_department_id():
    """Kiểm tra mã phòng ban bằng 0 -> 422 Unprocessable Entity"""
    payload = {
        "ma_phong_ban": 0,
        "ten_chuong_trinh": "Chương trình phòng ban 0"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 422


def test_create_program_same_dates_success():
    """Kiểm tra ngày kết thúc trùng với ngày bắt đầu (workshop 1 ngày) -> 201 Created"""
    payload = {
        "ma_phong_ban": 1,
        "ten_chuong_trinh": "Workshop Định hướng nghề nghiệp 1 ngày",
        "ngay_bat_dau": "2026-10-15",
        "ngay_ket_thuc": "2026-10-15"
    }
    response = client.post("/api/v1/programs", json=payload)
    assert response.status_code == 201
    prog = response.json()["data"]
    assert prog["ngay_bat_dau"] == "2026-10-15"
    assert prog["ngay_ket_thuc"] == "2026-10-15"
