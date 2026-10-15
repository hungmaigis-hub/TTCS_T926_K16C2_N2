"""
Module Backup Service
Dịch vụ sao lưu cơ sở dữ liệu định kỳ và thủ công bằng mysqldump ra file nén an toàn (.sql.gz).
Hỗ trợ kiểm tra toàn vẹn (SHA-256), chống tấn công Path Traversal, chống xung đột sao lưu đồng thời (Concurrency Lock)
và hỗ trợ đa môi trường (MySQL mysqldump & SQLite / SQLAlchemy fallback cho môi trường test/dev).
"""
import os
import re
import gzip
import shutil
import hashlib
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

# Cấu hình logging
logger = logging.getLogger("backup_service")
logger.setLevel(logging.INFO)

# Đường dẫn thư mục lưu trữ bản sao lưu
BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BACKUP_DIR = BACKEND_DIR / "backups"

# Khóa Lock để ngăn chặn 2 tiến trình backup chạy đồng thời
_backup_lock = threading.Lock()
_is_backup_running = False

# Ngoại lệ tùy chỉnh
class BackupInProgressError(Exception):
    """Ngoại lệ khi đã có một tiến trình sao lưu đang thực thi"""
    pass

class BackupExecutionError(Exception):
    """Ngoại lệ khi quá trình thực thi lệnh sao lưu gặp lỗi"""
    pass

class BackupSecurityError(Exception):
    """Ngoại lệ khi phát hiện tên tệp không an toàn hoặc có dấu hiệu Path Traversal"""
    pass

class BackupNotFoundError(Exception):
    """Ngoại lệ khi không tìm thấy tệp sao lưu yêu cầu"""
    pass


def get_backup_directory() -> Path:
    """Lấy đường dẫn thư mục backup, tự động tạo nếu chưa tồn tại"""
    env_dir = os.getenv("BACKUP_DIR")
    if env_dir:
        backup_path = Path(env_dir).resolve()
    else:
        backup_path = DEFAULT_BACKUP_DIR
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


def format_bytes(size: int) -> str:
    """Đổi kích thước bytes sang chuỗi định dạng dễ đọc (KB, MB, GB)"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def calculate_sha256(filepath: Path) -> str:
    """Tính mã băm SHA-256 để kiểm tra tính toàn vẹn của tệp"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def validate_backup_filename(filename: str) -> str:
    """
    Xác thực tên tệp sao lưu nhằm ngăn chặn tấn công Path Traversal.
    Chỉ cho phép các ký tự an toàn [a-zA-Z0-9_.-] và phần mở rộng phải là .sql.gz
    """
    if not filename or not isinstance(filename, str):
        raise BackupSecurityError("Tên tệp sao lưu không được để trống")
    
    clean_name = filename.strip()
    if "/" in clean_name or "\\" in clean_name or ".." in clean_name:
        raise BackupSecurityError("Tên tệp sao lưu chứa ký tự đường dẫn không an toàn (Path Traversal)")
    
    if not re.match(r"^[a-zA-Z0-9_\-\.]+\.sql\.gz$", clean_name):
        raise BackupSecurityError("Tên tệp sao lưu không hợp lệ. Chỉ chấp nhận các ký tự an toàn và phần mở rộng .sql.gz")
    
    return clean_name


def find_mysqldump_binary() -> Optional[str]:
    """Tìm đường dẫn tệp thực thi mysqldump từ cấu hình hoặc các vị trí phổ biến"""
    # 1. Từ biến môi trường
    env_path = os.getenv("MYSQLDUMP_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    
    # 2. Từ biến PATH hệ thống
    which_path = shutil.which("mysqldump")
    if which_path:
        return which_path
    
    # 3. Các đường dẫn phổ biến trên Windows
    common_windows_paths = [
        r"C:\xampp\mysql\bin\mysqldump.exe",
        r"C:\laragon\bin\mysql\mysql-5.7.33-winx64\bin\mysqldump.exe",
        r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysqldump.exe",
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
        r"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe",
        r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
    ]
    for p in common_windows_paths:
        if os.path.isfile(p):
            return p
            
    return None


def _dump_mysql_to_gzip(target_gz_file: Path) -> None:
    """Thực thi mysqldump từ MySQL Server và ghi thẳng vào tệp nén gzip"""
    mysqldump_bin = find_mysqldump_binary()
    if not mysqldump_bin:
        raise BackupExecutionError(
            "Không tìm thấy công cụ mysqldump trên hệ thống. "
            "Vui lòng cài đặt MySQL Client hoặc cấu hình biến môi trường MYSQLDUMP_PATH."
        )

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "intern_management")

    cmd = [
        mysqldump_bin,
        f"--host={db_host}",
        f"--port={db_port}",
        f"--user={db_user}",
        "--single-transaction",
        "--quick",
        "--skip-lock-tables",
        "--default-character-set=utf8mb4",
    ]
    if db_password:
        cmd.append(f"--password={db_password}")

    cmd.append(db_name)

    # Khởi chạy mysqldump và stream output nén qua gzip
    temp_gz_file = target_gz_file.with_suffix(".tmp")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        with gzip.open(temp_gz_file, "wb", compresslevel=9) as gz_out:
            while True:
                chunk = proc.stdout.read(65536)
                if not chunk:
                    break
                gz_out.write(chunk)

        _, stderr = proc.communicate()
        if proc.returncode != 0:
            err_msg = stderr.decode("utf-8", errors="ignore")
            # Ẩn mật khẩu nếu có trong stderr
            if db_password and db_password in err_msg:
                err_msg = err_msg.replace(db_password, "******")
            raise BackupExecutionError(f"Lỗi khi thực thi mysqldump (code {proc.returncode}): {err_msg}")

        # Đổi tên tệp tạm thành tệp chính thức
        if target_gz_file.exists():
            target_gz_file.unlink()
        temp_gz_file.rename(target_gz_file)

    except Exception as e:
        if temp_gz_file.exists():
            try:
                temp_gz_file.unlink()
            except Exception:
                pass
        raise e


def _dump_sqlite_or_fallback_to_gzip(db_session: Session, target_gz_file: Path) -> None:
    """Sao lưu database SQLite hoặc fallback bằng SQLAlchemy SQL generator khi không có mysqldump"""
    temp_gz_file = target_gz_file.with_suffix(".tmp")
    try:
        engine = db_session.get_bind()
        connection = engine.connect()

        with gzip.open(temp_gz_file, "wt", encoding="utf-8", compresslevel=9) as gz_out:
            gz_out.write(f"-- ============================================================\n")
            gz_out.write(f"-- Database Backup - Fallback SQL Dumper\n")
            gz_out.write(f"-- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            gz_out.write(f"-- Dialect: {engine.dialect.name}\n")
            gz_out.write(f"-- ============================================================\n\n")

            if engine.dialect.name == "sqlite":
                # Lấy raw sqlite3 connection để sử dụng hàm iterdump() nguyên bản cực kỳ mạnh mẽ
                raw_conn = connection.connection.dbapi_connection
                for line in raw_conn.iterdump():
                    gz_out.write(f"{line}\n")
            else:
                # Quét các bảng và xuất dữ liệu dạng INSERT INTO
                from sqlalchemy import inspect
                inspector = inspect(engine)
                table_names = inspector.get_table_names()

                for tbl in table_names:
                    gz_out.write(f"\n-- Table: {tbl}\n")
                    # Lấy dữ liệu bảng
                    rows = connection.execute(text(f"SELECT * FROM `{tbl}`")).fetchall()
                    if rows:
                        cols = inspector.get_columns(tbl)
                        col_names = [f"`{c['name']}`" for c in cols]
                        for row in rows:
                            vals = []
                            for v in row:
                                if v is None:
                                    vals.append("NULL")
                                elif isinstance(v, (int, float)):
                                    vals.append(str(v))
                                else:
                                    esc_str = str(v).replace("'", "''").replace("\\", "\\\\")
                                    vals.append(f"'{esc_str}'")
                            gz_out.write(f"INSERT INTO `{tbl}` ({', '.join(col_names)}) VALUES ({', '.join(vals)});\n")

        connection.close()

        if target_gz_file.exists():
            target_gz_file.unlink()
        temp_gz_file.rename(target_gz_file)

    except Exception as e:
        if temp_gz_file.exists():
            try:
                temp_gz_file.unlink()
            except Exception:
                pass
        raise BackupExecutionError(f"Lỗi trong quá trình xuất dữ liệu fallback: {str(e)}")


def cleanup_old_backups(max_keep: Optional[int] = None) -> int:
    """
    Dọn dẹp các tệp sao lưu cũ nếu vượt quá số lượng tối đa cấu hình.
    Mặc định giữ lại 30 bản sao lưu mới nhất.
    Trả về số lượng tệp đã xóa.
    """
    if max_keep is None:
        max_keep = int(os.getenv("BACKUP_MAX_KEEP", "30"))
    
    if max_keep <= 0:
        return 0

    backup_dir = get_backup_directory()
    backup_files = []
    for f in backup_dir.glob("*.sql.gz"):
        if f.is_file():
            backup_files.append((f.stat().st_mtime, f))

    # Sắp xếp theo thời gian sửa đổi giảm dần (mới nhất lên đầu)
    backup_files.sort(key=lambda x: x[0], reverse=True)

    deleted_count = 0
    if len(backup_files) > max_keep:
        files_to_remove = backup_files[max_keep:]
        for _, f in files_to_remove:
            try:
                f.unlink()
                deleted_count += 1
                logger.info(f"Đã dọn dẹp bản sao lưu cũ: {f.name}")
            except Exception as e:
                logger.error(f"Không thể xóa tệp sao lưu cũ {f.name}: {e}")

    return deleted_count


def create_backup(
    db: Session,
    note: Optional[str] = None,
    filename_prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Kích hoạt tạo mới một bản sao lưu toàn bộ cơ sở dữ liệu.
    Nén an toàn định dạng .sql.gz, tính checksum SHA-256 và dọn dẹp bản sao lưu cũ.
    Bảo vệ bằng Concurrency Lock để chống xung đột thao tác đồng thời.
    """
    global _is_backup_running

    # Kiểm tra và giữ Lock chống chạy trùng lặp
    acquired = _backup_lock.acquire(blocking=False)
    if not acquired:
        raise BackupInProgressError("Một tiến trình sao lưu khác đang được thực hiện. Vui lòng thử lại sau.")

    if _is_backup_running:
        _backup_lock.release()
        raise BackupInProgressError("Một tiến trình sao lưu khác đang được thực hiện. Vui lòng thử lại sau.")

    _is_backup_running = True
    try:
        backup_dir = get_backup_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        prefix = filename_prefix or "backup_intern_management"
        prefix = re.sub(r"[^a-zA-Z0-9_\-]", "", prefix)
        if not prefix:
            prefix = "backup_intern_management"

        filename = f"{prefix}_{timestamp}.sql.gz"
        target_file = backup_dir / filename
        if target_file.exists():
            micro = datetime.now().strftime("%f")[:4]
            filename = f"{prefix}_{timestamp}_{micro}.sql.gz"
            target_file = backup_dir / filename

        engine = db.get_bind()
        db_type = engine.dialect.name.lower()

        # Kiểm tra phương thức backup phù hợp
        if "sqlite" in db_type:
            _dump_sqlite_or_fallback_to_gzip(db, target_file)
        else:
            # Ưu tiên dùng mysqldump nếu có
            mysqldump_bin = find_mysqldump_binary()
            if mysqldump_bin:
                _dump_mysql_to_gzip(target_file)
            else:
                logger.warning("Không tìm thấy mysqldump binary, sử dụng SQLAlchemy SQL fallback dumper.")
                _dump_sqlite_or_fallback_to_gzip(db, target_file)

        # Kiểm tra tính toàn vẹn của tệp đã tạo
        if not target_file.exists() or target_file.stat().st_size == 0:
            raise BackupExecutionError("Tệp sao lưu tạo ra không hợp lệ hoặc có dung lượng 0 bytes")

        # Kiểm tra tệp có mở được bằng gzip không
        try:
            with gzip.open(target_file, "rb") as gz_test:
                gz_test.read(100)
        except Exception as e:
            raise BackupExecutionError(f"Tệp sao lưu bị hỏng cấu trúc nén gzip: {str(e)}")

        file_stat = target_file.stat()
        file_size = file_stat.st_size
        checksum = calculate_sha256(target_file)
        created_at_dt = datetime.fromtimestamp(file_stat.st_ctime)

        # Dọn dẹp bản backup cũ vượt quá quota
        cleanup_old_backups()

        logger.info(f"Tạo bản sao lưu thành công: {filename} ({format_bytes(file_size)})")

        return {
            "filename": filename,
            "filepath": str(target_file),
            "size_bytes": file_size,
            "size_human": format_bytes(file_size),
            "created_at": created_at_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "checksum_sha256": checksum,
            "download_url": f"/api/v1/system/backups/{filename}/download",
            "note": note
        }

    finally:
        _is_backup_running = False
        _backup_lock.release()


def list_backups() -> Dict[str, Any]:
    """
    Lấy danh sách toàn bộ các tệp sao lưu hiện có trong thư mục sao lưu.
    Sắp xếp thứ tự tệp mới nhất lên đầu.
    """
    backup_dir = get_backup_directory()
    items = []
    total_size = 0

    for file_path in backup_dir.glob("*.sql.gz"):
        if not file_path.is_file():
            continue
        try:
            stat = file_path.stat()
            size = stat.st_size
            total_size += size
            mtime_dt = datetime.fromtimestamp(stat.st_mtime)

            items.append({
                "filename": file_path.name,
                "size_bytes": size,
                "size_human": format_bytes(size),
                "created_at": mtime_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "checksum_sha256": None, # Tính on-demand để tối ưu tốc độ đọc danh sách
                "download_url": f"/api/v1/system/backups/{file_path.name}/download",
                "_mtime": stat.st_mtime
            })
        except Exception as e:
            logger.warning(f"Không thể đọc thông tin tệp sao lưu {file_path.name}: {e}")

    # Sắp xếp tệp mới nhất lên đầu
    items.sort(key=lambda x: x["_mtime"], reverse=True)
    for it in items:
        del it["_mtime"]

    return {
        "total_files": len(items),
        "total_size_bytes": total_size,
        "total_size_human": format_bytes(total_size),
        "backups": items
    }


def get_backup_file_stream(filename: str, chunk_size: int = 65536) -> Tuple[Generator[bytes, None, None], int, Path]:
    """
    Xác thực tên tệp và tạo generator stream tải tệp nén .sql.gz về client.
    Bảo vệ chống tấn công Path Traversal và kiểm tra tệp tồn tại.
    """
    clean_name = validate_backup_filename(filename)
    backup_dir = get_backup_directory()
    file_path = (backup_dir / clean_name).resolve()

    # Kiểm tra tệp phải nằm trong thư mục backup
    if not str(file_path).startswith(str(backup_dir.resolve())):
        raise BackupSecurityError("Truy cập tệp sao lưu bị từ chối do vi phạm quy tắc an toàn thư mục")

    if not file_path.exists() or not file_path.is_file():
        raise BackupNotFoundError(f"Không tìm thấy tệp sao lưu: {clean_name}")

    file_size = file_path.stat().st_size

    def iter_file() -> Generator[bytes, None, None]:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    return iter_file(), file_size, file_path


def delete_backup(filename: str) -> bool:
    """Xóa một tệp sao lưu an toàn"""
    clean_name = validate_backup_filename(filename)
    backup_dir = get_backup_directory()
    file_path = (backup_dir / clean_name).resolve()

    if not str(file_path).startswith(str(backup_dir.resolve())):
        raise BackupSecurityError("Hành vi không an toàn khi xóa tệp")

    if not file_path.exists():
        raise BackupNotFoundError(f"Không tìm thấy tệp sao lưu: {clean_name}")

    file_path.unlink()
    return True


# ==============================================================
# BỘ LÊN LỊCH SAO LƯU TỰ ĐỘNG ĐỊNH KỲ (BACKUP SCHEDULER)
# ==============================================================
class BackupScheduler:
    """
    Quản lý luồng chạy nền sao lưu dữ liệu tự động định kỳ.
    Không làm block FastAPI server, hỗ trợ dừng/khởi động mượt mà và lấy trạng thái.
    """
    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._interval_seconds: int = 24 * 3600  # Mặc định 24 giờ
        self._is_enabled: bool = True
        self._last_run: Optional[datetime] = None
        self._last_status: str = "Chưa kích hoạt"
        self._db_session_factory = None

    def initialize(self, db_session_factory, interval_hours: Optional[float] = None, enabled: Optional[bool] = None):
        """Cấu hình các tham số cho scheduler"""
        self._db_session_factory = db_session_factory

        if enabled is not None:
            self._is_enabled = enabled
        else:
            self._is_enabled = os.getenv("BACKUP_AUTO_ENABLED", "true").lower() in ["true", "1", "yes"]

        if interval_hours is not None:
            self._interval_seconds = int(interval_hours * 3600)
        else:
            hours = float(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
            self._interval_seconds = int(hours * 3600)

    def start(self):
        """Bắt đầu chạy luồng scheduler định kỳ"""
        if not self._is_enabled:
            self._last_status = "Đã tắt tính năng tự động sao lưu"
            logger.info("BackupScheduler: Tính năng sao lưu tự động đã bị tắt trong cấu hình.")
            return

        if self._thread and self._thread.is_alive():
            logger.warning("BackupScheduler đã đang hoạt động.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="BackupSchedulerThread", daemon=True)
        self._thread.start()
        self._last_status = "Đang chạy"
        logger.info(f"BackupScheduler đã bắt đầu, chu kỳ sao lưu: {self._interval_seconds} giây.")

    def stop(self):
        """Dừng luồng scheduler"""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=3)
            self._last_status = "Đã dừng"
            logger.info("BackupScheduler đã dừng.")

    def trigger_now(self) -> Dict[str, Any]:
        """Kích hoạt sao lưu ngay lập tức thông qua session CSDL"""
        if not self._db_session_factory:
            raise RuntimeError("Database session factory chưa được nạp cho BackupScheduler")

        db = self._db_session_factory()
        try:
            result = create_backup(db, note="Sao lưu thủ công kích hoạt từ Scheduler")
            self._last_run = datetime.now()
            self._last_status = "Sao lưu thành công"
            return result
        except Exception as e:
            self._last_status = f"Lỗi sao lưu: {str(e)}"
            raise e
        finally:
            db.close()

    def _run_loop(self):
        """Vòng lặp chạy nền định kỳ"""
        # Đợi một khoảng thời gian ban đầu để hệ thống ổn định khi khởi động (ví dụ 60s, hoặc có thể cấu hình)
        initial_wait = min(60, self._interval_seconds)
        if self._stop_event.wait(timeout=initial_wait):
            return

        while not self._stop_event.is_set():
            logger.info("BackupScheduler: Bắt đầu tiến trình sao lưu tự động định kỳ...")
            try:
                if self._db_session_factory:
                    db = self._db_session_factory()
                    try:
                        create_backup(db, note="Sao lưu tự động định kỳ theo lịch trình")
                        self._last_run = datetime.now()
                        self._last_status = "Sao lưu định kỳ thành công"
                    finally:
                        db.close()
            except Exception as e:
                self._last_status = f"Lỗi sao lưu định kỳ: {str(e)}"
                logger.error(f"BackupScheduler gặp lỗi: {e}")

            # Đợi chu kỳ tiếp theo
            if self._stop_event.wait(timeout=self._interval_seconds):
                break

    def get_status(self) -> Dict[str, Any]:
        """Lấy thông tin trạng thái hiện tại của bộ lập lịch"""
        return {
            "enabled": self._is_enabled,
            "running": bool(self._thread and self._thread.is_alive()),
            "interval_hours": round(self._interval_seconds / 3600, 2),
            "last_run": self._last_run.strftime("%Y-%m-%d %H:%M:%S") if self._last_run else None,
            "status": self._last_status,
            "backup_dir": str(get_backup_directory())
        }

# Khởi tạo singleton scheduler
backup_scheduler = BackupScheduler()
