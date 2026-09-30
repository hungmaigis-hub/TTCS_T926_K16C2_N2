from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class DonNghiPhep(Base):
    __tablename__ = "don_nghi_phep"

    ma_don = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    ngay_nghi = Column(Date, nullable=False)
    ly_do = Column(String(255), nullable=False)
    trang_thai = Column(String(50), default="ChoDuyet")  # ChoDuyet, DaDuyet, TuChoi

    # Quan hệ
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_nghi_phep")

    def to_dict(self):
        """Chuyển đổi thông tin đơn nghỉ phép thành dict để trả về API"""
        return {
            "ma_don": self.ma_don,
            "ma_ho_so": self.ma_ho_so,
            "ngay_nghi": self.ngay_nghi.isoformat() if self.ngay_nghi else None,
            "ly_do": self.ly_do,
            "trang_thai": self.trang_thai,
        }
