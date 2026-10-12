import pytest
from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models.ho_so import HoSoThucTap
from database.models.nguoi_dung import NguoiDung

client = TestClient(app)

def test_get_evaluations_by_profile_success_student_1():
    response = client.get("/api/v1/evaluations/by-profile/1")
    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert "data" in body
    data = body["data"]
    assert data["ho_so_id"] == 1
    assert data["ho_ten"] == "Nguyễn Văn A"
    assert "vana@example.com" in data["email"]
    assert data["diem_trung_binh_chung"] >= 8.5
    assert data["xep_loai_chung"] in ["Gioi", "XuatSac"]
    assert len(data["danh_sach_danh_gia"]) == 2
    
    types = [it["loai_danh_gia"] for it in data["danh_sach_danh_gia"]]
    assert "GiuaKy" in types
    assert "CuoiKy" in types
    
    mid_eval = next(it for it in data["danh_sach_danh_gia"] if it["loai_danh_gia"] == "GiuaKy")
    assert mid_eval["diem_ky_nang"] == 8.5
    assert mid_eval["diem_thai_do"] == 9.0
    assert mid_eval["diem_trung_binh"] == 8.75
    assert mid_eval["ten_nguoi_danh_gia"] == "Nguyễn Hướng Dẫn"

def test_get_evaluations_by_profile_success_student_2():
    response = client.get("/api/v1/evaluations/by-profile/2")
    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert data["ho_so_id"] == 2
    assert data["ho_ten"] == "Trần Thị B"
    assert len(data["danh_sach_danh_gia"]) == 2

def test_get_evaluations_by_profile_empty_evaluations():
    from conftest import TestSessionLocal
    session = TestSessionLocal()
    try:
        new_user = NguoiDung(
            ma_nguoi_dung=999,
            ma_phong_ban=1,
            ho_ten="Sinh Viên Test Chưa Đánh Giá",
            email="chuadanhgia@test.com",
            mat_khau_hash="123456",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        session.add(new_user)
        session.flush()

        new_hs = HoSoThucTap(
            ma_ho_so=999,
            ma_nguoi_dung=999,
            ma_truong=1,
            ma_chuong_trinh=1,
            chuyen_nganh="An toàn thông tin",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        session.add(new_hs)
        session.commit()
    finally:
        session.close()

    response = client.get("/api/v1/evaluations/by-profile/999")
    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert data["ho_so_id"] == 999
    assert data["diem_trung_binh_chung"] == 0.0
    assert data["xep_loai_chung"] == "ChuaDanhGia"
    assert data["danh_sach_danh_gia"] == []

def test_get_evaluations_by_profile_not_found():
    response = client.get("/api/v1/evaluations/by-profile/999999")
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert "Không tìm thấy hồ sơ" in body["detail"]

def test_get_evaluations_query_param_profile_filter():
    response = client.get("/api/v1/evaluations?ma_ho_so=1")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["ho_so_id"] == 1
    assert len(body["data"]["danh_sach_danh_gia"]) == 2

def test_get_evaluations_list_all():
    response = client.get("/api/v1/evaluations")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 4
