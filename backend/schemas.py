from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
import re

# ==============================================================
# SCHEMA CHO REQUEST CẬP NHẬT THÔNG TIN HỒ SƠ THỰC TẬP SINH (PUT)
# ==============================================================
class InternUpdate(BaseModel):
    # Thông tin tài khoản người dùng
    ho_ten: str = Field(..., min_length=1, max_length=100, description="Họ và tên")
    email: str = Field(..., min_length=1, max_length=100, description="Địa chỉ email")
    so_dien_thoai: Optional[str] = Field(default=None, description="Số điện thoại liên lạc")
    
    # Thông tin hồ sơ thực tập
    chuyen_nganh: Optional[str] = Field(default=None, max_length=100, description="Chuyên ngành đào tạo")
    ma_truong: Optional[int] = Field(default=None, description="Mã trường đại học")
    trang_thai_thuc_tap: Optional[str] = Field(default="DangThucTap", description="Trạng thái: DangThucTap, HoanThanh, ThoiHoc")

    # Validate họ tên: không được để trống khoảng trắng và chỉ chứa chữ cái tiếng Việt
    @field_validator('ho_ten')
    def validate_ho_ten(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Họ tên không được để trống hoặc chỉ chứa khoảng trắng")
        if not re.match(r"^[a-zA-Z\s\u00C0-\u1EF9]+$", cleaned):
            raise ValueError("Họ tên không hợp lệ (chỉ được chứa chữ cái)")
        return cleaned

    # Validate email: đúng định dạng cú pháp email
    @field_validator('email')
    def validate_email(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Email không được để trống hoặc chỉ chứa khoảng trắng")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", cleaned):
            raise ValueError("Email không đúng định dạng hợp lệ")
        return cleaned

    # Validate số điện thoại: nếu nhập thì phải chuẩn 10 chữ số
    @field_validator('so_dien_thoai')
    def validate_so_dien_thoai(cls, value: Optional[str]):
        if not value or not value.strip():
            return None
        cleaned = value.strip()
        if not re.match(r"^(0|\+84)[0-9]{9}$|^[0-9]{10}$", cleaned):
            raise ValueError("Số điện thoại không hợp lệ (phải gồm 10 chữ số)")
        return cleaned


# ==============================================================
# SCHEMA CHO RESPONSE CHI TIẾT THỰC TẬP SINH (GET)
# ==============================================================
class InternDetailData(BaseModel):
    ma_ho_so: int
    ma_nguoi_dung: int
    ho_ten: Optional[str] = None
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    ma_truong: Optional[int] = None
    ten_truong: Optional[str] = None
    ma_chuong_trinh: Optional[int] = None
    ten_chuong_trinh: Optional[str] = None
    ngay_bat_dau: Optional[str] = None
    ngay_ket_thuc: Optional[str] = None
    ma_mentor: Optional[int] = None
    ten_mentor: Optional[str] = None
    trang_thai_xet_duyet: Optional[str] = None
    trang_thai_thuc_tap: Optional[str] = None

class InternResponse(BaseModel):
    status_code: int = 200
    message: str
    data: Optional[InternDetailData] = None


# ==============================================================
# SCHEMAS CHO TÀI LIỆU HỒ SƠ (DOCUMENTS API)
# ==============================================================
class DocumentStatusUpdate(BaseModel):
    """Schema cập nhật trạng thái duyệt tài liệu (PATCH)"""
    trang_thai_duyet: str = Field(..., description="Trạng thái duyệt: ChoDuyet, DaDuyet, TuChoi")

    @field_validator('trang_thai_duyet')
    def validate_trang_thai_duyet(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Trạng thái duyệt không được để trống hoặc chỉ chứa khoảng trắng")
        
        valid_statuses = ["ChoDuyet", "DaDuyet", "TuChoi"]
        cleaned = value.strip()
        if cleaned not in valid_statuses:
            raise ValueError(f"Trạng thái duyệt không hợp lệ. Chỉ chấp nhận một trong các giá trị: {', '.join(valid_statuses)}")
        return cleaned


class DocumentItem(BaseModel):
    ma_tai_lieu: int
    ma_ho_so: int
    loai_tai_lieu: str
    duong_dan_file: str
    trang_thai_duyet: str

class DocumentListResponse(BaseModel):
    status_code: int = 200
    message: str
    data: List[DocumentItem]
