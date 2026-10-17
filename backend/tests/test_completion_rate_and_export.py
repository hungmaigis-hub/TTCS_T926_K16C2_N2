import io
import pytest
from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import HoSoThucTap

client = TestClient(app)


def test_get_completion_rate_success():
    response = client.get("/api/v1/reports/completion-rate")
    assert response.status_code == 200
    data = response.json()
    assert "tong_so_sinh_vien" in data
    assert "so_luong_dang_thuc_tap" in data
    assert "so_luong_hoan_thanh" in data
    assert "so_luong_thoi_hoc" in data
    assert "ty_le_hoan_thanh" in data
    assert "chi_tiet_theo_trang_thai" in data
    assert 0.0 <= data["ty_le_hoan_thanh"] <= 100.0


def test_export_reports_excel_success():
    response = client.get("/api/v1/reports/export?format=excel")
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")
    assert len(response.content) > 100


def test_export_reports_pdf_success():
    response = client.get("/api/v1/reports/export?format=pdf")
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")
    assert response.content.startswith(b"%PDF")


def test_export_reports_invalid_format():
    response = client.get("/api/v1/reports/export?format=csv")
    assert response.status_code == 400
    assert "không được hỗ trợ" in response.json().get("detail", "")
