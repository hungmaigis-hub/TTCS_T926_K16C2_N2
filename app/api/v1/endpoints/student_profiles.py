from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.ho_so import HoSo
from app.schemas.ho_so import HoSoCreate, HoSoResponse, HoSoUpdate

router = APIRouter()


@router.post("", response_model=HoSoResponse, status_code=status.HTTP_201_CREATED, summary="Tạo hồ sơ thực tập mới")
def create_student_profile(profile_in: HoSoCreate, db: Session = Depends(get_db)):
    existing = db.query(HoSo).filter(HoSo.ma_sinh_vien == profile_in.ma_sinh_vien).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã sinh viên {profile_in.ma_sinh_vien} đã tồn tại hồ sơ thực tập."
        )
    profile = HoSo(**profile_in.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=List[HoSoResponse], summary="Lấy danh sách hồ sơ thực tập")
def get_student_profiles(db: Session = Depends(get_db)):
    return db.query(HoSo).all()


@router.get("/{id}", response_model=HoSoResponse, summary="Lấy chi tiết hồ sơ thực tập theo mã")
def get_student_profile_by_id(id: int, db: Session = Depends(get_db)):
    profile = db.query(HoSo).filter(HoSo.ma_ho_so == id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ thực tập với mã {id}."
        )
    return profile
