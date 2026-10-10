import pytest
from fastapi.testclient import TestClient
from main import app
from database.session import SessionLocal
from database.models import HoSoThucTap, TruongDaiHoc, NguoiDung
from security import get_password_hash

client = TestClient(app)


def test_get_faculty_report_default_success():
    """Kiểm tra gọi API thống kê sinh viên theo trường và chuyên ngành mặc định thành công (HTTP 200 OK)"""
    response = client.get("/api/v1/reports/interns-by-faculty")
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["status_code"] == 200
    assert "Lấy báo cáo thống kê" in res_data["message"]
    assert "data" in res_data

    data = res_data["data"]
    summary = data["summary"]
    assert summary["tong_sinh_vien"] == 2
    assert summary["tong_so_truong"] == 2
    assert summary["tong_so_chuyen_nganh"] == 2
    assert summary["truong_nhieu_sinh_vien_nhat"] is not None
    assert summary["chuyen_nganh_nhieu_sinh_vien_nhat"] is not None

    # Kiểm tra danh sách thống kê theo trường
    by_univ = data["thong_ke_theo_truong"]
    assert len(by_univ) == 2
    names = [u["ten_truong"] for u in by_univ]
    assert "Đại học Thái Nguyên" in names
    assert "Đại học Bách Khoa Hà Nội" in names

    # Kiểm tra danh sách thống kê theo chuyên ngành
    by_maj = data["thong_ke_theo_chuyen_nganh"]
    assert len(by_maj) == 2
    majors = [m["chuyen_nganh"] for m in by_maj]
    assert "Công nghệ thông tin" in majors
    assert "Khoa học máy tính" in majors

    # Kiểm tra chi tiết gom nhóm hai chiều
    details = data["chi_tiet"]
    assert len(details) == 2
    for item in details:
        assert item["so_luong"] == 1
        assert item["ty_le_phan_tram"] == 50.0


def test_get_faculty_report_filter_by_ma_truong_success():
    """Kiểm tra lọc theo ma_truong hợp lệ -> chỉ trả về dữ liệu của trường đó"""
    response = client.get("/api/v1/reports/interns-by-faculty?ma_truong=1")
    assert response.status_code == 200
    res_data = response.json()
    data = res_data["data"]

    assert data["summary"]["tong_sinh_vien"] == 1
    assert data["summary"]["tong_so_truong"] == 1
    assert data["summary"]["truong_nhieu_sinh_vien_nhat"] == "Đại học Thái Nguyên"

    assert len(data["thong_ke_theo_truong"]) == 1
    assert data["thong_ke_theo_truong"][0]["ma_truong"] == 1
    assert data["thong_ke_theo_truong"][0]["ten_truong"] == "Đại học Thái Nguyên"
    assert data["thong_ke_theo_truong"][0]["tong_sinh_vien"] == 1


def test_get_faculty_report_filter_by_ma_truong_not_found():
    """Kiểm tra truyền ma_truong không tồn tại -> HTTP 404"""
    response = client.get("/api/v1/reports/interns-by-faculty?ma_truong=99999")
    assert response.status_code == 404
    assert "Trường đại học không tồn tại" in response.json()["detail"]


def test_get_faculty_report_filter_by_ma_truong_invalid_value():
    """Kiểm tra truyền ma_truong <= 0 hoặc sai kiểu -> HTTP 422"""
    assert client.get("/api/v1/reports/interns-by-faculty?ma_truong=0").status_code == 422
    assert client.get("/api/v1/reports/interns-by-faculty?ma_truong=-3").status_code == 422
    assert client.get("/api/v1/reports/interns-by-faculty?ma_truong=abc").status_code == 422


def test_get_faculty_report_filter_by_ten_truong():
    """Kiểm tra tìm kiếm theo từ khóa tên trường đại học"""
    response = client.get("/api/v1/reports/interns-by-faculty?ten_truong=Bách+Khoa")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["summary"]["tong_sinh_vien"] == 1
    assert data["thong_ke_theo_truong"][0]["ten_truong"] == "Đại học Bách Khoa Hà Nội"

    # Tìm trường không tồn tại -> trả về rỗng 200 OK
    res_empty = client.get("/api/v1/reports/interns-by-faculty?ten_truong=Trường+Chưa+Từng+Có")
    assert res_empty.status_code == 200
    data_empty = res_empty.json()["data"]
    assert data_empty["summary"]["tong_sinh_vien"] == 0
    assert len(data_empty["thong_ke_theo_truong"]) == 0
    assert len(data_empty["chi_tiet"]) == 0


