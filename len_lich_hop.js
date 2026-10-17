/* ============================================================
   LÊN LỊCH HỌP - JavaScript (Fetch API)
   POST /api/v1/meetings
   ============================================================ */

const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let danhSachThucTapSinh = [];
let danhSachLichHop = [];

// ==========================================
// 1. KHỞI TẠO TRANG
// ==========================================
document.addEventListener("DOMContentLoaded", function () {
  capNhatNgayHeader();
  capNhatThoiGianMacDinh();
  taiDanhSachThucTapSinh();
  taiDanhSachLichHop();
  ganSuKienHinhThucHop();
});

/** Cập nhật ngày hiện tại trên header */
function capNhatNgayHeader() {
  const now = new Date();
  const opts = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
  const el = document.getElementById("ngayHienTaiHeader");
  if (el) el.textContent = now.toLocaleDateString("vi-VN", opts);
}

/** Đặt thời gian mặc định cho form (bắt đầu +1h, kết thúc +2h) */
function capNhatThoiGianMacDinh() {
  const now = new Date();
  const batDau = new Date(now.getTime() + 60 * 60 * 1000);
  const ketThuc = new Date(now.getTime() + 2 * 60 * 60 * 1000);

  const fmt = (d) => {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    const hh = String(d.getHours()).padStart(2, "0");
    const mm = String(d.getMinutes()).padStart(2, "0");
    return `${y}-${m}-${dd}T${hh}:${mm}`;
  };

  const elBD = document.getElementById("thoiGianBatDau");
  const elKT = document.getElementById("thoiGianKetThuc");
  if (elBD) elBD.value = fmt(batDau);
  if (elKT) elKT.value = fmt(ketThuc);
}

/** Gán sự kiện thay đổi hình thức họp (trực tiếp / online) */
function ganSuKienHinhThucHop() {
  document.querySelectorAll("input[name='hinhThucHop']").forEach((radio) => {
    radio.addEventListener("change", function () {
      const icon = document.getElementById("iconDiaDiem");
      const input = document.getElementById("diaDiemHop");
      if (this.value === "Online") {
        if (icon) icon.textContent = "link";
        if (input) input.placeholder = "VD: https://meet.google.com/abc-defg-hij";
      } else {
        if (icon) icon.textContent = "meeting_room";
        if (input) input.placeholder = "VD: Phòng A301 - Tòa nhà CNTT";
      }
    });
  });
}

// ==========================================
// 2. TẢI DANH SÁCH THỰC TẬP SINH
// ==========================================
async function taiDanhSachThucTapSinh() {
  try {
    const res = await fetch(`${duongDanApi}/students`);
    const json = await res.json();
    if (json.data && Array.isArray(json.data)) {
      danhSachThucTapSinh = json.data;
    } else {
      danhSachThucTapSinh = [];
    }
  } catch (err) {
    console.error("Lỗi tải danh sách TTS:", err);
    danhSachThucTapSinh = [];
  }
  hienThiDanhSachTTS(danhSachThucTapSinh);
}

/** Hiển thị danh sách thực tập sinh với checkbox */
function hienThiDanhSachTTS(danhSach) {
  const container = document.getElementById("danhSachTTSThamGia");
  if (!container) return;

  if (!danhSach || danhSach.length === 0) {
    container.innerHTML = `
      <div class="py-4 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-2xl text-slate-300 block mb-1">person_off</span>
        <p>Không tìm thấy thực tập sinh nào</p>
      </div>
    `;
    capNhatSoLuongDaChon();
    return;
  }

  container.innerHTML = danhSach.map((sv) => {
    const maSV = sv.ma_sinh_vien || sv.email.split("@")[0].toUpperCase();
    const tenSV = sv.ho_ten || "Chưa rõ";
    const id = sv.ma_nguoi_dung;
    return `
      <label class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-ictu-50 cursor-pointer transition-colors border border-transparent hover:border-ictu-100" for="tts_${id}">
        <input type="checkbox" id="tts_${id}" value="${id}" data-email="${sv.email || ''}" class="cb-tts w-4 h-4 text-ictu-600 border-slate-300 rounded focus:ring-ictu-500 cursor-pointer" onchange="capNhatSoLuongDaChon()" />
        <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-ictu-500 to-sky-400 flex items-center justify-center text-white text-[11px] font-bold shrink-0">
          ${layTenVietTatSV(tenSV)}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-xs font-bold text-slate-800 truncate">${tenSV}</p>
          <p class="text-[10px] text-slate-400 truncate">${maSV} • ${sv.chuyen_nganh || "CNTT"}</p>
        </div>
      </label>
    `;
  }).join("");

  capNhatSoLuongDaChon();
}

