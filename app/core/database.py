
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Cấu hình engine kết nối database
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
=======
"""
Quản lý kết nối Cơ sở dữ liệu và SQLAlchemy Session.
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Xử lý tham số kết nối cho SQLite (cần check_same_thread=False)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    """
    Dependency generator cung cấp DB session cho mỗi request
    và tự động đóng khi request kết thúc.
=======
def get_db() -> Generator:
    """
    Dependency cung cấp database session cho từng request.
    Đảm bảo session luôn được đóng sau khi xử lý xong.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
