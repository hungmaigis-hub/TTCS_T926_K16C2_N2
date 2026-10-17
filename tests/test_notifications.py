import pytest
from app.models.thong_bao import ThongBao


def test_get_my_notifications_unauthenticated(client):
    """
    Kiểm thử: Khi không đăng nhập/không truyền token,
    hệ thống phải trả về 401 Unauthorized.
    """
    response = client.get("/api/v1/notifications/my")
    assert response.status_code == 401
    assert "Không thể xác thực" in response.json()["detail"]


def test_get_my_notifications_returns_200_and_filters_user(
    client, db_session, user1, user2, token_user1
):
    """
    Kiểm thử theo yêu cầu Tester:
    - Xem danh sách thông báo trả về 200 OK.
    - Hiển thị đúng người dùng (User 1 chỉ thấy thông báo của User 1, không thấy thông báo của User 2).
    - Kiểm tra đúng các trường dữ liệu: ma_thong_bao, ma_nguoi_nhan, tieu_de, noi_dung, loai_thong_bao, da_doc, ngay_tao.
    """
    # Tạo 2 thông báo cho user 1
    notif1_user1 = ThongBao(
        ma_nguoi_nhan=user1.ma_nguoi_dung,
        tieu_de="Lịch phỏng vấn thực tập",
        noi_dung="Thời gian phỏng vấn: 09:00 Thứ Hai",
        loai_thong_bao="LICH_TRINH",
        da_doc=False
    )
    notif2_user1 = ThongBao(
        ma_nguoi_nhan=user1.ma_nguoi_dung,
        tieu_de="Quy định làm việc tuần đầu",
        noi_dung="Vui lòng có mặt đúng 8:00 sáng",
        loai_thong_bao="HE_THONG",
        da_doc=True
    )
    # Tạo 1 thông báo cho user 2
    notif_user2 = ThongBao(
        ma_nguoi_nhan=user2.ma_nguoi_dung,
        tieu_de="Thông báo riêng của User 2",
        noi_dung="Nội dung bí mật của User 2",
        loai_thong_bao="CONG_VIEC",
        da_doc=False
    )
    db_session.add_all([notif1_user1, notif2_user1, notif_user2])
    db_session.commit()

    # User 1 gọi API lấy danh sách thông báo của mình
    response = client.get(
        "/api/v1/notifications/my",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "unread_count" in data

    items = data["items"]
    assert len(items) == 2
    assert data["total"] == 2
    assert data["unread_count"] == 1  # 1 chưa đọc, 1 đã đọc

    # Đảm bảo tất cả thông báo đều thuộc về User 1
    for item in items:
        assert item["ma_nguoi_nhan"] == user1.ma_nguoi_dung
        assert "ma_thong_bao" in item
        assert "tieu_de" in item
        assert "noi_dung" in item
        assert "loai_thong_bao" in item
        assert "da_doc" in item
        assert "ngay_tao" in item

    # Đảm bảo không chứa thông báo của User 2
    titles = [item["tieu_de"] for item in items]
    assert "Thông báo riêng của User 2" not in titles


def test_mark_notification_as_read_success(client, db_session, user1, token_user1):
    """
    Kiểm thử theo yêu cầu Tester:
    - Khi click đánh dấu đã đọc (PATCH /api/v1/notifications/{id}/read),
      trạng thái đổi thành "đã đọc" (da_doc = True) thành công (200 OK).
    """
    notif = ThongBao(
        ma_nguoi_nhan=user1.ma_nguoi_dung,
        tieu_de="Chào mừng thực tập sinh mới",
        noi_dung="Chào mừng bạn đến với công ty",
        loai_thong_bao="CHUNG",
        da_doc=False
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    # Trước khi đọc: da_doc là False
    assert notif.da_doc is False

    response = client.patch(
        f"/api/v1/notifications/{notif.ma_thong_bao}/read",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["ma_thong_bao"] == notif.ma_thong_bao
    assert res_data["da_doc"] is True

    # Kiểm tra trong database đã cập nhật thành True
    db_session.refresh(notif)
    assert notif.da_doc is True


def test_mark_notification_not_found_404(client, token_user1):
    """
    Kiểm thử theo yêu cầu Tester:
    - Khi bấm vào thông báo không tồn tại -> trả về 404 Not Found.
    """
    fake_id = 999999
    response = client.patch(
        f"/api/v1/notifications/{fake_id}/read",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 404
    assert f"Không tìm thấy thông báo với mã {fake_id}" in response.json()["detail"]


def test_mark_notification_forbidden_403(client, db_session, user2, token_user1):
    """
    Kiểm thử theo yêu cầu Tester:
    - Khi cố tình bấm đọc thông báo không thuộc quyền sở hữu của mình -> trả về 403 Forbidden.
    """
    # Tạo thông báo thuộc về User 2
    notif_user2 = ThongBao(
        ma_nguoi_nhan=user2.ma_nguoi_dung,
        tieu_de="Thông báo riêng User 2",
        noi_dung="Chỉ User 2 mới có quyền xem và đọc",
        loai_thong_bao="CONG_VIEC",
        da_doc=False
    )
    db_session.add(notif_user2)
    db_session.commit()
    db_session.refresh(notif_user2)

    # User 1 cố tình gửi PATCH để đọc thông báo của User 2
    response = client.patch(
        f"/api/v1/notifications/{notif_user2.ma_thong_bao}/read",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 403
    assert "Bạn không có quyền truy cập" in response.json()["detail"]

    # Đảm bảo trạng thái thông báo của User 2 vẫn giữ nguyên là False
    db_session.refresh(notif_user2)
    assert notif_user2.da_doc is False


def test_get_my_notifications_with_x_user_id_header(client, db_session, user1):
    """
    Kiểm thử hỗ trợ linh hoạt X-User-Id header (dành cho các dev frontend test nhanh mà không cần JWT)
    """
    notif = ThongBao(
        ma_nguoi_nhan=user1.ma_nguoi_dung,
        tieu_de="Test qua X-User-Id",
        noi_dung="Test nhanh giữa frontend và backend",
        loai_thong_bao="CHUNG",
        da_doc=False
    )
    db_session.add(notif)
    db_session.commit()

    response = client.get(
        "/api/v1/notifications/my",
        headers={"X-User-Id": str(user1.ma_nguoi_dung)}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
