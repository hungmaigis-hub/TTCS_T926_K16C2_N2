const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

const sessionAdminHienTai = typeof layThongTinSession === "function" ? layThongTinSession("manager") : JSON.parse(localStorage.getItem("ictu_admin_session") || "null");
if (sessionAdminHienTai && (sessionAdminHienTai.vai_tro === "Mentor" || sessionAdminHienTai.vai_tro === "mentor" || sessionAdminHienTai.vai_tro === "NhaTruong")) {
  window.location.href = "dashboard.html";
}

let trangHienTaiNhatKy = 1;
let kichThuocTrangHienTaiNhatKy = 15;
let tongSoTrangNhatKy = 1;
let dangTaiNhatKy = false;
let debounceTimerNhatKy = null;
let danhSachNhatKyHienTai = [];

function layTenVietTat(hoTen) {
  if (!hoTen) return "AD";
  const words = hoTen.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
  }
  return hoTen.substring(0, 2).toUpperCase();
}

function layEmailDangNhapHienTai() {
  const sessionAdmin = typeof layThongTinSession === "function" ? layThongTinSession("manager") : JSON.parse(localStorage.getItem("ictu_admin_session") || "null");
  return sessionAdmin && sessionAdmin.email ? sessionAdmin.email : "admin@ictu.edu.vn";
}

function layHeadersXacThuc() {
  const email = layEmailDangNhapHienTai();
  return {
    "Content-Type": "application/json",
    "X-User-Email": email,
    "Authorization": `Bearer ${email}`
  };
}

function layCauHinhHanhDongNhatKy(hanhDong) {
  const mapHanhDong = {
    "DANG_NHAP": { text: "Đăng nhập", color: "bg-blue-50 text-blue-700 border-blue-200", icon: "login" },
    "DANG_XUAT": { text: "Đăng xuất", color: "bg-slate-50 text-slate-700 border-slate-200", icon: "logout" },
    "PHAN_QUYEN_RBAC": { text: "Phân quyền RBAC", color: "bg-amber-50 text-amber-700 border-amber-200", icon: "admin_panel_settings" },
    "SAO_LUU_CSDL": { text: "Sao lưu CSDL", color: "bg-emerald-50 text-emerald-700 border-emerald-200", icon: "backup" },
    "NHAP_HO_SO_HANG_LOAT": { text: "Nạp hồ sơ SV", color: "bg-indigo-50 text-indigo-700 border-indigo-200", icon: "upload_file" },
    "XET_DUYET_HO_SO": { text: "Xét duyệt hồ sơ", color: "bg-teal-50 text-teal-700 border-teal-200", icon: "how_to_reg" },
    "CAP_NHAT_NGUOI_DUNG": { text: "Cập nhật tài khoản", color: "bg-violet-50 text-violet-700 border-violet-200", icon: "edit_square" },
    "TAO_NGUOI_DUNG": { text: "Tạo tài khoản", color: "bg-cyan-50 text-cyan-700 border-cyan-200", icon: "person_add" },
    "KHOA_TAI_KHOAN": { text: "Khóa tài khoản", color: "bg-rose-50 text-rose-700 border-rose-200", icon: "lock" },
    "GIAO_NHIEM_VU": { text: "Giao nhiệm vụ", color: "bg-purple-50 text-purple-700 border-purple-200", icon: "assignment" },
    "LEN_LICH_HOP": { text: "Lên lịch họp", color: "bg-sky-50 text-sky-700 border-sky-200", icon: "calendar_month" },
    "CHAM_CONG_QR": { text: "Chấm công QR", color: "bg-emerald-50 text-emerald-700 border-emerald-200", icon: "qr_code_scanner" },
    "DONG_BO_HRM": { text: "Đồng bộ HRM", color: "bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200", icon: "sync" }
  };
  return mapHanhDong[hanhDong] || { text: hanhDong || "Hoạt động", color: "bg-slate-50 text-slate-700 border-slate-200", icon: "info" };
}

function layBadgePhuongThucHTTP(method) {
  const m = (method || "GET").toUpperCase();
  if (m === "POST") return '<span class="px-2 py-0.5 rounded text-[10px] font-mono font-extrabold bg-emerald-100 text-emerald-800">POST</span>';
  if (m === "PUT") return '<span class="px-2 py-0.5 rounded text-[10px] font-mono font-extrabold bg-amber-100 text-amber-800">PUT</span>';
  if (m === "PATCH") return '<span class="px-2 py-0.5 rounded text-[10px] font-mono font-extrabold bg-sky-100 text-sky-800">PATCH</span>';
  if (m === "DELETE") return '<span class="px-2 py-0.5 rounded text-[10px] font-mono font-extrabold bg-rose-100 text-rose-800">DELETE</span>';
  return '<span class="px-2 py-0.5 rounded text-[10px] font-mono font-extrabold bg-slate-100 text-slate-700">GET</span>';
}

