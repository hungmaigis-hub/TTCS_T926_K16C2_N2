from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    ma_nguoi_dung = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_phong_ban = Column(Integer, ForeignKey("phong_ban.ma_phong_ban"), nullable=True)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    so_dien_thoai = Column(String(20), unique=True, nullable=True)
    vai_tro = Column(String(50), default="ThucTapSinh")  # Admin, HR, Mentor, ThucTapSinh
    trang_thai = Column(String(50), default="HoatDong")   # HoatDong, Khoa

    # Quan hệ
    phong_ban = relationship("PhongBan", back_populates="nguoi_dung")
    ho_so_thuc_tap = relationship("HoSoThucTap", foreign_keys="[HoSoThucTap.ma_nguoi_dung]", back_populates="thuc_tap_sinh", uselist=False)
    danh_sach_huong_dan = relationship("HoSoThucTap", foreign_keys="[HoSoThucTap.ma_mentor]", back_populates="mentor")
