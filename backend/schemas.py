from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import date
import re

class InternUpdate(BaseModel):

    # Các trường bắt buộc: dùng '...' nghĩa là không được phép null
    full_name: str = Field(..., min_length=1, max_length=50, description="Họ tên")
    email: str = Field(..., min_length=1, max_length=100, description="Email")
    
    # Các trường không bắt buộc: cho phép Optional và mặc định là None
    phone: Optional[str] = Field(default=None, min_length=10, max_length=10, description="Số điện thoại")
    university: Optional[str] = Field(default=None, max_length=100, description="Trường Đại học")
    major: Optional[str] = Field(default=None, max_length=100, description="Chuyên ngành")
    status: Optional[str] = Field(default="Đang thực tập", description="Trạng thái")
    start_date: Optional[date] = Field(default=None, description="Ngày bắt đầu thực tập")
    end_date: Optional[date] = Field(default=None, description="Ngày kết thúc thực tập")

    # Validate họ tên: không được chỉ toàn dấu cách và không chứa ký tự lạ/số
    @field_validator('full_name')
    def validate_full_name(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Họ tên không được để trống hoặc chỉ chứa khoảng trắng")
        # Kiểm tra chỉ chứa chữ cái tiếng Việt và khoảng trắng
        if not re.match(r"^[a-zA-Z\s\u00C0-\u1EF9]+$", cleaned):
            raise ValueError("Họ tên không hợp lệ (chỉ được chứa chữ cái)")
        return cleaned

    # Validate email: không để trống và đúng cấu trúc a@b.c
    @field_validator('email')
    def validate_email(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Email không được để trống hoặc chỉ chứa khoảng trắng")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", cleaned):
            raise ValueError("Email không đúng định dạng hợp lệ")
        return cleaned

    # Validate số điện thoại: nếu có nhập thì phải đủ 10 chữ số
    @field_validator('phone')
    def validate_phone(cls, value: Optional[str]):
        if not value or not value.strip():
            return None
        cleaned = value.strip()
        if not re.match(r"^(0|\+84)[0-9]{9}$|^[0-9]{10}$", cleaned):
            raise ValueError("Số điện thoại không hợp lệ (phải gồm 10 chữ số)")
        return cleaned

    # Validate logic nghiệp vụ: ngày kết thúc >= ngày bắt đầu
    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu")
        return self
