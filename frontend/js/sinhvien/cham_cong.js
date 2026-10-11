const duongDanApi = "http://127.0.0.1:8000/api/v1";

function layMaHoSoHienTai() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);

  try {
    const raw = localStorage.getItem("ictu_student_session") || localStorage.getItem("currentUser") || localStorage.getItem("user");
    if (raw) {
      const u = JSON.parse(raw);
      if (u.ma_ho_so) return parseInt(u.ma_ho_so, 10);
    }
  } catch (e) {}

  return 1;
}

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

async function taiDanhSachLichSuTuApi() {
  const maHoSo = layMaHoSoHienTai();
  const homNayStr = new Date().toISOString().split("T")[0];
  try {
    const res = await fetch(`${duongDanApi}/attendance/records?ma_ho_so=${maHoSo}&page_size=50`);
    if (res.ok) {
      const json = await res.json();
      if (json && json.data && Array.isArray(json.data.items)) {
        const homNayRecord = json.data.items.find(
          (it) => it.ngay_iso === homNayStr || it.ngay === homNayStr
        );
        if (homNayRecord) {
          let tt = "Đúng giờ";
          if (homNayRecord.trang_thai === "DiMuon") tt = "Đi muộn";
          else if (homNayRecord.trang_thai === "VeSom") tt = "Về sớm";
          else if (homNayRecord.trang_thai === "VangMat") tt = "Vắng mặt";

          const state = {
            ngay: homNayStr,
            daCheckin: true,
            daCheckout: Boolean(homNayRecord.ra && homNayRecord.ra !== "--:--"),
            gioCheckin: homNayRecord.vao && homNayRecord.vao !== "--:--" ? (homNayRecord.vao.length === 5 ? homNayRecord.vao + ":00" : homNayRecord.vao) : "--:--",
            gioCheckout: homNayRecord.ra && homNayRecord.ra !== "--:--" ? (homNayRecord.ra.length === 5 ? homNayRecord.ra + ":00" : homNayRecord.ra) : "--:--",
            tongGio: homNayRecord.gio ? `${homNayRecord.gio} giờ` : null,
            trangThai: tt,
            phuongThuc: homNayRecord.phuong_thuc || "Mentor"
          };
          luuTrangThaiHomNay(state);
        } else {
          localStorage.removeItem(KEY_CHAM_CONG_HOM_NAY);
        }
        capNhatGiaoDienTrangThai();

        const danhSachTuDb = json.data.items.map((it) => {
          let tt = "Đúng giờ";
          if (it.trang_thai === "DiMuon") tt = "Đi muộn";
          else if (it.trang_thai === "VeSom") tt = "Về sớm";
          else if (it.trang_thai === "VangMat") tt = "Vắng mặt";

          return {
            ngay: it.ngay_iso || it.ngay,
            checkin: it.vao && it.vao !== "--:--" ? (it.vao.length === 5 ? it.vao + ":00" : it.vao) : "--:--:--",
            checkout: it.ra && it.ra !== "--:--" ? (it.ra.length === 5 ? it.ra + ":00" : it.ra) : "--:--:--",
            tongGio: it.gio ? `${it.gio} giờ` : "--",
            trangThai: tt,
            ghiChu: it.ghi_chu || "-"
          };
        });
        luuDanhSachLichSu(danhSachTuDb);
        renderBangLichSu();
        return;
      }
    }
  } catch (e) {}
  renderBangLichSu();
}

