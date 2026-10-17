from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.nguoi_dung import NguoiDung

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    x_test_user_id: Optional[str] = Header(None, alias="X-Test-User-Id"),
    db: Session = Depends(get_db)
) -> NguoiDung:
    """
    Xác thực người dùng hiện tại từ JWT Bearer token hoặc header hỗ trợ testing
    """
    # 1. Hỗ trợ test header nếu không có token JWT
    if not token and x_test_user_id:
        try:
            uid = int(x_test_user_id)
            user = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == uid).first()
            if user:
                return user
        except ValueError:
            pass

    # 2. Xác thực bằng JWT Token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập hoặc thiếu token xác thực",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin người dùng trong token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )

    if not user.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản người dùng đã bị khóa",
        )

    return user


async def require_admin(
    current_user: NguoiDung = Depends(get_current_user)
) -> NguoiDung:
    """
    Ràng buộc phân quyền chỉ cho phép tài khoản có vai trò 'Admin' truy cập
    """
    if current_user.vai_tro != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quyền truy cập bị từ chối: Chỉ quản trị viên (Admin) mới có quyền truy cập nhật ký hoạt động.",
        )
    return current_user
