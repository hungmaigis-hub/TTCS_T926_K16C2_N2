const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

function layIdSinhVien() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);
  try {
    const raw =
      localStorage.getItem("ictu_student_session") ||
      localStorage.getItem("currentUser") ||
      localStorage.getItem("user");
    if (raw) {
      const u = JSON.parse(raw);
      if (u.ma_ho_so) return parseInt(u.ma_ho_so, 10);
      if (u.id) return parseInt(u.id, 10);
    }
  } catch (e) {}
  return 15;
}

function taoAvatarVietTat(hoTen) {
  if (!hoTen) return "SV";
  const words = hoTen.trim().split(/\s+/);
  return words.length >= 2
    ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
    : hoTen.substring(0, 2).toUpperCase();
}

function dongBoSidebar(hoTen, email, lop) {
  if (!hoTen) return;
  const elTen = document.getElementById("sidebarTenSinhVien");
  if (elTen) elTen.textContent = hoTen;
  const elAvatar = document.getElementById("avatarInitials");
  if (elAvatar) elAvatar.textContent = taoAvatarVietTat(hoTen);
  const elMa = document.getElementById("sidebarMaSinhVien");
  if (elMa) {
    if (lop) {
      elMa.textContent = lop;
    } else if (email) {
      elMa.textContent = email;
    }
  }
}

