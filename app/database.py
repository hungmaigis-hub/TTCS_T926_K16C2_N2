"""
Kết nối CSDL sử dụng SQLAlchemy + MySQL (PyMySQL driver).
Cấu hình thông qua biến môi trường trong file .env
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# -----------------------------------------------------------
# Tạo engine kết nối MySQL
# -----------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,          # log SQL khi DEBUG
    pool_pre_ping=True,             # kiểm tra kết nối trước mỗi request
    pool_recycle=3600,              # recycle sau 1 giờ (tránh MySQL "gone away")
    pool_size=10,
    max_overflow=20,
)

# -----------------------------------------------------------
# Session factory
# -----------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------------------------------------
# Base class cho tất cả ORM model
# -----------------------------------------------------------
Base = declarative_base()


# -----------------------------------------------------------
# Dependency – dùng trong các router FastAPI
# -----------------------------------------------------------
def get_db():
    """
    Tạo session DB cho mỗi request, tự động đóng khi xong.
    Sử dụng: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
