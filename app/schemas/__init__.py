from app.schemas.mentor import MentorBase, MentorCreate, MentorResponse, MentorSimpleResponse
from app.schemas.intern import (
    AssignMentorRequest,
    AssignMentorResponse,
    HoSoThucTapBase,
    HoSoThucTapCreate,
    HoSoThucTapResponse
)
from app.schemas.report import CompletionRateResponse

__all__ = [
    "MentorBase",
    "MentorCreate",
    "MentorResponse",
    "MentorSimpleResponse",
    "AssignMentorRequest",
    "AssignMentorResponse",
    "HoSoThucTapBase",
    "HoSoThucTapCreate",
    "HoSoThucTapResponse",
    "CompletionRateResponse",
]
