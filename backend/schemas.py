from pydantic import BaseModel, Field, field_validator, model_validator
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
    ghi_chu: Optional[str] = Field(default=None, max_length=500, description="Ghi chú hoặc lý do phê duyệt / từ chối gửi tới thực tập sinh")

    @field_validator('trang_thai_duyet')
    def validate_trang_thai_duyet(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Trạng thái duyệt không được để trống hoặc chỉ chứa khoảng trắng")
        
        valid_statuses = ["ChoDuyet", "DaDuyet", "TuChoi"]
        cleaned = value.strip()
        if cleaned not in valid_statuses:
            raise ValueError(f"Trạng thái duyệt không hợp lệ. Chỉ chấp nhận một trong các giá trị: {', '.join(valid_statuses)}")
        return cleaned

    @field_validator('ghi_chu')
    def validate_ghi_chu(cls, value: Optional[str]):
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None


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


# ==============================================================
# SCHEMAS CHO CHƯƠNG TRÌNH THỰC TẬP (PROGRAMS API)
# ==============================================================
class ProgramCreate(BaseModel):
    """Schema tạo mới chương trình thực tập (POST)"""
    ma_phong_ban: int = Field(..., gt=0, description="Mã phòng ban quản lý chương trình")
    ten_chuong_trinh: str = Field(..., min_length=1, max_length=150, description="Tên chương trình thực tập")
    mo_ta: Optional[str] = Field(default=None, description="Mô tả nội dung chương trình")
    ngay_bat_dau: Optional[date] = Field(default=None, description="Ngày bắt đầu (tùy chọn, mặc định hôm nay)")
    ngay_ket_thuc: Optional[date] = Field(default=None, description="Ngày kết thúc (tùy chọn, mặc định sau 3 tháng)")

    @field_validator('ten_chuong_trinh')
    def validate_ten_chuong_trinh(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên chương trình thực tập không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned

    @field_validator('mo_ta')
    def validate_mo_ta(cls, value: Optional[str]):
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None

    @model_validator(mode='after')
    def validate_dates(self):
        if self.ngay_bat_dau and self.ngay_ket_thuc:
            if self.ngay_ket_thuc < self.ngay_bat_dau:
                raise ValueError("Ngày kết thúc phải diễn ra sau hoặc cùng ngày với ngày bắt đầu")
        return self


class ProgramDetailData(BaseModel):
    ma_chuong_trinh: int
    ma_phong_ban: int
    ten_phong_ban: Optional[str] = None
    ten_chuong_trinh: str
    ngay_bat_dau: Optional[str] = None
    ngay_ket_thuc: Optional[str] = None
    mo_ta: Optional[str] = None

class ProgramResponse(BaseModel):
    status_code: int = 201
    message: str
    data: Optional[ProgramDetailData] = None

