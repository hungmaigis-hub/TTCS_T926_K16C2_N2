from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Mentor(Base):
    __tablename__ = "mentor"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ma_mentor = Column(String(50), unique=True, index=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    chuc_vu = Column(String(100), nullable=True)
    phong_ban = Column(String(100), nullable=True)
    role = Column(String(50), default="Mentor")  # Để phục vụ tester test role
    is_active = Column(Boolean, default=True)
