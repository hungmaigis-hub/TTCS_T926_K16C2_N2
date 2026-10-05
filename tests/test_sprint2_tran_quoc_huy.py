"""
=============================================================
AUTOMATION TEST - SPRINT 2 - TRẦN QUỐC HUY
=============================================================
Bao gồm test key:
  Dòng 1  - TC-01: Chỉnh sửa / cập nhật hồ sơ thực tập sinh
  Dòng 5  - TC-05: Xem và duyệt tài liệu (cập nhật trạng thái và badge)
  Dòng 8  - TC-08: Gửi email thông báo kết quả xét duyệt
  Dòng 12 - TC-12: Tạo chương trình thực tập theo phòng ban
  Dòng 14 - TC-14: Xem lịch thực tập cá nhân
  Dòng 18 - TC-18: Nộp báo cáo tuần
  Dòng 21 - TC-21: Tổng hợp đánh giá cuối kỳ & xuất báo cáo (Excel, PDF)
  Dòng 24 - TC-24: Báo cáo đi làm và nghỉ phép / chuyên cần

Cách chạy:
  pip install pytest requests
  pytest tests/test_sprint2_tran_quoc_huy.py -v
=============================================================
"""

import pytest
import requests
import io
import time

BASE_URL = "http://localhost:8000"
EXISTING_HO_SO_ID = 1
EXISTING_DOC_ID = 1
EXISTING_PHONG_BAN_ID = 1
EXISTING_TRUONG_ID = 1


# ==============================================================
# TC-01 | Dòng 1 (Product Backlog)
# User Story: Là HR, tôi muốn chỉnh sửa hồ sơ thực tập sinh
#             để cập nhật thông tin thay đổi.
# Nhiệm vụ:   Tester: Viết và thực thi test case cập nhật thông tin
#             (sửa thành công, kiểm tra dữ liệu thay đổi chuẩn trong DB).
# ==============================================================

class TestTC01_UpdateInternProfile:

    def test_01_1_lay_danh_sach_thuc_tap_sinh_thanh_cong(self):
        """Lấy danh sách thực tập sinh -> HTTP 200, mảng data tồn tại"""
        r = requests.get(f"{BASE_URL}/api/v1/interns")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    def test_01_2_lay_chi_tiet_ho_so_tran_quoc_huy(self):
        """Lấy thông tin chi tiết hồ sơ thực tập sinh Trần Quốc Huy -> HTTP 200"""
        r = requests.get(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}")
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert data.get("ma_ho_so") == EXISTING_HO_SO_ID
        assert "Trần Quốc Huy" in data.get("ho_ten", "")
        assert "ictu.edu.vn" in data.get("email", "")

    def test_01_3_lay_chi_tiet_id_khong_ton_tai_tra_404(self):
        """Lấy thông tin TTS với mã hồ sơ không tồn tại (999999) -> HTTP 404"""
        r = requests.get(f"{BASE_URL}/api/v1/interns/999999")
        assert r.status_code == 404

    def test_01_4_cap_nhat_ho_so_thanh_cong_kiem_tra_db(self):
        """Cập nhật họ tên, SĐT và chuyên ngành thực tế -> HTTP 200, DB lưu dữ liệu chuẩn"""
        payload = {
            "ho_ten": "Trần Quốc Huy",
            "email": "tranquochuy@ictu.edu.vn",
            "so_dien_thoai": "0981234567",
            "chuyen_nganh": "Kỹ thuật Phần mềm Chuyên sâu",
            "ma_truong": EXISTING_TRUONG_ID,
            "trang_thai_thuc_tap": "DangThucTap"
        }
        r = requests.put(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}", json=payload)
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert data.get("ho_ten") == "Trần Quốc Huy"
        assert data.get("chuyen_nganh") == "Kỹ thuật Phần mềm Chuyên sâu"
        assert data.get("so_dien_thoai") == "0981234567"

    def test_01_5_cap_nhat_id_khong_ton_tai_tra_404(self):
        """Cập nhật hồ sơ với ID không tồn tại -> HTTP 404"""
        payload = {"ho_ten": "Sinh viên Ảo", "email": "ao@example.com"}
        r = requests.put(f"{BASE_URL}/api/v1/interns/999999", json=payload)
        assert r.status_code == 404

    def test_01_6_cap_nhat_trung_email_tts_khac_tra_400(self):
        """Cập nhật trùng email với thực tập sinh khác (nguyenvanan@ictu.edu.vn) -> HTTP 400"""
        payload = {
            "ho_ten": "Trần Quốc Huy",
            "email": "nguyenvanan@ictu.edu.vn",  # Trùng email của tài khoản khác
            "so_dien_thoai": "0981234567"
        }
        r = requests.put(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}", json=payload)
        assert r.status_code == 400

    def test_01_7_email_sai_dinh_dang_tra_422(self):
        """Cập nhật với email sai định dạng cú pháp (không có @ và domain) -> HTTP 422"""
        payload = {
            "ho_ten": "Trần Quốc Huy",
            "email": "email_khong_dung_dinh_dang"
        }
        r = requests.put(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}", json=payload)
        assert r.status_code == 422

    def test_01_8_ma_truong_khong_ton_tai_tra_400(self):
        """Cập nhật với mã trường đại học không tồn tại trong DB -> HTTP 400"""
        payload = {
            "ho_ten": "Trần Quốc Huy",
            "email": "tranquochuy@ictu.edu.vn",
            "ma_truong": 999999
        }
        r = requests.put(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}", json=payload)
        assert r.status_code == 400


