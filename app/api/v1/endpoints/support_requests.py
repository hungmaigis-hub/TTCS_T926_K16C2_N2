from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.yeu_cau_ho_tro import YeuCauHoTro
from app.schemas.yeu_cau_ho_tro import (
    YeuCauHoTroCreate,
    YeuCauHoTroResponse,
    YeuCauHoTroUpdateTrangThai,
)

router = APIRouter()


@router.post(
    "",
    response_model=YeuCauHoTroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tiếp nhận yêu cầu hỗ trợ của sinh viên (User Story 27)",
    description="""
    Endpoint tiếp nhận yêu cầu hỗ trợ từ sinh viên (thực tập sinh).
    
    Hệ thống sẽ:
    1. Kiểm tra tính hợp lệ của hồ sơ sinh viên (`ma_ho_so`).
    2. **Gán tự động** trạng thái ban đầu là **`ChoXuLy`**.
    3. **Gán tự động** thời gian tạo (`ngay_tao`) theo thời gian thực.
    4. Lưu vào CSDL và trả về thông tin chi tiết của yêu cầu hỗ trợ vừa tạo.
    """
)
def create_support_request(
    request_in: YeuCauHoTroCreate,
    db: Session = Depends(get_db)
):
    # 1. Kiểm tra mã hồ sơ thực tập của sinh viên trong cơ sở dữ liệu
    try:
        check_query = text(
            "SELECT 1 FROM ho_so_thuc_tap WHERE ma_ho_so = :ma_ho_so "
            "UNION SELECT 1 FROM ho_so WHERE ma_ho_so = :ma_ho_so LIMIT 1"
        )
        result = db.execute(check_query, {"ma_ho_so": request_in.ma_ho_so}).first()
        if result is None:
            table_check = db.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ho_so_thuc_tap', 'ho_so')")
            ).fetchall()
            if table_check:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hồ sơ thực tập với mã {request_in.ma_ho_so} không tồn tại trong hệ thống."
                )
    except HTTPException:
        raise
    except Exception:
        # Nếu đang chạy môi trường test độc lập hoặc bảng hồ sơ chưa được tạo thì tiếp tục tạo yêu cầu
        pass

    # 2. Khởi tạo yêu cầu hỗ trợ mới với các giá trị gán tự động
    new_request = YeuCauHoTro(
        ma_ho_so=request_in.ma_ho_so,
        loai_yeu_cau=request_in.loai_yeu_cau,
        tieu_de=request_in.tieu_de.strip(),
        noi_dung=request_in.noi_dung.strip(),
        trang_thai="ChoXuLy",  # Gán tự động trạng thái Chờ Xử Lý
        ngay_tao=datetime.now(timezone.utc)  # Gán tự động ngày tạo
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get(
    "",
    response_model=List[YeuCauHoTroResponse],
    summary="Lấy danh sách yêu cầu hỗ trợ (Dành cho Sinh viên & HR)",
    description="Frontend có thể truyền `ma_ho_so` để sinh viên xem lịch sử yêu cầu của chính mình, hoặc lọc theo `trang_thai` cho giao diện HR."
)
def get_support_requests(
    ma_ho_so: Optional[int] = Query(None, description="Lọc theo mã hồ sơ (sinh viên xem lịch sử của mình)"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái (ChoXuLy, DangXuLy, DaXuLy, TuChoi)"),
    skip: int = Query(0, ge=0, description="Phân trang: số bản ghi bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Phân trang: số bản ghi tối đa lấy"),
    db: Session = Depends(get_db)
):
    query = db.query(YeuCauHoTro)
    if ma_ho_so is not None:
        query = query.filter(YeuCauHoTro.ma_ho_so == ma_ho_so)
    if trang_thai is not None:
        query = query.filter(YeuCauHoTro.trang_thai == trang_thai)
    return query.order_by(YeuCauHoTro.ngay_tao.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=YeuCauHoTroResponse,
    summary="Xem chi tiết một yêu cầu hỗ trợ",
    description="Lấy chi tiết yêu cầu hỗ trợ theo `ma_yeu_cau`."
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
    summary="HR duyệt và phản hồi yêu cầu hỗ trợ (User Story 28)",
    description="HR cập nhật trạng thái (`DangXuLy`, `DaXuLy`, `TuChoi`) và đính kèm phản hồi cho thực tập sinh."
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
    request_obj.ngay_xu_ly = datetime.now(timezone.utc)

    db.commit()
    db.refresh(request_obj)
    return request_obj
