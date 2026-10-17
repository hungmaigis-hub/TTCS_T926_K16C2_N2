"""
Pydantic Schemas cho Người dùng & Quản trị tài khoản
Phân hệ: Quản trị hệ thống - Quản lý tài khoản & phân quyền
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserRole(str, Enum):
    """
    4 vai trò hợp lệ trong hệ thống theo đúng tài liệu đặc tả:
    - Admin: Quản trị viên hệ thống
    - HR: Nhân sự quản lý tuyển dụng và thực tập sinh
    - Mentor: Người hướng dẫn
    - ThucTapSinh: Thực tập sinh tham gia chương trình
    """
    ADMIN = "Admin"
    HR = "HR"
    MENTOR = "Mentor"
    THUCTAPSINH = "ThucTapSinh"


class UserBase(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100, description="Họ và tên người dùng")
    email: EmailStr = Field(..., description="Email định danh duy nhất của người dùng")
    ten_dang_nhap: str = Field(..., min_length=3, max_length=50, description="Tên đăng nhập (username) duy nhất")
    vai_tro: UserRole = Field(..., description="Vai trò: Admin, HR, Mentor, ThucTapSinh")


class UserCreate(BaseModel):
    """
    Schema nhận dữ liệu từ Frontend / Client gửi lên endpoint POST /api/v1/admin/users.
    Hỗ trợ cả tên trường tiếng Việt (ho_ten, email, ten_dang_nhap, mat_khau, vai_tro)
    lẫn tiếng Anh (full_name, username, password, role) để Frontend và Tester thao tác thuận tiện nhất.
    """
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100, description="Họ và tên người dùng")
    email: EmailStr = Field(..., description="Email định danh của người dùng")
    ten_dang_nhap: Optional[str] = Field(None, min_length=3, max_length=50, description="Tên đăng nhập duy nhất")
    mat_khau: Optional[str] = Field(None, min_length=6, max_length=128, description="Mật khẩu thô (sẽ được băm bằng bcrypt)")
    vai_tro: Optional[UserRole] = Field(None, description="Vai trò người dùng")

    # Các trường alias tiếng Anh tùy chọn
    full_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_and_validate_fields(cls, data: dict):
        if not isinstance(data, dict):
            return data
        
        # Đồng bộ ho_ten <-> full_name
        if not data.get("ho_ten") and data.get("full_name"):
            data["ho_ten"] = data["full_name"]
        elif not data.get("ho_ten") and not data.get("full_name"):
            raise ValueError("Trường 'ho_ten' (họ và tên) là bắt buộc.")

        # Đồng bộ ten_dang_nhap <-> username
        if not data.get("ten_dang_nhap") and data.get("username"):
            data["ten_dang_nhap"] = data["username"]
        elif not data.get("ten_dang_nhap") and not data.get("username"):
            raise ValueError("Trường 'ten_dang_nhap' (tên đăng nhập / username) là bắt buộc.")

        # Đồng bộ mat_khau <-> password
        if not data.get("mat_khau") and data.get("password"):
            data["mat_khau"] = data["password"]
        elif not data.get("mat_khau") and not data.get("password"):
            raise ValueError("Trường 'mat_khau' (mật khẩu / password) là bắt buộc.")

        # Đồng bộ vai_tro <-> role
        if not data.get("vai_tro") and data.get("role"):
            data["vai_tro"] = data["role"]
        elif not data.get("vai_tro") and not data.get("role"):
            raise ValueError("Trường 'vai_tro' (vai trò / role) là bắt buộc.")

        return data


class UserResponse(BaseModel):
    """
    Schema trả về thông tin tài khoản sau khi tạo thành công (201 Created).
    BẢO MẬT: Tuyệt đối không trả về mật khẩu thô hoặc mật khẩu đã băm!
    """
    ma_nguoi_dung: int
    ten_dang_nhap: str
    email: str
    ho_ten: str
    vai_tro: str
    trang_thai: bool
    ngay_tao: datetime

    # Cung cấp alias hỗ trợ Frontend / Tester
    id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

    @model_validator(mode="after")
    def populate_aliases(self):
        self.id = self.ma_nguoi_dung
        self.username = self.ten_dang_nhap
        self.full_name = self.ho_ten
        self.role = self.vai_tro
        return self

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """
    Schema đăng nhập lấy JWT token (phục vụ test và xác thực)
    """
    ten_dang_nhap: Optional[str] = None
    username: Optional[str] = None
    mat_khau: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_login_data(cls, data: dict):
        if not isinstance(data, dict):
            return data
        if not data.get("ten_dang_nhap") and data.get("username"):
            data["ten_dang_nhap"] = data["username"]
        if not data.get("mat_khau") and data.get("password"):
            data["mat_khau"] = data["password"]
        return data


class TokenResponse(BaseModel):
    """
    Schema trả về token đăng nhập
    """
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
