from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.report import CompletionRateResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports - Báo cáo & Thống kê"])

@router.get(
    "/completion-rate",
    response_model=CompletionRateResponse,
    status_code=status.HTTP_200_OK,
    summary="Báo cáo tỷ lệ hoàn thành chương trình thực tập",
    description=(
        "Endpoint truy vấn tổng số lượng sinh viên, đếm số lượng theo từng trạng thái "
        "(DangThucTap, HoanThanh, ThoiHoc) và tự động tính toán tỷ lệ phần trăm (%) hoàn thành chương trình thực tập."
    )
)
def get_completion_rate(db: Session = Depends(get_db)):
    """
    API GET /api/v1/reports/completion-rate
    Truy vấn số liệu và tính tỷ lệ hoàn thành thực tập
    """
    return ReportService.get_completion_rate(db=db)
