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
from sqlalchemy import extract, or_

from schemas import (
    InternCreate,
    InternUpdate,
    InternApprovalUpdate,
    ContractConfirmRequest,
    DocumentStatusUpdate,
    DocumentUploadResponse,
    ProgramCreate,
    ProgramResponse,
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
    LeaveRequestCreate,
    LeaveRequestCreateResponse,
    LeaveRequestItemData,
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
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng")

    # 2. Kiểm tra trùng lặp số điện thoại nếu có gửi lên
    if intern_data.so_dien_thoai:
        existing_phone = db.query(NguoiDung).filter(NguoiDung.so_dien_thoai == intern_data.so_dien_thoai).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng")

    # 3. Kiểm tra mã trường đại học nếu có gửi lên
    if intern_data.ma_truong:
        truong = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == intern_data.ma_truong).first()
        if not truong:
            raise HTTPException(status_code=400, detail="Mã trường đại học không tồn tại trong hệ thống")

    # 4. Kiểm tra mã chương trình thực tập nếu có gửi lên
    if intern_data.ma_chuong_trinh:
        chuong_trinh = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == intern_data.ma_chuong_trinh).first()
        if not chuong_trinh:
            raise HTTPException(status_code=400, detail="Mã chương trình thực tập không tồn tại trong hệ thống")

    # 5. Kiểm tra mã mentor nếu có gửi lên
    if intern_data.ma_mentor:
        mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_data.ma_mentor).first()
        if not mentor:
            raise HTTPException(status_code=400, detail="Mã người hướng dẫn (mentor) không tồn tại trong hệ thống")

    try:
        # 6. Khởi tạo tài khoản người dùng cho thực tập sinh (bảng NGUOI_DUNG)
        new_user = NguoiDung(
            ho_ten=intern_data.ho_ten,
            email=intern_data.email,
            so_dien_thoai=intern_data.so_dien_thoai,
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add(new_user)
        db.flush()  # Sinh mã new_user.ma_nguoi_dung cho khóa ngoại

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


# api get intern list
@app.get("/api/v1/interns", status_code=200)
def get_interns_list(
    trang_thai_xet_duyet: Optional[str] = None,
    trang_thai_thuc_tap: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách hồ sơ thực tập sinh từ cơ sở dữ liệu.
    Hỗ trợ lọc theo trạng thái xét duyệt (ChoDuyet, DaDuyet, TuChoi) và trạng thái thực tập (DangThucTap, HoanThanh, ThoiHoc).
    Sắp xếp theo mã hồ sơ mới nhất (desc).
    """
    query = db.query(HoSoThucTap)
    if trang_thai_xet_duyet:
        query = query.filter(HoSoThucTap.trang_thai_xet_duyet == trang_thai_xet_duyet)
    if trang_thai_thuc_tap:
        query = query.filter(HoSoThucTap.trang_thai_thuc_tap == trang_thai_thuc_tap)

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
    email_normalized = data.email.strip().lower()

    user = db.query(NguoiDung).filter(NguoiDung.email == email_normalized).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")

    if not user.mat_khau_hash or not verify_password(data.mat_khau, user.mat_khau_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")

    if user.trang_thai == "Khoa":
        raise HTTPException(status_code=403, detail="Tài khoản này đang bị khóa")

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
    - Lưu bản ghi vào bảng don_xin_nghi.
    - Trả về mã HTTP 201 Created cùng dữ liệu đơn xin nghỉ vừa tạo.
    """
    # 1. Kiểm tra hồ sơ thực tập sinh có tồn tại trong hệ thống không
    ho_so = db.query(HoSoThucTap).filter(HoSoThucTap.ma_ho_so == req.ma_ho_so).first()
    if not ho_so:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hồ sơ thực tập sinh với mã ID: {req.ma_ho_so}"
        )

    # 2. Khởi tạo bản ghi đơn xin nghỉ mới
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



