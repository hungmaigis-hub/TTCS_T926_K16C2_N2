from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class YeuCauHoTro(Base):
    """
    Model yeu_cau_ho_tro lưu trữ yêu cầu hỗ trợ từ sinh viên / thực tập sinh.
    Bao gồm các trường:
    - ma_yeu_cau: Khóa chính, tự tăng
    - ma_ho_so: Khóa ngoại tham chiếu đến bảng ho_so
    - loai_yeu_cau: Phân loại yêu cầu hỗ trợ (chứng nhận, giấy tờ, kỹ thuật,...)
    - tieu_de: Tiêu đề yêu cầu
    - noi_dung: Chi tiết nội dung cần hỗ trợ
    - trang_thai: Trạng thái xử lý (mặc định: "ChoXuLy")
    - ngay_tao: Thời điểm tiếp nhận yêu cầu (tự động gán thời gian)
    """
    __tablename__ = "yeu_cau_ho_tro"

    ma_yeu_cau = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="Mã yêu cầu hỗ trợ")
    ma_ho_so = Column(String(50), ForeignKey("ho_so.ma_ho_so"), nullable=False, index=True, comment="Mã hồ sơ sinh viên")
    loai_yeu_cau = Column(String(100), nullable=False, comment="Loại yêu cầu hỗ trợ (Giấy tờ, Kỹ thuật, Phụ cấp,...)")
    tieu_de = Column(String(255), nullable=False, comment="Tiêu đề yêu cầu hỗ trợ")
    noi_dung = Column(Text, nullable=False, comment="Nội dung chi tiết yêu cầu hỗ trợ")
    trang_thai = Column(String(50), default="ChoXuLy", nullable=False, comment="Trạng thái (ChoXuLy, DangXuLy, DaGiaiQuyet, TuChoi)")
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Thời gian tạo yêu cầu")

    # Mối quan hệ với bảng hồ sơ sinh viên
    ho_so = relationship("HoSo", back_populates="yeu_cau_ho_tro")
