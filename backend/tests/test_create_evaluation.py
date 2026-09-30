import sys
from pathlib import Path
import pytest

# Thiết lập đường dẫn import backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import DanhGia, HoSoThucTap, NguoiDung

client = TestClient(app)

@pytest.fixture
def sample_test_intern():
    """Tạo một thực tập sinh mới độc lập cho bài test đánh giá và tự dọn dẹp sau khi test"""
    try:
        from tests.conftest import MYSQL_AVAILABLE, TestSessionLocal
        Session = SessionLocal if MYSQL_AVAILABLE else TestSessionLocal
    except Exception:
        Session = SessionLocal

    db = Session()
    intern_id = 999
    try:
        # Xóa dọn nếu trước đó còn tồn đọng
        db.query(DanhGia).filter(DanhGia.ma_ho_so == intern_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == intern_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_id).delete()
        db.commit()

        user = NguoiDung(
            ma_nguoi_dung=intern_id,
            ma_phong_ban=1,
            ho_ten="Sinh Viên Kiểm Thử Đánh Giá",
            email="eval_intern_test@example.com",
            so_dien_thoai="0933999888",
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add(user)
        db.flush()

        ho_so = HoSoThucTap(
            ma_ho_so=intern_id,
            ma_nguoi_dung=intern_id,
            ma_truong=1,
            ma_chuong_trinh=1,
            ma_mentor=3,
            chuyen_nganh="Kỹ thuật phần mềm",
            trang_thai_xet_duyet="DaDuyet",
            trang_thai_thuc_tap="DangThucTap"
        )
        db.add(ho_so)
        db.commit()
    finally:
        db.close()

    yield intern_id

    # Dọn dẹp sau khi hoàn thành test
    db = Session()
    try:
        db.query(DanhGia).filter(DanhGia.ma_ho_so == intern_id).delete()
        db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == intern_id).delete()
        db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_id).delete()
        db.commit()
    finally:
        db.close()


# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/evaluations
# ==============================================================================

def test_create_evaluation_giuaky_success(sample_test_intern):
    """Kiểm tra tạo đánh giá Giữa kỳ thành công với đầy đủ các trường -> 201 Created"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.5,
        "diem_thai_do": 9.0,
        "nhan_xet": "Sinh viên nắm vững kiến thức thực tế, chủ động học hỏi",
        "de_xuat_tuyen_dung": False
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status_code"] == 201
    assert res_data["message"] == "Tạo đánh giá thực tập sinh thành công"
    assert "data" in res_data

    eval_item = res_data["data"]
    assert eval_item["ma_ho_so"] == sample_test_intern
    assert eval_item["ma_nguoi_danh_gia"] == 3
    assert eval_item["loai_danh_gia"] == "GiuaKy"
    assert eval_item["diem_ky_nang"] == 8.5
    assert eval_item["diem_thai_do"] == 9.0
    assert eval_item["diem_trung_binh"] == 8.75
    assert eval_item["xep_loai"] == "Gioi"
    assert eval_item["de_xuat_tuyen_chinh_thuc"] is False
    assert "chủ động học hỏi" in eval_item["nhan_xet_chi_tiet"]


def test_create_evaluation_cuoiky_success(sample_test_intern):
    """Kiểm tra tạo đánh giá Cuối kỳ với điểm xuất sắc và đề xuất tuyển dụng -> 201 Created"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "CuoiKy",
        "diem_ky_nang": 9.5,
        "diem_thai_do": 9.5,
        "nhan_xet_chi_tiet": "Hoàn thành xuất sắc nhiệm vụ, năng lực kỹ thuật tốt",
        "de_xuat_tuyen_chinh_thuc": True
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    eval_item = res_data["data"]
    assert eval_item["loai_danh_gia"] == "CuoiKy"
    assert eval_item["diem_trung_binh"] == 9.5
    assert eval_item["xep_loai"] == "XuatSac"
    assert eval_item["de_xuat_tuyen_chinh_thuc"] is True


