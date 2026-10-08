const duongDanApi = "http://127.0.0.1:8000/api/v1";

let danhSachKhoa = [];
let danhSachTatCaSinhVien = [];
let banGhiChamCongHienTai = {};
let danhSachDonNghiHienTai = {};
let danhSachHienThi = [];
let danhSachCaLamViec = [];
let trangHienTai = 1;
let soBanGhiTrenTrang = 10;

const mockKhoaThucTap = [
  { ma_chuong_trinh: 1, ten_chuong_trinh: "Chương trình Thực tập K19 (Niên khóa 2026 - 2027)" },
  { ma_chuong_trinh: 22, ten_chuong_trinh: "Thực tập chuyên sâu Web & Cloud K19" },
  { ma_chuong_trinh: 23, ten_chuong_trinh: "Thực tập cơ sở doanh nghiệp K20 - Đảm bảo chất lượng" },
  { ma_chuong_trinh: 24, ten_chuong_trinh: "Chương trình thực tập Tài năng Trí tuệ Nhân tạo ICTU" }
];

const mockSinhVienMacDinh = [
  { ma_ho_so: 1, ma_sv: "DTC2051060124", ho_ten: "Nguyễn Văn An", email: "annv@ictu.edu.vn", ma_chuong_trinh: 1, chuyen_nganh: "Công nghệ thông tin", phong_ban: "Trung tâm Phần mềm" },
  { ma_ho_so: 2, ma_sv: "DTC2051060188", ho_ten: "Trần Thị Mai Anh", email: "maianh@ictu.edu.vn", ma_chuong_trinh: 1, chuyen_nganh: "Khoa học máy tính", phong_ban: "Phòng AI & Big Data" },
  { ma_ho_so: 9, ma_sv: "DTC2051060045", ho_ten: "Hoàng Minh Đức", email: "duchm@ictu.edu.vn", ma_chuong_trinh: 1, chuyen_nganh: "An toàn Thông tin & An ninh Mạng", phong_ban: "Phòng Hạ tầng Mạng & Cloud" },
  { ma_ho_so: 14, ma_sv: "DTC2051060312", ho_ten: "Lê Thu Trang", email: "tranglt@ictu.edu.vn", ma_chuong_trinh: 1, chuyen_nganh: "Hệ thống Thông tin Quản lý (BA)", phong_ban: "Trung tâm Phần mềm" },
  { ma_ho_so: 15, ma_sv: "DTC2051060244", ho_ten: "Vũ Quang Huy", email: "huyvq@ictu.edu.vn", ma_chuong_trinh: 1, chuyen_nganh: "Kỹ thuật Phần mềm (Frontend Lead)", phong_ban: "Trung tâm Phần mềm" },
  { ma_ho_so: 16, ma_sv: "DTC2051060012", ho_ten: "Phạm Thùy Linh", email: "linhpt@ictu.edu.vn", ma_chuong_trinh: 22, chuyen_nganh: "Kỹ thuật Phần mềm", phong_ban: "Phòng Đào tạo & R&D" },
  { ma_ho_so: 17, ma_sv: "DTC2051060199", ho_ten: "Đặng Thị Hoa", email: "hoadt@ictu.edu.vn", ma_chuong_trinh: 24, chuyen_nganh: "Khoa học máy tính", phong_ban: "Phòng AI & Big Data" },
  { ma_ho_so: 18, ma_sv: "DTC2051060098", ho_ten: "Bùi Tiến Đạt", email: "datbt@ictu.edu.vn", ma_chuong_trinh: 23, chuyen_nganh: "An toàn Thông tin & An ninh Mạng", phong_ban: "Phòng Hạ tầng Mạng & Cloud" }
];

function layNgayHomNayYMD() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function dinhDangNgayVN(ngayYMD) {
  if (!ngayYMD) return { dmy: "--/--/----", thu: "" };
  const parts = ngayYMD.split("-").map(Number);
  const d = new Date(parts[0], parts[1] - 1, parts[2]);
  const dayIdx = d.getDay();
  const mapThuVN = {
    0: "Chủ nhật",
    1: "Thứ Hai",
    2: "Thứ Ba",
    3: "Thứ Tư",
    4: "Thứ Năm",
    5: "Thứ Sáu",
    6: "Thứ Bảy"
  };
  const tenThu = mapThuVN[dayIdx] || "Thứ Hai";
  const ngayStr = String(parts[2]).padStart(2, "0");
  const thangStr = String(parts[1]).padStart(2, "0");
  const namStr = String(parts[0]);
  return {
    dmy: `${ngayStr}/${thangStr}/${namStr}`,
    thu: tenThu
  };
}

function capNhatHienThiNgayVN() {
  const el = document.getElementById("boLocNgay");
  const val = el && el.value ? el.value : layNgayHomNayYMD();
  const info = dinhDangNgayVN(val);
  const span = document.getElementById("hienThiNgayDinhDang");
  if (span) span.textContent = info.dmy;
  const badgeThu = document.getElementById("nhanThuHienTai");
  if (badgeThu) badgeThu.textContent = info.thu;
}

function capNhatHienThiNgayModalVN() {
  const el = document.getElementById("ngayDienRaMoi");
  const val = el && el.value ? el.value : layNgayHomNayYMD();
  const info = dinhDangNgayVN(val);
  const span = document.getElementById("hienThiNgayModalDinhDang");
  if (span) span.textContent = info.dmy;
  const badgeThu = document.getElementById("nhanThuModalMoi");
  if (badgeThu) badgeThu.textContent = info.thu;
}

function moHopChonNgay(idInput) {
  const el = document.getElementById(idInput);
  if (!el) return;
  if (el.showPicker) {
    el.showPicker();
  } else {
    el.focus();
  }
}

function kiemTraSinhVienThuocChuyenNganh(svChuyenNganh, caChuyenNganh) {
  if (!caChuyenNganh || caChuyenNganh === "tat-ca" || caChuyenNganh.toLowerCase() === "tất cả") return true;
  if (!svChuyenNganh) return false;
  const svCn = svChuyenNganh.toLowerCase().trim();
  const caCn = caChuyenNganh.toLowerCase().trim();

  if (svCn === caCn) return true;

  if (caCn.includes("ktpm") || caCn.includes("phần mềm")) {
    return svCn.includes("phần mềm") || svCn.includes("ktpm");
  }
  if (caCn.includes("cntt") || caCn.includes("công nghệ thông tin")) {
    return svCn.includes("công nghệ thông tin") || svCn.includes("cntt");
  }
  if (caCn.includes("ai") || caCn.includes("trí tuệ nhân tạo") || caCn.includes("khoa học máy tính") || caCn.includes("khmt")) {
    return svCn.includes("khoa học máy tính") || svCn.includes("khmt") || svCn.includes("trí tuệ nhân tạo") || svCn.includes("ai");
  }
  if (caCn.includes("attt") || caCn.includes("an toàn") || caCn.includes("an ninh")) {
    return svCn.includes("an toàn") || svCn.includes("an ninh") || svCn.includes("attt");
  }
  if (caCn.includes("httt") || caCn.includes("hệ thống thông tin")) {
    return svCn.includes("hệ thống thông tin") || svCn.includes("httt");
  }

  return svCn.includes(caCn) || caCn.includes(svCn);
}

function layKhungGioCa(tenCa) {
  if (Array.isArray(danhSachCaLamViec) && danhSachCaLamViec.length > 0) {
    const timCa = danhSachCaLamViec.find(ca => ca.ten_ca === tenCa);
    if (timCa && timCa.gio_bat_dau && timCa.gio_ket_thuc) {
      const bd = String(timCa.gio_bat_dau).slice(0, 5);
      const kt = String(timCa.gio_ket_thuc).slice(0, 5);
      return { in: bd, out: kt, text: `${bd} - ${kt}` };
    }
  }
  const c = (tenCa || "").toLowerCase();
  if (c.includes("sáng")) {
    return { in: "08:00", out: "12:00", text: "08:00 - 12:00" };
  } else if (c.includes("chiều")) {
    return { in: "13:30", out: "17:30", text: "13:30 - 17:30" };
  }
  return { in: "08:00", out: "17:30", text: "08:00 - 17:30" };
}

