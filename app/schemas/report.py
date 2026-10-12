from typing import Dict
from pydantic import BaseModel, Field

class CompletionRateResponse(BaseModel):
    tong_so_sinh_vien: int = Field(..., description="Tổng số lượng sinh viên trong hệ thống", ge=0)
    so_luong_dang_thuc_tap: int = Field(..., description="Số lượng sinh viên trạng thái DangThucTap", ge=0)
    so_luong_hoan_thanh: int = Field(..., description="Số lượng sinh viên trạng thái HoanThanh", ge=0)
    so_luong_thoi_hoc: int = Field(..., description="Số lượng sinh viên trạng thái ThoiHoc", ge=0)
    ty_le_hoan_thanh: float = Field(..., description="Tỷ lệ phần trăm (%) hoàn thành chương trình thực tập", ge=0.0, le=100.0)
    chi_tiet_theo_trang_thai: Dict[str, int] = Field(default_factory=dict, description="Chi tiết số lượng theo từng trạng thái")

    class Config:
        from_attributes = True
