import sys
from pathlib import Path
from datetime import datetime, date, time
import pytest

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import ChamCong, HoSoThucTap, NguoiDung

client = TestClient(app)


@pytest.fixture
def attendance_test_intern():
    """Tạo thực tập sinh độc lập phục vụ test chấm công và tự dọn dẹp sau khi kiểm thử"""
    try:
        from tests.conftest import TestSessionLocal
        Session = TestSessionLocal
    except Exception:
        Session = SessionLocal

    db = Session()
    intern_id = 888
    try:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == intern_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == intern_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_id).delete()
        db.commit()

        user = NguoiDung(
            ma_nguoi_dung=intern_id,
            ma_phong_ban=1,
            ho_ten="Sinh Viên Test Chấm Công",
            email="attendance_test@example.com",
            so_dien_thoai="0944888777",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add(user)
        db.flush()

        ho_so = HoSoThucTap(
            ma_ho_so=intern_id,
            ma_nguoi_dung=intern_id,
            ma_truong=1,
            ma_chuong_trinh=1,
            ma_mentor=3,
            chuyen_nganh="Khoa học dữ liệu",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        db.add(ho_so)
        db.commit()
    finally:
        db.close()

    yield intern_id

    # Dọn dẹp sau test
    db = Session()
    try:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == intern_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == intern_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_id).delete()
        db.commit()
    finally:
        db.close()


# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/attendance/check-in
# ==============================================================================

def test_checkin_on_time_success(attendance_test_intern):
    """Kiểm tra check-in đúng giờ (trước 08:30) -> 201 Created, trang_thai = 'DungGio'"""
    checkin_dt = "2026-10-15T08:15:00"
    payload = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": checkin_dt,
        "phuong_thuc": "Web",
        "ghi_chu": "Đi làm đúng giờ"
    }
    response = client.post("/api/v1/attendance/check-in", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status_code"] == 201
    assert res_data["message"] == "Check-in thành công"
    assert "data" in res_data

    item = res_data["data"]
    assert item["ma_ho_so"] == attendance_test_intern
    assert item["ngay_cham_cong"] == "2026-10-15"
    assert item["trang_thai"] == "DungGio"
    assert "08:15" in item["gio_check_in"]
    assert item["phuong_thuc"] == "Web"
    assert item["thoi_gian_checkout"] is None


def test_checkin_late_success(attendance_test_intern):
    """Kiểm tra check-in muộn (sau 08:30) -> 201 Created, trang_thai = 'DiMuon'"""
    checkin_dt = "2026-10-16T08:45:30"
    payload = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": checkin_dt,
        "phuong_thuc": "QR",
        "ghi_chu": "Tắc đường tuyến QL3"
    }
    response = client.post("/api/v1/attendance/check-in", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    item = res_data["data"]
    assert item["trang_thai"] == "DiMuon"
    assert "08:45" in item["gio_check_in"]
    assert item["phuong_thuc"] == "QR"


def test_checkin_default_current_time(attendance_test_intern):
    """Kiểm tra check-in khi không truyền thoi_gian_checkin -> tự động lấy thời gian hiện tại"""
    payload = {
        "ma_ho_so": attendance_test_intern
    }
    response = client.post("/api/v1/attendance/check-in", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    item = res_data["data"]
    assert item["ma_ho_so"] == attendance_test_intern
    assert item["thoi_gian_checkin"] is not None
    assert item["gio_check_in"] is not None


def test_checkin_duplicate_same_day_rejected(attendance_test_intern):
    """Kiểm tra check-in 2 lần trong cùng một ngày -> 400 Bad Request"""
    payload = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": "2026-10-17T08:00:00"
    }
    # Lần 1: thành công
    res1 = client.post("/api/v1/attendance/check-in", json=payload)
    assert res1.status_code == 201

    # Lần 2: bị từ chối
    res2 = client.post("/api/v1/attendance/check-in", json=payload)
    assert res2.status_code == 400
    assert "đã thực hiện check-in" in res2.json()["detail"]


def test_checkin_intern_not_found():
    """Kiểm tra mã hồ sơ không tồn tại -> 404 Not Found"""
    payload = {
        "ma_ho_so": 999999,
        "thoi_gian_checkin": "2026-10-15T08:00:00"
    }
    response = client.post("/api/v1/attendance/check-in", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]


def test_checkin_invalid_negative_intern_id():
    """Kiểm tra mã hồ sơ số âm -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": -5
    }
    response = client.post("/api/v1/attendance/check-in", json=payload)
    assert response.status_code == 422


# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/attendance/check-out
# ==============================================================================

def test_checkout_success(attendance_test_intern):
    """Kiểm tra check-out sau khi đã check-in thành công -> 200 OK, cập nhật thoi_gian_checkout"""
    # 1. Check-in lúc 08:00
    client.post("/api/v1/attendance/check-in", json={
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": "2026-10-18T08:00:00"
    })

    # 2. Check-out lúc 17:30
    payload_out = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkout": "2026-10-18T17:30:00",
        "ghi_chu": "Hoàn thành ca làm việc"
    }
    response = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["message"] == "Check-out thành công"
    item = res_data["data"]
    assert "17:30" in item["gio_check_out"]
    assert item["thoi_gian_checkout"] is not None
    assert "Hoàn thành ca làm việc" in item["ghi_chu"]


def test_checkout_early_departure(attendance_test_intern):
    """Kiểm tra check-out về sớm (trước 17:00) -> 200 OK, cập nhật trang_thai = 'VeSom'"""
    # 1. Check-in đúng giờ 08:00
    client.post("/api/v1/attendance/check-in", json={
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": "2026-10-19T08:00:00"
    })

    # 2. Check-out lúc 16:00
    payload_out = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkout": "2026-10-19T16:00:00",
        "ghi_chu": "Xin về sớm có việc riêng"
    }
    response = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert response.status_code == 200
    res_data = response.json()
    item = res_data["data"]
    assert item["trang_thai"] == "VeSom"


def test_checkout_without_checkin_rejected(attendance_test_intern):
    """Kiểm tra check-out khi chưa từng check-in trong ngày -> 400 Bad Request"""
    payload_out = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkout": "2026-10-20T17:30:00"
    }
    response = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert response.status_code == 400
    assert "chưa thực hiện check-in" in response.json()["detail"]


def test_checkout_duplicate_rejected(attendance_test_intern):
    """Kiểm tra check-out 2 lần trong 1 ngày -> 400 Bad Request"""
    # 1. Check-in
    client.post("/api/v1/attendance/check-in", json={
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": "2026-10-21T08:00:00"
    })

    # 2. Check-out lần 1: thành công
    payload_out = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkout": "2026-10-21T17:30:00"
    }
    res1 = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert res1.status_code == 200

    # 3. Check-out lần 2: bị từ chối
    res2 = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert res2.status_code == 400
    assert "đã hoàn thành check-out" in res2.json()["detail"]


def test_checkout_before_checkin_time_rejected(attendance_test_intern):
    """Kiểm tra thời gian check-out trước thời gian check-in -> 400 Bad Request"""
    client.post("/api/v1/attendance/check-in", json={
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": "2026-10-22T08:30:00"
    })

    payload_out = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkout": "2026-10-22T07:15:00"
    }
    response = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert response.status_code == 400
    assert "không thể trước thời gian check-in" in response.json()["detail"]


def test_checkout_intern_not_found():
    """Kiểm tra check-out với mã hồ sơ không tồn tại -> 404 Not Found"""
    payload_out = {
        "ma_ho_so": 999999,
        "thoi_gian_checkout": "2026-10-23T17:30:00"
    }
    response = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]


def test_checkout_invalid_negative_intern_id():
    """Kiểm tra check-out với mã hồ sơ số âm -> 422 Unprocessable Entity"""
    payload_out = {
        "ma_ho_so": -10
    }
    response = client.post("/api/v1/attendance/check-out", json=payload_out)
    assert response.status_code == 422


def test_full_flow_checkin_and_checkout(attendance_test_intern):
    """Kiểm tra chu trình hoàn chỉnh: Check-in sáng và Check-out chiều cùng ngày"""
    date_str = "2026-10-24"
    in_payload = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkin": f"{date_str}T08:10:00",
        "phuong_thuc": "Web",
        "ghi_chu": "Bắt đầu ngày làm việc on-site"
    }
    in_res = client.post("/api/v1/attendance/check-in", json=in_payload)
    assert in_res.status_code == 201

    out_payload = {
        "ma_ho_so": attendance_test_intern,
        "thoi_gian_checkout": f"{date_str}T17:35:00",
        "ghi_chu": "Đã bàn giao task cuối ngày"
    }
    out_res = client.post("/api/v1/attendance/check-out", json=out_payload)
    assert out_res.status_code == 200
    data = out_res.json()["data"]
    assert data["ngay_cham_cong"] == date_str
    assert "08:10" in data["gio_check_in"]
    assert "17:35" in data["gio_check_out"]
    assert data["trang_thai"] == "DungGio"
    assert "Bắt đầu ngày làm việc" in data["ghi_chu"]
    assert "Đã bàn giao task" in data["ghi_chu"]
