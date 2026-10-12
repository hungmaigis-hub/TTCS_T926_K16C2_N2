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

window.addEventListener("DOMContentLoaded", () => {
  taiDanhSachNguoiDung();
});
