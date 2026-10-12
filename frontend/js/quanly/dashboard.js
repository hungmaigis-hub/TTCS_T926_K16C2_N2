const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";
let danhSachSinhVienMentorCuaToi = [];
let maHoSoDangXemNhiemVu = null;
let hoTenDangXemNhiemVu = "";

function layTenVietTat(hoTen) {
  if (!hoTen) return "NA";
  const words = hoTen.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
  }
  return hoTen.substring(0, 2).toUpperCase();
}

function dinhDangNgayVn(ngayStr) {
  if (!ngayStr) return "";
  const parts = ngayStr.split("-");
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return ngayStr;
}

function capNhatThongTinDotThucTap(programData, tongSo = 0, choDuyet = 0, daKy = 0) {
  const elHeader = document.getElementById("theDotThucTapHeader");
  const elTieuDe = document.getElementById("tieuDeTienDoDot");
  const elThoiGian = document.getElementById("thoiGianTienDoDot");
  const elGiaiDoan = document.getElementById("theGiaiDoanDotText");
  const elTienDoSo = document.getElementById("chuSoTienDoTongThe");
  const elThanhTienDo = document.getElementById("thanhTienDoTongThe");

  const elTiepNhan = document.getElementById("tienDoBuocTiepNhan");
  const elKyHopDong = document.getElementById("tienDoBuocKyHopDong");
  const elDangThucTap = document.getElementById("tienDoBuocDangThucTap");
  const elDanhGia = document.getElementById("tienDoBuocDanhGia");

  let ten = "";
  let batDau = "";
  let ketThuc = "";

  if (programData && programData.ten_chuong_trinh) {
    ten = programData.ten_chuong_trinh;
    batDau = programData.ngay_bat_dau || "";
    ketThuc = programData.ngay_ket_thuc || "";
  } else {
    const now = new Date();
    const curY = now.getFullYear();
    const startY = now.getMonth() >= 8 ? curY : curY - 1;
    const nienKhoa = `${startY} - ${startY + 1}`;
    const hocKy = now.getMonth() >= 8 || now.getMonth() <= 0 ? "Học kỳ I" : "Học kỳ II";
    ten = `Đợt thực tập ${hocKy} (${nienKhoa})`;
    batDau = `${startY}-09-01`;
    ketThuc = `${startY}-12-31`;
  }

  if (elHeader) elHeader.textContent = ten;
  if (elTieuDe) elTieuDe.textContent = `Tiến Độ: ${ten}`;

  if (batDau && ketThuc) {
    const dStart = new Date(batDau);
    const dEnd = new Date(ketThuc);
    const dNow = new Date();

    const fStart = dinhDangNgayVn(batDau);
    const fEnd = dinhDangNgayVn(ketThuc);

    let tuan = 1;
    let percent = 0;
    const diffMs = dNow.getTime() - dStart.getTime();
    const totalMs = dEnd.getTime() - dStart.getTime();
    const tongSoTuan = Math.max(1, Math.ceil(totalMs / (7 * 24 * 60 * 60 * 1000)));

    if (dNow < dStart) {
      if (elGiaiDoan) elGiaiDoan.textContent = "Sắp diễn ra";
      if (elThoiGian) elThoiGian.textContent = `Thời gian dự kiến: ${fStart} - ${fEnd}`;
      percent = 0;
      tuan = 1;
    } else if (dNow > dEnd) {
      if (elGiaiDoan) elGiaiDoan.textContent = "Đã hoàn thành đợt";
      if (elThoiGian) elThoiGian.textContent = `Thời gian thực tế: ${fStart} - ${fEnd} (Đã kết thúc)`;
      percent = 100;
      tuan = tongSoTuan;
    } else {
      tuan = Math.max(1, Math.ceil(diffMs / (7 * 24 * 60 * 60 * 1000)));
      percent = totalMs > 0 ? Math.min(100, Math.max(0, Math.round((diffMs / totalMs) * 100))) : 0;
      if (elGiaiDoan) elGiaiDoan.textContent = `Giai đoạn: Đang thực tập (Tuần ${tuan})`;
      if (elThoiGian) elThoiGian.textContent = `Thời gian thực tế: ${fStart} - ${fEnd} (Tuần thứ ${tuan})`;
    }

    if (elTienDoSo) elTienDoSo.textContent = `${percent}% Hoàn tất`;
    if (elThanhTienDo) elThanhTienDo.style.width = `${percent}%`;

    if (elTiepNhan && tongSo > 0) {
      const tyLeTiepNhan = Math.round(((tongSo - choDuyet) / tongSo) * 100);
      elTiepNhan.innerHTML = `
        <span class="material-symbols-outlined text-[16px]">check_circle</span>
        <span>${tyLeTiepNhan}%</span>
      `;
    }

    if (elKyHopDong && tongSo > 0) {
      const tyLeKy = Math.round((daKy / tongSo) * 100);
      elKyHopDong.innerHTML = `
        <span class="material-symbols-outlined text-[16px]">check_circle</span>
        <span>${tyLeKy}%</span>
      `;
    }

    if (elDangThucTap) {
      const tuanHienTai = Math.min(tongSoTuan, tuan);
      elDangThucTap.innerHTML = `
        <span class="material-symbols-outlined text-[16px]">timelapse</span>
        <span>Tuần ${tuanHienTai}/${tongSoTuan}</span>
      `;
    }

    if (elDanhGia) {
      const thangKetThuc = dEnd.getMonth() + 1;
      elDanhGia.innerHTML = `
        <span class="material-symbols-outlined text-[16px]">hourglass_empty</span>
        <span>Dự kiến T${thangKetThuc}</span>
      `;
    }

    const elHanChotBaoCaoTieuDe = document.getElementById("hanChotBaoCaoTieuDe");
    const elHanChotKetThucDotThoiGian = document.getElementById("hanChotKetThucDotThoiGian");
    if (elHanChotBaoCaoTieuDe) {
      elHanChotBaoCaoTieuDe.textContent = `Nộp báo cáo tuần ${tuan}`;
    }
    if (elHanChotKetThucDotThoiGian) {
      elHanChotKetThucDotThoiGian.textContent = `Hạn chót đợt: ${fEnd}`;
    }
  }
}

function renderBangSinhVien(danhSach) {
  const bangTbody = document.getElementById("bangSinhVienHoatDong");
  if (!bangTbody) return;

  const user = layVaiTroNguoiDungHienTai();
  const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

  const elTieuDe = document.getElementById("tieuDeBangHoSoMoiNhat");
  const elMoTa = document.getElementById("moTaBangHoSoMoiNhat");
  const elLink = document.getElementById("linkXemToanBoHoSo");
  const elTxtLink = document.getElementById("txtXemToanBoHoSo");
  const elThCot3 = document.getElementById("thCot3HoSo");

  let danhSachLoc = danhSach || [];

  if (laMentor) {
    danhSachLoc = (danhSach || []).filter((sv) => {
      if (sv.ma_mentor && (sv.ma_mentor === user.id || sv.ma_mentor === user.ma_nguoi_dung)) return true;
      if (user.ho_ten && sv.ten_mentor && (sv.ten_mentor.toLowerCase().includes(user.ho_ten.toLowerCase()) || user.ho_ten.toLowerCase().includes(sv.ten_mentor.toLowerCase()))) return true;
      return false;
    });

    if (elTieuDe) elTieuDe.textContent = "Sinh Viên Tôi Đang Hướng Dẫn";
    if (elMoTa) elMoTa.textContent = `Danh sách ${danhSachLoc.length} sinh viên thuộc nhóm hướng dẫn của ${user.ho_ten || "bạn"}`;
    if (elLink) elLink.href = "danh_gia.html";
    if (elTxtLink) elTxtLink.textContent = "Xem toàn bộ đánh giá";
    if (elThCot3) elThCot3.textContent = "Trường & Lớp sinh viên";
  } else {
    if (elTieuDe) elTieuDe.textContent = "Hồ Sơ & Hoạt Động Mới Nhất";
    if (elMoTa) elMoTa.textContent = "Danh sách các sinh viên vừa cập nhật hồ sơ trong đợt thực tập";
    if (elLink) elLink.href = "xet_duyet_ho_so.html";
    if (elTxtLink) elTxtLink.textContent = "Xem toàn bộ hồ sơ";
    if (elThCot3) elThCot3.textContent = "Doanh nghiệp tiếp nhận";
  }

  bangTbody.innerHTML = "";

  if (danhSachLoc.length === 0) {
    const thongBaoTrong = laMentor
      ? "Bạn hiện chưa có sinh viên nào được phân công trong đợt này."
      : "Chưa có sinh viên nào trong danh sách.";
    bangTbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-400 font-medium">${thongBaoTrong}</td></tr>`;
    return;
  }

  const hienThi = danhSachLoc.slice(0, 6);
  hienThi.forEach((sv) => {
    const hoTen = sv.ho_ten || "Sinh viên";
    const email = sv.email || "sv@ictu.edu.vn";
    const initials = layTenVietTat(hoTen);
    const chuyenNganh = sv.chuyen_nganh || "Công nghệ thông tin";
    const donVi = laMentor
      ? `${sv.ten_truong || "ICTU"} &bull; ${sv.lop || "K19"}`
      : (sv.ten_mentor ? `Mentor: ${sv.ten_mentor}` : (sv.ten_truong || "FPT Software"));
    
    let badgeHtml = "";
    if (sv.trang_thai_xet_duyet === "ChoDuyet") {
      badgeHtml = `
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
          Chờ xét duyệt
        </span>
      `;
    } else if (sv.trang_thai_thuc_tap === "DangThucTap") {
      badgeHtml = `
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Đang thực tập
        </span>
      `;
    } else {
      badgeHtml = `
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-blue-50 text-blue-800 border border-blue-200">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          Đã tiếp nhận
        </span>
      `;
    }

    let thaoTacHtml = "";
    if (laMentor) {
      thaoTacHtml = `
        <div class="flex items-center justify-end gap-1.5">
          <button type="button" onclick="moModalGiaoViec(${sv.ma_ho_so}, '${encodeURIComponent(hoTen)}')" class="px-2.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-700 font-semibold text-xs transition-colors cursor-pointer flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">add_task</span>
            <span>Giao việc</span>
          </button>
          <a href="cham_cong.html" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors">
            Điểm danh
          </a>
          <a href="danh_gia.html?id=${sv.ma_ho_so}" class="px-2.5 py-1.5 rounded-lg bg-ictu-50 hover:bg-ictu-600 hover:text-white text-ictu-700 font-semibold text-xs transition-colors">
            Đánh giá
          </a>
        </div>
      `;
    } else {
      thaoTacHtml = `
        <a href="xet_duyet_ho_so.html" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-ictu-600 hover:text-white font-semibold text-slate-700 transition-colors inline-block">
          Chi tiết
        </a>
      `;
    }

    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50/50 transition-colors";
    tr.innerHTML = `
      <td class="py-4 px-6">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-ictu-100 text-ictu-700 font-bold flex items-center justify-center text-xs">
            ${initials}
          </div>
          <div>
            <p class="font-bold text-slate-900">${hoTen}</p>
            <p class="text-[11px] text-slate-400">${email}</p>
          </div>
        </div>
      </td>
      <td class="py-4 px-6 text-slate-600 font-medium">
        ${chuyenNganh}
      </td>
      <td class="py-4 px-6 text-slate-800 font-semibold">
        ${donVi}
      </td>
      <td class="py-4 px-6">
        ${badgeHtml}
      </td>
      <td class="py-4 px-6 text-right">
        ${thaoTacHtml}
      </td>
    `;
    bangTbody.appendChild(tr);
  });
}

function thoatHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

let duLieuFacultyReportGoc = null;
let tabFacultyHienTai = "nganh";
let tuKhoaTimKiemFaculty = "";

function locDanhSachFacultyReport(kw) {
  tuKhoaTimKiemFaculty = (kw || "").trim().toLowerCase();
  renderFacultyReportHienTai();
}

function chuyenTabThongKeFaculty(tab) {
  tabFacultyHienTai = tab;
  tuKhoaTimKiemFaculty = "";
  const oTimKiem = document.getElementById("oTimKiemFaculty");
  if (oTimKiem) oTimKiem.value = "";
  renderFacultyReportHienTai();
}

