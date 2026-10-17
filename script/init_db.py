import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
import pymysql

# 1. Đọc thông tin kết nối từ file .env
env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("Đang kết nối tới MySQL Server...")

try:
    #  Kết nối tới MySQL Server
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4',
        autocommit=True
    )

    # Đọc nội dung file init_db.sql
    sql_file_path = Path(__file__).resolve().parent / "database" / "init_db.sql"
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Thực thi lệnh trong file init_db.sql
    with connection.cursor() as cursor:
        statements = sql_content.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)

        # Đảm bảo các cột mới nhất luôn tồn tại (auto-migration nếu DB đã được tạo từ trước)
        migrations = [
            "ALTER TABLE intern_management.truong_dai_hoc ADD COLUMN IF NOT EXISTS danh_sach_nganh TEXT NULL",
            "ALTER TABLE intern_management.ho_so_thuc_tap ADD COLUMN IF NOT EXISTS lop VARCHAR(50) NULL",
            "ALTER TABLE intern_management.ca_lam_viec ADD COLUMN IF NOT EXISTS ngay_dien_ra DATE NULL",
            "ALTER TABLE intern_management.ca_lam_viec ADD COLUMN IF NOT EXISTS chuyen_nganh VARCHAR(100) NULL",
            "ALTER TABLE intern_management.ca_lam_viec ADD COLUMN IF NOT EXISTS lop VARCHAR(50) NULL",
            "ALTER TABLE intern_management.ca_lam_viec ADD COLUMN IF NOT EXISTS ma_chuong_trinh INT NULL",
            "ALTER TABLE intern_management.phu_cap ADD COLUMN IF NOT EXISTS thang INT NULL",
            "ALTER TABLE intern_management.phu_cap ADD COLUMN IF NOT EXISTS nam INT NULL",
            "ALTER TABLE intern_management.phu_cap ADD COLUMN IF NOT EXISTS ngay_chi_tra DATE NULL",
            "ALTER TABLE intern_management.phu_cap ADD COLUMN IF NOT EXISTS trang_thai VARCHAR(50) DEFAULT 'ChuaChiTra'",
            "ALTER TABLE intern_management.phu_cap ADD COLUMN IF NOT EXISTS ghi_chu VARCHAR(255) NULL"
        ]
        for m in migrations:
            try:
                cursor.execute(m)
            except Exception:
                pass

    print("khởi tạo thành công")
    connection.close()

except Exception as e:
    print(f"Lỗi khi khởi tạo CSDL: {e}")
