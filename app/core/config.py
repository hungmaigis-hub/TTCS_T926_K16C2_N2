from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hệ thống Quản lý Thực tập sinh"
    API_V1_STR: str = "/api/v1"
    AUTHOR: str = "Nguyễn Văn Hiếu (Backend Developer)"
    
    # Database configuration (Mặc định SQLite cục bộ, có thể override sang PostgreSQL/MySQL)
    DATABASE_URL: str = "sqlite:///./internship_management.db"
    
    # Cấu hình CORS để cho phép Frontend kết nối mượt mà từ localhost
    BACKEND_CORS_ORIGINS: List[str] = [
        "*",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    class Config:
        case_sensitive = True

settings = Settings()
