from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.models.mentor import Mentor
from app.schemas.intern import (
    AssignMentorRequest,
    AssignMentorResponse,
    InternResponse,
    MentorResponse,
)

router = APIRouter()


# ── ENDPOINT CHÍNH CỦA NHIỆM VỤ ──────────────────────────────────────────────
@router.patch(
    "/{id}/assign-mentor",
    response_model=AssignMentorResponse,
    status_code=status.HTTP_200_OK,
    summary="Phân công mentor cho thực tập sinh",
    description="Cập nhật trường ma_mentor trong bảng ho_so_thuc_tap dựa theo id thực tập sinh.",
)
def assign_mentor(
    id: int,
    payload: AssignMentorRequest,
    db: Session = Depends(get_db),
):
    """
    Endpoint PATCH /api/v1/interns/{id}/assign-mentor:
    - Kiểm tra hồ sơ thực tập sinh theo id
    - Kiểm tra mã mentor tồn tại và hợp lệ (role Mentor)
    - Cập nhật ma_mentor trong bảng ho_so_thuc_tap
    """
    # 1. Tìm hồ sơ thực tập sinh theo id
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.id == id).first()
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ thực tập sinh có id = {id}",
        )

    # 2. Kiểm tra mentor có tồn tại không
    mentor = db.query(Mentor).filter(Mentor.ma_mentor == payload.ma_mentor).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mentor với mã '{payload.ma_mentor}' không tồn tại trong hệ thống.",
        )

    # 3. Kiểm tra kiểm thử: chỉ người dùng có role Mentor và đang hoạt động mới được chọn
    if mentor.role != "Mentor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Người dùng '{mentor.ho_ten}' không có vai trò Mentor (Role hiện tại: {mentor.role}).",
        )
    if not mentor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mentor '{mentor.ho_ten}' hiện đang không hoạt động.",
        )

    # 4. Cập nhật trường ma_mentor trong ho_so_thuc_tap
    ho_so.ma_mentor = payload.ma_mentor
    db.commit()
    db.refresh(ho_so)

    return AssignMentorResponse(
        message="Gán mentor cho thực tập sinh thành công",
        data=InternResponse.model_validate(ho_so),
    )


# ── CÁC ENDPOINT HỖ TRỢ CHO FRONTEND VÀ TESTER ──────────────────────────────
@router.get(
    "",
    response_model=List[InternResponse],
    summary="Lấy danh sách hồ sơ thực tập sinh",
    description="Frontend sử dụng để hiển thị bảng danh sách thực tập sinh.",
)
def get_interns(db: Session = Depends(get_db)):
    return db.query(HoSoThucTap).all()


@router.get(
    "/mentors",
    response_model=List[MentorResponse],
    summary="Lấy danh sách mentor hợp lệ",
    description="Frontend sử dụng để đổ dữ liệu vào dropdown <select> chọn mentor.",
)
def get_mentors(db: Session = Depends(get_db)):
    return (
        db.query(Mentor)
        .filter(Mentor.role == "Mentor", Mentor.is_active == True)
        .all()
    )


@router.get(
    "/{id}",
    response_model=InternResponse,
    summary="Chi tiết một hồ sơ thực tập sinh",
)
def get_intern_detail(id: int, db: Session = Depends(get_db)):
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.id == id).first()
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ thực tập sinh có id = {id}",
        )
    return ho_so
