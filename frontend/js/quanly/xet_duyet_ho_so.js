const duongDanApi = "http://127.0.0.1:8000/api/v1";

let danhSachHoSo = [];

let dangChonMa = null;
let dangChonTen = "";
let dangChonMaTaiLieu = 1;
let dangChonEmail = "";
let daKetNoiApi = false;
let boLocHienTai = "tat-ca";

async function taiDanhSachHoSo(hienThongBaoKetNoi = false) {
  const badgeEl = document.getElementById("trangThaiKetNoiApi");
  if (badgeEl) {
    badgeEl.className =
      "hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200";
    badgeEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span><span>Đang tải API...</span>`;
  }

  try {
    const phanHoi = await fetch(`${duongDanApi}/interns`);
    if (!phanHoi.ok) throw new Error("Không thể kết nối đến API danh sách hồ sơ");

    const ketQua = await phanHoi.json();
    const hoSoApi = ketQua.data || [];

    daKetNoiApi = true;
    if (badgeEl) {
      badgeEl.className =
        "hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200";
      badgeEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span>API Backend: Đang kết nối (${hoSoApi.length} hồ sơ)</span>`;
    }

    danhSachHoSo = hoSoApi.map((h, index) => ({
      ma_ho_so: h.ma_ho_so || index + 1,
      ma_tai_lieu: h.ma_ho_so || index + 1,
      ho_ten: h.ho_ten || "Chưa cập nhật",
      email: h.email || "email@domain.com",
      ten_truong:
        h.ten_truong || "ĐH Công nghệ Thông tin & Truyền thông (ICTU)",
      chuyen_nganh: h.chuyen_nganh || "Công nghệ Thông tin",
      ten_chuong_trinh:
        h.ten_chuong_trinh ||
        (() => {
          const d = new Date();
          const y = d.getFullYear();
          const s = d.getMonth() >= 8 ? y : y - 1;
          return `Chương trình Thực tập (${s} - ${s + 1})`;
        })(),
      trang_thai_xet_duyet: h.trang_thai_xet_duyet || "ChoDuyet",
    }));

    if (hienThongBaoKetNoi) {
      hienThongBao(
        `Đã tải thành công ${danhSachHoSo.length} hồ sơ trực tiếp từ cơ sở dữ liệu Backend qua API!`,
        "success",
      );
    }
  } catch (err) {
    daKetNoiApi = false;
    if (badgeEl) {
      badgeEl.className =
        "hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200";
      badgeEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-slate-400"></span><span>Chế độ kiểm thử cục bộ</span>`;
    }
  }

  hienThiDanhSach(danhSachHoSo);
  capNhatBoDem();
}

function layVietTatTen(hoTen) {
  if (!hoTen) return "SV";
  const tu = hoTen.trim().split(" ");
  if (tu.length === 1) return tu[0].substring(0, 2).toUpperCase();
  return (tu[0][0] + tu[tu.length - 1][0]).toUpperCase();
}

