from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class YeuCauHoTro(Base):
    __tablename__ = "yeu_cau_ho_tro"

    ma_yeu_cau = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    loai_yeu_cau = Column(String(50), nullable=False)  # 'XinChungNhan', 'GiayXacNhan', 'Khac'
    noi_dung = Column(Text, nullable=False)
    phan_hoi_hr = Column(Text, nullable=True)
    trang_thai = Column(String(50), default="ChoXuLy")  # 'ChoXuLy', 'DaXuLy', 'TuChoi'

    # Quan hệ liên kết ngược tới hồ sơ thực tập
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_yeu_cau_ho_tro")

    def to_dict(self):
        """Chuyển đổi thông tin yêu cầu hỗ trợ thành dict"""
        return {
            "ma_yeu_cau": self.ma_yeu_cau,
            "ma_ho_so": self.ma_ho_so,
            "loai_yeu_cau": self.loai_yeu_cau,
            "noi_dung": self.noi_dung,
            "phan_hoi_hr": self.phan_hoi_hr,
            "trang_thai": self.trang_thai,
        }
