"""
Router Xác thực & Đăng nhập (Auth)
Hỗ trợ đăng nhập sinh JWT Bearer token cho Admin, HR, Mentor, ThucTapSinh.
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.nguoi_dung import NguoiDung
from app.crud.crud_nguoi_dung import crud_nguoi_dung
from app.schemas.nguoi_dung import Token, NguoiDungCreate, NguoiDungResponse
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
        or_(
            NguoiDung.ten_dang_nhap == login_data.ten_dang_nhap,
            NguoiDung.email == login_data.ten_dang_nhap
        )
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

    if not user.kich_hoat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa."
        )

    identifier = user.ten_dang_nhap or user.email
    access_token = create_access_token(subject=identifier, role=user.vai_tro)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.vai_tro,
        username=identifier
    )


@router.post("/login/access-token", response_model=Token, summary="OAuth2 form login cho Swagger UI")
def login_form_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(NguoiDung).filter(
        or_(
            NguoiDung.ten_dang_nhap == form_data.username,
            NguoiDung.email == form_data.username
        )
    ).first()
    if not user or not verify_password(form_data.password, user.mat_khau_hash):
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

    return {
        "access_token": create_access_token(
            subject=user.ma_nguoi_dung, role=user.vai_tro
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
