import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.models.yeu_cau_ho_tro import YeuCauHoTro

# Database SQLite riêng cho unit test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_support.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    # Seed hồ sơ mẫu để phục vụ test yêu cầu hỗ trợ
    db = TestingSessionLocal()
    try:
        hs = HoSoThucTap(
            ma_ho_so="HS001",
            ma_sinh_vien="SV001",
            ho_ten="Nguyễn Văn A",
            email="vana@test.com",
            trang_thai="DangThucTap"
        )
        db.add(hs)
        db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)


def test_create_support_request_success():
    """Tạo mới yêu cầu hỗ trợ thành công (US 27)"""
    payload = {
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "GiayTo",
        "tieu_de": "Xin cấp giấy xác nhận thực tập",
        "noi_dung": "Em cần xin giấy xác nhận hoàn thành thực tập để nộp về trường."
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ma_ho_so"] == "HS001"
    assert data["loai_yeu_cau"] == "GiayTo"
    assert data["tieu_de"] == "Xin cấp giấy xác nhận thực tập"
    assert data["trang_thai"] == "ChoXuLy"
    assert "ma_yeu_cau" in data
    assert "ngay_tao" in data


def test_create_support_request_intern_not_found():
    """Tạo yêu cầu hỗ trợ thất bại khi mã hồ sơ không tồn tại (404)"""
    payload = {
        "ma_ho_so": "HS999",
        "loai_yeu_cau": "KyThuat",
        "tieu_de": "Lỗi tài khoản",
        "noi_dung": "Không thể đăng nhập vào Git nội bộ."
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 404
    assert "không tồn tại" in response.json()["detail"]


def test_get_support_requests_list():
    """Lấy danh sách yêu cầu hỗ trợ"""
    client.post("/api/v1/support-requests", json={
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "ChungNhan",
        "tieu_de": "Cấp chứng nhận",
        "noi_dung": "Xin chứng nhận thực tập sinh xuất sắc."
    })
    response = client.get("/api/v1/support-requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["trang_thai"] == "ChoXuLy"


def test_get_support_request_by_id():
    """Xem chi tiết một yêu cầu hỗ trợ"""
    create_res = client.post("/api/v1/support-requests", json={
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "PhuCap",
        "tieu_de": "Hỏi về phụ cấp tháng 9",
        "noi_dung": "Em chưa nhận được thông tin chuyển khoản phụ cấp."
    })
    ma_yeu_cau = create_res.json()["ma_yeu_cau"]

    response = client.get(f"/api/v1/support-requests/{ma_yeu_cau}")
    assert response.status_code == 200
    data = response.json()
    assert data["ma_yeu_cau"] == ma_yeu_cau
    assert data["loai_yeu_cau"] == "PhuCap"


def test_update_support_request_status_by_hr():
    """Cập nhật trạng thái và phản hồi yêu cầu hỗ trợ bởi HR (US 28)"""
    res = client.post("/api/v1/support-requests", json={
        "ma_ho_so": "HS001",
        "loai_yeu_cau": "KyThuat",
        "tieu_de": "Lỗi phần mềm",
        "noi_dung": "Không truy cập được server nội bộ."
    })
    ma_yeu_cau = res.json()["ma_yeu_cau"]

    patch_res = client.patch(
        f"/api/v1/support-requests/{ma_yeu_cau}/status",
        json={
            "trang_thai": "DaXuLy",
            "phan_hoi": "IT đã mở quyền truy cập cho bạn rồi nhé."
        }
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["trang_thai"] == "DaXuLy"
    assert patch_res.json()["phan_hoi"] == "IT đã mở quyền truy cập cho bạn rồi nhé."
