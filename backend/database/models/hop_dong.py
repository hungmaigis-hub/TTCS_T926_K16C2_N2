from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class HopDong(Base):
    __tablename__ = "hop_dong"

    ma_hop_dong = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    duong_dan_file = Column(String(255), nullable=False)
    ngay_tai_len = Column(Date, default=date.today)
    ngay_ky = Column(Date, nullable=True)
    trang_thai = Column(String(50), default="ChuaXacNhan")  # ChuaXacNhan, DaXacNhan

    # Quan hệ liên kết ngược tới hồ sơ thực tập
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_hop_dong")

    def to_dict(self):
        """Chuyển đổi thông tin hợp đồng thành dict để trả về response API"""
        intern_info = None
        if self.ho_so and self.ho_so.thuc_tap_sinh:
            intern_info = {
                "ho_ten": self.ho_so.thuc_tap_sinh.ho_ten,
                "email": self.ho_so.thuc_tap_sinh.email,
                "chuyen_nganh": self.ho_so.chuyen_nganh,
            }

        return {
            "ma_hop_dong": self.ma_hop_dong,
            "ma_ho_so": self.ma_ho_so,
            "duong_dan_file": self.duong_dan_file,
            "ngay_tai_len": self.ngay_tai_len.isoformat() if self.ngay_tai_len else None,
            "ngay_ky": self.ngay_ky.isoformat() if self.ngay_ky else None,
            "trang_thai": self.trang_thai,
            "trang_thai_thuc_tap": self.ho_so.trang_thai_thuc_tap if self.ho_so else None,
            "sinh_vien": intern_info
        }
