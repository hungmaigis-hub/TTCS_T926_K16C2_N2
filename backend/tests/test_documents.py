import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient
from main import app

# Khởi tạo client giả lập để gửi request test đến API mà không cần bật server
client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: GET /api/v1/documents/{ho_so_id}
# ==============================================================================

def test_get_documents_success():
    """Kiểm tra lấy thành công danh sách tài liệu của hồ sơ có sẵn (ho_so_id = 1) -> 200"""
    response = client.get("/api/v1/documents/1")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert "data" in res_data
    assert isinstance(res_data["data"], list)
    assert len(res_data["data"]) >= 1

    # Kiểm tra cấu trúc từng tài liệu trả về
    first_doc = res_data["data"][0]
    assert "ma_tai_lieu" in first_doc
    assert "ma_ho_so" in first_doc
    assert first_doc["ma_ho_so"] == 1
    assert "loai_tai_lieu" in first_doc
    assert "duong_dan_file" in first_doc
    assert "trang_thai_duyet" in first_doc

def test_get_documents_empty_list():
    """Kiểm tra hồ sơ tồn tại nhưng chưa có tài liệu nào (ho_so_id = 2) -> 200, data = []"""
    response = client.get("/api/v1/documents/2")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert "data" in res_data
    assert isinstance(res_data["data"], list)
    assert len(res_data["data"]) == 0

def test_get_documents_ho_so_not_found():
    """Kiểm tra mã hồ sơ không tồn tại trong CSDL -> 404 Not Found"""
    response = client.get("/api/v1/documents/99999")
    assert response.status_code == 404
    res_data = response.json()
    assert "detail" in res_data
    assert "Không tìm thấy hồ sơ thực tập" in res_data["detail"]

def test_get_documents_invalid_id_string():
    """Kiểm tra mã hồ sơ là chuỗi chữ cái -> 422 Unprocessable Entity"""
    response = client.get("/api/v1/documents/abc")
    assert response.status_code == 422

def test_get_documents_invalid_id_float():
    """Kiểm tra mã hồ sơ là số thực (float) -> 422 Unprocessable Entity"""
    response = client.get("/api/v1/documents/1.5")
    assert response.status_code == 422

def test_get_documents_negative_id():
    """Kiểm tra mã hồ sơ là số âm (biên dưới) -> 404 Not Found"""
    response = client.get("/api/v1/documents/-1")
    assert response.status_code == 404

def test_get_documents_zero_id():
    """Kiểm tra mã hồ sơ = 0 (biên không tồn tại) -> 404 Not Found"""
    response = client.get("/api/v1/documents/0")
    assert response.status_code == 404


# ==============================================================================
# BỘ KIỂM THỬ CHO API: PATCH /api/v1/documents/{id}/status
# ==============================================================================

def test_patch_status_to_daduyet_success():
    """Kiểm tra duyệt tài liệu: chuyển trạng thái sang DaDuyet -> 200 OK"""
    payload = {"trang_thai_duyet": "DaDuyet"}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    assert res_data["message"] == "Cập nhật trạng thái duyệt tài liệu thành công"
    assert res_data["data"]["ma_tai_lieu"] == 1
    assert res_data["data"]["trang_thai_duyet"] == "DaDuyet"

def test_patch_status_to_tuchoi_success():
    """Kiểm tra từ chối tài liệu: chuyển trạng thái sang TuChoi -> 200 OK"""
    payload = {"trang_thai_duyet": "TuChoi"}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai_duyet"] == "TuChoi"

def test_patch_status_to_choduyet_success():
    """Kiểm tra khôi phục trạng thái về ChoDuyet -> 200 OK"""
    payload = {"trang_thai_duyet": "ChoDuyet"}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["trang_thai_duyet"] == "ChoDuyet"

def test_patch_status_strip_whitespace():
    """Kiểm tra giá trị có khoảng trắng ở hai đầu -> Tự động strip và hợp lệ (200)"""
    payload = {"trang_thai_duyet": "  DaDuyet  "}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["trang_thai_duyet"] == "DaDuyet"

def test_patch_status_document_not_found():
    """Kiểm tra cập nhật tài liệu với ID không tồn tại -> 404 Not Found"""
    payload = {"trang_thai_duyet": "DaDuyet"}
    response = client.patch("/api/v1/documents/99999/status", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy tài liệu" in response.json()["detail"]

def test_patch_status_invalid_value_word():
    """Kiểm tra truyền giá trị không nằm trong danh mục (ví dụ 'Approved', 'ChapThuan') -> 422"""
    payload = {"trang_thai_duyet": "Approved"}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_case_sensitive():
    """Kiểm tra truyền sai chữ hoa/thường (ví dụ 'daduyet' thay vì 'DaDuyet') -> 422"""
    payload = {"trang_thai_duyet": "daduyet"}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_empty_string():
    """Kiểm tra truyền chuỗi rỗng -> 422 Unprocessable Entity"""
    payload = {"trang_thai_duyet": ""}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_only_whitespace():
    """Kiểm tra truyền chuỗi chỉ chứa khoảng trắng -> 422 Unprocessable Entity"""
    payload = {"trang_thai_duyet": "     "}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_field_is_null():
    """Kiểm tra truyền null cho trường bắt buộc -> 422 Unprocessable Entity"""
    payload = {"trang_thai_duyet": None}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_missing_field():
    """Kiểm tra gửi body rỗng thiếu trường bắt buộc -> 422 Unprocessable Entity"""
    payload = {}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_invalid_data_type():
    """Kiểm tra truyền sai kiểu dữ liệu (số thay vì chuỗi) -> 422 Unprocessable Entity"""
    payload = {"trang_thai_duyet": 12345}
    response = client.patch("/api/v1/documents/1/status", json=payload)
    assert response.status_code == 422

def test_patch_status_invalid_id_string():
    """Kiểm tra mã tài liệu là chuỗi ký tự -> 422 Unprocessable Entity"""
    payload = {"trang_thai_duyet": "DaDuyet"}
    response = client.patch("/api/v1/documents/invalid_id/status", json=payload)
    assert response.status_code == 422

def test_patch_status_negative_id():
    """Kiểm tra mã tài liệu là số âm (biên dưới) -> 404 Not Found"""
    payload = {"trang_thai_duyet": "DaDuyet"}
    response = client.patch("/api/v1/documents/-10/status", json=payload)
    assert response.status_code == 404
