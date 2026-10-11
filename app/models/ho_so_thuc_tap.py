"""
ORM Model cho bảng ho_so_thuc_tap (hồ sơ thực tập sinh).

Bảng này lưu trữ toàn bộ thông tin về đợt thực tập của sinh viên,
bao gồm trường ma_mentor trỏ về nguoi_dung.
"""
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class HoSoThucTap(Base):
    __tablename__ = "ho_so_thuc_tap"

    # -------------------------------------------------------
    # Primary key
    # -------------------------------------------------------
    ma_ho_so = Column(
        String(20),
        primary_key=True,
        index=True,
        comment="Mã hồ sơ thực tập (VD: HS001)",
    )

    # -------------------------------------------------------
    # Thông tin intern
    # -------------------------------------------------------
    ma_sinh_vien = Column(
        String(20),
        ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Mã sinh viên (FK → nguoi_dung)",
    )

    ho_ten = Column(String(100), nullable=False, comment="Họ tên sinh viên")
    email = Column(String(150), nullable=True, comment="Email liên lạc")
    so_dien_thoai = Column(String(15), nullable=True, comment="Số điện thoại")
    truong_dai_hoc = Column(String(200), nullable=True, comment="Trường đại học")
    nganh_hoc = Column(String(100), nullable=True, comment="Ngành học")
    gioi_thieu_ban_than = Column(Text, nullable=True, comment="Giới thiệu bản thân")

    # -------------------------------------------------------
    # Thông tin thực tập
    # -------------------------------------------------------
    vi_tri_thuc_tap = Column(String(100), nullable=True, comment="Vị trí thực tập")
    ngay_bat_dau = Column(Date, nullable=True, comment="Ngày bắt đầu thực tập")
    ngay_ket_thuc = Column(Date, nullable=True, comment="Ngày kết thúc thực tập")

    trang_thai = Column(
        Enum(
            "ChoDuyet",
            "DaDuyet",
            "TuChoi",
            "DangThucTap",
            "HoanThanh",
            name="trang_thai_enum",
        ),
        default="ChoDuyet",
        nullable=False,
        comment="Trạng thái hồ sơ thực tập",
    )

    ghi_chu = Column(Text, nullable=True, comment="Ghi chú thêm")

    # -------------------------------------------------------
    # Mentor – trường cần cập nhật qua PATCH /mentor
    # -------------------------------------------------------
    ma_mentor = Column(
        String(20),
        ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Mã mentor phụ trách (FK → nguoi_dung, vai_tro='Mentor')",
    )

    # -------------------------------------------------------
    # Thời gian
    # -------------------------------------------------------
    ngay_tao = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Ngày tạo hồ sơ",
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
    sinh_vien = relationship(
        "NguoiDung",
        back_populates=None,          # không cần back_populates từ phía NguoiDung
        foreign_keys=[ma_sinh_vien],
    )

    mentor = relationship(
        "NguoiDung",
        back_populates="ho_so_thuc_tap",
        foreign_keys=[ma_mentor],
    )

    def __repr__(self) -> str:
        return (
            f"<HoSoThucTap ma={self.ma_ho_so!r} "
            f"sinh_vien={self.ma_sinh_vien!r} "
            f"mentor={self.ma_mentor!r}>"
        )