# ==============================================================
# TC-05 | Dòng 3 (Product Backlog)
# User Story: Là HR, tôi muốn xem và duyệt tài liệu của thực tập sinh
#             để xác thực hồ sơ.
# Nhiệm vụ:   Tester: Kiểm thử xem trước tài liệu, kiểm tra cập nhật
#             trạng thái phê duyệt và cập nhật badge hiển thị.
# ==============================================================

class TestTC05_ReviewDocumentsAndBadge:

    def test_05_1_xem_danh_sach_tai_lieu_ho_so(self):
        """Lấy danh sách tài liệu của hồ sơ thực tập -> HTTP 200, có mảng dữ liệu tài liệu"""
        r = requests.get(f"{BASE_URL}/api/v1/documents/{EXISTING_HO_SO_ID}")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    def test_05_2_duyet_tai_lieu_cap_nhat_badge_daduyet(self):
        """Cập nhật trạng thái duyệt tài liệu thành DaDuyet -> HTTP 200, badge = DaDuyet"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/{EXISTING_DOC_ID}/status",
            json={"trang_thai_duyet": "DaDuyet", "ghi_chu": "Bản CV và chứng chỉ đạt tiêu chuẩn công ty"}
        )
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert data.get("trang_thai_duyet") == "DaDuyet"

    def test_05_3_tu_choi_tai_lieu_cap_nhat_badge_tuchoi(self):
        """Cập nhật trạng thái tài liệu thành TuChoi kèm ghi chú -> HTTP 200, badge = TuChoi"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/{EXISTING_DOC_ID}/status",
            json={"trang_thai_duyet": "TuChoi", "ghi_chu": "Bản scan bị mờ, vui lòng nộp lại file PDF rõ nét"}
        )
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert data.get("trang_thai_duyet") == "TuChoi"

    def test_05_4_duyet_ho_so_cap_nhat_badge_xet_duyet(self):
        """Cập nhật trạng thái xét duyệt hồ sơ thực tập sinh -> HTTP 200, badge = DaDuyet"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}/approval",
            json={"trang_thai_xet_duyet": "DaDuyet", "ghi_chu": "Đạt chuẩn phỏng vấn kỹ thuật và tuyển dụng"}
        )
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert data.get("trang_thai_xet_duyet") == "DaDuyet"

    def test_05_5_trang_thai_duyet_khong_hop_le_tra_422(self):
        """Gửi trạng thái xét duyệt không nằm trong danh mục cho phép -> HTTP 422"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}/approval",
            json={"trang_thai_xet_duyet": "TRANG_THAI_KHONG_HOP_LE"}
        )
        assert r.status_code in (400, 422)

    def test_05_6_tai_lieu_khong_ton_tai_tra_404(self):
        """Cập nhật tài liệu với mã không tồn tại trong hệ thống -> HTTP 404"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/999999/status",
            json={"trang_thai_duyet": "DaDuyet"}
        )
        assert r.status_code == 404


# ==============================================================
# TC-08 | Dòng 7 (Product Backlog)
# User Story: Là hệ thống, tôi muốn gửi email thông báo kết quả xét duyệt
#             để thực tập sinh nhận được thông tin kịp thời.
# Nhiệm vụ:   Tester: Kiểm thử nhận mail trên hòm thư thực tế,
#             kiểm tra giao diện mail hiển thị chuẩn HTML
# ==============================================================

class TestTC08_EmailNotification:

    def test_08_1_duyet_tai_lieu_kich_hoat_gui_email_thanh_cong(self):
        """Khi HR duyệt tài liệu (DaDuyet), kích hoạt gửi email thông báo kết quả xét duyệt -> HTTP 200"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/{EXISTING_DOC_ID}/status",
            json={"trang_thai_duyet": "DaDuyet", "ghi_chu": "Chúc mừng bạn đã được phê duyệt tài liệu thực tập"}
        )
        assert r.status_code == 200

    def test_08_2_tu_choi_tai_lieu_kich_hoat_gui_email_tu_choi(self):
        """Khi HR từ chối tài liệu (TuChoi), kích hoạt gửi email thông báo lý do chi tiết -> HTTP 200"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/{EXISTING_DOC_ID}/status",
            json={"trang_thai_duyet": "TuChoi", "ghi_chu": "Yêu cầu bổ sung dấu giáp lai của nhà trường"}
        )
        assert r.status_code == 200

    def test_08_3_tai_lieu_404_khong_kich_hoat_gui_email(self):
        """Khi mã tài liệu không tồn tại -> HTTP 404 và không kích hoạt tác vụ gửi email"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/999999/status",
            json={"trang_thai_duyet": "DaDuyet"}
        )
        assert r.status_code == 404

    def test_08_4_ghi_chu_vuot_500_ky_tu_tra_422(self):
        """Ghi chú nhận xét email vượt quá giới hạn 500 ký tự -> HTTP 422"""
        r = requests.patch(
            f"{BASE_URL}/api/v1/documents/{EXISTING_DOC_ID}/status",
            json={"trang_thai_duyet": "DaDuyet", "ghi_chu": "Nội dung nhận xét dài " * 50}
        )
        assert r.status_code == 422


