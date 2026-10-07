from fastapi import APIRouter
from app.api.v1.endpoints import student_profiles, support_requests

api_router = APIRouter()

# Đăng ký các endpoints của v1
api_router.include_router(
    support_requests.router,
    prefix="/support-requests",
    tags=["Yêu Cầu Hỗ Trợ (Support Requests)"]
)

api_router.include_router(
    student_profiles.router,
    prefix="/students",
    tags=["Hồ Sơ Sinh Viên (Students)"]
)
