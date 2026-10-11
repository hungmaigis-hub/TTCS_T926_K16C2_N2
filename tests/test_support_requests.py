import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.yeu_cau_ho_tro import YeuCauHoTro

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_support_request_success():
    payload = {
        "ma_ho_so": 101,
        "loai_yeu_cau": "GiayTo",
        "tieu_de": "Xin cấp giấy xác nhận thực tập",
        "noi_dung": "Em cần xin giấy xác nhận hoàn thành thực tập để nộp về trường."
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ma_ho_so"] == 101
    assert data["loai_yeu_cau"] == "GiayTo"
    assert data["tieu_de"] == "Xin cấp giấy xác nhận thực tập"
    assert data["trang_thai"] == "ChoXuLy"  # Gán tự động
    assert "ma_yeu_cau" in data
    assert "ngay_tao" in data


def test_get_support_requests_list():
    client.post("/api/v1/support-requests", json={
        "ma_ho_so": 102,
        "loai_yeu_cau": "ChungNhan",
        "tieu_de": "Cấp chứng nhận",
        "noi_dung": "Xin chứng nhận thực tập sinh xuất sắc."
    })
    response = client.get("/api/v1/support-requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["trang_thai"] == "ChoXuLy"


def test_update_support_request_status_by_hr():
    res = client.post("/api/v1/support-requests", json={
        "ma_ho_so": 103,
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
