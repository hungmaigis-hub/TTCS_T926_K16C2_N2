"""
Ứng dụng FastAPI chính (Main Application)
Dự án: Hệ thống Quản lý Thực tập sinh (TTCS)
Phụ trách Backend: Nguyễn Văn Hiếu
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.nguoi_dung import NguoiDung
from app.models.thong_bao import ThongBao
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong
from app.schemas.user import UserRole
from app.api.v1.api import api_router
from app.routers.intern_router import router as intern_router
from app.middleware.audit_log import AuditLogMiddleware


def seed_initial_admin():
    """
    Tự động khởi tạo tài khoản Quản trị viên (Admin) mặc định nếu hệ thống chưa có.
    """
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
                trang_thai=True
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
    # Khởi tạo bảng cơ sở dữ liệu nếu chưa tồn tại
    Base.metadata.create_all(bind=engine)
    # Khởi tạo tài khoản Admin mặc định
    seed_initial_admin()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Hệ sinh thái API Backend cho Dự án Quản lý Thực tập sinh (TTCS).
    
    ### Chức năng Sprint 4:
    - **Notifications**: Thông báo cá nhân, đánh dấu đã đọc.
    - **Admin Users**: Quản trị tạo tài khoản người dùng và phân vai trò.
    - **Audit Logs**: Ghi log tự động và truy vấn nhật ký hoạt động hệ thống.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Audit Log Middleware (Tự động ghi lại các thao tác nghiệp vụ)
app.add_middleware(AuditLogMiddleware)

# 3. Đăng ký API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(intern_router)


@app.get("/", tags=["Hệ thống"])
def root():
    return {
        "status": "success",
        "message": "Chào mừng đến với Hệ thống Quản lý Thực tập sinh (TTCS) API",
        "author": "Nguyễn Văn Hiếu (Backend Developer)",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health", tags=["Hệ thống"])
def health_check():
    return {"status": "ok", "message": "Service is healthy"}


@app.get("/ping", tags=["Hệ thống"])
def ping():
    return {"ping": "pong"}


# Custom Exception Handler cho RequestValidationError để format thông báo lỗi thân thiện cho Frontend & Tester
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
            "message": "Dữ liệu gửi lên không hợp lệ hoặc thiếu trường bắt buộc (hoặc vai trò không hợp lệ)."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
