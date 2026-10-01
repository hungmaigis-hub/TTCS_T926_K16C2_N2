from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database.session import Base

class DonXinNghi(Base):
    __tablename__ = "don_xin_nghi"

    ma_don = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    tu_ngay = Column(Date, nullable=False)
    den_ngay = Column(Date, nullable=False)
    ly_do = Column(String(255), nullable=False)
    trang_thai = Column(String(50), default="Chờ duyệt", nullable=False)  # "Chờ duyệt", "Đã duyệt", "Từ chối"
    ngay_tao = Column(DateTime, default=func.now(), nullable=False)

    # Thiết lập quan hệ ngược về hồ sơ thực tập
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_don_xin_nghi")

    def to_dict(self):
        """Hỗ trợ chuyển đổi object sang dict để trả về API"""
        so_ngay = (self.den_ngay - self.tu_ngay).days + 1 if self.tu_ngay and self.den_ngay else 1
        return {
            "ma_don": self.ma_don,
            "ma_ho_so": self.ma_ho_so,
            "tu_ngay": self.tu_ngay.isoformat() if self.tu_ngay else None,
            "den_ngay": self.den_ngay.isoformat() if self.den_ngay else None,
            "so_ngay": so_ngay,
            "ly_do": self.ly_do,
            "trang_thai": self.trang_thai,
            "ngay_tao": self.ngay_tao.isoformat() if self.ngay_tao else None,
        }
