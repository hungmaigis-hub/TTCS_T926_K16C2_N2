
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.crud_nguoi_dung import crud_nguoi_dung
from app.schemas.nguoi_dung import Token, NguoiDungCreate, NguoiDungResponse
=======
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



@router.post("/login", response_model=Token, summary="Đăng nhập lấy JWT Token")
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 tương thích login endpoint.
    form_data.username truyền email hoặc username, form_data.password truyền mật khẩu.
    """
    user = crud_nguoi_dung.authenticate(
        db, email=form_data.username, mat_khau=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.kich_hoat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hóa"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.ma_nguoi_dung, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=NguoiDungResponse, summary="Đăng ký người dùng mới")
def register_user(
    user_in: NguoiDungCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Tạo người dùng mới để thử nghiệm hệ thống"""
    user = crud_nguoi_dung.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng trong hệ thống",
        )
    return crud_nguoi_dung.create(db, obj_in=user_in)
=======
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

