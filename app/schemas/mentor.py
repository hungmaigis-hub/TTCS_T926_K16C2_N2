from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class MentorBase(BaseModel):
    ma_can_bo: str
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    phong_ban: str
    chuc_vu: str
    chuyen_mon: Optional[str] = None
    so_luong_toi_da: int = 5
    trang_thai: str = "HoatDong"

class MentorCreate(MentorBase):
    pass

class MentorSimpleResponse(BaseModel):
    id: int
    ma_can_bo: str
    ho_ten: str
    email: str
    phong_ban: str
    chuc_vu: str
    chuyen_mon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MentorResponse(MentorBase):
    id: int
    so_luong_dang_huong_dan: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