def test_get_faculty_report_filter_by_chuyen_nganh():
    """Kiểm tra tìm kiếm / lọc theo tên chuyên ngành đào tạo"""
    response = client.get("/api/v1/reports/interns-by-faculty?chuyen_nganh=Khoa+học+máy+tính")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["summary"]["tong_sinh_vien"] == 1
    assert data["thong_ke_theo_chuyen_nganh"][0]["chuyen_nganh"] == "Khoa học máy tính"
    assert data["chi_tiet"][0]["chuyen_nganh"] == "Khoa học máy tính"


def test_get_faculty_report_filter_by_ma_chuong_trinh_success():
    """Kiểm tra lọc theo ma_chuong_trinh hợp lệ"""
    response = client.get("/api/v1/reports/interns-by-faculty?ma_chuong_trinh=1")
    assert response.status_code == 200
    assert response.json()["data"]["summary"]["tong_sinh_vien"] == 2


def test_get_faculty_report_filter_by_ma_chuong_trinh_not_found():
    """Kiểm tra truyền ma_chuong_trinh không tồn tại -> HTTP 404"""
    response = client.get("/api/v1/reports/interns-by-faculty?ma_chuong_trinh=99999")
    assert response.status_code == 404
    assert "Chương trình thực tập không tồn tại" in response.json()["detail"]


def test_get_faculty_report_filter_by_ma_chuong_trinh_invalid():
    """Kiểm tra truyền ma_chuong_trinh <= 0 -> HTTP 422"""
    assert client.get("/api/v1/reports/interns-by-faculty?ma_chuong_trinh=0").status_code == 422


def test_get_faculty_report_filter_by_trang_thai_xet_duyet():
    """Kiểm tra lọc theo trạng thái xét duyệt hợp lệ và không hợp lệ"""
    # DaDuyet: 2 hồ sơ
    resp_da_duyet = client.get("/api/v1/reports/interns-by-faculty?trang_thai_xet_duyet=DaDuyet")
    assert resp_da_duyet.status_code == 200
    assert resp_da_duyet.json()["data"]["summary"]["tong_sinh_vien"] == 2

    # ChoDuyet: 0 hồ sơ
    resp_cho_duyet = client.get("/api/v1/reports/interns-by-faculty?trang_thai_xet_duyet=ChoDuyet")
    assert resp_cho_duyet.status_code == 200
    assert resp_cho_duyet.json()["data"]["summary"]["tong_sinh_vien"] == 0

    # Trạng thái không hợp lệ -> HTTP 400
    resp_invalid = client.get("/api/v1/reports/interns-by-faculty?trang_thai_xet_duyet=SaiTrangThai")
    assert resp_invalid.status_code == 400
    assert "Trạng thái xét duyệt không hợp lệ" in resp_invalid.json()["detail"]


def test_get_faculty_report_filter_by_trang_thai_thuc_tap():
    """Kiểm tra lọc theo trạng thái thực tập hợp lệ và không hợp lệ"""
    # ChuaThucTap: 1 hồ sơ
    resp_chua = client.get("/api/v1/reports/interns-by-faculty?trang_thai_thuc_tap=ChuaThucTap")
    assert resp_chua.status_code == 200
    assert resp_chua.json()["data"]["summary"]["tong_sinh_vien"] == 1

    # DangThucTap: 1 hồ sơ
    resp_dang = client.get("/api/v1/reports/interns-by-faculty?trang_thai_thuc_tap=DangThucTap")
    assert resp_dang.status_code == 200
    assert resp_dang.json()["data"]["summary"]["tong_sinh_vien"] == 1

    # Trạng thái không hợp lệ -> HTTP 400
    resp_invalid = client.get("/api/v1/reports/interns-by-faculty?trang_thai_thuc_tap=KhongDungTrangThai")
    assert resp_invalid.status_code == 400
    assert "Trạng thái thực tập không hợp lệ" in resp_invalid.json()["detail"]


