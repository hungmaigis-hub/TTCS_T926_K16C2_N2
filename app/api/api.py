from fastapi import APIRouter
from app.api.endpoints import contracts

api_router = APIRouter()

# Đăng ký router contracts -> đường dẫn đầy đủ: /api/v1/contracts
api_router.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["Contracts (Quản lý Hợp đồng)"]
)