function renderFacultyReportHienTai() {
  const container = document.getElementById("danhSachPhanBoNganh");
  const txtTong = document.getElementById("txtTongSoNganhDaoTao");
  const tieuDe = document.getElementById("tieuDePhanBoNganh");
  const btnNganh = document.getElementById("btnTabThongKeNganh");
  const btnTruong = document.getElementById("btnTabThongKeTruong");
  const hopTimKiem = document.getElementById("hopTimKiemFaculty");

  if (!container) return;

  if (btnNganh && btnTruong) {
    if (tabFacultyHienTai === "nganh") {
      btnNganh.className = "px-3 py-1 rounded-lg bg-white text-slate-900 shadow-xs cursor-pointer font-bold transition-all";
      btnTruong.className = "px-3 py-1 rounded-lg text-slate-600 hover:text-slate-900 cursor-pointer transition-all";
    } else {
      btnNganh.className = "px-3 py-1 rounded-lg text-slate-600 hover:text-slate-900 cursor-pointer transition-all";
      btnTruong.className = "px-3 py-1 rounded-lg bg-white text-slate-900 shadow-xs cursor-pointer font-bold transition-all";
    }
  }

  if (!duLieuFacultyReportGoc) {
    if (hopTimKiem) hopTimKiem.classList.add("hidden");
    container.innerHTML = `<div class="text-xs text-slate-400 py-4 text-center">Chưa có dữ liệu báo cáo từ CSDL</div>`;
    if (txtTong) txtTong.textContent = "0 ngành & 0 trường";
    return;
  }

  const summary = duLieuFacultyReportGoc.summary || {};
  const tongSv = summary.tong_sinh_vien || 1;

  const danhSachMau = [
    "bg-ictu-600",
    "bg-sky-500",
    "bg-emerald-500",
    "bg-violet-500",
    "bg-amber-500",
    "bg-rose-500",
    "bg-teal-500",
    "bg-indigo-500"
  ];

  container.innerHTML = "";

  if (tabFacultyHienTai === "nganh") {
    if (tieuDe) tieuDe.textContent = "Phân Bổ Thực Tập Sinh Theo Ngành Đào Tạo";
    const listNganh = duLieuFacultyReportGoc.thong_ke_theo_chuyen_nganh || [];
    if (txtTong) {
      txtTong.textContent = `${summary.tong_so_chuyen_nganh || listNganh.length} chuyên ngành (${summary.tong_sinh_vien || 0} SV từ ${summary.tong_so_truong || 0} trường)`;
    }

    if (hopTimKiem) {
      hopTimKiem.classList.toggle("hidden", listNganh.length <= 5);
    }

    if (listNganh.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-400 py-4 text-center">Không có chuyên ngành nào được ghi nhận</div>`;
      return;
    }

    let listHienThi = listNganh;
    if (tuKhoaTimKiemFaculty) {
      listHienThi = listNganh.filter((item) => {
        const matchName = (item.chuyen_nganh || "").toLowerCase().includes(tuKhoaTimKiemFaculty);
        const matchTruong = (item.danh_sach_truong || []).some((t) => (t.ten_truong || "").toLowerCase().includes(tuKhoaTimKiemFaculty));
        return matchName || matchTruong;
      });
    }

    if (listHienThi.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-400 py-6 text-center">Không tìm thấy chuyên ngành phù hợp với từ khóa "${thoatHtml(tuKhoaTimKiemFaculty)}"</div>`;
      return;
    }

    listHienThi.forEach((item, idx) => {
      const soLuong = item.tong_sinh_vien || 0;
      const phanTram = Math.max(1, Math.round((soLuong / tongSv) * 100));
      const mau = danhSachMau[idx % danhSachMau.length];

      let subtext = "";
      let fullTitle = "";
      if (item.danh_sach_truong && item.danh_sach_truong.length > 0) {
        const arrStr = item.danh_sach_truong.map((t) => `${t.ten_truong} (${t.so_luong} SV)`);
        fullTitle = arrStr.join(" | ");
        const topUnis = item.danh_sach_truong.slice(0, 2).map((t) => `${t.ten_truong} (${t.so_luong})`).join(", ");
        const conLai = item.danh_sach_truong.length - 2;
        subtext = conLai > 0 ? `${topUnis} +${conLai} trường khác` : topUnis;
      }

      const wrapper = document.createElement("div");
      wrapper.className = "p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 hover:border-slate-200 hover:bg-slate-50 transition-all";
      wrapper.innerHTML = `
        <div class="flex items-center justify-between text-xs font-semibold mb-1">
          <span class="text-slate-800 font-bold flex items-center gap-1.5 truncate pr-2">
            <span class="w-2 h-2 rounded-full ${mau} shrink-0"></span>
            <span class="truncate" title="${thoatHtml(item.chuyen_nganh)}">${thoatHtml(item.chuyen_nganh)}</span>
          </span>
          <span class="text-slate-900 font-bold shrink-0">${soLuong} SV <span class="text-slate-400 font-medium">(${phanTram}%)</span></span>
        </div>
        <div class="w-full bg-slate-200/70 rounded-full h-2 overflow-hidden mb-1.5">
          <div class="${mau} h-2 rounded-full transition-all duration-500" style="width: ${phanTram}%"></div>
        </div>
        ${subtext ? `<div class="text-[11px] text-slate-400 truncate flex items-center gap-1" title="${thoatHtml(fullTitle)}"><span class="material-symbols-outlined text-[13px] shrink-0">school</span><span class="truncate">${thoatHtml(subtext)}</span></div>` : ""}
      `;
      container.appendChild(wrapper);
    });

    if (listHienThi.length > 5 && !tuKhoaTimKiemFaculty) {
      const hint = document.createElement("div");
      hint.className = "pt-1 text-center text-[11px] text-slate-400 font-medium flex items-center justify-center gap-1";
      hint.innerHTML = `<span class="material-symbols-outlined text-[13px]">unfold_more</span>Cuộn danh sách để xem tất cả ${listHienThi.length} ngành`;
      container.appendChild(hint);
    }
  } else {
    if (tieuDe) tieuDe.textContent = "Phân Bổ Thực Tập Sinh Theo Trường Đại Học";
    const listTruong = duLieuFacultyReportGoc.thong_ke_theo_truong || [];
    if (txtTong) {
      txtTong.textContent = `${summary.tong_so_truong || listTruong.length} trường liên kết (${summary.tong_sinh_vien || 0} SV)`;
    }

    if (hopTimKiem) {
      hopTimKiem.classList.toggle("hidden", listTruong.length <= 5);
    }

    if (listTruong.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-400 py-4 text-center">Không có trường đại học nào được ghi nhận</div>`;
      return;
    }

    let listHienThi = listTruong;
    if (tuKhoaTimKiemFaculty) {
      listHienThi = listTruong.filter((item) => {
        const matchName = (item.ten_truong || "").toLowerCase().includes(tuKhoaTimKiemFaculty);
        const matchNganh = (item.danh_sach_chuyen_nganh || []).some((m) => (m.chuyen_nganh || "").toLowerCase().includes(tuKhoaTimKiemFaculty));
        return matchName || matchNganh;
      });
    }

    if (listHienThi.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-400 py-6 text-center">Không tìm thấy trường phù hợp với từ khóa "${thoatHtml(tuKhoaTimKiemFaculty)}"</div>`;
      return;
    }

    listHienThi.forEach((item, idx) => {
      const soLuong = item.tong_sinh_vien || 0;
      const phanTram = Math.max(1, Math.round((soLuong / tongSv) * 100));
      const mau = danhSachMau[idx % danhSachMau.length];

      let subtext = "";
      let fullTitle = "";
      if (item.danh_sach_chuyen_nganh && item.danh_sach_chuyen_nganh.length > 0) {
        const arrStr = item.danh_sach_chuyen_nganh.map((m) => `${m.chuyen_nganh} (${m.so_luong} SV)`);
        fullTitle = arrStr.join(" | ");
        const topMajors = item.danh_sach_chuyen_nganh.slice(0, 3).map((m) => `${m.chuyen_nganh} (${m.so_luong})`).join(", ");
        const conLai = item.danh_sach_chuyen_nganh.length - 3;
        subtext = conLai > 0 ? `${topMajors} +${conLai} ngành khác` : topMajors;
      }

      const wrapper = document.createElement("div");
      wrapper.className = "p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 hover:border-slate-200 hover:bg-slate-50 transition-all";
      wrapper.innerHTML = `
        <div class="flex items-center justify-between text-xs font-semibold mb-1">
          <span class="text-slate-800 font-bold flex items-center gap-1.5 truncate pr-2">
            <span class="w-2 h-2 rounded-full ${mau} shrink-0"></span>
            <span class="truncate" title="${thoatHtml(item.ten_truong)}">${thoatHtml(item.ten_truong)}</span>
          </span>
          <span class="text-slate-900 font-bold shrink-0">${soLuong} SV <span class="text-slate-400 font-medium">(${phanTram}%)</span></span>
        </div>
        <div class="w-full bg-slate-200/70 rounded-full h-2 overflow-hidden mb-1.5">
          <div class="${mau} h-2 rounded-full transition-all duration-500" style="width: ${phanTram}%"></div>
        </div>
        ${subtext ? `<div class="text-[11px] text-slate-400 truncate flex items-center gap-1" title="${thoatHtml(fullTitle)}"><span class="material-symbols-outlined text-[13px] shrink-0">menu_book</span><span class="truncate">${thoatHtml(subtext)}</span></div>` : ""}
      `;
      container.appendChild(wrapper);
    });

    if (listHienThi.length > 5 && !tuKhoaTimKiemFaculty) {
      const hint = document.createElement("div");
      hint.className = "pt-1 text-center text-[11px] text-slate-400 font-medium flex items-center justify-center gap-1";
      hint.innerHTML = `<span class="material-symbols-outlined text-[13px]">unfold_more</span>Cuộn danh sách để xem tất cả ${listHienThi.length} trường`;
      container.appendChild(hint);
    }
  }
}

async function taiBaoCaoSinhVienTheoNganhVaTruong(danhSachInternsFallback = []) {
  const cucTab = document.getElementById("cucTabThongKeFaculty");
  const hopTimKiem = document.getElementById("hopTimKiemFaculty");
  const user = layVaiTroNguoiDungHienTai();
  const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

  if (laMentor) {
    if (cucTab) cucTab.style.display = "none";
    if (hopTimKiem) hopTimKiem.classList.add("hidden");
    renderPhanBoNganh(danhSachInternsFallback);
    return;
  }

  if (cucTab) cucTab.style.display = "flex";

  try {
    const res = await fetch(`${duongDanApi}/reports/interns-by-faculty`);
    if (!res.ok) {
      renderPhanBoNganh(danhSachInternsFallback);
      return;
    }
    const json = await res.json();
    duLieuFacultyReportGoc = json.data || null;
    renderFacultyReportHienTai();
  } catch {
    renderPhanBoNganh(danhSachInternsFallback);
  }
}

function renderPhanBoNganh(danhSach) {
  const container = document.getElementById("danhSachPhanBoNganh");
  const txtTong = document.getElementById("txtTongSoNganhDaoTao");
  const tieuDe = document.getElementById("tieuDePhanBoNganh");
  const hopTimKiem = document.getElementById("hopTimKiemFaculty");
  if (!container) return;

  if (hopTimKiem) hopTimKiem.classList.add("hidden");

  const user = layVaiTroNguoiDungHienTai();
  const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

  let danhSachLoc = danhSach || [];
  if (laMentor) {
    danhSachLoc = (danhSach || []).filter((sv) => {
      if (sv.ma_mentor && (sv.ma_mentor === user.id || sv.ma_mentor === user.ma_nguoi_dung)) return true;
      if (user.ho_ten && sv.ten_mentor && (sv.ten_mentor.toLowerCase().includes(user.ho_ten.toLowerCase()) || user.ho_ten.toLowerCase().includes(sv.ten_mentor.toLowerCase()))) return true;
      return false;
    });
    if (tieuDe) tieuDe.textContent = "Chuyên Ngành Nhóm Sinh Viên Tôi Kèm";
  } else {
    if (tieuDe) tieuDe.textContent = "Phân Bổ Thực Tập Sinh Theo Ngành Đào Tạo";
  }

  if (danhSachLoc.length === 0) {
    const thongBao = laMentor ? "Bạn hiện chưa có sinh viên nào được phân công trong đợt này." : "Chưa có dữ liệu sinh viên trong CSDL";
    container.innerHTML = `<div class="text-xs text-slate-400 py-4 text-center">${thongBao}</div>`;
    if (txtTong) txtTong.textContent = laMentor ? "0 ngành (0 SV)" : "0 ngành";
    return;
  }

  const thongKe = {};
  danhSachLoc.forEach((sv) => {
    const raw = sv.chuyen_nganh || "Công nghệ Thông tin";
    const nganh = raw.trim();
    thongKe[nganh] = (thongKe[nganh] || 0) + 1;
  });

  const danhSachSapXep = Object.entries(thongKe).sort((a, b) => b[1] - a[1]);
  const tongSv = danhSachLoc.length;

  if (txtTong) {
    txtTong.textContent = laMentor ? `${danhSachSapXep.length} ngành (${tongSv} SV nhóm tôi)` : `${danhSachSapXep.length} ngành (${tongSv} SV)`;
  }

  const danhSachMau = [
    "bg-ictu-600",
    "bg-sky-500",
    "bg-emerald-500",
    "bg-violet-500",
    "bg-amber-500",
    "bg-rose-500",
    "bg-teal-500",
    "bg-indigo-500"
  ];

  container.innerHTML = "";
  danhSachSapXep.forEach(([nganh, soLuong], idx) => {
    const phanTram = Math.max(1, Math.round((soLuong / tongSv) * 100));
    const mau = danhSachMau[idx % danhSachMau.length];
    const wrapper = document.createElement("div");
    wrapper.className = "p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 hover:border-slate-200 transition-all";
    wrapper.innerHTML = `
      <div class="flex justify-between text-xs font-semibold mb-1">
        <span class="text-slate-700">${thoatHtml(nganh)}</span>
        <span class="text-slate-900">${soLuong} sinh viên (${phanTram}%)</span>
      </div>
      <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          class="${mau} h-2 rounded-full transition-all duration-500"
          style="width: ${phanTram}%"
        ></div>
      </div>
    `;
    container.appendChild(wrapper);
  });
}

window.chuyenTabThongKeFaculty = chuyenTabThongKeFaculty;
window.taiBaoCaoSinhVienTheoNganhVaTruong = taiBaoCaoSinhVienTheoNganhVaTruong;
window.locDanhSachFacultyReport = locDanhSachFacultyReport;

function renderLoiTatNghiepVu(choDuyet = 0) {
  const container = document.getElementById("danhSachLoiTatNghiepVu");
  if (!container) return;

  const user = layVaiTroNguoiDungHienTai();
  const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

  if (laMentor) {
    container.innerHTML = `
      <a
        href="cham_cong.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-emerald-50 hover:text-emerald-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">fact_check</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-emerald-800">
              1. Điểm danh hàng ngày
            </p>
            <p class="text-[10px] text-slate-400">
              Chấm công & chuyên cần sinh viên
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="danh_gia.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-rose-50 hover:text-rose-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">rate_review</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-rose-800">
              2. Đánh giá & Chấm điểm
            </p>
            <p class="text-[10px] text-slate-400">
              Phiếu đánh giá kết quả thực tập
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="#khuVucMentorWorkload"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-sky-50 hover:text-sky-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">groups</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-sky-800">
              3. Sinh viên đang kèm cặp
            </p>
            <p class="text-[10px] text-slate-400">
              Khối lượng & nhóm hướng dẫn của tôi
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="danh_gia.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-indigo-50 hover:text-indigo-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">task_alt</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-indigo-800">
              4. Nhiệm vụ & Báo cáo
            </p>
            <p class="text-[10px] text-slate-400">
              Theo dõi tiến độ báo cáo tuần
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>
    `;
  } else {
    container.innerHTML = `
      <a
        href="them_ho_so.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-ictu-50 hover:text-ictu-700 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">person_add</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-ictu-700">
              1. Thêm mới hồ sơ
            </p>
            <p class="text-[10px] text-slate-400">
              Nhập ứng viên mới
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="xet_duyet_ho_so.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-amber-50 hover:text-amber-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">how_to_reg</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-amber-800">
              2. Xét duyệt hồ sơ
            </p>
            <p id="txtLoiTatChoDuyet" class="text-[10px] text-amber-700 font-semibold">
              ${choDuyet} hồ sơ chờ duyệt
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="lich_thuc_tap.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-sky-50 hover:text-sky-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">calendar_month</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-sky-800">
              3. Kế hoạch đợt thực tập
            </p>
            <p class="text-[10px] text-slate-400">
              Cấu hình đợt & thời gian
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="danh_gia.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-rose-50 hover:text-rose-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">rate_review</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-rose-800">
              4. Đánh giá cuối kỳ
            </p>
            <p class="text-[10px] text-slate-400">
              Chấm điểm & xếp loại
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <a
        href="xet_duyet_ho_so.html"
        class="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-emerald-50 hover:text-emerald-800 transition-colors group border border-slate-100"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
            <span class="material-symbols-outlined text-[18px]">history_edu</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-emerald-800">
              5. Ký kết hợp đồng
            </p>
            <p class="text-[10px] text-slate-400">
              Xác nhận thỏa thuận
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </a>

      <button
        type="button"
        onclick="moModalNhapPhuCap()"
        class="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-emerald-50 hover:text-emerald-800 transition-colors group border border-slate-100 text-left cursor-pointer"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-[18px]">payments</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-emerald-800">
              6. Nhập phụ cấp sinh viên
            </p>
            <p class="text-[10px] text-slate-400">
              Chi trả và quản lý quyền lợi
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </button>

      <button
        type="button"
        onclick="moModalDuyetYeuCauHoTro()"
        class="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-violet-50 hover:text-violet-800 transition-colors group border border-slate-100 text-left cursor-pointer"
      >
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-violet-100 text-violet-700 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-[18px]">support_agent</span>
          </span>
          <div>
            <p class="text-xs font-bold text-slate-800 group-hover:text-violet-800">
              8. Xử lý yêu cầu hỗ trợ
            </p>
            <p id="txtLoiTatChoXuLyYeuCau" class="text-[10px] text-slate-400">
              Giấy tờ, con dấu, cơ sở vật chất
            </p>
          </div>
        </div>
        <span class="material-symbols-outlined text-[16px] text-slate-400 group-hover:translate-x-1 transition-transform">chevron_right</span>
      </button>
    `;
  }
}

