import json
import math
import os
import uuid
from datetime import date, timedelta, datetime, time
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form, Query, Path as FastApiPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import extract, or_, func

from schemas import (
    FacultyReportResponse,
    FacultyReportData,
    FacultyReportSummary,
    FacultyUniversityStat,
    FacultyMajorStat,
    FacultyMajorItem,
    FacultyUniversityItem,
    FacultyInternBreakdownItem,
    InternCreate,
    InternUpdate,
    InternApprovalUpdate,
    ContractConfirmRequest,
    DocumentStatusUpdate,
    DocumentUploadResponse,
    ProgramCreate,
    ProgramResponse,
    ProgramListItem,
    ProgramListResponse,
    InternRegisterRequest,
    LoginRequest,
    AuthResponse,
    ProgramTimelineUpdate,
    ProgramTimelineResponse,
    TaskCreate,
    TaskCreateResponse,
    TaskProgressUpdate,
    TaskProgressResponse,
    MyScheduleResponse,
    ReportCreate,
    ReportResponse,
    ReportListResponse,
    ReportItemData,
    ReportPagination,
    ReportListData,
    ReportFeedbackRequest,
    ReportFeedbackResponse,
    EvaluationSummaryResponse,
    EvaluationCreate,
    EvaluationCreateResponse,
    AttendanceReportResponse,
    AttendanceReportData,
    AttendanceReportSummary,
    AttendanceReportItem,
    AttendancePagination,
    CheckInRequest,
    CheckOutRequest,
    CheckInResponse,
    CheckOutResponse,
    RollCallRequest,
    RollCallResponse,
    ShiftCreateRequest,
    ShiftCreateResponse,
    LeaveRequestCreate,
    LeaveRequestCreateResponse,
    LeaveRequestItemData,
    LeaveStatusUpdateRequest,
    LeaveStatusUpdateResponse,
    ScheduleCreate,
    ScheduleCreateResponse,
    AllowanceItem,
    AllowanceSummary,
    AllowanceDetailData,
    AllowanceResponse,
    MentorCreate,
    MentorResponse,
)
from security import get_password_hash, verify_password

# Thư mục database & models
from database.session import get_db, Base, engine
from database.models import (
    HoSoThucTap,
    NguoiDung,
    TruongDaiHoc,
    TaiLieuHoSo,
    PhongBan,
    ChuongTrinhThucTap,
    HopDong,
    NhiemVu,
    BaoCaoTuan,
    DanhGia,
    ChamCong,
    DonNghiPhep,
    DonXinNghi,
    CaLamViec,
    PhuCap,
)

from services.export_service import export_evaluations_to_excel, export_evaluations_to_pdf

# Tự động tạo các bảng CSDL còn thiếu theo model nếu chưa tồn tại
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

# Dịch vụ gửi email thông báo
from services.email_service import (
    send_document_approval_email,
    send_profile_approval_email,
    send_contract_confirmed_email,
)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="Internship Management API", version="1.0.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình thư mục uploads và mount static files
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Danh mục định dạng file cho phép và kích thước tối đa (10MB)
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024

# api post create intern
@app.post("/api/v1/interns", status_code=201)
def create_intern(intern_data: InternCreate, db: Session = Depends(get_db)):
    """
    Tạo mới hồ sơ thực tập sinh (kèm tài khoản sinh viên, trường đại học, chuyên ngành, chương trình).
    Thực hiện kiểm tra trùng lặp email/SĐT, kiểm tra khóa ngoại và lưu trữ trong cùng một Database Transaction.
    """
    # 1. Kiểm tra trùng lặp email với người dùng đã có
    existing_email = db.query(NguoiDung).filter(NguoiDung.email == intern_data.email).first()
    if existing_email:
        existing_hs = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == existing_email.ma_nguoi_dung).first()
        if existing_hs:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng")

    # 2. Kiểm tra trùng lặp số điện thoại nếu có gửi lên
    if intern_data.so_dien_thoai:
        existing_phone = db.query(NguoiDung).filter(NguoiDung.so_dien_thoai == intern_data.so_dien_thoai).first()
        if existing_phone and (not existing_email or existing_phone.ma_nguoi_dung != existing_email.ma_nguoi_dung):
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng")

    # 3. Kiểm tra mã trường đại học nếu có gửi lên
    if intern_data.ma_truong:
        truong = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == intern_data.ma_truong).first()
        if not truong:
            raise HTTPException(status_code=400, detail="Mã trường đại học không tồn tại trong hệ thống")

    # 4. Kiểm tra mã chương trình thực tập nếu có gửi lên và kiểm tra chỉ tiêu
    if intern_data.ma_chuong_trinh:
        chuong_trinh = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == intern_data.ma_chuong_trinh).first()
        if not chuong_trinh:
            raise HTTPException(status_code=400, detail="Mã chương trình thực tập không tồn tại trong hệ thống")
        count_prog = db.query(HoSoThucTap).filter(HoSoThucTap.ma_chuong_trinh == intern_data.ma_chuong_trinh).count()
        if count_prog >= 50:
            raise HTTPException(status_code=400, detail="Chương trình thực tập đã đủ chỉ tiêu sinh viên (50/50), không thể tiếp nhận thêm")

    # 5. Kiểm tra mã mentor nếu có gửi lên và kiểm tra chỉ tiêu hướng dẫn
    if intern_data.ma_mentor:
        mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_data.ma_mentor).first()
        if not mentor:
            raise HTTPException(status_code=400, detail="Mã người hướng dẫn (mentor) không tồn tại trong hệ thống")
        count_mentor = db.query(HoSoThucTap).filter(HoSoThucTap.ma_mentor == intern_data.ma_mentor).count()
        if count_mentor >= 5:
            raise HTTPException(status_code=400, detail="Mentor đã đủ chỉ tiêu hướng dẫn (tối đa 5 sinh viên)")

    try:
        # 6. Khởi tạo tài khoản người dùng hoặc tái sử dụng tài khoản sinh viên đã đăng ký
        if existing_email:
            new_user = existing_email
            if intern_data.ho_ten:
                new_user.ho_ten = intern_data.ho_ten
            if intern_data.so_dien_thoai:
                new_user.so_dien_thoai = intern_data.so_dien_thoai
        else:
            new_user = NguoiDung(
                ho_ten=intern_data.ho_ten,
                email=intern_data.email,
                so_dien_thoai=intern_data.so_dien_thoai,
                vai_tro="ThucTapSinh",
                trang_thai="HoatDong"
            )
            db.add(new_user)
            db.flush()

        # 7. Khởi tạo hồ sơ thực tập sinh (bảng HO_SO_THUC_TAP)
        new_ho_so = HoSoThucTap(
            ma_nguoi_dung=new_user.ma_nguoi_dung,
            ma_truong=intern_data.ma_truong,
            ma_chuong_trinh=intern_data.ma_chuong_trinh,
            ma_mentor=intern_data.ma_mentor,
            chuyen_nganh=intern_data.chuyen_nganh,
            trang_thai_xet_duyet=intern_data.trang_thai_xet_duyet or "ChoDuyet",
            trang_thai_thuc_tap=intern_data.trang_thai_thuc_tap or "DangThucTap"
        )
        db.add(new_ho_so)
        db.commit()
        db.refresh(new_ho_so)

        # 8. Trả về phản hồi thành công HTTP 201 Created
        return {
            "status_code": 201,
            "message": "Tạo hồ sơ thực tập sinh thành công",
            "data": new_ho_so.to_dict()
        }
    except Exception as e:
        db.rollback()
        raise e

# ==============================================================
# API TRUY VẤN LỊCH TRÌNH VÀ NHIỆM VỤ CÁ NHÂN (MY-SCHEDULE)
# ==============================================================

