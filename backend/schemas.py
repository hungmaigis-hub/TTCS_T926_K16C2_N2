from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import date
import re

# ==============================================================
# SCHEMA CHO REQUEST TẠO MỚI HỒ SƠ THỰC TẬP SINH (POST)
# ==============================================================
class InternCreate(BaseModel):
    # Thông tin tài khoản sinh viên (bảng NGUOI_DUNG)
    ho_ten: str = Field(..., min_length=1, max_length=100, description="Họ và tên sinh viên")
    email: str = Field(..., min_length=1, max_length=100, description="Địa chỉ email")
    so_dien_thoai: Optional[str] = Field(default=None, description="Số điện thoại liên lạc")
    
    # Thông tin hồ sơ thực tập (bảng HO_SO_THUC_TAP)
    chuyen_nganh: Optional[str] = Field(default=None, max_length=100, description="Chuyên ngành đào tạo")
    ma_truong: Optional[int] = Field(default=None, description="Mã trường đại học")
    ma_chuong_trinh: Optional[int] = Field(default=None, description="Mã chương trình thực tập")
    ma_mentor: Optional[int] = Field(default=None, description="Mã mentor hướng dẫn")
    trang_thai_xet_duyet: Optional[str] = Field(default="ChoDuyet", description="Trạng thái duyệt: ChoDuyet, DaDuyet, TuChoi")
    trang_thai_thuc_tap: Optional[str] = Field(default="DangThucTap", description="Trạng thái thực tập: DangThucTap, HoanThanh, ThoiHoc")

    @field_validator('ho_ten')
    def validate_ho_ten(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Họ tên không được để trống hoặc chỉ chứa khoảng trắng")
        if not re.match(r"^[a-zA-Z\s\u00C0-\u1EF9]+$", cleaned):
            raise ValueError("Họ tên không hợp lệ (chỉ được chứa chữ cái)")
        return cleaned

    @field_validator('email')
    def validate_email(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Email không được để trống hoặc chỉ chứa khoảng trắng")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", cleaned):
            raise ValueError("Email không đúng định dạng hợp lệ")
        return cleaned

    @field_validator('so_dien_thoai')
    def validate_so_dien_thoai(cls, value: Optional[str]):
        if not value or not value.strip():
            return None
        cleaned = value.strip()
        if not re.match(r"^(0|\+84)[0-9]{9}$|^[0-9]{10}$", cleaned):
            raise ValueError("Số điện thoại không hợp lệ (phải gồm 10 chữ số)")
        return cleaned

    @field_validator('trang_thai_xet_duyet')
    def validate_trang_thai_xet_duyet(cls, value: Optional[str]):
        if value is None:
            return "ChoDuyet"
        cleaned = value.strip()
        valid = ["ChoDuyet", "DaDuyet", "TuChoi"]
        if cleaned not in valid:
            raise ValueError(f"Trạng thái xét duyệt không hợp lệ. Chỉ chấp nhận: {', '.join(valid)}")
        return cleaned

    @field_validator('trang_thai_thuc_tap')
    def validate_trang_thai_thuc_tap(cls, value: Optional[str]):
        if value is None:
            return "DangThucTap"
        cleaned = value.strip()
        valid = ["DangThucTap", "HoanThanh", "ThoiHoc"]
        if cleaned not in valid:
            raise ValueError(f"Trạng thái thực tập không hợp lệ. Chỉ chấp nhận: {', '.join(valid)}")
        return cleaned


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
# SCHEMA CHO REQUEST CẬP NHẬT TRẠNG THÁI DUYỆT HỒ SƠ (PATCH)
# ==============================================================
class InternApprovalUpdate(BaseModel):
    """Schema cập nhật trạng thái xét duyệt hồ sơ thực tập sinh (PATCH)"""
    trang_thai_xet_duyet: Optional[str] = Field(default=None, description="Trạng thái: ChoDuyet, DaDuyet, TuChoi")
    trang_thai_duyet: Optional[str] = Field(default=None, description="Alias cho trang_thai_xet_duyet")
    ghi_chu: Optional[str] = Field(default=None, max_length=500, description="Ghi chú / nhận xét hoặc lý do từ chối")

    @field_validator('trang_thai_xet_duyet', 'trang_thai_duyet')
    def validate_status(cls, value: Optional[str]):
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Trạng thái xét duyệt không được để trống hoặc chỉ chứa khoảng trắng")
        valid_statuses = ["ChoDuyet", "DaDuyet", "TuChoi"]
        if cleaned not in valid_statuses:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận một trong các giá trị: {', '.join(valid_statuses)}")
        return cleaned

    @field_validator('ghi_chu')
    def validate_ghi_chu(cls, value: Optional[str]):
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None

    def get_status(self) -> str:
        status = self.trang_thai_xet_duyet or self.trang_thai_duyet
        if not status:
            raise ValueError("Vui lòng cung cấp 'trang_thai_duyet' hoặc 'trang_thai_xet_duyet'")
        return status


# ==============================================================
# SCHEMA CHO REQUEST XÁC NHẬN KÝ HỢP ĐỒNG (PATCH)
# ==============================================================
class ContractConfirmRequest(BaseModel):
    """Schema cho request xác nhận ký hợp đồng điện tử (PATCH)"""
    trang_thai: Optional[str] = Field(default="DaXacNhan", description="Trạng thái hợp đồng: DaXacNhan hoặc ChuaXacNhan")
    trang_thai_thuc_tap: Optional[str] = Field(default="DangThucTap", description="Trạng thái thực tập: ChuaThucTap, DangThucTap, HoanThanh, ThoiHoc")
    ngay_ky: Optional[date] = Field(default=None, description="Ngày ký (mặc định hôm nay nếu để trống)")
    ghi_chu: Optional[str] = Field(default=None, max_length=500, description="Ghi chú xác nhận / mã OTP chữ ký")

    @field_validator('trang_thai')
    def validate_trang_thai(cls, value: Optional[str]):
        if value is None:
            return "DaXacNhan"
        cleaned = value.strip()
        if not cleaned:
            return "DaXacNhan"
        valid_statuses = ["ChuaXacNhan", "DaXacNhan"]
        if cleaned not in valid_statuses:
            raise ValueError(f"Trạng thái hợp đồng không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}")
        return cleaned

    @field_validator('trang_thai_thuc_tap')
    def validate_trang_thai_thuc_tap(cls, value: Optional[str]):
        if value is None:
            return "DangThucTap"
        cleaned = value.strip()
        if not cleaned:
            return "DangThucTap"
        valid_statuses = ["ChuaThucTap", "DangThucTap", "HoanThanh", "ThoiHoc"]
        if cleaned not in valid_statuses:
            raise ValueError(f"Trạng thái thực tập không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}")
        return cleaned

    @field_validator('ghi_chu')
    def validate_ghi_chu(cls, value: Optional[str]):
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None


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


class InternCreateResponse(BaseModel):
    status_code: int = 201
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


class DocumentUploadResponse(BaseModel):
    status_code: int = 201
    message: str
    data: DocumentItem

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


class ProgramTimelineUpdate(BaseModel):
    """Schema cập nhật thời gian chương trình thực tập (PATCH /api/v1/programs/{id}/timeline)"""
    ngay_bat_dau: Optional[date] = Field(default=None, description="Ngày bắt đầu mới của chương trình")
    ngay_ket_thuc: Optional[date] = Field(default=None, description="Ngày kết thúc mới của chương trình")

    @model_validator(mode='after')
    def validate_timeline(self):
        if self.ngay_bat_dau is None and self.ngay_ket_thuc is None:
            raise ValueError("Cần cung cấp ít nhất một trường: ngay_bat_dau hoặc ngay_ket_thuc")
        if self.ngay_bat_dau and self.ngay_ket_thuc:
            if self.ngay_ket_thuc <= self.ngay_bat_dau:
                raise ValueError("Ngày kết thúc phải lớn hơn ngày bắt đầu")
        return self


class ProgramTimelineResponse(BaseModel):
    status_code: int = 200
    message: str
    data: Optional[ProgramDetailData] = None


# ==============================================================
# SCHEMAS CHO NHIỆM VỤ THỰC TẬP (TASKS API)
# ==============================================================
class TaskProgressUpdate(BaseModel):
    """Schema cập nhật tiến độ nhiệm vụ (PATCH)"""
    tien_do_phantram: int = Field(
        ...,
        ge=0,
        le=100,
        description="Tiến độ hoàn thành của nhiệm vụ (từ 0% đến 100%)"
    )


class TaskDetailData(BaseModel):
    ma_nhiem_vu: int
    ma_ho_so: int
    ten_nhiem_vu: str
    mo_ta: Optional[str] = None
    han_hoan_thanh: Optional[str] = None
    tien_do_phantram: int
    trang_thai: str


class TaskProgressResponse(BaseModel):
    status_code: int = 200
    message: str
    data: Optional[TaskDetailData] = None


# ==============================================================
# SCHEMAS CHO LỊCH TRÌNH VÀ NHIỆM VỤ (MY-SCHEDULE API)
# ==============================================================

class TaskItemResponse(BaseModel):
    ma_nhiem_vu: int
    ma_ho_so: int
    ten_nhiem_vu: str
    mo_ta: Optional[str] = None
    han_hoan_thanh: Optional[str] = None
    tien_do_phantram: int = 0
    trang_thai: str = "Moi"


class MyScheduleData(BaseModel):
    ma_ho_so: int
    ho_ten: Optional[str] = None
    ten_chuong_trinh: Optional[str] = None
    ngay_bat_dau: Optional[str] = None
    ngay_ket_thuc: Optional[str] = None
    trang_thai_thuc_tap: Optional[str] = None
    danh_sach_nhiem_vu: List[TaskItemResponse] = []


class MyScheduleResponse(BaseModel):
    status_code: int = 200
    message: str
    data: Optional[MyScheduleData] = None


# ==============================================================
# SCHEMAS CHO BÁO CÁO TUẦN (REPORTS API)
# ==============================================================

class ReportCreate(BaseModel):
    """Schema tạo mới báo cáo tuần (POST /api/v1/reports)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    ma_nhiem_vu: Optional[int] = Field(default=None, gt=0, description="Mã nhiệm vụ liên kết (tùy chọn)")
    tuan_so: int = Field(..., ge=1, description="Số thứ tự tuần thực tập (>= 1)")
    noi_dung_cong_viec: str = Field(..., min_length=1, description="Nội dung công việc thực hiện trong tuần")
    ket_qua_dat_duoc: Optional[str] = Field(default=None, description="Kết quả hoặc sản phẩm đạt được")

    @field_validator('noi_dung_cong_viec')
    def validate_noi_dung(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nội dung công việc không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned

    @field_validator('ket_qua_dat_duoc')
    def validate_ket_qua(cls, value: Optional[str]):
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None


class ReportDetailData(BaseModel):
    ma_bao_cao: int
    ma_ho_so: int
    ma_nhiem_vu: Optional[int] = None
    tuan_so: int
    noi_dung_cong_viec: str
    ket_qua_dat_duoc: Optional[str] = None
    phan_hoi_mentor: Optional[str] = None
    thoi_gian_nop: Optional[str] = None


class ReportResponse(BaseModel):
    status_code: int = 201
    message: str
    data: Optional[ReportDetailData] = None


