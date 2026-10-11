import pytest
import sys
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ==============================================================
# TEST CASES CHO POST /api/v1/schedules
# ==============================================================

def test_create_schedule_success():
    """Kiểm tra tạo ca làm việc thành công với danh sách các ngày trong tuần (HTTP 201)"""
    payload = {
        "ten_ca": "Ca Tối Thực Tập",
        "gio_bat_dau": "18:00:00",
        "gio_ket_thuc": "21:30:00",
        "cac_ngay_trong_tuan": ["Thứ 2", "Thứ 4", "Thứ 6"],
        "ghi_chu": "Ca thực tập ngoài giờ",
        "trang_thai": "HoatDong"
    }
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 201
    res = response.json()

    assert res["status_code"] == 201
    assert "Tạo ca làm việc thành công" in res["message"]
    assert "data" in res

    data = res["data"]
    assert data["ma_ca"] > 0
    assert data["ten_ca"] == "Ca Tối Thực Tập"
    assert "18:00:00" in data["gio_bat_dau"]
    assert "21:30:00" in data["gio_ket_thuc"]
    assert "Thứ 2, Thứ 4, Thứ 6" in data["cac_ngay_trong_tuan"]
    assert data["ghi_chu"] == "Ca thực tập ngoài giờ"
    assert data["trang_thai"] == "HoatDong"


def test_create_schedule_string_days_success():
    """Kiểm tra tạo ca làm việc thành công khi truyền chuỗi các ngày trong tuần"""
    payload = {
        "ten_ca": "Ca Sáng Thứ 7",
        "gio_bat_dau": "08:30",
        "gio_ket_thuc": "11:30",
        "cac_ngay_trong_tuan": "Thứ 7",
        "ghi_chu": "Ca phụ đạo cuối tuần"
    }
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 201
    res = response.json()
    assert res["data"]["ten_ca"] == "Ca Sáng Thứ 7"
    assert res["data"]["cac_ngay_trong_tuan"] == "Thứ 7"


def test_create_schedule_end_time_before_start_time():
    """Kiểm tra validate: gio_ket_thuc < gio_bat_dau -> Trả về HTTP 422"""
    payload = {
        "ten_ca": "Ca Lỗi Thời Gian",
        "gio_bat_dau": "17:00:00",
        "gio_ket_thuc": "08:00:00",
        "cac_ngay_trong_tuan": ["Thứ 2", "Thứ 3"]
    }
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 422
    res = response.json()
    assert "detail" in res
    detail_str = str(res["detail"])
    assert "Giờ kết thúc phải lớn hơn giờ bắt đầu" in detail_str


def test_create_schedule_equal_times():
    """Kiểm tra validate: gio_ket_thuc == gio_bat_dau -> Trả về HTTP 422"""
    payload = {
        "ten_ca": "Ca Giờ Trùng",
        "gio_bat_dau": "08:00:00",
        "gio_ket_thuc": "08:00:00",
        "cac_ngay_trong_tuan": ["Thứ 2"]
    }
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 422
    res = response.json()
    assert "detail" in res
    detail_str = str(res["detail"])
    assert "Giờ kết thúc phải lớn hơn giờ bắt đầu" in detail_str


def test_create_schedule_empty_name():
    """Kiểm tra validate: ten_ca rỗng hoặc toàn khoảng trắng -> Trả về HTTP 422"""
    payload = {
        "ten_ca": "   ",
        "gio_bat_dau": "08:00:00",
        "gio_ket_thuc": "12:00:00",
        "cac_ngay_trong_tuan": ["Thứ 2"]
    }
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 422


def test_create_schedule_missing_required_fields():
    """Kiểm tra khi thiếu trường bắt buộc (ví dụ thiếu ten_ca hoặc gio_bat_dau) -> Trả về HTTP 422"""
    # Thiếu ten_ca
    payload1 = {
        "gio_bat_dau": "08:00:00",
        "gio_ket_thuc": "12:00:00",
        "cac_ngay_trong_tuan": ["Thứ 2"]
    }
    res1 = client.post("/api/v1/schedules", json=payload1)
    assert res1.status_code == 422

    # Thiếu gio_ket_thuc
    payload2 = {
        "ten_ca": "Ca Chiều",
        "gio_bat_dau": "13:00:00",
        "cac_ngay_trong_tuan": ["Thứ 2"]
    }
    res2 = client.post("/api/v1/schedules", json=payload2)
    assert res2.status_code == 422


def test_create_schedule_invalid_time_format():
    """Kiểm tra khi định dạng giờ không hợp lệ -> Trả về HTTP 422"""
    payload = {
        "ten_ca": "Ca Sai Định Dạng Giờ",
        "gio_bat_dau": "25:99:99",
        "gio_ket_thuc": "12:00:00",
        "cac_ngay_trong_tuan": ["Thứ 2"]
    }
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 422
