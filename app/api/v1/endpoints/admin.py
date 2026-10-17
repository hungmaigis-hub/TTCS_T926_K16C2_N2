"""
Router Admin: Quản trị tài khoản & người dùng
Endpoint: POST /api/v1/admin/users
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.core.security import hash_password
from app.models.nguoi_dung import NguoiDung
from app.schemas.user import UserCreate, UserResponse, UserRole

router = APIRouter()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin tạo tài khoản người dùng mới",
    description="""
    Endpoint dành riêng cho Quản trị viên (Admin) tạo tài khoản cho các đối tượng trong hệ thống:
    - Băm mật khẩu bảo mật bằng thuật toán **bcrypt**.
    - Gán một trong 4 vai trò hợp lệ: **Admin**, **HR**, **Mentor**, **ThucTapSinh**.
    - Kiểm tra và chống trùng lặp **username (tên đăng nhập)** và **email** trong bảng `nguoi_dung`.
    - Trả về mã HTTP **201 Created** khi tạo thành công.
    - Trả về mã HTTP **400 Bad Request** khi username hoặc email đã tồn tại.
    - Trả về mã HTTP **422 Unprocessable Entity** khi dữ liệu thiếu trường hoặc vai trò không hợp lệ.
    - Trả về mã HTTP **403 Forbidden** nếu tài khoản thực hiện không có quyền Admin.
    """
)
def create_user_by_admin(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: NguoiDung = Depends(get_current_admin)
):
    """
    Xử lý logic tạo tài khoản người dùng bởi Admin.
    """
    # 1. Kiểm tra chống trùng lặp Tên đăng nhập (username)
    user_exists_username = db.query(NguoiDung).filter(
        NguoiDung.ten_dang_nhap == user_in.ten_dang_nhap
    ).first()
    if user_exists_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{user_in.ten_dang_nhap}' đã tồn tại trong hệ thống. Vui lòng chọn tên đăng nhập khác."
        )

    # 2. Kiểm tra chống trùng lặp Email
    user_exists_email = db.query(NguoiDung).filter(
        NguoiDung.email == user_in.email
    ).first()
    if user_exists_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' đã tồn tại trong hệ thống. Vui lòng sử dụng email khác."
        )

    # 3. Băm mật khẩu bằng thuật toán bcrypt
    hashed_pwd = hash_password(user_in.mat_khau)

    # 4. Xác định giá trị vai trò
    role_value = user_in.vai_tro.value if hasattr(user_in.vai_tro, "value") else str(user_in.vai_tro)

    # 5. Khởi tạo bản ghi người dùng mới trong bảng nguoi_dung
    new_user = NguoiDung(
        ten_dang_nhap=user_in.ten_dang_nhap,
        email=user_in.email,
        mat_khau_hash=hashed_pwd,
        ho_ten=user_in.ho_ten,
        vai_tro=role_value,
        trang_thai=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lưu người dùng vào cơ sở dữ liệu: {str(e)}"
        )

    return new_user


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Admin xem danh sách người dùng",
    description="Endpoint hỗ trợ Frontend hiển thị bảng danh sách tài khoản sau khi tạo mới."
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    vai_tro: Optional[UserRole] = Query(None, description="Lọc theo vai trò"),
    db: Session = Depends(get_db),
    current_admin: NguoiDung = Depends(get_current_admin)
):
    query = db.query(NguoiDung)
    if vai_tro:
        query = query.filter(NguoiDung.vai_tro == vai_tro.value)
    users = query.offset(skip).limit(limit).all()
    return users
