import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Tìm .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Lấy thông tin từ .env (có fallback mặc định an toàn)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "intern_management")

# Tạo chuỗi kết nối (hỗ trợ override DATABASE_URL cho môi trường test/sqlite)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# Tạo engine
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL, 
    echo=False,         # echo=True để hiển thị SQL
    pool_pre_ping=True, # kiểm tra kết nối trước khi sử dụng
    connect_args=connect_args
) 

# Tạo session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo base
Base = declarative_base()

# Tạo dependency để sử dụng session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
