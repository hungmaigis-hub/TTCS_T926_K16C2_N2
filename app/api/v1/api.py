from fastapi import APIRouter
from app.api.v1.endpoints.support_requests import router as support_requests_router

api_router = APIRouter()

# Endpoint tiếp nhận yêu cầu hỗ trợ sinh viên: POST /api/v1/support-requests
api_router.include_router(
    support_requests_router,
    prefix="/support-requests",
    tags=["Yêu cầu hỗ trợ (Support Requests)"]
)
