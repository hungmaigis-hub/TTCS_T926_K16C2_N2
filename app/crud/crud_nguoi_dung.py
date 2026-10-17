from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.nguoi_dung import NguoiDung
from app.schemas.nguoi_dung import NguoiDungCreate
from app.core.security import get_password_hash, verify_password


class CRUDNguoiDung:
    def get_by_id(self, db: Session, ma_nguoi_dung: Any) -> Optional[NguoiDung]:
        return db.query(NguoiDung).filter(
            (NguoiDung.ma_nguoi_dung == str(ma_nguoi_dung)) | (NguoiDung.ma_nguoi_dung == ma_nguoi_dung)
        ).first()

    def get_by_email(self, db: Session, email: str) -> Optional[NguoiDung]:
        return db.query(NguoiDung).filter(NguoiDung.email == email).first()

    def create(self, db: Session, obj_in: NguoiDungCreate) -> NguoiDung:
        db_obj = NguoiDung(
            email=obj_in.email,
            mat_khau_hash=get_password_hash(obj_in.mat_khau),
            ho_ten=obj_in.ho_ten,
            vai_tro=obj_in.vai_tro or "ThucTapSinh",
            kich_hoat=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, email: str, mat_khau: str) -> Optional[NguoiDung]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(mat_khau, user.mat_khau_hash):
            return None
        return user


crud_nguoi_dung = CRUDNguoiDung()
