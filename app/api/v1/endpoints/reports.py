from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import CompletionRateResponse
from app.services.report_service import ReportService

router = APIRouter()

@router.get(
    "/completion-rate",
    response_model=CompletionRateResponse,
    status_code=status.HTTP_200_OK,
    summary="Báo cáo tỷ lệ hoàn thành chương trình thực tập",
    description="""
### Mục tiêu nghiệp vụ (User Story #33):
**Là HR, tôi muốn xem tỷ lệ hoàn thành chương trình để đánh giá chất lượng thực tập.**

### Chức năng:
* Truy vấn **tổng số lượng sinh viên** (`total_students`).
* Đếm số lượng sinh viên phân loại theo từng trạng thái:
    - **`DangThucTap`**: Đang tham gia thực tập.
    - **`HoanThanh`**: Đã hoàn thành chương trình thực tập.
    - **`ThoiHoc`**: Thôi học hoặc nghỉ giữa chừng.
* Tự động tính toán tỷ lệ phần trăm (%):
    - **`completion_rate`**: `(HoanThanh / total_students) * 100`
    - Cùng tỷ lệ % của các trạng thái còn lại.
* Cung cấp mảng **`chart_data`** với nhãn tiếng Việt và mã màu chuẩn HEX giúp Frontend tích hợp vẽ biểu đồ Donut / Pie / Bar chart ngay lập tức.
    """
)
def get_internship_completion_rate(
    university: Optional[str] = Query(
        None,
        description="Lọc theo tên trường Đại học (tìm kiếm tương đối, không phân biệt hoa thường)"
    ),
    department: Optional[str] = Query(
        None,
        description="Lọc theo phòng ban thực tập (ví dụ: 'Backend', 'Frontend', 'Mobile'...)"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Lọc theo thời gian bắt đầu thực tập từ ngày (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Lọc theo thời gian kết thúc thực tập đến ngày (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db)
) -> CompletionRateResponse:
    """Endpoint xử lý truy vấn báo cáo và thống kê tỷ lệ hoàn thành thực tập."""
    try:
        report_data = ReportService.get_completion_rate_report(
            db=db,
            university=university,
            department=department,
            start_date=start_date,
            end_date=end_date
        )
        return CompletionRateResponse(
            success=True,
            message="Lấy dữ liệu tỷ lệ hoàn thành chương trình thực tập thành công",
            data=report_data
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đã xảy ra lỗi khi tạo báo cáo thống kê: {str(exc)}"
        )
