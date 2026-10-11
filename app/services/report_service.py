from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.schemas.report import CompletionRateResponse

class ReportService:
    @staticmethod
    def get_completion_rate(db: Session) -> CompletionRateResponse:
        """
        Truy vấn tổng số lượng sinh viên, đếm số lượng theo từng trạng thái
        (DangThucTap, HoanThanh, ThoiHoc) và tự động tính toán tỷ lệ phần trăm (%) hoàn thành.
        """
        # 1. Truy vấn tổng số lượng sinh viên trong hệ thống
        tong_so_sinh_vien = db.query(func.count(HoSoThucTap.id)).scalar() or 0

        # 2. Truy vấn đếm số lượng theo từng trạng thái bằng GROUP BY để tối ưu hiệu năng
        status_counts = (
            db.query(HoSoThucTap.trang_thai, func.count(HoSoThucTap.id))
            .group_by(HoSoThucTap.trang_thai)
            .all()
        )

        status_map = {status: count for status, count in status_counts if status is not None}

        # 3. Trích xuất số lượng theo từng trạng thái nghiệp vụ yêu cầu
        so_luong_dang_thuc_tap = status_map.get("DangThucTap", 0)
        so_luong_hoan_thanh = status_map.get("HoanThanh", 0)
        so_luong_thoi_hoc = status_map.get("ThoiHoc", 0)

        # 4. Tự động tính toán tỷ lệ phần trăm (%) hoàn thành chương trình thực tập
        # Tránh lỗi ZeroDivisionError khi tổng số lượng sinh viên bằng 0
        if tong_so_sinh_vien > 0:
            ty_le_hoan_thanh = round((so_luong_hoan_thanh / tong_so_sinh_vien) * 100.0, 2)
        else:
            ty_le_hoan_thanh = 0.0

        # Đảm bảo tỷ lệ phần trăm luôn nằm trong khoảng hợp lệ [0.0, 100.0]
        ty_le_hoan_thanh = max(0.0, min(100.0, ty_le_hoan_thanh))

        return CompletionRateResponse(
            tong_so_sinh_vien=tong_so_sinh_vien,
            so_luong_dang_thuc_tap=so_luong_dang_thuc_tap,
            so_luong_hoan_thanh=so_luong_hoan_thanh,
            so_luong_thoi_hoc=so_luong_thoi_hoc,
            ty_le_hoan_thanh=ty_le_hoan_thanh,
            chi_tiet_theo_trang_thai=status_map
        )