@app.get("/api/v1/interns/my-schedule", response_model=MyScheduleResponse)
def get_my_schedule(
    ho_so_id: int = Query(..., description="Mã hồ sơ thực tập của sinh viên"),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin lịch trình và nhiệm vụ cá nhân của thực tập sinh:
    - Ngày bắt đầu và ngày kết thúc (từ chương trình thực tập).
    - Danh sách nhiệm vụ được phân công và tiến độ hoàn thành.
    """
    # 1. Kiểm tra hồ sơ thực tập có tồn tại trong hệ thống không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == ho_so_id).first()
    if not ho_so:
        raise HTTPException(
            status_code=404, 
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {ho_so_id}"
        )

    # 2. Lấy thông tin thời gian thực tập từ chương trình liên kết
    chuong_trinh = ho_so.chuong_trinh
    ngay_bat_dau_str = chuong_trinh.ngay_bat_dau.isoformat() if (chuong_trinh and chuong_trinh.ngay_bat_dau) else None
    ngay_ket_thuc_str = chuong_trinh.ngay_ket_thuc.isoformat() if (chuong_trinh and chuong_trinh.ngay_ket_thuc) else None
    ten_chuong_trinh = chuong_trinh.ten_chuong_trinh if chuong_trinh else None

    # 3. Lấy danh sách nhiệm vụ được giao cho hồ sơ này
    tasks = db.query(NhiemVu).filter(NhiemVu.ma_ho_so == ho_so_id).all()
    danh_sach_nhiem_vu = [task.to_dict() for task in tasks]

    # 4. Trả về phản hồi đầy đủ dữ liệu
    return {
        "status_code": 200,
        "message": "Lấy lịch trình và danh sách nhiệm vụ thành công",
        "data": {
            "ma_ho_so": ho_so.ma_ho_so,
            "ho_ten": ho_so.thuc_tap_sinh.ho_ten if ho_so.thuc_tap_sinh else None,
            "ten_chuong_trinh": ten_chuong_trinh,
            "ngay_bat_dau": ngay_bat_dau_str,
            "ngay_ket_thuc": ngay_ket_thuc_str,
            "trang_thai_thuc_tap": ho_so.trang_thai_thuc_tap,
            "danh_sach_nhiem_vu": danh_sach_nhiem_vu,
        }
    }


@app.get("/api/v1/students", status_code=200)
def get_students_for_assignment(db: Session = Depends(get_db)):
    students = db.query(NguoiDung).filter(NguoiDung.vai_tro == "ThucTapSinh").order_by(NguoiDung.ma_nguoi_dung.asc()).all()
    result = []
    for s in students:
        hs = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == s.ma_nguoi_dung).first()
        prog = None
        mentor = None
        truong = None
        if hs:
            if hs.ma_chuong_trinh:
                prog = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == hs.ma_chuong_trinh).first()
            if hs.ma_mentor:
                mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == hs.ma_mentor).first()
            if hs.ma_truong:
                truong = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == hs.ma_truong).first()
        
        email_prefix = s.email.split("@")[0].upper() if "@" in s.email else f"DTC{s.ma_nguoi_dung:04d}"
        result.append({
            "ma_nguoi_dung": s.ma_nguoi_dung,
            "ho_ten": s.ho_ten,
            "email": s.email,
            "so_dien_thoai": s.so_dien_thoai or "",
            "ma_sinh_vien": email_prefix,
            "ma_ho_so": hs.ma_ho_so if hs else None,
            "chuyen_nganh": (hs.chuyen_nganh if hs else None) or "Kỹ thuật phần mềm",
            "ma_truong": hs.ma_truong if hs else 1,
            "ten_truong": truong.ten_truong if truong else "Đại học Công nghệ Thông tin & Truyền thông (ICTU)",
            "ma_chuong_trinh": hs.ma_chuong_trinh if hs else None,
            "ten_chuong_trinh": prog.ten_chuong_trinh if prog else None,
            "ngay_bat_dau": str(prog.ngay_bat_dau) if (prog and prog.ngay_bat_dau) else "2026-09-01",
            "ngay_ket_thuc": str(prog.ngay_ket_thuc) if (prog and prog.ngay_ket_thuc) else "2026-12-31",
            "ma_mentor": hs.ma_mentor if hs else None,
            "ten_mentor": mentor.ho_ten if mentor else None,
            "trang_thai_xet_duyet": hs.trang_thai_xet_duyet if hs else "ChoDuyet",
            "trang_thai_thuc_tap": hs.trang_thai_thuc_tap if hs else "DangThucTap"
        })
    return {
        "status_code": 200,
        "total": len(result),
        "data": result
    }


@app.get("/api/v1/mentors", status_code=200)
def get_mentor_list(db: Session = Depends(get_db)):
    mentors = db.query(NguoiDung).filter(NguoiDung.vai_tro.in_(["Mentor", "GiangVien"])).order_by(NguoiDung.ma_nguoi_dung.asc()).all()
    result = []
    for m in mentors:
        count = db.query(HoSoThucTap).filter(HoSoThucTap.ma_mentor == m.ma_nguoi_dung).count()
        result.append({
            "ma_nguoi_dung": m.ma_nguoi_dung,
            "ho_ten": m.ho_ten,
            "email": m.email,
            "so_dien_thoai": m.so_dien_thoai or "",
            "chuc_vu": "Mentor Doanh nghiệp" if m.vai_tro == "Mentor" else "Giảng viên hướng dẫn",
            "so_sinh_vien_huong_dan": count,
            "chi_tieu_huong_dan": 5,
            "da_du_chi_tieu": count >= 5
        })
    return {
        "status_code": 200,
        "total": len(result),
        "data": result
    }


# api get intern list
@app.get("/api/v1/interns", status_code=200)
def get_interns_list(
    trang_thai_xet_duyet: Optional[str] = None,
    trang_thai_thuc_tap: Optional[str] = None,
    ma_chuong_trinh: Optional[int] = None,
    chuyen_nganh: Optional[str] = None,
    ma_mentor: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách hồ sơ thực tập sinh từ cơ sở dữ liệu.
    Hỗ trợ lọc theo trạng thái xét duyệt, trạng thái thực tập, khóa thực tập, chuyên ngành/lớp, mentor.
    Sắp xếp theo mã hồ sơ mới nhất (desc).
    """
    query = db.query(HoSoThucTap)
    if trang_thai_xet_duyet:
        query = query.filter(HoSoThucTap.trang_thai_xet_duyet == trang_thai_xet_duyet)
    if trang_thai_thuc_tap:
        query = query.filter(HoSoThucTap.trang_thai_thuc_tap == trang_thai_thuc_tap)
    if ma_chuong_trinh:
        query = query.filter(HoSoThucTap.ma_chuong_trinh == ma_chuong_trinh)
    if chuyen_nganh and chuyen_nganh != "tat-ca":
        query = query.filter(HoSoThucTap.chuyen_nganh == chuyen_nganh)
    if ma_mentor:
        query = query.filter(HoSoThucTap.ma_mentor == ma_mentor)

    total = query.count()
    items = query.order_by(HoSoThucTap.ma_ho_so.desc()).offset(offset).limit(limit).all()

    return {
        "status_code": 200,
        "message": "Danh sách thực tập sinh",
        "total": total,
        "data": [item.to_dict() for item in items]
    }



# api get intern detail
@app.get("/api/v1/interns/{id}")
def get_intern_detail(id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết hồ sơ thực tập sinh theo mã hồ sơ (ID).
    Trả về dữ liệu tổng hợp từ hồ sơ, tài khoản người dùng, trường học và chương trình.
    """
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thực tập sinh ID: {id}")
    
    return {
        "status_code": 200,
        "message": "Thông tin thực tập sinh",
        "data": ho_so.to_dict()
    }


# api put intern update
@app.put("/api/v1/interns/{id}")
def update_intern(id: int, intern_data: InternUpdate, db: Session = Depends(get_db)):
    """
    Cập nhật thông tin hồ sơ thực tập sinh theo mã hồ sơ (ID).
    Đồng bộ cập nhật thông tin người dùng (họ tên, email, sđt) và thông tin hồ sơ (chuyên ngành, trường, trạng thái).
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong CSDL không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thực tập sinh ID: {id}")
    
    user = ho_so.thuc_tap_sinh
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài khoản người dùng liên kết với hồ sơ ID: {id}")

    # 2. Kiểm tra trùng lặp email với người dùng khác
    existing_email = db.query(NguoiDung).filter(
        NguoiDung.email == intern_data.email,
        NguoiDung.ma_nguoi_dung != user.ma_nguoi_dung
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng")

    # 3. Kiểm tra trùng lặp số điện thoại với người dùng khác
    if intern_data.so_dien_thoai:
        existing_phone = db.query(NguoiDung).filter(
            NguoiDung.so_dien_thoai == intern_data.so_dien_thoai,
            NguoiDung.ma_nguoi_dung != user.ma_nguoi_dung
        ).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng")

    # 4. Kiểm tra mã trường đại học nếu có gửi lên
    if intern_data.ma_truong:
        truong = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == intern_data.ma_truong).first()
        if not truong:
            raise HTTPException(status_code=400, detail="Mã trường đại học không tồn tại trong hệ thống")

    # 5. Cập nhật thông tin vào bảng NGUOI_DUNG
    user.ho_ten = intern_data.ho_ten
    user.email = intern_data.email
    user.so_dien_thoai = intern_data.so_dien_thoai

    # 6. Cập nhật thông tin vào bảng HO_SO_THUC_TAP
    ho_so.chuyen_nganh = intern_data.chuyen_nganh
    ho_so.ma_truong = intern_data.ma_truong
    if intern_data.ma_chuong_trinh is not None:
        if intern_data.ma_chuong_trinh != ho_so.ma_chuong_trinh:
            count_prog = db.query(HoSoThucTap).filter(HoSoThucTap.ma_chuong_trinh == intern_data.ma_chuong_trinh).count()
            if count_prog >= 50:
                raise HTTPException(status_code=400, detail="Chương trình thực tập đã đủ chỉ tiêu sinh viên (50/50), không thể tiếp nhận thêm")
        ho_so.ma_chuong_trinh = intern_data.ma_chuong_trinh
    if intern_data.ma_mentor is not None:
        if intern_data.ma_mentor != ho_so.ma_mentor:
            count_mentor = db.query(HoSoThucTap).filter(HoSoThucTap.ma_mentor == intern_data.ma_mentor).count()
            if count_mentor >= 5:
                raise HTTPException(status_code=400, detail="Mentor đã đủ chỉ tiêu hướng dẫn (tối đa 5 sinh viên)")
        ho_so.ma_mentor = intern_data.ma_mentor
    if intern_data.trang_thai_xet_duyet:
        ho_so.trang_thai_xet_duyet = intern_data.trang_thai_xet_duyet
    if intern_data.trang_thai_thuc_tap:
        ho_so.trang_thai_thuc_tap = intern_data.trang_thai_thuc_tap

    # 7. Lưu thay đổi vào CSDL
    db.commit()
    db.refresh(ho_so)

    # 8. Trả về phản hồi thành công
    return {
        "status_code": 200,
        "message": "Cập nhật thông tin thực tập sinh thành công",
        "data": ho_so.to_dict()
    }


# api patch intern approval
@app.patch("/api/v1/interns/{id}/approval", status_code=200)
def update_intern_approval_status(
    id: int,
    approval_data: InternApprovalUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cập nhật trường trang_thai_xet_duyet trong ho_so_thuc_tap.
    Hỗ trợ alias trang_thai_duyet hoặc trang_thai_xet_duyet (ChoDuyet, DaDuyet, TuChoi)
    kèm ghi chú lý do / nhận xét tùy chọn.
    Tự động gửi email thông báo kết quả phê duyệt cho thực tập sinh qua BackgroundTasks.
    """
    # 1. Tìm hồ sơ thực tập theo ID
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thực tập sinh ID: {id}")

    # 2. Lấy trạng thái duyệt hợp lệ
    try:
        new_status = approval_data.get_status()
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    # 3. Cập nhật trường trạng thái xét duyệt
    ho_so.trang_thai_xet_duyet = new_status

    # Tự động đồng bộ trạng thái duyệt cho toàn bộ tài liệu đính kèm của hồ sơ
    if new_status == "DaDuyet":
        pending_docs = db.query(TaiLieuHoSo).filter(
            TaiLieuHoSo.ma_ho_so == id,
            TaiLieuHoSo.trang_thai_duyet != "DaDuyet"
        ).all()
        for doc in pending_docs:
            doc.trang_thai_duyet = "DaDuyet"
    elif new_status == "TuChoi":
        pending_docs = db.query(TaiLieuHoSo).filter(
            TaiLieuHoSo.ma_ho_so == id,
            TaiLieuHoSo.trang_thai_duyet == "ChoDuyet"
        ).all()
        for doc in pending_docs:
            doc.trang_thai_duyet = "TuChoi"
            if approval_data.ghi_chu:
                doc.ghi_chu = approval_data.ghi_chu

    db.commit()
    db.refresh(ho_so)

    # 4. Gửi email thông báo qua BackgroundTasks nếu thực tập sinh có email
    intern = ho_so.thuc_tap_sinh
    if intern and intern.email:
        prog_name = ho_so.chuong_trinh.ten_chuong_trinh if ho_so.chuong_trinh else None
        background_tasks.add_task(
            send_profile_approval_email,
            to_email=intern.email,
            intern_name=intern.ho_ten or "Thực tập sinh",
            program_name=prog_name,
            status=new_status,
            note=approval_data.ghi_chu
        )

    # 5. Trả về kết quả
    return {
        "status_code": 200,
        "message": "Cập nhật trạng thái xét duyệt hồ sơ thành công",
        "data": ho_so.to_dict()
    }


# ==============================================================
# API TRUY VẤN DANH SÁCH VÀ TÍNH TOÁN PHỤ CẤP THỰC TẬP SINH
# ==============================================================

@app.get("/api/v1/interns/{id}/allowances", response_model=AllowanceResponse)
def get_intern_allowances(id: int, db: Session = Depends(get_db)):
    """
    Truy vấn danh sách các khoản phụ cấp đã được phê duyệt từ bảng phu_cap theo ma_ho_so (id).
    Tự động tính toán tổng số tiền phụ cấp đã nhận (DaChiTra) và các khoản đang chờ giải ngân (ChuaChiTra)
    trả về cho Client.
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong hệ thống không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thực tập sinh ID: {id}")

    # 2. Truy vấn danh sách các khoản phụ cấp của thực tập sinh
    allowances = (
        db.query(PhuCap)
        .filter(PhuCap.ma_ho_so == id)
        .order_by(PhuCap.thang_nam.desc(), PhuCap.ma_phu_cap.desc())
        .all()
    )

    # 3. Phân loại và tự động tính toán tổng tiền
    tong_tien_da_nhan = 0.0
    tong_tien_cho_giai_ngan = 0.0
    danh_sach_phu_cap = []
    cac_khoan_da_nhan = []
    cac_khoan_cho_giai_ngan = []

    for item in allowances:
        so_tien_val = float(item.so_tien or 0.0)
        item_schema = AllowanceItem(
            ma_phu_cap=item.ma_phu_cap,
            ma_ho_so=item.ma_ho_so,
            thang_nam=item.thang_nam,
            so_tien=so_tien_val,
            trang_thai_chi_tra=item.trang_thai_chi_tra,
        )
        danh_sach_phu_cap.append(item_schema)

        if item.trang_thai_chi_tra == "DaChiTra":
            tong_tien_da_nhan += so_tien_val
            cac_khoan_da_nhan.append(item_schema)
        else:
            tong_tien_cho_giai_ngan += so_tien_val
            cac_khoan_cho_giai_ngan.append(item_schema)

    tong_tien_phu_cap = tong_tien_da_nhan + tong_tien_cho_giai_ngan

    summary = AllowanceSummary(
        tong_tien_da_nhan=round(tong_tien_da_nhan, 2),
        tong_tien_cho_giai_ngan=round(tong_tien_cho_giai_ngan, 2),
        tong_tien_phu_cap=round(tong_tien_phu_cap, 2),
        so_khoan_da_nhan=len(cac_khoan_da_nhan),
        so_khoan_cho_giai_ngan=len(cac_khoan_cho_giai_ngan),
    )

    return {
        "status_code": 200,
        "message": "Lấy danh sách phụ cấp thực tập sinh thành công",
        "data": {
            "ma_ho_so": ho_so.ma_ho_so,
            "ho_ten": ho_so.thuc_tap_sinh.ho_ten if ho_so.thuc_tap_sinh else None,
            "email": ho_so.thuc_tap_sinh.email if ho_so.thuc_tap_sinh else None,
            "summary": summary,
            "danh_sach_phu_cap": danh_sach_phu_cap,
            "cac_khoan_da_nhan": cac_khoan_da_nhan,
            "cac_khoan_cho_giai_ngan": cac_khoan_cho_giai_ngan,
        }
    }



# api patch confirm contract
@app.patch("/api/v1/contracts/{id}/confirm", status_code=200)
def confirm_contract(
    id: int,
    confirm_data: Optional[ContractConfirmRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Xác nhận ký hợp đồng thực tập điện tử và kích hoạt trạng thái thực tập:
    1. Cập nhật bảng hop_dong: trang_thai = 'DaXacNhan', ngay_ky = ngay_ky hoặc hôm nay.
    2. Cập nhật bảng ho_so_thuc_tap: trang_thai_thuc_tap = 'DangThucTap'.
    3. Tự động gửi email thông báo xác nhận thành công tới thực tập sinh qua BackgroundTasks.
    """
    if confirm_data is None:
        confirm_data = ContractConfirmRequest()

    # 1. Tìm bản ghi hợp đồng
    hop_dong = db.query(HopDong).filter(HopDong.ma_hop_dong == id).first()
    if not hop_dong:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hợp đồng ID: {id}")

    # 2. Tìm hồ sơ thực tập sinh liên kết
    ho_so = hop_dong.ho_so or db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == hop_dong.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hồ sơ thực tập liên kết với hợp đồng ID: {id}")

    # 3. Cập nhật thông tin hợp đồng
    target_status = confirm_data.trang_thai or "DaXacNhan"
    sign_date = confirm_data.ngay_ky or date.today()

    hop_dong.trang_thai = target_status
    hop_dong.ngay_ky = sign_date

    # 4. Cập nhật trạng thái thực tập trong hồ sơ
    target_internship_status = confirm_data.trang_thai_thuc_tap or "DangThucTap"
    ho_so.trang_thai_thuc_tap = target_internship_status

    # 5. Lưu vào CSDL trong một transaction nguyên tử
    db.commit()
    db.refresh(hop_dong)
    db.refresh(ho_so)

    # 6. Gửi email thông báo qua BackgroundTasks nếu sinh viên có email
    intern = ho_so.thuc_tap_sinh
    if intern and intern.email:
        background_tasks.add_task(
            send_contract_confirmed_email,
            to_email=intern.email,
            intern_name=intern.ho_ten or "Thực tập sinh",
            contract_id=hop_dong.ma_hop_dong,
            sign_date=sign_date.isoformat(),
            internship_status=target_internship_status,
            note=confirm_data.ghi_chu
        )

    return {
        "status_code": 200,
        "message": "Xác nhận ký hợp đồng và cập nhật trạng thái thực tập thành công",
        "data": hop_dong.to_dict()
    }


# api post upload document
@app.post("/api/v1/documents/upload", status_code=201)
async def upload_document(
    ma_ho_so: int = Form(..., description="Mã hồ sơ thực tập"),
    loai_tai_lieu: str = Form(..., description="Loại tài liệu: CV, DonXinThucTap, GiayGioiThieu..."),
    file: UploadFile = File(..., description="File tài liệu cần tải lên"),
    db: Session = Depends(get_db)
):
    """
    Tải lên tài liệu đính kèm cho hồ sơ thực tập (UploadFile).
    Lưu file an toàn vào thư mục uploads/ và ghi nhận bản ghi vào bảng tai_lieu_ho_so.
    """
    # 1. Validate loại tài liệu
    cleaned_loai = loai_tai_lieu.strip() if loai_tai_lieu else ""
    if not cleaned_loai:
        raise HTTPException(status_code=422, detail="Loại tài liệu không được để trống hoặc chỉ chứa khoảng trắng")

    # 2. Kiểm tra hồ sơ thực tập có tồn tại không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == ma_ho_so).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hồ sơ thực tập ID: {ma_ho_so}")

    # 3. Validate tệp tải lên
    if not file.filename:
        raise HTTPException(status_code=422, detail="Tên tệp không hợp lệ")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng tệp '{file_ext}' không được hỗ trợ. Chỉ chấp nhận các định dạng: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # 4. Đọc nội dung file & kiểm tra dung lượng tối đa 10MB
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Dung lượng tệp vượt quá giới hạn cho phép (tối đa 10MB)")

    # 5. Lưu tệp an toàn vào thư mục uploads/
    safe_token = uuid.uuid4().hex[:8]
    safe_filename = f"{ma_ho_so}_{cleaned_loai}_{safe_token}{file_ext}"
    dest_path = UPLOAD_DIR / safe_filename

    try:
        with open(dest_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu tệp trên máy chủ: {str(e)}")

    # 6. Ghi bản ghi vào bảng tai_lieu_ho_so
    relative_path = f"uploads/{safe_filename}"
    tai_lieu = TaiLieuHoSo(
        ma_ho_so=ma_ho_so,
        loai_tai_lieu=cleaned_loai,
        duong_dan_file=relative_path,
        trang_thai_duyet="ChoDuyet"
    )
    db.add(tai_lieu)
    db.commit()
    db.refresh(tai_lieu)

    return {
        "status_code": 201,
        "message": "Tải lên tài liệu thành công",
        "data": tai_lieu.to_dict()
    }


# api get documents by ho_so_id
@app.get("/api/v1/documents/{ho_so_id}")
def get_documents_by_internship_profile(ho_so_id: int, db: Session = Depends(get_db)):
    """
    Lấy danh sách tài liệu của hồ sơ thực tập theo mã hồ sơ (ho_so_id).
    """
    # 1. Kiểm tra hồ sơ thực tập có tồn tại không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == ho_so_id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hồ sơ thực tập ID: {ho_so_id}")

    # 2. Lấy danh sách tài liệu thuộc hồ sơ
    documents = db.query(TaiLieuHoSo).filter(TaiLieuHoSo.ma_ho_so == ho_so_id).all()
    return {
        "status_code": 200,
        "message": "Danh sách tài liệu của hồ sơ thực tập",
        "data": [doc.to_dict() for doc in documents]
    }


# api patch document status
@app.patch("/api/v1/documents/{id}/status")
def update_document_status(
    id: int,
    status_data: DocumentStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cập nhật trạng thái duyệt tài liệu (ChoDuyet, DaDuyet, TuChoi) theo mã tài liệu (ID).
    Tự động gửi email thông báo kết quả cho thực tập sinh thông qua BackgroundTasks.
    """
    # 1. Tìm tài liệu theo mã ID
    tai_lieu = db.query(TaiLieuHoSo).filter(TaiLieuHoSo.ma_tai_lieu == id).first()
    if not tai_lieu:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài liệu ID: {id}")

    # 2. Cập nhật trạng thái duyệt mới
    tai_lieu.trang_thai_duyet = status_data.trang_thai_duyet
    db.commit()
    db.refresh(tai_lieu)

    # 3. Kích hoạt BackgroundTasks gửi email thông báo kết quả duyệt cho thực tập sinh
    ho_so = tai_lieu.ho_so
    if ho_so and ho_so.thuc_tap_sinh and ho_so.thuc_tap_sinh.email:
        intern = ho_so.thuc_tap_sinh
        background_tasks.add_task(
            send_document_approval_email,
            to_email=intern.email,
            intern_name=intern.ho_ten or "Thực tập sinh",
            document_type=tai_lieu.loai_tai_lieu,
            status=tai_lieu.trang_thai_duyet,
            note=status_data.ghi_chu
        )

    return {
        "status_code": 200,
        "message": "Cập nhật trạng thái duyệt tài liệu thành công",
        "data": tai_lieu.to_dict()
    }


# api post approve all documents of profile
@app.post("/api/v1/documents/{ho_so_id}/approve-all", status_code=200)
def approve_all_documents_of_profile(ho_so_id: int, db: Session = Depends(get_db)):
    """
    Phê duyệt đồng loạt toàn bộ tài liệu đính kèm của hồ sơ thực tập.
    """
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == ho_so_id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hồ sơ ID: {ho_so_id}")

    docs = db.query(TaiLieuHoSo).filter(TaiLieuHoSo.ma_ho_so == ho_so_id).all()
    count = 0
    for doc in docs:
        if doc.trang_thai_duyet != "DaDuyet":
            doc.trang_thai_duyet = "DaDuyet"
            count += 1
    db.commit()
    return {
        "status_code": 200,
        "message": f"Đã phê duyệt {count} tài liệu của hồ sơ #{ho_so_id}",
        "data": [d.to_dict() for d in docs]
    }



# ==============================================================
# API QUẢN LÝ CHƯƠNG TRÌNH THỰC TẬP (PROGRAMS)
# ==============================================================

# api post create program
@app.post("/api/v1/programs", status_code=201, response_model=ProgramResponse)
def create_program(program_data: ProgramCreate, db: Session = Depends(get_db)):
    """
    Tạo mới một chương trình thực tập.
    Liên kết với phòng ban (ma_phong_ban), lưu tên chương trình, mô tả và thời gian diễn ra.
    """
    # 1. Kiểm tra phòng ban có tồn tại trong hệ thống không
    phong_ban = db.query(PhongBan).filter(PhongBan.ma_phong_ban == program_data.ma_phong_ban).first()
    if not phong_ban:
        raise HTTPException(status_code=400, detail="Mã phòng ban không tồn tại trong hệ thống")

    # 2. Kiểm tra trùng lặp tên chương trình trong cùng phòng ban
    existing_program = db.query(ChuongTrinhThucTap).filter(
        ChuongTrinhThucTap.ma_phong_ban == program_data.ma_phong_ban,
        ChuongTrinhThucTap.ten_chuong_trinh == program_data.ten_chuong_trinh
    ).first()
    if existing_program:
        raise HTTPException(status_code=400, detail="Tên chương trình thực tập này đã tồn tại trong phòng ban")

    # 3. Tính toán ngày bắt đầu và kết thúc (mặc định hôm nay và 3 tháng sau nếu không gửi)
    start_date = program_data.ngay_bat_dau or date.today()
    end_date = program_data.ngay_ket_thuc or (start_date + timedelta(days=90))

    # 4. Khởi tạo đối tượng chương trình thực tập
    new_program = ChuongTrinhThucTap(
        ma_phong_ban=program_data.ma_phong_ban,
        ten_chuong_trinh=program_data.ten_chuong_trinh,
        mo_ta=program_data.mo_ta,
        ngay_bat_dau=start_date,
        ngay_ket_thuc=end_date
    )

    # 5. Lưu vào cơ sở dữ liệu
    db.add(new_program)
    db.commit()
    db.refresh(new_program)

    # 6. Trả về phản hồi thành công (HTTP 201 Created)
    return {
        "status_code": 201,
        "message": "Tạo chương trình thực tập thành công",
        "data": new_program.to_dict()
    }


# api get all departments
@app.get("/api/v1/departments", status_code=200)
def get_departments(db: Session = Depends(get_db)):
    """
    Lấy danh sách các phòng ban tiếp nhận thực tập sinh.
    """
    departments = db.query(PhongBan).all()
    return {
        "status_code": 200,
        "message": "Lấy danh sách phòng ban thành công",
        "data": [
            {
                "ma_phong_ban": pb.ma_phong_ban,
                "ten_phong_ban": pb.ten_phong_ban,
                "mo_ta": pb.mo_ta
            } for pb in departments
        ]
    }


# api get all universities
@app.get("/api/v1/universities", status_code=200)
def get_universities(db: Session = Depends(get_db)):
    """
    Lấy danh mục các trường đại học đối tác / liên kết từ bảng truong_dai_hoc trong cơ sở dữ liệu.
    """
    universities = db.query(TruongDaiHoc).order_by(TruongDaiHoc.ma_truong.asc()).all()
    data = []
    for t in universities:
        chuyen_nganh_list = []
        if getattr(t, "danh_sach_nganh", None):
            try:
                chuyen_nganh_list = json.loads(t.danh_sach_nganh)
            except Exception:
                chuyen_nganh_list = [n.strip() for n in t.danh_sach_nganh.split(",") if n.strip()]
        data.append({
            "ma_truong": t.ma_truong,
            "ten_truong": t.ten_truong,
            "dia_chi": t.dia_chi,
            "nguoi_lien_he": t.nguoi_lien_he,
            "email_lien_he": t.email_lien_he,
            "chuyen_nganh": chuyen_nganh_list
        })
    return {
        "status_code": 200,
        "message": "Lấy danh sách trường đại học thành công",
        "data": data
    }



# api get all programs
@app.get("/api/v1/programs", status_code=200, response_model=ProgramListResponse)
def get_programs(
    ma_phong_ban: Optional[int] = Query(None, description="Lọc theo mã phòng ban"),
    tu_khoa: Optional[str] = Query(None, description="Tìm kiếm theo tên chương trình"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách các chương trình thực tập.
    Hỗ trợ lọc theo phòng ban, tìm kiếm từ khóa, tính toán thời lượng tuần và số lượng sinh viên tham gia.
    """
    query = db.query(ChuongTrinhThucTap)

    if ma_phong_ban is not None:
        if ma_phong_ban <= 0:
            raise HTTPException(status_code=422, detail="Mã phòng ban phải là số nguyên dương")
        query = query.filter(ChuongTrinhThucTap.ma_phong_ban == ma_phong_ban)

    if tu_khoa and tu_khoa.strip():
        kw = f"%{tu_khoa.strip()}%"
        query = query.filter(ChuongTrinhThucTap.ten_chuong_trinh.ilike(kw))

    total = query.count()
    programs = query.order_by(ChuongTrinhThucTap.ma_chuong_trinh.desc()).offset(skip).limit(limit).all()

    today = date.today()
    results = []
    for p in programs:
        weeks = None
        if p.ngay_bat_dau and p.ngay_ket_thuc:
            diff_days = (p.ngay_ket_thuc - p.ngay_bat_dau).days
            weeks = max(1, round(diff_days / 7))

        intern_count = db.query(HoSoThucTap).filter(HoSoThucTap.ma_chuong_trinh == p.ma_chuong_trinh).count()

        status = "Đang diễn ra"
        if p.ngay_bat_dau and today < p.ngay_bat_dau:
            status = "Sắp bắt đầu"
        elif p.ngay_ket_thuc and today > p.ngay_ket_thuc:
            status = "Đã kết thúc"

        results.append({
            "ma_chuong_trinh": p.ma_chuong_trinh,
            "ma_phong_ban": p.ma_phong_ban,
            "ten_phong_ban": p.phong_ban.ten_phong_ban if p.phong_ban else None,
            "ten_chuong_trinh": p.ten_chuong_trinh,
            "ngay_bat_dau": p.ngay_bat_dau.isoformat() if p.ngay_bat_dau else None,
            "ngay_ket_thuc": p.ngay_ket_thuc.isoformat() if p.ngay_ket_thuc else None,
            "mo_ta": p.mo_ta,
            "thoi_luong_tuan": weeks,
            "so_luong_sinh_vien": intern_count,
            "chi_tieu_sinh_vien": 50,
            "trang_thai": status
        })

    return {
        "status_code": 200,
        "message": "Lấy danh sách chương trình thực tập thành công",
        "total": total,
        "data": results
    }



@app.post("/api/v1/auth/register", status_code=201, response_model=AuthResponse)
def register_intern(data: InternRegisterRequest, db: Session = Depends(get_db)):
    if data.vai_tro and data.vai_tro != "ThucTapSinh":
        raise HTTPException(
            status_code=400,
            detail="Cổng đăng ký trực tuyến chỉ dành cho Thực tập sinh. Tài khoản Mentor hoặc Nhà trường do Quản trị viên cấp."
        )

    email_normalized = data.email.strip().lower()

    existing_user = db.query(NguoiDung).filter(NguoiDung.email == email_normalized).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng trong hệ thống")

    if data.so_dien_thoai:
        existing_phone = db.query(NguoiDung).filter(NguoiDung.so_dien_thoai == data.so_dien_thoai.strip()).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng trong hệ thống")

    if data.ma_truong:
        truong = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == data.ma_truong).first()
        if not truong:
            raise HTTPException(status_code=400, detail="Mã trường đại học không tồn tại trong hệ thống")

    hashed_password = get_password_hash(data.mat_khau)

    new_user = NguoiDung(
        ho_ten=data.ho_ten.strip(),
        email=email_normalized,
        mat_khau_hash=hashed_password,
        so_dien_thoai=data.so_dien_thoai.strip() if data.so_dien_thoai else None,
        vai_tro="ThucTapSinh",
        trang_thai="HoatDong"
    )
    db.add(new_user)
    db.flush()

    new_profile = HoSoThucTap(
        ma_nguoi_dung=new_user.ma_nguoi_dung,
        ma_truong=data.ma_truong,
        chuyen_nganh=data.chuyen_nganh.strip() if data.chuyen_nganh else None,
        trang_thai_xet_duyet="ChoDuyet",
        trang_thai_thuc_tap="DangThucTap"
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)
    db.refresh(new_profile)

    return {
        "status_code": 201,
        "message": "Đăng ký tài khoản thực tập sinh và tạo hồ sơ thành công",
        "data": {
            "ma_nguoi_dung": new_user.ma_nguoi_dung,
            "ho_ten": new_user.ho_ten,
            "email": new_user.email,
            "vai_tro": new_user.vai_tro,
            "so_dien_thoai": new_user.so_dien_thoai,
            "ma_ho_so": new_profile.ma_ho_so
        }
    }


@app.post("/api/v1/auth/login", status_code=200, response_model=AuthResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    raw_ident = data.email.strip().lower()

    user = db.query(NguoiDung).filter(
        or_(
            NguoiDung.email == raw_ident,
            NguoiDung.email == f"{raw_ident}@ictu.edu.vn",
            NguoiDung.so_dien_thoai == data.email.strip()
        )
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại trong cơ sở dữ liệu")

    if not user.mat_khau_hash or not verify_password(data.mat_khau, user.mat_khau_hash):
        raise HTTPException(status_code=401, detail="Mật khẩu không chính xác")

    if user.trang_thai == "Khoa":
        raise HTTPException(status_code=403, detail="Tài khoản này đang bị khóa")

    if data.vai_tro:
        portal = data.vai_tro.strip().lower()
        if portal == "student" and user.vai_tro != "ThucTapSinh":
            raise HTTPException(status_code=403, detail="Tài khoản này không thuộc vai trò Sinh viên")
        elif portal == "mentor" and user.vai_tro == "ThucTapSinh":
            raise HTTPException(status_code=403, detail="Tài khoản sinh viên không có quyền đăng nhập vào cổng Doanh nghiệp / Mentor")
        elif portal == "faculty" and user.vai_tro == "ThucTapSinh":
            raise HTTPException(status_code=403, detail="Tài khoản sinh viên không có quyền đăng nhập vào cổng Nhà trường / Quản lý")

    profile = db.query(HoSoThucTap).filter(HoSoThucTap.ma_nguoi_dung == user.ma_nguoi_dung).first()

    return {
        "status_code": 200,
        "message": "Đăng nhập thành công",
        "data": {
            "ma_nguoi_dung": user.ma_nguoi_dung,
            "ho_ten": user.ho_ten,
            "email": user.email,
            "vai_tro": user.vai_tro,
            "so_dien_thoai": user.so_dien_thoai,
            "ma_ho_so": profile.ma_ho_so if profile else None
        }
    }


@app.patch("/api/v1/programs/{id}/timeline", status_code=200, response_model=ProgramTimelineResponse)
def update_program_timeline(
    id: int,
    timeline_data: ProgramTimelineUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật mốc thời gian (ngay_bat_dau, ngay_ket_thuc) của chương trình thực tập.
    Validate logic: ngày kết thúc phải lớn hơn ngày bắt đầu (ngay_ket_thuc > ngay_bat_dau).
    """
    if id <= 0:
        raise HTTPException(status_code=422, detail="Mã chương trình không hợp lệ")

    program = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == id).first()
    if not program:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chương trình thực tập ID: {id}")

    new_start = timeline_data.ngay_bat_dau if timeline_data.ngay_bat_dau is not None else program.ngay_bat_dau
    new_end = timeline_data.ngay_ket_thuc if timeline_data.ngay_ket_thuc is not None else program.ngay_ket_thuc

    if new_start and new_end and new_end <= new_start:
        raise HTTPException(
            status_code=400,
            detail="Ngày kết thúc phải lớn hơn ngày bắt đầu"
        )

    if timeline_data.ngay_bat_dau is not None:
        program.ngay_bat_dau = timeline_data.ngay_bat_dau
    if timeline_data.ngay_ket_thuc is not None:
        program.ngay_ket_thuc = timeline_data.ngay_ket_thuc

    db.commit()
    db.refresh(program)

    return {
        "status_code": 200,
        "message": "Cập nhật thời gian chương trình thực tập thành công",
        "data": program.to_dict()
    }
# ==============================================================
# API QUẢN LÝ NHIỆM VỤ THỰC TẬP (TASKS)
# ==============================================================

# api patch task progress
@app.patch("/api/v1/tasks/{id}/progress", status_code=200, response_model=TaskProgressResponse)
def update_task_progress(
    id: int,
    progress_data: TaskProgressUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật tiến độ hoàn thành của nhiệm vụ (tien_do_phantram từ 0 đến 100%).
    Tự động cập nhật trang_thai:
    - Nếu tien_do_phantram == 100: tự động chuyển sang "Hoàn thành"
    - Nếu 0 < tien_do_phantram < 100: chuyển sang "Đang thực hiện"
    - Nếu tien_do_phantram == 0: chuyển sang "Chưa bắt đầu"
    """
    # 1. Kiểm tra ID hợp lệ
    if id <= 0:
        raise HTTPException(status_code=422, detail="Mã nhiệm vụ không hợp lệ")

    # 2. Tìm nhiệm vụ trong CSDL
    task = db.query(NhiemVu).filter(NhiemVu.ma_nhiem_vu == id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhiệm vụ ID: {id}")

    # 3. Cập nhật tiến độ phần trăm
    task.tien_do_phantram = progress_data.tien_do_phantram

    # 4. Tự động chuyển đổi trạng thái tương ứng
    if progress_data.tien_do_phantram == 100:
        task.trang_thai = "Hoàn thành"
    elif progress_data.tien_do_phantram > 0:
        task.trang_thai = "Đang thực hiện"
    else:
        task.trang_thai = "Chưa bắt đầu"

    # 5. Lưu vào CSDL
    db.commit()
    db.refresh(task)

    # 6. Trả về phản hồi thành công
    return {
        "status_code": 200,
        "message": "Cập nhật tiến độ nhiệm vụ thành công",
        "data": task.to_dict()
    }


# ==============================================================
# API BÁO CÁO TUẦN (REPORTS)
# ==============================================================

@app.post("/api/v1/reports", status_code=201, response_model=ReportResponse)
def create_weekly_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    """
    Nộp báo cáo định kỳ tuần của thực tập sinh:
    - Lưu mã hồ sơ (ma_ho_so), mã nhiệm vụ liên kết (ma_nhiem_vu tùy chọn).
    - Lưu số tuần (tuan_so), nội dung công việc (noi_dung_cong_viec), kết quả đạt được (ket_qua_dat_duoc).
    - Tự động gán thoi_gian_nop = datetime.now() tại thời điểm nộp.
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong hệ thống không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == report_data.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {report_data.ma_ho_so}"
        )

    # 2. Kiểm tra mã nhiệm vụ nếu có gửi lên
    if report_data.ma_nhiem_vu is not None:
        nhiem_vu = db.query(NhiemVu).filter(NhiemVu.ma_nhiem_vu == report_data.ma_nhiem_vu).first()
        if not nhiem_vu:
            raise HTTPException(
                status_code=400,
                detail=f"Mã nhiệm vụ không tồn tại trong hệ thống: {report_data.ma_nhiem_vu}"
            )
        if nhiem_vu.ma_ho_so != report_data.ma_ho_so:
            raise HTTPException(
                status_code=400,
                detail="Nhiệm vụ không thuộc về hồ sơ thực tập sinh này"
            )

    # 3. Khởi tạo đối tượng báo cáo tuần kèm gán thoi_gian_nop = datetime.now()
    new_report = BaoCaoTuan(
        ma_ho_so=report_data.ma_ho_so,
        ma_nhiem_vu=report_data.ma_nhiem_vu,
        tuan_so=report_data.tuan_so,
        noi_dung_cong_viec=report_data.noi_dung_cong_viec,
        ket_qua_dat_duoc=report_data.ket_qua_dat_duoc,
        thoi_gian_nop=datetime.now()
    )

    # 4. Lưu vào CSDL
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # 5. Trả về phản hồi thành công (HTTP 201 Created)
    return {
        "status_code": 201,
        "message": "Nộp báo cáo tuần thành công",
        "data": new_report.to_dict()
    }


def format_report_item(report: BaoCaoTuan) -> dict:
    """Helper chuyển đổi bản ghi BaoCaoTuan và các quan hệ liên kết thành dict chi tiết"""
    hs = report.ho_so
    sinh_vien = hs.thuc_tap_sinh if hs else None
    mentor_obj = hs.mentor if hs else None
    nv = report.nhiem_vu

    return {
        "ma_bao_cao": report.ma_bao_cao,
        "ma_ho_so": report.ma_ho_so,
        "ma_nguoi_dung": sinh_vien.ma_nguoi_dung if sinh_vien else None,
        "ho_ten_sinh_vien": sinh_vien.ho_ten if sinh_vien else None,
        "email_sinh_vien": sinh_vien.email if sinh_vien else None,
        "ma_mentor": hs.ma_mentor if hs else None,
        "ho_ten_mentor": mentor_obj.ho_ten if mentor_obj else None,
        "ma_nhiem_vu": report.ma_nhiem_vu,
        "ten_nhiem_vu": nv.ten_nhiem_vu if nv else None,
        "tuan_so": report.tuan_so,
        "noi_dung_cong_viec": report.noi_dung_cong_viec,
        "ket_qua_dat_duoc": report.ket_qua_dat_duoc,
        "phan_hoi_mentor": report.phan_hoi_mentor,
        "thoi_gian_nop": report.thoi_gian_nop.isoformat() if report.thoi_gian_nop else None,
    }


@app.get("/api/v1/reports", response_model=ReportListResponse)
def get_weekly_reports(
    ma_mentor: Optional[int] = Query(None, description="Lọc báo cáo theo sinh viên mà Mentor phụ trách"),
    ma_ho_so: Optional[int] = Query(None, description="Lọc báo cáo theo mã hồ sơ thực tập sinh"),
    tuan_so: Optional[int] = Query(None, ge=1, description="Lọc theo tuần số"),
    da_phan_hoi: Optional[bool] = Query(None, description="Lọc theo trạng thái đã có phản hồi hay chưa (true/false)"),
    tu_khoa: Optional[str] = Query(None, description="Tìm kiếm từ khóa trong nội dung hoặc họ tên sinh viên"),
    page: int = Query(1, ge=1, description="Số trang hiện tại (>= 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng bản ghi mỗi trang (1 - 100)"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách báo cáo tuần:
    - Hỗ trợ lọc theo mã Mentor phụ trách (ma_mentor).
    - Hỗ trợ lọc theo mã hồ sơ thực tập (ma_ho_so), tuần số (tuan_so), trạng thái phản hồi (da_phan_hoi).
    - Hỗ trợ tìm kiếm từ khóa theo nội dung hoặc tên sinh viên (tu_khoa).
    - Hỗ trợ phân trang chuẩn RESTful (page, page_size).
    """
    # 1. Nếu có ma_mentor, kiểm tra mentor có tồn tại trong hệ thống không
    if ma_mentor is not None:
        mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == ma_mentor).first()
        if not mentor:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thông tin Mentor với mã ID: {ma_mentor}"
            )

    # 2. Xây dựng truy vấn cơ sở kết hợp các bảng liên quan
    query = (
        db.query(BaoCaoTuan)
        .join(HoSoThucTap, BaoCaoTuan.ma_ho_so == HoSoThucTap.ma_ho_so)
        .outerjoin(NguoiDung, HoSoThucTap.ma_nguoi_dung == NguoiDung.ma_nguoi_dung)
    )

    # 3. Áp dụng các điều kiện lọc
    if ma_mentor is not None:
        query = query.filter(HoSoThucTap.ma_mentor == ma_mentor)

    if ma_ho_so is not None:
        query = query.filter(BaoCaoTuan.ma_ho_so == ma_ho_so)

    if tuan_so is not None:
        query = query.filter(BaoCaoTuan.tuan_so == tuan_so)

    if da_phan_hoi is not None:
        if da_phan_hoi:
            query = query.filter(BaoCaoTuan.phan_hoi_mentor.isnot(None), BaoCaoTuan.phan_hoi_mentor != "")
        else:
            query = query.filter(or_(BaoCaoTuan.phan_hoi_mentor.is_(None), BaoCaoTuan.phan_hoi_mentor == ""))

    if tu_khoa:
        keyword = f"%{tu_khoa.strip()}%"
        query = query.filter(
            or_(
                BaoCaoTuan.noi_dung_cong_viec.ilike(keyword),
                BaoCaoTuan.ket_qua_dat_duoc.ilike(keyword),
                NguoiDung.ho_ten.ilike(keyword)
            )
        )

    # 4. Tính toán phân trang
    total_items = query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    offset = (page - 1) * page_size

    # Sắp xếp mặc định: thời gian nộp mới nhất lên đầu, tiếp đến mã báo cáo giảm dần
    reports = (
        query.order_by(BaoCaoTuan.thoi_gian_nop.desc(), BaoCaoTuan.ma_bao_cao.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 5. Format danh sách kết quả
    items = [format_report_item(r) for r in reports]

    return {
        "status_code": 200,
        "message": "Lấy danh sách báo cáo tuần thành công",
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }
    }


@app.post("/api/v1/reports/{id}/feedback", response_model=ReportFeedbackResponse)
def submit_report_feedback(
    id: int = FastApiPath(..., gt=0, description="Mã báo cáo tuần cần gửi phản hồi"),
    feedback_data: ReportFeedbackRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Gửi phản hồi / ghi nhận của Mentor cho báo cáo tuần:
    - Tìm báo cáo tuần theo mã ID (ma_bao_cao).
    - Nếu gửi kèm ma_mentor, kiểm tra mentor có tồn tại và có phụ trách thực tập sinh này không.
    - Cập nhật trường phan_hoi_mentor và lưu vào cơ sở dữ liệu.
    """
    # 1. Tìm báo cáo tuần trong cơ sở dữ liệu
    report = db.query(BaoCaoTuan).filter(BaoCaoTuan.ma_bao_cao == id).first()
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy báo cáo tuần với mã ID: {id}"
        )

    # 2. Kiểm tra quyền của mentor nếu có gửi ma_mentor
    ho_so = report.ho_so
    if feedback_data.ma_mentor is not None:
        mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == feedback_data.ma_mentor).first()
        if not mentor:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy thông tin Mentor với mã ID: {feedback_data.ma_mentor}"
            )
        if ho_so and ho_so.ma_mentor != feedback_data.ma_mentor:
            raise HTTPException(
                status_code=403,
                detail="Mentor không có quyền phản hồi báo cáo này do không phụ trách sinh viên tương ứng"
            )

    # 3. Cập nhật phản hồi vào báo cáo
    report.phan_hoi_mentor = feedback_data.phan_hoi_mentor
    db.commit()
    db.refresh(report)

    # 4. Trả về kết quả
    return {
        "status_code": 200,
        "message": "Gửi phản hồi báo cáo tuần thành công",
        "data": format_report_item(report)
    }


# ==============================================================
# API BÁO CÁO TỔNG HỢP CHẤM CÔNG (ATTENDANCE REPORTS API)
# ==============================================================
@app.get("/api/v1/attendance/reports", response_model=AttendanceReportResponse)
def get_attendance_reports(
    thang: Optional[int] = Query(None, ge=1, le=12, description="Tháng báo cáo (1 - 12)"),
    nam: Optional[int] = Query(None, ge=2000, description="Năm báo cáo (mặc định năm hiện tại)"),
    ma_phong_ban: Optional[int] = Query(None, description="Lọc theo mã phòng ban"),
    gio_chuan: str = Query("08:30:00", description="Giờ chuẩn bắt đầu làm việc (HH:MM:SS) để tính đi muộn"),
    page: int = Query(1, ge=1, description="Trang hiện tại (>= 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng bản ghi trên một trang (1 - 100)"),
    db: Session = Depends(get_db),
):
    """
    Endpoint lọc và tổng hợp dữ liệu chấm công của thực tập sinh:
    - Lọc theo tháng, năm, phòng ban.
    - Tổng hợp số ngày đi làm, số lần đi muộn (so với giờ chuẩn), số ngày nghỉ có phép (đơn đã duyệt).
    - Trả về KPI tổng quan và danh sách chi tiết có hỗ trợ phân trang.
    """
    target_year = nam if nam is not None else datetime.now().year
    target_month = thang

    # 1. Parse giờ chuẩn quy định
    try:
        gio_chuan_time = datetime.strptime(gio_chuan, "%H:%M:%S").time()
    except ValueError:
        gio_chuan_time = time(8, 30, 0)

    # 2. Kiểm tra phòng ban nếu có truyền ma_phong_ban
    ten_phong_ban = None
    if ma_phong_ban is not None:
        pb = db.query(PhongBan).filter(PhongBan.ma_phong_ban == ma_phong_ban).first()
        if not pb:
            raise HTTPException(status_code=404, detail="Phòng ban không tồn tại")
        ten_phong_ban = pb.ten_phong_ban

    # 3. Xác định khoảng thời gian lọc (SARGable query tối ưu index)
    if target_month is not None:
        start_date = date(target_year, target_month, 1)
        if target_month == 12:
            end_date = date(target_year + 1, 1, 1)
        else:
            end_date = date(target_year, target_month + 1, 1)
    else:
        start_date = date(target_year, 1, 1)
        end_date = date(target_year + 1, 1, 1)

    # 4. Lấy danh sách hồ sơ thực tập sinh
    query_hs = db.query(HoSoThucTap).join(NguoiDung, HoSoThucTap.ma_nguoi_dung == NguoiDung.ma_nguoi_dung)
    if ma_phong_ban is not None:
        query_hs = query_hs.outerjoin(ChuongTrinhThucTap, HoSoThucTap.ma_chuong_trinh == ChuongTrinhThucTap.ma_chuong_trinh)
        query_hs = query_hs.filter(
            or_(
                ChuongTrinhThucTap.ma_phong_ban == ma_phong_ban,
                NguoiDung.ma_phong_ban == ma_phong_ban
            )
        )

    ho_so_list = query_hs.order_by(HoSoThucTap.ma_ho_so.asc()).all()

    # 5. Tính toán cho từng hồ sơ
    all_items = []
    tong_so_ngay_di_lam = 0
    tong_so_lan_di_muon = 0
    tong_so_ngay_nghi = 0

    for hs in ho_so_list:
        user = hs.thuc_tap_sinh
        ho_ten = user.ho_ten if user else f"Thực tập sinh #{hs.ma_ho_so}"
        email = user.email if user else ""

        # Xác định phòng ban của TTS
        hs_phong_ban_id = None
        hs_ten_phong_ban = None
        if hs.chuong_trinh and hs.chuong_trinh.phong_ban:
            hs_phong_ban_id = hs.chuong_trinh.phong_ban.ma_phong_ban
            hs_ten_phong_ban = hs.chuong_trinh.phong_ban.ten_phong_ban
        elif user and user.phong_ban:
            hs_phong_ban_id = user.phong_ban.ma_phong_ban
            hs_ten_phong_ban = user.phong_ban.ten_phong_ban

        # Truy vấn chấm công
        cc_query = db.query(ChamCong).filter(
            ChamCong.ma_ho_so == hs.ma_ho_so,
            ChamCong.ngay_cham_cong >= start_date,
            ChamCong.ngay_cham_cong < end_date
        )
        cham_cong_records = cc_query.all()

        so_ngay_di_lam = len(cham_cong_records)
        so_lan_di_muon = 0
        for cc in cham_cong_records:
            if cc.gio_check_in and cc.gio_check_in > gio_chuan_time:
                so_lan_di_muon += 1

        # Truy vấn đơn nghỉ phép đã duyệt
        dnp_query = db.query(DonNghiPhep).filter(
            DonNghiPhep.ma_ho_so == hs.ma_ho_so,
            DonNghiPhep.trang_thai == "DaDuyet",
            DonNghiPhep.ngay_nghi >= start_date,
            DonNghiPhep.ngay_nghi < end_date
        )
        so_ngay_nghi = dnp_query.count()

        # Cộng dồn KPI
        tong_so_ngay_di_lam += so_ngay_di_lam
        tong_so_lan_di_muon += so_lan_di_muon
        tong_so_ngay_nghi += so_ngay_nghi

        all_items.append(
            AttendanceReportItem(
                ma_ho_so=hs.ma_ho_so,
                ma_nguoi_dung=hs.ma_nguoi_dung,
                ho_ten=ho_ten,
                email=email,
                ma_phong_ban=hs_phong_ban_id,
                ten_phong_ban=hs_ten_phong_ban,
                chuyen_nganh=hs.chuyen_nganh,
                so_ngay_di_lam=so_ngay_di_lam,
                so_lan_di_muon=so_lan_di_muon,
                so_ngay_nghi=so_ngay_nghi,
            )
        )

    # 5. Tính toán KPI tổng quan
    tong_so_tts = len(all_items)
    ty_le_di_muon = round((tong_so_lan_di_muon / tong_so_ngay_di_lam * 100), 2) if tong_so_ngay_di_lam > 0 else 0.0
    trung_binh_ngay_cong = round(tong_so_ngay_di_lam / tong_so_tts, 2) if tong_so_tts > 0 else 0.0

    summary = AttendanceReportSummary(
        thang=target_month,
        nam=target_year,
        ma_phong_ban=ma_phong_ban,
        ten_phong_ban=ten_phong_ban,
        tong_so_thuc_tap_sinh=tong_so_tts,
        tong_so_ngay_di_lam=tong_so_ngay_di_lam,
        tong_so_lan_di_muon=tong_so_lan_di_muon,
        tong_so_ngay_nghi=tong_so_ngay_nghi,
        ty_le_di_muon=ty_le_di_muon,
        trung_binh_ngay_cong=trung_binh_ngay_cong,
    )

    # 6. Phân trang kết quả
    total_items = len(all_items)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = all_items[start_idx:end_idx]

    pagination = AttendancePagination(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )

    return {
        "status_code": 200,
        "message": "Lấy báo cáo chấm công thành công",
        "data": {
            "summary": summary,
            "items": paginated_items,
            "pagination": pagination,
        }
    }


# ==============================================================
# API ĐIỂM DANH / CHẤM CÔNG (ATTENDANCE CHECK-IN & CHECK-OUT)
# ==============================================================

@app.post("/api/v1/attendance/check-in", status_code=201, response_model=CheckInResponse)
def attendance_check_in(req: CheckInRequest, db: Session = Depends(get_db)):
    """
    Endpoint tiếp nhận yêu cầu Check-in của thực tập sinh:
    - Kiểm tra hồ sơ thực tập sinh tồn tại (404 Not Found nếu không tìm thấy).
    - Xác định ngày và giờ check-in (lấy thời gian truyền lên hoặc thời gian hệ thống hiện tại).
    - Kiểm tra xem hồ sơ đã check-in trong ngày hôm đó chưa (400 Bad Request nếu đã check-in).
    - Tự động xác định trạng thái:
        + Nếu giờ vào <= 08:30:00 -> "DungGio"
        + Nếu giờ vào > 08:30:00 -> "DiMuon"
    - Lưu bản ghi vào bảng cham_cong.
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == req.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {req.ma_ho_so}"
        )

    # 2. Xác định thời điểm check-in
    now_dt = req.thoi_gian_checkin if req.thoi_gian_checkin is not None else datetime.now()
    target_date = now_dt.date()
    target_time = now_dt.time()

    # 3. Kiểm tra xem ngày này hồ sơ đã check-in chưa
    existing_attendance = db.query(ChamCong).filter(
        ChamCong.ma_ho_so == req.ma_ho_so,
        ChamCong.ngay_cham_cong == target_date
    ).first()
    if existing_attendance:
        raise HTTPException(
            status_code=400,
            detail=f"Thực tập sinh ID {req.ma_ho_so} đã thực hiện check-in vào ngày {target_date}"
        )

    # 4. Xác định trạng thái vào làm (mốc chuẩn 08:30:00)
    gio_chuan = time(8, 30, 0)
    trang_thai = "DiMuon" if target_time > gio_chuan else "DungGio"

    # 5. Khởi tạo bản ghi chấm công mới
    new_record = ChamCong(
        ma_ho_so=req.ma_ho_so,
        ngay_cham_cong=target_date,
        thoi_gian_checkin=now_dt,
        thoi_gian_checkout=None,
        gio_check_in=target_time,
        gio_check_out=None,
        trang_thai=trang_thai,
        phuong_thuc=req.phuong_thuc or "Web",
        ghi_chu=req.ghi_chu
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "status_code": 201,
        "message": "Check-in thành công",
        "data": new_record.to_dict()
    }


@app.post("/api/v1/attendance/check-out", status_code=200, response_model=CheckOutResponse)
def attendance_check_out(req: CheckOutRequest, db: Session = Depends(get_db)):
    """
    Endpoint tiếp nhận yêu cầu Check-out kết thúc ca làm của thực tập sinh:
    - Kiểm tra hồ sơ thực tập sinh tồn tại (404 Not Found nếu không tìm thấy).
    - Xác định ngày và giờ check-out.
    - Tìm bản ghi chấm công trong ngày của hồ sơ:
        + Nếu chưa có bản ghi check-in -> báo lỗi 400 Bad Request ("Chưa thực hiện check-in trong ngày hôm nay, không thể check-out").
        + Nếu đã check-out rồi -> báo lỗi 400 Bad Request ("Đã thực hiện check-out trong ngày hôm nay rồi").
        + Nếu thời gian check-out nhỏ hơn thời gian check-in -> báo lỗi 400 Bad Request.
    - Cập nhật thời gian check-out và lưu CSDL.
    """
    # 1. Kiểm tra hồ sơ thực tập sinh tồn tại không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == req.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {req.ma_ho_so}"
        )

    # 2. Xác định thời điểm check-out
    now_dt = req.thoi_gian_checkout if req.thoi_gian_checkout is not None else datetime.now()
    target_date = now_dt.date()
    target_time = now_dt.time()

    # 3. Tìm bản ghi chấm công trong ngày của hồ sơ
    attendance = db.query(ChamCong).filter(
        ChamCong.ma_ho_so == req.ma_ho_so,
        ChamCong.ngay_cham_cong == target_date
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=400,
            detail=f"Thực tập sinh ID {req.ma_ho_so} chưa thực hiện check-in vào ngày {target_date}, không thể check-out"
        )

    # 4. Kiểm tra xem đã check-out chưa
    if attendance.thoi_gian_checkout is not None or attendance.gio_check_out is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Thực tập sinh ID {req.ma_ho_so} đã hoàn thành check-out vào ngày {target_date}"
        )

    # 5. Kiểm tra tính hợp lệ của thời gian check-out so với check-in
    if attendance.thoi_gian_checkin and now_dt < attendance.thoi_gian_checkin:
        raise HTTPException(
            status_code=400,
            detail="Thời gian check-out không thể trước thời gian check-in"
        )
    elif attendance.gio_check_in and target_time < attendance.gio_check_in:
        raise HTTPException(
            status_code=400,
            detail="Giờ check-out không thể trước giờ check-in"
        )

    # 6. Cập nhật bản ghi chấm công
    attendance.thoi_gian_checkout = now_dt
    attendance.gio_check_out = target_time
    if req.ghi_chu:
        if attendance.ghi_chu:
            attendance.ghi_chu = f"{attendance.ghi_chu}; {req.ghi_chu}"
        else:
            attendance.ghi_chu = req.ghi_chu

    # Cập nhật trạng thái nếu về sớm (trước 17:00:00) hoặc giữ nguyên/hoàn thành
    gio_tan_ca = time(17, 0, 0)
    if target_time < gio_tan_ca and attendance.trang_thai == "DungGio":
        attendance.trang_thai = "VeSom"

    db.commit()
    db.refresh(attendance)

    return {
        "status_code": 200,
        "message": "Check-out thành công",
        "data": attendance.to_dict()
    }


@app.get("/api/v1/attendance/records")
def get_attendance_records(
    ma_ho_so: Optional[int] = Query(None, description="Lọc theo mã hồ sơ"),
    ngay: Optional[str] = Query(None, description="Lọc theo ngày cụ thể (YYYY-MM-DD)"),
    thang: Optional[int] = Query(None, ge=1, le=12, description="Lọc theo tháng (1 - 12)"),
    nam: Optional[int] = Query(None, ge=2000, description="Lọc theo năm"),
    ma_chuong_trinh: Optional[int] = Query(None, description="Lọc theo khóa thực tập"),
    chuyen_nganh: Optional[str] = Query(None, description="Lọc theo lớp / chuyên ngành"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(50, ge=1, le=200, description="Số lượng bản ghi mỗi trang"),
    db: Session = Depends(get_db)
):
    query = (
        db.query(ChamCong)
        .join(HoSoThucTap, ChamCong.ma_ho_so == HoSoThucTap.ma_ho_so)
        .join(NguoiDung, HoSoThucTap.ma_nguoi_dung == NguoiDung.ma_nguoi_dung)
    )

    if ma_ho_so:
        query = query.filter(ChamCong.ma_ho_so == ma_ho_so)
    if ma_chuong_trinh:
        query = query.filter(HoSoThucTap.ma_chuong_trinh == ma_chuong_trinh)
    if chuyen_nganh and chuyen_nganh != "tat-ca":
        query = query.filter(HoSoThucTap.chuyen_nganh == chuyen_nganh)

    target_year = nam if nam else datetime.now().year
    if ngay:
        try:
            d_filter = datetime.strptime(ngay, "%Y-%m-%d").date()
            query = query.filter(ChamCong.ngay_cham_cong == d_filter)
        except Exception:
            pass
    elif thang:
        start_d = date(target_year, thang, 1)
        end_d = date(target_year + 1, 1, 1) if thang == 12 else date(target_year, thang + 1, 1)
        query = query.filter(ChamCong.ngay_cham_cong >= start_d, ChamCong.ngay_cham_cong < end_d)
    elif nam:
        start_d = date(target_year, 1, 1)
        end_d = date(target_year + 1, 1, 1)
        query = query.filter(ChamCong.ngay_cham_cong >= start_d, ChamCong.ngay_cham_cong < end_d)

    if trang_thai and trang_thai not in ["tat-ca", "VangMat"]:
        query = query.filter(ChamCong.trang_thai == trang_thai)

    query = query.order_by(ChamCong.ngay_cham_cong.desc(), ChamCong.gio_check_in.desc())
    records = query.all()

    items = []
    dung_gio_count = 0
    di_muon_count = 0
    ve_som_count = 0

    for cc in records:
        hs = cc.ho_so
        user = hs.thuc_tap_sinh if hs else None

        gio_float = 0.0
        if cc.gio_check_in and cc.gio_check_out:
            t1 = datetime.combine(cc.ngay_cham_cong, cc.gio_check_in)
            t2 = datetime.combine(cc.ngay_cham_cong, cc.gio_check_out)
            diff_hours = (t2 - t1).total_seconds() / 3600.0
            gio_float = round(max(0.0, diff_hours), 1)
        elif cc.gio_check_in:
            gio_float = 8.5

        st = cc.trang_thai or "DungGio"
        if st == "DungGio":
            dung_gio_count += 1
        elif st == "DiMuon":
            di_muon_count += 1
        elif st == "VeSom":
            ve_som_count += 1

        pb_name = "Trung tâm Phát triển Phần mềm ICTU"
        if hs and hs.chuong_trinh and hs.chuong_trinh.phong_ban:
            pb_name = hs.chuong_trinh.phong_ban.ten_phong_ban
        elif user and user.phong_ban:
            pb_name = user.phong_ban.ten_phong_ban

        student_code = f"DTC20510{1000 + (hs.ma_ho_so if hs else 0)}"[-13:]

        items.append({
            "ma_cham_cong": cc.ma_cham_cong,
            "ma_ho_so": cc.ma_ho_so,
            "ma_sv": student_code,
            "ho_ten": user.ho_ten if user else f"Thực tập sinh #{cc.ma_ho_so}",
            "email": user.email if user else "",
            "phong_ban": pb_name,
            "chuyen_nganh": hs.chuyen_nganh if hs else "Công nghệ thông tin",
            "ngay": cc.ngay_cham_cong.strftime("%d/%m/%Y") if cc.ngay_cham_cong else "",
            "ngay_iso": cc.ngay_cham_cong.isoformat() if cc.ngay_cham_cong else "",
            "vao": cc.gio_check_in.strftime("%H:%M") if cc.gio_check_in else "--:--",
            "ra": cc.gio_check_out.strftime("%H:%M") if cc.gio_check_out else "--:--",
            "gio": gio_float,
            "trang_thai": st,
            "phuong_thuc": cc.phuong_thuc or "Web",
            "ghi_chu": cc.ghi_chu or ("Đúng giờ ca làm việc" if st == "DungGio" else ("Đi muộn" if st == "DiMuon" else "Về sớm")),
        })

    vang_count = 0
    if not trang_thai or trang_thai in ["tat-ca", "VangMat"]:
        dnp_query = (
            db.query(DonNghiPhep)
            .join(HoSoThucTap, DonNghiPhep.ma_ho_so == HoSoThucTap.ma_ho_so)
            .join(NguoiDung, HoSoThucTap.ma_nguoi_dung == NguoiDung.ma_nguoi_dung)
            .filter(DonNghiPhep.trang_thai == "DaDuyet")
        )
        if ma_ho_so:
            dnp_query = dnp_query.filter(DonNghiPhep.ma_ho_so == ma_ho_so)
        if ma_chuong_trinh:
            dnp_query = dnp_query.filter(HoSoThucTap.ma_chuong_trinh == ma_chuong_trinh)
        if chuyen_nganh and chuyen_nganh != "tat-ca":
            dnp_query = dnp_query.filter(HoSoThucTap.chuyen_nganh == chuyen_nganh)

        if ngay:
            try:
                d_filter = datetime.strptime(ngay, "%Y-%m-%d").date()
                dnp_query = dnp_query.filter(DonNghiPhep.ngay_nghi == d_filter)
            except Exception:
                pass
        elif thang:
            start_d = date(target_year, thang, 1)
            end_d = date(target_year + 1, 1, 1) if thang == 12 else date(target_year, thang + 1, 1)
            dnp_query = dnp_query.filter(DonNghiPhep.ngay_nghi >= start_d, DonNghiPhep.ngay_nghi < end_d)
        elif nam:
            start_d = date(target_year, 1, 1)
            end_d = date(target_year + 1, 1, 1)
            dnp_query = dnp_query.filter(DonNghiPhep.ngay_nghi >= start_d, DonNghiPhep.ngay_nghi < end_d)

        leaves = dnp_query.order_by(DonNghiPhep.ngay_nghi.desc()).all()
        vang_count = len(leaves)
        for lv in leaves:
            hs = lv.ho_so
            user = hs.thuc_tap_sinh if hs else None
            pb_name = "Trung tâm Phát triển Phần mềm ICTU"
            if hs and hs.chuong_trinh and hs.chuong_trinh.phong_ban:
                pb_name = hs.chuong_trinh.phong_ban.ten_phong_ban
            elif user and user.phong_ban:
                pb_name = user.phong_ban.ten_phong_ban

            student_code = f"DTC20510{1000 + (hs.ma_ho_so if hs else 0)}"[-13:]
            items.append({
                "ma_cham_cong": None,
                "ma_ho_so": lv.ma_ho_so,
                "ma_sv": student_code,
                "ho_ten": user.ho_ten if user else f"Thực tập sinh #{lv.ma_ho_so}",
                "email": user.email if user else "",
                "phong_ban": pb_name,
                "chuyen_nganh": hs.chuyen_nganh if hs else "Công nghệ thông tin",
                "ngay": lv.ngay_nghi.strftime("%d/%m/%Y") if lv.ngay_nghi else "",
                "ngay_iso": lv.ngay_nghi.isoformat() if lv.ngay_nghi else "",
                "vao": "--:--",
                "ra": "--:--",
                "gio": 0.0,
                "trang_thai": "VangMat",
                "phuong_thuc": "Đơn nghỉ phép",
                "ghi_chu": f"Nghỉ phép có lý do: {lv.ly_do}",
            })

    items.sort(key=lambda x: x.get("ngay_iso", ""), reverse=True)
    total_count = len(items)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = items[start_idx:end_idx]

    return {
        "status_code": 200,
        "message": "Lấy danh sách bản ghi chấm công thành công",
        "data": {
            "summary": {
                "tong": total_count,
                "dung_gio": dung_gio_count,
                "di_muon": di_muon_count,
                "ve_som": ve_som_count,
                "vang": vang_count,
            },
            "items": paginated_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size if total_count > 0 else 0,
            },
        },
    }


@app.get("/api/v1/attendance/shifts", status_code=200)
def get_attendance_shifts(ngay: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Lấy danh mục ca làm việc (Shift / Schedule / Mentoring Session) phục vụ việc Mentor chọn ca điểm danh.
    Hỗ trợ lọc theo ngày cụ thể nếu có truyền query param `ngay=YYYY-MM-DD`.
    """
    query = db.query(CaLamViec).filter(CaLamViec.trang_thai == "HoatDong")
    if ngay:
        try:
            d_filter = datetime.strptime(ngay, "%Y-%m-%d").date()
            # Lấy ca có ngày diễn ra đúng bằng d_filter HOẶC ca lặp lại không gán ngày cố định
            query = query.filter(
                (CaLamViec.ngay_dien_ra == d_filter) | (CaLamViec.ngay_dien_ra.is_(None))
            )
        except Exception:
            pass

    shifts = query.order_by(CaLamViec.gio_bat_dau.asc()).all()
    return {
        "status_code": 200,
        "message": "Lấy danh mục ca làm việc thành công",
        "data": [s.to_dict() for s in shifts]
    }


@app.post("/api/v1/attendance/shifts", status_code=201, response_model=ShiftCreateResponse)
def create_attendance_shift(req: ShiftCreateRequest, db: Session = Depends(get_db)):
    """
    Endpoint tạo mới ca làm việc / buổi gặp mặt (Mentoring session linh hoạt):
    - Hỗ trợ lưu ngày diễn ra cụ thể, lớp/chuyên ngành tham gia, khóa thực tập.
    - Kiểm tra tên ca không trùng lặp trong cùng ngày / hệ thống (HTTP 409 Conflict).
    - Validate giờ kết thúc > giờ bắt đầu (xử lý qua Pydantic schema).
    - Lưu bản ghi vào bảng ca_lam_viec trong cơ sở dữ liệu.
    """
    d_dien_ra = None
    if req.ngay_dien_ra:
        try:
            d_dien_ra = datetime.strptime(req.ngay_dien_ra[:10], "%Y-%m-%d").date()
        except Exception:
            pass

    existing_query = db.query(CaLamViec).filter(
        CaLamViec.ten_ca == req.ten_ca,
        CaLamViec.trang_thai == "HoatDong"
    )
    if d_dien_ra:
        existing_query = existing_query.filter(CaLamViec.ngay_dien_ra == d_dien_ra)

    existing = existing_query.first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Ca làm việc hoặc buổi gặp mang tên '{req.ten_ca}' đã tồn tại trong ngày đã chọn."
        )

    t_start = datetime.strptime(req.gio_bat_dau[:5], "%H:%M").time()
    t_end = datetime.strptime(req.gio_ket_thuc[:5], "%H:%M").time()

    new_shift = CaLamViec(
        ten_ca=req.ten_ca,
        gio_bat_dau=t_start,
        gio_ket_thuc=t_end,
        cac_ngay_trong_tuan=req.cac_ngay_trong_tuan or "Tất cả các ngày",
        ngay_dien_ra=d_dien_ra,
        chuyen_nganh=req.chuyen_nganh or None,
        ma_chuong_trinh=req.ma_chuong_trinh or None,
        ghi_chu=req.ghi_chu or "",
        trang_thai="HoatDong"
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    return {
        "status_code": 201,
        "message": "Tạo ca làm việc / buổi gặp thành công",
        "data": new_shift.to_dict()
    }


@app.post("/api/v1/attendance/roll-call", status_code=200, response_model=RollCallResponse)
def mentor_roll_call(req: RollCallRequest, db: Session = Depends(get_db)):
    """
    Endpoint tiếp nhận sổ điểm danh từ Mentor theo ngày, ca làm việc, khóa và lớp:
    - Chặn điểm danh trước cho ngày trong tương lai (Business Rule Validation).
    - Mentor chọn ngày, ca làm việc, khóa và lớp sinh viên.
    - Duyệt qua từng sinh viên trong danh sách:
      + Tạo mới hoặc cập nhật bản ghi trong bảng ChamCong với phuong_thuc="Mentor".
      + Đảm bảo sinh viên có đơn nghỉ phép đã duyệt được giữ trạng thái vắng/nghỉ phép.
      + Tự động tính toán giờ vào/giờ ra theo ca làm việc nếu client không truyền.
    """
    if req.ngay_cham_cong > datetime.now().date():
        raise HTTPException(
            status_code=400,
            detail=f"Không thể điểm danh trước cho ngày trong tương lai ({req.ngay_cham_cong.strftime('%d/%m/%Y')}). Chỉ có thể điểm danh khi đến ngày diễn ra ca họp."
        )

    if not req.records:
        raise HTTPException(status_code=400, detail="Danh sách điểm danh không được để trống")

    default_in = time(8, 0, 0)
    default_out = time(17, 30, 0)

    # Ưu tiên tìm đúng ca làm việc trong cơ sở dữ liệu
    shift_record = db.query(CaLamViec).filter(CaLamViec.ten_ca == req.ca_lam_viec).first()
    if shift_record:
        default_in = shift_record.gio_bat_dau
        default_out = shift_record.gio_ket_thuc
    else:
        ca_str = (req.ca_lam_viec or "").lower()
        if "sáng" in ca_str:
            default_in = time(8, 0, 0)
            default_out = time(12, 0, 0)
        elif "chiều" in ca_str:
            default_in = time(13, 30, 0)
            default_out = time(17, 30, 0)

    saved_items = []
    for item in req.records:
        ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == item.ma_ho_so).first()
        if not ho_so:
            continue

        t_in = default_in
        t_out = default_out
        if item.gio_check_in:
            try:
                parts = item.gio_check_in.split(":")
                t_in = time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
            except Exception:
                pass
        if item.gio_check_out:
            try:
                parts = item.gio_check_out.split(":")
                t_out = time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
            except Exception:
                pass

        if item.trang_thai == "VangMat":
            t_in = None
            t_out = None

        existing = db.query(ChamCong).filter(
            ChamCong.ma_ho_so == item.ma_ho_so,
            ChamCong.ngay_cham_cong == req.ngay_cham_cong
        ).first()

        note_prefix = f"[{req.ca_lam_viec}] " if req.ca_lam_viec else ""
        full_note = f"{note_prefix}{item.ghi_chu or ''}".strip()

        dt_in = datetime.combine(req.ngay_cham_cong, t_in) if t_in else None
        dt_out = datetime.combine(req.ngay_cham_cong, t_out) if t_out else None

        if existing:
            existing.trang_thai = item.trang_thai
            existing.gio_check_in = t_in
            existing.gio_check_out = t_out
            existing.thoi_gian_checkin = dt_in
            existing.thoi_gian_checkout = dt_out
            existing.phuong_thuc = "Mentor"
            if full_note:
                existing.ghi_chu = full_note
            saved_items.append(existing.to_dict())
        else:
            new_record = ChamCong(
                ma_ho_so=item.ma_ho_so,
                ngay_cham_cong=req.ngay_cham_cong,
                thoi_gian_checkin=dt_in,
                thoi_gian_checkout=dt_out,
                gio_check_in=t_in,
                gio_check_out=t_out,
                trang_thai=item.trang_thai,
                phuong_thuc="Mentor",
                ghi_chu=full_note
            )
            db.add(new_record)
            db.flush()
            saved_items.append(new_record.to_dict())

    db.commit()
    return {
        "status_code": 200,
        "message": f"Lưu thành công sổ điểm danh cho {len(saved_items)} thực tập sinh",
        "total_saved": len(saved_items),
        "data": saved_items
    }




# ==============================================================
# API QUẢN LÝ ĐƠN XIN NGHỈ PHÉP (LEAVE REQUESTS)
# ==============================================================

@app.post("/api/v1/leave-requests", status_code=201, response_model=LeaveRequestCreateResponse)
def create_leave_request(req: LeaveRequestCreate, db: Session = Depends(get_db)):
    """
    Endpoint tiếp nhận yêu cầu tạo đơn xin nghỉ phép của thực tập sinh:
    - Tiếp nhận: ma_ho_so, tu_ngay, den_ngay, ly_do, trang_thai (mặc định 'Chờ duyệt').
    - Validate mã hồ sơ thực tập sinh (404 Not Found nếu không tìm thấy).
    - Validate tu_ngay >= ngày hiện tại và den_ngay >= tu_ngay (xử lý qua schema validator).
    - Kiểm tra quỹ nghỉ phép tối đa 3 ngày của thực tập sinh.
    - Lưu bản ghi vào bảng don_xin_nghi.
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong hệ thống không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == req.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {req.ma_ho_so}"
        )

    # 2. Kiểm tra hạn mức quỹ phép tối đa 3 ngày
    so_ngay_xin = (req.den_ngay - req.tu_ngay).days + 1
    if so_ngay_xin > 3:
        raise HTTPException(
            status_code=400,
            detail=f"Số ngày xin nghỉ ({so_ngay_xin} ngày) vượt quá hạn mức tối đa 3 ngày phép của toàn bộ kỳ thực tập."
        )

    # Chặn nộp trùng lặp khoảng thời gian đã xin trước đó (ngoại trừ đơn đã bị Từ chối)
    overlapping = db.query(DonXinNghi).filter(
        DonXinNghi.ma_ho_so == req.ma_ho_so,
        DonXinNghi.trang_thai.notin_(["Từ chối", "TuChoi"]),
        DonXinNghi.tu_ngay <= req.den_ngay,
        DonXinNghi.den_ngay >= req.tu_ngay
    ).first()
    if overlapping:
        raise HTTPException(
            status_code=409,
            detail=f"Bạn đã có đơn nghỉ phép (mã NP-{overlapping.ma_don:03d}, trạng thái: {overlapping.trang_thai}) trùng hoặc giao thoa với khoảng thời gian này ({overlapping.tu_ngay.strftime('%d/%m/%Y')} - {overlapping.den_ngay.strftime('%d/%m/%Y')})."
        )

    # Chỉ tính các đơn đã được duyệt chính thức vào số ngày đã trừ
    approved_leaves = db.query(DonXinNghi).filter(
        DonXinNghi.ma_ho_so == req.ma_ho_so,
        DonXinNghi.trang_thai.in_(["Đã duyệt", "DaDuyet"])
    ).all()

    so_ngay_da_duyet = sum((d.den_ngay - d.tu_ngay).days + 1 for d in approved_leaves)
    so_ngay_con_lai = max(0, 3 - so_ngay_da_duyet)

    if so_ngay_con_lai <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bạn đã sử dụng hết hạn mức 3 ngày nghỉ phép quy định của kỳ thực tập (đã duyệt 3/3 ngày). Không thể nộp thêm đơn mới."
        )

    if so_ngay_xin > so_ngay_con_lai:
        raise HTTPException(
            status_code=400,
            detail=f"Số ngày xin nghỉ ({so_ngay_xin} ngày) vượt quá hạn mức nghỉ phép còn lại của bạn ({so_ngay_con_lai} ngày còn lại trên tổng 3 ngày)."
        )

    # Kiểm tra tổng số ngày chờ duyệt để chặn nộp dồn dập vượt quá quỹ phép
    pending_leaves = db.query(DonXinNghi).filter(
        DonXinNghi.ma_ho_so == req.ma_ho_so,
        DonXinNghi.trang_thai.in_(["Chờ duyệt", "ChoDuyet"])
    ).all()
    so_ngay_cho_duyet = sum((d.den_ngay - d.tu_ngay).days + 1 for d in pending_leaves)
    if so_ngay_xin > (so_ngay_con_lai - so_ngay_cho_duyet):
        raise HTTPException(
            status_code=400,
            detail=f"Bạn hiện có {so_ngay_cho_duyet} ngày nghỉ đang chờ xét duyệt và {so_ngay_da_duyet} ngày đã duyệt (tổng {so_ngay_da_duyet + so_ngay_cho_duyet}/3 ngày). Bạn chỉ có thể nộp thêm tối đa {max(0, so_ngay_con_lai - so_ngay_cho_duyet)} ngày nghỉ nữa."
        )

    # 3. Khởi tạo bản ghi đơn xin nghỉ mới
    new_request = DonXinNghi(
        ma_ho_so=req.ma_ho_so,
        tu_ngay=req.tu_ngay,
        den_ngay=req.den_ngay,
        ly_do=req.ly_do,
        trang_thai=req.trang_thai or "Chờ duyệt"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "status_code": 201,
        "message": "Tạo đơn xin nghỉ thành công",
        "data": new_request.to_dict()
    }


@app.get("/api/v1/leave-requests")
def get_leave_requests(
    ma_ho_so: Optional[int] = Query(None, description="Lọc theo mã hồ sơ"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái đơn"),
    db: Session = Depends(get_db)
):
    query = db.query(DonXinNghi)
    if ma_ho_so:
        query = query.filter(DonXinNghi.ma_ho_so == ma_ho_so)
    if trang_thai and trang_thai != "tat-ca":
        query = query.filter(DonXinNghi.trang_thai == trang_thai)

    rows = query.order_by(DonXinNghi.ngay_tao.desc(), DonXinNghi.ma_don.desc()).all()

    data = []
    for r in rows:
        hs = r.ho_so
        user = hs.thuc_tap_sinh if hs else None

        # Tính tổng số ngày đã duyệt của sinh viên này
        approved_leaves = [
            x for x in (hs.danh_sach_don_xin_nghi if hs else [])
            if x.trang_thai in ["Đã duyệt", "DaDuyet"]
        ]
        so_ngay_da_duyet = sum((x.den_ngay - x.tu_ngay).days + 1 for x in approved_leaves)

        item_dict = r.to_dict()
        item_dict["ho_ten"] = user.ho_ten if user else f"Thực tập sinh #{r.ma_ho_so}"
        item_dict["email"] = user.email if user else ""
        item_dict["ma_sv"] = f"DTC20510{1000 + r.ma_ho_so}"[-13:]
        item_dict["chuyen_nganh"] = hs.chuyen_nganh if hs else "Công nghệ thông tin"
        item_dict["so_ngay_da_duyet"] = so_ngay_da_duyet
        item_dict["so_ngay_con_lai"] = max(0, 3 - so_ngay_da_duyet)
        data.append(item_dict)

    return {
        "status_code": 200,
        "message": "Lấy danh sách đơn xin nghỉ thành công",
        "data": data
    }


@app.patch("/api/v1/leave-requests/{id}/status", status_code=200, response_model=LeaveStatusUpdateResponse)
def update_leave_request_status(
    id: int,
    req: LeaveStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint phê duyệt hoặc từ chối đơn xin nghỉ phép của Mentor/HR:
    - Nếu duyệt: kiểm tra không vượt quá hạn mức 3 ngày phép của sinh viên, đồng bộ vào danh sách nghỉ phép.
    - Nếu từ chối: không trừ ngày phép của sinh viên.
    """
    don = db.query(DonXinNghi).filter(DonXinNghi.ma_don == id).first()
    if not don:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn xin nghỉ phép với ID: {id}")

    if req.trang_thai in ["Đã duyệt", "DaDuyet"]:
        # Kiểm tra quỹ phép nếu duyệt đơn này
        other_approved = db.query(DonXinNghi).filter(
            DonXinNghi.ma_ho_so == don.ma_ho_so,
            DonXinNghi.ma_don != don.ma_don,
            DonXinNghi.trang_thai.in_(["Đã duyệt", "DaDuyet"])
        ).all()

        so_ngay_da_duyet = sum((d.den_ngay - d.tu_ngay).days + 1 for d in other_approved)
        so_ngay_don_nay = (don.den_ngay - don.tu_ngay).days + 1

        if so_ngay_da_duyet + so_ngay_don_nay > 3:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể duyệt: Đơn này ({so_ngay_don_nay} ngày) khiến tổng số ngày nghỉ vượt quá hạn mức tối đa 3 ngày (sinh viên đã được duyệt {so_ngay_da_duyet} ngày trước đó)."
            )

        don.trang_thai = "Đã duyệt"

        # Đồng bộ sang bảng don_nghi_phep theo từng ngày để liên thông với sổ điểm danh
        curr = don.tu_ngay
        while curr <= don.den_ngay:
            dnp = db.query(DonNghiPhep).filter(
                DonNghiPhep.ma_ho_so == don.ma_ho_so,
                DonNghiPhep.ngay_nghi == curr
            ).first()
            if not dnp:
                db.add(DonNghiPhep(
                    ma_ho_so=don.ma_ho_so,
                    ngay_nghi=curr,
                    ly_do=don.ly_do,
                    trang_thai="DaDuyet"
                ))
            else:
                dnp.trang_thai = "DaDuyet"
            curr += timedelta(days=1)

        # Tự động cập nhật các đơn chờ duyệt khác của sinh viên nếu không còn đủ quỹ phép
        so_ngay_sau_duyet = so_ngay_da_duyet + so_ngay_don_nay
        so_ngay_con_lai_moi = max(0, 3 - so_ngay_sau_duyet)

        other_pending = db.query(DonXinNghi).filter(
            DonXinNghi.ma_ho_so == don.ma_ho_so,
            DonXinNghi.ma_don != don.ma_don,
            DonXinNghi.trang_thai.in_(["Chờ duyệt", "ChoDuyet"])
        ).all()

        for op in other_pending:
            op_so_ngay = (op.den_ngay - op.tu_ngay).days + 1
            if so_ngay_con_lai_moi == 0:
                op.trang_thai = "Từ chối"
                op.ly_do = f"{op.ly_do} [Hệ thống tự động từ chối: Sinh viên đã dùng hết 3/3 ngày phép]"
            elif op_so_ngay > so_ngay_con_lai_moi:
                op.trang_thai = "Từ chối"
                op.ly_do = f"{op.ly_do} [Hệ thống tự động từ chối: Số ngày xin ({op_so_ngay} ngày) vượt quá quỹ còn lại ({so_ngay_con_lai_moi} ngày)]"

    elif req.trang_thai in ["Từ chối", "TuChoi"]:
        don.trang_thai = "Từ chối"
        curr = don.tu_ngay
        while curr <= don.den_ngay:
            dnp = db.query(DonNghiPhep).filter(
                DonNghiPhep.ma_ho_so == don.ma_ho_so,
                DonNghiPhep.ngay_nghi == curr
            ).first()
            if dnp:
                dnp.trang_thai = "TuChoi"
            curr += timedelta(days=1)
    else:
        don.trang_thai = req.trang_thai

    db.commit()
    db.refresh(don)

    return {
        "status_code": 200,
        "message": f"Đơn xin nghỉ phép đã được chuyển sang trạng thái: {don.trang_thai}",
        "data": don.to_dict()
    }




# ==============================================================
# API QUẢN LÝ ĐÁNH GIÁ THỰC TẬP (EVALUATIONS)
# ==============================================================

# api post create evaluation
@app.post("/api/v1/evaluations", status_code=201, response_model=EvaluationCreateResponse)
def create_evaluation(eval_data: EvaluationCreate, db: Session = Depends(get_db)):
    """
    Tạo mới đánh giá thực tập sinh (Giữa kỳ hoặc Cuối kỳ):
    - Lưu mã hồ sơ (ma_ho_so), mã người đánh giá (ma_nguoi_danh_gia).
    - Lưu loại đánh giá (loai_danh_gia: GiuaKy / CuoiKy).
    - Lưu điểm kỹ năng chuyên môn (diem_ky_nang) và điểm thái độ kỷ luật (diem_thai_do) từ 0.0 đến 10.0.
    - Lưu nhận xét (nhan_xet) và đề xuất tuyển dụng (de_xuat_tuyen_dung).
    - Tự động tính điểm trung bình (diem_trung_binh) và xếp loại rèn luyện (xep_loai).
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong hệ thống không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == eval_data.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {eval_data.ma_ho_so}"
        )

    # 2. Kiểm tra người đánh giá có tồn tại trong hệ thống không
    nguoi_danh_gia = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == eval_data.ma_nguoi_danh_gia).first()
    if not nguoi_danh_gia:
        raise HTTPException(
            status_code=400,
            detail=f"Người đánh giá với mã ID {eval_data.ma_nguoi_danh_gia} không tồn tại trong hệ thống"
        )

    # 3. Kiểm tra trùng lặp đợt đánh giá: một hồ sơ chỉ có tối đa 1 đánh giá giữa kỳ và 1 đánh giá cuối kỳ
    existing_eval = db.query(DanhGia).filter(
        DanhGia.ma_ho_so == eval_data.ma_ho_so,
        DanhGia.loai_danh_gia == eval_data.loai_danh_gia
    ).first()
    if existing_eval:
        raise HTTPException(
            status_code=400,
            detail=f"Hồ sơ ID {eval_data.ma_ho_so} đã có đánh giá {eval_data.loai_danh_gia}"
        )

    # 4. Khởi tạo bản ghi đánh giá mới
    new_eval = DanhGia(
        ma_ho_so=eval_data.ma_ho_so,
        ma_nguoi_danh_gia=eval_data.ma_nguoi_danh_gia,
        loai_danh_gia=eval_data.loai_danh_gia,
        diem_ky_nang=eval_data.diem_ky_nang,
        diem_thai_do=eval_data.diem_thai_do,
        nhan_xet_chi_tiet=eval_data.get_nhan_xet(),
        de_xuat_tuyen_chinh_thuc=eval_data.get_de_xuat()
    )

    # 5. Lưu vào CSDL
    db.add(new_eval)
    db.commit()
    db.refresh(new_eval)

    # 6. Đảm bảo tên người đánh giá được nạp đầy đủ trong response
    result_dict = new_eval.to_dict()
    if result_dict.get("ten_nguoi_danh_gia") is None and nguoi_danh_gia:
        result_dict["ten_nguoi_danh_gia"] = nguoi_danh_gia.ho_ten

    # 7. Trả về phản hồi thành công (HTTP 201 Created)
    return {
        "status_code": 201,
        "message": "Tạo đánh giá thực tập sinh thành công",
        "data": result_dict
    }


# ==============================================================
# API TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ (EVALUATIONS SUMMARY)
# ==============================================================

@app.get("/api/v1/evaluations/summary")
def get_evaluations_summary(
    ma_truong: Optional[int] = Query(None, description="Lọc theo mã trường đại học"),
    loai_danh_gia: Optional[str] = Query(None, description="Lọc theo đợt đánh giá (GiuaKy, CuoiKy)"),
    trang_thai_thuc_tap: Optional[str] = Query(None, description="Lọc theo trạng thái thực tập (DangThucTap, HoanThanh, ThoiHoc)"),
    de_xuat_tuyen_chinh_thuc: Optional[bool] = Query(None, description="Lọc theo đề xuất tuyển dụng (true/false)"),
    tu_khoa: Optional[str] = Query(None, description="Tìm kiếm theo tên sinh viên, email, trường hoặc chuyên ngành"),
    format: Optional[str] = Query("json", description="Định dạng dữ liệu trả về: json (mặc định), excel, pdf"),
    page: int = Query(1, ge=1, description="Số trang khi xem dạng json"),
    page_size: int = Query(50, ge=1, le=100, description="Số bản ghi mỗi trang khi xem dạng json"),
    db: Session = Depends(get_db),
):
    """
    Endpoint tổng hợp dữ liệu kết quả đánh giá thực tập sinh:
    - Tổng hợp thông tin từ 3 bảng chính: ho_so_thuc_tap, danh_gia, truong_dai_hoc (kèm nguoi_dung).
    - Hỗ trợ các bộ lọc linh hoạt: mã trường, đợt đánh giá, trạng thái thực tập, đề xuất tuyển dụng, tìm kiếm từ khóa.
    - Cung cấp các chỉ số KPI thống kê: Điểm kỹ năng TB, điểm thái độ TB, điểm tổng kết TB, tỷ lệ đề xuất tuyển dụng, phân bổ xếp loại rèn luyện và thống kê theo từng trường đại học.
    - Hỗ trợ xuất dữ liệu ra 3 định dạng: JSON API, Excel (.xlsx), hoặc PDF (.pdf).
    """
    # 1. Kiểm tra tham số format
    fmt = format.strip().lower() if format else "json"
    if fmt not in ["json", "excel", "xlsx", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Định dạng xuất file không được hỗ trợ. Chỉ chấp nhận: json, excel, pdf"
        )

    # 2. Xây dựng câu truy vấn kết hợp các bảng dữ liệu
    query = (
        db.query(DanhGia, HoSoThucTap, TruongDaiHoc, NguoiDung)
        .join(HoSoThucTap, DanhGia.ma_ho_so == HoSoThucTap.ma_ho_so)
        .outerjoin(TruongDaiHoc, HoSoThucTap.ma_truong == TruongDaiHoc.ma_truong)
        .outerjoin(NguoiDung, HoSoThucTap.ma_nguoi_dung == NguoiDung.ma_nguoi_dung)
    )

    # 3. Áp dụng các bộ lọc tìm kiếm
    if ma_truong is not None:
        query = query.filter(HoSoThucTap.ma_truong == ma_truong)

    if loai_danh_gia and loai_danh_gia.strip():
        query = query.filter(DanhGia.loai_danh_gia.ilike(f"%{loai_danh_gia.strip()}%"))

    if trang_thai_thuc_tap and trang_thai_thuc_tap.strip():
        query = query.filter(HoSoThucTap.trang_thai_thuc_tap.ilike(f"%{trang_thai_thuc_tap.strip()}%"))

    if de_xuat_tuyen_chinh_thuc is not None:
        query = query.filter(DanhGia.de_xuat_tuyen_chinh_thuc == de_xuat_tuyen_chinh_thuc)

    if tu_khoa and tu_khoa.strip():
        kw = f"%{tu_khoa.strip()}%"
        query = query.filter(
            or_(
                NguoiDung.ho_ten.ilike(kw),
                NguoiDung.email.ilike(kw),
                HoSoThucTap.chuyen_nganh.ilike(kw),
                TruongDaiHoc.ten_truong.ilike(kw),
            )
        )

    # 4. Thực thi truy vấn lấy toàn bộ kết quả phù hợp sắp xếp theo mã đánh giá giảm dần
    records = query.order_by(DanhGia.ma_danh_gia.desc()).all()

    # 5. Xây dựng danh sách chi tiết các đánh giá
    all_items = []
    unique_ho_so_ids = set()
    total_evaluations = len(records)
    total_ky_nang = 0.0
    total_thai_do = 0.0
    total_tong_ket = 0.0
    so_luong_de_xuat = 0

    phan_bo_xep_loai = {
        "XuatSac": 0,
        "Gioi": 0,
        "Kha": 0,
        "TrungBinh": 0,
        "Yeu": 0
    }

    # Thống kê điểm và số lượng theo trường
    truong_stats_map = {} # ma_truong: {"ten_truong": str, "scores": []}

    for dg, hs, tr, nd in records:
        unique_ho_so_ids.add(hs.ma_ho_so)
        total_ky_nang += dg.diem_ky_nang
        total_thai_do += dg.diem_thai_do
        dtb = dg.diem_trung_binh
        total_tong_ket += dtb

        if dg.de_xuat_tuyen_chinh_thuc:
            so_luong_de_xuat += 1

        xl = dg.xep_loai
        if xl in phan_bo_xep_loai:
            phan_bo_xep_loai[xl] += 1

        t_id = tr.ma_truong if tr else None
        t_name = tr.ten_truong if tr else "Chưa xác định"
        if t_id not in truong_stats_map:
            truong_stats_map[t_id] = {
                "ma_truong": t_id,
                "ten_truong": t_name,
                "scores": []
            }
        truong_stats_map[t_id]["scores"].append(dtb)

        # Lấy tên người đánh giá
        nguoi_dg_name = dg.nguoi_danh_gia.ho_ten if dg.nguoi_danh_gia else None

        item_dict = {
            "ma_danh_gia": dg.ma_danh_gia,
            "ma_ho_so": hs.ma_ho_so,
            "ho_ten": nd.ho_ten if nd else None,
            "email": nd.email if nd else None,
            "so_dien_thoai": nd.so_dien_thoai if nd else None,
            "chuyen_nganh": hs.chuyen_nganh,
            "ma_truong": tr.ma_truong if tr else None,
            "ten_truong": tr.ten_truong if tr else None,
            "trang_thai_thuc_tap": hs.trang_thai_thuc_tap,
            "loai_danh_gia": dg.loai_danh_gia,
            "diem_ky_nang": dg.diem_ky_nang,
            "diem_thai_do": dg.diem_thai_do,
            "diem_trung_binh": dtb,
            "xep_loai": xl,
            "nhan_xet_chi_tiet": dg.nhan_xet_chi_tiet,
            "de_xuat_tuyen_chinh_thuc": dg.de_xuat_tuyen_chinh_thuc,
            "nguoi_danh_gia": nguoi_dg_name,
        }
        all_items.append(item_dict)

    # 6. Tính toán các chỉ số thống kê KPI
    diem_ky_nang_tb = round(total_ky_nang / total_evaluations, 2) if total_evaluations else 0.0
    diem_thai_do_tb = round(total_thai_do / total_evaluations, 2) if total_evaluations else 0.0
    diem_tong_ket_tb = round(total_tong_ket / total_evaluations, 2) if total_evaluations else 0.0
    ty_le_de_xuat = round((so_luong_de_xuat / total_evaluations) * 100.0, 2) if total_evaluations else 0.0

    thong_ke_theo_truong = []
    for t_id, data in truong_stats_map.items():
        scs = data["scores"]
        avg_s = round(sum(scs) / len(scs), 2) if scs else 0.0
        thong_ke_theo_truong.append({
            "ma_truong": data["ma_truong"],
            "ten_truong": data["ten_truong"],
            "so_luong_danh_gia": len(scs),
            "diem_trung_binh": avg_s
        })
    thong_ke_theo_truong.sort(key=lambda x: x["so_luong_danh_gia"], reverse=True)

    summary_data = {
        "tong_so_ho_so": len(unique_ho_so_ids),
        "tong_so_danh_gia": total_evaluations,
        "diem_ky_nang_tb": diem_ky_nang_tb,
        "diem_thai_do_tb": diem_thai_do_tb,
        "diem_tong_ket_tb": diem_tong_ket_tb,
        "so_luong_de_xuat_tuyen_dung": so_luong_de_xuat,
        "ty_le_de_xuat_tuyen_dung": ty_le_de_xuat,
        "phan_bo_xep_loai": phan_bo_xep_loai,
        "thong_ke_theo_truong": thong_ke_theo_truong,
    }

    # 7. Xử lý xuất file theo format
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt in ["excel", "xlsx"]:
        excel_stream = export_evaluations_to_excel(summary_data, all_items)
        filename = f"Bao_cao_tong_hop_danh_gia_{timestamp_str}.xlsx"
        return StreamingResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

    if fmt == "pdf":
        pdf_stream = export_evaluations_to_pdf(summary_data, all_items)
        filename = f"Bao_cao_tong_hop_danh_gia_{timestamp_str}.pdf"
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

    # 8. Mặc định trả về JSON response kèm phân trang
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = all_items[start_idx:end_idx]
    total_pages = (total_evaluations + page_size - 1) // page_size if total_evaluations > 0 else 0

    return {
        "status_code": 200,
        "message": "Lấy dữ liệu tổng hợp đánh giá thành công",
        "data": {
            "summary": summary_data,
            "items": paginated_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_evaluations,
                "total_pages": total_pages,
            }
        }
    }


# ==============================================================
# API QUẢN LÝ NHIỆM VỤ THỰC TẬP (TASKS)
# ==============================================================

# api post create task
@app.post("/api/v1/tasks", status_code=201, response_model=TaskCreateResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo mới nhiệm vụ cho thực tập sinh (gắn theo mã hồ sơ thực tập).
    Lưu trữ:
    - ma_ho_so: Khóa ngoại trỏ về ho_so_thuc_tap
    - tieu_de: Tiêu đề nhiệm vụ
    - mo_ta: Mô tả chi tiết nhiệm vụ (tùy chọn)
    - han_hoan_thanh: Hạn hoàn thành công việc (YYYY-MM-DD)
    - tien_do_phantram: Mặc định là 0%
    - trang_thai: Mặc định là 'Chưa bắt đầu'
    """
    # 1. Kiểm tra hồ sơ thực tập có tồn tại trong CSDL hay không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == task_data.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập với mã: {task_data.ma_ho_so}"
        )

    # 2. Khởi tạo đối tượng NhiemVu mới
    new_task = NhiemVu(
        ma_ho_so=task_data.ma_ho_so,
        ten_nhiem_vu=task_data.tieu_de,
        mo_ta=task_data.mo_ta,
        han_hoan_thanh=task_data.han_hoan_thanh,
        tien_do_phantram=task_data.tien_do_phantram if task_data.tien_do_phantram is not None else 0,
        trang_thai=task_data.trang_thai or "Chưa bắt đầu"
    )

    # 3. Lưu vào CSDL
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 4. Trả về phản hồi thành công
    return {
        "status_code": 201,
        "message": "Tạo nhiệm vụ mới thành công",
        "data": new_task.to_dict()
    }


# api patch task progress
@app.patch("/api/v1/tasks/{id}/progress", status_code=200, response_model=TaskProgressResponse)
def update_task_progress(
    id: int,
    progress_data: TaskProgressUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật tiến độ hoàn thành của nhiệm vụ (tien_do_phantram từ 0 đến 100%).
    Tự động cập nhật trang_thai:
    - Nếu tien_do_phantram == 100: tự động chuyển sang "Hoàn thành"
    - Nếu 0 < tien_do_phantram < 100: chuyển sang "Đang thực hiện"
    - Nếu tien_do_phantram == 0: chuyển sang "Chưa bắt đầu"
    """
    # 1. Kiểm tra ID hợp lệ
    if id <= 0:
        raise HTTPException(status_code=422, detail="Mã nhiệm vụ không hợp lệ")

    # 2. Tìm nhiệm vụ trong CSDL
    task = db.query(NhiemVu).filter(NhiemVu.ma_nhiem_vu == id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhiệm vụ ID: {id}")

    # 3. Cập nhật tiến độ phần trăm
    task.tien_do_phantram = progress_data.tien_do_phantram

    # 4. Tự động chuyển đổi trạng thái tương ứng
    if progress_data.tien_do_phantram == 100:
        task.trang_thai = "Hoàn thành"
    elif progress_data.tien_do_phantram > 0:
        task.trang_thai = "Đang thực hiện"
    else:
        task.trang_thai = "Chưa bắt đầu"

    # 5. Lưu vào CSDL
    db.commit()
    db.refresh(task)

    # 6. Trả về phản hồi thành công
    return {
        "status_code": 200,
        "message": "Cập nhật tiến độ nhiệm vụ thành công",
        "data": task.to_dict()
    }


# ==============================================================
# API QUẢN LÝ CA LÀM VIỆC (SCHEDULES / WORK SHIFTS API)
# ==============================================================

@app.post("/api/v1/schedules", status_code=201, response_model=ScheduleCreateResponse)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo ca làm việc mới cho hệ thống.
    Lưu các thông tin: ten_ca, gio_bat_dau, gio_ket_thuc, cac_ngay_trong_tuan.
    Ràng buộc gio_ket_thuc > gio_bat_dau được tự động validate qua schema ScheduleCreate.
    """
    new_schedule = CaLamViec(
        ten_ca=schedule_data.ten_ca,
        gio_bat_dau=schedule_data.gio_bat_dau,
        gio_ket_thuc=schedule_data.gio_ket_thuc,
        cac_ngay_trong_tuan=schedule_data.cac_ngay_trong_tuan,
        ghi_chu=schedule_data.ghi_chu,
        trang_thai=schedule_data.trang_thai or "HoatDong",
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return {
        "status_code": 201,
        "message": "Tạo ca làm việc thành công",
        "data": new_schedule.to_dict()
    }


# ==============================================================
# API QUẢN LÝ NGƯỜI HƯỚNG DẪN (MENTOR API)
# ==============================================================

@app.post("/api/v1/mentors", status_code=201, response_model=MentorResponse)
def create_mentor(
    data: MentorCreate,
    db: Session = Depends(get_db)
):
    """
    Tiếp nhận thông tin người hướng dẫn, tạo tài khoản mới vào bảng nguoi_dung với vai_tro = 'Mentor'.
    """
    email_normalized = data.email.strip().lower()

    # Kiểm tra trùng email
    existing_email = db.query(NguoiDung).filter(NguoiDung.email == email_normalized).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng trong hệ thống")

    # Kiểm tra trùng số điện thoại
    phone_normalized = None
    if data.so_dien_thoai:
        phone_normalized = data.so_dien_thoai.strip()
        existing_phone = db.query(NguoiDung).filter(NguoiDung.so_dien_thoai == phone_normalized).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng trong hệ thống")

    # Kiểm tra phòng ban
    department = None
    if data.ma_phong_ban is not None:
        department = db.query(PhongBan).filter(PhongBan.ma_phong_ban == data.ma_phong_ban).first()
        if not department:
            raise HTTPException(status_code=400, detail="Mã phòng ban không tồn tại trong hệ thống")

    # Băm mật khẩu bằng bcrypt
    hashed_password = get_password_hash(data.mat_khau)

    new_mentor = NguoiDung(
        ho_ten=data.ho_ten.strip(),
        email=email_normalized,
        mat_khau_hash=hashed_password,
        so_dien_thoai=phone_normalized,
        ma_phong_ban=data.ma_phong_ban,
        vai_tro="Mentor",
        trang_thai="HoatDong"
    )

    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)

    return {
        "status_code": 201,
        "message": "Tạo tài khoản người hướng dẫn thành công",
        "data": {
            "ma_nguoi_dung": new_mentor.ma_nguoi_dung,
            "ho_ten": new_mentor.ho_ten,
            "email": new_mentor.email,
            "so_dien_thoai": new_mentor.so_dien_thoai,
            "ma_phong_ban": new_mentor.ma_phong_ban,
            "ten_phong_ban": department.ten_phong_ban if department else None,
            "vai_tro": new_mentor.vai_tro,
            "trang_thai": new_mentor.trang_thai
        }
    }


# ==============================================================
# API BÁO CÁO THỐNG KÊ SINH VIÊN THEO TRƯỜNG & CHUYÊN NGÀNH
# (REPORTS INTERNS BY FACULTY / UNIVERSITY & MAJOR)
# ==============================================================
@app.get("/api/v1/reports/interns-by-faculty", response_model=FacultyReportResponse)
def get_interns_by_faculty_report(
    ma_truong: Optional[int] = Query(None, ge=1, description="Lọc theo mã trường đại học (>= 1)"),
    ten_truong: Optional[str] = Query(None, description="Tìm kiếm theo tên trường đại học"),
    chuyen_nganh: Optional[str] = Query(None, description="Lọc hoặc tìm kiếm theo chuyên ngành đào tạo"),
    ma_chuong_trinh: Optional[int] = Query(None, ge=1, description="Lọc theo mã chương trình thực tập (>= 1)"),
    trang_thai_xet_duyet: Optional[str] = Query(None, description="Lọc theo trạng thái xét duyệt: ChoDuyet, DaDuyet, TuChoi"),
    trang_thai_thuc_tap: Optional[str] = Query(None, description="Lọc theo trạng thái thực tập: ChuaThucTap, DangThucTap, HoanThanh, ThoiHoc"),
    db: Session = Depends(get_db),
):
    """
    Endpoint thống kê tổng hợp số lượng sinh viên bằng cách gom nhóm hai chiều
    theo tên trường đại học (ten_truong) và chuyên ngành đào tạo (chuyen_nganh)
    từ các bảng truong_dai_hoc và ho_so_thuc_tap:
    - Bắt trọn vẹn ngoại lệ đầu vào và nghiệp vụ (400, 404, 422).
    - Gom nhóm hai chiều (Trường x Chuyên ngành).
    - Cung cấp chỉ số tổng quan KPI (summary), thống kê phân cấp theo trường,
      thống kê phân cấp theo chuyên ngành, và danh sách chi tiết hai chiều.
    """
    # 1. Kiểm tra mã trường nếu có truyền
    if ma_truong is not None:
        truong_db = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == ma_truong).first()
        if not truong_db:
            raise HTTPException(status_code=404, detail="Trường đại học không tồn tại trong hệ thống")

    # 2. Kiểm tra mã chương trình nếu có truyền
    if ma_chuong_trinh is not None:
        ct_db = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == ma_chuong_trinh).first()
        if not ct_db:
            raise HTTPException(status_code=404, detail="Chương trình thực tập không tồn tại trong hệ thống")

    # 3. Kiểm tra tính hợp lệ của trạng thái xét duyệt
    hop_le_xet_duyet = {"ChoDuyet", "DaDuyet", "TuChoi"}
    if trang_thai_xet_duyet is not None:
        val_xet_duyet = trang_thai_xet_duyet.strip()
        if val_xet_duyet not in hop_le_xet_duyet:
            raise HTTPException(
                status_code=400,
                detail=f"Trạng thái xét duyệt không hợp lệ. Chỉ chấp nhận một trong các giá trị: {', '.join(sorted(hop_le_xet_duyet))}"
            )

    # 4. Kiểm tra tính hợp lệ của trạng thái thực tập
    hop_le_thuc_tap = {"ChuaThucTap", "DangThucTap", "HoanThanh", "ThoiHoc"}
    if trang_thai_thuc_tap is not None:
        val_thuc_tap = trang_thai_thuc_tap.strip()
        if val_thuc_tap not in hop_le_thuc_tap:
            raise HTTPException(
                status_code=400,
                detail=f"Trạng thái thực tập không hợp lệ. Chỉ chấp nhận một trong các giá trị: {', '.join(sorted(hop_le_thuc_tap))}"
            )

    # 5. Xây dựng truy vấn gom nhóm hai chiều từ truong_dai_hoc và ho_so_thuc_tap
    query = (
        db.query(
            TruongDaiHoc.ma_truong,
            TruongDaiHoc.ten_truong,
            func.coalesce(HoSoThucTap.chuyen_nganh, "Chưa phân ngành").label("chuyen_nganh"),
            func.count(HoSoThucTap.ma_ho_so).label("so_luong")
        )
        .join(TruongDaiHoc, HoSoThucTap.ma_truong == TruongDaiHoc.ma_truong)
    )

    # Áp dụng các bộ lọc
    if ma_truong is not None:
        query = query.filter(HoSoThucTap.ma_truong == ma_truong)

    if ten_truong and ten_truong.strip():
        query = query.filter(TruongDaiHoc.ten_truong.ilike(f"%{ten_truong.strip()}%"))

    if chuyen_nganh and chuyen_nganh.strip():
        query = query.filter(HoSoThucTap.chuyen_nganh.ilike(f"%{chuyen_nganh.strip()}%"))

    if ma_chuong_trinh is not None:
        query = query.filter(HoSoThucTap.ma_chuong_trinh == ma_chuong_trinh)

    if trang_thai_xet_duyet is not None:
        query = query.filter(HoSoThucTap.trang_thai_xet_duyet == trang_thai_xet_duyet.strip())

    if trang_thai_thuc_tap is not None:
        query = query.filter(HoSoThucTap.trang_thai_thuc_tap == trang_thai_thuc_tap.strip())

    # Gom nhóm theo Trường và Chuyên ngành
    records = (
        query.group_by(
            TruongDaiHoc.ma_truong,
            TruongDaiHoc.ten_truong,
            func.coalesce(HoSoThucTap.chuyen_nganh, "Chưa phân ngành")
        )
        .order_by(
            TruongDaiHoc.ten_truong.asc(),
            func.count(HoSoThucTap.ma_ho_so).desc()
        )
        .all()
    )

    tong_sinh_vien = sum(r.so_luong for r in records)

    # 6. Xây dựng cấu trúc dữ liệu tổng hợp
    chi_tiet_items = []
    universities_map = {}
    majors_map = {}

    for r in records:
        m_truong = r.ma_truong
        t_truong = r.ten_truong
        c_nganh = r.chuyen_nganh if r.chuyen_nganh else "Chưa phân ngành"
        s_luong = r.so_luong
        ty_le = round((s_luong / tong_sinh_vien * 100), 2) if tong_sinh_vien > 0 else 0.0

        # Danh sách chi tiết
        chi_tiet_items.append(
            FacultyInternBreakdownItem(
                ma_truong=m_truong,
                ten_truong=t_truong,
                chuyen_nganh=c_nganh,
                so_luong=s_luong,
                ty_le_phan_tram=ty_le
            )
        )

        # Gom nhóm theo Trường
        if m_truong not in universities_map:
            universities_map[m_truong] = {
                "ma_truong": m_truong,
                "ten_truong": t_truong,
                "tong_sinh_vien": 0,
                "majors": []
            }
        universities_map[m_truong]["tong_sinh_vien"] += s_luong
        universities_map[m_truong]["majors"].append({
            "chuyen_nganh": c_nganh,
            "so_luong": s_luong
        })

        # Gom nhóm theo Chuyên ngành
        if c_nganh not in majors_map:
            majors_map[c_nganh] = {
                "chuyen_nganh": c_nganh,
                "tong_sinh_vien": 0,
                "universities": []
            }
        majors_map[c_nganh]["tong_sinh_vien"] += s_luong
        majors_map[c_nganh]["universities"].append({
            "ma_truong": m_truong,
            "ten_truong": t_truong,
            "so_luong": s_luong
        })

    # Chuyển đổi dữ liệu nhóm Trường sang schema
    thong_ke_theo_truong = []
    for u in universities_map.values():
        u_total = u["tong_sinh_vien"]
        danh_sach_cn = [
            FacultyMajorItem(
                chuyen_nganh=m["chuyen_nganh"],
                so_luong=m["so_luong"],
                ty_le_phan_tram=round((m["so_luong"] / u_total * 100), 2) if u_total > 0 else 0.0
            )
            for m in u["majors"]
        ]
        thong_ke_theo_truong.append(
            FacultyUniversityStat(
                ma_truong=u["ma_truong"],
                ten_truong=u["ten_truong"],
                tong_sinh_vien=u_total,
                danh_sach_chuyen_nganh=danh_sach_cn
            )
        )
    thong_ke_theo_truong.sort(key=lambda x: x.tong_sinh_vien, reverse=True)

    # Chuyển đổi dữ liệu nhóm Chuyên ngành sang schema
    thong_ke_theo_chuyen_nganh = []
    for m in majors_map.values():
        m_total = m["tong_sinh_vien"]
        danh_sach_tr = [
            FacultyUniversityItem(
                ma_truong=tr["ma_truong"],
                ten_truong=tr["ten_truong"],
                so_luong=tr["so_luong"],
                ty_le_phan_tram=round((tr["so_luong"] / m_total * 100), 2) if m_total > 0 else 0.0
            )
            for tr in m["universities"]
        ]
        thong_ke_theo_chuyen_nganh.append(
            FacultyMajorStat(
                chuyen_nganh=m["chuyen_nganh"],
                tong_sinh_vien=m_total,
                danh_sach_truong=danh_sach_tr
            )
        )
    thong_ke_theo_chuyen_nganh.sort(key=lambda x: x.tong_sinh_vien, reverse=True)

    # Xác định trường và chuyên ngành có nhiều sinh viên nhất
    truong_top = thong_ke_theo_truong[0].ten_truong if thong_ke_theo_truong else None
    nganh_top = thong_ke_theo_chuyen_nganh[0].chuyen_nganh if thong_ke_theo_chuyen_nganh else None

    summary = FacultyReportSummary(
        tong_sinh_vien=tong_sinh_vien,
        tong_so_truong=len(universities_map),
        tong_so_chuyen_nganh=len(majors_map),
        truong_nhieu_sinh_vien_nhat=truong_top,
        chuyen_nganh_nhieu_sinh_vien_nhat=nganh_top
    )

    data = FacultyReportData(
        summary=summary,
        thong_ke_theo_truong=thong_ke_theo_truong,
        thong_ke_theo_chuyen_nganh=thong_ke_theo_chuyen_nganh,
        chi_tiet=chi_tiet_items
    )

    return FacultyReportResponse(
        status_code=200,
        message="Lấy báo cáo thống kê sinh viên theo trường và chuyên ngành thành công",
        data=data
    )

