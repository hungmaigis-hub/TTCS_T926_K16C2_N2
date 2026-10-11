import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.mentor import Mentor
from app.models.ho_so_thuc_tap import HoSoThucTap

# Database in-memory riêng cho unit test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Tạo Mentor mẫu
    m1 = Mentor(
        id=1,
        ma_can_bo="MEN01",
        ho_ten="Nguyễn Minh Tuấn",
        email="tuan.nguyen@test.com",
        phong_ban="Phòng Kỹ thuật",
        chuc_vu="Tech Lead",
        so_luong_toi_da=2,
        trang_thai="HoatDong"
    )
    m2 = Mentor(
        id=2,
        ma_can_bo="MEN02",
        ho_ten="Vũ Hải Đăng",
        email="dang.vu@test.com",
        phong_ban="Phòng QA",
        chuc_vu="QA Lead",
        so_luong_toi_da=2,
        trang_thai="TamNghi"
    )
    db.add_all([m1, m2])

    # Tạo Intern mẫu
    i1 = HoSoThucTap(
        id=1,
        ma_sv="DTC245180138",
        ho_ten="Nguyễn Văn Hiếu",
        email="hieu.nv@test.com",
        ma_mentor=None,
        trang_thai="DangThucTap"
    )
    i2 = HoSoThucTap(
        id=2,
        ma_sv="DTC245180139",
        ho_ten="Phùng Văn Thắng",
        email="thang.pv@test.com",
        ma_mentor=1,
        trang_thai="DangThucTap"
    )
    db.add_all([i1, i2])
    db.commit()

    yield

    Base.metadata.drop_all(bind=engine)

def test_assign_mentor_success():
    """Kiểm tra gán mentor thành công"""
    response = client.patch(
        "/api/v1/interns/1/assign-mentor",
        json={"ma_mentor": 1, "ghi_chu": "Phân công hướng dẫn Backend"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["ma_mentor"] == 1
    assert data["data"]["mentor"]["ho_ten"] == "Nguyễn Minh Tuấn"
    assert data["data"]["ghi_chu_phan_cong"] == "Phân công hướng dẫn Backend"
    assert data["data"]["ngay_gan_mentor"] is not None

def test_assign_mentor_not_found_intern():
    """Kiểm tra báo lỗi 404 khi không tìm thấy thực tập sinh"""
    response = client.patch(
        "/api/v1/interns/999/assign-mentor",
        json={"ma_mentor": 1}
    )
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]

def test_assign_mentor_not_found_mentor():
    """Kiểm tra báo lỗi 404 khi mentor không tồn tại"""
    response = client.patch(
        "/api/v1/interns/1/assign-mentor",
        json={"ma_mentor": 999}
    )
    assert response.status_code == 404
    assert "Không tìm thấy mentor" in response.json()["detail"]

def test_assign_mentor_inactive_mentor():
    """Kiểm tra báo lỗi 400 khi mentor đang tạm nghỉ / không hoạt động"""
    response = client.patch(
        "/api/v1/interns/1/assign-mentor",
        json={"ma_mentor": 2}
    )
    assert response.status_code == 400
    assert "không khả dụng" in response.json()["detail"]

def test_unassign_mentor():
    """Kiểm tra hủy phân công mentor khi truyền ma_mentor: null"""
    response = client.patch(
        "/api/v1/interns/2/assign-mentor",
        json={"ma_mentor": None, "ghi_chu": "Hủy gán để chuyển phòng ban"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["ma_mentor"] is None
    assert data["data"]["mentor"] is None