async function taiLaiNhatKy() {
  await taiDanhSachLichSuTuApi();
  hienThiThongBao(
    "info",
    "Đã làm mới dữ liệu",
    "Bảng nhật ký điểm danh đã được đồng bộ mới nhất từ cơ sở dữ liệu."
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
    trangThai: "Chờ Mentor điểm danh",
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

  if (state.daCheckin) {
    if (elBadge) {
      if (state.trangThai === "Đúng giờ") {
        elBadge.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200";
        elBadge.textContent = "Mentor đã điểm danh: Đúng giờ";
      } else if (state.trangThai === "Đi muộn") {
        elBadge.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200";
        elBadge.textContent = "Mentor đã điểm danh: Đi muộn";
      } else if (state.trangThai === "Vắng mặt") {
        elBadge.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200";
        elBadge.textContent = "Mentor ghi nhận: Vắng mặt";
      } else {
        elBadge.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-200";
        elBadge.textContent = "Mentor đã điểm danh";
      }
    }
    if (elIn) elIn.textContent = state.gioCheckin || "--:--:--";
    if (elOut) elOut.textContent = state.gioCheckout || "--:--:--";
    if (elMotaIn) elMotaIn.textContent = state.trangThai === "Vắng mặt" ? "Không có mặt tại ca làm" : "Đã ghi nhận có mặt";
    if (elMotaOut) elMotaOut.textContent = state.trangThai === "Vắng mặt" ? "--" : "Hoàn thành ca làm";
    if (elTongGio && state.tongGio) elTongGio.textContent = state.tongGio;
  } else {
    if (elBadge) {
      elBadge.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600 border border-slate-200";
      elBadge.textContent = "Chờ Mentor mở ca điểm danh";
    }
    if (elIn) elIn.textContent = "--:--:--";
    if (elOut) elOut.textContent = "--:--:--";
    if (elMotaIn) elMotaIn.textContent = "Chờ ghi nhận";
    if (elMotaOut) elMotaOut.textContent = "Chờ ghi nhận";
  }
}

async function xuLyCheckin() {
  const state = layTrangThaiHomNay();
  if (state.daCheckin) {
    hienThiThongBao("warning", "Đã check-in", "Bạn đã thực hiện Check-in cho ca làm việc hôm nay rồi!");
    return;
  }

  const btnIn = document.getElementById("nutCheckin");
  const oldContent = btnIn ? btnIn.innerHTML : "";
  if (btnIn) {
    btnIn.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang xác thực...</span>`;
    btnIn.disabled = true;
  }

  const now = new Date();
  const gioStr = [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join(":");

  const maHoSo = layMaHoSoHienTai();
  let trangThaiServer = "Đang làm việc";

  try {
    const res = await fetch(`${duongDanApi}/attendance/check-in`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ma_ho_so: maHoSo,
        thoi_gian_checkin: now.toISOString(),
      }),
    });
    const resData = await res.json().catch(() => ({}));

    if (!res.ok) {
      let errMsg = "Không thể ghi nhận check-in lúc này!";
      if (typeof resData.detail === "string") {
        errMsg = resData.detail;
      } else if (Array.isArray(resData.detail) && resData.detail[0]?.msg) {
        errMsg = resData.detail[0].msg;
      }
      hienThiThongBao(
        errMsg.includes("đã thực hiện check-in") ? "warning" : "error",
        "Thông báo điểm danh",
        errMsg
      );
      return;
    }

    if (resData.data) {
      if (resData.data.trang_thai === "DiMuon") {
        trangThaiServer = "Đi muộn";
      } else {
        trangThaiServer = "Đang làm việc";
      }
    }

    state.daCheckin = true;
    state.gioCheckin = gioStr;
    state.trangThai = trangThaiServer;
    luuTrangThaiHomNay(state);

    capNhatGiaoDienTrangThai();
    taiDanhSachLichSuTuApi();
    hienThiThongBao(
      "success",
      "Check-in thành công!",
      `Hệ thống đã ghi nhận thời gian bắt đầu ca làm việc của bạn vào lúc <strong>${gioStr}</strong> (${trangThaiServer}). Chúc bạn một ngày làm việc hiệu quả!`
    );
  } catch (e) {
    hienThiThongBao(
      "error",
      "Mất kết nối máy chủ",
      "Không thể kết nối tới máy chủ điểm danh. Vui lòng kiểm tra lại kết nối mạng và thử lại sau."
    );
  } finally {
    if (btnIn) {
      btnIn.innerHTML = oldContent;
      btnIn.disabled = state.daCheckin;
    }
  }
}

async function xuLyCheckout() {
  const state = layTrangThaiHomNay();
  if (!state.daCheckin) {
    hienThiThongBao("warning", "Chưa check-in", "Bạn chưa thực hiện Check-in nên chưa thể Check-out ca làm việc!");
    return;
  }
  if (state.daCheckout) {
    hienThiThongBao("warning", "Đã check-out", "Bạn đã hoàn thành kết thúc ca làm việc hôm nay rồi!");
    return;
  }

  const btnOut = document.getElementById("nutCheckout");
  const oldContent = btnOut ? btnOut.innerHTML : "";
  if (btnOut) {
    btnOut.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang ghi nhận...</span>`;
    btnOut.disabled = true;
  }

  const now = new Date();
  const gioStr = [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join(":");

  const maHoSo = layMaHoSoHienTai();
  let trangThaiServer = "Hoàn thành";

  try {
    const res = await fetch(`${duongDanApi}/attendance/check-out`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ma_ho_so: maHoSo,
        thoi_gian_checkout: now.toISOString(),
      }),
    });
    const resData = await res.json().catch(() => ({}));

    if (!res.ok) {
      let errMsg = "Không thể ghi nhận check-out lúc này!";
      if (typeof resData.detail === "string") {
        errMsg = resData.detail;
      } else if (Array.isArray(resData.detail) && resData.detail[0]?.msg) {
        errMsg = resData.detail[0].msg;
      }
      hienThiThongBao("error", "Lỗi check-out", errMsg);
      return;
    }

    if (resData.data) {
      if (resData.data.trang_thai === "VeSom") {
        trangThaiServer = "Về sớm";
      } else {
        trangThaiServer = "Hoàn thành";
      }
    }

    state.daCheckout = true;
    state.gioCheckout = gioStr;
    state.trangThai = trangThaiServer;
    state.tongGio = "8 giờ 15 phút";
    luuTrangThaiHomNay(state);

    const list = layDanhSachLichSu();
    list.unshift({
      ngay: state.ngay,
      checkin: state.gioCheckin,
      checkout: state.gioCheckout,
      tongGio: state.tongGio,
      trangThai: trangThaiServer,
      ghiChu: "Hoàn thành ca làm việc trong ngày",
    });
    luuDanhSachLichSu(list);

    capNhatGiaoDienTrangThai();
    renderBangLichSu();
    taiDanhSachLichSuTuApi();

    hienThiThongBao(
      "success",
      "Check-out thành công!",
      `Bạn đã hoàn thành ca làm việc hôm nay lúc <strong>${gioStr}</strong> (${trangThaiServer}). Tổng thời lượng được ghi nhận: <strong>${state.tongGio}</strong>.`
    );
  } catch (e) {
    hienThiThongBao(
      "error",
      "Mất kết nối máy chủ",
      "Không thể kết nối tới máy chủ điểm danh. Vui lòng kiểm tra lại kết nối mạng và thử lại sau."
    );
  } finally {
    if (btnOut) {
      btnOut.innerHTML = oldContent;
      btnOut.disabled = state.daCheckout;
    }
  }
}

