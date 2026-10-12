const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let danhSachBaoCaoGoc = [];
let danhSachNhiemVuGoc = [];
let tabBoLocHienTai = "tat_ca";

function layIdSinhVien() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);
  try {
    const raw = localStorage.getItem("ictu_student_session") || localStorage.getItem("currentUser") || localStorage.getItem("user");
    if (raw) {
      const u = JSON.parse(raw);
      if (u.ma_ho_so) return parseInt(u.ma_ho_so, 10);
      if (u.id) return parseInt(u.id, 10);
    }
  } catch (e) {}
  return 15;
}

function dinhDangNgayGioVN(isoString) {
  if (!isoString) return "--";
  try {
    const d = new Date(isoString);
    if (!isNaN(d.getTime())) {
      const gio = String(d.getHours()).padStart(2, "0");
      const phut = String(d.getMinutes()).padStart(2, "0");
      const ngay = String(d.getDate()).padStart(2, "0");
      const thang = String(d.getMonth() + 1).padStart(2, "0");
      const nam = d.getFullYear();
      return `${gio}:${phut} - ${ngay}/${thang}/${nam}`;
    }
  } catch (e) {}
  return isoString;
}

function dongBoSidebar(hoTen, email, lop) {
  if (!hoTen) return;
  const elTen = document.getElementById("sidebarTenSinhVien");
  if (elTen) elTen.textContent = hoTen;
  const elAvatar = document.getElementById("avatarInitials");
  if (elAvatar) {
    const words = hoTen.trim().split(/\s+/);
    elAvatar.textContent = words.length >= 2
      ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
      : hoTen.substring(0, 2).toUpperCase();
  }
  const elMa = document.getElementById("sidebarMaSinhVien");
  if (elMa) {
    const maSV = email && email.includes("@") ? email.split("@")[0].toUpperCase() : "DTC2051060124";
    elMa.textContent = `${maSV} - ${lop || "K19"}`;
  }
}

function hienThiThongBaoChung(loai, tieuDe, noiDung) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) return;

  let bgClass = "bg-emerald-50 text-emerald-950 border border-emerald-200";
  let iconColor = "bg-emerald-600 text-white";
  let iconName = "check_circle";

  if (loai === "error") {
    bgClass = "bg-rose-50 text-rose-950 border border-rose-200";
    iconColor = "bg-rose-600 text-white";
    iconName = "error";
  } else if (loai === "warning") {
    bgClass = "bg-amber-50 text-amber-950 border border-amber-200";
    iconColor = "bg-amber-600 text-white";
    iconName = "warning";
  } else if (loai === "info") {
    bgClass = "bg-blue-50 text-blue-950 border border-blue-200";
    iconColor = "bg-blue-600 text-white";
    iconName = "info";
  }

  hopThongBao.className = `rounded-2xl ${bgClass} p-4 shadow-xs flex items-start gap-3.5 transition-all`;
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-xl ${iconColor} flex items-center justify-center shrink-0 shadow-xs mt-0.5">
      <span class="material-symbols-outlined text-[20px]">${iconName}</span>
    </div>
    <div class="flex-1 text-xs sm:text-sm">
      <div class="flex items-center justify-between">
        <span class="font-bold">${tieuDe}</span>
        <span class="text-[11px] text-slate-400">Vừa xong</span>
      </div>
      <p class="mt-1 leading-relaxed text-slate-600">
        ${noiDung}
      </p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-slate-400 hover:text-slate-700 p-1 rounded-lg transition-colors cursor-pointer" title="Đóng">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hopThongBao.classList.remove("hidden");
  hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function moModalBaoCao() {
  const modal = document.getElementById("modalBaoCaoTuan");
  const errBox = document.getElementById("loiFormBaoCao");
  if (errBox) errBox.classList.add("hidden");
  if (modal) modal.classList.remove("hidden");
}

function dongModalBaoCao() {
  const modal = document.getElementById("modalBaoCaoTuan");
  if (modal) modal.classList.add("hidden");
}

function dongModalChiTiet() {
  const modal = document.getElementById("modalChiTietBaoCao");
  if (modal) modal.classList.add("hidden");
}

