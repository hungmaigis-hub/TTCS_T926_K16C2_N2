import pytest
import sys
from pathlib import Path
from datetime import date, timedelta

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from tests.conftest import MYSQL_AVAILABLE, TestSessionLocal
from database.session import SessionLocal
from database.models import ChuongTrinhThucTap

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_created_test_programs():
    """Dọn dẹp các chương trình được tạo trong quá trình test sau mỗi test case"""
    yield
    db = SessionLocal() if MYSQL_AVAILABLE else TestSessionLocal()
    try:
        # Xóa các chương trình test có mã lớn hơn 1 (dữ liệu mẫu ban đầu là 1)
        db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh > 1).delete()
        # Khôi phục mốc thời gian ban đầu của chương trình mẫu 1
        prog1 = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == 1).first()
        if prog1:
            prog1.ngay_bat_dau = date(2026, 9, 1)
            prog1.ngay_ket_thuc = date(2026, 12, 30)
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


# ==============================================================================
# BỘ KIỂM THỬ CHO API: PATCH /api/v1/programs/{id}/timeline
# ==============================================================================

def test_update_timeline_success_both_dates():
    """Kiểm tra cập nhật thành công cả ngày bắt đầu và kết thúc (ngay_ket_thuc > ngay_bat_dau) -> 200 OK"""
    payload = {
        "ngay_bat_dau": "2026-10-01",
        "ngay_ket_thuc": "2026-12-31"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["message"] == "Cập nhật thời gian chương trình thực tập thành công"
    assert res_data["data"]["ma_chuong_trinh"] == 1
    assert res_data["data"]["ngay_bat_dau"] == "2026-10-01"
    assert res_data["data"]["ngay_ket_thuc"] == "2026-12-31"


def test_update_timeline_success_start_date_only():
    """Kiểm tra cập nhật chỉ ngày bắt đầu mới (hợp lệ với ngày kết thúc hiện tại trong DB) -> 200 OK"""
    payload = {
        "ngay_bat_dau": "2026-09-15"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["ngay_bat_dau"] == "2026-09-15"
    assert res_data["data"]["ngay_ket_thuc"] == "2026-12-30"


def test_update_timeline_success_end_date_only():
    """Kiểm tra cập nhật chỉ ngày kết thúc mới (hợp lệ với ngày bắt đầu hiện tại trong DB) -> 200 OK"""
    payload = {
        "ngay_ket_thuc": "2026-11-30"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["ngay_bat_dau"] == "2026-09-01"
    assert res_data["data"]["ngay_ket_thuc"] == "2026-11-30"


def test_update_timeline_invalid_end_before_start():
    """Kiểm tra gửi cả 2 ngày nhưng ngày kết thúc trước ngày bắt đầu -> 422 Unprocessable Entity"""
    payload = {
        "ngay_bat_dau": "2026-11-01",
        "ngay_ket_thuc": "2026-10-01"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 422


def test_update_timeline_invalid_end_equals_start():
    """Kiểm tra gửi cả 2 ngày nhưng ngày kết thúc bằng ngày bắt đầu (yêu cầu kết thúc > bắt đầu) -> 422 Unprocessable Entity"""
    payload = {
        "ngay_bat_dau": "2026-11-01",
        "ngay_ket_thuc": "2026-11-01"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 422


def test_update_timeline_conflict_with_existing_end():
    """Kiểm tra chỉ đổi ngày bắt đầu nhưng lớn hơn hoặc bằng ngày kết thúc hiện tại trong DB -> 400 Bad Request"""
    payload = {
        "ngay_bat_dau": "2027-01-01"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 400
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu" in response.json()["detail"]


def test_update_timeline_conflict_with_existing_start():
    """Kiểm tra chỉ đổi ngày kết thúc nhưng nhỏ hơn hoặc bằng ngày bắt đầu hiện tại trong DB -> 400 Bad Request"""
    payload = {
        "ngay_ket_thuc": "2026-08-01"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 400
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu" in response.json()["detail"]


def test_update_timeline_same_as_existing_boundary_rejected():
    """Kiểm tra chỉ đổi ngày kết thúc trùng đúng ngày bắt đầu hiện tại (2026-09-01) -> 400 Bad Request"""
    payload = {
        "ngay_ket_thuc": "2026-09-01"
    }
    response = client.patch("/api/v1/programs/1/timeline", json=payload)
    assert response.status_code == 400
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu" in response.json()["detail"]


def test_update_timeline_empty_body():
    """Kiểm tra không gửi trường nào trong body -> 422 Unprocessable Entity"""
    response = client.patch("/api/v1/programs/1/timeline", json={})
    assert response.status_code == 422


def test_update_timeline_not_found():
    """Kiểm tra cập nhật timeline của chương trình không tồn tại -> 404 Not Found"""
    payload = {
        "ngay_bat_dau": "2026-10-01",
        "ngay_ket_thuc": "2026-12-31"
    }
    response = client.patch("/api/v1/programs/9999/timeline", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy chương trình thực tập ID: 9999" in response.json()["detail"]


def test_update_timeline_invalid_id():
    """Kiểm tra ID âm hoặc bằng 0 -> 422 Unprocessable Entity"""
    payload = {
        "ngay_bat_dau": "2026-10-01",
        "ngay_ket_thuc": "2026-12-31"
    }
    response = client.patch("/api/v1/programs/0/timeline", json=payload)
    assert response.status_code == 422

