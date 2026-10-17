import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.nguoi_dung import NguoiDung
from app.models.thong_bao import ThongBao

# Sử dụng SQLite In-Memory Database riêng biệt cho test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Tạo mới toàn bộ bảng trước mỗi test case và xóa sau khi hoàn thành"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient với override get_db dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def user1(db_session):
    """Tạo người dùng 1 (Thực tập sinh A)"""
    user = NguoiDung(
        email="thuctapsinh.a@example.com",
        mat_khau_hash=get_password_hash("password123"),
        ho_ten="Nguyễn Văn A",
        vai_tro="ThucTapSinh",
        kich_hoat=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def user2(db_session):
    """Tạo người dùng 2 (Thực tập sinh B)"""
    user = NguoiDung(
        email="thuctapsinh.b@example.com",
        mat_khau_hash=get_password_hash("password123"),
        ho_ten="Trần Thị B",
        vai_tro="ThucTapSinh",
        kich_hoat=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def token_user1(user1):
    """Tạo JWT token cho User 1"""
    return create_access_token(user1.ma_nguoi_dung)


@pytest.fixture(scope="function")
def token_user2(user2):
    """Tạo JWT token cho User 2"""
    return create_access_token(user2.ma_nguoi_dung)
