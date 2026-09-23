from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from schemas import InternUpdate

#thư mục database
from database.database import get_db
from database.models import Intern

# khởi tạo
app = FastAPI(title="Internship ictu API")

# cấu hình cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# viết api get thông tin thực tập sinh 
@app.get("/api/interns/{id}")
def get_intern_detail(id: int, db: Session = Depends(get_db)):
    intern = db.query(Intern).filter(Intern.id == id).first()
    if not intern:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thực tập sinh ID: {id}")
    return {
        "status_code": 200,
        "message": "Thông tin thực tập sinh",
        "data": intern.to_dict()
    }

# viết api cập nhật thông tin thực tập sinh
@app.put("/api/interns/{id}")
def update_intern(id: int, intern_data: InternUpdate, db: Session = Depends(get_db)):
    
    # Kiểm tra thuc tap sinh có tồn tại trong CSDL không
    intern = db.query(Intern).filter(Intern.id == id).first()
    if not intern:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thực tập sinh ID: {id}")
    
    # Kiểm tra trùng lặp email
    existing_email = db.query(Intern).filter(
        Intern.email == intern_data.email,
        Intern.id != id
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng")
    # Kiểm tra sdt
    if intern_data.phone:
        existing_phone = db.query(Intern).filter(
            Intern.phone == intern_data.phone,
            Intern.id != id
        ).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng")
    
    # Cập nhật các trường thông tin mới
    intern.full_name = intern_data.full_name
    intern.email = intern_data.email
    intern.phone = intern_data.phone
    intern.university = intern_data.university
    intern.major = intern_data.major
    intern.status = intern_data.status
    intern.start_date = intern_data.start_date
    intern.end_date = intern_data.end_date

    # Lưu thay đổi vào Database
    db.commit()
    db.refresh(intern)

    # Trả về phản hồi
    return {
        "status_code": 200,
        "message": "Cập nhật thông tin thực tập sinh thành công",
        "data": intern.to_dict()
    }
