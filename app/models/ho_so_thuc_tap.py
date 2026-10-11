from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class HoSoThucTap(Base):
    __tablename__ = "ho_so_thuc_tap"

    id = Column(Integer, primary_key=True, index=True)
    ma_sv = Column(String(50), unique=True, index=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(20), nullable=True)
    truong_hoc = Column(String(150), nullable=True)
    chuyen_nganh = Column(String(100), nullable=True)

    # TRƯỜNG TRỌNG TÂM: ma_mentor (Khóa ngoại trỏ đến mentors.id)
    ma_mentor = Column(Integer, ForeignKey("mentors.id", ondelete="SET NULL"), nullable=True, index=True)

    trang_thai = Column(String(50), default="DangThucTap")  # DangThucTap, MoiTiepNhan, HoanThanh, ThoiHoc
    ngay_bat_dau = Column(Date, nullable=True, default=date.today)
    ngay_ket_thuc = Column(Date, nullable=True)
    ghi_chu_phan_cong = Column(String(255), nullable=True)
    ngay_gan_mentor = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ với mentor
    mentor = relationship("Mentor", back_populates="danh_sach_thuc_tap_sinh")
