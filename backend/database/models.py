from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from database.database import Base

class Intern(Base):
    # khai báo tên bảng trong csdl
    __tablename__ = "interns"

    # khai báo các cột trong bảng interns (cách 1)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    university = Column(String(150))
    major = Column(String(100))
    status = Column(String(50), default="Đang thực tập")
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    
    # cách 2 (tự động load các cột từ csdl)
    # __table_args__ = {"autoload_with": engine}


    # viết hàm để đổi object sang dict
    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            # Nếu là kiểu ngày tháng (Date/DateTime) thì đổi sang định dạng chuỗi YYYY-MM-DD
            if hasattr(val, "isoformat"):
                val = val.isoformat()
            result[col.name] = val
        return result