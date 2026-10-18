"""
=============================================================
AUTOMATION TEST - SPRINT 4 - LÊ QUANG HƯNG (TESTER)
=============================================================
Bao gồm các Test Case tự động kiểm thử toàn diện 3 nhiệm vụ được giao trên Sprint 4 Backlog:

1. NHIỆM VỤ 1 (Thông báo):
   User Story: Là thực tập sinh, tôi muốn nhận thông báo trên ứng dụng để không bỏ lỡ lịch trình.
   Phụ trách Tester: Lê Quang Hưng (Estimate: 2 SP/h, Priority: Cao)
   Yêu cầu kiểm thử:
     - Kiểm tra người dùng chỉ xem đúng thông báo của mình (200 OK)
     - Kiểm tra cập nhật trạng thái đã đọc thành công (PATCH /api/v1/notifications/{id}/read)
     - Bắt lỗi khi cập nhật mã thông báo không tồn tại (404 Not Found)
     - Bắt lỗi khi cập nhật mã thông báo không thuộc quyền sở hữu (403 Forbidden)
     - Kiểm tra phân quyền: Không có token trả về 401 Unauthorized
     - Kiểm tra tiện ích đánh dấu tất cả đã đọc (PATCH /api/v1/notifications/read-all)

2. NHIỆM VỤ 2 (Tạo tài khoản Admin):
   User Story: Là admin, tôi muốn tạo tài khoản cho HR, mentor và thực tập sinh để họ sử dụng hệ thống.
   Phụ trách Tester: Lê Quang Hưng (Estimate: 2 SP/h, Priority: Cao)
   Yêu cầu kiểm thử:
     - Tạo tài khoản thành công với các vai trò khác nhau (201 Created): Admin, HR, Mentor, ThucTapSinh
     - Kiểm tra mật khẩu được băm an toàn bằng bcrypt trong DB và không lộ mật khẩu trong response
     - Bắt lỗi khi nhập email/username đã tồn tại (400 Bad Request / 409 Conflict)
     - Bắt lỗi khi thiếu các trường bắt buộc (email, username, password, fullname, role) (422)
     - Bắt lỗi mật khẩu không đủ tiêu chuẩn hoặc định dạng email sai (422)
     - Bắt lỗi vai trò không hợp lệ (422)
     - Chặn người dùng không có quyền Admin tạo tài khoản (403 Forbidden: HR, Mentor, Thực tập sinh)

3. NHIỆM VỤ 3 (Nhật ký hoạt động Audit Logs):
   User Story: Là admin, tôi muốn xem nhật ký hoạt động để theo dõi các thao tác trong hệ thống.
   Phụ trách Tester: Lê Quang Hưng (Estimate: 2 SP/h, Priority: Cao)
   Yêu cầu kiểm thử:
     - Kiểm tra hệ thống ghi nhận log chuẩn xác khi phát sinh thao tác dữ liệu (200 OK)
     - Kiểm tra bộ lọc và phân trang audit logs hoạt động chính xác (ngày, người dùng, hành động, từ khóa)
     - Kiểm tra chỉ Admin mới có quyền xem log (403 Forbidden đối với Thực tập sinh/HR/Mentor, 401 khi chưa đăng nhập)
     - Kiểm tra middleware ghi nhận các thao tác thất bại (400 Bad Request)

Cách chạy kiểm thử:
  pytest tests/test_sprint4_le_quang_hung.py -v
=============================================================
"""

import pytest
from datetime import datetime, timedelta
from app.models.nguoi_dung import NguoiDung
from app.models.thong_bao import ThongBao
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong
from app.core.security import verify_password
from app.schemas.user import UserRole


# ==============================================================================
# PHẦN 1: USER STORY 1 - KIỂM THỬ THÔNG BÁO CÁ NHÂN & ĐÁNH DẤU ĐÃ ĐỌC
# ==============================================================================

