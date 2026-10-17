from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class NhatKyHoatDong(Base):
    """
    Model nhat_ky_hoat_dong lưu trữ lịch sử thao tác của người dùng và hệ thống
    Bao gồm:
    - ma_nhat_ky: Khóa chính tự tăng
    - ma_nguoi_dung: Khóa ngoại tham chiếu tới người dùng thực hiện thao tác (có thể null nếu là thao tác vô danh/chưa đăng nhập)
    - hanh_dong: Tên hành động nghiệp vụ (Vd: DANG_NHAP, TAO_NGUOI_DUNG, CAP_NHAT, XOA, XEM_DANH_SACH)
    - endpoint: Đường dẫn URL của API được gọi
    - phuong_thuc: Phương thức HTTP (GET, POST, PUT, DELETE, PATCH, ...)
    - dia_chi_ip: Địa chỉ IP của client gọi yêu cầu
    - mo_ta: Chi tiết thông tin thao tác, trạng thái kết quả hoặc lỗi phát sinh
    - thoi_gian: Thời điểm thực hiện hành động
    """
    __tablename__ = "nhat_ky_hoat_dong"

    ma_nhat_ky = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ma_nguoi_dung = Column(String(50), ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="SET NULL"), nullable=True, index=True)
    hanh_dong = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    phuong_thuc = Column(String(10), nullable=False, index=True)
    dia_chi_ip = Column(String(50), nullable=True)
    mo_ta = Column(Text, nullable=True)
    thoi_gian = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Quan hệ với bảng nguoi_dung
    nguoi_dung = relationship("NguoiDung", back_populates="nhat_ky_hoat_dongs")

    def __repr__(self):
        return f"<NhatKyHoatDong(ma_nhat_ky={self.ma_nhat_ky}, hanh_dong='{self.hanh_dong}', endpoint='{self.endpoint}', phuong_thuc='{self.phuong_thuc}', thoi_gian='{self.thoi_gian}')>"