function napDuLieuCacheDashboard() {
  try {
    const raw = localStorage.getItem("ictu_dashboard_cache");
    if (!raw) {
      capNhatThongTinDotThucTap(null, 0, 0, 0);
      renderLoiTatNghiepVu(0);
      return;
    }
    const cache = JSON.parse(raw);
    const elTong = document.getElementById("kpiTongTTS");
    if (elTong && cache.tongSo !== undefined) elTong.textContent = cache.tongSo.toLocaleString("vi-VN");
    const elChoDuyet = document.getElementById("kpiHoSoChoDuyet");
    if (elChoDuyet && cache.choDuyet !== undefined) elChoDuyet.textContent = cache.choDuyet.toLocaleString("vi-VN");
    const elDaKy = document.getElementById("kpiHopDongDaKy");
    if (elDaKy && cache.daKy !== undefined) elDaKy.textContent = cache.daKy.toLocaleString("vi-VN");
    const elDoanhNghiep = document.getElementById("kpiDoanhNghiep");
    if (elDoanhNghiep && cache.soDoanhNghiep !== undefined) elDoanhNghiep.textContent = cache.soDoanhNghiep.toLocaleString("vi-VN");
    const badgeSidebar = document.getElementById("sidebarBadgeChoDuyet");
    if (badgeSidebar && cache.choDuyet !== undefined) badgeSidebar.textContent = `${cache.choDuyet} chờ`;
    const elLoiTatChoDuyet = document.getElementById("txtLoiTatChoDuyet");
    if (elLoiTatChoDuyet && cache.choDuyet !== undefined) elLoiTatChoDuyet.textContent = `${cache.choDuyet} hồ sơ chờ duyệt`;
    
    if (cache.programData) {
      capNhatThongTinDotThucTap(cache.programData, cache.tongSo || 0, cache.choDuyet || 0, cache.daKy || 0);
    } else {
      capNhatThongTinDotThucTap(null, cache.tongSo || 0, cache.choDuyet || 0, cache.daKy || 0);
    }
    if (cache.danhSach && cache.danhSach.length > 0) {
      renderBangSinhVien(cache.danhSach);
    }
    if (cache.danhSachNganh && cache.danhSachNganh.length > 0) {
      renderPhanBoNganh(cache.danhSachNganh);
    }
    renderLoiTatNghiepVu(cache.choDuyet || 0);
  } catch {
    capNhatThongTinDotThucTap(null, 0, 0, 0);
    renderLoiTatNghiepVu(0);
  }
}

async function taiDuLieuDashboard() {
  try {
    const [resInterns, resUnis, resSupport] = await Promise.all([
      fetch(`${duongDanApi}/interns`),
      fetch(`${duongDanApi}/universities`).catch(() => null),
      fetch(`${duongDanApi}/support-requests`).catch(() => null)
    ]);

    if (!resInterns.ok) return;
    const json = await resInterns.json();
    const danhSach = json.data || [];
    const tongSo = json.total !== undefined ? json.total : danhSach.length;

    const choDuyet = danhSach.filter((x) => x.trang_thai_xet_duyet === "ChoDuyet").length;
    const daKy = danhSach.filter((x) => x.trang_thai_thuc_tap === "DangThucTap" || x.trang_thai_xet_duyet === "DaDuyet").length;
    
    const setDoanhNghiep = new Set();
    danhSach.forEach((x) => {
      if (x.ten_mentor) setDoanhNghiep.add(x.ten_mentor);
      if (x.ten_truong) setDoanhNghiep.add(x.ten_truong);
    });

    if (resUnis && resUnis.ok) {
      try {
        const jsonUnis = await resUnis.json();
        const arrUnis = jsonUnis.data || [];
        arrUnis.forEach((u) => {
          if (u.ten_truong) setDoanhNghiep.add(u.ten_truong);
        });
      } catch {}
    }

    if (resSupport && resSupport.ok) {
      try {
        const jsonSupport = await resSupport.json();
        cacheDanhSachYeuCauHoTro = jsonSupport.data || [];
        capNhatSoLuongYeuCauChoXuLy();
      } catch {}
    }

    const soDoanhNghiep = setDoanhNghiep.size;

    const user = layVaiTroNguoiDungHienTai();
    const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

    const lblKpi1 = document.getElementById("lblKpi1");
    const lblKpi2 = document.getElementById("lblKpi2");
    const lblKpi3 = document.getElementById("lblKpi3");
    const lblKpi4 = document.getElementById("lblKpi4");

    const elTong = document.getElementById("kpiTongTTS");
    const elChoDuyet = document.getElementById("kpiHoSoChoDuyet");
    const elDaKy = document.getElementById("kpiHopDongDaKy");
    const elDoanhNghiep = document.getElementById("kpiDoanhNghiep");
    const badgeSidebar = document.getElementById("sidebarBadgeChoDuyet");
    const elLoiTatChoDuyet = document.getElementById("txtLoiTatChoDuyet");

    if (laMentor) {
      const svCuaMentor = danhSach.filter((sv) => {
        if (sv.ma_mentor && (sv.ma_mentor === user.id || sv.ma_mentor === user.ma_nguoi_dung)) return true;
        if (user.ho_ten && sv.ten_mentor && (sv.ten_mentor.toLowerCase().includes(user.ho_ten.toLowerCase()) || user.ho_ten.toLowerCase().includes(sv.ten_mentor.toLowerCase()))) return true;
        return false;
      });
      const slKpi = svCuaMentor.length;
      const maxKpi = user.chi_tieu_huong_dan || 5;
      const choTrongKpi = Math.max(0, maxKpi - slKpi);

      if (lblKpi1) lblKpi1.textContent = "SV Tôi Đang Kèm";
      if (elTong) elTong.textContent = `${slKpi} sinh viên`;

      if (lblKpi2) lblKpi2.textContent = "Chỉ Tiêu Hướng Dẫn";
      if (elChoDuyet) elChoDuyet.textContent = `${maxKpi} SV`;

      if (lblKpi3) lblKpi3.textContent = "Chỗ Khả Dụng";
      if (elDaKy) elDaKy.textContent = `${choTrongKpi} chỗ`;

      if (lblKpi4) lblKpi4.textContent = "Đơn Vị Hướng Dẫn";
      if (elDoanhNghiep) elDoanhNghiep.textContent = user.ten_phong_ban || user.chuc_vu || "Mentor Doanh nghiệp";

      if (badgeSidebar) badgeSidebar.style.display = "none";
      if (elLoiTatChoDuyet) elLoiTatChoDuyet.textContent = "Dành cho cán bộ HR";
    } else {
      if (lblKpi1) lblKpi1.textContent = "Tổng Thực Tập Sinh";
      if (elTong) elTong.textContent = tongSo.toLocaleString("vi-VN");

      if (lblKpi2) lblKpi2.textContent = "Hồ Sơ Chờ Duyệt";
      if (elChoDuyet) elChoDuyet.textContent = choDuyet.toLocaleString("vi-VN");

      if (lblKpi3) lblKpi3.textContent = "Hợp Đồng Đã Ký";
      if (elDaKy) elDaKy.textContent = daKy.toLocaleString("vi-VN");

      if (lblKpi4) lblKpi4.textContent = "Doanh Nghiệp Liên Kết";
      if (elDoanhNghiep) elDoanhNghiep.textContent = soDoanhNghiep.toLocaleString("vi-VN");

      if (badgeSidebar) {
        badgeSidebar.style.display = "";
        badgeSidebar.textContent = `${choDuyet} chờ`;
      }
      if (elLoiTatChoDuyet) {
        elLoiTatChoDuyet.textContent = `${choDuyet} hồ sơ chờ duyệt`;
      }
    }

    const itemCoChuongTrinh = danhSach.find((x) => x.ten_chuong_trinh && x.ngay_bat_dau && x.ngay_ket_thuc);
    const progData = itemCoChuongTrinh ? {
      ten_chuong_trinh: itemCoChuongTrinh.ten_chuong_trinh,
      ngay_bat_dau: itemCoChuongTrinh.ngay_bat_dau,
      ngay_ket_thuc: itemCoChuongTrinh.ngay_ket_thuc
    } : null;

    capNhatThongTinDotThucTap(progData, tongSo, choDuyet, daKy);
    renderBangSinhVien(danhSach);
    taiBaoCaoSinhVienTheoNganhVaTruong(danhSach);
    renderLoiTatNghiepVu(choDuyet);

    try {
      localStorage.setItem("ictu_dashboard_cache", JSON.stringify({
        tongSo,
        choDuyet,
        daKy,
        soDoanhNghiep,
        programData: progData,
        danhSach: danhSach.slice(0, 6),
        danhSachNganh: danhSach
      }));
    } catch {}
  } catch (err) {}
}

let danhSachWorkloadGoc = [];
let tabWorkloadHienTai = "all";
let cheDoXemWorkload = "card";

function chuyenCheDoXemWorkload(cheDo) {
  cheDoXemWorkload = cheDo;
  const btnCard = document.getElementById("btnCheDoCard");
  const btnBang = document.getElementById("btnCheDoBang");
  const containerCard = document.getElementById("danhSachMentorWorkload");
  const containerBang = document.getElementById("bangMentorWorkloadContainer");

  const classActive = "p-1 rounded-lg bg-white text-slate-900 shadow-xs";
  const classInactive = "p-1 rounded-lg text-slate-500 hover:text-slate-900";

  if (btnCard) btnCard.className = cheDo === "card" ? classActive : classInactive;
  if (btnBang) btnBang.className = cheDo === "table" ? classActive : classInactive;

  if (cheDo === "card") {
    if (containerCard) containerCard.classList.remove("hidden");
    if (containerBang) containerBang.classList.add("hidden");
  } else {
    if (containerCard) containerCard.classList.add("hidden");
    if (containerBang) containerBang.classList.remove("hidden");
  }

  renderDanhSachMentorWorkload();
}

function locMentorWorkload(tab) {
  tabWorkloadHienTai = tab;
  const btnAll = document.getElementById("tabWorkloadAll");
  const btnActive = document.getElementById("tabWorkloadActive");
  const btnFull = document.getElementById("tabWorkloadFull");
  const btnOverload = document.getElementById("tabWorkloadOverload");

  const classActive = "px-3 py-1 rounded-lg bg-white text-slate-900 shadow-xs font-bold";
  const classInactive = "px-3 py-1 rounded-lg hover:text-slate-900 font-medium text-slate-600";

  if (btnAll) btnAll.className = tab === "all" ? classActive : classInactive;
  if (btnActive) btnActive.className = tab === "active" ? "px-3 py-1 rounded-lg bg-emerald-50 text-emerald-800 shadow-xs font-bold" : classInactive;
  if (btnFull) btnFull.className = tab === "full" ? "px-3 py-1 rounded-lg bg-amber-50 text-amber-800 shadow-xs font-bold" : "px-3 py-1 rounded-lg hover:text-amber-800 font-medium text-slate-600";
  if (btnOverload) btnOverload.className = tab === "overload" ? "px-3 py-1 rounded-lg bg-rose-50 text-rose-700 shadow-xs font-bold" : "px-3 py-1 rounded-lg hover:text-rose-700 font-medium text-slate-600";

  renderDanhSachMentorWorkload();
}

function layVaiTroNguoiDungHienTai() {
  if (typeof layThongTinSession === "function") {
    const admin = layThongTinSession("manager");
    if (admin) return admin;
  }
  try {
    const raw = localStorage.getItem("ictu_admin_session") || localStorage.getItem("user") || localStorage.getItem("currentUser");
    if (raw) return JSON.parse(raw);
  } catch {}
  return null;
}

