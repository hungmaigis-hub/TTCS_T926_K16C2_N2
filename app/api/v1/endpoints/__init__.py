from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router

__all__ = ["admin_router", "auth_router"]
