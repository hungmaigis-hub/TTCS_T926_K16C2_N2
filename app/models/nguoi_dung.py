"""
SQLAlchemy Model cho bảng `nguoi_dung`
Phân hệ: Quản trị hệ thống - Quản lý tài khoản & phân quyền
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

import itertools
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

_user_id_counter = itertools.count(1001)

def default_ma_nguoi_dung():
    return str(next(_user_id_counter))


class NguoiDung(Base):
    """
    Bảng người dùng (Admin, HR, Mentor, Thực tập sinh)
    """
    __tablename__ = "nguoi_dung"

    ma_nguoi_dung = Column(String(50), primary_key=True, index=True, default=default_ma_nguoi_dung)
    ten_dang_nhap = Column(String(50), unique=True, index=True, nullable=True, comment="Tên đăng nhập (username)")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="Email định danh người dùng")
    mat_khau_hash = Column(String(255), nullable=False, comment="Mật khẩu đã băm bằng bcrypt")
    ho_ten = Column(String(100), nullable=False, comment="Họ và tên người dùng")
    so_dien_thoai = Column(String(20), nullable=True, comment="Số điện thoại")
    vai_tro = Column(String(50), default="ThucTapSinh", nullable=False, comment="Vai trò: Admin, HR, Mentor, ThucTapSinh")
    trang_thai = Column(Boolean, default=True, nullable=False, comment="Trạng thái tài khoản (True: Hoạt động, False: Khóa)")
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Thời điểm tạo tài khoản")
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="Thời điểm cập nhật")

    # Property kich_hoat đồng bộ với trang_thai (để tương thích cả 2 module)
    @property
    def kich_hoat(self) -> bool:
        return bool(self.trang_thai)

    @kich_hoat.setter
    def kich_hoat(self, value: bool):
        self.trang_thai = bool(value)

    # Các thuộc tính ánh xạ (aliases/properties)
    @property
    def id(self):
        return self.ma_nguoi_dung

    @property
    def username(self):
        return self.ten_dang_nhap or self.email

    @property
    def full_name(self):
        return self.ho_ten

    @property
    def role(self):
        return self.vai_tro

    # Quan hệ với các bảng khác
    thong_bao_list = relationship("ThongBao", back_populates="nguoi_nhan", cascade="all, delete-orphan")
    nhat_ky_hoat_dongs = relationship("NhatKyHoatDong", back_populates="nguoi_dung")

    def __repr__(self):
        return f"<NguoiDung(ma_nguoi_dung={self.ma_nguoi_dung}, email='{self.email}', vai_tro='{self.vai_tro}')>"
