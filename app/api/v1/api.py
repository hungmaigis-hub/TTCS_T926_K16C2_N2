from fastapi import APIRouter
from app.api.v1.endpoints import interns, mentors, reports, support_requests

api_router = APIRouter()
api_router.include_router(interns.router)
api_router.include_router(mentors.router)
api_router.include_router(reports.router)
api_router.include_router(support_requests.router)
