import math
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, func, extract

from database.models.nhat_ky_hoat_dong import NhatKyHoatDong
from database.models.nguoi_dung import NguoiDung


def record_audit_log(
    db: Session,
    hanh_dong: str,
    endpoint: str,
    phuong_thuc: str,
    ma_nguoi_dung: Optional[int] = None,
    dia_chi_ip: Optional[str] = "127.0.0.1",
    mo_ta: Optional[str] = None,
    trang_thai_http: int = 200,
    thoi_gian: Optional[datetime] = None
) -> NhatKyHoatDong:
    """
    Ghi nhận một sự kiện nhật ký hoạt động hệ thống vào CSDL
    """
    log_entry = NhatKyHoatDong(
        ma_nguoi_dung=ma_nguoi_dung,
        hanh_dong=hanh_dong,
        endpoint=endpoint,
        phuong_thuc=phuong_thuc.upper(),
        dia_chi_ip=dia_chi_ip,
        mo_ta=mo_ta,
        trang_thai_http=trang_thai_http,
        thoi_gian=thoi_gian or datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_audit_logs(
    db: Session,
    tu_khoa: Optional[str] = None,
    hanh_dong: Optional[str] = None,
    phuong_thuc: Optional[str] = None,
    tu_ngay: Optional[str] = None,
    den_ngay: Optional[str] = None,
    page: int = 1,
    page_size: int = 15
) -> Dict[str, Any]:
    """
    Truy vấn nhật ký hoạt động kèm thống kê KPI và phân trang
    """
    # Tự động nạp dữ liệu mẫu ban đầu nếu bảng rỗng
    if db.query(NhatKyHoatDong).count() == 0:
        seed_sample_audit_logs(db)

    query = db.query(NhatKyHoatDong).outerjoin(
        NguoiDung, NhatKyHoatDong.ma_nguoi_dung == NguoiDung.ma_nguoi_dung
    ).options(joinedload(NhatKyHoatDong.nguoi_dung))

    # 1. Tìm kiếm theo từ khóa
    if tu_khoa and tu_khoa.strip():
        kw = f"%{tu_khoa.strip()}%"
        query = query.filter(
            or_(
                NhatKyHoatDong.mo_ta.ilike(kw),
                NhatKyHoatDong.hanh_dong.ilike(kw),
                NhatKyHoatDong.endpoint.ilike(kw),
                NhatKyHoatDong.dia_chi_ip.ilike(kw),
                NguoiDung.ho_ten.ilike(kw),
                NguoiDung.email.ilike(kw),
            )
        )

    # 2. Lọc theo hành động
    if hanh_dong and hanh_dong.strip():
        query = query.filter(NhatKyHoatDong.hanh_dong.ilike(f"%{hanh_dong.strip()}%"))

    # 3. Lọc theo phương thức HTTP
    if phuong_thuc and phuong_thuc.strip():
        query = query.filter(NhatKyHoatDong.phuong_thuc == phuong_thuc.strip().upper())

    # 4. Lọc theo khoảng ngày
    if tu_ngay and tu_ngay.strip():
        try:
            dt_from = datetime.fromisoformat(tu_ngay.strip())
            query = query.filter(NhatKyHoatDong.thoi_gian >= dt_from)
        except Exception:
            pass

    if den_ngay and den_ngay.strip():
        try:
            dt_to = datetime.fromisoformat(den_ngay.strip())
            # Nếu chỉ truyền ngày YYYY-MM-DD thì cộng đến hết ngày
            if len(den_ngay.strip()) <= 10:
                dt_to = dt_to + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(NhatKyHoatDong.thoi_gian <= dt_to)
        except Exception:
            pass

    total = query.count()
    page = max(1, page)
    page_size = max(1, min(10000, page_size))
    total_pages = max(1, math.ceil(total / page_size))

    # Sắp xếp mới nhất lên đầu
    query = query.order_by(desc(NhatKyHoatDong.thoi_gian), desc(NhatKyHoatDong.ma_nhat_ky))
    offset = (page - 1) * page_size
    records = query.offset(offset).limit(page_size).all()

    # Thống kê tổng quan KPI
    today = datetime.utcnow().date()
    today_count = db.query(NhatKyHoatDong).filter(
        func.date(NhatKyHoatDong.thoi_gian) == today
    ).count()

    total_all = db.query(NhatKyHoatDong).count()
    success_count = db.query(NhatKyHoatDong).filter(
        NhatKyHoatDong.trang_thai_http >= 200,
        NhatKyHoatDong.trang_thai_http < 300
    ).count()
    success_rate = round((success_count / total_all * 100), 1) if total_all > 0 else 100.0

    unique_users = db.query(func.count(func.distinct(NhatKyHoatDong.ma_nguoi_dung))).scalar() or 0

    items = []
    for r in records:
        user = r.nguoi_dung
        items.append({
            "ma_nhat_ky": r.ma_nhat_ky,
            "ma_nguoi_dung": r.ma_nguoi_dung,
            "ho_ten": user.ho_ten if user else "Hệ thống / Ẩn danh",
            "email": user.email if user else "--",
            "vai_tro": user.vai_tro if user else "System",
            "hanh_dong": r.hanh_dong,
            "endpoint": r.endpoint,
            "phuong_thuc": r.phuong_thuc,
            "dia_chi_ip": r.dia_chi_ip or "127.0.0.1",
            "mo_ta": r.mo_ta or "--",
            "trang_thai_http": r.trang_thai_http,
            "thoi_gian": r.thoi_gian.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "status_code": 200,
        "message": "Lấy danh sách nhật ký hoạt động thành công",
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "stats": {
            "total_logs": total_all,
            "today_logs": today_count,
            "success_rate": success_rate,
            "unique_users": unique_users
        },
        "items": items
    }


def seed_sample_audit_logs(db: Session):
    """
    Khởi tạo danh sách nhật ký mẫu thực tế ban đầu
    """
    admin_user = db.query(NguoiDung).filter(NguoiDung.vai_tro == "Admin").first()
    admin_id = admin_user.ma_nguoi_dung if admin_user else None

    hr_user = db.query(NguoiDung).filter(NguoiDung.vai_tro == "HR").first()
    hr_id = hr_user.ma_nguoi_dung if hr_user else admin_id

    mentor_user = db.query(NguoiDung).filter(NguoiDung.vai_tro == "Mentor").first()
    mentor_id = mentor_user.ma_nguoi_dung if mentor_user else admin_id

    now = datetime.utcnow()
    sample_logs = [
        {
            "user_id": admin_id,
            "action": "SAO_LUU_CSDL",
            "endpoint": "/api/v1/system/backup",
            "method": "POST",
            "ip": "127.0.0.1",
            "desc": "Tạo bản sao lưu dữ liệu toàn diện hệ thống: backup_intern_management_20261018.sql.gz",
            "status": 201,
            "time": now - timedelta(minutes=5)
        },
        {
            "user_id": admin_id,
            "action": "PHAN_QUYEN_RBAC",
            "endpoint": "/api/v1/admin/roles/HR/permissions",
            "method": "PUT",
            "ip": "127.0.0.1",
            "desc": "Cập nhật phân quyền 9 quyền hạn cho vai trò 'Cán Bộ HR'",
            "status": 200,
            "time": now - timedelta(minutes=25)
        },
        {
            "user_id": hr_id,
            "action": "NHAP_HO_SO_HANG_LOAT",
            "endpoint": "/api/v1/users/import",
            "method": "POST",
            "ip": "192.168.1.105",
            "desc": "Nạp danh sách 10 sinh viên thực tập từ tệp Excel và phân công Mentor hướng dẫn",
            "status": 200,
            "time": now - timedelta(hours=1, minutes=10)
        },
        {
            "user_id": hr_id,
            "action": "XET_DUYET_HO_SO",
            "endpoint": "/api/v1/interns/15/approval",
            "method": "PATCH",
            "ip": "192.168.1.105",
            "desc": "Phê duyệt hồ sơ thực tập cho sinh viên 'Nguyễn Văn An' (ICTU)",
            "status": 200,
            "time": now - timedelta(hours=2, minutes=15)
        },
        {
            "user_id": mentor_id,
            "action": "GIAO_NHIEM_VU",
            "endpoint": "/api/v1/tasks",
            "method": "POST",
            "ip": "192.168.1.118",
            "desc": "Giao nhiệm vụ 'Nghiên cứu kiến trúc Microservices & JWT Authentication' cho nhóm thực tập",
            "status": 201,
            "time": now - timedelta(hours=3, minutes=30)
        },
        {
            "user_id": admin_id,
            "action": "DANG_NHAP",
            "endpoint": "/api/v1/auth/login",
            "method": "POST",
            "ip": "127.0.0.1",
            "desc": "Đăng nhập thành công vào Cổng Quản Trị Hệ Thống ICTU",
            "status": 200,
            "time": now - timedelta(hours=4)
        },
        {
            "user_id": hr_id,
            "action": "LEN_LICH_HOP",
            "endpoint": "/api/v1/meetings",
            "method": "POST",
            "ip": "192.168.1.105",
            "desc": "Khởi tạo cuộc họp trực tuyến 'Phỏng vấn đợt tuyển thực tập sinh K16C2'",
            "status": 201,
            "time": now - timedelta(hours=5, minutes=45)
        },
        {
            "user_id": admin_id,
            "action": "DONG_BO_HRM",
            "endpoint": "/api/v1/integrations/hrm/sync",
            "method": "POST",
            "ip": "10.0.0.8",
            "desc": "Webhook đối soát & đồng bộ 15 nhân sự từ hệ thống HRM đối tác",
            "status": 200,
            "time": now - timedelta(days=1, hours=2)
        },
        {
            "user_id": None,
            "action": "CHAM_CONG_QR",
            "endpoint": "/api/v1/attendance/qr-scan",
            "method": "POST",
            "ip": "192.168.1.201",
            "desc": "Quét mã QR điểm danh ca làm việc buổi sáng (Check-in thành công)",
            "status": 200,
            "time": now - timedelta(days=1, hours=5)
        },
        {
            "user_id": admin_id,
            "action": "CAP_NHAT_NGUOI_DUNG",
            "endpoint": "/api/v1/users/1",
            "method": "PUT",
            "ip": "127.0.0.1",
            "desc": "Cập nhật thông tin liên hệ và phòng ban phụ trách",
            "status": 200,
            "time": now - timedelta(days=1, hours=8)
        }
    ]

    for log in sample_logs:
        entry = NhatKyHoatDong(
            ma_nguoi_dung=log["user_id"],
            hanh_dong=log["action"],
            endpoint=log["endpoint"],
            phuong_thuc=log["method"],
            dia_chi_ip=log["ip"],
            mo_ta=log["desc"],
            trang_thai_http=log["status"],
            thoi_gian=log["time"]
        )
        db.add(entry)

    db.commit()
