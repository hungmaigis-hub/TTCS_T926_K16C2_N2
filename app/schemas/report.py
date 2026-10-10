from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class StatusCountDetail(BaseModel):
    """Số lượng chi tiết theo từng trạng thái."""
    DangThucTap: int = Field(0, description="Số lượng sinh viên đang trong quá trình thực tập")
    HoanThanh: int = Field(0, description="Số lượng sinh viên đã hoàn thành thực tập")
    ThoiHoc: int = Field(0, description="Số lượng sinh viên đã thôi học / ngừng thực tập")

    class Config:
        json_schema_extra = {
            "example": {
                "DangThucTap": 15,
                "HoanThanh": 30,
                "ThoiHoc": 5
            }
        }

class StatusPercentageDetail(BaseModel):
    """Tỷ lệ phần trăm (%) chi tiết theo từng trạng thái."""
    DangThucTap: float = Field(0.0, description="Tỷ lệ % sinh viên đang thực tập")
    HoanThanh: float = Field(0.0, description="Tỷ lệ % sinh viên đã hoàn thành (Completion Rate)")
    ThoiHoc: float = Field(0.0, description="Tỷ lệ % sinh viên thôi học")

    class Config:
        json_schema_extra = {
            "example": {
                "DangThucTap": 30.0,
                "HoanThanh": 60.0,
                "ThoiHoc": 10.0
            }
        }

class ChartItem(BaseModel):
    """Dữ liệu định dạng sẵn để Frontend dễ dàng render biểu đồ (Pie / Donut / Bar Chart)."""
    status: str = Field(..., description="Mã trạng thái")
    label: str = Field(..., description="Nhãn hiển thị tiếng Việt")
    count: int = Field(..., description="Số lượng sinh viên")
    percentage: float = Field(..., description="Tỷ lệ phần trăm (%)")
    color: str = Field(..., description="Mã màu HEX gợi ý cho biểu đồ")

class CompletionRateReportData(BaseModel):
    """Dữ liệu phản hồi chi tiết báo cáo tỷ lệ hoàn thành thực tập."""
    total_students: int = Field(..., description="Tổng số lượng sinh viên trong phạm vi thống kê")
    status_counts: StatusCountDetail = Field(..., description="Đếm số lượng sinh viên theo từng trạng thái")
    completion_rate: float = Field(
        ..., 
        description="Tỷ lệ phần trăm (%) hoàn thành chương trình thực tập (HoanThanh / Tổng số * 100)"
    )
    percentages: StatusPercentageDetail = Field(..., description="Tỷ lệ phần trăm của từng trạng thái")
    chart_data: List[ChartItem] = Field(..., description="Mảng dữ liệu sẵn sàng cho các thư viện biểu đồ frontend (Recharts, Chart.js...)")
    summary: str = Field(..., description="Tóm tắt kết quả thống kê bằng ngôn ngữ tự nhiên")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Bộ lọc đã áp dụng (nếu có)")

    class Config:
        json_schema_extra = {
            "example": {
                "total_students": 50,
                "status_counts": {
                    "DangThucTap": 15,
                    "HoanThanh": 30,
                    "ThoiHoc": 5
                },
                "completion_rate": 60.0,
                "percentages": {
                    "DangThucTap": 30.0,
                    "HoanThanh": 60.0,
                    "ThoiHoc": 10.0
                },
                "chart_data": [
                    {
                        "status": "HoanThanh",
                        "label": "Đã hoàn thành",
                        "count": 30,
                        "percentage": 60.0,
                        "color": "#10B981"
                    },
                    {
                        "status": "DangThucTap",
                        "label": "Đang thực tập",
                        "count": 15,
                        "percentage": 30.0,
                        "color": "#3B82F6"
                    },
                    {
                        "status": "ThoiHoc",
                        "label": "Thôi học",
                        "count": 5,
                        "percentage": 10.0,
                        "color": "#EF4444"
                    }
                ],
                "summary": "Tổng cộng 50 sinh viên. Tỷ lệ hoàn thành chương trình thực tập đạt 60.0%.",
                "filters_applied": {
                    "university": None,
                    "department": None,
                    "start_date": None,
                    "end_date": None
                }
            }
        }

class CompletionRateResponse(BaseModel):
    """Chuẩn Response đóng gói gửi về cho Frontend."""
    success: bool = Field(True, description="Trạng thái phản hồi thành công hay thất bại")
    message: str = Field("Lấy dữ liệu tỷ lệ hoàn thành chương trình thực tập thành công", description="Thông báo")
    data: CompletionRateReportData = Field(..., description="Dữ liệu báo cáo")
