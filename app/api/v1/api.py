from fastapi import APIRouter
from app.api.v1.endpoints import notifications, auth

api_router = APIRouter()

# Đăng ký router notifications
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications (Thông báo)"]
)

# Đăng ký router auth
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication (Xác thực)"]
)