function moChiTietBaoCao(maBaoCao) {
  const report = danhSachBaoCaoGoc.find(r => r.ma_bao_cao === maBaoCao);
  if (!report) return;

  const modal = document.getElementById("modalChiTietBaoCao");
  if (!modal) return;

  const elTieuDe = document.getElementById("ctTieuDeBaoCao");
  const elThoiGian = document.getElementById("ctThoiGianNop");
  const elTuanSo = document.getElementById("ctTuanSo");
  const elNhiemVu = document.getElementById("ctNhiemVu");
  const elSinhVien = document.getElementById("ctSinhVien");
  const elMentor = document.getElementById("ctMentor");
  const elNoiDung = document.getElementById("ctNoiDung");
  const elKetQua = document.getElementById("ctKetQua");
  const elPhanHoi = document.getElementById("ctPhanHoiMentor");

  if (elTieuDe) elTieuDe.textContent = `Báo Cáo Tiến Độ Tuần ${report.tuan_so}`;
  if (elThoiGian) elThoiGian.textContent = `Nộp lúc: ${dinhDangNgayGioVN(report.thoi_gian_nop)}`;
  if (elTuanSo) elTuanSo.textContent = `Tuần ${report.tuan_so}`;
  if (elNhiemVu) {
    elNhiemVu.textContent = report.ten_nhiem_vu ? `[Mã #${report.ma_nhiem_vu}] ${report.ten_nhiem_vu}` : "Không gắn nhiệm vụ cụ thể";
  }
  if (elSinhVien) {
    elSinhVien.textContent = report.ho_ten_sinh_vien ? `${report.ho_ten_sinh_vien} (${report.email_sinh_vien || ""})` : "--";
  }
  if (elMentor) {
    elMentor.textContent = report.ho_ten_mentor ? `${report.ho_ten_mentor} (Mentor phụ trách)` : "Chưa phân công Mentor";
  }
  if (elNoiDung) elNoiDung.textContent = report.noi_dung_cong_viec || "--";
  if (elKetQua) elKetQua.textContent = report.ket_qua_dat_duoc || "Chưa có kết quả hoặc link bàn giao kèm theo.";

  if (elPhanHoi) {
    if (report.phan_hoi_mentor && report.phan_hoi_mentor.trim() !== "") {
      elPhanHoi.className = "p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs sm:text-sm text-emerald-950 leading-relaxed whitespace-pre-line";
      elPhanHoi.innerHTML = `
        <div class="flex items-center gap-2 mb-1.5 font-bold text-emerald-800">
          <span class="material-symbols-outlined text-[18px]">verified</span>
          <span>Ý kiến đánh giá của ${report.ho_ten_mentor || "Mentor"}:</span>
        </div>
        <p>${report.phan_hoi_mentor}</p>
      `;
    } else {
      elPhanHoi.className = "p-4 rounded-2xl bg-amber-50/70 border border-amber-200 text-xs sm:text-sm text-amber-950 leading-relaxed whitespace-pre-line";
      elPhanHoi.innerHTML = `
        <div class="flex items-center gap-2 font-medium text-amber-800">
          <span class="material-symbols-outlined text-[18px]">hourglass_empty</span>
          <span>Báo cáo đang trong hàng đợi chờ Mentor hướng dẫn thẩm định và ghi nhận.</span>
        </div>
      `;
    }
  }

  modal.classList.remove("hidden");
}

async function taiDanhSachNhiemVu(maHoSo) {
  const selectEl = document.getElementById("baoCaoNhiemVu");
  if (!selectEl) return;

  try {
    const res = await fetch(`${duongDanApi}/interns/my-schedule?ho_so_id=${maHoSo}`);
    if (!res.ok) {
      selectEl.innerHTML = '<option value="">-- Không gắn nhiệm vụ cụ thể --</option>';
      return;
    }

    const json = await res.json();
    const data = json.data;
    if (data && data.ho_ten) {
      dongBoSidebar(data.ho_ten, data.email, data.lop);
    }

    danhSachNhiemVuGoc = data && data.danh_sach_nhiem_vu ? data.danh_sach_nhiem_vu : [];

    let optionsHtml = '<option value="">-- Không gắn nhiệm vụ cụ thể --</option>';
    danhSachNhiemVuGoc.forEach(task => {
      optionsHtml += `<option value="${task.ma_nhiem_vu}">[Mã #${task.ma_nhiem_vu}] ${task.ten_nhiem_vu}</option>`;
    });

    selectEl.innerHTML = optionsHtml;
  } catch (err) {
    selectEl.innerHTML = '<option value="">-- Không gắn nhiệm vụ cụ thể --</option>';
  }
}

