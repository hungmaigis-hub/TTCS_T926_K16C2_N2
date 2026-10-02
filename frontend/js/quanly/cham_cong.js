const duongDanApi = "http://127.0.0.1:8000/api/v1";

const mockDataChamCong = [
  { ma_sv: "DTC2051060124", ho_ten: "Nguyễn Văn An", phong_ban: "Trung tâm Phần mềm", chuyen_nganh: "Kỹ thuật phần mềm", ngay: "01/10/2026", vao: "07:55", ra: "17:30", gio: 8.5, trang_thai: "DungGio", ghi_chu: "Đúng giờ ca sáng" },
  { ma_sv: "DTC2051060188", ho_ten: "Trần Thị Mai Anh", phong_ban: "Phòng AI & Big Data", chuyen_nganh: "Khoa học máy tính", ngay: "01/10/2026", vao: "08:18", ra: "17:30", gio: 8.0, trang_thai: "DiMuon", ghi_chu: "Đi muộn 18 phút (Kẹt xe QL3)" },
  { ma_sv: "DTC2051060045", ho_ten: "Hoàng Minh Đức", phong_ban: "Phòng Hạ tầng Mạng & Cloud", chuyen_nganh: "Mạng máy tính", ngay: "01/10/2026", vao: "08:00", ra: "17:30", gio: 8.5, trang_thai: "DungGio", ghi_chu: "On-site tại trung tâm dữ liệu" },
  { ma_sv: "DTC2051060312", ho_ten: "Lê Thu Trang", phong_ban: "Trung tâm Phần mềm", chuyen_nganh: "Hệ thống thông tin", ngay: "01/10/2026", vao: "--:--", ra: "--:--", gio: 0, trang_thai: "VangMat", ghi_chu: "Nghỉ ốm (Đã nộp đơn xin nghỉ)" },
  { ma_sv: "DTC2051060012", ho_ten: "Phạm Thùy Linh", phong_ban: "Phòng Đào tạo & R&D", chuyen_nganh: "Kỹ thuật phần mềm", ngay: "01/10/2026", vao: "07:50", ra: "17:35", gio: 8.6, trang_thai: "DungGio", ghi_chu: "Đến sớm 10 phút, hỗ trợ chuẩn bị lab" },
  { ma_sv: "DTC2051060244", ho_ten: "Vũ Quang Huy", phong_ban: "Trung tâm Phần mềm", chuyen_nganh: "Kỹ thuật phần mềm", ngay: "01/10/2026", vao: "07:52", ra: "17:40", gio: 8.8, trang_thai: "DungGio", ghi_chu: "Trưởng nhóm thực tập sinh - hoàn thành tốt" },
  { ma_sv: "DTC2051060199", ho_ten: "Đặng Thị Hoa", phong_ban: "Phòng AI & Big Data", chuyen_nganh: "Khoa học máy tính", ngay: "01/10/2026", vao: "08:25", ra: "17:30", gio: 7.9, trang_thai: "DiMuon", ghi_chu: "Đi muộn 25 phút" },
  { ma_sv: "DTC2051060098", ho_ten: "Bùi Tiến Đạt", phong_ban: "Phòng Hạ tầng Mạng & Cloud", chuyen_nganh: "An toàn thông tin", ngay: "01/10/2026", vao: "08:02", ra: "17:30", gio: 8.4, trang_thai: "DungGio", ghi_chu: "Đúng giờ làm việc" }
];

let danhSachHienTai = [...mockDataChamCong];

