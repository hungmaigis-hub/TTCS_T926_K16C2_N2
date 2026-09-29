import pytest
import sys
from datetime import datetime, timezone
from pathlib import Path

# Đảm bảo import được module main từ thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import BaoCaoTuan

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/reports (Nộp báo cáo định kỳ tuần)
# ==============================================================================

@pytest.fixture(autouse=True)
def cleanup_created_reports():
    """Dọn dẹp các báo cáo được tạo trong quá trình test để đảm bảo tính độc lập"""
    yield
    try:
        from tests.conftest import MYSQL_AVAILABLE, TestSessionLocal
        Session = SessionLocal if MYSQL_AVAILABLE else TestSessionLocal
    except Exception:
        Session = SessionLocal
    db = Session()
    try:
        # Xóa các báo cáo tuần có số tuần >= 90 (dùng cho test case)
        db.query(BaoCaoTuan).filter(BaoCaoTuan.tuan_so >= 90).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def test_create_report_full_success():
    """Kiểm tra nộp báo cáo tuần thành công với đầy đủ các trường thông tin -> 201 Created"""
    payload = {
        "ma_ho_so": 1,
        "ma_nhiem_vu": 1,
        "tuan_so": 91,
        "noi_dung_cong_viec": "Nghiên cứu kiến trúc Microservices & triển khai Docker",
        "ket_qua_dat_duoc": "Đã chạy thành công docker-compose với backend và mysql"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["status_code"] == 201
    assert res_data["message"] == "Nộp báo cáo tuần thành công"
    assert "data" in res_data

    data = res_data["data"]
    assert data["ma_ho_so"] == 1
    assert data["ma_nhiem_vu"] == 1
    assert data["tuan_so"] == 91
    assert data["noi_dung_cong_viec"] == "Nghiên cứu kiến trúc Microservices & triển khai Docker"
    assert data["ket_qua_dat_duoc"] == "Đã chạy thành công docker-compose với backend và mysql"
    assert "thoi_gian_nop" in data
    assert data["thoi_gian_nop"] is not None


def test_create_report_minimal_success():
    """Kiểm tra nộp báo cáo tuần chỉ với các trường bắt buộc (không có nhiệm vụ, không có kết quả) -> 201 Created"""
    payload = {
        "ma_ho_so": 1,
        "tuan_so": 92,
        "noi_dung_cong_viec": "Tuần làm quen với môi trường công ty và văn hóa doanh nghiệp"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    res_data = response.json()

    data = res_data["data"]
    assert data["ma_ho_so"] == 1
    assert data["ma_nhiem_vu"] is None
    assert data["tuan_so"] == 92
    assert data["ket_qua_dat_duoc"] is None
    assert data["thoi_gian_nop"] is not None


def test_create_report_auto_assign_current_timestamp():
    """Kiểm tra thoi_gian_nop được tự động gán chính xác bằng thời điểm hiện tại"""
    time_before = datetime.now()
    payload = {
        "ma_ho_so": 1,
        "tuan_so": 93,
        "noi_dung_cong_viec": "Kiểm tra tự động gán thời gian nộp"
    }
    response = client.post("/api/v1/reports", json=payload)
    time_after = datetime.now()

    assert response.status_code == 201
    data = response.json()["data"]
    thoi_gian_nop_str = data["thoi_gian_nop"]
    thoi_gian_nop = datetime.fromisoformat(thoi_gian_nop_str)

    # Đảm bảo thoi_gian_nop nằm giữa time_before và time_after (dung sai 2 giây)
    assert time_before.timestamp() - 2 <= thoi_gian_nop.timestamp() <= time_after.timestamp() + 2


def test_create_report_strip_whitespace():
    """Kiểm tra tự động cắt khoảng trắng thừa ở nội dung và kết quả"""
    payload = {
        "ma_ho_so": 1,
        "tuan_so": 94,
        "noi_dung_cong_viec": "   Nội dung có khoảng trắng thừa đầu cuối   ",
        "ket_qua_dat_duoc": "   Kết quả có khoảng trắng thừa   "
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["noi_dung_cong_viec"] == "Nội dung có khoảng trắng thừa đầu cuối"
    assert data["ket_qua_dat_duoc"] == "Kết quả có khoảng trắng thừa"


def test_create_report_ho_so_not_found():
    """Kiểm tra khi mã hồ sơ không tồn tại -> Trả về 404 Not Found"""
    payload = {
        "ma_ho_so": 99999,
        "tuan_so": 1,
        "noi_dung_cong_viec": "Báo cáo cho hồ sơ không tồn tại"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "99999" in response.json()["detail"]


def test_create_report_nhiem_vu_not_found():
    """Kiểm tra khi mã nhiệm vụ không tồn tại trong hệ thống -> Trả về 400 Bad Request"""
    payload = {
        "ma_ho_so": 1,
        "ma_nhiem_vu": 99999,
        "tuan_so": 1,
        "noi_dung_cong_viec": "Báo cáo với nhiệm vụ không tồn tại"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 400
    assert "Mã nhiệm vụ không tồn tại" in response.json()["detail"]


def test_create_report_nhiem_vu_mismatch_ho_so():
    """Kiểm tra khi mã nhiệm vụ thuộc về thực tập sinh khác -> Trả về 400 Bad Request"""
    # ma_nhiem_vu 3 thuộc về hồ sơ 2 trong CSDL
    payload = {
        "ma_ho_so": 1,
        "ma_nhiem_vu": 3,
        "tuan_so": 1,
        "noi_dung_cong_viec": "Nộp nhiệm vụ của người khác"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 400
    assert "không thuộc về hồ sơ" in response.json()["detail"]


def test_create_report_invalid_tuan_so_zero():
    """Kiểm tra khi tuần số = 0 -> Trả về 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "tuan_so": 0,
        "noi_dung_cong_viec": "Tuần số không hợp lệ"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422


def test_create_report_invalid_tuan_so_negative():
    """Kiểm tra khi tuần số là số âm -> Trả về 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": 1,
        "tuan_so": -5,
        "noi_dung_cong_viec": "Tuần số âm"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422


def test_create_report_empty_noi_dung():
    """Kiểm tra khi nội dung công việc là chuỗi rỗng -> Trả về 422"""
    payload = {
        "ma_ho_so": 1,
        "tuan_so": 1,
        "noi_dung_cong_viec": ""
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422


def test_create_report_only_whitespace_noi_dung():
    """Kiểm tra khi nội dung chỉ chứa khoảng trắng -> Trả về 422"""
    payload = {
        "ma_ho_so": 1,
        "tuan_so": 1,
        "noi_dung_cong_viec": "     "
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422


def test_create_report_missing_required_fields():
    """Kiểm tra khi thiếu các trường bắt buộc -> Trả về 422"""
    # Thiếu tuan_so và noi_dung_cong_viec
    payload = {
        "ma_ho_so": 1
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422


def test_create_report_invalid_data_types():
    """Kiểm tra khi truyền sai kiểu dữ liệu (chuỗi thay vì số nguyên) -> Trả về 422"""
    payload = {
        "ma_ho_so": "abc",
        "tuan_so": "mot",
        "noi_dung_cong_viec": "Sai kiểu dữ liệu"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422
