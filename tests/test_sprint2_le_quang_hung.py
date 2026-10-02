"""
=============================================================
AUTOMATION TEST - SPRINT 2 - LÊ QUANG HƯNG
=============================================================
Bao gồm test key:
  Dòng 3  - TC-03: Lọc/tìm kiếm thực tập sinh theo nhiều tiêu chí
  Dòng 6  - TC-06: Phê duyệt / từ chối hồ sơ (gửi email thông báo)
  Dòng 11 - TC-11: Upload file hợp đồng / tài liệu, kiểm tra FK ma_ho_so
  Dòng 17 - TC-17: Xác nhận ký hợp đồng điện tử
  Dòng 22 - TC-22: Phân công nhiệm vụ cho thực tập sinh
  Dòng 30 - TC-30: Mentor nộp / xem báo cáo tuần

Cách chạy:
  pip install pytest requests
  pytest tests/test_sprint2_le_quang_hung.py -v
=============================================================
"""

import pytest
import requests
import io

BASE_URL = "http://localhost:8000"
EXISTING_HO_SO_ID = 1
EXISTING_HOP_DONG_ID = 1


# ==============================================================
# TC-03 | Dòng 3
# User Story: Là HR, tôi muốn tìm kiếm và lọc thực tập sinh
#             theo trường/ngành để dễ dàng quản lý
# ==============================================================

class TestTC03_FilterInterns:

    def test_03_1_get_all_interns_no_filter(self):
        """Lấy toàn bộ danh sách, không có filter → status 200"""
        r = requests.get(f"{BASE_URL}/api/v1/interns")
        assert r.status_code == 200
        body = r.json()
        assert body["status_code"] == 200
        assert isinstance(body["data"], list)

    def test_03_2_filter_by_da_duyet(self):
        """Lọc theo trang_thai_xet_duyet = DaDuyet"""
        r = requests.get(f"{BASE_URL}/api/v1/interns", params={"trang_thai_xet_duyet": "DaDuyet"})
        assert r.status_code == 200
        for item in r.json()["data"]:
            assert item["trang_thai_xet_duyet"] == "DaDuyet"

    def test_03_3_filter_by_cho_duyet(self):
        """Lọc theo trang_thai_xet_duyet = ChoDuyet"""
        r = requests.get(f"{BASE_URL}/api/v1/interns", params={"trang_thai_xet_duyet": "ChoDuyet"})
        assert r.status_code == 200
        for item in r.json()["data"]:
            assert item["trang_thai_xet_duyet"] == "ChoDuyet"

    def test_03_4_filter_by_trang_thai_thuc_tap(self):
        """Lọc theo trang_thai_thuc_tap = DangThucTap"""
        r = requests.get(f"{BASE_URL}/api/v1/interns", params={"trang_thai_thuc_tap": "DangThucTap"})
        assert r.status_code == 200
        for item in r.json()["data"]:
            assert item["trang_thai_thuc_tap"] == "DangThucTap"

    def test_03_5_filter_ket_hop_hai_tieu_chi(self):
        """Lọc kết hợp 2 tiêu chí cùng lúc"""
        r = requests.get(f"{BASE_URL}/api/v1/interns", params={
            "trang_thai_xet_duyet": "DaDuyet",
            "trang_thai_thuc_tap": "DangThucTap"
        })
        assert r.status_code == 200
        for item in r.json()["data"]:
            assert item["trang_thai_xet_duyet"] == "DaDuyet"
            assert item["trang_thai_thuc_tap"] == "DangThucTap"

    def test_03_6_filter_gia_tri_khong_ton_tai_tra_rong(self):
        """Lọc với giá trị không tồn tại → danh sách rỗng (không lỗi 500)"""
        r = requests.get(f"{BASE_URL}/api/v1/interns", params={"trang_thai_xet_duyet": "KHONG_TON_TAI"})
        assert r.status_code == 200
        assert r.json()["data"] == []


