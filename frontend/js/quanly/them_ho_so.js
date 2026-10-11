const duongDanApiInterns = "http://127.0.0.1:8000/api/v1/interns";
const duongDanApiStudents = "http://127.0.0.1:8000/api/v1/students";
const duongDanApiPrograms = "http://127.0.0.1:8000/api/v1/programs";
const duongDanApiMentors = "http://127.0.0.1:8000/api/v1/mentors";
const duongDanApiUniversities = "http://127.0.0.1:8000/api/v1/universities";

let danhSachSinhVien = [];
let danhSachChuongTrinh = [];
let danhSachMentor = [];

let sinhVienDaChon = null;
let chuongTrinhDaChon = null;
let mentorDaChon = null;
let trangThaiHienTai = "Đang thực tập";

let tabSinhVienHienTai = "all";
let tuKhoaSinhVienHienTai = "";

let tabChuongTrinhHienTai = "all";
let tuKhoaChuongTrinhHienTai = "";

let tabMentorHienTai = "all";
let tuKhoaMentorHienTai = "";

let maHoSoHienTai = null;

let thoiGianHenGioToast = null;
let thongDiepToastHienTai = "";

let danhSachTruongChuan = [
  { id: 1, tenNgan: "ICTU", ten: "Trường ĐH Công nghệ Thông tin & Truyền thông - ĐHTN (ICTU)", loai: "Đối tác trọng điểm" },
  { id: 2, tenNgan: "HUST", ten: "Đại học Bách Khoa Hà Nội (HUST)", loai: "Đối tác liên kết" },
  { id: 3, tenNgan: "FPT", ten: "Trường Đại học FPT Hà Nội", loai: "Đối tác liên kết" },
  { id: 4, tenNgan: "UIT", ten: "Trường ĐH Công nghệ Thông tin - ĐHQG TP.HCM (UIT)", loai: "Đối tác liên kết" },
  { id: 5, tenNgan: "NEU", ten: "Trường Đại học Kinh tế Quốc dân (NEU)", loai: "Đối tác liên kết" },
  { id: 6, tenNgan: "ĐHQG", ten: "Trường Đại học Quốc gia TP.HCM", loai: "Đối tác liên kết" },
  { id: 7, tenNgan: "PTIT", ten: "Học viện Công nghệ Bưu chính Viễn thông (PTIT)", loai: "Đối tác liên kết" },
  { id: 8, tenNgan: "UET", ten: "Trường Đại học Công nghệ - ĐHQGHN (UET)", loai: "Đối tác liên kết" }
];

let goiYChuyenNganhTheoTruong = {
  1: [
    "Kỹ thuật phần mềm",
    "Công nghệ thông tin",
    "Khoa học máy tính",
    "Trí tuệ nhân tạo",
    "An toàn thông tin",
    "Hệ thống thông tin",
    "Truyền thông và mạng máy tính",
    "Kỹ thuật máy tính",
    "Công nghệ đa phương tiện & Thiết kế đồ họa",
    "Thương mại điện tử & Kinh tế số",
    "Công nghệ vi mạch bán dẫn",
    "Công nghệ kỹ thuật điện tử - viễn thông",
    "Công nghệ thông tin ứng dụng",
    "Công nghệ phần mềm song bằng (Kyungpook - Hàn Quốc)",
    "Công nghệ thông tin Quốc tế (IT Global)",
    "Công nghệ thông tin Trọng điểm (IT Core)"
  ],
  2: [
    "Khoa học máy tính (IT1)",
    "Kỹ thuật máy tính (IT2)",
    "Khoa học dữ liệu & Trí tuệ nhân tạo (IT-E10)",
    "An toàn không gian số (Cyber Security)",
    "Công nghệ thông tin Global ICT",
    "Hệ thống nhúng thông minh & IoT",
    "Kỹ thuật phần mềm"
  ],
  3: [
    "Kỹ thuật phần mềm (SE)",
    "An toàn thông tin (IA)",
    "Trí tuệ nhân tạo (AI)",
    "Hệ thống thông tin (IS)",
    "Thiết kế mỹ thuật số (Digital Art & Design)",
    "Thiết kế đồ họa"
  ],
  4: [
    "Kỹ thuật phần mềm",
    "Khoa học máy tính",
    "An toàn thông tin",
    "Mạng máy tính & Truyền thông",
    "Kỹ thuật dữ liệu",
    "Trí tuệ nhân tạo",
    "Hệ thống thông tin"
  ],
  5: [
    "Hệ thống thông tin quản lý (MIS)",
    "Công nghệ thông tin trong kinh tế",
    "Khoa học dữ liệu trong kinh tế & kinh doanh",
    "Chuyển đổi số & Thương mại điện tử"
  ],
  6: [
    "Khoa học máy tính",
    "Kỹ thuật phần mềm",
    "Công nghệ thông tin",
    "Kỹ thuật máy tính",
    "An toàn thông tin"
  ],
  7: [
    "Công nghệ thông tin",
    "An toàn thông tin",
    "Khoa học máy tính",
    "Kỹ thuật điện tử viễn thông",
    "Công nghệ đa phương tiện"
  ],
  8: [
    "Công nghệ thông tin",
    "Khoa học máy tính",
    "Hệ thống thông tin",
    "Mạng máy tính & Truyền thông dữ liệu",
    "Kỹ thuật Robot"
  ]
};

const danhSachNganhChung = [
  "Kỹ thuật phần mềm",
  "Công nghệ thông tin",
  "An toàn thông tin",
  "Khoa học máy tính",
  "Trí tuệ nhân tạo & Khoa học dữ liệu",
  "Hệ thống thông tin",
  "Mạng máy tính & Truyền thông",
  "Kỹ thuật máy tính",
  "Thiết kế đồ họa",
  "Thương mại điện tử",
  "Hệ thống thông tin quản lý",
  "Kỹ thuật vi mạch bán dẫn"
];

function toggleDropdownTruong(forceState) {
  const menu = document.getElementById("menuDropdownTruong");
  const icon = document.getElementById("iconMuiTenTruong");
  if (!menu) return;

  const dangMo = !menu.classList.contains("hidden");
  const muonMo = forceState !== undefined ? forceState : !dangMo;

  if (muonMo) {
    dongDropdownChuyenNganh();
    dongDropdownSinhVien();
    dongDropdownMentor();
    dongDropdownChuongTrinh();
    dongDropdownTrangThai();
    menu.classList.remove("hidden");
    if (icon) icon.classList.add("rotate-180");
    veDropdownTruong("", true);
  } else {
    menu.classList.add("hidden");
    if (icon) icon.classList.remove("rotate-180");
  }
}

function moDropdownTruong() {
  toggleDropdownTruong(true);
}

function dongDropdownTruong() {
  toggleDropdownTruong(false);
}

function locDropdownTruong(tuKhoa) {
  const menu = document.getElementById("menuDropdownTruong");
  const icon = document.getElementById("iconMuiTenTruong");
  if (menu && menu.classList.contains("hidden")) {
    dongDropdownChuyenNganh();
    dongDropdownSinhVien();
    dongDropdownMentor();
    dongDropdownChuongTrinh();
    dongDropdownTrangThai();
    menu.classList.remove("hidden");
    if (icon) icon.classList.add("rotate-180");
  }
  veDropdownTruong(tuKhoa, false);
}

