from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.nguoi_dung import NguoiDung
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong
from app.middleware.audit_log import AuditLogMiddleware
from app.api.v1.api import api_router


def init_database_data():
    """Khởi tạo cấu trúc bảng và nạp dữ liệu mẫu ban đầu cho mục đích phát triển & kiểm thử"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Tạo tài khoản Admin mặc định nếu chưa tồn tại
        admin_user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "admin").first()
        if not admin_user:
            admin_user = NguoiDung(
                ten_dang_nhap="admin",
                email="admin@hethong.vn",
                mat_khau_hash=get_password_hash("admin123"),
                ho_ten="Quản Trị Viên Hệ Thống",
                vai_tro="Admin",
                trang_thai=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        # 2. Tạo tài khoản Mentor và Thực tập sinh mẫu
        mentor_user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "mentor_hung").first()
        if not mentor_user:
            mentor_user = NguoiDung(
                ten_dang_nhap="mentor_hung",
                email="hung.le@hethong.vn",
                mat_khau_hash=get_password_hash("mentor123"),
                ho_ten="Lê Văn Hùng (Mentor)",
                vai_tro="Mentor",
                trang_thai=True
            )
            db.add(mentor_user)

        intern_user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "intern_hieu").first()
        if not intern_user:
            intern_user = NguoiDung(
                ten_dang_nhap="intern_hieu",
                email="hieu.nguyen@hethong.vn",
                mat_khau_hash=get_password_hash("intern123"),
                ho_ten="Nguyễn Văn Hiếu (Thực tập sinh)",
                vai_tro="ThucTapSinh",
                trang_thai=True
            )
            db.add(intern_user)
        db.commit()

        # 3. Tạo một số bản ghi mẫu cho nhật ký hoạt động nếu bảng đang trống
        count_logs = db.query(NhatKyHoatDong).count()
        if count_logs == 0:
            now = datetime.utcnow()
            sample_logs = [
                NhatKyHoatDong(
                    ma_nguoi_dung=admin_user.ma_nguoi_dung,
                    hanh_dong="DANG_NHAP",
                    endpoint="/api/v1/auth/login",
                    phuong_thuc="POST",
                    dia_chi_ip="192.168.1.100",
                    mo_ta="[200] Quản trị viên đăng nhập vào hệ thống thành công",
                    thoi_gian=now - timedelta(days=2, hours=3)
                ),
                NhatKyHoatDong(
                    ma_nguoi_dung=admin_user.ma_nguoi_dung,
                    hanh_dong="TAO_NGUOI_DUNG",
                    endpoint="/api/v1/admin/users",
                    phuong_thuc="POST",
                    dia_chi_ip="192.168.1.100",
                    mo_ta="[201] Admin tạo tài khoản Mentor Lê Văn Hùng",
                    thoi_gian=now - timedelta(days=2, hours=2)
                ),
                NhatKyHoatDong(
                    ma_nguoi_dung=admin_user.ma_nguoi_dung,
                    hanh_dong="TAO_NGUOI_DUNG",
                    endpoint="/api/v1/admin/users",
                    phuong_thuc="POST",
                    dia_chi_ip="192.168.1.100",
                    mo_ta="[201] Admin tạo tài khoản Thực tập sinh Nguyễn Văn Hiếu",
                    thoi_gian=now - timedelta(days=1, hours=5)
                ),
                NhatKyHoatDong(
                    ma_nguoi_dung=None,
                    hanh_dong="DANG_NHAP_THAT_BAI",
                    endpoint="/api/v1/auth/login",
                    phuong_thuc="POST",
                    dia_chi_ip="113.190.23.45",
                    mo_ta="[400] Sai mật khẩu khi đăng nhập tài khoản guest_01",
                    thoi_gian=now - timedelta(hours=12)
                ),
                NhatKyHoatDong(
                    ma_nguoi_dung=admin_user.ma_nguoi_dung,
                    hanh_dong="XEM_NHAT_KY_HOAT_DONG",
                    endpoint="/api/v1/admin/audit-logs",
                    phuong_thuc="GET",
                    dia_chi_ip="127.0.0.1",
                    mo_ta="[200] Admin truy cập trang kiểm tra lịch sử hoạt động",
                    thoi_gian=now - timedelta(minutes=15)
                ),
            ]
            db.add_all(sample_logs)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động ứng dụng
    init_database_data()
    yield
    # Dọn dẹp tài nguyên khi tắt ứng dụng


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Hệ thống Quản lý Thực tập sinh - Backend API
    **Nhiệm vụ:**
    - Thiết kế Model `nhat_ky_hoat_dong`
    - Xây dựng Middleware tự động ghi log thao tác nghiệp vụ
    - Cung cấp API `GET /api/v1/admin/audit-logs` hỗ trợ tìm kiếm, lọc theo ngày và phân trang
    - Tác giả Backend: **Nguyễn Văn Hiếu**
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Cấu hình CORS để Frontend (HTML/JS Fetch API) kết nối mượt mà
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Kích hoạt Middleware tự động ghi log thao tác nghiệp vụ
app.add_middleware(AuditLogMiddleware)

# 3. Gắn các Router API v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Thông tin chung"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "author": "Nguyễn Văn Hiếu (Backend Developer)",
        "module": "Audit Log & Activity Tracking",
        "docs_url": "/docs",
        "audit_logs_api": "/api/v1/admin/audit-logs",
        "frontend_demo_url": "/demo"
    }


@app.get("/demo", tags=["Giao diện"])
def demo_ui():
    """Phục vụ trang demo HTML cho Frontend dev và Tester kiểm thử trực tiếp"""
    import os
    from fastapi.responses import FileResponse
    demo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_demo", "audit_logs.html")
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    return {"message": "File demo không tìm thấy"}


@app.get("/ping", tags=["Thông tin chung"])
def ping():
    return {"status": "ok", "timestamp": datetime.utcnow()}
