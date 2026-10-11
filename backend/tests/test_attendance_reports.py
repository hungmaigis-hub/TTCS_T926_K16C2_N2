from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_attendance_reports_success_default():
    """Kiểm tra gọi API báo cáo chấm công với tháng 9 năm 2026 thành công (200 OK)"""
    response = client.get("/api/v1/attendance/reports?thang=9&nam=2026")
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status_code"] == 200
    assert res_data["message"] == "Lấy báo cáo chấm công thành công"
    assert "data" in res_data
    
    summary = res_data["data"]["summary"]
    assert summary["thang"] == 9
    assert summary["nam"] == 2026
    assert summary["tong_so_thuc_tap_sinh"] == 2
    assert summary["tong_so_ngay_di_lam"] == 5
    assert summary["tong_so_lan_di_muon"] == 2
    assert summary["tong_so_ngay_nghi"] == 2
    assert summary["ty_le_di_muon"] == 40.0
    assert summary["trung_binh_ngay_cong"] == 2.5

    items = res_data["data"]["items"]
    assert len(items) == 2

    # TTS 1: 3 ngày đi làm, 1 lần muộn (08:45), 1 ngày nghỉ đã duyệt (09-05, đơn 09-12 còn ChoDuyet)
    item1 = next((i for i in items if i["ma_ho_so"] == 1), None)
    assert item1 is not None
    assert item1["ho_ten"] == "Nguyễn Văn A"
    assert item1["so_ngay_di_lam"] == 3
    assert item1["so_lan_di_muon"] == 1
    assert item1["so_ngay_nghi"] == 1

    # TTS 2: 2 ngày đi làm, 1 lần muộn (08:50), 1 ngày nghỉ đã duyệt (09-08)
    item2 = next((i for i in items if i["ma_ho_so"] == 2), None)
    assert item2 is not None
    assert item2["ho_ten"] == "Trần Thị B"
    assert item2["so_ngay_di_lam"] == 2
    assert item2["so_lan_di_muon"] == 1
    assert item2["so_ngay_nghi"] == 1


def test_filter_by_department_found():
    """Kiểm tra lọc theo ma_phong_ban = 1 tìm thấy đúng dữ liệu phòng ban"""
    response = client.get("/api/v1/attendance/reports?thang=9&nam=2026&ma_phong_ban=1")
    assert response.status_code == 200
    res_data = response.json()
    summary = res_data["data"]["summary"]
    assert summary["ma_phong_ban"] == 1
    assert summary["ten_phong_ban"] == "Trung tâm Phần mềm"
    assert summary["tong_so_thuc_tap_sinh"] == 2


def test_filter_by_department_not_found():
    """Kiểm tra truyền ma_phong_ban không tồn tại -> trả về lỗi 404"""
    response = client.get("/api/v1/attendance/reports?thang=9&nam=2026&ma_phong_ban=999")
    assert response.status_code == 404
    res_data = response.json()
    assert res_data["detail"] == "Phòng ban không tồn tại"


def test_filter_by_month_with_no_attendance_data():
    """Kiểm tra tháng không có dữ liệu chấm công -> số liệu bằng 0"""
    response = client.get("/api/v1/attendance/reports?thang=1&nam=2026")
    assert response.status_code == 200
    res_data = response.json()
    summary = res_data["data"]["summary"]
    assert summary["thang"] == 1
    assert summary["nam"] == 2026
    assert summary["tong_so_ngay_di_lam"] == 0
    assert summary["tong_so_lan_di_muon"] == 0
    assert summary["tong_so_ngay_nghi"] == 0
    assert summary["ty_le_di_muon"] == 0.0

    items = res_data["data"]["items"]
    for it in items:
        assert it["so_ngay_di_lam"] == 0
        assert it["so_lan_di_muon"] == 0
        assert it["so_ngay_nghi"] == 0


def test_custom_standard_time_all_late():
    """Kiểm tra tùy chỉnh giờ chuẩn gio_chuan = '08:00:00' khiến tất cả lượt đi làm đều thành đi muộn"""
    response = client.get("/api/v1/attendance/reports?thang=9&nam=2026&gio_chuan=08:00:00")
    assert response.status_code == 200
    res_data = response.json()
    summary = res_data["data"]["summary"]
    # Tất cả 5 lượt check-in đều sau 08:00:00 -> 5 lần đi muộn (100%)
    assert summary["tong_so_ngay_di_lam"] == 5
    assert summary["tong_so_lan_di_muon"] == 5
    assert summary["ty_le_di_muon"] == 100.0


def test_custom_standard_time_none_late():
    """Kiểm tra tùy chỉnh giờ chuẩn gio_chuan = '09:00:00' khiến không ai bị tính đi muộn"""
    response = client.get("/api/v1/attendance/reports?thang=9&nam=2026&gio_chuan=09:00:00")
    assert response.status_code == 200
    res_data = response.json()
    summary = res_data["data"]["summary"]
    assert summary["tong_so_ngay_di_lam"] == 5
    assert summary["tong_so_lan_di_muon"] == 0
    assert summary["ty_le_di_muon"] == 0.0


def test_leave_request_status_filtering():
    """Kiểm tra chỉ các đơn nghỉ phép trạng thái DaDuyet mới được tính, bỏ qua ChoDuyet"""
    response = client.get("/api/v1/attendance/reports?thang=9&nam=2026")
    assert response.status_code == 200
    res_data = response.json()
    items = res_data["data"]["items"]
    # TTS 1 có 2 đơn trong tháng 9 (1 DaDuyet ngày 09-05, 1 ChoDuyet ngày 09-12)
    item1 = next((i for i in items if i["ma_ho_so"] == 1), None)
    assert item1["so_ngay_nghi"] == 1


def test_attendance_reports_pagination():
    """Kiểm tra phân trang: page_size = 1"""
    # Trang 1
    resp1 = client.get("/api/v1/attendance/reports?thang=9&nam=2026&page=1&page_size=1")
    assert resp1.status_code == 200
    data1 = resp1.json()["data"]
    assert data1["pagination"]["page"] == 1
    assert data1["pagination"]["page_size"] == 1
    assert data1["pagination"]["total_items"] == 2
    assert data1["pagination"]["total_pages"] == 2
    assert len(data1["items"]) == 1
    assert data1["items"][0]["ma_ho_so"] == 1

    # Trang 2
    resp2 = client.get("/api/v1/attendance/reports?thang=9&nam=2026&page=2&page_size=1")
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    assert data2["pagination"]["page"] == 2
    assert len(data2["items"]) == 1
    assert data2["items"][0]["ma_ho_so"] == 2


def test_invalid_month_validation():
    """Kiểm tra tháng ngoài khoảng 1-12 trả về lỗi 422 Unprocessable Entity"""
    resp_under = client.get("/api/v1/attendance/reports?thang=0")
    assert resp_under.status_code == 422

    resp_over = client.get("/api/v1/attendance/reports?thang=13")
    assert resp_over.status_code == 422


def test_invalid_year_validation():
    """Kiểm tra năm trước 2000 trả về lỗi 422 Unprocessable Entity"""
    resp_year = client.get("/api/v1/attendance/reports?nam=1998")
    assert resp_year.status_code == 422


def test_invalid_pagination_validation():
    """Kiểm tra page < 1 hoặc page_size < 1 trả về lỗi 422 Unprocessable Entity"""
    resp_page = client.get("/api/v1/attendance/reports?page=0")
    assert resp_page.status_code == 422

    resp_size = client.get("/api/v1/attendance/reports?page_size=0")
    assert resp_size.status_code == 422