function veDropdownTruong(tuKhoa, xemTatCa = false) {
  const elCuon = document.getElementById("danhSachTruongCuon");
  if (!elCuon) return;

  const oInput = document.getElementById("truongDaiHoc");
  const giaTriHienTai = oInput ? oInput.value.trim() : "";

  const key = xemTatCa ? "" : (tuKhoa || "").toLowerCase().trim();
  const dsLoc = danhSachTruongChuan.filter((t) => {
    if (!key) return true;
    return t.ten.toLowerCase().includes(key) || t.tenNgan.toLowerCase().includes(key);
  });

  let html = "";
  if (dsLoc.length > 0) {
    dsLoc.forEach((t) => {
      const isSelected = giaTriHienTai.toLowerCase() === t.ten.toLowerCase();

      html += `
        <div onclick="chonTruongChuan(${t.id})" class="p-2.5 rounded-xl border transition-all flex items-center justify-between gap-2.5 cursor-pointer ${
          isSelected
            ? "bg-ictu-50/80 border-ictu-300 ring-1 ring-ictu-400/20"
            : "bg-white hover:bg-slate-50 border-slate-100 hover:border-slate-200"
        }">
          <div class="flex items-center gap-2.5 min-w-0 flex-1">
            <div class="w-7 h-7 rounded-lg bg-sky-50 text-sky-600 border border-sky-200/80 flex items-center justify-center font-bold text-[11px] shrink-0">
              ${t.tenNgan}
            </div>
            <div class="min-w-0 flex-1">
              <span class="font-bold text-slate-800 text-xs block truncate">${t.ten}</span>
              <span class="text-[10px] text-slate-400 block truncate">${t.loai}</span>
            </div>
          </div>
          ${isSelected ? `<span class="material-symbols-outlined text-[18px] text-ictu-600 shrink-0">check</span>` : ""}
        </div>
      `;
    });
  }

  if (key) {
    const coTrungKhopChinhXac = danhSachTruongChuan.some(
      (t) => t.ten.toLowerCase() === key || t.tenNgan.toLowerCase() === key
    );

    if (!coTrungKhopChinhXac) {
      const tenAnToan = tuKhoa.trim().replace(/"/g, "&quot;");
      const htmlThemTruong = `
        <div onclick="chonTruongTuyChon('${tenAnToan}')" class="p-2.5 rounded-xl border border-dashed border-sky-300 bg-sky-50/80 hover:bg-sky-100 text-sky-900 cursor-pointer flex items-center justify-between gap-2 transition-all mt-1">
          <div class="flex items-center gap-2 min-w-0 flex-1">
            <span class="material-symbols-outlined text-[18px] text-sky-600 shrink-0">add_circle</span>
            <span class="text-xs truncate">Sử dụng trường mới: <b class="font-bold text-sky-950">${tenAnToan}</b></span>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-200/80 text-sky-800 shrink-0">Ngoài danh mục</span>
        </div>
      `;

      if (dsLoc.length === 0) {
        html = htmlThemTruong + `
          <div class="pt-2 pb-1 px-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Danh mục trường đại học đối tác:
          </div>
        ` + danhSachTruongChuan.map((t) => `
          <div onclick="chonTruongChuan(${t.id})" class="p-2.5 rounded-xl border border-slate-100 hover:border-slate-200 hover:bg-slate-50 transition-all flex items-center justify-between gap-2.5 cursor-pointer">
            <div class="flex items-center gap-2.5 min-w-0 flex-1">
              <div class="w-7 h-7 rounded-lg bg-sky-50 text-sky-600 border border-sky-200/80 flex items-center justify-center font-bold text-[11px] shrink-0">
                ${t.tenNgan}
              </div>
              <div class="min-w-0 flex-1">
                <span class="font-bold text-slate-800 text-xs block truncate">${t.ten}</span>
                <span class="text-[10px] text-slate-400 block truncate">${t.loai}</span>
              </div>
            </div>
          </div>
        `).join("");
      } else {
        html += htmlThemTruong;
      }
    }
  }

  if (!html) {
    html = `<div class="py-4 text-center text-xs text-slate-400">Không tìm thấy trường nào phù hợp</div>`;
  }

  elCuon.innerHTML = html;
}

function chonTruongChuan(id, dongMenu = true) {
  const truongObj = danhSachTruongChuan.find((t) => t.id === Number(id)) || danhSachTruongChuan[0];
  const inputTen = document.getElementById("truongDaiHoc");
  const inputMa = document.getElementById("maTruong");
  const badge = document.getElementById("badgeNguonTruong");
  const nhanTheoTruong = document.getElementById("nhanTheoTruong");

  if (inputTen) inputTen.value = truongObj.ten;
  if (inputMa) inputMa.value = truongObj.id;

  if (badge) {
    badge.className = "text-[10px] text-ictu-600 bg-ictu-50 px-2 py-0.5 rounded-full border border-ictu-100 font-semibold";
    badge.textContent = "Chuẩn danh mục";
  }

  if (nhanTheoTruong) {
    nhanTheoTruong.textContent = `Theo ${truongObj.tenNgan}`;
  }

  if (dongMenu) dongDropdownTruong();
}

function chonTruongTuyChon(tenMoi, dongMenu = true) {
  const inputTen = document.getElementById("truongDaiHoc");
  const inputMa = document.getElementById("maTruong");
  const badge = document.getElementById("badgeNguonTruong");
  const nhanTheoTruong = document.getElementById("nhanTheoTruong");

  if (inputTen) inputTen.value = tenMoi;
  if (inputMa) inputMa.value = 1;

  if (badge) {
    badge.className = "text-[10px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200 font-semibold";
    badge.textContent = "Trường mới (Tùy chọn)";
  }

  if (nhanTheoTruong) {
    nhanTheoTruong.textContent = "Ngành mở rộng";
  }

  if (dongMenu) dongDropdownTruong();
}

function toggleDropdownChuyenNganh(forceState) {
  const menu = document.getElementById("menuDropdownChuyenNganh");
  const icon = document.getElementById("iconMuiTenChuyenNganh");
  if (!menu) return;

  const dangMo = !menu.classList.contains("hidden");
  const muonMo = forceState !== undefined ? forceState : !dangMo;

  if (muonMo) {
    dongDropdownTruong();
    dongDropdownSinhVien();
    dongDropdownMentor();
    dongDropdownChuongTrinh();
    dongDropdownTrangThai();
    menu.classList.remove("hidden");
    if (icon) icon.classList.add("rotate-180");
    veDropdownChuyenNganh("", true);
  } else {
    menu.classList.add("hidden");
    if (icon) icon.classList.remove("rotate-180");
  }
}

function moDropdownChuyenNganh() {
  toggleDropdownChuyenNganh(true);
}

function dongDropdownChuyenNganh() {
  toggleDropdownChuyenNganh(false);
}

function locDropdownChuyenNganh(tuKhoa) {
  const menu = document.getElementById("menuDropdownChuyenNganh");
  const icon = document.getElementById("iconMuiTenChuyenNganh");
  if (menu && menu.classList.contains("hidden")) {
    dongDropdownTruong();
    dongDropdownSinhVien();
    dongDropdownMentor();
    dongDropdownChuongTrinh();
    dongDropdownTrangThai();
    menu.classList.remove("hidden");
    if (icon) icon.classList.add("rotate-180");
  }
  veDropdownChuyenNganh(tuKhoa, false);
}

function veDropdownChuyenNganh(tuKhoa, xemTatCa = false) {
  const elCuon = document.getElementById("danhSachChuyenNganhCuon");
  if (!elCuon) return;

  const inputMaTruong = document.getElementById("maTruong");
  const maTruong = inputMaTruong ? Number(inputMaTruong.value) || 1 : 1;
  const dsGoiY = goiYChuyenNganhTheoTruong[maTruong] || danhSachNganhChung;

  const oInput = document.getElementById("chuyenNganh");
  const giaTriHienTai = oInput ? oInput.value.trim() : "";

  const key = xemTatCa ? "" : (tuKhoa || "").toLowerCase().trim();
  const dsLoc = dsGoiY.filter((n) => {
    if (!key) return true;
    return n.toLowerCase().includes(key);
  });

  let html = "";
  if (dsLoc.length > 0) {
    dsLoc.forEach((n) => {
      const isSelected = giaTriHienTai.toLowerCase() === n.toLowerCase();

      html += `
        <div onclick="chonChuyenNganhGoiY('${n}')" class="p-2 rounded-lg border transition-all flex items-center justify-between gap-2 cursor-pointer ${
          isSelected
            ? "bg-ictu-50/80 border-ictu-300 font-bold text-ictu-800"
            : "bg-white hover:bg-slate-50 border-slate-100 hover:border-slate-200 text-slate-700"
        }">
          <span class="text-xs truncate">${n}</span>
          ${isSelected ? `<span class="material-symbols-outlined text-[16px] text-ictu-600 shrink-0">check</span>` : ""}
        </div>
      `;
    });
  }

  if (key) {
    const coTrungKhop = dsGoiY.some((n) => n.toLowerCase() === key);
    if (!coTrungKhop) {
      const tenAnToan = tuKhoa.trim().replace(/"/g, "&quot;");
      const htmlThemMoi = `
        <div onclick="chonChuyenNganhTuyChon('${tenAnToan}')" class="p-2 rounded-lg border border-dashed border-amber-300 bg-amber-50/80 hover:bg-amber-100 text-amber-900 cursor-pointer flex items-center justify-between gap-2 transition-all mt-1">
          <div class="flex items-center gap-1.5 min-w-0 flex-1">
            <span class="material-symbols-outlined text-[17px] text-amber-600 shrink-0">add_circle</span>
            <span class="text-xs truncate">Thêm chuyên ngành mới: <b class="font-bold text-amber-950">${tenAnToan}</b></span>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-200/80 text-amber-800 shrink-0">Ngành mới</span>
        </div>
      `;

      if (dsLoc.length === 0) {
        html = htmlThemMoi + `
          <div class="pt-2 pb-1 px-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Các chuyên ngành chuẩn của trường (${dsGoiY.length} ngành):
          </div>
        ` + dsGoiY.map((n) => `
          <div onclick="chonChuyenNganhGoiY('${n}')" class="p-2 rounded-lg border border-slate-100 hover:border-slate-200 hover:bg-slate-50 text-slate-700 transition-all flex items-center justify-between gap-2 cursor-pointer">
            <span class="text-xs truncate">${n}</span>
          </div>
        `).join("");
      } else {
        html += htmlThemMoi;
      }
    }
  }

  if (!html) {
    html = `<div class="py-4 text-center text-xs text-slate-400">Không tìm thấy chuyên ngành gợi ý</div>`;
  }

  elCuon.innerHTML = html;
}

function chonChuyenNganhGoiY(tenNganh, dongMenu = true) {
  const oInput = document.getElementById("chuyenNganh");
  if (oInput) oInput.value = tenNganh;
  if (dongMenu) dongDropdownChuyenNganh();
}

function chonChuyenNganhTuyChon(tenMoi, dongMenu = true) {
  const oInput = document.getElementById("chuyenNganh");
  if (oInput) oInput.value = tenMoi;
  if (dongMenu) dongDropdownChuyenNganh();
}

function napDanhSachTruongTuDatabase(dsTruongDb) {
  if (!Array.isArray(dsTruongDb) || dsTruongDb.length === 0) return;
  dsTruongDb.forEach((t) => {
    if (Array.isArray(t.chuyen_nganh) && t.chuyen_nganh.length > 0) {
      goiYChuyenNganhTheoTruong[t.ma_truong] = t.chuyen_nganh;
    }
  });
  danhSachTruongChuan = dsTruongDb.map((t) => {
    let tenNgan = "ĐH";
    const tenLower = (t.ten_truong || "").toLowerCase();
    if (t.ten_truong.includes("ICTU")) tenNgan = "ICTU";
    else if (t.ten_truong.includes("HUST") || tenLower.includes("bách khoa")) tenNgan = "HUST";
    else if (t.ten_truong.includes("FPT")) tenNgan = "FPT";
    else if (t.ten_truong.includes("UIT")) tenNgan = "UIT";
    else if (t.ten_truong.includes("NEU") || tenLower.includes("kinh tế quốc dân")) tenNgan = "NEU";
    else if (t.ten_truong.includes("PTIT") || tenLower.includes("bưu chính")) tenNgan = "PTIT";
    else if (t.ten_truong.includes("UET") || tenLower.includes("công nghệ - đhqg")) tenNgan = "UET";
    else if (tenLower.includes("quốc gia")) tenNgan = "ĐHQG";
    else {
      const tu = (t.ten_truong || "").split(/\s+/);
      tenNgan = tu.map((w) => w[0]?.toUpperCase()).join("").slice(0, 4) || "ĐH";
    }

    return {
      id: t.ma_truong,
      tenNgan: tenNgan,
      ten: t.ten_truong,
      loai: t.ma_truong === 1 ? "Đối tác trọng điểm" : "Đối tác liên kết"
    };
  });
}

async function napTatCaDuLieu() {
  try {
    chonTruongChuan(1, false);
    chonChuyenNganhGoiY("Kỹ thuật phần mềm", false);

    const [phanHoiStudents, phanHoiPrograms, phanHoiMentors, phanHoiUniversities] = await Promise.all([
      fetch(duongDanApiStudents).catch(() => null),
      fetch(`${duongDanApiPrograms}?limit=100`).catch(() => null),
      fetch(duongDanApiMentors).catch(() => null),
      fetch(duongDanApiUniversities).catch(() => null)
    ]);

    if (phanHoiUniversities && phanHoiUniversities.ok) {
      const dataJson = await phanHoiUniversities.json();
      if (dataJson.data && dataJson.data.length > 0) {
        napDanhSachTruongTuDatabase(dataJson.data);
      }
    }

    if (phanHoiStudents && phanHoiStudents.ok) {
      const dataJson = await phanHoiStudents.json();
      danhSachSinhVien = dataJson.data || [];
      dienDanhSachSinhVien(danhSachSinhVien);
    } else {
      const elCuon = document.getElementById("danhSachSinhVienCuon");
      if (elCuon) elCuon.innerHTML = `<div class="p-3 text-center text-xs text-rose-500">Không thể tải danh sách sinh viên từ máy chủ</div>`;
    }

    if (phanHoiPrograms && phanHoiPrograms.ok) {
      const dataJson = await phanHoiPrograms.json();
      danhSachChuongTrinh = dataJson.items || dataJson.data || [];
      dienDanhSachChuongTrinh(danhSachChuongTrinh);
    } else {
      const elCuon = document.getElementById("danhSachChuongTrinhCuon");
      if (elCuon) elCuon.innerHTML = `<div class="p-3 text-center text-xs text-rose-500">Không thể tải danh sách chương trình từ máy chủ</div>`;
    }

    if (phanHoiMentors && phanHoiMentors.ok) {
      const dataJson = await phanHoiMentors.json();
      danhSachMentor = dataJson.data || [];
      dienDanhSachMentor(danhSachMentor);
    } else {
      const elCuon = document.getElementById("danhSachMentorCuon");
      if (elCuon) elCuon.innerHTML = `<div class="p-3 text-center text-xs text-rose-500">Không thể tải danh sách mentor từ máy chủ</div>`;
    }

    kiemTraThamSoUrl();
    taiHoSoGanDay();
  } catch (err) {
    hienThongBaoLoi("Lỗi nạp dữ liệu khởi tạo từ hệ thống máy chủ: " + (err.message || "Mất kết nối API"));
  }
}

function dienDanhSachSinhVien(danhSach) {
  danhSachSinhVien = danhSach || [];
  capNhatThongKeSinhVien();
  veDanhSachSinhVien();
}

function capNhatThongKeSinhVien() {
  const elAll = document.getElementById("demSinhVienAll");
  const elNew = document.getElementById("demSinhVienNew");
  const elAssigned = document.getElementById("demSinhVienAssigned");

  const total = danhSachSinhVien.length;
  let countNew = 0;
  let countAssigned = 0;

  danhSachSinhVien.forEach((sv) => {
    if (sv.ma_ho_so) countAssigned++;
    else countNew++;
  });

  if (elAll) elAll.textContent = total;
  if (elNew) elNew.textContent = countNew;
  if (elAssigned) elAssigned.textContent = countAssigned;
}

function toggleDropdownSinhVien(forceState) {
  const hopDropdown = document.getElementById("hopDropdownSinhVien");
  const iconMuiTen = document.getElementById("iconMuiTenSinhVien");
  if (!hopDropdown) return;

  const dangMo = !hopDropdown.classList.contains("hidden");
  const muonMo = forceState !== undefined ? forceState : !dangMo;

  if (muonMo) {
    dongDropdownMentor();
    dongDropdownChuongTrinh();
    dongDropdownTrangThai();
    hopDropdown.classList.remove("hidden");
    if (iconMuiTen) iconMuiTen.classList.add("rotate-180");
    const oSearch = document.getElementById("oTimKiemSinhVien");
    if (oSearch) setTimeout(() => oSearch.focus(), 50);
  } else {
    hopDropdown.classList.add("hidden");
    if (iconMuiTen) iconMuiTen.classList.remove("rotate-180");
  }
}

function dongDropdownSinhVien() {
  toggleDropdownSinhVien(false);
}

function locTabSinhVien(tab) {
  tabSinhVienHienTai = tab;

  const btnAll = document.getElementById("tabSinhVienAll");
  const btnNew = document.getElementById("tabSinhVienNew");
  const btnAssigned = document.getElementById("tabSinhVienAssigned");

  const activeClass = "px-2.5 py-1 rounded-lg bg-ictu-50 text-ictu-700 transition-colors font-bold cursor-pointer";
  const inactiveClass = "px-2.5 py-1 rounded-lg text-slate-500 hover:bg-slate-50 transition-colors cursor-pointer font-medium";

  if (btnAll) btnAll.className = tab === "all" ? activeClass : inactiveClass;
  if (btnNew) btnNew.className = tab === "new" ? activeClass : inactiveClass;
  if (btnAssigned) btnAssigned.className = tab === "assigned" ? activeClass : inactiveClass;

  veDanhSachSinhVien();
}

function locDanhSachSinhVien(tuKhoa) {
  tuKhoaSinhVienHienTai = (tuKhoa || "").toLowerCase().trim();
  const nutXoa = document.getElementById("nutXoaTimKiemSinhVien");
  if (nutXoa) {
    if (tuKhoaSinhVienHienTai) nutXoa.classList.remove("hidden");
    else nutXoa.classList.add("hidden");
  }
  veDanhSachSinhVien();
}

function xoaTimKiemSinhVien() {
  const oSearch = document.getElementById("oTimKiemSinhVien");
  if (oSearch) oSearch.value = "";
  locDanhSachSinhVien("");
  if (oSearch) oSearch.focus();
}

function veDanhSachSinhVien() {
  const elCuon = document.getElementById("danhSachSinhVienCuon");
  if (!elCuon) return;

  const danhSachLoc = danhSachSinhVien.filter((sv) => {
    if (tabSinhVienHienTai === "new" && sv.ma_ho_so) return false;
    if (tabSinhVienHienTai === "assigned" && !sv.ma_ho_so) return false;

    if (!tuKhoaSinhVienHienTai) return true;

    const ten = (sv.ho_ten || "").toLowerCase();
    const email = (sv.email || "").toLowerCase();
    const mssv = (sv.ma_sinh_vien || "").toLowerCase();
    const chuyenNganh = (sv.chuyen_nganh || "").toLowerCase();
    const sdt = (sv.so_dien_thoai || "").toLowerCase();
    const maId = String(sv.ma_nguoi_dung);

    return (
      ten.includes(tuKhoaSinhVienHienTai) ||
      email.includes(tuKhoaSinhVienHienTai) ||
      mssv.includes(tuKhoaSinhVienHienTai) ||
      chuyenNganh.includes(tuKhoaSinhVienHienTai) ||
      sdt.includes(tuKhoaSinhVienHienTai) ||
      maId.includes(tuKhoaSinhVienHienTai)
    );
  });

  if (danhSachLoc.length === 0) {
    elCuon.innerHTML = `
      <div class="py-8 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-2xl text-slate-300 block mb-1">person_search</span>
        Không tìm thấy sinh viên phù hợp với từ khóa "${tuKhoaSinhVienHienTai || "đang chọn"}"
      </div>
    `;
    return;
  }

  const bangMau = [
    "from-ictu-600 to-sky-500",
    "from-blue-600 to-indigo-600",
    "from-emerald-500 to-teal-600",
    "from-purple-500 to-indigo-600",
    "from-amber-500 to-orange-600"
  ];

  let html = "";
  danhSachLoc.forEach((sv, idx) => {
    const isDangChon = sinhVienDaChon && String(sinhVienDaChon.ma_nguoi_dung) === String(sv.ma_nguoi_dung);
    const parts = (sv.ho_ten || "SV").trim().split(/\s+/);
    const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();
    const mauGradient = bangMau[idx % bangMau.length];

    let badgeStatus = "";
    if (sv.ma_ho_so) {
      badgeStatus = `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">Hồ sơ #${sv.ma_ho_so}</span>`;
    } else {
      badgeStatus = `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-50 text-sky-700 border border-sky-200 shrink-0">Tài khoản mới</span>`;
    }

    let classThe = "p-2.5 rounded-xl border transition-all flex items-center justify-between gap-3 text-left cursor-pointer ";
    if (isDangChon) {
      classThe += "bg-ictu-50/70 border-ictu-300 ring-1 ring-ictu-400/30 ";
    } else {
      classThe += "bg-white hover:bg-slate-50 border-slate-200/90 hover:border-slate-300 shadow-2xs ";
    }

    html += `
      <div onclick="chonSinhVien(${sv.ma_nguoi_dung})" class="${classThe}">
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr ${mauGradient} text-white font-bold text-xs flex items-center justify-center shadow-2xs shrink-0">
            ${initials}
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="font-bold text-slate-800 text-xs truncate">${sv.ho_ten}</span>
              ${sv.ma_sinh_vien ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">${sv.ma_sinh_vien}</span>` : ""}
              <span class="text-[10px] text-slate-500 truncate">• ${sv.chuyen_nganh || "Kỹ thuật phần mềm"}</span>
            </div>
            <div class="flex items-center gap-2 text-[11px] text-slate-500 truncate mt-0.5">
              <span class="truncate">${sv.email}</span>
              ${sv.so_dien_thoai ? `<span class="text-slate-300">|</span><span>${sv.so_dien_thoai}</span>` : ""}
            </div>
          </div>
        </div>
        <div class="shrink-0 flex items-center gap-2">
          ${badgeStatus}
          ${isDangChon ? `<span class="material-symbols-outlined text-[18px] text-ictu-600">check</span>` : ""}
        </div>
      </div>
    `;
  });

  elCuon.innerHTML = html;
}

function chonSinhVien(maNguoiDung) {
  const sv = danhSachSinhVien.find((x) => String(x.ma_nguoi_dung) === String(maNguoiDung));
  if (!sv) return;

  sinhVienDaChon = sv;
  const inputEl = document.getElementById("chonSinhVien");
  if (inputEl) inputEl.value = sv.ma_nguoi_dung;

  const hienThiEl = document.getElementById("hienThiSinhVienDaChon");
  const nutXoa = document.getElementById("nutXoaChonSinhVien");

  const parts = (sv.ho_ten || "SV").trim().split(/\s+/);
  const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();

  if (hienThiEl) {
    hienThiEl.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-ictu-600 to-sky-500 text-white font-bold text-xs flex items-center justify-center shadow-xs shrink-0">
        ${initials}
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-900 text-sm truncate">${sv.ho_ten}</span>
          ${sv.ma_sinh_vien ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700">${sv.ma_sinh_vien}</span>` : ""}
          <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold ${sv.ma_ho_so ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-sky-50 text-sky-700 border border-sky-200"} shrink-0">
            ${sv.ma_ho_so ? `Hồ sơ #${sv.ma_ho_so}` : "Tài khoản mới"}
          </span>
        </div>
        <div class="text-[11px] text-slate-500 truncate">
          ${sv.email} • ${sv.chuyen_nganh || "Kỹ thuật phần mềm"}
        </div>
      </div>
    `;
  }

  if (nutXoa) nutXoa.classList.remove("hidden");
  dongDropdownSinhVien();
  veDanhSachSinhVien();
  xuLyChonSinhVien(maNguoiDung);
}

function boChonSinhVien() {
  sinhVienDaChon = null;
  const inputEl = document.getElementById("chonSinhVien");
  if (inputEl) inputEl.value = "";

  const hienThiEl = document.getElementById("hienThiSinhVienDaChon");
  const nutXoa = document.getElementById("nutXoaChonSinhVien");

  if (hienThiEl) {
    hienThiEl.innerHTML = `
      <span class="w-8 h-8 rounded-lg bg-slate-100 text-slate-400 flex items-center justify-center shrink-0 group-hover:text-ictu-600 transition-colors">
        <span class="material-symbols-outlined text-[19px]">person_search</span>
      </span>
      <span class="text-sm text-slate-400 font-medium truncate">
        -- Nhấp để tìm kiếm sinh viên theo Tên, MSSV, Email, Ngành... --
      </span>
    `;
  }

  if (nutXoa) nutXoa.classList.add("hidden");
  veDanhSachSinhVien();
  xuLyChonSinhVien(null);
}

function xuLyChonSinhVien(maNguoiDung) {
  const theInfo = document.getElementById("theThongTinSinhVienChon");
  const badgeTrangThai = document.getElementById("badgeTrangThaiSinhVien");
  const nutLuu = document.getElementById("nutLuuHoSo");

  if (!maNguoiDung) {
    if (theInfo) theInfo.classList.add("hidden");
    if (badgeTrangThai) {
      badgeTrangThai.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200";
      badgeTrangThai.innerHTML = `<span class="w-2 h-2 rounded-full bg-slate-400"></span> Chưa chọn sinh viên`;
    }
    if (nutLuu) {
      nutLuu.innerHTML = `<span class="material-symbols-outlined text-[19px]">assignment_turned_in</span> <span>Phân công &amp; Lưu hồ sơ thực tập</span>`;
    }
    maHoSoHienTai = null;
    boChonMentor();
    boChonChuongTrinh();
    chonTruongChuan(1, false);
    const oChuyenNganh = document.getElementById("chuyenNganh");
    if (oChuyenNganh) oChuyenNganh.value = "Kỹ thuật phần mềm";
    return;
  }

  const sv = danhSachSinhVien.find((x) => String(x.ma_nguoi_dung) === String(maNguoiDung));
  if (!sv) return;

  maHoSoHienTai = sv.ma_ho_so || null;

  if (theInfo) {
    theInfo.classList.remove("hidden");
    const elTen = document.getElementById("tenSinhVienChon");
    const elMssv = document.getElementById("mssvSinhVienChon");
    const elEmail = document.getElementById("emailSinhVienChon");
    const elChuyenNganh = document.getElementById("chuyenNganhSinhVienChon");
    const elAvatar = document.getElementById("avatarSinhVienChon");
    const elBadgeHoSo = document.getElementById("badgeChiTietHoSo");

    if (elTen) elTen.textContent = sv.ho_ten || "Sinh viên";
    if (elMssv) elMssv.textContent = sv.ma_sinh_vien || `ID #${sv.ma_nguoi_dung}`;
    if (elEmail) elEmail.textContent = sv.email || "";
    if (elChuyenNganh) elChuyenNganh.textContent = sv.chuyen_nganh || "Kỹ thuật phần mềm";

    if (elAvatar && sv.ho_ten) {
      const parts = sv.ho_ten.trim().split(/\s+/);
      elAvatar.textContent = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();
    }

    if (elBadgeHoSo) {
      if (sv.ma_ho_so) {
        elBadgeHoSo.innerHTML = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Đã có hồ sơ #${sv.ma_ho_so}</span>`;
      } else {
        elBadgeHoSo.innerHTML = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">Tài khoản mới</span>`;
      }
    }
  }

  if (badgeTrangThai) {
    if (sv.ma_ho_so) {
      badgeTrangThai.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200";
      badgeTrangThai.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span> Đã có hồ sơ #${sv.ma_ho_so}`;
    } else {
      badgeTrangThai.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200";
      badgeTrangThai.innerHTML = `<span class="w-2 h-2 rounded-full bg-sky-500"></span> Sẵn sàng phân công`;
    }
  }

  const oHoTen = document.getElementById("hoTen");
  const oEmail = document.getElementById("email");
  const oSdt = document.getElementById("soDienThoai");
  const oNgayBatDau = document.getElementById("ngayBatDau");
  const oNgayKetThuc = document.getElementById("ngayKetThuc");

  if (oHoTen && sv.ho_ten) oHoTen.value = sv.ho_ten;
  if (oEmail && sv.email) oEmail.value = sv.email;
  if (oSdt) oSdt.value = sv.so_dien_thoai || "";

  if (sv.ten_truong || sv.ma_truong) {
    let truongTim = null;
    if (sv.ma_truong) {
      truongTim = danhSachTruongChuan.find((t) => t.id === Number(sv.ma_truong));
    }
    if (!truongTim && sv.ten_truong) {
      truongTim = danhSachTruongChuan.find((t) =>
        t.ten.toLowerCase().includes(sv.ten_truong.toLowerCase()) ||
        sv.ten_truong.toLowerCase().includes(t.tenNgan.toLowerCase())
      );
    }
    if (truongTim) {
      chonTruongChuan(truongTim.id, false);
    } else if (sv.ten_truong) {
      chonTruongTuyChon(sv.ten_truong, false);
    }
  } else {
    chonTruongChuan(1, false);
  }

  const oChuyenNganh = document.getElementById("chuyenNganh");
  if (oChuyenNganh) {
    oChuyenNganh.value = sv.chuyen_nganh || "Kỹ thuật phần mềm";
  }

  if (sv.ma_chuong_trinh) {
    chonChuongTrinh(sv.ma_chuong_trinh, false);
  } else {
    boChonChuongTrinh();
  }

  if (sv.ma_mentor) {
    chonMentor(sv.ma_mentor, true);
  } else {
    boChonMentor();
  }

  if (sv.trang_thai_thuc_tap) {
    if (sv.trang_thai_thuc_tap === "DangThucTap") chonTrangThai("Đang thực tập");
    else if (sv.trang_thai_thuc_tap === "HoanThanh") chonTrangThai("Đã hoàn thành");
    else if (sv.trang_thai_thuc_tap === "ThoiHoc") chonTrangThai("Tạm dừng");
    else if (sv.trang_thai_xet_duyet === "ChoDuyet") chonTrangThai("Chờ duyệt");
  }

  if (oNgayBatDau && sv.ngay_bat_dau) oNgayBatDau.value = sv.ngay_bat_dau;
  if (oNgayKetThuc && sv.ngay_ket_thuc) oNgayKetThuc.value = sv.ngay_ket_thuc;

  if (nutLuu) {
    if (sv.ma_ho_so) {
      nutLuu.innerHTML = `<span class="material-symbols-outlined text-[19px]">sync</span> <span>Cập nhật hồ sơ thực tập (#${sv.ma_ho_so})</span>`;
    } else {
      nutLuu.innerHTML = `<span class="material-symbols-outlined text-[19px]">assignment_turned_in</span> <span>Phân công &amp; Lưu hồ sơ thực tập</span>`;
    }
  }
}

function dienDanhSachChuongTrinh(danhSach) {
  danhSachChuongTrinh = danhSach || [];
  capNhatThongKeChuongTrinh();
  veDanhSachChuongTrinh();
}

function capNhatThongKeChuongTrinh() {
  const elAll = document.getElementById("demChuongTrinhAll");
  const elAvailable = document.getElementById("demChuongTrinhAvailable");
  const elFull = document.getElementById("demChuongTrinhFull");

  const total = danhSachChuongTrinh.length;
  let countAvailable = 0;
  let countFull = 0;

  danhSachChuongTrinh.forEach((p) => {
    const sl = p.so_luong_sinh_vien || 0;
    const chiTieu = p.chi_tieu_sinh_vien || 50;
    if (sl >= chiTieu) countFull++;
    else countAvailable++;
  });

  if (elAll) elAll.textContent = total;
  if (elAvailable) elAvailable.textContent = countAvailable;
  if (elFull) elFull.textContent = countFull;
}

function toggleDropdownChuongTrinh(forceState) {
  const hopDropdown = document.getElementById("hopDropdownChuongTrinh");
  const iconMuiTen = document.getElementById("iconMuiTenChuongTrinh");
  if (!hopDropdown) return;

  const dangMo = !hopDropdown.classList.contains("hidden");
  const muonMo = forceState !== undefined ? forceState : !dangMo;

  if (muonMo) {
    dongDropdownSinhVien();
    dongDropdownMentor();
    dongDropdownTrangThai();
    hopDropdown.classList.remove("hidden");
    if (iconMuiTen) iconMuiTen.classList.add("rotate-180");
    const oSearch = document.getElementById("oTimKiemChuongTrinh");
    if (oSearch) setTimeout(() => oSearch.focus(), 50);
  } else {
    hopDropdown.classList.add("hidden");
    if (iconMuiTen) iconMuiTen.classList.remove("rotate-180");
  }
}

function dongDropdownChuongTrinh() {
  toggleDropdownChuongTrinh(false);
}

function locTabChuongTrinh(tab) {
  tabChuongTrinhHienTai = tab;

  const btnAll = document.getElementById("tabChuongTrinhAll");
  const btnAvailable = document.getElementById("tabChuongTrinhAvailable");
  const btnFull = document.getElementById("tabChuongTrinhFull");

  const activeClass = "px-2.5 py-1 rounded-lg bg-ictu-50 text-ictu-700 transition-colors font-bold cursor-pointer";
  const inactiveClass = "px-2.5 py-1 rounded-lg text-slate-500 hover:bg-slate-50 transition-colors cursor-pointer font-medium";

  if (btnAll) btnAll.className = tab === "all" ? activeClass : inactiveClass;
  if (btnAvailable) btnAvailable.className = tab === "available" ? activeClass : inactiveClass;
  if (btnFull) btnFull.className = tab === "full" ? activeClass : inactiveClass;

  veDanhSachChuongTrinh();
}

function locDanhSachChuongTrinh(tuKhoa) {
  tuKhoaChuongTrinhHienTai = (tuKhoa || "").toLowerCase().trim();
  const nutXoa = document.getElementById("nutXoaTimKiemChuongTrinh");
  if (nutXoa) {
    if (tuKhoaChuongTrinhHienTai) nutXoa.classList.remove("hidden");
    else nutXoa.classList.add("hidden");
  }
  veDanhSachChuongTrinh();
}

function xoaTimKiemChuongTrinh() {
  const oSearch = document.getElementById("oTimKiemChuongTrinh");
  if (oSearch) oSearch.value = "";
  locDanhSachChuongTrinh("");
  if (oSearch) oSearch.focus();
}

function veDanhSachChuongTrinh() {
  const elCuon = document.getElementById("danhSachChuongTrinhCuon");
  if (!elCuon) return;

  const danhSachLoc = danhSachChuongTrinh.filter((p) => {
    const sl = p.so_luong_sinh_vien || 0;
    const chiTieu = p.chi_tieu_sinh_vien || 50;
    const isFull = sl >= chiTieu;

    if (tabChuongTrinhHienTai === "available" && isFull) return false;
    if (tabChuongTrinhHienTai === "full" && !isFull) return false;

    if (!tuKhoaChuongTrinhHienTai) return true;

    const ten = (p.ten_chuong_trinh || "").toLowerCase();
    const phongBan = (p.ten_phong_ban || "").toLowerCase();
    const moTa = (p.mo_ta || "").toLowerCase();
    const maId = String(p.ma_chuong_trinh);

    return (
      ten.includes(tuKhoaChuongTrinhHienTai) ||
      phongBan.includes(tuKhoaChuongTrinhHienTai) ||
      moTa.includes(tuKhoaChuongTrinhHienTai) ||
      maId.includes(tuKhoaChuongTrinhHienTai)
    );
  });

  if (danhSachLoc.length === 0) {
    elCuon.innerHTML = `
      <div class="py-8 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-2xl text-slate-300 block mb-1">search_off</span>
        Không tìm thấy chương trình thực tập phù hợp với từ khóa "${tuKhoaChuongTrinhHienTai || "đang chọn"}"
      </div>
    `;
    return;
  }

  let html = "";
  danhSachLoc.forEach((p) => {
    const sl = p.so_luong_sinh_vien || 0;
    const chiTieu = p.chi_tieu_sinh_vien || 50;
    const isFull = sl >= chiTieu;
    const isDangChon = chuongTrinhDaChon && String(chuongTrinhDaChon.ma_chuong_trinh) === String(p.ma_chuong_trinh);

    const thoiGian =
      p.ngay_bat_dau && p.ngay_ket_thuc
        ? `${dinhDangNgay(p.ngay_bat_dau)} - ${dinhDangNgay(p.ngay_ket_thuc)} (${p.thoi_luong_tuan || 12} tuần)`
        : "Học kỳ 2026 - 2027";

    let badgeQuota = "";
    if (isFull) {
      badgeQuota = `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 shrink-0"><span class="material-symbols-outlined text-[13px]">lock</span> Đã kín (${sl}/${chiTieu} SV)</span>`;
    } else {
      badgeQuota = `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">Còn ${chiTieu - sl} suất (${sl}/${chiTieu} SV)</span>`;
    }

    let classThe = "p-2.5 rounded-xl border transition-all flex items-center justify-between gap-3 text-left ";
    if (isDangChon) {
      classThe += "bg-ictu-50/70 border-ictu-300 ring-1 ring-ictu-400/30 ";
    } else if (isFull) {
      classThe += "bg-slate-50/70 border-slate-200/70 opacity-60 cursor-not-allowed ";
    } else {
      classThe += "bg-white hover:bg-slate-50 border-slate-200/90 hover:border-slate-300 cursor-pointer shadow-2xs ";
    }

    const clickAction = isFull
      ? `canhBaoChuongTrinhKinChiTieu('${p.ten_chuong_trinh}', ${sl}, ${chiTieu})`
      : `chonChuongTrinh(${p.ma_chuong_trinh})`;

    html += `
      <div onclick="${clickAction}" class="${classThe}">
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-ictu-600 to-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow-2xs shrink-0">
            <span class="material-symbols-outlined text-[18px]">workspace_premium</span>
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="font-bold text-slate-800 text-xs truncate">${p.ten_chuong_trinh}</span>
              ${p.ten_phong_ban ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-ictu-50 text-ictu-700 border border-ictu-100">${p.ten_phong_ban}</span>` : ""}
              <span class="text-[10px] text-slate-400">• ${p.trang_thai || "Đang diễn ra"}</span>
            </div>
            <div class="text-[11px] text-slate-500 truncate mt-0.5">
              ${thoiGian}
            </div>
          </div>
        </div>
        <div class="shrink-0 flex items-center gap-2">
          ${badgeQuota}
          ${isDangChon ? `<span class="material-symbols-outlined text-[18px] text-ictu-600">check</span>` : ""}
        </div>
      </div>
    `;
  });

  elCuon.innerHTML = html;
}

function chonChuongTrinh(maChuongTrinh, tuDongDienNgay = true) {
  const p = danhSachChuongTrinh.find((x) => String(x.ma_chuong_trinh) === String(maChuongTrinh));
  if (!p) return;

  const sl = p.so_luong_sinh_vien || 0;
  const chiTieu = p.chi_tieu_sinh_vien || 50;

  if (sl >= chiTieu) {
    canhBaoChuongTrinhKinChiTieu(p.ten_chuong_trinh, sl, chiTieu);
    return;
  }

  chuongTrinhDaChon = p;
  const inputEl = document.getElementById("maChuongTrinh");
  if (inputEl) inputEl.value = p.ma_chuong_trinh;

  const hienThiEl = document.getElementById("hienThiChuongTrinhDaChon");
  const nutXoa = document.getElementById("nutXoaChonChuongTrinh");

  const thoiGian =
    p.ngay_bat_dau && p.ngay_ket_thuc
      ? `${dinhDangNgay(p.ngay_bat_dau)} - ${dinhDangNgay(p.ngay_ket_thuc)} (${p.thoi_luong_tuan || 12} tuần)`
      : "Kỳ thực tập 2026 - 2027";

  if (hienThiEl) {
    hienThiEl.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-ictu-600 to-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow-xs shrink-0">
        <span class="material-symbols-outlined text-[18px]">workspace_premium</span>
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-900 text-sm truncate">${p.ten_chuong_trinh}</span>
          ${p.ten_phong_ban ? `<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-ictu-50 text-ictu-700 border border-ictu-100">${p.ten_phong_ban}</span>` : ""}
          <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
            ${sl}/${chiTieu} SV
          </span>
        </div>
        <div class="text-[11px] text-slate-500 truncate">
          ${thoiGian}
        </div>
      </div>
    `;
  }

  if (nutXoa) nutXoa.classList.remove("hidden");
  dongDropdownChuongTrinh();
  veDanhSachChuongTrinh();
  xuLyChonChuongTrinh(maChuongTrinh, tuDongDienNgay);
}

function boChonChuongTrinh() {
  chuongTrinhDaChon = null;
  const inputEl = document.getElementById("maChuongTrinh");
  if (inputEl) inputEl.value = "";

  const hienThiEl = document.getElementById("hienThiChuongTrinhDaChon");
  const nutXoa = document.getElementById("nutXoaChonChuongTrinh");

  if (hienThiEl) {
    hienThiEl.innerHTML = `
      <span class="w-8 h-8 rounded-lg bg-slate-100 text-slate-400 flex items-center justify-center shrink-0 group-hover:text-ictu-600 transition-colors">
        <span class="material-symbols-outlined text-[19px]">workspace_premium</span>
      </span>
      <span class="text-sm text-slate-400 font-medium truncate">
        -- Nhấp để tìm kiếm &amp; chọn chương trình thực tập tiếp nhận --
      </span>
    `;
  }

  if (nutXoa) nutXoa.classList.add("hidden");
  veDanhSachChuongTrinh();

  const nutLuu = document.getElementById("nutLuuHoSo");
  if (nutLuu) nutLuu.disabled = false;
}

function xuLyChonChuongTrinh(maChuongTrinh, tuDongDienNgay = true) {
  if (!maChuongTrinh) return;
  const p = danhSachChuongTrinh.find((x) => String(x.ma_chuong_trinh) === String(maChuongTrinh));
  if (!p) return;

  const sl = p.so_luong_sinh_vien || 0;
  const chiTieu = p.chi_tieu_sinh_vien || 50;
  const nutLuu = document.getElementById("nutLuuHoSo");

  if (sl >= chiTieu) {
    hienThongBaoLoi(`Chương trình thực tập "${p.ten_chuong_trinh}" đã đủ chỉ tiêu sinh viên (${sl}/${chiTieu}), không thể tiếp nhận thêm!`);
    if (nutLuu) nutLuu.disabled = true;
    return;
  } else {
    if (nutLuu) nutLuu.disabled = false;
  }

  if (tuDongDienNgay) {
    const oNgayBatDau = document.getElementById("ngayBatDau");
    const oNgayKetThuc = document.getElementById("ngayKetThuc");
    if (oNgayBatDau && p.ngay_bat_dau) {
      oNgayBatDau.value = p.ngay_bat_dau.slice(0, 10);
    }
    if (oNgayKetThuc && p.ngay_ket_thuc) {
      oNgayKetThuc.value = p.ngay_ket_thuc.slice(0, 10);
    }
  }
}

function canhBaoChuongTrinhKinChiTieu(ten, cur, max) {
  hienThongBaoLoi(`Chương trình thực tập <b>${ten}</b> đã đủ chỉ tiêu tiếp nhận (<b>${cur}/${max} sinh viên</b>). Không thể tiếp nhận thêm sinh viên vào chương trình này!`);
}

function dienDanhSachMentor(danhSach) {
  danhSachMentor = danhSach || [];
  capNhatThongKeMentor();
  veDanhSachMentor();
}

function capNhatThongKeMentor() {
  const elAll = document.getElementById("demMentorAll");
  const elAvailable = document.getElementById("demMentorAvailable");
  const elFull = document.getElementById("demMentorFull");

  const total = danhSachMentor.length;
  let available = 0;
  let full = 0;

  danhSachMentor.forEach((m) => {
    const sl = m.so_sinh_vien_huong_dan || 0;
    const maxHd = m.chi_tieu_huong_dan || 5;
    if (sl >= maxHd || m.da_du_chi_tieu) {
      full++;
    } else {
      available++;
    }
  });

  if (elAll) elAll.textContent = total;
  if (elAvailable) elAvailable.textContent = available;
  if (elFull) elFull.textContent = full;
}

function toggleDropdownMentor(forceState) {
  const hopDropdown = document.getElementById("hopDropdownMentor");
  const iconMuiTen = document.getElementById("iconMuiTenMentor");
  if (!hopDropdown) return;

  const dangMo = !hopDropdown.classList.contains("hidden");
  const muonMo = forceState !== undefined ? forceState : !dangMo;

  if (muonMo) {
    dongDropdownSinhVien();
    dongDropdownChuongTrinh();
    dongDropdownTrangThai();
    hopDropdown.classList.remove("hidden");
    if (iconMuiTen) iconMuiTen.classList.add("rotate-180");
    const oSearch = document.getElementById("oTimKiemMentor");
    if (oSearch) setTimeout(() => oSearch.focus(), 50);
  } else {
    hopDropdown.classList.add("hidden");
    if (iconMuiTen) iconMuiTen.classList.remove("rotate-180");
  }
}

function dongDropdownMentor() {
  toggleDropdownMentor(false);
}

function locTabMentor(tab) {
  tabMentorHienTai = tab;

  const btnAll = document.getElementById("tabMentorAll");
  const btnAvailable = document.getElementById("tabMentorAvailable");
  const btnFull = document.getElementById("tabMentorFull");

  const activeClass = "px-2.5 py-1 rounded-lg bg-ictu-50 text-ictu-700 transition-colors font-bold cursor-pointer";
  const inactiveClass = "px-2.5 py-1 rounded-lg text-slate-500 hover:bg-slate-50 transition-colors cursor-pointer font-medium";

  if (btnAll) btnAll.className = tab === "all" ? activeClass : inactiveClass;
  if (btnAvailable) btnAvailable.className = tab === "available" ? activeClass : inactiveClass;
  if (btnFull) btnFull.className = tab === "full" ? activeClass : inactiveClass;

  veDanhSachMentor();
}

function locDanhSachMentor(tuKhoa) {
  tuKhoaMentorHienTai = (tuKhoa || "").toLowerCase().trim();
  const nutXoa = document.getElementById("nutXoaTimKiemMentor");
  if (nutXoa) {
    if (tuKhoaMentorHienTai) nutXoa.classList.remove("hidden");
    else nutXoa.classList.add("hidden");
  }
  veDanhSachMentor();
}

function xoaTimKiemMentor() {
  const oSearch = document.getElementById("oTimKiemMentor");
  if (oSearch) oSearch.value = "";
  locDanhSachMentor("");
  if (oSearch) oSearch.focus();
}

function veDanhSachMentor() {
  const elCuon = document.getElementById("danhSachMentorCuon");
  if (!elCuon) return;

  const danhSachLoc = danhSachMentor.filter((m) => {
    const sl = m.so_sinh_vien_huong_dan || 0;
    const maxHd = m.chi_tieu_huong_dan || 5;
    const isFull = sl >= maxHd || m.da_du_chi_tieu;

    if (tabMentorHienTai === "available" && isFull) return false;
    if (tabMentorHienTai === "full" && !isFull) return false;

    if (!tuKhoaMentorHienTai) return true;

    const ten = (m.ho_ten || "").toLowerCase();
    const email = (m.email || "").toLowerCase();
    const sdt = (m.so_dien_thoai || "").toLowerCase();
    const chucVu = (m.chuc_vu || "").toLowerCase();
    const maId = String(m.ma_nguoi_dung);

    return (
      ten.includes(tuKhoaMentorHienTai) ||
      email.includes(tuKhoaMentorHienTai) ||
      sdt.includes(tuKhoaMentorHienTai) ||
      chucVu.includes(tuKhoaMentorHienTai) ||
      maId.includes(tuKhoaMentorHienTai)
    );
  });

  if (danhSachLoc.length === 0) {
    elCuon.innerHTML = `
      <div class="py-8 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-2xl text-slate-300 block mb-1">person_search</span>
        Không tìm thấy Mentor phù hợp với từ khóa "${tuKhoaMentorHienTai || "đang chọn"}"
      </div>
    `;
    return;
  }

  const bangMau = [
    "from-blue-600 to-indigo-600",
    "from-sky-500 to-ictu-600",
    "from-emerald-500 to-teal-600",
    "from-purple-500 to-indigo-600",
    "from-amber-500 to-orange-600"
  ];

  let html = "";
  danhSachLoc.forEach((m, idx) => {
    const sl = m.so_sinh_vien_huong_dan || 0;
    const maxHd = m.chi_tieu_huong_dan || 5;
    const isFull = sl >= maxHd || m.da_du_chi_tieu;
    const isDangChon = mentorDaChon && String(mentorDaChon.ma_nguoi_dung) === String(m.ma_nguoi_dung);

    const parts = (m.ho_ten || "M").trim().split(/\s+/);
    const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();
    const mauGradient = bangMau[idx % bangMau.length];

    let badgeQuota = "";
    if (isFull) {
      badgeQuota = `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 shrink-0"><span class="material-symbols-outlined text-[13px]">lock</span> Đã kín (${sl}/${maxHd})</span>`;
    } else if (sl === 0) {
      badgeQuota = `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">Còn 5 chỗ (0/${maxHd})</span>`;
    } else {
      badgeQuota = `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-50 text-sky-700 border border-sky-200 shrink-0">Còn ${maxHd - sl} chỗ (${sl}/${maxHd})</span>`;
    }

    let classThe = "p-2.5 rounded-xl border transition-all flex items-center justify-between gap-3 text-left ";
    if (isDangChon) {
      classThe += "bg-ictu-50/70 border-ictu-300 ring-1 ring-ictu-400/30 ";
    } else if (isFull) {
      classThe += "bg-slate-50/70 border-slate-200/70 opacity-60 cursor-not-allowed ";
    } else {
      classThe += "bg-white hover:bg-slate-50 border-slate-200/90 hover:border-slate-300 cursor-pointer shadow-2xs ";
    }

    const clickAction = isFull
      ? `canhBaoMentorKinChiTieu('${m.ho_ten}', ${sl}, ${maxHd})`
      : `chonMentor(${m.ma_nguoi_dung})`;

    html += `
      <div onclick="${clickAction}" class="${classThe}">
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr ${mauGradient} text-white font-bold text-xs flex items-center justify-center shadow-2xs shrink-0">
            ${initials}
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="font-bold text-slate-800 text-xs truncate">${m.ho_ten}</span>
              <span class="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">#${m.ma_nguoi_dung}</span>
              <span class="text-[10px] font-semibold text-slate-500">• ${m.chuc_vu}</span>
            </div>
            <div class="flex items-center gap-2 text-[11px] text-slate-500 truncate mt-0.5">
              <span class="truncate">${m.email}</span>
              ${m.so_dien_thoai ? `<span class="text-slate-300">|</span><span>${m.so_dien_thoai}</span>` : ""}
            </div>
          </div>
        </div>
        <div class="shrink-0 flex items-center gap-2">
          ${badgeQuota}
          ${isDangChon ? `<span class="material-symbols-outlined text-[18px] text-ictu-600">check</span>` : ""}
        </div>
      </div>
    `;
  });

  elCuon.innerHTML = html;
}