async function renderGiaoDienChoMentor(myMentor, containerCard) {
  const sl = myMentor ? (myMentor.so_sinh_vien_huong_dan || 0) : 0;
  const maxHd = myMentor ? (myMentor.chi_tieu_huong_dan || 5) : 5;
  const percent = myMentor ? (myMentor.ty_le_phan_tram || Math.round((sl / maxHd) * 100)) : 0;
  const isQuaTai = sl > 5;
  const isDaDu = sl === 5;
  const initials = layTenVietTat(myMentor.ho_ten);

  let mauThanh = "bg-emerald-500";
  let mauChu = "text-emerald-700 font-bold";
  let badgeHtml = "";

  if (isQuaTai) {
    mauThanh = "bg-rose-500";
    mauChu = "text-rose-700 font-bold";
    badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300 animate-pulse"><span class="material-symbols-outlined text-[13px]">warning</span> Quá tải (${sl}/${maxHd})</span>`;
  } else if (isDaDu) {
    mauThanh = "bg-amber-500";
    mauChu = "text-amber-700 font-bold";
    badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300"><span class="material-symbols-outlined text-[13px]">lock</span> Đã đủ (5/5)</span>`;
  } else if (sl === 0) {
    mauThanh = "bg-slate-300";
    mauChu = "text-slate-500 font-semibold";
    badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">Còn 5 chỗ (0/5)</span>`;
  } else {
    mauThanh = sl >= 3 ? "bg-blue-500" : "bg-emerald-500";
    mauChu = sl >= 3 ? "text-blue-700 font-bold" : "text-emerald-700 font-bold";
    badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Còn ${maxHd - sl} chỗ (${sl}/${maxHd})</span>`;
  }

  let warningBox = "";
  if (isQuaTai) {
    warningBox = `
      <div class="col-span-full p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-900 flex items-start gap-3">
        <div class="w-8 h-8 rounded-lg bg-rose-200 text-rose-700 flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-[20px]">warning</span>
        </div>
        <div class="flex-1">
          <h4 class="font-bold text-xs uppercase tracking-wide text-rose-800">Cảnh Báo Vượt Định Mức Hướng Dẫn</h4>
          <p class="text-xs text-rose-700 mt-0.5 leading-relaxed font-medium">
            Bạn hiện đang phụ trách <strong>${sl}/5</strong> sinh viên (vượt quá <strong>${sl - 5}</strong> sinh viên so với chỉ tiêu tối đa). Vui lòng liên hệ với bộ phận Quản lý / HR để điều phối bớt sinh viên sang Mentor khác nhằm đảm bảo chất lượng hướng dẫn!
          </p>
        </div>
      </div>
    `;
  }

  containerCard.innerHTML = `
    ${warningBox}
    <div class="col-span-full bg-slate-50/70 border border-slate-200/80 rounded-2xl p-5 space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-3.5">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-bold flex items-center justify-center text-base shadow-sm shrink-0">
            ${initials}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h4 class="text-base font-bold text-slate-900">${myMentor.ho_ten}</h4>
              ${badgeHtml}
            </div>
            <p class="text-xs text-slate-500 mt-0.5">${myMentor.ten_phong_ban || myMentor.chuc_vu || "Mentor Doanh nghiệp"} &bull; ${myMentor.email || ""}</p>
          </div>
        </div>
        <div>
          <p class="text-xs text-slate-500 font-medium">Tỷ lệ công việc cá nhân</p>
          <p class="text-lg font-black ${mauChu}">${sl}/${maxHd} SV (${percent}%)</p>
        </div>
      </div>
      <div class="space-y-1.5">
        <div class="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
          <div class="${mauThanh} h-2.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, percent)}%"></div>
        </div>
      </div>
    </div>

    <div id="khuVucMentorInterns" class="col-span-full bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
      <div class="px-5 py-3.5 bg-slate-50/80 border-b border-slate-200/80 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-[18px] text-ictu-600">groups</span>
          <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wide">
            Danh Sách Sinh Viên Bạn Đang Kèm Cặp (${sl} sinh viên)
          </h4>
        </div>
        <div class="flex items-center gap-2">
          <button type="button" onclick="moModalGiaoViecNhanhMentor()" class="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm transition-all cursor-pointer">
            <span class="material-symbols-outlined text-[16px]">add_task</span>
            <span>+ Giao nhiệm vụ</span>
          </button>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 text-slate-600 uppercase font-bold text-[11px] border-b border-slate-100">
            <tr>
              <th class="py-2.5 px-4">STT</th>
              <th class="py-2.5 px-4">Sinh Viên</th>
              <th class="py-2.5 px-4">Liên Hệ</th>
              <th class="py-2.5 px-4">Chuyên Ngành &amp; Lớp</th>
              <th class="py-2.5 px-4 text-center">Trạng Thái</th>
              <th class="py-2.5 px-4 text-right">Thao Tác</th>
            </tr>
          </thead>
          <tbody id="tbodySvMentorDashboard" class="divide-y divide-slate-100">
            <tr>
              <td colspan="6" class="py-6 text-center text-slate-400">
                <span class="inline-block w-4 h-4 border-2 border-ictu-600 border-t-transparent rounded-full animate-spin mb-1"></span>
                <p>Đang tải danh sách sinh viên của bạn...</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;

  try {
    const res = await fetch(`${duongDanApi}/interns?ma_mentor=${myMentor.ma_mentor}`);
    const tbody = document.getElementById("tbodySvMentorDashboard");
    if (!tbody) return;
    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-rose-500 font-medium">Không thể tải danh sách sinh viên.</td></tr>`;
      return;
    }
    const json = await res.json();
    const ds = json.data || [];
    danhSachSinhVienMentorCuaToi = ds;
    if (ds.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-400">Bạn chưa có sinh viên nào được phân công.</td></tr>`;
      return;
    }
    let rows = "";
    ds.forEach((sv, i) => {
      const initialsSv = layTenVietTat(sv.ho_ten);
      const hoTenSv = sv.ho_ten || "Sinh viên";
      const emailSv = sv.email || "N/A";
      const sdtSv = sv.so_dien_thoai || "";
      const chuyenNganhSv = sv.chuyen_nganh || "Công nghệ thông tin";
      const lopSv = sv.lop || "KTPM-K19A";
      let badgeTrangThai = "";
      if (sv.trang_thai_thuc_tap === "DangThucTap") {
        badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Đang thực tập</span>`;
      } else if (sv.trang_thai_thuc_tap === "HoanThanh") {
        badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200"><span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span> Hoàn thành</span>`;
      } else if (sv.trang_thai_thuc_tap === "ChuaThucTap") {
        badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Chờ ký HĐ</span>`;
      } else {
        badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">${sv.trang_thai_thuc_tap || "Chưa rõ"}</span>`;
      }

      rows += `
        <tr class="hover:bg-slate-50 transition-colors">
          <td class="py-3 px-4 text-slate-400 font-medium">${i + 1}</td>
          <td class="py-3 px-4">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-ictu-100 text-ictu-700 font-bold flex items-center justify-center text-xs shrink-0">
                ${initialsSv}
              </div>
              <div>
                <p class="font-bold text-slate-900">${hoTenSv}</p>
                <p class="text-[11px] text-slate-400">${sv.ten_truong || "ICTU"}</p>
              </div>
            </div>
          </td>
          <td class="py-3 px-4 text-slate-500">
            <p>${emailSv}</p>
            <p class="text-[10px] text-slate-400">${sdtSv}</p>
          </td>
          <td class="py-3 px-4 text-slate-600">
            <p class="font-medium">${chuyenNganhSv}</p>
            <p class="text-[10px] text-slate-400">${lopSv}</p>
          </td>
          <td class="py-3 px-4 text-center">
            ${badgeTrangThai}
          </td>
          <td class="py-3 px-4 text-right">
            <div class="inline-flex items-center gap-1.5">
              <button type="button" onclick="moModalGiaoViec(${sv.ma_ho_so}, '${encodeURIComponent(hoTenSv)}')" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-700 transition-colors flex items-center gap-1 cursor-pointer">
                <span class="material-symbols-outlined text-[13px]">add_task</span>
                <span>Giao việc</span>
              </button>
              <button type="button" onclick="moModalXemNhiemVuSv(${sv.ma_ho_so}, '${encodeURIComponent(hoTenSv)}')" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-700 transition-colors flex items-center gap-1 cursor-pointer">
                <span class="material-symbols-outlined text-[13px]">checklist</span>
                <span>Nhiệm vụ</span>
              </button>
              <a href="cham_cong.html" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors">
                Điểm danh
              </a>
              <a href="danh_gia.html" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-ictu-50 hover:bg-ictu-100 text-ictu-700 transition-colors">
                Đánh giá
              </a>
            </div>
          </td>
        </tr>
      `;
    });
    tbody.innerHTML = rows;
  } catch (e) {
    const tbody = document.getElementById("tbodySvMentorDashboard");
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-rose-500 font-medium">Lỗi kết nối khi tải sinh viên.</td></tr>`;
  }
}

function capNhatKpiWorkload() {
  const user = layVaiTroNguoiDungHienTai();
  const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

  const elTongMentor = document.getElementById("kpiWorkloadTongMentor");
  const elTongSv = document.getElementById("kpiWorkloadTongSv");
  const elQuaTai = document.getElementById("kpiWorkloadQuaTai");
  const elChoTrong = document.getElementById("kpiWorkloadChoTrong");
  const theQuaTai = document.getElementById("theKpiQuaTai");
  const iconQuaTai = document.getElementById("iconKpiQuaTai");

  const lbl1 = document.getElementById("lblKpiWorkload1");
  const lbl2 = document.getElementById("lblKpiWorkload2");
  const lbl3 = document.getElementById("lblKpiWorkload3");
  const lbl4 = document.getElementById("lblKpiWorkload4");

  if (laMentor) {
    let myMentor = danhSachWorkloadGoc.find(m => m.ma_mentor === user.ma_nguoi_dung);
    if (!myMentor && danhSachWorkloadGoc.length > 0) {
      myMentor = danhSachWorkloadGoc[0];
    }
    const sl = myMentor ? (myMentor.so_sinh_vien_huong_dan || 0) : 0;
    const maxHd = myMentor ? (myMentor.chi_tieu_huong_dan || 5) : 5;
    const isQuaTai = sl > 5;
    const isDaDu = sl === 5;
    const choTrong = Math.max(0, maxHd - sl);

    if (lbl1) lbl1.textContent = "Chỉ Tiêu Hướng Dẫn";
    if (elTongMentor) elTongMentor.textContent = `${maxHd} SV`;

    if (lbl2) lbl2.textContent = "SV Đang Kèm Cặp";
    if (elTongSv) elTongSv.textContent = `${sl} SV`;

    if (lbl3) lbl3.textContent = "Trạng Thái Tải";
    if (elQuaTai) elQuaTai.textContent = isQuaTai ? `Quá tải (${sl}/${maxHd})` : (isDaDu ? "Đã đủ (5/5)" : `Đang kèm (${sl}/${maxHd})`);

    if (lbl4) lbl4.textContent = "Chỗ Tiếp Nhận Còn";
    if (elChoTrong) elChoTrong.textContent = `${choTrong} chỗ`;

    if (theQuaTai && iconQuaTai) {
      if (isQuaTai) {
        theQuaTai.className = "bg-rose-50/80 border border-rose-300 rounded-xl p-3 flex items-center gap-3 transition-colors ring-1 ring-rose-200";
        iconQuaTai.className = "w-9 h-9 rounded-lg bg-rose-200 text-rose-700 flex items-center justify-center shrink-0 animate-pulse";
        if (elQuaTai) elQuaTai.className = "text-base font-bold text-rose-700 leading-tight";
      } else {
        theQuaTai.className = "bg-slate-50 border border-slate-200/70 rounded-xl p-3 flex items-center gap-3 transition-colors";
        iconQuaTai.className = "w-9 h-9 rounded-lg bg-slate-200 text-slate-600 flex items-center justify-center shrink-0";
        if (elQuaTai) elQuaTai.className = "text-base font-bold text-slate-900 leading-tight";
      }
    }
    return;
  }

  if (lbl1) lbl1.textContent = "Tổng Mentor";
  if (lbl2) lbl2.textContent = "SV Đang Kèm";
  if (lbl3) lbl3.textContent = "Quá Tải (> 5 SV)";
  if (lbl4) lbl4.textContent = "Chỗ Trống Khả Dụng";

  const tongMentor = danhSachWorkloadGoc.length;
  let tongSv = 0;
  let soQuaTai = 0;
  let soDaDu = 0;
  let choTrong = 0;

  danhSachWorkloadGoc.forEach((m) => {
    const sl = m.so_sinh_vien_huong_dan || 0;
    tongSv += sl;
    if (sl > 5) soQuaTai += 1;
    else if (sl === 5) soDaDu += 1;
    choTrong += Math.max(0, 5 - sl);
  });

  if (elTongMentor) elTongMentor.textContent = tongMentor;
  if (elTongSv) elTongSv.textContent = `${tongSv} SV`;
  if (elQuaTai) elQuaTai.textContent = soQuaTai;
  if (elChoTrong) elChoTrong.textContent = `${choTrong} chỗ`;

  if (theQuaTai && iconQuaTai) {
    if (soQuaTai > 0) {
      theQuaTai.className = "bg-rose-50/80 border border-rose-300 rounded-xl p-3 flex items-center gap-3 transition-colors ring-1 ring-rose-200";
      iconQuaTai.className = "w-9 h-9 rounded-lg bg-rose-200 text-rose-700 flex items-center justify-center shrink-0 animate-pulse";
      if (elQuaTai) elQuaTai.className = "text-base font-bold text-rose-700 leading-tight";
    } else {
      theQuaTai.className = "bg-slate-50 border border-slate-200/70 rounded-xl p-3 flex items-center gap-3 transition-colors";
      iconQuaTai.className = "w-9 h-9 rounded-lg bg-slate-200 text-slate-600 flex items-center justify-center shrink-0";
      if (elQuaTai) elQuaTai.className = "text-base font-bold text-slate-900 leading-tight";
    }
  }

  const elDemAll = document.getElementById("demWorkloadAll");
  const elDemActive = document.getElementById("demWorkloadActive");
  const elDemFull = document.getElementById("demWorkloadFull");
  const elDemOverload = document.getElementById("demWorkloadOverload");

  if (elDemAll) elDemAll.textContent = tongMentor;
  if (elDemActive) elDemActive.textContent = danhSachWorkloadGoc.filter((m) => (m.so_sinh_vien_huong_dan || 0) > 0 && (m.so_sinh_vien_huong_dan || 0) < 5).length;
  if (elDemFull) elDemFull.textContent = soDaDu;
  if (elDemOverload) elDemOverload.textContent = soQuaTai;
}

