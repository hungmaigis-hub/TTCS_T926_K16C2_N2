from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database.session import Base


class QuyenHan(Base):
    """Bảng lưu trữ danh mục quyền hạn trong hệ thống (RBAC Permissions)"""
    __tablename__ = "quyen_han"

    ma_quyen_han = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_quyen = Column(String(100), unique=True, index=True, nullable=False, comment="Mã quyền duy nhất, ví dụ: intern:read, role:manage")
    ten_quyen = Column(String(150), nullable=False, comment="Tên hiển thị của quyền")
    mo_ta = Column(String(255), nullable=True, comment="Mô tả chi tiết quyền hạn")
    nhom_quyen = Column(String(50), nullable=False, default="HeThong", comment="Nhóm quyền: ThucTapSinh, NhiemVu, BaoCao, ChamCong, LichHop, HeThong")

    # Quan hệ liên kết tới bảng phân quyền vai trò
    danh_sach_vai_tro = relationship(
        "VaiTroQuyenHan",
        back_populates="quyen_han",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "ma_quyen_han": self.ma_quyen_han,
            "ma_quyen": self.ma_quyen,
            "ten_quyen": self.ten_quyen,
            "mo_ta": self.mo_ta,
            "nhom_quyen": self.nhom_quyen,
        }


class VaiTroQuyenHan(Base):
    """Bảng liên kết giữa Vai trò (Role) và QuyenHan (RBAC Role-Permission Mapping)"""
    __tablename__ = "vai_tro_quyen_han"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vai_tro = Column(String(50), index=True, nullable=False, comment="Vai trò: Admin, HR, Mentor, ThucTapSinh, NhaTruong, QuanLy")
    ma_quyen_han = Column(Integer, ForeignKey("quyen_han.ma_quyen_han", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("vai_tro", "ma_quyen_han", name="uq_vai_tro_quyen_han"),
    )

    # Quan hệ
    quyen_han = relationship("QuyenHan", back_populates="danh_sach_vai_tro")

    def to_dict(self):
        return {
            "id": self.id,
            "vai_tro": self.vai_tro,
            "ma_quyen_han": self.ma_quyen_han,
            "ma_quyen": self.quyen_han.ma_quyen if self.quyen_han else None,
            "ten_quyen": self.quyen_han.ten_quyen if self.quyen_han else None,
            "nhom_quyen": self.quyen_han.nhom_quyen if self.quyen_han else None,
        }
