from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class HoSoBase(BaseModel):
    ma_sinh_vien: str
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    ma_mentor: Optional[int] = None
    trang_thai: Optional[str] = "DangThucTap"


class HoSoCreate(HoSoBase):
    pass


class HoSoUpdate(BaseModel):
    ho_ten: Optional[str] = None
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    ma_mentor: Optional[int] = None
    trang_thai: Optional[str] = None


class HoSoResponse(HoSoBase):
    ma_ho_so: int
    ngay_tao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
