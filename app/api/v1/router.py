from fastapi import APIRouter
from app.api.v1.endpoints.interns import router as interns_router

api_router = APIRouter()
api_router.include_router(interns_router, prefix="/interns", tags=["Interns - Quản lý thực tập sinh"])
