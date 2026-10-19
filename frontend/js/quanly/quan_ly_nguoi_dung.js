const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

const sessionAdminHienTai = typeof layThongTinSession === "function" ? layThongTinSession("manager") : JSON.parse(localStorage.getItem("ictu_admin_session") || "null");
if (sessionAdminHienTai && (sessionAdminHienTai.vai_tro === "Mentor" || sessionAdminHienTai.vai_tro === "mentor" || sessionAdminHienTai.vai_tro === "NhaTruong")) {
  window.location.href = "dashboard.html";
}

let danhSachNguoiDungGoc = [];
let vaiTroLocHienTai = "";
let trangThaiLocHienTai = "";
let tuKhoaTimKiem = "";
let debounceTimer = null;

function layTenVietTat(hoTen) {
  if (!hoTen) return "ND";
  const words = hoTen.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
  }
  return hoTen.substring(0, 2).toUpperCase();
}

async function taiDanhSachNguoiDung() {
  const sessionAdmin = typeof layThongTinSession === "function" ? layThongTinSession("manager") : JSON.parse(localStorage.getItem("ictu_admin_session") || "null");
  if (sessionAdmin && (sessionAdmin.vai_tro === "Mentor" || sessionAdmin.vai_tro === "mentor" || sessionAdmin.vai_tro === "NhaTruong")) {
    window.location.href = "dashboard.html";
    return;
  }

  const tbody = document.getElementById("bangNguoiDungTbody");
  const errorBox = document.getElementById("thongBaoLoi");
  const errorText = document.getElementById("noiDungLoi");
  if (errorBox) errorBox.classList.add("hidden");

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-12 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl animate-spin text-slate-400">progress_activity</span>
            <p class="font-medium text-xs">Đang tải danh sách người dùng...</p>
          </div>
        </td>
      </tr>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/users`);
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      let msg = "Không thể tải danh sách người dùng từ máy chủ";
      if (typeof errJson.detail === "string") msg = errJson.detail;
      throw new Error(msg);
    }

    const resJson = await res.json();
    danhSachNguoiDungGoc = resJson.data || [];
    
    if (resJson.summary) {
      capNhatKpiCards(resJson.summary);
    }
    
    apDungBoLocVaRender();
  } catch (err) {
    if (errorBox && errorText) {
      errorText.textContent = `Lỗi nạp dữ liệu: ${err.message || err}`;
      errorBox.classList.remove("hidden");
    }
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="py-10 text-center text-rose-500 font-semibold">
            <div class="flex flex-col items-center justify-center gap-2">
              <span class="material-symbols-outlined text-3xl">error</span>
              <p>${err.message || "Lỗi nạp dữ liệu từ máy chủ"}</p>
            </div>
          </td>
        </tr>
      `;
    }
  }
}

function capNhatKpiCards(summary) {
  const elTong = document.getElementById("kpiTongNguoiDung");
  const elSv = document.getElementById("kpiSinhVien");
  const elMentor = document.getElementById("kpiMentor");
  const elHr = document.getElementById("kpiHR");
  const elKhoa = document.getElementById("kpiBiKhoa");

  if (elTong && summary.tong_so !== undefined) elTong.textContent = summary.tong_so;
  if (elSv && summary.sinh_vien !== undefined) elSv.textContent = summary.sinh_vien;
  if (elMentor && summary.mentor !== undefined) elMentor.textContent = summary.mentor;
  if (elHr && summary.hr_admin !== undefined) elHr.textContent = summary.hr_admin;
  if (elKhoa && summary.bi_khoa !== undefined) elKhoa.textContent = summary.bi_khoa;
}

function locVaiTro(role) {
  vaiTroLocHienTai = role || "";
  const tabButtons = document.querySelectorAll("#tabGroupVaiTro button");
  tabButtons.forEach(btn => {
    const r = btn.getAttribute("data-role") || "";
    if (r === vaiTroLocHienTai) {
      btn.className = "tab-btn px-4 py-2 rounded-xl text-xs font-bold transition-all bg-white text-slate-900 shadow-xs cursor-pointer whitespace-nowrap";
    } else {
      btn.className = "tab-btn px-4 py-2 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-slate-900 cursor-pointer whitespace-nowrap";
    }
  });
  apDungBoLocVaRender();
}

function locTrangThai(status) {
  trangThaiLocHienTai = status || "";
  apDungBoLocVaRender();
}

function xuLyTimKiem(val) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    tuKhoaTimKiem = (val || "").trim().toLowerCase();
    apDungBoLocVaRender();
  }, 250);
}

