import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.database import Base
from app.main import app
from app.models.ho_so import HoSo

# CSDL SQLite in-memory độc lập cho test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Tạo mới cấu trúc CSDL và nạp dữ liệu cho từng test case."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed dữ liệu hồ sơ test
    test_students = [
        HoSo(
            ma_ho_so="HS001",
            ho_ten="Nguyễn Văn Hiếu",
            email="hieu.test@example.com",
            so_dien_thoai="0987654321",
            truong_dai_hoc="Đại học Bách Khoa",
            chuyen_nganh="CNTT",
            trang_thai="DangThucTap",  # Hợp lệ
            ngay_tao=datetime.utcnow(),
        ),
        HoSo(
            ma_ho_so="HS_LOCKED",
            ho_ten="Sinh Viên Bị Khóa",
            email="locked@example.com",
            so_dien_thoai="0900000000",
            truong_dai_hoc="Đại học X",
            chuyen_nganh="Kế toán",
            trang_thai="Khoa",  # Bị khóa -> Không hợp lệ
            ngay_tao=datetime.utcnow(),
        ),
    ]
    for s in test_students:
        db.add(s)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Override dependency get_db để dùng database test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
