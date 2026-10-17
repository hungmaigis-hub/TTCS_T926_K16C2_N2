from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class LichHop(Base):
    __tablename__ = "lich_hop"

    ma_lich_hop = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tieu_de = Column(String(255), nullable=False)
    thoi_gian_bat_dau = Column(DateTime, nullable=False)
    thoi_gian_ket_thuc = Column(DateTime, nullable=False)
    dia_diem = Column(String(255), nullable=False)
    ma_nguoi_chu_tri = Column(Integer, ForeignKey("nguoi_dung.ma_nguoi_dung"), nullable=False)

    # Quan hệ liên kết tới người chủ trì cuộc họp (Mentor, HR, Admin)
    nguoi_chu_tri = relationship(
        "NguoiDung",
        foreign_keys=[ma_nguoi_chu_tri],
        back_populates="danh_sach_lich_hop_chu_tri"
    )

    def to_dict(self):
        """Chuyển đổi thông tin lịch họp thành dictionary"""
        return {
            "ma_lich_hop": self.ma_lich_hop,
            "tieu_de": self.tieu_de,
            "thoi_gian_bat_dau": self.thoi_gian_bat_dau.isoformat() if self.thoi_gian_bat_dau else None,
            "thoi_gian_ket_thuc": self.thoi_gian_ket_thuc.isoformat() if self.thoi_gian_ket_thuc else None,
            "dia_diem": self.dia_diem,
            "ma_nguoi_chu_tri": self.ma_nguoi_chu_tri,
        }
