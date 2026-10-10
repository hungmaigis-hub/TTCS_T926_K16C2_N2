import pytest
import sys
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import get_db
from database.models import NguoiDung, HoSoThucTap

client = TestClient(app)

# ==============================================================
# BỘ KIỂM THỬ CHO API: GET /api/v1/mentors/workload
# ==============================================================

def test_get_mentor_workload_default_success():
    """Kiểm tra gọi API lấy workload mentor mặc định thành công (HTTP 200)"""
    response = client.get("/api/v1/mentors/workload")
    assert response.status_code == 200

    res = response.json()
    assert res["status_code"] == 200
    assert "thành công" in res["message"]
    assert "data" in res

    data = res["data"]
    summary = data["summary"]
    danh_sach = data["danh_sach_workload"]

    assert summary["tong_so_mentor"] >= 2
    assert summary["tong_so_thuc_tap_sinh_duoc_huong_dan"] == 2
    assert summary["so_mentor_chua_co_sinh_vien"] >= 1
    assert summary["mentor_nhieu_sinh_vien_nhat"] == "Nguyễn Hướng Dẫn"
    assert len(danh_sach) >= 2


def test_mentor_with_interns_counted_correctly():
    """Kiểm tra mentor đang phụ trách sinh viên (ID 3) có đúng số lượng = 2"""
    response = client.get("/api/v1/mentors/workload")
    assert response.status_code == 200

    danh_sach = response.json()["data"]["danh_sach_workload"]
    mentor_3 = next((m for m in danh_sach if m["ma_mentor"] == 3), None)
    assert mentor_3 is not None
    assert mentor_3["ho_ten"] == "Nguyễn Hướng Dẫn"
    assert mentor_3["so_luong_thuc_tap_sinh"] == 2
    assert mentor_3["ten_phong_ban"] == "Trung tâm Phần mềm"


def test_mentor_zero_interns_outerjoin_preserved():
    """Kiểm tra cơ chế LEFT OUTER JOIN: mentor chưa có sinh viên (ID 4) vẫn xuất hiện với số lượng = 0"""
    response = client.get("/api/v1/mentors/workload")
    assert response.status_code == 200

    danh_sach = response.json()["data"]["danh_sach_workload"]
    mentor_4 = next((m for m in danh_sach if m["ma_mentor"] == 4), None)
    assert mentor_4 is not None
    assert mentor_4["ho_ten"] == "Lê Thị Mentor"
    assert mentor_4["so_luong_thuc_tap_sinh"] == 0


def test_filter_by_phong_ban_success_and_not_found():
    """Kiểm tra lọc theo phòng ban hợp lệ và báo lỗi 404 khi phòng ban không tồn tại"""
    # Phòng ban 1 tồn tại
    res1 = client.get("/api/v1/mentors/workload", params={"ma_phong_ban": 1})
    assert res1.status_code == 200
    for m in res1.json()["data"]["danh_sach_workload"]:
        assert m["ma_phong_ban"] == 1

    # Phòng ban 9999 không tồn tại -> 404
    res2 = client.get("/api/v1/mentors/workload", params={"ma_phong_ban": 9999})
    assert res2.status_code == 404
    assert "Phòng ban không tồn tại" in res2.json()["detail"]


def test_filter_by_tu_khoa():
    """Kiểm tra tìm kiếm mentor theo từ khóa họ tên hoặc email"""
    res = client.get("/api/v1/mentors/workload", params={"tu_khoa": "mentor2@example.com"})
    assert res.status_code == 200
    danh_sach = res.json()["data"]["danh_sach_workload"]
    assert len(danh_sach) == 1
    assert danh_sach[0]["email"] == "mentor2@example.com"


def test_filter_by_trang_thai():
    """Kiểm tra lọc theo trạng thái hoạt động và bắt lỗi 400 khi truyền trạng thái không hợp lệ"""
    # Hợp lệ
    res = client.get("/api/v1/mentors/workload", params={"trang_thai": "HoatDong"})
    assert res.status_code == 200

    # Không hợp lệ
    res_err = client.get("/api/v1/mentors/workload", params={"trang_thai": "TrangThaiSai"})
    assert res_err.status_code == 400
    assert "Trạng thái không hợp lệ" in res_err.json()["detail"]


def test_workload_summary_kpi_metrics():
    """Kiểm tra tính toán chính xác các chỉ số KPI summary"""
    res = client.get("/api/v1/mentors/workload")
    assert res.status_code == 200

    summary = res.json()["data"]["summary"]
    danh_sach = res.json()["data"]["danh_sach_workload"]

    assert summary["tong_so_mentor"] == len(danh_sach)
    expected_sum = sum(m["so_luong_thuc_tap_sinh"] for m in danh_sach)
    assert summary["tong_so_thuc_tap_sinh_duoc_huong_dan"] == expected_sum

    expected_avg = round(expected_sum / len(danh_sach), 2)
    assert summary["trung_binh_sinh_vien_moi_mentor"] == expected_avg