function thongBao(thongDiep, loai = "thanh_cong") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const mauSac = {
    thanh_cong: "bg-emerald-600 text-white shadow-emerald-600/20",
    loi: "bg-red-600 text-white shadow-red-600/20",
    canh_bao: "bg-amber-500 text-white shadow-amber-500/20",
    thong_tin: "bg-slate-800 text-white shadow-slate-800/20",
  }[loai] || "bg-slate-800 text-white";

  const bieuTuong = {
    thanh_cong: "check_circle",
    loi: "error",
    canh_bao: "warning",
    thong_tin: "info",
  }[loai] || "info";

  const toast = document.createElement("div");
  toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-auto ${mauSac}`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-[20px] shrink-0">${bieuTuong}</span>
    <span class="flex-1">${thongDiep}</span>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-4", "opacity-0");
  });

  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function layCauHinhXepLoai(xepLoai) {
  switch (xepLoai) {
    case "XuatSac":
      return {
        ten: "Xuất sắc",
        lopMau: "bg-emerald-100 text-emerald-800 border-emerald-200",
        mauText: "text-emerald-700",
        mauBar: "bg-emerald-500",
        moTa: "Đạt thành tích vượt trội toàn diện",
      };
    case "Gioi":
      return {
        ten: "Giỏi",
        lopMau: "bg-blue-100 text-blue-800 border-blue-200",
        mauText: "text-blue-700",
        mauBar: "bg-blue-500",
        moTa: "Năng lực chuyên môn vững vàng, thái độ tốt",
      };
    case "Kha":
      return {
        ten: "Khá",
        lopMau: "bg-amber-100 text-amber-800 border-amber-200",
        mauText: "text-amber-700",
        mauBar: "bg-amber-500",
        moTa: "Hoàn thành tốt các nhiệm vụ được giao",
      };
    case "TrungBinh":
      return {
        ten: "Trung bình",
        lopMau: "bg-orange-100 text-orange-800 border-orange-200",
        mauText: "text-orange-700",
        mauBar: "bg-orange-500",
        moTa: "Cần cải thiện kỹ năng và tính chủ động",
      };
    case "Yeu":
      return {
        ten: "Yếu",
        lopMau: "bg-red-100 text-red-800 border-red-200",
        mauText: "text-red-700",
        mauBar: "bg-red-500",
        moTa: "Chưa đạt yêu cầu của đợt thực tập",
      };
    default:
      return {
        ten: "Chưa đánh giá",
        lopMau: "bg-slate-100 text-slate-700 border-slate-200",
        mauText: "text-slate-600",
        mauBar: "bg-slate-400",
        moTa: "Đang chờ kết quả ghi nhận từ Mentor",
      };
  }
}

function layTenLoaiDanhGia(loai) {
  if (loai === "GiuaKy") return "Đánh Giá Giữa Kỳ";
  if (loai === "CuoiKy") return "Đánh Giá Cuối Kỳ";
  return loai || "Định kỳ";
}

function capNhatGiaoDien(duLieu) {
  if (!duLieu) return;

  const hoTen = duLieu.ho_ten || "Sinh viên";
  const email = duLieu.email || "--";
  const chuyenNganh = duLieu.chuyen_nganh || "Công nghệ Thông tin";
  const tenTruong = duLieu.ten_truong || "Trường ĐH Công nghệ Thông tin & Truyền thông";
  const trangThai = duLieu.trang_thai_thuc_tap || "DangThucTap";
  const coMentor = Boolean(duLieu.mentor && String(duLieu.mentor).trim());
  const tenMentor = coMentor ? duLieu.mentor : "Chưa phân công";
  const diemTB = duLieu.diem_trung_binh_chung || 0;
  const xepLoai = duLieu.xep_loai_chung || "ChuaDanhGia";
  const danhSach = duLieu.danh_sach_danh_gia || [];

  dongBoSidebar(hoTen, email, chuyenNganh);

  const elHeroAvatar = document.getElementById("heroAvatar");
  if (elHeroAvatar) elHeroAvatar.textContent = taoAvatarVietTat(hoTen);

  const elHeroTen = document.getElementById("heroTenSinhVien");
  if (elHeroTen) elHeroTen.textContent = hoTen;

  const elHeroChuyenNganh = document.getElementById("heroChuyenNganh");
  if (elHeroChuyenNganh) elHeroChuyenNganh.textContent = chuyenNganh;

  const elHeroTruong = document.getElementById("heroTruong");
  if (elHeroTruong) elHeroTruong.textContent = tenTruong;

  const elHeroEmail = document.getElementById("heroEmail");
  if (elHeroEmail) elHeroEmail.textContent = email;

  const elHeroMentor = document.getElementById("heroMentor");
  const elHeroMentorSub = document.getElementById("heroMentorSub");
  const elHeroMentorIcon = document.getElementById("heroMentorIcon");
  const elHeroMentorIconWrapper = document.getElementById("heroMentorIconWrapper");

  if (elHeroMentor) elHeroMentor.textContent = tenMentor;
  if (coMentor) {
    if (elHeroMentorSub) {
      elHeroMentorSub.textContent = "Bộ phận Công nghệ & Đào tạo";
      elHeroMentorSub.className = "text-[11px] text-emerald-300 block";
    }
    if (elHeroMentorIcon) elHeroMentorIcon.textContent = "person_pin";
    if (elHeroMentorIconWrapper) {
      elHeroMentorIconWrapper.className = "w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-emerald-300 shrink-0";
    }
  } else {
    if (elHeroMentorSub) {
      elHeroMentorSub.textContent = "Chờ doanh nghiệp chỉ định";
      elHeroMentorSub.className = "text-[11px] text-slate-400 block";
    }
    if (elHeroMentorIcon) elHeroMentorIcon.textContent = "person_off";
    if (elHeroMentorIconWrapper) {
      elHeroMentorIconWrapper.className = "w-10 h-10 rounded-lg bg-slate-500/20 border border-slate-400/30 flex items-center justify-center text-slate-300 shrink-0";
    }
  }

  const elHeroTrangThai = document.getElementById("heroTrangThai");
  if (elHeroTrangThai) {
    if (trangThai === "DangThucTap") {
      elHeroTrangThai.textContent = "Đang thực tập";
      elHeroTrangThai.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
    } else if (trangThai === "HoanThanh") {
      elHeroTrangThai.textContent = "Đã hoàn thành";
      elHeroTrangThai.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30";
    } else if (trangThai === "ChuaThucTap") {
      elHeroTrangThai.textContent = "Chưa thực tập";
      elHeroTrangThai.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30";
    } else {
      elHeroTrangThai.textContent = "Thực tập sinh";
      elHeroTrangThai.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/20 text-slate-300 border border-slate-500/30";
    }
  }

  const elXacNhanMa = document.getElementById("xacNhanMaHoSo");
  if (elXacNhanMa) elXacNhanMa.textContent = `#HS-${duLieu.ho_so_id || "00"}`;

  const elXacNhanHoTen = document.getElementById("xacNhanHoTen");
  if (elXacNhanHoTen) elXacNhanHoTen.textContent = hoTen;

  const elXacNhanChuyenNganh = document.getElementById("xacNhanChuyenNganh");
  if (elXacNhanChuyenNganh) elXacNhanChuyenNganh.textContent = chuyenNganh;

  const elXacNhanTruong = document.getElementById("xacNhanTruong");
  if (elXacNhanTruong) elXacNhanTruong.textContent = tenTruong;

  const elXacNhanMentor = document.getElementById("xacNhanMentor");
  if (elXacNhanMentor) elXacNhanMentor.textContent = tenMentor;

  const cfgXepLoai = layCauHinhXepLoai(xepLoai);
  const elKpiDiemTB = document.getElementById("kpiDiemTrungBinh");
  if (elKpiDiemTB) elKpiDiemTB.textContent = diemTB > 0 ? diemTB.toFixed(2) : "0.0";

  const elKpiBadgeXepLoai = document.getElementById("kpiBadgeXepLoai");
  if (elKpiBadgeXepLoai) {
    elKpiBadgeXepLoai.textContent = cfgXepLoai.ten;
    elKpiBadgeXepLoai.className = `px-2.5 py-0.5 rounded-full text-xs font-bold border ${cfgXepLoai.lopMau}`;
  }

  const elKpiBarDiemTB = document.getElementById("kpiBarDiemTB");
  if (elKpiBarDiemTB) {
    const phanTram = Math.min(100, Math.max(0, (diemTB / 10) * 100));
    elKpiBarDiemTB.style.width = `${phanTram}%`;
    elKpiBarDiemTB.className = `${cfgXepLoai.mauBar} h-1.5 rounded-full transition-all duration-500`;
  }

  const elKpiMoTaXepLoai = document.getElementById("kpiMoTaXepLoai");
  if (elKpiMoTaXepLoai) elKpiMoTaXepLoai.textContent = cfgXepLoai.moTa;

  let tongKyNang = 0;
  let tongThaiDo = 0;
  let coDeXuatTuyenDung = false;

  danhSach.forEach((item) => {
    tongKyNang += item.diem_ky_nang || 0;
    tongThaiDo += item.diem_thai_do || 0;
    if (item.de_xuat_tuyen_chinh_thuc === true) {
      coDeXuatTuyenDung = true;
    }
  });

  const diemKyNangTB = danhSach.length > 0 ? (tongKyNang / danhSach.length).toFixed(1) : "0.0";
  const diemThaiDoTB = danhSach.length > 0 ? (tongThaiDo / danhSach.length).toFixed(1) : "0.0";

  const elKpiKyNang = document.getElementById("kpiDiemKyNang");
  if (elKpiKyNang) elKpiKyNang.textContent = diemKyNangTB;

  const elKpiBarKyNang = document.getElementById("kpiBarKyNang");
  if (elKpiBarKyNang) {
    const ptKyNang = Math.min(100, Math.max(0, (parseFloat(diemKyNangTB) / 10) * 100));
    elKpiBarKyNang.style.width = `${ptKyNang}%`;
  }

  const elKpiThaiDo = document.getElementById("kpiDiemThaiDo");
  if (elKpiThaiDo) elKpiThaiDo.textContent = diemThaiDoTB;

  const elKpiBarThaiDo = document.getElementById("kpiBarThaiDo");
  if (elKpiBarThaiDo) {
    const ptThaiDo = Math.min(100, Math.max(0, (parseFloat(diemThaiDoTB) / 10) * 100));
    elKpiBarThaiDo.style.width = `${ptThaiDo}%`;
  }

  const elKpiBadgeDeXuat = document.getElementById("kpiBadgeDeXuat");
  const elKpiMoTaDeXuat = document.getElementById("kpiMoTaDeXuat");
  if (elKpiBadgeDeXuat) {
    if (danhSach.length === 0) {
      elKpiBadgeDeXuat.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold bg-slate-100 text-slate-600";
      elKpiBadgeDeXuat.innerHTML = `<span class="material-symbols-outlined text-[16px]">schedule</span>Chờ đánh giá`;
      if (elKpiMoTaDeXuat) elKpiMoTaDeXuat.textContent = "Mentor chưa ghi nhận đợt đánh giá";
    } else if (coDeXuatTuyenDung) {
      elKpiBadgeDeXuat.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200";
      elKpiBadgeDeXuat.innerHTML = `<span class="material-symbols-outlined text-[16px] text-emerald-600">verified</span>Được đề xuất tuyển`;
      if (elKpiMoTaDeXuat) elKpiMoTaDeXuat.textContent = "Mentor đề xuất tiếp nhận nhân viên chính thức";
    } else {
      elKpiBadgeDeXuat.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200";
      elKpiBadgeDeXuat.innerHTML = `<span class="material-symbols-outlined text-[16px] text-amber-600">info</span>Chưa đề xuất`;
      if (elKpiMoTaDeXuat) elKpiMoTaDeXuat.textContent = "Chờ xem xét vào đợt đánh giá cuối kỳ";
    }
  }

  const elBadgeSoDot = document.getElementById("soDotDanhGiaBadge");
  if (elBadgeSoDot) {
    elBadgeSoDot.textContent = `${danhSach.length} kỳ đánh giá`;
  }

  renderDanhSachDanhGia(danhSach, coMentor ? duLieu.mentor : "");
}

