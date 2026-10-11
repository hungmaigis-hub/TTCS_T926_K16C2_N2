from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.models import Mentor, HoSoThucTap

# Tự động tạo bảng trong DB nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "### Dự án Quản lý Thực tập sinh - Phân hệ Backend (FastAPI)\n\n"
        "- **Thành viên thực hiện:** Nguyễn Văn Hiếu (Backend Developer)\n"
        "- **Nhiệm vụ chính:** Endpoint `PATCH /api/v1/interns/{id}/assign-mentor` cập nhật trường `ma_mentor` trong `ho_so_thuc_tap`.\n"
        "- **Hỗ trợ đồng đội Frontend:** Cung cấp sẵn API danh sách Thực tập sinh, danh sách Mentor và Swagger tương tác trực tiếp."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS mở rộng cho phép frontend (React/Vue/HTML) kết nối không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các route của API V1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Hệ thống"])
def root():
    return {
        "message": "Chào mừng đến với Hệ thống Quản lý Thực tập sinh - TTCS T926 K16C2 N2",
        "developer": settings.DEVELOPER_NAME,
        "feature_endpoint": "PATCH /api/v1/interns/{id}/assign-mentor",
        "swagger_docs": "/docs",
        "redoc_docs": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
