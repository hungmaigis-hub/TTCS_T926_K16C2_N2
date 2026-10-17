import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hệ thống Quản lý Thực tập sinh"
    API_V1_STR: str = "/api/v1"
    
    # Cấu hình Database (Mặc định dùng SQLite cục bộ, có thể đổi sang PostgreSQL)
    DATABASE_URL: str = "sqlite:///./audit_logs_system.db"
    
    # Cấu hình JWT Token & Bảo mật
    SECRET_KEY: str = "super_secret_jwt_key_nguyen_van_hieu_audit_log_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 ngày
    
    # Cấu hình Middleware Audit Log
    # Các endpoint bỏ qua không ghi log để tránh spam (swagger, openapi, static, health)
    AUDIT_LOG_EXCLUDE_PATHS: List[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/ping",
        "/health",
        "/static",
    ]
    
    # Chế độ ghi log: nếu True thì ghi log các method thay đổi dữ liệu (POST, PUT, DELETE, PATCH)
    # và các GET quan trọng (như GET audit-logs hoặc đăng nhập)
    AUDIT_LOG_ALL_METHODS: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
