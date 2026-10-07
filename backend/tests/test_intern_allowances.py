import pytest
import sys
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import get_db
from database.models import HoSoThucTap, NguoiDung

client = TestClient(app)

# ==============================================================
# BỘ KIỂM THỬ CHO API: GET /api/v1/interns/{id}/allowances
# ==============================================================

def test_get_intern_allowances_success_intern_1():
    """
    Kiểm tra lấy thành công danh sách phụ cấp của thực tập sinh ID 1:
    - Đã nhận 2 khoản (2026-09, 2026-10): 3.000.000 + 3.000.000 = 6.000.000 VNĐ
    - Chờ giải ngân 1 khoản (2026-11): 3.500.000 VNĐ
    - Tổng phụ cấp: 9.500.000 VNĐ
    """
    response = client.get("/api/v1/interns/1/allowances")
    assert response.status_code == 200

    res = response.json()
    assert res["status_code"] == 200
    assert "data" in res

    data = res["data"]
    assert data["ma_ho_so"] == 1
    assert data["ho_ten"] == "Nguyễn Văn A"
    assert data["email"] == "vana@example.com"

    summary = data["summary"]
    assert summary["tong_tien_da_nhan"] == 6000000.0
    assert summary["tong_tien_cho_giai_ngan"] == 3500000.0
    assert summary["tong_tien_phu_cap"] == 9500000.0
    assert summary["so_khoan_da_nhan"] == 2
    assert summary["so_khoan_cho_giai_ngan"] == 1

    # Kiểm tra danh sách chi tiết
    danh_sach = data["danh_sach_phu_cap"]
    assert len(danh_sach) == 3
    assert len(data["cac_khoan_da_nhan"]) == 2
    assert len(data["cac_khoan_cho_giai_ngan"]) == 1

    # Kiểm tra thứ tự sắp xếp giảm dần theo tháng
    assert danh_sach[0]["thang_nam"] == "2026-11"
    assert danh_sach[0]["trang_thai_chi_tra"] == "ChuaChiTra"
    assert danh_sach[1]["thang_nam"] == "2026-10"
    assert danh_sach[2]["thang_nam"] == "2026-09"


def test_get_intern_allowances_success_intern_2():
    """
    Kiểm tra lấy thành công danh sách phụ cấp của thực tập sinh ID 2:
    - Đã nhận 1 khoản (2026-09): 2.500.000 VNĐ
    - Chờ giải ngân 1 khoản (2026-10): 2.500.000 VNĐ
    - Tổng phụ cấp: 5.000.000 VNĐ
    """
    response = client.get("/api/v1/interns/2/allowances")
    assert response.status_code == 200

    res = response.json()
    data = res["data"]
    assert data["ma_ho_so"] == 2
    assert data["ho_ten"] == "Trần Thị B"

    summary = data["summary"]
    assert summary["tong_tien_da_nhan"] == 2500000.0
    assert summary["tong_tien_cho_giai_ngan"] == 2500000.0
    assert summary["tong_tien_phu_cap"] == 5000000.0
    assert summary["so_khoan_da_nhan"] == 1
    assert summary["so_khoan_cho_giai_ngan"] == 1


def test_get_intern_allowances_empty_list():
    """
    Kiểm tra khi thực tập sinh tồn tại nhưng chưa có khoản phụ cấp nào:
    - Tổng tiền các khoản đều bằng 0
    - Danh sách các khoản phụ cấp là mảng rỗng []
    """
    # Tạo thực tập sinh mới chưa có phụ cấp
    db = next(app.dependency_overrides[get_db]())
    try:
        user = NguoiDung(
            ma_nguoi_dung=10,
            ho_ten="Lê Văn Trắng",
            email="trang@example.com",
            so_dien_thoai="0933333333",
            vai_tro="ThucTapSinh"
        )
        db.add(user)
        db.flush()

        ho_so = HoSoThucTap(
            ma_ho_so=10,
            ma_nguoi_dung=user.ma_nguoi_dung,
            chuyen_nganh="An toàn thông tin",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        db.add(ho_so)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/interns/10/allowances")
    assert response.status_code == 200

    res = response.json()
    data = res["data"]
    assert data["ma_ho_so"] == 10
    assert data["ho_ten"] == "Lê Văn Trắng"

    summary = data["summary"]
    assert summary["tong_tien_da_nhan"] == 0.0
    assert summary["tong_tien_cho_giai_ngan"] == 0.0
    assert summary["tong_tien_phu_cap"] == 0.0
    assert summary["so_khoan_da_nhan"] == 0
    assert summary["so_khoan_cho_giai_ngan"] == 0

    assert data["danh_sach_phu_cap"] == []
    assert data["cac_khoan_da_nhan"] == []
    assert data["cac_khoan_cho_giai_ngan"] == []


def test_get_intern_allowances_not_found():
    """Kiểm tra khi mã hồ sơ không tồn tại trong hệ thống -> Trả về HTTP 404"""
    response = client.get("/api/v1/interns/99999/allowances")
    assert response.status_code == 404
    assert "Không tìm thấy thực tập sinh ID: 99999" in response.json()["detail"]


def test_get_intern_allowances_invalid_id():
    """Kiểm tra khi ID không phải là số nguyên -> Trả về HTTP 422 Unprocessable Entity"""
    response = client.get("/api/v1/interns/abc/allowances")
    assert response.status_code == 422