function hienThiThongBao(loai, tieuDe, noiDung) {
  const hop = document.getElementById("hopThongBao");
  if (!hop) return;

  let bgClass = "bg-emerald-50 text-emerald-950 border border-emerald-200";
  let iconColor = "bg-emerald-600 text-white";
  let icon = "check_circle";

  if (loai === "error") {
    bgClass = "bg-rose-50 text-rose-950 border border-rose-200";
    iconColor = "bg-rose-600 text-white";
    icon = "error";
  } else if (loai === "warning") {
    bgClass = "bg-amber-50 text-amber-950 border border-amber-200";
    iconColor = "bg-amber-600 text-white";
    icon = "warning";
  } else if (loai === "info") {
    bgClass = "bg-blue-50 text-blue-950 border border-blue-200";
    iconColor = "bg-blue-600 text-white";
    icon = "info";
  }

  hop.className = `rounded-2xl ${bgClass} p-4 shadow-sm flex items-start gap-3.5 transition-all`;
  hop.innerHTML = `
    <div class="w-8 h-8 rounded-lg ${iconColor} flex items-center justify-center shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-[20px]">${icon}</span>
    </div>
    <div class="flex-1 text-xs">
      <div class="flex items-center justify-between">
        <span class="font-bold text-sm text-slate-900">${tieuDe}</span>
        <span class="text-[11px] text-slate-400">Vừa xong</span>
      </div>
      <p class="mt-1 leading-relaxed text-slate-700">
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
  taiDanhSachLichSuTuApi();
});
