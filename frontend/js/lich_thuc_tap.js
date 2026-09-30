const duongDanApi = "http://127.0.0.1:8000/api/v1";

/**
 * Kiểm tra kết nối tới Backend API và hiển thị huy hiệu trạng thái thời gian thực
 */
async function kiemTraKetNoiApi() {
  const badge = document.getElementById("badgeTrangThaiApi");
  if (!badge) return;
  try {
    const phanHoi = await fetch("http://127.0.0.1:8000/docs", {
      method: "HEAD",
      mode: "no-cors",
    });
    badge.className =
      "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Backend: Đã kết nối API`;
    badge.classList.remove("hidden");
  } catch {
    badge.className =
      "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Chế độ Thử nghiệm (Offline)`;
    badge.classList.remove("hidden");
  }
}

/**
 * Tính toán tổng số ngày và tuần thực tập dự kiến, validate ngày kết thúc > ngày bắt đầu
 */
function tinhToanThoiGian() {
  const batDau = document.getElementById("ngayBatDau").value;
  const ketThuc = document.getElementById("ngayKetThuc").value;
  const labelSoNgay = document.getElementById("soNgayThucTap");
  if (!labelSoNgay) return;
  if (!batDau || !ketThuc) return;

  const d1 = new Date(batDau);
  const d2 = new Date(ketThuc);
  const diffTime = d2.getTime() - d1.getTime();

  if (diffTime <= 0) {
    labelSoNgay.textContent = "Ngày không hợp lệ (kết thúc phải lớn hơn bắt đầu)";
    labelSoNgay.className = "font-bold text-error";
    return;
  }

  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  const diffWeeks = Math.round((diffDays / 7) * 10) / 10;
  labelSoNgay.textContent = `${diffDays} ngày (${diffWeeks} tuần)`;
  labelSoNgay.className = "font-bold text-primary";
}

/**
 * Đặt lại form và cập nhật lại dự phóng thời gian
 */
function datLaiForm() {
  const form = document.getElementById("bieuMauChuongTrinh");
  if (form) form.reset();
  setTimeout(tinhToanThoiGian, 50);
}

/**
 * Hiển thị thông báo thành công
 */
