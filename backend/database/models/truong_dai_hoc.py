from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.session import Base

class TruongDaiHoc(Base):
    __tablename__ = "truong_dai_hoc"

    ma_truong = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ten_truong = Column(String(200), nullable=False)
    dia_chi = Column(String(255), nullable=True)
    nguoi_lien_he = Column(String(100), nullable=True)
    email_lien_he = Column(String(100), nullable=True)

    # Quan hệ
    ho_so = relationship("HoSoThucTap", back_populates="truong")
