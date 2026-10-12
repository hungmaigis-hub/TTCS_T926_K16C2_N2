import pytest
import sys
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import get_db
from database.models import PhuCap

client = TestClient(app)

# ==============================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/allowances
# ==============================================================

def test_create_allowance_success_full():
    """Kiểm tra tạo phụ cấp thành công với đầy đủ các trường (HTTP 201)"""
    payload = {
        "ma_ho_so": 1,
        "thang": 12,
        "nam": 2026,
        "so_tien": 4000000.0,
        "ngay_chi_tra": "2026-12-25",
        "trang_thai": "ChuaChiTra"
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 201

    res = response.json()
    assert res["status_code"] == 201
    assert "data" in res

    data = res["data"]
    assert data["ma_ho_so"] == 1
    assert data["thang"] == 12
    assert data["nam"] == 2026
    assert data["thang_nam"] == "2026-12"
    assert data["so_tien"] == 4000000.0
    assert data["ngay_chi_tra"] == "2026-12-25"
    assert data["trang_thai"] == "ChuaChiTra"
    assert "ma_phu_cap" in data


def test_create_allowance_success_defaults():
    """Kiểm tra tạo phụ cấp với các trường mặc định (ngay_chi_tra = None, trang_thai mặc định)"""
    payload = {
        "ma_ho_so": 2,
        "thang": 12,
        "nam": 2026,
        "so_tien": 3000000.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 201

    res = response.json()
    data = res["data"]
    assert data["ma_ho_so"] == 2
    assert data["thang"] == 12
    assert data["nam"] == 2026
    assert data["so_tien"] == 3000000.0
    assert data["ngay_chi_tra"] is None
    assert data["trang_thai"] == "ChuaChiTra"


def test_create_allowance_intern_not_found():
    """Kiểm tra báo lỗi HTTP 404 khi ma_ho_so không tồn tại trong CSDL"""
    payload = {
        "ma_ho_so": 99999,
        "thang": 1,
        "nam": 2026,
        "so_tien": 3000000.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]


def test_create_allowance_invalid_so_tien_zero():
    """Kiểm tra báo lỗi HTTP 422 khi so_tien = 0 (phải > 0)"""
    payload = {
        "ma_ho_so": 1,
        "thang": 1,
        "nam": 2026,
        "so_tien": 0.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 422


def test_create_allowance_invalid_so_tien_negative():
    """Kiểm tra báo lỗi HTTP 422 khi so_tien âm"""
    payload = {
        "ma_ho_so": 1,
        "thang": 1,
        "nam": 2026,
        "so_tien": -1500000.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 422


def test_create_allowance_invalid_thang_zero():
    """Kiểm tra báo lỗi HTTP 422 khi thang = 0 (< 1)"""
    payload = {
        "ma_ho_so": 1,
        "thang": 0,
        "nam": 2026,
        "so_tien": 3000000.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 422


def test_create_allowance_invalid_thang_greater_than_12():
    """Kiểm tra báo lỗi HTTP 422 khi thang = 13 (> 12)"""
    payload = {
        "ma_ho_so": 1,
        "thang": 13,
        "nam": 2026,
        "so_tien": 3000000.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 422


def test_create_allowance_duplicate_month_year():
    """Kiểm tra báo lỗi HTTP 400 khi tạo trùng khoản phụ cấp cùng kỳ (tháng, năm) cho cùng 1 sinh viên"""
    # Hồ sơ 1 đã có phụ cấp tháng 09/2026 trong seed data
    payload = {
        "ma_ho_so": 1,
        "thang": 9,
        "nam": 2026,
        "so_tien": 2000000.0
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 400
    assert "đã tồn tại" in response.json()["detail"]


def test_create_allowance_invalid_date_format():
    """Kiểm tra báo lỗi HTTP 422 khi sai định dạng ngày chi trả"""
    payload = {
        "ma_ho_so": 1,
        "thang": 5,
        "nam": 2027,
        "so_tien": 3000000.0,
        "ngay_chi_tra": "25-12-2027"
    }
    response = client.post("/api/v1/allowances", json=payload)
    assert response.status_code == 422


def test_create_allowance_missing_required_fields():
    """Kiểm tra báo lỗi HTTP 422 khi thiếu các trường bắt buộc"""
    response = client.post("/api/v1/allowances", json={"thang": 5})
    assert response.status_code == 422
