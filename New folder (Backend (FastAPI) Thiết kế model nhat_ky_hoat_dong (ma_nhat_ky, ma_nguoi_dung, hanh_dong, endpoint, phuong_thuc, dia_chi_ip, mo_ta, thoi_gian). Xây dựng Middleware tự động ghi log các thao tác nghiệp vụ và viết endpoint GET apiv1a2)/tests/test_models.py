from datetime import datetime
import pytest
from app.models.nguoi_dung import NguoiDung
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong


def test_nhat_ky_hoat_dong_model_fields():
    """Kiểm tra sự tồn tại đầy đủ các thuộc tính theo yêu cầu bài toán"""
    expected_fields = [
        "ma_nhat_ky",
        "ma_nguoi_dung",
        "hanh_dong",
        "endpoint",
        "phuong_thuc",
        "dia_chi_ip",
        "mo_ta",
        "thoi_gian",
    ]
    for field in expected_fields:
        assert hasattr(NhatKyHoatDong, field), f"Model NhatKyHoatDong thiếu trường: {field}"


def test_create_nhat_ky_hoat_dong(db_session, admin_user):
    """Kiểm tra việc lưu và truy xuất bản ghi nhat_ky_hoat_dong"""
    log_entry = NhatKyHoatDong(
        ma_nguoi_dung=admin_user.ma_nguoi_dung,
        hanh_dong="TAO_NGUOI_DUNG",
        endpoint="/api/v1/admin/users",
        phuong_thuc="POST",
        dia_chi_ip="192.168.1.50",
        mo_ta="Tạo tài khoản thử nghiệm cho thực tập sinh",
        thoi_gian=datetime.utcnow()
    )
    db_session.add(log_entry)
    db_session.commit()
    db_session.refresh(log_entry)

    assert log_entry.ma_nhat_ky is not None
    assert log_entry.ma_nhat_ky > 0
    assert log_entry.ma_nguoi_dung == admin_user.ma_nguoi_dung
    assert log_entry.hanh_dong == "TAO_NGUOI_DUNG"
    assert log_entry.endpoint == "/api/v1/admin/users"
    assert log_entry.phuong_thuc == "POST"
    assert log_entry.dia_chi_ip == "192.168.1.50"
    assert "thực tập sinh" in log_entry.mo_ta
    assert isinstance(log_entry.thoi_gian, datetime)


def test_nhat_ky_hoat_dong_anonymous(db_session):
    """Kiểm tra bản ghi hoạt động cho thao tác vô danh (ma_nguoi_dung = None)"""
    log_entry = NhatKyHoatDong(
        ma_nguoi_dung=None,
        hanh_dong="DANG_NHAP_THAT_BAI",
        endpoint="/api/v1/auth/login",
        phuong_thuc="POST",
        dia_chi_ip="113.20.10.5",
        mo_ta="Thử đăng nhập sai mật khẩu 3 lần",
        thoi_gian=datetime.utcnow()
    )
    db_session.add(log_entry)
    db_session.commit()
    db_session.refresh(log_entry)

    assert log_entry.ma_nhat_ky is not None
    assert log_entry.ma_nguoi_dung is None
    assert log_entry.hanh_dong == "DANG_NHAP_THAT_BAI"


def test_nhat_ky_hoat_dong_relationship(db_session, admin_user):
    """Kiểm tra quan hệ ORM giữa NhatKyHoatDong và NguoiDung"""
    log_entry = NhatKyHoatDong(
        ma_nguoi_dung=admin_user.ma_nguoi_dung,
        hanh_dong="XEM_NHAT_KY",
        endpoint="/api/v1/admin/audit-logs",
        phuong_thuc="GET",
        dia_chi_ip="127.0.0.1",
        mo_ta="Kiểm tra quan hệ ORM",
        thoi_gian=datetime.utcnow()
    )
    db_session.add(log_entry)
    db_session.commit()
    db_session.refresh(log_entry)

    assert log_entry.nguoi_dung is not None
    assert log_entry.nguoi_dung.ten_dang_nhap == admin_user.ten_dang_nhap
    assert log_entry.nguoi_dung.vai_tro == "Admin"
