from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class PhuCap(Base):
    __tablename__ = "phu_cap"

    ma_phu_cap = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    thang_nam = Column(String(7), nullable=False)  # Định dạng 'YYYY-MM'
    so_tien = Column(Numeric(12, 2), nullable=False, default=0.00)
    trang_thai_chi_tra = Column(String(50), default="ChuaChiTra")  # 'DaChiTra', 'ChuaChiTra'

    # Quan hệ liên kết ngược tới hồ sơ thực tập
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_phu_cap")

    def to_dict(self):
        """Chuyển đổi thông tin phụ cấp thành dict"""
        return {
            "ma_phu_cap": self.ma_phu_cap,
            "ma_ho_so": self.ma_ho_so,
            "thang_nam": self.thang_nam,
            "so_tien": float(self.so_tien) if self.so_tien is not None else 0.0,
            "trang_thai_chi_tra": self.trang_thai_chi_tra,
        }
