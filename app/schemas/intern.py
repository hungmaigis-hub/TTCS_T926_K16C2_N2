from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── REQUEST SCHEMA ──────────────────────────────────────────
class AssignMentorRequest(BaseModel):
    """Payload gửi lên từ Frontend khi chọn mentor trong dropdown và bấm Lưu."""
    ma_mentor: str = Field(
        ...,
        min_length=1,
        description="Mã của mentor được phân công",
        json_schema_extra={"example": "MTR001"}
    )


# ── RESPONSE SCHEMAS ─────────────────────────────────────────
class InternResponse(BaseModel):
    id: int
    ma_thuc_tap_sinh: str
    ho_ten: str
    email: Optional[str] = None
    truong_dai_hoc: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    vi_tri_thuc_tap: Optional[str] = None
    ma_phong_ban: Optional[str] = None
    ma_mentor: Optional[str] = None
    trang_thai: Optional[str] = None
    ngay_cap_nhat: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssignMentorResponse(BaseModel):
    message: str = "Phân công mentor thành công"
    data: InternResponse


class MentorResponse(BaseModel):
    id: int
    ma_mentor: str
    ho_ten: str
    email: Optional[str] = None
    chuc_vu: Optional[str] = None
    phong_ban: Optional[str] = None
    role: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