function renderDanhSachMentorWorkload() {
  capNhatKpiWorkload();

  const user = layVaiTroNguoiDungHienTai();
  const laMentor = user && (user.vai_tro === "Mentor" || user.vai_tro === "mentor");

  const tieuDe = document.getElementById("tieuDeKhuVucWorkload");
  const moTa = document.getElementById("moTaKhuVucWorkload");
  const cucBoLoc = document.getElementById("cucBoLocWorkload");
  const cucCheDo = document.getElementById("cucCheDoXemWorkload");
  const btnPhanCong = document.getElementById("btnPhanCongWorkload");
  const btnThemMentor = document.getElementById("btnMoModalThemMentor");

  const containerCard = document.getElementById("danhSachMentorWorkload");
  const containerBang = document.getElementById("bangMentorWorkloadContainer");
  const tbodyBang = document.getElementById("bangMentorWorkloadTbody");

  if (laMentor) {
    if (tieuDe) tieuDe.textContent = "Khối Lượng Hướng Dẫn Của Tôi (My Capacity & Interns)";
    if (moTa) moTa.textContent = "Theo dõi số lượng sinh viên bạn đang trực tiếp phụ trách (Định mức tối đa: 5 sinh viên)";
    if (cucBoLoc) cucBoLoc.style.display = "none";
    if (cucCheDo) cucCheDo.style.display = "none";
    if (btnPhanCong) btnPhanCong.style.display = "none";
    if (btnThemMentor) btnThemMentor.style.display = "none";
    if (containerBang) containerBang.classList.add("hidden");
    if (containerCard) containerCard.classList.remove("hidden");

    let myMentor = danhSachWorkloadGoc.find(m => m.ma_mentor === user.ma_nguoi_dung);
    if (!myMentor && danhSachWorkloadGoc.length > 0) {
      myMentor = danhSachWorkloadGoc[0];
    }
    if (!myMentor) {
      if (containerCard) {
        containerCard.innerHTML = `
          <div class="col-span-full py-8 text-center text-xs text-slate-400">
            Không tìm thấy thông tin hướng dẫn của bạn
          </div>
        `;
      }
      return;
    }

    renderGiaoDienChoMentor(myMentor, containerCard);
    return;
  }

  if (tieuDe) tieuDe.textContent = "Khối Lượng Hướng Dẫn Mentor (Workload & Capacity)";
  if (moTa) moTa.textContent = "Theo dõi tải công việc và cảnh báo phân công vượt chỉ tiêu tối đa (5 sinh viên / Mentor)";
  if (cucBoLoc) cucBoLoc.style.display = "";
  if (cucCheDo) cucCheDo.style.display = "";
  if (btnPhanCong) btnPhanCong.style.display = "";
  if (btnThemMentor) btnThemMentor.style.display = "";

  let danhSachLoc = [...danhSachWorkloadGoc];
  if (tabWorkloadHienTai === "active") {
    danhSachLoc = danhSachLoc.filter((m) => (m.so_sinh_vien_huong_dan || 0) > 0 && (m.so_sinh_vien_huong_dan || 0) < 5);
  } else if (tabWorkloadHienTai === "full") {
    danhSachLoc = danhSachLoc.filter((m) => (m.so_sinh_vien_huong_dan || 0) === 5);
  } else if (tabWorkloadHienTai === "overload") {
    danhSachLoc = danhSachLoc.filter((m) => (m.so_sinh_vien_huong_dan || 0) > 5);
  }

  const bangMau = [
    "from-blue-600 to-indigo-600",
    "from-sky-500 to-ictu-600",
    "from-emerald-500 to-teal-600",
    "from-purple-500 to-indigo-600",
    "from-amber-500 to-orange-600"
  ];

  if (danhSachLoc.length === 0) {
    const emptyHtml = `
      <div class="col-span-full py-10 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-4xl text-slate-300 block mb-2">group_off</span>
        <p class="font-semibold text-slate-600">Không có dữ liệu Mentor trong trạng thái lọc này</p>
        <p class="text-[11px] text-slate-400 mt-0.5">Vui lòng chọn tab lọc khác để xem danh sách</p>
      </div>
    `;
    if (containerCard) containerCard.innerHTML = emptyHtml;
    if (tbodyBang) {
      tbodyBang.innerHTML = `
        <tr>
          <td colspan="8" class="py-8 text-center text-slate-400 font-medium">
            Không có Mentor nào trong nhóm lọc này
          </td>
        </tr>
      `;
    }
    return;
  }

  let htmlCards = "";
  let htmlTableRows = "";

  danhSachLoc.forEach((m, idx) => {
    const sl = m.so_sinh_vien_huong_dan || 0;
    const maxHd = m.chi_tieu_huong_dan || 5;
    const percent = Math.min(100, Math.round((sl / maxHd) * 100));
    const isQuaTai = sl > 5;
    const isDaDu = sl === 5;
    const initials = layTenVietTat(m.ho_ten);
    const mauGradient = bangMau[idx % bangMau.length];

    let mauThanh = "bg-emerald-500";
    let mauChu = "text-emerald-700 font-bold";
    let badgeHtml = "";
    let cardClass = "bg-slate-50/60 border border-slate-200/80 rounded-2xl p-4.5 space-y-3.5 transition-all hover:bg-white hover:shadow-sm";
    let alertMsgHtml = "";

    if (isQuaTai) {
      mauThanh = "bg-rose-500";
      mauChu = "text-rose-700 font-bold";
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300 animate-pulse"><span class="material-symbols-outlined text-[13px]">warning</span> Quá tải (${sl}/${maxHd})</span>`;
      cardClass = "bg-rose-50/30 border border-rose-300 ring-2 ring-rose-200/80 rounded-2xl p-4.5 space-y-3.5 transition-all shadow-xs";
      alertMsgHtml = `
        <div class="px-2.5 py-1.5 rounded-lg bg-rose-100/80 border border-rose-200 text-[11px] text-rose-800 font-medium flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[14px] text-rose-600">error</span>
          <span>Vượt quá ${sl - maxHd} SV so với định mức quy định</span>
        </div>
      `;
    } else if (isDaDu) {
      mauThanh = "bg-amber-500";
      mauChu = "text-amber-700 font-bold";
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300"><span class="material-symbols-outlined text-[13px]">lock</span> Đã đủ (5/5)</span>`;
    } else if (sl === 0) {
      mauThanh = "bg-slate-300";
      mauChu = "text-slate-500 font-semibold";
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">Còn 5 chỗ (0/5)</span>`;
    } else {
      mauThanh = sl >= 3 ? "bg-blue-500" : "bg-emerald-500";
      mauChu = sl >= 3 ? "text-blue-700 font-bold" : "text-emerald-700 font-bold";
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Còn ${maxHd - sl} chỗ (${sl}/${maxHd})</span>`;
    }

    htmlCards += `
      <div class="${cardClass}">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr ${mauGradient} text-white font-bold flex items-center justify-center text-sm shadow-xs shrink-0">
              ${initials}
            </div>
            <div class="min-w-0">
              <h4 class="text-sm font-bold text-slate-900 truncate leading-tight">${m.ho_ten || "Mentor"}</h4>
              <p class="text-[11px] text-slate-500 truncate mt-0.5">${m.ten_phong_ban || m.chuc_vu || "Mentor Doanh nghiệp"}</p>
            </div>
          </div>
          ${badgeHtml}
        </div>

        ${alertMsgHtml}

        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-500 font-medium">Tải kèm cặp</span>
            <span class="${mauChu}">${sl}/${maxHd} SV (${m.ty_le_phan_tram || percent}%)</span>
          </div>
          <div class="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
            <div class="${mauThanh} h-2 rounded-full transition-all duration-500" style="width: ${percent}%"></div>
          </div>
        </div>

        <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
          <button type="button" onclick="moModalChiTietSvMentor(${m.ma_mentor})" class="font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 cursor-pointer">
            <span class="material-symbols-outlined text-[15px]">groups</span>
            <span>Chi tiết (${sl})</span>
          </button>
          <a href="them_ho_so.html" class="font-semibold text-ictu-600 hover:text-ictu-800 shrink-0 flex items-center gap-0.5">
            <span>Phân công</span>
            <span class="material-symbols-outlined text-[13px]">chevron_right</span>
          </a>
        </div>
      </div>
    `;

    htmlTableRows += `
      <tr class="hover:bg-slate-50/80 transition-colors ${isQuaTai ? 'bg-rose-50/20' : ''}">
        <td class="py-3 px-4 text-slate-400 font-medium">${idx + 1}</td>
        <td class="py-3 px-4">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-tr ${mauGradient} text-white font-bold flex items-center justify-center text-xs shrink-0 shadow-xs">
              ${initials}
            </div>
            <div>
              <p class="font-bold text-slate-900 leading-tight">${m.ho_ten || "Mentor"}</p>
              <p class="text-[11px] text-slate-400">${m.chuc_vu || "Mentor Doanh nghiệp"}</p>
            </div>
          </div>
        </td>
        <td class="py-3 px-4 text-slate-600 font-medium">${m.ten_phong_ban || "Chưa phân bổ"}</td>
        <td class="py-3 px-4 text-slate-500">
          <p class="text-[11px]">${m.email || "N/A"}</p>
          <p class="text-[10px] text-slate-400">${m.so_dien_thoai || ""}</p>
        </td>
        <td class="py-3 px-4 text-center font-bold ${mauChu}">
          ${sl} / ${maxHd} SV
        </td>
        <td class="py-3 px-4">
          <div class="space-y-1">
            <div class="flex items-center justify-between text-[11px]">
              <span class="text-slate-400">Tiến độ</span>
              <span class="${mauChu}">${m.ty_le_phan_tram || percent}%</span>
            </div>
            <div class="w-full bg-slate-200/80 rounded-full h-1.5 overflow-hidden">
              <div class="${mauThanh} h-1.5 rounded-full" style="width: ${percent}%"></div>
            </div>
          </div>
        </td>
        <td class="py-3 px-4 text-center">
          ${badgeHtml}
        </td>
        <td class="py-3 px-4 text-right">
          <div class="inline-flex items-center gap-1.5">
            <button type="button" onclick="moModalChiTietSvMentor(${m.ma_mentor})" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors cursor-pointer">
              Xem SV
            </button>
            <a href="them_ho_so.html" class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-ictu-50 hover:bg-ictu-100 text-ictu-700 transition-colors">
              Gán SV
            </a>
          </div>
        </td>
      </tr>
    `;
  });

  if (containerCard) containerCard.innerHTML = htmlCards;
  if (tbodyBang) tbodyBang.innerHTML = htmlTableRows;
}

async function taiDuLieuMentorWorkload() {
  const containerCard = document.getElementById("danhSachMentorWorkload");
  const errorBox = document.getElementById("thongBaoLoiWorkload");
  const errorMsg = document.getElementById("noiDungLoiWorkload");

  if (errorBox) errorBox.classList.add("hidden");

  if (containerCard && danhSachWorkloadGoc.length === 0) {
    containerCard.innerHTML = `
      <div class="col-span-full py-8 text-center text-xs text-slate-400">
        <span class="inline-block w-8 h-8 border-2 border-ictu-600 border-t-transparent rounded-full animate-spin mb-2"></span>
        <p>Đang tải dữ liệu khối lượng hướng dẫn Mentor...</p>
      </div>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/mentors/workload`);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      let msg = "Không thể tải báo cáo khối lượng mentor từ máy chủ.";
      if (typeof errData.detail === "string") {
        msg = errData.detail;
      } else if (Array.isArray(errData.detail) && errData.detail.length > 0) {
        msg = errData.detail.map(d => d.msg || d.message).join("; ");
      } else if (errData.message) {
        msg = errData.message;
      }
      if (errorBox && errorMsg) {
        errorMsg.textContent = msg;
        errorBox.classList.remove("hidden");
      }
      if (containerCard) {
        containerCard.innerHTML = `
          <div class="col-span-full py-8 text-center text-xs text-rose-500">
            <span class="material-symbols-outlined text-3xl mb-1">error</span>
            <p>${msg}</p>
          </div>
        `;
      }
      return;
    }

    const json = await res.json();
    const rawData = json.data || {};
    if (Array.isArray(rawData)) {
      danhSachWorkloadGoc = rawData;
    } else if (Array.isArray(rawData.danh_sach_workload)) {
      danhSachWorkloadGoc = rawData.danh_sach_workload;
    } else {
      danhSachWorkloadGoc = [];
    }
    renderDanhSachMentorWorkload();
  } catch (err) {
    if (errorBox && errorMsg) {
      errorMsg.textContent = "Mất kết nối đến máy chủ Backend. Vui lòng kiểm tra lại dịch vụ kết nối.";
      errorBox.classList.remove("hidden");
    }
    if (containerCard) {
      containerCard.innerHTML = `
        <div class="col-span-full py-8 text-center text-xs text-rose-500">
          <span class="material-symbols-outlined text-3xl mb-1">error</span>
          <p>${err.message || "Lỗi xử lý dữ liệu"}</p>
        </div>
      `;
    }
  }
}

async function moModalChiTietSvMentor(maMentor) {
  const modal = document.getElementById("modalChiTietSvMentor");
  const tieuDe = document.getElementById("tieuDeModalChiTietSv");
  const moTa = document.getElementById("moTaModalChiTietSv");
  const canhBao = document.getElementById("canhBaoQuaTaiModal");
  const txtCanhBao = document.getElementById("txtCanhBaoQuaTaiModal");
  const tbody = document.getElementById("tbodyDanhSachSvMentor");

  const mentor = danhSachWorkloadGoc.find((m) => m.ma_mentor === maMentor);
  if (!modal || !mentor) return;

  const sl = mentor.so_sinh_vien_huong_dan || 0;
  if (tieuDe) tieuDe.textContent = `Sinh Viên Hướng Dẫn: ${mentor.ho_ten}`;
  if (moTa) moTa.textContent = `${mentor.chuc_vu || "Mentor"} - ${mentor.ten_phong_ban || "Đang phụ trách"} (${sl}/5 sinh viên)`;

  if (canhBao && txtCanhBao) {
    if (sl > 5) {
      canhBao.classList.remove("hidden");
      txtCanhBao.textContent = `CẢNH BÁO: Mentor đang quá tải (${sl}/5 sinh viên). Vượt quá quy định tiếp nhận tối đa!`;
    } else {
      canhBao.classList.add("hidden");
    }
  }

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="py-6 text-center text-slate-400">
          <span class="inline-block w-5 h-5 border-2 border-ictu-600 border-t-transparent rounded-full animate-spin mb-1"></span>
          <p>Đang tải danh sách sinh viên...</p>
        </td>
      </tr>
    `;
  }

  modal.classList.remove("hidden");

  try {
    const res = await fetch(`${duongDanApi}/interns?ma_mentor=${maMentor}`);
    if (!res.ok) {
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" class="py-6 text-center text-rose-500 font-medium">
              Không thể tải danh sách sinh viên. Vui lòng thử lại sau.
            </td>
          </tr>
        `;
      }
      return;
    }

    const json = await res.json();
    const ds = json.data || [];

    if (ds.length === 0) {
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" class="py-8 text-center text-slate-400">
              <span class="material-symbols-outlined text-3xl text-slate-300 block mb-1">person_off</span>
              Hiện chưa có sinh viên nào được gán cho Mentor này
            </td>
          </tr>
        `;
      }
      return;
    }

    let rowsHtml = "";
    ds.forEach((sv) => {
      const hoTen = sv.ho_ten || "Sinh viên";
      const email = sv.email || "N/A";
      const sdt = sv.so_dien_thoai || "";
      const nganh = sv.chuyen_nganh || "Công nghệ thông tin";
      const lop = sv.lop || "KTPM-K19A";
      const trangThai = sv.trang_thai_thuc_tap === "DangThucTap" ? "Đang thực tập" : (sv.trang_thai_thuc_tap === "HoanThanh" ? "Hoàn thành" : sv.trang_thai_thuc_tap);

      rowsHtml += `
        <tr class="hover:bg-slate-50 transition-colors">
          <td class="py-2.5 px-3 font-bold text-slate-900">${hoTen}</td>
          <td class="py-2.5 px-3 text-slate-500">
            <p>${email}</p>
            <p class="text-[10px] text-slate-400">${sdt}</p>
          </td>
          <td class="py-2.5 px-3 text-slate-600">
            <p class="font-medium">${nganh}</p>
            <p class="text-[10px] text-slate-400">${lop}</p>
          </td>
          <td class="py-2.5 px-3 text-center">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              ${trangThai}
            </span>
          </td>
        </tr>
      `;
    });

    if (tbody) tbody.innerHTML = rowsHtml;
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="py-6 text-center text-rose-500 font-medium">
            Mất kết nối mạng khi tải danh sách sinh viên.
          </td>
        </tr>
      `;
    }
  }
}

function dongModalChiTietSvMentor() {
  const modal = document.getElementById("modalChiTietSvMentor");
  if (modal) modal.classList.add("hidden");
}

async function taiDanhSachPhongBanChoModal() {
  const select = document.getElementById("mentorPhongBan");
  if (!select) return;
  try {
    const res = await fetch(`${duongDanApi}/departments`);
    if (!res.ok) return;
    const json = await res.json();
    const list = json.data || [];
    select.innerHTML = '<option value="">-- Chọn phòng ban --</option>' + list.map(pb => `<option value="${pb.ma_phong_ban}">${pb.ten_phong_ban}</option>`).join('');
  } catch (err) {}
}

function moModalThemMentor() {
  const modal = document.getElementById("modalThemMentor");
  const form = document.getElementById("formThemMentor");
  const tb = document.getElementById("thongBaoLoiThemMentor");
  if (form) form.reset();
  if (tb) {
    tb.className = "hidden p-3 rounded-xl text-xs font-medium border";
    tb.textContent = "";
  }
  if (modal) modal.classList.remove("hidden");
  taiDanhSachPhongBanChoModal();
}

function dongModalThemMentor() {
  const modal = document.getElementById("modalThemMentor");
  if (modal) modal.classList.add("hidden");
}

function hienThiLoiThemMentor(msg) {
  const tb = document.getElementById("thongBaoLoiThemMentor");
  if (!tb) return;
  tb.className = "block p-3 rounded-xl text-xs font-medium border bg-rose-50 border-rose-200 text-rose-800";
  tb.textContent = msg;
}

async function xuLyThemMentor(event) {
  event.preventDefault();
  const tb = document.getElementById("thongBaoLoiThemMentor");
  const btn = document.getElementById("btnSubmitThemMentor");
  const txtBtn = document.getElementById("txtBtnThemMentor");

  const hoTen = (document.getElementById("mentorHoTen")?.value || "").trim();
  const email = (document.getElementById("mentorEmail")?.value || "").trim().toLowerCase();
  const soDienThoai = (document.getElementById("mentorSoDienThoai")?.value || "").trim();
  const maPhongBanVal = document.getElementById("mentorPhongBan")?.value;
  const matKhau = (document.getElementById("mentorMatKhau")?.value || "").trim();

  if (!hoTen) {
    hienThiLoiThemMentor("Vui lòng nhập họ và tên người hướng dẫn");
    return;
  }
  if (!/^[a-zA-Z\s\u00C0-\u1EF9]+$/.test(hoTen)) {
    hienThiLoiThemMentor("Họ tên không hợp lệ (chỉ được chứa chữ cái và khoảng trắng)");
    return;
  }
  if (!email || !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
    hienThiLoiThemMentor("Email không đúng định dạng chuẩn");
    return;
  }
  if (soDienThoai && !/^(0[3|5|7|8|9])[0-9]{8}$/.test(soDienThoai)) {
    hienThiLoiThemMentor("Số điện thoại không đúng định dạng Việt Nam (10 số, bắt đầu bằng 03, 05, 07, 08, 09)");
    return;
  }
  if (!matKhau || matKhau.length < 6) {
    hienThiLoiThemMentor("Mật khẩu khởi tạo phải có ít nhất 6 ký tự");
    return;
  }

  const payload = {
    ho_ten: hoTen,
    email: email,
    mat_khau: matKhau,
    so_dien_thoai: soDienThoai || null,
    ma_phong_ban: maPhongBanVal ? parseInt(maPhongBanVal, 10) : null
  };

  if (btn) btn.disabled = true;
  if (txtBtn) txtBtn.textContent = "Đang tạo...";

  try {
    const res = await fetch(`${duongDanApi}/mentors`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const json = await res.json().catch(() => ({}));

    if (!res.ok) {
      let msg = "Không thể tạo tài khoản mentor. Vui lòng thử lại.";
      if (typeof json.detail === "string") {
        msg = json.detail;
      } else if (Array.isArray(json.detail) && json.detail.length > 0) {
        msg = json.detail.map(d => d.msg || d.message).join("; ");
      } else if (json.message) {
        msg = json.message;
      }
      hienThiLoiThemMentor(msg);
      if (btn) btn.disabled = false;
      if (txtBtn) txtBtn.textContent = "Tạo Tài Khoản Mentor";
      return;
    }

    if (tb) {
      tb.className = "block p-3 rounded-xl text-xs font-medium border bg-emerald-50 border-emerald-200 text-emerald-800";
      tb.textContent = "Tạo tài khoản người hướng dẫn thành công!";
    }

    taiDuLieuMentorWorkload();

    setTimeout(() => {
      dongModalThemMentor();
      if (btn) btn.disabled = false;
      if (txtBtn) txtBtn.textContent = "Tạo Tài Khoản Mentor";
    }, 900);

  } catch (err) {
    hienThiLoiThemMentor("Mất kết nối đến máy chủ. Vui lòng kiểm tra lại đường truyền.");
    if (btn) btn.disabled = false;
    if (txtBtn) txtBtn.textContent = "Tạo Tài Khoản Mentor";
  }
}

function capNhatSelectSinhVienGiaoViec(maChon) {
  const select = document.getElementById("giaoViecSelectSinhVien");
  if (!select) return;
  const ds = (danhSachSinhVienMentorCuaToi && danhSachSinhVienMentorCuaToi.length > 0)
    ? danhSachSinhVienMentorCuaToi
    : (danhSachInternsFallback || []);
  let html = '<option value="">-- Chọn sinh viên --</option>';
  ds.forEach(sv => {
    const isSelected = maChon && String(sv.ma_ho_so) === String(maChon);
    html += `<option value="${sv.ma_ho_so}" ${isSelected ? 'selected' : ''}>${sv.ho_ten} (${sv.lop || 'ICTU'} - #${sv.ma_ho_so})</option>`;
  });
  select.innerHTML = html;
}

async function thayDoiSinhVienGiaoViec(maHoSoVal) {
  const inputMaHs = document.getElementById("giaoViecMaHoSo");
  const moTaSv = document.getElementById("moTaGiaoViecSv");
  if (inputMaHs) inputMaHs.value = maHoSoVal || "";
  if (!maHoSoVal) {
    if (moTaSv) moTaSv.textContent = "Dành cho thực tập sinh bạn phụ trách";
    const khung = document.getElementById("khungNhiemVuHienCoCuaSv");
    if (khung) khung.classList.add("hidden");
    return;
  }
  const ds = (danhSachSinhVienMentorCuaToi && danhSachSinhVienMentorCuaToi.length > 0)
    ? danhSachSinhVienMentorCuaToi
    : (danhSachInternsFallback || []);
  const found = ds.find(s => String(s.ma_ho_so) === String(maHoSoVal));
  if (found && moTaSv) {
    moTaSv.textContent = `Sinh viên: ${found.ho_ten} (Mã HS #${found.ma_ho_so})`;
  }
  await taiNhiemVuHienCoChoModal(maHoSoVal);
}

async function taiNhiemVuHienCoChoModal(maHoSo) {
  const khung = document.getElementById("khungNhiemVuHienCoCuaSv");
  const soLuongEl = document.getElementById("soLuongNhiemVuHienCo");
  const danhSachEl = document.getElementById("danhSachNhiemVuHienCo");
  if (!khung || !soLuongEl || !danhSachEl || !maHoSo) return;
  khung.classList.remove("hidden");
  danhSachEl.innerHTML = '<p class="text-slate-400 italic text-[11px]">Đang tải nhiệm vụ...</p>';
  try {
    const res = await fetch(`${duongDanApi}/interns/my-schedule?ho_so_id=${maHoSo}`);
    if (!res.ok) {
      danhSachEl.innerHTML = '<p class="text-slate-400 italic text-[11px]">Chưa có dữ liệu nhiệm vụ.</p>';
      soLuongEl.textContent = "0 nhiệm vụ";
      return;
    }
    const json = await res.json();
    const tasks = (json.data && json.data.danh_sach_nhiem_vu) || [];
    soLuongEl.textContent = `${tasks.length} nhiệm vụ`;
    if (tasks.length === 0) {
      danhSachEl.innerHTML = '<p class="text-slate-400 italic text-[11px]">Sinh viên chưa có nhiệm vụ nào được giao.</p>';
      return;
    }
    let html = "";
    tasks.forEach(t => {
      const pct = t.tien_do_phantram ?? 0;
      let badgeCls = "bg-slate-100 text-slate-700";
      if (pct === 100) badgeCls = "bg-emerald-100 text-emerald-800";
      else if (pct > 0) badgeCls = "bg-blue-100 text-blue-800";
      html += `
        <div class="p-2 rounded-lg bg-white border border-slate-200/80 flex items-center justify-between gap-2">
          <div class="min-w-0">
            <p class="font-bold text-slate-800 truncate leading-tight">${t.ten_nhiem_vu || t.tieu_de || "Nhiệm vụ"}</p>
            <p class="text-[10px] text-slate-400 mt-0.5">Hạn: ${t.han_hoan_thanh || "Không thời hạn"}</p>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold shrink-0 ${badgeCls}">${pct}%</span>
        </div>
      `;
    });
    danhSachEl.innerHTML = html;
  } catch {
    danhSachEl.innerHTML = '<p class="text-slate-400 italic text-[11px]">Không thể tải danh sách nhiệm vụ.</p>';
  }
}

function moModalGiaoViecNhanhMentor() {
  const firstSv = (danhSachSinhVienMentorCuaToi && danhSachSinhVienMentorCuaToi.length > 0)
    ? danhSachSinhVienMentorCuaToi[0]
    : null;
  if (firstSv) {
    moModalGiaoViec(firstSv.ma_ho_so, encodeURIComponent(firstSv.ho_ten || ""));
  } else {
    moModalGiaoViec(null, "");
  }
}

function moModalGiaoViec(maHoSo, encodedName) {
  const modal = document.getElementById("modalGiaoViecMentor");
  const inputMaHs = document.getElementById("giaoViecMaHoSo");
  const moTaSv = document.getElementById("moTaGiaoViecSv");
  const inputHan = document.getElementById("giaoViecHanHoanThanh");
  const inputTieuDe = document.getElementById("giaoViecTieuDe");
  const inputMoTa = document.getElementById("giaoViecMoTa");

  capNhatSelectSinhVienGiaoViec(maHoSo);

  const hoTen = decodeURIComponent(encodedName || "");
  if (inputMaHs) inputMaHs.value = maHoSo || "";
  if (moTaSv) {
    moTaSv.textContent = maHoSo ? `Sinh viên: ${hoTen} (Mã HS #${maHoSo})` : "Dành cho thực tập sinh bạn phụ trách";
  }

  const d = new Date();
  d.setDate(d.getDate() + 7);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  if (inputHan) {
    inputHan.value = `${y}-${m}-${day}`;
    const todayStr = new Date().toISOString().split("T")[0];
    inputHan.min = todayStr;
  }
  if (inputTieuDe) inputTieuDe.value = "";
  if (inputMoTa) inputMoTa.value = "";

  if (maHoSo) {
    taiNhiemVuHienCoChoModal(maHoSo);
  } else {
    const khung = document.getElementById("khungNhiemVuHienCoCuaSv");
    if (khung) khung.classList.add("hidden");
  }

  if (modal) modal.classList.remove("hidden");
  if (inputTieuDe) inputTieuDe.focus();
}

function dongModalGiaoViec() {
  const modal = document.getElementById("modalGiaoViecMentor");
  if (modal) modal.classList.add("hidden");
}

async function moModalXemNhiemVuSv(maHoSo, encodedName) {
  maHoSoDangXemNhiemVu = maHoSo;
  const hoTen = decodeURIComponent(encodedName || "Sinh viên");
  hoTenDangXemNhiemVu = hoTen;

  const modal = document.getElementById("modalXemNhiemVuMentor");
  const tieuDe = document.getElementById("tieuDeModalXemNhiemVu");
  const moTa = document.getElementById("moTaModalXemNhiemVu");
  const vungNoiDung = document.getElementById("vungNoiDungNhiemVuSv");

  if (tieuDe) tieuDe.textContent = `Nhiệm Vụ Của: ${hoTen}`;
  if (moTa) moTa.textContent = `Mã hồ sơ #${maHoSo} - Theo dõi tiến độ Sprint`;
  if (vungNoiDung) {
    vungNoiDung.innerHTML = `
      <div class="py-8 text-center text-slate-400">
        <span class="inline-block w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mb-2"></span>
        <p class="text-xs">Đang tải danh sách nhiệm vụ...</p>
      </div>
    `;
  }
  if (modal) modal.classList.remove("hidden");

  try {
    const res = await fetch(`${duongDanApi}/interns/my-schedule?ho_so_id=${maHoSo}`);
    if (!res.ok) {
      if (vungNoiDung) {
        vungNoiDung.innerHTML = `<p class="text-center text-xs text-rose-500 py-6">Không thể tải dữ liệu nhiệm vụ từ máy chủ.</p>`;
      }
      return;
    }
    const json = await res.json();
    const tasks = (json.data && json.data.danh_sach_nhiem_vu) || [];

    if (tasks.length === 0) {
      if (vungNoiDung) {
        vungNoiDung.innerHTML = `
          <div class="py-10 text-center space-y-3">
            <span class="material-symbols-outlined text-4xl text-slate-300">task_alt</span>
            <p class="text-sm font-bold text-slate-700">Sinh viên chưa có nhiệm vụ nào được phân công</p>
            <p class="text-xs text-slate-400 max-w-sm mx-auto">Hãy bắt đầu giao các đầu việc trong đợt thực tập để sinh viên cập nhật tiến độ.</p>
            <button type="button" onclick="chuyenSangGiaoViecTuModalXem()" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition-all cursor-pointer inline-flex items-center gap-1.5 mt-2">
              <span class="material-symbols-outlined text-[16px]">add_task</span>
              <span>Giao nhiệm vụ ngay</span>
            </button>
          </div>
        `;
      }
      return;
    }

    let rowsHtml = "";
    tasks.forEach((t, i) => {
      const pct = t.tien_do_phantram ?? 0;
      let badgeCls = "bg-slate-100 text-slate-600 border border-slate-200";
      let barCls = "bg-slate-300";
      let statusText = t.trang_thai || "Chưa bắt đầu";
      if (pct === 100) {
        badgeCls = "bg-emerald-50 text-emerald-700 border border-emerald-200";
        barCls = "bg-emerald-500";
        statusText = "Hoàn thành";
      } else if (pct > 0) {
        badgeCls = "bg-blue-50 text-blue-700 border border-blue-200";
        barCls = "bg-blue-500";
        statusText = "Đang thực hiện";
      }

      rowsHtml += `
        <div class="p-4 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-2.5">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-lg bg-slate-100 text-slate-600 font-bold text-[11px] flex items-center justify-center shrink-0">#${i + 1}</span>
                <h4 class="font-bold text-sm text-slate-900 leading-tight">${t.ten_nhiem_vu || t.tieu_de || "Nhiệm vụ"}</h4>
              </div>
              ${t.moTa || t.mo_ta ? `<p class="text-xs text-slate-500 mt-1 pl-8 leading-relaxed">${t.moTa || t.mo_ta}</p>` : ''}
            </div>
            <span class="px-2.5 py-1 rounded-full text-[11px] font-bold shrink-0 ${badgeCls}">${statusText}</span>
          </div>
          <div class="pl-8 space-y-1.5 pt-1">
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400 text-[11px]">Hạn chót: <strong>${t.han_hoan_thanh || "Chưa đặt"}</strong></span>
              <span class="font-bold text-slate-700">${pct}%</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div class="${barCls} h-2 rounded-full transition-all duration-500" style="width: ${pct}%"></div>
            </div>
          </div>
        </div>
      `;
    });

    if (vungNoiDung) {
      vungNoiDung.innerHTML = `
        <div class="flex items-center justify-between pb-2 border-b border-slate-100 text-xs text-slate-500">
          <span>Tổng số <strong>${tasks.length}</strong> nhiệm vụ</span>
          <span>Cập nhật theo thời gian thực</span>
        </div>
        ${rowsHtml}
      `;
    }
  } catch (err) {
    if (vungNoiDung) {
      vungNoiDung.innerHTML = `<p class="text-center text-xs text-rose-500 py-6">Lỗi kết nối: ${err.message || err}</p>`;
    }
  }
}

function dongModalXemNhiemVuSv() {
  const modal = document.getElementById("modalXemNhiemVuMentor");
  if (modal) modal.classList.add("hidden");
}

function chuyenSangGiaoViecTuModalXem() {
  const ma = maHoSoDangXemNhiemVu;
  const name = hoTenDangXemNhiemVu;
  dongModalXemNhiemVuSv();
  moModalGiaoViec(ma, encodeURIComponent(name));
}

async function guiNhiemVuMoi() {
  const inputMaHs = document.getElementById("giaoViecMaHoSo");
  const selectSv = document.getElementById("giaoViecSelectSinhVien");
  const inputTieuDe = document.getElementById("giaoViecTieuDe");
  const inputHan = document.getElementById("giaoViecHanHoanThanh");
  const inputMoTa = document.getElementById("giaoViecMoTa");
  const btn = document.getElementById("btnLuuGiaoViec");
  const icon = document.getElementById("iconLuuGiaoViec");
  const text = document.getElementById("textLuuGiaoViec");

  let maHoSo = inputMaHs ? parseInt(inputMaHs.value) : null;
  if (!maHoSo && selectSv && selectSv.value) {
    maHoSo = parseInt(selectSv.value);
  }
  const tieuDe = inputTieuDe ? inputTieuDe.value.trim() : "";
  const hanHoanThanh = inputHan ? inputHan.value : "";
  const moTa = inputMoTa ? inputMoTa.value.trim() : "";

  if (!maHoSo) {
    alert("Vui lòng chọn sinh viên tiếp nhận nhiệm vụ");
    if (selectSv) selectSv.focus();
    return;
  }

  if (!tieuDe) {
    alert("Vui lòng nhập tiêu đề nhiệm vụ");
    if (inputTieuDe) inputTieuDe.focus();
    return;
  }

  if (!hanHoanThanh) {
    alert("Vui lòng chọn hạn hoàn thành");
    if (inputHan) inputHan.focus();
    return;
  }

  const todayStr = new Date().toISOString().split("T")[0];
  if (hanHoanThanh < todayStr) {
    alert("Hạn hoàn thành nhiệm vụ không được nằm trong quá khứ");
    if (inputHan) inputHan.focus();
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang giao...";
  }

  try {
    const res = await fetch(`${duongDanApi}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ma_ho_so: maHoSo,
        tieu_de: tieuDe,
        mo_ta: moTa || null,
        han_hoan_thanh: hanHoanThanh,
        tien_do_phantram: 0,
        trang_thai: "Chưa bắt đầu"
      })
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      alert(`Đã giao nhiệm vụ '${tieuDe}' cho sinh viên thành công!`);
      dongModalGiaoViec();
      if (maHoSoDangXemNhiemVu && maHoSoDangXemNhiemVu === maHoSo) {
        moModalXemNhiemVuSv(maHoSo, encodeURIComponent(hoTenDangXemNhiemVu));
      }
    } else {
      let msg = "Không thể tạo nhiệm vụ";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        msg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }
      alert(`Lỗi: ${msg}`);
    }
  } catch (err) {
    alert(`Lỗi kết nối máy chủ: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "send";
      if (text) text.textContent = "Giao nhiệm vụ";
    }
  }
}

let danhSachSinhVienPhuCapCache = [];

async function taiDanhSachSinhVienNhapPhuCap() {
  const selectSv = document.getElementById("nhapPhuCapSinhVien");
  if (!selectSv) return;
  if (danhSachSinhVienPhuCapCache && danhSachSinhVienPhuCapCache.length > 0) {
    doDuLieuVaoSelectSinhVienPhuCap(danhSachSinhVienPhuCapCache);
    return;
  }
  try {
    const res = await fetch(`${duongDanApi}/interns?limit=200`);
    if (!res.ok) throw new Error("Không thể tải danh sách sinh viên");
    const json = await res.json();
    const danhSach = Array.isArray(json) ? json : (json.data || []);
    danhSachSinhVienPhuCapCache = danhSach;
    doDuLieuVaoSelectSinhVienPhuCap(danhSach);
  } catch (err) {
    selectSv.innerHTML = `<option value="">Lỗi: ${err.message || "Không tải được danh sách"}</option>`;
  }
}

function doDuLieuVaoSelectSinhVienPhuCap(danhSach) {
  const selectSv = document.getElementById("nhapPhuCapSinhVien");
  if (!selectSv) return;
  if (!danhSach || danhSach.length === 0) {
    selectSv.innerHTML = `<option value="">-- Chưa có sinh viên trong hệ thống --</option>`;
    return;
  }
  let html = `<option value="">-- Chọn thực tập sinh --</option>`;
  danhSach.forEach(sv => {
    const maHs = sv.ma_ho_so || sv.id;
    const hoTen = sv.ho_ten || "Sinh viên";
    const mssv = sv.ma_sinh_vien ? ` (${sv.ma_sinh_vien})` : "";
    const nganh = sv.chuyen_nganh ? ` - ${sv.chuyen_nganh}` : "";
    html += `<option value="${maHs}">${hoTen}${mssv}${nganh}</option>`;
  });
  selectSv.innerHTML = html;
}

function capNhatPreviewTienPhuCap(val) {
  const preview = document.getElementById("hienThiTienVndPreview");
  if (!preview) return;
  const num = parseFloat(val);
  if (!val || isNaN(num) || num < 0) {
    preview.textContent = "0 VNĐ";
    return;
  }
  preview.textContent = new Intl.NumberFormat("vi-VN").format(num) + " VNĐ";
}

function moModalNhapPhuCap() {
  const modal = document.getElementById("modalNhapPhuCap");
  if (!modal) return;
  const errorBox = document.getElementById("thongBaoLoiNhapPhuCap");
  if (errorBox) errorBox.classList.add("hidden");

  const d = new Date();
  const thangSelect = document.getElementById("nhapPhuCapThang");
  const namInput = document.getElementById("nhapPhuCapNam");
  const ngayChiTraInput = document.getElementById("nhapPhuCapNgayChiTra");
  const soTienInput = document.getElementById("nhapPhuCapSoTien");

  if (thangSelect) thangSelect.value = String(d.getMonth() + 1);
  if (namInput) namInput.value = String(d.getFullYear());
  if (ngayChiTraInput) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    ngayChiTraInput.value = `${y}-${m}-25`;
  }
  if (soTienInput) {
    soTienInput.value = "3000000";
    capNhatPreviewTienPhuCap("3000000");
  }

  modal.classList.remove("hidden");
  taiDanhSachSinhVienNhapPhuCap();
}

