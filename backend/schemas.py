from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Union
from datetime import date, datetime, time
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

class InternRegisterRequest(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    mat_khau: str = Field(..., min_length=6, max_length=100)
    vai_tro: Optional[str] = Field(default="ThucTapSinh")
    so_dien_thoai: Optional[str] = Field(default=None)
    chuyen_nganh: Optional[str] = Field(default=None, max_length=100)
    ma_truong: Optional[int] = Field(default=None, gt=0)

    @field_validator('vai_tro')
    def validate_vai_tro(cls, value: Optional[str]):
        if not value or not value.strip():
            return "ThucTapSinh"
        cleaned = value.strip()
        mapping = {
            "intern": "ThucTapSinh",
            "thuctapsinh": "ThucTapSinh",
            "ThucTapSinh": "ThucTapSinh",
            "mentor": "Mentor",
            "Mentor": "Mentor",
            "university": "NhaTruong",
            "nhatruong": "NhaTruong",
            "NhaTruong": "NhaTruong",
            "admin": "Admin",
            "Admin": "Admin",
            "hr": "HR",
            "HR": "HR"
        }
        return mapping.get(cleaned, cleaned)

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

    @field_validator('mat_khau')
    def validate_mat_khau(cls, value: str):
        cleaned = value.strip()
        if len(cleaned) < 6:
            raise ValueError("Mật khẩu phải có tối thiểu 6 ký tự")
        return cleaned

    @field_validator('so_dien_thoai')
    def validate_so_dien_thoai(cls, value: Optional[str]):
        if not value or not value.strip():
            return None
        cleaned = value.strip()
        if not re.match(r"^(0|\+84)[0-9]{9}$|^[0-9]{10}$", cleaned):
            raise ValueError("Số điện thoại không hợp lệ (phải gồm 10 chữ số)")
        return cleaned


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    mat_khau: str = Field(..., min_length=1)

    @field_validator('email')
    def validate_email(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Email không được để trống")
        return cleaned

    @field_validator('mat_khau')
    def validate_mat_khau(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Mật khẩu không được để trống")
        return cleaned


class UserAuthData(BaseModel):
    ma_nguoi_dung: int
    ho_ten: str
    email: str
    vai_tro: str
    so_dien_thoai: Optional[str] = None
    ma_ho_so: Optional[int] = None


class AuthResponse(BaseModel):
    status_code: int = 200
    message: str
    data: Optional[UserAuthData] = None


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


class ReportItemData(BaseModel):
    """Chi tiết báo cáo tuần kèm thông tin sinh viên, mentor và nhiệm vụ liên quan"""
    ma_bao_cao: int
    ma_ho_so: int
    ma_nguoi_dung: Optional[int] = None
    ho_ten_sinh_vien: Optional[str] = None
    email_sinh_vien: Optional[str] = None
    ma_mentor: Optional[int] = None
    ho_ten_mentor: Optional[str] = None
    ma_nhiem_vu: Optional[int] = None
    ten_nhiem_vu: Optional[str] = None
    tuan_so: int
    noi_dung_cong_viec: str
    ket_qua_dat_duoc: Optional[str] = None
    phan_hoi_mentor: Optional[str] = None
    thoi_gian_nop: Optional[str] = None


class ReportPagination(BaseModel):
    """Thông tin phân trang danh sách báo cáo"""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class ReportListData(BaseModel):
    """Cấu trúc dữ liệu trả về cho danh sách báo cáo kèm phân trang"""
    items: List[ReportItemData]
    pagination: ReportPagination


class ReportListResponse(BaseModel):
    """Response chuẩn trả về cho GET /api/v1/reports"""
    status_code: int = 200
    message: str = "Lấy danh sách báo cáo tuần thành công"
    data: ReportListData


class ReportFeedbackRequest(BaseModel):
    """Request body cho POST /api/v1/reports/{id}/feedback"""
    phan_hoi_mentor: str = Field(..., min_length=1, description="Nội dung phản hồi hoặc ghi nhận của mentor")
    ma_mentor: Optional[int] = Field(default=None, gt=0, description="Mã người dùng của mentor gửi phản hồi (tùy chọn)")

    @field_validator('phan_hoi_mentor')
    def validate_phan_hoi(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nội dung phản hồi không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned


class ReportFeedbackResponse(BaseModel):
    """Response chuẩn trả về cho POST /api/v1/reports/{id}/feedback"""
    status_code: int = 200
    message: str = "Gửi phản hồi báo cáo tuần thành công"
    data: Optional[ReportItemData] = None


# ==============================================================
# SCHEMAS CHO ENDPOINT TỔNG HỢP ĐÁNH GIÁ (GET /api/v1/evaluations/summary)
# ==============================================================

class GradeDistribution(BaseModel):
    """Phân bổ xếp loại đánh giá"""
    XuatSac: int = 0
    Gioi: int = 0
    Kha: int = 0
    TrungBinh: int = 0
    Yeu: int = 0


class UniversityEvaluationStat(BaseModel):
    """Thống kê kết quả đánh giá theo từng trường đại học"""
    ma_truong: Optional[int] = None
    ten_truong: str
    so_luong_danh_gia: int
    diem_trung_binh: float


class EvaluationSummaryStats(BaseModel):
    """Tổng hợp chỉ số KPI toàn diện của đợt thực tập"""
    tong_so_ho_so: int
    tong_so_danh_gia: int
    diem_ky_nang_tb: float
    diem_thai_do_tb: float
    diem_tong_ket_tb: float
    so_luong_de_xuat_tuyen_dung: int
    ty_le_de_xuat_tuyen_dung: float
    phan_bo_xep_loai: GradeDistribution
    thong_ke_theo_truong: List[UniversityEvaluationStat]


class EvaluationDetailItem(BaseModel):
    """Thông tin chi tiết một bản đánh giá kèm hồ sơ và trường đại học"""
    ma_danh_gia: int
    ma_ho_so: int
    ho_ten: Optional[str] = None
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    ma_truong: Optional[int] = None
    ten_truong: Optional[str] = None
    trang_thai_thuc_tap: Optional[str] = None
    loai_danh_gia: str
    diem_ky_nang: float
    diem_thai_do: float
    diem_trung_binh: float
    xep_loai: str
    nhan_xet_chi_tiet: Optional[str] = None
    de_xuat_tuyen_chinh_thuc: bool
    nguoi_danh_gia: Optional[str] = None


class EvaluationPagination(BaseModel):
    """Thông tin phân trang danh sách đánh giá"""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class EvaluationSummaryData(BaseModel):
    """Cấu trúc dữ liệu trả về của Evaluation Summary"""
    summary: EvaluationSummaryStats
    items: List[EvaluationDetailItem]
    pagination: EvaluationPagination


class EvaluationSummaryResponse(BaseModel):
    """Response chuẩn trả về cho endpoint GET /api/v1/evaluations/summary"""
    status_code: int = 200
    message: str = "Lấy dữ liệu tổng hợp đánh giá thành công"
    data: EvaluationSummaryData


# ==============================================================
# SCHEMAS CHO BÁO CÁO CHẤM CÔNG (ATTENDANCE REPORTS API)
# ==============================================================

class AttendanceReportItem(BaseModel):
    """Thông tin tổng hợp chấm công của từng thực tập sinh"""
    ma_ho_so: int
    ma_nguoi_dung: int
    ho_ten: str
    email: str
    ma_phong_ban: Optional[int] = None
    ten_phong_ban: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    so_ngay_di_lam: int = 0
    so_lan_di_muon: int = 0
    so_ngay_nghi: int = 0


class AttendanceReportSummary(BaseModel):
    """Tổng hợp KPI chấm công toàn bộ phòng ban / kỳ báo cáo"""
    thang: Optional[int] = None
    nam: int
    ma_phong_ban: Optional[int] = None
    ten_phong_ban: Optional[str] = None
    tong_so_thuc_tap_sinh: int = 0
    tong_so_ngay_di_lam: int = 0
    tong_so_lan_di_muon: int = 0
    tong_so_ngay_nghi: int = 0
    ty_le_di_muon: float = 0.0
    trung_binh_ngay_cong: float = 0.0


class AttendancePagination(BaseModel):
    """Thông tin phân trang báo cáo chấm công"""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class AttendanceReportData(BaseModel):
    """Dữ liệu phản hồi báo cáo chấm công"""
    summary: AttendanceReportSummary
    items: List[AttendanceReportItem] = []
    pagination: AttendancePagination


class AttendanceReportResponse(BaseModel):
    """Response bọc chuẩn trả về cho client"""
    status_code: int = 200
    message: str
    data: AttendanceReportData


# ==============================================================
# SCHEMAS CHO TẠO ĐÁNH GIÁ THỰC TẬP SINH (POST /api/v1/evaluations)
# ==============================================================

class EvaluationCreate(BaseModel):
    """Schema tạo mới đánh giá thực tập sinh (POST /api/v1/evaluations)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    ma_nguoi_danh_gia: int = Field(..., gt=0, description="Mã người đánh giá")
    loai_danh_gia: str = Field(..., description="Loại đánh giá: GiuaKy hoặc CuoiKy")
    diem_ky_nang: float = Field(..., ge=0.0, le=10.0, description="Điểm kỹ năng chuyên môn (0.0 - 10.0)")
    diem_thai_do: float = Field(..., ge=0.0, le=10.0, description="Điểm thái độ kỷ luật (0.0 - 10.0)")
    nhan_xet: Optional[str] = Field(default=None, description="Nhận xét chi tiết")
    nhan_xet_chi_tiet: Optional[str] = Field(default=None, description="Nhận xét chi tiết (alias)")
    de_xuat_tuyen_dung: Optional[bool] = Field(default=None, description="Đề xuất tuyển dụng chính thức")
    de_xuat_tuyen_chinh_thuc: Optional[bool] = Field(default=None, description="Đề xuất tuyển dụng chính thức (alias)")

    @field_validator('loai_danh_gia')
    def validate_loai_danh_gia(cls, v: str):
        cleaned = v.strip()
        if cleaned not in ["GiuaKy", "CuoiKy"]:
            raise ValueError("Loại đánh giá phải là 'GiuaKy' hoặc 'CuoiKy'")
        return cleaned

    def get_nhan_xet(self) -> Optional[str]:
        if self.nhan_xet is not None:
            cleaned = self.nhan_xet.strip()
            return cleaned if cleaned else None
        if self.nhan_xet_chi_tiet is not None:
            cleaned = self.nhan_xet_chi_tiet.strip()
            return cleaned if cleaned else None
        return None

    def get_de_xuat(self) -> bool:
        if self.de_xuat_tuyen_dung is not None:
            return bool(self.de_xuat_tuyen_dung)
        if self.de_xuat_tuyen_chinh_thuc is not None:
            return bool(self.de_xuat_tuyen_chinh_thuc)
        return False


class EvaluationItemData(BaseModel):
    ma_danh_gia: int
    ma_ho_so: int
    ma_nguoi_danh_gia: int
    ten_nguoi_danh_gia: Optional[str] = None
    loai_danh_gia: str
    diem_ky_nang: float
    diem_thai_do: float
    diem_trung_binh: float
    xep_loai: str
    nhan_xet_chi_tiet: Optional[str] = None
    de_xuat_tuyen_chinh_thuc: bool = False


class EvaluationCreateResponse(BaseModel):
    status_code: int = 201
    message: str = "Tạo đánh giá thực tập sinh thành công"
    data: Optional[EvaluationItemData] = None


# ==============================================================
# SCHEMAS CHO ĐIỂM DANH / CHẤM CÔNG (CHECK-IN & CHECK-OUT API)
# ==============================================================

class CheckInRequest(BaseModel):
    """Schema yêu cầu check-in ca làm việc (POST /api/v1/attendance/check-in)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    thoi_gian_checkin: Optional[datetime] = Field(default=None, description="Thời điểm check-in (ISO 8601). Mặc định lấy thời gian hiện tại nếu không truyền.")
    phuong_thuc: Optional[str] = Field(default="Web", description="Phương thức chấm công: Web, QR, The")
    ghi_chu: Optional[str] = Field(default=None, description="Ghi chú thêm (lý do muộn, on-site...)")


class CheckOutRequest(BaseModel):
    """Schema yêu cầu check-out kết thúc ca làm việc (POST /api/v1/attendance/check-out)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    thoi_gian_checkout: Optional[datetime] = Field(default=None, description="Thời điểm check-out (ISO 8601). Mặc định lấy thời gian hiện tại nếu không truyền.")
    ghi_chu: Optional[str] = Field(default=None, description="Ghi chú thêm")


class AttendanceItemData(BaseModel):
    """Dữ liệu chi tiết bản ghi chấm công trả về cho client"""
    ma_cham_cong: int
    ma_ho_so: int
    ngay_cham_cong: str
    thoi_gian_checkin: Optional[str] = None
    thoi_gian_checkout: Optional[str] = None
    gio_check_in: Optional[str] = None
    gio_check_out: Optional[str] = None
    trang_thai: str = "DungGio"
    phuong_thuc: str = "Web"
    ghi_chu: Optional[str] = None


class CheckInResponse(BaseModel):
    """Phản hồi sau khi check-in thành công (HTTP 201 Created)"""
    status_code: int = 201
    message: str = "Check-in thành công"
    data: Optional[AttendanceItemData] = None


class CheckOutResponse(BaseModel):
    """Phản hồi sau khi check-out thành công (HTTP 200 OK)"""
    status_code: int = 200
    message: str = "Check-out thành công"
    data: Optional[AttendanceItemData] = None


# ==============================================================
# SCHEMAS CHO ĐƠN XIN NGHỈ PHÉP (LEAVE REQUESTS API)
# ==============================================================

class LeaveRequestCreate(BaseModel):
    """Schema yêu cầu tạo đơn xin nghỉ phép (POST /api/v1/leave-requests)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    tu_ngay: date = Field(..., description="Ngày bắt đầu nghỉ")
    den_ngay: date = Field(..., description="Ngày kết thúc nghỉ")
    ly_do: str = Field(..., min_length=1, max_length=255, description="Lý do xin nghỉ")
    trang_thai: Optional[str] = Field(default="Chờ duyệt", description="Trạng thái đơn: Chờ duyệt, Đã duyệt, Từ chối")

    @field_validator("tu_ngay")
    def validate_tu_ngay(cls, v: date):
        if v < date.today():
            raise ValueError("Ngày bắt đầu nghỉ (tu_ngay) không được nhỏ hơn ngày hiện tại")
        return v

    @field_validator("ly_do")
    def validate_ly_do(cls, v: str):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Lý do xin nghỉ không được để trống")
        return cleaned

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.den_ngay < self.tu_ngay:
            raise ValueError("Ngày kết thúc nghỉ (den_ngay) phải lớn hơn hoặc bằng ngày bắt đầu nghỉ (tu_ngay)")
        return self


class LeaveRequestItemData(BaseModel):
    """Dữ liệu chi tiết đơn xin nghỉ trả về cho client"""
    ma_don: int
    ma_ho_so: int
    tu_ngay: str
    den_ngay: str
    so_ngay: int
    ly_do: str
    trang_thai: str = "Chờ duyệt"
    ngay_tao: Optional[str] = None


class LeaveRequestCreateResponse(BaseModel):
    """Phản hồi sau khi tạo đơn xin nghỉ thành công (HTTP 201 Created)"""
    status_code: int = 201
    message: str = "Tạo đơn xin nghỉ thành công"
    data: Optional[LeaveRequestItemData] = None


# ==============================================================
# SCHEMAS CHO QUẢN LÝ NHIỆM VỤ (TASKS API)
# ==============================================================
class TaskCreate(BaseModel):
    """Schema cho request tạo mới nhiệm vụ thực tập (POST /api/v1/tasks)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập liên kết")
    tieu_de: Optional[str] = Field(default=None, max_length=150, description="Tiêu đề nhiệm vụ")
    ten_nhiem_vu: Optional[str] = Field(default=None, max_length=150, description="Tên nhiệm vụ (alias của tieu_de)")
    mo_ta: Optional[str] = Field(default=None, description="Mô tả chi tiết nội dung nhiệm vụ")
    han_hoan_thanh: date = Field(..., description="Hạn hoàn thành nhiệm vụ (YYYY-MM-DD)")
    tien_do_phantram: Optional[int] = Field(default=0, ge=0, le=100, description="Tiến độ hoàn thành (từ 0% đến 100%)")
    trang_thai: Optional[str] = Field(default="Chưa bắt đầu", description="Trạng thái nhiệm vụ")

    @model_validator(mode="after")
    def validate_task_fields(self):
        title = self.tieu_de or self.ten_nhiem_vu
        if not title or not title.strip():
            raise ValueError("Tiêu đề nhiệm vụ không được để trống hoặc chỉ chứa khoảng trắng")
        self.tieu_de = title.strip()
        self.ten_nhiem_vu = title.strip()
        if not self.trang_thai or not self.trang_thai.strip():
            self.trang_thai = "Chưa bắt đầu"
        else:
            self.trang_thai = self.trang_thai.strip()
        if self.tien_do_phantram is None:
            self.tien_do_phantram = 0
        return self


class TaskDetailData(BaseModel):
    """Cấu trúc dữ liệu chi tiết của một nhiệm vụ"""
    ma_nhiem_vu: int
    ma_ho_so: int
    tieu_de: str
    ten_nhiem_vu: str
    mo_ta: Optional[str] = None
    han_hoan_thanh: Optional[str] = None
    tien_do_phantram: int = 0
    trang_thai: str = "Chưa bắt đầu"


class TaskCreateResponse(BaseModel):
    """Phản hồi sau khi tạo nhiệm vụ thành công (HTTP 201 Created)"""
    status_code: int = 201
    message: str = "Tạo nhiệm vụ mới thành công"
    data: Optional[TaskDetailData] = None


class TaskProgressUpdate(BaseModel):
    """Schema cập nhật tiến độ nhiệm vụ (PATCH)"""
    tien_do_phantram: int = Field(
        ...,
        ge=0,
        le=100,
        description="Tiến độ hoàn thành của nhiệm vụ (từ 0% đến 100%)"
    )


class TaskProgressResponse(BaseModel):
    status_code: int = 200
    message: str
    data: Optional[TaskDetailData] = None


# ==============================================================
# SCHEMAS CHO CA LÀM VIỆC (SCHEDULES / WORK SHIFTS API)
# ==============================================================

class ScheduleCreate(BaseModel):
    """Schema tạo mới ca làm việc (POST /api/v1/schedules)"""
    ten_ca: str = Field(..., min_length=1, max_length=100, description="Tên ca làm việc")
    gio_bat_dau: time = Field(..., description="Thời gian bắt đầu ca làm việc (HH:MM hoặc HH:MM:SS)")
    gio_ket_thuc: time = Field(..., description="Thời gian kết thúc ca làm việc (HH:MM hoặc HH:MM:SS)")
    cac_ngay_trong_tuan: Union[List[str], str] = Field(..., description="Các ngày áp dụng trong tuần")
    ghi_chu: Optional[str] = Field(default=None, max_length=255, description="Ghi chú thêm")
    trang_thai: Optional[str] = Field(default="HoatDong", description="Trạng thái ca làm việc (HoatDong, TamNgung)")

    @field_validator('ten_ca')
    def validate_ten_ca(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên ca làm việc không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned

    @field_validator('cac_ngay_trong_tuan')
    def validate_cac_ngay(cls, value: Union[List[str], str]):
        if isinstance(value, list):
            cleaned_list = [str(day).strip() for day in value if str(day).strip()]
            if not cleaned_list:
                raise ValueError("Danh sách các ngày trong tuần không được để trống")
            return ", ".join(cleaned_list)
        elif isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("Các ngày trong tuần không được để trống")
            return cleaned
        raise ValueError("Định dạng các ngày trong tuần không hợp lệ")

    @model_validator(mode="after")
    def validate_shift_times(self):
        if self.gio_ket_thuc <= self.gio_bat_dau:
            raise ValueError("Giờ kết thúc phải lớn hơn giờ bắt đầu (gio_ket_thuc > gio_bat_dau)")
        return self


class ScheduleData(BaseModel):
    """Dữ liệu chi tiết của ca làm việc"""
    ma_ca: int
    ten_ca: str
    gio_bat_dau: str
    gio_ket_thuc: str
    cac_ngay_trong_tuan: str
    ghi_chu: Optional[str] = None
    trang_thai: Optional[str] = "HoatDong"
    ngay_tao: Optional[str] = None


class ScheduleCreateResponse(BaseModel):
    """Response trả về khi tạo ca làm việc thành công (HTTP 201)"""
    status_code: int = 201
    message: str = "Tạo ca làm việc thành công"
    data: Optional[ScheduleData] = None


# ==============================================================
# SCHEMAS CHO PHỤ CẤP THỰC TẬP SINH (ALLOWANCES API)
# ==============================================================

class AllowanceItem(BaseModel):
    """Thông tin chi tiết một khoản phụ cấp"""
    ma_phu_cap: int
    ma_ho_so: int
    thang_nam: str
    so_tien: float
    trang_thai_chi_tra: str


class AllowanceSummary(BaseModel):
    """Tổng hợp tài chính phụ cấp"""
    tong_tien_da_nhan: float
    tong_tien_cho_giai_ngan: float
    tong_tien_phu_cap: float
    so_khoan_da_nhan: int
    so_khoan_cho_giai_ngan: int


class AllowanceDetailData(BaseModel):
    """Dữ liệu chi tiết danh sách phụ cấp trả về cho Client"""
    ma_ho_so: int
    ho_ten: Optional[str] = None
    email: Optional[str] = None
    summary: AllowanceSummary
    danh_sach_phu_cap: List[AllowanceItem]
    cac_khoan_da_nhan: List[AllowanceItem]
    cac_khoan_cho_giai_ngan: List[AllowanceItem]


class AllowanceResponse(BaseModel):
    """Response chuẩn trả về khi truy vấn danh sách phụ cấp thành công (HTTP 200)"""
    status_code: int = 200
    message: str = "Lấy danh sách phụ cấp thành công"
    data: Optional[AllowanceDetailData] = None






