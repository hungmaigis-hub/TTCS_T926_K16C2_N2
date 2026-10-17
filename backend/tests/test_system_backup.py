"""
Test Suite kiểm thử toàn diện cho Dịch vụ sao lưu cơ sở dữ liệu hệ thống (System Backup Service):
- Kích hoạt sao lưu thủ công qua API: POST /api/v1/system/backup
- Truy vấn danh sách bản sao lưu: GET /api/v1/system/backups
- Stream tải bản sao lưu nén (.sql.gz): GET /api/v1/system/backups/{filename}/download
- Xóa bản sao lưu: DELETE /api/v1/system/backups/{filename}
- Cơ chế nén gzip, kiểm tra tính toàn vẹn Checksum SHA-256
- Cơ chế chống tấn công Path Traversal Security
- Cơ chế chống xung đột thao tác đồng thời (Concurrency Lock / 409 Conflict)
- Cơ chế dọn dẹp bản sao lưu cũ (Retention Policy)
- Bộ lập lịch sao lưu tự động định kỳ (BackupScheduler)
- Phân quyền RBAC (system:backup / Admin / Chặn Thực tập sinh & Tài khoản khóa)
"""
import os
import sys
import gzip
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app
from database.session import get_db
from tests.conftest import TestSessionLocal
from services.backup_service import (
    create_backup,
    list_backups,
    get_backup_file_stream,
    delete_backup,
    cleanup_old_backups,
    backup_scheduler,
    validate_backup_filename,
    calculate_sha256,
    format_bytes,
    get_backup_directory,
    _dump_mysql_to_gzip,
    BackupInProgressError,
    BackupExecutionError,
    BackupSecurityError,
    BackupNotFoundError,
)

client = TestClient(app)


def test_format_bytes_utility():
    """Kiểm tra hàm format dung lượng bytes sang đơn vị dễ đọc"""
    assert format_bytes(500) == "500 B"
    assert "KB" in format_bytes(2048)
    assert "MB" in format_bytes(5 * 1024 * 1024)
    assert "GB" in format_bytes(2 * 1024 * 1024 * 1024)


def test_validate_backup_filename_security():
    """Kiểm tra tính an toàn của tên file sao lưu, chặn Path Traversal triệt để"""
    # Hợp lệ
    assert validate_backup_filename("backup_test_20261015.sql.gz") == "backup_test_20261015.sql.gz"
    assert validate_backup_filename("my-backup_1.0.sql.gz") == "my-backup_1.0.sql.gz"

    # Không hợp lệ: Chứa ../, ..\\, ký tự đường dẫn
    with pytest.raises(BackupSecurityError):
        validate_backup_filename("../../etc/passwd.sql.gz")

    with pytest.raises(BackupSecurityError):
        validate_backup_filename("..\\..\\windows\\system32.sql.gz")

    with pytest.raises(BackupSecurityError):
        validate_backup_filename("/var/backups/test.sql.gz")

    with pytest.raises(BackupSecurityError):
        validate_backup_filename("test.sql")  # Thiếu .gz

    with pytest.raises(BackupSecurityError):
        validate_backup_filename("shell.php")

    with pytest.raises(BackupSecurityError):
        validate_backup_filename("")