function dongModalNhapPhuCap() {
  const modal = document.getElementById("modalNhapPhuCap");
  if (modal) modal.classList.add("hidden");
  const errorBox = document.getElementById("thongBaoLoiNhapPhuCap");
  if (errorBox) errorBox.classList.add("hidden");
}

async function guiNhapPhuCap() {
  const selectSv = document.getElementById("nhapPhuCapSinhVien");
  const selectThang = document.getElementById("nhapPhuCapThang");
  const inputNam = document.getElementById("nhapPhuCapNam");
  const inputSoTien = document.getElementById("nhapPhuCapSoTien");
  const inputNgayChiTra = document.getElementById("nhapPhuCapNgayChiTra");
  const selectTrangThai = document.getElementById("nhapPhuCapTrangThai");
  const errorBox = document.getElementById("thongBaoLoiNhapPhuCap");
  const errorText = document.getElementById("noiDungLoiNhapPhuCap");
  const btn = document.getElementById("btnSubmitNhapPhuCap");
  const icon = document.getElementById("iconSubmitNhapPhuCap");
  const text = document.getElementById("textSubmitNhapPhuCap");

  const baoLoi = (msg) => {
    if (errorBox && errorText) {
      errorText.textContent = msg;
      errorBox.classList.remove("hidden");
    } else {
      alert(msg);
    }
  };

  if (errorBox) errorBox.classList.add("hidden");

  const maHoSo = selectSv ? parseInt(selectSv.value) : null;
  const thang = selectThang ? parseInt(selectThang.value) : null;
  const nam = inputNam ? parseInt(inputNam.value) : null;
  const soTien = inputSoTien ? parseFloat(inputSoTien.value) : null;
  const ngayChiTra = inputNgayChiTra ? inputNgayChiTra.value.trim() : null;
  const trangThai = selectTrangThai ? selectTrangThai.value : "ChuaChiTra";

  if (!maHoSo || isNaN(maHoSo)) {
    baoLoi("Vui lòng chọn thực tập sinh nhận phụ cấp");
    if (selectSv) selectSv.focus();
    return;
  }
  if (!thang || isNaN(thang) || thang < 1 || thang > 12) {
    baoLoi("Tháng chi trả phải từ 1 đến 12");
    if (selectThang) selectThang.focus();
    return;
  }
  if (!nam || isNaN(nam) || nam < 2020) {
    baoLoi("Năm chi trả không hợp lệ");
    if (inputNam) inputNam.focus();
    return;
  }
  if (!soTien || isNaN(soTien) || soTien <= 0) {
    baoLoi("Số tiền phụ cấp phải lớn hơn 0 VNĐ");
    if (inputSoTien) inputSoTien.focus();
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang lưu...";
  }

  try {
    const payload = {
      ma_ho_so: maHoSo,
      thang: thang,
      nam: nam,
      so_tien: soTien,
      ngay_chi_tra: ngayChiTra || null,
      trang_thai: trangThai
    };

    const res = await fetch(`${duongDanApi}/allowances`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      alert(`Đã lưu thành công khoản phụ cấp Tháng ${thang}/${nam} cho thực tập sinh!`);
      dongModalNhapPhuCap();
      if (typeof taiDuLieuDashboard === "function") {
        taiDuLieuDashboard();
      }
    } else {
      let msg = "Không thể lưu khoản phụ cấp";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        msg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }
      baoLoi(msg);
    }
  } catch (err) {
    baoLoi(`Lỗi kết nối máy chủ: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "save";
      if (text) text.textContent = "Lưu phụ cấp";
    }
  }
}

async function taiDuLieuCompletionRate() {
  const elBadgeText = document.getElementById("kpiCompletionTrendText");
  const elBadge = document.getElementById("kpiCompletionTrendBadge");
  const elCircle = document.getElementById("vongTronTienDoHoanThanh");
  const elPercent = document.getElementById("soPhanTramHoanThanh");
  const elTong = document.getElementById("kpiTongSoSinhVien");
  const elDang = document.getElementById("kpiDangThucTap");
  const elHoanThanh = document.getElementById("kpiHoanThanh");
  const elThoiHoc = document.getElementById("kpiThoiHoc");
  const elTyLeDang = document.getElementById("tyLeDangThucTap");
  const elTyLeHt = document.getElementById("tyLeHoanThanhChiTiet");
  const elTyLeThoi = document.getElementById("tyLeThoiHoc");
  const elNhanXet = document.getElementById("nhanXetTienDoKpi");

  if (elBadgeText) elBadgeText.textContent = "Đang tải...";

  try {
    const res = await fetch(`${duongDanApi}/reports/completion-rate`);
    if (!res.ok) throw new Error("Không thể tải báo cáo tỷ lệ hoàn thành");
    const data = await res.json();

    const tongSo = data.tong_so_sinh_vien || 0;
    const dangTt = data.so_luong_dang_thuc_tap || 0;
    const hoanThanh = data.so_luong_hoan_thanh || 0;
    const thoiHoc = data.so_luong_thoi_hoc || 0;
    const tyLe = typeof data.ty_le_hoan_thanh === "number" ? data.ty_le_hoan_thanh : 0;

    if (elTong) elTong.textContent = tongSo;
    if (elDang) elDang.textContent = dangTt;
    if (elHoanThanh) elHoanThanh.textContent = hoanThanh;
    if (elThoiHoc) elThoiHoc.textContent = thoiHoc;
    if (elPercent) elPercent.textContent = `${tyLe}%`;

    if (elTyLeDang) {
      elTyLeDang.textContent = tongSo > 0 ? `${Math.round((dangTt / tongSo) * 100)}% tổng số` : "0% tổng số";
    }
    if (elTyLeHt) {
      elTyLeHt.textContent = `${tyLe}% hoàn tất`;
    }
    if (elTyLeThoi) {
      elTyLeThoi.textContent = tongSo > 0 ? `${Math.round((thoiHoc / tongSo) * 100)}% tỷ lệ dừng` : "0% tỷ lệ dừng";
    }

    if (elCircle) {
      const chuVi = 314.16;
      const phanTramAnToan = Math.min(100, Math.max(0, tyLe));
      const offset = chuVi - (phanTramAnToan / 100) * chuVi;
      elCircle.style.strokeDashoffset = offset;
    }

    if (elNhanXet) {
      if (tyLe >= 80) {
        elNhanXet.textContent = "Tiến độ xuất sắc! Tỷ lệ hoàn thành đạt mức tối ưu.";
      } else if (tyLe >= 50) {
        elNhanXet.textContent = "Đang tiến triển ổn định theo đúng lộ trình kế hoạch.";
      } else if (dangTt > 0) {
        elNhanXet.textContent = `Đang có ${dangTt} sinh viên đang trong giai đoạn thực tập tích cực.`;
      } else {
        elNhanXet.textContent = "Chưa có sinh viên hoàn thành trong đợt này.";
      }
    }

    if (elBadgeText) elBadgeText.textContent = "Thời gian thực";
    if (elBadge) {
      elBadge.className = "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700";
    }
  } catch (err) {
    if (elBadgeText) elBadgeText.textContent = "Lỗi kết nối";
    if (elBadge) {
      elBadge.className = "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700";
    }
    if (elNhanXet) elNhanXet.textContent = `Không thể nạp dữ liệu: ${err.message || err}`;
  }
}

async function xuatBaoCao(format) {
  const isPdf = format === "pdf";
  const btn = document.getElementById(isPdf ? "btnXuatPdf" : "btnXuatExcel");
  const icon = document.getElementById(isPdf ? "iconXuatPdf" : "iconXuatExcel");
  const text = document.getElementById(isPdf ? "textXuatPdf" : "textXuatExcel");

  const originalText = isPdf ? "Xuất PDF" : "Xuất Excel";
  const originalIcon = isPdf ? "picture_as_pdf" : "table_view";

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[16px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang xuất...";
  }

  try {
    const res = await fetch(`${duongDanApi}/reports/export?format=${format}`);
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || "Không thể xuất file báo cáo");
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const ext = isPdf ? "pdf" : "xlsx";
    const timeStr = new Date().toISOString().slice(0, 10);
    a.download = `Bao_cao_tong_hop_${timeStr}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Lỗi xuất báo cáo: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[16px]";
      if (icon) icon.textContent = originalIcon;
      if (text) text.textContent = originalText;
    }
  }
}

