from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TrangThaiYeuCau(str, Enum):
    CHO_XU_LY = "ChoXuLy"
    DANG_XU_LY = "DangXuLy"
    DA_XU_LY = "DaXuLy"
    TU_CHOI = "TuChoi"


class YeuCauHoTroBase(BaseModel):
    ma_ho_so: str = Field(..., example="HS001", description="Mã hồ sơ thực tập sinh")
    loai_yeu_cau: str = Field(..., example="GiayTo", description="Loại yêu cầu hỗ trợ (GiayTo, ChungNhan, KyThuat, PhuCap, Khac)")
    tieu_de: str = Field(..., min_length=1, max_length=255, example="Xin giấy xác nhận thực tập", description="Tiêu đề yêu cầu")
    noi_dung: str = Field(..., min_length=1, example="Em cần giấy xác nhận hoàn thành thực tập để nộp về trường.", description="Nội dung chi tiết yêu cầu")


class YeuCauHoTroCreate(YeuCauHoTroBase):
    pass


class YeuCauHoTroResponse(YeuCauHoTroBase):
    ma_yeu_cau: int
    trang_thai: str = "ChoXuLy"
    ngay_tao: datetime
    phan_hoi: Optional[str] = None
    ngay_xu_ly: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class YeuCauHoTroUpdateTrangThai(BaseModel):
    trang_thai: TrangThaiYeuCau = Field(..., description="Trạng thái mới của yêu cầu")
    phan_hoi: Optional[str] = Field(None, description="Nội dung phản hồi từ HR")