# ==============================================================
# TC-06 | Dòng 6
# User Story: Là HR, tôi muốn phê duyệt / từ chối hồ sơ
#             và gửi email thông báo cho thực tập sinh
# ==============================================================

class TestTC06_ApprovalStatus:

    def test_06_1_duyet_ho_so_thanh_cong(self):
        """Duyệt hồ sơ hợp lệ → 200, trang_thai = DaDuyet"""
        r = requests.patch(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}/approval",
            json={"trang_thai_xet_duyet": "DaDuyet", "ghi_chu": "Hồ sơ đầy đủ"})
        assert r.status_code == 200
        assert r.json()["data"]["trang_thai_xet_duyet"] == "DaDuyet"

    def test_06_2_tu_choi_ho_so(self):
        """Từ chối hồ sơ → 200, trang_thai = TuChoi"""
        r = requests.patch(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}/approval",
            json={"trang_thai_xet_duyet": "TuChoi", "ghi_chu": "Thiếu giấy tờ"})
        assert r.status_code == 200
        assert r.json()["data"]["trang_thai_xet_duyet"] == "TuChoi"

    def test_06_3_id_khong_ton_tai_tra_ve_404(self):
        """ID hồ sơ không tồn tại → 404"""
        r = requests.patch(f"{BASE_URL}/api/v1/interns/999999/approval",
            json={"trang_thai_xet_duyet": "DaDuyet"})
        assert r.status_code == 404

    def test_06_4_trang_thai_khong_hop_le_tra_ve_422(self):
        """Trạng thái không hợp lệ → 400 hoặc 422"""
        r = requests.patch(f"{BASE_URL}/api/v1/interns/{EXISTING_HO_SO_ID}/approval",
            json={"trang_thai_xet_duyet": "INVALID_STATUS"})
        assert r.status_code in (400, 422)


# ==============================================================
# TC-11 | Dòng 11
# User Story: Là HR, tôi muốn tải lên hợp đồng / tài liệu
#             (kiểm tra FK ma_ho_so, định dạng file)
# ==============================================================

class TestTC11_UploadDocument:

    def test_11_1_upload_pdf_hop_le(self):
        """Upload PDF hợp lệ → 201 Created"""
        files = {"file": ("hop_dong.pdf", io.BytesIO(b"%PDF fake content"), "application/pdf")}
        data = {"ma_ho_so": EXISTING_HO_SO_ID, "loai_tai_lieu": "HopDong"}
        r = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files, data=data)
        assert r.status_code == 201

    def test_11_2_ma_ho_so_khong_ton_tai_tra_404(self):
        """Upload với ma_ho_so không tồn tại → 404 (FK fail)"""
        files = {"file": ("test.pdf", io.BytesIO(b"%PDF fake"), "application/pdf")}
        data = {"ma_ho_so": 999999, "loai_tai_lieu": "HopDong"}
        r = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files, data=data)
        assert r.status_code == 404

    def test_11_3_dinh_dang_khong_cho_phep_tra_400(self):
        """Upload file .exe → 400 (định dạng không hỗ trợ)"""
        files = {"file": ("virus.exe", io.BytesIO(b"MZ fake exe"), "application/octet-stream")}
        data = {"ma_ho_so": EXISTING_HO_SO_ID, "loai_tai_lieu": "HopDong"}
        r = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files, data=data)
        assert r.status_code == 400

    def test_11_4_lay_danh_sach_tai_lieu_cua_ho_so(self):
        """Lấy danh sách tài liệu của hồ sơ → 200"""
        r = requests.get(f"{BASE_URL}/api/v1/documents/{EXISTING_HO_SO_ID}")
        assert r.status_code == 200

    def test_11_5_cap_nhat_trang_thai_tai_lieu(self):
        """Cập nhật trạng thái tài liệu → 200"""
        r = requests.get(f"{BASE_URL}/api/v1/documents/{EXISTING_HO_SO_ID}")
        docs = r.json()
        items = docs if isinstance(docs, list) else docs.get("data", [])
        if not items:
            pytest.skip("Không có tài liệu để test")
        doc_id = items[0].get("ma_tai_lieu") or items[0].get("id")
        r2 = requests.patch(f"{BASE_URL}/api/v1/documents/{doc_id}/status",
            json={"trang_thai_duyet": "DaDuyet"})  # field đúng: trang_thai_duyet
        assert r2.status_code == 200


