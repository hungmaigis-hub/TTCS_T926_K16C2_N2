"""
Test suite cho endpoint PATCH /api/v1/interns/{id}/mentor

Sử dụng pytest + SQLite in-memory để test độc lập (không cần MySQL thật).

Chạy test:
    pytest tests/ -v
    pytest tests/ -v --tb=short          # output ngắn hơn
    pytest tests/test_assign_mentor.py   # chỉ file này
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.nguoi_dung import NguoiDung
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.services.intern_service import MAX_INTERNS_PER_MENTOR

# ============================================================
# Setup: SQLite in-memory database
# ============================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_intern.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Client
client = TestClient(app)


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture(autouse=True)
def setup_database():
    """Tạo bảng và seed data trước mỗi test, xóa sau khi test xong."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()
    try:
        # Seed nguoi_dung
        users = [
            NguoiDung(
                ma_nguoi_dung="HR01",
                ho_ten="Nguyễn Thị Hoa",
                email="hoa@company.com",
                mat_khau_hash="hash_hr01",
                so_dien_thoai="0900000001",
                vai_tro="HR",
                kich_hoat=True,
            ),
            NguoiDung(
                ma_nguoi_dung="MENTOR01",
                ho_ten="Lê Văn Phúc",
                email="phuc@company.com",
                mat_khau_hash="hash_m01",
                so_dien_thoai="0901111001",
                vai_tro="Mentor",
                kich_hoat=True,
            ),
            NguoiDung(
                ma_nguoi_dung="MENTOR02",
                ho_ten="Nguyễn Thị Lan",
                email="lan@company.com",
                mat_khau_hash="hash_m02",
                so_dien_thoai="0901111002",
                vai_tro="Mentor",
                kich_hoat=True,
            ),
            NguoiDung(
                ma_nguoi_dung="MENTOR_INACTIVE",
                ho_ten="Vũ Thanh Tùng",
                email="tung@company.com",
                mat_khau_hash="hash_inactive",
                so_dien_thoai="0901111003",
                vai_tro="Mentor",
                kich_hoat=False,   # ← bị vô hiệu hóa
            ),
            NguoiDung(
                ma_nguoi_dung="TTS001",
                ho_ten="Trần Văn An",
                email="an@uni.edu.vn",
                mat_khau_hash="hash_tts001",
                so_dien_thoai="0902222001",
                vai_tro="ThucTapSinh",
                kich_hoat=True,
            ),
        ]
        db.add_all(users)
        db.flush()

        # Seed ho_so_thuc_tap
        ho_sos = [
            HoSoThucTap(
                ma_ho_so="HS001",
                ma_sinh_vien="TTS001",
                ho_ten="Trần Văn An",
                email="an@uni.edu.vn",
                vi_tri_thuc_tap="Backend Developer",
                trang_thai="DaDuyet",
                ma_mentor=None,
            ),
            HoSoThucTap(
                ma_ho_so="HS002",
                ma_sinh_vien="TTS001",
                ho_ten="Trần Văn An",
                email="an@uni.edu.vn",
                vi_tri_thuc_tap="Frontend Developer",
                trang_thai="DangThucTap",
                ma_mentor="MENTOR01",
            ),
        ]
        db.add_all(ho_sos)
        db.commit()
    finally:
        db.close()

    yield  # Chạy test

    # Teardown
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)


# ============================================================
# Test cases
# ============================================================

class TestAssignMentorSuccess:
    """Các test case thành công (200)."""

    def test_assign_mentor_to_intern_without_mentor(self):
        """Gán mentor mới cho hồ sơ chưa có mentor → 200."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mentor"]["ma_mentor"] == "MENTOR01"
        assert data["data"]["ho_so"]["ma_ho_so"] == "HS001"

    def test_change_mentor_for_intern_with_existing_mentor(self):
        """Thay đổi mentor của hồ sơ đã có mentor → 200."""
        response = client.patch(
            "/api/v1/interns/HS002/mentor",
            json={"ma_mentor": "MENTOR02"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mentor"]["ma_mentor"] == "MENTOR02"

    def test_unassign_mentor_by_passing_null(self):
        """Hủy gán mentor bằng cách truyền null → 200."""
        response = client.patch(
            "/api/v1/interns/HS002/mentor",
            json={"ma_mentor": None},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mentor"] is None

    def test_assign_same_mentor_again(self):
        """Gán lại cùng mentor → vẫn 200 (idempotent)."""
        response = client.patch(
            "/api/v1/interns/HS002/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 200

    def test_response_contains_ngay_cap_nhat(self):
        """Response phải có trường ngay_cap_nhat."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 200
        assert "ngay_cap_nhat" in response.json()["data"]


