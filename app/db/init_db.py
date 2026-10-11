from app.core.database import Base, engine, SessionLocal
from app.models.ho_so import HoSo
from app.models.yeu_cau_ho_tro import YeuCauHoTro


def init_db():
    Base.metadata.create_all(bind=engine)

    # Seed sample data if empty
    db = SessionLocal()
    try:
        sample_ho_so = db.query(HoSo).first()
        if not sample_ho_so:
            sample_ho_so = HoSo(
                ma_sinh_vien="SV001",
                ho_ten="Nguyễn Văn A",
                email="nguyenvana@ictu.edu.vn",
                so_dien_thoai="0987654321",
                ma_mentor=1,
                trang_thai="DangThucTap"
            )
            db.add(sample_ho_so)
            db.commit()
            db.refresh(sample_ho_so)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
