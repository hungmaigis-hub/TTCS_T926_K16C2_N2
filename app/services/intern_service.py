"""
Service layer cho chức năng quản lý intern (thực tập sinh).

Tách biệt business logic khỏi router để dễ test và bảo trì.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ho_so_thuc_tap import HoSoThucTap
from app.models.nguoi_dung import NguoiDung
from app.schemas.intern import (
    AssignMentorData,
    AssignMentorResponse,
    InternBriefInfo,
    MentorInfo,
)

logger = logging.getLogger(__name__)

# Giới hạn chỉ tiêu phân công sinh viên cho mỗi Mentor
MAX_INTERNS_PER_MENTOR = 5


# ============================================================
# assign_mentor_service
# ============================================================
def assign_mentor_service(
    intern_id: str,
    ma_mentor: Optional[str],
    db: Session,
) -> AssignMentorResponse:
    """
    Business logic cho PATCH /api/v1/interns/{id}/mentor.

    Luồng xử lý:
        1. Tìm hồ sơ thực tập theo intern_id (ma_ho_so).
        2. Nếu ma_mentor != null → validate mentor:
               a. Mentor phải tồn tại trong bảng nguoi_dung.
               b. Mentor phải có vai_tro = 'Mentor'.
               c. Tài khoản Mentor phải đang kích hoạt.
        3. Cập nhật ma_mentor vào bảng ho_so_thuc_tap.
        4. Commit & trả về response.

    Args:
        intern_id:  Mã hồ sơ thực tập (ma_ho_so).
        ma_mentor:  Mã mentor muốn gán; None để hủy gán.
        db:         SQLAlchemy session.

    Returns:
        AssignMentorResponse với đầy đủ thông tin cập nhật.

    Raises:
        HTTPException 404: Hồ sơ thực tập hoặc Mentor không tồn tại.
        HTTPException 422: Người dùng tồn tại nhưng không phải Mentor.
        HTTPException 403: Tài khoản Mentor bị vô hiệu hóa.
    """
    # ----------------------------------------------------------
    # BƯỚC 1: Tìm hồ sơ thực tập
    # ----------------------------------------------------------
    logger.info(
        "assign_mentor_service | intern_id=%s | ma_mentor=%s",
        intern_id,
        ma_mentor,
    )

    ho_so: Optional[HoSoThucTap] = (
        db.query(HoSoThucTap)
        .filter(HoSoThucTap.ma_ho_so == intern_id)
        .first()
    )

    if ho_so is None:
        logger.warning("Hồ sơ thực tập không tồn tại: %s", intern_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "INTERN_NOT_FOUND",
                "message": f"Không tìm thấy hồ sơ thực tập với mã '{intern_id}'.",
                "field": "id",
            },
        )

    # ----------------------------------------------------------
    # BƯỚC 2: Validate mentor (chỉ khi không null)
    # ----------------------------------------------------------
    mentor_record: Optional[NguoiDung] = None

    if ma_mentor is not None:
        # 2a. Mentor phải tồn tại trong bảng nguoi_dung
        mentor_record = (
            db.query(NguoiDung)
            .filter(NguoiDung.ma_nguoi_dung == ma_mentor)
            .first()
        )

        if mentor_record is None:
            logger.warning("Mentor không tồn tại trong hệ thống: %s", ma_mentor)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "MENTOR_NOT_FOUND",
                    "message": (
                        f"Không tìm thấy người dùng với mã '{ma_mentor}' "
                        f"trong hệ thống."
                    ),
                    "field": "ma_mentor",
                },
            )

        # 2b. Phải có vai trò là "Mentor"
        if mentor_record.vai_tro != "Mentor":
            logger.warning(
                "Người dùng '%s' có vai trò '%s', không phải 'Mentor'.",
                ma_mentor,
                mentor_record.vai_tro,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": "INVALID_MENTOR_ROLE",
                    "message": (
                        f"Người dùng '{ma_mentor}' có vai trò "
                        f"'{mentor_record.vai_tro}', không phải 'Mentor'. "
                        f"Chỉ người dùng có vai trò 'Mentor' mới được gán."
                    ),
                    "field": "ma_mentor",
                },
            )

        # 2c. Tài khoản mentor phải đang kích hoạt
        if not mentor_record.kich_hoat:
            logger.warning("Tài khoản Mentor bị vô hiệu hóa: %s", ma_mentor)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "MENTOR_INACTIVE",
                    "message": (
                        f"Tài khoản của Mentor '{ma_mentor}' "
                        f"đã bị vô hiệu hóa, không thể gán."
                    ),
                    "field": "ma_mentor",
                },
            )

        # 2d. Kiểm tra giới hạn chỉ tiêu (Quota: tối đa MAX_INTERNS_PER_MENTOR sinh viên)
        current_count = (
            db.query(HoSoThucTap)
            .filter(HoSoThucTap.ma_mentor == ma_mentor, HoSoThucTap.ma_ho_so != intern_id)
            .count()
        )
        if current_count >= MAX_INTERNS_PER_MENTOR:
            logger.warning(
                "Mentor '%s' đã đủ chỉ tiêu hướng dẫn: %d/%d",
                ma_mentor,
                current_count,
                MAX_INTERNS_PER_MENTOR,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "MENTOR_QUOTA_EXCEEDED",
                    "message": (
                        f"Mentor '{mentor_record.ho_ten}' đã đủ chỉ tiêu hướng dẫn tối đa "
                        f"({current_count}/{MAX_INTERNS_PER_MENTOR} sinh viên), không thể tiếp nhận thêm."
                    ),
                    "field": "ma_mentor",
                },
            )

    # ----------------------------------------------------------
    # BƯỚC 3: Cập nhật ma_mentor
    # ----------------------------------------------------------
    old_mentor = ho_so.ma_mentor
    ho_so.ma_mentor = ma_mentor
    ho_so.ngay_cap_nhat = datetime.utcnow()

    try:
        db.commit()
        db.refresh(ho_so)
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Lỗi khi commit cập nhật mentor cho hồ sơ '%s': %s",
            intern_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DB_ERROR",
                "message": "Đã xảy ra lỗi khi lưu dữ liệu. Vui lòng thử lại.",
            },
        ) from exc

    logger.info(
        "Cập nhật mentor thành công | ho_so=%s | %s → %s",
        intern_id,
        old_mentor,
        ma_mentor,
    )

    # ----------------------------------------------------------
    # BƯỚC 4: Xây dựng response
    # ----------------------------------------------------------
    # Thông tin intern (brief)
    intern_brief = InternBriefInfo(
        ma_ho_so=ho_so.ma_ho_so,
        ho_ten=ho_so.ho_ten,
        email=ho_so.email,
        vi_tri_thuc_tap=ho_so.vi_tri_thuc_tap,
        trang_thai=ho_so.trang_thai,
    )

    # Thông tin mentor (nếu có)
    mentor_info: Optional[MentorInfo] = None
    if mentor_record is not None:
        mentor_info = MentorInfo(
            ma_mentor=mentor_record.ma_nguoi_dung,
            ho_ten=mentor_record.ho_ten,
            email=mentor_record.email,
            so_dien_thoai=mentor_record.so_dien_thoai,
        )

    # Thông báo phù hợp
    if ma_mentor is not None:
        message = (
            f"Gán Mentor '{mentor_record.ho_ten}' cho hồ sơ '{intern_id}' thành công."
        )
    else:
        message = f"Đã hủy gán Mentor khỏi hồ sơ '{intern_id}' thành công."

    return AssignMentorResponse(
        success=True,
        message=message,
        data=AssignMentorData(
            ho_so=intern_brief,
            mentor=mentor_info,
            ngay_cap_nhat=ho_so.ngay_cap_nhat,
        ),
    )


class InternService:
    """Class wrapper hỗ trợ các endpoint v1 truy vấn dữ liệu"""

    @staticmethod
    def assign_mentor(db: Session, intern_id: int, request: any):
        resp = assign_mentor_service(intern_id=str(intern_id), ma_mentor=request.ma_mentor, db=db)
        return resp.data.ho_so

    @staticmethod
    def get_all_mentors(db: Session):
        from app.models.mentor import Mentor
        try:
            return db.query(Mentor).all()
        except Exception:
            return []

    @staticmethod
    def get_all_interns(db: Session, skip: int = 0, limit: int = 100):
        return db.query(HoSoThucTap).offset(skip).limit(limit).all()

    @staticmethod
    def get_intern_by_id(db: Session, intern_id: int):
        ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == str(intern_id)).first()
        if not ho_so:
            raise HTTPException(status_code=404, detail="Hồ sơ không tồn tại")
        return ho_so

