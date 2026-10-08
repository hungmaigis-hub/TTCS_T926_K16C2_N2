from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Time, Date, DateTime
from database.session import Base


class CaLamViec(Base):
    """
    Model quản lý danh mục ca làm việc và lịch gặp Mentor (Work Shift / Mentoring Session).
    Hỗ trợ cấu hình ca theo ngày cụ thể, ca lặp lại và theo lớp / chuyên ngành.
    """
    __tablename__ = "ca_lam_viec"

    ma_ca = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ten_ca = Column(String(100), nullable=False)
    gio_bat_dau = Column(Time, nullable=False)
    gio_ket_thuc = Column(Time, nullable=False)
    cac_ngay_trong_tuan = Column(String(255), nullable=False)
    ngay_dien_ra = Column(Date, nullable=True)
    chuyen_nganh = Column(String(100), nullable=True)
    ma_chuong_trinh = Column(Integer, nullable=True)
    ghi_chu = Column(String(255), nullable=True)
    trang_thai = Column(String(50), default="HoatDong")  # HoatDong, TamNgung
    ngay_tao = Column(DateTime, default=datetime.now)

    def to_dict(self):
        """Chuyển đổi thông tin ca làm việc thành dictionary chuẩn để trả về API"""
        return {
            "ma_ca": self.ma_ca,
            "ten_ca": self.ten_ca,
            "gio_bat_dau": self.gio_bat_dau.strftime("%H:%M:%S") if hasattr(self.gio_bat_dau, "strftime") else str(self.gio_bat_dau),
            "gio_ket_thuc": self.gio_ket_thuc.strftime("%H:%M:%S") if hasattr(self.gio_ket_thuc, "strftime") else str(self.gio_ket_thuc),
            "cac_ngay_trong_tuan": self.cac_ngay_trong_tuan,
            "ngay_dien_ra": self.ngay_dien_ra.isoformat() if self.ngay_dien_ra else None,
            "chuyen_nganh": self.chuyen_nganh,
            "ma_chuong_trinh": self.ma_chuong_trinh,
            "ghi_chu": self.ghi_chu,
            "trang_thai": self.trang_thai,
            "ngay_tao": self.ngay_tao.isoformat() if self.ngay_tao else None,
        }