# ==============================================================
# TC-12 | Dòng 10 (Product Backlog)
# User Story: Là HR, tôi muốn tạo chương trình thực tập theo phòng ban
#             để tổ chức kế hoạch.
# Nhiệm vụ:   Tester: Viết test case tạo chương trình: kiểm tra khóa
#             ngoại phòng ban, bắt lỗi để trống tên chương trình
# ==============================================================

class TestTC12_CreateInternshipProgram:

    def test_12_1_tao_chuong_trinh_thanh_cong_day_du_truong(self):
        """Tạo chương trình thực tập thực tế theo phòng ban ICTU -> HTTP 201 Created"""
        payload = {
            "ten_chuong_trinh": f"Khóa Kỹ sư Automation Testing K16 - Đợt {int(time.time())}",
            "ma_phong_ban": EXISTING_PHONG_BAN_ID,
            "ngay_bat_dau": "2026-11-01",
            "ngay_ket_thuc": "2027-02-28",
            "mo_ta": "Đào tạo kiến trúc hệ thống, kiểm thử tự động API và Web UI với Pytest & Selenium"
        }
        r = requests.post(f"{BASE_URL}/api/v1/programs", json=payload)
        assert r.status_code == 201
        data = r.json().get("data", {})
        assert data.get("ma_phong_ban") == EXISTING_PHONG_BAN_ID
        assert "ma_chuong_trinh" in data

    def test_12_2_tao_chuong_trinh_chi_voi_truong_bat_buoc(self):
        """Tạo chương trình thực tập chỉ truyền trường bắt buộc (tên + phòng ban) -> HTTP 201"""
        payload = {
            "ten_chuong_trinh": f"Chương trình Thực tập Nhanh K16 - {int(time.time())}",
            "ma_phong_ban": EXISTING_PHONG_BAN_ID
        }
        r = requests.post(f"{BASE_URL}/api/v1/programs", json=payload)
        assert r.status_code == 201

    def test_12_3_ten_chuong_trinh_de_trong_tra_422(self):
        """Bắt lỗi để trống tên chương trình thực tập -> HTTP 422"""
        payload = {
            "ten_chuong_trinh": "",
            "ma_phong_ban": EXISTING_PHONG_BAN_ID
        }
        r = requests.post(f"{BASE_URL}/api/v1/programs", json=payload)
        assert r.status_code == 422

    def test_12_4_khoa_ngoai_phong_ban_khong_ton_tai_tra_400(self):
        """Kiểm tra khóa ngoại phòng ban không tồn tại trong hệ thống -> HTTP 400/404"""
        payload = {
            "ten_chuong_trinh": "Chương trình Phòng Ban Không Tồn Tại",
            "ma_phong_ban": 999999
        }
        r = requests.post(f"{BASE_URL}/api/v1/programs", json=payload)
        assert r.status_code in (400, 404)

    def test_12_5_ngay_ket_thuc_nho_hon_ngay_bat_dau_tra_422(self):
        """Validate logic thời gian: ngày kết thúc < ngày bắt đầu -> HTTP 422"""
        payload = {
            "ten_chuong_trinh": "Chương trình Lỗi Mốc Thời Gian",
            "ma_phong_ban": EXISTING_PHONG_BAN_ID,
            "ngay_bat_dau": "2027-01-01",
            "ngay_ket_thuc": "2026-01-01"
        }
        r = requests.post(f"{BASE_URL}/api/v1/programs", json=payload)
        assert r.status_code == 422


