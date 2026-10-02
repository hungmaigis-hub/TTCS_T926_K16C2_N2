from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.hop_dong import HopDong
from app.schemas.hop_dong import (
    HopDongCreate,
    HopDongResponse,
    HopDongListResponse,
    HopDongUpdate,
    HopDongConfirm
)

router = APIRouter()


@router.post(
    "",
    response_model=HopDongResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới hợp đồng thực tập",
    description="Endpoint lưu ma_so_hop_dong, ngay_ky, muc_phu_cap_co_ban, kèm mã hồ sơ và file đính kèm. Kiểm tra mã hợp đồng không được trùng lặp."
)
def create_contract(
    contract_in: HopDongCreate,
    db: Session = Depends(get_db)
):
    """
    Nhiệm vụ Backend (FastAPI) - Nguyễn Văn Hiếu:
    - Lưu thông tin hợp đồng: ma_so_hop_dong, ngay_ky, muc_phu_cap_co_ban
    - Lưu khóa ngoại ma_ho_so liên kết hồ sơ thực tập sinh
    - Kiểm tra tính duy nhất của ma_so_hop_dong (nếu trùng trả về 400 Bad Request)
    - Trả về mã HTTP 201 Created cùng dữ liệu hợp đồng vừa tạo
    """
    # 1. Kiểm tra mã số hợp đồng đã tồn tại trong database chưa
    existing_contract = db.query(HopDong).filter(
        HopDong.ma_so_hop_dong == contract_in.ma_so_hop_dong
    ).first()
    
    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã số hợp đồng '{contract_in.ma_so_hop_dong}' đã tồn tại trên hệ thống!"
        )

    # 2. Tạo đối tượng model hop_dong
    db_contract = HopDong(
        ma_so_hop_dong=contract_in.ma_so_hop_dong,
        ngay_ky=contract_in.ngay_ky,
        muc_phu_cap_co_ban=contract_in.muc_phu_cap_co_ban,
        ma_ho_so=contract_in.ma_ho_so,
        file_url=contract_in.file_url,
        trang_thai=contract_in.trang_thai or "Chờ xác nhận",
        ghi_chu=contract_in.ghi_chu
    )

    # 3. Lưu vào database
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return db_contract


@router.get(
    "",
    response_model=HopDongListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách hợp đồng thực tập",
    description="Cung cấp API cho Frontend hiển thị bảng danh sách hợp đồng kèm phân trang và tìm kiếm theo mã hợp đồng hoặc mã hồ sơ."
)
def get_contracts(
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua (offset)"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng bản ghi tối đa trả về"),
    ma_so_hop_dong: Optional[str] = Query(None, description="Tìm kiếm theo mã số hợp đồng"),
    ma_ho_so: Optional[str] = Query(None, description="Tìm kiếm theo mã hồ sơ thực tập sinh"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái hợp đồng"),
    db: Session = Depends(get_db)
):
    query = db.query(HopDong)

    if ma_so_hop_dong:
        query = query.filter(HopDong.ma_so_hop_dong.ilike(f"%{ma_so_hop_dong.strip()}%"))
    if ma_ho_so:
        query = query.filter(HopDong.ma_ho_so == ma_ho_so.strip())
    if trang_thai:
        query = query.filter(HopDong.trang_thai == trang_thai.strip())

    total = query.count()
    items = query.order_by(HopDong.id.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}


@router.get(
    "/{contract_id}",
    response_model=HopDongResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết hợp đồng theo ID"
)
def get_contract_by_id(
    contract_id: int,
    db: Session = Depends(get_db)
):
    contract = db.query(HopDong).filter(HopDong.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hợp đồng với ID = {contract_id}"
        )
    return contract


@router.patch(
    "/{contract_id}/confirm",
    response_model=HopDongResponse,
    status_code=status.HTTP_200_OK,
    summary="Thực tập sinh xác nhận hợp đồng (User Story STT 10)"
)
def confirm_contract(
    contract_id: int,
    payload: HopDongConfirm,
    db: Session = Depends(get_db)
):
    contract = db.query(HopDong).filter(HopDong.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hợp đồng với ID = {contract_id}"
        )
    
    if contract.trang_thai == "Đã xác nhận":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hợp đồng này đã được xác nhận trước đó, không thể xác nhận nhiều lần!"
        )

    contract.trang_thai = "Đã xác nhận"
    if payload.ghi_chu:
        contract.ghi_chu = f"{contract.ghi_chu or ''} | TTS phản hồi: {payload.ghi_chu}".strip()

    db.commit()
    db.refresh(contract)
    return contract


@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa hợp đồng theo ID"
)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db)
):
    contract = db.query(HopDong).filter(HopDong.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hợp đồng với ID = {contract_id}"
        )
    db.delete(contract)
    db.commit()
    return None