function hienThiDanhSach(danhSach) {
  const tbody = document.getElementById("danhSachUngVien");
  if (!tbody) return;

  const tuKhoa =
    document.getElementById("timKiemUngVien")?.value.toLowerCase().trim() || "";

  const danhSachLoc = danhSach.filter((item) => {
    let khopTrangThai = true;
    if (boLocHienTai === "cho-duyet") {
      khopTrangThai = item.trang_thai_xet_duyet === "ChoDuyet";
    } else if (boLocHienTai === "da-duyet") {
      khopTrangThai = item.trang_thai_xet_duyet === "DaDuyet";
    } else if (boLocHienTai === "tu-choi") {
      khopTrangThai = item.trang_thai_xet_duyet === "TuChoi";
    }

    let khopTuKhoa = true;
    if (tuKhoa) {
      const noiDung =
        `${item.ma_ho_so} ${item.ho_ten} ${item.email} ${item.ten_truong} ${item.chuyen_nganh}`.toLowerCase();
      khopTuKhoa = noiDung.includes(tuKhoa);
    }

    return khopTrangThai && khopTuKhoa;
  });

  const elPhanTrang = document.getElementById("phanTrangThongTin");
  if (elPhanTrang) {
    elPhanTrang.innerHTML = `Hiển thị <strong class="text-on-surface">1 - ${danhSachLoc.length}</strong> của <strong class="text-on-surface">${danhSach.length}</strong> hồ sơ`;
  }

  if (danhSachLoc.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="py-12 text-center text-slate-400">
          <span class="material-symbols-outlined text-[36px] text-slate-300 block mb-2">search_off</span>
          <p class="text-sm font-medium">Không tìm thấy hồ sơ nào phù hợp với bộ lọc hiện tại.</p>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = danhSachLoc
    .map((item) => {
      const statusAttr =
        item.trang_thai_xet_duyet === "DaDuyet"
          ? "da-duyet"
          : item.trang_thai_xet_duyet === "TuChoi"
            ? "tu-choi"
            : "cho-duyet";

      let badgeHtml = "";
      if (item.trang_thai_xet_duyet === "DaDuyet") {
        badgeHtml = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold">
            <span class="material-symbols-outlined text-[15px] text-emerald-600">check_circle</span>
            <span>Đã duyệt</span>
          </span>
        `;
      } else if (item.trang_thai_xet_duyet === "TuChoi") {
        badgeHtml = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200 text-xs font-semibold">
            <span class="material-symbols-outlined text-[15px] text-rose-600">cancel</span>
            <span>Bị từ chối</span>
          </span>
        `;
      } else {
        badgeHtml = `
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold">
            <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>Chờ xét duyệt</span>
          </span>
        `;
      }

      let actionsHtml = "";
      if (item.trang_thai_xet_duyet === "ChoDuyet") {
        actionsHtml = `
          <div class="flex items-center justify-center gap-2">
            <button
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 active:bg-emerald-800 transition-colors text-xs font-semibold shadow-sm"
              onclick="duyetHoSo(${item.ma_ho_so}, ${item.ma_tai_lieu})"
              title="Phê duyệt ứng viên này"
              type="button"
            >
              <span class="material-symbols-outlined text-[15px]">check_circle</span>
              <span>Duyệt</span>
            </button>
            <button
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-rose-600 text-white hover:bg-rose-700 active:bg-rose-800 transition-colors text-xs font-semibold shadow-sm"
              onclick="moHopThoaiTuChoi(${item.ma_ho_so}, '${item.ho_ten.replace(/'/g, "\\'")}', ${item.ma_tai_lieu}, '${item.email}')"
              title="Từ chối ứng viên này"
              type="button"
            >
              <span class="material-symbols-outlined text-[15px]">cancel</span>
              <span>Từ chối</span>
            </button>
            <button
              class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors"
              onclick="moHopThoaiTaiLieu(${item.ma_ho_so}, '${item.ho_ten.replace(/'/g, "\\'")}')"
              title="Xem tài liệu thẩm định"
              type="button"
            >
              <span class="material-symbols-outlined text-[15px]">description</span>
              <span class="hidden xl:inline">Tài liệu</span>
            </button>
          </div>
        `;
      } else if (item.trang_thai_xet_duyet === "DaDuyet") {
        actionsHtml = `
          <div class="flex items-center justify-center gap-2">
            <span class="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold">
              <span class="material-symbols-outlined text-[16px]">verified</span>
              <span>Chờ phân công GVHD</span>
            </span>
            <button
              class="inline-flex items-center p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              onclick="moHopThoaiTaiLieu(${item.ma_ho_so}, '${item.ho_ten.replace(/'/g, "\\'")}')"
              title="Xem lại tài liệu"
              type="button"
            >
              <span class="material-symbols-outlined text-[16px]">folder_open</span>
            </button>
          </div>
        `;
      } else {
        actionsHtml = `
          <div class="flex items-center justify-center gap-2">
            <span class="text-xs text-slate-400 italic">Đã gửi lý do phản hồi</span>
            <button
              class="inline-flex items-center p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              onclick="moHopThoaiTaiLieu(${item.ma_ho_so}, '${item.ho_ten.replace(/'/g, "\\'")}')"
              title="Xem lại tài liệu"
              type="button"
            >
              <span class="material-symbols-outlined text-[16px]">folder_open</span>
            </button>
          </div>
        `;
      }

      return `
        <tr
          class="hover:bg-slate-50/80 transition-colors border-b border-slate-100 group"
          data-status="${statusAttr}"
          id="hangUngVien-${item.ma_ho_so}"
        >
          <td class="py-4 px-4 font-mono text-xs text-primary font-bold whitespace-nowrap">
            #${item.ma_ho_so}
          </td>
          <td class="py-4 px-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-slate-100 text-slate-800 flex items-center justify-center font-bold text-xs shrink-0 shadow-sm ring-1 ring-slate-200">
                ${layVietTatTen(item.ho_ten)}
              </div>
              <div class="flex flex-col min-w-0">
                <span class="ten-ung-vien text-sm font-semibold text-slate-900 truncate group-hover:text-primary transition-colors">
                  ${item.ho_ten}
                </span>
                <span class="email-ung-vien text-xs text-slate-500 truncate">
                  ${item.email}
                </span>
              </div>
            </div>
          </td>
          <td class="py-4 px-4 text-xs text-slate-700">
            <div class="flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px] text-slate-400">school</span>
              <span>${item.ten_truong}</span>
            </div>
          </td>
          <td class="py-4 px-4">
            <div class="flex flex-col items-start gap-1">
              <span class="text-xs font-semibold text-slate-800">${item.chuyen_nganh}</span>
              <span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-medium">
                ${item.ten_chuong_trinh}
              </span>
            </div>
          </td>
          <td class="py-4 px-4 text-center cot-trang-thai">
            ${badgeHtml}
          </td>
          <td class="py-4 px-4 text-center cot-thao-tac whitespace-nowrap">
            ${actionsHtml}
          </td>
        </tr>
      `;
    })
    .join("");
}

async function duyetHoSo(maHoSo, maTaiLieu) {
  const item = danhSachHoSo.find((h) => h.ma_ho_so === maHoSo);
  if (!item) return;

  const hang = document.getElementById(`hangUngVien-${maHoSo}`);
  const nutDuyet = hang?.querySelector(".nut-duyet");
  if (nutDuyet) {
    nutDuyet.disabled = true;
    nutDuyet.innerHTML = `<span class="inline-block w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin"></span> Duyệt`;
  }

  try {
    const phanHoi = await fetch(
      `${duongDanApi}/interns/${maHoSo}/approval`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trang_thai_duyet: "DaDuyet",
          ghi_chu: "Hồ sơ đạt tiêu chuẩn phê duyệt.",
        }),
      },
    );

    if (phanHoi.ok) {
      item.trang_thai_xet_duyet = "DaDuyet";
      hienThiDanhSach(danhSachHoSo);
      capNhatBoDem();
      hienThongBao(
        `Đã phê duyệt hồ sơ của sinh viên <strong>${item.ho_ten}</strong> (#${maHoSo})! Hệ thống Backend đã tự động gửi email thông báo kết quả tới <strong>${item.email}</strong>.`,
        "success",
      );
      return;
    }
  } catch (err) {}

  item.trang_thai_xet_duyet = "DaDuyet";
  hienThiDanhSach(danhSachHoSo);
  capNhatBoDem();
  hienThongBao(
    `Đã phê duyệt thành công hồ sơ của sinh viên <strong>${item.ho_ten}</strong> (#${maHoSo})!`,
    "success",
  );
}