function chonMentor(maNguoiDung, boQuaKiemTra = false) {
  const m = danhSachMentor.find((x) => String(x.ma_nguoi_dung) === String(maNguoiDung));
  if (!m) return;

  const sl = m.so_sinh_vien_huong_dan || 0;
  const maxHd = m.chi_tieu_huong_dan || 5;

  if (!boQuaKiemTra && (sl >= maxHd || m.da_du_chi_tieu)) {
    canhBaoMentorKinChiTieu(m.ho_ten, sl, maxHd);
    return;
  }

  mentorDaChon = m;
  const inputMaMentor = document.getElementById("maMentor");
  if (inputMaMentor) inputMaMentor.value = m.ma_nguoi_dung;

  const hienThiEl = document.getElementById("hienThiMentorDaChon");
  const nutXoa = document.getElementById("nutXoaChonMentor");

  const parts = (m.ho_ten || "M").trim().split(/\s+/);
  const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();

  if (hienThiEl) {
    hienThiEl.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-ictu-600 to-sky-500 text-white font-bold text-xs flex items-center justify-center shadow-xs shrink-0">
        ${initials}
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-900 text-sm truncate">${m.ho_ten}</span>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
            ${sl}/${maxHd} SV
          </span>
        </div>
        <div class="text-[11px] text-slate-500 truncate">
          ${m.email} • ${m.chuc_vu}
        </div>
      </div>
    `;
  }

  if (nutXoa) nutXoa.classList.remove("hidden");
  dongDropdownMentor();
  veDanhSachMentor();
}

function boChonMentor() {
  mentorDaChon = null;
  const inputMaMentor = document.getElementById("maMentor");
  if (inputMaMentor) inputMaMentor.value = "";

  const hienThiEl = document.getElementById("hienThiMentorDaChon");
  const nutXoa = document.getElementById("nutXoaChonMentor");

  if (hienThiEl) {
    hienThiEl.innerHTML = `
      <span class="w-8 h-8 rounded-lg bg-slate-100 text-slate-400 flex items-center justify-center shrink-0 group-hover:text-ictu-600 transition-colors">
        <span class="material-symbols-outlined text-[19px]">supervisor_account</span>
      </span>
      <span class="text-sm text-slate-400 font-medium truncate">
        -- Nhấp để tìm kiếm &amp; chọn Mentor phụ trách --
      </span>
    `;
  }

  if (nutXoa) nutXoa.classList.add("hidden");
  veDanhSachMentor();
}

function canhBaoMentorKinChiTieu(ten, cur, max) {
  hienThongBaoLoi(`Mentor <b>${ten}</b> đã nhận đủ chỉ tiêu hướng dẫn (<b>${cur}/${max} sinh viên</b>). Theo quy chế thực tập, vui lòng phân công mentor khác!`);
}

function toggleDropdownTrangThai(forceState) {
  const hopDropdown = document.getElementById("hopDropdownTrangThai");
  const iconMuiTen = document.getElementById("iconMuiTenTrangThai");
  if (!hopDropdown) return;

  const dangMo = !hopDropdown.classList.contains("hidden");
  const muonMo = forceState !== undefined ? forceState : !dangMo;

  if (muonMo) {
    dongDropdownSinhVien();
    dongDropdownChuongTrinh();
    dongDropdownMentor();
    hopDropdown.classList.remove("hidden");
    if (iconMuiTen) iconMuiTen.classList.add("rotate-180");
  } else {
    hopDropdown.classList.add("hidden");
    if (iconMuiTen) iconMuiTen.classList.remove("rotate-180");
  }
}

function dongDropdownTrangThai() {
  toggleDropdownTrangThai(false);
}

function chonTrangThai(tenTrangThai) {
  trangThaiHienTai = tenTrangThai;
  const inputEl = document.getElementById("trangThai");
  if (inputEl) inputEl.value = tenTrangThai;

  const hienThiEl = document.getElementById("hienThiTrangThaiDaChon");
  if (hienThiEl) {
    let mauDot = "bg-blue-500";
    let moTa = "• Tiếp nhận chính thức";
    if (tenTrangThai === "Chờ duyệt") {
      mauDot = "bg-amber-500";
      moTa = "• Đang chờ thẩm định";
    } else if (tenTrangThai === "Đã hoàn thành") {
      mauDot = "bg-emerald-500";
      moTa = "• Hoàn tất kỳ thực tập";
    } else if (tenTrangThai === "Tạm dừng") {
      mauDot = "bg-slate-400";
      moTa = "• Tạm hoãn / Thôi học";
    }

    hienThiEl.innerHTML = `
      <span class="w-2.5 h-2.5 rounded-full ${mauDot} shrink-0"></span>
      <span class="text-xs font-bold text-slate-800">${tenTrangThai}</span>
      <span class="text-[11px] text-slate-400 font-medium truncate">${moTa}</span>
    `;
  }

  const checkDangThucTap = document.getElementById("checkTrangThaiDangThucTap");
  const checkChoDuyet = document.getElementById("checkTrangThaiChoDuyet");
  const checkDaHoanThanh = document.getElementById("checkTrangThaiDaHoanThanh");
  const checkTamDung = document.getElementById("checkTrangThaiTamDung");

  if (checkDangThucTap) checkDangThucTap.className = tenTrangThai === "Đang thực tập" ? "material-symbols-outlined text-[18px] text-ictu-600" : "hidden";
  if (checkChoDuyet) checkChoDuyet.className = tenTrangThai === "Chờ duyệt" ? "material-symbols-outlined text-[18px] text-ictu-600" : "hidden";
  if (checkDaHoanThanh) checkDaHoanThanh.className = tenTrangThai === "Đã hoàn thành" ? "material-symbols-outlined text-[18px] text-ictu-600" : "hidden";
  if (checkTamDung) checkTamDung.className = tenTrangThai === "Tạm dừng" ? "material-symbols-outlined text-[18px] text-ictu-600" : "hidden";

  dongDropdownTrangThai();
}

async function handleLuuHoSo() {
  const inputSinhVien = document.getElementById("chonSinhVien");
  const maNguoiDungChon = inputSinhVien ? inputSinhVien.value : null;

  if (!maNguoiDungChon) {
    hienThongBaoLoi("Vui lòng chọn tài khoản sinh viên từ danh sách cần phân công!");
    toggleDropdownSinhVien(true);
    return;
  }

  const inputChuongTrinh = document.getElementById("maChuongTrinh");
  const maChuongTrinh = inputChuongTrinh ? inputChuongTrinh.value : null;
  if (!maChuongTrinh) {
    hienThongBaoLoi("Vui lòng chọn chương trình thực tập phân công cho sinh viên!");
    toggleDropdownChuongTrinh(true);
    return;
  }

  const progObj = danhSachChuongTrinh.find((x) => String(x.ma_chuong_trinh) === String(maChuongTrinh));
  if (progObj && (progObj.so_luong_sinh_vien || 0) >= (progObj.chi_tieu_sinh_vien || 50)) {
    hienThongBaoLoi(`Chương trình thực tập "${progObj.ten_chuong_trinh}" đã đủ chỉ tiêu sinh viên (${progObj.so_luong_sinh_vien}/${progObj.chi_tieu_sinh_vien}), không thể tiếp nhận thêm!`);
    return;
  }

  const inputMaMentor = document.getElementById("maMentor");
  const maMentor = inputMaMentor ? inputMaMentor.value : null;
  if (!maMentor) {
    hienThongBaoLoi("Vui lòng chọn Người hướng dẫn / Mentor phụ trách thực tập!");
    toggleDropdownMentor(true);
    return;
  }

  const mentorObj = danhSachMentor.find((x) => String(x.ma_nguoi_dung) === String(maMentor));
  if (mentorObj && (mentorObj.so_sinh_vien_huong_dan || 0) >= (mentorObj.chi_tieu_huong_dan || 5)) {
    hienThongBaoLoi(`Mentor ${mentorObj.ho_ten} đã đủ chỉ tiêu hướng dẫn (${mentorObj.so_sinh_vien_huong_dan}/${mentorObj.chi_tieu_huong_dan}), vui lòng chọn mentor khác!`);
    return;
  }

  const hoTen = document.getElementById("hoTen")?.value.trim();
  const email = document.getElementById("email")?.value.trim();
  const soDienThoai = document.getElementById("soDienThoai")?.value.trim();
  const truongDaiHoc = document.getElementById("truongDaiHoc")?.value.trim();
  const chuyenNganh = document.getElementById("chuyenNganh")?.value.trim();
  const ngayBatDau = document.getElementById("ngayBatDau")?.value;
  const ngayKetThuc = document.getElementById("ngayKetThuc")?.value;
  const nutLuu = document.getElementById("nutLuuHoSo");

  if (!hoTen) {
    hienThongBaoLoi("Vui lòng điền họ và tên của sinh viên.");
    document.getElementById("hoTen")?.focus();
    return;
  }

  const bieuThucEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !bieuThucEmail.test(email)) {
    hienThongBaoLoi("Địa chỉ email sinh viên không đúng cú pháp hợp lệ.");
    document.getElementById("email")?.focus();
    return;
  }

  if (soDienThoai && !/^(0|\+84)[0-9]{9}$/.test(soDienThoai)) {
    hienThongBaoLoi("Số điện thoại không hợp lệ (yêu cầu 10 chữ số chuẩn Việt Nam).");
    document.getElementById("soDienThoai")?.focus();
    return;
  }

  if (!truongDaiHoc) {
    hienThongBaoLoi("Vui lòng chọn hoặc nhập tên Trường đại học của sinh viên!");
    document.getElementById("truongDaiHoc")?.focus();
    return;
  }

  if (!chuyenNganh) {
    hienThongBaoLoi("Vui lòng chọn hoặc nhập Chuyên ngành đào tạo của sinh viên!");
    document.getElementById("chuyenNganh")?.focus();
    return;
  }

  if (ngayBatDau && ngayKetThuc && ngayKetThuc < ngayBatDau) {
    hienThongBaoLoi("Ngày kết thúc thực tập không được nhỏ hơn ngày bắt đầu tiếp nhận!");
    document.getElementById("ngayKetThuc")?.focus();
    return;
  }

  const noiDungNutBanDau = nutLuu ? nutLuu.innerHTML : "";
  if (nutLuu) {
    nutLuu.innerHTML = `<span class="inline-block w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span> <span>Đang lưu trữ & phân công...</span>`;
    nutLuu.disabled = true;
  }

  let trangThaiThucTap = "DangThucTap";
  let trangThaiXetDuyet = "DaDuyet";
  if (trangThaiHienTai === "Đã hoàn thành") {
    trangThaiThucTap = "HoanThanh";
  } else if (trangThaiHienTai === "Tạm dừng") {
    trangThaiThucTap = "ThoiHoc";
  } else if (trangThaiHienTai === "Chờ duyệt") {
    trangThaiXetDuyet = "ChoDuyet";
  }

  const inputMaTruong = document.getElementById("maTruong");
  const maTruong = inputMaTruong ? Number(inputMaTruong.value) || 1 : 1;

  try {
    let ketQuaPhanHoi = null;
    let urlGui = "";
    let methodGui = "";
    let bodyGui = {};

    if (maHoSoHienTai) {
      urlGui = `${duongDanApiInterns}/${maHoSoHienTai}`;
      methodGui = "PUT";
      bodyGui = {
        ho_ten: hoTen,
        email: email,
        so_dien_thoai: soDienThoai || null,
        chuyen_nganh: chuyenNganh || null,
        ma_truong: maTruong,
        ma_chuong_trinh: Number(maChuongTrinh),
        ma_mentor: Number(maMentor),
        trang_thai_thuc_tap: trangThaiThucTap,
        trang_thai_xet_duyet: trangThaiXetDuyet
      };
    } else {
      urlGui = duongDanApiInterns;
      methodGui = "POST";
      bodyGui = {
        ho_ten: hoTen,
        email: email,
        so_dien_thoai: soDienThoai || null,
        chuyen_nganh: chuyenNganh || null,
        ma_truong: maTruong,
        ma_chuong_trinh: Number(maChuongTrinh),
        ma_mentor: Number(maMentor),
        trang_thai_thuc_tap: trangThaiThucTap,
        trang_thai_xet_duyet: trangThaiXetDuyet
      };
    }

    const phanHoi = await fetch(urlGui, {
      method: methodGui,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyGui)
    });

    ketQuaPhanHoi = await phanHoi.json().catch(() => ({}));

    if (phanHoi.ok) {
      const tenProg = progObj ? progObj.ten_chuong_trinh : "Chương trình thực tập";
      const tenMentor = mentorObj ? mentorObj.ho_ten : "Mentor hướng dẫn";
      const thongDiep = maHoSoHienTai
        ? `Cập nhật thành công hồ sơ #${maHoSoHienTai} của sinh viên <b>${hoTen}</b> (Trạng thái: <b>${trangThaiHienTai}</b>)!`
        : `Phân công thành công sinh viên <b>${hoTen}</b> vào <b>${tenProg}</b> (Mentor: <b>${tenMentor}</b>)! Dữ liệu đã được lưu trữ an toàn.`;
      hienThongBaoThanhCong(thongDiep);
      await napTatCaDuLieu();
      chonSinhVien(maNguoiDungChon);
    } else {
      let loiChiTiet = "Có lỗi xảy ra khi lưu trữ thông tin phân công!";
      if (typeof ketQuaPhanHoi.detail === "string") {
        loiChiTiet = ketQuaPhanHoi.detail;
      } else if (Array.isArray(ketQuaPhanHoi.detail) && ketQuaPhanHoi.detail[0]?.msg) {
        loiChiTiet = ketQuaPhanHoi.detail[0].msg;
      } else if (ketQuaPhanHoi.message) {
        loiChiTiet = ketQuaPhanHoi.message;
      }
      hienThongBaoLoi(loiChiTiet);
    }
  } catch (loiKetNoi) {
    hienThongBaoLoi("Không thể kết nối đến máy chủ API. Vui lòng kiểm tra dịch vụ Backend đang chạy hoặc đường truyền mạng!");
  } finally {
    if (nutLuu) {
      nutLuu.innerHTML = noiDungNutBanDau;
      nutLuu.disabled = false;
    }
  }
}

