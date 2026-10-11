from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.mentor import Mentor
from app.schemas.mentor import MentorResponse, MentorCreate
from app.services.intern_service import InternService

router = APIRouter(prefix="/mentors", tags=["Mentors - Quản lý Danh sách Người hướng dẫn"])

@router.get(
    "",
    response_model=List[MentorResponse],
    summary="Lấy danh sách tất cả Mentor",
    description="Hỗ trợ Frontend hiển thị danh sách / dropdown để HR chọn Mentor khi phân công thực tập sinh."
)
def list_mentors(db: Session = Depends(get_db)):
    return InternService.get_all_mentors(db=db)

@router.post(
    "",
    response_model=MentorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm mới Mentor (hỗ trợ test)",
    description="Thêm nhanh một Mentor vào hệ thống để thử nghiệm chức năng phân công."
)
def create_mentor(payload: MentorCreate, db: Session = Depends(get_db)):
    mentor = Mentor(
        ma_can_bo=payload.ma_can_bo,
        ho_ten=payload.ho_ten,
        email=payload.email,
        so_dien_thoai=payload.so_dien_thoai,
        phong_ban=payload.phong_ban,
        chuc_vu=payload.chuc_vu,
        chuyen_mon=payload.chuyen_mon,
        so_luong_toi_da=payload.so_luong_toi_da,
        trang_thai=payload.trang_thai
    )
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    mentor.so_luong_dang_huong_dan = 0
    return mentor
