from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hệ thống Quản lý Thực tập sinh (Internship Management API)"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./internship_system.db"
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