function kiemTraThamSoUrl() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const maNguoiDung = params.get("ma_nguoi_dung");

  if (id) {
    const sv = danhSachSinhVien.find((x) => String(x.ma_ho_so) === String(id));
    if (sv) chonSinhVien(sv.ma_nguoi_dung);
  } else if (maNguoiDung) {
    chonSinhVien(maNguoiDung);
  }
}

function layKhuVucToast() {
  let khuVuc = document.getElementById("khuVucToast");
  if (!khuVuc) {
    khuVuc = document.createElement("div");
    khuVuc.id = "khuVucToast";
    khuVuc.className =
      "fixed top-5 right-5 z-[9999] flex flex-col gap-2.5 pointer-events-none max-w-sm sm:max-w-md w-full px-4 sm:px-0";
    document.body.appendChild(khuVuc);
  }
  return khuVuc;
}

function dongToast(toast, ngayLapTuc = false) {
  if (!toast || !toast.parentNode) return;
  if (thoiGianHenGioToast) {
    clearTimeout(thoiGianHenGioToast);
    thoiGianHenGioToast = null;
  }
  thongDiepToastHienTai = "";
  if (ngayLapTuc) {
    toast.remove();
  } else {
    toast.classList.remove("translate-x-0", "opacity-100");
    toast.classList.add("translate-x-12", "opacity-0");
    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, 250);
  }
}

