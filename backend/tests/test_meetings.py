import pytest
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import LichHop, NguoiDung, HoSoThucTap
from services.email_service import (
    send_meeting_invitation_email,
    sent_emails_history,
)
from tests.conftest import MYSQL_AVAILABLE, TestSessionLocal

client = TestClient(app)


def get_test_db():
    """Lấy database session phù hợp môi trường test"""
    from database.session import get_db
    override_fn = app.dependency_overrides.get(get_db)
    if override_fn:
        db_gen = override_fn()
        return next(db_gen)
    return SessionLocal() if MYSQL_AVAILABLE else TestSessionLocal()


@pytest.fixture(autouse=True)
def clear_email_history():
    """Tự động dọn sạch lịch sử email trước mỗi test case"""
    sent_emails_history.clear()
    yield
    sent_emails_history.clear()


# ==============================================================================
# KIỂM THỬ TẠO LỊCH HỌP VÀ GỬI EMAIL HTML TỰ ĐỘNG (BACKGROUND TASKS)
# ==============================================================================

def test_create_meeting_success_and_sends_html_email():
    """
    Kiểm tra tạo lịch họp thành công:
    - API trả về HTTP 201 Created
    - CSDL lưu bản ghi LichHop với thông tin chính xác
    - BackgroundTasks gửi email HTML tự động tới tất cả thực tập sinh được mời
    - Nội dung email HTML chứa đầy đủ tiêu đề, thời gian, địa điểm, người chủ trì
    """
    now = datetime.now()
    start_time = now + timedelta(days=2, hours=9)
    end_time = now + timedelta(days=2, hours=10, minutes=30)

    payload = {
        "tieu_de": "Họp triển khai nhiệm vụ Sprint 4",
        "thoi_gian_bat_dau": start_time.isoformat(),
        "thoi_gian_ket_thuc": end_time.isoformat(),
        "dia_diem": "Phòng họp A1 - Tầng 3",
        "ma_nguoi_chu_tri": 3,  # Nguyễn Hướng Dẫn (Mentor)
        "danh_sach_thuc_tap_sinh": [1, 2],  # Nguyễn Văn A (vana@example.com), Trần Thị B (thib@example.com)
        "noi_dung": "Mang theo laptop và chuẩn bị slide demo kết quả Sprint 3."
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["code"] == 201
    assert "Tạo lịch họp thành công" in res_data["message"]
    assert res_data["data"]["tieu_de"] == "Họp triển khai nhiệm vụ Sprint 4"
    assert res_data["data"]["dia_diem"] == "Phòng họp A1 - Tầng 3"
    assert res_data["data"]["ma_nguoi_chu_tri"] == 3
    assert res_data["data"]["so_luong_nguoi_moi"] == 2
    assert "vana@example.com" in res_data["data"]["danh_sach_email_duoc_moi"]
    assert "thib@example.com" in res_data["data"]["danh_sach_email_duoc_moi"]

    # Kiểm tra CSDL
    db = get_test_db()
    meeting_id = res_data["data"]["ma_lich_hop"]
    saved_meeting = db.query(LichHop).filter(LichHop.ma_lich_hop == meeting_id).first()
    assert saved_meeting is not None
    assert saved_meeting.tieu_de == "Họp triển khai nhiệm vụ Sprint 4"
    assert saved_meeting.dia_diem == "Phòng họp A1 - Tầng 3"
    assert saved_meeting.ma_nguoi_chu_tri == 3

    # Kiểm tra BackgroundTasks gửi email HTML
    assert len(sent_emails_history) >= 2
    emails = [e for e in sent_emails_history if e.get("to_email") in ["vana@example.com", "thib@example.com"]]
    assert len(emails) == 2

    for em in emails:
        assert "[Thư mời họp] Họp triển khai nhiệm vụ Sprint 4" in em["subject"]
        # Kiểm tra văn bản thuần túy fallback
        assert "Họp triển khai nhiệm vụ Sprint 4" in em["content"]
        assert "Phòng họp A1 - Tầng 3" in em["content"]
        assert "Nguyễn Hướng Dẫn" in em["content"]
        assert "Mang theo laptop và chuẩn bị slide demo" in em["content"]

        # Kiểm tra HTML content
        assert "html_content" in em
        html = em["html_content"]
        assert "<!DOCTYPE html>" in html
        assert "THƯ MỜI THAM GIA CUỘC HỌP" in html
        assert "Họp triển khai nhiệm vụ Sprint 4" in html
        assert "Phòng họp A1 - Tầng 3" in html
        assert "Nguyễn Hướng Dẫn" in html
        assert "Mang theo laptop và chuẩn bị slide demo" in html


def test_create_meeting_invalid_time_end_before_start():
    """Kiểm tra ngoại lệ: thời gian kết thúc trước hoặc bằng thời gian bắt đầu -> báo lỗi 400 hoặc 422"""
    now = datetime.now()
    start_time = now + timedelta(days=1, hours=10)
    end_time = now + timedelta(days=1, hours=9)  # Kết thúc trước bắt đầu!

    payload = {
        "tieu_de": "Họp review code",
        "thoi_gian_bat_dau": start_time.isoformat(),
        "thoi_gian_ket_thuc": end_time.isoformat(),
        "dia_diem": "Google Meet",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": [1]
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code in (400, 422)
    err_detail = str(response.json())
    assert "lớn hơn thời gian bắt đầu" in err_detail


def test_create_meeting_start_time_in_past():
    """Kiểm tra ngoại lệ: thời gian bắt đầu cuộc họp nằm trong quá khứ -> 400 Bad Request"""
    now = datetime.now()
    start_time = now - timedelta(days=2)  # Quá khứ!
    end_time = now - timedelta(days=2, hours=-1)

    payload = {
        "tieu_de": "Họp quá khứ",
        "thoi_gian_bat_dau": start_time.isoformat(),
        "thoi_gian_ket_thuc": end_time.isoformat(),
        "dia_diem": "Phòng 101",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": [1]
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 400
    assert "quá khứ" in response.json()["detail"]


def test_create_meeting_empty_title_or_whitespace():
    """Kiểm tra ngoại lệ: tiêu đề rỗng hoặc chỉ toàn khoảng trắng -> 400 hoặc 422"""
    now = datetime.now()
    start_time = now + timedelta(days=1)
    end_time = now + timedelta(days=1, hours=1)

    payload = {
        "tieu_de": "   ",
        "thoi_gian_bat_dau": start_time.isoformat(),
        "thoi_gian_ket_thuc": end_time.isoformat(),
        "dia_diem": "Phòng 101",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": [1]
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code in (400, 422)
    assert "tiêu đề" in str(response.json()).lower() or "tieu_de" in str(response.json()).lower()


def test_create_meeting_empty_location():
    """Kiểm tra ngoại lệ: địa điểm rỗng hoặc chỉ toàn khoảng trắng -> 400 hoặc 422"""
    now = datetime.now()
    start_time = now + timedelta(days=1)
    end_time = now + timedelta(days=1, hours=1)

    payload = {
        "tieu_de": "Họp hướng dẫn",
        "thoi_gian_bat_dau": start_time.isoformat(),
        "thoi_gian_ket_thuc": end_time.isoformat(),
        "dia_diem": "   ",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": [1]
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code in (400, 422)
    assert "địa điểm" in str(response.json()).lower() or "dia_diem" in str(response.json()).lower()


def test_create_meeting_host_not_found():
    """Kiểm tra ngoại lệ: người chủ trì không tồn tại trong hệ thống -> 404 Not Found"""
    now = datetime.now()
    start_time = now + timedelta(days=1)
    end_time = now + timedelta(days=1, hours=1)

    payload = {
        "tieu_de": "Họp định kỳ",
        "thoi_gian_bat_dau": start_time.isoformat(),
        "thoi_gian_ket_thuc": end_time.isoformat(),
        "dia_diem": "Phòng họp số 1",
        "ma_nguoi_chu_tri": 999999,  # ID không tồn tại
        "danh_sach_thuc_tap_sinh": [1]
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 404
    assert "người chủ trì" in response.json()["detail"].lower()


def test_create_meeting_host_locked_account():
    """Kiểm tra ngoại lệ: tài khoản người chủ trì đang bị khóa -> 400 Bad Request"""
    db = get_test_db()
    # Tạo user bị khóa
    locked_user = db.query(NguoiDung).filter(NguoiDung.email == "locked_mentor@example.com").first()
    if not locked_user:
        locked_user = NguoiDung(
            ho_ten="Mentor Bị Khóa",
            email="locked_mentor@example.com",
            vai_tro="Mentor",
            trang_thai="Khoa"
        )
        db.add(locked_user)
        db.commit()
        db.refresh(locked_user)
    else:
        locked_user.trang_thai = "Khoa"
        db.commit()

    now = datetime.now()
    payload = {
        "tieu_de": "Họp thử nghiệm",
        "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
        "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
        "dia_diem": "Phòng họp 2",
        "ma_nguoi_chu_tri": locked_user.ma_nguoi_dung,
        "danh_sach_thuc_tap_sinh": [1]
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 400
    assert "bị khóa" in response.json()["detail"]


def test_create_meeting_empty_intern_list():
    """Kiểm tra ngoại lệ: danh sách thực tập sinh rỗng -> 400 hoặc 422"""
    now = datetime.now()
    payload = {
        "tieu_de": "Họp cá nhân",
        "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
        "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
        "dia_diem": "Phòng 101",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": []
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code in (400, 422)


def test_create_meeting_intern_not_found():
    """Kiểm tra ngoại lệ: có thực tập sinh trong danh sách không tồn tại -> 404 Not Found"""
    now = datetime.now()
    payload = {
        "tieu_de": "Họp nhóm dự án",
        "thoi_gian_bat_dau": (now + timedelta(days=1)).isoformat(),
        "thoi_gian_ket_thuc": (now + timedelta(days=1, hours=1)).isoformat(),
        "dia_diem": "Phòng họp 2",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": [1, 888888]  # 888888 không tồn tại
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 404
    assert "888888" in response.json()["detail"]


def test_create_meeting_online_link_and_special_chars():
    """Kiểm tra tạo lịch họp trực tuyến với đường link URL và ký tự tiếng Việt có dấu"""
    now = datetime.now()
    payload = {
        "tieu_de": "Trao đổi kỹ thuật: Kiến trúc Microservices & Docker hóa",
        "thoi_gian_bat_dau": (now + timedelta(days=3, hours=14)).isoformat(),
        "thoi_gian_ket_thuc": (now + timedelta(days=3, hours=16)).isoformat(),
        "dia_diem": "https://meet.google.com/xyz-abcd-uvw",
        "ma_nguoi_chu_tri": 3,
        "danh_sach_thuc_tap_sinh": [1],
        "noi_dung": "Yêu cầu đọc trước tài liệu Docker & Kubernetes trước buổi họp."
    }

    response = client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["dia_diem"] == "https://meet.google.com/xyz-abcd-uvw"

    assert len(sent_emails_history) >= 1
    last_email = sent_emails_history[-1]
    assert "https://meet.google.com/xyz-abcd-uvw" in last_email["content"]
    assert "https://meet.google.com/xyz-abcd-uvw" in last_email["html_content"]
    assert "Kiến trúc Microservices" in last_email["html_content"]


def test_lich_hop_model_to_dict_and_orm():
    """Kiểm tra phương thức to_dict() và quan hệ ORM của model LichHop"""
    db = get_test_db()
    meeting = LichHop(
        tieu_de="Họp tổng kết tháng",
        thoi_gian_bat_dau=datetime(2026, 11, 1, 8, 30),
        thoi_gian_ket_thuc=datetime(2026, 11, 1, 10, 0),
        dia_diem="Hội trường B",
        ma_nguoi_chu_tri=3
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    d = meeting.to_dict()
    assert d["ma_lich_hop"] == meeting.ma_lich_hop
    assert d["tieu_de"] == "Họp tổng kết tháng"
    assert "2026-11-01" in d["thoi_gian_bat_dau"]
    assert d["dia_diem"] == "Hội trường B"
    assert d["ma_nguoi_chu_tri"] == 3

    # Kiểm tra quan hệ ORM
    assert meeting.nguoi_chu_tri is not None
    assert meeting.nguoi_chu_tri.ma_nguoi_dung == 3
    assert any(m.ma_lich_hop == meeting.ma_lich_hop for m in meeting.nguoi_chu_tri.danh_sach_lich_hop_chu_tri)


def test_send_meeting_invitation_email_service_directly():
    """Kiểm thử trực tiếp hàm send_meeting_invitation_email trong email_service"""
    sent = send_meeting_invitation_email(
        to_email="student_test@example.com",
        intern_name="Lê Văn Test",
        meeting_title="Phỏng vấn đánh giá cuối kỳ",
        start_time="09:00 ngày 15/11/2026",
        end_time="10:00 ngày 15/11/2026",
        location="Văn phòng HR Tầng 5",
        host_name="Trần Trưởng Phòng",
        note="Chuẩn bị báo cáo tổng kết"
    )
    assert sent is True
    assert len(sent_emails_history) >= 1
    email = sent_emails_history[-1]
    assert email["to_email"] == "student_test@example.com"
    assert "Phỏng vấn đánh giá cuối kỳ" in email["subject"]
    assert "Lê Văn Test" in email["content"]
    assert "<!DOCTYPE html>" in email["html_content"]
    assert "Văn phòng HR Tầng 5" in email["html_content"]


def test_get_meetings_list_and_filter():
    """Kiểm tra API GET /api/v1/meetings lấy danh sách và lọc"""
    response = client.get("/api/v1/meetings")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "items" in data["data"]
    assert "total" in data["data"]


def test_meeting_qr_checkin_all_edge_cases():
    """Kiểm tra toàn diện các ngoại lệ của API POST /api/v1/meetings/{id}/checkin"""
    db = get_test_db()
    now = datetime.now()
    meeting = LichHop(
        tieu_de="Họp Sprint Review Tuần 2 Test",
        thoi_gian_bat_dau=now - timedelta(minutes=5),
        thoi_gian_ket_thuc=now + timedelta(minutes=55),
        dia_diem="Phòng Lab 302",
        ma_nguoi_chu_tri=3
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    hs1 = db.query(HoSoThucTap).filter(HoSoThucTap.ma_mentor == 3, HoSoThucTap.trang_thai_xet_duyet == "DaDuyet").first()
    assert hs1 is not None

    # 1. Điểm danh thành công
    res = client.post(f"/api/v1/meetings/{meeting.ma_lich_hop}/checkin", json={
        "ma_dinh_danh": str(hs1.ma_ho_so),
        "ghi_chu": "Có mặt đầy đủ"
    })
    assert res.status_code == 200
    assert res.json()["code"] == 200
    assert "Điểm danh thành công" in res.json()["message"]

    # 2. Chống double check-in (HTTP 409)
    res_dup = client.post(f"/api/v1/meetings/{meeting.ma_lich_hop}/checkin", json={
        "ma_dinh_danh": str(hs1.ma_ho_so)
    })
    assert res_dup.status_code == 409
    assert "đã điểm danh tham gia" in res_dup.json()["detail"]

    # 3. Cuộc họp không tồn tại (HTTP 404)
    res_not_found = client.post("/api/v1/meetings/99999/checkin", json={
        "ma_dinh_danh": str(hs1.ma_ho_so)
    })
    assert res_not_found.status_code == 404

    # 4. Sinh viên không tồn tại (HTTP 404)
    res_fake_user = client.post(f"/api/v1/meetings/{meeting.ma_lich_hop}/checkin", json={
        "ma_dinh_danh": "NOT_EXISTING_ID_99999"
    })
    assert res_fake_user.status_code == 404

    # 5. Sinh viên KHÔNG THUỘC LỚP/NHÓM CỦA MENTOR CHỦ TRÌ (HTTP 403)
    hs_other = db.query(HoSoThucTap).filter(
        HoSoThucTap.ma_mentor != 3,
        HoSoThucTap.ma_mentor != None,
        HoSoThucTap.trang_thai_xet_duyet == "DaDuyet"
    ).first()
    if not hs_other:
        hs_other = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so != hs1.ma_ho_so).first()
        if hs_other:
            hs_other.ma_mentor = 999
            db.commit()

    if hs_other:
        res_forbidden = client.post(f"/api/v1/meetings/{meeting.ma_lich_hop}/checkin", json={
            "ma_dinh_danh": str(hs_other.ma_ho_so)
        })
        assert res_forbidden.status_code == 403
        assert "không thuộc nhóm hướng dẫn" in res_forbidden.json()["detail"]

    # 6. Buổi họp đã kết thúc (QR hết hạn) (HTTP 400)
    past_meeting = LichHop(
        tieu_de="Họp đã kết thúc tuần trước Test",
        thoi_gian_bat_dau=now - timedelta(days=2, hours=2),
        thoi_gian_ket_thuc=now - timedelta(days=2, hours=1),
        dia_diem="Online Meet",
        ma_nguoi_chu_tri=3
    )
    db.add(past_meeting)
    db.commit()
    db.refresh(past_meeting)

    res_expired = client.post(f"/api/v1/meetings/{past_meeting.ma_lich_hop}/checkin", json={
        "ma_dinh_danh": str(hs1.ma_ho_so)
    })
    assert res_expired.status_code == 400
    assert "đã kết thúc" in res_expired.json()["detail"]
