import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Tìm .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# lấy thông tin từ .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# tạo chuỗi kết nối
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# tạo engine
engine = create_engine(
    DATABASE_URL, 
    echo=False,# echo=True để hiển thị SQL
    pool_pre_ping=True # kiểm tra kết nối trước khi sử dụng
    ) 
# tạo session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# tạo base
Base = declarative_base()

# tạo dependency để sử dụng session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()