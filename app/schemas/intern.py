from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.mentor import MentorSimpleResponse

class AssignMentorRequest(BaseModel):
    """
    Schema nhận payload phân công mentor cho thực tập sinh.
    - ma_mentor: ID của Mentor trong hệ thống (hoặc null nếu hủy gán)
    - ghi_chu: Ghi chú nội dung phân công / dự án hướng dẫn
    """
    ma_mentor: Optional[int] = Field(
        default=...,
        description="ID của Mentor (tương ứng trường id trong bảng mentors) cần gán cho thực tập sinh. Truyền null nếu muốn hủy gán."
    )
    ghi_chu: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Ghi chú phân công, ví dụ: 'Hướng dẫn dự án Quản lý TTS'"
    )

class HoSoThucTapBase(BaseModel):
    ma_sv: str
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    truong_hoc: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    trang_thai: str = "DangThucTap"
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None

class HoSoThucTapCreate(HoSoThucTapBase):
    ma_mentor: Optional[int] = None

class HoSoThucTapResponse(HoSoThucTapBase):
    id: int
    ma_mentor: Optional[int] = None
    mentor: Optional[MentorSimpleResponse] = None
    ghi_chu_phan_cong: Optional[str] = None
    ngay_gan_mentor: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssignMentorResponse(BaseModel):
    """Schema trả về chuẩn sau khi gán mentor thành công"""
    success: bool = True
    message: str = "Phân công mentor thành công"
    data: HoSoThucTapResponse
