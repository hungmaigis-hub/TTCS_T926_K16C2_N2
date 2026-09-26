import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from services.email_service import (
    send_document_approval_email,
    send_profile_approval_email,
    send_email_smtp,
    sent_emails_history
)

# Khởi tạo client test API
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_email_history():
    """Tự động dọn sạch lịch sử email trước mỗi test case"""
    sent_emails_history.clear()
    yield
    sent_emails_history.clear()


# ==============================================================================
# KIỂM THỬ TÍCH HỢP FASTAPI BACKGROUNDTASKS VỚI API DUYỆT TÀI LIỆU
# ==============================================================================

def test_patch_document_status_triggers_email_daduyet():
    """Kiểm tra khi duyệt tài liệu DaDuyet: API trả về 200 và tự động gửi email thông báo phê duyệt"""
    payload = {
        "trang_thai_duyet": "DaDuyet",
        "ghi_chu": "Hồ sơ CV đạt tiêu chuẩn yêu cầu của phòng kỹ thuật."
    }
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai_duyet"] == "DaDuyet"

    # Kiểm tra BackgroundTasks đã thực thi và email được ghi nhận
    assert len(sent_emails_history) >= 1
    latest_email = sent_emails_history[-1]
    
    # Tài liệu 1 thuộc hồ sơ 1 (Nguyễn Văn A - vana@example.com)
    assert latest_email["to_email"] == "vana@example.com"
    assert "PHÊ DUYỆT" in latest_email["subject"]
    assert "Nguyễn Văn A" in latest_email["content"]
    assert "Hồ sơ năng lực (CV)" in latest_email["content"]
    assert "ĐÃ PHÊ DUYỆT" in latest_email["content"]
    assert "Hồ sơ CV đạt tiêu chuẩn yêu cầu" in latest_email["content"]


def test_patch_document_status_triggers_email_tuchoi_with_note():
    """Kiểm tra khi từ chối tài liệu TuChoi kèm lý do: Email gửi đi thể hiện rõ trạng thái từ chối và lý do"""
    reason = "Bản scan CV bị mờ và thiếu thông tin liên lạc dự phòng. Vui lòng cập nhật lại."
    payload = {
        "trang_thai_duyet": "TuChoi",
        "ghi_chu": reason
    }
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["trang_thai_duyet"] == "TuChoi"

    assert len(sent_emails_history) >= 1
    latest_email = sent_emails_history[-1]
    assert latest_email["to_email"] == "vana@example.com"
    assert "TỪ CHỐI" in latest_email["subject"]
    assert "BỊ TỪ CHỐI" in latest_email["content"]
    assert reason in latest_email["content"]


def test_patch_document_status_triggers_email_choduyet():
    """Kiểm tra khi hoàn trạng thái về ChoDuyet: Email thông báo đúng trạng thái chờ duyệt"""
    payload = {
        "trang_thai_duyet": "ChoDuyet"
    }
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["trang_thai_duyet"] == "ChoDuyet"

    assert len(sent_emails_history) >= 1
    latest_email = sent_emails_history[-1]
    assert latest_email["to_email"] == "vana@example.com"
    assert "CHỜ DUYỆT" in latest_email["subject"].upper()
    assert "CHỜ DUYỆT" in latest_email["content"]


def test_patch_document_without_note_does_not_contain_note_line():
    """Kiểm tra khi duyệt không có ghi chú: Email không có dòng ghi chú thừa"""
    payload = {"trang_thai_duyet": "DaDuyet"}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200

    latest_email = sent_emails_history[-1]
    assert "Ghi chú / Nhận xét:" not in latest_email["content"]


def test_patch_document_strip_whitespace_in_note():
    """Kiểm tra ghi chú có khoảng trắng ở hai đầu được tự động cắt gọn gàng"""
    payload = {
        "trang_thai_duyet": "DaDuyet",
        "ghi_chu": "   Nội dung có khoảng trắng thừa   "
    }
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200

    latest_email = sent_emails_history[-1]
    assert "Nội dung có khoảng trắng thừa" in latest_email["content"]
    assert "   Nội dung có khoảng trắng thừa   " not in latest_email["content"]


def test_patch_document_note_only_whitespace_treated_as_none():
    """Kiểm tra ghi chú chỉ gồm khoảng trắng sẽ được coi như không có ghi chú"""
    payload = {
        "trang_thai_duyet": "DaDuyet",
        "ghi_chu": "      "
    }
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200

    latest_email = sent_emails_history[-1]
    assert "Ghi chú / Nhận xét:" not in latest_email["content"]


