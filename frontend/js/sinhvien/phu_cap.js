const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let danhSachPhuCapGoc = [];
let boLocHienTai = "tat_ca";

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

function dinhDangTienVN(soTien) {
  if (soTien === null || soTien === undefined) return "0 VNĐ";
  return Number(soTien).toLocaleString("vi-VN") + " VNĐ";
}

function dinhDangNgayVN(chuoiNgay) {
  if (!chuoiNgay) return "--";
  try {
    const parts = chuoiNgay.split("-");
    if (parts.length === 3) {
      return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    const d = new Date(chuoiNgay);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("vi-VN");
    }
  } catch (e) {}
  return chuoiNgay;
}

function locBangPhuCap(trangThai) {
  boLocHienTai = trangThai;
  const btnTatCa = document.getElementById("btnLocTatCa");
  const btnDaNhan = document.getElementById("btnLocDaNhan");
  const btnChoDuyet = document.getElementById("btnLocChoDuyet");

  const classActive = "px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 transition-colors";
  const classInactive = "px-3 py-1.5 rounded-xl text-xs font-medium text-slate-600 hover:text-slate-900 border border-transparent transition-colors";

  if (btnTatCa) btnTatCa.className = trangThai === "tat_ca" ? classActive : classInactive;
  if (btnDaNhan) btnDaNhan.className = trangThai === "DaChiTra" ? classActive : classInactive;
  if (btnChoDuyet) btnChoDuyet.className = trangThai === "ChuaChiTra" ? "px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 transition-colors" : classInactive;

  renderBangPhuCap();
}