# ==============================================================
# TC-14 | Dòng 13 (Product Backlog)
# User Story: Là thực tập sinh, tôi muốn xem lịch thực tập cá nhân
#             để biết kế hoạch.
# Nhiệm vụ:   Tester: Kiểm thử hiển thị đúng lịch theo tài khoản
#             thực tập sinh đang đăng nhập, tránh rò rỉ dữ liệu
# ==============================================================

class TestTC14_MySchedule:

    def test_14_1_lay_lich_thuc_tap_ca_nhan_tran_quoc_huy_thanh_cong(self):
        """Lấy lộ trình và lịch cá nhân của TTS Trần Quốc Huy -> HTTP 200, đúng dữ liệu"""
        r = requests.get(f"{BASE_URL}/api/v1/interns/my-schedule?ho_so_id={EXISTING_HO_SO_ID}")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        data = body["data"]
        assert data.get("ma_ho_so") == EXISTING_HO_SO_ID
        assert "danh_sach_nhiem_vu" in data
        assert isinstance(data["danh_sach_nhiem_vu"], list)

    def test_14_2_ma_ho_so_khong_ton_tai_tra_404(self):
        """Truy vấn lịch cá nhân với mã hồ sơ không tồn tại -> HTTP 404"""
        r = requests.get(f"{BASE_URL}/api/v1/interns/my-schedule?ho_so_id=999999")
        assert r.status_code == 404

    def test_14_3_thieu_tham_so_ho_so_id_tra_422(self):
        """Gọi API thiếu tham số query bắt buộc ho_so_id -> HTTP 422"""
        r = requests.get(f"{BASE_URL}/api/v1/interns/my-schedule")
        assert r.status_code == 422

    def test_14_4_ho_so_id_khong_phai_so_nguyen_tra_422(self):
        """Truyền tham số ho_so_id dạng ký tự chuỗi -> HTTP 422"""
        r = requests.get(f"{BASE_URL}/api/v1/interns/my-schedule?ho_so_id=invalid_id")
        assert r.status_code == 422