function renderDanhSachDanhGia(danhSach, mentorMacDinh) {
  const container = document.getElementById("danhSachDanhGiaContainer");
  if (!container) return;

  if (!danhSach || danhSach.length === 0) {
    container.innerHTML = `
      <div class="p-10 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
        <div class="w-16 h-16 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center mb-3">
          <span class="material-symbols-outlined text-3xl">rate_review</span>
        </div>
        <h4 class="text-base font-bold text-slate-800">Chưa có kết quả đánh giá nào từ Mentor</h4>
        <p class="text-xs text-slate-500 max-w-md mx-auto mt-1 leading-relaxed">
          Đợt đánh giá giữa kỳ sẽ được thực hiện sau 4 - 6 tuần thực tập. Khi Mentor ghi nhận kết quả, thông tin chi tiết sẽ hiển thị tại đây.
        </p>
      </div>
    `;
    return;
  }

  let coGiuaKy = false;
  let coCuoiKy = false;

  let htmlCards = "";

  danhSach.forEach((item) => {
    if (item.loai_danh_gia === "GiuaKy") coGiuaKy = true;
    if (item.loai_danh_gia === "CuoiKy") coCuoiKy = true;

    const tenLoai = layTenLoaiDanhGia(item.loai_danh_gia);
    const nguoiDanhGia = item.ten_nguoi_danh_gia || mentorMacDinh || "Cán bộ phụ trách";
    const cfgItem = layCauHinhXepLoai(item.xep_loai);
    const diemTBItem = (item.diem_trung_binh !== undefined && item.diem_trung_binh !== null)
      ? Number(item.diem_trung_binh).toFixed(2)
      : "0.0";
    const diemKN = (item.diem_ky_nang !== undefined && item.diem_ky_nang !== null)
      ? Number(item.diem_ky_nang).toFixed(1)
      : "0.0";
    const diemTD = (item.diem_thai_do !== undefined && item.diem_thai_do !== null)
      ? Number(item.diem_thai_do).toFixed(1)
      : "0.0";

    const nhanXet = item.nhan_xet_chi_tiet || "Mentor chưa để lại nhận xét chi tiết cho đợt đánh giá này.";

    const badgeDeXuat = item.de_xuat_tuyen_chinh_thuc
      ? `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
           <span class="material-symbols-outlined text-[14px]">recommend</span>Đề xuất tuyển chính thức
         </span>`
      : `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
           <span class="material-symbols-outlined text-[14px]">remove_done</span>Chưa đề xuất tuyển
         </span>`;

    htmlCards += `
      <div class="border border-slate-200/90 rounded-2xl overflow-hidden hover:border-slate-300 transition-all bg-white shadow-sm">
        <div class="p-5 bg-gradient-to-r from-slate-50 via-slate-50/50 to-white border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-emerald-100/80 text-emerald-800 flex items-center justify-center font-bold text-sm shrink-0 border border-emerald-200/50">
              <span class="material-symbols-outlined text-[22px]">assignment_turned_in</span>
            </div>
            <div>
              <h4 class="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>${tenLoai}</span>
                <span class="px-2 py-0.5 rounded text-[11px] font-bold border ${cfgItem.lopMau}">
                  ${cfgItem.ten}
                </span>
              </h4>
              <p class="text-xs text-slate-500 mt-0.5 flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[14px] text-slate-400">person</span>
                <span>Người đánh giá: <strong class="text-slate-700">${nguoiDanhGia}</strong></span>
              </p>
            </div>
          </div>
          <div>
            ${badgeDeXuat}
          </div>
        </div>

        <div class="p-5 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="p-3 rounded-xl bg-slate-50 border border-slate-100 text-center">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Kỹ Năng Chuyên Môn</span>
              <span class="text-xl font-black text-teal-700 mt-1 block">${diemKN} <span class="text-xs font-normal text-slate-400">/ 10</span></span>
            </div>
            <div class="p-3 rounded-xl bg-slate-50 border border-slate-100 text-center">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Thái Độ &amp; Kỷ Luật</span>
              <span class="text-xl font-black text-indigo-700 mt-1 block">${diemTD} <span class="text-xs font-normal text-slate-400">/ 10</span></span>
            </div>
            <div class="p-3 rounded-xl bg-emerald-50/60 border border-emerald-100 text-center">
              <span class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block">Điểm TB Đợt Này</span>
              <span class="text-xl font-black text-emerald-800 mt-1 block">${diemTBItem} <span class="text-xs font-normal text-emerald-600">/ 10</span></span>
            </div>
          </div>

          <div class="p-4 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-2">
            <div class="flex items-center gap-2 text-xs font-bold text-slate-700">
              <span class="material-symbols-outlined text-[18px] text-emerald-600">rate_review</span>
              <span>Nhận xét chi tiết từ Mentor:</span>
            </div>
            <p class="text-xs text-slate-700 leading-relaxed italic bg-white p-3 rounded-lg border border-slate-100">
              "${nhanXet}"
            </p>
          </div>
        </div>
      </div>
    `;
  });

  if (coGiuaKy && !coCuoiKy) {
    htmlCards += `
      <div class="border border-dashed border-slate-300 rounded-2xl p-6 bg-slate-50/50 flex flex-col sm:flex-row items-center gap-4 text-center sm:text-left">
        <div class="w-12 h-12 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center shrink-0">
          <span class="material-symbols-outlined text-2xl">pending_actions</span>
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-bold text-slate-800">Đợt Đánh Giá Cuối Kỳ (Đang chờ)</h4>
          <p class="text-xs text-slate-500 mt-0.5 leading-relaxed">
            Đợt đánh giá cuối kỳ sẽ được Mentor mở vào 2 tuần cuối của chương trình thực tập để tổng kết kết quả báo cáo tốt nghiệp.
          </p>
        </div>
        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
          Chưa diễn ra
        </span>
      </div>
    `;
  }

  container.innerHTML = htmlCards;
}

