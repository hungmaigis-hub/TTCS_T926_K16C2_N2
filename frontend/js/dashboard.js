const duongDanApi = "http://127.0.0.1:8000/api/v1";

function layTenVietTat(hoTen) {
  if (!hoTen) return "NA";
  const words = hoTen.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
  }
  return hoTen.substring(0, 2).toUpperCase();
}

function renderBangSinhVien(danhSach) {
  const bangTbody = document.getElementById("bangSinhVienHoatDong");
  if (!bangTbody || !danhSach || danhSach.length === 0) return;
  bangTbody.innerHTML = "";
  const hienThi = danhSach.slice(0, 6);
  hienThi.forEach((sv) => {
    const hoTen = sv.ho_ten || "Sinh viên";
    const email = sv.email || "sv@ictu.edu.vn";
    const initials = layTenVietTat(hoTen);
    const chuyenNganh = sv.chuyen_nganh || "Công nghệ thông tin";
    const donVi = sv.ten_mentor ? `Mentor: ${sv.ten_mentor}` : (sv.ten_truong || "FPT Software Hà Nội");
    
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
        <a href="xet_duyet_ho_so.html" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-ictu-600 hover:text-white font-semibold text-slate-700 transition-colors inline-block">
          Chi tiết
        </a>
      </td>
    `;
    bangTbody.appendChild(tr);
  });
}

function napDuLieuCacheDashboard() {
  try {
    const raw = localStorage.getItem("ictu_dashboard_cache");
    if (!raw) return;
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
    if (cache.danhSach && cache.danhSach.length > 0) {
      renderBangSinhVien(cache.danhSach);
    }
  } catch {}
}

async function taiDuLieuDashboard() {
  try {
    const res = await fetch(`${duongDanApi}/interns`);
    if (!res.ok) return;
    const json = await res.json();
    const danhSach = json.data || [];
    const tongSo = json.total || danhSach.length;

    const choDuyet = danhSach.filter((x) => x.trang_thai_xet_duyet === "ChoDuyet").length;
    const daKy = danhSach.filter((x) => x.trang_thai_thuc_tap === "DangThucTap" || x.trang_thai_xet_duyet === "DaDuyet").length;
    
    const setDoanhNghiep = new Set();
    danhSach.forEach((x) => {
      if (x.ten_mentor) setDoanhNghiep.add(x.ten_mentor);
      if (x.ten_truong) setDoanhNghiep.add(x.ten_truong);
    });
    const soDoanhNghiep = setDoanhNghiep.size || 18;

    const elTong = document.getElementById("kpiTongTTS");
    if (elTong) elTong.textContent = tongSo.toLocaleString("vi-VN");

    const elChoDuyet = document.getElementById("kpiHoSoChoDuyet");
    if (elChoDuyet) elChoDuyet.textContent = choDuyet.toLocaleString("vi-VN");

    const elDaKy = document.getElementById("kpiHopDongDaKy");
    if (elDaKy) elDaKy.textContent = daKy.toLocaleString("vi-VN");

    const elDoanhNghiep = document.getElementById("kpiDoanhNghiep");
    if (elDoanhNghiep) elDoanhNghiep.textContent = soDoanhNghiep.toLocaleString("vi-VN");

    const badgeSidebar = document.getElementById("sidebarBadgeChoDuyet");
    if (badgeSidebar) {
      badgeSidebar.textContent = `${choDuyet} chờ`;
    }

    renderBangSinhVien(danhSach);

    try {
      localStorage.setItem("ictu_dashboard_cache", JSON.stringify({
        tongSo,
        choDuyet,
        daKy,
        soDoanhNghiep,
        danhSach: danhSach.slice(0, 6)
      }));
    } catch {}
  } catch (err) {}
}

napDuLieuCacheDashboard();
window.addEventListener("DOMContentLoaded", () => {
  napDuLieuCacheDashboard();
  taiDuLieuDashboard();
});