# ==============================================================
# TC-17 | Dòng 17
# User Story: Là HR/thực tập sinh, xác nhận ký hợp đồng điện tử
#             → kích hoạt trạng thái DangThucTap
# ==============================================================

class TestTC17_ConfirmContract:

    def test_17_1_xac_nhan_hop_dong_thanh_cong(self):
        """Xác nhận hợp đồng → 200, trang_thai = DaXacNhan"""
        r = requests.patch(f"{BASE_URL}/api/v1/contracts/{EXISTING_HOP_DONG_ID}/confirm",
            json={"trang_thai": "DaXacNhan", "ngay_ky": "2026-10-01"})
        assert r.status_code == 200
        assert r.json()["data"]["trang_thai"] == "DaXacNhan"

    def test_17_2_id_khong_ton_tai_tra_404(self):
        """ID hợp đồng không tồn tại → 404"""
        r = requests.patch(f"{BASE_URL}/api/v1/contracts/999999/confirm", json={})
        assert r.status_code == 404

    def test_17_3_body_rong_dung_gia_tri_mac_dinh(self):
        """Không gửi body → dùng giá trị mặc định (DaXacNhan + ngày hôm nay)"""
        r = requests.patch(f"{BASE_URL}/api/v1/contracts/{EXISTING_HOP_DONG_ID}/confirm", json={})
        assert r.status_code == 200

    def test_17_4_ho_so_duoc_cap_nhat_trang_thai_thuc_tap(self):
        """Sau xác nhận, hồ sơ liên kết phải có trang_thai_thuc_tap = DangThucTap"""
        r = requests.patch(f"{BASE_URL}/api/v1/contracts/{EXISTING_HOP_DONG_ID}/confirm",
            json={"trang_thai_thuc_tap": "DangThucTap"})
        assert r.status_code == 200
        ma_ho_so = r.json()["data"].get("ma_ho_so")
        if ma_ho_so:
            r2 = requests.get(f"{BASE_URL}/api/v1/interns/{ma_ho_so}")
            assert r2.status_code == 200
            assert r2.json()["data"]["trang_thai_thuc_tap"] == "DangThucTap"


# ==============================================================
# TC-22 | Dòng 22
# User Story: Phân công nhiệm vụ cho thực tập sinh
# ==============================================================

