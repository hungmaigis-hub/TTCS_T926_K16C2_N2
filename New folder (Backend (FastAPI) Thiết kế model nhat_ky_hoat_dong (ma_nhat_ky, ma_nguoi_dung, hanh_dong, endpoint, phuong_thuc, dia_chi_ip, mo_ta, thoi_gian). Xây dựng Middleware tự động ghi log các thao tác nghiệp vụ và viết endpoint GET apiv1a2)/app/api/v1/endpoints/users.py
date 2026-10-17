from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.security import get_password_hash
from app.models.nguoi_dung import NguoiDung
from app.schemas.nguoi_dung import NguoiDungBrief

router = APIRouter()


class UserCreateRequest(BaseModel):
    ten_dang_nhap: str = Field(..., min_length=3, max_length=50, example="mentor_hung")
    email: EmailStr = Field(..., example="mentor.hung@gmail.com")
    mat_khau: str = Field(..., min_length=6, example="MatKhau@123")
    ho_ten: str = Field(..., example="Lê Văn Hùng")
    vai_tro: str = Field(default="ThucTapSinh", example="Mentor", description="Admin, HR, Mentor, ThucTapSinh")


@router.post(
    "/admin/users",
    response_model=NguoiDungBrief,
    status_code=status.HTTP_201_CREATED,
    summary="Admin tạo tài khoản người dùng mới",
    description="Endpoint cho phép Admin tạo mới người dùng, băm mật khẩu bằng bcrypt và gán vai trò tương ứng."
)
def create_user(
    req: Request,
    user_in: UserCreateRequest,
    current_admin: NguoiDung = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # Ràng buộc trùng lặp username hoặc email
    existing_user = db.query(NguoiDung).filter(
        (NguoiDung.ten_dang_nhap == user_in.ten_dang_nhap) | (NguoiDung.email == user_in.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập hoặc email đã tồn tại trong hệ thống"
        )

    # Validate vai trò
    valid_roles = ["Admin", "HR", "Mentor", "ThucTapSinh"]
    if user_in.vai_tro not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vai trò không hợp lệ. Chọn một trong: {', '.join(valid_roles)}"
        )

    # Gán ngữ cảnh cho AuditLogMiddleware
    req.state.audit_action = "TAO_NGUOI_DUNG"
    req.state.audit_description = f"Admin '{current_admin.ten_dang_nhap}' tạo mới người dùng '{user_in.ten_dang_nhap}' với vai trò '{user_in.vai_tro}'"

    new_user = NguoiDung(
        ten_dang_nhap=user_in.ten_dang_nhap,
        email=user_in.email,
        mat_khau_hash=get_password_hash(user_in.mat_khau),
        ho_ten=user_in.ho_ten,
        vai_tro=user_in.vai_tro,
        trang_thai=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "/admin/users",
    response_model=List[NguoiDungBrief],
    summary="Lấy danh sách người dùng",
    description="Trả về danh sách người dùng trong hệ thống (dành cho Admin)."
)
def get_users(
    current_admin: NguoiDung = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(NguoiDung).all()