function apDungBoLocVaRender() {
  let list = [...danhSachNguoiDungGoc];

  if (vaiTroLocHienTai) {
    const v = vaiTroLocHienTai.toLowerCase();
    if (v === "thuctapsinh") {
      list = list.filter(u => (u.vai_tro || "").toLowerCase() === "thuctapsinh" || (u.vai_tro || "").toLowerCase() === "sinhvien");
    } else if (v === "mentor") {
      list = list.filter(u => (u.vai_tro || "").toLowerCase() === "mentor");
    } else if (v === "hr") {
      list = list.filter(u => (u.vai_tro || "").toLowerCase() === "hr" || (u.vai_tro || "").toLowerCase() === "admin");
    } else if (v === "nhatruong") {
      list = list.filter(u => (u.vai_tro || "").toLowerCase() === "nhatruong");
    } else {
      list = list.filter(u => (u.vai_tro || "") === vaiTroLocHienTai);
    }
  }

  if (trangThaiLocHienTai) {
    list = list.filter(u => (u.trang_thai || "HoatDong") === trangThaiLocHienTai);
  }

  if (tuKhoaTimKiem) {
    list = list.filter(u => {
      const ht = (u.ho_ten || "").toLowerCase();
      const em = (u.email || "").toLowerCase();
      const sdt = (u.so_dien_thoai || "").toLowerCase();
      const lop = (u.thong_tin_sinh_vien?.lop || "").toLowerCase();
      const chuyenNganh = (u.thong_tin_sinh_vien?.chuyen_nganh || "").toLowerCase();
      return ht.includes(tuKhoaTimKiem) || em.includes(tuKhoaTimKiem) || sdt.includes(tuKhoaTimKiem) || lop.includes(tuKhoaTimKiem) || chuyenNganh.includes(tuKhoaTimKiem);
    });
  }

  renderBangNguoiDung(list);
}

