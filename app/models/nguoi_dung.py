"""
ORM Model cho bảng nguoi_dung (người dùng hệ thống).

Vai trò (vai_tro) hợp lệ:
    - "HR"
    - "Mentor"
    - "ThucTapSinh" (intern)
    - "Admin"
"""
from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    # -------------------------------------------------------
    # Primary key
    # -------------------------------------------------------
    ma_nguoi_dung = Column(
        String(20),
        primary_key=True,
        index=True,
        comment="Mã người dùng (VD: ND001, MENTOR01, HR01)",
    )

    # -------------------------------------------------------
    # Thông tin cơ bản
    # -------------------------------------------------------
    ho_ten = Column(String(100), nullable=False, comment="Họ và tên đầy đủ")

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
        comment="Địa chỉ email đăng nhập",
    )

    mat_khau_hash = Column(
        String(255),
        nullable=False,
        comment="Mật khẩu đã băm (bcrypt)",
    )

    so_dien_thoai = Column(String(15), nullable=True, comment="Số điện thoại")

    # -------------------------------------------------------
    # Vai trò
    # -------------------------------------------------------
    vai_tro = Column(
        Enum("HR", "Mentor", "ThucTapSinh", "Admin", name="vai_tro_enum"),
        nullable=False,
        comment="Vai trò người dùng trong hệ thống",
    )

    # -------------------------------------------------------
    # Trạng thái & thời gian
    # -------------------------------------------------------
    kich_hoat = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="True = tài khoản đang hoạt động",
    )

    ngay_tao = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Ngày tạo tài khoản",
    )

    ngay_cap_nhat = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
        comment="Lần cập nhật cuối",
    )

    # -------------------------------------------------------
    # Relationships
    # -------------------------------------------------------
    # Một Mentor có thể hướng dẫn nhiều hồ sơ thực tập
    ho_so_thuc_tap = relationship(
        "HoSoThucTap",
        back_populates="mentor",
        foreign_keys="HoSoThucTap.ma_mentor",
    )

    def __repr__(self) -> str:
        return (
            f"<NguoiDung ma={self.ma_nguoi_dung!r} "
            f"ten={self.ho_ten!r} vai_tro={self.vai_tro!r}>"
        )
