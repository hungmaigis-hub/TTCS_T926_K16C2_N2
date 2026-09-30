const duongDanApi = "http://127.0.0.1:8000/api/v1";
const KEY_DON_NGHI_PHEP = "ictu_danh_sach_don_nghi_phep";

const duLieuDonMau = [
  {
    maDon: "NP-2026-001",
    tuNgay: "2026-09-18",
    denNgay: "2026-09-18",
    soNgay: 1,
    loaiNghi: "Nghỉ ốm / Khám sức khỏe",
    lyDo: "Khám sức khỏe tổng quát định kỳ tại Bệnh viện A Thái Nguyên.",
    ngayGui: "2026-09-17",
    trangThai: "Đã duyệt",
  },
];

function layDanhSachDon() {
  try {
    const raw = localStorage.getItem(KEY_DON_NGHI_PHEP);
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return [...duLieuDonMau];
}

function luuDanhSachDon(danhSach) {
  try {
    localStorage.setItem(KEY_DON_NGHI_PHEP, JSON.stringify(danhSach));
  } catch (e) {}
}

function tinhSoNgayNghi() {
  const elTuNgay = document.getElementById("tuNgay");
  const elDenNgay = document.getElementById("denNgay");
  const elNhan = document.getElementById("nhanSoNgayNghi");

  if (!elTuNgay || !elDenNgay || !elNhan) return;

  const tu = elTuNgay.value;
  const den = elDenNgay.value;

  if (!tu || !den) {
    elNhan.textContent = "0 ngày";
    return;
  }

  const dTu = new Date(tu);
  const dDen = new Date(den);

  if (dDen < dTu) {
    elNhan.textContent = "Ngày không hợp lệ";
    elNhan.className = "font-bold text-rose-600 font-mono";
    return;
  }

  const diffTime = Math.abs(dDen - dTu);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

  elNhan.textContent = `${diffDays} ngày`;
  elNhan.className = "font-bold text-emerald-700 font-mono";
}

function renderBangLichSu() {
  const tbody = document.getElementById("bangLichSuDonNghiPhep");
  if (!tbody) return;

  const danhSach = layDanhSachDon();
  let soNgayDaDung = 0;

  tbody.innerHTML = danhSach
    .map((item) => {
      if (item.trangThai === "Đã duyệt") {
        soNgayDaDung += item.soNgay || 1;
      }

      let badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
      if (item.trangThai === "Đã duyệt") {
        badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
      } else if (item.trangThai === "Từ chối") {
        badgeClass = "bg-rose-50 text-rose-700 border-rose-200";
      }

      return `
        <tr class="hover:bg-slate-50/60 transition-colors">
          <td class="py-3 px-4 font-mono font-bold text-slate-900">${item.maDon}</td>
          <td class="py-3 px-4 font-mono text-slate-700">
            ${item.tuNgay} <span class="text-slate-400">➔</span> ${item.denNgay}
          </td>
          <td class="py-3 px-4 font-bold text-slate-800 font-mono">${item.soNgay} ngày</td>
          <td class="py-3 px-4 font-semibold text-slate-700">${item.loaiNghi}</td>
          <td class="py-3 px-4 text-slate-600 max-w-xs truncate" title="${item.lyDo}">${item.lyDo}</td>
          <td class="py-3 px-4 font-mono text-slate-500">${item.ngayGui}</td>
          <td class="py-3 px-4">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold border ${badgeClass}">
              ${item.trangThai}
            </span>
          </td>
        </tr>
      `;
    })
    .join("");

  const elDaDung = document.getElementById("soNgayDaDung");
  const elConLai = document.getElementById("soNgayConLai");
  if (elDaDung) {
    elDaDung.innerHTML = `${String(soNgayDaDung).padStart(2, "0")} <span class="text-base font-medium text-slate-500">ngày</span>`;
  }
  if (elConLai) {
    const conLai = Math.max(0, 3 - soNgayDaDung);
    elConLai.innerHTML = `${String(conLai).padStart(2, "0")} <span class="text-base font-medium text-slate-500">ngày</span>`;
  }
}

function taiLaiLichSuDon() {
  renderBangLichSu();
  hienThiThongBao(
    "info",
    "Đã làm mới dữ liệu",
    "Bảng theo dõi lịch sử đơn nghỉ phép đã được cập nhật mới nhất."
  );
}

async function guiDonNghiPhep() {
  const tuNgay = document.getElementById("tuNgay")?.value;
  const denNgay = document.getElementById("denNgay")?.value;
  const loaiNghi = document.getElementById("loaiNghiPhep")?.value;
  const lyDo = document.getElementById("lyDoNghi")?.value.trim();
  const nutGui = document.getElementById("nutGuiDon");

  if (!tuNgay || !denNgay || !lyDo) {
    alert("Vui lòng điền đầy đủ các thông tin bắt buộc!");
    return;
  }

  if (new Date(denNgay) < new Date(tuNgay)) {
    alert("Ngày kết thúc nghỉ phép không được nhỏ hơn ngày bắt đầu!");
    return;
  }

  const dTu = new Date(tuNgay);
  const dDen = new Date(denNgay);
  const diffTime = Math.abs(dDen - dTu);
  const soNgay = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

  const oldBtnHtml = nutGui ? nutGui.innerHTML : "";
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang gửi đơn lên HR...</span>`;
  }

  const homNayStr = new Date().toISOString().split("T")[0];
  const maDonMoi = `NP-2026-${String(Math.floor(100 + Math.random() * 900))}`;

  try {
    const payload = {
      ma_ho_so: 1,
      tu_ngay: tuNgay,
      den_ngay: denNgay,
      ly_do: `[${loaiNghi}] ${lyDo}`,
      trang_thai: "Chờ duyệt",
    };

    await fetch(`${duongDanApi}/leave-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.warn("Backend leave-requests offline, fallback lưu cục bộ.");
  } finally {
    if (nutGui) {
      nutGui.disabled = false;
      nutGui.innerHTML = oldBtnHtml;
    }
  }

  const danhSach = layDanhSachDon();
  danhSach.unshift({
    maDon: maDonMoi,
    tuNgay: tuNgay,
    denNgay: denNgay,
    soNgay: soNgay,
    loaiNghi: loaiNghi,
    lyDo: lyDo,
    ngayGui: homNayStr,
    trangThai: "Chờ duyệt",
  });
  luuDanhSachDon(danhSach);

  document.getElementById("formDangKyNghiPhep")?.reset();
  setTimeout(tinhSoNgayNghi, 50);
  renderBangLichSu();

  hienThiThongBao(
    "success",
    "Gửi đơn xin nghỉ phép thành công!",
    `Đơn xin nghỉ phép mã <strong>${maDonMoi}</strong> (${soNgay} ngày, từ ${tuNgay} đến ${denNgay}) đã được tiếp nhận và chuyển đến phòng Nhân sự (HR) phê duyệt.`
  );
}

function datLaiFormNghiPhep() {
  document.getElementById("formDangKyNghiPhep")?.reset();
  setTimeout(tinhSoNgayNghi, 50);
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
    const userStr = localStorage.getItem("currentUser");
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
  const homNay = new Date().toISOString().split("T")[0];
  const elTu = document.getElementById("tuNgay");
  const elDen = document.getElementById("denNgay");
  if (elTu) {
    elTu.value = homNay;
    elTu.min = homNay;
  }
  if (elDen) {
    elDen.value = homNay;
    elDen.min = homNay;
  }

  tinhSoNgayNghi();
  dongBoThongTinNguoiDung();
  renderBangLichSu();
});
