from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class TaiLieuHoSo(Base):
    __tablename__ = "tai_lieu_ho_so"

    ma_tai_lieu = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    loai_tai_lieu = Column(String(50), nullable=False)  # CV, DonXinThucTap, GiayGioiThieu
    duong_dan_file = Column(String(255), nullable=False)
    trang_thai_duyet = Column(String(50), default="ChoDuyet")  # ChoDuyet, DaDuyet, TuChoi

    # Quan hệ
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_tai_lieu")

    def to_dict(self):
        """Chuyển đổi thông tin tài liệu thành dict để trả về response"""
        return {
            "ma_tai_lieu": self.ma_tai_lieu,
            "ma_ho_so": self.ma_ho_so,
            "loai_tai_lieu": self.loai_tai_lieu,
            "duong_dan_file": self.duong_dan_file,
            "trang_thai_duyet": self.trang_thai_duyet,
        }
