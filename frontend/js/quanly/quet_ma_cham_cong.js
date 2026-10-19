const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let cameraStream = null;
let dangQuet = false;
let nhatKyChamCong = [];

document.addEventListener("DOMContentLoaded", function () {
  capNhatDongHo();
  setInterval(capNhatDongHo, 1000);
  capNhatNgayNhatKy();
  taiNhatKyChamCong();
});

function capNhatDongHo() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  const el = document.getElementById("dongHoHienTai");
  if (el) el.textContent = `${hh}:${mm}:${ss}`;
}

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
    const trangThai = document.getElementById("trangThaiCamera");
    if (trangThai) trangThai.textContent = "Không thể truy cập camera. Hãy nhập mã thẻ thủ công.";
    hienThiToast("Không thể truy cập camera. Vui lòng cho phép quyền truy cập hoặc nhập mã thẻ thủ công!", "warning");
  }
}

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
    if (typeof jsQR !== "undefined") {
      const code = jsQR(imageData.data, imageData.width, imageData.height);
      if (code && code.data) {
        dangQuet = false;
        hienThiToast("Đã quét được mã QR!", "success");
        xuLyMaQuet(code.data);
        setTimeout(() => {
          dangQuet = true;
          quetQRTuCamera();
        }, 3000);
        return;
      }
    }
  } catch (e) {
  }

  requestAnimationFrame(quetQRTuCamera);
}

function guiMaChamCong() {
  const input = document.getElementById("oNhapMaThe");
  const maThe = input ? input.value.trim() : "";

  if (!maThe) {
    hienThiToast("Vui lòng nhập mã thẻ, email hoặc mã hồ sơ!", "error");
    return;
  }

  xuLyMaQuet(maThe);
  if (input) input.value = "";
}

async function xuLyMaQuet(maQuet) {
  const payload = {
    ma_dinh_danh: maQuet,
    phuong_thuc: cameraStream ? "QR" : "Card"
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
      hienThiPopupKetQua("success", json);
      capNhatQuetGanNhat(json.data || {});
      taiNhatKyChamCong();
    } else {
      const msg = json.detail || json.message || "Không thể ghi nhận chấm công";
      hienThiPopupKetQua("error", { message: msg });
      hienThiToast(typeof msg === "string" ? msg : JSON.stringify(msg), "error");
    }
  } catch (err) {
    hienThiPopupKetQua("error", { message: "Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng!" });
    hienThiToast("Lỗi kết nối máy chủ!", "error");
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

function hienThiPopupKetQua(loai, duLieu) {
  const popup = document.getElementById("popupKetQua");
  const iconWrap = document.getElementById("popupIconWrap");
  const icon = document.getElementById("popupIcon");
  const tieuDe = document.getElementById("popupTieuDe");
  const noiDung = document.getElementById("popupNoiDung");
  const chiTiet = document.getElementById("popupChiTiet");

  if (!popup) return;

  if (loai === "success") {
    const data = duLieu.data || {};
    const hoTen = data.ho_ten || "Thực tập sinh";
    const maHoSo = data.ma_ho_so || "--";
    const hanhDong = data.hanh_dong === "CHECK_OUT" ? "Check-out (Ra ca)" : "Check-in (Vào ca)";
    const gio = data.gio_checkout || data.gio_check_out || data.gio_checkin || data.gio_check_in || "--:--";

    if (iconWrap) iconWrap.className = "w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-sm ring-4 bg-emerald-50 text-emerald-600 ring-emerald-100";
    if (icon) icon.textContent = "check_circle";
    if (tieuDe) tieuDe.textContent = "Chấm công thành công!";
    if (noiDung) noiDung.textContent = duLieu.message || `Đã ghi nhận ${hanhDong} cho thực tập sinh.`;

    const elHoTen = document.getElementById("popupHoTen");
    const elMaThe = document.getElementById("popupMaThe");
    const elThoiGian = document.getElementById("popupThoiGian");
    const elLoai = document.getElementById("popupLoai");

    if (elHoTen) elHoTen.textContent = hoTen;
    if (elMaThe) elMaThe.textContent = `#${maHoSo}`;
    if (elThoiGian) elThoiGian.textContent = gio;
    if (elLoai) {
      elLoai.textContent = hanhDong;
      elLoai.className = data.hanh_dong === "CHECK_OUT" ? "font-bold text-amber-600" : "font-bold text-emerald-600";
    }

    if (chiTiet) chiTiet.classList.remove("hidden");
    hienThiToast(`Chấm công thành công cho ${hoTen}!`, "success");
  } else {
    if (iconWrap) iconWrap.className = "w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-sm ring-4 bg-rose-50 text-rose-600 ring-rose-100";
    if (icon) icon.textContent = "error";
    if (tieuDe) tieuDe.textContent = "Chấm công thất bại!";
    if (noiDung) noiDung.textContent = duLieu.message || "Vui lòng kiểm tra lại thông tin mã thẻ hoặc QR!";
    if (chiTiet) chiTiet.classList.add("hidden");
  }

  popup.classList.remove("opacity-0", "pointer-events-none");
}

function dongPopup() {
  const popup = document.getElementById("popupKetQua");
  if (popup) {
    popup.classList.add("opacity-0", "pointer-events-none");
  }
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
  if (elMa) elMa.textContent = `#${ketQua.ma_ho_so || "--"}`;
  if (elGio) elGio.textContent = ketQua.gio_checkout || ketQua.gio_checkin || dinhDangGio(new Date().toISOString());

  const loaiCC = ketQua.hanh_dong || "CHECK_IN";
  if (elLoai) {
    elLoai.textContent = loaiCC === "CHECK_OUT" ? "Check-out" : "Check-in";
    elLoai.className = loaiCC === "CHECK_OUT"
      ? "text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full"
      : "text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full";
  }
}

async function taiNhatKyChamCong() {
  const now = new Date();
  const ngay = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;

  try {
    const res = await fetch(`${duongDanApi}/attendance/records?ngay=${ngay}`);
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
    const maThe = `#${item.ma_ho_so || item.ma_sinh_vien || "--"}`;
    const loai = item.loai || (item.gio_check_out || item.gio_checkout ? "CheckOut" : "CheckIn");
    const thoiGian = item.gio_check_in || item.gio_checkin || item.gio_check_out || item.gio_checkout || "";
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
  const checkIn = danhSach.filter((i) => (i.loai || "CheckIn") === "CheckIn" || i.gio_check_in || i.gio_checkin).length;
  const checkOut = danhSach.filter((i) => i.loai === "CheckOut" || i.gio_check_out || i.gio_checkout).length;
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

function dinhDangGio(isoStr) {
  if (!isoStr) return "--:--";
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) {
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
