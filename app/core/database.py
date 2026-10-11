from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Cấu hình engine kết nối SQLite (hoặc Postgres nếu cấu hình qua DATABASE_URL)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency cung cấp session DB cho từng request FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