function layTenVietTatSV(hoTen) {
  if (!hoTen) return "??";
  const words = hoTen.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
  }
  return hoTen.substring(0, 2).toUpperCase();
}

/** Lọc danh sách TTS theo từ khoá */
function locDanhSachTTS(keyword) {
  const kw = keyword.toLowerCase().trim();
  if (!kw) {
    hienThiDanhSachTTS(danhSachThucTapSinh);
    return;
  }
  const filtered = danhSachThucTapSinh.filter((sv) => {
    const hoTen = (sv.ho_ten || "").toLowerCase();
    const maSV = (sv.ma_sinh_vien || "").toLowerCase();
    const email = (sv.email || "").toLowerCase();
    return hoTen.includes(kw) || maSV.includes(kw) || email.includes(kw);
  });
  hienThiDanhSachTTS(filtered);
}

/** Chọn tất cả */
function chonTatCaTTS() {
  document.querySelectorAll(".cb-tts").forEach((cb) => (cb.checked = true));
  capNhatSoLuongDaChon();
}

/** Bỏ chọn tất cả */
function boChonTatCaTTS() {
  document.querySelectorAll(".cb-tts").forEach((cb) => (cb.checked = false));
  capNhatSoLuongDaChon();
}

/** Cập nhật số lượng đã chọn */
function capNhatSoLuongDaChon() {
  const count = document.querySelectorAll(".cb-tts:checked").length;
  const el = document.getElementById("soLuongDaChon");
  if (el) el.textContent = count;
}

// ==========================================
// 3. GỬI DỮ LIỆU TẠO LỊCH HỌP (Fetch API)
// ==========================================
async function guiLichHop() {
  const tieuDe = document.getElementById("tieuDeCuocHop").value.trim();
  const batDau = document.getElementById("thoiGianBatDau").value;
  const ketThuc = document.getElementById("thoiGianKetThuc").value;
  const hinhThuc = document.querySelector("input[name='hinhThucHop']:checked").value;
  const diaDiem = document.getElementById("diaDiemHop").value.trim();
  const noiDung = document.getElementById("noiDungHop").value.trim();
  const guiMail = document.getElementById("guiMailThongBao").checked;

  // Validate
  if (!tieuDe) {
    hienThiToast("Vui lòng nhập tiêu đề cuộc họp!", "error");
    return;
  }
  if (!batDau || !ketThuc) {
    hienThiToast("Vui lòng chọn thời gian bắt đầu và kết thúc!", "error");
    return;
  }
  if (new Date(batDau) >= new Date(ketThuc)) {
    hienThiToast("Thời gian kết thúc phải sau thời gian bắt đầu!", "error");
    return;
  }

  const danhSachThamGia = [];
  document.querySelectorAll(".cb-tts:checked").forEach((cb) => {
    danhSachThamGia.push(parseInt(cb.value, 10));
  });

  if (danhSachThamGia.length === 0) {
    hienThiToast("Vui lòng chọn ít nhất 1 thực tập sinh tham gia!", "error");
    return;
  }

  const payload = {
    tieu_de: tieuDe,
    thoi_gian_bat_dau: batDau,
    thoi_gian_ket_thuc: ketThuc,
    hinh_thuc: hinhThuc,
    dia_diem: diaDiem,
    noi_dung: noiDung,
    gui_mail: guiMail,
    danh_sach_tham_gia: danhSachThamGia
  };

  const nutGui = document.getElementById("nutTaoLichHop");
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang gửi...</span>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/meetings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const json = await res.json();

    if (res.ok) {
      hienThiToast(`Tạo lịch họp thành công! ${guiMail ? "(Đã gửi email thông báo)" : ""}`, "success");
      datLaiFormHop();
      taiDanhSachLichHop();
    } else {
      const msg = json.detail || json.message || "Không thể tạo lịch họp";
      hienThiToast(`Lỗi: ${msg}`, "error");
    }
  } catch (err) {
    console.error("Lỗi gửi lịch họp:", err);
    hienThiToast("Không thể kết nối đến máy chủ. Vui lòng thử lại!", "error");
  } finally {
    if (nutGui) {
      nutGui.disabled = false;
      nutGui.innerHTML = `
        <span class="material-symbols-outlined text-lg">send</span>
        <span>Tạo lịch họp</span>
      `;
    }
  }
}

/** Đặt lại form */
function datLaiFormHop() {
  const form = document.getElementById("formLenLichHop");
  if (form) form.reset();
  capNhatThoiGianMacDinh();
  boChonTatCaTTS();
  const icon = document.getElementById("iconDiaDiem");
  if (icon) icon.textContent = "meeting_room";
  const input = document.getElementById("diaDiemHop");
  if (input) input.placeholder = "VD: Phòng A301 - Tòa nhà CNTT";
}

