import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from database.models import NguoiDung, HoSoThucTap, PhongBan, TruongDaiHoc
from schemas import (
    HRMSyncRequest,
    HRMSyncResponse,
    HRMSyncSummary,
    HRMSyncDetailItem,
    HRMEmployeeSyncItem,
    HRMInternSyncItem,
)
from security import get_password_hash

logger = logging.getLogger(__name__)


def sync_hrm_data(payload: HRMSyncRequest, db: Session) -> HRMSyncResponse:
    """
    Dịch vụ tích hợp, đối soát và đồng bộ dữ liệu nhân viên (Mentor/HR) và sinh viên thực tập từ HRM.
    Áp dụng kỹ thuật Idempotent Upsert (Cập nhật bản ghi cũ hoặc thêm mới bản ghi chưa tồn tại).
    """
    summary = HRMSyncSummary()
    details = []

    total_items = len(payload.employees) + len(payload.interns)
    summary.total_received = total_items

    # 1. ĐỐI SOÁT VÀ ĐỒNG BỘ DANH SÁCH NHÂN VIÊN (MENTOR / HR / CÁN BỘ)
    for emp in payload.employees:
        clean_email = emp.email.strip().lower()
        try:
            # Phân giải phòng ban (nếu được truyền)
            dept_id: Optional[int] = emp.ma_phong_ban
            if not dept_id and emp.ten_phong_ban:
                clean_dept_name = emp.ten_phong_ban.strip()
                dept = db.query(PhongBan).filter(PhongBan.ten_phong_ban == clean_dept_name).first()
                if not dept:
                    dept = PhongBan(ten_phong_ban=clean_dept_name, mo_ta=f"Phòng ban đồng bộ từ HRM ({payload.source})")
                    db.add(dept)
                    db.flush()
                dept_id = dept.ma_phong_ban

            # Tìm kiếm nhân viên theo email
            existing_user = db.query(NguoiDung).filter(NguoiDung.email == clean_email).first()
            if existing_user:
                # Cập nhật thông tin nhân viên cũ (giữ nguyên mật khẩu đã tạo)
                existing_user.ho_ten = emp.ho_ten.strip()
                if emp.so_dien_thoai:
                    existing_user.so_dien_thoai = emp.so_dien_thoai.strip()
                if emp.vai_tro:
                    existing_user.vai_tro = emp.vai_tro.strip()
                if emp.trang_thai:
                    existing_user.trang_thai = emp.trang_thai.strip()
                if dept_id:
                    existing_user.ma_phong_ban = dept_id

                summary.employees_updated += 1
                details.append(
                    HRMSyncDetailItem(
                        email=clean_email,
                        type="EMPLOYEE",
                        action="UPDATED",
                        message=f"Đã cập nhật thông tin nhân viên '{existing_user.ho_ten}' (Mã: {existing_user.ma_nguoi_dung})",
                    )
                )
            else:
                # Thêm mới nhân viên
                default_password_hash = get_password_hash("123456")
                new_user = NguoiDung(
                    ho_ten=emp.ho_ten.strip(),
                    email=clean_email,
                    mat_khau_hash=default_password_hash,
                    so_dien_thoai=emp.so_dien_thoai.strip() if emp.so_dien_thoai else None,
                    vai_tro=emp.vai_tro.strip() if emp.vai_tro else "Mentor",
                    trang_thai=emp.trang_thai.strip() if emp.trang_thai else "HoatDong",
                    ma_phong_ban=dept_id,
                )
                db.add(new_user)
                db.flush()

                summary.employees_created += 1
                details.append(
                    HRMSyncDetailItem(
                        email=clean_email,
                        type="EMPLOYEE",
                        action="CREATED",
                        message=f"Đã thêm mới nhân viên '{new_user.ho_ten}' (Mã: {new_user.ma_nguoi_dung})",
                    )
                )

        except Exception as e:
            logger.error(f"Lỗi khi đồng bộ nhân viên {clean_email}: {e}")
            summary.failed_count += 1
            details.append(
                HRMSyncDetailItem(
                    email=clean_email,
                    type="EMPLOYEE",
                    action="FAILED",
                    message=f"Lỗi đồng bộ: {str(e)}",
                )
            )

    # 2. ĐỐI SOÁT VÀ ĐỒNG BỘ DANH SÁCH SINH VIÊN THỰC TẬP
    for intern in payload.interns:
        clean_email = intern.email.strip().lower()
        try:
            # Phân giải trường đại học (nếu có)
            school_id: Optional[int] = intern.ma_truong
            if not school_id and intern.ten_truong:
                clean_school_name = intern.ten_truong.strip()
                school = db.query(TruongDaiHoc).filter(TruongDaiHoc.ten_truong == clean_school_name).first()
                if not school:
                    school = TruongDaiHoc(ten_truong=clean_school_name)
                    db.add(school)
                    db.flush()
                school_id = school.ma_truong

            # Phân giải Mentor phụ trách qua mentor_email
            mentor_id: Optional[int] = None
            if intern.mentor_email:
                clean_mentor_email = intern.mentor_email.strip().lower()
                mentor_user = db.query(NguoiDung).filter(NguoiDung.email == clean_mentor_email).first()
                if mentor_user:
                    mentor_id = mentor_user.ma_nguoi_dung

            # Tìm kiếm tài khoản sinh viên theo email
            intern_user = db.query(NguoiDung).filter(NguoiDung.email == clean_email).first()
            user_is_new = False
            if not intern_user:
                user_is_new = True
                default_password_hash = get_password_hash("123456")
                intern_user = NguoiDung(
                    ho_ten=intern.ho_ten.strip(),
                    email=clean_email,
                    mat_khau_hash=default_password_hash,
                    so_dien_thoai=intern.so_dien_thoai.strip() if intern.so_dien_thoai else None,
                    vai_tro="ThucTapSinh",
                    trang_thai="HoatDong",
                )
                db.add(intern_user)
                db.flush()
            else:
                # Cập nhật thông tin tài khoản nếu đã có
                intern_user.ho_ten = intern.ho_ten.strip()
                if intern.so_dien_thoai:
                    intern_user.so_dien_thoai = intern.so_dien_thoai.strip()

            # Đối soát Hồ sơ thực tập (ho_so_thuc_tap)
            profile = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == intern_user.ma_nguoi_dung).first()
            if profile:
                # Cập nhật hồ sơ thực tập cũ
                if intern.chuyen_nganh:
                    profile.chuyen_nganh = intern.chuyen_nganh.strip()
                if intern.lop:
                    profile.lop = intern.lop.strip()
                if school_id:
                    profile.ma_truong = school_id
                if mentor_id:
                    profile.ma_mentor = mentor_id
                if intern.ma_chuong_trinh:
                    profile.ma_chuong_trinh = intern.ma_chuong_trinh
                if intern.trang_thai_thuc_tap:
                    profile.trang_thai_thuc_tap = intern.trang_thai_thuc_tap
                if intern.trang_thai_xet_duyet:
                    profile.trang_thai_xet_duyet = intern.trang_thai_xet_duyet

                summary.interns_updated += 1
                details.append(
                    HRMSyncDetailItem(
                        email=clean_email,
                        type="INTERN",
                        action="UPDATED",
                        message=f"Đã cập nhật hồ sơ thực tập của sinh viên '{intern_user.ho_ten}' (Mã hồ sơ: {profile.ma_ho_so})",
                    )
                )
            else:
                # Tạo mới hồ sơ thực tập
                new_profile = HoSoThucTap(
                    ma_nguoi_dung=intern_user.ma_nguoi_dung,
                    ma_truong=school_id,
                    ma_chuong_trinh=intern.ma_chuong_trinh or 1,
                    ma_mentor=mentor_id,
                    chuyen_nganh=intern.chuyen_nganh.strip() if intern.chuyen_nganh else None,
                    lop=intern.lop.strip() if intern.lop else None,
                    trang_thai_xet_duyet=intern.trang_thai_xet_duyet or "DaDuyet",
                    trang_thai_thuc_tap=intern.trang_thai_thuc_tap or "DangThucTap",
                )
                db.add(new_profile)
                db.flush()

                summary.interns_created += 1
                details.append(
                    HRMSyncDetailItem(
                        email=clean_email,
                        type="INTERN",
                        action="CREATED",
                        message=f"Đã tạo mới tài khoản và hồ sơ thực tập cho sinh viên '{intern_user.ho_ten}' (Mã hồ sơ: {new_profile.ma_ho_so})",
                    )
                )

        except Exception as e:
            logger.error(f"Lỗi khi đồng bộ sinh viên {clean_email}: {e}")
            summary.failed_count += 1
            details.append(
                HRMSyncDetailItem(
                    email=clean_email,
                    type="INTERN",
                    action="FAILED",
                    message=f"Lỗi đồng bộ: {str(e)}",
                )
            )

    # Lưu thay đổi an toàn vào database
    db.commit()

    return HRMSyncResponse(
        status_code=200,
        message=f"Đối soát và đồng bộ dữ liệu HRM thành công ({summary.total_received} bản ghi tiếp nhận)",
        summary=summary,
        details=details,
    )
