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

    def to_dict(self):
        """Chuyển đổi thông tin chương trình thực tập thành dict để trả về response"""
        return {
            "ma_chuong_trinh": self.ma_chuong_trinh,
            "ma_phong_ban": self.ma_phong_ban,
            "ten_phong_ban": self.phong_ban.ten_phong_ban if self.phong_ban else None,
            "ten_chuong_trinh": self.ten_chuong_trinh,
            "ngay_bat_dau": self.ngay_bat_dau.isoformat() if self.ngay_bat_dau else None,
            "ngay_ket_thuc": self.ngay_ket_thuc.isoformat() if self.ngay_ket_thuc else None,
            "mo_ta": self.mo_ta,
        }
