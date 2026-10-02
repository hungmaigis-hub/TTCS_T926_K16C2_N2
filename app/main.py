from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base, SessionLocal
from app.models.ho_so_thuc_tap import HoSoThucTap
from app.models.mentor import Mentor
from app.api.v1.router import api_router


def seed_initial_data():
    """Tạo sẵn dữ liệu mẫu cho thực tập sinh và mentor để frontend/tester test được ngay."""
    db = SessionLocal()
    try:
        # Tạo bảng nếu chưa có
        Base.metadata.create_all(bind=engine)

        # Seed Mentor nếu chưa có
        if db.query(Mentor).count() == 0:
            sample_mentors = [
                Mentor(
                    ma_mentor="MTR001",
                    ho_ten="Trần Quốc Huy",
                    email="huy.tran@company.com",
                    chuc_vu="Senior Backend Engineer",
                    phong_ban="Phòng Phát triển Phần mềm",
                    role="Mentor",
                    is_active=True,
                ),
                Mentor(
                    ma_mentor="MTR002",
                    ho_ten="Nguyễn Trung Học",
                    email="hoc.nguyen@company.com",
                    chuc_vu="Tech Lead",
                    phong_ban="Phòng Kỹ thuật",
                    role="Mentor",
                    is_active=True,
                ),
                Mentor(
                    ma_mentor="MTR003",
                    ho_ten="Dương Đình Hoàng",
                    email="hoang.duong@company.com",
                    chuc_vu="Senior DevOps",
                    phong_ban="Phòng Hạ tầng",
                    role="Mentor",
                    is_active=True,
                ),
                Mentor(
                    ma_mentor="USR999",
                    ho_ten="Nguyễn Văn Test",
                    email="test@company.com",
                    chuc_vu="Nhân viên",
                    phong_ban="Phòng Hành chính",
                    role="Employee",  # Không phải Mentor để test case phân quyền
                    is_active=True,
                ),
            ]
            db.add_all(sample_mentors)
            db.commit()

        # Seed Hồ sơ thực tập sinh nếu chưa có
        if db.query(HoSoThucTap).count() == 0:
            sample_interns = [
                HoSoThucTap(
                    ma_thuc_tap_sinh="TTS2024001",
                    ho_ten="Lê Hoàng Huy",
                    email="huy.le@university.edu.vn",
                    truong_dai_hoc="Đại học Quốc gia",
                    chuyen_nganh="Công nghệ Thông tin",
                    vi_tri_thuc_tap="Frontend Intern",
                    ma_phong_ban="PB01",
                    ma_mentor=None,  # Chưa gán mentor
                    trang_thai="dang_thuc_tap",
                ),
                HoSoThucTap(
                    ma_thuc_tap_sinh="TTS2024002",
                    ho_ten="Lý Văn Hưng",
                    email="hung.ly@university.edu.vn",
                    truong_dai_hoc="Đại học Bách Khoa",
                    chuyen_nganh="Kỹ thuật Phần mềm",
                    vi_tri_thuc_tap="Frontend Intern",
                    ma_phong_ban="PB01",
                    ma_mentor="MTR001",  # Đã gán mentor
                    trang_thai="dang_thuc_tap",
                ),
                HoSoThucTap(
                    ma_thuc_tap_sinh="TTS2024003",
                    ho_ten="Võ Quang Huy",
                    email="huy.vo@university.edu.vn",
                    truong_dai_hoc="Đại học Công nghệ",
                    chuyen_nganh="Khoa học Máy tính",
                    vi_tri_thuc_tap="Backend Intern",
                    ma_phong_ban="PB01",
                    ma_mentor=None,  # Chưa gán mentor
                    trang_thai="dang_thuc_tap",
                ),
            ]
            db.add_all(sample_interns)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo db và dữ liệu mẫu khi start app
    seed_initial_data()
    yield


app = FastAPI(
    title="Hệ thống Quản lý Thực tập sinh (Intern Management API)",
    description="Backend API viết bằng FastAPI phục vụ quản lý thực tập sinh, phân công mentor.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Cấu hình CORS để frontend HTML/JS/React gọi không bị chặn ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Đăng ký API Routers ───────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "message": "API Quản lý thực tập sinh đang hoạt động.",
        "docs_url": "/docs",
    }
