from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from schemas import InternCreate, InternUpdate, DocumentStatusUpdate

# Thư mục database & models
from database.session import get_db
from database.models import HoSoThucTap, NguoiDung, TruongDaiHoc, TaiLieuHoSo, ChuongTrinhThucTap

# Dịch vụ gửi email thông báo
from services.email_service import send_document_approval_email

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="Internship Management API", version="1.0.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# api post create intern
@app.post("/api/v1/interns", status_code=201)
def create_intern(intern_data: InternCreate, db: Session = Depends(get_db)):
    """
    Tạo mới hồ sơ thực tập sinh:
    1. Kiểm tra tính hợp lệ và không trùng lặp của email, số điện thoại.
    2. Kiểm tra tồn tại của các khóa ngoại: trường đại học, chương trình, mentor.
    3. Tạo tài khoản người dùng NguoiDung (vai_tro='ThucTapSinh').
    4. Tạo bản ghi hồ sơ thực tập HoSoThucTap trong cùng một transaction.
    """
    # 1. Kiểm tra trùng email
    exist_email = db.query(NguoiDung).filter(NguoiDung.email == intern_data.email).first()
    if exist_email:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng trong hệ thống")

    # 2. Kiểm tra trùng số điện thoại (nếu có cung cấp)
    if intern_data.so_dien_thoai:
        exist_phone = db.query(NguoiDung).filter(NguoiDung.so_dien_thoai == intern_data.so_dien_thoai).first()
        if exist_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng trong hệ thống")

    # 3. Kiểm tra khóa ngoại ma_truong
    if intern_data.ma_truong:
        truong = db.query(TruongDaiHoc).filter(TruongDaiHoc.ma_truong == intern_data.ma_truong).first()
        if not truong:
            raise HTTPException(status_code=400, detail="Mã trường đại học không tồn tại trong hệ thống")

    # 4. Kiểm tra khóa ngoại ma_chuong_trinh
    if intern_data.ma_chuong_trinh:
        chuong_trinh = db.query(ChuongTrinhThucTap).filter(ChuongTrinhThucTap.ma_chuong_trinh == intern_data.ma_chuong_trinh).first()
        if not chuong_trinh:
            raise HTTPException(status_code=400, detail="Mã chương trình thực tập không tồn tại trong hệ thống")

    # 5. Kiểm tra khóa ngoại ma_mentor
    if intern_data.ma_mentor:
        mentor = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == intern_data.ma_mentor).first()
        if not mentor:
            raise HTTPException(status_code=400, detail="Mã người hướng dẫn (mentor) không tồn tại trong hệ thống")

    try:
        # 6. Tạo người dùng mới với vai trò ThucTapSinh
        new_user = NguoiDung(
            ho_ten=intern_data.ho_ten,
            email=intern_data.email,
            so_dien_thoai=intern_data.so_dien_thoai,
            vai_tro="ThucTapSinh",
            trang_thai="HoatDong"
        )
        db.add(new_user)
        db.flush()  # Lấy new_user.ma_nguoi_dung tự tăng mà chưa commit

        # 7. Tạo hồ sơ thực tập liên kết
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

        return {
            "status_code": 201,
            "message": "Tạo hồ sơ thực tập sinh thành công",
            "data": new_ho_so.to_dict()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi tạo hồ sơ: {str(e)}")


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
