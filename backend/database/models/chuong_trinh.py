from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class ChuongTrinhThucTap(Base):
    __tablename__ = "chuong_trinh_thuc_tap"

    ma_chuong_trinh = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_phong_ban = Column(Integer, ForeignKey("phong_ban.ma_phong_ban"), nullable=False)
    ten_chuong_trinh = Column(String(150), nullable=False)
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=False)
    mo_ta = Column(Text, nullable=True)

    # Quan hệ
    phong_ban = relationship("PhongBan", back_populates="chuong_trinh")
    ho_so = relationship("HoSoThucTap", back_populates="chuong_trinh")
