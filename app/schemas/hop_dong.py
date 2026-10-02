from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List


class HopDongBase(BaseModel):
    """Schema cơ bản cho hợp đồng thực tập"""
    ma_so_hop_dong: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mã số hợp đồng (duy nhất)",
        examples=["HD-2026-001"]
    )
    ngay_ky: date = Field(
        ...,
        description="Ngày ký hợp đồng",
        examples=["2026-10-02"]
    )
    muc_phu_cap_co_ban: Decimal = Field(
        ...,
        ge=0,
        description="Mức phụ cấp cơ bản (VNĐ, >= 0)",
        examples=[3500000.00]
    )
    ma_ho_so: Optional[str] = Field(
        None,
        max_length=50,
        description="Mã hồ sơ thực tập sinh liên kết",
        examples=["HS-2026-TTS-01"]
    )
    file_url: Optional[str] = Field(
        None,
        max_length=500,
        description="Đường dẫn file hợp đồng upload",
        examples=["https://storage.example.com/contracts/hd-001.pdf"]
    )
    ghi_chu: Optional[str] = Field(
        None,
        description="Ghi chú thêm về hợp đồng"
    )

    @field_validator("ma_so_hop_dong")
    @classmethod
    def validate_ma_so_hop_dong(cls, value: str) -> str:
        clean_val = value.strip()
        if not clean_val:
            raise ValueError("Mã số hợp đồng không được để trống hoặc chỉ chứa khoảng trắng.")
        return clean_val


class HopDongCreate(HopDongBase):
    """Schema dữ liệu khi tạo mới hợp đồng (POST /api/v1/contracts)"""
    trang_thai: Optional[str] = Field(
        default="Chờ xác nhận",
        description="Trạng thái ban đầu của hợp đồng"
    )


class HopDongUpdate(BaseModel):
    """Schema dữ liệu khi cập nhật hợp đồng"""
    ngay_ky: Optional[date] = None
    muc_phu_cap_co_ban: Optional[Decimal] = Field(None, ge=0)
    ma_ho_so: Optional[str] = None
    file_url: Optional[str] = None
    trang_thai: Optional[str] = None
    ghi_chu: Optional[str] = None


class HopDongConfirm(BaseModel):
    """Schema khi thực tập sinh xác nhận hợp đồng"""
    xac_nhan: bool = Field(True, description="Đồng ý xác nhận hợp đồng")
    ghi_chu: Optional[str] = Field(None, description="Ý kiến hoặc ghi chú của thực tập sinh")


class HopDongResponse(HopDongBase):
    """Schema trả về chi tiết hợp đồng cho client/frontend"""
    id: int = Field(..., description="ID định danh")
    trang_thai: str = Field(..., description="Trạng thái hợp đồng")
    created_at: datetime = Field(..., description="Thời gian tạo")
    updated_at: datetime = Field(..., description="Thời gian cập nhật")

    class Config:
        from_attributes = True


class HopDongListResponse(BaseModel):
    """Schema trả về danh sách hợp đồng kèm phân trang"""
    total: int = Field(..., description="Tổng số bản ghi")
    items: List[HopDongResponse] = Field(..., description="Danh sách hợp đồng")