function hienThiThongBao(message, type = "success") {
  const toast = document.getElementById("hopThongBaoToast");
  if (!toast) return;

  const isSuccess = type === "success";
  const bgClass = isSuccess ? "bg-emerald-50 border-emerald-300 text-emerald-800" : "bg-rose-50 border-rose-300 text-rose-800";
  const icon = isSuccess ? "check_circle" : "error";

  toast.className = `p-4 rounded-2xl border ${bgClass} shadow-md flex items-center justify-between gap-3 transition-all duration-300 mb-2`;
  toast.innerHTML = `
    <div class="flex items-center gap-3">
      <span class="material-symbols-outlined text-[22px] ${isSuccess ? "text-emerald-600" : "text-rose-600"}">${icon}</span>
      <span class="text-xs font-bold leading-relaxed">${message}</span>
    </div>
    <button type="button" onclick="dongThongBao()" class="p-1 rounded-lg hover:bg-black/5 text-slate-400 hover:text-slate-600">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  toast.classList.remove("hidden");

  if (window.toastTimeout) clearTimeout(window.toastTimeout);
  window.toastTimeout = setTimeout(() => {
    dongThongBao();
  }, 5000);
}

function dongThongBao() {
  const toast = document.getElementById("hopThongBaoToast");
  if (toast) toast.classList.add("hidden");
}

async function kiemTraKetNoiApi() {
  const badge = document.getElementById("badgeTrangThaiApi");
  if (!badge) return false;
  try {
    const res = await fetch(`${duongDanApi}/attendance/records?thang=10&nam=2026&page=1&page_size=1`, { method: "GET" });
    if (res.ok) {
      badge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Máy chủ: Đã kết nối`;
      badge.classList.remove("hidden");
      return true;
    }
  } catch (e) {}
  badge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
  badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Ngoại tuyến`;
  badge.classList.remove("hidden");
  return false;
}

function capNhatHocKyChamCong() {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;
  const el = document.getElementById("theHocKyChamCong");
  if (el) el.textContent = `Niên khóa ${nienKhoa} • Sprint 2`;
}

async function taiDanhSachKhoaThucTap() {
  const selectKhoa = document.getElementById("boLocKhoaThucTap");
  if (!selectKhoa) return;

  try {
    const res = await fetch(`${duongDanApi}/programs?skip=0&limit=100`);
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.data) && json.data.length > 0) {
        danhSachKhoa = json.data;
      } else {
        danhSachKhoa = [...mockKhoaThucTap];
      }
    } else {
      danhSachKhoa = [...mockKhoaThucTap];
    }
  } catch (e) {
    danhSachKhoa = [...mockKhoaThucTap];
  }

  let html = `<option value="tat-ca">Tất cả các khóa thực tập</option>`;
  danhSachKhoa.forEach(k => {
    html += `<option value="${k.ma_chuong_trinh}">${k.ten_chuong_trinh}</option>`;
  });
  selectKhoa.innerHTML = html;
}

async function taiDanhSachSinhVienVaLop() {
  try {
    const res = await fetch(`${duongDanApi}/interns?limit=200`);
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.data) && json.data.length > 0) {
        danhSachTatCaSinhVien = json.data.map(it => {
          return {
            ma_ho_so: it.ma_ho_so,
            ma_sv: `DTC20510${String(1000 + (it.ma_ho_so || 0)).slice(-4)}`,
            ho_ten: it.ho_ten || `Thực tập sinh #${it.ma_ho_so}`,
            email: it.email || `sv${it.ma_ho_so}@ictu.edu.vn`,
            ma_chuong_trinh: it.ma_chuong_trinh || 1,
            ten_chuong_trinh: it.ten_chuong_trinh || "Chương trình Thực tập K19",
            chuyen_nganh: it.chuyen_nganh || "Công nghệ thông tin",
            phong_ban: "Trung tâm Phát triển Phần mềm ICTU"
          };
        });
      } else {
        danhSachTatCaSinhVien = [...mockSinhVienMacDinh];
      }
    } else {
      danhSachTatCaSinhVien = [...mockSinhVienMacDinh];
    }
  } catch (e) {
    danhSachTatCaSinhVien = [...mockSinhVienMacDinh];
  }

  capNhatDanhSachLopTheoKhoa();
}

function capNhatDanhSachLopTheoKhoa() {
  const selectKhoa = document.getElementById("boLocKhoaThucTap");
  const selectLop = document.getElementById("boLocLop");
  const caEl = document.getElementById("boLocCaLamViec");
  if (!selectLop) return;

  const khoaVal = selectKhoa ? selectKhoa.value : "tat-ca";
  let pool = danhSachTatCaSinhVien;
  if (khoaVal !== "tat-ca") {
    const kId = parseInt(khoaVal, 10);
    pool = pool.filter(sv => sv.ma_chuong_trinh === kId);
  }

  const tenCa = caEl ? caEl.value : "";
  const caHienTai = Array.isArray(danhSachCaLamViec) ? danhSachCaLamViec.find(c => c.ten_ca === tenCa) : null;
  if (caHienTai && caHienTai.chuyen_nganh && caHienTai.chuyen_nganh !== "tat-ca") {
    pool = pool.filter(sv => kiemTraSinhVienThuocChuyenNganh(sv.chuyen_nganh, caHienTai.chuyen_nganh));
  }
  if (caHienTai && caHienTai.ma_chuong_trinh) {
    pool = pool.filter(sv => sv.ma_chuong_trinh === caHienTai.ma_chuong_trinh);
  }

  const dsLop = Array.from(new Set(pool.map(sv => sv.chuyen_nganh).filter(Boolean)));
  const nhanTatCa = caHienTai && caHienTai.chuyen_nganh && caHienTai.chuyen_nganh !== "tat-ca"
    ? `Tất cả các lớp trong ca họp (${pool.length} SV)`
    : `Tất cả các lớp / chuyên ngành (${pool.length} SV)`;

  const giaTriHienTai = selectLop.value;
  let html = `<option value="tat-ca">${nhanTatCa}</option>`;
  dsLop.forEach(lop => {
    const count = pool.filter(sv => sv.chuyen_nganh === lop).length;
    html += `<option value="${lop}">Lớp ${lop} (${count} SV)</option>`;
  });
  selectLop.innerHTML = html;

  if (giaTriHienTai && dsLop.includes(giaTriHienTai)) {
    selectLop.value = giaTriHienTai;
  } else {
    selectLop.value = "tat-ca";
  }
}

async function taiDanhSachDonNghiPhep(ngayYMD) {
  danhSachDonNghiHienTai = {};
  try {
    const res = await fetch(`${duongDanApi}/leave-requests`);
    if (res.ok) {
      const json = await res.json();
      const list = json && (json.data || json.items || (Array.isArray(json) ? json : []));
      if (Array.isArray(list)) {
        list.forEach(don => {
          if (don.trang_thai === "DaDuyet" || don.trang_thai === "Đã duyệt") {
            const tuNgay = don.tu_ngay || don.ngay_nghi;
            const denNgay = don.den_ngay || don.tu_ngay || don.ngay_nghi;
            if (tuNgay && denNgay && ngayYMD >= tuNgay && ngayYMD <= denNgay) {
              danhSachDonNghiHienTai[don.ma_ho_so] = {
                ly_do: don.ly_do || "Đã duyệt nghỉ phép",
                tu_ngay: tuNgay,
                den_ngay: denNgay
              };
            }
          }
        });
      }
    }
  } catch (e) {}
}

async function taiBanGhiChamCongTheoNgay(ngayYMD) {
  banGhiChamCongHienTai = {};
  try {
    const res = await fetch(`${duongDanApi}/attendance/records?ngay=${ngayYMD}&page=1&page_size=200`);
    if (res.ok) {
      const json = await res.json();
      if (json && json.data && Array.isArray(json.data.items)) {
        json.data.items.forEach(it => {
          if (it.ma_ho_so && it.phuong_thuc !== "Đơn nghỉ phép") {
            banGhiChamCongHienTai[it.ma_ho_so] = it;
          }
        });
      }
    }
  } catch (e) {}
}

function kiemTraCaCoHoatDongKhong(tenCa, ngayYMD) {
  if (!ngayYMD) return { hopLe: false, daLuu: false, laTuongLai: false, lyDo: "Vui lòng chọn ngày điểm danh." };

  const ca = Array.isArray(danhSachCaLamViec) ? danhSachCaLamViec.find(c => c.ten_ca === tenCa) : null;
  if (!tenCa || !ca || danhSachCaLamViec.length === 0) {
    return {
      hopLe: false,
      daLuu: false,
      laTuongLai: false,
      lyDo: "Ngày này chưa có ca làm việc hoặc buổi gặp nào được lên lịch trên hệ thống."
    };
  }

  const homNayYMD = layNgayHomNayYMD();
  const laTuongLai = ngayYMD > homNayYMD;

  if (laTuongLai) {
    return {
      hopLe: true,
      daLuu: false,
      laTuongLai: true,
      lyDo: "Buổi gặp / ca làm việc này được lên lịch trong tương lai. Chưa đến thời điểm điểm danh."
    };
  }

  if (banGhiChamCongHienTai && Object.keys(banGhiChamCongHienTai).length > 0) {
    return {
      hopLe: true,
      daLuu: true,
      laTuongLai: false,
      lyDo: "Đã có dữ liệu điểm danh lưu trên hệ thống"
    };
  }

  return {
    hopLe: true,
    daLuu: false,
    laTuongLai: false,
    lyDo: "Ca làm việc sẵn sàng điểm danh"
  };
}