def test_post_trigger_backup_success():
    """Kiểm tra Admin kích hoạt sao lưu thủ công thành công (HTTP 201 Created)"""
    response = client.post(
        "/api/v1/system/backup",
        headers={"X-User-Email": "admin@example.com"},
        json={"note": "Bản sao lưu kiểm thử đơn vị", "prefix": "test_unit"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status_code"] == 201
    assert "thành công" in data["message"].lower()

    backup = data["backup"]
    filename = backup["filename"]
    assert filename.startswith("test_unit_")
    assert filename.endswith(".sql.gz")
    assert backup["size_bytes"] > 0
    assert backup["checksum_sha256"] is not None
    assert backup["note"] == "Bản sao lưu kiểm thử đơn vị"
    assert f"/api/v1/system/backups/{filename}/download" in backup["download_url"]

    # Kiểm tra file vật lý trên đĩa
    backup_dir = get_backup_directory()
    filepath = backup_dir / filename
    assert filepath.exists()

    # Kiểm tra giải nén tệp .sql.gz và kiểm tra nội dung SQL
    with gzip.open(filepath, "rt", encoding="utf-8") as gz_in:
        sql_content = gz_in.read()
        assert len(sql_content) > 0
        assert "TABLE" in sql_content.upper() or "INSERT" in sql_content.upper() or "DATABASE" in sql_content.upper()

    # Kiểm tra đối soát Checksum SHA-256
    calculated_hash = calculate_sha256(filepath)
    assert calculated_hash == backup["checksum_sha256"]


def test_post_backup_unauthorized_and_forbidden():
    """Kiểm tra bảo mật RBAC: Chặn chưa đăng nhập, sinh viên và tài khoản bị khóa"""
    # 1. Không có thông tin xác thực
    res_no_auth = client.post("/api/v1/system/backup")
    assert res_no_auth.status_code == 401

    # 2. Sinh viên thực tập (vai trò ThucTapSinh - không có quyền system:backup)
    res_intern = client.post(
        "/api/v1/system/backup",
        headers={"X-User-Email": "vana@example.com"}
    )
    assert res_intern.status_code == 403
    assert "thiếu quyền" in res_intern.json()["detail"].lower()

    # 3. Tài khoản bị khóa
    res_locked = client.post(
        "/api/v1/system/backup",
        headers={"X-User-Email": "locked@example.com"}
    )
    assert res_locked.status_code == 403
    assert "bị khóa" in res_locked.json()["detail"].lower()


def test_concurrency_lock_conflict():
    """Kiểm tra chống xung đột thao tác đồng thời (Concurrency Lock trả về HTTP 409 Conflict)"""
    from services import backup_service
    # Giả lập trạng thái một tiến trình backup đang chiếm giữ khóa
    backup_service._is_backup_running = True
    try:
        response = client.post(
            "/api/v1/system/backup",
            headers={"X-User-Email": "admin@example.com"},
            json={"note": "Thử chạy song song"}
        )
        assert response.status_code == 409
        assert "đang được thực hiện" in response.json()["detail"].lower()
    finally:
        backup_service._is_backup_running = False


def test_get_backups_list_success():
    """Kiểm tra lấy danh sách bản sao lưu và trạng thái scheduler (HTTP 200 OK)"""
    response = client.get(
        "/api/v1/system/backups",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["total_files"] >= 1
    assert data["total_size_bytes"] > 0
    assert "backups" in data
    assert len(data["backups"]) >= 1

    # Kiểm tra cấu trúc item
    first_item = data["backups"][0]
    assert "filename" in first_item
    assert "size_bytes" in first_item
    assert "size_human" in first_item
    assert "download_url" in first_item

    # Kiểm tra trạng thái scheduler
    assert "scheduler" in data
    assert data["scheduler"] is not None
    assert "enabled" in data["scheduler"]
    assert "running" in data["scheduler"]


def test_stream_download_backup_file_success():
    """Kiểm tra stream tải file sao lưu nén (.sql.gz) về client (HTTP 200 OK)"""
    # Lấy danh sách để chọn 1 file
    list_res = client.get(
        "/api/v1/system/backups",
        headers={"X-User-Email": "admin@example.com"}
    )
    filename = list_res.json()["backups"][0]["filename"]

    # Gọi stream download
    dl_res = client.get(
        f"/api/v1/system/backups/{filename}/download",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert dl_res.status_code == 200
    assert dl_res.headers.get("content-type") == "application/gzip"
    assert f'filename="{filename}"' in dl_res.headers.get("content-disposition", "")
    assert int(dl_res.headers.get("content-length", 0)) > 0

    # Kiểm tra stream data giải nén được bằng gzip
    decompressed = gzip.decompress(dl_res.content)
    assert len(decompressed) > 0


def test_stream_download_path_traversal_blocked():
    """Kiểm tra chặn Path Traversal khi cố tình tải file qua tên bất thường"""
    # Gửi tên file chứa ký tự đường dẫn hoặc cố tình leo thư mục
    res_bad = client.get(
        "/api/v1/system/backups/..%2F..%2Fmain.py/download",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert res_bad.status_code in [400, 404]

    res_bad_ext = client.get(
        "/api/v1/system/backups/passwd.txt/download",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert res_bad_ext.status_code == 400


def test_stream_download_not_found():
    """Kiểm tra báo lỗi 404 Not Found nếu file sao lưu không tồn tại"""
    res = client.get(
        "/api/v1/system/backups/backup_non_existent_file_999999.sql.gz/download",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert res.status_code == 404
    assert "không tìm thấy" in res.json()["detail"].lower()


def test_delete_backup_success_and_not_found():
    """Kiểm tra API xóa tệp sao lưu thành công và kiểm tra xóa tệp không tồn tại"""
    # 1. Tạo 1 bản backup riêng để test xóa
    create_res = client.post(
        "/api/v1/system/backup",
        headers={"X-User-Email": "admin@example.com"},
        json={"prefix": "delete_target"}
    )
    assert create_res.status_code == 201, f"Tạo backup thất bại: {create_res.status_code} - {create_res.text}"
    filename = create_res.json()["backup"]["filename"]

    # 2. Xóa tệp
    del_res = client.delete(
        f"/api/v1/system/backups/{filename}",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert del_res.status_code == 200
    assert "thành công" in del_res.json()["message"].lower()

    # 3. Kiểm tra file không còn tồn tại trên đĩa
    backup_dir = get_backup_directory()
    assert not (backup_dir / filename).exists()

    # 4. Thử xóa lại lần 2 -> 404 Not Found
    del_res2 = client.delete(
        f"/api/v1/system/backups/{filename}",
        headers={"X-User-Email": "admin@example.com"}
    )
    assert del_res2.status_code == 404


def test_backup_retention_policy_cleanup():
    """Kiểm tra chính sách dọn dẹp giữ lại tối đa N bản sao lưu (Retention Quota)"""
    backup_dir = get_backup_directory()

    # Tạo 4 file sao lưu giả lập
    test_files = []
    for i in range(4):
        f = backup_dir / f"test_retention_{i:02d}.sql.gz"
        with gzip.open(f, "wt", encoding="utf-8") as gz_f:
            gz_f.write(f"-- dummy backup {i}")
        test_files.append(f)

    try:
        # Gọi cleanup với max_keep = 2
        deleted = cleanup_old_backups(max_keep=2)
        assert deleted >= 2
    finally:
        # Dọn dẹp các tệp test còn sót lại
        for f in test_files:
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass


def test_backup_scheduler_operations():
    """Kiểm tra hoạt động của bộ lập lịch sao lưu tự động định kỳ BackupScheduler"""
    backup_scheduler.stop()
    session = TestSessionLocal()
    try:
        backup_scheduler.initialize(TestSessionLocal, interval_hours=12, enabled=True)
        status = backup_scheduler.get_status()
        assert status["enabled"] is True
        assert status["interval_hours"] == 12

        # Kiểm tra trigger_now
        result = backup_scheduler.trigger_now()
        assert "filename" in result
        assert result["filename"].endswith(".sql.gz")

        # Kiểm tra start & stop mượt mà
        backup_scheduler.start()
        assert backup_scheduler.get_status()["running"] is True
        backup_scheduler.stop()
        assert backup_scheduler.get_status()["running"] is False
    finally:
        session.close()


def test_dump_mysql_to_gzip_mock_execution():
    """Kiểm tra lệnh gọi mysqldump với mock subprocess để xác minh command line arguments và xử lý lỗi"""
    target_gz = get_backup_directory() / "test_mock_mysql.sql.gz"

    # Giả lập thành công
    with patch("services.backup_service.find_mysqldump_binary", return_value="C:\\mysql\\bin\\mysqldump.exe"):
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = MagicMock()
            mock_proc.stdout.read.side_effect = [b"CREATE TABLE test;", b""]
            mock_proc.communicate.return_value = (b"", b"")
            mock_proc.returncode = 0
            mock_popen.return_value = mock_proc

            _dump_mysql_to_gzip(target_gz)

            # Kiểm tra các tham số bắt buộc của mysqldump
            args, _ = mock_popen.call_args
            cmd_list = args[0]
            assert cmd_list[0] == "C:\\mysql\\bin\\mysqldump.exe"
            assert "--single-transaction" in cmd_list
            assert "--quick" in cmd_list
            assert "--skip-lock-tables" in cmd_list

            # File gzip đã được tạo
            assert target_gz.exists()
            with gzip.open(target_gz, "rb") as gz_f:
                content = gz_f.read()
                assert b"CREATE TABLE test;" in content

    # Xóa file test
    if target_gz.exists():
        target_gz.unlink()

    # Giả lập mysqldump trả về lỗi
    with patch("services.backup_service.find_mysqldump_binary", return_value="C:\\mysql\\bin\\mysqldump.exe"):
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = MagicMock()
            mock_proc.stdout.read.side_effect = [b""]
            mock_proc.communicate.return_value = (b"", b"Access denied for user 'root'")
            mock_proc.returncode = 2
            mock_popen.return_value = mock_proc

            with pytest.raises(BackupExecutionError) as exc_info:
                _dump_mysql_to_gzip(target_gz)
            assert "Access denied" in str(exc_info.value)
