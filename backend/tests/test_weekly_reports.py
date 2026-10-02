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


# ==============================================================================
# BỘ KIỂM THỬ CHO API: GET /api/v1/reports (Lấy danh sách & lọc theo Mentor)
# ==============================================================================

def test_get_weekly_reports_default_success():
    """Kiểm tra lấy danh sách báo cáo tuần mặc định không truyền param -> 200 OK"""
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status_code"] == 200
    assert "data" in res_data
    assert "items" in res_data["data"]
    assert "pagination" in res_data["data"]

    pagination = res_data["data"]["pagination"]
    assert pagination["page"] == 1
    assert pagination["page_size"] == 20
    assert pagination["total_items"] >= 1


def test_get_weekly_reports_filter_by_mentor_success():
    """Kiểm tra lọc danh sách báo cáo theo Mentor phụ trách (ma_mentor=3) -> 200 OK"""
    response = client.get("/api/v1/reports?ma_mentor=3")
    assert response.status_code == 200
    res_data = response.json()

    items = res_data["data"]["items"]
    assert len(items) >= 1
    for item in items:
        assert item["ma_mentor"] == 3
        assert item["ho_ten_mentor"] == "Nguyễn Hướng Dẫn"


def test_get_weekly_reports_filter_by_mentor_not_found():
    """Kiểm tra khi lọc theo mã Mentor không tồn tại trong hệ thống -> 404 Not Found"""
    response = client.get("/api/v1/reports?ma_mentor=99999")
    assert response.status_code == 404
    res_data = response.json()
    assert "detail" in res_data
    assert "99999" in res_data["detail"]


def test_get_weekly_reports_filter_by_ho_so():
    """Kiểm tra lọc báo cáo theo mã hồ sơ (ma_ho_so=1) -> 200 OK"""
    response = client.get("/api/v1/reports?ma_ho_so=1")
    assert response.status_code == 200
    res_data = response.json()

    items = res_data["data"]["items"]
    assert len(items) >= 1
    for item in items:
        assert item["ma_ho_so"] == 1
        assert item["ho_ten_sinh_vien"] == "Nguyễn Văn A"


def test_get_weekly_reports_filter_by_tuan_so():
    """Kiểm tra lọc báo cáo theo tuần số (tuan_so=1) -> 200 OK"""
    response = client.get("/api/v1/reports?tuan_so=1")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    for item in items:
        assert item["tuan_so"] == 1


def test_get_weekly_reports_filter_by_feedback_status():
    """Kiểm tra lọc theo trạng thái đã phản hồi (da_phan_hoi)"""
    # 1. da_phan_hoi=false: báo cáo chưa có nhận xét
    resp_unanswered = client.get("/api/v1/reports?da_phan_hoi=false")
    assert resp_unanswered.status_code == 200
    items_un = resp_unanswered.json()["data"]["items"]
    for it in items_un:
        assert not it.get("phan_hoi_mentor")

    # 2. Cập nhật feedback cho 1 báo cáo rồi lọc da_phan_hoi=true
    client.post("/api/v1/reports/1/feedback", json={"phan_hoi_mentor": "Đã ghi nhận tốt"})
    resp_answered = client.get("/api/v1/reports?da_phan_hoi=true")
    assert resp_answered.status_code == 200
    items_ans = resp_answered.json()["data"]["items"]
    assert len(items_ans) >= 1
    assert any(it["ma_bao_cao"] == 1 for it in items_ans)


def test_get_weekly_reports_search_tu_khoa():
    """Kiểm tra tìm kiếm báo cáo theo từ khóa (tu_khoa)"""
    # Tìm kiếm theo tên sinh viên "Nguyễn Văn A"
    resp = client.get("/api/v1/reports?tu_khoa=Nguyễn+Văn+A")
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert len(items) >= 1
    assert all("Nguyễn Văn A" in it["ho_ten_sinh_vien"] for it in items)

    # Tìm kiếm theo nội dung công việc "Docker"
    resp_docker = client.get("/api/v1/reports?tu_khoa=Docker")
    assert resp_docker.status_code == 200
    assert len(resp_docker.json()["data"]["items"]) >= 1


