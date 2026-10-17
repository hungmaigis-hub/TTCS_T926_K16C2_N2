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
def scan_test_intern():
    """Tạo thực tập sinh độc lập phục vụ test quét mã định danh chấm công"""
    try:
        from tests.conftest import TestSessionLocal
        Session = TestSessionLocal
    except Exception:
        Session = SessionLocal

    db = Session()
    intern_id = 998
    user_id = 998
    try:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == intern_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == intern_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == user_id).delete()
        db.commit()

        user = NguoiDung(
            ma_nguoi_dung=user_id,
            ma_phong_ban=1,
            ho_ten="Thực Tập Sinh Quét Thẻ Test",
            email="scan_test_intern@example.com",
            so_dien_thoai="0988776655",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add(user)
        db.flush()

        ho_so = HoSoThucTap(
            ma_ho_so=intern_id,
            ma_nguoi_dung=user_id,
            ma_truong=1,
            ma_chuong_trinh=1,
            ma_mentor=3,
            chuyen_nganh="Công nghệ thông tin",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        db.add(ho_so)
        db.commit()
    finally:
        db.close()

    yield {
        "ma_ho_so": intern_id,
        "email": "scan_test_intern@example.com",
        "so_dien_thoai": "0988776655"
    }

    # Dọn dẹp sau test
    db = Session()
    try:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == intern_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == intern_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == user_id).delete()
        db.commit()
    finally:
        db.close()


# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/attendance/scan
# ==============================================================================

def test_scan_checkin_qr_on_time_success(scan_test_intern):
    """Kiểm tra quét mã QR check-in đúng giờ (trước 08:30) -> 200 OK, hanh_dong = 'CHECK_IN', trang_thai = 'DungGio'"""
    payload = {
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "phuong_thuc": "QR",
        "thoi_gian_quet": "2026-10-25T08:15:00",
        "ghi_chu": "Quét mã QR tại cổng vào"
    }
    response = client.post("/api/v1/attendance/scan", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert "Quét mã check-in thành công" in res_data["message"]

    data = res_data["data"]
    assert data["ma_ho_so"] == scan_test_intern["ma_ho_so"]
    assert data["hanh_dong"] == "CHECK_IN"
    assert data["trang_thai"] == "DungGio"
    assert data["phuong_thuc"] == "QR"
    assert data["ngay_cham_cong"] == "2026-10-25"
    assert "08:15" in data["gio_checkin"]
    assert "08:15" in data["gio_check_in"]
    assert data["gio_checkout"] is None
    assert data["ho_ten"] == "Thực Tập Sinh Quét Thẻ Test"


def test_scan_checkin_card_late_success(scan_test_intern):
    """Kiểm tra quẹt thẻ Card RFID check-in muộn (sau 08:30) -> 200 OK, hanh_dong = 'CHECK_IN', trang_thai = 'DiMuon'"""
    payload = {
        "ma_dinh_danh": f"CARD-{scan_test_intern['ma_ho_so']}",
        "phuong_thuc": "Card",
        "thoi_gian_quet": "2026-10-26T08:45:00",
        "ghi_chu": "Quẹt thẻ từ đầu đọc RFID"
    }
    response = client.post("/api/v1/attendance/scan", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    data = res_data["data"]
    assert data["hanh_dong"] == "CHECK_IN"
    assert data["trang_thai"] == "DiMuon"
    assert data["phuong_thuc"] == "Card"
    assert "08:45" in data["gio_checkin"]


def test_scan_checkin_default_qr_card_method(scan_test_intern):
    """Kiểm tra quét không truyền phương thức -> mặc định 'QR/Card'"""
    payload = {
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": "2026-10-27T08:00:00"
    }
    response = client.post("/api/v1/attendance/scan", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["phuong_thuc"] == "QR/Card"
    assert data["hanh_dong"] == "CHECK_IN"


def test_scan_by_email_or_phone_identifier(scan_test_intern):
    """Kiểm tra quét mã định danh dạng email hoặc số điện thoại sinh viên -> 200 OK"""
    # 1. Quét bằng email
    payload_email = {
        "ma_dinh_danh": scan_test_intern["email"],
        "thoi_gian_quet": "2026-10-28T08:20:00"
    }
    res_email = client.post("/api/v1/attendance/scan", json=payload_email)
    assert res_email.status_code == 200
    assert res_email.json()["data"]["ma_ho_so"] == scan_test_intern["ma_ho_so"]

    # 2. Quét bằng số điện thoại ở ngày khác
    payload_phone = {
        "ma_dinh_danh": scan_test_intern["so_dien_thoai"],
        "thoi_gian_quet": "2026-10-29T08:25:00"
    }
    res_phone = client.post("/api/v1/attendance/scan", json=payload_phone)
    assert res_phone.status_code == 200
    assert res_phone.json()["data"]["ma_ho_so"] == scan_test_intern["ma_ho_so"]


def test_scan_checkout_success(scan_test_intern):
    """Kiểm tra quy trình hoàn chỉnh: Quét lần 1 (Check-in) -> Quét lần 2 (Check-out) -> 200 OK"""
    date_str = "2026-10-30"

    # Lần 1: Check-in lúc 08:00
    client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T08:00:00",
        "phuong_thuc": "QR"
    })

    # Lần 2: Check-out lúc 17:30
    res_out = client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T17:30:00",
        "phuong_thuc": "QR",
        "ghi_chu": "Quét mã kết thúc ca"
    })
    assert res_out.status_code == 200
    data = res_out.json()["data"]
    assert data["hanh_dong"] == "CHECK_OUT"
    assert "08:00" in data["gio_checkin"]
    assert "17:30" in data["gio_checkout"]
    assert "17:30" in data["gio_check_out"]
    assert data["trang_thai"] == "DungGio"
    assert "Quét mã kết thúc ca" in data["ghi_chu"]


