from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    ma_nguoi_dung = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ten_dang_nhap = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    mat_khau_hash = Column(String(255), nullable=False)
    ho_ten = Column(String(100), nullable=False)
    vai_tro = Column(String(20), default="ThucTapSinh", nullable=False)  # Admin, HR, Mentor, ThucTapSinh
    trang_thai = Column(Boolean, default=True, nullable=False)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Quan hệ tới nhật ký hoạt động
    nhat_ky_hoat_dongs = relationship(
        "NhatKyHoatDong",
        back_populates="nguoi_dung",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