// ==========================================
// 4. TẢI & HIỂN THỊ DANH SÁCH LỊCH HỌP
// ==========================================
async function taiDanhSachLichHop() {
  try {
    const res = await fetch(`${duongDanApi}/meetings`);
    if (!res.ok) {
      hienThiBangTrong();
      return;
    }
    const json = await res.json();
    if (json.data && Array.isArray(json.data)) {
      danhSachLichHop = json.data;
      hienThiBangLichHop(danhSachLichHop);
      capNhatThongKe(danhSachLichHop);
    } else {
      hienThiBangTrong();
    }
  } catch (err) {
    console.error("Lỗi tải danh sách lịch họp:", err);
    hienThiBangTrong();
  }
}

function hienThiBangLichHop(danhSach) {
  const tbody = document.getElementById("bangDanhSachLichHop");
  if (!tbody) return;

  if (!danhSach || danhSach.length === 0) {
    hienThiBangTrong();
    return;
  }

  tbody.innerHTML = danhSach.map((hop, idx) => {
    const hinhThucClass = hop.hinh_thuc === "Online"
      ? "bg-indigo-50 text-indigo-700 border-indigo-100"
      : "bg-emerald-50 text-emerald-700 border-emerald-100";
    const hinhThucIcon = hop.hinh_thuc === "Online" ? "videocam" : "groups";
    const soThanhVien = hop.danh_sach_tham_gia ? hop.danh_sach_tham_gia.length : 0;

    return `
      <tr class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
        <td class="py-3 px-3 text-xs text-slate-400 font-mono">${idx + 1}</td>
        <td class="py-3 px-3">
          <p class="text-xs font-bold text-slate-800">${hop.tieu_de || "Chưa đặt tên"}</p>
          <p class="text-[10px] text-slate-400 mt-0.5 truncate max-w-[200px]">${hop.noi_dung || ""}</p>
        </td>
        <td class="py-3 px-3">
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${hinhThucClass} border">
            <span class="material-symbols-outlined text-xs">${hinhThucIcon}</span>
            ${hop.hinh_thuc || "N/A"}
          </span>
        </td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono">${dinhDangThoiGian(hop.thoi_gian_bat_dau)}</td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono">${dinhDangThoiGian(hop.thoi_gian_ket_thuc)}</td>
        <td class="py-3 px-3">
          <span class="inline-flex items-center gap-1 text-xs font-semibold text-slate-600">
            <span class="material-symbols-outlined text-sm">group</span>
            ${soThanhVien} người
          </span>
        </td>
        <td class="py-3 px-3">
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-100">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Đã lên lịch
          </span>
        </td>
      </tr>
    `;
  }).join("");
}

function hienThiBangTrong() {
  const tbody = document.getElementById("bangDanhSachLichHop");
  if (!tbody) return;
  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="py-8 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-3xl text-slate-300 block mb-2">event_busy</span>
        Chưa có lịch họp nào. Hãy tạo cuộc họp đầu tiên!
      </td>
    </tr>
  `;
}

function capNhatThongKe(danhSach) {
  const now = new Date();
  const today = now.toISOString().split("T")[0];

  const tongHop = danhSach.length;
  const homNay = danhSach.filter((h) => (h.thoi_gian_bat_dau || "").startsWith(today)).length;
  const sapToi = danhSach.filter((h) => new Date(h.thoi_gian_bat_dau) > now).length;
  const online = danhSach.filter((h) => h.hinh_thuc === "Online").length;

  const el1 = document.getElementById("thongKeTongHop");
  const el2 = document.getElementById("thongKeHomNay");
  const el3 = document.getElementById("thongKeSapToi");
  const el4 = document.getElementById("thongKeOnline");

  if (el1) el1.textContent = tongHop;
  if (el2) el2.textContent = homNay;
  if (el3) el3.textContent = sapToi;
  if (el4) el4.textContent = online;
}

// ==========================================
// 5. TIỆN ÍCH
// ==========================================

/** Định dạng thời gian ISO → dễ đọc */
function dinhDangThoiGian(isoStr) {
  if (!isoStr) return "--";
  try {
    const d = new Date(isoStr);
    const ngay = String(d.getDate()).padStart(2, "0");
    const thang = String(d.getMonth() + 1).padStart(2, "0");
    const nam = d.getFullYear();
    const gio = String(d.getHours()).padStart(2, "0");
    const phut = String(d.getMinutes()).padStart(2, "0");
    return `${ngay}/${thang}/${nam} ${gio}:${phut}`;
  } catch {
    return isoStr;
  }
}

/** Hiển thị Toast thông báo */
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