async function kiemTraKetNoiApi() {
  const badge = document.getElementById("badgeTrangThaiApi");
  if (!badge) return;
  try {
    const res = await fetch(`${duongDanApi}/attendance/reports?thang=10&nam=2026&page=1&page_size=1`, {
      method: "GET"
    });
    if (res.ok) {
      badge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Backend: Đã kết nối API`;
      badge.classList.remove("hidden");
      return true;
    }
  } catch (e) {}
  badge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
  badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Chế độ Thử nghiệm (Offline)`;
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

async function taiDuLieuChamCong() {
  const thangEl = document.getElementById("boLocThang");
  const namEl = document.getElementById("boLocNam");
  const thang = thangEl ? parseInt(thangEl.value, 10) : 10;
  const nam = namEl ? parseInt(namEl.value, 10) : 2026;

  try {
    const res = await fetch(`${duongDanApi}/attendance/reports?thang=${thang}&nam=${nam}&page=1&page_size=100`);
    if (res.ok) {
      const json = await res.json();
      if (json && json.data && Array.isArray(json.data.items) && json.data.items.length > 0) {
        danhSachHienTai = json.data.items.map((it, idx) => {
          const soDiMuon = it.so_lan_di_muon || 0;
          const soNghi = it.so_ngay_nghi || 0;
          let tt = "DungGio";
          let ghiChu = "Đúng giờ ca làm việc";
          if (soNghi > 0) {
            tt = "VangMat";
            ghiChu = `Đã nghỉ ${soNghi} ngày`;
          } else if (soDiMuon > 0) {
            tt = "DiMuon";
            ghiChu = `Đi muộn ${soDiMuon} lần`;
          }

          return {
            ma_sv: `DTC20510${String(1000 + (it.ma_ho_so || idx)).slice(-4)}`,
            ho_ten: it.ho_ten || `Thực tập sinh #${it.ma_ho_so}`,
            phong_ban: it.ten_phong_ban || "Trung tâm Phần mềm",
            chuyen_nganh: it.chuyen_nganh || "Công nghệ thông tin",
            ngay: `01/${String(thang).padStart(2, "0")}/${nam}`,
            vao: soDiMuon > 0 ? "08:15" : (tt === "VangMat" ? "--:--" : "07:55"),
            ra: tt === "VangMat" ? "--:--" : "17:30",
            gio: tt === "VangMat" ? 0 : 8.5,
            trang_thai: tt,
            ghi_chu: ghiChu
          };
        });
      } else {
        danhSachHienTai = [...mockDataChamCong];
      }
    } else {
      danhSachHienTai = [...mockDataChamCong];
    }
  } catch (e) {
    danhSachHienTai = [...mockDataChamCong];
  }

  locDuLieu();
}

function locDuLieu() {
  const ttEl = document.getElementById("boLocTrangThai");
  const kwEl = document.getElementById("timKiem");
  const tt = ttEl ? ttEl.value : "tat-ca";
  const kw = kwEl ? kwEl.value.trim().toLowerCase() : "";

  const ketQua = danhSachHienTai.filter(item => {
    const khopTT = tt === "tat-ca" || item.trang_thai === tt;
    const khopKW = !kw ||
      (item.ma_sv && item.ma_sv.toLowerCase().includes(kw)) ||
      (item.ho_ten && item.ho_ten.toLowerCase().includes(kw)) ||
      (item.phong_ban && item.phong_ban.toLowerCase().includes(kw)) ||
      (item.chuyen_nganh && item.chuyen_nganh.toLowerCase().includes(kw));
    return khopTT && khopKW;
  });

  renderGiaoDien(ketQua);
}

function renderGiaoDien(list) {
  const cardTong = document.getElementById("cardTong");
  const cardDungGio = document.getElementById("cardDungGio");
  const cardDiMuon = document.getElementById("cardDiMuon");
  const cardVang = document.getElementById("cardVang");

  const tong = list.length;
  const dungGio = list.filter(i => i.trang_thai === "DungGio").length;
  const diMuon = list.filter(i => i.trang_thai === "DiMuon").length;
  const vang = list.filter(i => i.trang_thai === "VangMat").length;

  if (cardTong) cardTong.textContent = tong;
  if (cardDungGio) cardDungGio.textContent = dungGio;
  if (cardDiMuon) cardDiMuon.textContent = diMuon;
  if (cardVang) cardVang.textContent = vang;

  const theDem = document.getElementById("theDemBanGhi");
  if (theDem) theDem.textContent = `${list.length} bản ghi`;

  const moTa = document.getElementById("moTaKetQuaBang");
  if (moTa) {
    const thang = document.getElementById("boLocThang") ? document.getElementById("boLocThang").value : "10";
    const nam = document.getElementById("boLocNam") ? document.getElementById("boLocNam").value : "2026";
    moTa.textContent = `Báo cáo chuyên cần Tháng ${thang}/${nam} • Hiển thị ${list.length} thực tập sinh`;
  }

  const tbody = document.getElementById("bangChamCongBody");
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" class="p-8 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl text-slate-300">search_off</span>
            <p class="font-medium text-sm text-slate-500">Không tìm thấy bản ghi chấm công nào phù hợp</p>
            <p class="text-xs text-slate-400">Vui lòng thử chọn tháng/năm khác hoặc thay đổi bộ lọc tìm kiếm.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = list.map(item => {
    let badgeHtml = "";
    if (item.trang_thai === "DungGio") {
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold text-[11px]"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Đúng giờ</span>`;
    } else if (item.trang_thai === "DiMuon") {
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold text-[11px]"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Đi muộn</span>`;
    } else {
      badgeHtml = `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 font-semibold text-[11px]"><span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>Vắng mặt</span>`;
    }

    return `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="p-3.5 text-center font-mono font-bold text-ictu-600">${item.ma_sv}</td>
        <td class="p-3.5">
          <div class="font-bold text-slate-900">${item.ho_ten}</div>
          <div class="text-[11px] text-slate-400 font-normal">${item.chuyen_nganh || ""}</div>
        </td>
        <td class="p-3.5 text-slate-600">${item.phong_ban || "Trung tâm Phần mềm"}</td>
        <td class="p-3.5 text-center font-mono text-slate-600">${item.ngay}</td>
        <td class="p-3.5 text-center font-mono font-semibold text-slate-800">${item.vao}</td>
        <td class="p-3.5 text-center font-mono font-semibold text-slate-800">${item.ra}</td>
        <td class="p-3.5 text-center font-mono font-bold ${item.gio > 0 ? "text-emerald-700" : "text-slate-400"}">${item.gio} hrs</td>
        <td class="p-3.5 text-center">${badgeHtml}</td>
        <td class="p-3.5 text-slate-500 max-w-xs truncate" title="${item.ghi_chu}">${item.ghi_chu}</td>
      </tr>
    `;
  }).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  capNhatHocKyChamCong();
  kiemTraKetNoiApi();
  taiDuLieuChamCong();
});