function layBadgeHttpStatus(code) {
  const c = parseInt(code, 10) || 200;
  if (c >= 200 && c < 300) {
    return `<span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">${c} OK</span>`;
  }
  if (c >= 400 && c < 500) {
    return `<span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-50 text-amber-700 border border-amber-200">${c} Err</span>`;
  }
  return `<span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-rose-50 text-rose-700 border border-rose-200">${c} Fail</span>`;
}

function dongThongBaoLoi() {
  const errBox = document.getElementById("thongBaoLoiNhatKy");
  if (errBox) errBox.classList.add("hidden");
}

async function taiDanhSachNhatKyHoatDong() {
  if (dangTaiNhatKy) return;

  const tbody = document.getElementById("bangNhatKyTbody");
  const errBox = document.getElementById("thongBaoLoiNhatKy");
  const errMsg = document.getElementById("noiDungLoiNhatKy");
  const iconLamMoi = document.getElementById("iconLamMoi");
  const btnLamMoi = document.getElementById("btnLamMoiNhatKy");

  if (errBox) errBox.classList.add("hidden");
  if (iconLamMoi) iconLamMoi.classList.add("animate-spin");
  if (btnLamMoi) btnLamMoi.disabled = true;

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-12 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl animate-spin text-violet-500">progress_activity</span>
            <p class="font-medium text-xs">Đang tải lịch sử hoạt động hệ thống...</p>
          </div>
        </td>
      </tr>
    `;
  }

  dangTaiNhatKy = true;

  try {
    const tuKhoa = document.getElementById("timKiemNhatKy")?.value.trim() || "";
    const hanhDong = document.getElementById("locHanhDongNhatKy")?.value || "";
    const phuongThuc = document.getElementById("locPhuongThucNhatKy")?.value || "";
    const tuNgay = document.getElementById("locTuNgayNhatKy")?.value || "";
    const denNgay = document.getElementById("locDenNgayNhatKy")?.value || "";

    if (tuNgay && denNgay && tuNgay > denNgay) {
      throw new Error("Ngày bắt đầu không được lớn hơn ngày kết thúc trong bộ lọc thời gian!");
    }

    const params = new URLSearchParams({
      page: String(trangHienTaiNhatKy),
      page_size: String(kichThuocTrangHienTaiNhatKy)
    });

    if (tuKhoa) params.append("tu_khoa", tuKhoa);
    if (hanhDong) params.append("hanh_dong", hanhDong);
    if (phuongThuc) params.append("phuong_thuc", phuongThuc);
    if (tuNgay) params.append("tu_ngay", tuNgay);
    if (denNgay) params.append("den_ngay", denNgay);

    const res = await fetch(`${duongDanApi}/admin/audit-logs?${params.toString()}`, {
      headers: layHeadersXacThuc()
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      let msg = "Không thể tải danh sách nhật ký hoạt động";
      if (typeof errJson.detail === "string") {
        msg = errJson.detail;
      } else if (Array.isArray(errJson.detail)) {
        msg = errJson.detail.map(d => d.msg || JSON.stringify(d)).join(", ");
      }
      throw new Error(msg);
    }

    const data = await res.json();
    danhSachNhatKyHienTai = data.items || [];
    tongSoTrangNhatKy = data.total_pages || 1;
    trangHienTaiNhatKy = data.page || 1;

    const kpiTong = document.getElementById("kpiTongNhatKy");
    if (kpiTong) kpiTong.textContent = data.stats?.total_logs ?? data.total ?? 0;

    const kpiHomNay = document.getElementById("kpiNhatKyHomNay");
    if (kpiHomNay) kpiHomNay.textContent = data.stats?.today_logs ?? 0;

    const kpiTyLe = document.getElementById("kpiTyLeThanhCong");
    if (kpiTyLe) kpiTyLe.textContent = `${data.stats?.success_rate ?? 100}%`;

    const kpiNguoiDung = document.getElementById("kpiNguoiDungThaoTac");
    if (kpiNguoiDung) kpiNguoiDung.textContent = data.stats?.unique_users ?? 0;

    renderBangNhatKy(danhSachNhatKyHienTai);

    const txtTrang = document.getElementById("txtTrangHienTaiNhatKy");
    if (txtTrang) txtTrang.textContent = `${trangHienTaiNhatKy} / ${tongSoTrangNhatKy}`;

    const btnTruoc = document.getElementById("btnTrangTruocNhatKy");
    if (btnTruoc) btnTruoc.disabled = trangHienTaiNhatKy <= 1;

    const btnSau = document.getElementById("btnTrangSauNhatKy");
    if (btnSau) btnSau.disabled = trangHienTaiNhatKy >= tongSoTrangNhatKy;

    const thongKe = document.getElementById("txtThongKeNhatKy");
    if (thongKe) {
      const start = data.total === 0 ? 0 : (trangHienTaiNhatKy - 1) * kichThuocTrangHienTaiNhatKy + 1;
      const end = Math.min(trangHienTaiNhatKy * kichThuocTrangHienTaiNhatKy, data.total || 0);
      thongKe.textContent = `Hiển thị ${start} - ${end} trên ${data.total || 0} bản ghi`;
    }

  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="py-12 text-center text-rose-500 font-semibold">
            <div class="flex flex-col items-center justify-center gap-2">
              <span class="material-symbols-outlined text-4xl">error</span>
              <p>${err.message || "Lỗi tải nhật ký hoạt động từ máy chủ"}</p>
              <button type="button" onclick="taiDanhSachNhatKyHoatDong()" class="mt-2 px-3 py-1.5 rounded-lg bg-rose-100 hover:bg-rose-200 text-rose-700 text-xs font-bold transition-all cursor-pointer">Thử lại</button>
            </div>
          </td>
        </tr>
      `;
    }
    if (errBox && errMsg) {
      errMsg.textContent = err.message || "Lỗi tải dữ liệu nhật ký";
      errBox.classList.remove("hidden");
    }
  } finally {
    dangTaiNhatKy = false;
    if (iconLamMoi) iconLamMoi.classList.remove("animate-spin");
    if (btnLamMoi) btnLamMoi.disabled = false;
  }
}