async function taiDuLieuDanhGia() {
  const btnLamMoi = document.getElementById("btnLamMoi");
  const maHoSo = layIdSinhVien();

  if (btnLamMoi) {
    btnLamMoi.disabled = true;
    btnLamMoi.classList.add("opacity-70", "cursor-not-allowed");
    btnLamMoi.innerHTML = `
      <span class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
      <span>Đang tải...</span>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/evaluations/by-profile/${maHoSo}`);

    if (!res.ok) {
      let thongBaoLoi = "Không thể lấy dữ liệu đánh giá từ máy chủ.";
      try {
        const errorJson = await res.json();
        if (errorJson.detail) {
          thongBaoLoi = typeof errorJson.detail === "string"
            ? errorJson.detail
            : Array.isArray(errorJson.detail)
            ? errorJson.detail.map((e) => e.msg || e.message).join(", ")
            : errorJson.detail;
        } else if (errorJson.message) {
          thongBaoLoi = errorJson.message;
        }
      } catch (e) {}

      if (res.status === 404) {
        thongBao(`Không tìm thấy hồ sơ thực tập sinh ID: ${maHoSo}`, "canh_bao");
        renderDanhSachDanhGia([], "Mentor");
        return;
      }

      thongBao(`Lỗi (${res.status}): ${thongBaoLoi}`, "loi");
      return;
    }

    const ketQua = await res.json();
    if (ketQua && ketQua.data) {
      capNhatGiaoDien(ketQua.data);
    } else {
      thongBao("Dữ liệu đánh giá trả về không đúng định dạng", "canh_bao");
    }
  } catch (loiKetNoi) {
    thongBao("Lỗi kết nối máy chủ backend. Vui lòng kiểm tra API hoặc thử lại sau.", "loi");
    const container = document.getElementById("danhSachDanhGiaContainer");
    if (container) {
      container.innerHTML = `
        <div class="p-8 text-center bg-red-50/50 rounded-2xl border border-red-200">
          <span class="material-symbols-outlined text-4xl text-red-400">cloud_off</span>
          <h4 class="text-sm font-bold text-red-800 mt-2">Mất kết nối máy chủ API</h4>
          <p class="text-xs text-red-600 max-w-sm mx-auto mt-1">
            Không thể tải dữ liệu đánh giá thực tập lúc này. Vui lòng bấm "Tải lại" để thử lại.
          </p>
        </div>
      `;
    }
  } finally {
    if (btnLamMoi) {
      btnLamMoi.disabled = false;
      btnLamMoi.classList.remove("opacity-70", "cursor-not-allowed");
      btnLamMoi.innerHTML = `
        <span class="material-symbols-outlined text-[18px]">refresh</span>
        <span>Tải lại</span>
      `;
    }
  }
}

function xuLyDangXuat() {
  if (confirm("Bạn có chắc chắn muốn đăng xuất khỏi Cổng sinh viên không?")) {
    try {
      localStorage.removeItem("ictu_student_session");
      localStorage.removeItem("currentUser");
      localStorage.removeItem("user");
      localStorage.removeItem("access_token");
      localStorage.removeItem("token");
    } catch (e) {}
    window.location.href = "../public/dangnhap.html";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  taiDuLieuDanhGia();
});
