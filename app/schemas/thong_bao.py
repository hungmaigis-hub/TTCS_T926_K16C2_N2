from datetime import datetime
from typing import Optional, List, Union, Any
from pydantic import BaseModel, Field, ConfigDict


class ThongBaoBase(BaseModel):
    tieu_de: str = Field(..., max_length=255, description="Tiêu đề thông báo")
    noi_dung: str = Field(..., description="Nội dung chi tiết thông báo")
    loai_thong_bao: Optional[str] = Field("CHUNG", max_length=50, description="Loại thông báo (LICH_TRINH, CONG_VIEC, HE_THONG, CHUNG)")


class ThongBaoCreate(ThongBaoBase):
    ma_nguoi_nhan: Union[int, str] = Field(..., description="ID người nhận thông báo")


class ThongBaoUpdate(BaseModel):
    da_doc: Optional[bool] = Field(None, description="Trạng thái đã đọc (True / False)")
    tieu_de: Optional[str] = Field(None, max_length=255)
    noi_dung: Optional[str] = None
    loai_thong_bao: Optional[str] = None


class ThongBaoResponse(BaseModel):
    ma_thong_bao: int = Field(..., description="Mã định danh thông báo")
    id: Optional[Union[int, str]] = Field(None, description="Alias tương thích id cho frontend")
    ma_nguoi_nhan: Union[int, str] = Field(..., description="Mã người nhận")
    tieu_de: str
    noi_dung: str
    loai_thong_bao: str
    da_doc: bool
    ngay_tao: datetime

    # Hỗ trợ cả Pydantic v1 và v2
    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **data):
        # Tự động gán id = ma_thong_bao nếu id chưa có để frontend tiện sử dụng
        if "id" not in data or data["id"] is None:
            if "ma_thong_bao" in data:
                data["id"] = data["ma_thong_bao"]
            elif hasattr(data, "ma_thong_bao"):
                data["id"] = getattr(data, "ma_thong_bao")
        super().__init__(**data)


class ThongBaoListResponse(BaseModel):
    """
    Schema trả về cho endpoint GET /my
    Bao gồm danh sách thông báo và số lượng chưa đọc (để hiển thị badge ở Header)
    """
    items: List[ThongBaoResponse]
    total: int = Field(..., description="Tổng số thông báo")
    unread_count: int = Field(..., description="Số lượng thông báo chưa đọc (để hiển thị badge)")
    limit: int
    skip: int

    model_config = ConfigDict(from_attributes=True)
