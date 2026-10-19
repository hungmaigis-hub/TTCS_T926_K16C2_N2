import pytest
from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models.nguoi_dung import NguoiDung
from database.models.nhat_ky_hoat_dong import NhatKyHoatDong

client = TestClient(app)

@pytest.fixture(autouse=True)
def ensure_admin_exists():
    db = SessionLocal()
    try:
        admin = db.query(NguoiDung).filter(NguoiDung.email == "admin@ictu.edu.vn").first()
        if not admin:
            admin = NguoiDung(
                ho_ten="Ban Quản trị Hệ thống ICTU",
                email="admin@ictu.edu.vn",
                vai_tro="Admin",
                trang_thai="HoatDong"
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def test_get_audit_logs_success():
    res = client.get(
        "/api/v1/admin/audit-logs",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status_code"] == 200
    assert "items" in data
    assert "stats" in data
    assert data["total"] >= 1
    assert data["stats"]["total_logs"] >= 1
    assert data["stats"]["success_rate"] >= 0


def test_filter_audit_logs_by_action():
    res = client.get(
        "/api/v1/admin/audit-logs?hanh_dong=SAO_LUU_CSDL",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert "SAO_LUU_CSDL" in item["hanh_dong"]


def test_create_and_query_custom_audit_log():
    payload = {
        "hanh_dong": "KIEM_THU_AUDIT",
        "endpoint": "/api/v1/test",
        "phuong_thuc": "POST",
        "dia_chi_ip": "10.10.10.10",
        "mo_ta": "Ghi log thử nghiệm tự động từ unit test",
        "trang_thai_http": 201
    }
    create_res = client.post(
        "/api/v1/admin/audit-logs",
        headers={"X-User-Email": "admin@example.com"},
        json=payload
    )
    assert create_res.status_code == 201
    log_id = create_res.json()["ma_nhat_ky"]
    assert log_id > 0

    # Query lại bằng keyword
    get_res = client.get(
        "/api/v1/admin/audit-logs?tu_khoa=KIEM_THU_AUDIT",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert get_res.status_code == 200
    items = get_res.json()["items"]
    assert any(it["hanh_dong"] == "KIEM_THU_AUDIT" for it in items)


def test_audit_logs_unauthorized():
    # Không gửi header auth
    res = client.get("/api/v1/admin/audit-logs")
    assert res.status_code in [401, 403]