def test_patch_document_note_exceeds_max_length():
    """Kiểm tra ghi chú vượt quá 500 ký tự -> Lỗi 422 Unprocessable Entity"""
    payload = {
        "trang_thai_duyet": "DaDuyet",
        "ghi_chu": "A" * 501
    }
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422
    assert len(sent_emails_history) == 0


def test_patch_document_not_found_does_not_send_email():
    """Kiểm tra khi tài liệu không tồn tại -> 404 và không kích hoạt gửi email"""
    payload = {"trang_thai_duyet": "DaDuyet"}
    response = client.patch("/api/v1/documents/99999/status", json=payload)
    assert response.status_code == 404
    assert len(sent_emails_history) == 0


# ==============================================================================
# KIỂM THỬ TRỰC TIẾP MODULE DỊCH VỤ EMAIL (EMAIL SERVICE)
# ==============================================================================

def test_send_document_approval_email_direct():
    """Kiểm tra gọi trực tiếp hàm send_document_approval_email với loại tài liệu khác nhau"""
    result = send_document_approval_email(
        to_email="test.student@univ.edu.vn",
        intern_name="Trần Thị B",
        document_type="DonXinThucTap",
        status="DaDuyet",
        note="Đã kiểm tra xác nhận từ khoa CNTT"
    )
    assert result is True
    assert len(sent_emails_history) == 1
    mail = sent_emails_history[0]
    assert mail["to_email"] == "test.student@univ.edu.vn"
    assert "Đơn xin thực tập" in mail["subject"]
    assert "Trần Thị B" in mail["content"]
    assert "Đã kiểm tra xác nhận" in mail["content"]


def test_send_profile_approval_email_direct():
    """Kiểm tra gọi trực tiếp hàm send_profile_approval_email cho xét duyệt hồ sơ thực tập"""
    result = send_profile_approval_email(
        to_email="candidate@gmail.com",
        intern_name="Lê Văn C",
        program_name="Thực tập sinh Khóa Mùa Thu 2026",
        status="DaDuyet",
        note="Chào mừng bạn đến với công ty."
    )
    assert result is True
    assert len(sent_emails_history) == 1
    mail = sent_emails_history[0]
    assert mail["to_email"] == "candidate@gmail.com"
    assert "Chúc mừng" in mail["subject"]
    assert "Thực tập sinh Khóa Mùa Thu 2026" in mail["content"]


def test_smtp_send_real_mode_success():
    """Kiểm tra khi MAIL_ENABLED=true và cấu hình hợp lệ: Quy trình kết nối và gửi mail qua SMTP hoạt động chuẩn xác"""
    mock_env = {
        "MAIL_ENABLED": "true",
        "SMTP_HOST": "smtp.mockserver.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "mailer@test.com",
        "SMTP_PASSWORD": "secretpassword",
        "SMTP_FROM_EMAIL": "hr@company.com",
        "SMTP_FROM_NAME": "Phòng Nhân Sự"
    }

    with patch.dict("os.environ", mock_env, clear=False):
        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_server = MagicMock()
            mock_smtp_class.return_value.__enter__.return_value = mock_server

            success = send_email_smtp(
                to_email="recipient@test.com",
                subject="Tiêu đề thử nghiệm",
                content="Nội dung thử nghiệm gửi mail"
            )

            assert success is True
            mock_smtp_class.assert_called_once_with("smtp.mockserver.com", 587, timeout=10)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("mailer@test.com", "secretpassword")
            mock_server.sendmail.assert_called_once()
            assert sent_emails_history[-1]["status"] == "sent"


def test_smtp_send_handles_exception_gracefully():
    """Kiểm tra khi SMTP ném Exception (mất mạng, xác thực sai): Hệ thống không bị crash, trả về False và ghi log lỗi"""
    mock_env = {
        "MAIL_ENABLED": "true",
        "SMTP_HOST": "smtp.invalid.domain",
        "SMTP_PORT": "587",
        "SMTP_USER": "testuser",
        "SMTP_PASSWORD": "testpass"
    }

    with patch.dict("os.environ", mock_env, clear=False):
        with patch("smtplib.SMTP", side_effect=Exception("Không thể kết nối đến máy chủ SMTP")):
            success = send_email_smtp(
                to_email="error.target@test.com",
                subject="Test lỗi",
                content="Nội dung lỗi"
            )

            assert success is False
            assert len(sent_emails_history) == 1
            assert sent_emails_history[-1]["status"] == "failed"
            assert "Không thể kết nối đến máy chủ SMTP" in sent_emails_history[-1]["error"]
