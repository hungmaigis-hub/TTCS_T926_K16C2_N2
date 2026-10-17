
=======
"""
Pytest Fixtures: Thiết lập môi trường kiểm thử độc lập cho FastAPI và Database.
Phụ trách: Nguyễn Văn Hiếu (Backend) - Hỗ trợ Tester (Lê Quang Huy)
"""


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
=======
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.nguoi_dung import NguoiDung
from app.schemas.user import UserRole
from app.main import app

# Sử dụng in-memory SQLite database độc lập cho test

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
=======
    """
    Tạo cấu trúc bảng mới cho mỗi test case và rollback/drop sau khi test xong.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Tạo sẵn các tài khoản mẫu với các vai trò để kiểm thử phân quyền RBAC
    admin_user = NguoiDung(
        ten_dang_nhap="admin_test",
        email="admin_test@ttcs.edu.vn",
        mat_khau_hash=hash_password("Admin@123456"),
        ho_ten="Quản Trị Viên Test",
        vai_tro=UserRole.ADMIN.value,
        trang_thai=True
    )
    hr_user = NguoiDung(
        ten_dang_nhap="hr_test",
        email="hr_test@ttcs.edu.vn",
        mat_khau_hash=hash_password("Hr@123456"),
        ho_ten="Nhân Viên HR Test",
        vai_tro=UserRole.HR.value,
        trang_thai=True
    )
    mentor_user = NguoiDung(
        ten_dang_nhap="mentor_test",
        email="mentor_test@ttcs.edu.vn",
        mat_khau_hash=hash_password("Mentor@123456"),
        ho_ten="Người Hướng Dẫn Test",
        vai_tro=UserRole.MENTOR.value,
        trang_thai=True
    )
    intern_user = NguoiDung(
        ten_dang_nhap="intern_test",
        email="intern_test@ttcs.edu.vn",
        mat_khau_hash=hash_password("Intern@123456"),
        ho_ten="Thực Tập Sinh Test",
        vai_tro=UserRole.THUCTAPSINH.value,
        trang_thai=True
    )

    session.add_all([admin_user, hr_user, mentor_user, intern_user])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):

    """TestClient với override get_db dependency"""
=======
    """
    FastAPI TestClient với dependency get_db được override về database test in-memory.
    """

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
=======
@pytest.fixture
def admin_headers():
    """Header Authorization mang JWT Token của Quản trị viên (Admin)"""
    token = create_access_token(subject="admin_test", role=UserRole.ADMIN.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hr_headers():
    """Header Authorization mang JWT Token của Nhân viên HR (Không phải Admin)"""
    token = create_access_token(subject="hr_test", role=UserRole.HR.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mentor_headers():
    """Header Authorization mang JWT Token của Mentor (Không phải Admin)"""
    token = create_access_token(subject="mentor_test", role=UserRole.MENTOR.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def intern_headers():
    """Header Authorization mang JWT Token của Thực tập sinh (Không phải Admin)"""
    token = create_access_token(subject="intern_test", role=UserRole.THUCTAPSINH.value)
    return {"Authorization": f"Bearer {token}"}

