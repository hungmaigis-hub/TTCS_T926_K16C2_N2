from fastapi import APIRouter
from app.api.v1.endpoints import interns, mentors

api_router = APIRouter()
api_router.include_router(interns.router)
api_router.include_router(mentors.router)
