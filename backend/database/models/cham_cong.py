from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship, synonym
from database.session import Base

class ChamCong(Base):
    __tablename__ = "cham_cong"

    ma_cham_cong = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    ngay_cham_cong = Column(Date, nullable=False)
    gio_checkin = Column("gio_check_in", Time, nullable=True)
    gio_checkout = Column("gio_check_out", Time, nullable=True)
    gio_check_in = synonym("gio_checkin")
    gio_check_out = synonym("gio_checkout")
    thoi_gian_checkin = Column(DateTime, nullable=True)
    thoi_gian_checkout = Column(DateTime, nullable=True)
    trang_thai = Column(String(50), default="DungGio")  # DungGio, DiMuon, VeSom, HoanThanh
    phuong_thuc = Column(String(50), default="QR/Card")  # QR/Card, QR, Card, The, Web
    ghi_chu = Column(String(255), nullable=True)

    # Quan hệ
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_cham_cong")

    def to_dict(self):
        """Chuyển đổi thông tin chấm công thành dict để trả về API"""
        gio_in_str = self.gio_checkin.isoformat() if self.gio_checkin else None
        gio_out_str = self.gio_checkout.isoformat() if self.gio_checkout else None
        return {
            "ma_cham_cong": self.ma_cham_cong,
            "ma_ho_so": self.ma_ho_so,
            "ngay_cham_cong": self.ngay_cham_cong.isoformat() if self.ngay_cham_cong else None,
            "gio_checkin": gio_in_str,
            "gio_checkout": gio_out_str,
            "gio_check_in": gio_in_str,
            "gio_check_out": gio_out_str,
            "thoi_gian_checkin": self.thoi_gian_checkin.isoformat() if self.thoi_gian_checkin else None,
            "thoi_gian_checkout": self.thoi_gian_checkout.isoformat() if self.thoi_gian_checkout else None,
            "trang_thai": self.trang_thai,
            "phuong_thuc": self.phuong_thuc,
            "ghi_chu": self.ghi_chu,
        }
