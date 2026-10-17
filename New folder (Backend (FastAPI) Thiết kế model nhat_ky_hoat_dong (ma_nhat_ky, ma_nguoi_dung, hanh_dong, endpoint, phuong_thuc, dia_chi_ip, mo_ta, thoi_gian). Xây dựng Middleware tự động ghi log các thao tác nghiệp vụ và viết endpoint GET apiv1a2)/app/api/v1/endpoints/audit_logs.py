from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.nguoi_dung import NguoiDung
from app.schemas.nhat_ky_hoat_dong import PaginatedAuditLogResponse
from app.services.audit_log_service import audit_log_service

router = APIRouter()


@router.get(
    "/admin/audit-logs",
    response_model=PaginatedAuditLogResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách nhật ký hoạt động hệ thống (Dành cho Admin)",
    description="""
    Truy vấn danh sách nhật ký hoạt động của toàn bộ hệ thống với các tính năng:
    - **Tìm kiếm**: Tìm theo từ khóa trong mô tả, hành động, endpoint, IP, họ tên hoặc username.
    - **Lọc theo ngày**: Lọc theo mốc thời gian bắt đầu (`tu_ngay`) và kết thúc (`den_ngay`).
    - **Lọc người dùng**: Lọc theo `ma_nguoi_dung`.
    - **Lọc hành động & phương thức**: Lọc theo mã hành động (`hanh_dong`) hoặc phương thức (`phuong_thuc`).
    - **Phân trang**: Hỗ trợ `page` (mặc định 1) và `page_size` (mặc định 20, tối đa 100).
    
    Yêu cầu quyền: **Admin** (Quản trị viên hệ thống).
    """,
    responses={
        200: {
            "description": "Lấy danh sách nhật ký hoạt động thành công",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "ma_nhat_ky": 1,
                                "ma_nguoi_dung": 1,
                                "ten_dang_nhap": "admin",
                                "ho_ten": "Quản Trị Viên Hệ Thống",
                                "vai_tro": "Admin",
                                "hanh_dong": "TAO_NGUOI_DUNG",
                                "endpoint": "/api/v1/admin/users",
                                "phuong_thuc": "POST",
                                "dia_chi_ip": "127.0.0.1",
                                "mo_ta": "[201] Admin tạo mới người dùng thuc_tap_sinh_1",
                                "thoi_gian": "2026-10-17T07:30:00"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "page_size": 20,
                        "total_pages": 1
                    }
                }
            }
        },
        401: {"description": "Chưa xác thực hoặc token không hợp lệ"},
        403: {"description": "Không có quyền truy cập (Chỉ Admin mới có quyền)"}
    }
)
async def get_audit_logs(
    request: Request,
    search: Optional[str] = Query(
        None,
        description="Từ khóa tìm kiếm trong mô tả, hành động, endpoint, địa chỉ IP hoặc tên người dùng"
    ),
    tu_ngay: Optional[datetime] = Query(
        None,
        description="Lọc từ ngày (định dạng ISO, ví dụ: 2026-10-01T00:00:00 hoặc 2026-10-01)"
    ),
    den_ngay: Optional[datetime] = Query(
        None,
        description="Lọc đến ngày (định dạng ISO, ví dụ: 2026-10-17T23:59:59 hoặc 2026-10-17)"
    ),
    ma_nguoi_dung: Optional[int] = Query(
        None,
        description="Lọc theo mã ID người dùng thực hiện thao tác"
    ),
    hanh_dong: Optional[str] = Query(
        None,
        description="Lọc theo tên hành động nghiệp vụ (Ví dụ: TAO_NGUOI_DUNG, DANG_NHAP, ...)"
    ),
    phuong_thuc: Optional[str] = Query(
        None,
        description="Lọc theo phương thức HTTP (GET, POST, PUT, DELETE, PATCH)"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Số thứ tự trang cần lấy (bắt đầu từ 1)"
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Số lượng bản ghi trên mỗi trang (tối đa 100)"
    ),
    current_admin: NguoiDung = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # Gắn thông tin ngữ cảnh nghiệp vụ vào request để Middleware có thể ghi nhận
    request.state.audit_action = "XEM_NHAT_KY_HOAT_DONG"
    request.state.audit_description = (
        f"Admin '{current_admin.ten_dang_nhap}' tra cứu danh sách nhật ký hoạt động "
        f"(Trang {page}, bộ lọc search='{search or ''}')"
    )

    items, total, total_pages = audit_log_service.get_audit_logs(
        db=db,
        search=search,
        tu_ngay=tu_ngay,
        den_ngay=den_ngay,
        ma_nguoi_dung=ma_nguoi_dung,
        hanh_dong=hanh_dong,
        phuong_thuc=phuong_thuc,
        page=page,
        page_size=page_size,
    )

    return PaginatedAuditLogResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