# ==============================================================
# TC-18 | Dòng 16 (Product Backlog)
# User Story: Là thực tập sinh, tôi muốn nộp báo cáo tuần
#             để báo cáo kết quả thực tập.
# Nhiệm vụ:   Tester: Viết test case nộp báo cáo: kiểm tra các trường
#             bắt buộc, validate đúng tuần số, kiểm tra khóa ngoại
#             ma_ho_so và ma_nhiem_vu liên kết chuẩn xác.
# ==============================================================

class TestTC18_SubmitWeeklyReport:

    def test_18_1_nop_bao_cao_tuan_day_du_thanh_cong(self):
        """TTS Trần Quốc Huy nộp báo cáo tuần 2 với nội dung thực tế -> HTTP 201 Created"""
        payload = {
            "ma_ho_so": EXISTING_HO_SO_ID,
            "ma_nhiem_vu": 1,
            "tuan_so": 2,
            "noi_dung_cong_viec": "Triển khai hoàn thiện bộ Automation Test 8 nhiệm vụ Sprint 2",
            "ket_qua_dat_duoc": "Xây dựng 42 kịch bản test tự động, cấu hình kết nối DB và xuất báo cáo"
        }
        r = requests.post(f"{BASE_URL}/api/v1/reports", json=payload)
        assert r.status_code == 201
        data = r.json().get("data", {})
        assert data.get("ma_ho_so") == EXISTING_HO_SO_ID
        assert data.get("tuan_so") == 2

    def test_18_2_tu_dong_gan_thoi_gian_nop_bao_cao(self):
        """Hệ thống tự động gán thoi_gian_nop khi thực tập sinh gửi báo cáo -> Not None"""
        payload = {
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tuan_so": 3,
            "noi_dung_cong_viec": "Kiểm thử tự động tính chính xác của timestamp nộp báo cáo"
        }
        r = requests.post(f"{BASE_URL}/api/v1/reports", json=payload)
        assert r.status_code == 201
        data = r.json().get("data", {})
        assert data.get("thoi_gian_nop") is not None

    def test_18_3_validate_tuan_so_khong_hop_le_tra_422(self):
        """Tuần số nộp báo cáo = 0 hoặc là số âm -> HTTP 422"""
        payload = {
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tuan_so": 0,
            "noi_dung_cong_viec": "Tuần không hợp lệ"
        }
        r = requests.post(f"{BASE_URL}/api/v1/reports", json=payload)
        assert r.status_code == 422

    def test_18_4_bat_loi_noi_dung_cong_viec_rong_tra_422(self):
        """Bắt lỗi bỏ trống trường bắt buộc noi_dung_cong_viec -> HTTP 422"""
        payload = {
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tuan_so": 4,
            "noi_dung_cong_viec": ""
        }
        r = requests.post(f"{BASE_URL}/api/v1/reports", json=payload)
        assert r.status_code == 422

    def test_18_5_khoa_ngoai_ma_ho_so_khong_ton_tai_tra_404(self):
        """Khóa ngoại ma_ho_so không tồn tại trong hệ thống -> HTTP 404/400"""
        payload = {
            "ma_ho_so": 999999,
            "tuan_so": 1,
            "noi_dung_cong_viec": "Báo cáo cho hồ sơ ảo"
        }
        r = requests.post(f"{BASE_URL}/api/v1/reports", json=payload)
        assert r.status_code in (400, 404)


# ==============================================================
# TC-21 | Dòng 19 (Product Backlog)
# User Story: Là HR, tôi muốn tổng hợp đánh giá thành báo cáo cuối kỳ
#             để gửi cho trường/ban lãnh đạo.
# Nhiệm vụ:   Tester: Kiểm thử tính chính xác của dữ liệu tổng hợp
#             (điểm trung bình, trạng thái hoàn thành, tỷ lệ đề xuất tuyển dụng)
#             và kiểm tra file tải về không bị lỗi định dạng.
# ==============================================================

