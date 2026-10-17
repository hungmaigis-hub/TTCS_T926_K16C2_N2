"""
Cấu hình hệ thống (Settings & Configuration)
Dự án Quản lý Thực tập sinh (TTCS)
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

import os
from typing import List

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings
    SettingsConfigDict = None


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hệ thống Quản lý Thực tập sinh (TTCS)"
    API_V1_STR: str = "/api/v1"
    
    # Cấu hình bảo mật JWT & Bcrypt
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-ttcs-admin-management-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 ngày
    
    # Cấu hình Cơ sở dữ liệu (SQLite mặc định cho phát triển & kiểm thử, có thể đổi sang Postgres/MySQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ql_thuctapsinh.db")
    
    # Danh sách vai trò hợp lệ trong hệ thống
    VALID_ROLES: List[str] = ["Admin", "HR", "Mentor", "ThucTapSinh"]
    
    # Cấu hình CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Cấu hình Audit Log Middleware
    AUDIT_LOG_EXCLUDE_PATHS: List[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/ping",
        "/favicon.ico",
        "/static"
    ]
    AUDIT_LOG_ALL_METHODS: bool = False

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(
            case_sensitive=True,
            env_file=".env",
            extra="ignore"
        )
    else:
        class Config:
            case_sensitive = True
            env_file = ".env"
            extra = "ignore"


settings = Settings()