def test_scan_checkout_early_departure(scan_test_intern):
    """Kiểm tra quét check-out về sớm (trước 17:00) -> trang_thai chuyển sang 'VeSom'"""
    date_str = "2026-10-31"

    # Check-in 08:15 (DungGio)
    client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T08:15:00"
    })

    # Check-out 16:00 (về sớm)
    res_out = client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T16:00:00",
        "ghi_chu": "Xin về sớm"
    })
    assert res_out.status_code == 200
    data = res_out.json()["data"]
    assert data["hanh_dong"] == "CHECK_OUT"
    assert data["trang_thai"] == "VeSom"


def test_scan_checkout_before_checkin_rejected(scan_test_intern):
    """Kiểm tra thời gian quét check-out trước thời gian check-in -> 400 Bad Request"""
    date_str = "2026-11-01"

    # Check-in lúc 08:30
    client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T08:30:00"
    })

    # Quét với thời gian 07:00 (trước 08:30)
    res_out = client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T07:00:00"
    })
    assert res_out.status_code == 400
    assert "không thể trước thời gian check-in" in res_out.json()["detail"]


def test_scan_duplicate_immediate_scan_rejected(scan_test_intern):
    """Kiểm tra chặn quét trùng lặp ngay sau khi vừa check-in trong vòng 60 giây -> 400 Bad Request"""
    date_str = "2026-11-02"

    # Quét lần 1 lúc 08:00:00
    res1 = client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T08:00:00"
    })
    assert res1.status_code == 200

    # Quét lần 2 lúc 08:00:15 (sau 15 giây - quét đúp)
    res2 = client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T08:00:15"
    })
    assert res2.status_code == 400
    assert "không quét trùng lặp" in res2.json()["detail"]


def test_scan_duplicate_after_full_shift_rejected(scan_test_intern):
    """Kiểm tra chặn quét trùng lặp trong cùng ca khi đã hoàn tất cả check-in và check-out -> 400 Bad Request"""
    date_str = "2026-11-03"

    # 1. Check-in
    client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T08:00:00"
    })

    # 2. Check-out
    client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T17:30:00"
    })

    # 3. Quét lần thứ 3 trong cùng ngày/ca -> Bị chặn trùng lặp
    res3 = client.post("/api/v1/attendance/scan", json={
        "ma_dinh_danh": str(scan_test_intern["ma_ho_so"]),
        "thoi_gian_quet": f"{date_str}T18:00:00"
    })
    assert res3.status_code == 400
    assert "Không thể quét trùng lặp" in res3.json()["detail"]


