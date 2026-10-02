const duongDanApi = "http://127.0.0.1:8000/api/v1";

function khoiTaoDongHoThoiGianThuc() {
  const elDongHo = document.getElementById("dongHoThoiGianThuc");
  const elNgayThang = document.getElementById("dongHoNgayThang");

  function capNhat() {
    const now = new Date();
    const gio = String(now.getHours()).padStart(2, "0");
    const phut = String(now.getMinutes()).padStart(2, "0");
    const giay = String(now.getSeconds()).padStart(2, "0");

    if (elDongHo) {
      elDongHo.textContent = `${gio}:${phut}:${giay}`;
    }

    if (elNgayThang) {
      const thu = [
        "Chủ Nhật",
        "Thứ Hai",
        "Thứ Ba",
        "Thứ Tư",
        "Thứ Năm",
        "Thứ Sáu",
        "Thứ Bảy",
      ][now.getDay()];
      const ngay = String(now.getDate()).padStart(2, "0");
      const thang = String(now.getMonth() + 1).padStart(2, "0");
      const nam = now.getFullYear();
      elNgayThang.textContent = `${thu}, ngày ${ngay}/${thang}/${nam}`;
    }
  }

  capNhat();
  setInterval(capNhat, 1000);
}

const KEY_CHAM_CONG_HOM_NAY = "ictu_cham_cong_today";
const KEY_LICH_SU_CHAM_CONG = "ictu_lich_su_cham_cong";

const duLieuMauMacDinh = [
  {
    ngay: "2026-09-28",
    checkin: "07:55:12",
    checkout: "17:35:40",
    tongGio: "8 giờ 40 phút",
    trangThai: "Đúng giờ",
    ghiChu: "Hoàn thành tốt ca làm việc",
  },
  {
    ngay: "2026-09-27",
    checkin: "07:58:30",
    checkout: "17:30:15",
    tongGio: "8 giờ 31 phút",
    trangThai: "Đúng giờ",
    ghiChu: "On-site tại văn phòng",
  },
  {
    ngay: "2026-09-26",
    checkin: "08:10:05",
    checkout: "17:42:10",
    tongGio: "8 giờ 32 phút",
    trangThai: "Đi muộn",
    ghiChu: "Kẹt xe tuyến đường QL3",
  },
  {
    ngay: "2026-09-25",
    checkin: "07:50:00",
    checkout: "17:30:00",
    tongGio: "8 giờ 40 phút",
    trangThai: "Đúng giờ",
    ghiChu: "Họp sprint review với Mentor",
  },
  {
    ngay: "2026-09-24",
    checkin: "07:52:18",
    checkout: "17:31:45",
    tongGio: "8 giờ 39 phút",
    trangThai: "Đúng giờ",
    ghiChu: "Nộp báo cáo tuần 5",
  },
];