def test_create_evaluation_duplicate_same_type_rejected(sample_test_intern):
    """Kiểm tra tạo 2 lần cùng loại đánh giá Giữa kỳ cho 1 hồ sơ -> 400 Bad Request"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.0,
        "diem_thai_do": 8.0,
    }
    # Lần 1: thành công
    res1 = client.post("/api/v1/evaluations", json=payload)
    assert res1.status_code == 201

    # Lần 2: trùng lặp -> phải bị chặn
    res2 = client.post("/api/v1/evaluations", json=payload)
    assert res2.status_code == 400
    assert "đã có đánh giá GiuaKy" in res2.json()["detail"]


def test_create_evaluation_both_midterm_and_final_allowed(sample_test_intern):
    """Kiểm tra 1 hồ sơ được phép có cả đánh giá Giữa kỳ và Cuối kỳ -> Cả 2 đều 201 Created"""
    payload_mid = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 7.0,
        "diem_thai_do": 8.0,
    }
    payload_final = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "CuoiKy",
        "diem_ky_nang": 9.0,
        "diem_thai_do": 9.0,
    }
    res_mid = client.post("/api/v1/evaluations", json=payload_mid)
    res_final = client.post("/api/v1/evaluations", json=payload_final)
    assert res_mid.status_code == 201
    assert res_final.status_code == 201


def test_create_evaluation_invalid_skill_score_negative(sample_test_intern):
    """Kiểm tra điểm kỹ năng âm (< 0) -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": -1.0,
        "diem_thai_do": 8.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 422


def test_create_evaluation_invalid_skill_score_above_10(sample_test_intern):
    """Kiểm tra điểm kỹ năng vượt quá 10.0 -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 10.5,
        "diem_thai_do": 8.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 422


def test_create_evaluation_invalid_attitude_score_negative(sample_test_intern):
    """Kiểm tra điểm thái độ âm (< 0) -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.0,
        "diem_thai_do": -0.5,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 422


def test_create_evaluation_invalid_attitude_score_above_10(sample_test_intern):
    """Kiểm tra điểm thái độ vượt quá 10.0 -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.0,
        "diem_thai_do": 11.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 422


def test_create_evaluation_invalid_loai_danh_gia(sample_test_intern):
    """Kiểm tra loại đánh giá không phải GiuaKy/CuoiKy -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "DinhKyHangThang",
        "diem_ky_nang": 8.0,
        "diem_thai_do": 8.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 422


def test_create_evaluation_intern_not_found():
    """Kiểm tra mã hồ sơ không tồn tại trong hệ thống -> 404 Not Found"""
    payload = {
        "ma_ho_so": 999999,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.0,
        "diem_thai_do": 8.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập sinh" in response.json()["detail"]


def test_create_evaluation_evaluator_not_found(sample_test_intern):
    """Kiểm tra mã người đánh giá không tồn tại trong hệ thống -> 400 Bad Request"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 999999,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.0,
        "diem_thai_do": 8.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 400
    assert "Người đánh giá với mã ID" in response.json()["detail"]


def test_create_evaluation_boundary_scores_min(sample_test_intern):
    """Kiểm tra điểm số biên tối thiểu 0.0 -> Xếp loại 'Yeu' -> 201 Created"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 0.0,
        "diem_thai_do": 0.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    eval_item = response.json()["data"]
    assert eval_item["diem_trung_binh"] == 0.0
    assert eval_item["xep_loai"] == "Yeu"


def test_create_evaluation_boundary_scores_max(sample_test_intern):
    """Kiểm tra điểm số biên tối đa 10.0 -> Xếp loại 'XuatSac' -> 201 Created"""
    payload = {
        "ma_ho_so": sample_test_intern,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "CuoiKy",
        "diem_ky_nang": 10.0,
        "diem_thai_do": 10.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    eval_item = response.json()["data"]
    assert eval_item["diem_trung_binh"] == 10.0
    assert eval_item["xep_loai"] == "XuatSac"


def test_create_evaluation_invalid_negative_intern_id():
    """Kiểm tra mã hồ sơ là số âm -> 422 Unprocessable Entity"""
    payload = {
        "ma_ho_so": -5,
        "ma_nguoi_danh_gia": 3,
        "loai_danh_gia": "GiuaKy",
        "diem_ky_nang": 8.0,
        "diem_thai_do": 8.0,
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 422
