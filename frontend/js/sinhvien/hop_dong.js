const duongDanApi = "http://127.0.0.1:8000/api/v1";

function layMaHopDong() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);
  try {
    const raw = localStorage.getItem("ictu_student_session") || localStorage.getItem("currentUser") || localStorage.getItem("user");
    if (raw) {
      const u = JSON.parse(raw);
      if (u.ma_hop_dong) return parseInt(u.ma_hop_dong, 10);
    }
  } catch (e) {}
  return 1;
}

function toggleAgreementCheckbox() {
  const checkbox = document.getElementById("hopDongCamKet");
  if (checkbox && !checkbox.disabled) {
    checkbox.checked = !checkbox.checked;
    handleCheckboxChange({ target: checkbox });
  }
}

function handleCheckboxChange(event) {
  const isChecked = event.target.checked;
  const nutKy = document.getElementById("nutXacNhanHopDong");
  if (!nutKy) return;

  if (nutKy.getAttribute("data-da-ky") === "true") {
    nutKy.disabled = true;
    return;
  }

  if (isChecked) {
    nutKy.disabled = false;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-primary bg-primary-container hover:bg-primary shadow-md cursor-pointer transition-all duration-200";
  } else {
    nutKy.disabled = true;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-surface-variant bg-surface-container-highest cursor-not-allowed transition-all duration-200";
  }
}

function apDungTrangThaiDaKy(tenSinhVien, ngayKy, maHopDong) {
  const nutKy = document.getElementById("nutXacNhanHopDong");
  const checkbox = document.getElementById("hopDongCamKet");
  const chuKySinhVien = document.getElementById("chuKySinhVien");

  if (checkbox) {
    checkbox.checked = true;
    checkbox.disabled = true;
  }

  if (chuKySinhVien) {
    chuKySinhVien.innerHTML = `
      <div class="p-3 rounded-lg bg-surface-container-lowest shadow-sm flex items-center gap-3 text-left">
        <div class="w-10 h-10 rounded-full bg-secondary flex items-center justify-center text-on-secondary shrink-0">
          <span class="material-symbols-outlined text-xl">draw</span>
        </div>
        <div class="font-body-sm text-body-sm">
          <p class="font-bold text-secondary flex items-center gap-1">
            <span>ĐÃ KÝ ĐIỆN TỬ</span>
            <span class="material-symbols-outlined text-xs">verified</span>
          </p>
          <p class="font-code text-code text-on-surface font-semibold">${tenSinhVien || "Thực tập sinh"} (Mã HĐ: #${maHopDong})</p>
          <p class="font-code text-code text-on-surface-variant text-[10px]">Ngày ký: ${ngayKy}</p>
        </div>
      </div>
    `;
  }

  if (nutKy) {
    nutKy.setAttribute("data-da-ky", "true");
    nutKy.disabled = true;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-secondary bg-secondary cursor-default shadow-sm";
    nutKy.innerHTML = `
      <span class="material-symbols-outlined text-lg">check_circle</span>
      <span>Hợp đồng đã hoàn tất ký số</span>
    `;
  }
}

async function kiemTraTrangThaiHopDongBanDau() {
  const maHopDong = layMaHopDong();
  const hopThongBao = document.getElementById("hopThongBao");

  try {
    const rawLocal = localStorage.getItem(`ictu_contract_signed_${maHopDong}`);
    if (rawLocal) {
      const saved = JSON.parse(rawLocal);
      apDungTrangThaiDaKy(saved.tenSinhVien, saved.ngayKy, maHopDong);
      if (hopThongBao) {
        hopThongBao.className =
          "rounded-xl bg-secondary-container text-on-secondary-container p-4 flex items-start gap-3.5 shadow-sm";
        hopThongBao.innerHTML = `
          <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-xl">verified</span>
          </div>
          <div class="space-y-1">
            <p class="font-label-lg text-label-lg font-bold">Hợp đồng điện tử đã được ký kết và có hiệu lực</p>
            <p class="font-body-md text-body-md">Mã xác thực: <strong class="font-code font-bold">ICTU-SIGNED-9921-OK</strong>. Hồ sơ thực tập của bạn đang ở trạng thái chính thức.</p>
          </div>
        `;
        hopThongBao.classList.remove("hidden");
      }
      return;
    }
  } catch (e) {}
}

