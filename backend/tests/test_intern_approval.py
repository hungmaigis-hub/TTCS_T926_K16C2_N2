import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from services.email_service import sent_emails_history

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: PATCH /api/v1/interns/{id}/approval
# ==============================================================================

@pytest.fixture(autouse=True)
def clear_email_history():
    """Xóa lịch sử gửi email trước và sau mỗi test case"""
    sent_emails_history.clear()
    yield
    sent_emails_history.clear()


def test_approve_intern_success_da_duyet():
    """Kiểm tra duyệt hồ sơ thành công với trạng thái DaDuyet và có ghi chú"""
    payload = {
        "trang_thai_xet_duyet": "DaDuyet",
        "ghi_chu": "Hồ sơ đạt tiêu chuẩn tuyển dụng, phỏng vấn tốt"
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["message"] == "Cập nhật trạng thái xét duyệt hồ sơ thành công"
    assert "data" in res_data

    intern = res_data["data"]
    assert intern["ma_ho_so"] == 1
    assert intern["trang_thai_xet_duyet"] == "DaDuyet"

    # Kiểm tra email thông báo đã được gửi qua BackgroundTasks
    assert len(sent_emails_history) >= 1
    last_email = sent_emails_history[-1]
    assert "vana" in last_email["to_email"]
    assert "PHÊ DUYỆT" in last_email["subject"]
    assert "Hồ sơ đạt tiêu chuẩn tuyển dụng" in last_email["content"]


def test_approve_intern_success_tu_choi():
    """Kiểm tra từ chối hồ sơ với trạng thái TuChoi và ghi rõ lý do"""
    payload = {
        "trang_thai_xet_duyet": "TuChoi",
        "ghi_chu": "Chưa hoàn thành đủ số tín chỉ yêu cầu"
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["data"]["trang_thai_xet_duyet"] == "TuChoi"

    # Kiểm tra email từ chối
    assert len(sent_emails_history) >= 1
    last_email = sent_emails_history[-1]
    assert "vana" in last_email["to_email"]
    assert "chưa đạt yêu cầu" in last_email["subject"]
    assert "Chưa hoàn thành đủ số tín chỉ yêu cầu" in last_email["content"]


def test_approve_intern_success_cho_duyet():
    """Kiểm tra chuyển trạng thái về ChoDuyet"""
    payload = {
        "trang_thai_xet_duyet": "ChoDuyet"
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai_xet_duyet"] == "ChoDuyet"


def test_approve_intern_success_using_alias_field():
    """Kiểm tra cập nhật dùng alias 'trang_thai_duyet' theo đúng yêu cầu đề bài"""
    payload = {
        "trang_thai_duyet": "DaDuyet",
        "ghi_chu": "Duyệt thông qua alias trang_thai_duyet"
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai_xet_duyet"] == "DaDuyet"


def test_approve_intern_whitespace_stripping():
    """Kiểm tra hệ thống tự động loại bỏ khoảng trắng thừa đầu cuối"""
    payload = {
        "trang_thai_xet_duyet": "   DaDuyet   ",
        "ghi_chu": "   Hồ sơ rất tốt   "
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai_xet_duyet"] == "DaDuyet"


def test_approve_intern_not_found_404():
    """Kiểm tra báo lỗi 404 khi ma_ho_so không tồn tại trong hệ thống"""
    payload = {
        "trang_thai_xet_duyet": "DaDuyet"
    }
    response = client.patch("/api/v1/interns/99999/approval", json=payload)
    assert response.status_code == 404
    res_data = response.json()
    assert "Không tìm thấy thực tập sinh ID: 99999" in res_data["detail"]


def test_approve_intern_invalid_status_value_422():
    """Kiểm tra báo lỗi 422 khi truyền giá trị trạng thái không nằm trong whitelist"""
    payload = {
        "trang_thai_xet_duyet": "Approved"
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 422
    res_data = response.json()
    detail_str = str(res_data["detail"])
    assert "Trạng thái không hợp lệ" in detail_str


def test_approve_intern_empty_status_string_422():
    """Kiểm tra báo lỗi 422 khi truyền chuỗi rỗng hoặc chỉ có khoảng trắng"""
    payload = {
        "trang_thai_xet_duyet": "   "
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 422
    res_data = response.json()
    assert "không được để trống" in str(res_data["detail"])


def test_approve_intern_missing_both_status_fields_422():
    """Kiểm tra báo lỗi 422 khi không gửi cả trang_thai_duyet và trang_thai_xet_duyet"""
    payload = {
        "ghi_chu": "Chỉ có ghi chú mà không có trạng thái"
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 422
    res_data = response.json()
    assert "Vui lòng cung cấp 'trang_thai_duyet' hoặc 'trang_thai_xet_duyet'" in str(res_data["detail"])


def test_approve_intern_note_exceeds_max_length_422():
    """Kiểm tra báo lỗi 422 khi độ dài ghi chú vượt quá 500 ký tự"""
    payload = {
        "trang_thai_xet_duyet": "DaDuyet",
        "ghi_chu": "A" * 501
    }
    response = client.patch("/api/v1/interns/1/approval", json=payload)
    assert response.status_code == 422


def test_approve_intern_invalid_id_type_422():
    """Kiểm tra báo lỗi 422 khi ID không phải là số nguyên"""
    payload = {
        "trang_thai_xet_duyet": "DaDuyet"
    }
    response = client.patch("/api/v1/interns/abc/approval", json=payload)
    assert response.status_code == 422
