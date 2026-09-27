from datetime import date
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from services.email_service import sent_emails_history
from database.session import get_db
from database.models import HopDong, HoSoThucTap

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: PATCH /api/v1/contracts/{id}/confirm
# ==============================================================================

@pytest.fixture(autouse=True)
def clear_email_history():
    """Xóa lịch sử gửi email trước và sau mỗi test case"""
    sent_emails_history.clear()
    yield
    sent_emails_history.clear()


def test_confirm_contract_success_default_payload():
    """Kiểm tra xác nhận ký hợp đồng thành công với body mặc định ({}) -> 200 OK"""
    response = client.patch("/api/v1/contracts/1/confirm", json={})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["message"] == "Xác nhận ký hợp đồng và cập nhật trạng thái thực tập thành công"
    assert "data" in res_data

    contract = res_data["data"]
    assert contract["ma_hop_dong"] == 1
    assert contract["ma_ho_so"] == 1
    assert contract["trang_thai"] == "DaXacNhan"
    assert contract["trang_thai_thuc_tap"] == "DangThucTap"
    assert contract["ngay_ky"] == date.today().isoformat()
    assert contract["sinh_vien"]["ho_ten"] == "Nguyễn Văn A"


def test_confirm_contract_success_without_body():
    """Kiểm tra gọi endpoint không truyền body request -> tự động nhận diện giá trị mặc định"""
    response = client.patch("/api/v1/contracts/1/confirm")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai"] == "DaXacNhan"
    assert res_data["data"]["trang_thai_thuc_tap"] == "DangThucTap"


def test_confirm_contract_success_with_custom_date_and_note():
    """Kiểm tra xác nhận hợp đồng với ngày ký cụ thể và ghi chú mã ký số OTP"""
    custom_sign_date = "2026-09-27"
    payload = {
        "trang_thai": "DaXacNhan",
        "trang_thai_thuc_tap": "DangThucTap",
        "ngay_ky": custom_sign_date,
        "ghi_chu": "Mã xác thực OTP: ICTU-SIGNED-9921-OK"
    }
    response = client.patch("/api/v1/contracts/1/confirm", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai"] == "DaXacNhan"
    assert res_data["data"]["ngay_ky"] == custom_sign_date
    assert res_data["data"]["trang_thai_thuc_tap"] == "DangThucTap"


def test_confirm_contract_updates_database_atomically():
    """Kiểm tra tính toàn vẹn (Atomic): Cả bảng hop_dong và ho_so_thuc_tap đều được lưu vào CSDL"""
    response = client.patch("/api/v1/contracts/1/confirm", json={
        "trang_thai": "DaXacNhan",
        "trang_thai_thuc_tap": "DangThucTap"
    })
    assert response.status_code == 200

    # Kiểm tra đồng bộ qua API GET /api/v1/interns/1
    res_intern = client.get("/api/v1/interns/1")
    assert res_intern.status_code == 200
    assert res_intern.json()["data"]["trang_thai_thuc_tap"] == "DangThucTap"


def test_confirm_contract_sends_email_notification():
    """Kiểm tra hệ thống tự động gửi email thông báo ký hợp đồng thành công qua BackgroundTasks"""
    response = client.patch("/api/v1/contracts/1/confirm", json={
        "ghi_chu": "Ký số thành công qua giao thức VNPT-CA"
    })
    assert response.status_code == 200

    # Xác minh trong lịch sử gửi email
    assert len(sent_emails_history) >= 1
    last_email = sent_emails_history[-1]
    assert "vana" in last_email["to_email"]
    assert "Hợp đồng thực tập #1" in last_email["subject"]
    assert "Đang thực tập (Chính thức)" in last_email["content"]
    assert "VNPT-CA" in last_email["content"]


def test_confirm_contract_not_found_404():
    """Kiểm tra báo lỗi 404 khi ma_hop_dong không tồn tại"""
    response = client.patch("/api/v1/contracts/99999/confirm", json={})
    assert response.status_code == 404
    assert "Không tìm thấy hợp đồng ID: 99999" in response.json()["detail"]


def test_confirm_contract_invalid_status_value_422():
    """Kiểm tra báo lỗi 422 khi truyền trạng thái hợp đồng không hợp lệ"""
    payload = {
        "trang_thai": "HopDongKhongHopLe"
    }
    response = client.patch("/api/v1/contracts/1/confirm", json=payload)
    assert response.status_code == 422
    assert "Trạng thái hợp đồng không hợp lệ" in str(response.json()["detail"])


def test_confirm_contract_invalid_internship_status_422():
    """Kiểm tra báo lỗi 422 khi truyền trạng thái thực tập không nằm trong whitelist"""
    payload = {
        "trang_thai_thuc_tap": "TrangThaiSai"
    }
    response = client.patch("/api/v1/contracts/1/confirm", json=payload)
    assert response.status_code == 422
    assert "Trạng thái thực tập không hợp lệ" in str(response.json()["detail"])


def test_confirm_contract_whitespace_stripping():
    """Kiểm tra hệ thống tự động cắt khoảng trắng thừa đầu cuối của các trường text"""
    payload = {
        "trang_thai": "   DaXacNhan   ",
        "trang_thai_thuc_tap": "   DangThucTap   ",
        "ghi_chu": "   Đã xác nhận ký điện tử   "
    }
    response = client.patch("/api/v1/contracts/1/confirm", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai"] == "DaXacNhan"
    assert res_data["data"]["trang_thai_thuc_tap"] == "DangThucTap"


def test_confirm_contract_note_exceeds_max_length_422():
    """Kiểm tra báo lỗi 422 khi ghi chú vượt quá 500 ký tự"""
    payload = {
        "ghi_chu": "X" * 501
    }
    response = client.patch("/api/v1/contracts/1/confirm", json=payload)
    assert response.status_code == 422


def test_confirm_contract_invalid_id_type_422():
    """Kiểm tra báo lỗi 422 khi mã hợp đồng ID không phải số nguyên"""
    response = client.patch("/api/v1/contracts/abc/confirm", json={})
    assert response.status_code == 422