let cacheDanhSachYeuCauHoTro = [];
let boLocTrangThaiYeuCauHienTai = "";

function moModalDuyetYeuCauHoTro() {
  const modal = document.getElementById("modalDuyetYeuCauHoTro");
  if (!modal) return;
  modal.classList.remove("hidden");
  taiDanhSachYeuCauHoTroHR();
}

function dongModalDuyetYeuCauHoTro() {
  const modal = document.getElementById("modalDuyetYeuCauHoTro");
  if (modal) modal.classList.add("hidden");
  const errorBox = document.getElementById("thongBaoLoiYeuCauHoTro");
  if (errorBox) errorBox.classList.add("hidden");
}

async function taiDanhSachYeuCauHoTroHR() {
  const tbody = document.getElementById("danhSachYeuCauHoTroTableBody");
  const errorBox = document.getElementById("thongBaoLoiYeuCauHoTro");
  const errorText = document.getElementById("noiDungLoiYeuCauHoTro");
  if (errorBox) errorBox.classList.add("hidden");

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-8 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-3xl animate-spin text-slate-400">progress_activity</span>
            <p>Đang tải dữ liệu yêu cầu hỗ trợ...</p>
          </div>
        </td>
      </tr>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/support-requests`);
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || "Không thể tải danh sách yêu cầu hỗ trợ");
    }
    const json = await res.json();
    cacheDanhSachYeuCauHoTro = json.data || [];
    capNhatSoLuongYeuCauChoXuLy();
    apDungBoLocYeuCau();
  } catch (err) {
    if (errorBox && errorText) {
      errorText.textContent = `Lỗi: ${err.message || err}`;
      errorBox.classList.remove("hidden");
    }
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="py-8 text-center text-rose-500 font-medium">
            <div class="flex flex-col items-center justify-center gap-2">
              <span class="material-symbols-outlined text-3xl">error</span>
              <p>${err.message || "Lỗi nạp dữ liệu từ máy chủ"}</p>
            </div>
          </td>
        </tr>
      `;
    }
  }
}