def test_get_faculty_report_multi_student_aggregation():
    """Kiểm tra gom nhóm hai chiều với nhiều sinh viên trên cùng trường và tính tỷ lệ % chính xác"""
    from tests.conftest import TestSessionLocal
    db = TestSessionLocal()
    try:
        # Thêm 2 người dùng và 2 hồ sơ mới vào trường Thái Nguyên (ma_truong=1)
        pass_hash = get_password_hash("123456")
        u4 = NguoiDung(ma_nguoi_dung=4, ma_phong_ban=1, ho_ten="Lê Văn C", email="vanc@example.com", mat_khau_hash=pass_hash, vai_tro="ThucTapSinh")
        u5 = NguoiDung(ma_nguoi_dung=5, ma_phong_ban=1, ho_ten="Hoàng Thị D", email="thid@example.com", mat_khau_hash=pass_hash, vai_tro="ThucTapSinh")
        db.add_all([u4, u5])
        db.flush()

        # u4 học Công nghệ thông tin (ma_truong=1) -> Thái Nguyên có 2 sinh viên CNTT
        # u5 học An toàn thông tin (ma_truong=1) -> Thái Nguyên có 1 sinh viên ATTT
        hs3 = HoSoThucTap(ma_ho_so=3, ma_nguoi_dung=4, ma_truong=1, ma_chuong_trinh=1, chuyen_nganh="Công nghệ thông tin", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="DangThucTap")
        hs4 = HoSoThucTap(ma_ho_so=4, ma_nguoi_dung=5, ma_truong=1, ma_chuong_trinh=1, chuyen_nganh="An toàn thông tin", trang_thai_xet_duyet="DaDuyet", trang_thai_thuc_tap="DangThucTap")
        db.add_all([hs3, hs4])
        db.commit()

        # Gọi API kiểm tra
        response = client.get("/api/v1/reports/interns-by-faculty")
        assert response.status_code == 200
        data = response.json()["data"]

        # Tổng cộng: 4 sinh viên (hs1, hs2, hs3, hs4)
        assert data["summary"]["tong_sinh_vien"] == 4
        assert data["summary"]["tong_so_truong"] == 2
        assert data["summary"]["tong_so_chuyen_nganh"] == 3
        assert data["summary"]["truong_nhieu_sinh_vien_nhat"] == "Đại học Thái Nguyên"
        assert data["summary"]["chuyen_nganh_nhieu_sinh_vien_nhat"] == "Công nghệ thông tin"

        # ĐH Thái Nguyên có 3 sinh viên: 2 CNTT (66.67%), 1 ATTT (33.33%)
        tn_stat = next((u for u in data["thong_ke_theo_truong"] if u["ma_truong"] == 1), None)
        assert tn_stat is not None
        assert tn_stat["tong_sinh_vien"] == 3
        cntt = next((m for m in tn_stat["danh_sach_chuyen_nganh"] if m["chuyen_nganh"] == "Công nghệ thông tin"), None)
        attt = next((m for m in tn_stat["danh_sach_chuyen_nganh"] if m["chuyen_nganh"] == "An toàn thông tin"), None)
        assert cntt["so_luong"] == 2
        assert cntt["ty_le_phan_tram"] == 66.67
        assert attt["so_luong"] == 1
        assert attt["ty_le_phan_tram"] == 33.33

        # Chi tiết chi_tiet: CNTT Thái Nguyên (2 SV, 50.0%)
        dt_cntt = next((d for d in data["chi_tiet"] if d["ma_truong"] == 1 and d["chuyen_nganh"] == "Công nghệ thông tin"), None)
        assert dt_cntt is not None
        assert dt_cntt["so_luong"] == 2
        assert dt_cntt["ty_le_phan_tram"] == 50.0

    finally:
        db.close()


def test_get_faculty_report_empty_state():
    """Kiểm tra khi bảng hồ sơ không có dữ liệu khớp -> trả về 200 với các chỉ số 0 và None"""
    # Lọc trạng thái xét duyệt "TuChoi" mà hệ thống không có hồ sơ nào bị từ chối
    response = client.get("/api/v1/reports/interns-by-faculty?trang_thai_xet_duyet=TuChoi")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status_code"] == 200
    summary = res_data["data"]["summary"]
    assert summary["tong_sinh_vien"] == 0
    assert summary["tong_so_truong"] == 0
    assert summary["tong_so_chuyen_nganh"] == 0
    assert summary["truong_nhieu_sinh_vien_nhat"] is None
    assert summary["chuyen_nganh_nhieu_sinh_vien_nhat"] is None
    assert res_data["data"]["thong_ke_theo_truong"] == []
    assert res_data["data"]["thong_ke_theo_chuyen_nganh"] == []
    assert res_data["data"]["chi_tiet"] == []
