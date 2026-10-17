from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
import app.models  # Đảm bảo các models được load để SQLAlchemy tạo bảng

# Tự động tạo các bảng trong cơ sở dữ liệu nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API cho Module Quản lý Thông báo thực tập sinh (Thực hiện bởi: Nguyễn Văn Hiếu)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Cấu hình CORS Middleware để Frontend có thể gọi API mà không bị chặn
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Đăng ký API router v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "author": "Nguyễn Văn Hiếu",
        "role": "Backend Developer",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Service is healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