function capNhatSoLuongYeuCauChoXuLy() {
  const choXuLyCount = cacheDanhSachYeuCauHoTro.filter(x => x.trang_thai === "ChoXuLy").length;
  const badgeModal = document.getElementById("badgeTongYeuCauCho");
  if (badgeModal) {
    badgeModal.textContent = `${choXuLyCount} chờ xử lý`;
    if (choXuLyCount > 0) {
      badgeModal.className = "px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 animate-pulse";
    } else {
      badgeModal.className = "px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600";
    }
  }
  const elLoiTatChoXuLy = document.getElementById("txtLoiTatChoXuLyYeuCau");
  if (elLoiTatChoXuLy) {
    if (choXuLyCount > 0) {
      elLoiTatChoXuLy.textContent = `${choXuLyCount} yêu cầu chờ duyệt`;
      elLoiTatChoXuLy.className = "text-[10px] text-amber-600 font-bold";
    } else {
      elLoiTatChoXuLy.textContent = "Giấy tờ, con dấu, cơ sở vật chất";
      elLoiTatChoXuLy.className = "text-[10px] text-slate-400";
    }
  }
}

function locYeuCauHoTroHR(trangThai) {
  boLocTrangThaiYeuCauHienTai = trangThai || "";
  const tabButtons = document.querySelectorAll("#tabGroupYeuCauHoTro button");
  tabButtons.forEach(btn => {
    const filter = btn.getAttribute("data-filter") || "";
    if (filter === boLocTrangThaiYeuCauHienTai) {
      btn.className = "tab-btn-filter px-3 py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-slate-900 shadow-xs cursor-pointer";
    } else {
      btn.className = "tab-btn-filter px-3 py-1.5 rounded-lg text-xs font-bold transition-all text-slate-600 hover:text-slate-900 cursor-pointer";
    }
  });
  apDungBoLocYeuCau();
}

function apDungBoLocYeuCau() {
  let danhSachLoc = cacheDanhSachYeuCauHoTro;
  if (boLocTrangThaiYeuCauHienTai) {
    danhSachLoc = cacheDanhSachYeuCauHoTro.filter(x => x.trang_thai === boLocTrangThaiYeuCauHienTai);
  }
  renderDanhSachYeuCauHoTroHR(danhSachLoc);
}

function renderDanhSachYeuCauHoTroHR(items) {
  const tbody = document.getElementById("danhSachYeuCauHoTroTableBody");
  const countEl = document.getElementById("txtThongKeYeuCauBang");
  if (countEl) countEl.textContent = `Hiển thị ${items.length} yêu cầu`;
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-10 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-1.5">
            <span class="material-symbols-outlined text-3xl text-slate-300">inbox</span>
            <p class="text-xs font-semibold text-slate-500">Không có yêu cầu hỗ trợ nào phù hợp bộ lọc</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  const mapLoai = {
    "XinChungNhan": "Xin cấp chứng nhận",
    "GiayXacNhan": "Xin giấy xác nhận thực tập",
    "ThietBi": "Hỗ trợ thiết bị làm việc",
    "Khac": "Yêu cầu khác"
  };

  tbody.innerHTML = items.map(yc => {
    let badgeTrangThai = "";
    if (yc.trang_thai === "ChoXuLy") {
      badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
        <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Chờ xử lý
      </span>`;
    } else if (yc.trang_thai === "DaXuLy") {
      badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Đã duyệt
      </span>`;
    } else {
      badgeTrangThai = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
        <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Từ chối
      </span>`;
    }

    const tenLoai = mapLoai[yc.loai_yeu_cau] || yc.loai_yeu_cau || "Yêu cầu hỗ trợ";
    const hoTen = yc.ho_ten_sinh_vien || `Hồ sơ #${yc.ma_ho_so}`;
    const email = yc.email_sinh_vien || "Chưa có email";
    const phanHoiText = yc.phan_hoi_hr ? yc.phan_hoi_hr : `<span class="text-slate-400 italic">Chưa có phản hồi</span>`;

    let hanhDongButtons = "";
    if (yc.trang_thai === "ChoXuLy") {
      hanhDongButtons = `
        <div class="flex items-center justify-end gap-1.5">
          <button
            type="button"
            onclick="moModalPhanHoiYeuCau(${yc.ma_yeu_cau}, 'DaXuLy')"
            class="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-[11px] transition-all flex items-center gap-1 cursor-pointer active:scale-95"
            title="Duyệt yêu cầu"
          >
            <span class="material-symbols-outlined text-[14px]">check</span>
            <span>Duyệt</span>
          </button>
          <button
            type="button"
            onclick="moModalPhanHoiYeuCau(${yc.ma_yeu_cau}, 'TuChoi')"
            class="px-2.5 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-[11px] border border-rose-200 transition-all flex items-center gap-1 cursor-pointer active:scale-95"
            title="Từ chối yêu cầu"
          >
            <span class="material-symbols-outlined text-[14px]">close</span>
            <span>Từ chối</span>
          </button>
        </div>
      `;
    } else {
      hanhDongButtons = `
        <div class="flex items-center justify-end">
          <button
            type="button"
            onclick="moModalPhanHoiYeuCau(${yc.ma_yeu_cau}, '${yc.trang_thai}')"
            class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[11px] transition-all flex items-center gap-1 cursor-pointer"
            title="Chỉnh sửa phản hồi"
          >
            <span class="material-symbols-outlined text-[14px]">edit_note</span>
            <span>Cập nhật</span>
          </button>
        </div>
      `;
    }

    return `
      <tr class="hover:bg-slate-50/70 transition-colors">
        <td class="py-3 px-3.5 font-mono font-bold text-slate-700">#${yc.ma_yeu_cau}</td>
        <td class="py-3 px-3.5">
          <p class="font-bold text-slate-900">${hoTen}</p>
          <p class="text-[11px] text-slate-500 font-mono">${email}</p>
        </td>
        <td class="py-3 px-3.5">
          <span class="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-violet-50 text-violet-700 border border-violet-100">${tenLoai}</span>
        </td>
        <td class="py-3 px-3.5 max-w-xs">
          <p class="line-clamp-2 text-slate-700 leading-relaxed" title="${yc.noi_dung || ""}">${yc.noi_dung || ""}</p>
        </td>
        <td class="py-3 px-3.5 whitespace-nowrap">${badgeTrangThai}</td>
        <td class="py-3 px-3.5 max-w-xs">
          <p class="line-clamp-2 text-xs leading-relaxed">${phanHoiText}</p>
        </td>
        <td class="py-3 px-3.5 text-right whitespace-nowrap">${hanhDongButtons}</td>
      </tr>
    `;
  }).join("");
}

function moModalPhanHoiYeuCau(maYeuCau, trangThaiMacDinh) {
  const yc = cacheDanhSachYeuCauHoTro.find(x => x.ma_yeu_cau === maYeuCau);
  if (!yc) return;

  const modal = document.getElementById("modalPhanHoiYeuCau");
  if (!modal) return;

  const hiddenId = document.getElementById("hiddenPhanHoiMaYeuCau");
  const txtTen = document.getElementById("txtPhanHoiTenSinhVien");
  const txtLoai = document.getElementById("txtPhanHoiLoaiYeuCau");
  const txtNoiDung = document.getElementById("txtPhanHoiNoiDungGoc");
  const selectStatus = document.getElementById("selectPhanHoiTrangThai");
  const txtHR = document.getElementById("txtPhanHoiHRNoiDung");
  const errorBox = document.getElementById("thongBaoLoiPhanHoi");
  const headerIcon = document.getElementById("iconModalPhanHoi");
  const iconBox = document.getElementById("iconContainerPhanHoi");
  const title = document.getElementById("tieuDeModalPhanHoi");

  if (errorBox) errorBox.classList.add("hidden");
  if (hiddenId) hiddenId.value = String(maYeuCau);
  if (txtTen) txtTen.textContent = yc.ho_ten_sinh_vien ? `${yc.ho_ten_sinh_vien} (#${yc.ma_ho_so})` : `Hồ sơ #${yc.ma_ho_so}`;
  
  const mapLoai = {
    "XinChungNhan": "Xin cấp chứng nhận",
    "GiayXacNhan": "Xin giấy xác nhận thực tập",
    "ThietBi": "Hỗ trợ thiết bị làm việc",
    "Khac": "Yêu cầu khác"
  };
  if (txtLoai) txtLoai.textContent = mapLoai[yc.loai_yeu_cau] || yc.loai_yeu_cau || "Yêu cầu hỗ trợ";
  if (txtNoiDung) txtNoiDung.textContent = yc.noi_dung || "(Không có nội dung)";

  const newStatus = (trangThaiMacDinh === "TuChoi") ? "TuChoi" : "DaXuLy";
  if (selectStatus) selectStatus.value = newStatus;
  if (txtHR) txtHR.value = yc.phan_hoi_hr || "";

  if (newStatus === "TuChoi") {
    if (headerIcon) headerIcon.textContent = "cancel";
    if (iconBox) iconBox.className = "w-10 h-10 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center shrink-0";
    if (title) title.textContent = "Từ Chối Yêu Cầu Hỗ Trợ";
  } else {
    if (headerIcon) headerIcon.textContent = "check_circle";
    if (iconBox) iconBox.className = "w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0";
    if (title) title.textContent = "Duyệt & Phản Hồi Yêu Cầu Hỗ Trợ";
  }

  modal.classList.remove("hidden");
}

function dongModalPhanHoiYeuCau() {
  const modal = document.getElementById("modalPhanHoiYeuCau");
  if (modal) modal.classList.add("hidden");
  const errorBox = document.getElementById("thongBaoLoiPhanHoi");
  if (errorBox) errorBox.classList.add("hidden");
}

async function xacNhanXuLyYeuCau() {
  const hiddenId = document.getElementById("hiddenPhanHoiMaYeuCau");
  const selectStatus = document.getElementById("selectPhanHoiTrangThai");
  const txtHR = document.getElementById("txtPhanHoiHRNoiDung");
  const errorBox = document.getElementById("thongBaoLoiPhanHoi");
  const errorText = document.getElementById("noiDungLoiPhanHoi");
  const btn = document.getElementById("btnXacNhanXuLyYeuCau");
  const icon = document.getElementById("iconXacNhanXuLyYeuCau");
  const text = document.getElementById("textXacNhanXuLyYeuCau");

  const baoLoi = (msg) => {
    if (errorBox && errorText) {
      errorText.textContent = msg;
      errorBox.classList.remove("hidden");
    } else {
      alert(msg);
    }
  };

  if (errorBox) errorBox.classList.add("hidden");

  const maYeuCau = hiddenId ? parseInt(hiddenId.value) : null;
  const trangThai = selectStatus ? selectStatus.value : "DaXuLy";
  const phanHoi = txtHR ? txtHR.value.trim() : "";

  if (!maYeuCau || isNaN(maYeuCau)) {
    baoLoi("Không xác định được mã yêu cầu cần cập nhật");
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang xử lý...";
  }

  try {
    const payload = {
      trang_thai: trangThai,
      phan_hoi_hr: phanHoi || null
    };

    const res = await fetch(`${duongDanApi}/support-requests/${maYeuCau}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      const hanhDongText = (trangThai === "DaXuLy") ? "Duyệt thành công" : "Đã từ chối";
      alert(`${hanhDongText} yêu cầu #${maYeuCau}! Đã gửi email thông báo kết quả cho sinh viên.`);
      dongModalPhanHoiYeuCau();
      await taiDanhSachYeuCauHoTroHR();
    } else {
      let msg = "Không thể cập nhật yêu cầu hỗ trợ";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        msg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }
      baoLoi(msg);
    }
  } catch (err) {
    baoLoi(`Lỗi kết nối máy chủ: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "check";
      if (text) text.textContent = "Lưu & Gửi thông báo";
    }
  }
}

napDuLieuCacheDashboard();
window.addEventListener("DOMContentLoaded", () => {
  napDuLieuCacheDashboard();
  taiDuLieuDashboard();
  taiDuLieuMentorWorkload();
  taiDuLieuCompletionRate();
});


