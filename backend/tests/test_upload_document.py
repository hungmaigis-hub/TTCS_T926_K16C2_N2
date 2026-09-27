import os
import sys
import io
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app, UPLOAD_DIR

client = TestClient(app)

# ==============================================================================
# BỘ KIỂM THỬ CHO API: POST /api/v1/documents/upload (Upload tài liệu hồ sơ)
# ==============================================================================

@pytest.fixture(autouse=True)
def cleanup_uploaded_test_files():
    """Dọn dẹp các file rác sinh ra trong quá trình test upload"""
    yield
    # Sau mỗi test case, dọn dẹp các file test nếu cần
    for f in UPLOAD_DIR.glob("*_test_*"):
        try:
            f.unlink()
        except OSError:
            pass


def test_upload_document_pdf_success():
    """Kiểm tra upload tài liệu PDF thành công cho hồ sơ ID 1 -> 201 Created"""
    file_content = b"%PDF-1.4 Mock PDF Content For Testing Purposes"
    file_obj = io.BytesIO(file_content)
    
    files = {
        "file": ("test_cv_sample.pdf", file_obj, "application/pdf")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "CV"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status_code"] == 201
    assert res_data["message"] == "Tải lên tài liệu thành công"
    assert "data" in res_data
    
    doc = res_data["data"]
    assert doc["ma_ho_so"] == 1
    assert doc["loai_tai_lieu"] == "CV"
    assert doc["trang_thai_duyet"] == "ChoDuyet"
    assert doc["duong_dan_file"].startswith("uploads/1_CV_")
    assert doc["duong_dan_file"].endswith(".pdf")
    
    # Kiểm tra file thực tế đã được lưu trên ổ cứng
    saved_file_name = doc["duong_dan_file"].replace("uploads/", "")
    saved_file_path = UPLOAD_DIR / saved_file_name
    assert saved_file_path.exists()
    assert saved_file_path.read_bytes() == file_content
    
    # Dọn dẹp file
    if saved_file_path.exists():
        saved_file_path.unlink()


def test_upload_document_image_png_success():
    """Kiểm tra upload hình ảnh tài liệu PNG thành công -> 201 Created"""
    file_content = b"\x89PNG\r\n\x1a\nMock PNG bytes"
    file_obj = io.BytesIO(file_content)
    
    files = {
        "file": ("test_scan_cert.png", file_obj, "image/png")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "ChungChi"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 201
    doc = response.json()["data"]
    assert doc["loai_tai_lieu"] == "ChungChi"
    assert doc["duong_dan_file"].endswith(".png")
    
    # Dọn dẹp file
    saved_file_name = doc["duong_dan_file"].replace("uploads/", "")
    saved_file_path = UPLOAD_DIR / saved_file_name
    if saved_file_path.exists():
        saved_file_path.unlink()


def test_upload_document_docx_success():
    """Kiểm tra upload file tài liệu Word (.docx) thành công -> 201 Created"""
    file_content = b"PK\x03\x04Mock DOCX Content"
    file_obj = io.BytesIO(file_content)
    
    files = {
        "file": ("test_don_xin.docx", file_obj, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "DonXinThucTap"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 201
    doc = response.json()["data"]
    assert doc["loai_tai_lieu"] == "DonXinThucTap"
    assert doc["duong_dan_file"].endswith(".docx")
    
    saved_file_name = doc["duong_dan_file"].replace("uploads/", "")
    saved_file_path = UPLOAD_DIR / saved_file_name
    if saved_file_path.exists():
        saved_file_path.unlink()


def test_upload_document_static_file_serving():
    """Kiểm tra xem file đã upload có thể truy cập tĩnh qua endpoint /uploads/<filename> không"""
    file_content = b"Static Serving Verification Content"
    file_obj = io.BytesIO(file_content)
    
    files = {
        "file": ("verify_static.pdf", file_obj, "application/pdf")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "GiayGioiThieu"
    }
    
    upload_res = client.post("/api/v1/documents/upload", data=data, files=files)
    assert upload_res.status_code == 201
    relative_path = upload_res.json()["data"]["duong_dan_file"]
    
    # Truy vấn file tĩnh
    get_res = client.get(f"/{relative_path}")
    assert get_res.status_code == 200
    assert get_res.content == file_content
    
    # Dọn dẹp file
    saved_file_name = relative_path.replace("uploads/", "")
    saved_file_path = UPLOAD_DIR / saved_file_name
    if saved_file_path.exists():
        saved_file_path.unlink()


def test_upload_document_ho_so_not_found():
    """Kiểm tra khi mã hồ sơ không tồn tại trong CSDL -> 404 Not Found"""
    file_obj = io.BytesIO(b"Dummy Content")
    files = {
        "file": ("sample.pdf", file_obj, "application/pdf")
    }
    data = {
        "ma_ho_so": 99999,
        "loai_tai_lieu": "CV"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ thực tập" in response.json()["detail"]


def test_upload_document_disallowed_extension_exe():
    """Kiểm tra chặn file thực thi .exe nguy hiểm -> 400 Bad Request"""
    file_obj = io.BytesIO(b"MZ executable mock content")
    files = {
        "file": ("malicious.exe", file_obj, "application/x-msdownload")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "CV"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 400
    assert "Định dạng tệp '.exe' không được hỗ trợ" in response.json()["detail"]


def test_upload_document_disallowed_extension_sh():
    """Kiểm tra chặn file script .sh nguy hiểm -> 400 Bad Request"""
    file_obj = io.BytesIO(b"#!/bin/bash\necho hi")
    files = {
        "file": ("script.sh", file_obj, "application/x-sh")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "CV"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 400
    assert "Định dạng tệp '.sh' không được hỗ trợ" in response.json()["detail"]


def test_upload_document_empty_loai_tai_lieu():
    """Kiểm tra khi loại tài liệu rỗng hoặc chỉ toàn khoảng trắng -> 422 Unprocessable Entity"""
    file_obj = io.BytesIO(b"PDF Content")
    files = {
        "file": ("sample.pdf", file_obj, "application/pdf")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "    "
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 422
    assert "Loại tài liệu không được để trống" in response.json()["detail"]


def test_upload_document_missing_file():
    """Kiểm tra khi không gửi file đính kèm -> 422 Unprocessable Entity"""
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "CV"
    }
    response = client.post("/api/v1/documents/upload", data=data)
    assert response.status_code == 422


def test_upload_document_missing_ma_ho_so():
    """Kiểm tra khi không gửi ma_ho_so -> 422 Unprocessable Entity"""
    file_obj = io.BytesIO(b"PDF Content")
    files = {
        "file": ("sample.pdf", file_obj, "application/pdf")
    }
    data = {
        "loai_tai_lieu": "CV"
    }
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 422


def test_upload_document_exceeds_max_size():
    """Kiểm tra chặn file vượt quá giới hạn 10MB -> 400 Bad Request"""
    # Tạo chuỗi bytes > 10MB
    large_content = b"0" * (10 * 1024 * 1024 + 1024)
    file_obj = io.BytesIO(large_content)
    
    files = {
        "file": ("large_file.pdf", file_obj, "application/pdf")
    }
    data = {
        "ma_ho_so": 1,
        "loai_tai_lieu": "CV"
    }
    
    response = client.post("/api/v1/documents/upload", data=data, files=files)
    assert response.status_code == 400
    assert "vượt quá giới hạn cho phép" in response.json()["detail"]
