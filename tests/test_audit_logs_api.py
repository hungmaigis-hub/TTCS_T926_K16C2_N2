from datetime import datetime, timedelta
import pytest
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong


@pytest.fixture
def seed_audit_logs(db_session, admin_user, normal_user):
    """Nạp dữ liệu thử nghiệm phong phú để test lọc, tìm kiếm và phân trang"""
    now = datetime(2026, 10, 17, 10, 0, 0)
    
    logs = [
        NhatKyHoatDong(
            ma_nguoi_dung=admin_user.ma_nguoi_dung,
            hanh_dong="DANG_NHAP",
            endpoint="/api/v1/auth/login",
            phuong_thuc="POST",
            dia_chi_ip="192.168.1.10",
            mo_ta="[200] Đăng nhập quản trị",
            thoi_gian=now - timedelta(days=5)  # 2026-10-12
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=admin_user.ma_nguoi_dung,
            hanh_dong="TAO_NGUOI_DUNG",
            endpoint="/api/v1/admin/users",
            phuong_thuc="POST",
            dia_chi_ip="192.168.1.10",
            mo_ta="[201] Admin tạo tài khoản Nguyễn Văn An",
            thoi_gian=now - timedelta(days=3)  # 2026-10-14
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=normal_user.ma_nguoi_dung,
            hanh_dong="TAO_YEU_CAU_HO_TRO",
            endpoint="/api/v1/support-requests",
            phuong_thuc="POST",
            dia_chi_ip="192.168.1.20",
            mo_ta="[201] Sinh viên gửi yêu cầu xin nghỉ thực tập",
            thoi_gian=now - timedelta(days=1)  # 2026-10-16
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=admin_user.ma_nguoi_dung,
            hanh_dong="CAP_NHAT_NGUOI_DUNG",
            endpoint="/api/v1/admin/users/2",
            phuong_thuc="PUT",
            dia_chi_ip="192.168.1.10",
            mo_ta="[200] Phân quyền mentor cho Nguyễn Văn An",
            thoi_gian=now - timedelta(hours=4)  # 2026-10-17 06:00
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=None,
            hanh_dong="DANG_NHAP_THAT_BAI",
            endpoint="/api/v1/auth/login",
            phuong_thuc="POST",
            dia_chi_ip="10.10.10.99",
            mo_ta="[400] Thử mật khẩu sai từ địa chỉ IP lạ",
            thoi_gian=now - timedelta(minutes=30)  # 2026-10-17 09:30
        ),
    ]
    db_session.add_all(logs)
    db_session.commit()
    return logs


def test_get_audit_logs_unauthorized(client):
    """Không có token -> 401 Unauthorized"""
    response = client.get("/api/v1/admin/audit-logs")
    assert response.status_code == 401


def test_get_audit_logs_forbidden_for_intern(client, normal_headers):
    """Người dùng thực tập sinh không có quyền xem nhật ký hệ thống -> 403 Forbidden"""
    response = client.get("/api/v1/admin/audit-logs", headers=normal_headers)
    assert response.status_code == 403
    assert "Chỉ quản trị viên (Admin)" in response.json()["detail"]


def test_get_audit_logs_admin_success(client, admin_headers, seed_audit_logs):
    """Admin có quyền xem danh sách nhật ký hoạt động -> 200 OK"""
    response = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= len(seed_audit_logs)


def test_audit_logs_pagination(client, admin_headers, seed_audit_logs):
    """Kiểm tra chức năng phân trang chính xác"""
    # Trang 1: lấy 2 bản ghi
    res_p1 = client.get("/api/v1/admin/audit-logs?page=1&page_size=2", headers=admin_headers)
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert len(data_p1["items"]) == 2
    assert data_p1["page"] == 1
    assert data_p1["page_size"] == 2
    assert data_p1["total_pages"] >= 3

    # Trang 2: lấy 2 bản ghi tiếp theo
    res_p2 = client.get("/api/v1/admin/audit-logs?page=2&page_size=2", headers=admin_headers)
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert len(data_p2["items"]) == 2
    assert data_p2["page"] == 2

    # Các bản ghi của trang 1 và trang 2 không được trùng lặp
    p1_ids = [item["ma_nhat_ky"] for item in data_p1["items"]]
    p2_ids = [item["ma_nhat_ky"] for item in data_p2["items"]]
    assert set(p1_ids).isdisjoint(set(p2_ids))


def test_audit_logs_search_keyword(client, admin_headers, seed_audit_logs):
    """Kiểm tra tìm kiếm theo từ khóa trong mô tả và hành động"""
    # Tìm kiếm từ khóa 'Nguyễn Văn An'
    res = client.get("/api/v1/admin/audit-logs?search=Nguyễn+Văn+An", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert "Nguyễn Văn An" in item["mo_ta"]

    # Tìm kiếm theo IP
    res_ip = client.get("/api/v1/admin/audit-logs?search=10.10.10.99", headers=admin_headers)
    assert res_ip.status_code == 200
    data_ip = res_ip.json()
    assert data_ip["total"] == 1
    assert data_ip["items"][0]["dia_chi_ip"] == "10.10.10.99"


def test_audit_logs_filter_by_date(client, admin_headers, seed_audit_logs):
    """Kiểm tra lọc theo khoảng thời gian tu_ngay và den_ngay"""
    # Lọc từ ngày 2026-10-15 đến 2026-10-17
    tu_ngay = "2026-10-15T00:00:00"
    den_ngay = "2026-10-17T23:59:59"

    res = client.get(
        f"/api/v1/admin/audit-logs?tu_ngay={tu_ngay}&den_ngay={den_ngay}",
        headers=admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    # Các bản ghi trong khoảng này: xin nghỉ thực tập (16/10), phân quyền mentor (17/10), mật khẩu sai (17/10), và log truy vấn
    for item in data["items"]:
        dt = datetime.fromisoformat(item["thoi_gian"].replace("Z", "+00:00")).replace(tzinfo=None)
        assert dt >= datetime(2026, 10, 15, 0, 0, 0)
        assert dt <= datetime(2026, 10, 17, 23, 59, 59)


def test_audit_logs_filter_by_user(client, admin_headers, normal_user, seed_audit_logs):
    """Kiểm tra lọc theo mã người dùng ma_nguoi_dung"""
    res = client.get(
        f"/api/v1/admin/audit-logs?ma_nguoi_dung={normal_user.ma_nguoi_dung}",
        headers=admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["ma_nguoi_dung"] == normal_user.ma_nguoi_dung
    assert data["items"][0]["ten_dang_nhap"] == normal_user.ten_dang_nhap


def test_audit_logs_filter_by_action_and_method(client, admin_headers, seed_audit_logs):
    """Kiểm tra lọc theo hành động và phương thức HTTP"""
    res = client.get(
        "/api/v1/admin/audit-logs?hanh_dong=TAO_NGUOI_DUNG&phuong_thuc=POST",
        headers=admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["hanh_dong"] == "TAO_NGUOI_DUNG"
        assert item["phuong_thuc"] == "POST"