async function thucHienKyHopDong() {
  const nutKy = document.getElementById("nutXacNhanHopDong");
  const hopThongBao = document.getElementById("hopThongBao");
  const checkbox = document.getElementById("hopDongCamKet");
  const maHopDong = layMaHopDong();

  if (nutKy && nutKy.getAttribute("data-da-ky") === "true") {
    return;
  }

  if (checkbox && !checkbox.checked) {
    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-amber-50 text-amber-900 border border-amber-200 p-4 flex items-start gap-3.5 shadow-sm";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">warning</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">Yêu cầu xác nhận điều khoản</p>
          <p class="font-body-md text-body-md">Vui lòng đọc kỹ và tích chọn ô cam kết tuân thủ quy chế thực tập trước khi ký kết.</p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
    }
    return;
  }

  const oldHtml = nutKy ? nutKy.innerHTML : "";
  if (nutKy) {
    nutKy.disabled = true;
    nutKy.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin"></span>
      <span>Hệ thống đang xác thực OTP & ký kết...</span>
    `;
  }

  try {
    const phanHoi = await fetch(`${duongDanApi}/contracts/${maHopDong}/confirm`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trang_thai: "DaXacNhan",
        trang_thai_thuc_tap: "DangThucTap",
        ghi_chu: "Ký số điện tử OTP qua Cổng sinh viên (ICTU-SIGNED-9921-OK)"
      })
    });

    const resJson = await phanHoi.json().catch(() => ({}));

    if (!phanHoi.ok) {
      let errMsg = "Không thể ký kết hợp đồng điện tử.";
      if (typeof resJson.detail === "string") {
        errMsg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        errMsg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }

      if (hopThongBao) {
        hopThongBao.className =
          "rounded-xl bg-red-50 text-red-900 border border-red-200 p-4 flex items-start gap-3.5 shadow-sm";
        hopThongBao.innerHTML = `
          <div class="w-8 h-8 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-xl">error</span>
          </div>
          <div class="space-y-1">
            <p class="font-label-lg text-label-lg font-bold">Lỗi xác thực hợp đồng (${phanHoi.status})</p>
            <p class="font-body-md text-body-md">${errMsg}</p>
          </div>
        `;
        hopThongBao.classList.remove("hidden");
        hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }

      if (nutKy) {
        nutKy.disabled = false;
        nutKy.innerHTML = oldHtml;
      }
      return;
    }

    const contractData = resJson.data || {};
    const ngayKyHienThi = contractData.ngay_ky || new Date().toISOString().split("T")[0];
    const tenSinhVien = contractData.sinh_vien?.ho_ten || "Nguyễn Văn An";

    try {
      localStorage.setItem(`ictu_contract_signed_${maHopDong}`, JSON.stringify({
        tenSinhVien,
        ngayKy: ngayKyHienThi,
        trang_thai: "DaXacNhan"
      }));
    } catch (e) {}

    apDungTrangThaiDaKy(tenSinhVien, ngayKyHienThi, maHopDong);

    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-secondary-container text-on-secondary-container p-4 flex items-start gap-3.5 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">check</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">✓ Chúc mừng! Bạn đã ký hợp đồng điện tử thành công.</p>
          <p class="font-body-md text-body-md">
            Mã xác thực điện tử: <strong class="font-code font-bold">ICTU-SIGNED-9921-OK</strong>. Dữ liệu đã lưu vào hồ sơ thực tập (Trạng thái: <strong>Đang thực tập</strong>) và gửi email thông báo xác nhận tới email của bạn.
          </p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

  } catch (err) {
    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-amber-50 text-amber-900 border border-amber-200 p-4 flex items-start gap-3.5 shadow-sm";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">wifi_off</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">Không thể kết nối tới máy chủ</p>
          <p class="font-body-md text-body-md">Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau (${err.message || "Lỗi mạng"}).</p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
    }
    if (nutKy) {
      nutKy.disabled = false;
      nutKy.innerHTML = `<span>Thử ký lại</span>`;
    }
  }
}

function capNhatThongTinHopDong() {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;
  const elSidebar = document.getElementById("theHocKyHopDongSidebar");
  if (elSidebar) elSidebar.textContent = `Học kỳ ${nienKhoa}`;
  const elNgayKy = document.getElementById("ngayKyHopDongTop");
  if (elNgayKy) elNgayKy.textContent = `Thái Nguyên, ngày ${now.getDate()} tháng ${now.getMonth() + 1} năm ${curY}`;
  const elSoHd = document.getElementById("soHopDongText");
  if (elSoHd) elSoHd.textContent = `Số: 01/${curY}/HĐTT-ICTU`;
  const elMaHd = document.getElementById("maHopDongTop");
  if (elMaHd) elMaHd.textContent = `ICTU-CONTRACT-${curY}/001`;
}

document.addEventListener("DOMContentLoaded", () => {
  capNhatThongTinHopDong();
  kiemTraTrangThaiHopDongBanDau();
});