def test_get_weekly_reports_pagination():
    """Kiểm tra tính năng phân trang (page, page_size)"""
    # Tạo thêm 1 báo cáo để có ít nhất 2 bản ghi
    client.post("/api/v1/reports", json={
        "ma_ho_so": 1,
        "tuan_so": 95,
        "noi_dung_cong_viec": "Báo cáo thử nghiệm phân trang"
    })

    resp = client.get("/api/v1/reports?page=1&page_size=1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) == 1
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 1
    assert data["pagination"]["total_pages"] >= 2


def test_get_weekly_reports_invalid_params():
    """Kiểm tra khi truyền tham số phân trang hoặc tuần số không hợp lệ -> 422"""
    # page <= 0
    assert client.get("/api/v1/reports?page=0").status_code == 422
    # page_size <= 0
    assert client.get("/api/v1/reports?page_size=0").status_code == 422
    # page_size > 100
    assert client.get("/api/v1/reports?page_size=101").status_code == 422
    # tuan_so < 1
    assert client.get("/api/v1/reports?tuan_so=0").status_code == 422


# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/reports/{id}/feedback (Gửi phản hồi)
# ==============================================================================

def test_submit_report_feedback_success_without_mentor_id():
    """Kiểm tra gửi phản hồi thành công không truyền ma_mentor -> 200 OK"""
    payload = {
        "phan_hoi_mentor": "Nội dung công việc rất tốt, tiếp tục phát huy!"
    }
    response = client.post("/api/v1/reports/1/feedback", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status_code"] == 200
    assert res_data["message"] == "Gửi phản hồi báo cáo tuần thành công"
    assert "data" in res_data
    assert res_data["data"]["ma_bao_cao"] == 1
    assert res_data["data"]["phan_hoi_mentor"] == "Nội dung công việc rất tốt, tiếp tục phát huy!"


def test_submit_report_feedback_success_with_valid_mentor():
    """Kiểm tra gửi phản hồi thành công kèm mã Mentor hợp lệ phụ trách sinh viên -> 200 OK"""
    payload = {
        "phan_hoi_mentor": "Mentor đã duyệt và đồng ý với kết quả này.",
        "ma_mentor": 3
    }
    response = client.post("/api/v1/reports/1/feedback", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["data"]["phan_hoi_mentor"] == "Mentor đã duyệt và đồng ý với kết quả này."
    assert res_data["data"]["ma_mentor"] == 3


def test_submit_report_feedback_not_found():
    """Kiểm tra gửi phản hồi cho báo cáo không tồn tại -> 404 Not Found"""
    payload = {
        "phan_hoi_mentor": "Phản hồi cho ID ảo"
    }
    response = client.post("/api/v1/reports/99999/feedback", json=payload)
    assert response.status_code == 404
    assert "99999" in response.json()["detail"]


def test_submit_report_feedback_mentor_not_found():
    """Kiểm tra khi gửi ma_mentor không tồn tại trong hệ thống -> 404 Not Found"""
    payload = {
        "phan_hoi_mentor": "Phản hồi báo cáo",
        "ma_mentor": 99999
    }
    response = client.post("/api/v1/reports/1/feedback", json=payload)
    assert response.status_code == 404
    assert "99999" in response.json()["detail"]


def test_submit_report_feedback_unauthorized_mentor():
    """Kiểm tra khi mentor gửi phản hồi không phụ trách sinh viên của báo cáo -> 403 Forbidden"""
    # User 1 là sinh viên, không phụ trách hồ sơ 1 (ma_mentor của hồ sơ 1 là 3)
    payload = {
        "phan_hoi_mentor": "Cố tình can thiệp báo cáo của người khác",
        "ma_mentor": 1
    }
    response = client.post("/api/v1/reports/1/feedback", json=payload)
    assert response.status_code == 403
    assert "không có quyền" in response.json()["detail"]


def test_submit_report_feedback_empty_content():
    """Kiểm tra khi gửi phản hồi rỗng hoặc chỉ toàn khoảng trắng -> 422"""
    # Chuỗi rỗng
    resp1 = client.post("/api/v1/reports/1/feedback", json={"phan_hoi_mentor": ""})
    assert resp1.status_code == 422

    # Chỉ toàn khoảng trắng
    resp2 = client.post("/api/v1/reports/1/feedback", json={"phan_hoi_mentor": "     "})
    assert resp2.status_code == 422


def test_submit_report_feedback_missing_required_field():
    """Kiểm tra khi thiếu trường phan_hoi_mentor -> 422"""
    response = client.post("/api/v1/reports/1/feedback", json={"ma_mentor": 3})
    assert response.status_code == 422


def test_submit_report_feedback_invalid_path_id():
    """Kiểm tra khi ID trên đường dẫn <= 0 hoặc sai kiểu -> 422"""
    assert client.post("/api/v1/reports/0/feedback", json={"phan_hoi_mentor": "test"}).status_code == 422
    assert client.post("/api/v1/reports/abc/feedback", json={"phan_hoi_mentor": "test"}).status_code == 422
