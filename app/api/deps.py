"""
FastAPI Dependencies: Database session & Phân quyền RBAC (Role-Based Access Control).
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from typing import Optional, Union, Any
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.nguoi_dung import NguoiDung
from app.crud.crud_nguoi_dung import crud_nguoi_dung
from app.schemas.user import UserRole

# Khởi tạo OAuth2 Scheme tương thích Swagger UI
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    x_user_id: Optional[Union[int, str]] = Header(None, alias="X-User-Id", description="ID người dùng giả lập"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role", description="Header giả lập vai trò (hỗ trợ kiểm thử tự động)")
) -> NguoiDung:
    """
    Xác định người dùng hiện tại từ:
    1. Bearer JWT Token
    2. Header X-User-Role (hỗ trợ kiểm thử phân quyền nhanh)
    3. Header X-User-Id
    Nếu chưa đăng nhập / không hợp lệ: Trả về HTTP 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập (Vui lòng đăng nhập)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user: Optional[NguoiDung] = None

    # 1. Bearer Token
    if token:
        payload = decode_access_token(token)
        if not payload:
            raise credentials_exception
        
        user_id = payload.get("user_id")
        sub = payload.get("sub")
        if user_id is not None:
            user = crud_nguoi_dung.get_by_id(db, ma_nguoi_dung=user_id)
        if not user and sub is not None:
            # Tra cứu theo ID, ten_dang_nhap hoặc email
            user = crud_nguoi_dung.get_by_id(db, ma_nguoi_dung=sub)
            if not user:
                user = db.query(NguoiDung).filter(
                    (NguoiDung.ten_dang_nhap == sub) | (NguoiDung.email == sub)
                ).first()
        if not user:
            raise credentials_exception

    # 2. X-User-Role Header
    elif x_user_role:
        user = db.query(NguoiDung).filter(NguoiDung.vai_tro == x_user_role).first()
        if not user:
            user = NguoiDung(
                ma_nguoi_dung="9999",
                ten_dang_nhap=f"mock_{x_user_role.lower()}",
                email=f"{x_user_role.lower()}@test.com",
                mat_khau_hash="mock_hash",
                ho_ten=f"Mock {x_user_role}",
                vai_tro=x_user_role,
                trang_thai=True
            )
            return user

    # 3. X-User-Id Header
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


def get_current_admin(
    current_user: NguoiDung = Depends(get_current_user)
) -> NguoiDung:
    """
    Yêu cầu quyền Quản trị viên (Admin).
    Nếu không phải Admin -> 403 Forbidden.
    """
    role_str = current_user.vai_tro.value if hasattr(current_user.vai_tro, "value") else str(current_user.vai_tro)
    if role_str != UserRole.ADMIN.value and role_str != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ có Quản trị viên (Admin) / Chỉ quản trị viên (Admin) mới có quyền thực hiện thao tác này."
        )
    return current_user


require_admin = get_current_admin
