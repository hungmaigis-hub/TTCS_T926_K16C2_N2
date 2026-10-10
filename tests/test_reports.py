import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.intern import Intern, InternStatus

# Khởi tạo in-memory SQLite database riêng biệt cho tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="function")
def db_session():
    """Fixture tạo database schema và session sạch cho mỗi bài test."""
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test)

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture override dependency get_db để dùng test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_completion_rate_empty_db(client):
    """Kiểm tra khi database chưa có sinh viên nào (xử lý không lỗi chia cho 0)."""
    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    res_json = response.json()
    
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["total_students"] == 0
    assert data["status_counts"]["DangThucTap"] == 0
    assert data["status_counts"]["HoanThanh"] == 0
    assert data["status_counts"]["ThoiHoc"] == 0
    assert data["completion_rate"] == 0.0
    assert data["percentages"]["DangThucTap"] == 0.0
    assert data["percentages"]["HoanThanh"] == 0.0
    assert data["percentages"]["ThoiHoc"] == 0.0

def test_completion_rate_with_data(client, db_session):
    """Kiểm tra tính toán chính xác tổng số, đếm trạng thái và tỷ lệ hoàn thành %."""
    # Thêm 10 sinh viên:
    # 5 Hoàn thành, 3 Đang thực tập, 2 Thôi học
    interns = [
        # 5 Hoàn thành
        Intern(student_code="SV1", full_name="A", university="ĐH Bách Khoa", department="Backend", status=InternStatus.HoanThanh),
        Intern(student_code="SV2", full_name="B", university="ĐH Bách Khoa", department="Backend", status=InternStatus.HoanThanh),
        Intern(student_code="SV3", full_name="C", university="ĐH CNTT", department="Frontend", status=InternStatus.HoanThanh),
        Intern(student_code="SV4", full_name="D", university="ĐH CNTT", department="Frontend", status=InternStatus.HoanThanh),
        Intern(student_code="SV5", full_name="E", university="ĐH Quốc Gia", department="QA", status=InternStatus.HoanThanh),
        # 3 Đang thực tập
        Intern(student_code="SV6", full_name="F", university="ĐH Bách Khoa", department="Backend", status=InternStatus.DangThucTap),
        Intern(student_code="SV7", full_name="G", university="ĐH CNTT", department="Frontend", status=InternStatus.DangThucTap),
        Intern(student_code="SV8", full_name="H", university="ĐH Quốc Gia", department="Mobile", status=InternStatus.DangThucTap),
        # 2 Thôi học
        Intern(student_code="SV9", full_name="I", university="ĐH Bách Khoa", department="Backend", status=InternStatus.ThoiHoc),
        Intern(student_code="SV10", full_name="K", university="ĐH CNTT", department="Frontend", status=InternStatus.ThoiHoc),
    ]
    db_session.add_all(interns)
    db_session.commit()

    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    res_json = response.json()
    data = res_json["data"]

    # Tổng số sinh viên
    assert data["total_students"] == 10
    
    # Đếm theo từng trạng thái
    assert data["status_counts"]["HoanThanh"] == 5
    assert data["status_counts"]["DangThucTap"] == 3
    assert data["status_counts"]["ThoiHoc"] == 2

    # Tỷ lệ phần trăm
    # Tỷ lệ hoàn thành = 5/10 * 100 = 50.0%
    assert data["completion_rate"] == 50.0
    assert data["percentages"]["HoanThanh"] == 50.0
    assert data["percentages"]["DangThucTap"] == 30.0
    assert data["percentages"]["ThoiHoc"] == 20.0

    # Chart data
    assert len(data["chart_data"]) == 3
    assert data["chart_data"][0]["status"] == "HoanThanh"
    assert data["chart_data"][0]["count"] == 5
    assert data["chart_data"][0]["percentage"] == 50.0

def test_completion_rate_filter_by_department(client, db_session):
    """Kiểm tra chức năng lọc theo phòng ban (Backend)."""
    interns = [
        Intern(student_code="SV1", full_name="A", university="ĐH Bách Khoa", department="Backend", status=InternStatus.HoanThanh),
        Intern(student_code="SV2", full_name="B", university="ĐH Bách Khoa", department="Backend", status=InternStatus.DangThucTap),
        Intern(student_code="SV3", full_name="C", university="ĐH CNTT", department="Frontend", status=InternStatus.HoanThanh),
    ]
    db_session.add_all(interns)
    db_session.commit()

    response = client.get("/api/v1/reports/completion-rate?department=Backend")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["total_students"] == 2
    assert data["status_counts"]["HoanThanh"] == 1
    assert data["status_counts"]["DangThucTap"] == 1
    assert data["status_counts"]["ThoiHoc"] == 0
    assert data["completion_rate"] == 50.0
    assert data["filters_applied"]["department"] == "Backend"