function renderGiaoDienKhongCoLich(kiemTra) {
  const cardTong = document.getElementById("cardTong");
  const cardDungGio = document.getElementById("cardDungGio");
  const cardDiMuon = document.getElementById("cardDiMuon");
  const cardVang = document.getElementById("cardVang");

  if (cardTong) cardTong.textContent = "0";
  if (cardDungGio) cardDungGio.textContent = "0";
  if (cardDiMuon) cardDiMuon.textContent = "0";
  if (cardVang) cardVang.textContent = "0";

  const subtextTong = document.getElementById("subtextTong");
  if (subtextTong) subtextTong.textContent = "Không có ca hoạt động";

  const theDem = document.getElementById("theDemBanGhi");
  if (theDem) theDem.textContent = "(0 sinh viên)";

  const ngayEl = document.getElementById("boLocNgay");
  const ngay = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();
  const [y, m, d] = ngay.split("-");

  const moTa = document.getElementById("moTaKetQuaBang");
  if (moTa) {
    moTa.textContent = `Ngày ${d}/${m}/${y} • Phiên không có lịch làm việc`;
  }

  const thePhien = document.getElementById("theHienThiPhien");
  const nhanPhien = document.getElementById("nhanPhienHienTai");
  if (thePhien && nhanPhien) {
    thePhien.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-300";
    nhanPhien.textContent = `Phiên: (Không có ca) • ${d}/${m}/${y}`;
  }

  const btnLuu = document.getElementById("btnLuuDiemDanh");
  const btnDiemDanh = document.getElementById("btnDiemDanhTatCa");
  if (btnLuu) {
    btnLuu.disabled = true;
    btnLuu.classList.add("opacity-40", "cursor-not-allowed");
    btnLuu.title = "Ngày này không có buổi làm việc hoặc ca họp";
  }
  if (btnDiemDanh) {
    btnDiemDanh.disabled = true;
    btnDiemDanh.classList.add("opacity-40", "cursor-not-allowed");
    btnDiemDanh.title = "Ngày này không có buổi làm việc hoặc ca họp";
  }

  const tbody = document.getElementById("bangChamCongBody");
  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-16 px-6 text-center">
          <div class="max-w-md mx-auto flex flex-col items-center justify-center text-center">
            <div class="w-16 h-16 rounded-3xl bg-slate-100 text-slate-400 flex items-center justify-center mb-4 shadow-inner">
              <span class="material-symbols-outlined text-3xl">event_busy</span>
            </div>
            <h4 class="text-base font-extrabold text-slate-800 mb-1.5">Ngày ${d}/${m}/${y} không có ca làm việc hoặc buổi gặp nào</h4>
            <p class="text-xs text-slate-500 leading-relaxed mb-5">${kiemTra.lyDo}</p>
            <div class="flex items-center gap-3">
              <button
                type="button"
                onclick="moModalThemCa()"
                class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-ictu-600 hover:bg-ictu-700 text-white text-xs font-bold transition-all shadow-md shadow-ictu-600/20 cursor-pointer active:scale-95"
              >
                <span class="material-symbols-outlined text-[17px]">more_time</span>
                <span>+ Tạo ca họp / buổi gặp cho ngày này</span>
              </button>
            </div>
          </div>
        </td>
      </tr>
    `;
  }

  const infoEl = document.getElementById("phanTrangThongTin");
  if (infoEl) infoEl.textContent = "Không có sinh viên cần điểm danh";
  const navEl = document.getElementById("phanTrangNutDieuHuong");
  if (navEl) navEl.innerHTML = "";
}

async function doiPhienDiemDanh(chiDoiCa = false) {
  const ngayEl = document.getElementById("boLocNgay");
  const ngayYMD = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();

  capNhatHienThiNgayVN();

  if (!chiDoiCa) {
    await taiDanhSachCaLamViec(ngayYMD);
  }

  const caEl = document.getElementById("boLocCaLamViec");
  const tenCa = caEl ? caEl.value : "";
  const nhanPhien = document.getElementById("nhanPhienHienTai");

  if (nhanPhien) {
    const [y, m, d] = ngayYMD.split("-");
    nhanPhien.textContent = tenCa ? `Phiên: ${tenCa} • ${d}/${m}/${y}` : `Phiên: (Không có ca) • ${d}/${m}/${y}`;
  }

  await taiDanhSachDonNghiPhep(ngayYMD);
  await taiBanGhiChamCongTheoNgay(ngayYMD);
  capNhatDanhSachLopTheoKhoa();
  locDuLieu();
}

function doiKhoaThucTap() {
  capNhatDanhSachLopTheoKhoa();
  locDuLieu();
}

function locDuLieu() {
  const khoaEl = document.getElementById("boLocKhoaThucTap");
  const lopEl = document.getElementById("boLocLop");
  const ttEl = document.getElementById("boLocTrangThai");
  const kwEl = document.getElementById("timKiem");
  const caEl = document.getElementById("boLocCaLamViec");
  const ngayEl = document.getElementById("boLocNgay");

  const khoaVal = khoaEl ? khoaEl.value : "tat-ca";
  const lopVal = lopEl ? lopEl.value : "tat-ca";
  const ttVal = ttEl ? ttEl.value : "tat-ca";
  const kw = kwEl ? kwEl.value.trim().toLowerCase() : "";
  const tenCa = caEl ? caEl.value : "";
  const khungGio = layKhungGioCa(tenCa);
  const ngayYMD = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();

  const kiemTra = kiemTraCaCoHoatDongKhong(tenCa, ngayYMD);
  if (!kiemTra.hopLe) {
    danhSachHienThi = [];
    renderGiaoDienKhongCoLich(kiemTra);
    return;
  }

  const btnLuu = document.getElementById("btnLuuDiemDanh");
  const btnDiemDanh = document.getElementById("btnDiemDanhTatCa");
  if (kiemTra.laTuongLai) {
    if (btnLuu) {
      btnLuu.disabled = true;
      btnLuu.classList.add("opacity-40", "cursor-not-allowed");
      btnLuu.title = "Buổi gặp trong tương lai, chưa đến thời điểm điểm danh";
    }
    if (btnDiemDanh) {
      btnDiemDanh.disabled = true;
      btnDiemDanh.classList.add("opacity-40", "cursor-not-allowed");
      btnDiemDanh.title = "Buổi gặp trong tương lai, chưa đến thời điểm điểm danh";
    }
  } else {
    if (btnLuu) {
      btnLuu.disabled = false;
      btnLuu.classList.remove("opacity-40", "cursor-not-allowed");
      btnLuu.title = "";
    }
    if (btnDiemDanh) {
      btnDiemDanh.disabled = false;
      btnDiemDanh.classList.remove("opacity-40", "cursor-not-allowed");
      btnDiemDanh.title = "";
    }
  }

  const thePhien = document.getElementById("theHienThiPhien");
  const nhanPhien = document.getElementById("nhanPhienHienTai");
  const [y, m, d] = ngayYMD.split("-");
  if (thePhien && nhanPhien) {
    if (kiemTra.laTuongLai) {
      thePhien.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-800 border border-sky-300";
      nhanPhien.innerHTML = `<span class="material-symbols-outlined text-[14px] text-sky-600">upcoming</span> Phiên: ${tenCa} • ${d}/${m}/${y} (⏳ Sắp diễn ra • Chưa đến thời điểm điểm danh)`;
    } else if (kiemTra.daLuu) {
      thePhien.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300";
      nhanPhien.innerHTML = `<span class="material-symbols-outlined text-[14px] text-emerald-600">verified</span> Phiên: ${tenCa} • ${d}/${m}/${y} (Đã lưu CSDL)`;
    } else {
      thePhien.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-300";
      nhanPhien.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span> Phiên: ${tenCa} • ${d}/${m}/${y} (Chưa lưu điểm danh)`;
    }
  }

  const caHienTai = Array.isArray(danhSachCaLamViec) ? danhSachCaLamViec.find(c => c.ten_ca === tenCa) : null;

  let list = danhSachTatCaSinhVien.map(sv => {
    const donNghi = danhSachDonNghiHienTai[sv.ma_ho_so];
    const daCham = banGhiChamCongHienTai[sv.ma_ho_so];

    let trangThai = null;
    let ghiChu = "";
    let gioVao = khungGio.in;
    let gioRa = khungGio.out;

    if (donNghi) {
      trangThai = "VangMat";
      ghiChu = `Nghỉ phép: ${donNghi.ly_do}`;
      gioVao = "--:--";
      gioRa = "--:--";
    } else if (daCham) {
      trangThai = daCham.trang_thai || "DungGio";
      ghiChu = daCham.ghi_chu || "";
      gioVao = daCham.vao || khungGio.in;
      gioRa = daCham.ra || khungGio.out;
    }

    return {
      ...sv,
      trang_thai: trangThai,
      don_nghi: donNghi,
      ghi_chu: ghiChu,
      gio_vao: gioVao,
      gio_ra: gioRa
    };
  });

  if (caHienTai) {
    if (caHienTai.chuyen_nganh && caHienTai.chuyen_nganh !== "tat-ca") {
      list = list.filter(sv => kiemTraSinhVienThuocChuyenNganh(sv.chuyen_nganh, caHienTai.chuyen_nganh));
    }
    if (caHienTai.ma_chuong_trinh) {
      list = list.filter(sv => sv.ma_chuong_trinh === caHienTai.ma_chuong_trinh);
    }
  }

  if (khoaVal !== "tat-ca") {
    const kId = parseInt(khoaVal, 10);
    list = list.filter(sv => sv.ma_chuong_trinh === kId);
  }

  if (lopVal !== "tat-ca") {
    list = list.filter(sv => sv.chuyen_nganh === lopVal);
  }

  if (ttVal !== "tat-ca") {
    list = list.filter(sv => sv.trang_thai === ttVal);
  }

  if (kw) {
    list = list.filter(sv =>
      (sv.ma_sv && sv.ma_sv.toLowerCase().includes(kw)) ||
      (sv.ho_ten && sv.ho_ten.toLowerCase().includes(kw)) ||
      (sv.email && sv.email.toLowerCase().includes(kw)) ||
      (sv.chuyen_nganh && sv.chuyen_nganh.toLowerCase().includes(kw))
    );
  }

  danhSachHienThi = list;
  trangHienTai = 1;
  renderGiaoDien(list);
}

