"""
Script khởi tạo dữ liệu mẫu (Seed Data) cho hệ thống Quản lý Thực tập sinh
Người thực hiện: Nguyễn Văn Hiếu (Backend Developer)
"""
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.nguoi_dung import NguoiDung
from app.models.thong_bao import ThongBao
from datetime import datetime, timedelta


def seed():
    print("-> Đang khởi tạo các bảng cơ sở dữ liệu...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Kiểm tra nếu đã có dữ liệu thì không seed lại
        if db.query(NguoiDung).count() > 0:
            print("-> Dữ liệu người dùng đã tồn tại. Bỏ qua bước seed.")
            return

        print("-> Đang tạo tài khoản người dùng mẫu...")
        hieu = NguoiDung(
            email="hieu.nguyen@example.com",
            mat_khau_hash=get_password_hash("123456"),
            ho_ten="Nguyễn Văn Hiếu",
            vai_tro="ThucTapSinh",
            kich_hoat=True
        )
        hoang = NguoiDung(
            email="hoang.duong@example.com",
            mat_khau_hash=get_password_hash("123456"),
            ho_ten="Dương Đình Hoàng",
            vai_tro="HR",
            kich_hoat=True
        )
        huy = NguoiDung(
            email="huy.le@example.com",
            mat_khau_hash=get_password_hash("123456"),
            ho_ten="Lê Quang Huy",
            vai_tro="Mentor",
            kich_hoat=True
        )
        db.add_all([hieu, hoang, huy])
        db.commit()
        db.refresh(hieu)
        db.refresh(hoang)
        db.refresh(huy)

        print(f"   [+] Đã tạo user: {hieu.ho_ten} (ID: {hieu.ma_nguoi_dung}, Email: {hieu.email})")
        print(f"   [+] Đã tạo user: {hoang.ho_ten} (ID: {hoang.ma_nguoi_dung}, Email: {hoang.email})")
        print(f"   [+] Đã tạo user: {huy.ho_ten} (ID: {huy.ma_nguoi_dung}, Email: {huy.email})")

        print("-> Đang tạo danh sách thông báo mẫu cho Nguyễn Văn Hiếu...")
        now = datetime.utcnow()
        notifications = [
            ThongBao(
                ma_nguoi_nhan=hieu.ma_nguoi_dung,
                tieu_de="Lịch họp tiếp nhận thực tập sinh K16C2",
                noi_dung="Buổi gặp mặt và phổ biến quy chế thực tập diễn ra vào 08:30 ngày 20/10 tại phòng họp 302 (hoặc qua Google Meet).",
                loai_thong_bao="LICH_TRINH",
                da_doc=False,
                ngay_tao=now - timedelta(hours=2)
            ),
            ThongBao(
                ma_nguoi_nhan=hieu.ma_nguoi_dung,
                tieu_de="Phân công người hướng dẫn (Mentor)",
                noi_dung="Anh Lê Quang Huy đã được chỉ định làm Mentor đồng hành cùng bạn trong đề tài tốt nghiệp đợt này.",
                loai_thong_bao="CONG_VIEC",
                da_doc=False,
                ngay_tao=now - timedelta(hours=5)
            ),
            ThongBao(
                ma_nguoi_nhan=hieu.ma_nguoi_dung,
                tieu_de="Nhắc nhở nộp báo cáo tiến độ tuần 1",
                noi_dung="Hạn chót nộp báo cáo tuần 1 trên hệ thống là 17:00 Thứ Sáu tuần này. Vui lòng cập nhật đầy đủ công việc.",
                loai_thong_bao="CONG_VIEC",
                da_doc=False,
                ngay_tao=now - timedelta(days=1)
            ),
            ThongBao(
                ma_nguoi_nhan=hieu.ma_nguoi_dung,
                tieu_de="Hồ sơ thực tập của bạn đã được duyệt",
                noi_dung="Phòng Nhân sự (HR) đã phê duyệt hồ sơ tiếp nhận thực tập sinh của bạn. Chúc bạn có kỳ thực tập hiệu quả!",
                loai_thong_bao="HE_THONG",
                da_doc=True,
                ngay_tao=now - timedelta(days=2)
            ),
            ThongBao(
                ma_nguoi_nhan=hieu.ma_nguoi_dung,
                tieu_de="Cập nhật quy định chấm công QR code",
                noi_dung="Từ tuần này, toàn bộ thực tập sinh sẽ điểm danh check-in/out qua mã QR tại quầy lễ tân.",
                loai_thong_bao="CHUNG",
                da_doc=False,
                ngay_tao=now - timedelta(days=3)
            ),
            # Thông báo cho Dương Đình Hoàng
            ThongBao(
                ma_nguoi_nhan=hoang.ma_nguoi_dung,
                tieu_de="Yêu cầu duyệt danh sách thực tập sinh mới",
                noi_dung="Có 15 hồ sơ ứng viên đang chờ duyệt từ các trường Đại học.",
                loai_thong_bao="HE_THONG",
                da_doc=False,
                ngay_tao=now - timedelta(hours=1)
            )
        ]

        db.add_all(notifications)
        db.commit()
        print(f"   [+] Đã tạo thành công {len(notifications)} thông báo mẫu.")
        print("-> Seed data hoàn tất thành công! Sẵn sàng cho Backend, Frontend và Tester.")

    except Exception as e:
        db.rollback()
        print(f"-> Lỗi khi seed dữ liệu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
