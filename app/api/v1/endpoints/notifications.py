from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.nguoi_dung import NguoiDung
from app.models.thong_bao import ThongBao
from app.crud.crud_thong_bao import crud_thong_bao
from app.schemas.thong_bao import (
    ThongBaoResponse,
    ThongBaoListResponse,
    ThongBaoCreate,
    ThongBaoUpdate
)

router = APIRouter()


@router.get(
    "/my",
    response_model=ThongBaoListResponse,
    summary="Lấy danh sách thông báo cá nhân",
    description="Lấy danh sách thông báo của người dùng hiện tại (thực tập sinh, mentor, HR). Sắp xếp từ mới nhất đến cũ nhất."
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
    unread_only: bool = Query(False, description="Chỉ lấy các thông báo chưa đọc"),
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua (phân trang)"),
    limit: int = Query(50, ge=1, le=100, description="Số lượng bản ghi tối đa lấy về")
) -> Any:
    """
    Endpoint GET /api/v1/notifications/my
    - Lấy thông báo theo ma_nguoi_nhan của current_user
    - Trả về danh sách thông báo, tổng số lượng và số lượng chưa đọc (phục vụ hiển thị badge số lượng)
    """
    notifications = crud_thong_bao.get_multi_by_user(
        db=db,
        ma_nguoi_nhan=current_user.ma_nguoi_dung,
        unread_only=unread_only,
        skip=skip,
        limit=limit
    )
    total = crud_thong_bao.count_by_user(
        db=db,
        ma_nguoi_nhan=current_user.ma_nguoi_dung,
        unread_only=unread_only
    )
    unread_count = crud_thong_bao.count_unread_by_user(
        db=db,
        ma_nguoi_nhan=current_user.ma_nguoi_dung
    )

    return ThongBaoListResponse(
        items=notifications,
        total=total,
        unread_count=unread_count,
        limit=limit,
        skip=skip
    )


@router.patch(
    "/{id}/read",
    response_model=ThongBaoResponse,
    summary="Đánh dấu thông báo đã đọc",
    description="Cập nhật trạng thái `da_doc = True` cho thông báo có ID tương ứng. Kiểm tra quyền sở hữu của người nhận."
)
def mark_notification_as_read(
    id: int = Path(..., ge=1, description="Mã thông báo (ma_thong_bao)"),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
) -> Any:
    """
    Endpoint PATCH /api/v1/notifications/{id}/read
    - Kiểm tra thông báo có tồn tại hay không -> 404 Not Found
    - Kiểm tra thông báo có thuộc về người dùng hiện tại không -> 403 Forbidden
    - Đánh dấu da_doc = True và lưu vào cơ sở dữ liệu
    """
    notification = crud_thong_bao.get_by_id(db=db, ma_thong_bao=id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy thông báo với mã {id}"
        )

    # Kiểm tra quyền sở hữu
    if notification.ma_nguoi_nhan != current_user.ma_nguoi_dung:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập hoặc chỉnh sửa thông báo này"
        )

    # Nếu đã đọc rồi thì vẫn trả về kết quả thành công mà không lỗi
    if not notification.da_doc:
        notification = crud_thong_bao.mark_as_read(db=db, thong_bao=notification)

    return notification


@router.patch(
    "/read-all",
    summary="Đánh dấu tất cả thông báo cá nhân là đã đọc",
    description="Tiện ích hỗ trợ Frontend khi người dùng bấm 'Đánh dấu tất cả là đã đọc'"
)
def mark_all_my_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
) -> Any:
    updated_count = crud_thong_bao.mark_all_as_read(
        db=db,
        ma_nguoi_nhan=current_user.ma_nguoi_dung
    )
    return {
        "success": True,
        "message": f"Đã đánh dấu {updated_count} thông báo là đã đọc",
        "updated_count": updated_count
    }


@router.post(
    "",
    response_model=ThongBaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo thông báo mới (Hệ thống/Admin/Mentor)",
    description="Tạo thông báo gửi tới một người dùng cụ thể (dành cho API nội bộ hoặc tích hợp các sự kiện khác)."
)
def create_notification(
    obj_in: ThongBaoCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
) -> Any:
    # Cho phép tạo thông báo để phục vụ hệ thống và test
    notification = crud_thong_bao.create(db=db, obj_in=obj_in)
    return notification
