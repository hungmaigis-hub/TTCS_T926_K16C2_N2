from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
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
