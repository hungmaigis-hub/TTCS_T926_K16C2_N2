from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.models.mentor import Mentor
from app.schemas.intern import AssignMentorRequest

class InternService:
    @staticmethod
    def assign_mentor(db: Session, intern_id: int, request: AssignMentorRequest) -> HoSoThucTap:
        """
        Nhiệm vụ chính của Nguyễn Văn Hiếu:
        Cập nhật trường ma_mentor trong bảng ho_so_thuc_tap cho thực tập sinh id.
        Kiểm tra tính hợp lệ của intern và mentor trước khi cập nhật.
        """
        # 1. Kiểm tra sự tồn tại của hồ sơ thực tập sinh
        ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.id == intern_id).first()
        if not ho_so:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy hồ sơ thực tập sinh với ID = {intern_id}"
            )

        # 2. Xử lý logic gán hoặc hủy gán mentor
        if request.ma_mentor is not None:
            # Kiểm tra mentor có tồn tại không
            mentor = db.query(Mentor).filter(Mentor.id == request.ma_mentor).first()
            if not mentor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy mentor với ID = {request.ma_mentor}"
                )

            # Kiểm tra trạng thái mentor
            if mentor.trang_thai != "HoatDong":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mentor '{mentor.ho_ten}' hiện không khả dụng (Trạng thái: {mentor.trang_thai})"
                )

            # Kiểm tra giới hạn số lượng thực tập sinh của mentor (User Story 31)
            so_luong_hien_tai = db.query(HoSoThucTap).filter(
                HoSoThucTap.ma_mentor == mentor.id,
                HoSoThucTap.id != intern_id
            ).count()

            if so_luong_hien_tai >= mentor.so_luong_toi_da:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mentor '{mentor.ho_ten}' đã đạt giới hạn tối đa ({mentor.so_luong_toi_da} thực tập sinh)"
                )

            # Cập nhật trường ma_mentor và thông tin phân công
            ho_so.ma_mentor = request.ma_mentor
            ho_so.ngay_gan_mentor = datetime.utcnow()
            if request.ghi_chu is not None:
                ho_so.ghi_chu_phan_cong = request.ghi_chu

        else:
            # Trường hợp request.ma_mentor is None: Hủy phân công mentor
            ho_so.ma_mentor = None
            ho_so.ngay_gan_mentor = None
            if request.ghi_chu is not None:
                ho_so.ghi_chu_phan_cong = request.ghi_chu

        # 3. Cập nhật thời gian sửa đổi và commit
        ho_so.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ho_so)

        return ho_so

    @staticmethod
    def get_intern_by_id(db: Session, intern_id: int) -> HoSoThucTap:
        """Lấy chi tiết hồ sơ thực tập sinh theo ID"""
        ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.id == intern_id).first()
        if not ho_so:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy hồ sơ thực tập sinh với ID = {intern_id}"
            )
        return ho_so

    @staticmethod
    def get_all_interns(db: Session, skip: int = 0, limit: int = 100) -> List[HoSoThucTap]:
        """Lấy danh sách tất cả thực tập sinh để hỗ trợ frontend hiển thị bảng chọn"""
        return db.query(HoSoThucTap).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_mentors(db: Session) -> List[dict]:
        """Lấy danh sách mentor kèm số lượng thực tập sinh đang hướng dẫn để hỗ trợ frontend đổ dropdown"""
        mentors = db.query(Mentor).all()
        result = []
        for m in mentors:
            count = db.query(HoSoThucTap).filter(HoSoThucTap.ma_mentor == m.id).count()
            mentor_dict = {
                "id": m.id,
                "ma_can_bo": m.ma_can_bo,
                "ho_ten": m.ho_ten,
                "email": m.email,
                "so_dien_thoai": m.so_dien_thoai,
                "phong_ban": m.phong_ban,
                "chuc_vu": m.chuc_vu,
                "chuyen_mon": m.chuyen_mon,
                "so_luong_toi_da": m.so_luong_toi_da,
                "trang_thai": m.trang_thai,
                "so_luong_dang_huong_dan": count,
                "created_at": m.created_at,
                "updated_at": m.updated_at
            }
            result.append(mentor_dict)
        return result