function chuyenTrang(trangMoi) {
  trangHienTai = trangMoi;
  renderGiaoDien(danhSachHienThi);
}

function doiSoBanGhiMoiTrang(soLuong) {
  soBanGhiTrenTrang = soLuong === "all" ? "all" : parseInt(soLuong, 10);
  trangHienTai = 1;
  renderGiaoDien(danhSachHienThi);
}

function capNhatGhiChu(maHoSo, ghiChuMoi) {
  const item = danhSachHienThi.find(it => it.ma_ho_so === maHoSo);
  if (item) {
    item.ghi_chu = ghiChuMoi;
  }
  const fullItem = danhSachTatCaSinhVien.find(it => it.ma_ho_so === maHoSo);
  if (fullItem) {
    fullItem.ghi_chu = ghiChuMoi;
  }
}

function renderGiaoDien(list) {
  const cardTong = document.getElementById("cardTong");
  const cardDungGio = document.getElementById("cardDungGio");
  const cardDiMuon = document.getElementById("cardDiMuon");
  const cardVang = document.getElementById("cardVang");

  const caEl = document.getElementById("boLocCaLamViec");
  const ngayEl = document.getElementById("boLocNgay");
  const ngayYMD = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();
  const tenCa = caEl ? caEl.value : "";
  const kiemTra = kiemTraCaCoHoatDongKhong(tenCa, ngayYMD);
  const laTuongLai = kiemTra.laTuongLai;

  const tong = list.length;
  const dungGio = list.filter(i => i.trang_thai === "DungGio").length;
  const diMuon = list.filter(i => i.trang_thai === "DiMuon").length;
  const vang = list.filter(i => i.trang_thai === "VangMat").length;

  if (cardTong) cardTong.textContent = tong;
  if (cardDungGio) cardDungGio.textContent = dungGio;
  if (cardDiMuon) cardDiMuon.textContent = diMuon;
  if (cardVang) cardVang.textContent = vang;

  const subtextTong = document.getElementById("subtextTong");
  if (subtextTong) {
    if (laTuongLai) {
      subtextTong.textContent = "Dự kiến tham gia";
    } else {
      subtextTong.textContent = "100% sinh viên";
    }
  }

  const theDem = document.getElementById("theDemBanGhi");
  if (theDem) theDem.textContent = `(${list.length} sinh viên)`;

  const moTa = document.getElementById("moTaKetQuaBang");
  if (moTa) {
    const khoaEl = document.getElementById("boLocKhoaThucTap");
    const lopEl = document.getElementById("boLocLop");

    const [y, m, d] = ngayYMD.split("-");
    const khoaTxt = khoaEl && khoaEl.selectedIndex >= 0 ? khoaEl.options[khoaEl.selectedIndex].text : "Tất cả các khóa";
    const lopTxt = lopEl && lopEl.selectedIndex >= 0 ? lopEl.options[lopEl.selectedIndex].text : "Tất cả các lớp";

    moTa.textContent = `Ngày ${d}/${m}/${y} • ${tenCa || "Ca làm việc"} • ${khoaTxt} • ${lopTxt}${laTuongLai ? " (Chưa đến thời điểm điểm danh)" : ""}`;
  }

  const tongBanGhi = list.length;
  const perPage = soBanGhiTrenTrang === "all" ? (tongBanGhi || 1) : parseInt(soBanGhiTrenTrang, 10);
  const tongSoTrang = Math.max(1, Math.ceil(tongBanGhi / perPage));

  if (trangHienTai > tongSoTrang) {
    trangHienTai = tongSoTrang;
  }
  if (trangHienTai < 1) {
    trangHienTai = 1;
  }

  const batDau = (trangHienTai - 1) * perPage;
  const ketThuc = soBanGhiTrenTrang === "all" ? tongBanGhi : Math.min(batDau + perPage, tongBanGhi);
  const listTrang = list.slice(batDau, ketThuc);

  const infoEl = document.getElementById("phanTrangThongTin");
  if (infoEl) {
    if (tongBanGhi === 0) {
      infoEl.textContent = "Hiển thị 0 sinh viên";
    } else {
      infoEl.textContent = `Hiển thị ${batDau + 1} - ${ketThuc} trong số ${tongBanGhi} sinh viên`;
    }
  }

  const navEl = document.getElementById("phanTrangNutDieuHuong");
  if (navEl) {
    if (tongSoTrang <= 1) {
      navEl.innerHTML = "";
    } else {
      let btnsHtml = `
        <button
          type="button"
          onclick="chuyenTrang(${trangHienTai - 1})"
          ${trangHienTai === 1 ? "disabled" : ""}
          class="px-2.5 py-1 rounded-lg border border-slate-200 text-xs font-semibold ${trangHienTai === 1 ? "opacity-40 cursor-not-allowed bg-slate-50 text-slate-400" : "bg-white text-slate-700 hover:bg-slate-100 cursor-pointer shadow-2xs"}"
        >
          ‹ Trước
        </button>
      `;

      for (let p = 1; p <= tongSoTrang; p++) {
        if (p === 1 || p === tongSoTrang || (p >= trangHienTai - 1 && p <= trangHienTai + 1)) {
          const isActive = p === trangHienTai;
          btnsHtml += `
            <button
              type="button"
              onclick="chuyenTrang(${p})"
              class="w-7 h-7 rounded-lg text-xs font-bold transition-all ${isActive ? "bg-ictu-600 text-white shadow-xs" : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 cursor-pointer"}"
            >
              ${p}
            </button>
          `;
        } else if (p === trangHienTai - 2 || p === trangHienTai + 2) {
          btnsHtml += `<span class="px-1 text-slate-400 text-xs">...</span>`;
        }
      }

      btnsHtml += `
        <button
          type="button"
          onclick="chuyenTrang(${trangHienTai + 1})"
          ${trangHienTai === tongSoTrang ? "disabled" : ""}
          class="px-2.5 py-1 rounded-lg border border-slate-200 text-xs font-semibold ${trangHienTai === tongSoTrang ? "opacity-40 cursor-not-allowed bg-slate-50 text-slate-400" : "bg-white text-slate-700 hover:bg-slate-100 cursor-pointer shadow-2xs"}"
        >
          Sau ›
        </button>
      `;
      navEl.innerHTML = btnsHtml;
    }
  }

  const tbody = document.getElementById("bangChamCongBody");
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="p-10 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl text-slate-300">group_off</span>
            <p class="font-bold text-sm text-slate-600">Không tìm thấy sinh viên nào trong phiên điểm danh này</p>
            <p class="text-xs text-slate-400">Vui lòng thay đổi khóa thực tập, lớp chuyên ngành hoặc từ khóa tìm kiếm.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = listTrang.map(item => {
    const parts = (item.ho_ten || "SV").trim().split(/\s+/);
    const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();

    let donNghiHtml = `<span class="text-slate-300 text-xs font-mono">—</span>`;
    if (item.don_nghi) {
      donNghiHtml = `
        <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-200" title="${item.don_nghi.ly_do}">
          <span class="material-symbols-outlined text-[13px] text-purple-600">event_busy</span>
          <span>Có đơn phép</span>
        </span>
      `;
    }

    const isDungGio = item.trang_thai === "DungGio";
    const isDiMuon = item.trang_thai === "DiMuon";
    const isVang = item.trang_thai === "VangMat";

    const pillWrapperClass = laTuongLai
      ? "inline-flex items-center p-0.5 rounded-xl bg-slate-100/90 border border-slate-200 gap-0.5 text-[11px] pointer-events-none opacity-60 cursor-not-allowed"
      : "inline-flex items-center p-0.5 rounded-xl bg-slate-100/90 border border-slate-200 gap-0.5 text-[11px]";

    return `
      <tr class="hover:bg-slate-50/70 transition-colors" id="hang-sv-${item.ma_ho_so}">
        <td class="px-3 py-2.5 text-center font-mono font-bold text-ictu-600 text-xs">${item.ma_sv}</td>
        <td class="px-3 py-2.5">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full bg-gradient-to-tr from-ictu-600 to-indigo-500 text-white font-bold text-[11px] flex items-center justify-center shrink-0 shadow-2xs">
              ${initials}
            </div>
            <div class="min-w-0">
              <div class="font-bold text-slate-900 truncate text-xs">${item.ho_ten}</div>
              <div class="text-[11px] text-slate-400 truncate">${item.email}</div>
            </div>
          </div>
        </td>
        <td class="px-3 py-2.5">
          <div class="font-semibold text-slate-800 text-xs truncate" title="${item.chuyen_nganh}">${item.chuyen_nganh}</div>
          <div class="text-[10px] text-slate-400 truncate" title="${item.ten_chuong_trinh || "Khóa K19"}">${item.ten_chuong_trinh || "Khóa K19"}</div>
        </td>
        <td class="px-3 py-2.5 text-center">
          ${donNghiHtml}
        </td>
        <td class="px-3 py-2.5 text-center">
          <div class="${pillWrapperClass}">
            <label
              id="lbl-dung-gio-${item.ma_ho_so}"
              onclick="thayDoiTrangThaiDong(${item.ma_ho_so}, 'DungGio')"
              class="flex items-center gap-1 px-2 py-1 rounded-lg ${laTuongLai ? "cursor-not-allowed" : "cursor-pointer"} transition-all ${isDungGio ? "bg-emerald-600 text-white font-bold shadow-xs active:scale-95" : "text-slate-600 hover:text-emerald-700 hover:bg-slate-200/50"}"
            >
              <input
                type="radio"
                name="trang_thai_${item.ma_ho_so}"
                value="DungGio"
                ${isDungGio ? "checked" : ""}
                ${laTuongLai ? "disabled" : ""}
                class="sr-only"
              />
              <span id="dot-dung-gio-${item.ma_ho_so}" class="w-1.5 h-1.5 rounded-full ${isDungGio ? "bg-white" : "bg-emerald-500"}"></span>
              <span>Đúng giờ</span>
            </label>

            <label
              id="lbl-di-muon-${item.ma_ho_so}"
              onclick="thayDoiTrangThaiDong(${item.ma_ho_so}, 'DiMuon')"
              class="flex items-center gap-1 px-2 py-1 rounded-lg ${laTuongLai ? "cursor-not-allowed" : "cursor-pointer"} transition-all ${isDiMuon ? "bg-amber-500 text-white font-bold shadow-xs active:scale-95" : "text-slate-600 hover:text-amber-700 hover:bg-slate-200/50"}"
            >
              <input
                type="radio"
                name="trang_thai_${item.ma_ho_so}"
                value="DiMuon"
                ${isDiMuon ? "checked" : ""}
                ${laTuongLai ? "disabled" : ""}
                class="sr-only"
              />
              <span id="dot-di-muon-${item.ma_ho_so}" class="w-1.5 h-1.5 rounded-full ${isDiMuon ? "bg-white" : "bg-amber-500"}"></span>
              <span>Đi muộn</span>
            </label>

            <label
              id="lbl-vang-mat-${item.ma_ho_so}"
              onclick="thayDoiTrangThaiDong(${item.ma_ho_so}, 'VangMat')"
              class="flex items-center gap-1 px-2 py-1 rounded-lg ${laTuongLai ? "cursor-not-allowed" : "cursor-pointer"} transition-all ${isVang ? "bg-rose-600 text-white font-bold shadow-xs active:scale-95" : "text-slate-600 hover:text-rose-700 hover:bg-slate-200/50"}"
            >
              <input
                type="radio"
                name="trang_thai_${item.ma_ho_so}"
                value="VangMat"
                ${isVang ? "checked" : ""}
                ${laTuongLai ? "disabled" : ""}
                class="sr-only"
              />
              <span id="dot-vang-mat-${item.ma_ho_so}" class="w-1.5 h-1.5 rounded-full ${isVang ? "bg-white" : "bg-rose-500"}"></span>
              <span>Vắng mặt</span>
            </label>
          </div>
        </td>
        <td class="px-3 py-2.5 text-center font-mono text-xs text-slate-600">
          <span id="gio-ca-${item.ma_ho_so}" class="${isVang ? "text-slate-300" : "font-semibold text-slate-700"}">
            ${isVang ? "--:--" : `${item.gio_vao} - ${item.gio_ra}`}
          </span>
        </td>
        <td class="px-3 py-2.5">
          <input
            type="text"
            id="ghi-chu-${item.ma_ho_so}"
            value="${item.ghi_chu || ""}"
            ${laTuongLai ? "disabled readonly" : `oninput="capNhatGhiChu(${item.ma_ho_so}, this.value)"`}
            placeholder="${laTuongLai ? "Chưa đến giờ họp..." : "Ghi chú đánh giá..."}"
            class="w-full h-7 px-2 border border-slate-200 rounded-lg text-xs ${laTuongLai ? "text-slate-400 bg-slate-50 cursor-not-allowed" : "text-slate-700 focus:ring-1 focus:ring-ictu-500 focus:border-ictu-500 bg-white"}"
          />
        </td>
      </tr>
    `;
  }).join("");
}