class TestSprint4_ThongBao:
    """
    Kiểm thử tự động cho tính năng Thông báo cá nhân:
    - GET   /api/v1/notifications/my
    - PATCH /api/v1/notifications/{id}/read
    - PATCH /api/v1/notifications/read-all
    - POST  /api/v1/notifications
    """

    def test_tc01_get_notifications_unauthenticated_returns_401(self, client):
        """
        TC1.1: Người dùng chưa đăng nhập truy cập xem thông báo -> 401 Unauthorized
        """
        response = client.get("/api/v1/notifications/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        assert "Không thể xác thực" in response.json()["detail"]

    def test_tc02_user_only_sees_own_notifications_200_ok(
        self, client, db_session, user1, user2, token_user1
    ):
        """
        TC1.2: Người dùng chỉ xem đúng thông báo của chính mình, không lộ thông báo của người khác.
        Kỳ vọng: 200 OK, đúng tổng số, đúng số lượng chưa đọc, cấu trúc trường đầy đủ.
        """
        # Tạo thông báo cho User 1 (1 chưa đọc, 1 đã đọc)
        notif1 = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Lịch đánh giá giữa kỳ",
            noi_dung="Buổi đánh giá diễn ra lúc 14:00 Thứ Sáu tại phòng họp B.",
            loai_thong_bao="LICH_TRINH",
            da_doc=False,
        )
        notif2 = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Chào mừng thực tập sinh",
            noi_dung="Chào mừng bạn đến với kỳ thực tập công nghệ thông tin.",
            loai_thong_bao="HE_THONG",
            da_doc=True,
        )
        # Tạo thông báo riêng cho User 2 (User 1 KHÔNG được nhìn thấy)
        notif_user2 = ThongBao(
            ma_nguoi_nhan=user2.ma_nguoi_dung,
            tieu_de="Thông báo bảo mật User 2",
            noi_dung="Nội dung bảo mật của User 2",
            loai_thong_bao="CONG_VIEC",
            da_doc=False,
        )
        db_session.add_all([notif1, notif2, notif_user2])
        db_session.commit()

        # User 1 gọi API lấy thông báo
        response = client.get(
            "/api/v1/notifications/my",
            headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] == 2
        assert data["unread_count"] == 1

        items = data["items"]
        assert len(items) == 2
        for item in items:
            assert item["ma_nguoi_nhan"] == user1.ma_nguoi_dung
            assert "ma_thong_bao" in item
            assert "tieu_de" in item
            assert "noi_dung" in item
            assert "loai_thong_bao" in item
            assert "da_doc" in item
            assert "ngay_tao" in item

    def test_tc03_filter_unread_only_notifications(
        self, client, db_session, user1, token_user1
    ):
        """
        TC1.3: Bộ lọc unread_only=True chỉ trả về các thông báo chưa đọc (da_doc = False).
        """
        notif_read = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Thông báo đã đọc",
            noi_dung="Nội dung đã xem",
            loai_thong_bao="HE_THONG",
            da_doc=True
        )
        notif_unread = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Thông báo chưa đọc",
            noi_dung="Nội dung cần xem ngay",
            loai_thong_bao="CONG_VIEC",
            da_doc=False
        )
        db_session.add_all([notif_read, notif_unread])
        db_session.commit()

        response = client.get(
            "/api/v1/notifications/my?unread_only=true",
            headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["da_doc"] is False
        assert data["items"][0]["tieu_de"] == "Thông báo chưa đọc"

    def test_tc04_mark_notification_as_read_success_200(
        self, client, db_session, user1, token_user1
    ):
        """
        TC1.4: Cập nhật trạng thái thông báo thành đã đọc thành công (PATCH /api/v1/notifications/{id}/read)
        Kỳ vọng: 200 OK, da_doc = True.
        """
        notif = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Thông báo cần đọc",
            noi_dung="Nội dung chi tiết thông báo",
            loai_thong_bao="CONG_VIEC",
            da_doc=False
        )
        db_session.add(notif)
        db_session.commit()
        db_session.refresh(notif)

        response = client.patch(
            f"/api/v1/notifications/{notif.ma_thong_bao}/read",
            headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["da_doc"] is True
        assert data["ma_thong_bao"] == notif.ma_thong_bao

        # Kiểm tra trực tiếp trong DB
        db_session.refresh(notif)
        assert notif.da_doc is True

    def test_tc05_mark_notification_not_found_returns_404(
        self, client, token_user1
    ):
        """
        TC1.5: Bắt lỗi khi cập nhật mã thông báo không tồn tại trong DB -> 404 Not Found.
        """
        non_existent_id = 999999
        response = client.patch(
            f"/api/v1/notifications/{non_existent_id}/read",
            headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 404
        assert "Không tìm thấy" in response.json()["detail"]

    def test_tc06_mark_notification_forbidden_for_other_user_returns_403(
        self, client, db_session, user2, token_user1
    ):
        """
        TC1.6: Bắt lỗi khi người dùng cố tình cập nhật thông báo của người khác -> 403 Forbidden.
        (User 1 dùng token của mình để đánh dấu đọc thông báo thuộc về User 2).
        """
        notif_user2 = ThongBao(
            ma_nguoi_nhan=user2.ma_nguoi_dung,
            tieu_de="Thông báo của User 2",
            noi_dung="Nội dung mật của User 2",
            loai_thong_bao="CONG_VIEC",
            da_doc=False
        )
        db_session.add(notif_user2)
        db_session.commit()
        db_session.refresh(notif_user2)

        # User 1 gửi request cố sửa thông báo của User 2
        response = client.patch(
            f"/api/v1/notifications/{notif_user2.ma_thong_bao}/read",
            headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 403
        assert "Bạn không có quyền" in response.json()["detail"]

    def test_tc07_mark_all_notifications_as_read_convenience(
        self, client, db_session, user1, token_user1
    ):
        """
        TC1.7: Tiện ích đánh dấu tất cả thông báo cá nhân là đã đọc (PATCH /api/v1/notifications/read-all)
        """
        # Tạo 3 thông báo chưa đọc cho user 1
        for i in range(3):
            db_session.add(ThongBao(
                ma_nguoi_nhan=user1.ma_nguoi_dung,
                tieu_de=f"Thông báo số {i+1}",
                noi_dung="Nội dung thông báo",
                loai_thong_bao="HE_THONG",
                da_doc=False
            ))
        db_session.commit()

        response = client.patch(
            "/api/v1/notifications/read-all",
            headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["updated_count"] >= 3

        # Kiểm tra lại số lượng chưa đọc còn 0
        get_res = client.get(
            "/api/v1/notifications/my",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert get_res.json()["unread_count"] == 0


# ==============================================================================
# PHẦN 2: USER STORY 2 - KIỂM THỬ ADMIN TẠO TÀI KHOẢN NGƯỜI DÙNG
# ==============================================================================

class TestSprint4_AdminTaoTaiKhoan:
    """
    Kiểm thử tự động cho tính năng Admin tạo tài khoản:
    - Endpoint: POST /api/v1/admin/users
    """

    @pytest.mark.parametrize("role", ["Admin", "HR", "Mentor", "ThucTapSinh"])
    def test_tc08_admin_create_user_all_valid_roles_201_created(
        self, client, admin_headers, db_session, role
    ):
        """
        TC2.1: Admin tạo tài khoản thành công với tất cả các vai trò hợp lệ (201 Created).
        Kiểm tra: Admin, HR, Mentor, ThucTapSinh.
        """
        username = f"user_test_{role.lower()}_2026"
        email = f"{role.lower()}.sprint4@company.com"
        payload = {
            "ho_ten": f"Người Dùng {role}",
            "email": email,
            "ten_dang_nhap": username,
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": role
        }

        response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)

        assert response.status_code == 201, f"Failed for role {role}: {response.text}"
        data = response.json()
        assert data["ten_dang_nhap"] == username
        assert data["email"] == email
        assert data["vai_tro"] == role
        assert data["trang_thai"] is True
        assert "ma_nguoi_dung" in data

    def test_tc09_password_is_securely_hashed_and_not_exposed(
        self, client, admin_headers, db_session
    ):
        """
        TC2.2: Mật khẩu PHẢI được băm bằng bcrypt trong DB và KHÔNG được để lộ trong response.
        """
        raw_password = "MatKhauBaoMatTuyetDoi@2026"
        payload = {
            "ho_ten": "Lê Văn Hướng Dẫn",
            "email": "mentor.levan@ttcs.vn",
            "ten_dang_nhap": "mentor_levan_hash",
            "mat_khau": raw_password,
            "vai_tro": "Mentor"
        }

        response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert response.status_code == 201
        data = response.json()

        # 1. Bảo mật Response: Tuyệt đối không lộ mật khẩu gốc hay hash
        assert "mat_khau" not in data
        assert "mat_khau_hash" not in data
        assert "password" not in data

        # 2. Kiểm tra trong Database: Mật khẩu lưu trữ dạng bcrypt hash
        user_in_db = db_session.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "mentor_levan_hash").first()
        assert user_in_db is not None
        assert user_in_db.mat_khau_hash != raw_password
        assert user_in_db.mat_khau_hash.startswith("$2") or len(user_in_db.mat_khau_hash) >= 50
        assert verify_password(raw_password, user_in_db.mat_khau_hash) is True

    def test_tc10_duplicate_username_returns_400_or_409(
        self, client, admin_headers, db_session
    ):
        """
        TC2.3: Bắt lỗi trùng lặp username (tên đăng nhập) -> 400 Bad Request / 409 Conflict.
        """
        payload1 = {
            "ho_ten": "Trần Văn A",
            "email": "user.unique1@ttcs.vn",
            "ten_dang_nhap": "trung_username_2026",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "ThucTapSinh"
        }
        res1 = client.post("/api/v1/admin/users", json=payload1, headers=admin_headers)
        assert res1.status_code == 201

        # Tạo tài khoản thứ 2 có cùng ten_dang_nhap nhưng khác email
        payload2 = {
            "ho_ten": "Trần Văn B",
            "email": "user.unique2@ttcs.vn",
            "ten_dang_nhap": "trung_username_2026",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "Mentor"
        }
        res2 = client.post("/api/v1/admin/users", json=payload2, headers=admin_headers)

        assert res2.status_code in [400, 409]
        assert "đã tồn tại" in res2.json()["detail"]

    def test_tc11_duplicate_email_returns_400_or_409(
        self, client, admin_headers, db_session
    ):
        """
        TC2.4: Bắt lỗi trùng lặp email -> 400 Bad Request / 409 Conflict.
        """
        payload1 = {
            "ho_ten": "Hoàng Văn C",
            "email": "trung_email_2026@ttcs.vn",
            "ten_dang_nhap": "username_c_2026",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "HR"
        }
        res1 = client.post("/api/v1/admin/users", json=payload1, headers=admin_headers)
        assert res1.status_code == 201

        # Tạo tài khoản thứ 2 có cùng email nhưng khác ten_dang_nhap
        payload2 = {
            "ho_ten": "Hoàng Văn D",
            "email": "trung_email_2026@ttcs.vn",
            "ten_dang_nhap": "username_d_2026",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "ThucTapSinh"
        }
        res2 = client.post("/api/v1/admin/users", json=payload2, headers=admin_headers)

        assert res2.status_code in [400, 409]
        assert "Email" in res2.json()["detail"] and "đã tồn tại" in res2.json()["detail"]

    def test_tc12_missing_required_fields_returns_422(
        self, client, admin_headers
    ):
        """
        TC2.5: Bắt lỗi thiếu bất kỳ trường bắt buộc nào -> 422 Unprocessable Entity.
        """
        # 1. Thiếu email
        r1 = client.post("/api/v1/admin/users", json={
            "ten_dang_nhap": "u1", "mat_khau": "Pass@123", "ho_ten": "Tên", "vai_tro": "HR"
        }, headers=admin_headers)
        assert r1.status_code == 422

        # 2. Thiếu ten_dang_nhap
        r2 = client.post("/api/v1/admin/users", json={
            "email": "a@b.com", "mat_khau": "Pass@123", "ho_ten": "Tên", "vai_tro": "HR"
        }, headers=admin_headers)
        assert r2.status_code == 422

        # 3. Thiếu mat_khau
        r3 = client.post("/api/v1/admin/users", json={
            "ten_dang_nhap": "u3", "email": "a3@b.com", "ho_ten": "Tên", "vai_tro": "HR"
        }, headers=admin_headers)
        assert r3.status_code == 422

        # 4. Thiếu ho_ten
        r4 = client.post("/api/v1/admin/users", json={
            "ten_dang_nhap": "u4", "email": "a4@b.com", "mat_khau": "Pass@123", "vai_tro": "HR"
        }, headers=admin_headers)
        assert r4.status_code == 422

        # 5. Thiếu vai_tro
        r5 = client.post("/api/v1/admin/users", json={
            "ten_dang_nhap": "u5", "email": "a5@b.com", "mat_khau": "Pass@123", "ho_ten": "Tên"
        }, headers=admin_headers)
        assert r5.status_code == 422

    def test_tc13_invalid_role_returns_422(
        self, client, admin_headers
    ):
        """
        TC2.6: Bắt lỗi vai trò không thuộc danh mục hợp lệ (Admin, HR, Mentor, ThucTapSinh) -> 422.
        """
        payload = {
            "ho_ten": "Người Dùng Lỗi Vai Trò",
            "email": "invalid_role@ttcs.vn",
            "ten_dang_nhap": "invalid_role_user",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "GiamDocDieuHanh"
        }
        response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert response.status_code == 422

    def test_tc14_invalid_email_format_returns_422(
        self, client, admin_headers
    ):
        """
        TC2.7: Bắt lỗi định dạng email không hợp lệ -> 422 Unprocessable Entity.
        """
        payload = {
            "ho_ten": "Email Sai Định Dạng",
            "email": "khong-phai-email-hop-le",
            "ten_dang_nhap": "bad_email_user",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "ThucTapSinh"
        }
        response = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert response.status_code == 422

    def test_tc15_forbidden_for_non_admin_roles_403(
        self, client, hr_headers, mentor_headers, intern_headers
    ):
        """
        TC2.8: Chặn người dùng không có quyền Admin (HR, Mentor, Thực tập sinh) -> 403 Forbidden.
        """
        sample_payload = {
            "ho_ten": "Người Mới",
            "email": "test_block@ttcs.vn",
            "ten_dang_nhap": "test_block",
            "mat_khau": "MatKhauChuan@123",
            "vai_tro": "ThucTapSinh"
        }

        # 1. HR thử tạo tài khoản
        r_hr = client.post("/api/v1/admin/users", json=sample_payload, headers=hr_headers)
        assert r_hr.status_code == 403

        # 2. Mentor thử tạo tài khoản
        r_mentor = client.post("/api/v1/admin/users", json=sample_payload, headers=mentor_headers)
        assert r_mentor.status_code == 403

        # 3. Thực tập sinh thử tạo tài khoản
        r_intern = client.post("/api/v1/admin/users", json=sample_payload, headers=intern_headers)
        assert r_intern.status_code == 403

    def test_tc16_unauthorized_without_token_401(self, client):
        """
        TC2.9: Người dùng chưa xác thực (không gửi Bearer Token) -> 401 Unauthorized.
        """
        response = client.post("/api/v1/admin/users", json={
            "ho_ten": "Không Token",
            "email": "no_token@ttcs.vn",
            "ten_dang_nhap": "no_token_user",
            "mat_khau": "Pass@123",
            "vai_tro": "Mentor"
        })
        assert response.status_code == 401


# ==============================================================================
# PHẦN 3: USER STORY 3 - KIỂM THỬ NHẬT KÝ HOẠT ĐỘNG (AUDIT LOGS)
# ==============================================================================

@pytest.fixture
def seed_audit_logs_sprint4(db_session, admin_user, normal_user):
    """Fixture tạo dữ liệu nhật ký mẫu phong phú cho kiểm thử Sprint 4"""
    now = datetime(2026, 10, 18, 10, 0, 0)
    logs = [
        NhatKyHoatDong(
            ma_nguoi_dung=admin_user.ma_nguoi_dung,
            hanh_dong="DANG_NHAP",
            endpoint="/api/v1/auth/login",
            phuong_thuc="POST",
            dia_chi_ip="192.168.1.10",
            mo_ta="[200] Đăng nhập quản trị",
            thoi_gian=now - timedelta(days=5)  # 2026-10-13
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=admin_user.ma_nguoi_dung,
            hanh_dong="TAO_NGUOI_DUNG",
            endpoint="/api/v1/admin/users",
            phuong_thuc="POST",
            dia_chi_ip="192.168.1.10",
            mo_ta="[201] Admin tạo tài khoản Nguyễn Văn An",
            thoi_gian=now - timedelta(days=3)  # 2026-10-15
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=normal_user.ma_nguoi_dung,
            hanh_dong="TAO_YEU_CAU_HO_TRO",
            endpoint="/api/v1/support-requests",
            phuong_thuc="POST",
            dia_chi_ip="192.168.1.20",
            mo_ta="[201] Sinh viên gửi yêu cầu xin nghỉ thực tập",
            thoi_gian=now - timedelta(days=1)  # 2026-10-17
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=admin_user.ma_nguoi_dung,
            hanh_dong="CAP_NHAT_NGUOI_DUNG",
            endpoint="/api/v1/admin/users/2",
            phuong_thuc="PUT",
            dia_chi_ip="192.168.1.10",
            mo_ta="[200] Phân quyền mentor cho Nguyễn Văn An",
            thoi_gian=now - timedelta(hours=4)  # 2026-10-18 06:00
        ),
        NhatKyHoatDong(
            ma_nguoi_dung=None,
            hanh_dong="DANG_NHAP_THAT_BAI",
            endpoint="/api/v1/auth/login",
            phuong_thuc="POST",
            dia_chi_ip="10.10.10.99",
            mo_ta="[400] Thử mật khẩu sai từ địa chỉ IP lạ",
            thoi_gian=now - timedelta(minutes=30)  # 2026-10-18 09:30
        ),
    ]
    db_session.add_all(logs)
    db_session.commit()
    return logs


class TestSprint4_NhatKyHoatDong:
    """
    Kiểm thử tự động cho tính năng Nhật ký hoạt động (Audit Logs):
    - Endpoint: GET /api/v1/admin/audit-logs
    - Middleware: AuditLogMiddleware
    """

    def test_tc17_audit_logs_unauthorized_returns_401(self, client):
        """
        TC3.1: Không có token / chưa đăng nhập -> 401 Unauthorized.
        """
        response = client.get("/api/v1/admin/audit-logs")
        assert response.status_code == 401

    def test_tc18_audit_logs_forbidden_for_intern_or_non_admin_403(
        self, client, intern_headers, hr_headers, mentor_headers
    ):
        """
        TC3.2: Người dùng không phải Admin (Thực tập sinh, HR, Mentor) cố xem nhật ký -> 403 Forbidden.
        """
        # Thực tập sinh
        r1 = client.get("/api/v1/admin/audit-logs", headers=intern_headers)
        assert r1.status_code == 403
        assert "Chỉ quản trị viên (Admin)" in r1.json()["detail"]

        # HR
        r2 = client.get("/api/v1/admin/audit-logs", headers=hr_headers)
        assert r2.status_code == 403

        # Mentor
        r3 = client.get("/api/v1/admin/audit-logs", headers=mentor_headers)
        assert r3.status_code == 403

    def test_tc19_admin_get_audit_logs_success_200(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """
        TC3.3: Admin xem danh sách nhật ký hoạt động thành công -> 200 OK.
        Kiểm tra cấu trúc: items, total, page, page_size, total_pages.
        """
        response = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] >= len(seed_audit_logs_sprint4)

        # Kiểm tra chi tiết cấu trúc từng bản ghi nhật ký
        sample_log = data["items"][0]
        assert "ma_nhat_ky" in sample_log
        assert "endpoint" in sample_log
        assert "phuong_thuc" in sample_log
        assert "hanh_dong" in sample_log
        assert "thoi_gian" in sample_log

    def test_tc20_audit_logs_pagination_works_correctly(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """
        TC3.4: Kiểm tra tính năng phân trang (page, page_size) hoạt động chuẩn xác,
        dữ liệu giữa trang 1 và trang 2 không bị trùng lặp.
        """
        # Trang 1 lấy 2 bản ghi
        res1 = client.get("/api/v1/admin/audit-logs?page=1&page_size=2", headers=admin_headers)
        assert res1.status_code == 200
        d1 = res1.json()
        assert len(d1["items"]) == 2
        assert d1["page"] == 1
        assert d1["page_size"] == 2
        assert d1["total_pages"] >= 3

        # Trang 2 lấy 2 bản ghi
        res2 = client.get("/api/v1/admin/audit-logs?page=2&page_size=2", headers=admin_headers)
        assert res2.status_code == 200
        d2 = res2.json()
        assert len(d2["items"]) == 2
        assert d2["page"] == 2

        # Đảm bảo các bản ghi không bị trùng giữa 2 trang
        p1_ids = [item["ma_nhat_ky"] for item in d1["items"]]
        p2_ids = [item["ma_nhat_ky"] for item in d2["items"]]
        assert set(p1_ids).isdisjoint(set(p2_ids))

    def test_tc21_audit_logs_search_keyword(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """
        TC3.5: Kiểm tra tìm kiếm nhật ký theo từ khóa search (trong mô tả, hành động, endpoint, IP).
        """
        res = client.get("/api/v1/admin/audit-logs?search=Nguyễn+Văn+An", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert "Nguyễn Văn An" in item["mo_ta"]

    def test_tc22_audit_logs_filter_by_date_range(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """
        TC3.6: Kiểm tra bộ lọc nhật ký theo khoảng thời gian tu_ngay và den_ngay.
        """
        # Lọc ngày 2026-10-15 đến 2026-10-17
        res = client.get(
            "/api/v1/admin/audit-logs?tu_ngay=2026-10-15T00:00:00&den_ngay=2026-10-17T23:59:59",
            headers=admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["hanh_dong"] in ["TAO_NGUOI_DUNG", "TAO_YEU_CAU_HO_TRO"]

    def test_tc23_audit_logs_filter_by_user(
        self, client, admin_headers, normal_user, seed_audit_logs_sprint4
    ):
        """
        TC3.7: Kiểm tra lọc nhật ký theo mã người dùng ma_nguoi_dung.
        """
        res = client.get(
            f"/api/v1/admin/audit-logs?ma_nguoi_dung={normal_user.ma_nguoi_dung}",
            headers=admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["ma_nguoi_dung"] == normal_user.ma_nguoi_dung
        assert data["items"][0]["hanh_dong"] == "TAO_YEU_CAU_HO_TRO"

    def test_tc24_audit_logs_filter_by_action_and_method(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """
        TC3.8: Kiểm tra lọc kết hợp theo mã hành động và phương thức HTTP.
        """
        res = client.get(
            "/api/v1/admin/audit-logs?hanh_dong=CAP_NHAT_NGUOI_DUNG&phuong_thuc=PUT",
            headers=admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["phuong_thuc"] == "PUT"
        assert data["items"][0]["hanh_dong"] == "CAP_NHAT_NGUOI_DUNG"

    def test_tc25_middleware_automatically_logs_data_operation(
        self, client, admin_headers, admin_user, db_session
    ):
        """
        TC3.9: Kiểm tra Middleware tự động ghi nhận log chuẩn xác khi phát sinh thao tác dữ liệu:
        Khi Admin gửi POST /api/v1/admin/users tạo người dùng -> Middleware ghi nhận bản ghi nhật ký mới.
        """
        initial_count = db_session.query(NhatKyHoatDong).count()

        payload = {
            "ten_dang_nhap": "middleware_audit_user",
            "email": "middleware_audit@ttcs.vn",
            "mat_khau": "ChuanPass@123",
            "ho_ten": "Kiểm Thử Middleware",
            "vai_tro": "ThucTapSinh"
        }

        response = client.post(
            "/api/v1/admin/users",
            json=payload,
            headers={**admin_headers, "X-Forwarded-For": "10.0.1.55"}
        )
        assert response.status_code == 201

        # Đảm bảo số lượng log tăng thêm ít nhất 1 bản ghi
        new_count = db_session.query(NhatKyHoatDong).count()
        assert new_count == initial_count + 1

        # Kiểm tra nội dung log mới nhất
        latest = db_session.query(NhatKyHoatDong).order_by(NhatKyHoatDong.ma_nhat_ky.desc()).first()
        assert latest.endpoint == "/api/v1/admin/users"
        assert latest.phuong_thuc == "POST"
        assert latest.dia_chi_ip == "10.0.1.55"
        assert latest.ma_nguoi_dung == admin_user.ma_nguoi_dung
        assert latest.hanh_dong == "TAO_NGUOI_DUNG"
        assert "201" in latest.mo_ta
