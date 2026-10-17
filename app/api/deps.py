from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.nguoi_dung import NguoiDung
from app.crud.crud_nguoi_dung import crud_nguoi_dung

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    x_user_id: Optional[int] = Header(None, alias="X-User-Id", description="Dùng cho dev/test hoặc API gateway nếu không truyền Bearer token")
) -> NguoiDung:
    """
    Dependency lấy người dùng hiện tại đang đăng nhập.
    Ưu tiên 1: Bearer JWT Token trong Header Authorization.
    Ưu tiên 2: X-User-Id trong Header (hỗ trợ kiểm thử nhanh giữa các bạn Frontend/Tester).
    Nếu không có hoặc không hợp lệ -> 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập (Vui lòng đăng nhập)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user: Optional[NguoiDung] = None

    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            user = crud_nguoi_dung.get_by_id(db, ma_nguoi_dung=int(user_id))
        except (JWTError, ValueError):
            raise credentials_exception
    elif x_user_id is not None:
        user = crud_nguoi_dung.get_by_id(db, ma_nguoi_dung=x_user_id)
        if not user:
            raise credentials_exception
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    if not user.kich_hoat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản người dùng đã bị vô hiệu hóa"
        )
    return user