function capNhatGiaoDienTrangThaiPill(maHoSo, trangThaiMoi) {
  const lblDung = document.getElementById(`lbl-dung-gio-${maHoSo}`);
  const dotDung = document.getElementById(`dot-dung-gio-${maHoSo}`);
  const lblMuon = document.getElementById(`lbl-di-muon-${maHoSo}`);
  const dotMuon = document.getElementById(`dot-di-muon-${maHoSo}`);
  const lblVang = document.getElementById(`lbl-vang-mat-${maHoSo}`);
  const dotVang = document.getElementById(`dot-vang-mat-${maHoSo}`);

  const isDung = trangThaiMoi === "DungGio";
  const isMuon = trangThaiMoi === "DiMuon";
  const isVang = trangThaiMoi === "VangMat";

  if (lblDung) {
    lblDung.className = `flex items-center gap-1 px-2 py-1 rounded-lg cursor-pointer transition-all ${isDung ? "bg-emerald-600 text-white font-bold shadow-xs active:scale-95" : "text-slate-600 hover:text-emerald-700 hover:bg-slate-200/50"}`;
  }
  if (dotDung) {
    dotDung.className = `w-1.5 h-1.5 rounded-full ${isDung ? "bg-white" : "bg-emerald-500"}`;
  }

  if (lblMuon) {
    lblMuon.className = `flex items-center gap-1 px-2 py-1 rounded-lg cursor-pointer transition-all ${isMuon ? "bg-amber-500 text-white font-bold shadow-xs active:scale-95" : "text-slate-600 hover:text-amber-700 hover:bg-slate-200/50"}`;
  }
  if (dotMuon) {
    dotMuon.className = `w-1.5 h-1.5 rounded-full ${isMuon ? "bg-white" : "bg-amber-500"}`;
  }

  if (lblVang) {
    lblVang.className = `flex items-center gap-1 px-2 py-1 rounded-lg cursor-pointer transition-all ${isVang ? "bg-rose-600 text-white font-bold shadow-xs active:scale-95" : "text-slate-600 hover:text-rose-700 hover:bg-slate-200/50"}`;
  }
  if (dotVang) {
    dotVang.className = `w-1.5 h-1.5 rounded-full ${isVang ? "bg-white" : "bg-rose-500"}`;
  }

  const radio = document.querySelector(`input[name="trang_thai_${maHoSo}"][value="${trangThaiMoi}"]`);
  if (radio) {
    radio.checked = true;
  }
}