function renderBangNhatKy(items) {
  const tbody = document.getElementById("bangNhatKyTbody");
  if (!tbody) return;

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-12 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl text-slate-300">history_toggle_off</span>
            <p class="font-medium text-xs">Không tìm thấy bản ghi nhật ký hoạt động nào phù hợp.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map((r) => {
    const actCfg = layCauHinhHanhDongNhatKy(r.hanh_dong);
    const methodBadge = layBadgePhuongThucHTTP(r.phuong_thuc);
    const statusBadge = layBadgeHttpStatus(r.trang_thai_http);
    const initials = layTenVietTat(r.ho_ten);

    const roleBadge = r.vai_tro === "Admin"
      ? '<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-rose-100 text-rose-700">Admin</span>'
      : r.vai_tro === "HR"
      ? '<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-100 text-amber-700">HR</span>'
      : r.vai_tro === "Mentor"
      ? '<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-violet-100 text-violet-700">Mentor</span>'
      : '<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-slate-100 text-slate-600">' + (r.vai_tro || "User") + '</span>';

    return `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="py-3.5 px-6 whitespace-nowrap">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-slate-700 font-mono">${r.thoi_gian || "--"}</span>
            ${statusBadge}
          </div>
        </td>
        <td class="py-3.5 px-4 whitespace-nowrap">
          <div class="flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 font-extrabold text-[11px] flex items-center justify-center shrink-0 border border-slate-200">
              ${initials}
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-bold text-slate-900">${r.ho_ten || "Hệ thống"}</span>
                ${roleBadge}
              </div>
              <p class="text-[10px] text-slate-400 font-mono">${r.email || "--"}</p>
            </div>
          </div>
        </td>
        <td class="py-3.5 px-4 whitespace-nowrap">
          <span class="px-2.5 py-1 rounded-lg text-xs font-semibold border inline-flex items-center gap-1.5 ${actCfg.color}">
            <span class="material-symbols-outlined text-[14px]">${actCfg.icon}</span>
            <span>${actCfg.text}</span>
          </span>
        </td>
        <td class="py-3.5 px-4">
          <div class="flex items-center gap-1.5 max-w-[260px]">
            ${methodBadge}
            <span class="text-xs font-mono text-slate-600 truncate" title="${r.endpoint}">${r.endpoint}</span>
          </div>
        </td>
        <td class="py-3.5 px-4 whitespace-nowrap">
          <span class="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[11px] font-mono border border-slate-200/60">
            ${r.dia_chi_ip || "127.0.0.1"}
          </span>
        </td>
        <td class="py-3.5 px-6">
          <p class="text-xs text-slate-600 leading-relaxed line-clamp-2" title="${r.mo_ta || ''}">
            ${r.mo_ta || "--"}
          </p>
        </td>
        <td class="py-3.5 px-4 text-center whitespace-nowrap">
          <button
            type="button"
            onclick="xemChiTietNhatKy(${r.ma_nhat_ky})"
            class="w-8 h-8 rounded-lg hover:bg-violet-50 text-slate-400 hover:text-violet-700 transition-colors inline-flex items-center justify-center cursor-pointer"
            title="Xem chi tiết bản ghi"
          >
            <span class="material-symbols-outlined text-[18px]">visibility</span>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function xemChiTietNhatKy(maNhatKy) {
  const item = danhSachNhatKyHienTai.find(x => x.ma_nhat_ky === maNhatKy);
  if (!item) return;

  const modal = document.getElementById("modalChiTietNhatKy");
  if (!modal) return;

  const actCfg = layCauHinhHanhDongNhatKy(item.hanh_dong);

  const elMa = document.getElementById("modalMaNhatKy");
  if (elMa) elMa.textContent = `#LOG-${item.ma_nhat_ky}`;

  const elThoiGian = document.getElementById("modalThoiGian");
  if (elThoiGian) elThoiGian.textContent = item.thoi_gian || "--";

  const elTrangThai = document.getElementById("modalTrangThaiHttp");
  if (elTrangThai) elTrangThai.innerHTML = `${layBadgeHttpStatus(item.trang_thai_http)} ${layBadgePhuongThucHTTP(item.phuong_thuc)}`;

  const elNguoi = document.getElementById("modalNguoiThaoTac");
  if (elNguoi) elNguoi.textContent = item.ho_ten || "Hệ thống tự động";

  const elEmailVaiTro = document.getElementById("modalEmailVaiTro");
  if (elEmailVaiTro) elEmailVaiTro.textContent = `${item.email || '--'} (${item.vai_tro || 'User'})`;

  const elHanhDong = document.getElementById("modalHanhDong");
  if (elHanhDong) elHanhDong.textContent = `${actCfg.text} [${item.hanh_dong}]`;

  const elIp = document.getElementById("modalDiaChiIp");
  if (elIp) elIp.textContent = item.dia_chi_ip || "127.0.0.1";

  const elEndpoint = document.getElementById("modalEndpoint");
  if (elEndpoint) elEndpoint.textContent = `${item.phuong_thuc || 'GET'} ${item.endpoint || '/'}`;

  const elMoTa = document.getElementById("modalMoTa");
  if (elMoTa) elMoTa.textContent = item.mo_ta || "Không có mô tả chi tiết cho thao tác này.";

  modal.classList.remove("hidden");
}

function dongModalChiTietNhatKy() {
  const modal = document.getElementById("modalChiTietNhatKy");
  if (modal) modal.classList.add("hidden");
}

function chuyenTrangNhatKy(delta) {
  const trangMoi = trangHienTaiNhatKy + delta;
  if (trangMoi >= 1 && trangMoi <= tongSoTrangNhatKy) {
    trangHienTaiNhatKy = trangMoi;
    taiDanhSachNhatKyHoatDong();
  }
}

function thayDoiKichThuocTrangNhatKy(val) {
  const sz = parseInt(val, 10);
  if (!isNaN(sz) && sz > 0) {
    kichThuocTrangHienTaiNhatKy = sz;
    trangHienTaiNhatKy = 1;
    taiDanhSachNhatKyHoatDong();
  }
}

function xuLyTimKiemNhatKyDebounce() {
  clearTimeout(debounceTimerNhatKy);
  debounceTimerNhatKy = setTimeout(() => {
    trangHienTaiNhatKy = 1;
    taiDanhSachNhatKyHoatDong();
  }, 350);
}

function datLaiBoLocNhatKy() {
  const elTk = document.getElementById("timKiemNhatKy");
  const elHd = document.getElementById("locHanhDongNhatKy");
  const elPt = document.getElementById("locPhuongThucNhatKy");
  const elTn = document.getElementById("locTuNgayNhatKy");
  const elDn = document.getElementById("locDenNgayNhatKy");

  if (elTk) elTk.value = "";
  if (elHd) elHd.value = "";
  if (elPt) elPt.value = "";
  if (elTn) elTn.value = "";
  if (elDn) elDn.value = "";

  trangHienTaiNhatKy = 1;
  taiDanhSachNhatKyHoatDong();
}

async function xuatBaoCaoNhatKyCSV() {
  const btnXuat = document.getElementById("btnXuatCsvNhatKy");
  if (btnXuat) btnXuat.disabled = true;

  try {
    const tuKhoa = document.getElementById("timKiemNhatKy")?.value.trim() || "";
    const hanhDong = document.getElementById("locHanhDongNhatKy")?.value || "";
    const phuongThuc = document.getElementById("locPhuongThucNhatKy")?.value || "";
    const tuNgay = document.getElementById("locTuNgayNhatKy")?.value || "";
    const denNgay = document.getElementById("locDenNgayNhatKy")?.value || "";

    const params = new URLSearchParams({
      page: "1",
      page_size: "10000"
    });

    if (tuKhoa) params.append("tu_khoa", tuKhoa);
    if (hanhDong) params.append("hanh_dong", hanhDong);
    if (phuongThuc) params.append("phuong_thuc", phuongThuc);
    if (tuNgay) params.append("tu_ngay", tuNgay);
    if (denNgay) params.append("den_ngay", denNgay);

    const res = await fetch(`${duongDanApi}/admin/audit-logs?${params.toString()}`, {
      headers: layHeadersXacThuc()
    });

    if (!res.ok) {
      throw new Error("Không thể trích xuất dữ liệu từ máy chủ");
    }

    const data = await res.json();
    const danhSachXuat = data.items || [];

    if (danhSachXuat.length === 0) {
      alert("Không tìm thấy bản ghi nhật ký hoạt động nào để xuất báo cáo!");
      return;
    }

    const tieuDe = ["Mã Nhật Ký", "Thời Gian", "Người Thực Hiện", "Email", "Vai Trò", "Hành Động", "Phương Thức", "Endpoint API", "Địa Chỉ IP", "Mã HTTP", "Mô Tả"];
    const hangDuLieu = danhSachXuat.map(item => [
      item.ma_nhat_ky,
      `"${item.thoi_gian || ''}"`,
      `"${(item.ho_ten || '').replace(/"/g, '""')}"`,
      `"${item.email || ''}"`,
      `"${item.vai_tro || ''}"`,
      `"${item.hanh_dong || ''}"`,
      `"${item.phuong_thuc || ''}"`,
      `"${item.endpoint || ''}"`,
      `"${item.dia_chi_ip || ''}"`,
      item.trang_thai_http || 200,
      `"${(item.mo_ta || '').replace(/"/g, '""')}"`
    ]);

    const noiDungCsv = "\uFEFF" + [tieuDe.join(","), ...hangDuLieu.map(h => h.join(","))].join("\r\n");
    const blob = new Blob([noiDungCsv], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const thoiGianStr = new Date().toISOString().slice(0, 10);
    const tenFile = tuKhoa ? `Nhat_Ky_${tuKhoa.replace(/[^a-zA-Z0-9]/g, '_')}_${thoiGianStr}.csv` : `Nhat_Ky_Hoat_Dong_ICTU_${thoiGianStr}.csv`;
    a.download = tenFile;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Lỗi xuất tệp CSV: ${err.message || err}`);
  } finally {
    if (btnXuat) btnXuat.disabled = false;
  }
}

function dongBoThongTinNguoiDung() {
  const sessionAdmin = typeof layThongTinSession === "function" ? layThongTinSession("manager") : JSON.parse(localStorage.getItem("ictu_admin_session") || "null");
  if (!sessionAdmin) return;

  const elName = document.getElementById("adminSidebarName");
  const elEmail = document.getElementById("adminSidebarEmail");
  const elRole = document.getElementById("adminSidebarRole");
  const elAvatar = document.getElementById("adminAvatarInitials");

  if (elName && sessionAdmin.ho_ten) elName.textContent = sessionAdmin.ho_ten;
  if (elEmail && sessionAdmin.email) elEmail.textContent = sessionAdmin.email;
  if (elRole && sessionAdmin.vai_tro) elRole.textContent = sessionAdmin.vai_tro === "Admin" ? "Quản trị viên" : sessionAdmin.vai_tro;
  if (elAvatar && sessionAdmin.ho_ten) elAvatar.textContent = layTenVietTat(sessionAdmin.ho_ten);
}

window.addEventListener("DOMContentLoaded", () => {
  dongBoThongTinNguoiDung();
  taiDanhSachNhatKyHoatDong();
});
