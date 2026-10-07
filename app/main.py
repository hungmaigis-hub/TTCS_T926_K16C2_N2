from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo CSDL & seed dữ liệu mẫu khi app khởi động
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Hệ Thống Quản Lý Thực Tập Sinh - API Tiếp Nhận Yêu Cầu Hỗ Trợ
    
    ### Thông tin phụ trách:
    - **Backend Developer:** Nguyễn Văn Hiếu
    - **Nhiệm vụ:** Xây dựng API và CSDL tiếp nhận yêu cầu hỗ trợ từ sinh viên / thực tập sinh.
    - **Mô hình hỗ trợ:**
      - Tiếp nhận loại yêu cầu: giấy tờ, chứng nhận, kỹ thuật, phụ cấp,...
      - Tự động gán trạng thái `ChoXuLy` và thời gian tạo `ngay_tao`.
      - Tự động kiểm tra tính hợp lệ của mã hồ sơ sinh viên (`ma_ho_so`).
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Cấu hình CORS để Frontend (React, Vue, Vite,...) gọi API không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn router API v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Hệ Thống"])
def root():
    return {
        "message": "Chào mừng đến với API Quản lý Yêu cầu Hỗ trợ Thực tập sinh",
        "author": "Nguyễn Văn Hiếu (Backend Developer)",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["Hệ Thống"])
def health_check():
    return {"status": "ok", "author": "Nguyễn Văn Hiếu"}
