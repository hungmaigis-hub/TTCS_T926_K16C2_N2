from sqlalchemy import Column, Integer, String, Text, DateTime, func
from datetime import datetime
from app.database import Base


class YeuCauHoTro(Base):
    """
    Model SQLAlchemy: yeu_cau_ho_tro
    Liên kết với ho_so_thuc_tap (ma_ho_so).
    Phục vụ tiếp nhận yêu cầu hỗ trợ sinh viên thực tập.
    """
    __tablename__ = "yeu_cau_ho_tro"

    ma_yeu_cau = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(String(20), nullable=False, index=True)
    loai_yeu_cau = Column(String(100), nullable=False)
    tieu_de = Column(String(255), nullable=False)
    noi_dung = Column(Text, nullable=False)
    trang_thai = Column(String(50), default="ChoXuLy", nullable=False)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Trường phản hồi từ HR
    phan_hoi = Column(Text, nullable=True)
    ngay_xu_ly = Column(DateTime, nullable=True)
