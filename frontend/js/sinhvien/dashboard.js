const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

function laySessionSinhVien() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  let sessionUser = null;
  try {
    const raw =
      localStorage.getItem("ictu_student_session") ||
      localStorage.getItem("currentUser") ||
      localStorage.getItem("user");
    if (raw) sessionUser = JSON.parse(raw);
  } catch (e) {}

  return {
    idFromUrl: idFromUrl ? parseInt(idFromUrl, 10) : null,
    user: sessionUser
  };
}

function layTenVietTat(hoTen) {
  if (!hoTen) return "SV";
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

function thongBaoDangCapNhat(tieuDe) {
  alert(tieuDe + ": Tính năng đang được tối ưu và cập nhật dữ liệu.");
}

async function taiDuLieuDashboardSinhVien() {
  const { idFromUrl, user } = laySessionSinhVien();

  let hoSoData = null;
  let maHoSo = idFromUrl;

  if (maHoSo) {
    try {
      const res = await fetch(`${duongDanApi}/interns/${maHoSo}`);
      if (res.ok) {
        const json = await res.json();
        hoSoData = json.data;
      }
    } catch (e) {}
  }

  if (!hoSoData && user?.ma_ho_so) {
    maHoSo = parseInt(user.ma_ho_so, 10);
    try {
      const res = await fetch(`${duongDanApi}/interns/${maHoSo}`);
      if (res.ok) {
        const json = await res.json();
        hoSoData = json.data;
      }
    } catch (e) {}
  }

  if (!hoSoData && user?.ma_nguoi_dung) {
    try {
      const res = await fetch(`${duongDanApi}/interns?ma_nguoi_dung=${user.ma_nguoi_dung}`);
      if (res.ok) {
        const json = await res.json();
        if (json.data && json.data.length > 0) {
          hoSoData = json.data[0];
          maHoSo = hoSoData.ma_ho_so;
        }
      }
    } catch (e) {}
  }

  if (!hoSoData && user?.email) {
    try {
      const res = await fetch(`${duongDanApi}/interns`);
      if (res.ok) {
        const json = await res.json();
        const list = json.data || [];
        const match = list.find((i) => i.email === user.email);
        if (match) {
          hoSoData = match;
          maHoSo = hoSoData.ma_ho_so;
        }
      }
    } catch (e) {}
  }

  if (!hoSoData && !user && !idFromUrl) {
    try {
      const res = await fetch(`${duongDanApi}/interns`);
      if (res.ok) {
        const json = await res.json();
        const list = json.data || [];
        if (list.length > 0) {
          hoSoData = list[0];
          maHoSo = hoSoData.ma_ho_so;
        }
      }
    } catch (e) {}
  }

  if (!hoSoData && user) {
    hoSoData = {
      ma_ho_so: null,
      ma_nguoi_dung: user.ma_nguoi_dung || null,
      ho_ten: user.ho_ten || "Sinh viên",
      email: user.email || "",
      so_dien_thoai: user.so_dien_thoai || "",
      chuyen_nganh: user.chuyen_nganh || "Chuyên ngành đào tạo",
      ten_truong: "Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU)",
      ten_chuong_trinh: "Chương trình thực tập 2026",
      trang_thai_xet_duyet: "ChuaNop",
      trang_thai_thuc_tap: "ChuaThucTap",
      ten_mentor: null,
      ma_mentor: null
    };
  }

  let scheduleData = null;
  if (maHoSo) {
    try {
      const res = await fetch(`${duongDanApi}/interns/my-schedule?ho_so_id=${maHoSo}`);
      if (res.ok) {
        const json = await res.json();
        scheduleData = json.data;
      }
    } catch (e) {}
  }

  let evaluationData = null;
  if (maHoSo) {
    try {
      const res = await fetch(`${duongDanApi}/evaluations/summary?ho_so_id=${maHoSo}`);
      if (res.ok) {
        const json = await res.json();
        evaluationData = json.data;
      }
    } catch (e) {}
  }

  let contractData = null;
  if (maHoSo) {
    try {
      const res = await fetch(`${duongDanApi}/contracts/by-profile/${maHoSo}`);
      if (res.ok) {
        const json = await res.json();
        contractData = json.data;
      }
    } catch (e) {}
  }

  capNhatThongTinHoSo(hoSoData, contractData);
  capNhatTienDoThucTap(hoSoData, scheduleData, contractData);
  capNhatNhiemVu(scheduleData, hoSoData);
  const evalResult = capNhatDanhGia(evaluationData, hoSoData);
  capNhatLoTrinh(hoSoData, contractData, evalResult, scheduleData);
  capNhatNguoiHuongDan(hoSoData);
  capNhatThongBao(hoSoData, contractData, scheduleData);
}

function capNhatThongTinHoSo(sv, contract) {
  if (!sv) return;

  const hoTen = sv.ho_ten || "Sinh viên";
  const elTen = document.getElementById("welcomeTenSinhVien");
  if (elTen) elTen.textContent = hoTen;

  const tenTruong = sv.ten_truong || "ĐH CNTT & Truyền Thông (ICTU)";
  const chuyenNganh = sv.chuyen_nganh || "Chuyên ngành đào tạo";
  const donVi = sv.ten_mentor
    ? `Mentor: ${sv.ten_mentor}`
    : (sv.ten_chuong_trinh ? sv.ten_chuong_trinh.split("(")[0].trim() : tenTruong);

  const elDonViTop = document.getElementById("tenDonViThucTapTop");
  if (elDonViTop) elDonViTop.textContent = donVi;

  const elChuyenNganhTop = document.getElementById("chuyenNganhTop");
  if (elChuyenNganhTop) elChuyenNganhTop.textContent = chuyenNganh;

  const elMoTaDoanhNghiep = document.getElementById("moTaDoanhNghiep");
  if (elMoTaDoanhNghiep) {
    elMoTaDoanhNghiep.textContent = sv.ten_mentor ? `Doanh nghiệp (Mentor ${sv.ten_mentor})` : tenTruong;
  }

  const elMoTaTrangThai = document.getElementById("welcomeMoTaTrangThai");
  if (elMoTaTrangThai) {
    if (sv.trang_thai_xet_duyet === "ChoDuyet") {
      elMoTaTrangThai.innerHTML = `Hồ sơ của bạn đang được phòng Đào tạo &amp; Doanh nghiệp <strong class="text-white font-semibold">xét duyệt tiếp nhận</strong>. Vui lòng theo dõi kết quả phê duyệt trên hệ thống!`;
    } else if (sv.trang_thai_xet_duyet === "DaDuyet" && (!contract || (contract.trang_thai !== "DaXacNhan" && contract.trang_thai !== "DaKy"))) {
      elMoTaTrangThai.innerHTML = `Chúc mừng bạn! Hồ sơ đã được <strong class="text-white font-semibold">phê duyệt tiếp nhận</strong>. Vui lòng vào mục <a href="hop_dong.html" class="text-emerald-300 font-bold underline">Hợp đồng</a> để ký hợp đồng thực tập điện tử.`;
    } else if (sv.trang_thai_xet_duyet === "TuChoi") {
      elMoTaTrangThai.innerHTML = `Hồ sơ thực tập của bạn chưa được tiếp nhận trong đợt này. Vui lòng liên hệ Văn phòng Khoa để được hỗ trợ hướng dẫn.`;
    } else {
      elMoTaTrangThai.innerHTML = `Bạn đang trong <strong id="moTaTuanThucTap" class="text-white font-semibold">tiến độ thực tập</strong> tại <strong id="moTaDoanhNghiep" class="text-white font-semibold">${sv.ten_mentor ? `Doanh nghiệp (Mentor ${sv.ten_mentor})` : tenTruong}</strong>. Hãy duy trì báo cáo định kỳ và hoàn thành các nhiệm vụ được giao!`;
    }
  }

  const elTrangThaiHopDong = document.getElementById("trangThaiHopDongTxt");
  const elSoHopDong = document.getElementById("soHopDongTxt");
  const elMoTaKyKet = document.getElementById("moTaKyKetTxt");
  const elHopDongIcon = document.getElementById("hopDongIcon");
  const elBadgeWrap = document.getElementById("hopDongBadgeWrap");

  if (contract && (contract.trang_thai === "DaXacNhan" || contract.trang_thai === "DaKy")) {
    if (elTrangThaiHopDong) elTrangThaiHopDong.textContent = "Đã Hoàn Tất";
    if (elSoHopDong) elSoHopDong.textContent = `Hợp đồng số #${contract.ma_hop_dong || 1}/HĐ-ICTU`;
    if (elMoTaKyKet) {
      elMoTaKyKet.textContent = contract.ngay_ky ? `Đã ký kết ngày ${dinhDangNgayVn(contract.ngay_ky)}` : "Đã ký số và lưu trữ trong CSDL";
    }
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-emerald-600 font-semibold mb-2";
    if (elHopDongIcon) elHopDongIcon.textContent = "check_circle";
  } else if (sv.trang_thai_xet_duyet === "DaDuyet") {
    if (elTrangThaiHopDong) elTrangThaiHopDong.textContent = "Chờ Ký HĐ";
    if (elSoHopDong) elSoHopDong.textContent = `Hồ sơ ID #${sv.ma_ho_so || 1}`;
    if (elMoTaKyKet) elMoTaKyKet.textContent = "Hồ sơ đã duyệt, cần ký hợp đồng thực tập";
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-amber-600 font-semibold mb-2";
    if (elHopDongIcon) elHopDongIcon.textContent = "edit_document";
  } else if (sv.trang_thai_xet_duyet === "ChoDuyet") {
    if (elTrangThaiHopDong) elTrangThaiHopDong.textContent = "Chờ Xét Duyệt";
    if (elSoHopDong) elSoHopDong.textContent = `Hồ sơ ID #${sv.ma_ho_so || 1}`;
    if (elMoTaKyKet) elMoTaKyKet.textContent = "Hồ sơ đang chờ phòng Đào tạo/HR duyệt";
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-amber-600 font-semibold mb-2";
    if (elHopDongIcon) elHopDongIcon.textContent = "hourglass_top";
  } else if (sv.trang_thai_xet_duyet === "TuChoi") {
    if (elTrangThaiHopDong) elTrangThaiHopDong.textContent = "Từ Chối";
    if (elSoHopDong) elSoHopDong.textContent = `Hồ sơ ID #${sv.ma_ho_so || 1}`;
    if (elMoTaKyKet) elMoTaKyKet.textContent = "Hồ sơ không được phê duyệt tiếp nhận";
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-rose-600 font-semibold mb-2";
    if (elHopDongIcon) elHopDongIcon.textContent = "cancel";
  } else {
    if (elTrangThaiHopDong) elTrangThaiHopDong.textContent = "Chưa Nộp";
    if (elSoHopDong) elSoHopDong.textContent = "Chưa có hồ sơ";
    if (elMoTaKyKet) elMoTaKyKet.textContent = "Vui lòng nộp CV & tài liệu thực tập";
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-slate-500 font-semibold mb-2";
    if (elHopDongIcon) elHopDongIcon.textContent = "pending";
  }
}

function capNhatTienDoThucTap(hoSoData, scheduleData, contractData) {
  let batDau = hoSoData?.ngay_bat_dau || scheduleData?.ngay_bat_dau;
  let ketThuc = hoSoData?.ngay_ket_thuc || scheduleData?.ngay_ket_thuc;
  let tenChuongTrinh = hoSoData?.ten_chuong_trinh || scheduleData?.ten_chuong_trinh || "Chương trình thực tập 2026";

  const elBanner = document.getElementById("theHocKySinhVienBanner");
  if (elBanner && tenChuongTrinh) {
    elBanner.textContent = tenChuongTrinh;
  }

  const elSidebar = document.getElementById("theHocKySinhVienSidebar");
  if (elSidebar && tenChuongTrinh) {
    elSidebar.textContent = tenChuongTrinh.length > 25 ? tenChuongTrinh.substring(0, 22) + "..." : tenChuongTrinh;
  }

  if (!batDau || !ketThuc || !hoSoData?.ma_chuong_trinh) {
    if (elMoTaTuan) elMoTaTuan.textContent = "Chưa xếp lịch thực tập";
    if (elChuSoTuan) {
      elChuSoTuan.innerHTML = `Chưa xếp lịch <span id="tongSoTuanTxt" class="text-sm font-normal text-slate-500">/ -- tuần</span>`;
    }
    if (elThanhTienDo) elThanhTienDo.style.width = "0%";
    if (elPhanTram) elPhanTram.textContent = "Đạt 0% thời gian";
    if (elSoTuanCon) elSoTuanCon.textContent = "Chờ phân bổ chương trình";
    return;
  }

  const dStart = new Date(batDau);
  const dEnd = new Date(ketThuc);
  const totalMs = Math.max(1, dEnd.getTime() - dStart.getTime());
  const tongSoTuan = Math.max(1, Math.ceil(totalMs / (7 * 24 * 60 * 60 * 1000)));

  const daKyHopDong = contractData && (contractData.trang_thai === "DaXacNhan" || contractData.trang_thai === "DaKy");
  const dangThucTap = daKyHopDong && (hoSoData?.trang_thai_thuc_tap === "DangThucTap" || !!hoSoData?.ten_mentor);
  const daHoanThanh = hoSoData?.trang_thai_thuc_tap === "HoanThanh";

  const elMoTaTuan = document.getElementById("moTaTuanThucTap");
  const elChuSoTuan = document.getElementById("chuSoTienDoTuan");
  const elThanhTienDo = document.getElementById("thanhTienDoTuan");
  const elPhanTram = document.getElementById("phanTramThoiGianTxt");
  const elSoTuanCon = document.getElementById("soTuanConLaiTxt");

  if (daHoanThanh) {
    if (elMoTaTuan) elMoTaTuan.textContent = `Đã hoàn thành ${tongSoTuan} tuần thực tập`;
    if (elChuSoTuan) {
      elChuSoTuan.innerHTML = `${tongSoTuan} <span id="tongSoTuanTxt" class="text-sm font-normal text-slate-500">/ ${tongSoTuan} tuần</span>`;
    }
    if (elThanhTienDo) elThanhTienDo.style.width = "100%";
    if (elPhanTram) elPhanTram.textContent = "Hoàn thành 100%";
    if (elSoTuanCon) elSoTuanCon.textContent = "Đã kết thúc kỳ thực tập";
    return;
  }

  if (!dangThucTap) {
    if (elMoTaTuan) elMoTaTuan.textContent = "Giai đoạn chuẩn bị thực tập";
    if (elChuSoTuan) {
      elChuSoTuan.innerHTML = `Chưa bắt đầu <span id="tongSoTuanTxt" class="text-sm font-normal text-slate-500">/ ${tongSoTuan} tuần</span>`;
    }
    if (elThanhTienDo) elThanhTienDo.style.width = "0%";
    if (elPhanTram) elPhanTram.textContent = "Đạt 0% thời gian";
    if (elSoTuanCon) {
      elSoTuanCon.textContent = `Kế hoạch ${tongSoTuan} tuần`;
    }
    return;
  }

  const dNow = new Date();
  const diffMs = Math.max(0, dNow.getTime() - dStart.getTime());
  const tuan = Math.max(1, Math.min(tongSoTuan, Math.ceil(diffMs / (7 * 24 * 60 * 60 * 1000))));
  const percent = Math.min(100, Math.max(0, Math.round((diffMs / totalMs) * 100)));
  const soTuanCon = Math.max(0, tongSoTuan - tuan);

  if (elMoTaTuan) elMoTaTuan.textContent = `Tuần thứ ${tuan} / ${tongSoTuan}`;
  if (elChuSoTuan) {
    elChuSoTuan.innerHTML = `Tuần ${tuan} <span id="tongSoTuanTxt" class="text-sm font-normal text-slate-500">/ ${tongSoTuan} tuần</span>`;
  }
  if (elThanhTienDo) {
    elThanhTienDo.style.width = `${percent}%`;
  }
  if (elPhanTram) {
    elPhanTram.textContent = `Đạt ${percent}% thời gian`;
  }
  if (elSoTuanCon) {
    elSoTuanCon.textContent = soTuanCon > 0 ? `Còn ${soTuanCon} tuần` : "Đã hoàn thành";
  }
}

function capNhatNhiemVu(scheduleData, hoSoData) {
  const danhSach = scheduleData?.danh_sach_nhiem_vu || [];
  const tongSo = danhSach.length;

  const hoanThanh = danhSach.filter((t) => (t.tien_do_phantram >= 100) || t.trang_thai === "Hoàn thành" || t.trang_thai === "Đã hoàn thành").length;
  const dangLam = danhSach.filter((t) => (t.tien_do_phantram > 0 && t.tien_do_phantram < 100) || t.trang_thai === "Đang thực hiện").length;
  const sapToi = Math.max(0, tongSo - hoanThanh - dangLam);

  const elChuSoNhiemVu = document.getElementById("chuSoNhiemVuSprint");
  if (elChuSoNhiemVu) {
    elChuSoNhiemVu.innerHTML = `${hoanThanh} <span id="tongSoNhiemVuSprint" class="text-sm font-normal text-slate-500">/ ${tongSo} hoàn thành</span>`;
  }

  const elThanhTienDo = document.getElementById("thanhTienDoNhiemVu");
  if (elThanhTienDo) {
    const phanTram = tongSo > 0 ? Math.round((hoanThanh / tongSo) * 100) : 0;
    elThanhTienDo.style.width = `${phanTram}%`;
  }

  const elDangLam = document.getElementById("nhiemVuDangLamTxt");
  if (elDangLam) elDangLam.textContent = `${dangLam} đang làm`;

  const elSapToi = document.getElementById("nhiemVuSapToiTxt");
  if (elSapToi) elSapToi.textContent = `${sapToi} sắp tới`;

  const elMoTaNhiemVu = document.getElementById("moTaNhiemVuPhanCong");
  if (elMoTaNhiemVu) {
    if (hoSoData?.ten_mentor) {
      elMoTaNhiemVu.textContent = `Các đầu việc được Mentor ${hoSoData.ten_mentor} phân công trực tiếp`;
    } else {
      elMoTaNhiemVu.textContent = "Các đầu việc được phân công từ người hướng dẫn";
    }
  }

  const container = document.getElementById("danhSachNhiemVuSprintContainer");
  if (!container) return;

  if (danhSach.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center text-xs text-slate-400 border border-dashed border-slate-200 rounded-2xl">
        <span class="material-symbols-outlined text-[28px] text-slate-300 mb-1">task</span>
        <p class="font-medium text-slate-600">Chưa có nhiệm vụ phân công trong CSDL</p>
        <p class="text-[11px] text-slate-400 mt-0.5">Người hướng dẫn sẽ giao nhiệm vụ theo từng giai đoạn thực tập.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = "";
  const hienThi = danhSach.slice(0, 4);

  hienThi.forEach((nv) => {
    const progress = nv.tien_do_phantram || 0;
    let badgeColor = "bg-slate-100 text-slate-700 border-slate-200";
    let badgeText = "Chưa làm";

    if (progress >= 100) {
      badgeColor = "bg-emerald-50 text-emerald-800 border-emerald-200";
      badgeText = "Hoàn thành";
    } else if (progress > 0) {
      badgeColor = "bg-blue-50 text-blue-700 border-blue-200";
      badgeText = `Đang làm ${progress}%`;
    }

    const item = document.createElement("div");
    item.className = "p-4 rounded-2xl border border-slate-200/90 hover:border-emerald-300 hover:bg-slate-50/50 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4";
    item.innerHTML = `
      <div class="space-y-1.5 flex-1">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-slate-900">${nv.ten_nhiem_vu || "Nhiệm vụ thực tập"}</span>
        </div>
        <p class="text-xs text-slate-500">${nv.mo_ta || "Theo dõi tiến độ từ người hướng dẫn"}</p>
        <div class="flex items-center gap-4 text-[11px] text-slate-400">
          <span class="flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">calendar_today</span>
            Hạn: ${dinhDangNgayVn(nv.han_hoan_thanh) || "Đang cập nhật"}
          </span>
        </div>
      </div>
      <div class="sm:text-right shrink-0 flex sm:flex-col items-center sm:items-end justify-between gap-2">
        <span class="px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeColor}">
          ${badgeText}
        </span>
        <a href="nhiem_vu.html" class="text-xs font-bold text-emerald-700 hover:text-emerald-800 hover:underline">
          Báo cáo tiến độ
        </a>
      </div>
    `;
    container.appendChild(item);
  });
}

function capNhatDanhGia(evalData, hoSoData) {
  const elDiem = document.getElementById("chuSoDiemRenLuyen");
  const elXepLoai = document.getElementById("xepLoaiTxt");
  const elNhanXet = document.getElementById("nhanXetDiemTxt");
  const elBadgeWrap = document.getElementById("xepLoaiBadgeWrap");
  const elIcon = document.getElementById("xepLoaiIcon");

  let diem = null;
  let xepLoai = null;
  let nhanXet = null;

  if (evalData) {
    let records = [];
    if (Array.isArray(evalData)) {
      records = evalData;
    } else if (evalData.danh_gia_thuc_tap && Array.isArray(evalData.danh_gia_thuc_tap)) {
      records = evalData.danh_gia_thuc_tap;
    }

    if (hoSoData && records.length > 0) {
      const match = records.find((r) => r.ma_ho_so === hoSoData.ma_ho_so);
      if (match) {
        diem = match.diem_trung_binh;
        xepLoai = match.xep_loai === "XuatSac" ? "Xuất sắc" : (match.xep_loai === "Gioi" ? "Giỏi" : (match.xep_loai || "Khá"));
        if (match.nhan_xet_chi_tiet) nhanXet = match.nhan_xet_chi_tiet;
      }
    }
  }

  if (diem !== null && diem !== undefined) {
    if (elDiem) elDiem.innerHTML = `${diem} <span class="text-sm font-normal text-slate-500">/ 10</span>`;
    if (elXepLoai) elXepLoai.textContent = `Xếp loại: ${xepLoai}`;
    if (elNhanXet) elNhanXet.textContent = nhanXet || "Đánh giá chuyên cần & kết quả thực tập";
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-amber-600 font-semibold mb-2";
    if (elIcon) {
      elIcon.className = "material-symbols-outlined text-[16px] fill";
      elIcon.textContent = "thumb_up";
    }
    return { hasEvaluation: true, diem, xepLoai, nhanXet };
  } else {
    if (elDiem) elDiem.innerHTML = `-- <span class="text-sm font-normal text-slate-500">/ 10</span>`;
    if (elXepLoai) elXepLoai.textContent = "Chưa đánh giá";
    if (elNhanXet) elNhanXet.textContent = "Chưa có kết quả đánh giá từ Mentor";
    if (elBadgeWrap) elBadgeWrap.className = "flex items-center gap-1.5 text-xs text-slate-500 font-semibold mb-2";
    if (elIcon) {
      elIcon.className = "material-symbols-outlined text-[16px]";
      elIcon.textContent = "rate_review";
    }
    return { hasEvaluation: false, diem: null, xepLoai: null, nhanXet: null };
  }
}

function capNhatLoTrinh(hoSoData, contractData, evalResult, scheduleData) {
  const container = document.getElementById("loTrinh5GiaiDoanContainer");
  const elBadgeChang = document.getElementById("badgeChangHienTai");
  if (!container) return;

  const daNopHoSo = !!hoSoData?.ma_ho_so;
  const daDuyet = hoSoData?.trang_thai_xet_duyet === "DaDuyet";
  const dangChoDuyet = hoSoData?.trang_thai_xet_duyet === "ChoDuyet";
  const biTuChoi = hoSoData?.trang_thai_xet_duyet === "TuChoi";

  const daKyHopDong = contractData && (contractData.trang_thai === "DaXacNhan" || contractData.trang_thai === "DaKy");
  const choKyHopDong = daDuyet && !daKyHopDong;

  const coMentor = !!hoSoData?.ten_mentor;
  const dangThucTap = daKyHopDong && (hoSoData?.trang_thai_thuc_tap === "DangThucTap" || coMentor);

  const daCoDanhGia = evalResult && evalResult.hasEvaluation;

  let changHienTaiTxt = "Chặng hiện tại: Giai đoạn 1";
  if (daCoDanhGia) {
    changHienTaiTxt = "Chặng hiện tại: Giai đoạn 5 (Tổng kết)";
  } else if (dangThucTap) {
    changHienTaiTxt = "Chặng hiện tại: Giai đoạn 4 (Thực tập)";
  } else if (choKyHopDong) {
    changHienTaiTxt = "Chặng hiện tại: Giai đoạn 3 (Ký hợp đồng)";
  } else if (dangChoDuyet) {
    changHienTaiTxt = "Chặng hiện tại: Giai đoạn 2 (Chờ duyệt)";
  } else if (biTuChoi) {
    changHienTaiTxt = "Chặng hiện tại: Giai đoạn 2 (Từ chối)";
  } else if (daNopHoSo) {
    changHienTaiTxt = "Chặng hiện tại: Giai đoạn 2 (Xét duyệt)";
  }
  if (elBadgeChang) elBadgeChang.textContent = changHienTaiTxt;

  let card1 = `
    <div class="p-4 rounded-2xl ${daNopHoSo ? "bg-emerald-50/70 border border-emerald-200" : "bg-gradient-to-b from-emerald-100 to-teal-50 border-2 border-emerald-500 shadow-sm ring-2 ring-emerald-200"} relative">
      <div class="flex items-center justify-between mb-2">
        <span class="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold">1</span>
        <span class="material-symbols-outlined text-emerald-600 text-[18px]">${daNopHoSo ? "check_circle" : "hourglass_top"}</span>
      </div>
      <h3 class="text-xs font-bold text-slate-900 mb-1">Nộp hồ sơ &amp; CV</h3>
      <p class="text-[11px] text-slate-500 mb-2">${daNopHoSo ? "Đã nộp hồ sơ vào CSDL" : "Chưa hoàn tất nộp hồ sơ"}</p>
      <a href="tai_tai_lieu.html" class="text-[11px] font-semibold text-emerald-700 hover:underline inline-flex items-center gap-0.5">
        ${daNopHoSo ? "Xem lại hồ sơ" : "Nộp hồ sơ ngay"}
        <span class="material-symbols-outlined text-[12px]">chevron_right</span>
      </a>
    </div>
  `;

  let card2Class = "p-4 rounded-2xl bg-slate-50 border border-slate-200 opacity-80 relative";
  let card2Icon = "lock";
  let card2Title = "Xét duyệt tiếp nhận";
  let card2Sub = "Chờ nộp hồ sơ";
  let card2Badge = `<span class="text-[11px] font-medium text-slate-400">Chưa mở khóa</span>`;

  if (daDuyet) {
    card2Class = "p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 relative";
    card2Icon = "check_circle";
    card2Sub = hoSoData.ten_truong ? `${hoSoData.ten_truong.split("-")[0].trim()} duyệt` : "Đã tiếp nhận";
    card2Badge = `<span class="text-[11px] font-semibold text-emerald-700">Đã phê duyệt</span>`;
  } else if (dangChoDuyet) {
    card2Class = "p-4 rounded-2xl bg-gradient-to-b from-amber-50 to-amber-100/60 border-2 border-amber-400 shadow-sm ring-2 ring-amber-200 relative";
    card2Icon = "hourglass_top";
    card2Sub = "Đang chờ HR/Nhà trường duyệt";
    card2Badge = `<span class="text-[11px] font-bold text-amber-700 animate-pulse">Đang xét duyệt</span>`;
  } else if (biTuChoi) {
    card2Class = "p-4 rounded-2xl bg-rose-50 border border-rose-200 relative";
    card2Icon = "cancel";
    card2Sub = hoSoData.ghi_chu ? `Lý do: ${hoSoData.ghi_chu}` : "Hồ sơ không đạt yêu cầu";
    card2Badge = `<span class="text-[11px] font-semibold text-rose-700">Đã từ chối</span>`;
  }

  let card2 = `
    <div class="${card2Class}">
      <div class="flex items-center justify-between mb-2">
        <span class="w-7 h-7 rounded-full ${daDuyet ? "bg-emerald-600 text-white" : (dangChoDuyet ? "bg-amber-500 text-white" : "bg-slate-300 text-slate-600")} flex items-center justify-center text-xs font-bold">2</span>
        <span class="material-symbols-outlined ${daDuyet ? "text-emerald-600" : (dangChoDuyet ? "text-amber-600" : "text-slate-400")} text-[18px]">${card2Icon}</span>
      </div>
      <h3 class="text-xs font-bold text-slate-900 mb-1">${card2Title}</h3>
      <p class="text-[11px] text-slate-500 mb-2 truncate">${card2Sub}</p>
      ${card2Badge}
    </div>
  `;

  let card3Class = "p-4 rounded-2xl bg-slate-50 border border-slate-200 opacity-80 relative";
  let card3Icon = "lock";
  let card3Sub = "Chờ duyệt hồ sơ";
  let card3Link = `<span class="text-[11px] font-medium text-slate-400">Chưa mở khóa</span>`;

  if (daKyHopDong) {
    card3Class = "p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 relative";
    card3Icon = "check_circle";
    card3Sub = contractData.ngay_ky ? `Đã ký ngày ${dinhDangNgayVn(contractData.ngay_ky)}` : "Đã ký số 3 bên";
    card3Link = `
      <a href="hop_dong.html" class="text-[11px] font-semibold text-emerald-700 hover:underline inline-flex items-center gap-0.5">
        Xem hợp đồng
        <span class="material-symbols-outlined text-[12px]">chevron_right</span>
      </a>
    `;
  } else if (choKyHopDong) {
    card3Class = "p-4 rounded-2xl bg-gradient-to-b from-emerald-100 to-teal-50 border-2 border-emerald-500 shadow-sm relative ring-2 ring-emerald-200";
    card3Icon = "edit_document";
    card3Sub = "Cần ký hợp đồng thực tập";
    card3Link = `
      <a href="hop_dong.html" class="text-[11px] font-bold text-emerald-800 hover:underline inline-flex items-center gap-0.5">
        Ký hợp đồng ngay
        <span class="material-symbols-outlined text-[12px]">chevron_right</span>
      </a>
    `;
  }

  let card3 = `
    <div class="${card3Class}">
      <div class="flex items-center justify-between mb-2">
        <span class="w-7 h-7 rounded-full ${daKyHopDong ? "bg-emerald-600 text-white" : (choKyHopDong ? "bg-emerald-600 text-white" : "bg-slate-300 text-slate-600")} flex items-center justify-center text-xs font-bold">3</span>
        <span class="material-symbols-outlined ${daKyHopDong || choKyHopDong ? "text-emerald-600" : "text-slate-400"} text-[18px]">${card3Icon}</span>
      </div>
      <h3 class="text-xs font-bold text-slate-900 mb-1">Ký kết hợp đồng</h3>
      <p class="text-[11px] text-slate-500 mb-2 truncate">${card3Sub}</p>
      ${card3Link}
    </div>
  `;

  let card4Class = "p-4 rounded-2xl bg-slate-50 border border-slate-200 opacity-80 relative";
  let card4Icon = "lock";
  let card4Sub = coMentor ? "Chờ bắt đầu" : "Chờ phân công Mentor";
  let card4Link = `<span class="text-[11px] font-medium text-slate-400">Chưa bắt đầu</span>`;

  if (dangThucTap) {
    card4Class = "p-4 rounded-2xl bg-gradient-to-b from-emerald-100 to-teal-50 border-2 border-emerald-500 shadow-sm relative ring-2 ring-emerald-200";
    card4Icon = "work";
    card4Sub = coMentor ? `Mentor ${hoSoData.ten_mentor}` : "Đang thực hiện";
    card4Link = `
      <a href="nhiem_vu.html" class="text-[11px] font-bold text-emerald-700 hover:underline inline-flex items-center gap-0.5">
        Cập nhật nhiệm vụ
        <span class="material-symbols-outlined text-[12px]">chevron_right</span>
      </a>
    `;
  }

  let card4 = `
    <div class="${card4Class}">
      <div class="flex items-center justify-between mb-2">
        <span class="w-7 h-7 rounded-full ${dangThucTap ? "bg-emerald-600 text-white" : "bg-slate-300 text-slate-600"} flex items-center justify-center text-xs font-bold">4</span>
        <span class="material-symbols-outlined ${dangThucTap ? "text-emerald-600" : "text-slate-400"} text-[18px]">${card4Icon}</span>
      </div>
      <h3 class="text-xs font-bold text-emerald-950 mb-1">Thực tập &amp; Báo cáo</h3>
      <p class="text-[11px] text-emerald-800 font-medium mb-2 truncate">${card4Sub}</p>
      ${card4Link}
    </div>
  `;

  let card5Class = "p-4 rounded-2xl bg-slate-50 border border-slate-200 opacity-80 relative";
  let card5Icon = "lock";
  let card5Sub = "Chưa có đánh giá";
  let card5Link = `<span class="text-[11px] font-medium text-slate-400">Chưa mở khóa</span>`;

  if (daCoDanhGia) {
    card5Class = "p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 relative";
    card5Icon = "verified";
    card5Sub = `Điểm: ${evalResult.diem} / 10`;
    card5Link = `
      <a href="danh_gia.html" class="text-[11px] font-bold text-emerald-700 hover:underline inline-flex items-center gap-0.5">
        Xem phiếu đánh giá
        <span class="material-symbols-outlined text-[12px]">chevron_right</span>
      </a>
    `;
  }

  let card5 = `
    <div class="${card5Class}">
      <div class="flex items-center justify-between mb-2">
        <span class="w-7 h-7 rounded-full ${daCoDanhGia ? "bg-emerald-600 text-white" : "bg-slate-300 text-slate-600"} flex items-center justify-center text-xs font-bold">5</span>
        <span class="material-symbols-outlined ${daCoDanhGia ? "text-emerald-600" : "text-slate-400"} text-[18px]">${card5Icon}</span>
      </div>
      <h3 class="text-xs font-bold text-slate-700 mb-1">Báo cáo &amp; Đánh giá</h3>
      <p class="text-[11px] text-slate-500 mb-2 truncate">${card5Sub}</p>
      ${card5Link}
    </div>
  `;

  container.innerHTML = card1 + card2 + card3 + card4 + card5;
}

function capNhatNguoiHuongDan(hoSoData) {
  const gvhdDonVi = document.getElementById("gvhdDonVi");
  if (gvhdDonVi && hoSoData?.ten_truong) {
    gvhdDonVi.textContent = hoSoData.ten_truong;
  }

  const cardMentor = document.getElementById("cardMentorDoanhNghiep");
  const avatarInitials = document.getElementById("avatarInitialsDN");
  const mentorTen = document.getElementById("mentorTenDN");
  const mentorChucVu = document.getElementById("mentorChucVuDN");
  const mentorEmail = document.getElementById("mentorEmailDN");
  const mentorDonVi = document.getElementById("mentorDonViDN");
  const btnNhanTin = document.getElementById("btnNhanTinMentor");

  if (!cardMentor) return;

  if (hoSoData?.ten_mentor) {
    cardMentor.className = "p-3.5 rounded-2xl bg-emerald-50/60 border border-emerald-200/80";
    if (avatarInitials) {
      avatarInitials.className = "w-9 h-9 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center";
      avatarInitials.textContent = layTenVietTat(hoSoData.ten_mentor);
    }
    if (mentorTen) mentorTen.textContent = hoSoData.ten_mentor;
    if (mentorChucVu) {
      mentorChucVu.className = "text-[10px] text-emerald-800 font-semibold";
      mentorChucVu.textContent = "Người hướng dẫn thực tập";
    }
    if (mentorEmail) mentorEmail.textContent = "mentor@ictu.edu.vn";
    if (mentorDonVi) mentorDonVi.textContent = hoSoData.ten_chuong_trinh || "Đơn vị thực tập tiếp nhận";
    if (btnNhanTin) {
      btnNhanTin.disabled = false;
      btnNhanTin.className = "w-full py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-semibold transition-colors flex items-center justify-center gap-1";
      btnNhanTin.innerHTML = `<span class="material-symbols-outlined text-[14px]">chat</span><span>Nhắn tin Mentor</span>`;
    }
  } else {
    cardMentor.className = "p-3.5 rounded-2xl bg-slate-50 border border-dashed border-slate-200";
    if (avatarInitials) {
      avatarInitials.className = "w-9 h-9 rounded-full bg-slate-200 text-slate-500 font-bold text-xs flex items-center justify-center";
      avatarInitials.innerHTML = `<span class="material-symbols-outlined text-[18px]">person_off</span>`;
    }
    if (mentorTen) mentorTen.textContent = "Chưa phân công Mentor";
    if (mentorChucVu) {
      mentorChucVu.className = "text-[10px] text-slate-500 font-medium";
      mentorChucVu.textContent = "Đang chờ HR/Quản lý chỉ định";
    }
    if (mentorEmail) mentorEmail.textContent = "Chưa có thông tin";
    if (mentorDonVi) mentorDonVi.textContent = "Chưa phân công đơn vị";
    if (btnNhanTin) {
      btnNhanTin.disabled = true;
      btnNhanTin.className = "w-full py-1.5 px-3 rounded-lg bg-slate-100 text-slate-400 text-[11px] font-semibold transition-colors flex items-center justify-center gap-1 cursor-not-allowed";
      btnNhanTin.innerHTML = `<span class="material-symbols-outlined text-[14px]">lock</span><span>Chờ phân công Mentor</span>`;
    }
  }
}

function capNhatThongBao(hoSoData, contractData, scheduleData) {
  const container = document.getElementById("danhSachThongBaoContainer");
  if (!container) return;

  const thongBaoList = [];

  if (hoSoData?.trang_thai_xet_duyet === "ChoDuyet") {
    thongBaoList.push({
      donVi: "Phòng Tuyển dụng / HR",
      mauDonVi: "text-amber-600",
      thoiGian: "Hệ thống",
      tieuDe: "Hồ sơ thực tập đang chờ xét duyệt",
      noiDung: "Hồ sơ của bạn đã được ghi nhận trên hệ thống và đang chờ Phòng Nhân sự / Đào tạo xét duyệt chỉ tiêu tiếp nhận."
    });
  } else if (hoSoData?.trang_thai_xet_duyet === "DaDuyet") {
    if (!contractData || (contractData.trang_thai !== "DaXacNhan" && contractData.trang_thai !== "DaKy")) {
      thongBaoList.push({
        donVi: "Ban Tiếp nhận Thực tập",
        mauDonVi: "text-emerald-700",
        thoiGian: "Ưu tiên",
        tieuDe: "Hồ sơ đã được duyệt - Ký hợp đồng",
        noiDung: "Hồ sơ thực tập đã được phê duyệt hợp lệ. Vui lòng vào mục Hợp đồng để ký hợp đồng thực tập điện tử."
      });
    } else {
      thongBaoList.push({
        donVi: "Quản lý Hợp đồng",
        mauDonVi: "text-emerald-700",
        thoiGian: "Hợp lệ",
        tieuDe: "Hợp đồng thực tập đã kích hoạt",
        noiDung: `Hợp đồng thực tập số #${contractData.ma_hop_dong || 1} đã được xác nhận điện tử và lưu trữ an toàn trong CSDL.`
      });
    }
  }

  if (hoSoData?.ten_mentor) {
    thongBaoList.push({
      donVi: "Người hướng dẫn",
      mauDonVi: "text-blue-700",
      thoiGian: "Mentor",
      tieuDe: `Đã phân công: ${hoSoData.ten_mentor}`,
      noiDung: `Bạn được phân công dưới sự hướng dẫn chuyên môn của Mentor ${hoSoData.ten_mentor}. Hãy chủ động trao đổi nhiệm vụ.`
    });
  } else {
    thongBaoList.push({
      donVi: "Phòng Nhân sự / HR",
      mauDonVi: "text-slate-600",
      thoiGian: "Thông báo",
      tieuDe: "Chờ phân công Mentor hướng dẫn",
      noiDung: "Hệ thống đang sắp xếp Mentor phù hợp với chuyên ngành đào tạo của bạn. Thông tin sẽ được cập nhật sớm."
    });
  }

  const dsNhiemVu = scheduleData?.danh_sach_nhiem_vu || [];
  const chuaXong = dsNhiemVu.filter((n) => n.tien_do_phantram < 100);
  if (chuaXong.length > 0) {
    const nv = chuaXong[0];
    thongBaoList.push({
      donVi: "Nhiệm vụ thực tập",
      mauDonVi: "text-purple-700",
      thoiGian: "Tiến độ",
      tieuDe: `Nhắc nhở: ${nv.ten_nhiem_vu || "Nhiệm vụ tuần"}`,
      noiDung: `Hạn hoàn thành: ${dinhDangNgayVn(nv.han_hoan_thanh) || "Đang cập nhật"}. Hãy cập nhật tiến độ công việc trước hạn.`
    });
  } else {
    thongBaoList.push({
      donVi: "Cổng sinh viên ICTU",
      mauDonVi: "text-teal-700",
      thoiGian: "Định kỳ",
      tieuDe: "Báo cáo thực tập hàng tuần",
      noiDung: "Hãy nhớ nộp báo cáo định kỳ hàng tuần đúng thời hạn để người hướng dẫn và nhà trường theo dõi tiến độ."
    });
  }

  let html = "";
  thongBaoList.forEach((tb) => {
    html += `
      <div class="p-3 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100/60 transition-colors">
        <div class="flex items-center justify-between text-[10px] text-slate-400 mb-1">
          <span class="font-bold ${tb.mauDonVi}">${tb.donVi}</span>
          <span>${tb.thoiGian}</span>
        </div>
        <h4 class="text-xs font-bold text-slate-800 mb-1">${tb.tieuDe}</h4>
        <p class="text-[11px] text-slate-500 leading-relaxed">${tb.noiDung}</p>
      </div>
    `;
  });

  container.innerHTML = html;
}

document.addEventListener("DOMContentLoaded", () => {
  taiDuLieuDashboardSinhVien();
});
