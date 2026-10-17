/* ============================================================
   QUÉT MÃ CHẤM CÔNG - JavaScript (Fetch API)
   POST /api/v1/attendance/scan
   ============================================================ */

const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let cameraStream = null;
let dangQuet = false;
let nhatKyChamCong = [];

// ==========================================
// 1. KHỞI TẠO TRANG
// ==========================================
document.addEventListener("DOMContentLoaded", function () {
  capNhatDongHo();
  setInterval(capNhatDongHo, 1000);
  capNhatNgayNhatKy();
  taiNhatKyChamCong();
});

/** Đồng hồ thời gian thực */
function capNhatDongHo() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  const el = document.getElementById("dongHoHienTai");
  if (el) el.textContent = `${hh}:${mm}:${ss}`;
}

/** Cập nhật ngày nhật ký */
function capNhatNgayNhatKy() {
  const now = new Date();
  const ngay = String(now.getDate()).padStart(2, "0");
  const thang = String(now.getMonth() + 1).padStart(2, "0");
  const nam = now.getFullYear();
  const mapThu = { 0: "Chủ nhật", 1: "Thứ Hai", 2: "Thứ Ba", 3: "Thứ Tư", 4: "Thứ Năm", 5: "Thứ Sáu", 6: "Thứ Bảy" };

  const elNgay = document.getElementById("ngayNhatKy");
  const elThu = document.getElementById("thuNhatKy");
  if (elNgay) elNgay.textContent = `${ngay}/${thang}/${nam}`;
  if (elThu) elThu.textContent = mapThu[now.getDay()] || "";
}

// ==========================================
// 2. QUẢN LÝ CAMERA QR
// ==========================================

/** Bật camera */
async function batCamera() {
  try {
    const video = document.getElementById("cameraPreview");
    const overlay = document.getElementById("cameraOverlay");
    const trangThai = document.getElementById("trangThaiCamera");
    const scanLine = document.getElementById("scanLine");
    const nutBat = document.getElementById("nutBatCamera");
    const nutTat = document.getElementById("nutTatCamera");

    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 640 } }
    });

    if (video) {
      video.srcObject = cameraStream;
      video.classList.remove("hidden");
    }
    if (trangThai) trangThai.textContent = "Đang quét... Đưa mã QR vào khung hình";
    if (scanLine) scanLine.classList.remove("hidden");
    if (nutBat) nutBat.classList.add("hidden");
    if (nutTat) nutTat.classList.remove("hidden");

    dangQuet = true;
    quetQRTuCamera();
  } catch (err) {
    console.error("Lỗi truy cập camera:", err);
    const trangThai = document.getElementById("trangThaiCamera");
    if (trangThai) trangThai.textContent = "Không thể truy cập camera. Hãy nhập mã thẻ thủ công.";
    hienThiToast("Không thể truy cập camera. Vui lòng cho phép quyền truy cập hoặc nhập mã thẻ thủ công!", "warning");
  }
}

/** Tắt camera */
function tatCamera() {
  dangQuet = false;

  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }

  const video = document.getElementById("cameraPreview");
  const trangThai = document.getElementById("trangThaiCamera");
  const scanLine = document.getElementById("scanLine");
  const nutBat = document.getElementById("nutBatCamera");
  const nutTat = document.getElementById("nutTatCamera");

  if (video) {
    video.srcObject = null;
    video.classList.add("hidden");
  }
  if (trangThai) trangThai.textContent = "Camera đã tắt. Nhấn nút để bật lại.";
  if (scanLine) scanLine.classList.add("hidden");
  if (nutBat) nutBat.classList.remove("hidden");
  if (nutTat) nutTat.classList.add("hidden");
}

