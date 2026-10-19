from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Union, Dict
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
    ma_chuong_trinh: Optional[int] = Field(default=None, description="Mã chương trình thực tập")
    ma_mentor: Optional[int] = Field(default=None, description="Mã mentor hướng dẫn")
    trang_thai_xet_duyet: Optional[str] = Field(default=None, description="Trạng thái xét duyệt: ChoDuyet, DaDuyet, TuChoi")
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

class ProgramListItem(BaseModel):
    ma_chuong_trinh: int
    ma_phong_ban: int
    ten_phong_ban: Optional[str] = None
    ten_chuong_trinh: str
    ngay_bat_dau: Optional[str] = None
    ngay_ket_thuc: Optional[str] = None
    mo_ta: Optional[str] = None
    thoi_luong_tuan: Optional[int] = None
    so_luong_sinh_vien: int = 0
    chi_tieu_sinh_vien: int = 50
    trang_thai: str = "Đang diễn ra"

class ProgramListResponse(BaseModel):
    status_code: int = 200
    message: str
    total: int
    data: List[ProgramListItem]

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
    vai_tro: Optional[str] = None

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
    ma_hop_dong: Optional[int] = None
    trang_thai_hop_dong: Optional[str] = None


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
    mentor: Optional[str] = None
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
    lop: Optional[str] = None
    ma_mentor: Optional[int] = None
    ten_mentor: Optional[str] = None
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


