from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.notifications import router as notifications_router

api_router = APIRouter()

api_router.include_router(admin_router, prefix="/admin", tags=["Admin - Quản trị hệ thống"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication - Xác thực"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications - Thông báo"])
