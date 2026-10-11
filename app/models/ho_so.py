from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class HoSo(Base):
    __tablename__ = "ho_so"

    ma_ho_so = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_sinh_vien = Column(String(50), unique=True, index=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(20), nullable=True)
    ma_mentor = Column(Integer, nullable=True)
    trang_thai = Column(String(50), default="DangThucTap", nullable=False)
    ngay_tao = Column(DateTime(timezone=True), server_default=func.now())

    # Quan hệ 1-N với YeuCauHoTro
    yeu_cau_ho_tro = relationship("YeuCauHoTro", back_populates="ho_so", cascade="all, delete-orphan")
