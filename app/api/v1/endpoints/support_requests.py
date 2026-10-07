from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.ho_so import HoSo
from app.models.yeu_cau_ho_tro import YeuCauHoTro
from app.schemas.yeu_cau_ho_tro import (
    SupportRequestCreate,
    SupportRequestResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=SupportRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tiếp nhận yêu cầu hỗ trợ của sinh viên",
    description="""
    Tiếp nhận yêu cầu hỗ trợ từ sinh viên / thực tập sinh:
    - Kiểm tra tính hợp lệ của hồ sơ sinh viên (`ma_ho_so`).
    - Gán tự động thời gian tạo (`ngay_tao`).
    - Gán tự động trạng thái ban đầu (`trang_thai = "ChoXuLy"`).
    """,
    responses={
        201: {
            "description": "Tiếp nhận yêu cầu hỗ trợ thành công",
            "model": SupportRequestResponse,
        },
        400: {
            "description": "Hồ sơ không hợp lệ (bị khóa hoặc ngừng hoạt động)",
        },
        404: {
            "description": "Không tìm thấy hồ sơ sinh viên trong hệ thống",
        },
        422: {
            "description": "Dữ liệu gửi lên không đúng định dạng",
        },
    },
)
def create_support_request(
    payload: SupportRequestCreate,
    db: Session = Depends(get_db),
):
    # 1. Kiểm tra sự tồn tại của hồ sơ sinh viên
    ho_so = db.query(HoSo).filter(HoSo.ma_ho_so == payload.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hồ sơ sinh viên với mã '{payload.ma_ho_so}' không tồn tại trong hệ thống.",
        )

    # 2. Kiểm tra tính hợp lệ của hồ sơ (không bị khóa / hủy)
    cac_trang_thai_vo_hieu = ["Khoa", "BiHuy", "NgungHoatDong"]
    if ho_so.trang_thai in cac_trang_thai_vo_hieu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hồ sơ sinh viên '{payload.ma_ho_so}' đang ở trạng thái '{ho_so.trang_thai}', không hợp lệ để gửi yêu cầu hỗ trợ.",
        )

    # 3. Tạo yêu cầu hỗ trợ mới với thời gian tạo tự động và trạng thái ChoXuLy
    yeu_cau_moi = YeuCauHoTro(
        ma_ho_so=payload.ma_ho_so,
        loai_yeu_cau=payload.loai_yeu_cau.strip(),
        tieu_de=payload.tieu_de.strip(),
        noi_dung=payload.noi_dung.strip(),
        trang_thai="ChoXuLy",  # Yêu cầu mặc định đề bài
        ngay_tao=datetime.utcnow(),  # Gán tự động thời gian tạo
    )

    db.add(yeu_cau_moi)
    db.commit()
    db.refresh(yeu_cau_moi)

    return yeu_cau_moi


@router.get(
    "",
    response_model=List[SupportRequestResponse],
    summary="Lấy danh sách yêu cầu hỗ trợ",
    description="Hỗ trợ lọc theo mã hồ sơ, trạng thái và phân trang (dành cho HR và Sinh viên).",
)
def get_support_requests(
    ma_ho_so: Optional[str] = Query(None, description="Lọc theo mã hồ sơ sinh viên"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái xử lý"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(50, ge=1, le=100, description="Số bản ghi tối đa lấy về"),
    db: Session = Depends(get_db),
):
    query = db.query(YeuCauHoTro)
    if ma_ho_so:
        query = query.filter(YeuCauHoTro.ma_ho_so == ma_ho_so)
    if trang_thai:
        query = query.filter(YeuCauHoTro.trang_thai == trang_thai)

    return query.order_by(YeuCauHoTro.ngay_tao.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{ma_yeu_cau}",
    response_model=SupportRequestResponse,
    summary="Xem chi tiết một yêu cầu hỗ trợ",
    description="Tra cứu chi tiết yêu cầu hỗ trợ theo mã yêu cầu.",
)
def get_support_request_by_id(
    ma_yeu_cau: int,
    db: Session = Depends(get_db),
):
    yeu_cau = db.query(YeuCauHoTro).filter(YeuCauHoTro.ma_yeu_cau == ma_yeu_cau).first()
    if not yeu_cau:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy yêu cầu hỗ trợ với mã {ma_yeu_cau}.",
        )
    return yeu_cau