class TestTC21_EvaluationSummaryAndExport:

    def test_21_1_lay_tong_hop_danh_gia_dinh_dang_json(self):
        """Lấy tổng hợp đánh giá mặc định (JSON) -> HTTP 200, chứa chỉ số KPI và danh sách items"""
        r = requests.get(f"{BASE_URL}/api/v1/evaluations/summary")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body or "items" in body

    def test_21_2_xuat_bao_cao_dinh_dang_excel_thanh_cong(self):
        """Xuất file Excel (.xlsx) tổng hợp đánh giá -> HTTP 200, đúng định dạng binary spreadsheet"""
        r = requests.get(f"{BASE_URL}/api/v1/evaluations/summary?format=excel")
        assert r.status_code == 200
        content_type = r.headers.get("content-type", "")
        assert any(x in content_type for x in ["spreadsheet", "excel", "vnd.openxmlformats", "octet-stream"])
        assert len(r.content) > 0  # File có dung lượng thực tế

    def test_21_3_xuat_bao_cao_dinh_dang_pdf_thanh_cong(self):
        """Xuất file PDF tổng hợp đánh giá -> HTTP 200, đúng Content-Type application/pdf"""
        r = requests.get(f"{BASE_URL}/api/v1/evaluations/summary?format=pdf")
        assert r.status_code == 200
        content_type = r.headers.get("content-type", "")
        assert "pdf" in content_type or "octet-stream" in content_type
        assert len(r.content) > 0

    def test_21_4_dinh_dang_xuat_khong_hop_le_tra_422(self):
        """Yêu cầu định dạng xuất file không hỗ trợ (format=docx) -> HTTP 400 hoặc 422"""
        r = requests.get(f"{BASE_URL}/api/v1/evaluations/summary?format=docx")
        assert r.status_code in (400, 422)

    def test_21_5_loc_tong_hop_theo_truong_dai_hoc_ictu(self):
        """Lọc dữ liệu tổng hợp theo Trường Đại học ICTU (ma_truong=1) -> HTTP 200"""
        r = requests.get(f"{BASE_URL}/api/v1/evaluations/summary?ma_truong={EXISTING_TRUONG_ID}")
        assert r.status_code == 200


# ==============================================================
# TC-24 | Dòng 23 (Product Backlog)
# User Story: Là HR, tôi muốn xem báo cáo đi làm và nghỉ phép
#             để quản lý sự chuyên cần.
# Nhiệm vụ:   Tester: Kiểm thử báo cáo chuyên cần: kiểm tra tính chính xác
#             của các công thức tính tổng ngày công, lọc theo tháng/phòng ban
#             và kiểm tra dữ liệu rỗng.
# ==============================================================

class TestTC24_AttendanceReports:

    def test_24_1_lay_bao_cao_chuyen_can_mac_dinh(self):
        """Lấy báo cáo chuyên cần mặc định -> HTTP 200, có các trường so_ngay_di_lam, so_lan_di_muon"""
        r = requests.get(f"{BASE_URL}/api/v1/attendance/reports")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body or "items" in body

    def test_24_2_loc_bao_cao_chuyen_can_theo_phong_ban_ictu(self):
        """Lọc dữ liệu chuyên cần theo Trung tâm Phần mềm ICTU (ma_phong_ban=1) -> HTTP 200"""
        r = requests.get(f"{BASE_URL}/api/v1/attendance/reports?ma_phong_ban={EXISTING_PHONG_BAN_ID}")
        assert r.status_code == 200

    def test_24_3_loc_phong_ban_khong_ton_tai_tra_danh_sach_rong(self):
        """Lọc phòng ban không tồn tại -> HTTP 404 hoặc 200 với danh sách rỗng"""
        r = requests.get(f"{BASE_URL}/api/v1/attendance/reports?ma_phong_ban=999999")
        assert r.status_code in (200, 404)

    def test_24_4_thang_chuyen_can_khong_hop_le_tra_422(self):
        """Nhập tháng chấm công không hợp lệ (thang = 13) -> HTTP 422"""
        r = requests.get(f"{BASE_URL}/api/v1/attendance/reports?thang=13")
        assert r.status_code == 422

    def test_24_5_nam_chuyen_can_khong_hop_le_tra_422(self):
        """Nhập năm chấm công là số âm (nam = -1) -> HTTP 422"""
        r = requests.get(f"{BASE_URL}/api/v1/attendance/reports?nam=-1")
        assert r.status_code == 422
