"""
API v1 Router gom tất cả các endpoint của phiên bản 1.
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from fastapi import APIRouter

from app.api.v1.endpoints import notifications, auth, admin, audit_logs, interns, mentors, reports, support_requests

api_router = APIRouter()

# 1. Đăng ký router Notifications: /api/v1/notifications
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications (Thông báo)"]
)

# 2. Đăng ký router Quản trị Admin: /api/v1/admin/users
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin - Quản trị hệ thống"]
)

# 3. Đăng ký router Nhật ký hoạt động: /api/v1/admin/audit-logs
api_router.include_router(
    audit_logs.router,
    tags=["Admin - Nhật ký hoạt động (Audit Logs)"]
)

# 4. Đăng ký router Xác thực Auth: /api/v1/auth
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication (Xác thực)"]
)

# 5. Đăng ký router Hồ sơ Thực tập sinh: /api/v1/interns
api_router.include_router(
    interns.router,
    tags=["Interns - Quản lý Hồ sơ Thực tập sinh"]
)

# 6. Đăng ký router Người hướng dẫn: /api/v1/mentors
api_router.include_router(
    mentors.router,
    tags=["Mentors - Quản lý Danh sách Người hướng dẫn"]
)

# 7. Đăng ký router Báo cáo: /api/v1/reports
api_router.include_router(
    reports.router,
    tags=["Reports - Báo cáo & Thống kê"]
)

# 8. Đăng ký router Yêu cầu hỗ trợ: /api/v1/support-requests
api_router.include_router(
    support_requests.router,
    tags=["Yêu cầu hỗ trợ (Support Requests)"]
)
