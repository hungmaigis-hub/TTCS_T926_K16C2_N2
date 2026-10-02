import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Dùng SQLite in-memory cho testing để không ảnh hưởng dữ liệu thật
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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
    # Tạo bảng trước mỗi test và drop sau mỗi test
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_contract_success():
    """
    Test 1: Tạo mới hợp đồng thành công (HTTP 201 Created)
    Lưu ma_so_hop_dong, ngay_ky, muc_phu_cap_co_ban, ma_ho_so
    """
    payload = {
        "ma_so_hop_dong": "HD-2026-TTS-001",
        "ngay_ky": "2026-10-02",
        "muc_phu_cap_co_ban": 3500000.0,
        "ma_ho_so": "HS-2026-001",
        "file_url": "https://storage.company.com/contracts/hd-001.pdf",
        "ghi_chu": "Hợp đồng thử việc 3 tháng"
    }
    response = client.post("/api/v1/contracts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ma_so_hop_dong"] == "HD-2026-TTS-001"
    assert data["ngay_ky"] == "2026-10-02"
    assert float(data["muc_phu_cap_co_ban"]) == 3500000.0
    assert data["ma_ho_so"] == "HS-2026-001"
    assert data["trang_thai"] == "Chờ xác nhận"
    assert "id" in data


def test_create_contract_duplicate_ma_so_hop_dong():
    """
    Test 2: Kiểm tra ngăn chặn trùng lặp ma_so_hop_dong (HTTP 400 Bad Request)
    """
    payload = {
        "ma_so_hop_dong": "HD-2026-DUPLICATE",
        "ngay_ky": "2026-10-02",
        "muc_phu_cap_co_ban": 4000000.0,
        "ma_ho_so": "HS-2026-002"
    }
    # Tạo lần 1 -> Thành công
    res1 = client.post("/api/v1/contracts", json=payload)
    assert res1.status_code == 201

    # Tạo lần 2 với cùng mã số hợp đồng -> Lỗi 400
    res2 = client.post("/api/v1/contracts", json=payload)
    assert res2.status_code == 400
    assert "đã tồn tại" in res2.json()["detail"]


def test_create_contract_negative_allowance():
    """
    Test 3: Kiểm tra mức phụ cấp âm (HTTP 422 Unprocessable Entity do Pydantic validate ge=0)
    """
    payload = {
        "ma_so_hop_dong": "HD-2026-INVALID",
        "ngay_ky": "2026-10-02",
        "muc_phu_cap_co_ban": -500000.0
    }
    response = client.post("/api/v1/contracts", json=payload)
    assert response.status_code == 422


def test_create_contract_missing_required_fields():
    """
    Test 4: Kiểm tra thiếu trường bắt buộc (ma_so_hop_dong, ngay_ky, muc_phu_cap_co_ban)
    """
    payload = {
        "ma_so_hop_dong": "HD-2026-MISSING"
        # thiếu ngay_ky và muc_phu_cap_co_ban
    }
    response = client.post("/api/v1/contracts", json=payload)
    assert response.status_code == 422


def test_get_contracts_list():
    """
    Test 5: Lấy danh sách hợp đồng (GET /api/v1/contracts)
    """
    # Tạo 2 hợp đồng mẫu
    client.post("/api/v1/contracts", json={
        "ma_so_hop_dong": "HD-01",
        "ngay_ky": "2026-10-01",
        "muc_phu_cap_co_ban": 3000000.0,
        "ma_ho_so": "HS-01"
    })
    client.post("/api/v1/contracts", json={
        "ma_so_hop_dong": "HD-02",
        "ngay_ky": "2026-10-02",
        "muc_phu_cap_co_ban": 3500000.0,
        "ma_ho_so": "HS-02"
    })

    response = client.get("/api/v1/contracts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_confirm_contract():
    """
    Test 6: Thực tập sinh xác nhận hợp đồng và không cho xác nhận nhiều lần (STT 10)
    """
    create_res = client.post("/api/v1/contracts", json={
        "ma_so_hop_dong": "HD-CONFIRM-01",
        "ngay_ky": "2026-10-02",
        "muc_phu_cap_co_ban": 5000000.0,
        "ma_ho_so": "HS-01"
    })
    contract_id = create_res.json()["id"]

    # Xác nhận lần 1 -> Thành công
    confirm_res = client.patch(f"/api/v1/contracts/{contract_id}/confirm", json={"xac_nhan": True, "ghi_chu": "Đã đọc kỹ và đồng ý"})
    assert confirm_res.status_code == 200
    assert confirm_res.json()["trang_thai"] == "Đã xác nhận"

    # Xác nhận lần 2 -> Báo lỗi 400 không cho xác nhận nhiều lần
    confirm_res2 = client.patch(f"/api/v1/contracts/{contract_id}/confirm", json={"xac_nhan": True})
    assert confirm_res2.status_code == 400
    assert "đã được xác nhận trước đó" in confirm_res2.json()["detail"]
