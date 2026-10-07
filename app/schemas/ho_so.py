from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class HoSoBase(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100, description="Họ và tên sinh viên")
    email: EmailStr = Field(..., description="Email của sinh viên")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="Số điện thoại liên hệ")
    truong_dai_hoc: Optional[str] = Field(None, max_length=150, description="Trường đại học")
    chuyen_nganh: Optional[str] = Field(None, max_length=100, description="Chuyên ngành")
    trang_thai: str = Field("DangThucTap", description="Trạng thái hồ sơ: DangThucTap, DaTiepNhan, Khoa, BiHuy")


class HoSoCreate(HoSoBase):
    ma_ho_so: str = Field(..., min_length=3, max_length=50, description="Mã hồ sơ định danh")


class HoSoResponse(HoSoBase):
    ma_ho_so: str
    ngay_tao: datetime

    model_config = ConfigDict(from_attributes=True)
