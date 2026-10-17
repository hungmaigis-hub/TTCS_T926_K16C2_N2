"""
Cấu hình hệ thống (Settings & Configuration)
Dự án Quản lý Thực tập sinh (TTCS)
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

import os
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


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

    # Cấu hình CORS để Frontend có thể Fetch API dễ dàng
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Cấu hình Audit Log: giữ chung nếu project có module nhật ký hoạt động
    AUDIT_LOG_EXCLUDE_PATHS: List[str] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/ping",
        "/health",
        "/static",
    ]
    AUDIT_LOG_ALL_METHODS: bool = False

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
