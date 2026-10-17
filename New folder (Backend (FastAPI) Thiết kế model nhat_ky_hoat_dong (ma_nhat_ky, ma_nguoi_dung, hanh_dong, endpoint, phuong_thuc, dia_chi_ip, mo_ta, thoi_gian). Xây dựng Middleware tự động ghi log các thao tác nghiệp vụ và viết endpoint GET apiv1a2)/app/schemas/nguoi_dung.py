from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class NguoiDungBrief(BaseModel):
    ma_nguoi_dung: int
    ten_dang_nhap: str
    ho_ten: str
    email: str
    vai_tro: str

    model_config = ConfigDict(from_attributes=True)


class NguoiDungLogin(BaseModel):
    ten_dang_nhap: str
    mat_khau: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: NguoiDungBrief
