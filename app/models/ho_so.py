from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class HoSo(Base):
    """
    Model lưu trữ thông tin hồ sơ sinh viên / thực tập sinh.
    Dùng để kiểm tra tính hợp lệ của hồ sơ khi gửi yêu cầu hỗ trợ.
    """
    __tablename__ = "ho_so"

    ma_ho_so = Column(String(50), primary_key=True, index=True, comment="Mã hồ sơ sinh viên")
    ho_ten = Column(String(100), nullable=False, comment="Họ và tên sinh viên")
    email = Column(String(100), nullable=False, comment="Địa chỉ email")
    so_dien_thoai = Column(String(20), nullable=True, comment="Số điện thoại liên lạc")
    truong_dai_hoc = Column(String(150), nullable=True, comment="Trường đại học đang theo học")
    chuyen_nganh = Column(String(100), nullable=True, comment="Chuyên ngành đào tạo")
    trang_thai = Column(
        String(50),
        default="DangThucTap",
        nullable=False,
        comment="Trạng thái hồ sơ: DangThucTap, DaTiepNhan, Khoa, BiHuy"
    )
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Thời gian tạo hồ sơ")

    # Mối quan hệ với các yêu cầu hỗ trợ
    yeu_cau_ho_tro = relationship("YeuCauHoTro", back_populates="ho_so", cascade="all, delete-orphan")