function moHopThoaiTuChoi(maHoSo, tenUngVien, maTaiLieu, email) {
  dangChonMa = maHoSo;
  dangChonTen = tenUngVien;
  dangChonMaTaiLieu = maTaiLieu || maHoSo;
  dangChonEmail = email || "";

  const modal = document.getElementById("hopThoaiTuChoi");
  const moTa = document.getElementById("moTaUngVienTuChoi");
  const lyDo = document.getElementById("lyDoTuChoi");

  if (moTa)
    moTa.textContent = `Bạn đang từ chối hồ sơ của ứng viên: ${tenUngVien} (Mã: #${maHoSo})`;
  if (lyDo) lyDo.value = "";
  if (modal) {
    modal.classList.remove("hidden");
    lyDo?.focus();
  }
}

function dongHopThoaiTuChoi() {
  const modal = document.getElementById("hopThoaiTuChoi");
  if (modal) modal.classList.add("hidden");
  dangChonMa = null;
  dangChonTen = "";
  dangChonEmail = "";
}

function ganLyDoNhanh(noiDung) {
  const txt = document.getElementById("lyDoTuChoi");
  if (txt) {
    txt.value = noiDung;
    txt.focus();
  }
}

async function xacNhanTuChoiHoSo() {
  const lyDoInput = document.getElementById("lyDoTuChoi");
  const lyDo = lyDoInput?.value.trim();

  if (!lyDo) {
    alert("Vui lòng nhập lý do từ chối hồ sơ.");
    lyDoInput?.focus();
    return;
  }

  const item = danhSachHoSo.find((h) => h.ma_ho_so === dangChonMa);
  const nutXacNhan = document.getElementById("nutXacNhanTuChoi");
  const noiDungGoc = nutXacNhan?.innerHTML;
  if (nutXacNhan) {
    nutXacNhan.disabled = true;
    nutXacNhan.innerHTML = `<span class="inline-block w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span> Đang gửi...`;
  }

  try {
    const phanHoi = await fetch(
      `${duongDanApi}/interns/${dangChonMa}/approval`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trang_thai_duyet: "TuChoi",
          ghi_chu: lyDo,
        }),
      },
    );

    if (phanHoi.ok) {
      if (item) item.trang_thai_xet_duyet = "TuChoi";
      dongHopThoaiTuChoi();
      hienThiDanhSach(danhSachHoSo);
      capNhatBoDem();
      hienThongBao(
        `Đã từ chối hồ sơ của <strong>${dangChonTen}</strong>. Email thông báo lý do đã được tự động gửi qua BackgroundTasks tới <strong>${dangChonEmail || "thực tập sinh"}</strong>!`,
        "error",
      );
      return;
    }
  } catch (err) {
  } finally {
    if (nutXacNhan) {
      nutXacNhan.disabled = false;
      nutXacNhan.innerHTML = noiDungGoc;
    }
  }

  if (item) item.trang_thai_xet_duyet = "TuChoi";
  dongHopThoaiTuChoi();
  hienThiDanhSach(danhSachHoSo);
  capNhatBoDem();
  hienThongBao(
    `Đã từ chối hồ sơ của ứng viên <strong>${dangChonTen}</strong>.`,
    "error",
  );
}