function renderBangPhuCap() {
  const tbody = document.getElementById("tbodyDanhSachPhuCap");
  if (!tbody) return;

  let danhSachHienThi = [...danhSachPhuCapGoc];
  if (boLocHienTai !== "tat_ca") {
    danhSachHienThi = danhSachHienThi.filter(item => item.trang_thai_chi_tra === boLocHienTai);
  }

  const elDemTatCa = document.getElementById("demTatCa");
  const elDemDaNhan = document.getElementById("demDaNhan");
  const elDemChoDuyet = document.getElementById("demChoDuyet");

  if (elDemTatCa) elDemTatCa.textContent = danhSachPhuCapGoc.length;
  if (elDemDaNhan) elDemDaNhan.textContent = danhSachPhuCapGoc.filter(x => x.trang_thai_chi_tra === "DaChiTra").length;
  if (elDemChoDuyet) elDemChoDuyet.textContent = danhSachPhuCapGoc.filter(x => x.trang_thai_chi_tra === "ChuaChiTra").length;

  if (danhSachHienThi.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="py-12 text-center text-slate-400">
          <span class="material-symbols-outlined text-[36px] text-slate-300 block mb-2">account_balance_wallet</span>
          <p class="font-medium text-slate-600 mb-1">Chưa có khoản phụ cấp nào</p>
          <p class="text-xs text-slate-400">Dữ liệu phụ cấp sẽ được cập nhật sau khi doanh nghiệp giải ngân</p>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = danhSachHienThi.map((item) => {
    const daNhan = item.trang_thai_chi_tra === "DaChiTra";
    const badgeTrangThai = daNhan
      ? `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Đã chi trả
        </span>`
      : `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
          Chờ giải ngân
        </span>`;

    let kyPhuCapText = "Kỳ thực tập";
    if (item.thang && item.nam) {
      kyPhuCapText = `Tháng ${item.thang}/${item.nam}`;
    } else if (item.thang_nam && item.thang_nam.includes("-")) {
      const p = item.thang_nam.split("-");
      kyPhuCapText = `Tháng ${p[1]}/${p[0]}`;
    }

    const ngayChiTraText = item.ngay_chi_tra ? dinhDangNgayVN(item.ngay_chi_tra) : (daNhan ? "--" : "Chờ giải ngân");
    const ghiChuText = item.ghi_chu || (daNhan ? "Chi trả phụ cấp thực tập" : "Đang chờ giải ngân");

    return `
      <tr class="hover:bg-slate-50/70 transition-colors">
        <td class="py-4 px-6">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg ${daNhan ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"} flex items-center justify-center font-bold text-xs shrink-0">
              <span class="material-symbols-outlined text-[18px]">${daNhan ? "check_circle" : "hourglass_top"}</span>
            </div>
            <div>
              <span class="font-bold text-slate-900 block">${kyPhuCapText}</span>
              <span class="text-[11px] text-slate-400 font-mono">Mã PC: #${item.ma_phu_cap}</span>
            </div>
          </div>
        </td>
        <td class="py-4 px-6 font-mono text-slate-600">
          ${ngayChiTraText}
        </td>
        <td class="py-4 px-6">
          <span class="font-mono font-extrabold text-sm ${daNhan ? "text-emerald-700" : "text-amber-700"}">
            ${dinhDangTienVN(item.so_tien)}
          </span>
        </td>
        <td class="py-4 px-6">
          ${badgeTrangThai}
        </td>
        <td class="py-4 px-6 text-slate-500 max-w-xs truncate">
          ${ghiChuText}
        </td>
      </tr>
    `;
  }).join("");
}

async function taiDuLieuPhuCap() {
  const tbody = document.getElementById("tbodyDanhSachPhuCap");
  const internId = layIdSinhVien();

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="py-12 text-center text-slate-400">
          <span class="inline-block w-8 h-8 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mb-2"></span>
          <p>Đang tải dữ liệu phụ cấp thực tập sinh...</p>
        </td>
      </tr>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/interns/${internId}/allowances`);
    if (!res.ok) {
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="5" class="py-12 text-center text-rose-500">
              <span class="material-symbols-outlined text-[36px] text-rose-400 block mb-2">error</span>
              <p class="font-bold mb-1">Không thể tải thông tin phụ cấp</p>
              <p class="text-xs text-slate-400 mb-3">Mã hồ sơ sinh viên không tồn tại hoặc chưa được khởi tạo phụ cấp</p>
              <button type="button" onclick="taiDuLieuPhuCap()" class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold text-xs hover:bg-emerald-700 cursor-pointer">
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
    if (!data) return;

    if (data.ho_ten) {
      const elTen = document.getElementById("sidebarTenSinhVien");
      if (elTen) elTen.textContent = data.ho_ten;
      const elAvatar = document.getElementById("avatarInitials");
      if (elAvatar) {
        const words = data.ho_ten.trim().split(/\s+/);
        elAvatar.textContent = words.length >= 2
          ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
          : data.ho_ten.substring(0, 2).toUpperCase();
      }
    }
    if (data.lop || data.email) {
      const elMa = document.getElementById("sidebarMaSinhVien");
      if (elMa) {
        const email = data.email || "";
        const maSV = email.includes("@") ? email.split("@")[0].toUpperCase() : "QUANGHUY.DTC";
        elMa.textContent = `${maSV} - ${data.lop || "K19"}`;
      }
    }

    const summary = data.summary || {};
    const elTong = document.getElementById("kpiTongPhuCap");
    const elDaNhan = document.getElementById("kpiDaNhan");
    const elChoGiaiNgan = document.getElementById("kpiChoGiaiNgan");
    const elSoDaNhan = document.getElementById("kpiSoKhoanDaNhan");
    const elSoCho = document.getElementById("kpiSoKhoanCho");

    if (elTong) elTong.textContent = dinhDangTienVN(summary.tong_tien_phu_cap);
    if (elDaNhan) elDaNhan.textContent = dinhDangTienVN(summary.tong_tien_da_nhan);
    if (elChoGiaiNgan) elChoGiaiNgan.textContent = dinhDangTienVN(summary.tong_tien_cho_giai_ngan);
    if (elSoDaNhan) elSoDaNhan.textContent = summary.so_khoan_da_nhan || 0;
    if (elSoCho) elSoCho.textContent = summary.so_khoan_cho_giai_ngan || 0;

    const elTienDo = document.getElementById("kpiTienDoGiaiNgan");
    const elSoDot = document.getElementById("kpiSoDotHoanTat");
    const tongKhoan = (data.danh_sach_phu_cap || []).length;
    const phanTram = summary.tong_tien_phu_cap > 0
      ? Math.round((summary.tong_tien_da_nhan / summary.tong_tien_phu_cap) * 100)
      : 0;
    if (elTienDo) elTienDo.textContent = `${phanTram}%`;
    if (elSoDot) elSoDot.textContent = `${summary.so_khoan_da_nhan || 0}/${tongKhoan}`;

    danhSachPhuCapGoc = data.danh_sach_phu_cap || [];
    renderBangPhuCap();

  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="py-12 text-center text-rose-500">
            <span class="material-symbols-outlined text-[36px] text-rose-400 block mb-2">wifi_off</span>
            <p class="font-bold mb-1">Mất kết nối máy chủ</p>
            <p class="text-xs text-slate-400 mb-3">Vui lòng kiểm tra lại mạng hoặc kết nối Backend</p>
            <button type="button" onclick="taiDuLieuPhuCap()" class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-semibold text-xs hover:bg-emerald-700 cursor-pointer">
              Thử lại
            </button>
          </td>
        </tr>
      `;
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  if (typeof dongBoThongTinNguoiDung === "function") {
    dongBoThongTinNguoiDung();
  }
  taiDuLieuPhuCap();
});
