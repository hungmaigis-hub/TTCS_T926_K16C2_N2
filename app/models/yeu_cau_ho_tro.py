from sqlalchemy import Column, Integer, String, Text, DateTime, func
from datetime import datetime, timezone
from app.core.database import Base


class YeuCauHoTro(Base):
    """
    Model SQLAlchemy: yeu_cau_ho_tro
    Phục vụ User Story 27 & 28:
    - Là thực tập sinh, tôi muốn gửi yêu cầu hỗ trợ (chứng nhận, giấy tờ...) để được giải quyết.
    - Là HR, tôi muốn duyệt và phản hồi yêu cầu hỗ trợ kịp thời.
    """
    __tablename__ = "yeu_cau_ho_tro"

    ma_yeu_cau = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, nullable=False, index=True)
    loai_yeu_cau = Column(String(100), nullable=False)
    tieu_de = Column(String(255), nullable=False)
    noi_dung = Column(Text, nullable=False)
    trang_thai = Column(String(50), default="ChoXuLy", nullable=False)
    ngay_tao = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Trường hỗ trợ cho quy trình phản hồi của HR (User story 28)
    phan_hoi = Column(Text, nullable=True)
    ngay_xu_ly = Column(DateTime(timezone=True), nullable=True)
