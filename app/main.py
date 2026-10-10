from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo các bảng database nếu chưa tồn tại
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
API Quản lý thực tập sinh - Module Báo cáo & Thống kê (Reports & Analytics).
Phát triển bởi: **Nguyễn Văn Hiếu (Backend Developer)**

### Tài liệu dành cho Frontend:
* Toàn bộ API tuân thủ chuẩn RESTful và OpenAPI 3.0.
* Endpoint báo cáo: `GET /api/v1/reports/completion-rate`
* CORS đã được cấu hình cho phép kết nối trực tiếp từ các cổng thông dụng (`localhost:3000`, `localhost:5173`...).
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Cấu hình CORS để Frontend không gặp lỗi Cross-Origin Request Blocked
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router chính
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Hệ thống"])
def root():
    """Kiểm tra thông tin API và điều hướng tài liệu."""
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "author": settings.AUTHOR,
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoint_can_dung": f"{settings.API_V1_STR}/reports/completion-rate"
    }

@app.get("/health", tags=["Hệ thống"])
def health_check():
    """Kiểm tra trạng thái hoạt động của Backend server."""
    return {"status": "healthy"}
