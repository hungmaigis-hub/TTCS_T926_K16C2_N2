from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import Base, engine
from app.models.ho_so import HoSo
from app.models.yeu_cau_ho_tro import YeuCauHoTro


def init_db(db: Session) -> None:
    """
    Tạo các bảng nếu chưa có và nạp sẵn dữ liệu hồ sơ mẫu phục vụ test / frontend dev.
    """
    # 1. Tạo tất cả bảng CSDL
    Base.metadata.create_all(bind=engine)

    # 2. Seed dữ liệu hồ sơ sinh viên mẫu nếu chưa có
    sample_students = [
        {
            "ma_ho_so": "HS001",
            "ho_ten": "Nguyễn Văn Hiếu",
            "email": "hieu.nguyen@example.com",
            "so_dien_thoai": "0987654321",
            "truong_dai_hoc": "Đại học Bách Khoa",
            "chuyen_nganh": "Công nghệ thông tin",
            "trang_thai": "DangThucTap",  # Hồ sơ hợp lệ
        },
        {
            "ma_ho_so": "HS002",
            "ho_ten": "Trần Thị Mai",
            "email": "mai.tran@example.com",
            "so_dien_thoai": "0912345678",
            "truong_dai_hoc": "Đại học Kinh tế Quốc dân",
            "chuyen_nganh": "Quản trị Nhân lực",
            "trang_thai": "DaTiepNhan",  # Hồ sơ hợp lệ
        },
        {
            "ma_ho_so": "HS003",
            "ho_ten": "Lê Hoàng Nam",
            "email": "nam.le@example.com",
            "so_dien_thoai": "0934567890",
            "truong_dai_hoc": "Đại học Công nghệ",
            "chuyen_nganh": "Khoa học Máy tính",
            "trang_thai": "Khoa",  # Hồ sơ BỊ KHÓA (để test lỗi 400 Bad Request)
        },
    ]

    for student_data in sample_students:
        exists = db.query(HoSo).filter(HoSo.ma_ho_so == student_data["ma_ho_so"]).first()
        if not exists:
            student = HoSo(
                **student_data,
                ngay_tao=datetime.utcnow(),
            )
            db.add(student)

    db.commit()
