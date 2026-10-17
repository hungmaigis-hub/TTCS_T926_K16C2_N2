"""
API v1 Router gom tất cả các endpoint của phiên bản 1.
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from fastapi import APIRouter
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router

api_router = APIRouter()

# Đăng ký router Quản trị Admin: POST /api/v1/admin/users
api_router.include_router(admin_router, prefix="/admin", tags=["Admin - Quản trị hệ thống"])

# Đăng ký router Xác thực Auth: POST /api/v1/auth/login
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication - Xác thực"])
