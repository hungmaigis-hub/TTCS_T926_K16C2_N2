
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hệ thống Quản lý Thực tập sinh - Module Thông báo (Notification Service)"
    API_V1_STR: str = "/api/v1"
    
    # JWT Settings
    SECRET_KEY: str = "super-secret-key-change-in-production-09876543210!@#$%"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 ngày
    
    # Database Settings
    # Mặc định sử dụng SQLite cho môi trường dev & test, có thể override qua biến môi trường sang PostgreSQL/MySQL
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # CORS Origins
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

    class Config:
        case_sensitive = True
        env_file = ".env"
=======
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
    
    # Cấu hình CORS để Frontend (Lê Văn Hùng) có thể Fetch API dễ dàng
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True


settings = Settings()