class TestAssignMentorNotFound:
    """Các test case 404 Not Found."""

    def test_intern_not_found(self):
        """Hồ sơ thực tập không tồn tại → 404."""
        response = client.patch(
            "/api/v1/interns/HS999/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "INTERN_NOT_FOUND"
        assert "HS999" in detail["message"]

    def test_mentor_not_found_in_system(self):
        """Mentor không tồn tại trong bảng nguoi_dung → 404."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR_NOT_EXIST"},
        )
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "MENTOR_NOT_FOUND"
        assert detail["field"] == "ma_mentor"


class TestAssignMentorInvalidRole:
    """Test case 422 – sai vai trò."""

    def test_assign_hr_user_as_mentor(self):
        """Gán người dùng có vai trò HR thay vì Mentor → 422."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "HR01"},
        )
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert detail["error_code"] == "INVALID_MENTOR_ROLE"
        assert "HR01" in detail["message"]
        assert detail["field"] == "ma_mentor"

    def test_assign_intern_as_mentor(self):
        """Gán thực tập sinh làm mentor → 422."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "TTS001"},
        )
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert detail["error_code"] == "INVALID_MENTOR_ROLE"


class TestAssignMentorInactive:
    """Test case 403 – mentor bị vô hiệu hóa."""

    def test_assign_inactive_mentor(self):
        """Gán mentor bị vô hiệu hóa → 403."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR_INACTIVE"},
        )
        assert response.status_code == 403
        detail = response.json()["detail"]
        assert detail["error_code"] == "MENTOR_INACTIVE"
        assert detail["field"] == "ma_mentor"


class TestAssignMentorInputValidation:
    """Test case validation input."""

    def test_empty_body_returns_error(self):
        """Body rỗng → 422 từ Pydantic."""
        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={},
        )
        assert response.status_code == 422

    def test_whitespace_ma_mentor_treated_as_null(self):
        """ma_mentor chứa toàn khoảng trắng → coi như null (hủy gán)."""
        response = client.patch(
            "/api/v1/interns/HS002/mentor",
            json={"ma_mentor": "   "},
        )
        # Sau khi strip → None → hủy gán → 200
        assert response.status_code == 200
        assert response.json()["data"]["mentor"] is None


class TestAssignMentorQuota:
    """Test case kiểm tra giới hạn chỉ tiêu (Quota: tối đa MAX_INTERNS_PER_MENTOR sinh viên)."""

    def test_assign_mentor_exceeds_quota(self):
        """Khi mentor đã hướng dẫn đủ MAX_INTERNS_PER_MENTOR sinh viên, gán thêm sinh viên mới phải trả về 400 Bad Request."""
        db = TestingSessionLocal()
        # Đã có 1 sinh viên (HS002) được gán cho MENTOR01 trong fixture.
        # Tạo thêm (MAX_INTERNS_PER_MENTOR - 1) sinh viên để đạt đúng ngưỡng tối đa.
        for i in range(10, 10 + (MAX_INTERNS_PER_MENTOR - 1)):
            hs = HoSoThucTap(
                ma_ho_so=f"HS{i:05d}",
                ma_sinh_vien="TTS001",
                ho_ten=f"Sinh viên {i}",
                vi_tri_thuc_tap="Tester",
                trang_thai="DangThucTap",
                ma_mentor="MENTOR01",
            )
            db.add(hs)
        db.commit()
        db.close()

        response = client.patch(
            "/api/v1/interns/HS001/mentor",
            json={"ma_mentor": "MENTOR01"},
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["error_code"] == "MENTOR_QUOTA_EXCEEDED"

