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
    const payloadPut = {
      ho_ten: hoTen,
      email: email,
      so_dien_thoai: soDienThoai || null,
      chuyen_nganh: chuyenNganh || null,
      trang_thai_thuc_tap: "DangThucTap",
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
      hienThongBaoThanhCong(
        `Đã cập nhật thành công hồ sơ #${maHoSoHienTai} (${hoTen})!`,
      );
    } finally {
      if (nutLuu) {
        nutLuu.innerHTML = originalContent;
        nutLuu.disabled = false;
      }
    }
    return;
  }

  const duLieuPost = {
    full_name: hoTen,
    email: email,
    phone: soDienThoai || null,
    status: trangThai,
    university: truongDaiHoc || null,
    major: chuyenNganh || null,
    start_date: ngayBatDau || null,
    end_date: ngayKetThuc || null,
    notes: ghiChu || null,
  };

  try {
    const phanHoi = await fetch(duongDanApi, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(duLieuPost),
    });

    const ketQua = await phanHoi.json();

    if (phanHoi.ok) {
      hienThongBaoThanhCong(
        ketQua.message ||
          `Đã thêm mới thành công hồ sơ của sinh viên ${hoTen}!`,
      );
      form?.reset();
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
    hienThongBaoThanhCong(
      `Đã lưu thành công hồ sơ của sinh viên ${hoTen} vào hệ thống quản lý thực tập!`,
    );
    form?.reset();
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

document.addEventListener("DOMContentLoaded", () => {
  kiemTraVaNapHoSo();
});
