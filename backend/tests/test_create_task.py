import pytest
import sys
from datetime import date
from pathlib import Path

# Đảm bảo import được module từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import NhiemVu

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/tasks (Tạo mới nhiệm vụ thực tập)
# ==============================================================================

@pytest.fixture(autouse=True)
def cleanup_created_tasks():
    """Dọn dẹp các nhiệm vụ thử nghiệm sau mỗi test case để tránh dữ liệu rác"""
    yield
    try:
        from tests.conftest import TestSessionLocal
        Session = TestSessionLocal
    except Exception:
        Session = SessionLocal
    db = Session()
    try:
        db.query(NhiemVu).filter(NhiemVu.ten_nhiem_vu.like("TEST_%")).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def test_create_task_minimal_success():
    """Kiểm tra tạo nhiệm vụ thành công với các trường tối thiểu -> 201 Created, default tien_do_phantram = 0, trang_thai = 'Chưa bắt đầu'"""
    payload = {
        "ma_ho_so": 1,
        "tieu_de": "TEST_Nhiệm vụ tối thiểu",
        "han_hoan_thanh": "2026-11-15"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["status_code"] == 201
    assert res_data["message"] == "Tạo nhiệm vụ mới thành công"
    assert "data" in res_data

    task = res_data["data"]
    assert task["ma_ho_so"] == 1
    assert task["tieu_de"] == "TEST_Nhiệm vụ tối thiểu"
    assert task["ten_nhiem_vu"] == "TEST_Nhiệm vụ tối thiểu"
    assert task["han_hoan_thanh"] == "2026-11-15"
    assert task["tien_do_phantram"] == 0
    assert task["trang_thai"] == "Chưa bắt đầu"
    assert task["ma_nhiem_vu"] is not None


def test_create_task_full_success():
    """Kiểm tra tạo nhiệm vụ với đầy đủ các trường thông tin -> 201 Created"""
    payload = {
        "ma_ho_so": 1,
        "tieu_de": "TEST_Nhiệm vụ đầy đủ thông tin",
        "mo_ta": "Mô tả chi tiết nội dung công việc cần thực hiện",
        "han_hoan_thanh": "2026-12-01",
        "tien_do_phantram": 10,
        "trang_thai": "Đang thực hiện"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    res_data = response.json()

    task = res_data["data"]
    assert task["ma_ho_so"] == 1
    assert task["tieu_de"] == "TEST_Nhiệm vụ đầy đủ thông tin"
    assert task["mo_ta"] == "Mô tả chi tiết nội dung công việc cần thực hiện"
    assert task["han_hoan_thanh"] == "2026-12-01"
    assert task["tien_do_phantram"] == 10
    assert task["trang_thai"] == "Đang thực hiện"


def test_create_task_with_ten_nhiem_vu_alias():
    """Kiểm tra tạo nhiệm vụ khi client truyền trường ten_nhiem_vu thay vì tieu_de -> 201 Created"""
    payload = {
        "ma_ho_so": 1,
        "ten_nhiem_vu": "TEST_Nhiệm vụ dùng alias ten_nhiem_vu",
        "han_hoan_thanh": "2026-11-20"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    res_data = response.json()

    task = res_data["data"]
    assert task["tieu_de"] == "TEST_Nhiệm vụ dùng alias ten_nhiem_vu"
    assert task["ten_nhiem_vu"] == "TEST_Nhiệm vụ dùng alias ten_nhiem_vu"


def test_create_task_ho_so_not_found_404():
    """Kiểm tra khi mã hồ sơ không tồn tại trong hệ thống -> 404 Not Found"""
    payload = {
        "ma_ho_so": 99999,
        "tieu_de": "TEST_Nhiệm vụ hồ sơ không tồn tại",
        "han_hoan_thanh": "2026-11-15"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 404
    res_data = response.json()
    assert "detail" in res_data
    assert "99999" in res_data["detail"]


def test_create_task_missing_title_422():
    """Kiểm tra khi không truyền trường tieu_de / ten_nhiem_vu -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "han_hoan_thanh": "2026-11-15"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_empty_title_422():
    """Kiểm tra khi tieu_de chỉ chứa khoảng trắng rỗng -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "tieu_de": "   ",
        "han_hoan_thanh": "2026-11-15"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_missing_deadline_422():
    """Kiểm tra khi thiếu hạn hoàn thành han_hoan_thanh -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "tieu_de": "TEST_Nhiệm vụ thiếu deadline"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_invalid_deadline_format_422():
    """Kiểm tra khi truyền hạn hoàn thành sai định dạng (không phải YYYY-MM-DD) -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "tieu_de": "TEST_Nhiệm vụ sai format ngày",
        "han_hoan_thanh": "15/11/2026"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_invalid_ma_ho_so_zero_or_negative_422():
    """Kiểm tra khi ma_ho_so <= 0 -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 0,
        "tieu_de": "TEST_Nhiệm vụ ma_ho_so bằng 0",
        "han_hoan_thanh": "2026-11-15"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422

    payload["ma_ho_so"] = -1
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_invalid_progress_percentage_422():
    """Kiểm tra khi truyền tiến độ < 0 hoặc > 100 -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "tieu_de": "TEST_Nhiệm vụ tiến độ âm",
        "han_hoan_thanh": "2026-11-15",
        "tien_do_phantram": -10
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422

    payload["tien_do_phantram"] = 105
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422
