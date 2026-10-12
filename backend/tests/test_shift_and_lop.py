import sys
from pathlib import Path
from datetime import datetime
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.models import CaLamViec
from database.session import SessionLocal

client = TestClient(app)


def test_interns_endpoint_returns_lop():
    response = client.get("/api/v1/interns?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    intern = data["data"][0]
    assert "lop" in intern
    assert intern["lop"] is not None


def test_create_shift_with_lop():
    try:
        from tests.conftest import TestSessionLocal
        db = TestSessionLocal()
    except Exception:
        db = SessionLocal()
    shift_name = f"Test Shift Lop {datetime.now().strftime('%H%M%S%f')}"
    try:
        payload = {
            "ten_ca": shift_name,
            "gio_bat_dau": "14:00",
            "gio_ket_thuc": "16:00",
            "cac_ngay_trong_tuan": "Linh hoạt",
            "ngay_dien_ra": "2026-10-15",
            "chuyen_nganh": "KTPM-K19A",
            "lop": "KTPM-K19A",
            "ghi_chu": "Ca họp test phân quyền theo lớp"
        }
        res = client.post("/api/v1/attendance/shifts", json=payload)
        assert res.status_code == 201
        res_data = res.json()
        assert res_data["status_code"] == 201
        assert "data" in res_data
        assert res_data["data"]["lop"] == "KTPM-K19A"
        assert res_data["data"]["chuyen_nganh"] == "KTPM-K19A"

        # Check in DB
        db_shift = db.query(CaLamViec).filter(CaLamViec.ten_ca == shift_name).first()
        assert db_shift is not None
        assert db_shift.lop == "KTPM-K19A"
    finally:
        db.query(CaLamViec).filter(CaLamViec.ten_ca == shift_name).delete()
        db.commit()
        db.close()
