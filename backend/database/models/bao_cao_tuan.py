from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class BaoCaoTuan(Base):
    __tablename__ = "bao_cao_tuan"

    ma_bao_cao = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    ma_nhiem_vu = Column(Integer, ForeignKey("nhiem_vu.ma_nhiem_vu"), nullable=True)
    tuan_so = Column(Integer, nullable=False)
    noi_dung_cong_viec = Column(Text, nullable=False)
    ket_qua_dat_duoc = Column(Text, nullable=True)
    phan_hoi_mentor = Column(Text, nullable=True)
    thoi_gian_nop = Column(DateTime, default=datetime.now, nullable=False)

    # Thiết lập quan hệ
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_bao_cao")
    nhiem_vu = relationship("NhiemVu")

    def to_dict(self):
        """Hỗ trợ chuyển đổi object sang dict để trả về API"""
        return {
            "ma_bao_cao": self.ma_bao_cao,
            "ma_ho_so": self.ma_ho_so,
            "ma_nhiem_vu": self.ma_nhiem_vu,
            "tuan_so": self.tuan_so,
            "noi_dung_cong_viec": self.noi_dung_cong_viec,
            "ket_qua_dat_duoc": self.ket_qua_dat_duoc,
            "phan_hoi_mentor": self.phan_hoi_mentor,
            "thoi_gian_nop": self.thoi_gian_nop.isoformat() if self.thoi_gian_nop else None,
        }