function thayDoiTabLoc(tab) {
  tabBoLocHienTai = tab;

  const btnTatCa = document.getElementById("btnLocTatCa");
  const btnChoPhanHoi = document.getElementById("btnLocChoPhanHoi");
  const btnDaNhanXet = document.getElementById("btnLocDaNhanXet");

  const classActive = "px-3 py-1.5 rounded-lg text-xs font-bold bg-white text-emerald-700 shadow-2xs border border-slate-200/60 transition-colors";
  const classInactive = "px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors";

  if (btnTatCa) btnTatCa.className = tab === "tat_ca" ? classActive : classInactive;
  if (btnChoPhanHoi) btnChoPhanHoi.className = tab === "cho_phan_hoi" ? classActive : classInactive;
  if (btnDaNhanXet) btnDaNhanXet.className = tab === "da_nhan_xet" ? classActive : classInactive;

  apDungBoLoc();
}

function apDungBoLoc() {
  const oTimKiem = document.getElementById("oTimKiemBaoCao");
  const tuKhoa = oTimKiem ? oTimKiem.value.trim().toLowerCase() : "";

  let danhSachLoc = [...danhSachBaoCaoGoc];

  if (tabBoLocHienTai === "cho_phan_hoi") {
    danhSachLoc = danhSachLoc.filter(r => !r.phan_hoi_mentor || r.phan_hoi_mentor.trim() === "");
  } else if (tabBoLocHienTai === "da_nhan_xet") {
    danhSachLoc = danhSachLoc.filter(r => r.phan_hoi_mentor && r.phan_hoi_mentor.trim() !== "");
  }

  if (tuKhoa) {
    danhSachLoc = danhSachLoc.filter(r => {
      const noiDung = (r.noi_dung_cong_viec || "").toLowerCase();
      const ketQua = (r.ket_qua_dat_duoc || "").toLowerCase();
      const tenNv = (r.ten_nhiem_vu || "").toLowerCase();
      const phanHoi = (r.phan_hoi_mentor || "").toLowerCase();
      return noiDung.includes(tuKhoa) || ketQua.includes(tuKhoa) || tenNv.includes(tuKhoa) || phanHoi.includes(tuKhoa);
    });
  }

  renderBangBaoCao(danhSachLoc);
}

