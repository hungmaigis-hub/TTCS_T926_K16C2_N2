from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class NguoiDungBase(BaseModel):
    email: EmailStr
    ho_ten: str
    vai_tro: Optional[str] = "ThucTapSinh"
    kich_hoat: Optional[bool] = True


class NguoiDungCreate(NguoiDungBase):
    mat_khau: str


class NguoiDungResponse(NguoiDungBase):
    ma_nguoi_dung: int
    ngay_tao: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
