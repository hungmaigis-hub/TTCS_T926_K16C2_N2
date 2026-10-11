import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
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
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_completion_rate_empty_db():
    """Kiểm tra khi hệ thống chưa có sinh viên nào (0 sinh viên)"""
    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    data = response.json()
    assert data["tong_so_sinh_vien"] == 0
    assert data["so_luong_dang_thuc_tap"] == 0
    assert data["so_luong_hoan_thanh"] == 0
    assert data["so_luong_thoi_hoc"] == 0
    assert data["ty_le_hoan_thanh"] == 0.0

def test_completion_rate_with_various_statuses():
    """Kiểm tra đếm đúng theo trạng thái và tính tỷ lệ hoàn thành chính xác"""
    db = TestingSessionLocal()
    # Tạo 4 sinh viên mẫu: 2 Hoàn thành, 1 Đang thực tập, 1 Thôi học
    s1 = HoSoThucTap(ma_sv="SV01", ho_ten="Nguyễn Văn A", email="a@test.com", trang_thai="HoanThanh")
    s2 = HoSoThucTap(ma_sv="SV02", ho_ten="Trần Thị B", email="b@test.com", trang_thai="HoanThanh")
    s3 = HoSoThucTap(ma_sv="SV03", ho_ten="Lê Văn C", email="c@test.com", trang_thai="DangThucTap")
    s4 = HoSoThucTap(ma_sv="SV04", ho_ten="Phạm Văn D", email="d@test.com", trang_thai="ThoiHoc")
    db.add_all([s1, s2, s3, s4])
    db.commit()
    db.close()

    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    data = response.json()
    assert data["tong_so_sinh_vien"] == 4
    assert data["so_luong_dang_thuc_tap"] == 1
    assert data["so_luong_hoan_thanh"] == 2
    assert data["so_luong_thoi_hoc"] == 1
    # 2 / 4 * 100 = 50.0%
    assert data["ty_le_hoan_thanh"] == 50.0
    assert data["chi_tiet_theo_trang_thai"]["HoanThanh"] == 2
    assert data["chi_tiet_theo_trang_thai"]["DangThucTap"] == 1
    assert data["chi_tiet_theo_trang_thai"]["ThoiHoc"] == 1

def test_completion_rate_rounding():
    """Kiểm tra làm tròn 2 chữ số thập phân (1/3 = 33.33%)"""
    db = TestingSessionLocal()
    s1 = HoSoThucTap(ma_sv="SV01", ho_ten="Nguyễn Văn A", email="a@test.com", trang_thai="HoanThanh")
    s2 = HoSoThucTap(ma_sv="SV02", ho_ten="Trần Thị B", email="b@test.com", trang_thai="DangThucTap")
    s3 = HoSoThucTap(ma_sv="SV03", ho_ten="Lê Văn C", email="c@test.com", trang_thai="DangThucTap")
    db.add_all([s1, s2, s3])
    db.commit()
    db.close()

    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    data = response.json()
    assert data["tong_so_sinh_vien"] == 3
    assert data["so_luong_hoan_thanh"] == 1
    assert data["so_luong_dang_thuc_tap"] == 2
    assert data["ty_le_hoan_thanh"] == 33.33

def test_completion_rate_all_completed():
    """Kiểm tra tỷ lệ 100% khi tất cả đều hoàn thành"""
    db = TestingSessionLocal()
    s1 = HoSoThucTap(ma_sv="SV01", ho_ten="Nguyễn Văn A", email="a@test.com", trang_thai="HoanThanh")
    s2 = HoSoThucTap(ma_sv="SV02", ho_ten="Trần Thị B", email="b@test.com", trang_thai="HoanThanh")
    db.add_all([s1, s2])
    db.commit()
    db.close()

    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    data = response.json()
    assert data["tong_so_sinh_vien"] == 2
    assert data["so_luong_hoan_thanh"] == 2
    assert data["ty_le_hoan_thanh"] == 100.0
