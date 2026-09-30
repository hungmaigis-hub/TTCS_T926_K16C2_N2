const duongDanApi = "http://127.0.0.1:8000/api/v1/interns";

let maHoSoHienTai = null;

async function kiemTraVaNapHoSo() {
  const thamSoUrl = new URLSearchParams(window.location.search);
  const id = thamSoUrl.get("id");
  if (!id) return;

  maHoSoHienTai = id;
  const tieuDeForm = document.querySelector("h2.text-base");
  if (tieuDeForm)
    tieuDeForm.textContent = `Chỉnh Sửa Hồ Sơ Thực Tập Sinh (Mã: #${id})`;

  try {
    const phanHoi = await fetch(`${duongDanApi}/${id}`);
    if (!phanHoi.ok) return;

    const ketQua = await phanHoi.json();
    const data = ketQua.data;
    if (!data) return;

    const oHoTen = document.getElementById("hoTen");
    const oEmail = document.getElementById("email");
    const oSdt = document.getElementById("soDienThoai");
    const oChuyenNganh = document.getElementById("chuyenNganh");
    const oTruong = document.getElementById("truongDaiHoc");
    const oTrangThai = document.getElementById("trangThai");
    const oNgayBatDau = document.getElementById("ngayBatDau");
    const oNgayKetThuc = document.getElementById("ngayKetThuc");

    if (oHoTen && data.ho_ten) oHoTen.value = data.ho_ten;
    if (oEmail && data.email) oEmail.value = data.email;
    if (oSdt && data.so_dien_thoai) oSdt.value = data.so_dien_thoai;
    if (oChuyenNganh && data.chuyen_nganh)
      oChuyenNganh.value = data.chuyen_nganh;
    if (oTruong && data.ten_truong) oTruong.value = data.ten_truong;
    if (oNgayBatDau && data.ngay_bat_dau) oNgayBatDau.value = data.ngay_bat_dau;
    if (oNgayKetThuc && data.ngay_ket_thuc)
      oNgayKetThuc.value = data.ngay_ket_thuc;
    if (oTrangThai && data.trang_thai_thuc_tap) {
      if (data.trang_thai_thuc_tap === "DangThucTap")
        oTrangThai.value = "Đang thực tập";
      else if (data.trang_thai_thuc_tap === "HoanThanh")
        oTrangThai.value = "Đã hoàn thành";
    }

    hienThongBaoThanhCong(
      `Đã kết nối API Backend và tải thành công dữ liệu hồ sơ #${id} (${data.ho_ten})!`,
    );
  } catch (err) {}
}

async function handleLuuHoSo() {
  const hoTen = document.getElementById("hoTen")?.value.trim();
  const email = document.getElementById("email")?.value.trim();
  const soDienThoai = document.getElementById("soDienThoai")?.value.trim();
  const trangThai = document.getElementById("trangThai")?.value;
  const truongDaiHoc = document.getElementById("truongDaiHoc")?.value.trim();
  const chuyenNganh = document.getElementById("chuyenNganh")?.value.trim();
  const ngayBatDau = document.getElementById("ngayBatDau")?.value;
  const ngayKetThuc = document.getElementById("ngayKetThuc")?.value;
  const ghiChu = document.getElementById("ghiChu")?.value.trim() || "";
  const nutLuu = document.getElementById("nutLuuHoSo");
  const form = document.getElementById("formHoSo");

  if (!hoTen) {
    hienThongBaoLoi("Vui lòng nhập họ và tên thực tập sinh.");
    document.getElementById("hoTen")?.focus();
    return;
  }

  const bieuThucEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !bieuThucEmail.test(email)) {
    hienThongBaoLoi("Địa chỉ email không đúng định dạng.");
    document.getElementById("email")?.focus();
    return;
  }

  if (soDienThoai && !/^\d{10}$/.test(soDienThoai)) {
    hienThongBaoLoi("Số điện thoại phải bao gồm đúng 10 chữ số.");
    document.getElementById("soDienThoai")?.focus();
    return;
  }

  if (ngayBatDau && ngayKetThuc && ngayKetThuc < ngayBatDau) {
    hienThongBaoLoi("Ngày kết thúc không được nhỏ hơn ngày bắt đầu.");
    document.getElementById("ngayKetThuc")?.focus();
    return;
  }

  const originalContent = nutLuu ? nutLuu.innerHTML : "";
  if (nutLuu) {
    nutLuu.innerHTML = `<span class="inline-block w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span> <span>Đang đồng bộ API...</span>`;
    nutLuu.disabled = true;
  }

  if (maHoSoHienTai) {
    let trangThaiThucTap = "DangThucTap";
    if (trangThai === "Đã hoàn thành") {
      trangThaiThucTap = "HoanThanh";
    } else if (trangThai === "Tạm dừng") {
      trangThaiThucTap = "ThoiHoc";
    }

    let maTruong = 1;
    if (truongDaiHoc && truongDaiHoc.toLowerCase().includes("bách khoa")) {
      maTruong = 2;
    }

    const payloadPut = {
      ho_ten: hoTen,
      email: email,
      so_dien_thoai: soDienThoai || null,
      chuyen_nganh: chuyenNganh || null,
      ma_truong: maTruong,
      trang_thai_thuc_tap: trangThaiThucTap,
    };

    try {
      const phanHoi = await fetch(`${duongDanApi}/${maHoSoHienTai}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payloadPut),
      });
      const ketQua = await phanHoi.json();
      if (phanHoi.ok) {
        hienThongBaoThanhCong(
          ketQua.message ||
            `Cập nhật thành công hồ sơ #${maHoSoHienTai} vào CSDL MySQL!`,
        );
      } else {
        hienThongBaoLoi(ketQua.detail || "Không thể cập nhật hồ sơ qua API!");
      }
    } catch (err) {
      hienThongBaoLoi(
        "Không thể kết nối đến máy chủ Backend (http://127.0.0.1:8000). Vui lòng kiểm tra lại server!",
      );
    } finally {
      if (nutLuu) {
        nutLuu.innerHTML = originalContent;
        nutLuu.disabled = false;
      }
    }
    return;
  }

  let trangThaiThucTap = "DangThucTap";
  let trangThaiXetDuyet = "ChoDuyet";
  if (trangThai === "Đã hoàn thành") {
    trangThaiThucTap = "HoanThanh";
  } else if (trangThai === "Tạm dừng") {
    trangThaiThucTap = "ThoiHoc";
  } else if (trangThai === "Chờ duyệt") {
    trangThaiXetDuyet = "ChoDuyet";
  }

  let maTruong = 1;
  if (truongDaiHoc && truongDaiHoc.toLowerCase().includes("bách khoa")) {
    maTruong = 2;
  }

  const duLieuPost = {
    ho_ten: hoTen,
    email: email,
    so_dien_thoai: soDienThoai || null,
    chuyen_nganh: chuyenNganh || null,
    ma_truong: maTruong,
    ma_chuong_trinh: 1,
    trang_thai_xet_duyet: trangThaiXetDuyet,
    trang_thai_thuc_tap: trangThaiThucTap,
  };

  try {
    const phanHoi = await fetch(duongDanApi, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(duLieuPost),
    });

    const ketQua = await phanHoi.json();

    if (phanHoi.ok) {
      const maHoSoTaoMoi = ketQua.data?.ma_ho_so;
      hienThongBaoThanhCong(
        ketQua.message ||
          `Đã thêm mới thành công hồ sơ của sinh viên ${hoTen} (Mã hồ sơ: #${maHoSoTaoMoi || ""}) vào CSDL Backend!`,
      );
      form?.reset();
      taiHoSoGanDay();
    } else {
      let loiChiTiet = "Có lỗi xảy ra khi lưu hồ sơ!";
      if (typeof ketQua.detail === "string") {
        loiChiTiet = ketQua.detail;
      } else if (Array.isArray(ketQua.detail) && ketQua.detail[0]?.msg) {
        loiChiTiet = ketQua.detail[0].msg;
      }
      hienThongBaoLoi(loiChiTiet);
    }
  } catch (loiKetNoi) {
    hienThongBaoLoi(
      "Không thể kết nối đến máy chủ Backend (http://127.0.0.1:8000). Vui lòng đảm bảo server FastAPI đang chạy!",
    );
  } finally {
    if (nutLuu) {
      nutLuu.innerHTML = originalContent;
      nutLuu.disabled = false;
    }
  }
}