function renderBangBaoCao(danhSach) {
  const tbody = document.getElementById("tbodyDanhSachBaoCao");
  if (!tbody) return;

  if (danhSach.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="py-12 text-center text-slate-400">
          <div class="max-w-sm mx-auto space-y-3">
            <span class="material-symbols-outlined text-[42px] text-slate-300 block">description</span>
            <p class="font-bold text-slate-700 text-sm">Chưa có báo cáo tuần nào phù hợp</p>
            <p class="text-xs text-slate-400">Bạn chưa nộp báo cáo hoặc không tìm thấy bản ghi theo bộ lọc hiện tại.</p>
            <button type="button" onclick="moModalBaoCao()" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-xs cursor-pointer">
              <span class="material-symbols-outlined text-[16px]">add</span>
              <span>Nộp Báo Cáo Ngay</span>
            </button>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  let htmlRows = "";
  danhSach.forEach(item => {
    const daNhanXet = item.phan_hoi_mentor && item.phan_hoi_mentor.trim() !== "";
    const badgeDanhGia = daNhanXet
      ? `
        <div class="space-y-1">
          <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
            <span class="material-symbols-outlined text-[13px]">verified</span>
            Đã nhận xét
          </span>
          <p class="text-slate-600 text-[11px] truncate max-w-xs" title="${item.phan_hoi_mentor}">
            "${item.phan_hoi_mentor}"
          </p>
        </div>
      `
      : `
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
          <span class="material-symbols-outlined text-[13px]">hourglass_top</span>
          Chờ phản hồi
        </span>
      `;

    const nhiemVuTag = item.ten_nhiem_vu
      ? `
        <div class="space-y-0.5">
          <span class="text-emerald-700 font-bold block">[#${item.ma_nhiem_vu}]</span>
          <span class="text-slate-700 line-clamp-2 max-w-xs block" title="${item.ten_nhiem_vu}">${item.ten_nhiem_vu}</span>
        </div>
      `
      : `<span class="text-slate-400 italic">Không gắn nhiệm vụ</span>`;

    htmlRows += `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="py-4 px-6 whitespace-nowrap">
          <div class="space-y-1">
            <span class="inline-block px-2.5 py-0.5 rounded-lg text-xs font-bold bg-slate-100 text-slate-800 border border-slate-200">
              Tuần ${item.tuan_so}
            </span>
            <span class="text-[11px] text-slate-400 block">${dinhDangNgayGioVN(item.thoi_gian_nop)}</span>
          </div>
        </td>
        <td class="py-4 px-6">
          ${nhiemVuTag}
        </td>
        <td class="py-4 px-6">
          <div class="text-slate-700 text-xs leading-relaxed max-w-md line-clamp-2" title="${item.noi_dung_cong_viec}">
            ${item.noi_dung_cong_viec}
          </div>
        </td>
        <td class="py-4 px-6">
          <div class="text-slate-700 text-xs leading-relaxed max-w-xs line-clamp-2" title="${item.ket_qua_dat_duoc || ''}">
            ${item.ket_qua_dat_duoc ? item.ket_qua_dat_duoc : '<span class="text-slate-400 italic">--</span>'}
          </div>
        </td>
        <td class="py-4 px-6 whitespace-nowrap">
          ${badgeDanhGia}
        </td>
        <td class="py-4 px-6 text-center whitespace-nowrap">
          <button
            type="button"
            onclick="moChiTietBaoCao(${item.ma_bao_cao})"
            class="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-emerald-700 transition-colors cursor-pointer shadow-2xs"
          >
            <span class="material-symbols-outlined text-[15px]">visibility</span>
            <span>Chi tiết</span>
          </button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = htmlRows;
}

function capNhatThongKeKPI() {
  const elTong = document.getElementById("kpiTongBaoCao");
  const elDaNhan = document.getElementById("kpiDaNhanXet");
  const elCho = document.getElementById("kpiChoPhanHoi");
  const elTuan = document.getElementById("kpiTuanGanNhat");
  const elDemTatCa = document.getElementById("demTatCa");
  const elDemCho = document.getElementById("demChoPhanHoi");
  const elDemDa = document.getElementById("demDaNhanXet");

  const tong = danhSachBaoCaoGoc.length;
  let daNhanXet = 0;
  let choPhanHoi = 0;
  let tuanMax = 0;

  danhSachBaoCaoGoc.forEach(r => {
    if (r.phan_hoi_mentor && r.phan_hoi_mentor.trim() !== "") {
      daNhanXet++;
    } else {
      choPhanHoi++;
    }
    if (r.tuan_so && r.tuan_so > tuanMax) {
      tuanMax = r.tuan_so;
    }
  });

  if (elTong) elTong.textContent = tong;
  if (elDaNhan) elDaNhan.textContent = daNhanXet;
  if (elCho) elCho.textContent = choPhanHoi;
  if (elTuan) elTuan.textContent = tuanMax > 0 ? `Tuần ${tuanMax}` : "--";

  if (elDemTatCa) elDemTatCa.textContent = tong;
  if (elDemCho) elDemCho.textContent = choPhanHoi;
  if (elDemDa) elDemDa.textContent = daNhanXet;

  const oTuanInput = document.getElementById("baoCaoTuanSo");
  if (oTuanInput && !oTuanInput.value) {
    oTuanInput.value = tuanMax > 0 ? tuanMax + 1 : 1;
  }
}

async function taiDuLieuBaoCao() {
  const maHoSo = layIdSinhVien();
  const tbody = document.getElementById("tbodyDanhSachBaoCao");

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="py-12 text-center text-slate-400">
          <span class="inline-block w-8 h-8 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mb-2"></span>
          <p>Đang tải danh sách báo cáo tuần...</p>
        </td>
      </tr>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/reports?ma_ho_so=${maHoSo}&page_size=100`);
    if (!res.ok) {
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="py-12 text-center text-rose-500">
              <span class="material-symbols-outlined text-[36px] text-rose-400 block mb-2">error</span>
              <p class="font-bold mb-1">Không thể tải danh sách báo cáo</p>
              <p class="text-xs text-slate-400 mb-3">Hồ sơ thực tập sinh không tồn tại hoặc lỗi máy chủ</p>
              <button type="button" onclick="taiDuLieuBaoCao()" class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold text-xs hover:bg-emerald-700 cursor-pointer">
                Thử lại
              </button>
            </td>
          </tr>
        `;
      }
      return;
    }

    const json = await res.json();
    const data = json.data;
    danhSachBaoCaoGoc = data && data.items ? data.items : [];

    if (danhSachBaoCaoGoc.length > 0) {
      const dauTien = danhSachBaoCaoGoc[0];
      dongBoSidebar(dauTien.ho_ten_sinh_vien, dauTien.email_sinh_vien);
    }

    capNhatThongKeKPI();
    apDungBoLoc();

  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="py-12 text-center text-rose-500">
            <span class="material-symbols-outlined text-[36px] text-rose-400 block mb-2">wifi_off</span>
            <p class="font-bold mb-1">Mất kết nối máy chủ</p>
            <p class="text-xs text-slate-400 mb-3">Vui lòng kiểm tra lại kết nối mạng hoặc server Backend</p>
            <button type="button" onclick="taiDuLieuBaoCao()" class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold text-xs hover:bg-emerald-700 cursor-pointer">
              Thử lại
            </button>
          </td>
        </tr>
      `;
    }
  }
}

async function xuLyGuiBaoCao(event) {
  event.preventDefault();

  const maHoSo = layIdSinhVien();
  const oTuan = document.getElementById("baoCaoTuanSo");
  const oNhiemVu = document.getElementById("baoCaoNhiemVu");
  const oNoiDung = document.getElementById("baoCaoNoiDung");
  const oKetQua = document.getElementById("baoCaoKetQua");
  const nutGui = document.getElementById("nutGuiBaoCao");
  const errBox = document.getElementById("loiFormBaoCao");

  if (errBox) errBox.classList.add("hidden");

  const tuanSo = parseInt(oTuan?.value || "0", 10);
  const maNhiemVuRaw = oNhiemVu?.value;
  const maNhiemVu = maNhiemVuRaw ? parseInt(maNhiemVuRaw, 10) : null;
  const noiDung = oNoiDung?.value ? oNoiDung.value.trim() : "";
  const ketQua = oKetQua?.value ? oKetQua.value.trim() : "";

  if (isNaN(tuanSo) || tuanSo < 1 || tuanSo > 52) {
    if (errBox) {
      errBox.textContent = "Tuần báo cáo không hợp lệ! Vui lòng nhập số tuần từ 1 đến 52.";
      errBox.classList.remove("hidden");
    }
    return;
  }

  if (!noiDung || noiDung.length < 10) {
    if (errBox) {
      errBox.textContent = "Nội dung công việc quá ngắn! Vui lòng nhập chi tiết ít nhất 10 ký tự.";
      errBox.classList.remove("hidden");
    }
    return;
  }

  const oldHtml = nutGui ? nutGui.innerHTML : "";
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang gửi báo cáo...</span>
    `;
  }

  try {
    const payload = {
      ma_ho_so: maHoSo,
      tuan_so: tuanSo,
      ma_nhiem_vu: maNhiemVu,
      noi_dung_cong_viec: noiDung,
      ket_qua_dat_duoc: ketQua || null
    };

    const res = await fetch(`${duongDanApi}/reports`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      dongModalBaoCao();
      document.getElementById("formNopBaoCao")?.reset();
      hienThiThongBaoChung(
        "success",
        `Nộp Báo Cáo Tuần ${tuanSo} Thành Công!`,
        `Bản ghi nhật ký tiến độ tuần ${tuanSo} của bạn đã được ghi nhận trên hệ thống và chuyển tới Mentor hướng dẫn đánh giá.`
      );
      await taiDuLieuBaoCao();
    } else {
      let thongBaoLoi = "Không thể gửi báo cáo tuần!";
      if (typeof resJson.detail === "string") {
        thongBaoLoi = resJson.detail;
      } else if (Array.isArray(resJson.detail) && resJson.detail[0]?.msg) {
        thongBaoLoi = resJson.detail[0].msg;
      }
      if (errBox) {
        errBox.textContent = thongBaoLoi;
        errBox.classList.remove("hidden");
      }
      hienThiThongBaoChung("error", "Lỗi nộp báo cáo", thongBaoLoi);
    }

  } catch (err) {
    const thongBao = "Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối mạng!";
    if (errBox) {
      errBox.textContent = thongBao;
      errBox.classList.remove("hidden");
    }
    hienThiThongBaoChung("error", "Mất kết nối", thongBao);
  } finally {
    if (nutGui) {
      nutGui.disabled = false;
      nutGui.innerHTML = oldHtml;
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const maHoSo = layIdSinhVien();
  if (typeof dongBoThongTinNguoiDung === "function") {
    dongBoThongTinNguoiDung();
  }
  taiDanhSachNhiemVu(maHoSo);
  taiDuLieuBaoCao();
});
