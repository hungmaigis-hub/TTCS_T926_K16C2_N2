import sys
from pathlib import Path
import pytest

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: PATCH /api/v1/tasks/{id}/progress
# ==============================================================================

def test_update_task_progress_to_100_percent_auto_complete():
    """Kiểm tra khi tiến độ đạt 100%, hệ thống tự động đổi trạng thái sang 'Hoàn thành' -> 200 OK"""
    payload = {"tien_do_phantram": 100}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["message"] == "Cập nhật tiến độ nhiệm vụ thành công"
    assert "data" in res_data

    task = res_data["data"]
    assert task["ma_nhiem_vu"] == 1
    assert task["tien_do_phantram"] == 100
    assert task["trang_thai"] == "Hoàn thành"


def test_update_task_progress_in_progress():
    """Kiểm tra khi cập nhật tiến độ trong khoảng (0, 100), trạng thái chuyển sang 'Đang thực hiện' -> 200 OK"""
    # Nhiệm vụ 2 ban đầu là 0% ("Chưa bắt đầu")
    payload = {"tien_do_phantram": 60}
    response = client.patch("/api/v1/tasks/2/progress", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200

    task = res_data["data"]
    assert task["ma_nhiem_vu"] == 2
    assert task["tien_do_phantram"] == 60
    assert task["trang_thai"] == "Đang thực hiện"


def test_update_task_progress_to_zero():
    """Kiểm tra khi tiến độ bằng 0%, trạng thái chuyển sang 'Chưa bắt đầu' -> 200 OK"""
    payload = {"tien_do_phantram": 0}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    task = res_data["data"]
    assert task["ma_nhiem_vu"] == 1
    assert task["tien_do_phantram"] == 0
    assert task["trang_thai"] == "Chưa bắt đầu"


def test_update_task_progress_from_100_down_to_in_progress():
    """Kiểm tra khi giảm tiến độ từ 100% ('Hoàn thành') về 75%, trạng thái đổi về 'Đang thực hiện' -> 200 OK"""
    # Nhiệm vụ 3 ban đầu là 100% ("Hoàn thành")
    payload = {"tien_do_phantram": 75}
    response = client.patch("/api/v1/tasks/3/progress", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    task = res_data["data"]
    assert task["ma_nhiem_vu"] == 3
    assert task["tien_do_phantram"] == 75
    assert task["trang_thai"] == "Đang thực hiện"


def test_update_task_progress_not_found_404():
    """Kiểm tra khi cập nhật nhiệm vụ không tồn tại -> 404 Not Found"""
    payload = {"tien_do_phantram": 50}
    response = client.patch("/api/v1/tasks/99999/progress", json=payload)
    assert response.status_code == 404
    res_data = response.json()
    assert "detail" in res_data
    assert "99999" in res_data["detail"]


def test_update_task_progress_negative_percent_422():
    """Kiểm tra khi truyền tiến độ âm (< 0) -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": -1}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_exceed_100_percent_422():
    """Kiểm tra khi truyền tiến độ vượt quá 100 (> 100) -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": 105}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_invalid_type_string_422():
    """Kiểm tra khi truyền tiến độ là chuỗi chữ không hợp lệ -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": "mot_tram"}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_missing_body_field_422():
    """Kiểm tra khi không truyền trường tien_do_phantram trong body -> 422 Unprocessable Entity"""
    payload = {}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_null_value_422():
    """Kiểm tra khi truyền giá trị null -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": None}
    response = client.patch("/api/v1/tasks/1/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_invalid_id_zero_422():
    """Kiểm tra khi truyền ID = 0 -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": 50}
    response = client.patch("/api/v1/tasks/0/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_invalid_id_negative_422():
    """Kiểm tra khi truyền ID âm -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": 50}
    response = client.patch("/api/v1/tasks/-10/progress", json=payload)
    assert response.status_code == 422


def test_update_task_progress_invalid_id_string_422():
    """Kiểm tra khi truyền ID dạng chuỗi chữ -> 422 Unprocessable Entity"""
    payload = {"tien_do_phantram": 50}
    response = client.patch("/api/v1/tasks/abc/progress", json=payload)
    assert response.status_code == 422
