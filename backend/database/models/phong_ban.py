from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.session import Base

class PhongBan(Base):
    __tablename__ = "phong_ban"

    ma_phong_ban = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ten_phong_ban = Column(String(100), nullable=False)
    mo_ta = Column(String(255), nullable=True)

    # Quan hệ
    nguoi_dung = relationship("NguoiDung", back_populates="phong_ban")
    chuong_trinh = relationship("ChuongTrinhThucTap", back_populates="phong_ban")
