from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class ChamCong(Base):
    __tablename__ = "cham_cong"

    ma_cham_cong = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    ngay_cham_cong = Column(Date, nullable=False)
    thoi_gian_checkin = Column(DateTime, nullable=True)
    thoi_gian_checkout = Column(DateTime, nullable=True)
    gio_check_in = Column(Time, nullable=True)
    gio_check_out = Column(Time, nullable=True)
    trang_thai = Column(String(50), default="DungGio")  # DungGio, DiMuon, VeSom, HoanThanh
    phuong_thuc = Column(String(50), default="Web")     # QR, The, Web
    ghi_chu = Column(String(255), nullable=True)

    # Quan hệ
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_cham_cong")

    def to_dict(self):
        """Chuyển đổi thông tin chấm công thành dict để trả về API"""
        return {
            "ma_cham_cong": self.ma_cham_cong,
            "ma_ho_so": self.ma_ho_so,
            "ngay_cham_cong": self.ngay_cham_cong.isoformat() if self.ngay_cham_cong else None,
            "thoi_gian_checkin": self.thoi_gian_checkin.isoformat() if self.thoi_gian_checkin else None,
            "thoi_gian_checkout": self.thoi_gian_checkout.isoformat() if self.thoi_gian_checkout else None,
            "gio_check_in": self.gio_check_in.isoformat() if self.gio_check_in else None,
            "gio_check_out": self.gio_check_out.isoformat() if self.gio_check_out else None,
            "trang_thai": self.trang_thai,
            "phuong_thuc": self.phuong_thuc,
            "ghi_chu": self.ghi_chu,
        }