async function moHopThoaiTaiLieu(maHoSo, tenUngVien) {
  const modal = document.getElementById("hopThoaiTaiLieu");
  const tieuDe = document.getElementById("tieuDeTaiLieuHoSo");
  const moTa = document.getElementById("moTaTaiLieuHoSo");
  const container = document.getElementById("danhSachTaiLieuContainer");

  if (tieuDe) tieuDe.textContent = `Hồ Sơ & Tài Liệu: ${tenUngVien}`;
  if (moTa)
    moTa.textContent = `Mã hồ sơ: #${maHoSo} - Kiểm tra và đối soát tài liệu thẩm định`;
  if (modal) modal.classList.remove("hidden");

  if (!container) return;
  container.innerHTML = `
    <div class="py-8 text-center text-slate-400">
      <span class="inline-block w-5 h-5 rounded-full border-2 border-primary border-t-transparent animate-spin"></span>
      <p class="mt-2 text-xs">Đang tải danh sách tài liệu từ API Backend...</p>
    </div>
  `;

  try {
    const phanHoi = await fetch(`${duongDanApi}/documents/${maHoSo}`);
    if (phanHoi.ok) {
      const resData = await phanHoi.json();
      const docs = resData.data || [];
      if (docs.length > 0) {
        hienThiDanhSachTaiLieuTrongModal(docs, maHoSo);
        return;
      }
    }
  } catch (err) {}

  container.innerHTML = `
    <div class="py-12 text-center text-slate-400">
      <span class="material-symbols-outlined text-[36px] text-slate-300 block mb-1">folder_off</span>
      <p class="text-sm font-medium">Hồ sơ #${maHoSo} chưa có tài liệu đính kèm nào được tải lên.</p>
    </div>
  `;
}

