"""
Entry point của ứng dụng FastAPI – Intern Management System.

Chạy development server:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Truy cập Swagger UI:
    http://localhost:8000/docs

Truy cập ReDoc:
    http://localhost:8000/redoc
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers.intern_router import router as intern_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.support_requests import router as support_requests_router

# ============================================================
# Logging config
# ============================================================
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ============================================================
# Lifespan – khởi động / tắt
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Khởi tạo tài nguyên khi server bắt đầu,
    dọn dẹp khi server dừng.
    """
    logger.info("🚀 Khởi động %s v%s ...", settings.APP_NAME, settings.APP_VERSION)

    # Tự động tạo bảng nếu chưa tồn tại (dev mode)
    # Production nên dùng Alembic migrate
    if settings.DEBUG:
        logger.info("DEBUG mode: tạo bảng CSDL nếu chưa có ...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ CSDL sẵn sàng.")

    yield  # ← server chạy ở đây

    logger.info("🛑 Đang dừng server ...")


# ============================================================
# Khởi tạo FastAPI app
# ============================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Intern Management System – Backend API

Hệ thống quản lý thực tập sinh xây dựng với **FastAPI** + **MySQL**.

### Modules chính
| Module | Mô tả |
|--------|-------|
| **Interns** | Quản lý hồ sơ thực tập sinh, gán Mentor |
| **Users**   | Quản lý người dùng (HR, Mentor, Intern, Admin) |

### Xác thực
> Hiện tại API chưa yêu cầu xác thực JWT (sẽ bổ sung ở v2).  
> Các endpoint nhạy cảm sẽ yêu cầu token Bearer.

### Người phát triển
- **Backend**: Nguyễn Văn Hiếu  
- **Nhóm**: TTCS_T926_K16C2_N2
""",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================
# CORS Middleware – cho phép frontend gọi API
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React dev server
        "http://localhost:5173",     # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",                         # TODO: giới hạn lại trên production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Global exception handler – trả về JSON đồng nhất
# ============================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s: %s", request.url, exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Đã xảy ra lỗi không xác định. Vui lòng liên hệ quản trị viên.",
        },
    )


# ============================================================
# Include routers
# ============================================================
app.include_router(intern_router)
app.include_router(reports_router, prefix="/api/v1")
app.include_router(support_requests_router, prefix="/api/v1")


# ============================================================
# Health check endpoint
# ============================================================
@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Kiểm tra trạng thái server.",
)
def health_check():
    """Endpoint kiểm tra server đang chạy."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get(
    "/",
    tags=["System"],
    summary="Root",
    include_in_schema=False,
)
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}",
        "docs": "/docs",
        "redoc": "/redoc",
    }
