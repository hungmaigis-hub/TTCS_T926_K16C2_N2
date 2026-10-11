import pytest
import sys
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import get_db
from database.models import YeuCauHoTro
from services.email_service import sent_emails_history

client = TestClient(app)

# ==============================================================
# BỘ KIỂM THỬ CHO API: PATCH /api/v1/support-requests/{id}
# ==============================================================

def test_update_support_request_daxuly_success():
    """Kiểm tra HR cập nhật trạng thái yêu cầu sang 'DaXuLy' thành công và gửi email trong nền (HTTP 200)"""
    sent_emails_history.clear()
    payload = {
        "trang_thai": "DaXuLy",
        "phan_hoi_hr": "HR đã ký xác nhận giấy chứng nhận, bạn có thể đến phòng HCNS để nhận."
    }
    response = client.patch("/api/v1/support-requests/1", json=payload)
    assert response.status_code == 200

    res = response.json()
    assert res["status_code"] == 200
    assert "Cập nhật trạng thái yêu cầu hỗ trợ thành công" in res["message"]
    assert "data" in res

    data = res["data"]
    assert data["ma_yeu_cau"] == 1
    assert data["trang_thai"] == "DaXuLy"
    assert data["phan_hoi_hr"] == "HR đã ký xác nhận giấy chứng nhận, bạn có thể đến phòng HCNS để nhận."
    assert data["email_sinh_vien"] == "vana@example.com"
    assert data["ho_ten_sinh_vien"] == "Nguyễn Văn A"

    # Kiểm tra email thông báo đã được gửi trong nền qua BackgroundTasks
    assert len(sent_emails_history) > 0
    latest_email = sent_emails_history[-1]
    assert latest_email["to_email"] == "vana@example.com"
    assert "ĐÃ ĐƯỢC XỬ LÝ" in latest_email["content"] or "XỬ LÝ" in latest_email["subject"]
    assert "HR đã ký xác nhận" in latest_email["content"]


def test_update_support_request_tuchoi_success():
    """Kiểm tra HR cập nhật trạng thái yêu cầu sang 'TuChoi' thành công kèm lý do phản hồi (HTTP 200)"""
    sent_emails_history.clear()
    payload = {
        "trang_thai": "TuChoi",
        "phan_hoi_hr": "Số giờ thực tập chưa đạt tối thiểu theo quy chế đào tạo."
    }
    response = client.patch("/api/v1/support-requests/2", json=payload)
    assert response.status_code == 200

    res = response.json()
    data = res["data"]
    assert data["ma_yeu_cau"] == 2
    assert data["trang_thai"] == "TuChoi"
    assert data["phan_hoi_hr"] == "Số giờ thực tập chưa đạt tối thiểu theo quy chế đào tạo."
    assert data["email_sinh_vien"] == "thib@example.com"
    assert data["ho_ten_sinh_vien"] == "Trần Thị B"

    # Kiểm tra email thông báo từ chối
    assert len(sent_emails_history) > 0
    latest_email = sent_emails_history[-1]
    assert latest_email["to_email"] == "thib@example.com"
    assert "TỪ CHỐI" in latest_email["subject"] or "TỪ CHỐI" in latest_email["content"]
    assert "Số giờ thực tập chưa đạt" in latest_email["content"]


def test_update_support_request_without_hr_feedback():
    """Kiểm tra HR cập nhật trạng thái thành công khi không nhập nội dung phan_hoi_hr (HTTP 200)"""
    payload = {
        "trang_thai": "DaXuLy"
    }
    response = client.patch("/api/v1/support-requests/1", json=payload)
    assert response.status_code == 200

    res = response.json()
    data = res["data"]
    assert data["ma_yeu_cau"] == 1
    assert data["trang_thai"] == "DaXuLy"
    assert data["phan_hoi_hr"] is None


def test_update_support_request_not_found():
    """Kiểm tra báo lỗi HTTP 404 khi ID yêu cầu không tồn tại trong hệ thống"""
    payload = {
        "trang_thai": "DaXuLy",
        "phan_hoi_hr": "Đã xử lý"
    }
    response = client.patch("/api/v1/support-requests/99999", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy yêu cầu hỗ trợ" in response.json()["detail"]


def test_update_support_request_invalid_status():
    """Kiểm tra báo lỗi HTTP 422 khi truyền trạng thái sai quy định (không phải DaXuLy hoặc TuChoi)"""
    payload = {
        "trang_thai": "DangXuLy",
        "phan_hoi_hr": "Đang tiến hành kiểm tra"
    }
    response = client.patch("/api/v1/support-requests/1", json=payload)
    assert response.status_code == 422


def test_update_support_request_missing_status():
    """Kiểm tra báo lỗi HTTP 422 khi thiếu trường bắt buộc trang_thai"""
    payload = {
        "phan_hoi_hr": "Chỉ có ghi chú"
    }
    response = client.patch("/api/v1/support-requests/1", json=payload)
    assert response.status_code == 422