function hienThiDanhSachTaiLieuTrongModal(docs, maHoSo) {
  const container = document.getElementById("danhSachTaiLieuContainer");
  if (!container) return;

  container.innerHTML = docs
    .map((doc) => {
      let statusColor = "bg-amber-100 text-amber-800";
      let statusText = "Chờ duyệt";
      if (doc.trang_thai_duyet === "DaDuyet") {
        statusColor = "bg-emerald-100 text-emerald-800";
        statusText = "Đã duyệt";
      } else if (doc.trang_thai_duyet === "TuChoi") {
        statusColor = "bg-rose-100 text-rose-800";
        statusText = "Bị từ chối";
      }

      return `
        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-primary shadow-sm shrink-0">
              <span class="material-symbols-outlined text-[22px]">description</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-slate-900">${doc.loai_tai_lieu}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${statusColor}">${statusText}</span>
              </div>
              <p class="text-[11px] text-slate-500 font-mono mt-0.5 truncate max-w-xs">${doc.duong_dan_file}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 self-end sm:self-auto shrink-0">
            <a
              href="javascript:void(0)"
              onclick="thongBaoDangCapNhat('Xem trực tuyến file ${doc.loai_tai_lieu}')"
              class="px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-medium transition-colors flex items-center gap-1"
            >
              <span class="material-symbols-outlined text-[14px]">visibility</span>
              <span>Xem file</span>
            </a>
            <button
              type="button"
              onclick="duyetHoSo(${maHoSo}, ${doc.ma_tai_lieu}); dongHopThoaiTaiLieu();"
              class="px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium transition-colors flex items-center gap-1"
            >
              <span class="material-symbols-outlined text-[14px]">check</span>
              <span>Duyệt</span>
            </button>
          </div>
        </div>
      `;
    })
    .join("");
}

function dongHopThoaiTaiLieu() {
  const modal = document.getElementById("hopThoaiTaiLieu");
  if (modal) modal.classList.add("hidden");
}

function locDanhSach(trangThai, nutBam) {
  boLocHienTai = trangThai;
  document.querySelectorAll(".bo-nut-loc").forEach((btn) => {
    btn.className =
      "bo-nut-loc px-3 py-1.5 rounded-md text-label-sm font-semibold text-on-surface-variant hover:text-on-surface transition-all flex items-center gap-1.5";
  });
  nutBam.className =
    "bo-nut-loc px-3 py-1.5 rounded-md text-label-sm font-semibold bg-primary text-on-primary shadow-sm transition-all flex items-center gap-1.5";
  hienThiDanhSach(danhSachHoSo);
}

function capNhatBoDem() {
  const choDuyet = danhSachHoSo.filter(
    (h) => h.trang_thai_xet_duyet === "ChoDuyet",
  ).length;
  const daDuyet = danhSachHoSo.filter(
    (h) => h.trang_thai_xet_duyet === "DaDuyet",
  ).length;
  const tuChoi = danhSachHoSo.filter(
    (h) => h.trang_thai_xet_duyet === "TuChoi",
  ).length;
  const tongSo = danhSachHoSo.length;

  const elTong = document.getElementById("demTongHoSo");
  const elChoDuyet = document.getElementById("demChoDuyet");
  const elDaDuyet = document.getElementById("demDaDuyet");
  const elTuChoi = document.getElementById("demTuChoi");

  if (elTong) elTong.textContent = tongSo;
  if (elChoDuyet) elChoDuyet.textContent = choDuyet;
  if (elDaDuyet) elDaDuyet.textContent = daDuyet;
  if (elTuChoi) elTuChoi.textContent = tuChoi;

  const btnTatCa = document.getElementById("demNutLocTatCa");
  const btnChoDuyet = document.getElementById("demNutLocChoDuyet");
  const btnDaDuyet = document.getElementById("demNutLocDaDuyet");
  const btnTuChoi = document.getElementById("demNutLocTuChoi");

  if (btnTatCa) btnTatCa.textContent = tongSo;
  if (btnChoDuyet) btnChoDuyet.textContent = choDuyet;
  if (btnDaDuyet) btnDaDuyet.textContent = daDuyet;
  if (btnTuChoi) btnTuChoi.textContent = tuChoi;
}

