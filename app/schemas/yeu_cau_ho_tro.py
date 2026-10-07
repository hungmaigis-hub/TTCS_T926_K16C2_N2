from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SupportRequestCreate(BaseModel):
    """
    Schema nhận dữ liệu từ sinh viên khi gửi yêu cầu hỗ trợ.
    Không cần truyền `trang_thai` và `ngay_tao` (backend tự gán tự động).
    """
    ma_ho_so: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mã hồ sơ sinh viên",
        examples=["HS001"]
    )
    loai_yeu_cau: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Loại yêu cầu hỗ trợ (Giấy tờ thực tập, Chứng nhận, Kỹ thuật, Trợ cấp,...)",
        examples=["Giấy tờ thực tập"]
    )
    tieu_de: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Tiêu đề yêu cầu hỗ trợ",
        examples=["Xin giấy xác nhận hoàn thành đợt thực tập"]
    )
    noi_dung: str = Field(
        ...,
        min_length=5,
        description="Nội dung chi tiết yêu cầu hỗ trợ",
        examples=["Em cần xin giấy xác nhận hoàn thành 3 tháng thực tập để nộp về khoa CNTT trường Đại học Bách Khoa."]
    )


class SupportRequestResponse(BaseModel):
    """
    Schema trả về cho frontend sau khi tiếp nhận yêu cầu hỗ trợ thành công.
    """
    ma_yeu_cau: int = Field(..., description="Mã định danh yêu cầu")
    ma_ho_so: str = Field(..., description="Mã hồ sơ sinh viên")
    loai_yeu_cau: str = Field(..., description="Loại yêu cầu hỗ trợ")
    tieu_de: str = Field(..., description="Tiêu đề yêu cầu")
    noi_dung: str = Field(..., description="Nội dung chi tiết")
    trang_thai: str = Field(..., description="Trạng thái xử lý (mặc định ChoXuLy)")
    ngay_tao: datetime = Field(..., description="Thời gian tạo tự động")

    model_config = ConfigDict(from_attributes=True)


class SupportRequestMessageResponse(BaseModel):
    """
    Schema chuẩn RESTful bọc kết quả kèm thông điệp phản hồi cho Frontend.
    """
    message: str = Field(..., description="Thông báo trạng thái")
    data: SupportRequestResponse = Field(..., description="Dữ liệu yêu cầu vừa tạo")
