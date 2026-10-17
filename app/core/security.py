"""
Module Bảo mật: Băm mật khẩu bằng bcrypt và xử lý JWT Token.
Phụ trách: Nguyễn Văn Hiếu (Backend FastAPI)
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
import bcrypt
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Băm mật khẩu người dùng sử dụng thuật toán bcrypt tiêu chuẩn.
    Tuân thủ đúng yêu cầu đề bài: băm mật khẩu bằng bcrypt.
    """
    # bcrypt yêu cầu bytes
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác minh mật khẩu dạng thô (plain text) với mật khẩu đã băm trong database.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Tạo JWT Access Token chứa subject (username / user_id) và role (Admin, HR, Mentor, ThucTapSinh).
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Giải mã và kiểm tra tính hợp lệ của JWT Token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
