from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ThongBao(Base):
    """
    Model thong_bao lưu trữ thông báo cho người dùng (thực tập sinh, mentor, HR, admin)
    Các trường theo đặc tả:
    - ma_thong_bao: Khóa chính định danh thông báo
    - ma_nguoi_nhan: Mã người dùng nhận thông báo (Foreign key)
    - tieu_de: Tiêu đề tóm tắt thông báo
    - noi_dung: Nội dung chi tiết thông báo
    - loai_thong_bao: Phân loại thông báo (LICH_TRINH, CONG_VIEC, HE_THONG, HO_TRO,...)
    - da_doc: Trạng thái đọc (False = Chưa đọc, True = Đã đọc)
    - ngay_tao: Thời gian tạo thông báo
    """
    __tablename__ = "thong_bao"

    ma_thong_bao = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_nguoi_nhan = Column(String(50), ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="CASCADE"), nullable=False, index=True)
    tieu_de = Column(String(255), nullable=False)
    noi_dung = Column(Text, nullable=False)
    loai_thong_bao = Column(String(50), nullable=False, default="CHUNG", index=True)
    da_doc = Column(Boolean, default=False, nullable=False, index=True)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Quan hệ với bảng người dùng
    nguoi_nhan = relationship("NguoiDung", back_populates="thong_bao_list")

    def __repr__(self):
        return (
            f"<ThongBao ma_thong_bao={self.ma_thong_bao} "
            f"ma_nguoi_nhan={self.ma_nguoi_nhan} "
            f"tieu_de='{self.tieu_de[:20]}' "
            f"da_doc={self.da_doc}>"
        )
