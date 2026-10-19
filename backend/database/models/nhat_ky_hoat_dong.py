from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class NhatKyHoatDong(Base):
    __tablename__ = "nhat_ky_hoat_dong"

    ma_nhat_ky = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ma_nguoi_dung = Column(Integer, ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="SET NULL"), nullable=True, index=True)
    hanh_dong = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    phuong_thuc = Column(String(10), nullable=False, index=True)
    dia_chi_ip = Column(String(50), nullable=True)
    mo_ta = Column(Text, nullable=True)
    trang_thai_http = Column(Integer, default=200, nullable=False)
    thoi_gian = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    nguoi_dung = relationship("NguoiDung", foreign_keys=[ma_nguoi_dung])
