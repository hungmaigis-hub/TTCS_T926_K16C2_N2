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

  return 15;
}

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

async function taiDanhSachDonTuApi() {
  const maHoSo = layMaHoSoHienTai();
  try {
    const res = await fetch(`${duongDanApi}/leave-requests?ma_ho_so=${maHoSo}`);
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.data) && json.data.length > 0) {
        const danhSachTuDb = json.data.map((item) => {
          let loai = "Nghỉ phép";
          let lyDoText = item.ly_do || "";
          if (lyDoText.startsWith("[")) {
            const idx = lyDoText.indexOf("]");
            if (idx > -1) {
              loai = lyDoText.substring(1, idx);
              lyDoText = lyDoText.substring(idx + 1).trim();
            }
          }

          return {
            maDon: `NP-2026-${String(100 + item.ma_don).slice(-3)}`,
            tuNgay: item.tu_ngay,
            denNgay: item.den_ngay,
            soNgay: item.so_ngay || 1,
            loaiNghi: loai,
            lyDo: lyDoText,
            ngayGui: item.ngay_tao ? item.ngay_tao.split("T")[0] : item.tu_ngay,
            trangThai: item.trang_thai || "Chờ duyệt",
          };
        });
        luuDanhSachDon(danhSachTuDb);
        renderBangLichSu();
        return;
      }
    }
  } catch (e) {}
  renderBangLichSu();
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

  const danhSach = layDanhSachDon();
  let soNgayDaDung = 0;
  let soNgayChoDuyet = 0;
  danhSach.forEach((item) => {
    if (item.trangThai === "Đã duyệt") {
      soNgayDaDung += item.soNgay || 1;
    } else if (item.trangThai === "Chờ duyệt") {
      soNgayChoDuyet += item.soNgay || 1;
    }
  });
  const conLai = Math.max(0, 3 - soNgayDaDung);
  const khaDungHienTai = Math.max(0, conLai - soNgayChoDuyet);

  if (diffDays > 3) {
    elNhan.textContent = `${diffDays} ngày (Vượt quá tối đa 3 ngày/kỳ)`;
    elNhan.className = "font-bold text-rose-600 font-mono text-xs";
  } else if (diffDays > conLai) {
    elNhan.textContent = `${diffDays} ngày (Vượt quá quỹ phép còn lại: ${conLai} ngày)`;
    elNhan.className = "font-bold text-rose-600 font-mono text-xs";
  } else if (diffDays > khaDungHienTai) {
    elNhan.textContent = `${diffDays} ngày (Đang có ${soNgayChoDuyet} ngày chờ duyệt, chỉ còn ${khaDungHienTai} ngày khả dụng)`;
    elNhan.className = "font-bold text-amber-600 font-mono text-xs";
  } else {
    elNhan.textContent = `${diffDays} ngày (Hợp lệ)`;
    elNhan.className = "font-bold text-emerald-700 font-mono";
  }
}

