import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_leave_request_success_future_date():
    """Kiểm tra tạo đơn xin nghỉ hợp lệ cho những ngày trong tương lai (HTTP 201 Created)"""
    today = date.today()
    start_date = today + timedelta(days=3)
    end_date = today + timedelta(days=5)

    payload = {
        "ma_ho_so": 1,
        "tu_ngay": start_date.isoformat(),
        "den_ngay": end_date.isoformat(),
        "ly_do": "Xin nghỉ về quê giải quyết việc gia đình",
        "trang_thai": "Chờ duyệt"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["status_code"] == 201
    assert res_data["message"] == "Tạo đơn xin nghỉ thành công"
    assert "data" in res_data

    item = res_data["data"]
    assert item["ma_ho_so"] == 1
    assert item["tu_ngay"] == start_date.isoformat()
    assert item["den_ngay"] == end_date.isoformat()
    assert item["so_ngay"] == 3
    assert item["ly_do"] == "Xin nghỉ về quê giải quyết việc gia đình"
    assert item["trang_thai"] == "Chờ duyệt"
    assert item["ma_don"] > 0
    assert item["ngay_tao"] is not None


def test_create_leave_request_single_day_today():
    """Kiểm tra tạo đơn xin nghỉ 1 ngày bắt đầu từ chính ngày hiện tại (hợp lệ tu_ngay >= today)"""
    today = date.today()

    payload = {
        "ma_ho_so": 1,
        "tu_ngay": today.isoformat(),
        "den_ngay": today.isoformat(),
        "ly_do": "Khám sức khỏe trong ngày"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 201
    item = response.json()["data"]

    assert item["tu_ngay"] == today.isoformat()
    assert item["den_ngay"] == today.isoformat()
    assert item["so_ngay"] == 1
    assert item["trang_thai"] == "Chờ duyệt"


def test_create_leave_request_default_status():
    """Kiểm tra không truyền trường trang_thai -> hệ thống tự gán mặc định là 'Chờ duyệt'"""
    today = date.today()
    payload = {
        "ma_ho_so": 2,
        "tu_ngay": (today + timedelta(days=1)).isoformat(),
        "den_ngay": (today + timedelta(days=2)).isoformat(),
        "ly_do": "Tham gia thi học phần ở trường đại học"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 201
    item = response.json()["data"]
    assert item["trang_thai"] == "Chờ duyệt"
    assert item["so_ngay"] == 2


def test_create_leave_request_past_date_rejected():
    """Kiểm tra validate: tu_ngay trong quá khứ (< ngày hiện tại) -> báo lỗi 422 Unprocessable Entity"""
    today = date.today()
    past_date = today - timedelta(days=1)

    payload = {
        "ma_ho_so": 1,
        "tu_ngay": past_date.isoformat(),
        "den_ngay": today.isoformat(),
        "ly_do": "Xin nghỉ bổ sung cho ngày hôm qua"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 422
    err_str = str(response.json())
    assert "Ngày bắt đầu nghỉ (tu_ngay) không được nhỏ hơn ngày hiện tại" in err_str


def test_create_leave_request_end_date_before_start_date_rejected():
    """Kiểm tra validate: den_ngay < tu_ngay -> báo lỗi 422 Unprocessable Entity"""
    today = date.today()
    start_date = today + timedelta(days=5)
    end_date = today + timedelta(days=2)

    payload = {
        "ma_ho_so": 1,
        "tu_ngay": start_date.isoformat(),
        "den_ngay": end_date.isoformat(),
        "ly_do": "Đăng ký sai thứ tự ngày bắt đầu và kết thúc"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 422
    err_str = str(response.json())
    assert "Ngày kết thúc nghỉ (den_ngay) phải lớn hơn hoặc bằng ngày bắt đầu nghỉ" in err_str


def test_create_leave_request_intern_not_found():
    """Kiểm tra ma_ho_so không tồn tại trong CSDL -> trả về lỗi HTTP 404 Not Found"""
    today = date.today()
    payload = {
        "ma_ho_so": 9999,
        "tu_ngay": (today + timedelta(days=1)).isoformat(),
        "den_ngay": (today + timedelta(days=1)).isoformat(),
        "ly_do": "Mã hồ sơ không tồn tại"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]


def test_create_leave_request_invalid_negative_intern_id():
    """Kiểm tra ma_ho_so <= 0 -> báo lỗi 422 Unprocessable Entity"""
    today = date.today()
    payload = {
        "ma_ho_so": -1,
        "tu_ngay": (today + timedelta(days=1)).isoformat(),
        "den_ngay": (today + timedelta(days=1)).isoformat(),
        "ly_do": "Mã hồ sơ âm"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 422


def test_create_leave_request_empty_reason():
    """Kiểm tra lý do để trống hoặc chỉ có khoảng trắng -> báo lỗi 422 Unprocessable Entity"""
    today = date.today()
    payload = {
        "ma_ho_so": 1,
        "tu_ngay": (today + timedelta(days=1)).isoformat(),
        "den_ngay": (today + timedelta(days=1)).isoformat(),
        "ly_do": "     "
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 422
    err_str = str(response.json())
    assert "Lý do xin nghỉ không được để trống" in err_str


def test_create_leave_request_frontend_payload_compatibility():
    """Kiểm tra payload gửi từ frontend/js/nghi_phep.js tương thích 100%"""
    today = date.today()
    payload = {
        "ma_ho_so": 1,
        "tu_ngay": (today + timedelta(days=2)).isoformat(),
        "den_ngay": (today + timedelta(days=4)).isoformat(),
        "ly_do": "[Nghỉ ốm / Khám sức khỏe] Khám sức khỏe tổng quát định kỳ tại Bệnh viện",
        "trang_thai": "Chờ duyệt"
    }

    response = client.post("/api/v1/leave-requests", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["ma_ho_so"] == 1
    assert data["so_ngay"] == 3
    assert data["trang_thai"] == "Chờ duyệt"
    assert data["ly_do"] == "[Nghỉ ốm / Khám sức khỏe] Khám sức khỏe tổng quát định kỳ tại Bệnh viện"


def test_create_multiple_leave_requests_different_interns():
    """Kiểm tra tạo liên tiếp các đơn xin nghỉ cho các thực tập sinh khác nhau"""
    today = date.today()

    res1 = client.post("/api/v1/leave-requests", json={
        "ma_ho_so": 1,
        "tu_ngay": (today + timedelta(days=1)).isoformat(),
        "den_ngay": (today + timedelta(days=2)).isoformat(),
        "ly_do": "Đơn số 1 của TTS 1"
    })
    assert res1.status_code == 201
    id1 = res1.json()["data"]["ma_don"]

    res2 = client.post("/api/v1/leave-requests", json={
        "ma_ho_so": 2,
        "tu_ngay": (today + timedelta(days=3)).isoformat(),
        "den_ngay": (today + timedelta(days=4)).isoformat(),
        "ly_do": "Đơn số 2 của TTS 2"
    })
    assert res2.status_code == 201
    id2 = res2.json()["data"]["ma_don"]

    assert id2 > id1