function hienToast(tieuDe, thongDiep, loai = "canh_bao") {
  const khuVuc = layKhuVucToast();
  const toastCu = khuVuc.querySelector("[data-toast]");

  if (toastCu) {
    if (thongDiepToastHienTai === thongDiep) {
      toastCu.classList.remove("scale-105");
      void toastCu.offsetWidth;
      toastCu.classList.add("scale-105");
      setTimeout(() => {
        toastCu.classList.remove("scale-105");
      }, 200);

      if (thoiGianHenGioToast) clearTimeout(thoiGianHenGioToast);
      thoiGianHenGioToast = setTimeout(() => {
        dongToast(toastCu);
      }, 3500);
      return;
    }
    dongToast(toastCu, true);
  }

  thongDiepToastHienTai = thongDiep;

  const toast = document.createElement("div");
  toast.setAttribute("data-toast", "true");
  toast.className =
    "pointer-events-auto transform translate-x-12 opacity-0 transition-all duration-300 ease-out shadow-xl rounded-2xl p-4 flex items-start gap-3.5 border backdrop-blur-md";

  if (loai === "thanh_cong") {
    toast.className +=
      " bg-white/95 border-emerald-200 text-slate-800 shadow-emerald-500/10";
    toast.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-500/25">
        <span class="material-symbols-outlined text-[20px]">check_circle</span>
      </div>
      <div class="flex-1 min-w-0 text-xs">
        <div class="flex items-center justify-between gap-2">
          <span class="font-bold text-slate-900 text-sm">${tieuDe || "Thông báo"}</span>
          <span class="text-[10px] text-emerald-700 font-semibold bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full shrink-0">Vừa xong</span>
        </div>
        <div class="text-slate-600 mt-1 leading-relaxed break-words">${thongDiep}</div>
      </div>
      <button type="button" class="text-slate-400 hover:text-slate-700 hover:bg-slate-100 p-1.5 rounded-lg transition-colors shrink-0" title="Đóng thông báo">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    `;
  } else {
    toast.className +=
      " bg-white/95 border-rose-200 text-slate-800 shadow-rose-500/10";
    toast.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-rose-500 to-rose-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-rose-500/25">
        <span class="material-symbols-outlined text-[20px]">warning</span>
      </div>
      <div class="flex-1 min-w-0 text-xs">
        <div class="flex items-center justify-between gap-2">
          <span class="font-bold text-slate-900 text-sm">${tieuDe || "Cảnh báo"}</span>
        </div>
        <div class="text-slate-600 mt-1 leading-relaxed break-words">${thongDiep}</div>
      </div>
      <button type="button" class="text-slate-400 hover:text-slate-700 hover:bg-slate-100 p-1.5 rounded-lg transition-colors shrink-0" title="Đóng thông báo">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    `;
  }

  const btnDong = toast.querySelector("button");
  if (btnDong) {
    btnDong.onclick = () => dongToast(toast);
  }

  khuVuc.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove("translate-x-12", "opacity-0");
    toast.classList.add("translate-x-0", "opacity-100");
  });

  if (thoiGianHenGioToast) clearTimeout(thoiGianHenGioToast);
  thoiGianHenGioToast = setTimeout(() => {
    dongToast(toast);
  }, 4000);
}