function thayDoiTrangThaiDong(maHoSo, trangThaiMoi) {
  const ngayEl = document.getElementById("boLocNgay");
  const caEl = document.getElementById("boLocCaLamViec");
  const ngayYMD = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();
  const tenCa = caEl ? caEl.value : "";
  if (kiemTraCaCoHoatDongKhong(tenCa, ngayYMD).laTuongLai) {
    hienThiThongBao("Buổi gặp này diễn ra trong tương lai, chưa đến thời điểm điểm danh.", "error");
    return;
  }

  const item = danhSachHienThi.find(it => it.ma_ho_so === maHoSo);
  if (item) {
    item.trang_thai = trangThaiMoi;
  }
  const fullItem = danhSachTatCaSinhVien.find(it => it.ma_ho_so === maHoSo);
  if (fullItem) {
    fullItem.trang_thai = trangThaiMoi;
  }

  capNhatGiaoDienTrangThaiPill(maHoSo, trangThaiMoi);

  const gioEl = document.getElementById(`gio-ca-${maHoSo}`);
  if (gioEl) {
    const khungGio = layKhungGioCa(tenCa);
    if (trangThaiMoi === "VangMat") {
      gioEl.textContent = "--:--";
      gioEl.className = "text-slate-300";
    } else {
      gioEl.textContent = `${khungGio.in} - ${khungGio.out}`;
      gioEl.className = "font-semibold text-slate-700";
    }
  }

  const cardTong = document.getElementById("cardTong");
  const cardDungGio = document.getElementById("cardDungGio");
  const cardDiMuon = document.getElementById("cardDiMuon");
  const cardVang = document.getElementById("cardVang");

  if (cardTong) cardTong.textContent = danhSachHienThi.length;
  if (cardDungGio) cardDungGio.textContent = danhSachHienThi.filter(i => i.trang_thai === "DungGio").length;
  if (cardDiMuon) cardDiMuon.textContent = danhSachHienThi.filter(i => i.trang_thai === "DiMuon").length;
  if (cardVang) cardVang.textContent = danhSachHienThi.filter(i => i.trang_thai === "VangMat").length;
}

function diemDanhTatCaCoMat() {
  const ngayEl = document.getElementById("boLocNgay");
  const caEl = document.getElementById("boLocCaLamViec");
  const ngayYMD = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();
  const tenCa = caEl ? caEl.value : "";
  if (kiemTraCaCoHoatDongKhong(tenCa, ngayYMD).laTuongLai) {
    hienThiThongBao("Buổi gặp này diễn ra trong tương lai, chưa đến thời điểm điểm danh.", "error");
    return;
  }

  let countThayDoi = 0;
  let countGiuNguyenVang = 0;

  danhSachHienThi.forEach(item => {
    if (item.trang_thai === "VangMat" || item.don_nghi) {
      countGiuNguyenVang++;
      return;
    }
    item.trang_thai = "DungGio";
    countThayDoi++;
    capNhatGiaoDienTrangThaiPill(item.ma_ho_so, "DungGio");
    const gioEl = document.getElementById(`gio-ca-${item.ma_ho_so}`);
    if (gioEl) {
      const khungGio = layKhungGioCa(tenCa);
      gioEl.textContent = `${khungGio.in} - ${khungGio.out}`;
      gioEl.className = "font-semibold text-slate-700";
    }
  });

  const cardTong = document.getElementById("cardTong");
  const cardDungGio = document.getElementById("cardDungGio");
  const cardDiMuon = document.getElementById("cardDiMuon");
  const cardVang = document.getElementById("cardVang");

  if (cardTong) cardTong.textContent = danhSachHienThi.length;
  if (cardDungGio) cardDungGio.textContent = danhSachHienThi.filter(i => i.trang_thai === "DungGio").length;
  if (cardDiMuon) cardDiMuon.textContent = danhSachHienThi.filter(i => i.trang_thai === "DiMuon").length;
  if (cardVang) cardVang.textContent = danhSachHienThi.filter(i => i.trang_thai === "VangMat").length;

  let msg = `Đã đánh dấu Đúng giờ cho ${countThayDoi} sinh viên đang có mặt.`;
  if (countGiuNguyenVang > 0) {
    msg += ` Giữ nguyên ${countGiuNguyenVang} sinh viên đã tích Vắng mặt hoặc có đơn nghỉ phép.`;
  }
  hienThiThongBao(msg, "success");
}

async function luuSoDiemDanh() {
  const btn = document.getElementById("btnLuuDiemDanh");
  const icon = document.getElementById("iconLuuDiemDanh");
  const text = document.getElementById("textLuuDiemDanh");
  const ngayEl = document.getElementById("boLocNgay");
  const caEl = document.getElementById("boLocCaLamViec");
  const khoaEl = document.getElementById("boLocKhoaThucTap");
  const lopEl = document.getElementById("boLocLop");

  const ngayYMD = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();
  const tenCa = caEl ? caEl.value : "";
  const khungGio = layKhungGioCa(tenCa);
  const maChuongTrinh = khoaEl && khoaEl.value !== "tat-ca" ? parseInt(khoaEl.value, 10) : null;
  const chuyenNganh = lopEl && lopEl.value !== "tat-ca" ? lopEl.value : null;

  if (kiemTraCaCoHoatDongKhong(tenCa, ngayYMD).laTuongLai) {
    hienThiThongBao("Không thể điểm danh trước cho ngày trong tương lai.", "error");
    return;
  }

  if (danhSachHienThi.length === 0) {
    hienThiThongBao("Không có sinh viên nào trong danh sách để lưu điểm danh", "error");
    return;
  }

  const chuaDiemDanh = danhSachHienThi.filter(it => !it.trang_thai);
  if (chuaDiemDanh.length > 0) {
    hienThiThongBao(`Còn ${chuaDiemDanh.length} sinh viên chưa được chọn trạng thái điểm danh. Vui lòng chọn cho từng bạn hoặc bấm 'Điểm danh tất cả có mặt'.`, "error");
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang lưu...";
  }

  try {
    const payloadRecords = danhSachHienThi.map(item => {
      const radioChecked = document.querySelector(`input[name="trang_thai_${item.ma_ho_so}"]:checked`);
      const trangThai = radioChecked ? radioChecked.value : item.trang_thai;
      const ghiChuInput = document.getElementById(`ghi-chu-${item.ma_ho_so}`);
      const ghiChu = ghiChuInput ? ghiChuInput.value.trim() : item.ghi_chu;

      return {
        ma_ho_so: item.ma_ho_so,
        trang_thai: trangThai,
        gio_check_in: trangThai === "VangMat" ? null : `${khungGio.in}:00`,
        gio_check_out: trangThai === "VangMat" ? null : `${khungGio.out}:00`,
        ghi_chu: ghiChu || ""
      };
    });

    const body = {
      ngay_cham_cong: ngayYMD,
      ca_lam_viec: tenCa,
      ma_chuong_trinh: maChuongTrinh,
      chuyen_nganh: chuyenNganh,
      records: payloadRecords
    };

    const res = await fetch(`${duongDanApi}/attendance/roll-call`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    if (res.ok) {
      const data = await res.json();
      hienThiThongBao(`Lưu sổ điểm danh thành công! Đã ghi nhận ${data.total_saved || payloadRecords.length} sinh viên cho ${tenCa}.`, "success");
      await taiBanGhiChamCongTheoNgay(ngayYMD);
      locDuLieu();
    } else {
      const err = await res.json().catch(() => ({}));
      const msg = err.detail || err.message || "Lỗi khi lưu điểm danh lên máy chủ";
      hienThiThongBao(`Không thể lưu sổ điểm danh: ${msg}`, "error");
    }
  } catch (err) {
    hienThiThongBao(`Mất kết nối máy chủ hoặc lỗi mạng: ${err.message || err}`, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "save";
      if (text) text.textContent = "Lưu sổ điểm danh";
    }
  }
}

let danhSachTatCaDonNghiModal = [];
let tabDonNghiHienTai = "ChoDuyet";

function moModalDuyetNghiPhep() {
  const modal = document.getElementById("modalDuyetNghiPhep");
  if (modal) {
    modal.classList.remove("hidden");
    taiDanhSachTatCaDonNghi();
  }
}

function dongModalDuyetNghiPhep() {
  const modal = document.getElementById("modalDuyetNghiPhep");
  if (modal) {
    modal.classList.add("hidden");
  }
}

function chuyenTabDonNghi(tab) {
  tabDonNghiHienTai = tab;
  const btnCho = document.getElementById("tabDonChoDuyet");
  const btnTatCa = document.getElementById("tabDonTatCa");

  if (tab === "ChoDuyet") {
    if (btnCho) btnCho.className = "px-3.5 py-1.5 rounded-xl text-xs font-bold bg-purple-600 text-white shadow-xs cursor-pointer";
    if (btnTatCa) btnTatCa.className = "px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 cursor-pointer";
  } else {
    if (btnCho) btnCho.className = "px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 cursor-pointer";
    if (btnTatCa) btnTatCa.className = "px-3.5 py-1.5 rounded-xl text-xs font-bold bg-purple-600 text-white shadow-xs cursor-pointer";
  }
  renderBangDonNghiPhep();
}

async function taiDanhSachTatCaDonNghi() {
  try {
    const res = await fetch(`${duongDanApi}/leave-requests`);
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.data)) {
        danhSachTatCaDonNghiModal = json.data;
      }
    }
  } catch (e) {}

  const soDonChoDuyet = danhSachTatCaDonNghiModal.filter(d => d.trang_thai === "Chờ duyệt" || d.trang_thai === "ChoDuyet").length;
  const badgeMain = document.getElementById("badgeSoDonChoDuyet");
  if (badgeMain) {
    badgeMain.textContent = soDonChoDuyet;
  }
  const demCho = document.getElementById("demDonChoDuyetTab");
  if (demCho) demCho.textContent = soDonChoDuyet;
  const demTatCa = document.getElementById("demDonTatCaTab");
  if (demTatCa) demTatCa.textContent = danhSachTatCaDonNghiModal.length;

  renderBangDonNghiPhep();
}

