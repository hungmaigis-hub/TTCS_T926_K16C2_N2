from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class HoSoThucTap(Base):
    __tablename__ = "ho_so_thuc_tap"

    ma_ho_so = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_nguoi_dung = Column(Integer, ForeignKey("nguoi_dung.ma_nguoi_dung"), nullable=False)
    ma_truong = Column(Integer, ForeignKey("truong_dai_hoc.ma_truong"), nullable=True)
    ma_chuong_trinh = Column(Integer, ForeignKey("chuong_trinh_thuc_tap.ma_chuong_trinh"), nullable=True)
    ma_mentor = Column(Integer, ForeignKey("nguoi_dung.ma_nguoi_dung"), nullable=True)
    chuyen_nganh = Column(String(100), nullable=True)
    trang_thai_xet_duyet = Column(String(50), default="ChoDuyet")   # ChoDuyet, DaDuyet, TuChoi
    trang_thai_thuc_tap = Column(String(50), default="DangThucTap") # DangThucTap, HoanThanh, ThoiHoc

    # Quan hệ
    thuc_tap_sinh = relationship("NguoiDung", foreign_keys=[ma_nguoi_dung], back_populates="ho_so_thuc_tap")
    mentor = relationship("NguoiDung", foreign_keys=[ma_mentor], back_populates="danh_sach_huong_dan")
    truong = relationship("TruongDaiHoc", back_populates="ho_so")
    chuong_trinh = relationship("ChuongTrinhThucTap", back_populates="ho_so")
    danh_sach_tai_lieu = relationship("TaiLieuHoSo", back_populates="ho_so", cascade="all, delete-orphan")

    def to_dict(self):
        """Chuyển đổi thông tin hồ sơ và các quan hệ liên kết thành dict để trả về API"""
        return {
            "ma_ho_so": self.ma_ho_so,
            "ma_nguoi_dung": self.ma_nguoi_dung,
            "ho_ten": self.thuc_tap_sinh.ho_ten if self.thuc_tap_sinh else None,
            "email": self.thuc_tap_sinh.email if self.thuc_tap_sinh else None,
            "so_dien_thoai": self.thuc_tap_sinh.so_dien_thoai if self.thuc_tap_sinh else None,
            "chuyen_nganh": self.chuyen_nganh,
            "ma_truong": self.ma_truong,
            "ten_truong": self.truong.ten_truong if self.truong else None,
            "ma_chuong_trinh": self.ma_chuong_trinh,
            "ten_chuong_trinh": self.chuong_trinh.ten_chuong_trinh if self.chuong_trinh else None,
            "ngay_bat_dau": self.chuong_trinh.ngay_bat_dau.isoformat() if (self.chuong_trinh and self.chuong_trinh.ngay_bat_dau) else None,
            "ngay_ket_thuc": self.chuong_trinh.ngay_ket_thuc.isoformat() if (self.chuong_trinh and self.chuong_trinh.ngay_ket_thuc) else None,
            "ma_mentor": self.ma_mentor,
            "ten_mentor": self.mentor.ho_ten if self.mentor else None,
            "trang_thai_xet_duyet": self.trang_thai_xet_duyet,
            "trang_thai_thuc_tap": self.trang_thai_thuc_tap,
        }
