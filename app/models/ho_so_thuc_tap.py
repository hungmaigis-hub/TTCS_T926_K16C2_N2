from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class HoSoThucTap(Base):
    __tablename__ = "ho_so_thuc_tap"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_thuc_tap_sinh = Column(String(50), unique=True, index=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    truong_dai_hoc = Column(String(150), nullable=True)
    chuyen_nganh = Column(String(100), nullable=True)
    vi_tri_thuc_tap = Column(String(100), nullable=True)
    ma_phong_ban = Column(String(50), nullable=True)
    ma_mentor = Column(String(50), nullable=True, index=True)  # Trường ma_mentor được cập nhật
    trang_thai = Column(String(50), default="dang_thuc_tap")
    ngay_tao = Column(DateTime, default=datetime.utcnow)
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
