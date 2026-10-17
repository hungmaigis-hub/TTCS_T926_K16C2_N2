from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.yeu_cau_ho_tro import YeuCauHoTro
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.schemas.yeu_cau_ho_tro import (
    YeuCauHoTroCreate,
    YeuCauHoTroResponse,
    YeuCauHoTroUpdateTrangThai,
)

router = APIRouter(prefix="/support-requests", tags=["Yêu cầu hỗ trợ (Support Requests)"])


@router.post(
    "",
    response_model=YeuCauHoTroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tiếp nhận yêu cầu hỗ trợ của sinh viên (User Story 27)",
    description="Endpoint tiếp nhận yêu cầu hỗ trợ từ thực tập sinh. Tự động gán trạng thái ChoXuLy và ngày tạo."
)
def create_support_request(
    request_in: YeuCauHoTroCreate,
    db: Session = Depends(get_db)
):
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong hệ thống hay không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == request_in.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hồ sơ thực tập với mã {request_in.ma_ho_so} không tồn tại trong hệ thống."
        )

    # 2. Khởi tạo yêu cầu hỗ trợ và gán tự động ChoXuLy, ngay_tao
    new_request = YeuCauHoTro(
        ma_ho_so=request_in.ma_ho_so,
        loai_yeu_cau=request_in.loai_yeu_cau,
        tieu_de=request_in.tieu_de.strip(),
        noi_dung=request_in.noi_dung.strip(),
        trang_thai="ChoXuLy",
        ngay_tao=datetime.utcnow()
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get(
    "",
    response_model=List[YeuCauHoTroResponse],
    summary="Lấy danh sách yêu cầu hỗ trợ",
    description="Hỗ trợ lọc theo mã hồ sơ (để sinh viên xem lịch sử) hoặc trạng thái (cho HR quản lý)."
)
def get_support_requests(
    ma_ho_so: Optional[str] = Query(None, description="Lọc theo mã hồ sơ thực tập"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái xử lý"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(YeuCauHoTro)
    if ma_ho_so:
        query = query.filter(YeuCauHoTro.ma_ho_so == ma_ho_so)
    if trang_thai:
        query = query.filter(YeuCauHoTro.trang_thai == trang_thai)
    return query.order_by(YeuCauHoTro.ngay_tao.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=YeuCauHoTroResponse,
    summary="Chi tiết yêu cầu hỗ trợ"
)
def get_support_request_by_id(id: int, db: Session = Depends(get_db)):
    request_obj = db.query(YeuCauHoTro).filter(YeuCauHoTro.ma_yeu_cau == id).first()
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy yêu cầu hỗ trợ với mã {id}."
        )
    return request_obj


@router.patch(
    "/{id}/status",
    response_model=YeuCauHoTroResponse,
    summary="HR duyệt và phản hồi yêu cầu hỗ trợ (User Story 28)"
)
def update_support_request_status(
    id: int,
    status_update: YeuCauHoTroUpdateTrangThai,
    db: Session = Depends(get_db)
):
    request_obj = db.query(YeuCauHoTro).filter(YeuCauHoTro.ma_yeu_cau == id).first()
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy yêu cầu hỗ trợ với mã {id}."
        )

    request_obj.trang_thai = status_update.trang_thai.value
    if status_update.phan_hoi:
        request_obj.phan_hoi = status_update.phan_hoi
    request_obj.ngay_xu_ly = datetime.utcnow()

    db.commit()
    db.refresh(request_obj)
    return request_obj
