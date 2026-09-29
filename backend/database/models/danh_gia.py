from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class DanhGia(Base):
    __tablename__ = "danh_gia"

    ma_danh_gia = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_ho_so = Column(Integer, ForeignKey("ho_so_thuc_tap.ma_ho_so"), nullable=False)
    ma_nguoi_danh_gia = Column(Integer, ForeignKey("nguoi_dung.ma_nguoi_dung"), nullable=False)
    loai_danh_gia = Column(String(50), nullable=False) # GiuaKy, CuoiKy
    diem_ky_nang = Column(Float, nullable=False)        # 0.0 - 10.0
    diem_thai_do = Column(Float, nullable=False)        # 0.0 - 10.0
    nhan_xet_chi_tiet = Column(Text, nullable=True)
    de_xuat_tuyen_chinh_thuc = Column(Boolean, default=False, nullable=False)

    # Thiết lập quan hệ ORM
    ho_so = relationship("HoSoThucTap", back_populates="danh_sach_danh_gia")
    nguoi_danh_gia = relationship("NguoiDung", foreign_keys=[ma_nguoi_danh_gia])

    @property
    def diem_trung_binh(self) -> float:
        """Tính điểm trung bình cộng giữa kỹ năng chuyên môn và thái độ kỷ luật"""
        return round((self.diem_ky_nang + self.diem_thai_do) / 2.0, 2)

    @property
    def xep_loai(self) -> str:
        """Xếp loại rèn luyện thực tập sinh dựa trên điểm trung bình"""
        dtb = self.diem_trung_binh
        if dtb >= 9.0:
            return "XuatSac"
        elif dtb >= 8.0:
            return "Gioi"
        elif dtb >= 6.5:
            return "Kha"
        elif dtb >= 5.0:
            return "TrungBinh"
        else:
            return "Yeu"

    def to_dict(self):
        """Hỗ trợ chuyển đổi object sang dict để trả về API"""
        return {
            "ma_danh_gia": self.ma_danh_gia,
            "ma_ho_so": self.ma_ho_so,
            "ma_nguoi_danh_gia": self.ma_nguoi_danh_gia,
            "ten_nguoi_danh_gia": self.nguoi_danh_gia.ho_ten if self.nguoi_danh_gia else None,
            "loai_danh_gia": self.loai_danh_gia,
            "diem_ky_nang": self.diem_ky_nang,
            "diem_thai_do": self.diem_thai_do,
            "diem_trung_binh": self.diem_trung_binh,
            "xep_loai": self.xep_loai,
            "nhan_xet_chi_tiet": self.nhan_xet_chi_tiet,
            "de_xuat_tuyen_chinh_thuc": self.de_xuat_tuyen_chinh_thuc,
        }
