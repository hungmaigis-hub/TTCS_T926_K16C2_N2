import pytest
import sys
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ==============================================================
# TEST CASES CHO GET /api/v1/interns/my-schedule
# ==============================================================

def test_get_my_schedule_success():
    """Kiểm tra lấy thành công lịch trình và nhiệm vụ của thực tập sinh (ID 1)"""
    response = client.get("/api/v1/interns/my-schedule?ho_so_id=1")
    assert response.status_code == 200
    res = response.json()

    assert res["status_code"] == 200
    assert "data" in res
    data = res["data"]
    
    # Kiểm tra các trường dữ liệu quan trọng
    assert data["ma_ho_so"] == 1
    assert "ngay_bat_dau" in data
    assert "ngay_ket_thuc" in data
    assert "danh_sach_nhiem_vu" in data
    assert isinstance(data["danh_sach_nhiem_vu"], list)


def test_get_my_schedule_not_found():
    """Kiểm tra khi tìm kiếm mã hồ sơ không tồn tại -> Trả về HTTP 404"""
    response = client.get("/api/v1/interns/my-schedule?ho_so_id=99999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_my_schedule_missing_param():
    """Kiểm tra khi không truyền tham số bắt buộc ho_so_id -> Trả về HTTP 422"""
    response = client.get("/api/v1/interns/my-schedule")
    assert response.status_code == 422


def test_get_my_schedule_invalid_id():
    """Kiểm tra khi ho_so_id là chữ thay vì số -> Trả về HTTP 422"""
    response = client.get("/api/v1/interns/my-schedule?ho_so_id=abc")
    assert response.status_code == 422