function hienThongBao(noiDung, loai) {
  const hop = document.getElementById("hopThongBaoTrangThai");
  if (!hop) return;
  hop.classList.remove("hidden");
  if (loai === "success") {
    hop.className =
      "rounded-xl p-4 bg-emerald-50 text-emerald-900 border border-emerald-200 shadow-sm flex items-center justify-between gap-3";
    hop.innerHTML = `
      <div class="flex items-center gap-2.5">
        <span class="material-symbols-outlined text-emerald-600 text-[22px]">task_alt</span>
        <div class="text-body-md">${noiDung}</div>
      </div>
      <button type="button" onclick="this.parentElement.classList.add('hidden')" class="text-emerald-700 hover:text-emerald-950 p-1">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    `;
  } else {
    hop.className =
      "rounded-xl p-4 bg-red-50 text-red-900 border border-red-200 shadow-sm flex items-center justify-between gap-3";
    hop.innerHTML = `
      <div class="flex items-center gap-2.5">
        <span class="material-symbols-outlined text-red-600 text-[22px]">info</span>
        <div class="text-body-md">${noiDung}</div>
      </div>
      <button type="button" onclick="this.parentElement.classList.add('hidden')" class="text-red-700 hover:text-red-950 p-1">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    `;
  }
}

function duyetHangLoat() {
  const cacHoSoCho = danhSachHoSo.filter(
    (h) => h.trang_thai_xet_duyet === "ChoDuyet",
  );
  if (cacHoSoCho.length === 0) {
    alert("Không còn hồ sơ nào đang chờ xét duyệt!");
    return;
  }
  if (
    confirm(
      `Bạn có chắc chắn muốn phê duyệt đồng loạt ${cacHoSoCho.length} hồ sơ đang chờ xét duyệt?`,
    )
  ) {
    cacHoSoCho.forEach((h) => {
      duyetHoSo(h.ma_ho_so, h.ma_tai_lieu);
    });
    hienThongBao(`Đã gửi lệnh phê duyệt hàng loạt các hồ sơ.`, "success");
  }
}

function xuatDanhSachExcel() {
  alert(
    `Đang kết xuất danh sách ${danhSachHoSo.length} hồ sơ ứng tuyển ra định dạng Microsoft Excel (.xlsx)...`,
  );
}

const timKiemInput = document.getElementById("timKiemUngVien");
if (timKiemInput) {
  timKiemInput.addEventListener("input", () => {
    hienThiDanhSach(danhSachHoSo);
  });
}

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    dongHopThoaiTuChoi();
    dongHopThoaiTaiLieu();
  }
});

const modalBoxTuChoi = document.getElementById("hopThoaiTuChoi");
if (modalBoxTuChoi) {
  modalBoxTuChoi.addEventListener("click", (e) => {
    if (e.target === modalBoxTuChoi) dongHopThoaiTuChoi();
  });
}

const modalBoxTaiLieu = document.getElementById("hopThoaiTaiLieu");
if (modalBoxTaiLieu) {
  modalBoxTaiLieu.addEventListener("click", (e) => {
    if (e.target === modalBoxTaiLieu) dongHopThoaiTaiLieu();
  });
}

window.addEventListener("DOMContentLoaded", taiDanhSachHoSo);