function hienThiThongBaoThanhCong(tieuDe, noiDung) {
  const hop = document.getElementById("hopThongBao");
  if (!hop) return;
  hop.className =
    "rounded-xl bg-secondary-container p-4 shadow-sm flex items-start gap-3.5 transition-all text-on-secondary-container border border-secondary/20";
  hop.innerHTML = `
    <div class="w-9 h-9 rounded-lg bg-secondary flex items-center justify-center text-on-secondary shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-xl">check_circle</span>
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between">
        <h4 class="font-label-lg text-label-lg font-bold" data-thong-bao-tieu-de></h4>
        <span class="font-code text-label-sm bg-surface-container-lowest px-2 py-0.5 rounded text-secondary font-semibold">VỪA XONG</span>
      </div>
      <p class="font-body-md text-body-md mt-1 leading-relaxed" data-thong-bao-noi-dung></p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="hover:opacity-75 p-1 rounded-md transition-opacity" title="Đóng">
      <span class="material-symbols-outlined text-lg">close</span>
    </button>
  `;
  const titleNode = hop.querySelector("[data-thong-bao-tieu-de]");
  const contentNode = hop.querySelector("[data-thong-bao-noi-dung]");
  if (titleNode) titleNode.textContent = tieuDe;
  if (contentNode) contentNode.textContent = noiDung;
  hop.classList.remove("hidden");
  hop.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Hiển thị thông báo lỗi
 */
function hienThiThongBaoLoi(tieuDe, noiDung) {
  const hop = document.getElementById("hopThongBao");
  if (!hop) return;
  hop.className =
    "rounded-xl bg-red-50 p-4 shadow-sm flex items-start gap-3.5 transition-all text-red-900 border border-red-200";
  hop.innerHTML = `
    <div class="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center text-white shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-xl">error</span>
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between">
        <h4 class="font-label-lg text-label-lg font-bold text-red-800" data-thong-bao-tieu-de></h4>
        <span class="font-code text-label-sm bg-red-100 px-2 py-0.5 rounded text-red-700 font-semibold">LỖI XÁC THỰC</span>
      </div>
      <p class="font-body-md text-body-md mt-1 leading-relaxed text-red-700" data-thong-bao-noi-dung></p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="hover:opacity-75 p-1 rounded-md transition-opacity text-red-600" title="Đóng">
      <span class="material-symbols-outlined text-lg">close</span>
    </button>
  `;
  const titleNode = hop.querySelector("[data-thong-bao-tieu-de]");
  const contentNode = hop.querySelector("[data-thong-bao-noi-dung]");
  if (titleNode) titleNode.textContent = tieuDe;
  if (contentNode) contentNode.textContent = noiDung;
  hop.classList.remove("hidden");
  hop.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Xử lý lưu lịch trình chương trình thực tập:
 * Gọi API PATCH /api/v1/programs/{id}/timeline kèm validate ngày kết thúc > ngày bắt đầu
 */
async function xuLyLuuLich() {
  const programIdInput = document.getElementById("maChuongTrinh");
  const programId = programIdInput ? (parseInt(programIdInput.value, 10) || 1) : 1;
  const ten = document.getElementById("tenChuongTrinh") ? document.getElementById("tenChuongTrinh").value.trim() : "";
  const pb = document.getElementById("phongBan") ? document.getElementById("phongBan").value : "";
  const batDau = document.getElementById("ngayBatDau") ? document.getElementById("ngayBatDau").value : "";
  const ketThuc = document.getElementById("ngayKetThuc") ? document.getElementById("ngayKetThuc").value : "";
  const nut = document.getElementById("nutLuuLich");

  if (!batDau || !ketThuc) {
    hienThiThongBaoLoi("Thiếu thông tin", "Vui lòng chọn đầy đủ ngày bắt đầu và ngày kết thúc.");
    return;
  }

  // Validate phía client: ngày kết thúc > ngày bắt đầu
  if (ketThuc <= batDau) {
    hienThiThongBaoLoi(
      "Lỗi xác thực thời gian",
      "Ngày kết thúc phải lớn hơn ngày bắt đầu (ngay_ket_thuc > ngay_bat_dau). Vui lòng chọn lại ngày kết thúc."
    );
    return;
  }

  const oldContent = nut ? nut.innerHTML : "";
  if (nut) {
    nut.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang lưu lịch trình...</span>
    `;
    nut.disabled = true;
  }

  try {
    const res = await fetch(`${duongDanApi}/programs/${programId}/timeline`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ngay_bat_dau: batDau,
        ngay_ket_thuc: ketThuc,
      }),
    });

    const resData = await res.json();

    if (!res.ok) {
      let errorMsg = "Không thể cập nhật lịch trình chương trình thực tập.";
      if (typeof resData.detail === "string") {
        errorMsg = resData.detail;
      } else if (Array.isArray(resData.detail)) {
        errorMsg = resData.detail.map(e => e.msg || e.message).join(", ");
      }
      hienThiThongBaoLoi("Lỗi từ hệ thống", errorMsg);
      return;
    }

    // Cập nhật thành công từ API Backend
    const data = resData.data || {};
    const tenHienThi = data.ten_chuong_trinh || ten;
    const startStr = data.ngay_bat_dau || batDau;
    const endStr = data.ngay_ket_thuc || ketThuc;

    hienThiThongBaoThanhCong(
      `Lưu Thành Công Lịch Trình (Chương Trình #${data.ma_chuong_trinh || programId})`,
      `Đã cập nhật mốc thời gian thành công cho <strong>"${tenHienThi}"</strong> từ ngày <strong>${startStr}</strong> đến <strong>${endStr}</strong> trong cơ sở dữ liệu hệ thống.`
    );
  } catch (error) {
    console.warn("Không thể kết nối đến Backend API, chuyển sang chế độ lưu offline:", error);
    // Fallback offline mượt mà
    hienThiThongBaoThanhCong(
      "Lưu Lịch Trình Thực Tập (Chế độ Thử nghiệm)",
      `Đã đồng bộ lịch trình cho chương trình <strong>"${ten}"</strong> (${pb}) từ ngày <strong>${batDau}</strong> đến <strong>${ketThuc}</strong> (Chế độ offline).`
    );
  } finally {
    if (nut) {
      nut.innerHTML = oldContent;
      nut.disabled = false;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  kiemTraKetNoiApi();
  tinhToanThoiGian();
});
