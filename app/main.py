"""
Ứng dụng FastAPI chính (Main Application)
Dự án: Hệ thống Quản lý Thực tập sinh (TTCS)
Phân hệ: Quản trị hệ thống - Quản lý tài khoản & phân quyền
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.nguoi_dung import NguoiDung
from app.schemas.user import UserRole


def seed_initial_admin():
    db = SessionLocal()
    try:
        admin_user = db.query(NguoiDung).filter(
            (NguoiDung.ten_dang_nhap == "admin") | (NguoiDung.vai_tro == UserRole.ADMIN.value)
        ).first()

        if not admin_user:
            default_admin = NguoiDung(
                ten_dang_nhap="admin",
                email="admin@ttcs.edu.vn",
                mat_khau_hash=hash_password("Admin@123456"),
                ho_ten="Quản Trị Viên Hệ Thống",
                vai_tro=UserRole.ADMIN.value,
                trang_thai=True,
            )
            db.add(default_admin)
            db.commit()
            print("[INFO] Đã khởi tạo tài khoản Admin mặc định (Username: 'admin' / Mật khẩu: 'Admin@123456')")
    except Exception as e:
        db.rollback()
        print(f"[WARNING] Không thể tạo tài khoản admin mặc định: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_initial_admin()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Hệ sinh thái API Backend cho Dự án Quản lý Thực tập sinh (TTCS).
    
    ### Chức năng chính:
    - POST /api/v1/admin/users: Admin tạo tài khoản người dùng mới.
    - POST /api/v1/auth/login: Đăng nhập lấy JWT token.
    - GET /api/v1/notifications/my: Lấy thông báo cá nhân.
    - PATCH /api/v1/notifications/{id}/read: Đánh dấu đã đọc.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Hệ thống"])
def root():
    return {
        "status": "success",
        "message": "Chào mừng đến với Hệ thống Quản lý Thực tập sinh (TTCS) API",
        "author": "Nguyễn Văn Hiếu (Backend Developer)",
        "docs_url": "/docs",
        "api_v1": "/api/v1",
    }


@app.get("/health", tags=["Hệ thống"])
def health_check():
    return {"status": "healthy", "database": "connected"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg")
        errors.append({"field": field, "message": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "message": "Dữ liệu gửi lên không hợp lệ hoặc thiếu trường bắt buộc (hoặc vai trò không hợp lệ).",
        },
    )
