from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.ho_so import HoSo
from app.schemas.ho_so import HoSoCreate, HoSoResponse

router = APIRouter()


@router.get(
    "",
    response_model=List[HoSoResponse],
    summary="Lấy danh sách hồ sơ sinh viên",
    description="Xem danh sách các hồ sơ sinh viên / thực tập sinh trong hệ thống.",
)
def list_students(db: Session = Depends(get_db)):
    return db.query(HoSo).all()


@router.post(
    "",
    response_model=HoSoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới hồ sơ sinh viên",
    description="Thêm hồ sơ sinh viên / thực tập sinh vào cơ sở dữ liệu.",
)
def create_student(payload: HoSoCreate, db: Session = Depends(get_db)):
    existing = db.query(HoSo).filter(HoSo.ma_ho_so == payload.ma_ho_so).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã hồ sơ '{payload.ma_ho_so}' đã tồn tại trong hệ thống.",
        )
    ho_so = HoSo(**payload.model_dump())
    db.add(ho_so)
    db.commit()
    db.refresh(ho_so)
    return ho_so


@router.get(
    "/{ma_ho_so}",
    response_model=HoSoResponse,
    summary="Chi tiết hồ sơ sinh viên",
    description="Tra cứu hồ sơ sinh viên theo mã hồ sơ.",
)
def get_student(ma_ho_so: str, db: Session = Depends(get_db)):
    ho_so = db.query(HoSo).filter(HoSo.ma_ho_so == ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ sinh viên với mã '{ma_ho_so}'.",
        )
    return ho_so
