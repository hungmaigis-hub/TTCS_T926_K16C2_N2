import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Enum, Date, DateTime, func
from app.core.database import Base

class InternStatus(str, enum.Enum):
    """Trạng thái thực tập sinh theo yêu cầu nghiệp vụ."""
    DangThucTap = "DangThucTap"  # Đang tham gia quá trình thực tập
    HoanThanh = "HoanThanh"      # Đã hoàn thành chương trình thực tập
    ThoiHoc = "ThoiHoc"          # Đã thôi học / ngừng thực tập

class Intern(Base):
    """Bảng lưu trữ thông tin thực tập sinh / sinh viên."""
    __tablename__ = "interns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_code = Column(String(50), unique=True, index=True, nullable=False, comment="Mã sinh viên")
    full_name = Column(String(100), nullable=False, comment="Họ và tên sinh viên")
    email = Column(String(100), nullable=True, comment="Email liên hệ")
    university = Column(String(150), nullable=True, index=True, comment="Trường Đại học / Cao đẳng")
    major = Column(String(100), nullable=True, comment="Chuyên ngành")
    department = Column(String(100), nullable=True, index=True, comment="Phòng ban thực tập")
    mentor_name = Column(String(100), nullable=True, comment="Mentor hướng dẫn")
    
    # Trạng thái thực tập: DangThucTap, HoanThanh, ThoiHoc
    status = Column(
        Enum(InternStatus, name="intern_status_enum", native_enum=False),
        nullable=False,
        default=InternStatus.DangThucTap,
        index=True,
        comment="Trạng thái thực tập"
    )
    
    start_date = Column(Date, nullable=True, comment="Ngày bắt đầu thực tập")
    end_date = Column(Date, nullable=True, comment="Ngày kết thúc thực tập")
    
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Intern {self.student_code} - {self.full_name} ({self.status})>"
