import math
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong
from app.models.nguoi_dung import NguoiDung
from app.schemas.nhat_ky_hoat_dong import NhatKyHoatDongCreate, NhatKyHoatDongResponse


class AuditLogService:
    @staticmethod
    def create_log(db: Session, log_in: NhatKyHoatDongCreate) -> NhatKyHoatDong:
        """
        Lưu một bản ghi nhật ký hoạt động vào database
        """
        db_log = NhatKyHoatDong(
            ma_nguoi_dung=log_in.ma_nguoi_dung,
            hanh_dong=log_in.hanh_dong,
            endpoint=log_in.endpoint,
            phuong_thuc=log_in.phuong_thuc.upper(),
            dia_chi_ip=log_in.dia_chi_ip,
            mo_ta=log_in.mo_ta,
            thoi_gian=log_in.thoi_gian or datetime.utcnow(),
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def get_audit_logs(
        db: Session,
        search: Optional[str] = None,
        tu_ngay: Optional[datetime] = None,
        den_ngay: Optional[datetime] = None,
        ma_nguoi_dung: Optional[int] = None,
        hanh_dong: Optional[str] = None,
        phuong_thuc: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[NhatKyHoatDongResponse], int, int]:
        """
        Truy vấn danh sách nhật ký hoạt động có hỗ trợ:
        - Tìm kiếm theo từ khóa (mô tả, hành động, endpoint, IP, tên đăng nhập)
        - Lọc theo khoảng thời gian (tu_ngay, den_ngay)
        - Lọc theo người dùng (ma_nguoi_dung)
        - Lọc theo hành động (hanh_dong)
        - Lọc theo phương thức HTTP (phuong_thuc)
        - Phân trang (page, page_size)
        
        Trả về: (danh_sach_logs, tong_so_ban_ghi, tong_so_trang)
        """
        query = db.query(NhatKyHoatDong).outerjoin(
            NguoiDung, NhatKyHoatDong.ma_nguoi_dung == NguoiDung.ma_nguoi_dung
        ).options(joinedload(NhatKyHoatDong.nguoi_dung))

        # 1. Tìm kiếm tổng quát theo từ khóa
        if search and search.strip():
            keyword = f"%{search.strip()}%"
            search_filter = or_(
                NhatKyHoatDong.mo_ta.ilike(keyword),
                NhatKyHoatDong.hanh_dong.ilike(keyword),
                NhatKyHoatDong.endpoint.ilike(keyword),
                NhatKyHoatDong.dia_chi_ip.ilike(keyword),
                NguoiDung.ten_dang_nhap.ilike(keyword),
                NguoiDung.ho_ten.ilike(keyword),
            )
            query = query.filter(search_filter)

        # 2. Lọc theo khoảng ngày
        if tu_ngay:
            query = query.filter(NhatKyHoatDong.thoi_gian >= tu_ngay)
        if den_ngay:
            query = query.filter(NhatKyHoatDong.thoi_gian <= den_ngay)

        # 3. Lọc theo người dùng
        if ma_nguoi_dung is not None:
            query = query.filter(NhatKyHoatDong.ma_nguoi_dung == ma_nguoi_dung)

        # 4. Lọc theo hành động
        if hanh_dong and hanh_dong.strip():
            query = query.filter(NhatKyHoatDong.hanh_dong.ilike(f"%{hanh_dong.strip()}%"))

        # 5. Lọc theo phương thức HTTP
        if phuong_thuc and phuong_thuc.strip():
            query = query.filter(NhatKyHoatDong.phuong_thuc == phuong_thuc.strip().upper())

        # Đếm tổng số bản ghi thỏa điều kiện
        total = query.count()

        # Tính tổng số trang
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        # Sắp xếp thời gian giảm dần (mới nhất lên đầu)
        query = query.order_by(desc(NhatKyHoatDong.thoi_gian), desc(NhatKyHoatDong.ma_nhat_ky))

        # Phân trang
        offset = (page - 1) * page_size
        db_items = query.offset(offset).limit(page_size).all()

        # Map dữ liệu sang schema response
        items: List[NhatKyHoatDongResponse] = []
        for item in db_items:
            res_item = NhatKyHoatDongResponse(
                ma_nhat_ky=item.ma_nhat_ky,
                ma_nguoi_dung=item.ma_nguoi_dung,
                hanh_dong=item.hanh_dong,
                endpoint=item.endpoint,
                phuong_thuc=item.phuong_thuc,
                dia_chi_ip=item.dia_chi_ip,
                mo_ta=item.mo_ta,
                thoi_gian=item.thoi_gian,
                ten_dang_nhap=item.nguoi_dung.ten_dang_nhap if item.nguoi_dung else None,
                ho_ten=item.nguoi_dung.ho_ten if item.nguoi_dung else None,
                vai_tro=item.nguoi_dung.vai_tro if item.nguoi_dung else None,
            )
            items.append(res_item)

        return items, total, total_pages


audit_log_service = AuditLogService()
