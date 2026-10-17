from fastapi import APIRouter
from app.api.v1.endpoints import audit_logs, auth, users

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Xác thực (Auth)"])
api_router.include_router(users.router, tags=["Quản trị Người dùng (Users)"])
api_router.include_router(audit_logs.router, tags=["Quản trị Nhật ký Hoạt động (Audit Logs)"])
