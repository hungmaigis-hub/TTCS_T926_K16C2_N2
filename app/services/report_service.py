from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.intern import Intern, InternStatus
from app.schemas.report import (
    StatusCountDetail,
    StatusPercentageDetail,
    ChartItem,
    CompletionRateReportData
)

class ReportService:
    @staticmethod
    def get_completion_rate_report(
        db: Session,
        university: Optional[str] = None,
        department: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> CompletionRateReportData:
        """
        Truy vấn tổng số lượng sinh viên, đếm số lượng theo từng trạng thái
        (DangThucTap, HoanThanh, ThoiHoc) và tự động tính toán tỷ lệ phần trăm (%)
        hoàn thành chương trình thực tập.
        
        Tối ưu hiệu năng: Sử dụng 1 SQL Query duy nhất với func.count() và case()
        để đếm trực tiếp trên Database Engine.
        """
        
        # Xây dựng câu truy vấn tổng hợp tối ưu
        stmt = db.query(
            func.count(Intern.id).label("total"),
            func.sum(case((Intern.status == InternStatus.DangThucTap, 1), else_=0)).label("dang_thuc_tap"),
            func.sum(case((Intern.status == InternStatus.HoanThanh, 1), else_=0)).label("hoan_thanh"),
            func.sum(case((Intern.status == InternStatus.ThoiHoc, 1), else_=0)).label("thoi_hoc")
        )

        # Áp dụng các bộ lọc nghiệp vụ nếu người dùng cung cấp
        filters_applied: Dict[str, Any] = {}
        
        if university:
            stmt = stmt.filter(Intern.university.ilike(f"%{university}%"))
            filters_applied["university"] = university
        else:
            filters_applied["university"] = None

        if department:
            stmt = stmt.filter(Intern.department.ilike(f"%{department}%"))
            filters_applied["department"] = department
        else:
            filters_applied["department"] = None

        if start_date:
            stmt = stmt.filter(Intern.start_date >= start_date)
            filters_applied["start_date"] = str(start_date)
        else:
            filters_applied["start_date"] = None

        if end_date:
            stmt = stmt.filter(Intern.end_date <= end_date)
            filters_applied["end_date"] = str(end_date)
        else:
            filters_applied["end_date"] = None

        # Thực thi truy vấn
        row = stmt.first()

        total_students = int(row.total or 0) if row else 0
        dang_thuc_tap_count = int(row.dang_thuc_tap or 0) if row else 0
        hoan_thanh_count = int(row.hoan_thanh or 0) if row else 0
        thoi_hoc_count = int(row.thoi_hoc or 0) if row else 0

        # Tính toán tỷ lệ phần trăm (Tránh ZeroDivisionError khi chưa có sinh viên nào)
        if total_students > 0:
            completion_rate = round((hoan_thanh_count / total_students) * 100, 2)
            dang_thuc_tap_rate = round((dang_thuc_tap_count / total_students) * 100, 2)
            thoi_hoc_rate = round((thoi_hoc_count / total_students) * 100, 2)
        else:
            completion_rate = 0.0
            dang_thuc_tap_rate = 0.0
            thoi_hoc_rate = 0.0

        status_counts = StatusCountDetail(
            DangThucTap=dang_thuc_tap_count,
            HoanThanh=hoan_thanh_count,
            ThoiHoc=thoi_hoc_count
        )

        percentages = StatusPercentageDetail(
            DangThucTap=dang_thuc_tap_rate,
            HoanThanh=completion_rate,
            ThoiHoc=thoi_hoc_rate
        )

        # Định dạng mảng dữ liệu cho biểu đồ frontend (Recharts, Chart.js, v.v.)
        chart_data = [
            ChartItem(
                status=InternStatus.HoanThanh.value,
                label="Đã hoàn thành",
                count=hoan_thanh_count,
                percentage=completion_rate,
                color="#10B981"  # Xanh lục (Success)
            ),
            ChartItem(
                status=InternStatus.DangThucTap.value,
                label="Đang thực tập",
                count=dang_thuc_tap_count,
                percentage=dang_thuc_tap_rate,
                color="#3B82F6"  # Xanh dương (Info)
            ),
            ChartItem(
                status=InternStatus.ThoiHoc.value,
                label="Thôi học",
                count=thoi_hoc_count,
                percentage=thoi_hoc_rate,
                color="#EF4444"  # Đỏ (Danger)
            )
        ]

        # Tóm tắt thông tin nghiệp vụ
        if total_students > 0:
            summary = (
                f"Tổng số {total_students} sinh viên. "
                f"Trong đó {hoan_thanh_count} hoàn thành ({completion_rate}%), "
                f"{dang_thuc_tap_count} đang thực tập ({dang_thuc_tap_rate}%), "
                f"và {thoi_hoc_count} thôi học ({thoi_hoc_rate}%)."
            )
        else:
            summary = "Không tìm thấy dữ liệu sinh viên phù hợp với tiêu chí lọc."

        return CompletionRateReportData(
            total_students=total_students,
            status_counts=status_counts,
            completion_rate=completion_rate,
            percentages=percentages,
            chart_data=chart_data,
            summary=summary,
            filters_applied=filters_applied
        )