class TestTC22_AssignTask:

    def test_22_1_tao_nhiem_vu_hop_le(self):
        """Tạo nhiệm vụ hợp lệ → 201 Created"""
        r = requests.post(f"{BASE_URL}/api/v1/tasks", json={
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tieu_de": "Hoàn thành module login",  # field đúng: tieu_de
            "mo_ta": "Xây dựng form đăng nhập + JWT",
            "han_hoan_thanh": "2026-12-01",        # field đúng: han_hoan_thanh
            "trang_thai": "Chưa bắt đầu"
        })
        assert r.status_code == 201

    def test_22_2_ma_ho_so_khong_ton_tai_tra_loi(self):
        """ma_ho_so không tồn tại → 404"""
        r = requests.post(f"{BASE_URL}/api/v1/tasks", json={
            "ma_ho_so": 999999,
            "tieu_de": "Task test",
            "mo_ta": "Nội dung test",
            "han_hoan_thanh": "2026-12-01",
            "trang_thai": "Chưa bắt đầu"
        })
        assert r.status_code == 404

    def test_22_3_thieu_truong_bat_buoc_tra_422(self):
        """Thiếu tieu_de (bắt buộc) → 422"""
        r = requests.post(f"{BASE_URL}/api/v1/tasks", json={
            "ma_ho_so": EXISTING_HO_SO_ID,
            "mo_ta": "Không có tiêu đề"
        })
        assert r.status_code == 422

    def test_22_4_cap_nhat_tien_do_nhiem_vu(self):
        """Cập nhật tiến độ nhiệm vụ → 200"""
        r_create = requests.post(f"{BASE_URL}/api/v1/tasks", json={
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tieu_de": "Task for progress update",
            "mo_ta": "Nội dung",
            "han_hoan_thanh": "2026-12-31",
            "trang_thai": "Chưa bắt đầu"
        })
        if r_create.status_code != 201:
            pytest.skip("Không tạo được nhiệm vụ")
        body = r_create.json()
        task_id = body.get("ma_nhiem_vu") or body.get("data", {}).get("ma_nhiem_vu")
        if not task_id:
            pytest.skip("Không lấy được ma_nhiem_vu")
        r_upd = requests.patch(f"{BASE_URL}/api/v1/tasks/{task_id}/progress",
            json={"tien_do_phantram": 50})  # field đúng: tien_do_phantram (0-100%)
        assert r_upd.status_code == 200


# ==============================================================
# TC-30 | Dòng 30
# User Story: Là mentor, xem báo cáo tuần của thực tập sinh
# ==============================================================

class TestTC30_WeeklyReport:

    def test_30_1_nop_bao_cao_tuan_hop_le(self):
        """Nộp báo cáo tuần hợp lệ → 201 Created"""
        r = requests.post(f"{BASE_URL}/api/v1/reports", json={
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tuan_so": 1,
            "noi_dung_cong_viec": "Tuần 1: Nghiên cứu tài liệu",
            "ket_qua_dat_duoc": "Hiểu cấu trúc dự án"
        })
        assert r.status_code == 201
        assert r.json().get("status_code") == 201

    def test_30_2_ma_ho_so_khong_ton_tai_tra_404(self):
        """ma_ho_so không tồn tại → 404"""
        r = requests.post(f"{BASE_URL}/api/v1/reports", json={
            "ma_ho_so": 999999, "tuan_so": 1,
            "noi_dung_cong_viec": "Test", "ket_qua_dat_duoc": "Test"
        })
        assert r.status_code == 404

    def test_30_3_nhiem_vu_khong_thuoc_ho_so_tra_400(self):
        """ma_nhiem_vu không thuộc hồ sơ → 400"""
        r = requests.post(f"{BASE_URL}/api/v1/reports", json={
            "ma_ho_so": EXISTING_HO_SO_ID,
            "ma_nhiem_vu": 999999,
            "tuan_so": 2,
            "noi_dung_cong_viec": "Test", "ket_qua_dat_duoc": "Test"
        })
        assert r.status_code in (400, 404)

    def test_30_4_thieu_truong_bat_buoc_tra_422(self):
        """Thiếu noi_dung_cong_viec → 422"""
        r = requests.post(f"{BASE_URL}/api/v1/reports", json={
            "ma_ho_so": EXISTING_HO_SO_ID, "tuan_so": 3
        })
        assert r.status_code == 422

    def test_30_5_thoi_gian_nop_tu_dong_gan(self):
        """Sau khi nộp, thoi_gian_nop phải được gán tự động (not null)"""
        r = requests.post(f"{BASE_URL}/api/v1/reports", json={
            "ma_ho_so": EXISTING_HO_SO_ID,
            "tuan_so": 99,
            "noi_dung_cong_viec": "Kiểm tra tự động gán thời gian",
            "ket_qua_dat_duoc": "OK"
        })
        assert r.status_code == 201
        assert r.json()["data"]["thoi_gian_nop"] is not None
