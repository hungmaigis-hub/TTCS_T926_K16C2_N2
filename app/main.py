from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import Base, engine
from app.api.api import api_router
import app.models  # Đảm bảo nạp các model trước khi create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo bảng cơ sở dữ liệu nếu chưa tồn tại
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Hệ thống Quản lý Thực tập sinh - Backend API (FastAPI)
    **Phụ trách phát triển Backend**: Nguyễn Văn Hiếu
    
    ### Chức năng chính:
    * **Model**: `hop_dong` (Lưu thông tin hợp đồng thực tập sinh)
    * **Endpoint**: `POST /api/v1/contracts` (Lưu `ma_so_hop_dong`, `ngay_ky`, `muc_phu_cap_co_ban`, `ma_ho_so`, `file_url`)
    * **Quản lý Hợp đồng**: Danh sách, Chi tiết, Xác nhận hợp đồng (dành cho Thực tập sinh & HR).
    * Hỗ trợ CORS đầy đủ cho Frontend kết nối.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Cấu hình CORS để Frontend (mấy ae forten) gọi API mượt mà không bị lỗi chặn CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router API v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "message": "Hệ thống Quản lý Thực tập sinh API đang hoạt động bình thường!",
        "author": "Nguyễn Văn Hiếu (Backend Developer)",
        "docs": "/docs",
        "api_endpoint": f"{settings.API_V1_STR}/contracts"
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "service": "internship-management-api"}
