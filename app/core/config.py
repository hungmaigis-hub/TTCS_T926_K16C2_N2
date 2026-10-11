from pydantic_settings import BaseSettings
from typing import List
import os

class Settings:
    PROJECT_NAME: str = "Hệ Thống Quản Lý Thực Tập Sinh (TTCS T926 K16C2 N2)"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./internship_system.db")
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    DEVELOPER_NAME: str = "Nguyễn Văn Hiếu"
    FEATURE_TASK: str = "PATCH /api/v1/interns/{id}/assign-mentor"

settings = Settings()