function renderBangNguoiDung(users) {
  const tbody = document.getElementById("bangNguoiDungTbody");
  const countEl = document.getElementById("txtThongKeBang");
  if (countEl) countEl.textContent = `Hiển thị ${users.length} trên tổng số ${danhSachNguoiDungGoc.length} người dùng`;
  if (!tbody) return;

  if (users.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="py-12 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-1.5">
            <span class="material-symbols-outlined text-4xl text-slate-300">search_off</span>
            <p class="text-xs font-bold text-slate-600">Không tìm thấy người dùng phù hợp bộ lọc</p>
            <p class="text-[11px] text-slate-400">Vui lòng thay đổi từ khóa hoặc bộ lọc trạng thái</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  const bangMau = [
    "from-blue-600 to-indigo-600",
    "from-sky-500 to-ictu-600",
    "from-emerald-500 to-teal-600",
    "from-violet-500 to-purple-600",
    "from-amber-500 to-orange-600"
  ];

  tbody.innerHTML = users.map((u, idx) => {
    const initials = layTenVietTat(u.ho_ten);
    const gradient = bangMau[idx % bangMau.length];
    
    let vaiTroBadge = "";
    const vtLower = (u.vai_tro || "").toLowerCase();
    if (vtLower === "thuctapsinh" || vtLower === "sinhvien") {
      vaiTroBadge = `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Sinh Viên
      </span>`;
    } else if (vtLower === "mentor") {
      vaiTroBadge = `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-violet-50 text-violet-700 border border-violet-200">
        <span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span> Mentor
      </span>`;
    } else if (vtLower === "hr" || vtLower === "admin") {
      vaiTroBadge = `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
        <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> HR / Admin
      </span>`;
    } else {
      vaiTroBadge = `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-sky-50 text-sky-700 border border-sky-200">
        <span class="w-1.5 h-1.5 rounded-full bg-sky-500"></span> ${u.vai_tro || "Người Dùng"}
      </span>`;
    }

    const isHoatDong = (u.trang_thai || "HoatDong") === "HoatDong";
    const trangThaiBadge = isHoatDong ? `
      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Hoạt động
      </span>
    ` : `
      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
        <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Bị khóa
      </span>
    `;

    let donViText = "";
    if (u.thong_tin_sinh_vien) {
      const sv = u.thong_tin_sinh_vien;
      donViText = `
        <p class="font-bold text-slate-800 text-[11px]">${sv.lop || "Lớp: N/A"}</p>
        <p class="text-[10px] text-slate-400 truncate max-w-xs">${sv.chuyen_nganh || sv.ten_truong || "ICTU"}</p>
      `;
    } else if (u.ten_phong_ban) {
      donViText = `
        <p class="font-bold text-slate-800 text-[11px]">${u.ten_phong_ban}</p>
        <p class="text-[10px] text-slate-400">Kèm: ${u.so_sinh_vien_huong_dan || 0} SV</p>
      `;
    } else {
      donViText = `<span class="text-slate-400 italic text-[11px]">Hệ thống chung</span>`;
    }

    const nutKhoa = isHoatDong ? `
      <button
        type="button"
        onclick="xacNhanKhoaNguoiDung(${u.ma_nguoi_dung}, 'Khoa')"
        class="w-8 h-8 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 flex items-center justify-center transition-colors cursor-pointer"
        title="Khóa tài khoản"
      >
        <span class="material-symbols-outlined text-[16px]">lock</span>
      </button>
    ` : `
      <button
        type="button"
        onclick="xacNhanKhoaNguoiDung(${u.ma_nguoi_dung}, 'HoatDong')"
        class="w-8 h-8 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 flex items-center justify-center transition-colors cursor-pointer"
        title="Mở khóa tài khoản"
      >
        <span class="material-symbols-outlined text-[16px]">lock_open</span>
      </button>
    `;

    return `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="py-3.5 px-5 font-mono font-bold text-slate-500">#${u.ma_nguoi_dung}</td>
        <td class="py-3.5 px-5">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr ${gradient} text-white font-bold flex items-center justify-center text-xs shrink-0 shadow-xs">
              ${initials}
            </div>
            <div>
              <p class="font-bold text-slate-900 leading-tight">${u.ho_ten}</p>
              <p class="text-[10px] text-slate-400 mt-0.5">UID: ${u.ma_nguoi_dung}</p>
            </div>
          </div>
        </td>
        <td class="py-3.5 px-5">
          <p class="font-bold text-slate-800 font-mono text-[11px]">${u.email}</p>
          <p class="text-[11px] text-slate-400 font-mono">${u.so_dien_thoai || "Chưa có SĐT"}</p>
        </td>
        <td class="py-3.5 px-5 whitespace-nowrap">${vaiTroBadge}</td>
        <td class="py-3.5 px-5">${donViText}</td>
        <td class="py-3.5 px-5 whitespace-nowrap">${trangThaiBadge}</td>
        <td class="py-3.5 px-5 text-right whitespace-nowrap">
          <div class="inline-flex items-center gap-1.5">
            <button
              type="button"
              onclick="moModalChiTietNguoiDung(${u.ma_nguoi_dung})"
              class="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition-colors cursor-pointer"
              title="Xem chi tiết"
            >
              <span class="material-symbols-outlined text-[16px]">visibility</span>
            </button>
            <button
              type="button"
              onclick="moModalSuaNguoiDung(${u.ma_nguoi_dung})"
              class="w-8 h-8 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-700 flex items-center justify-center transition-colors cursor-pointer"
              title="Chỉnh sửa thông tin"
            >
              <span class="material-symbols-outlined text-[16px]">edit</span>
            </button>
            <button
              type="button"
              onclick="moModalResetMatKhau(${u.ma_nguoi_dung}, '${u.email}', '${u.ho_ten}')"
              class="w-8 h-8 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 flex items-center justify-center transition-colors cursor-pointer"
              title="Đặt lại mật khẩu"
            >
              <span class="material-symbols-outlined text-[16px]">key</span>
            </button>
            ${nutKhoa}
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function moModalThemNguoiDung() {
  const modal = document.getElementById("modalThemNguoiDung");
  if (!modal) return;
  const errorBox = document.getElementById("thongBaoLoiThem");
  if (errorBox) errorBox.classList.add("hidden");
  
  const form = document.getElementById("formThemNguoiDung");
  if (form) form.reset();
  
  const matKhauInput = document.getElementById("themMatKhau");
  if (matKhauInput) matKhauInput.value = "123456";

  modal.classList.remove("hidden");
}

function dongModalThemNguoiDung() {
  const modal = document.getElementById("modalThemNguoiDung");
  if (modal) modal.classList.add("hidden");
}

async function guiThemNguoiDung() {
  const hoTenInput = document.getElementById("themHoTen");
  const emailInput = document.getElementById("themEmail");
  const sdtInput = document.getElementById("themSoDienThoai");
  const vaiTroInput = document.getElementById("themVaiTro");
  const matKhauInput = document.getElementById("themMatKhau");
  const errorBox = document.getElementById("thongBaoLoiThem");
  const errorText = document.getElementById("noiDungLoiThem");
  const btn = document.getElementById("btnSubmitThem");
  const icon = document.getElementById("iconSubmitThem");
  const text = document.getElementById("textSubmitThem");

  const baoLoi = (msg) => {
    if (errorBox && errorText) {
      errorText.textContent = msg;
      errorBox.classList.remove("hidden");
    } else {
      alert(msg);
    }
  };

  if (errorBox) errorBox.classList.add("hidden");

  const hoTen = hoTenInput ? hoTenInput.value.trim() : "";
  const email = emailInput ? emailInput.value.trim().toLowerCase() : "";
  const sdt = sdtInput ? sdtInput.value.trim() : "";
  const vaiTro = vaiTroInput ? vaiTroInput.value : "ThucTapSinh";
  const matKhau = matKhauInput ? matKhauInput.value.trim() : "123456";

  if (!hoTen) {
    baoLoi("Vui lòng nhập họ và tên người dùng");
    return;
  }
  if (!email) {
    baoLoi("Vui lòng nhập email đăng nhập hợp lệ");
    return;
  }
  if (matKhau.length < 6) {
    baoLoi("Mật khẩu ban đầu phải có tối thiểu 6 ký tự");
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang lưu...";
  }

  try {
    const payload = {
      ho_ten: hoTen,
      email: email,
      so_dien_thoai: sdt || null,
      vai_tro: vaiTro,
      mat_khau: matKhau
    };

    const res = await fetch(`${duongDanApi}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      alert(`Đã tạo thành công tài khoản cho ${hoTen} (${email}) với mật khẩu ban đầu là: ${matKhau}`);
      dongModalThemNguoiDung();
      await taiDanhSachNguoiDung();
    } else {
      let msg = "Không thể tạo tài khoản";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        msg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }
      baoLoi(msg);
    }
  } catch (err) {
    baoLoi(`Lỗi kết nối máy chủ: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "person_add";
      if (text) text.textContent = "Lưu tài khoản";
    }
  }
}

let danhSachPhongBanCache = null;

async function layDanhSachPhongBan() {
  if (danhSachPhongBanCache) return danhSachPhongBanCache;
  try {
    const res = await fetch(`${duongDanApi}/departments`);
    if (res.ok) {
      const data = await res.json();
      danhSachPhongBanCache = data.data || [];
      return danhSachPhongBanCache;
    }
  } catch (e) {}
  return [];
}

async function moModalSuaNguoiDung(userId) {
  const user = danhSachNguoiDungGoc.find(u => u.ma_nguoi_dung === userId);
  if (!user) {
    alert("Không tìm thấy thông tin người dùng cần chỉnh sửa");
    return;
  }

  const modal = document.getElementById("modalSuaNguoiDung");
  const errBox = document.getElementById("thongBaoLoiSua");
  if (errBox) errBox.classList.add("hidden");

  const inputId = document.getElementById("suaMaNguoiDung");
  const inputHoTen = document.getElementById("suaHoTen");
  const inputEmail = document.getElementById("suaEmail");
  const inputSdt = document.getElementById("suaSoDienThoai");
  const selectVaiTro = document.getElementById("suaVaiTro");
  const selectPhongBan = document.getElementById("suaPhongBan");

  if (inputId) inputId.value = user.ma_nguoi_dung;
  if (inputHoTen) inputHoTen.value = user.ho_ten || "";
  if (inputEmail) inputEmail.value = user.email || "";
  if (inputSdt) inputSdt.value = user.so_dien_thoai || "";
  if (selectVaiTro) selectVaiTro.value = user.vai_tro || "ThucTapSinh";

  if (selectPhongBan) {
    const departments = await layDanhSachPhongBan();
    let opts = '<option value="">-- Không phân bổ --</option>';
    departments.forEach(d => {
      const isSel = (user.ma_phong_ban === d.ma_phong_ban) ? "selected" : "";
      opts += `<option value="${d.ma_phong_ban}" ${isSel}>${d.ten_phong_ban}</option>`;
    });
    selectPhongBan.innerHTML = opts;
  }

  if (modal) modal.classList.remove("hidden");
}

function dongModalSuaNguoiDung() {
  const modal = document.getElementById("modalSuaNguoiDung");
  if (modal) modal.classList.add("hidden");
}

async function guiSuaNguoiDung() {
  const inputId = document.getElementById("suaMaNguoiDung");
  const inputHoTen = document.getElementById("suaHoTen");
  const inputEmail = document.getElementById("suaEmail");
  const inputSdt = document.getElementById("suaSoDienThoai");
  const selectVaiTro = document.getElementById("suaVaiTro");
  const selectPhongBan = document.getElementById("suaPhongBan");
  const errBox = document.getElementById("thongBaoLoiSua");
  const errText = document.getElementById("noiDungLoiSua");

  const btn = document.getElementById("btnSubmitSua");
  const icon = document.getElementById("iconSubmitSua");
  const text = document.getElementById("textSubmitSua");

  const userId = inputId ? parseInt(inputId.value) : null;
  const hoTen = inputHoTen ? inputHoTen.value.trim() : "";
  const email = inputEmail ? inputEmail.value.trim().toLowerCase() : "";
  const soDienThoai = inputSdt ? inputSdt.value.trim() : "";
  const vaiTro = selectVaiTro ? selectVaiTro.value : "ThucTapSinh";
  const maPhongBan = selectPhongBan && selectPhongBan.value ? parseInt(selectPhongBan.value) : null;

  function baoLoi(msg) {
    if (errBox && errText) {
      errText.textContent = msg;
      errBox.classList.remove("hidden");
    } else {
      alert(msg);
    }
  }

  if (errBox) errBox.classList.add("hidden");

  if (!userId || isNaN(userId)) {
    baoLoi("Không xác định được mã người dùng");
    return;
  }
  if (!hoTen) {
    baoLoi("Họ và tên người dùng không được để trống");
    return;
  }
  if (!email || !email.includes("@")) {
    baoLoi("Email không đúng định dạng hợp lệ");
    return;
  }
  if (soDienThoai && (!/^[0-9]{10}$/.test(soDienThoai) || !soDienThoai.startsWith("0"))) {
    baoLoi("Số điện thoại phải gồm đúng 10 chữ số và bắt đầu bằng số 0");
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) {
      icon.className = "material-symbols-outlined text-[17px] animate-spin";
      icon.textContent = "progress_activity";
    }
    if (text) text.textContent = "Đang lưu...";
  }

  try {
    const payload = {
      ho_ten: hoTen,
      email: email,
      so_dien_thoai: soDienThoai || null,
      vai_tro: vaiTro,
      ma_phong_ban: maPhongBan
    };

    const res = await fetch(`${duongDanApi}/users/${userId}`, {
      method: "PUT",
      headers: layHeadersXacThuc(),
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (!res.ok) {
      let msg = "Không thể cập nhật thông tin người dùng";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        msg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }
      baoLoi(msg);
      return;
    }

    dongModalSuaNguoiDung();
    await taiDanhSachNguoiDung();
    alert(`Cập nhật thông tin tài khoản '${hoTen}' thành công!`);
  } catch (err) {
    baoLoi(`Lỗi kết nối máy chủ: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) {
        icon.className = "material-symbols-outlined text-[17px]";
        icon.textContent = "save";
      }
      if (text) text.textContent = "Cập nhật";
    }
  }
}

