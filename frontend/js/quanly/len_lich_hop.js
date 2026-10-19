const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let danhSachTTS = [];
let danhSachLichHop = [];

document.addEventListener("DOMContentLoaded", function () {
  capNhatNgayHeader();
  capNhatThoiGianMacDinh();
  taiDanhSachTTS();
  taiDanhSachLichHop();

  const selectHinhThuc = document.getElementById("hinhThucHop");
  if (selectHinhThuc) {
    selectHinhThuc.addEventListener("change", function () {
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
  }
});

function capNhatNgayHeader() {
  const now = new Date();
  const opts = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
  const el = document.getElementById("ngayHienTaiHeader");
  if (el) el.textContent = now.toLocaleDateString("vi-VN", opts);
}

function capNhatThoiGianMacDinh() {
  const batDau = new Date();
  batDau.setHours(batDau.getHours() + 1, 0, 0, 0);

  const ketThuc = new Date(batDau);
  ketThuc.setHours(ketThuc.getHours() + 2);

  const inputBatDau = document.getElementById("thoiGianBatDau");
  const inputKetThuc = document.getElementById("thoiGianKetThuc");

  if (inputBatDau) inputBatDau.value = dinhDangDatetimeLocal(batDau);
  if (inputKetThuc) inputKetThuc.value = dinhDangDatetimeLocal(ketThuc);
}

function dinhDangDatetimeLocal(d) {
  const pad = (n) => String(n).padStart(2, "0");
  const yyyy = d.getFullYear();
  const MM = pad(d.getMonth() + 1);
  const dd = pad(d.getDate());
  const hh = pad(d.getHours());
  const mm = pad(d.getMinutes());
  return `${yyyy}-${MM}-${dd}T${hh}:${mm}`;
}

async function taiDanhSachTTS() {
  const container = document.getElementById("danhSachChonTTS");
  if (!container) return;

  try {
    const res = await fetch(`${duongDanApi}/interns?limit=100`);
    if (!res.ok) {
      container.innerHTML = `<div class="text-center py-4 text-xs text-rose-500">Không thể tải danh sách thực tập sinh</div>`;
      return;
    }
    const json = await res.json();
    const items = json.data && json.data.items ? json.data.items : [];
    danhSachTTS = items;

    if (items.length === 0) {
      container.innerHTML = `<div class="text-center py-4 text-xs text-slate-400">Chưa có thực tập sinh nào trong hệ thống</div>`;
      return;
    }

    container.innerHTML = items.map((tts) => {
      const hoTen = tts.ho_ten || `TTS #${tts.ma_ho_so}`;
      const email = tts.email || "";
      const maHoSo = tts.ma_ho_so;
      const mentor = tts.mentor_ho_ten || tts.ten_mentor || "Chưa có Mentor";

      return `
        <label class="flex items-center justify-between p-2 rounded-lg hover:bg-white transition-colors cursor-pointer border border-transparent hover:border-slate-200">
          <div class="flex items-center gap-2.5">
            <input
              type="checkbox"
              value="${maHoSo}"
              class="cb-tts w-4 h-4 rounded text-ictu-600 focus:ring-ictu-500 border-slate-300 cursor-pointer"
            />
            <div>
              <p class="text-xs font-bold text-slate-800 leading-tight">${hoTen}</p>
              <p class="text-[10px] text-slate-400">${email} &bull; Mentor: ${mentor}</p>
            </div>
          </div>
          <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
            #${maHoSo}
          </span>
        </label>
      `;
    }).join("");
  } catch (err) {
    container.innerHTML = `<div class="text-center py-4 text-xs text-rose-500">Lỗi kết nối máy chủ khi tải TTS</div>`;
  }
}

function chonTatCaTTS() {
  document.querySelectorAll(".cb-tts").forEach((cb) => (cb.checked = true));
  const elLoi = document.getElementById("loiChonTTS");
  if (elLoi) elLoi.classList.add("hidden");
}

function boChonTatCaTTS() {
  document.querySelectorAll(".cb-tts").forEach((cb) => (cb.checked = false));
}

async function guiLichHop() {
  const tieuDe = (document.getElementById("tieuDeHop")?.value || "").trim();
  const batDau = document.getElementById("thoiGianBatDau")?.value;
  const ketThuc = document.getElementById("thoiGianKetThuc")?.value;
  const hinhThuc = document.getElementById("hinhThucHop")?.value || "TrucTiep";
  const diaDiem = (document.getElementById("diaDiemHop")?.value || "").trim();
  const noiDung = (document.getElementById("noiDungHop")?.value || "").trim();
  const guiMail = document.getElementById("guiMailThongBao")?.checked ?? true;

  if (!tieuDe) {
    hienThiToast("Vui lòng nhập tiêu đề cuộc họp!", "error");
    document.getElementById("tieuDeHop")?.focus();
    return;
  }
  if (!batDau || !ketThuc) {
    hienThiToast("Vui lòng chọn thời gian bắt đầu và kết thúc!", "error");
    return;
  }
  if (new Date(ketThuc) <= new Date(batDau)) {
    hienThiToast("Thời gian kết thúc phải lớn hơn thời gian bắt đầu!", "error");
    return;
  }
  if (!diaDiem) {
    hienThiToast("Vui lòng nhập địa điểm hoặc liên kết phòng họp!", "error");
    document.getElementById("diaDiemHop")?.focus();
    return;
  }

  const danhSachThamGia = [];
  document.querySelectorAll(".cb-tts:checked").forEach((cb) => {
    danhSachThamGia.push(parseInt(cb.value, 10));
  });

  const elLoi = document.getElementById("loiChonTTS");
  if (danhSachThamGia.length === 0) {
    if (elLoi) elLoi.classList.remove("hidden");
    hienThiToast("Vui lòng chọn ít nhất 1 thực tập sinh tham gia!", "error");
    return;
  } else {
    if (elLoi) elLoi.classList.add("hidden");
  }

  let maNguoiChuTri = 1;
  const sessionUser = localStorage.getItem("ictu_user_session") || localStorage.getItem("ictu_student_session");
  if (sessionUser) {
    try {
      const parsed = JSON.parse(sessionUser);
      if (parsed.ma_nguoi_dung) maNguoiChuTri = parsed.ma_nguoi_dung;
    } catch (e) {}
  }

  const payload = {
    tieu_de: tieuDe,
    thoi_gian_bat_dau: new Date(batDau).toISOString(),
    thoi_gian_ket_thuc: new Date(ketThuc).toISOString(),
    dia_diem: diaDiem,
    ma_nguoi_chu_tri: maNguoiChuTri,
    danh_sach_thuc_tap_sinh: danhSachThamGia,
    noi_dung: noiDung
  };

  const nutGui = document.getElementById("nutTaoLichHop");
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang xử lý...</span>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/meetings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const json = await res.json().catch(() => ({}));

    if (res.ok) {
      hienThiToast("Tạo lịch họp thành công! Đã lên lịch và đồng bộ mã QR.", "success");
      datLaiFormHop();
      taiDanhSachLichHop();
    } else {
      let msg = "Không thể tạo lịch họp";
      if (json.detail) {
        msg = typeof json.detail === "string" ? json.detail : JSON.stringify(json.detail);
      } else if (json.message) {
        msg = json.message;
      }
      hienThiToast(`Lỗi: ${msg}`, "error");
    }
  } catch (err) {
    hienThiToast("Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng!", "error");
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

function datLaiFormHop() {
  const form = document.getElementById("formLenLichHop");
  if (form) form.reset();
  capNhatThoiGianMacDinh();
  boChonTatCaTTS();
  const icon = document.getElementById("iconDiaDiem");
  if (icon) icon.textContent = "meeting_room";
  const input = document.getElementById("diaDiemHop");
  if (input) input.placeholder = "VD: Phòng A301 - Tòa nhà CNTT";
  const elLoi = document.getElementById("loiChonTTS");
  if (elLoi) elLoi.classList.add("hidden");
}

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
    const hinhThucClass = (hop.dia_diem || "").toLowerCase().includes("http") || (hop.dia_diem || "").toLowerCase().includes("meet")
      ? "bg-indigo-50 text-indigo-700 border-indigo-100"
      : "bg-emerald-50 text-emerald-700 border-emerald-100";
    const hinhThucLabel = (hop.dia_diem || "").toLowerCase().includes("http") || (hop.dia_diem || "").toLowerCase().includes("meet")
      ? "Online"
      : "Trực tiếp";
    const hinhThucIcon = hinhThucLabel === "Online" ? "videocam" : "groups";
    const soThanhVien = hop.so_luong_nguoi_moi || (hop.danh_sach_thuc_tap_sinh_moi ? hop.danh_sach_thuc_tap_sinh_moi.length : 0);

    const hopJsonStr = JSON.stringify(hop).replace(/"/g, '&quot;');

    return `
      <tr class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
        <td class="py-3 px-3 text-xs text-slate-400 font-mono">${idx + 1}</td>
        <td class="py-3 px-3">
          <p class="text-xs font-bold text-slate-800">${hop.tieu_de || "Chưa đặt tên"}</p>
          <p class="text-[10px] text-slate-400 mt-0.5 truncate max-w-[200px]">Địa điểm: ${hop.dia_diem || "Chưa cập nhật"}</p>
        </td>
        <td class="py-3 px-3">
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${hinhThucClass} border">
            <span class="material-symbols-outlined text-xs">${hinhThucIcon}</span>
            ${hinhThucLabel}
          </span>
        </td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono">${dinhDangThoiGian(hop.thoi_gian_bat_dau)}</td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono">${dinhDangThoiGian(hop.thoi_gian_ket_thuc)}</td>
        <td class="py-3 px-3">
          <span class="inline-flex items-center gap-1 text-xs font-semibold text-slate-600">
            <span class="material-symbols-outlined text-sm">group</span>
            ${soThanhVien} bạn
          </span>
        </td>
        <td class="py-3 px-3 text-center">
          <button
            type="button"
            onclick='moModalChieuQr(${hopJsonStr})'
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-ictu-50 hover:bg-ictu-100 text-ictu-700 text-xs font-bold transition-all border border-ictu-200 cursor-pointer shadow-xs active:scale-95"
            title="Chiếu mã QR điểm danh cho sinh viên"
          >
            <span class="material-symbols-outlined text-sm">qr_code_2</span>
            <span>Chiếu QR</span>
          </button>
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
  const online = danhSach.filter((h) => (h.dia_diem || "").toLowerCase().includes("http") || (h.dia_diem || "").toLowerCase().includes("meet")).length;

  const el1 = document.getElementById("thongKeTongHop");
  const el2 = document.getElementById("thongKeHomNay");
  const el3 = document.getElementById("thongKeSapToi");
  const el4 = document.getElementById("thongKeOnline");

  if (el1) el1.textContent = tongHop;
  if (el2) el2.textContent = homNay;
  if (el3) el3.textContent = sapToi;
  if (el4) el4.textContent = online;
}

function moModalChieuQr(hop) {
  const modal = document.getElementById("modalChieuQr");
  if (!modal || !hop) return;

  const elTieuDe = document.getElementById("modalQrTieuDe");
  const elThoiGian = document.getElementById("modalQrThoiGian");
  const elDiaDiem = document.getElementById("modalQrDiaDiem");
  const elMaHop = document.getElementById("modalQrMaHop");
  const imgQr = document.getElementById("anhQrChieu");

  if (elTieuDe) elTieuDe.textContent = hop.tieu_de || "Cuộc họp hướng dẫn";
  if (elThoiGian) elThoiGian.textContent = `${dinhDangThoiGian(hop.thoi_gian_bat_dau)} - ${dinhDangThoiGian(hop.thoi_gian_ket_thuc)}`;
  if (elDiaDiem) elDiaDiem.textContent = `Địa điểm / Phòng: ${hop.dia_diem || "Tại phòng họp"}`;
  if (elMaHop) elMaHop.textContent = `Mã cuộc họp: #${hop.ma_lich_hop}`;

  const duLieuQr = JSON.stringify({
    action: "MEETING_CHECKIN",
    meeting_id: hop.ma_lich_hop,
    tieu_de: hop.tieu_de,
    bat_dau: hop.thoi_gian_bat_dau,
    ket_thuc: hop.thoi_gian_ket_thuc
  });

  if (imgQr) {
    imgQr.src = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=${encodeURIComponent(duLieuQr)}`;
  }

  modal.classList.remove("hidden");
}

function dongModalChieuQr() {
  const modal = document.getElementById("modalChieuQr");
  if (modal) modal.classList.add("hidden");
}

function dinhDangThoiGian(isoStr) {
  if (!isoStr) return "--";
  try {
    const d = new Date(isoStr);
    const ngay = String(d.getDate()).padStart(2, "0");
    const thang = String(d.getMonth() + 1).padStart(2, "0");
    const nam = d.getFullYear();
    const gio = String(d.getHours()).padStart(2, "0");
    const phut = String(d.getMinutes()).padStart(2, "0");
    return `${gio}:${phut} ${ngay}/${thang}/${nam}`;
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
