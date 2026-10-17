import pytest
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong


def test_middleware_automatically_logs_modifying_request(client, admin_headers, admin_user, db_session):
    """
    Kiểm tra Middleware tự động phát hiện và ghi log thao tác POST (tạo tài khoản mới)
    """
    initial_log_count = db_session.query(NhatKyHoatDong).count()

    payload = {
        "ten_dang_nhap": "new_intern_99",
        "email": "intern99@hethong.vn",
        "mat_khau": "Intern123@",
        "ho_ten": "Trần Thị Thu",
        "vai_tro": "ThucTapSinh"
    }

    # Gửi request với client IP giả lập
    response = client.post(
        "/api/v1/admin/users",
        json=payload,
        headers={**admin_headers, "X-Forwarded-For": "10.0.0.99"}
    )
    assert response.status_code == 201

    # Kiểm tra số lượng bản ghi nhật ký tăng thêm
    new_log_count = db_session.query(NhatKyHoatDong).count()
    assert new_log_count == initial_log_count + 1

    # Kiểm tra chi tiết bản ghi nhật ký vừa được Middleware ghi nhận
    latest_log = db_session.query(NhatKyHoatDong).order_by(NhatKyHoatDong.ma_nhat_ky.desc()).first()
    assert latest_log.endpoint == "/api/v1/admin/users"
    assert latest_log.phuong_thuc == "POST"
    assert latest_log.dia_chi_ip == "10.0.0.99"
    assert latest_log.ma_nguoi_dung == admin_user.ma_nguoi_dung
    assert latest_log.hanh_dong == "TAO_NGUOI_DUNG"
    assert "201" in latest_log.mo_ta


def test_middleware_excludes_healthcheck_endpoint(client, db_session):
    """
    Kiểm tra Middleware không ghi log các endpoint hệ thống như /ping, /docs để tránh spam DB
    """
    initial_log_count = db_session.query(NhatKyHoatDong).count()

    response = client.get("/ping")
    assert response.status_code == 200

    new_log_count = db_session.query(NhatKyHoatDong).count()
    assert new_log_count == initial_log_count, "Endpoint /ping không được tạo bản ghi nhật ký"


def test_middleware_records_failed_operation(client, admin_headers, db_session):
    """
    Kiểm tra Middleware ghi nhận cả trường hợp người dùng thao tác thất bại (HTTP 400)
    """
    initial_log_count = db_session.query(NhatKyHoatDong).count()

    # Gửi dữ liệu không hợp lệ (vai trò không tồn tại)
    bad_payload = {
        "ten_dang_nhap": "bad_user",
        "email": "bad_user@gmail.com",
        "mat_khau": "123456",
        "ho_ten": "Bad User",
        "vai_tro": "SuperAdminFake"
    }

    response = client.post("/api/v1/admin/users", json=bad_payload, headers=admin_headers)
    assert response.status_code == 400

    # Middleware vẫn phải ghi lại lịch sử thao tác lỗi này
    new_log_count = db_session.query(NhatKyHoatDong).count()
    assert new_log_count == initial_log_count + 1

    latest_log = db_session.query(NhatKyHoatDong).order_by(NhatKyHoatDong.ma_nhat_ky.desc()).first()
    assert latest_log.phuong_thuc == "POST"
    assert "400" in latest_log.mo_ta
