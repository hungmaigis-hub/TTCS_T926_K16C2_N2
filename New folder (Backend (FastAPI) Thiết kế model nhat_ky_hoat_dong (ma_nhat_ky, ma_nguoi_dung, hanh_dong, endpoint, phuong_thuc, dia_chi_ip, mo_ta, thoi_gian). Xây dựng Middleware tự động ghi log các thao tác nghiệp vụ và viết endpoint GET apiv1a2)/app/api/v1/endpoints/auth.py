from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.nguoi_dung import NguoiDung
from app.schemas.nguoi_dung import TokenResponse, NguoiDungBrief

router = APIRouter()


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Đăng nhập hệ thống",
    description="Xác thực thông tin tài khoản bằng tên đăng nhập và mật khẩu, trả về JWT Access Token."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == form_data.username).first()
    if not user or not verify_password(form_data.password, user.mat_khau_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị tạm khóa, vui lòng liên hệ quản trị viên",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.ten_dang_nhap, "user_id": user.ma_nguoi_dung, "vai_tro": user.vai_tro},
        expires_delta=access_token_expires
    )

    user_brief = NguoiDungBrief(
        ma_nguoi_dung=user.ma_nguoi_dung,
        ten_dang_nhap=user.ten_dang_nhap,
        ho_ten=user.ho_ten,
        email=user.email,
        vai_tro=user.vai_tro
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_brief
    )