def test_scan_empty_identifier_rejected():
    """Kiểm tra mã định danh rỗng hoặc khoảng trắng -> 422 Unprocessable Entity"""
    payload = {
        "ma_dinh_danh": "   "
    }
    response = client.post("/api/v1/attendance/scan", json=payload)
    assert response.status_code == 422


def test_scan_identifier_not_found():
    """Kiểm tra mã định danh không tồn tại -> 404 Not Found"""
    payload = {
        "ma_dinh_danh": "UNKNOWN_CODE_999999"
    }
    response = client.post("/api/v1/attendance/scan", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]


def test_scan_intern_not_approved_rejected():
    """Kiểm tra sinh viên chưa được duyệt hồ sơ ('ChoDuyet') -> 400 Bad Request theo quy tắc TTCS"""
    try:
        from tests.conftest import TestSessionLocal
        Session = TestSessionLocal
    except Exception:
        Session = SessionLocal

    db = Session()
    unapproved_id = 997
    try:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == unapproved_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == unapproved_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == unapproved_id).delete()
        db.commit()

        user = NguoiDung(
            ma_nguoi_dung=unapproved_id,
            ho_ten="Sinh Viên Chưa Duyệt",
            email="unapproved@example.com",
            so_dien_thoai="0911223344",
            vai_tro="ThucTapSinh"
        )
        db.add(user)
        db.flush()

        ho_so = HoSoThucTap(
            ma_ho_so=unapproved_id,
            ma_nguoi_dung=unapproved_id,
            trang_thai_xet_duyet="ChoDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        db.add(ho_so)
        db.commit()

        payload = {
            "ma_dinh_danh": str(unapproved_id)
        }
        response = client.post("/api/v1/attendance/scan", json=payload)
        assert response.status_code == 400
        assert "chưa được phê duyệt" in response.json()["detail"]
    finally:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == unapproved_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == unapproved_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == unapproved_id).delete()
        db.commit()
        db.close()


def test_scan_intern_dropped_out_rejected():
    """Kiểm tra sinh viên đã thôi học ('ThoiHoc') -> 400 Bad Request"""
    try:
        from tests.conftest import TestSessionLocal
        Session = TestSessionLocal
    except Exception:
        Session = SessionLocal

    db = Session()
    dropped_id = 996
    try:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == dropped_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == dropped_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == dropped_id).delete()
        db.commit()

        user = NguoiDung(
            ma_nguoi_dung=dropped_id,
            ho_ten="Sinh Viên Thôi Học",
            email="dropped@example.com",
            so_dien_thoai="0922334455",
            vai_tro="ThucTapSinh"
        )
        db.add(user)
        db.flush()

        ho_so = HoSoThucTap(
            ma_ho_so=dropped_id,
            ma_nguoi_dung=dropped_id,
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="ThoiHoc"
        )
        db.add(ho_so)
        db.commit()

        payload = {
            "ma_dinh_danh": str(dropped_id)
        }
        response = client.post("/api/v1/attendance/scan", json=payload)
        assert response.status_code == 400
        assert "đã thôi học" in response.json()["detail"]
    finally:
        db.query(ChamCong).filter(ChamCong.ma_ho_so == dropped_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == dropped_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == dropped_id).delete()
        db.commit()
        db.close()


def test_model_cham_cong_synonym_and_dict():
    """Kiểm tra model ChamCong hỗ trợ gio_checkin, gio_checkout, synonym tương thích ngược và to_dict()"""
    cc = ChamCong(
        ma_cham_cong=100,
        ma_ho_so=1,
        ngay_cham_cong=date(2026, 10, 20),
        gio_checkin=time(8, 15, 0),
        gio_checkout=time(17, 30, 0),
        phuong_thuc="QR/Card",
        trang_thai="DungGio"
    )
    # Kiểm tra truy cập qua synonym
    assert cc.gio_check_in == time(8, 15, 0)
    assert cc.gio_check_out == time(17, 30, 0)

    # Kiểm tra to_dict
    d = cc.to_dict()
    assert d["gio_checkin"] == "08:15:00"
    assert d["gio_checkout"] == "17:30:00"
    assert d["gio_check_in"] == "08:15:00"
    assert d["gio_check_out"] == "17:30:00"
    assert d["phuong_thuc"] == "QR/Card"
    assert d["trang_thai"] == "DungGio"
