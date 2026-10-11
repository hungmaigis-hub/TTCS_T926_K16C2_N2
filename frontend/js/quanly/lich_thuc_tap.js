const duongDanApi = "http://127.0.0.1:8000/api/v1";

let danhSachChuongTrinhGoc = [];

async function kiemTraKetNoiApi() {
  const badge = document.getElementById("badgeTrangThaiApi");
  if (!badge) return;
  try {
    const phanHoi = await fetch(`${duongDanApi}/programs`, {
      method: "GET",
    });
    if (phanHoi.ok) {
      badge.className =
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Máy chủ: Đã kết nối`;
      badge.classList.remove("hidden");
    } else {
      badge.className =
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Ngoại tuyến`;
      badge.classList.remove("hidden");
    }
  } catch {
    badge.className =
      "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Ngoại tuyến`;
    badge.classList.remove("hidden");
  }
}

function tinhToanThoiGian() {
  const batDau = document.getElementById("ngayBatDau") ? document.getElementById("ngayBatDau").value : "";
  const ketThuc = document.getElementById("ngayKetThuc") ? document.getElementById("ngayKetThuc").value : "";
  const labelSoNgay = document.getElementById("soNgayThucTap");
  if (!labelSoNgay) return;
  if (!batDau || !ketThuc) {
    labelSoNgay.textContent = "Chưa chọn đủ ngày";
    labelSoNgay.className = "font-bold text-slate-400";
    return;
  }

  const d1 = new Date(batDau);
  const d2 = new Date(ketThuc);
  const diffTime = d2.getTime() - d1.getTime();

  if (diffTime <= 0) {
    labelSoNgay.textContent = "Ngày không hợp lệ (kết thúc phải lớn hơn bắt đầu)";
    labelSoNgay.className = "font-bold text-error";
    return;
  }

  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  const diffWeeks = Math.round((diffDays / 7) * 10) / 10;
  labelSoNgay.textContent = `${diffDays} ngày (${diffWeeks} tuần)`;
  labelSoNgay.className = "font-bold text-primary";
}

function datLaiForm() {
  const form = document.getElementById("bieuMauChuongTrinh");
  if (form) form.reset();
  const idInput = document.getElementById("maChuongTrinh");
  if (idInput) idInput.value = "";
  const tieuDe = document.getElementById("tieuDeFormThongTin");
  if (tieuDe) tieuDe.textContent = "Thêm Mới Chương Trình Thực Tập";
  const nhanNut = document.getElementById("nhanNutLuuLich");
  if (nhanNut) nhanNut.textContent = "Tạo chương trình thực tập";
  setTimeout(tinhToanThoiGian, 50);
}

