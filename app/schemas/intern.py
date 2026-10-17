"""
Pydantic schemas cho endpoint PATCH /api/v1/interns/{id}/mentor
và các schema liên quan đến intern / mentor.

Quy ước:
    - Request schema kết thúc bằng ...Request
    - Response schema kết thúc bằng ...Response
    - Tất cả field đều có description rõ ràng (hiển thị đẹp trên Swagger UI)
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================
# MentorInfo – thông tin ngắn gọn của mentor (dùng trong response)
# ============================================================
class MentorInfo(BaseModel):
    """Thông tin cơ bản của Mentor được gán."""

    ma_mentor: str = Field(
        ...,
        description="Mã định danh của Mentor trong hệ thống",
        examples=["MENTOR01"],
    )
    ho_ten: str = Field(
        ...,
        description="Họ và tên đầy đủ của Mentor",
        examples=["Nguyễn Thị Lan"],
    )
    email: str = Field(
        ...,
        description="Email của Mentor",
        examples=["lan.nguyen@company.com"],
    )
    so_dien_thoai: Optional[str] = Field(
        None,
        description="Số điện thoại của Mentor",
        examples=["0901234567"],
    )

    model_config = {"from_attributes": True}


# ============================================================
# InternBriefInfo – thông tin ngắn gọn của intern (dùng trong response)
# ============================================================
class InternBriefInfo(BaseModel):
    """Thông tin tóm tắt của intern trong response."""

    ma_ho_so: str = Field(
        ...,
        description="Mã hồ sơ thực tập",
        examples=["HS001"],
    )
    ho_ten: str = Field(
        ...,
        description="Họ tên thực tập sinh",
        examples=["Trần Văn An"],
    )
    email: Optional[str] = Field(
        None,
        description="Email của thực tập sinh",
        examples=["an.tran@university.edu.vn"],
    )
    vi_tri_thuc_tap: Optional[str] = Field(
        None,
        description="Vị trí đang thực tập",
        examples=["Backend Developer"],
    )
    trang_thai: str = Field(
        ...,
        description="Trạng thái hồ sơ",
        examples=["DaDuyet"],
    )

    model_config = {"from_attributes": True}


# ============================================================
# AssignMentorRequest – body của PATCH /interns/{id}/mentor
# ============================================================
class AssignMentorRequest(BaseModel):
    """
    Payload gửi lên khi gán / thay đổi Mentor cho một thực tập sinh.

    Gửi `ma_mentor = null` để **hủy gán** mentor (bỏ trống).
    """

    ma_mentor: Optional[str] = Field(
        ...,
        description=(
            "Mã định danh của Mentor cần gán. "
            "Phải tồn tại trong bảng nguoi_dung với vai_tro = 'Mentor'. "
            "Truyền null để hủy gán mentor hiện tại."
        ),
        examples=["MENTOR01"],
    )

    @field_validator("ma_mentor", mode="before")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Loại bỏ khoảng trắng thừa nếu có."""
        if isinstance(v, str):
            v = v.strip()
            # Chuỗi rỗng sau strip coi như null
            return v if v else None
        return v


# ============================================================
# AssignMentorResponse – response trả về sau PATCH /interns/{id}/mentor
# ============================================================
class AssignMentorResponse(BaseModel):
    """Response trả về sau khi gán Mentor thành công."""

    success: bool = Field(
        True,
        description="Luôn True khi thành công",
    )
    message: str = Field(
        ...,
        description="Thông báo kết quả",
        examples=["Gán Mentor thành công."],
    )
    data: AssignMentorData = Field(
        ...,
        description="Dữ liệu trả về sau khi cập nhật",
    )


class AssignMentorData(BaseModel):
    """Dữ liệu cập nhật trong response."""

    ho_so: InternBriefInfo = Field(
        ...,
        description="Thông tin hồ sơ thực tập vừa được cập nhật",
    )
    mentor: Optional[MentorInfo] = Field(
        None,
        description="Thông tin Mentor vừa được gán. null nếu đã hủy gán.",
    )
    ngay_cap_nhat: datetime = Field(
        ...,
        description="Thời điểm cập nhật (UTC)",
    )

    model_config = {"from_attributes": True}


# Resolve forward references (Python < 3.11 cần)
AssignMentorResponse.model_rebuild()


# ============================================================
# Schemas cho quản lý danh sách hồ sơ thực tập sinh
# ============================================================
class HoSoThucTapCreate(BaseModel):
    ma_sv: str = Field(..., description="Mã sinh viên")
    ho_ten: str = Field(..., description="Họ và tên")
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    truong_hoc: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    ma_mentor: Optional[int] = None
    trang_thai: Optional[str] = "DangThucTap"
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None


class HoSoThucTapResponse(BaseModel):
    id: Optional[int] = None
    ma_ho_so: Optional[str] = None
    ma_sv: Optional[str] = None
    ho_ten: str
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    truong_hoc: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    ma_mentor: Optional[int] = None
    trang_thai: Optional[str] = None
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None
    mentor: Optional[dict] = None

    model_config = {"from_attributes": True}