class AttendanceScanRequest(BaseModel):
    """Schema yêu cầu quét mã định danh chấm công (POST /api/v1/attendance/scan)"""
    ma_dinh_danh: str = Field(..., description="Mã định danh của thực tập sinh (mã hồ sơ, mã thẻ RFID hoặc mã QR)")
    phuong_thuc: Optional[str] = Field(default="QR/Card", description="Phương thức quét: QR, Card, QR/Card")
    thoi_gian_quet: Optional[datetime] = Field(default=None, description="Thời điểm quét mã (ISO 8601). Mặc định thời gian hiện tại.")
    ghi_chu: Optional[str] = Field(default=None, max_length=255, description="Ghi chú thêm")

    @field_validator('ma_dinh_danh')
    def validate_ma_dinh_danh(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Mã định danh không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned


class AttendanceScanResponseData(BaseModel):
    """Dữ liệu phản hồi chi tiết sau khi quét mã định danh thành công"""
    ma_cham_cong: int
    ma_ho_so: int
    ho_ten: Optional[str] = None
    ngay_cham_cong: str
    gio_checkin: Optional[str] = None
    gio_checkout: Optional[str] = None
    gio_check_in: Optional[str] = None
    gio_check_out: Optional[str] = None
    hanh_dong: str = Field(..., description="Hành động được ghi nhận: CHECK_IN hoặc CHECK_OUT")
    trang_thai: str = "DungGio"
    phuong_thuc: str = "QR/Card"
    ghi_chu: Optional[str] = None


class AttendanceScanResponse(BaseModel):
    """Phản hồi sau khi quét mã định danh chấm công thành công (HTTP 200 OK)"""
    status_code: int = 200
    message: str = "Quét mã chấm công thành công"
    data: Optional[AttendanceScanResponseData] = None


class RollCallRecordItem(BaseModel):
    """Chi tiết điểm danh từng sinh viên trong sổ điểm danh của Mentor"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    trang_thai: str = Field(default="DungGio", description="Trạng thái: DungGio, DiMuon, VangMat, VeSom")
    gio_check_in: Optional[str] = Field(default=None, description="Giờ vào lớp (HH:MM hoặc HH:MM:SS)")
    gio_check_out: Optional[str] = Field(default=None, description="Giờ ra lớp (HH:MM hoặc HH:MM:SS)")
    ghi_chu: Optional[str] = Field(default=None, description="Ghi chú đánh giá chuyên cần")


class RollCallRequest(BaseModel):
    """Yêu cầu lưu sổ điểm danh theo ca, khóa và lớp của Mentor"""
    ngay_cham_cong: date = Field(..., description="Ngày điểm danh")
    ca_lam_viec: Optional[str] = Field(default="Ca Sáng", description="Ca làm việc / buổi gặp mặt")
    ma_chuong_trinh: Optional[int] = Field(default=None, description="Mã chương trình / khóa thực tập")
    chuyen_nganh: Optional[str] = Field(default=None, description="Lớp hoặc chuyên ngành")
    lop: Optional[str] = Field(default=None, description="Lớp sinh hoạt cụ thể (ví dụ KTPM-K19A)")
    records: List[RollCallRecordItem] = Field(..., min_items=1, description="Danh sách điểm danh sinh viên")


class RollCallResponse(BaseModel):
    """Kết quả lưu sổ điểm danh của Mentor"""
    status_code: int = 200
    message: str = "Lưu điểm danh thành công"
    total_saved: int = 0
    data: Optional[List[dict]] = None


class ShiftCreateRequest(BaseModel):
    """Schema yêu cầu tạo mới ca làm việc / buổi gặp mặt (POST /api/v1/attendance/shifts)"""
    ten_ca: str = Field(..., min_length=1, max_length=100, description="Tên ca làm việc / buổi gặp mặt")
    gio_bat_dau: str = Field(..., description="Giờ bắt đầu (định dạng HH:MM hoặc HH:MM:SS)")
    gio_ket_thuc: str = Field(..., description="Giờ kết thúc (định dạng HH:MM hoặc HH:MM:SS)")
    cac_ngay_trong_tuan: Optional[str] = Field(default="Tất cả các ngày", description="Các ngày áp dụng trong tuần")
    ngay_dien_ra: Optional[str] = Field(default=None, description="Ngày diễn ra cụ thể (định dạng YYYY-MM-DD)")
    chuyen_nganh: Optional[str] = Field(default=None, description="Lớp hoặc chuyên ngành áp dụng")
    lop: Optional[str] = Field(default=None, description="Lớp sinh hoạt áp dụng (ví dụ KTPM-K19A)")
    ma_chuong_trinh: Optional[int] = Field(default=None, description="Mã chương trình thực tập")
    ghi_chu: Optional[str] = Field(default="", description="Ghi chú chi tiết ca làm việc")
    trang_thai: Optional[str] = Field(default="HoatDong", description="Trạng thái hoạt động")

    @field_validator("ten_ca")
    def validate_ten_ca(cls, v: str):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Tên ca làm việc / buổi gặp không được để trống")
        return cleaned

    @model_validator(mode="after")
    def validate_shift_times(self):
        try:
            t_start = datetime.strptime(self.gio_bat_dau[:5], "%H:%M").time()
        except Exception:
            raise ValueError("Giờ bắt đầu không đúng định dạng (HH:MM)")

        try:
            t_end = datetime.strptime(self.gio_ket_thuc[:5], "%H:%M").time()
        except Exception:
            raise ValueError("Giờ kết thúc không đúng định dạng (HH:MM)")

        if t_end <= t_start:
            raise ValueError("Giờ kết thúc ca làm việc phải lớn hơn giờ bắt đầu")
        return self


class ShiftCreateResponse(BaseModel):
    """Phản hồi sau khi tạo ca làm việc thành công (HTTP 201 Created)"""
    status_code: int = 201
    message: str = "Tạo ca làm việc / buổi gặp thành công"
    data: Optional[dict] = None


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
        if (self.den_ngay - self.tu_ngay).days + 1 > 3:
            raise ValueError("Số ngày xin nghỉ trong một đơn không được vượt quá 3 ngày (hạn mức tối đa toàn kỳ thực tập)")
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


class LeaveStatusUpdateRequest(BaseModel):
    """Schema cập nhật trạng thái đơn xin nghỉ phép (PATCH /api/v1/leave-requests/{id}/status)"""
    trang_thai: str = Field(..., description="Trạng thái phê duyệt: Đã duyệt hoặc Từ chối")
    phan_hoi: Optional[str] = Field(default=None, description="Lý do hoặc phản hồi của Mentor/HR")


class LeaveStatusUpdateResponse(BaseModel):
    """Phản hồi sau khi cập nhật trạng thái đơn nghỉ phép"""
    status_code: int = 200
    message: str = "Cập nhật trạng thái đơn xin nghỉ thành công"
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
    ngay_chi_tra: Optional[str] = None
    ghi_chu: Optional[str] = None


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
    lop: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    ten_chuong_trinh: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    summary: AllowanceSummary
    danh_sach_phu_cap: List[AllowanceItem]
    cac_khoan_da_nhan: List[AllowanceItem]
    cac_khoan_cho_giai_ngan: List[AllowanceItem]


class AllowanceResponse(BaseModel):
    """Response chuẩn trả về khi truy vấn danh sách phụ cấp thành công (HTTP 200)"""
    status_code: int = 200
    message: str = "Lấy danh sách phụ cấp thành công"
    data: Optional[AllowanceDetailData] = None


class AllowanceCreate(BaseModel):
    """Schema tiếp nhận thông tin tạo mới bản ghi phụ cấp (POST /api/v1/allowances)"""
    ma_ho_so: int = Field(..., gt=0, description="Mã hồ sơ thực tập sinh")
    thang: int = Field(..., ge=1, le=12, description="Tháng nhận phụ cấp (1-12)")
    nam: int = Field(..., ge=2000, le=2100, description="Năm nhận phụ cấp")
    so_tien: float = Field(..., gt=0, description="Số tiền phụ cấp (phải > 0)")
    ngay_chi_tra: Optional[Union[date, str]] = Field(default=None, description="Ngày chi trả phụ cấp (YYYY-MM-DD)")
    trang_thai: Optional[str] = Field(default="ChuaChiTra", description="Trạng thái chi trả (ChuaChiTra, DaChiTra, ChoDuyet)")

    @field_validator("thang")
    def validate_thang(cls, value: int):
        if value < 1 or value > 12:
            raise ValueError("Tháng phải nằm trong khoảng từ 1 đến 12")
        return value

    @field_validator("so_tien")
    def validate_so_tien(cls, value: float):
        if value <= 0:
            raise ValueError("Số tiền phụ cấp phải lớn hơn 0")
        return value


class AllowanceCreateData(BaseModel):
    """Dữ liệu trả về chi tiết sau khi tạo mới bản ghi phụ cấp"""
    ma_phu_cap: int
    ma_ho_so: int
    thang: int
    nam: int
    thang_nam: Optional[str] = None
    so_tien: float
    ngay_chi_tra: Optional[str] = None
    trang_thai: str


class AllowanceCreateResponse(BaseModel):
    """Response chuẩn khi tạo mới phụ cấp thành công (HTTP 201)"""
    status_code: int = 201
    message: str = "Tạo bản ghi phụ cấp thành công"
    data: AllowanceCreateData


# ==============================================================
# SCHEMAS CHO QUẢN LÝ NGƯỜI HƯỚNG DẪN (MENTOR API)
# ==============================================================

class MentorCreate(BaseModel):
    ho_ten: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=100)
    mat_khau: str = Field(..., min_length=6, max_length=100)
    so_dien_thoai: Optional[str] = Field(default=None)
    ma_phong_ban: Optional[int] = Field(default=None)

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
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Email không được để trống hoặc chỉ chứa khoảng trắng")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", cleaned):
            raise ValueError("Email không đúng định dạng hợp lệ")
        return cleaned

    @field_validator('mat_khau')
    def validate_mat_khau(cls, value: str):
        cleaned = value.strip()
        if len(cleaned) < 6:
            raise ValueError("Mật khẩu phải chứa ít nhất 6 ký tự")
        return cleaned

    @field_validator('so_dien_thoai')
    def validate_so_dien_thoai(cls, value: Optional[str]):
        if not value or not value.strip():
            return None
        cleaned = value.strip()
        if not re.match(r"^(0|\+84)[0-9]{9}$|^[0-9]{10}$", cleaned):
            raise ValueError("Số điện thoại không hợp lệ (phải gồm 10 chữ số)")
        return cleaned


class MentorItemData(BaseModel):
    ma_nguoi_dung: int
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    ma_phong_ban: Optional[int] = None
    ten_phong_ban: Optional[str] = None
    vai_tro: str = "Mentor"
    trang_thai: str = "HoatDong"


class MentorResponse(BaseModel):
    status_code: int = 201
    message: str = "Tạo tài khoản người hướng dẫn thành công"
    data: MentorItemData


class MentorWorkloadItem(BaseModel):
    """Chi tiết khối lượng công việc của một người hướng dẫn"""
    ma_mentor: int
    ma_nguoi_dung: Optional[int] = None
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    vai_tro: Optional[str] = "Mentor"
    ma_phong_ban: Optional[int] = None
    ten_phong_ban: Optional[str] = None
    trang_thai: Optional[str] = "HoatDong"
    chuc_vu: Optional[str] = "Mentor Doanh nghiệp"
    so_luong_thuc_tap_sinh: int = 0
    so_sinh_vien_huong_dan: Optional[int] = 0
    chi_tieu_huong_dan: Optional[int] = 100
    ty_le_phan_tram: Optional[float] = 0.0
    trang_thai_tai: Optional[str] = "BinhThuong"
    canh_bao_qua_tai: Optional[bool] = False
    da_du_chi_tieu: Optional[bool] = False
    so_cho_trong: Optional[int] = 100


class MentorWorkloadSummary(BaseModel):
    """Tổng quan KPI phân bổ khối lượng hướng dẫn"""
    tong_so_mentor: int = 0
    tong_so_thuc_tap_sinh_duoc_huong_dan: int = 0
    trung_binh_sinh_vien_moi_mentor: float = 0.0
    mentor_nhieu_sinh_vien_nhat: Optional[str] = None
    so_mentor_chua_co_sinh_vien: int = 0


class MentorWorkloadData(BaseModel):
    """Dữ liệu khối lượng công việc trả về cho Client"""
    summary: MentorWorkloadSummary
    danh_sach_workload: List[MentorWorkloadItem] = []


class MentorWorkloadResponse(BaseModel):
    """Response chuẩn trả về khi truy vấn khối lượng công việc mentor thành công (HTTP 200)"""
    status_code: int = 200
    message: str = "Lấy thống kê khối lượng công việc của người hướng dẫn thành công"
    data: MentorWorkloadData


# ==============================================================
# SCHEMAS CHO BÁO CÁO THỐNG KÊ SINH VIÊN THEO TRƯỜNG & CHUYÊN NGÀNH
# (GET /api/v1/reports/interns-by-faculty)
# ==============================================================

class FacultyMajorItem(BaseModel):
    """Thông tin chuyên ngành thuộc một trường"""
    chuyen_nganh: str
    so_luong: int
    ty_le_phan_tram: float


class FacultyUniversityStat(BaseModel):
    """Thống kê tổng hợp theo trường đại học kèm danh sách chuyên ngành"""
    ma_truong: Optional[int] = None
    ten_truong: str
    tong_sinh_vien: int
    danh_sach_chuyen_nganh: List[FacultyMajorItem] = []


class FacultyUniversityItem(BaseModel):
    """Thông tin trường đại học thuộc một chuyên ngành"""
    ma_truong: Optional[int] = None
    ten_truong: str
    so_luong: int
    ty_le_phan_tram: float


class FacultyMajorStat(BaseModel):
    """Thống kê tổng hợp theo chuyên ngành kèm danh sách trường đại học"""
    chuyen_nganh: str
    tong_sinh_vien: int
    danh_sach_truong: List[FacultyUniversityItem] = []


class FacultyInternBreakdownItem(BaseModel):
    """Chi tiết thống kê gom nhóm hai chiều: Tên trường x Chuyên ngành"""
    ma_truong: Optional[int] = None
    ten_truong: str
    chuyen_nganh: str
    so_luong: int
    ty_le_phan_tram: float


class FacultyReportSummary(BaseModel):
    """Chỉ số KPI tổng quan báo cáo"""
    tong_sinh_vien: int = 0
    tong_so_truong: int = 0
    tong_so_chuyen_nganh: int = 0
    truong_nhieu_sinh_vien_nhat: Optional[str] = None
    chuyen_nganh_nhieu_sinh_vien_nhat: Optional[str] = None


class FacultyReportData(BaseModel):
    """Dữ liệu phản hồi báo cáo sinh viên theo trường và chuyên ngành"""
    summary: FacultyReportSummary
    thong_ke_theo_truong: List[FacultyUniversityStat] = []
    thong_ke_theo_chuyen_nganh: List[FacultyMajorStat] = []
    chi_tiet: List[FacultyInternBreakdownItem] = []


class FacultyReportResponse(BaseModel):
    """Response bọc chuẩn trả về cho client"""
    status_code: int = 200
    message: str = "Lấy báo cáo thống kê sinh viên theo trường và chuyên ngành thành công"
    data: FacultyReportData


# ==============================================================
# SCHEMAS CHO YÊU CẦU HỖ TRỢ (SUPPORT REQUESTS API)
# ==============================================================

class SupportRequestStatusUpdate(BaseModel):
    """Schema tiếp nhận thông tin cập nhật trạng thái yêu cầu hỗ trợ (PATCH /api/v1/support-requests/{id})"""
    trang_thai: str = Field(..., description="Trạng thái xử lý: DaXuLy hoặc TuChoi")
    phan_hoi_hr: Optional[str] = Field(default=None, description="Nội dung ghi chú / phản hồi từ HR")

    @field_validator("trang_thai")
    def validate_trang_thai(cls, value: str):
        allowed = ["DaXuLy", "TuChoi"]
        cleaned = value.strip()
        if cleaned not in allowed:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ cho phép các trạng thái: {', '.join(allowed)}")
        return cleaned


class SupportRequestItemData(BaseModel):
    """Dữ liệu chi tiết yêu cầu hỗ trợ sau khi cập nhật"""
    ma_yeu_cau: int
    ma_ho_so: int
    loai_yeu_cau: str
    noi_dung: str
    phan_hoi_hr: Optional[str] = None
    trang_thai: str
    ho_ten_sinh_vien: Optional[str] = None
    email_sinh_vien: Optional[str] = None


class SupportRequestCreate(BaseModel):
    """Schema tiếp nhận thông tin gửi yêu cầu hỗ trợ (POST /api/v1/support-requests)"""
    ma_ho_so: int = Field(..., description="Mã hồ sơ thực tập sinh", ge=1)
    loai_yeu_cau: str = Field(..., description="Loại yêu cầu hỗ trợ: XinChungNhan, GiayXacNhan, DongDauMoc, TaiLieu, Khac")
    noi_dung: str = Field(..., min_length=1, description="Nội dung chi tiết yêu cầu hỗ trợ")

    @field_validator("noi_dung")
    def validate_noi_dung(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nội dung yêu cầu không được để trống")
        return cleaned

    @field_validator("loai_yeu_cau")
    def validate_loai_yeu_cau(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Loại yêu cầu không được để trống")
        return cleaned


class SupportRequestResponse(BaseModel):
    """Response chuẩn trả về sau khi cập nhật trạng thái yêu cầu hỗ trợ thành công (HTTP 200)"""
    status_code: int = 200
    message: str = "Cập nhật trạng thái yêu cầu hỗ trợ thành công"
    data: SupportRequestItemData


class SupportRequestListResponse(BaseModel):
    """Response danh sách các yêu cầu hỗ trợ (GET /api/v1/support-requests)"""
    status_code: int = 200
    message: str = "Lấy danh sách yêu cầu hỗ trợ thành công"
    total: int = 0
    data: List[SupportRequestItemData]


class SupportRequestCreate(BaseModel):
    """Schema tiếp nhận yêu cầu hỗ trợ từ sinh viên (POST /api/v1/support-requests)"""
    ma_ho_so: int = Field(..., description="Mã hồ sơ thực tập sinh", gt=0)
    loai_yeu_cau: str = Field(..., description="Loại yêu cầu: XinChungNhan, GiayXacNhan, Khac")
    noi_dung: str = Field(..., description="Chi tiết nội dung cần hỗ trợ")

    @field_validator("noi_dung")
    def validate_noi_dung(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nội dung yêu cầu hỗ trợ không được để trống")
        return cleaned


class SupportRequestCreateResponse(BaseModel):
    """Response chuẩn trả về sau khi tạo yêu cầu hỗ trợ thành công (HTTP 201)"""
    status_code: int = 201
    message: str = "Gửi yêu cầu hỗ trợ thành công"
    data: SupportRequestItemData


class AssignMentorRequest(BaseModel):
    """Schema gán hoặc thay đổi Mentor (PATCH /api/v1/interns/{id}/mentor)"""
    ma_mentor: Optional[int] = Field(None, description="Mã mentor cần gán. Truyền null để hủy gán")


class AssignMentorResponse(BaseModel):
    """Response gán mentor thành công"""
    status_code: int = 200
    message: str = "Phân công mentor thành công"
    data: dict


class CompletionRateResponse(BaseModel):
    """Schema báo cáo tỷ lệ hoàn thành chương trình thực tập (GET /api/v1/reports/completion-rate)"""
    tong_so_sinh_vien: int = Field(..., description="Tổng số lượng sinh viên trong hệ thống", ge=0)
    so_luong_dang_thuc_tap: int = Field(..., description="Số lượng sinh viên trạng thái DangThucTap", ge=0)
    so_luong_hoan_thanh: int = Field(..., description="Số lượng sinh viên trạng thái HoanThanh", ge=0)
    so_luong_thoi_hoc: int = Field(..., description="Số lượng sinh viên trạng thái ThoiHoc", ge=0)
    ty_le_hoan_thanh: float = Field(..., description="Tỷ lệ phần trăm (%) hoàn thành chương trình thực tập", ge=0.0, le=100.0)
    chi_tiet_theo_trang_thai: Dict[str, int] = Field(default_factory=dict, description="Chi tiết số lượng theo từng trạng thái")

    class Config:
        from_attributes = True


class CompletionRateSummary(BaseModel):
    """Khối số liệu thống kê tỷ lệ hoàn thành thực tập"""
    tong_so_sinh_vien: int = 0
    so_luong_dang_thuc_tap: int = 0
    so_luong_hoan_thanh: int = 0
    so_luong_thoi_hoc: int = 0
    ty_le_hoan_thanh: float = 0.0
    chi_tiet_theo_trang_thai: dict = {}


class CompletionRateReportResponse(BaseModel):
    """Response chuẩn trả về báo cáo tỷ lệ hoàn thành (HTTP 200)"""
    status_code: int = 200
    message: str = "Lấy báo cáo tỷ lệ hoàn thành thực tập thành công"
    data: CompletionRateSummary


class UserStatusUpdate(BaseModel):
    trang_thai: str = Field(..., description="Trạng thái tài khoản: HoatDong hoặc Khoa")


class UserResetPasswordRequest(BaseModel):
    mat_khau_moi: Optional[str] = Field("123456", description="Mật khẩu mới cần đặt lại")


class UserCreateRequest(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100, description="Họ và tên người dùng")
    email: str = Field(..., min_length=5, max_length=100, description="Email đăng nhập")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    vai_tro: str = Field("ThucTapSinh", description="Vai trò: ThucTapSinh, Mentor, HR, Admin, NhaTruong")
    mat_khau: Optional[str] = Field("123456", min_length=6, description="Mật khẩu ban đầu")
    ma_phong_ban: Optional[int] = Field(None, description="Mã phòng ban nếu là Mentor hoặc Cán bộ")


class UserUpdateRequest(BaseModel):
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100, description="Họ và tên người dùng")
    email: Optional[str] = Field(None, min_length=5, max_length=100, description="Email đăng nhập")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    vai_tro: Optional[str] = Field(None, description="Vai trò: ThucTapSinh, Mentor, HR, Admin, NhaTruong")
    ma_phong_ban: Optional[int] = Field(None, description="Mã phòng ban nếu là Mentor hoặc Cán bộ")



# ==============================================================
# SCHEMA CHO LỊCH HỌP (MEETINGS)
# ==============================================================
class MeetingCreateRequest(BaseModel):
    """Schema yêu cầu tạo mới lịch họp"""
    tieu_de: str = Field(..., min_length=1, max_length=255, description="Tiêu đề cuộc họp")
    thoi_gian_bat_dau: datetime = Field(..., description="Thời gian bắt đầu họp")
    thoi_gian_ket_thuc: datetime = Field(..., description="Thời gian kết thúc họp")
    dia_diem: str = Field(..., min_length=1, max_length=255, description="Địa điểm hoặc phòng họp/link họp")
    ma_nguoi_chu_tri: int = Field(..., gt=0, description="Mã người dùng của người chủ trì cuộc họp")
    danh_sach_thuc_tap_sinh: List[int] = Field(..., min_length=1, description="Danh sách mã thực tập sinh được mời")
    noi_dung: Optional[str] = Field(None, description="Nội dung hoặc mô tả chi tiết cuộc họp")

    @field_validator('tieu_de')
    def validate_tieu_de(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tiêu đề cuộc họp không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned

    @field_validator('dia_diem')
    def validate_dia_diem(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Địa điểm không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned

    @model_validator(mode='after')
    def validate_meeting_time(self):
        if self.thoi_gian_ket_thuc <= self.thoi_gian_bat_dau:
            raise ValueError("Thời gian kết thúc phải lớn hơn thời gian bắt đầu")
        return self


class MeetingResponseData(BaseModel):
    """Dữ liệu chi tiết lịch họp trả về"""
    ma_lich_hop: int
    tieu_de: str
    thoi_gian_bat_dau: datetime
    thoi_gian_ket_thuc: datetime
    dia_diem: str
    ma_nguoi_chu_tri: int
    ten_nguoi_chu_tri: Optional[str] = None
    so_luong_nguoi_moi: int
    danh_sach_email_duoc_moi: List[str]
    danh_sach_thuc_tap_sinh_moi: List[int]

    model_config = ConfigDict(from_attributes=True)


class MeetingCreateResponse(BaseModel):
    """Phản hồi sau khi tạo lịch họp thành công (HTTP 201)"""
    code: int = 201
    message: str = "Tạo lịch họp thành công và đã gửi email mời tới thực tập sinh"
    data: MeetingResponseData


class MeetingCheckinRequest(BaseModel):
    """Schema yêu cầu điểm danh buổi họp qua mã QR"""
    ma_dinh_danh: str = Field(..., min_length=1, description="Mã sinh viên, email, số điện thoại hoặc mã thẻ")
    ghi_chu: Optional[str] = Field(None, description="Ghi chú khi điểm danh")

    @field_validator('ma_dinh_danh')
    def validate_identifier(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Mã định danh không được để trống hoặc chỉ chứa khoảng trắng")
        return cleaned


class MeetingCheckinResponse(BaseModel):
    """Phản hồi sau khi điểm danh buổi họp thành công (HTTP 200)"""
    code: int = 200
    message: str = "Điểm danh buổi họp thành công"
    data: dict


# ==============================================================
# SCHEMA TÍCH HỢP HRM (HRM INTEGRATION & RECONCILIATION)
# ==============================================================
EMAIL_REGEX_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

class HRMEmployeeSyncItem(BaseModel):
    """Thông tin cán bộ/nhân viên (Mentor, HR, Quản lý) từ HRM"""
    email: str = Field(..., min_length=5, max_length=100, description="Email định danh nhân viên")
    ho_ten: str = Field(..., min_length=1, max_length=100, description="Họ và tên nhân viên")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    vai_tro: Optional[str] = Field("Mentor", description="Vai trò: Mentor, HR, Admin, QuanLy")
    ten_phong_ban: Optional[str] = Field(None, description="Tên phòng ban làm việc")
    ma_phong_ban: Optional[int] = Field(None, description="Mã phòng ban nếu có")
    trang_thai: Optional[str] = Field("HoatDong", description="Trạng thái tài khoản: HoatDong hoặc Khoa")

    @field_validator("email")
    def validate_email(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Email không được để trống")
        if not re.match(EMAIL_REGEX_PATTERN, cleaned):
            raise ValueError("Email không đúng định dạng hợp lệ")
        return cleaned.lower()

    @field_validator("ho_ten")
    def validate_ho_ten(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Họ tên nhân viên không được để trống")
        return cleaned


class HRMInternSyncItem(BaseModel):
    """Thông tin sinh viên thực tập từ HRM"""
    email: str = Field(..., min_length=5, max_length=100, description="Email định danh sinh viên thực tập")
    ho_ten: str = Field(..., min_length=1, max_length=100, description="Họ và tên sinh viên")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    chuyen_nganh: Optional[str] = Field(None, max_length=100, description="Chuyên ngành đào tạo")
    lop: Optional[str] = Field(None, max_length=50, description="Lớp sinh hoạt")
    ten_truong: Optional[str] = Field(None, description="Tên trường đại học")
    ma_truong: Optional[int] = Field(None, description="Mã trường đại học nếu có")
    mentor_email: Optional[str] = Field(None, max_length=100, description="Email của Mentor trực tiếp hướng dẫn")
    ma_chuong_trinh: Optional[int] = Field(None, description="Mã chương trình thực tập")
    trang_thai_thuc_tap: Optional[str] = Field("DangThucTap", description="Trạng thái thực tập: DangThucTap, HoanThanh, ThoiHoc")
    trang_thai_xet_duyet: Optional[str] = Field("DaDuyet", description="Trạng thái hồ sơ: DaDuyet, ChoDuyet, TuChoi")

    @field_validator("email")
    def validate_email(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Email không được để trống")
        if not re.match(EMAIL_REGEX_PATTERN, cleaned):
            raise ValueError("Email không đúng định dạng hợp lệ")
        return cleaned.lower()

    @field_validator("mentor_email")
    def validate_mentor_email(cls, value: Optional[str]):
        if not value or not value.strip():
            return None
        cleaned = value.strip()
        if not re.match(EMAIL_REGEX_PATTERN, cleaned):
            raise ValueError("Email mentor không đúng định dạng hợp lệ")
        return cleaned.lower()

    @field_validator("ho_ten")
    def validate_ho_ten(cls, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Họ tên sinh viên không được để trống")
        return cleaned


class HRMSyncRequest(BaseModel):
    """Payload gửi lên từ HRM để đối soát và đồng bộ"""
    source: Optional[str] = Field("HRM_WEBHOOK", description="Tên nguồn dữ liệu HRM: HRM_WEBHOOK, SAP, WORKDAY...")
    sync_timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Thời điểm gửi đồng bộ")
    employees: List[HRMEmployeeSyncItem] = Field(default_factory=list, description="Danh sách nhân sự (Mentor, HR)")
    interns: List[HRMInternSyncItem] = Field(default_factory=list, description="Danh sách sinh viên thực tập")


class HRMSyncDetailItem(BaseModel):
    """Chi tiết kết quả xử lý của từng bản ghi"""
    email: str
    type: str                  # "EMPLOYEE" hoặc "INTERN"
    action: str                # "CREATED", "UPDATED", "FAILED", "SKIPPED"
    message: str


class HRMSyncSummary(BaseModel):
    """Thống kê tổng hợp kết quả đối soát"""
    total_received: int = 0
    employees_created: int = 0
    employees_updated: int = 0
    interns_created: int = 0
    interns_updated: int = 0
    failed_count: int = 0


class HRMSyncResponse(BaseModel):
    """Response trả về kết quả đồng bộ HRM (HTTP 200)"""
    status_code: int = 200
    message: str = "Đồng bộ và đối soát dữ liệu HRM thành công"
    summary: HRMSyncSummary
    details: List[HRMSyncDetailItem] = []


# ==============================================================
# SCHEMA PHÂN QUYỀN VAI TRÒ (RBAC - ROLE BASED ACCESS CONTROL)
# ==============================================================
class PermissionItemResponse(BaseModel):
    """Thông tin quyền hạn trả về cho API"""
    ma_quyen_han: int
    ma_quyen: str
    ten_quyen: str
    mo_ta: Optional[str] = None
    nhom_quyen: str

    model_config = ConfigDict(from_attributes=True)


class RolePermissionsUpdateRequest(BaseModel):
    """Payload cập nhật danh sách quyền hạn cho một vai trò"""
    permissions: List[Union[str, int]] = Field(
        ...,
        description="Danh sách mã quyền dạng chuỗi (VD: ['intern:read', 'role:manage']) hoặc mã số nguyên ID (VD: [1, 2])"
    )

    @field_validator("permissions")
    def validate_permissions_list(cls, value: List[Union[str, int]]):
        if not isinstance(value, list):
            raise ValueError("Danh sách quyền hạn phải là một mảng")
        return value


class RolePermissionsResponse(BaseModel):
    """Response trả về danh sách quyền của vai trò sau cập nhật hoặc truy vấn"""
    status_code: int = 200
    message: str = "Thành công"
    role: str
    total_permissions: int = 0
    permissions: List[PermissionItemResponse] = []


class PermissionListResponse(BaseModel):
    """Response danh mục toàn bộ quyền hạn trong hệ thống"""
    status_code: int = 200
    message: str = "Lấy danh mục quyền hạn thành công"
    total: int = 0
    data: List[PermissionItemResponse] = []


# ==============================================================
# SCHEMA SAO LƯU DỮ LIỆU HỆ THỐNG (SYSTEM BACKUP & RECOVERY)
# ==============================================================
class BackupItemResponse(BaseModel):
    """Thông tin chi tiết một tệp sao lưu dữ liệu (.sql.gz)"""
    filename: str = Field(..., description="Tên tệp sao lưu nén định dạng .sql.gz")
    size_bytes: int = Field(..., description="Kích thước tệp tính theo bytes")
    size_human: str = Field(..., description="Kích thước tệp định dạng dễ đọc (KB, MB, GB)")
    created_at: str = Field(..., description="Thời gian tạo bản sao lưu")
    checksum_sha256: Optional[str] = Field(default=None, description="Mã băm SHA-256 đối soát tính toàn vẹn")
    download_url: str = Field(..., description="Đường dẫn API stream tải file về")
    note: Optional[str] = Field(default=None, description="Ghi chú về bản sao lưu")


class BackupSchedulerStatus(BaseModel):
    """Trạng thái tiến trình chạy nền sao lưu tự động định kỳ"""
    enabled: bool = Field(..., description="Trạng thái bật/tắt của sao lưu tự động")
    running: bool = Field(..., description="Trạng thái luồng scheduler đang chạy")
    interval_hours: float = Field(..., description="Chu kỳ sao lưu tự động (giờ)")
    last_run: Optional[str] = Field(default=None, description="Thời điểm sao lưu gần nhất")
    status: str = Field(..., description="Mô tả trạng thái hiện tại của scheduler")
    backup_dir: str = Field(..., description="Đường dẫn thư mục lưu trữ file sao lưu")


class BackupListResponse(BaseModel):
    """Phản hồi danh sách các tệp sao lưu trong hệ thống (HTTP 200)"""
    status_code: int = 200
    message: str = "Lấy danh sách tệp sao lưu thành công"
    total_files: int = Field(..., description="Tổng số lượng tệp sao lưu")
    total_size_bytes: int = Field(..., description="Tổng dung lượng lưu trữ tính theo bytes")
    total_size_human: str = Field(..., description="Tổng dung lượng định dạng dễ đọc")
    scheduler: Optional[BackupSchedulerStatus] = Field(default=None, description="Thông tin trạng thái scheduler định kỳ")
    backups: List[BackupItemResponse] = Field(default_factory=list, description="Danh sách chi tiết các tệp sao lưu")


class BackupCreateRequest(BaseModel):
    """Payload yêu cầu kích hoạt sao lưu dữ liệu thủ công (POST)"""
    note: Optional[str] = Field(default=None, max_length=255, description="Ghi chú về mục đích bản sao lưu")
    prefix: Optional[str] = Field(default=None, max_length=50, description="Tiền tố tên file (mặc định: backup_intern_management)")

    @field_validator("note")
    def validate_note(cls, value: Optional[str]):
        if value is not None:
            cleaned = value.strip()
            if len(cleaned) > 255:
                raise ValueError("Ghi chú không được vượt quá 255 ký tự")
            return cleaned if cleaned else None
        return None

    @field_validator("prefix")
    def validate_prefix(cls, value: Optional[str]):
        if value is not None:
            cleaned = value.strip()
            if not re.match(r"^[a-zA-Z0-9_\-]+$", cleaned):
                raise ValueError("Tiền tố tên tệp chỉ được chứa chữ cái, số, dấu gạch dưới hoặc gạch ngang")
            return cleaned
        return None


class BackupCreateResponse(BaseModel):
    """Phản hồi sau khi tạo thành công bản sao lưu mới (HTTP 201)"""
    status_code: int = 201
    message: str = "Tạo bản sao lưu cơ sở dữ liệu thành công"
    backup: BackupItemResponse


# ==============================================================
# SCHEMA NHẬT KÝ HOẠT ĐỘNG HỆ THỐNG (AUDIT LOGS)
# ==============================================================
class AuditLogItemResponse(BaseModel):
    ma_nhat_ky: int = Field(..., description="ID bản ghi nhật ký")
    ma_nguoi_dung: Optional[int] = Field(None, description="ID người dùng thực hiện")
    ho_ten: Optional[str] = Field(None, description="Họ và tên người thực hiện")
    email: Optional[str] = Field(None, description="Email người thực hiện")
    vai_tro: Optional[str] = Field(None, description="Vai trò (Admin, HR, Mentor, ThucTapSinh)")
    hanh_dong: str = Field(..., description="Tên hành động nghiệp vụ")
    endpoint: str = Field(..., description="URL endpoint API")
    phuong_thuc: str = Field(..., description="Phương thức HTTP (GET, POST, PUT, DELETE, PATCH)")
    dia_chi_ip: Optional[str] = Field(None, description="Địa chỉ IP client")
    mo_ta: Optional[str] = Field(None, description="Chi tiết thao tác")
    trang_thai_http: int = Field(default=200, description="Mã phản hồi HTTP")
    thoi_gian: str = Field(..., description="Thời gian thực hiện hành động")

    model_config = ConfigDict(from_attributes=True)


class AuditLogStats(BaseModel):
    total_logs: int = 0
    today_logs: int = 0
    success_rate: float = 100.0
    unique_users: int = 0


class AuditLogPaginatedResponse(BaseModel):
    status_code: int = 200
    message: str = "Lấy danh sách nhật ký hoạt động thành công"
    total: int = 0
    page: int = 1
    page_size: int = 15
    total_pages: int = 1
    stats: AuditLogStats
    items: List[AuditLogItemResponse] = []


class AuditLogCreateRequest(BaseModel):
    hanh_dong: str = Field(..., max_length=100, description="Tên hành động nghiệp vụ")
    endpoint: str = Field(..., max_length=255, description="Đường dẫn endpoint")
    phuong_thuc: str = Field(..., max_length=10, description="Phương thức HTTP")
    dia_chi_ip: Optional[str] = Field(default=None, max_length=50, description="Địa chỉ IP")
    mo_ta: Optional[str] = Field(default=None, description="Chi tiết thao tác")
    trang_thai_http: Optional[int] = Field(default=200, description="HTTP status code")





