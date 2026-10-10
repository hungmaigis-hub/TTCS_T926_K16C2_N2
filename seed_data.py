from datetime import date, timedelta
from app.core.database import SessionLocal, engine, Base
from app.models.intern import Intern, InternStatus

def seed_sample_data():
    """Tạo dữ liệu mẫu sinh viên thực tập để phục vụ kiểm thử và cho team Frontend tích hợp."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Kiểm tra xem đã có dữ liệu chưa
        existing_count = db.query(Intern).count()
        if existing_count > 0:
            print(f"Cơ sở dữ liệu đã có {existing_count} sinh viên. Không cần seed lại.")
            return

        sample_interns = [
            # 18 Sinh viên đã Hoàn Thành (HoanThanh)
            {"student_code": "SV001", "full_name": "Nguyễn Văn An", "university": "ĐH Bách Khoa", "department": "Backend", "status": InternStatus.HoanThanh},
            {"student_code": "SV002", "full_name": "Trần Thị Bình", "university": "ĐH CNTT", "department": "Frontend", "status": InternStatus.HoanThanh},
            {"student_code": "SV003", "full_name": "Lê Văn Cường", "university": "ĐH Sư Phạm Kỹ Thuật", "department": "Mobile", "status": InternStatus.HoanThanh},
            {"student_code": "SV004", "full_name": "Phạm Minh Đức", "university": "ĐH Bách Khoa", "department": "Backend", "status": InternStatus.HoanThanh},
            {"student_code": "SV005", "full_name": "Hoàng Thùy Dung", "university": "ĐH Khoa Học Tự Nhiên", "department": "QA/QC", "status": InternStatus.HoanThanh},
            {"student_code": "SV006", "full_name": "Vũ Hải Đăng", "university": "ĐH Công Nghệ", "department": "DevOps", "status": InternStatus.HoanThanh},
            {"student_code": "SV007", "full_name": "Đặng Quốc Hưng", "university": "Học Viện Bưu Chính", "department": "Backend", "status": InternStatus.HoanThanh},
            {"student_code": "SV008", "full_name": "Ngô Bảo Khánh", "university": "ĐH Bách Khoa", "department": "Data", "status": InternStatus.HoanThanh},
            {"student_code": "SV009", "full_name": "Đỗ Thu Trang", "university": "ĐH CNTT", "department": "Frontend", "status": InternStatus.HoanThanh},
            {"student_code": "SV010", "full_name": "Bùi Tuấn Kiệt", "university": "ĐH Sư Phạm Kỹ Thuật", "department": "Backend", "status": InternStatus.HoanThanh},
            {"student_code": "SV011", "full_name": "Mai Thanh Lâm", "university": "ĐH Thủy Lợi", "department": "Frontend", "status": InternStatus.HoanThanh},
            {"student_code": "SV012", "full_name": "Lý Gia Hân", "university": "ĐH Bách Khoa", "department": "QA/QC", "status": InternStatus.HoanThanh},
            {"student_code": "SV013", "full_name": "Dương Văn Nam", "university": "ĐH Công Nghiệp", "department": "Backend", "status": InternStatus.HoanThanh},
            {"student_code": "SV014", "full_name": "Trịnh Mỹ Duyên", "university": "ĐH CNTT", "department": "Design UI/UX", "status": InternStatus.HoanThanh},
            {"student_code": "SV015", "full_name": "Đinh Quang Nhật", "university": "ĐH Quốc Gia", "department": "Mobile", "status": InternStatus.HoanThanh},
            {"student_code": "SV016", "full_name": "Hồ Ngọc Oanh", "university": "ĐH Khoa Học Tự Nhiên", "department": "Frontend", "status": InternStatus.HoanThanh},
            {"student_code": "SV017", "full_name": "Võ Tấn Phát", "university": "ĐH Bách Khoa", "department": "Backend", "status": InternStatus.HoanThanh},
            {"student_code": "SV018", "full_name": "Lưu Trọng Quân", "university": "Học Viện Bưu Chính", "department": "DevOps", "status": InternStatus.HoanThanh},

            # 9 Sinh viên đang thực tập (DangThucTap)
            {"student_code": "SV019", "full_name": "Trần Anh Quân", "university": "ĐH Bách Khoa", "department": "Backend", "status": InternStatus.DangThucTap},
            {"student_code": "SV020", "full_name": "Nguyễn Hoàng Sơn", "university": "ĐH CNTT", "department": "Frontend", "status": InternStatus.DangThucTap},
            {"student_code": "SV021", "full_name": "Phan Thanh Tâm", "university": "ĐH Sư Phạm Kỹ Thuật", "department": "Mobile", "status": InternStatus.DangThucTap},
            {"student_code": "SV022", "full_name": "Lê Anh Tuấn", "university": "ĐH Khoa Học Tự Nhiên", "department": "Backend", "status": InternStatus.DangThucTap},
            {"student_code": "SV023", "full_name": "Võ Minh Uyên", "university": "ĐH Công Nghệ", "department": "QA/QC", "status": InternStatus.DangThucTap},
            {"student_code": "SV024", "full_name": "Bùi Thế Vinh", "university": "ĐH Bách Khoa", "department": "Frontend", "status": InternStatus.DangThucTap},
            {"student_code": "SV025", "full_name": "Cao Xuân Vũ", "university": "ĐH Công Nghiệp", "department": "Backend", "status": InternStatus.DangThucTap},
            {"student_code": "SV026", "full_name": "Đoàn Như Ý", "university": "ĐH CNTT", "department": "Frontend", "status": InternStatus.DangThucTap},
            {"student_code": "SV027", "full_name": "Tạ Quang Dũng", "university": "Học Viện Bưu Chính", "department": "Backend", "status": InternStatus.DangThucTap},

            # 3 Sinh viên Thôi Học (ThoiHoc)
            {"student_code": "SV028", "full_name": "Phạm Quốc Bảo", "university": "ĐH Bách Khoa", "department": "Backend", "status": InternStatus.ThoiHoc},
            {"student_code": "SV029", "full_name": "Hoàng Kim Liên", "university": "ĐH CNTT", "department": "Frontend", "status": InternStatus.ThoiHoc},
            {"student_code": "SV030", "full_name": "Trần Văn Long", "university": "ĐH Thủy Lợi", "department": "QA/QC", "status": InternStatus.ThoiHoc},
        ]

        today = date.today()
        intern_objects = []
        for idx, item in enumerate(sample_interns):
            start = today - timedelta(days=90 - idx)
            end = today + timedelta(days=30) if item["status"] == InternStatus.DangThucTap else today - timedelta(days=10)
            
            intern = Intern(
                student_code=item["student_code"],
                full_name=item["full_name"],
                email=f"{item['student_code'].lower()}@school.edu.vn",
                university=item["university"],
                major="Công nghệ thông tin",
                department=item["department"],
                mentor_name="Nguyễn Văn Hiếu",
                status=item["status"],
                start_date=start,
                end_date=end
            )
            intern_objects.append(intern)

        db.add_all(intern_objects)
        db.commit()
        print(f"Đã tạo thành công {len(intern_objects)} sinh viên thực tập mẫu!")
        print("- HoanThanh: 18 sinh viên (60.0%)")
        print("- DangThucTap: 9 sinh viên (30.0%)")
        print("- ThoiHoc: 3 sinh viên (10.0%)")
        print("- Tỷ lệ hoàn thành (completion_rate): 60.0%")
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi seed data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
