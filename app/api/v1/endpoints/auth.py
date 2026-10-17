"""
Router Xác thực & Đăng nhập (Auth)
Hỗ trợ đăng nhập sinh JWT Bearer token cho Admin, HR, Mentor, ThucTapSinh.
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import verify_password, create_access_token
from app.models.nguoi_dung import NguoiDung
from app.schemas.user import UserLoginRequest, TokenResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập tài khoản lấy JWT Bearer Token",
    description="Cho phép Admin và các vai trò đăng nhập để lấy token thực hiện các tác vụ cần phân quyền."
)
def login_for_access_token(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(NguoiDung).filter(
        NguoiDung.ten_dang_nhap == login_data.ten_dang_nhap
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login_data.mat_khau, user.mat_khau_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa."
        )

    access_token = create_access_token(subject=user.ten_dang_nhap, role=user.vai_tro)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.vai_tro,
        username=user.ten_dang_nhap
    )
