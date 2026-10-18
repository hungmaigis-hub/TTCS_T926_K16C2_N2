"""
Kết nối CSDL sử dụng SQLAlchemy.
Cấu hình thông qua biến môi trường.
Đồng bộ với app.core.database để dùng chung Base registry.
"""
from app.core.database import Base, engine, SessionLocal, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
