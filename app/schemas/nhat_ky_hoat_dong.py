from datetime import datetime
from typing import Optional, List, Union, Any
from pydantic import BaseModel, Field, ConfigDict


class NhatKyHoatDongBase(BaseModel):
    ma_nguoi_dung: Optional[Union[int, str]] = Field(None, description="Mã người dùng thực hiện thao tác")
    hanh_dong: str = Field(..., description="Tên hành động nghiệp vụ (Vd: DANG_NHAP, TAO_NGUOI_DUNG, ...)")
    endpoint: str = Field(..., description="Đường dẫn API (Vd: /api/v1/admin/users)")
    phuong_thuc: str = Field(..., description="Phương thức HTTP (GET, POST, PUT, DELETE, PATCH)")
    dia_chi_ip: Optional[str] = Field(None, description="Địa chỉ IP client")
    mo_ta: Optional[str] = Field(None, description="Mô tả chi tiết hoặc trạng thái của thao tác")


class NhatKyHoatDongCreate(NhatKyHoatDongBase):
    """Schema dùng để tạo bản ghi nhật ký mới trong database"""
    thoi_gian: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Thời điểm ghi log")


class NhatKyHoatDongResponse(NhatKyHoatDongBase):
    """Schema phản hồi thông tin chi tiết một bản ghi nhật ký hoạt động"""
    ma_nhat_ky: int = Field(..., description="Mã nhật ký tự tăng (Primary Key)")
    thoi_gian: datetime = Field(..., description="Thời gian thực hiện hành động")
    
    # Bổ sung thông tin người dùng tiện lợi cho Frontend hiển thị
    ten_dang_nhap: Optional[str] = Field(None, description="Tên đăng nhập của người dùng")
    ho_ten: Optional[str] = Field(None, description="Họ tên của người dùng")
    vai_tro: Optional[str] = Field(None, description="Vai trò của người dùng (Admin, HR, Mentor, ThucTapSinh)")

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogResponse(BaseModel):
    """Schema phản hồi phân trang danh sách nhật ký hoạt động cho Admin"""
    items: List[NhatKyHoatDongResponse] = Field(description="Danh sách nhật ký hoạt động của trang")
    total: int = Field(..., description="Tổng số lượng bản ghi thỏa mãn bộ lọc")
    page: int = Field(..., description="Số trang hiện tại (bắt đầu từ 1)")
    page_size: int = Field(..., description="Số lượng bản ghi trên mỗi trang")
    total_pages: int = Field(..., description="Tổng số trang có sẵn")