/** Quét QR từ camera frame (sử dụng canvas) */
function quetQRTuCamera() {
  if (!dangQuet) return;

  const video = document.getElementById("cameraPreview");
  const canvas = document.getElementById("canvasQR");
  if (!video || !canvas || video.readyState < 2) {
    requestAnimationFrame(quetQRTuCamera);
    return;
  }

  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  try {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    // Nếu có thư viện jsQR, dùng để decode
    if (typeof jsQR !== "undefined") {
      const code = jsQR(imageData.data, imageData.width, imageData.height);
      if (code && code.data) {
        dangQuet = false;
        hienThiToast("Đã quét được mã QR!", "success");
        // Gửi mã quét lên server
        xuLyMaQuet(code.data);
        // Tiếp tục quét sau 3 giây
        setTimeout(() => {
          dangQuet = true;
          quetQRTuCamera();
        }, 3000);
        return;
      }
    }
  } catch (e) {
    // jsQR chưa có hoặc lỗi decode → tiếp tục quét
  }

  requestAnimationFrame(quetQRTuCamera);
}

// ==========================================
// 3. GỬI MÃ CHẤM CÔNG (Fetch API)
// ==========================================

/** Gửi mã thẻ từ ô nhập thủ công */
function guiMaChamCong() {
  const input = document.getElementById("oNhapMaThe");
  const maThe = input ? input.value.trim() : "";

  if (!maThe) {
    hienThiToast("Vui lòng nhập mã thẻ hoặc quét mã QR!", "error");
    return;
  }

  xuLyMaQuet(maThe);
  if (input) input.value = "";
}

/** Xử lý mã quét - POST /api/v1/attendance/scan */
async function xuLyMaQuet(maQuet) {
  const now = new Date();
  const payload = {
    ma_quet: maQuet,
    thoi_gian_quet: now.toISOString(),
    phuong_thuc: cameraStream ? "QR" : "TheCung"
  };

  const nutGui = document.getElementById("nutGuiMaChamCong");
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang xử lý...</span>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/attendance/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const json = await res.json();

    if (res.ok) {
      // Hiển thị popup thành công
      hienThiPopupKetQua("success", json);
      // Cập nhật nhật ký
      taiNhatKyChamCong();
    } else {
      const msg = json.detail || json.message || "Không thể ghi nhận chấm công";
      hienThiPopupKetQua("error", { message: msg });
    }
  } catch (err) {
    console.error("Lỗi gửi chấm công:", err);
    hienThiPopupKetQua("error", { message: "Không thể kết nối đến máy chủ. Vui lòng thử lại!" });
  } finally {
    if (nutGui) {
      nutGui.disabled = false;
      nutGui.innerHTML = `
        <span class="material-symbols-outlined text-lg">send</span>
        <span>Gửi Chấm Công</span>
      `;
    }
  }
}

// ==========================================
// 4. POPUP KẾT QUẢ
// ==========================================

function hienThiPopupKetQua(loai, data) {
  const popup = document.getElementById("popupKetQua");
  const card = document.getElementById("popupCard");
  const iconWrap = document.getElementById("popupIconWrap");
  const icon = document.getElementById("popupIcon");
  const tieuDe = document.getElementById("popupTieuDe");
  const noiDung = document.getElementById("popupNoiDung");
  const chiTiet = document.getElementById("popupChiTiet");

  if (loai === "success") {
    iconWrap.className = "w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center mb-4 shadow-sm ring-4 ring-emerald-50";
    icon.className = "material-symbols-outlined text-[32px] text-emerald-600";
    icon.textContent = "check_circle";
    tieuDe.textContent = "Chấm công thành công!";

    const ketQua = data.data || data;
    noiDung.textContent = data.message || "Đã ghi nhận chấm công cho thực tập sinh.";

    if (ketQua) {
      chiTiet.classList.remove("hidden");
      const elHoTen = document.getElementById("popupHoTen");
      const elMaThe = document.getElementById("popupMaThe");
      const elThoiGian = document.getElementById("popupThoiGian");
      const elLoai = document.getElementById("popupLoai");

      if (elHoTen) elHoTen.textContent = ketQua.ho_ten || "--";
      if (elMaThe) elMaThe.textContent = ketQua.ma_quet || ketQua.ma_the || "--";
      if (elThoiGian) elThoiGian.textContent = dinhDangGio(ketQua.thoi_gian_quet || new Date().toISOString());
      if (elLoai) {
        const loaiChamCong = ketQua.loai || "CheckIn";
        elLoai.textContent = loaiChamCong === "CheckOut" ? "Check-out" : "Check-in";
        elLoai.className = loaiChamCong === "CheckOut"
          ? "font-bold text-amber-600"
          : "font-bold text-emerald-600";
      }

      // Cập nhật thông tin quét gần nhất
      capNhatQuetGanNhat(ketQua);
    }
  } else {
    iconWrap.className = "w-16 h-16 rounded-2xl bg-rose-50 border border-rose-200 flex items-center justify-center mb-4 shadow-sm ring-4 ring-rose-50";
    icon.className = "material-symbols-outlined text-[32px] text-rose-600";
    icon.textContent = "error";
    tieuDe.textContent = "Chấm công thất bại!";
    noiDung.textContent = data.message || "Đã xảy ra lỗi. Vui lòng thử lại.";
    chiTiet.classList.add("hidden");
  }

  // Hiển thị popup
  popup.classList.remove("opacity-0", "pointer-events-none");
  popup.classList.add("opacity-100");
  card.classList.remove("scale-95");
  card.classList.add("scale-100");
}

