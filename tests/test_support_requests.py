from fastapi.testclient import TestClient


def test_create_support_request_success(client: TestClient):
    """
    Test tạo yêu cầu hỗ trợ thành công:
    - Hồ sơ HS001 hợp lệ
    - Tự động gán trang_thai = 'ChoXuLy'
    - Tự động gán ngay_tao
    - Trả về mã HTTP 201 Created
    """
    payload = {
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "Giấy tờ thực tập",
        "tieu_de": "Xin xác nhận hoàn thành thực tập",
        "noi_dung": "Em cần xác nhận số tuần thực tập và đánh giá của mentor để nộp về trường.",
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["ma_ho_so"] == "HS001"
    assert data["loai_yeu_cau"] == "Giấy tờ thực tập"
    assert data["tieu_de"] == "Xin xác nhận hoàn thành thực tập"
    assert data["noi_dung"] == payload["noi_dung"]
    assert data["trang_thai"] == "ChoXuLy"
    assert "ngay_tao" in data
    assert data["ngay_tao"] is not None
    assert "ma_yeu_cau" in data
    assert isinstance(data["ma_yeu_cau"], int)


def test_create_support_request_profile_not_found(client: TestClient):
    """
    Test gửi yêu cầu với mã hồ sơ không tồn tại:
    - Trả về 404 Not Found
    """
    payload = {
        "ma_ho_so": "HS_KHONG_CO_TRONG_DB",
        "loai_yeu_cau": "Hỗ trợ kỹ thuật",
        "tieu_de": "Lỗi tài khoản VPN",
        "noi_dung": "Không thể kết nối vào mạng nội bộ công ty.",
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 404
    error = response.json()
    assert "không tồn tại" in error["detail"]


def test_create_support_request_profile_locked(client: TestClient):
    """
    Test gửi yêu cầu với hồ sơ bị khóa / không hợp lệ:
    - Trả về 400 Bad Request
    """
    payload = {
        "ma_ho_so": "HS_LOCKED",
        "loai_yeu_cau": "Hỗ trợ phụ cấp",
        "tieu_de": "Xin nhận phụ cấp tháng vừa qua",
        "noi_dung": "Em chưa nhận được tiền phụ cấp tháng 9.",
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 400
    error = response.json()
    assert "không hợp lệ" in error["detail"] or "Khoa" in error["detail"]


def test_create_support_request_missing_required_fields(client: TestClient):
    """
    Test gửi payload thiếu các trường bắt buộc:
    - Trả về 422 Unprocessable Entity
    """
    # Thiếu tieu_de và noi_dung
    payload = {
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "Giấy tờ",
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 422


def test_get_support_requests_list_and_filter(client: TestClient):
    """
    Test lấy danh sách và lọc yêu cầu hỗ trợ.
    """
    # Tạo 2 yêu cầu
    req1 = {
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "Giấy tờ",
        "tieu_de": "Yêu cầu số 1",
        "noi_dung": "Nội dung yêu cầu 1 cho sinh viên HS001",
    }
    req2 = {
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "Kỹ thuật",
        "tieu_de": "Yêu cầu số 2",
        "noi_dung": "Nội dung yêu cầu 2 cho sinh viên HS001",
    }
    client.post("/api/v1/support-requests", json=req1)
    client.post("/api/v1/support-requests", json=req2)

    # Lấy danh sách
    response = client.get("/api/v1/support-requests")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 2

    # Lọc theo ma_ho_so
    response_filter = client.get("/api/v1/support-requests?ma_ho_so=HS001")
    assert response_filter.status_code == 200
    assert len(response_filter.json()) >= 2


def test_get_support_request_by_id(client: TestClient):
    """
    Test xem chi tiết yêu cầu hỗ trợ theo ID.
    """
    payload = {
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "Khác",
        "tieu_de": "Yêu cầu hỗ trợ đặc biệt",
        "noi_dung": "Chi tiết yêu cầu cần hỗ trợ từ mentor.",
    }
    created = client.post("/api/v1/support-requests", json=payload).json()
    ma_yeu_cau = created["ma_yeu_cau"]

    # Tra cứu ID hợp lệ
    response = client.get(f"/api/v1/support-requests/{ma_yeu_cau}")
    assert response.status_code == 200
    assert response.json()["ma_yeu_cau"] == ma_yeu_cau

    # Tra cứu ID không tồn tại
    response_404 = client.get("/api/v1/support-requests/99999")
    assert response_404.status_code == 404