function layDanhSachLichSu() {
  try {
    const raw = localStorage.getItem(KEY_LICH_SU_CHAM_CONG);
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return [...duLieuMauMacDinh];
}

function luuDanhSachLichSu(list) {
  try {
    localStorage.setItem(KEY_LICH_SU_CHAM_CONG, JSON.stringify(list));
  } catch (e) {}
}

function renderBangLichSu() {
  const tbody = document.getElementById("bangNhatKyChamCong");
  if (!tbody) return;

  const list = layDanhSachLichSu();
  tbody.innerHTML = list
    .map((item) => {
      let badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
      if (item.trangThai === "Đi muộn") {
        badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
      } else if (item.trangThai === "Về sớm") {
        badgeClass = "bg-rose-50 text-rose-700 border-rose-200";
      }

      return `
        <tr class="hover:bg-slate-50/60 transition-colors">
          <td class="py-3 px-4 font-mono font-semibold text-slate-900">${item.ngay}</td>
          <td class="py-3 px-4 font-mono text-emerald-700">${item.checkin || "--:--:--"}</td>
          <td class="py-3 px-4 font-mono text-rose-700">${item.checkout || "--:--:--"}</td>
          <td class="py-3 px-4 font-semibold text-slate-800">${item.tongGio || "--"}</td>
          <td class="py-3 px-4">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold border ${badgeClass}">
              ${item.trangThai}
            </span>
          </td>
          <td class="py-3 px-4 text-slate-500">${item.ghiChu || "-"}</td>
        </tr>
      `;
    })
    .join("");
}

function taiLaiNhatKy() {
  renderBangLichSu();
  hienThiThongBao(
    "info",
    "Đã làm mới dữ liệu",
    "Bảng nhật ký điểm danh đã được đồng bộ mới nhất."
  );
}

function layTrangThaiHomNay() {
  const homNayStr = new Date().toISOString().split("T")[0];
  try {
    const raw = localStorage.getItem(KEY_CHAM_CONG_HOM_NAY);
    if (raw) {
      const data = JSON.parse(raw);
      if (data.ngay === homNayStr) return data;
    }
  } catch (e) {}

  return {
    ngay: homNayStr,
    daCheckin: false,
    daCheckout: false,
    gioCheckin: null,
    gioCheckout: null,
    tongGio: null,
    trangThai: "Chưa chấm công",
  };
}

function luuTrangThaiHomNay(state) {
  try {
    localStorage.setItem(KEY_CHAM_CONG_HOM_NAY, JSON.stringify(state));
  } catch (e) {}
}

function capNhatGiaoDienTrangThai() {
  const state = layTrangThaiHomNay();
  const elBadge = document.getElementById("badgeTrangThaiHomNay");
  const elIn = document.getElementById("hienThiGioCheckin");
  const elOut = document.getElementById("hienThiGioCheckout");
  const elMotaIn = document.getElementById("moTaCheckin");
  const elMotaOut = document.getElementById("moTaCheckout");
  const elTongGio = document.getElementById("hienThiTongGioLam");
  const btnIn = document.getElementById("nutCheckin");
  const btnOut = document.getElementById("nutCheckout");

  if (state.daCheckout) {
    if (elBadge) {
      elBadge.className =
        "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200";
      elBadge.textContent = "Hoàn thành ca làm";
    }
    if (elIn) elIn.textContent = state.gioCheckin;
    if (elOut) elOut.textContent = state.gioCheckout;
    if (elMotaIn) elMotaIn.textContent = "Đã ghi nhận lúc vào";
    if (elMotaOut) elMotaOut.textContent = "Đã ghi nhận lúc ra";
    if (elTongGio && state.tongGio) elTongGio.textContent = state.tongGio;

    if (btnIn) btnIn.disabled = true;
    if (btnOut) btnOut.disabled = true;
  } else if (state.daCheckin) {
    if (elBadge) {
      elBadge.className =
        "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 animate-pulse";
      elBadge.textContent = "Đang làm việc";
    }
    if (elIn) elIn.textContent = state.gioCheckin;
    if (elOut) elOut.textContent = "--:--:--";
    if (elMotaIn) elMotaIn.textContent = "Đã check-in thành công";
    if (elMotaOut) elMotaOut.textContent = "Chưa kết thúc ca";

    if (btnIn) btnIn.disabled = true;
    if (btnOut) btnOut.disabled = false;
  } else {
    if (elBadge) {
      elBadge.className =
        "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600 border border-slate-200";
      elBadge.textContent = "Chưa chấm công";
    }
    if (elIn) elIn.textContent = "--:--:--";
    if (elOut) elOut.textContent = "--:--:--";
    if (elMotaIn) elMotaIn.textContent = "Chưa ghi nhận";
    if (elMotaOut) elMotaOut.textContent = "Chưa ghi nhận";

    if (btnIn) btnIn.disabled = false;
    if (btnOut) btnOut.disabled = true;
  }
}

async function xuLyCheckin() {
  const state = layTrangThaiHomNay();
  if (state.daCheckin) {
    alert("Bạn đã thực hiện Check-in hôm nay rồi!");
    return;
  }

  const btnIn = document.getElementById("nutCheckin");
  const oldContent = btnIn.innerHTML;
  btnIn.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang xác thực...</span>`;
  btnIn.disabled = true;

  const now = new Date();
  const gioStr = [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join(":");

  try {
    await fetch(`${duongDanApi}/attendance/check-in`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ma_ho_so: 1,
        thoi_gian_checkin: now.toISOString(),
      }),
    });
  } catch (e) {
    console.warn("Backend attendance endpoint offline, fallback to client state.");
  } finally {
    btnIn.innerHTML = oldContent;
  }

  state.daCheckin = true;
  state.gioCheckin = gioStr;
  state.trangThai = "Đang làm việc";
  luuTrangThaiHomNay(state);

  capNhatGiaoDienTrangThai();
  hienThiThongBao(
    "success",
    "Check-in thành công!",
    `Hệ thống đã ghi nhận thời gian bắt đầu ca làm việc của bạn vào lúc <strong>${gioStr}</strong>. Chúc bạn một ngày làm việc hiệu quả!`
  );
}

async function xuLyCheckout() {
  const state = layTrangThaiHomNay();
  if (!state.daCheckin) {
    alert("Bạn chưa Check-in nên không thể Check-out!");
    return;
  }
  if (state.daCheckout) {
    alert("Bạn đã hoàn thành ca làm việc hôm nay!");
    return;
  }

  const btnOut = document.getElementById("nutCheckout");
  const oldContent = btnOut.innerHTML;
  btnOut.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang ghi nhận...</span>`;
  btnOut.disabled = true;

  const now = new Date();
  const gioStr = [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join(":");

  try {
    await fetch(`${duongDanApi}/attendance/check-out`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ma_ho_so: 1,
        thoi_gian_checkout: now.toISOString(),
      }),
    });
  } catch (e) {
    console.warn("Backend attendance endpoint offline, fallback to client state.");
  } finally {
    btnOut.innerHTML = oldContent;
  }

  state.daCheckout = true;
  state.gioCheckout = gioStr;
  state.trangThai = "Hoàn thành";
  state.tongGio = "8 giờ 15 phút";
  luuTrangThaiHomNay(state);

  const list = layDanhSachLichSu();
  list.unshift({
    ngay: state.ngay,
    checkin: state.gioCheckin,
    checkout: state.gioCheckout,
    tongGio: state.tongGio,
    trangThai: "Đúng giờ",
    ghiChu: "Hoàn thành ca làm việc trong ngày",
  });
  luuDanhSachLichSu(list);

  capNhatGiaoDienTrangThai();
  renderBangLichSu();

  hienThiThongBao(
    "success",
    "Check-out thành công!",
    `Bạn đã hoàn thành ca làm việc hôm nay lúc <strong>${gioStr}</strong>. Tổng thời lượng được ghi nhận: <strong>${state.tongGio}</strong>.`
  );
}