function dongPopup() {
  const popup = document.getElementById("popupKetQua");
  const card = document.getElementById("popupCard");
  card.classList.remove("scale-100");
  card.classList.add("scale-95");
  popup.classList.remove("opacity-100");
  popup.classList.add("opacity-0", "pointer-events-none");
}

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") dongPopup();
});

function capNhatQuetGanNhat(ketQua) {
  const wrap = document.getElementById("thongTinQuetGanNhat");
  if (!wrap) return;
  wrap.classList.remove("hidden");

  const hoTen = ketQua.ho_ten || "Thực tập sinh";
  const words = hoTen.trim().split(/\s+/);
  const initials = words.length >= 2
    ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
    : hoTen.substring(0, 2).toUpperCase();

  const elAvatar = document.getElementById("avatarQuetGanNhat");
  const elTen = document.getElementById("tenQuetGanNhat");
  const elMa = document.getElementById("maQuetGanNhat");
  const elGio = document.getElementById("gioQuetGanNhat");
  const elLoai = document.getElementById("loaiQuetGanNhat");

  if (elAvatar) elAvatar.textContent = initials;
  if (elTen) elTen.textContent = hoTen;
  if (elMa) elMa.textContent = ketQua.ma_quet || ketQua.ma_the || "--";
  if (elGio) elGio.textContent = dinhDangGio(ketQua.thoi_gian_quet || new Date().toISOString());

  const loaiCC = ketQua.loai || "CheckIn";
  if (elLoai) {
    elLoai.textContent = loaiCC === "CheckOut" ? "Check-out" : "Check-in";
    elLoai.className = loaiCC === "CheckOut"
      ? "text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full"
      : "text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full";
  }
}

// ==========================================
// 5. BẢNG NHẬT KÝ CHẤM CÔNG
// ==========================================

async function taiNhatKyChamCong() {
  const now = new Date();
  const ngay = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;

  try {
    const res = await fetch(`${duongDanApi}/attendance?ngay=${ngay}`);
    if (!res.ok) {
      hienThiBangNhatKyTrong();
      capNhatKPI([]);
      return;
    }
    const json = await res.json();
    if (json.data && Array.isArray(json.data)) {
      nhatKyChamCong = json.data;
    } else if (json.data && json.data.items && Array.isArray(json.data.items)) {
      nhatKyChamCong = json.data.items;
    } else {
      nhatKyChamCong = [];
    }
    hienThiBangNhatKy(nhatKyChamCong);
    capNhatKPI(nhatKyChamCong);
  } catch (err) {
    console.error("Lỗi tải nhật ký chấm công:", err);
    hienThiBangNhatKyTrong();
    capNhatKPI([]);
  }
}

