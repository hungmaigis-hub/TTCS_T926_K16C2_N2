import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
import app.core.database
import app.middleware.audit_log
from app.core.security import get_password_hash, create_access_token
from app.models.nguoi_dung import NguoiDung
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong
from app.main import app

# Sử dụng SQLite in-memory chia sẻ qua StaticPool cho test suite
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Trỏ SessionLocal của hệ thống sang TestingSessionLocal
app.core.database.SessionLocal = TestingSessionLocal
app.middleware.audit_log.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Cung cấp database session sạch cho mỗi test case"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Tạo người dùng Admin mẫu trong test database"""
    user = db_session.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "test_admin").first()
    if not user:
        user = NguoiDung(
            ten_dang_nhap="test_admin",
            email="admin.test@hethong.vn",
            mat_khau_hash=get_password_hash("AdminPass123"),
            ho_ten="Admin Tester",
            vai_tro="Admin",
            trang_thai=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session):
    """Tạo người dùng Thực tập sinh mẫu (không có quyền Admin)"""
    user = db_session.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "test_intern").first()
    if not user:
        user = NguoiDung(
            ten_dang_nhap="test_intern",
            email="intern.test@hethong.vn",
            mat_khau_hash=get_password_hash("InternPass123"),
            ho_ten="Intern Tester",
            vai_tro="ThucTapSinh",
            trang_thai=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """JWT Token hợp lệ cho Admin"""
    return create_access_token(
        data={"sub": admin_user.ten_dang_nhap, "user_id": admin_user.ma_nguoi_dung, "vai_tro": "Admin"}
    )


@pytest.fixture
def normal_token(normal_user):
    """JWT Token hợp lệ cho Normal User"""
    return create_access_token(
        data={"sub": normal_user.ten_dang_nhap, "user_id": normal_user.ma_nguoi_dung, "vai_tro": "ThucTapSinh"}
    )


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def normal_headers(normal_token):
    return {"Authorization": f"Bearer {normal_token}"}