function hienThongBaoThanhCong(thongDiep) {
  hienToast("Thông báo", thongDiep, "thanh_cong");
}

function hienThongBaoLoi(thongDiep) {
  hienToast("Cảnh báo", thongDiep, "canh_bao");
}

async function taiHoSoGanDay() {
  const tbody = document.getElementById("bangHoSoGanDay");
  if (!tbody) return;

  try {
    const phanHoi = await fetch(`${duongDanApiInterns}?limit=6`);
    if (!phanHoi.ok) return;

    const ketQua = await phanHoi.json();
    const danhSach = ketQua.data;
    if (!danhSach || danhSach.length === 0) return;

    const mauAvatar = [
      "bg-blue-100 text-blue-700",
      "bg-indigo-100 text-indigo-700",
      "bg-emerald-100 text-emerald-700",
      "bg-amber-100 text-amber-700",
      "bg-purple-100 text-purple-700",
      "bg-sky-100 text-sky-700"
    ];

    tbody.innerHTML = danhSach
      .map((item, idx) => {
        const hoTen = item.ho_ten || "Chưa cập nhật";
        const email = item.email || "—";
        const chuyenNganh = item.chuyen_nganh || "Công nghệ thông tin";
        const thoiGian =
          item.ngay_bat_dau && item.ngay_ket_thuc
            ? `${dinhDangNgay(item.ngay_bat_dau)} - ${dinhDangNgay(item.ngay_ket_thuc)}`
            : "Học kỳ 2026 - 2027";

        let badgeTrangThai = "";
        if (item.trang_thai_xet_duyet === "DaDuyet") {
          badgeTrangThai = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Đã duyệt</span>`;
        } else if (item.trang_thai_xet_duyet === "TuChoi") {
          badgeTrangThai = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">Bị từ chối</span>`;
        } else if (item.trang_thai_thuc_tap === "DangThucTap") {
          badgeTrangThai = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">Đang thực tập</span>`;
        } else {
          badgeTrangThai = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">Chờ duyệt</span>`;
        }

        const tu = hoTen.trim().split(" ");
        const vietTat =
          tu.length === 1
            ? tu[0].substring(0, 2).toUpperCase()
            : (tu[0][0] + tu[tu.length - 1][0]).toUpperCase();

        const mau = mauAvatar[idx % mauAvatar.length];

        return `
          <tr class="hover:bg-slate-50/60 transition-colors">
            <td class="py-3 font-bold text-slate-900 flex items-center gap-2">
              <div class="w-6 h-6 rounded-full ${mau} flex items-center justify-center text-[10px] font-bold shrink-0">
                ${vietTat}
              </div>
              <a href="javascript:void(0)" onclick="chonSinhVienTuBang(${item.ma_ho_so})" class="hover:text-blue-600 transition-colors font-semibold" title="Nhấp để phân công lại hồ sơ #${item.ma_ho_so}">
                ${hoTen}
              </a>
            </td>
            <td class="py-3 text-slate-500">${email}</td>
            <td class="py-3">${chuyenNganh}</td>
            <td class="py-3 text-slate-500">${thoiGian}</td>
            <td class="py-3 text-center">${badgeTrangThai}</td>
          </tr>
        `;
      })
      .join("");

    const thoiGianCapNhat = document.getElementById("thoiGianCapNhatHoSo");
    if (thoiGianCapNhat) {
      thoiGianCapNhat.textContent = "Đã đồng bộ từ máy chủ CSDL";
    }
  } catch (err) {}
}

