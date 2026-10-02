import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Mặc định sử dụng SQLite để chạy ngay không cần setup phức tạp, có thể ghi đè qua DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./intern_management.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency cung cấp db session cho các router."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