function renderBangDonNghiPhep() {
  const tbody = document.getElementById("bangDonNghiPhepBody");
  if (!tbody) return;

  let danhSachLoc = danhSachTatCaDonNghiModal;
  if (tabDonNghiHienTai === "ChoDuyet") {
    danhSachLoc = danhSachTatCaDonNghiModal.filter(d => d.trang_thai === "Chờ duyệt" || d.trang_thai === "ChoDuyet");
  }

  if (danhSachLoc.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-8 text-slate-400">
          <div class="flex flex-col items-center gap-1.5">
            <span class="material-symbols-outlined text-3xl text-slate-300">inbox</span>
            <span>Không có đơn xin nghỉ phép nào ${tabDonNghiHienTai === "ChoDuyet" ? "đang chờ xét duyệt" : "trong danh sách"}.</span>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = danhSachLoc.map(item => {
    const isPending = item.trang_thai === "Chờ duyệt" || item.trang_thai === "ChoDuyet";
    const isApproved = item.trang_thai === "Đã duyệt" || item.trang_thai === "DaDuyet";
    const isRejected = item.trang_thai === "Từ chối" || item.trang_thai === "TuChoi";

    let badgeStatus = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">Chờ duyệt</span>`;
    if (isApproved) {
      badgeStatus = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Đã duyệt</span>`;
    } else if (isRejected) {
      badgeStatus = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Từ chối</span>`;
    }

    const daDuyet = item.so_ngay_da_duyet || 0;
    const conLai = item.so_ngay_con_lai != null ? item.so_ngay_con_lai : Math.max(0, 3 - daDuyet);

    const soNgayDon = item.so_ngay || 1;
    const khongDuQuy = soNgayDon > conLai;

    let actionButtons = `<span class="text-xs text-slate-400 italic">Đã xử lý</span>`;
    if (isPending) {
      if (khongDuQuy) {
        actionButtons = `
          <div class="flex items-center justify-center gap-1.5" id="actions-don-${item.ma_don}">
            <button
              type="button"
              disabled
              class="px-2 py-1 rounded-lg bg-slate-100 text-slate-400 font-bold text-xs flex items-center gap-1 cursor-not-allowed opacity-70 border border-slate-200"
              title="Không đủ quỹ phép (Xin ${soNgayDon} ngày, còn ${conLai} ngày)"
            >
              <span class="material-symbols-outlined text-[14px]">block</span>
              <span>Hết quỹ</span>
            </button>
            <button
              type="button"
              onclick="xuLyDuyetDonNghi(${item.ma_don}, 'TuChoi')"
              class="px-2.5 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 font-bold text-xs flex items-center gap-1 transition-all cursor-pointer active:scale-95"
              title="Từ chối đơn xin nghỉ"
            >
              <span class="material-symbols-outlined text-[15px]">close</span>
              <span>Từ chối</span>
            </button>
          </div>
        `;
      } else {
        actionButtons = `
          <div class="flex items-center justify-center gap-1.5" id="actions-don-${item.ma_don}">
            <button
              type="button"
              onclick="xuLyDuyetDonNghi(${item.ma_don}, 'DaDuyet')"
              class="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1 transition-all cursor-pointer shadow-xs active:scale-95"
              title="Duyệt đơn nghỉ phép"
            >
              <span class="material-symbols-outlined text-[15px]">check</span>
              <span>Duyệt</span>
            </button>
            <button
              type="button"
              onclick="xuLyDuyetDonNghi(${item.ma_don}, 'TuChoi')"
              class="px-2.5 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 font-bold text-xs flex items-center gap-1 transition-all cursor-pointer active:scale-95"
              title="Từ chối đơn xin nghỉ"
            >
              <span class="material-symbols-outlined text-[15px]">close</span>
              <span>Từ chối</span>
            </button>
          </div>
        `;
      }
    }

    return `
      <tr class="hover:bg-slate-50/70 transition-colors">
        <td class="p-3 text-center font-mono font-bold text-slate-900">NP-${String(item.ma_don).padStart(3, "0")}</td>
        <td class="p-3">
          <div class="font-bold text-slate-800">${item.ho_ten || "Sinh viên"}</div>
          <div class="text-[11px] text-slate-400 font-mono">${item.ma_sv || ""} • ${item.chuyen_nganh || ""}</div>
        </td>
        <td class="p-3 font-mono text-slate-700">
          ${item.tu_ngay} <span class="text-slate-400">➔</span> ${item.den_ngay}
        </td>
        <td class="p-3 text-center font-bold font-mono text-slate-800">${item.so_ngay || 1} ngày</td>
        <td class="p-3 text-center">
          <span class="font-mono text-xs font-semibold ${daDuyet >= 3 ? "text-rose-600" : "text-emerald-700"}">
            ${daDuyet}/3 ngày
          </span>
          <div class="text-[10px] text-slate-400">(Còn ${conLai} ngày)</div>
        </td>
        <td class="p-3 text-slate-600 max-w-xs truncate" title="${item.ly_do || ""}">${item.ly_do || ""}</td>
        <td class="p-3 text-center">${badgeStatus}</td>
        <td class="p-3 text-center">${actionButtons}</td>
      </tr>
    `;
  }).join("");
}

async function xuLyDuyetDonNghi(maDon, trangThaiMoi) {
  const container = document.getElementById(`actions-don-${maDon}`);
  if (container) {
    container.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></span>`;
  }

  try {
    const res = await fetch(`${duongDanApi}/leave-requests/${maDon}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        trang_thai: trangThaiMoi
      })
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok) {
      const loaiHanhDong = trangThaiMoi === "DaDuyet" ? "phê duyệt" : "từ chối";
      hienThiThongBao(`Đã ${loaiHanhDong} đơn xin nghỉ phép NP-${String(maDon).padStart(3, "0")} thành công!`, "success");
      await taiDanhSachTatCaDonNghi();
      await doiPhienDiemDanh();
    } else {
      let msg = "Lỗi xử lý duyệt đơn xin nghỉ";
      if (typeof data.detail === "string") {
        msg = data.detail;
      } else if (Array.isArray(data.detail)) {
        msg = data.detail.map(e => e.msg || e.message).join(", ");
      }
      hienThiThongBao(msg, "error");
      await taiDanhSachTatCaDonNghi();
    }
  } catch (err) {
    hienThiThongBao(`Mất kết nối máy chủ: ${err.message || err}`, "error");
    await taiDanhSachTatCaDonNghi();
  }
}

