from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TrangThaiYeuCau(str, Enum):
    CHO_XU_LY = "ChoXuLy"
    DANG_XU_LY = "DangXuLy"
    DA_XU_LY = "DaXuLy"
    TU_CHOI = "TuChoi"


class LoaiYeuCau(str, Enum):
    GIAY_TO = "GiayTo"           # Giấy xác nhận, giấy giới thiệu thực tập
    CHUNG_NHAN = "ChungNhan"     # Chứng nhận hoàn thành thực tập
    KY_THUAT = "KyThuat"         # Hỗ trợ kỹ thuật / tài khoản / phần mềm
    PHU_CAP = "PhuCap"           # Thắc mắc về phụ cấp / chấm công
    KHAC = "Khac"                # Các vấn đề phát sinh khác


class YeuCauHoTroBase(BaseModel):
    ma_ho_so: int = Field(..., description="Mã hồ sơ thực tập của sinh viên")
    loai_yeu_cau: str = Field(..., example="GiayTo", description="Loại yêu cầu hỗ trợ (GiayTo, ChungNhan, KyThuat, PhuCap, Khac)")
    tieu_de: str = Field(..., min_length=1, max_length=255, example="Xin cấp giấy xác nhận thực tập", description="Tiêu đề yêu cầu hỗ trợ")
    noi_dung: str = Field(..., min_length=1, example="Em cần xin giấy xác nhận hoàn thành thực tập 2 tháng để nộp cho nhà trường.", description="Nội dung chi tiết yêu cầu")


class YeuCauHoTroCreate(YeuCauHoTroBase):
    """Payload gửi lên từ Frontend khi sinh viên tạo yêu cầu hỗ trợ"""
    pass


class YeuCauHoTroResponse(YeuCauHoTroBase):
    """Dữ liệu trả về cho Frontend hiển thị"""
    ma_yeu_cau: int
    trang_thai: str = "ChoXuLy"
    ngay_tao: datetime
    phan_hoi: Optional[str] = None
    ngay_xu_ly: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class YeuCauHoTroUpdateTrangThai(BaseModel):
    """Dành cho HR duyệt/phản hồi yêu cầu (User Story 28)"""
    trang_thai: TrangThaiYeuCau = Field(..., description="Trạng thái cập nhật: ChoXuLy, DangXuLy, DaXuLy, TuChoi")
    phan_hoi: Optional[str] = Field(None, description="Nội dung phản hồi hoặc lý do từ HR")
