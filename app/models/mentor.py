from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    ma_can_bo = Column(String(50), unique=True, index=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    so_dien_thoai = Column(String(20), nullable=True)
    phong_ban = Column(String(100), nullable=False)
    chuc_vu = Column(String(100), nullable=False)
    chuyen_mon = Column(String(255), nullable=True)
    so_luong_toi_da = Column(Integer, default=5)
    trang_thai = Column(String(50), default="HoatDong")  # HoatDong, TamNghi, NgungHuongDan
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ 1-nhiều với hồ sơ thực tập sinh
    danh_sach_thuc_tap_sinh = relationship("HoSoThucTap", back_populates="mentor", lazy="select")