async function taiDanhSachCaLamViec(ngayYMD) {
  const select = document.getElementById("boLocCaLamViec");
  if (!select) return;

  const ngayParam = ngayYMD || (document.getElementById("boLocNgay") ? document.getElementById("boLocNgay").value : layNgayHomNayYMD());

  try {
    const url = ngayParam ? `${duongDanApi}/attendance/shifts?ngay=${ngayParam}` : `${duongDanApi}/attendance/shifts`;
    const res = await fetch(url);
    if (res.ok) {
      const json = await res.json();
      const ds = Array.isArray(json) ? json : (json.data || []);
      if (Array.isArray(ds)) {
        danhSachCaLamViec = ds;
        if (ds.length === 0) {
          select.innerHTML = `<option value="">(Không có ca họp nào)</option>`;
          select.value = "";
          return;
        }

        const giaTriHienTai = select.value;
        select.innerHTML = ds.map(ca => {
          const bd = String(ca.gio_bat_dau || "").slice(0, 5);
          const kt = String(ca.gio_ket_thuc || "").slice(0, 5);
          const target = ca.chuyen_nganh ? ` • ${ca.chuyen_nganh}` : "";
          return `<option value="${ca.ten_ca}">${ca.ten_ca} (${bd} - ${kt}${target})</option>`;
        }).join("");

        if (giaTriHienTai && ds.some(ca => ca.ten_ca === giaTriHienTai)) {
          select.value = giaTriHienTai;
        } else {
          select.value = ds[0].ten_ca;
        }
        return;
      }
    }
  } catch (e) {}

  danhSachCaLamViec = [];
  select.innerHTML = `<option value="">(Không có ca họp nào)</option>`;
  select.value = "";
}

function moModalThemCa() {
  const modal = document.getElementById("modalThemCaMoi");
  if (!modal) return;
  const tenInput = document.getElementById("tenCaMoi");
  if (tenInput) tenInput.value = "";
  const bdInput = document.getElementById("gioBatDauMoi");
  if (bdInput) bdInput.value = "14:00";
  const ktInput = document.getElementById("gioKetThucMoi");
  if (ktInput) ktInput.value = "16:30";
  const ghiChuInput = document.getElementById("ghiChuCaMoi");
  if (ghiChuInput) ghiChuInput.value = "";

  const ngayEl = document.getElementById("boLocNgay");
  const ngay = ngayEl && ngayEl.value ? ngayEl.value : layNgayHomNayYMD();

  const ngayInput = document.getElementById("ngayDienRaMoi");
  if (ngayInput) {
    ngayInput.value = ngay;
    capNhatHienThiNgayModalVN();
  }

  const selectCn = document.getElementById("chuyenNganhCaMoi");
  if (selectCn) {
    const dsLop = Array.from(new Set(danhSachTatCaSinhVien.map(sv => sv.chuyen_nganh).filter(Boolean)));
    let opts = `<option value="tat-ca" selected>Tất cả các lớp / sinh viên</option>`;
    opts += `<option value="KTPM">Kỹ thuật Phần mềm (KTPM)</option>`;
    opts += `<option value="Công nghệ thông tin">Công nghệ thông tin (CNTT)</option>`;
    opts += `<option value="Khoa học máy tính">Khoa học máy tính (AI / Data)</option>`;
    opts += `<option value="An toàn Thông tin & An ninh Mạng">An toàn Thông tin & An ninh Mạng</option>`;
    opts += `<option value="Hệ thống Thông tin Quản lý (BA)">Hệ thống Thông tin Quản lý (BA)</option>`;
    dsLop.forEach(l => {
      if (!opts.includes(`value="${l}"`)) {
        opts += `<option value="${l}">${l}</option>`;
      }
    });
    selectCn.innerHTML = opts;
  }

  tinhThoiLuongCaMoi();
  modal.classList.remove("hidden");
  if (tenInput) tenInput.focus();
}

function dongModalThemCa() {
  const modal = document.getElementById("modalThemCaMoi");
  if (!modal) return;
  modal.classList.add("hidden");
}

function tinhThoiLuongCaMoi() {
  const bdInput = document.getElementById("gioBatDauMoi");
  const ktInput = document.getElementById("gioKetThucMoi");
  const nhanThoiLuong = document.getElementById("nhanThoiLuongCa");
  if (!nhanThoiLuong || !bdInput || !ktInput) return;

  const bd = bdInput.value;
  const kt = ktInput.value;
  if (!bd || !kt) {
    nhanThoiLuong.textContent = "--";
    nhanThoiLuong.className = "font-extrabold font-mono text-slate-400";
    return;
  }

  const [h1, m1] = bd.split(":").map(Number);
  const [h2, m2] = kt.split(":").map(Number);
  const diffPhut = (h2 * 60 + m2) - (h1 * 60 + m1);

  if (diffPhut <= 0) {
    nhanThoiLuong.textContent = "Không hợp lệ (Giờ kết thúc phải lớn hơn giờ bắt đầu)";
    nhanThoiLuong.className = "font-extrabold font-mono text-rose-600";
  } else {
    const soGio = (diffPhut / 60).toFixed(1).replace(".0", "");
    nhanThoiLuong.textContent = `${soGio} giờ (${diffPhut} phút)`;
    nhanThoiLuong.className = "font-extrabold font-mono text-ictu-700";
  }
}

async function taoCaLamViecMoi() {
  const tenInput = document.getElementById("tenCaMoi");
  const bdInput = document.getElementById("gioBatDauMoi");
  const ktInput = document.getElementById("gioKetThucMoi");
  const ngayDienRaInput = document.getElementById("ngayDienRaMoi");
  const chuyenNganhInput = document.getElementById("chuyenNganhCaMoi");
  const ghiChuInput = document.getElementById("ghiChuCaMoi");
  const btn = document.getElementById("btnLuuCaMoi");
  const icon = document.getElementById("iconLuuCaMoi");
  const text = document.getElementById("textLuuCaMoi");

  const tenCa = tenInput ? tenInput.value.trim() : "";
  const bd = bdInput ? bdInput.value.trim() : "";
  const kt = ktInput ? ktInput.value.trim() : "";
  const ngayDienRa = ngayDienRaInput && ngayDienRaInput.value ? ngayDienRaInput.value : layNgayHomNayYMD();
  const chuyenNganh = chuyenNganhInput && chuyenNganhInput.value !== "tat-ca" ? chuyenNganhInput.value : null;
  const ghiChu = ghiChuInput ? ghiChuInput.value.trim() : "";

  if (!tenCa) {
    hienThiThongBao("Vui lòng nhập tên ca làm việc hoặc buổi gặp", "error");
    if (tenInput) tenInput.focus();
    return;
  }

  if (!bd || !kt) {
    hienThiThongBao("Vui lòng chọn đầy đủ giờ bắt đầu và giờ kết thúc", "error");
    return;
  }

  const [h1, m1] = bd.split(":").map(Number);
  const [h2, m2] = kt.split(":").map(Number);
  if ((h2 * 60 + m2) <= (h1 * 60 + m1)) {
    hienThiThongBao("Giờ kết thúc ca làm việc phải lớn hơn giờ bắt đầu", "error");
    if (ktInput) ktInput.focus();
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang tạo...";
  }

  try {
    const res = await fetch(`${duongDanApi}/attendance/shifts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ten_ca: tenCa,
        gio_bat_dau: bd,
        gio_ket_thuc: kt,
        cac_ngay_trong_tuan: "Linh hoạt",
        ngay_dien_ra: ngayDienRa,
        chuyen_nganh: chuyenNganh,
        ghi_chu: ghiChu || null
      })
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok) {
      hienThiThongBao(`Đã tạo ca làm việc / buổi gặp '${tenCa}' thành công!`, "success");
      dongModalThemCa();
      const ngayEl = document.getElementById("boLocNgay");
      if (ngayEl && ngayDienRa) {
        ngayEl.value = ngayDienRa;
      }
      await taiDanhSachCaLamViec(ngayDienRa);
      const select = document.getElementById("boLocCaLamViec");
      if (select) {
        select.value = tenCa;
      }
      await doiPhienDiemDanh(true);
    } else {
      let msg = "Không thể tạo ca làm việc";
      if (typeof data.detail === "string") {
        msg = data.detail;
      } else if (Array.isArray(data.detail)) {
        msg = data.detail.map(e => e.msg || e.message).join(", ");
      }
      hienThiThongBao(msg, "error");
    }
  } catch (err) {
    hienThiThongBao(`Mất kết nối máy chủ: ${err.message || err}`, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "save";
      if (text) text.textContent = "Tạo buổi gặp";
    }
  }
}

async function taiDuLieuChamCong() {
  const ngayEl = document.getElementById("boLocNgay");
  if (ngayEl && !ngayEl.value) {
    ngayEl.value = layNgayHomNayYMD();
  }
  await doiPhienDiemDanh();
}

document.addEventListener("DOMContentLoaded", async () => {
  capNhatHocKyChamCong();
  const ngayEl = document.getElementById("boLocNgay");
  const homNay = layNgayHomNayYMD();
  if (ngayEl) {
    ngayEl.value = homNay;
    capNhatHienThiNgayVN();
  }
  await kiemTraKetNoiApi();
  await taiDanhSachKhoaThucTap();
  await taiDanhSachSinhVienVaLop();
  await taiDanhSachCaLamViec(homNay);
  await doiPhienDiemDanh(true);
  await taiDanhSachTatCaDonNghi();
});