function renderBangLichSu() {
  const tbody = document.getElementById("bangLichSuDonNghiPhep");
  if (!tbody) return;

  const danhSach = layDanhSachDon();
  let soNgayDaDung = 0;
  let soNgayChoDuyet = 0;

  tbody.innerHTML = danhSach
    .map((item) => {
      if (item.trangThai === "Đã duyệt") {
        soNgayDaDung += item.soNgay || 1;
      } else if (item.trangThai === "Chờ duyệt") {
        soNgayChoDuyet += item.soNgay || 1;
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
  const conLai = Math.max(0, 3 - soNgayDaDung);

  if (elDaDung) {
    elDaDung.innerHTML = `${String(soNgayDaDung).padStart(2, "0")} <span class="text-base font-medium text-slate-500">ngày</span>`;
  }
  if (elConLai) {
    elConLai.innerHTML = `${String(conLai).padStart(2, "0")} <span class="text-base font-medium text-slate-500">ngày</span>`;
  }

  const nutGui = document.getElementById("nutGuiDon");
  if (nutGui) {
    if (conLai <= 0) {
      nutGui.disabled = true;
      nutGui.classList.add("opacity-50", "cursor-not-allowed");
      nutGui.title = "Đã sử dụng hết 3/3 ngày nghỉ phép quy định";
    } else {
      nutGui.disabled = false;
      nutGui.classList.remove("opacity-50", "cursor-not-allowed");
      nutGui.title = "";
    }
  }
}

async function taiLaiLichSuDon() {
  await taiDanhSachDonTuApi();
  hienThiThongBao(
    "info",
    "Đã làm mới dữ liệu",
    "Bảng theo dõi lịch sử đơn nghỉ phép đã được cập nhật mới nhất từ cơ sở dữ liệu."
  );
}

async function guiDonNghiPhep() {
  const tuNgay = document.getElementById("tuNgay")?.value;
  const denNgay = document.getElementById("denNgay")?.value;
  const loaiNghi = document.getElementById("loaiNghiPhep")?.value || "Nghỉ phép";
  const lyDo = document.getElementById("lyDoNghi")?.value.trim();
  const nutGui = document.getElementById("nutGuiDon");

  if (!tuNgay || !denNgay || !lyDo) {
    hienThiThongBao(
      "error",
      "Thiếu thông tin bắt buộc",
      "Vui lòng điền đầy đủ ngày bắt đầu, ngày kết thúc và lý do chi tiết xin nghỉ phép."
    );
    return;
  }

  const todayStr = new Date().toISOString().split("T")[0];
  if (tuNgay < todayStr) {
    hienThiThongBao(
      "error",
      "Ngày không hợp lệ",
      "Không thể gửi đơn xin nghỉ phép trong quá khứ so với thời điểm hiện tại."
    );
    return;
  }

  if (new Date(denNgay) < new Date(tuNgay)) {
    hienThiThongBao(
      "error",
      "Khoảng thời gian không hợp lệ",
      "Ngày kết thúc nghỉ phép phải lớn hơn hoặc bằng ngày bắt đầu (den_ngay >= tu_ngay)."
    );
    return;
  }

  const dTu = new Date(tuNgay);
  const dDen = new Date(denNgay);
  const diffTime = Math.abs(dDen - dTu);
  const soNgay = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

  if (soNgay > 3) {
    hienThiThongBao(
      "error",
      "Vượt quá hạn mức tối đa",
      `Mỗi kỳ thực tập sinh viên chỉ được nghỉ tối đa 3 ngày phép. Bạn đang xin ${soNgay} ngày.`
    );
    return;
  }

  const danhSach = layDanhSachDon();
  let soNgayDaDung = 0;
  let soNgayChoDuyet = 0;
  danhSach.forEach((item) => {
    if (item.trangThai === "Đã duyệt") {
      soNgayDaDung += item.soNgay || 1;
    } else if (item.trangThai === "Chờ duyệt") {
      soNgayChoDuyet += item.soNgay || 1;
    }
  });
  const conLai = Math.max(0, 3 - soNgayDaDung);
  const khaDungHienTai = Math.max(0, conLai - soNgayChoDuyet);

  if (conLai <= 0) {
    hienThiThongBao(
      "error",
      "Hết hạn mức nghỉ phép",
      "Bạn đã sử dụng hết hạn mức 3/3 ngày nghỉ phép của kỳ thực tập. Chỉ các đơn đã được duyệt mới tính trừ ngày phép."
    );
    return;
  }

  if (soNgay > conLai) {
    hienThiThongBao(
      "error",
      "Vượt quá quỹ phép còn lại",
      `Bạn xin nghỉ ${soNgay} ngày, nhưng hạn mức nghỉ phép còn lại chỉ còn ${conLai} ngày (trên tổng 3 ngày phép). Vui lòng điều chỉnh lại ngày nghỉ.`
    );
    return;
  }

  if (soNgay > khaDungHienTai) {
    hienThiThongBao(
      "error",
      "Đơn chờ duyệt chiếm quỹ phép",
      `Bạn hiện có ${soNgayChoDuyet} ngày nghỉ đang chờ xét duyệt và ${soNgayDaDung} ngày đã duyệt (tổng ${soNgayDaDung + soNgayChoDuyet}/3 ngày). Bạn chỉ có thể nộp thêm tối đa ${khaDungHienTai} ngày nghỉ nữa.`
    );
    return;
  }

  const trungLap = danhSach.find((item) => {
    if (item.trangThai === "Từ chối") return false;
    return item.tuNgay <= denNgay && item.denNgay >= tuNgay;
  });
  if (trungLap) {
    hienThiThongBao(
      "error",
      "Trùng lặp khoảng thời gian nghỉ",
      `Bạn đã có đơn ${trungLap.maDon} (${trungLap.tuNgay} đến ${trungLap.denNgay}, trạng thái: ${trungLap.trangThai}) trùng hoặc giao thoa với khoảng thời gian bạn vừa chọn. Vui lòng không nộp trùng lặp.`
    );
    return;
  }

  const oldBtnHtml = nutGui ? nutGui.innerHTML : "";
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang gửi đơn lên HR...</span>`;
  }

  const maHoSo = layMaHoSoHienTai();

  try {
    const payload = {
      ma_ho_so: maHoSo,
      tu_ngay: tuNgay,
      den_ngay: denNgay,
      ly_do: `[${loaiNghi}] ${lyDo}`,
      trang_thai: "Chờ duyệt",
    };

    const res = await fetch(`${duongDanApi}/leave-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const resData = await res.json().catch(() => ({}));

    if (!res.ok) {
      let errMsg = "Không thể gửi đơn xin nghỉ phép.";
      if (typeof resData.detail === "string") {
        errMsg = resData.detail;
      } else if (Array.isArray(resData.detail)) {
        errMsg = resData.detail.map((e) => e.msg || e.message).join(", ");
      }
      hienThiThongBao("error", "Lỗi từ chối từ hệ thống", errMsg);
      return;
    }

    document.getElementById("formDangKyNghiPhep")?.reset();
    setTimeout(tinhSoNgayNghi, 50);
    await taiDanhSachDonTuApi();

    hienThiThongBao(
      "success",
      "Gửi đơn xin nghỉ phép thành công!",
      `Đơn xin nghỉ phép (${soNgay} ngày, từ ${tuNgay} đến ${denNgay}) đã được chuyển đến bộ phận Nhân sự và Mentor phụ trách để xét duyệt.`
    );
  } catch (err) {
    hienThiThongBao(
      "error",
      "Mất kết nối máy chủ",
      `Không thể kết nối đến máy chủ (${err.message || "Lỗi mạng"}). Vui lòng kiểm tra lại dịch vụ Backend.`
    );
  } finally {
    if (nutGui) {
      nutGui.disabled = false;
      nutGui.innerHTML = oldBtnHtml;
    }
  }
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
  taiDanhSachDonTuApi();
});
