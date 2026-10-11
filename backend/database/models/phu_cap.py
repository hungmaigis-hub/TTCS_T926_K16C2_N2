from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship
from database.session import Base

class PhuCap(Base):
    __tablename__ = "phu_cap"

    ma_phu_cap = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    thang = Column(Integer, nullable=True)  # 1 - 12
    nam = Column(Integer, nullable=True)    # Ví dụ 2026
    thang_nam = Column(String(7), nullable=True)  # Định dạng 'YYYY-MM' (tương thích ngược)
    so_tien = Column(Numeric(12, 2), nullable=False, default=0.00)
    ngay_chi_tra = Column(Date, nullable=True)  # Ngày thực tế/dự kiến chi trả
    trang_thai = Column(String(50), nullable=True, default="ChuaChiTra")  # 'ChuaChiTra', 'DaChiTra', 'ChoDuyet'
    trang_thai_chi_tra = Column(String(50), nullable=True, default="ChuaChiTra")  # 'DaChiTra', 'ChuaChiTra' (tương thích ngược)

    # Quan hệ liên kết ngược tới hồ sơ thực tập
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_phu_cap")

    def to_dict(self):
        """Chuyển đổi thông tin phụ cấp thành dict"""
        return {
            "ma_phu_cap": self.ma_phu_cap,
            "ma_ho_so": self.ma_ho_so,
            "thang": self.thang,
            "nam": self.nam,
            "thang_nam": self.thang_nam or (f"{self.nam:04d}-{self.thang:02d}" if self.nam and self.thang else None),
            "so_tien": float(self.so_tien) if self.so_tien is not None else 0.0,
            "ngay_chi_tra": self.ngay_chi_tra.isoformat() if self.ngay_chi_tra else None,
            "trang_thai": self.trang_thai or self.trang_thai_chi_tra or "ChuaChiTra",
            "trang_thai_chi_tra": self.trang_thai_chi_tra or self.trang_thai or "ChuaChiTra",
        }

