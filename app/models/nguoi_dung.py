
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
=======
"""
SQLAlchemy Model cho bảng `nguoi_dung`
Phân hệ: Quản trị hệ thống - Quản lý tài khoản & phân quyền
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import declarative_base


from app.core.database import Base


class NguoiDung(Base):
    """
    Bảng người dùng (Admin, HR, Mentor, Thực tập sinh)
    """
    __tablename__ = "nguoi_dung"

    ma_nguoi_dung = Column(Integer, primary_key=True, index=True, autoincrement=True)

    email = Column(String(255), unique=True, index=True, nullable=False)
    mat_khau_hash = Column(String(255), nullable=False)
    ho_ten = Column(String(100), nullable=False)
    vai_tro = Column(String(50), default="ThucTapSinh", nullable=False)  # Admin, HR, Mentor, ThucTapSinh
    kich_hoat = Column(Boolean, default=True, nullable=False)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Quan hệ 1-N với thông báo nhận được
    thong_bao_list = relationship("ThongBao", back_populates="nguoi_nhan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NguoiDung ma_nguoi_dung={self.ma_nguoi_dung} email={self.email} ho_ten={self.ho_ten}>"
=======
    ten_dang_nhap = Column(String(50), unique=True, index=True, nullable=False, comment="Tên đăng nhập (username)")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="Email định danh người dùng")
    mat_khau_hash = Column(String(255), nullable=False, comment="Mật khẩu đã băm bằng bcrypt")
    ho_ten = Column(String(100), nullable=False, comment="Họ và tên người dùng")
    vai_tro = Column(String(20), nullable=False, comment="Vai trò: Admin, HR, Mentor, ThucTapSinh")
    trang_thai = Column(Boolean, default=True, nullable=False, comment="Trạng thái tài khoản (True: Hoạt động, False: Khóa)")
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Thời điểm tạo tài khoản")
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="Thời điểm cập nhật")

    # Các thuộc tính ánh xạ (aliases/properties) thuận tiện tương thích cho cả tiếng Anh & tiếng Việt
    @property
    def id(self):
        return self.ma_nguoi_dung

    @property
    def username(self):
        return self.ten_dang_nhap

    @property
    def full_name(self):
        return self.ho_ten

    @property
    def role(self):
        return self.vai_tro

    def __repr__(self):
        return f"<NguoiDung(ma_nguoi_dung={self.ma_nguoi_dung}, ten_dang_nhap='{self.ten_dang_nhap}', vai_tro='{self.vai_tro}')>"

