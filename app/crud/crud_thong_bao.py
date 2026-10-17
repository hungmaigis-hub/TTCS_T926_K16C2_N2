from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.thong_bao import ThongBao
from app.schemas.thong_bao import ThongBaoCreate


class CRUDThongBao:
    def get_by_id(self, db: Session, ma_thong_bao: int) -> Optional[ThongBao]:
        """Lấy thông báo theo mã thông báo."""
        return db.query(ThongBao).filter(ThongBao.ma_thong_bao == ma_thong_bao).first()

    def get_multi_by_user(
        self,
        db: Session,
        ma_nguoi_nhan: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ThongBao]:
        query = db.query(ThongBao).filter(ThongBao.ma_nguoi_nhan == ma_nguoi_nhan)
        if unread_only:
            query = query.filter(ThongBao.da_doc == False)
        return query.order_by(desc(ThongBao.ngay_tao)).offset(skip).limit(limit).all()

    def count_by_user(
        self,
        db: Session,
        ma_nguoi_nhan: int,
        unread_only: bool = False,
    ) -> int:
        query = db.query(ThongBao).filter(ThongBao.ma_nguoi_nhan == ma_nguoi_nhan)
        if unread_only:
            query = query.filter(ThongBao.da_doc == False)
        return query.count()

    def count_unread_by_user(self, db: Session, ma_nguoi_nhan: int) -> int:
        return db.query(ThongBao).filter(
            ThongBao.ma_nguoi_nhan == ma_nguoi_nhan,
            ThongBao.da_doc == False,
        ).count()

    def mark_as_read(self, db: Session, thong_bao: ThongBao) -> ThongBao:
        thong_bao.da_doc = True
        db.add(thong_bao)
        db.commit()
        db.refresh(thong_bao)
        return thong_bao

    def mark_all_as_read(self, db: Session, ma_nguoi_nhan: int) -> int:
        updated_rows = db.query(ThongBao).filter(
            ThongBao.ma_nguoi_nhan == ma_nguoi_nhan,
            ThongBao.da_doc == False,
        ).update({ThongBao.da_doc: True}, synchronize_session="fetch")
        db.commit()
        return updated_rows

    def create(self, db: Session, obj_in: ThongBaoCreate) -> ThongBao:
        db_obj = ThongBao(
            ma_nguoi_nhan=obj_in.ma_nguoi_nhan,
            tieu_de=obj_in.tieu_de,
            noi_dung=obj_in.noi_dung,
            loai_thong_bao=obj_in.loai_thong_bao or "CHUNG",
            da_doc=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_thong_bao = CRUDThongBao()
