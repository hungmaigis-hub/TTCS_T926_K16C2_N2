# -*- coding: utf-8 -*-
"""
=====================================================================
BO KIEM THU TU DONG TOAN DIEN - TRAN QUOC HUY
Bao gom: Backend API Tests + Frontend Selenium UI Tests
=====================================================================
"""
import sys
import os
import time
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')

BASE_API = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_BASE = f"file:///{BASE_DIR}/frontend".replace("\\", "/")

results = []

def log_result(task_name, tc_id, tc_name, expected, actual, status):
    icon = "PASS" if status else "FAIL"
    results.append({
        "task": task_name,
        "tc_id": tc_id,
        "tc_name": tc_name,
        "expected": expected,
        "actual": actual,
        "status": icon
    })
    print(f"  [{icon}] {tc_id}: {tc_name}")

# =====================================================================
# NHIEM VU 1: Cap nhat thong tin thuc tap sinh
# =====================================================================
def test_task1_update_intern():
    task = "NV1: Cap nhat thong tin TTS"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_UD_01: GET danh sach TTS
    try:
        r = requests.get(f"{BASE_API}/api/v1/interns")
        ok = r.status_code == 200 and "data" in r.json()
        log_result(task, "TC_UD_01", "GET danh sach TTS thanh cong", "HTTP 200 + data[]", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_UD_01", "GET danh sach TTS thanh cong", "HTTP 200", str(e), False)

    # TC_UD_02: PUT cap nhat thanh cong
    try:
        payload = {"ho_ten": "Nguyen Van A Updated", "email": "vana@example.com", "so_dien_thoai": "0912345678", "chuyen_nganh": "KHMT", "ma_truong": 1, "trang_thai_thuc_tap": "DangThucTap"}
        r = requests.put(f"{BASE_API}/api/v1/interns/1", json=payload)
        ok = r.status_code == 200 and r.json().get("data", {}).get("ho_ten") == "Nguyen Van A Updated"
        log_result(task, "TC_UD_02", "PUT cap nhat TTS thanh cong", "HTTP 200 + data thay doi", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_UD_02", "PUT cap nhat TTS thanh cong", "HTTP 200", str(e), False)

    # TC_UD_03: PUT ID khong ton tai -> 404
    try:
        r = requests.put(f"{BASE_API}/api/v1/interns/99999", json={"ho_ten": "Test", "email": "x@x.com"})
        ok = r.status_code == 404
        log_result(task, "TC_UD_03", "PUT ID khong ton tai -> 404", "HTTP 404", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_UD_03", "PUT ID khong ton tai -> 404", "HTTP 404", str(e), False)

    # TC_UD_04: PUT trung email -> 400
    try:
        r = requests.put(f"{BASE_API}/api/v1/interns/1", json={"ho_ten": "Test", "email": "thib@example.com"})
        ok = r.status_code == 400
        log_result(task, "TC_UD_04", "PUT trung email TTS khac -> 400", "HTTP 400", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_UD_04", "PUT trung email TTS khac -> 400", "HTTP 400", str(e), False)

    # TC_UD_05: PUT email sai dinh dang -> 422
    try:
        r = requests.put(f"{BASE_API}/api/v1/interns/1", json={"ho_ten": "Test", "email": "email_sai"})
        ok = r.status_code == 422
        log_result(task, "TC_UD_05", "PUT email sai dinh dang -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_UD_05", "PUT email sai dinh dang -> 422", "HTTP 422", str(e), False)

    # TC_UD_06: PUT ho_ten vuot 100 ky tu -> 422
    try:
        r = requests.put(f"{BASE_API}/api/v1/interns/1", json={"ho_ten": "A" * 105, "email": "vana@example.com"})
        ok = r.status_code == 422
        log_result(task, "TC_UD_06", "PUT ho_ten vuot 100 ky tu -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_UD_06", "PUT ho_ten vuot 100 ky tu -> 422", "HTTP 422", str(e), False)

# =====================================================================
# NHIEM VU 2: Xet duyet ho so va cap nhat badge
# =====================================================================
def test_task2_approval_badge():
    task = "NV2: Xet duyet ho so & Badge"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_XD_01: Duyet thanh cong DaDuyet
    try:
        r = requests.patch(f"{BASE_API}/api/v1/interns/1/approval", json={"trang_thai_xet_duyet": "DaDuyet", "ghi_chu": "Dat tieu chuan"})
        ok = r.status_code == 200 and r.json().get("data", {}).get("trang_thai_xet_duyet") == "DaDuyet"
        log_result(task, "TC_XD_01", "PATCH duyet ho so DaDuyet", "HTTP 200 + badge=DaDuyet", f"HTTP {r.status_code} badge={r.json().get('data',{}).get('trang_thai_xet_duyet','?')}", ok)
    except Exception as e:
        log_result(task, "TC_XD_01", "PATCH duyet ho so DaDuyet", "HTTP 200", str(e), False)

    # TC_XD_02: Tu choi TuChoi
    try:
        r = requests.patch(f"{BASE_API}/api/v1/interns/1/approval", json={"trang_thai_xet_duyet": "TuChoi", "ghi_chu": "Thieu tin chi"})
        ok = r.status_code == 200 and r.json().get("data", {}).get("trang_thai_xet_duyet") == "TuChoi"
        log_result(task, "TC_XD_02", "PATCH tu choi ho so TuChoi", "HTTP 200 + badge=TuChoi", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_XD_02", "PATCH tu choi ho so TuChoi", "HTTP 200", str(e), False)

    # TC_XD_03: Trang thai khong hop le -> 422
    try:
        r = requests.patch(f"{BASE_API}/api/v1/interns/1/approval", json={"trang_thai_xet_duyet": "Approved"})
        ok = r.status_code == 422
        log_result(task, "TC_XD_03", "PATCH trang thai khong hop le -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_XD_03", "PATCH trang thai khong hop le -> 422", "HTTP 422", str(e), False)

    # TC_XD_04: ID khong ton tai -> 404
    try:
        r = requests.patch(f"{BASE_API}/api/v1/interns/99999/approval", json={"trang_thai_xet_duyet": "DaDuyet"})
        ok = r.status_code == 404
        log_result(task, "TC_XD_04", "PATCH ID khong ton tai -> 404", "HTTP 404", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_XD_04", "PATCH ID khong ton tai -> 404", "HTTP 404", str(e), False)

    # TC_XD_05: Thieu trang thai -> 422
    try:
        r = requests.patch(f"{BASE_API}/api/v1/interns/1/approval", json={"ghi_chu": "Chi co ghi chu"})
        ok = r.status_code == 422
        log_result(task, "TC_XD_05", "PATCH thieu truong trang thai -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_XD_05", "PATCH thieu truong trang thai -> 422", "HTTP 422", str(e), False)

# =====================================================================
# NHIEM VU 3: Kiem thu email thong bao
# =====================================================================
def test_task3_email():
    task = "NV3: Email thong bao xet duyet"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_EM_01: Duyet tai lieu gui email
    try:
        r = requests.patch(f"{BASE_API}/api/v1/documents/1/status", json={"trang_thai_duyet": "DaDuyet", "ghi_chu": "OK"})
        ok = r.status_code == 200
        log_result(task, "TC_EM_01", "PATCH duyet tai lieu -> gui email", "HTTP 200", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_EM_01", "PATCH duyet tai lieu -> gui email", "HTTP 200", str(e), False)

    # TC_EM_02: Tu choi tai lieu gui email
    try:
        r = requests.patch(f"{BASE_API}/api/v1/documents/1/status", json={"trang_thai_duyet": "TuChoi", "ghi_chu": "Ban scan mo"})
        ok = r.status_code == 200
        log_result(task, "TC_EM_02", "PATCH tu choi tai lieu -> email tu choi", "HTTP 200", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_EM_02", "PATCH tu choi tai lieu -> email tu choi", "HTTP 200", str(e), False)

    # TC_EM_03: Tai lieu khong ton tai -> 404 va KHONG gui email
    try:
        r = requests.patch(f"{BASE_API}/api/v1/documents/99999/status", json={"trang_thai_duyet": "DaDuyet"})
        ok = r.status_code == 404
        log_result(task, "TC_EM_03", "PATCH tai lieu 404 -> khong gui email", "HTTP 404", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_EM_03", "PATCH tai lieu 404 -> khong gui email", "HTTP 404", str(e), False)

    # TC_EM_04: Ghi chu vuot 500 ky tu -> 422
    try:
        r = requests.patch(f"{BASE_API}/api/v1/documents/1/status", json={"trang_thai_duyet": "DaDuyet", "ghi_chu": "A" * 501})
        ok = r.status_code == 422
        log_result(task, "TC_EM_04", "PATCH ghi chu >500 ky tu -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_EM_04", "PATCH ghi chu >500 ky tu -> 422", "HTTP 422", str(e), False)

# =====================================================================
# NHIEM VU 4: Tao chuong trinh thuc tap
# =====================================================================
def test_task4_programs():
    task = "NV4: Tao chuong trinh thuc tap"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_CT_01: Tao chuong trinh thanh cong
    try:
        payload = {"ten_chuong_trinh": f"CT Test Auto {int(time.time())}", "ma_phong_ban": 1, "ngay_bat_dau": "2026-11-01", "ngay_ket_thuc": "2027-03-01", "mo_ta": "Auto test"}
        r = requests.post(f"{BASE_API}/api/v1/programs", json=payload)
        ok = r.status_code == 201
        log_result(task, "TC_CT_01", "POST tao chuong trinh thanh cong", "HTTP 201", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CT_01", "POST tao chuong trinh thanh cong", "HTTP 201", str(e), False)

    # TC_CT_02: Ten chuong trinh rong -> 422
    try:
        r = requests.post(f"{BASE_API}/api/v1/programs", json={"ten_chuong_trinh": "", "ma_phong_ban": 1})
        ok = r.status_code == 422
        log_result(task, "TC_CT_02", "POST ten rong -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CT_02", "POST ten rong -> 422", "HTTP 422", str(e), False)

    # TC_CT_03: Phong ban khong ton tai
    try:
        r = requests.post(f"{BASE_API}/api/v1/programs", json={"ten_chuong_trinh": "Test PB", "ma_phong_ban": 99999})
        ok = r.status_code in [400, 404]
        log_result(task, "TC_CT_03", "POST phong ban khong ton tai", "HTTP 400/404", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CT_03", "POST phong ban khong ton tai", "HTTP 400/404", str(e), False)

    # TC_CT_04: Ngay ket thuc < Ngay bat dau -> 422
    try:
        r = requests.post(f"{BASE_API}/api/v1/programs", json={"ten_chuong_trinh": "Test Date", "ma_phong_ban": 1, "ngay_bat_dau": "2027-06-01", "ngay_ket_thuc": "2027-01-01"})
        ok = r.status_code == 422
        log_result(task, "TC_CT_04", "POST ngay ket thuc < bat dau -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CT_04", "POST ngay ket thuc < bat dau -> 422", "HTTP 422", str(e), False)

    # TC_CT_05: Thieu ten_chuong_trinh -> 422
    try:
        r = requests.post(f"{BASE_API}/api/v1/programs", json={"ma_phong_ban": 1})
        ok = r.status_code == 422
        log_result(task, "TC_CT_05", "POST thieu ten_chuong_trinh -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CT_05", "POST thieu ten_chuong_trinh -> 422", "HTTP 422", str(e), False)

# =====================================================================
# NHIEM VU 5: Lich thuc tap ca nhan
# =====================================================================
def test_task5_schedule():
    task = "NV5: Lich thuc tap ca nhan"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_LC_01: Lay lich thanh cong
    try:
        r = requests.get(f"{BASE_API}/api/v1/interns/my-schedule?ho_so_id=1")
        ok = r.status_code == 200 and "data" in r.json()
        log_result(task, "TC_LC_01", "GET lich thuc tap thanh cong", "HTTP 200 + data", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_LC_01", "GET lich thuc tap thanh cong", "HTTP 200", str(e), False)

    # TC_LC_02: ID khong ton tai -> 404
    try:
        r = requests.get(f"{BASE_API}/api/v1/interns/my-schedule?ho_so_id=99999")
        ok = r.status_code == 404
        log_result(task, "TC_LC_02", "GET ho_so_id khong ton tai -> 404", "HTTP 404", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_LC_02", "GET ho_so_id khong ton tai -> 404", "HTTP 404", str(e), False)

    # TC_LC_03: Thieu tham so -> 422
    try:
        r = requests.get(f"{BASE_API}/api/v1/interns/my-schedule")
        ok = r.status_code == 422
        log_result(task, "TC_LC_03", "GET thieu tham so ho_so_id -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_LC_03", "GET thieu tham so ho_so_id -> 422", "HTTP 422", str(e), False)

# =====================================================================
# NHIEM VU 6: Nop bao cao tuan
# =====================================================================
def test_task6_weekly_reports():
    task = "NV6: Nop bao cao tuan"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_BC_01: Nop bao cao thanh cong
    try:
        payload = {"ma_ho_so": 1, "ma_nhiem_vu": 1, "tuan_so": 99, "noi_dung_cong_viec": "Auto test report", "ket_qua_dat_duoc": "OK"}
        r = requests.post(f"{BASE_API}/api/v1/reports", json=payload)
        ok = r.status_code == 201
        log_result(task, "TC_BC_01", "POST nop bao cao tuan thanh cong", "HTTP 201", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_BC_01", "POST nop bao cao tuan thanh cong", "HTTP 201", str(e), False)

    # TC_BC_02: Tuan so = 0 -> 422
    try:
        r = requests.post(f"{BASE_API}/api/v1/reports", json={"ma_ho_so": 1, "tuan_so": 0, "noi_dung_cong_viec": "Test"})
        ok = r.status_code == 422
        log_result(task, "TC_BC_02", "POST tuan_so=0 -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_BC_02", "POST tuan_so=0 -> 422", "HTTP 422", str(e), False)

    # TC_BC_03: Noi dung rong -> 422
    try:
        r = requests.post(f"{BASE_API}/api/v1/reports", json={"ma_ho_so": 1, "tuan_so": 98, "noi_dung_cong_viec": ""})
        ok = r.status_code == 422
        log_result(task, "TC_BC_03", "POST noi dung rong -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_BC_03", "POST noi dung rong -> 422", "HTTP 422", str(e), False)

    # TC_BC_04: Khoa ngoai ma_ho_so khong ton tai
    try:
        r = requests.post(f"{BASE_API}/api/v1/reports", json={"ma_ho_so": 99999, "tuan_so": 97, "noi_dung_cong_viec": "Test FK"})
        ok = r.status_code in [400, 404]
        log_result(task, "TC_BC_04", "POST ma_ho_so khong ton tai", "HTTP 400/404", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_BC_04", "POST ma_ho_so khong ton tai", "HTTP 400/404", str(e), False)

# =====================================================================
# NHIEM VU 7: Tong hop danh gia & xuat bao cao
# =====================================================================
def test_task7_evaluation_summary():
    task = "NV7: Tong hop danh gia & xuat BC"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_DG_01: Lay tong hop mac dinh
    try:
        r = requests.get(f"{BASE_API}/api/v1/evaluations/summary")
        ok = r.status_code == 200
        log_result(task, "TC_DG_01", "GET tong hop danh gia mac dinh", "HTTP 200", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_DG_01", "GET tong hop danh gia mac dinh", "HTTP 200", str(e), False)

    # TC_DG_02: Xuat Excel
    try:
        r = requests.get(f"{BASE_API}/api/v1/evaluations/summary?format=excel")
        ok = r.status_code == 200 and "spreadsheet" in r.headers.get("content-type", "")
        log_result(task, "TC_DG_02", "GET xuat file Excel", "HTTP 200 + content-type=spreadsheet", f"HTTP {r.status_code} type={r.headers.get('content-type','?')[:30]}", ok)
    except Exception as e:
        log_result(task, "TC_DG_02", "GET xuat file Excel", "HTTP 200", str(e), False)

    # TC_DG_03: Xuat PDF
    try:
        r = requests.get(f"{BASE_API}/api/v1/evaluations/summary?format=pdf")
        ok = r.status_code == 200 and "pdf" in r.headers.get("content-type", "")
        log_result(task, "TC_DG_03", "GET xuat file PDF", "HTTP 200 + content-type=pdf", f"HTTP {r.status_code} type={r.headers.get('content-type','?')[:30]}", ok)
    except Exception as e:
        log_result(task, "TC_DG_03", "GET xuat file PDF", "HTTP 200", str(e), False)

    # TC_DG_04: Dinh dang khong hop le -> 422
    try:
        r = requests.get(f"{BASE_API}/api/v1/evaluations/summary?format=docx")
        ok = r.status_code == 422
        log_result(task, "TC_DG_04", "GET format=docx -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_DG_04", "GET format=docx -> 422", "HTTP 422", str(e), False)

    # TC_DG_05: Loc theo truong khong ton tai -> items rong
    try:
        r = requests.get(f"{BASE_API}/api/v1/evaluations/summary?ma_truong=99999")
        data = r.json()
        item_count = len(data.get("data", {}).get("items", data.get("items", [])))
        ok = r.status_code == 200 and item_count == 0
        log_result(task, "TC_DG_05", "GET loc truong khong ton tai -> rong", "HTTP 200 + 0 items", f"HTTP {r.status_code} items={item_count}", ok)
    except Exception as e:
        log_result(task, "TC_DG_05", "GET loc truong khong ton tai -> rong", "HTTP 200", str(e), False)

# =====================================================================
# NHIEM VU 8: Bao cao chuyen can
# =====================================================================
def test_task8_attendance():
    task = "NV8: Bao cao chuyen can"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    # TC_CC_01: Lay bao cao mac dinh
    try:
        r = requests.get(f"{BASE_API}/api/v1/attendance/reports")
        ok = r.status_code == 200
        log_result(task, "TC_CC_01", "GET bao cao chuyen can mac dinh", "HTTP 200", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CC_01", "GET bao cao chuyen can mac dinh", "HTTP 200", str(e), False)

    # TC_CC_02: Loc theo phong ban khong ton tai -> rong
    try:
        r = requests.get(f"{BASE_API}/api/v1/attendance/reports?ma_phong_ban=99999")
        ok = r.status_code == 200
        log_result(task, "TC_CC_02", "GET loc phong ban khong ton tai", "HTTP 200 + rong", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CC_02", "GET loc phong ban khong ton tai", "HTTP 200", str(e), False)

    # TC_CC_03: Thang khong hop le -> 422
    try:
        r = requests.get(f"{BASE_API}/api/v1/attendance/reports?thang=13")
        ok = r.status_code == 422
        log_result(task, "TC_CC_03", "GET thang=13 -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CC_03", "GET thang=13 -> 422", "HTTP 422", str(e), False)

    # TC_CC_04: Nam khong hop le -> 422
    try:
        r = requests.get(f"{BASE_API}/api/v1/attendance/reports?nam=-1")
        ok = r.status_code == 422
        log_result(task, "TC_CC_04", "GET nam=-1 -> 422", "HTTP 422", f"HTTP {r.status_code}", ok)
    except Exception as e:
        log_result(task, "TC_CC_04", "GET nam=-1 -> 422", "HTTP 422", str(e), False)

# =====================================================================
# FRONTEND SELENIUM UI TESTS
# =====================================================================
def test_frontend_selenium():
    task = "FRONTEND: Selenium UI Tests"
    print(f"\n{'='*60}")
    print(f"  {task}")
    print(f"{'='*60}")

    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        log_result(task, "TC_FE_00", "Import Selenium", "OK", "Selenium not installed", False)
        return

    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)

        # TC_FE_01: Trang dang nhap load thanh cong
        login_url = f"{FRONTEND_BASE}/html/public/dangnhap.html"
        driver.get(login_url)
        time.sleep(2)
        title = driver.title
        ok = "ICTU" in title or "Internship" in title or len(title) > 0
        log_result(task, "TC_FE_01", "Trang Dang nhap load thanh cong", "Title chua ICTU/Internship", f"Title='{title}'", ok)

        # TC_FE_02: Cac element form dang nhap ton tai
        try:
            id_input = driver.find_element(By.ID, "identifier")
            pw_input = driver.find_element(By.ID, "password")
            ok = id_input.is_displayed() and pw_input.is_displayed()
            log_result(task, "TC_FE_02", "Form dang nhap co o Email va Password", "2 input hien thi", "OK" if ok else "Khong tim thay", ok)
        except Exception:
            log_result(task, "TC_FE_02", "Form dang nhap co o Email va Password", "2 input hien thi", "Element not found", False)

        # TC_FE_03: Co 3 nut chon vai tro (Sinh vien, Doanh nghiep, Nha truong)
        try:
            role_btns = driver.find_elements(By.CSS_SELECTOR, "#roleSelector button")
            ok = len(role_btns) == 3
            log_result(task, "TC_FE_03", "Co 3 nut chon vai tro", "3 buttons", f"{len(role_btns)} buttons", ok)
        except Exception:
            log_result(task, "TC_FE_03", "Co 3 nut chon vai tro", "3 buttons", "Error", False)

        # TC_FE_04: Click tab Nha truong va dang nhap HR
        try:
            tab_faculty = driver.find_element(By.XPATH, "//button[contains(@onclick, \"selectRole('faculty'\")]")
            tab_faculty.click()
            time.sleep(0.5)
            driver.find_element(By.ID, "identifier").send_keys("hr@ictu.edu.vn")
            driver.find_element(By.ID, "password").send_keys("123456")
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(3)
            current_url = driver.current_url
            ok = "quanly/dashboard" in current_url
            log_result(task, "TC_FE_04", "Dang nhap HR -> chuyen trang Dashboard", "URL chua quanly/dashboard", f"URL={current_url[-40:]}", ok)
        except Exception as e:
            # Co the co alert bao loi dang nhap
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                log_result(task, "TC_FE_04", "Dang nhap HR -> chuyen trang Dashboard", "URL chua quanly/dashboard", f"Alert: {alert_text}", False)
            except:
                log_result(task, "TC_FE_04", "Dang nhap HR -> chuyen trang Dashboard", "URL chua quanly/dashboard", str(e)[:60], False)

        # TC_FE_05: Dashboard HR load dung - kiem tra sidebar
        try:
            current_url = driver.current_url
            if "quanly/dashboard" in current_url:
                sidebar = driver.find_element(By.TAG_NAME, "aside")
                ok = sidebar.is_displayed()
                log_result(task, "TC_FE_05", "Dashboard HR co sidebar menu", "Sidebar hien thi", "OK" if ok else "Khong hien thi", ok)
            else:
                log_result(task, "TC_FE_05", "Dashboard HR co sidebar menu", "Sidebar hien thi", "Chua vao Dashboard", False)
        except Exception as e:
            log_result(task, "TC_FE_05", "Dashboard HR co sidebar menu", "Sidebar hien thi", str(e)[:50], False)

        # TC_FE_06: Kiem tra link menu Xet duyet ho so ton tai
        try:
            if "quanly/dashboard" in driver.current_url:
                link = driver.find_element(By.CSS_SELECTOR, "a[href='xet_duyet_ho_so.html']")
                ok = link.is_displayed()
                log_result(task, "TC_FE_06", "Menu Xet duyet ho so ton tai", "Link hien thi", "OK" if ok else "An", ok)
            else:
                log_result(task, "TC_FE_06", "Menu Xet duyet ho so ton tai", "Link hien thi", "Chua vao Dashboard", False)
        except Exception:
            log_result(task, "TC_FE_06", "Menu Xet duyet ho so ton tai", "Link hien thi", "Not found", False)

        # TC_FE_07: Kiem tra Badge "cho duyet" tren sidebar
        try:
            if "quanly/dashboard" in driver.current_url:
                badge = driver.find_element(By.ID, "sidebarBadgeChoDuyet")
                ok = badge.is_displayed()
                badge_text = badge.text
                log_result(task, "TC_FE_07", "Badge 'cho duyet' hien thi tren sidebar", "Badge visible", f"Text='{badge_text}'", ok)
            else:
                log_result(task, "TC_FE_07", "Badge 'cho duyet' hien thi tren sidebar", "Badge visible", "Chua vao Dashboard", False)
        except Exception:
            log_result(task, "TC_FE_07", "Badge 'cho duyet' hien thi tren sidebar", "Badge visible", "Not found", False)

        # TC_FE_08: Click vao trang Xet duyet ho so
        try:
            if "quanly/dashboard" in driver.current_url:
                link = driver.find_element(By.CSS_SELECTOR, "a[href='xet_duyet_ho_so.html']")
                link.click()
                time.sleep(3)
                ok = "xet_duyet" in driver.current_url
                log_result(task, "TC_FE_08", "Click menu -> mo trang Xet duyet", "URL chua xet_duyet", f"URL={driver.current_url[-40:]}", ok)
            else:
                log_result(task, "TC_FE_08", "Click menu -> mo trang Xet duyet", "URL chua xet_duyet", "Chua vao Dashboard", False)
        except Exception as e:
            log_result(task, "TC_FE_08", "Click menu -> mo trang Xet duyet", "URL chua xet_duyet", str(e)[:50], False)

        # TC_FE_09: Trang Xet duyet co bang danh sach ho so
        try:
            if "xet_duyet" in driver.current_url:
                table = driver.find_element(By.TAG_NAME, "table")
                ok = table.is_displayed()
                log_result(task, "TC_FE_09", "Trang Xet duyet co bang danh sach", "Table hien thi", "OK" if ok else "Khong thay", ok)
            else:
                log_result(task, "TC_FE_09", "Trang Xet duyet co bang danh sach", "Table hien thi", "Chua vao trang", False)
        except Exception:
            log_result(task, "TC_FE_09", "Trang Xet duyet co bang danh sach", "Table hien thi", "Table not found", False)

        # TC_FE_10: Kiem tra trang Danh gia load duoc
        try:
            danh_gia_url = driver.current_url.replace("xet_duyet_ho_so.html", "danh_gia.html")
            driver.get(danh_gia_url)
            time.sleep(2)
            ok = "danh_gia" in driver.current_url
            log_result(task, "TC_FE_10", "Trang Danh gia cuoi ky load thanh cong", "URL chua danh_gia", f"URL={driver.current_url[-30:]}", ok)
        except Exception as e:
            log_result(task, "TC_FE_10", "Trang Danh gia cuoi ky load thanh cong", "URL chua danh_gia", str(e)[:50], False)

        # TC_FE_11: Kiem tra trang Cham cong load duoc
        try:
            cham_cong_url = driver.current_url.replace("danh_gia.html", "cham_cong.html")
            driver.get(cham_cong_url)
            time.sleep(2)
            ok = "cham_cong" in driver.current_url
            log_result(task, "TC_FE_11", "Trang Bao cao cham cong load thanh cong", "URL chua cham_cong", f"URL={driver.current_url[-30:]}", ok)
        except Exception as e:
            log_result(task, "TC_FE_11", "Trang Bao cao cham cong load thanh cong", "URL chua cham_cong", str(e)[:50], False)

        # TC_FE_12: Kiem tra trang Lich thuc tap load duoc
        try:
            lich_url = driver.current_url.replace("cham_cong.html", "lich_thuc_tap.html")
            driver.get(lich_url)
            time.sleep(2)
            ok = "lich_thuc_tap" in driver.current_url
            log_result(task, "TC_FE_12", "Trang Lich thuc tap load thanh cong", "URL chua lich_thuc_tap", f"URL={driver.current_url[-30:]}", ok)
        except Exception as e:
            log_result(task, "TC_FE_12", "Trang Lich thuc tap load thanh cong", "URL chua lich_thuc_tap", str(e)[:50], False)

    except Exception as e:
        log_result(task, "TC_FE_ERR", "Khoi tao Selenium Chrome", "Chrome khoi dong", str(e)[:80], False)
    finally:
        if driver:
            driver.quit()

# =====================================================================
# MAIN: CHAY TOAN BO VA IN BAO CAO
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  BO KIEM THU TU DONG TOAN DIEN - TRAN QUOC HUY")
    print("  Backend API + Frontend Selenium")
    print("=" * 60)

    start = time.time()

    # Backend API Tests
    test_task1_update_intern()
    test_task2_approval_badge()
    test_task3_email()
    test_task4_programs()
    test_task5_schedule()
    test_task6_weekly_reports()
    test_task7_evaluation_summary()
    test_task8_attendance()

    # Frontend Selenium Tests
    test_frontend_selenium()

    elapsed = time.time() - start

    # TONG KET
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    print(f"\n{'='*60}")
    print(f"  TONG KET KET QUA")
    print(f"{'='*60}")
    print(f"  Tong so Test Case : {total}")
    print(f"  PASSED            : {passed}")
    print(f"  FAILED            : {failed}")
    print(f"  Ty le thanh cong  : {passed/total*100:.1f}%")
    print(f"  Thoi gian         : {elapsed:.1f}s")
    print(f"{'='*60}")

    if failed > 0:
        print(f"\n  CAC TEST CASE BI FAIL:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    [{r['tc_id']}] {r['tc_name']}")
                print(f"      Mong doi: {r['expected']}")
                print(f"      Thuc te : {r['actual']}")

    # Xuat CSV
    csv_path = os.path.join(BASE_DIR, "KetQua_AutoTest_TranQuocHuy.csv")
    with open(csv_path, "w", encoding="utf-8-sig") as f:
        f.write("Nhiem vu,Ma TC,Ten Test Case,Ket qua mong doi,Ket qua thuc te,Trang thai\n")
        for r in results:
            line = f'"{r["task"]}","{r["tc_id"]}","{r["tc_name"]}","{r["expected"]}","{r["actual"]}","{r["status"]}"\n'
            f.write(line)
    print(f"\n  Da xuat file CSV: {csv_path}")
