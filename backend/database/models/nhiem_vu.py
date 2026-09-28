from datetime import date
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class NhiemVu(Base):
    __tablename__ = "nhiem_vu"

    ma_nhiem_vu = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    ten_nhiem_vu = Column(String(150), nullable=False)
    mo_ta = Column(Text, nullable=True)
    han_hoan_thanh = Column(Date, nullable=False)
    tien_do_phantram = Column(Integer, default=0, nullable=False)
    trang_thai = Column(String(50), default="Chưa bắt đầu", nullable=False)

    # Quan hệ liên kết ngược tới hồ sơ thực tập
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_nhiem_vu")

    def to_dict(self):
        """Chuyển đổi thông tin nhiệm vụ thành dict để trả về response API"""
        return {
            "ma_nhiem_vu": self.ma_nhiem_vu,
            "ma_ho_so": self.ma_ho_so,
            "ten_nhiem_vu": self.ten_nhiem_vu,
            "mo_ta": self.mo_ta,
            "han_hoan_thanh": self.han_hoan_thanh.isoformat() if self.han_hoan_thanh else None,
            "tien_do_phantram": self.tien_do_phantram,
            "trang_thai": self.trang_thai,
        }
