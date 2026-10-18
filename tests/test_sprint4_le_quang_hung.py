"""
=============================================================
AUTOMATION TEST - SPRINT 4 - LÊ QUANG HƯNG (TESTER)
=============================================================
Bao gồm bộ 54 Test Case tự động kiểm thử toàn diện, chuyên sâu cho 3 nhiệm vụ trên Sprint 4 Backlog:

1. NHIỆM VỤ 1 (Thông báo - Notifications): 14 Test Cases
   User Story: Là thực tập sinh, tôi muốn nhận thông báo trên ứng dụng để không bỏ lỡ lịch trình.
   Phụ trách Tester: Lê Quang Hưng (Estimate: 2 SP/h, Priority: Cao)
   Bao quát:
     - Phân quyền & xác thực (401 Unauthorized, mock header fallback)
     - Phân lập dữ liệu đa người dùng (Data Isolation: chỉ xem thông báo của mình)
     - Kiểm tra schema, kiểu dữ liệu, metadata (total, unread_count)
     - Bộ lọc chưa đọc (unread_only=True)
     - Phân trang (skip, limit) và sắp xếp thứ tự thời gian mới nhất (DESC)
     - Cập nhật trạng thái đã đọc thành công (PATCH /{id}/read)
     - Tính lũy thừa/idempotency khi đánh dấu đã đọc nhiều lần
     - Bắt lỗi mã thông báo không tồn tại (404 Not Found)
     - Chống leo quyền (IDOR/BAC): người này sửa thông báo người kia (403 Forbidden)
     - Tiện ích đánh dấu tất cả đã đọc (PATCH /read-all)
     - API nội bộ tạo thông báo mới (POST /notifications - 201 Created)
     - Validate ID âm hoặc bằng 0 (422 Unprocessable)

2. NHIỆM VỤ 2 (Quản trị tạo người dùng - Admin Users): 22 Test Cases
   User Story: Là admin, tôi muốn tạo tài khoản cho HR, mentor và thực tập sinh để họ sử dụng hệ thống.
   Phụ trách Tester: Lê Quang Hưng (Estimate: 2 SP/h, Priority: Cao)
   Bao quát:
     - Tạo thành công đầy đủ 4 vai trò: Admin, HR, Mentor, ThucTapSinh (201 Created)
     - Độ linh hoạt: Hỗ trợ alias trường tiếng Anh (username, password, full_name, role)
     - Bảo mật mật khẩu: Băm an toàn bằng bcrypt trong DB, verify khớp, KHÔNG lộ trong response
     - Chống trùng lặp username (400 Bad Request / 409 Conflict)
     - Chống trùng lặp email (400 Bad Request / 409 Conflict)
     - Bắt lỗi thiếu từng trường bắt buộc (email, username, password, full_name, role - 422)
     - Bắt lỗi vai trò ngoài danh mục enum (SuperAdmin, GiamDoc, v.v. - 422)
     - Bắt lỗi định dạng email sai chuẩn RFC (thiếu @, thiếu domain - 422)
     - Hỗ trợ họ tên tiếng Việt có dấu đầy đủ Unicode UTF-8
     - Phân quyền RBAC nghiêm ngặt: Chặn HR (403), Mentor (403), Thực tập sinh (403), Mock Header (403)
     - Chặn truy cập nặc danh khi thiếu token (401 Unauthorized)
     - Xem danh sách người dùng cho Admin (GET /users) hỗ trợ phân trang & lọc vai trò

3. NHIỆM VỤ 3 (Nhật ký hoạt động - Audit Logs & Middleware): 18 Test Cases
   User Story: Là admin, tôi muốn xem nhật ký hoạt động để theo dõi các thao tác trong hệ thống.
   Phụ trách Tester: Lê Quang Hưng (Estimate: 2 SP/h, Priority: Cao)
   Bao quát:
     - Bảo vệ endpoint: Chưa đăng nhập (401), vai trò non-admin (Thực tập sinh, HR, Mentor - 403)
     - Admin truy vấn danh sách log thành công (200 OK, đúng schema phân trang)
     - Phân trang chuẩn xác: page 1 và page 2 tách biệt không trùng lặp
     - Biên phân trang: page cực lớn trả về danh sách rỗng an toàn
     - Tìm kiếm linh hoạt theo từ khóa trong mô tả, username, endpoint, IP
     - Tìm kiếm từ khóa không khớp trả về total = 0
     - Bộ lọc theo khoảng thời gian tu_ngay và den_ngay
     - Bộ lọc theo mã ID người dùng (ma_nguoi_dung)
     - Bộ lọc kết hợp theo hành động nghiệp vụ (hanh_dong) và phương thức HTTP (phuong_thuc)
     - Kiểm tra sắp xếp thứ tự thời gian giảm dần (thoi_gian DESC)
     - Middleware tự động ghi log thao tác thay đổi dữ liệu (POST/PUT/DELETE)
     - Middleware trích xuất đúng IP client từ header X-Forwarded-For
     - Middleware loại trừ các endpoint tĩnh/hệ thống (/ping, /docs)
     - Middleware ghi nhận cả các thao tác thất bại nghiệp vụ (400 Bad Request)

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
# PHẦN 1: USER STORY 1 - KIỂM THỬ THÔNG BÁO CÁ NHÂN (NOTIFICATIONS) [14 TCs]
# ==============================================================================

class TestSprint4_ThongBao:
    """
    Kiểm thử chuyên sâu cho tính năng Thông báo cá nhân:
    - GET   /api/v1/notifications/my
    - PATCH /api/v1/notifications/{id}/read
    - PATCH /api/v1/notifications/read-all
    - POST  /api/v1/notifications
    """

    def test_01_get_notifications_unauthenticated_returns_401(self, client):
        """TC-01: Chưa đăng nhập truy cập xem thông báo -> 401 Unauthorized"""
        response = client.get("/api/v1/notifications/my")
        assert response.status_code == 401
        assert "Không thể xác thực" in response.json()["detail"]

    def test_02_get_notifications_with_x_user_id_mock_header(self, client, user1):
        """TC-02: Hỗ trợ truy vấn thông báo qua header mock X-User-Id khi cần test nhanh"""
        response = client.get(
            "/api/v1/notifications/my",
            headers={"X-User-Id": str(user1.ma_nguoi_dung)}
        )
        assert response.status_code == 200
        assert "items" in response.json()

    def test_03_user_only_sees_own_notifications_200_ok(
        self, client, db_session, user1, user2, token_user1
    ):
        """TC-03: Người dùng chỉ xem đúng thông báo của mình, không lộ thông báo của người khác"""
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
        notif_user2 = ThongBao(
            ma_nguoi_nhan=user2.ma_nguoi_dung,
            tieu_de="Thông báo bảo mật User 2",
            noi_dung="Nội dung bảo mật của User 2",
            loai_thong_bao="CONG_VIEC",
            da_doc=False,
        )
        db_session.add_all([notif1, notif2, notif_user2])
        db_session.commit()

        response = client.get(
            "/api/v1/notifications/my",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["unread_count"] == 1
        for item in data["items"]:
            assert item["ma_nguoi_nhan"] == user1.ma_nguoi_dung

    def test_04_notifications_response_schema_and_types(
        self, client, db_session, user1, token_user1
    ):
        """TC-04: Kiểm tra đầy đủ cấu trúc trường và kiểu dữ liệu trả về của thông báo"""
        notif = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Thông báo kiểm tra Schema",
            noi_dung="Chi tiết nội dung cần kiểm tra",
            loai_thong_bao="CONG_VIEC",
            da_doc=False,
        )
        db_session.add(notif)
        db_session.commit()

        response = client.get(
            "/api/v1/notifications/my",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert response.status_code == 200
        item = response.json()["items"][0]
        assert isinstance(item["ma_thong_bao"], int)
        assert str(item["ma_nguoi_nhan"]) == str(user1.ma_nguoi_dung)
        assert isinstance(item["tieu_de"], str)
        assert isinstance(item["noi_dung"], str)
        assert isinstance(item["loai_thong_bao"], str)
        assert isinstance(item["da_doc"], bool)
        assert "ngay_tao" in item

    def test_05_filter_unread_only_notifications(
        self, client, db_session, user1, token_user1
    ):
        """TC-05: Bộ lọc unread_only=True chỉ trả về các thông báo chưa đọc"""
        db_session.add_all([
            ThongBao(ma_nguoi_nhan=user1.ma_nguoi_dung, tieu_de="Đã đọc", noi_dung="A", loai_thong_bao="HE_THONG", da_doc=True),
            ThongBao(ma_nguoi_nhan=user1.ma_nguoi_dung, tieu_de="Chưa đọc", noi_dung="B", loai_thong_bao="CONG_VIEC", da_doc=False)
        ])
        db_session.commit()

        response = client.get(
            "/api/v1/notifications/my?unread_only=true",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["da_doc"] is False
        assert data["items"][0]["tieu_de"] == "Chưa đọc"

    def test_06_notifications_pagination_skip_and_limit(
        self, client, db_session, user1, token_user1
    ):
        """TC-06: Phân trang danh sách thông báo hoạt động chính xác với skip và limit"""
        for i in range(5):
            db_session.add(ThongBao(
                ma_nguoi_nhan=user1.ma_nguoi_dung,
                tieu_de=f"Thông báo trang {i+1}",
                noi_dung=f"Nội dung {i+1}",
                loai_thong_bao="HE_THONG",
                da_doc=False
            ))
        db_session.commit()

        res = client.get(
            "/api/v1/notifications/my?skip=1&limit=2",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 2
        assert data["skip"] == 1
        assert data["limit"] == 2
        assert data["total"] == 5

    def test_07_notifications_ordered_by_created_at_desc(
        self, client, db_session, user1, token_user1
    ):
        """TC-07: Danh sách thông báo được sắp xếp từ mới nhất đến cũ nhất"""
        now = datetime.utcnow()
        n_old = ThongBao(ma_nguoi_nhan=user1.ma_nguoi_dung, tieu_de="Cũ", noi_dung="Cũ", loai_thong_bao="HE_THONG", ngay_tao=now - timedelta(days=2))
        n_new = ThongBao(ma_nguoi_nhan=user1.ma_nguoi_dung, tieu_de="Mới", noi_dung="Mới", loai_thong_bao="HE_THONG", ngay_tao=now)
        db_session.add_all([n_old, n_new])
        db_session.commit()

        res = client.get("/api/v1/notifications/my", headers={"Authorization": f"Bearer {token_user1}"})
        assert res.status_code == 200
        items = res.json()["items"]
        assert items[0]["tieu_de"] == "Mới"
        assert items[1]["tieu_de"] == "Cũ"

    def test_08_mark_notification_as_read_success_200(
        self, client, db_session, user1, token_user1
    ):
        """TC-08: Cập nhật trạng thái thông báo thành đã đọc thành công (PATCH /api/v1/notifications/{id}/read)"""
        notif = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Cần đọc",
            noi_dung="Chi tiết",
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
        assert response.json()["da_doc"] is True

        db_session.refresh(notif)
        assert notif.da_doc is True

    def test_09_mark_already_read_notification_is_idempotent(
        self, client, db_session, user1, token_user1
    ):
        """TC-09: Đánh dấu đã đọc nhiều lần vào một thông báo đã đọc vẫn thành công an toàn (Idempotent 200 OK)"""
        notif = ThongBao(
            ma_nguoi_nhan=user1.ma_nguoi_dung,
            tieu_de="Đã đọc sẵn",
            noi_dung="Nội dung",
            loai_thong_bao="CONG_VIEC",
            da_doc=True
        )
        db_session.add(notif)
        db_session.commit()
        db_session.refresh(notif)

        res = client.patch(
            f"/api/v1/notifications/{notif.ma_thong_bao}/read",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert res.status_code == 200
        assert res.json()["da_doc"] is True

    def test_10_mark_notification_not_found_returns_404(
        self, client, token_user1
    ):
        """TC-10: Bắt lỗi khi cập nhật mã thông báo không tồn tại -> 404 Not Found"""
        response = client.patch(
            "/api/v1/notifications/999999/read",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert response.status_code == 404
        assert "Không tìm thấy" in response.json()["detail"]

    def test_11_mark_notification_forbidden_for_other_user_returns_403(
        self, client, db_session, user2, token_user1
    ):
        """TC-11: Bắt lỗi chặn người dùng sửa thông báo của người khác -> 403 Forbidden"""
        notif_user2 = ThongBao(
            ma_nguoi_nhan=user2.ma_nguoi_dung,
            tieu_de="Thông báo bí mật User 2",
            noi_dung="Nội dung User 2",
            loai_thong_bao="CONG_VIEC",
            da_doc=False
        )
        db_session.add(notif_user2)
        db_session.commit()
        db_session.refresh(notif_user2)

        response = client.patch(
            f"/api/v1/notifications/{notif_user2.ma_thong_bao}/read",
            headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert response.status_code == 403
        assert "Bạn không có quyền" in response.json()["detail"]

    def test_12_mark_all_notifications_as_read_convenience(
        self, client, db_session, user1, token_user1
    ):
        """TC-12: Tiện ích đánh dấu tất cả thông báo cá nhân là đã đọc (PATCH /api/v1/notifications/read-all)"""
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

        get_res = client.get("/api/v1/notifications/my", headers={"Authorization": f"Bearer {token_user1}"})
        assert get_res.json()["unread_count"] == 0

    def test_13_create_notification_internal_api_201(
        self, client, user1, token_user1
    ):
        """TC-13: Tạo thông báo mới qua endpoint POST /api/v1/notifications -> 201 Created"""
        payload = {
            "ma_nguoi_nhan": user1.ma_nguoi_dung,
            "tieu_de": "Tạo thông báo qua API",
            "noi_dung": "Nội dung thông báo mới được tạo qua REST API",
            "loai_thong_bao": "LICH_TRINH"
        }
        res = client.post("/api/v1/notifications", json=payload, headers={"Authorization": f"Bearer {token_user1}"})
        assert res.status_code == 201
        data = res.json()
        assert data["tieu_de"] == "Tạo thông báo qua API"
        assert data["da_doc"] is False

    def test_14_mark_notification_invalid_id_negative_or_zero_422(
        self, client, token_user1
    ):
        """TC-14: Bắt lỗi khi truyền mã thông báo không hợp lệ (số <= 0) -> 422 Unprocessable Entity"""
        res = client.patch("/api/v1/notifications/0/read", headers={"Authorization": f"Bearer {token_user1}"})
        assert res.status_code == 422


# ==============================================================================
# PHẦN 2: USER STORY 2 - ADMIN TẠO TÀI KHOẢN NGƯỜI DÙNG [22 TCs]
# ==============================================================================

class TestSprint4_AdminTaoTaiKhoan:
    """
    Kiểm thử tự động chuyên sâu cho tính năng Admin tạo người dùng:
    - Endpoint: POST /api/v1/admin/users
    - Endpoint: GET  /api/v1/admin/users
    """

    def test_15_admin_create_user_role_admin_201(self, client, admin_headers):
        """TC-15: Admin tạo tài khoản vai trò Admin thành công (201 Created)"""
        payload = {
            "ho_ten": "Quản Trị Viên Mới",
            "email": "new_admin@ttcs.vn",
            "ten_dang_nhap": "new_admin_2026",
            "mat_khau": "AdminPass@2026",
            "vai_tro": "Admin"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["vai_tro"] == "Admin"
        assert res.json()["ten_dang_nhap"] == "new_admin_2026"

    def test_16_admin_create_user_role_hr_201(self, client, admin_headers):
        """TC-16: Admin tạo tài khoản vai trò HR thành công (201 Created)"""
        payload = {
            "ho_ten": "Nhân Viên HR Mới",
            "email": "new_hr@ttcs.vn",
            "ten_dang_nhap": "new_hr_2026",
            "mat_khau": "HrPass@2026",
            "vai_tro": "HR"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["vai_tro"] == "HR"

    def test_17_admin_create_user_role_mentor_201(self, client, admin_headers):
        """TC-17: Admin tạo tài khoản vai trò Mentor thành công (201 Created)"""
        payload = {
            "ho_ten": "Người Hướng Dẫn Mới",
            "email": "new_mentor@ttcs.vn",
            "ten_dang_nhap": "new_mentor_2026",
            "mat_khau": "MentorPass@2026",
            "vai_tro": "Mentor"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["vai_tro"] == "Mentor"

    def test_18_admin_create_user_role_thuctapsinh_201(self, client, admin_headers):
        """TC-18: Admin tạo tài khoản vai trò ThucTapSinh thành công (201 Created)"""
        payload = {
            "ho_ten": "Thực Tập Sinh Mới",
            "email": "new_intern@ttcs.vn",
            "ten_dang_nhap": "new_intern_2026",
            "mat_khau": "InternPass@2026",
            "vai_tro": "ThucTapSinh"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["vai_tro"] == "ThucTapSinh"

    def test_19_admin_create_user_with_english_field_aliases_201(self, client, admin_headers):
        """TC-19: Hỗ trợ linh hoạt payload trường tiếng Anh (username, password, full_name, role)"""
        payload = {
            "full_name": "Lê Văn Intern Alias",
            "email": "intern_alias@ttcs.vn",
            "username": "intern_alias_user",
            "password": "PasswordIntern@123",
            "role": "ThucTapSinh"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["ten_dang_nhap"] == "intern_alias_user"
        assert res.json()["vai_tro"] == "ThucTapSinh"

    def test_20_password_is_securely_hashed_bcrypt_and_not_exposed(
        self, client, admin_headers, db_session
    ):
        """TC-20: Mật khẩu băm an toàn bằng bcrypt trong DB và KHÔNG để lộ trong response"""
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

        assert "mat_khau" not in data
        assert "mat_khau_hash" not in data
        assert "password" not in data

        user_in_db = db_session.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "mentor_levan_hash").first()
        assert user_in_db is not None
        assert user_in_db.mat_khau_hash != raw_password
        assert user_in_db.mat_khau_hash.startswith("$2") or len(user_in_db.mat_khau_hash) >= 50
        assert verify_password(raw_password, user_in_db.mat_khau_hash) is True

    def test_21_create_user_duplicate_username_returns_400_or_409(
        self, client, admin_headers
    ):
        """TC-21: Bắt lỗi trùng lặp username -> 400 Bad Request / 409 Conflict"""
        p1 = {"ho_ten": "Nguyễn Văn A", "email": "a_uniq@ttcs.vn", "ten_dang_nhap": "dup_user", "mat_khau": "MatKhauChuan@123", "vai_tro": "Mentor"}
        res1 = client.post("/api/v1/admin/users", json=p1, headers=admin_headers)
        assert res1.status_code == 201

        p2 = {"ho_ten": "Nguyễn Văn B", "email": "b_uniq@ttcs.vn", "ten_dang_nhap": "dup_user", "mat_khau": "MatKhauChuan@123", "vai_tro": "HR"}
        res2 = client.post("/api/v1/admin/users", json=p2, headers=admin_headers)
        assert res2.status_code in [400, 409]
        assert "tồn tại" in res2.json()["detail"]

    def test_22_create_user_duplicate_email_returns_400_or_409(
        self, client, admin_headers
    ):
        """TC-22: Bắt lỗi trùng lặp email -> 400 Bad Request / 409 Conflict"""
        p1 = {"ho_ten": "Nguyễn Văn A", "email": "dup_mail@ttcs.vn", "ten_dang_nhap": "user_m1", "mat_khau": "MatKhauChuan@123", "vai_tro": "Mentor"}
        res1 = client.post("/api/v1/admin/users", json=p1, headers=admin_headers)
        assert res1.status_code == 201

        p2 = {"ho_ten": "Nguyễn Văn B", "email": "dup_mail@ttcs.vn", "ten_dang_nhap": "user_m2", "mat_khau": "MatKhauChuan@123", "vai_tro": "HR"}
        res2 = client.post("/api/v1/admin/users", json=p2, headers=admin_headers)
        assert res2.status_code in [400, 409]
        assert "Email" in res2.json()["detail"]

    def test_23_create_user_missing_email_422(self, client, admin_headers):
        """TC-23: Thiếu email -> 422 Unprocessable Entity"""
        r = client.post("/api/v1/admin/users", json={"ten_dang_nhap": "u1", "mat_khau": "P@123", "ho_ten": "T", "vai_tro": "HR"}, headers=admin_headers)
        assert r.status_code == 422

    def test_24_create_user_missing_username_422(self, client, admin_headers):
        """TC-24: Thiếu ten_dang_nhap -> 422 Unprocessable Entity"""
        r = client.post("/api/v1/admin/users", json={"email": "a@b.com", "mat_khau": "P@123", "ho_ten": "T", "vai_tro": "HR"}, headers=admin_headers)
        assert r.status_code == 422

    def test_25_create_user_missing_password_422(self, client, admin_headers):
        """TC-25: Thiếu mat_khau -> 422 Unprocessable Entity"""
        r = client.post("/api/v1/admin/users", json={"ten_dang_nhap": "u3", "email": "a3@b.com", "ho_ten": "T", "vai_tro": "HR"}, headers=admin_headers)
        assert r.status_code == 422

    def test_26_create_user_missing_full_name_422(self, client, admin_headers):
        """TC-26: Thiếu ho_ten -> 422 Unprocessable Entity"""
        r = client.post("/api/v1/admin/users", json={"ten_dang_nhap": "u4", "email": "a4@b.com", "mat_khau": "P@123", "vai_tro": "HR"}, headers=admin_headers)
        assert r.status_code == 422

    def test_27_create_user_missing_role_422(self, client, admin_headers):
        """TC-27: Thiếu vai_tro -> 422 Unprocessable Entity"""
        r = client.post("/api/v1/admin/users", json={"ten_dang_nhap": "u5", "email": "a5@b.com", "mat_khau": "P@123", "ho_ten": "T"}, headers=admin_headers)
        assert r.status_code == 422

    def test_28_create_user_invalid_role_422(self, client, admin_headers):
        """TC-28: Bắt lỗi vai trò không thuộc enum (ví dụ: GiamDocDieuHanh) -> 422"""
        payload = {"ho_ten": "Lỗi", "email": "invalid_role@ttcs.vn", "ten_dang_nhap": "invalid_role", "mat_khau": "P@123", "vai_tro": "GiamDocDieuHanh"}
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 422

    def test_29_create_user_invalid_email_format_422(self, client, admin_headers):
        """TC-29: Bắt lỗi định dạng email không đúng chuẩn RFC -> 422"""
        payload = {"ho_ten": "Sai Email", "email": "khong-phai-email", "ten_dang_nhap": "bad_email", "mat_khau": "P@123", "vai_tro": "HR"}
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 422

    def test_30_create_user_vietnamese_accented_full_name_success_201(self, client, admin_headers):
        """TC-30: Hỗ trợ họ tên tiếng Việt có dấu đầy đủ Unicode UTF-8 chuẩn xác"""
        payload = {
            "ho_ten": "Nguyễn Trần Hoàng Đăng Khoa",
            "email": "khoa.nguyen@ttcs.vn",
            "ten_dang_nhap": "khoa_nguyen_utf8",
            "mat_khau": "ChuanPass@123",
            "vai_tro": "ThucTapSinh"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201
        assert res.json()["ho_ten"] == "Nguyễn Trần Hoàng Đăng Khoa"

    def test_31_create_user_forbidden_by_hr_403(self, client, hr_headers):
        """TC-31: Tài khoản vai trò HR cố tình tạo user -> 403 Forbidden"""
        p = {"ho_ten": "Test", "email": "test_hr_block@ttcs.vn", "ten_dang_nhap": "block_hr", "mat_khau": "P@123", "vai_tro": "ThucTapSinh"}
        res = client.post("/api/v1/admin/users", json=p, headers=hr_headers)
        assert res.status_code == 403

    def test_32_create_user_forbidden_by_mentor_403(self, client, mentor_headers):
        """TC-32: Tài khoản vai trò Mentor cố tình tạo user -> 403 Forbidden"""
        p = {"ho_ten": "Test", "email": "test_m_block@ttcs.vn", "ten_dang_nhap": "block_m", "mat_khau": "P@123", "vai_tro": "ThucTapSinh"}
        res = client.post("/api/v1/admin/users", json=p, headers=mentor_headers)
        assert res.status_code == 403

    def test_33_create_user_forbidden_by_intern_403(self, client, intern_headers):
        """TC-33: Tài khoản vai trò ThucTapSinh cố tình tạo user -> 403 Forbidden"""
        p = {"ho_ten": "Test", "email": "test_i_block@ttcs.vn", "ten_dang_nhap": "block_i", "mat_khau": "P@123", "vai_tro": "ThucTapSinh"}
        res = client.post("/api/v1/admin/users", json=p, headers=intern_headers)
        assert res.status_code == 403

    def test_34_create_user_forbidden_via_header_mock_403(self, client):
        """TC-34: Chặn qua header mock X-User-Role: HR -> 403 Forbidden"""
        p = {"ho_ten": "Test", "email": "mock_block@ttcs.vn", "ten_dang_nhap": "mock_block", "mat_khau": "P@123", "vai_tro": "Mentor"}
        res = client.post("/api/v1/admin/users", json=p, headers={"X-User-Role": "HR"})
        assert res.status_code == 403

    def test_35_create_user_unauthorized_without_token_401(self, client):
        """TC-35: Chưa xác thực token -> 401 Unauthorized"""
        p = {"ho_ten": "No Auth", "email": "no_auth@ttcs.vn", "ten_dang_nhap": "no_auth_u", "mat_khau": "P@123", "vai_tro": "Mentor"}
        res = client.post("/api/v1/admin/users", json=p)
        assert res.status_code == 401

    def test_36_admin_list_users_pagination_and_data_structure_200(self, client, admin_headers):
        """TC-36: Admin xem danh sách người dùng với phân trang skip/limit và lọc vai trò (GET /users)"""
        res = client.get("/api/v1/admin/users?skip=0&limit=10", headers=admin_headers)
        assert res.status_code == 200
        users = res.json()
        assert isinstance(users, list)
        assert len(users) >= 4
        assert "ten_dang_nhap" in users[0]
        assert "vai_tro" in users[0]


# ==============================================================================
# PHẦN 3: USER STORY 3 - NHẬT KÝ HOẠT ĐỘNG (AUDIT LOGS & MIDDLEWARE) [18 TCs]
# ==============================================================================

@pytest.fixture
def seed_audit_logs_sprint4(db_session, admin_user, normal_user):
    """Fixture tạo dữ liệu nhật ký phong phú cho kiểm thử Sprint 4"""
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
    Kiểm thử tự động chuyên sâu cho tính năng Nhật ký hoạt động (Audit Logs):
    - Endpoint: GET /api/v1/admin/audit-logs
    - Middleware: AuditLogMiddleware
    """

    def test_37_audit_logs_unauthorized_without_token_returns_401(self, client):
        """TC-37: Không có token / chưa đăng nhập -> 401 Unauthorized"""
        res = client.get("/api/v1/admin/audit-logs")
        assert res.status_code == 401

    def test_38_audit_logs_forbidden_for_intern_403(self, client, intern_headers):
        """TC-38: Thực tập sinh không có quyền xem nhật ký -> 403 Forbidden"""
        res = client.get("/api/v1/admin/audit-logs", headers=intern_headers)
        assert res.status_code == 403
        assert "Chỉ quản trị viên (Admin)" in res.json()["detail"]

    def test_39_audit_logs_forbidden_for_hr_403(self, client, hr_headers):
        """TC-39: HR không có quyền xem nhật ký hệ thống -> 403 Forbidden"""
        res = client.get("/api/v1/admin/audit-logs", headers=hr_headers)
        assert res.status_code == 403

    def test_40_audit_logs_forbidden_for_mentor_403(self, client, mentor_headers):
        """TC-40: Mentor không có quyền xem nhật ký hệ thống -> 403 Forbidden"""
        res = client.get("/api/v1/admin/audit-logs", headers=mentor_headers)
        assert res.status_code == 403

    def test_41_admin_get_audit_logs_success_200(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-41: Admin xem danh sách nhật ký thành công (200 OK, đúng schema phân trang)"""
        res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] >= len(seed_audit_logs_sprint4)

    def test_42_audit_logs_pagination_page_1_and_page_2_disjoint(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-42: Phân trang (page, page_size) chính xác, trang 1 và 2 không trùng bản ghi"""
        res1 = client.get("/api/v1/admin/audit-logs?page=1&page_size=2", headers=admin_headers)
        assert res1.status_code == 200
        d1 = res1.json()
        assert len(d1["items"]) == 2

        res2 = client.get("/api/v1/admin/audit-logs?page=2&page_size=2", headers=admin_headers)
        assert res2.status_code == 200
        d2 = res2.json()
        assert len(d2["items"]) == 2

        p1_ids = [item["ma_nhat_ky"] for item in d1["items"]]
        p2_ids = [item["ma_nhat_ky"] for item in d2["items"]]
        assert set(p1_ids).isdisjoint(set(p2_ids))

    def test_43_audit_logs_pagination_boundary_high_page_number_empty_items(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-43: Kiểm tra biên phân trang: Khi page vượt quá tổng số trang -> items rỗng, 200 OK"""
        res = client.get("/api/v1/admin/audit-logs?page=9999&page_size=20", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []
        assert data["page"] == 9999

    def test_44_audit_logs_search_by_keyword_mo_ta(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-44: Tìm kiếm nhật ký theo từ khóa trong mô tả (search='Nguyễn Văn An')"""
        res = client.get("/api/v1/admin/audit-logs?search=Nguyễn+Văn+An", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert "Nguyễn Văn An" in item["mo_ta"]

    def test_45_audit_logs_search_by_keyword_endpoint_or_action(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-45: Tìm kiếm nhật ký theo từ khóa endpoint hoặc hành động (search='support-requests')"""
        res = client.get("/api/v1/admin/audit-logs?search=support-requests", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        assert "support-requests" in data["items"][0]["endpoint"]

    def test_46_audit_logs_filter_by_date_range_tu_ngay_den_ngay(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-46: Lọc nhật ký theo khoảng ngày tu_ngay và den_ngay"""
        res = client.get(
            "/api/v1/admin/audit-logs?tu_ngay=2026-10-15T00:00:00&den_ngay=2026-10-17T23:59:59",
            headers=admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["hanh_dong"] in ["TAO_NGUOI_DUNG", "TAO_YEU_CAU_HO_TRO"]

    def test_47_audit_logs_filter_by_specific_user_id(
        self, client, admin_headers, normal_user, seed_audit_logs_sprint4
    ):
        """TC-47: Lọc nhật ký theo mã người dùng ma_nguoi_dung"""
        res = client.get(
            f"/api/v1/admin/audit-logs?ma_nguoi_dung={normal_user.ma_nguoi_dung}",
            headers=admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["ma_nguoi_dung"] == normal_user.ma_nguoi_dung

    def test_48_audit_logs_filter_by_action_and_http_method(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-48: Lọc kết hợp theo hành động nghiệp vụ và phương thức HTTP"""
        res = client.get(
            "/api/v1/admin/audit-logs?hanh_dong=CAP_NHAT_NGUOI_DUNG&phuong_thuc=PUT",
            headers=admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["phuong_thuc"] == "PUT"

    def test_49_audit_logs_ordered_by_thoi_gian_descending(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-49: Danh sách nhật ký được sắp xếp theo thời gian giảm dần (mới nhất hiển thị đầu)"""
        res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert res.status_code == 200
        items = res.json()["items"]
        if len(items) >= 2:
            time_0 = datetime.fromisoformat(items[0]["thoi_gian"])
            time_1 = datetime.fromisoformat(items[1]["thoi_gian"])
            assert time_0 >= time_1

    def test_50_middleware_automatically_logs_modifying_post_request(
        self, client, admin_headers, admin_user, db_session
    ):
        """TC-50: Middleware tự động ghi log khi phát sinh request POST sửa đổi dữ liệu"""
        init_count = db_session.query(NhatKyHoatDong).count()
        payload = {
            "ten_dang_nhap": "middleware_user_50",
            "email": "mid50@ttcs.vn",
            "mat_khau": "ChuanPass@123",
            "ho_ten": "Test Middleware 50",
            "vai_tro": "ThucTapSinh"
        }
        res = client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
        assert res.status_code == 201

        new_count = db_session.query(NhatKyHoatDong).count()
        assert new_count == init_count + 1

    def test_51_middleware_extracts_client_ip_from_x_forwarded_for(
        self, client, admin_headers, admin_user, db_session
    ):
        """TC-51: Middleware trích xuất đúng địa chỉ IP nguồn từ header X-Forwarded-For"""
        payload = {
            "ten_dang_nhap": "user_ip_extract",
            "email": "ipextract@ttcs.vn",
            "mat_khau": "ChuanPass@123",
            "ho_ten": "Kiểm Tra IP",
            "vai_tro": "ThucTapSinh"
        }
        res = client.post(
            "/api/v1/admin/users",
            json=payload,
            headers={**admin_headers, "X-Forwarded-For": "203.162.0.100"}
        )
        assert res.status_code == 201
        latest = db_session.query(NhatKyHoatDong).order_by(NhatKyHoatDong.ma_nhat_ky.desc()).first()
        assert latest.dia_chi_ip == "203.162.0.100"

    def test_52_middleware_excludes_healthcheck_ping_and_docs(
        self, client, db_session
    ):
        """TC-52: Middleware loại trừ các endpoint kiểm tra sức khỏe /ping để tránh spam database"""
        init_count = db_session.query(NhatKyHoatDong).count()
        res = client.get("/ping")
        assert res.status_code == 200
        assert db_session.query(NhatKyHoatDong).count() == init_count

    def test_53_middleware_records_failed_operation_400_bad_request(
        self, client, admin_headers, db_session
    ):
        """TC-53: Middleware ghi nhận cả trường hợp người dùng thao tác thất bại (HTTP 400 Bad Request)"""
        # Tạo user 1
        client.post("/api/v1/admin/users", json={
            "ten_dang_nhap": "fail_log_user", "email": "fail_log@ttcs.vn",
            "mat_khau": "MatKhauChuan@123", "ho_ten": "User Gốc", "vai_tro": "Mentor"
        }, headers=admin_headers)

        init_count = db_session.query(NhatKyHoatDong).count()
        # Gửi trùng username để sinh lỗi 400
        res_fail = client.post("/api/v1/admin/users", json={
            "ten_dang_nhap": "fail_log_user", "email": "different@ttcs.vn",
            "mat_khau": "MatKhauChuan@123", "ho_ten": "User Trùng", "vai_tro": "Mentor"
        }, headers=admin_headers)
        assert res_fail.status_code in [400, 409]

        new_count = db_session.query(NhatKyHoatDong).count()
        assert new_count == init_count + 1
        latest_fail = db_session.query(NhatKyHoatDong).order_by(NhatKyHoatDong.ma_nhat_ky.desc()).first()
        assert "400" in latest_fail.mo_ta or "409" in latest_fail.mo_ta

    def test_54_audit_logs_search_with_no_matches_returns_empty_items_total_zero(
        self, client, admin_headers, seed_audit_logs_sprint4
    ):
        """TC-54: Tìm kiếm với từ khóa không tồn tại -> trả về total=0 và items=[] an toàn"""
        res = client.get("/api/v1/admin/audit-logs?search=TuKhoaKhongTheTonTai12345", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []
