from typing import Generator
from app.core.database import SessionLocal


def get_db() -> Generator:
    """
    Dependency lấy phiên làm việc (Session) cơ sở dữ liệu SQLAlchemy.
    Tự động đóng session sau khi xử lý xong request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
