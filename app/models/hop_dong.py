from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime
from datetime import datetime
from app.core.database import Base


class HopDong(Base):
    """
    Model hop_dong: Quản lý hợp đồng thực tập sinh
    Tác giả: Nguyễn Văn Hiếu (Backend Developer)
    Nhiệm vụ: Lưu ma_so_hop_dong, ngay_ky, muc_phu_cap_co_ban, khóa ngoại ma_ho_so
    """
    __tablename__ = "hop_dong"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, doc="ID định danh hợp đồng")
    ma_so_hop_dong = Column(String(50), unique=True, index=True, nullable=False, doc="Mã số hợp đồng duy nhất")
    ngay_ky = Column(Date, nullable=False, doc="Ngày ký hợp đồng")
    muc_phu_cap_co_ban = Column(Numeric(14, 2), nullable=False, doc="Mức phụ cấp cơ bản (VNĐ)")
    
    # Khóa ngoại / liên kết tới hồ sơ thực tập (ho_so_thuc_tap)
    ma_ho_so = Column(String(50), index=True, nullable=True, doc="Mã hồ sơ thực tập sinh liên kết")
    
    # Đường dẫn file tải lên (User Story: HR muốn tải lên hợp đồng để quản lý giấy tờ)
    file_url = Column(String(500), nullable=True, doc="Đường dẫn file hợp đồng đính kèm")
    
    # Trạng thái hợp đồng (User Story: TTS xác nhận hợp đồng trên hệ thống)
    trang_thai = Column(String(50), default="Chờ xác nhận", nullable=False, doc="Trạng thái: Chờ xác nhận, Đã xác nhận, Đã hủy")
    
    ghi_chu = Column(Text, nullable=True, doc="Ghi chú bổ sung")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, doc="Thời điểm tạo bản ghi")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, doc="Thời điểm cập nhật bản ghi")

    def __repr__(self):
        return f"<HopDong(id={self.id}, ma_so_hop_dong='{self.ma_so_hop_dong}', ngay_ky={self.ngay_ky}, muc_phu_cap={self.muc_phu_cap_co_ban})>"