function hienThiBangNhatKy(danhSach) {
  const tbody = document.getElementById("bangNhatKyChamCong");
  if (!tbody) return;

  if (!danhSach || danhSach.length === 0) {
    hienThiBangNhatKyTrong();
    return;
  }

  tbody.innerHTML = danhSach.map((item, idx) => {
    const hoTen = item.ho_ten || item.ten_sinh_vien || "--";
    const maThe = item.ma_quet || item.ma_the || item.ma_sinh_vien || "--";
    const loai = item.loai || (item.gio_check_out ? "CheckOut" : "CheckIn");
    const thoiGian = item.thoi_gian_quet || item.gio_check_in || item.gio_check_out || "";
    const trangThai = item.trang_thai || "DungGio";

    const loaiBadge = loai === "CheckOut"
      ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-100">
           <span class="material-symbols-outlined text-xs">logout</span>Check-out
         </span>`
      : `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-100">
           <span class="material-symbols-outlined text-xs">login</span>Check-in
         </span>`;

    const trangThaiBadge = trangThai === "TreGio" || trangThai === "DiTre"
      ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-100">
           <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>Trễ giờ
         </span>`
      : `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-100">
           <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Đúng giờ
         </span>`;

    const words = hoTen.trim().split(/\s+/);
    const initials = words.length >= 2
      ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
      : hoTen.substring(0, 2).toUpperCase();

    return `
      <tr class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
        <td class="py-3 px-3 text-xs text-slate-400 font-mono">${idx + 1}</td>
        <td class="py-3 px-3">
          <div class="flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-full bg-gradient-to-tr from-ictu-500 to-sky-400 flex items-center justify-center text-white text-[10px] font-bold shrink-0">${initials}</div>
            <span class="text-xs font-bold text-slate-800">${hoTen}</span>
          </div>
        </td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono font-semibold">${maThe}</td>
        <td class="py-3 px-3">${loaiBadge}</td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono font-semibold">${dinhDangGio(thoiGian)}</td>
        <td class="py-3 px-3">${trangThaiBadge}</td>
      </tr>
    `;
  }).join("");
}

function hienThiBangNhatKyTrong() {
  const tbody = document.getElementById("bangNhatKyChamCong");
  if (!tbody) return;
  tbody.innerHTML = `
    <tr>
      <td colspan="6" class="py-10 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-4xl text-slate-300 block mb-2">pending</span>
        Chưa có bản ghi chấm công nào hôm nay.<br>Quét mã QR hoặc nhập mã thẻ để bắt đầu!
      </td>
    </tr>
  `;
}

function capNhatKPI(danhSach) {
  const tong = danhSach.length;
  const checkIn = danhSach.filter((i) => (i.loai || "CheckIn") === "CheckIn" || i.gio_check_in).length;
  const checkOut = danhSach.filter((i) => i.loai === "CheckOut" || i.gio_check_out).length;
  const treGio = danhSach.filter((i) => i.trang_thai === "TreGio" || i.trang_thai === "DiTre").length;

  const el1 = document.getElementById("kpiTongQuet");
  const el2 = document.getElementById("kpiCheckIn");
  const el3 = document.getElementById("kpiCheckOut");
  const el4 = document.getElementById("kpiTreGio");

  if (el1) el1.textContent = tong;
  if (el2) el2.textContent = checkIn;
  if (el3) el3.textContent = checkOut;
  if (el4) el4.textContent = treGio;
}

// ==========================================
// 6. TIỆN ÍCH
// ==========================================

function dinhDangGio(isoStr) {
  if (!isoStr) return "--:--";
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) {
      // Có thể là format "HH:MM:SS"
      return isoStr.length <= 8 ? isoStr : "--:--";
    }
    const hh = String(d.getHours()).padStart(2, "0");
    const mm = String(d.getMinutes()).padStart(2, "0");
    const ss = String(d.getSeconds()).padStart(2, "0");
    return `${hh}:${mm}:${ss}`;
  } catch {
    return isoStr;
  }
}

function hienThiToast(noiDung, loai) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const colors = {
    success: "bg-emerald-600 text-white",
    error: "bg-rose-600 text-white",
    warning: "bg-amber-500 text-white",
    info: "bg-ictu-600 text-white"
  };
  const icons = {
    success: "check_circle",
    error: "error",
    warning: "warning",
    info: "info"
  };

  const toast = document.createElement("div");
  toast.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-lg ${colors[loai] || colors.info} transform translate-x-full opacity-0 transition-all duration-300`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-xl">${icons[loai] || icons.info}</span>
    <span class="text-sm font-semibold">${noiDung}</span>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove("translate-x-full", "opacity-0");
    toast.classList.add("translate-x-0", "opacity-100");
  });

  setTimeout(() => {
    toast.classList.add("translate-x-full", "opacity-0");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