function hienThiThongBaoThanhCong(tieuDe, noiDung) {
  const hop = document.getElementById("hopThongBao");
  if (!hop) return;
  hop.className =
    "rounded-xl bg-secondary-container p-4 shadow-sm flex items-start gap-3.5 transition-all text-on-secondary-container border border-secondary/20";
  hop.innerHTML = `
    <div class="w-9 h-9 rounded-lg bg-secondary flex items-center justify-center text-on-secondary shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-xl">check_circle</span>
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between">
        <h4 class="font-label-lg text-label-lg font-bold" data-thong-bao-tieu-de></h4>
        <span class="font-code text-label-sm bg-surface-container-lowest px-2 py-0.5 rounded text-secondary font-semibold">VỪA XONG</span>
      </div>
      <p class="font-body-md text-body-md mt-1 leading-relaxed" data-thong-bao-noi-dung></p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="hover:opacity-75 p-1 rounded-md transition-opacity" title="Đóng">
      <span class="material-symbols-outlined text-lg">close</span>
    </button>
  `;
  const titleNode = hop.querySelector("[data-thong-bao-tieu-de]");
  const contentNode = hop.querySelector("[data-thong-bao-noi-dung]");
  if (titleNode) titleNode.textContent = tieuDe;
  if (contentNode) contentNode.innerHTML = noiDung;
  hop.classList.remove("hidden");
  hop.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hienThiThongBaoLoi(tieuDe, noiDung) {
  const hop = document.getElementById("hopThongBao");
  if (!hop) return;
  hop.className =
    "rounded-xl bg-red-50 p-4 shadow-sm flex items-start gap-3.5 transition-all text-red-900 border border-red-200";
  hop.innerHTML = `
    <div class="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center text-white shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-xl">error</span>
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between">
        <h4 class="font-label-lg text-label-lg font-bold text-red-800" data-thong-bao-tieu-de></h4>
        <span class="font-code text-label-sm bg-red-100 px-2 py-0.5 rounded text-red-700 font-semibold">LỖI XÁC THỰC</span>
      </div>
      <p class="font-body-md text-body-md mt-1 leading-relaxed text-red-700" data-thong-bao-noi-dung></p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="hover:opacity-75 p-1 rounded-md transition-opacity text-red-600" title="Đóng">
      <span class="material-symbols-outlined text-lg">close</span>
    </button>
  `;
  const titleNode = hop.querySelector("[data-thong-bao-tieu-de]");
  const contentNode = hop.querySelector("[data-thong-bao-noi-dung]");
  if (titleNode) titleNode.textContent = tieuDe;
  if (contentNode) contentNode.innerHTML = noiDung;
  hop.classList.remove("hidden");
  hop.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function taiDanhSachPhongBan() {
  const selectPb = document.getElementById("phongBan");
  if (!selectPb) return;
  try {
    const res = await fetch(`${duongDanApi}/departments`);
    if (!res.ok) return;
    const json = await res.json();
    const ds = json.data || [];
    if (ds.length > 0) {
      selectPb.innerHTML = ds.map((pb, idx) => `
        <option value="${pb.ma_phong_ban}" ${idx === 0 ? "selected" : ""}>
          ${pb.ten_phong_ban}
        </option>
      `).join("");
    }
  } catch (err) {
    console.warn("Không tải được phòng ban:", err);
  }
}

async function taiDanhSachChuongTrinh() {
  const tbody = document.getElementById("danhSachChuongTrinhBody");
  if (!tbody) return;

  try {
    const res = await fetch(`${duongDanApi}/programs`);
    if (!res.ok) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="py-8 text-center text-red-600 font-medium">
            Không thể tải dữ liệu từ máy chủ (Mã lỗi: ${res.status}).
          </td>
        </tr>
      `;
      return;
    }

    const json = await res.json();
    danhSachChuongTrinhGoc = json.data || [];
    hienThiDanhSach(danhSachChuongTrinhGoc);

    const elFooter = document.getElementById("theHienThiTongSoChuongTrinh");
    if (elFooter) {
      elFooter.innerHTML = `Hiển thị <strong>${danhSachChuongTrinhGoc.length}</strong> trên tổng số <strong>${json.total || danhSachChuongTrinhGoc.length}</strong> chương trình thực tập`;
    }
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="py-8 text-center text-slate-500 font-medium">
          Mất kết nối với máy chủ API (${err.message || "Lỗi mạng"}). Vui lòng kiểm tra lại backend.
        </td>
      </tr>
    `;
  }
}

function hienThiDanhSach(ds) {
  const tbody = document.getElementById("danhSachChuongTrinhBody");
  if (!tbody) return;

  if (!ds || ds.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="py-8 text-center text-slate-400">
          Chưa có chương trình thực tập nào phù hợp.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = ds.map((p, index) => {
    const bgRow = index % 2 === 1 ? "bg-surface/30" : "";
    const maDot = `ICTU-PRG-2026-${String(p.ma_chuong_trinh).padStart(2, "0")}`;
    const startFmt = p.ngay_bat_dau ? p.ngay_bat_dau.split("-").reverse().join("/") : "--/--/----";
    const endFmt = p.ngay_ket_thuc ? p.ngay_ket_thuc.split("-").reverse().join("/") : "--/--/----";
    const soTuan = p.thoi_luong_tuan ? `${p.thoi_luong_tuan} tuần` : "12 tuần";
    const soLuongSV = p.so_luong_sinh_vien || 0;
    const chiTieu = p.chi_tieu_sinh_vien || 50;
    const phanTram = Math.min(100, Math.round((soLuongSV / chiTieu) * 100));

    let badgeStatus = `
      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm">
        <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span>
        Đang diễn ra
      </span>
    `;
    if (p.trang_thai === "Sắp bắt đầu") {
      badgeStatus = `
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-container-highest text-primary font-label-sm text-label-sm">
          <span class="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span>
          Sắp bắt đầu
        </span>
      `;
    } else if (p.trang_thai === "Đã kết thúc") {
      badgeStatus = `
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-label-sm text-label-sm">
          <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
          Đã kết thúc
        </span>
      `;
    }

    return `
      <tr class="hover:bg-surface/60 transition-colors ${bgRow}">
        <td class="py-4 px-6 font-code text-label-md text-primary font-semibold">
          ${maDot}
        </td>
        <td class="py-4 px-4 font-semibold text-on-surface">
          ${p.ten_chuong_trinh}
          <span class="block font-body-sm text-body-sm text-on-surface-variant font-normal">
            ${p.mo_ta || "Chương trình thực tập tiêu chuẩn ICTU"}
          </span>
        </td>
        <td class="py-4 px-4">
          <span class="inline-flex items-center gap-1.5 text-on-surface-variant text-sm">
            <span class="material-symbols-outlined text-base text-primary">hub</span>
            ${p.ten_phong_ban || "Khoa/Phòng phụ trách"}
          </span>
        </td>
        <td class="py-4 px-4 font-code text-body-sm">
          ${startFmt} - ${endFmt}
        </td>
        <td class="py-4 px-4 text-center">
          <span class="px-2.5 py-1 rounded-md bg-surface-container font-code text-label-sm font-semibold">
            ${soTuan}
          </span>
        </td>
        <td class="py-4 px-4">
          <div class="flex items-center gap-2">
            <span class="font-code font-bold text-secondary">${soLuongSV}/${chiTieu}</span>
            <span class="text-on-surface-variant font-body-sm">SV</span>
          </div>
          <div class="w-20 bg-surface-container-highest h-1.5 rounded-full overflow-hidden mt-1">
            <div class="bg-secondary h-full" style="width: ${phanTram}%"></div>
          </div>
        </td>
        <td class="py-4 px-4">
          ${badgeStatus}
        </td>
        <td class="py-4 px-6 text-right">
          <div class="inline-flex items-center gap-1">
            <button
              class="p-1.5 rounded-md hover:bg-surface-container text-on-surface-variant hover:text-primary transition-colors"
              title="Chỉnh sửa lịch"
              type="button"
              onclick="chuanBiChinhSua(${p.ma_chuong_trinh})"
            >
              <span class="material-symbols-outlined text-lg">edit</span>
            </button>
            <button
              class="p-1.5 rounded-md hover:bg-surface-container text-on-surface-variant hover:text-primary transition-colors"
              title="Xem chi tiết"
              type="button"
              onclick="xemChiTiet(${p.ma_chuong_trinh})"
            >
              <span class="material-symbols-outlined text-lg">visibility</span>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function locChuongTrinh() {
  const oTimKiem = document.getElementById("oTimKiemChuongTrinh");
  if (!oTimKiem) return;
  const tuKhoa = oTimKiem.value.trim().toLowerCase();
  if (!tuKhoa) {
    hienThiDanhSach(danhSachChuongTrinhGoc);
    return;
  }

  const ketQua = danhSachChuongTrinhGoc.filter((p) => {
    const maDot = `ICTU-PRG-2026-${String(p.ma_chuong_trinh).padStart(2, "0")}`.toLowerCase();
    const ten = (p.ten_chuong_trinh || "").toLowerCase();
    const phongBan = (p.ten_phong_ban || "").toLowerCase();
    const moTa = (p.mo_ta || "").toLowerCase();
    return maDot.includes(tuKhoa) || ten.includes(tuKhoa) || phongBan.includes(tuKhoa) || moTa.includes(tuKhoa);
  });

  hienThiDanhSach(ketQua);
}

function chuanBiChinhSua(id) {
  const p = danhSachChuongTrinhGoc.find((item) => item.ma_chuong_trinh === id);
  if (!p) {
    hienThiThongBaoLoi("Không tìm thấy", `Không tìm thấy thông tin chương trình thực tập #${id}`);
    return;
  }

  const idInput = document.getElementById("maChuongTrinh");
  const tenInput = document.getElementById("tenChuongTrinh");
  const pbInput = document.getElementById("phongBan");
  const startInput = document.getElementById("ngayBatDau");
  const endInput = document.getElementById("ngayKetThuc");
  const moTaInput = document.getElementById("ghiChuDot");
  const tieuDe = document.getElementById("tieuDeFormThongTin");
  const nhanNut = document.getElementById("nhanNutLuuLich");

  if (idInput) idInput.value = p.ma_chuong_trinh;
  if (tenInput) tenInput.value = p.ten_chuong_trinh;
  if (pbInput && p.ma_phong_ban) pbInput.value = p.ma_phong_ban;
  if (startInput && p.ngay_bat_dau) startInput.value = p.ngay_bat_dau;
  if (endInput && p.ngay_ket_thuc) endInput.value = p.ngay_ket_thuc;
  if (moTaInput) moTaInput.value = p.mo_ta || "";
  if (tieuDe) tieuDe.textContent = `Chỉnh Sửa Lịch Trình (Chương Trình #${p.ma_chuong_trinh})`;
  if (nhanNut) nhanNut.textContent = "Cập nhật lịch chương trình";

  tinhToanThoiGian();

  const formSection = document.getElementById("bieuMauChuongTrinh");
  if (formSection) {
    formSection.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function xemChiTiet(id) {
  chuanBiChinhSua(id);
}

async function xuLyLuuLich() {
  const programIdInput = document.getElementById("maChuongTrinh");
  const programIdStr = programIdInput ? programIdInput.value.trim() : "";
  const programId = programIdStr ? parseInt(programIdStr, 10) : null;

  const ten = document.getElementById("tenChuongTrinh") ? document.getElementById("tenChuongTrinh").value.trim() : "";
  const pbSelect = document.getElementById("phongBan");
  const maPhongBan = pbSelect ? parseInt(pbSelect.value, 10) : 1;
  const tenPhongBan = pbSelect && pbSelect.selectedOptions[0] ? pbSelect.selectedOptions[0].textContent.trim() : "";
  const batDau = document.getElementById("ngayBatDau") ? document.getElementById("ngayBatDau").value : "";
  const ketThuc = document.getElementById("ngayKetThuc") ? document.getElementById("ngayKetThuc").value : "";
  const ghiChu = document.getElementById("ghiChuDot") ? document.getElementById("ghiChuDot").value.trim() : "";
  const chiTieuInput = document.getElementById("chiTieuSV");
  const chiTieu = chiTieuInput ? parseInt(chiTieuInput.value, 10) : 50;
  const nut = document.getElementById("nutLuuLich");

  if (!ten) {
    hienThiThongBaoLoi("Thiếu thông tin bắt buộc", "Vui lòng nhập tên chương trình thực tập.");
    if (document.getElementById("tenChuongTrinh")) document.getElementById("tenChuongTrinh").focus();
    return;
  }

  if (!batDau || !ketThuc) {
    hienThiThongBaoLoi("Thiếu mốc thời gian", "Vui lòng chọn đầy đủ ngày bắt đầu và ngày kết thúc chương trình.");
    return;
  }

  if (ketThuc <= batDau) {
    hienThiThongBaoLoi(
      "Lỗi xác thực thời gian",
      "Ngày kết thúc phải lớn hơn ngày bắt đầu (ngay_ket_thuc > ngay_bat_dau). Vui lòng chọn lại mốc thời gian."
    );
    return;
  }

  if (chiTieu <= 0 || isNaN(chiTieu)) {
    hienThiThongBaoLoi("Chỉ tiêu không hợp lệ", "Chỉ tiêu số lượng sinh viên phải là số nguyên dương lớn hơn 0.");
    return;
  }

  const oldContent = nut ? nut.innerHTML : "";
  if (nut) {
    nut.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang lưu dữ liệu lên máy chủ...</span>
    `;
    nut.disabled = true;
  }

  try {
    let res;
    if (programId) {
      res = await fetch(`${duongDanApi}/programs/${programId}/timeline`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ngay_bat_dau: batDau,
          ngay_ket_thuc: ketThuc,
        }),
      });
    } else {
      res = await fetch(`${duongDanApi}/programs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ma_phong_ban: maPhongBan,
          ten_chuong_trinh: ten,
          mo_ta: ghiChu || null,
          ngay_bat_dau: batDau,
          ngay_ket_thuc: ketThuc,
        }),
      });
    }

    const resData = await res.json();

    if (!res.ok) {
      let errorMsg = "Không thể xử lý yêu cầu chương trình thực tập.";
      if (typeof resData.detail === "string") {
        errorMsg = resData.detail;
      } else if (Array.isArray(resData.detail)) {
        errorMsg = resData.detail.map((e) => e.msg || e.message).join(", ");
      }
      hienThiThongBaoLoi("Lỗi từ hệ thống", errorMsg);
      return;
    }

    const data = resData.data || {};
    const tenHienThi = data.ten_chuong_trinh || ten;
    const startStr = data.ngay_bat_dau || batDau;
    const endStr = data.ngay_ket_thuc || ketThuc;

    if (programId) {
      hienThiThongBaoThanhCong(
        `Cập Nhật Thành Công Lịch Trình (Chương Trình #${programId})`,
        `Đã cập nhật mốc thời gian thành công cho <strong>"${tenHienThi}"</strong> từ ngày <strong>${startStr}</strong> đến <strong>${endStr}</strong> trong cơ sở dữ liệu.`
      );
    } else {
      hienThiThongBaoThanhCong(
        "Tạo Mới Thành Công Chương Trình Thực Tập",
        `Đã tạo mới chương trình <strong>"${tenHienThi}"</strong> thuộc phòng ban <strong>${tenPhongBan}</strong> với thời gian từ <strong>${startStr}</strong> đến <strong>${endStr}</strong>.`
      );
    }

    datLaiForm();
    await taiDanhSachChuongTrinh();
  } catch (error) {
    hienThiThongBaoLoi(
      "Lỗi kết nối máy chủ",
      `Không thể gửi yêu cầu lên máy chủ (${error.message || "Mất mạng"}). Vui lòng kiểm tra lại dịch vụ Backend.`
    );
  } finally {
    if (nut) {
      nut.innerHTML = oldContent;
      nut.disabled = false;
    }
  }
}

function capNhatNienKhoaLichTrinh() {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;
  const hocKy = now.getMonth() >= 8 || now.getMonth() <= 1 ? "Đợt 1" : "Đợt 2";
  const elNienKhoa = document.getElementById("theNienKhoaLichTrinh");
  if (elNienKhoa) elNienKhoa.textContent = `Niên khóa ${nienKhoa} • ${hocKy}`;
  const elTieuDe = document.getElementById("tieuDeCacDotThucTap");
  if (elTieuDe) elTieuDe.textContent = `Các Đợt Thực Tập Đang Triển Khai (${nienKhoa})`;
}

document.addEventListener("DOMContentLoaded", () => {
  capNhatNienKhoaLichTrinh();
  kiemTraKetNoiApi();
  taiDanhSachPhongBan();
  taiDanhSachChuongTrinh();
  tinhToanThoiGian();
});
