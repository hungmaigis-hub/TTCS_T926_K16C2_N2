from typing import List, Optional
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.intern import (
    AssignMentorRequest,
    AssignMentorResponse,
    HoSoThucTapResponse,
    HoSoThucTapCreate
)
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.services.intern_service import InternService

router = APIRouter(prefix="/interns", tags=["Interns - Quản lý Hồ sơ Thực tập sinh"])

@router.patch(
    "/{id}/assign-mentor",
    response_model=AssignMentorResponse,
    status_code=status.HTTP_200_OK,
    summary="Phân công / Gán Mentor cho thực tập sinh (Nhiệm vụ: Nguyễn Văn Hiếu)",
    description=(
        "Endpoint này cập nhật trường `ma_mentor` trong bảng `ho_so_thuc_tap` cho thực tập sinh có `id` tương ứng.\n"
        "- **Validation:**\n"
        "  + Kiểm tra sự tồn tại của hồ sơ thực tập sinh (`id`).\n"
        "  + Kiểm tra sự tồn tại và tính khả dụng của Mentor (`ma_mentor`).\n"
        "  + Kiểm tra giới hạn số lượng sinh viên mà Mentor đang hướng dẫn.\n"
        "- **Hỗ trợ:**\n"
        "  + Nếu truyền `ma_mentor` là số nguyên hợp lệ: gán mentor và cập nhật thời điểm gán.\n"
        "  + Nếu truyền `ma_mentor: null`: hủy gán mentor cho thực tập sinh."
    )
)
def assign_mentor(
    id: int = Path(..., title="ID của Thực tập sinh trong ho_so_thuc_tap", example=1),
    payload: AssignMentorRequest = ...,
    db: Session = Depends(get_db)
):
    """
    API PATCH /api/v1/interns/{id}/assign-mentor
    Cập nhật trường ma_mentor trong ho_so_thuc_tap
    """
    updated_intern = InternService.assign_mentor(db=db, intern_id=id, request=payload)
    
    action_msg = "Phân công mentor thành công" if payload.ma_mentor is not None else "Đã hủy phân công mentor thành công"
    return AssignMentorResponse(
        success=True,
        message=action_msg,
        data=updated_intern
    )

@router.get(
    "/{id}",
    response_model=HoSoThucTapResponse,
    summary="Xem chi tiết hồ sơ thực tập sinh theo ID",
    description="Trả về thông tin chi tiết của 1 hồ sơ thực tập sinh kèm thông tin Mentor đã gán (nếu có)."
)
def get_intern_detail(
    id: int = Path(..., title="ID của Thực tập sinh", example=1),
    db: Session = Depends(get_db)
):
    return InternService.get_intern_by_id(db=db, intern_id=id)

@router.get(
    "",
    response_model=List[HoSoThucTapResponse],
    summary="Lấy danh sách tất cả hồ sơ thực tập sinh",
    description="Hỗ trợ Frontend hiển thị bảng danh sách thực tập sinh để chọn gán mentor."
)
def list_interns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return InternService.get_all_interns(db=db, skip=skip, limit=limit)

@router.post(
    "",
    response_model=HoSoThucTapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới hồ sơ thực tập sinh (hỗ trợ test)",
    description="Tạo nhanh 1 hồ sơ thực tập sinh mới vào hệ thống."
)
def create_intern(
    payload: HoSoThucTapCreate,
    db: Session = Depends(get_db)
):
    new_intern = HoSoThucTap(
        ma_sv=payload.ma_sv,
        ho_ten=payload.ho_ten,
        email=payload.email,
        so_dien_thoai=payload.so_dien_thoai,
        truong_hoc=payload.truong_hoc,
        chuyen_nganh=payload.chuyen_nganh,
        ma_mentor=payload.ma_mentor,
        trang_thai=payload.trang_thai,
        ngay_bat_dau=payload.ngay_bat_dau,
        ngay_ket_thuc=payload.ngay_ket_thuc
    )
    db.add(new_intern)
    db.commit()
    db.refresh(new_intern)
    return new_intern
