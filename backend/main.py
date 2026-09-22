from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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
    