function hienThongBaoThanhCong(thongDiep) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) return;
  hopThongBao.className =
    "rounded-xl border border-emerald-200 bg-emerald-50/90 text-emerald-900 p-4 transition-all duration-300 shadow-sm flex items-start gap-3.5";
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-[20px]">check_circle</span>
    </div>
    <div class="flex-1 text-xs">
      <div class="flex items-center justify-between">
        <span class="font-bold text-slate-900 text-sm">Thao tác thành công</span>
        <span class="text-[11px] text-emerald-700 font-semibold bg-emerald-100 px-2 py-0.5 rounded">Vừa xong</span>
      </div>
      <p class="text-slate-700 mt-1 leading-relaxed">${thongDiep}</p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-slate-400 hover:text-slate-600 p-1 rounded-md" title="Đóng thông báo">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hopThongBao.classList.remove("hidden");
  hopThongBao.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hienThongBaoLoi(thongDiep) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) {
    alert(thongDiep);
    return;
  }
  hopThongBao.className =
    "rounded-xl border border-rose-200 bg-rose-50 text-rose-900 p-4 transition-all duration-300 shadow-sm flex items-start gap-3.5";
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-[20px]">error</span>
    </div>
    <div class="flex-1 text-xs">
      <div class="flex items-center justify-between">
        <span class="font-bold text-rose-900 text-sm">Lỗi nhập liệu</span>
        <span class="text-[11px] text-rose-700 font-semibold bg-rose-100 px-2 py-0.5 rounded">Cần kiểm tra</span>
      </div>
      <p class="text-rose-800 mt-1 leading-relaxed">${thongDiep}</p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-rose-400 hover:text-rose-600 p-1 rounded-md" title="Đóng thông báo">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hopThongBao.classList.remove("hidden");
  hopThongBao.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function taiHoSoGanDay() {
  const tbody = document.getElementById("bangHoSoGanDay");
  if (!tbody) return;

  try {
    const phanHoi = await fetch(`${duongDanApi}?limit=6`);
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
      "bg-sky-100 text-sky-700",
    ];

    tbody.innerHTML = danhSach
      .map((item, idx) => {
        const hoTen = item.ho_ten || "Chưa cập nhật";
        const email = item.email || "—";
        const chuyenNganh = item.chuyen_nganh || "Công nghệ thông tin";
        const thoiGian =
          item.ngay_bat_dau && item.ngay_ket_thuc
            ? `${dinhDangNgay(item.ngay_bat_dau)} - ${dinhDangNgay(item.ngay_ket_thuc)}`
            : "Học kỳ 2024 - 2025";

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
              <a href="them_ho_so.html?id=${item.ma_ho_so}" class="hover:text-blue-600 transition-colors font-semibold" title="Nhấp để chỉnh sửa hồ sơ #${item.ma_ho_so}">
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
      thoiGianCapNhat.textContent = "Đồng bộ từ CSDL Backend";
    }
  } catch (err) {}
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

document.addEventListener("DOMContentLoaded", () => {
  kiemTraVaNapHoSo();
  taiHoSoGanDay();
});