function chonSinhVienTuBang(maHoSo) {
  const sv = danhSachSinhVien.find((x) => String(x.ma_ho_so) === String(maHoSo));
  if (sv) {
    chonSinhVien(sv.ma_nguoi_dung);
    window.scrollTo({ top: 300, behavior: "smooth" });
  }
}

function dinhDangNgay(chuoiNgay) {
  if (!chuoiNgay) return "";
  try {
    const d = new Date(chuoiNgay);
    return `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}/${d.getFullYear()}`;
  } catch {
    return chuoiNgay;
  }
}

function capNhatNienKhoaHeThong() {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;
  const elTieuDe = document.getElementById("theTieuDeNienKhoaThemHoSo");
  if (elTieuDe) elTieuDe.textContent = `Hệ Thống Phân Công Thực Tập ICTU - Niên Khóa ${nienKhoa}`;
  const elBadge = document.getElementById("theNienKhoaHoSo");
  if (elBadge) elBadge.textContent = `Niên khóa ${nienKhoa}`;
}

document.addEventListener("DOMContentLoaded", () => {
  capNhatNienKhoaHeThong();
  napTatCaDuLieu();

  document.addEventListener("click", (e) => {
    const boxSv = document.getElementById("hopChonSinhVienContainer");
    if (boxSv && !boxSv.contains(e.target)) {
      dongDropdownSinhVien();
    }

    const boxProg = document.getElementById("hopChonChuongTrinhContainer");
    if (boxProg && !boxProg.contains(e.target)) {
      dongDropdownChuongTrinh();
    }

    const boxMentor = document.getElementById("hopChonMentorContainer");
    if (boxMentor && !boxMentor.contains(e.target)) {
      dongDropdownMentor();
    }

    const boxTrangThai = document.getElementById("hopChonTrangThaiContainer");
    if (boxTrangThai && !boxTrangThai.contains(e.target)) {
      dongDropdownTrangThai();
    }

    const boxTruong = document.getElementById("hopChonTruongContainer");
    if (boxTruong && !boxTruong.contains(e.target)) {
      dongDropdownTruong();
    }

    const boxChuyenNganh = document.getElementById("hopChonChuyenNganhContainer");
    if (boxChuyenNganh && !boxChuyenNganh.contains(e.target)) {
      dongDropdownChuyenNganh();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      dongDropdownSinhVien();
      dongDropdownChuongTrinh();
      dongDropdownMentor();
      dongDropdownTrangThai();
      dongDropdownTruong();
      dongDropdownChuyenNganh();
    }
  });
});