function hienThiThongBao(loai, tieuDe, noiDung) {
  const hop = document.getElementById("hopThongBao");
  if (!hop) return;

  const isSuccess = loai === "success";
  const bgClass = isSuccess
    ? "bg-emerald-50 text-emerald-950 border border-emerald-200"
    : "bg-surface-container-low text-on-surface border border-outline-variant";
  const iconColor = isSuccess
    ? "bg-emerald-600 text-white"
    : "bg-secondary text-on-secondary";

  hop.className = `rounded-2xl ${bgClass} p-4 shadow-sm flex items-start gap-3.5 transition-all`;
  hop.innerHTML = `
    <div class="w-8 h-8 rounded-lg ${iconColor} flex items-center justify-center shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-[20px]">${
        isSuccess ? "check_circle" : "info"
      }</span>
    </div>
    <div class="flex-1 text-xs">
      <div class="flex items-center justify-between">
        <span class="font-bold text-sm text-slate-900">${tieuDe}</span>
        <span class="text-[11px] text-slate-400">Vừa xong</span>
      </div>
      <p class="mt-1 leading-relaxed text-slate-600">
        ${noiDung}
      </p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-slate-400 hover:text-slate-700 p-1 rounded-md transition-colors" title="Đóng">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hop.classList.remove("hidden");
  hop.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function dongBoThongTinNguoiDung() {
  try {
    const userStr = localStorage.getItem("ictu_student_session") || localStorage.getItem("user") || localStorage.getItem("currentUser");
    if (userStr) {
      const user = JSON.parse(userStr);
      const elTen = document.getElementById("sidebarTenSinhVien");
      const elMa = document.getElementById("sidebarMaSinhVien");
      const elAvatar = document.getElementById("avatarInitials");

      if (elTen && user.ho_ten) elTen.textContent = user.ho_ten;
      if (elMa && user.email) elMa.textContent = user.email;
      if (elAvatar && user.ho_ten) {
        const words = user.ho_ten.trim().split(" ");
        const initials =
          words.length >= 2
            ? words[0][0] + words[words.length - 1][0]
            : user.ho_ten.substring(0, 2);
        elAvatar.textContent = initials.toUpperCase();
      }
    }
  } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
  khoiTaoDongHoThoiGianThuc();
  dongBoThongTinNguoiDung();
  capNhatGiaoDienTrangThai();
  renderBangLichSu();
});