function moModalResetMatKhau(userId, email, name) {
  const modal = document.getElementById("modalResetMatKhau");
  if (!modal) return;
  const inputId = document.getElementById("resetUserId");
  const txtEmail = document.getElementById("resetUserEmail");
  const txtName = document.getElementById("resetUserName");
  const inputPass = document.getElementById("resetMatKhauMoi");

  if (inputId) inputId.value = String(userId);
  if (txtEmail) txtEmail.textContent = email;
  if (txtName) txtName.textContent = name;
  if (inputPass) inputPass.value = "123456";

  modal.classList.remove("hidden");
}

function dongModalResetMatKhau() {
  const modal = document.getElementById("modalResetMatKhau");
  if (modal) modal.classList.add("hidden");
}

async function xacNhanResetMatKhau() {
  const inputId = document.getElementById("resetUserId");
  const inputPass = document.getElementById("resetMatKhauMoi");
  const btn = document.getElementById("btnSubmitReset");
  const icon = document.getElementById("iconSubmitReset");
  const text = document.getElementById("textSubmitReset");

  const userId = inputId ? parseInt(inputId.value) : null;
  const matKhauMoi = inputPass ? inputPass.value.trim() : "123456";

  if (!userId || isNaN(userId)) {
    alert("Không xác định được người dùng cần đặt lại mật khẩu");
    return;
  }
  if (matKhauMoi.length < 6) {
    alert("Mật khẩu mới phải có tối thiểu 6 ký tự");
    return;
  }

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[17px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang xử lý...";
  }

  try {
    const res = await fetch(`${duongDanApi}/users/${userId}/reset-password`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mat_khau_moi: matKhauMoi })
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      alert(`Đã đặt lại mật khẩu thành công! Mật khẩu mới là: ${matKhauMoi}`);
      dongModalResetMatKhau();
    } else {
      let msg = "Không thể đặt lại mật khẩu";
      if (typeof resJson.detail === "string") msg = resJson.detail;
      alert(msg);
    }
  } catch (err) {
    alert(`Lỗi kết nối máy chủ: ${err.message || err}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[17px]";
      if (icon) icon.textContent = "check";
      if (text) text.textContent = "Xác nhận đặt lại";
    }
  }
}

async function xacNhanKhoaNguoiDung(userId, trangThaiMoi) {
  const user = danhSachNguoiDungGoc.find(u => u.ma_nguoi_dung === userId);
  const ten = user ? user.ho_ten : `#${userId}`;
  const hanhDong = trangThaiMoi === "Khoa" ? "KHÓA" : "MỞ KHÓA";

  const xacNhan = confirm(`Bạn có chắc chắn muốn ${hanhDong} tài khoản người dùng: "${ten}" không?`);
  if (!xacNhan) return;

  try {
    const res = await fetch(`${duongDanApi}/users/${userId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trang_thai: trangThaiMoi })
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      alert(`Đã ${hanhDong.toLowerCase()} tài khoản thành công!`);
      await taiDanhSachNguoiDung();
    } else {
      let msg = "Không thể thay đổi trạng thái";
      if (typeof resJson.detail === "string") msg = resJson.detail;
      alert(msg);
    }
  } catch (err) {
    alert(`Lỗi kết nối máy chủ: ${err.message || err}`);
  }
}

function moModalChiTietNguoiDung(userId) {
  const user = danhSachNguoiDungGoc.find(u => u.ma_nguoi_dung === userId);
  if (!user) return;

  const modal = document.getElementById("modalChiTietNguoiDung");
  if (!modal) return;

  const elAvatar = document.getElementById("chiTietAvatar");
  const elHoTen = document.getElementById("chiTietHoTen");
  const elVaiTro = document.getElementById("chiTietVaiTroBadge");
  const elMaNd = document.getElementById("chiTietMaNd");
  const elTrangThai = document.getElementById("chiTietTrangThai");
  const elEmail = document.getElementById("chiTietEmail");
  const elSdt = document.getElementById("chiTietSdt");

  const secSv = document.getElementById("chiTietKhuVucSinhVien");
  const secMentor = document.getElementById("chiTietKhuVucMentor");

  if (elAvatar) elAvatar.textContent = layTenVietTat(user.ho_ten);
  if (elHoTen) elHoTen.textContent = user.ho_ten;
  if (elVaiTro) elVaiTro.textContent = `Vai trò: ${user.vai_tro}`;
  if (elMaNd) elMaNd.textContent = `#${user.ma_nguoi_dung}`;
  if (elTrangThai) elTrangThai.textContent = (user.trang_thai || "HoatDong") === "HoatDong" ? "Đang hoạt động" : "Bị khóa";
  if (elEmail) elEmail.textContent = user.email;
  if (elSdt) elSdt.textContent = user.so_dien_thoai || "Chưa cập nhật";

  if (user.thong_tin_sinh_vien) {
    const sv = user.thong_tin_sinh_vien;
    if (secSv) secSv.classList.remove("hidden");
    if (secMentor) secMentor.classList.add("hidden");
    const elLop = document.getElementById("chiTietLop");
    const elCn = document.getElementById("chiTietChuyenNganh");
    const elTruong = document.getElementById("chiTietTruong");
    const elMt = document.getElementById("chiTietMentor");
    if (elLop) elLop.textContent = sv.lop || "N/A";
    if (elCn) elCn.textContent = sv.chuyen_nganh || "N/A";
    if (elTruong) elTruong.textContent = sv.ten_truong || "N/A";
    if (elMt) elMt.textContent = sv.ten_mentor || "Chưa phân công";
  } else if ((user.vai_tro || "").toLowerCase() === "mentor") {
    if (secSv) secSv.classList.add("hidden");
    if (secMentor) secMentor.classList.remove("hidden");
    const elPb = document.getElementById("chiTietPhongBan");
    const elSl = document.getElementById("chiTietSoSvMentor");
    if (elPb) elPb.textContent = user.ten_phong_ban || "Chưa phân bổ";
    if (elSl) elSl.textContent = `${user.so_sinh_vien_huong_dan || 0} / 5 sinh viên`;
  } else {
    if (secSv) secSv.classList.add("hidden");
    if (secMentor) secMentor.classList.add("hidden");
  }

  modal.classList.remove("hidden");
}

function dongModalChiTietNguoiDung() {
  const modal = document.getElementById("modalChiTietNguoiDung");
  if (modal) modal.classList.add("hidden");
}

function xuatExcelNguoiDung() {
  if (danhSachNguoiDungGoc.length === 0) {
    alert("Chưa có dữ liệu người dùng để xuất!");
    return;
  }

  const headers = ["Mã ID", "Họ và tên", "Email", "Số điện thoại", "Vai trò", "Trạng thái", "Đơn vị/Lớp"];
  const rows = danhSachNguoiDungGoc.map(u => {
    let donVi = "";
    if (u.thong_tin_sinh_vien) {
      donVi = `${u.thong_tin_sinh_vien.lop || ""} - ${u.thong_tin_sinh_vien.chuyen_nganh || ""}`;
    } else if (u.ten_phong_ban) {
      donVi = u.ten_phong_ban;
    }
    return [
      u.ma_nguoi_dung,
      `"${(u.ho_ten || '').replace(/"/g, '""')}"`,
      `"${u.email}"`,
      `"${u.so_dien_thoai || ''}"`,
      `"${u.vai_tro || ''}"`,
      `"${(u.trang_thai || 'HoatDong') === 'HoatDong' ? 'Hoạt động' : 'Bị khóa'}"`,
      `"${donVi.replace(/"/g, '""')}"`
    ];
  });

  const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(r => r.join(","))].join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const timeStr = new Date().toISOString().slice(0, 10);
  a.download = `Danh_sach_nguoi_dung_${timeStr}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
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

function chuyenTabTrangChinh(tab) {
  const btnTaiKhoan = document.getElementById("btnTabTaiKhoan");
  const btnSaoLuu = document.getElementById("btnTabSaoLuu");
  const khuVucTaiKhoan = document.getElementById("khuVucQuanLyTaiKhoan");
  const khuVucSaoLuu = document.getElementById("khuVucSaoLuuHeThong");

  if (!btnTaiKhoan || !khuVucTaiKhoan) return;

  const classActive = "px-5 py-2.5 rounded-lg text-xs font-extrabold transition-all flex items-center gap-2 shadow-xs bg-white text-ictu-700 cursor-pointer";
  const classInactive = "px-5 py-2.5 rounded-lg text-xs font-bold text-slate-600 hover:text-ictu-600 transition-all flex items-center gap-2 cursor-pointer";

  btnTaiKhoan.className = classInactive;
  if (btnSaoLuu) btnSaoLuu.className = classInactive;

  khuVucTaiKhoan.classList.add("hidden");
  if (khuVucSaoLuu) khuVucSaoLuu.classList.add("hidden");

  if (tab === "tai_khoan") {
    btnTaiKhoan.className = classActive;
    khuVucTaiKhoan.classList.remove("hidden");
  } else if (tab === "sao_luu") {
    if (btnSaoLuu) btnSaoLuu.className = classActive;
    if (khuVucSaoLuu) {
      khuVucSaoLuu.classList.remove("hidden");
      taiDanhSachSaoLuu();
    }
  }
}

let danhSachBanSaoLuu = [];
let dangKichHoatSaoLuu = false;

async function taiDanhSachSaoLuu() {
  const tbody = document.getElementById("bangSaoLuuTbody");
  const errBox = document.getElementById("thongBaoLoiSaoLuu");
  const errMsg = document.getElementById("noiDungLoiSaoLuu");
  if (errBox) errBox.classList.add("hidden");

  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="py-12 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl animate-spin text-slate-400">progress_activity</span>
            <p class="font-medium text-xs">Đang tải danh sách bản sao lưu hệ thống...</p>
          </div>
        </td>
      </tr>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/system/backups`, {
      headers: layHeadersXacThuc()
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      let msg = "Không thể tải danh sách bản sao lưu";
      if (typeof errJson.detail === "string") msg = errJson.detail;
      throw new Error(msg);
    }

    const data = await res.json();
    danhSachBanSaoLuu = data.backups || [];

    const kpiTong = document.getElementById("kpiTongBanSaoLuu");
    if (kpiTong) kpiTong.textContent = data.total_files || danhSachBanSaoLuu.length;

    const kpiDungLuong = document.getElementById("kpiTongDungLuongBackup");
    if (kpiDungLuong) kpiDungLuong.textContent = data.total_size_human || "0 KB";

    const kpiLich = document.getElementById("kpiTrangThaiLichBackup");
    if (kpiLich && data.scheduler) {
      if (data.scheduler.running) {
        kpiLich.textContent = "Mỗi 24 giờ";
      } else {
        kpiLich.textContent = "Tạm dừng";
      }
    }

    renderBangSaoLuu(danhSachBanSaoLuu);
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="py-12 text-center text-rose-500 font-semibold">
            <div class="flex flex-col items-center justify-center gap-2">
              <span class="material-symbols-outlined text-4xl">error</span>
              <p>${err.message || "Lỗi nạp danh sách sao lưu"}</p>
              <button type="button" onclick="taiDanhSachSaoLuu()" class="mt-2 px-3 py-1.5 rounded-lg bg-rose-100 hover:bg-rose-200 text-rose-700 text-xs font-bold transition-all">Thử lại</button>
            </div>
          </td>
        </tr>
      `;
    }
    if (errBox && errMsg) {
      errMsg.textContent = err.message || "Lỗi tải bản sao lưu";
      errBox.classList.remove("hidden");
    }
  }
}

function renderBangSaoLuu(ds) {
  const tbody = document.getElementById("bangSaoLuuTbody");
  const thongKe = document.getElementById("txtThongKeSaoLuu");
  if (!tbody) return;

  if (thongKe) {
    thongKe.textContent = `Hiển thị ${ds.length} bản sao lưu`;
  }

  if (!ds || ds.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="py-12 text-center text-slate-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-4xl text-slate-300">folder_off</span>
            <p class="font-medium text-xs">Chưa có bản sao lưu cơ sở dữ liệu nào trong kho lưu trữ.</p>
            <button
              type="button"
              onclick="kichHoatSaoLuuThuCong()"
              class="mt-2 px-4 py-2 rounded-xl bg-ictu-600 hover:bg-ictu-700 text-white text-xs font-bold shadow-xs cursor-pointer transition-all"
            >
              Tạo bản sao lưu đầu tiên
            </button>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = ds.map((item) => {
    const checksumHienThi = item.checksum_sha256
      ? `<span class="px-2 py-1 rounded-md bg-amber-50 text-amber-800 text-[11px] font-mono font-semibold inline-flex items-center gap-1 border border-amber-200" title="${item.checksum_sha256}">
          <span class="material-symbols-outlined text-[13px] text-amber-600">verified</span>
          ${item.checksum_sha256.substring(0, 10)}...${item.checksum_sha256.substring(item.checksum_sha256.length - 6)}
        </span>`
      : `<span class="px-2 py-1 rounded-md bg-slate-100 text-slate-600 text-[11px] font-mono font-medium inline-flex items-center gap-1">
          <span class="material-symbols-outlined text-[13px] text-emerald-600">check_circle</span>
          Đạt chuẩn .sql.gz
        </span>`;

    return `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="py-4 px-6">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-[20px]">folder_zip</span>
            </div>
            <div>
              <p class="font-extrabold text-slate-800 font-mono text-xs">${item.filename}</p>
              ${item.note ? `<p class="text-[11px] text-slate-400 mt-0.5 line-clamp-1">${item.note}</p>` : `<p class="text-[11px] text-slate-400 mt-0.5">Bản sao lưu CSDL MySQL</p>`}
            </div>
          </div>
        </td>
        <td class="py-4 px-4 text-xs font-semibold text-slate-600">
          ${item.created_at || "Vừa xong"}
        </td>
        <td class="py-4 px-4">
          <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-100">
            ${item.size_human || "0 KB"}
          </span>
        </td>
        <td class="py-4 px-4">
          ${checksumHienThi}
        </td>
        <td class="py-4 px-6 text-right">
          <div class="flex items-center justify-end gap-1.5">
            <button
              type="button"
              onclick="taiXuongBanSaoLuu('${item.filename}')"
              class="h-8 px-3 rounded-lg bg-ictu-50 hover:bg-ictu-100 text-ictu-700 font-bold text-xs inline-flex items-center gap-1.5 transition-colors cursor-pointer"
              title="Tải xuống tệp .sql.gz"
            >
              <span class="material-symbols-outlined text-[16px]">download</span>
              <span>Tải về</span>
            </button>
            <button
              type="button"
              onclick="xacNhanXoaTepSaoLuu('${item.filename}')"
              class="w-8 h-8 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 inline-flex items-center justify-center transition-colors cursor-pointer"
              title="Xóa bản sao lưu này"
            >
              <span class="material-symbols-outlined text-[16px]">delete</span>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

async function kichHoatSaoLuuThuCong() {
  if (dangKichHoatSaoLuu) return;

  const btnKichHoat = document.getElementById("btnKichHoatBackup");
  const iconKichHoat = document.getElementById("iconKichHoatBackup");
  const textKichHoat = document.getElementById("textKichHoatBackup");
  const errBox = document.getElementById("thongBaoLoiSaoLuu");
  const errMsg = document.getElementById("noiDungLoiSaoLuu");
  const succBox = document.getElementById("thongBaoThanhCongSaoLuu");
  const succMsg = document.getElementById("noiDungThanhCongSaoLuu");

  if (errBox) errBox.classList.add("hidden");
  if (succBox) succBox.classList.add("hidden");

  const email = layEmailDangNhapHienTai();
  const ghiChu = prompt("Nhập ghi chú cho bản sao lưu (không bắt buộc):", `Sao lưu thủ công bởi ${email}`);
  if (ghiChu === null) return;

  dangKichHoatSaoLuu = true;
  if (btnKichHoat) btnKichHoat.disabled = true;
  if (iconKichHoat) {
    iconKichHoat.textContent = "progress_activity";
    iconKichHoat.classList.add("animate-spin");
  }
  if (textKichHoat) textKichHoat.textContent = "Đang nén & sao lưu...";

  try {
    const res = await fetch(`${duongDanApi}/system/backup`, {
      method: "POST",
      headers: layHeadersXacThuc(),
      body: JSON.stringify({
        note: ghiChu.trim() || `Sao lưu thủ công bởi ${email}`
      })
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      let msg = "Không thể tạo bản sao lưu";
      if (typeof errJson.detail === "string") msg = errJson.detail;
      else if (Array.isArray(errJson.detail)) msg = errJson.detail.map(d => d.msg || JSON.stringify(d)).join(", ");
      throw new Error(msg);
    }

    const data = await res.json();
    const backupItem = data.backup || {};

    if (succBox && succMsg) {
      succMsg.textContent = `Tạo bản sao lưu thành công! Tệp: ${backupItem.filename || ""} (${backupItem.size_human || ""})`;
      succBox.classList.remove("hidden");
      setTimeout(() => {
        succBox.classList.add("hidden");
      }, 6000);
    }

    await taiDanhSachSaoLuu();
  } catch (err) {
    if (errBox && errMsg) {
      errMsg.textContent = err.message || "Lỗi tạo bản sao lưu";
      errBox.classList.remove("hidden");
    } else {
      alert(`Lỗi tạo bản sao lưu: ${err.message || err}`);
    }
  } finally {
    dangKichHoatSaoLuu = false;
    if (btnKichHoat) btnKichHoat.disabled = false;
    if (iconKichHoat) {
      iconKichHoat.textContent = "backup";
      iconKichHoat.classList.remove("animate-spin");
    }
    if (textKichHoat) textKichHoat.textContent = "Tạo Bản Sao Lưu Ngay";
  }
}

async function taiXuongBanSaoLuu(tenTep) {
  if (!tenTep) return;
  try {
    const res = await fetch(`${duongDanApi}/system/backups/${encodeURIComponent(tenTep)}/download`, {
      headers: layHeadersXacThuc()
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      let msg = "Không thể tải tệp sao lưu";
      if (typeof errJson.detail === "string") msg = errJson.detail;
      throw new Error(msg);
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = tenTep;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Lỗi tải xuống tệp sao lưu: ${err.message || err}`);
  }
}

async function xacNhanXoaTepSaoLuu(tenTep) {
  if (!tenTep) return;
  const xacNhan = confirm(`Bạn có chắc chắn muốn xóa vĩnh viễn tệp sao lưu:\n"${tenTep}"\nkhỏi máy chủ? Thao tác này không thể hoàn tác.`);
  if (!xacNhan) return;

  try {
    const res = await fetch(`${duongDanApi}/system/backups/${encodeURIComponent(tenTep)}`, {
      method: "DELETE",
      headers: layHeadersXacThuc()
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      let msg = "Không thể xóa tệp sao lưu";
      if (typeof errJson.detail === "string") msg = errJson.detail;
      throw new Error(msg);
    }

    const succBox = document.getElementById("thongBaoThanhCongSaoLuu");
    const succMsg = document.getElementById("noiDungThanhCongSaoLuu");
    if (succBox && succMsg) {
      succMsg.textContent = `Đã xóa tệp sao lưu "${tenTep}" thành công!`;
      succBox.classList.remove("hidden");
      setTimeout(() => {
        succBox.classList.add("hidden");
      }, 5000);
    }

    await taiDanhSachSaoLuu();
  } catch (err) {
    alert(`Lỗi xóa tệp sao lưu: ${err.message || err}`);
  }
}


window.addEventListener("DOMContentLoaded", () => {
  taiDanhSachNguoiDung();
});


