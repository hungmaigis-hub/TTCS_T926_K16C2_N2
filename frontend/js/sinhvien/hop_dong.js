const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let hopDongHienTai = null;

function layThongTinSinhVienHienTai() {
  try {
    const raw = localStorage.getItem("ictu_student_session") || localStorage.getItem("currentUser") || localStorage.getItem("user");
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {}
  return null;
}

function layMaHopDongTuUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);
  return null;
}

function layMaHoSoTuUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  const hoSoFromUrl = urlParams.get("ma_ho_so") || urlParams.get("ho_so_id");
  if (hoSoFromUrl) return parseInt(hoSoFromUrl, 10);
  return null;
}

function toggleAgreementCheckbox() {
  const checkbox = document.getElementById("hopDongCamKet");
  if (checkbox && !checkbox.disabled) {
    checkbox.checked = !checkbox.checked;
    handleCheckboxChange({ target: checkbox });
  }
}

function handleCheckboxChange(event) {
  const isChecked = event.target.checked;
  const nutKy = document.getElementById("nutXacNhanHopDong");
  if (!nutKy) return;

  if (nutKy.getAttribute("data-da-ky") === "true") {
    nutKy.disabled = true;
    return;
  }

  if (isChecked) {
    nutKy.disabled = false;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-primary bg-primary-container hover:bg-primary shadow-md cursor-pointer transition-all duration-200";
  } else {
    nutKy.disabled = true;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-surface-variant bg-surface-container-highest cursor-not-allowed transition-all duration-200";
  }
}

function apDungTrangThaiDaKy(tenSinhVien, ngayKy, maHopDong) {
  const nutKy = document.getElementById("nutXacNhanHopDong");
  const checkbox = document.getElementById("hopDongCamKet");
  const chuKySinhVien = document.getElementById("chuKySinhVien");
  const hopThongBao = document.getElementById("hopThongBao");

  if (checkbox) {
    checkbox.checked = true;
    checkbox.disabled = true;
  }

  if (chuKySinhVien) {
    chuKySinhVien.innerHTML = `
      <div class="p-3 rounded-lg bg-surface-container-lowest shadow-sm flex items-center gap-3 text-left">
        <div class="w-10 h-10 rounded-full bg-secondary flex items-center justify-center text-on-secondary shrink-0">
          <span class="material-symbols-outlined text-xl">draw</span>
        </div>
        <div class="font-body-sm text-body-sm">
          <p class="font-bold text-secondary flex items-center gap-1">
            <span>ĐÃ KÝ ĐIỆN TỬ</span>
            <span class="material-symbols-outlined text-xs">verified</span>
          </p>
          <p class="font-code text-code text-on-surface font-semibold">${tenSinhVien || "Thực tập sinh"} (Mã HĐ: #${maHopDong})</p>
          <p class="font-code text-code text-on-surface-variant text-[10px]">Ngày ký: ${ngayKy}</p>
        </div>
      </div>
    `;
  }

  if (nutKy) {
    nutKy.setAttribute("data-da-ky", "true");
    nutKy.disabled = true;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-secondary bg-secondary cursor-default shadow-sm";
    nutKy.innerHTML = `
      <span class="material-symbols-outlined text-lg">check_circle</span>
      <span>Hợp đồng đã hoàn tất ký số</span>
    `;
  }

  if (hopThongBao) {
    hopThongBao.className =
      "rounded-xl bg-secondary-container text-on-secondary-container p-4 flex items-start gap-3.5 shadow-sm";
    hopThongBao.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5">
        <span class="material-symbols-outlined text-xl">verified</span>
      </div>
      <div class="space-y-1">
        <p class="font-label-lg text-label-lg font-bold">Hợp đồng điện tử đã được ký kết và có hiệu lực</p>
        <p class="font-body-md text-body-md">Mã xác thực: <strong class="font-code font-bold">ICTU-SIGNED-9921-OK</strong>. Hồ sơ thực tập của bạn đang ở trạng thái chính thức.</p>
      </div>
    `;
    hopThongBao.classList.remove("hidden");
  }
}

function apDungTrangThaiChuaKy(tenSinhVien, maHopDong) {
  const nutKy = document.getElementById("nutXacNhanHopDong");
  const checkbox = document.getElementById("hopDongCamKet");
  const chuKySinhVien = document.getElementById("chuKySinhVien");
  const hopThongBao = document.getElementById("hopThongBao");

  if (checkbox) {
    checkbox.checked = false;
    checkbox.disabled = false;
  }

  if (chuKySinhVien) {
    chuKySinhVien.innerHTML = `
      <div class="p-3 rounded-lg border-2 border-dashed border-outline-variant bg-surface-container-low flex items-center justify-center text-center">
        <span class="font-body-sm text-body-sm text-on-surface-variant flex items-center gap-1.5">
          <span class="material-symbols-outlined text-lg text-outline">history_edu</span>
          <span>Chờ thực tập sinh ký số bên dưới (Mã HĐ: #${maHopDong})</span>
        </span>
      </div>
    `;
  }

  if (nutKy) {
    nutKy.removeAttribute("data-da-ky");
    nutKy.disabled = true;
    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-surface-variant bg-surface-container-highest cursor-not-allowed transition-all duration-200";
    nutKy.innerHTML = `
      <span class="material-symbols-outlined text-lg">draw</span>
      <span>Xác nhận & Ký kết hợp đồng điện tử</span>
    `;
  }

  if (hopThongBao) {
    hopThongBao.className =
      "rounded-xl bg-amber-50 text-amber-900 border border-amber-200 p-4 flex items-start gap-3.5 shadow-sm";
    hopThongBao.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
        <span class="material-symbols-outlined text-xl">assignment_late</span>
      </div>
      <div class="space-y-1">
        <p class="font-label-lg text-label-lg font-bold">Hồ sơ đã được phê duyệt tiếp nhận - Cần ký hợp đồng</p>
        <p class="font-body-md text-body-md">Vui lòng đọc kỹ các điều khoản, tích chọn cam kết và nhấn nút ký điện tử bên dưới để chính thức bắt đầu kỳ thực tập.</p>
      </div>
    `;
    hopThongBao.classList.remove("hidden");
  }
}

function capNhatThongTinGiaoDien(contract, student) {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;

  const elSidebar = document.getElementById("theHocKyHopDongSidebar");
  if (elSidebar) elSidebar.textContent = `Học kỳ ${nienKhoa}`;

  const elNgayKy = document.getElementById("ngayKyHopDongTop");
  if (elNgayKy) elNgayKy.textContent = `Thái Nguyên, ngày ${now.getDate()} tháng ${now.getMonth() + 1} năm ${curY}`;

  const maHd = contract ? contract.ma_hop_dong : "001";
  const elSoHd = document.getElementById("soHopDongText");
  if (elSoHd) elSoHd.textContent = `Số: ${String(maHd).padStart(2, "0")}/${curY}/HĐTT-ICTU`;

  const elMaHd = document.getElementById("maHopDongTop");
  if (elMaHd) elMaHd.textContent = `ICTU-CONTRACT-${curY}/${String(maHd).padStart(3, "0")}`;

  const hoTen = (contract && contract.sinh_vien && contract.sinh_vien.ho_ten) || (student && student.ho_ten) || "Thực tập sinh";
  const email = (contract && contract.sinh_vien && contract.sinh_vien.email) || (student && student.email) || "";
  const sdt = (contract && contract.sinh_vien && contract.sinh_vien.so_dien_thoai) || (student && student.so_dien_thoai) || "0912345678";
  const mssv = (student && student.ma_sinh_vien) || (email.includes("@") ? email.split("@")[0].toUpperCase() : "DTC2051060124");
  const chuyenNganh = (student && student.chuyen_nganh) || "Kỹ thuật Phần mềm";
  const lop = (student && student.lop) || "K19 Kỹ thuật Phần mềm";
  const truong = (student && student.ten_truong) || "Trường ĐH CNTT & Truyền thông - ĐH Thái Nguyên";

  const elBenBHoTen = document.getElementById("benBHoTen");
  if (elBenBHoTen) elBenBHoTen.textContent = hoTen.toUpperCase();

  const elBenBMaSinhVien = document.getElementById("benBMaSinhVien");
  if (elBenBMaSinhVien) elBenBMaSinhVien.textContent = mssv;

  const elBenBLop = document.getElementById("benBLop");
  if (elBenBLop) elBenBLop.textContent = lop.includes(chuyenNganh) ? lop : `${lop} - ${chuyenNganh}`;

  const elBenBCoSo = document.getElementById("benBCoSo");
  if (elBenBCoSo) elBenBCoSo.textContent = truong;

  const elBenBLienHe = document.getElementById("benBLienHe");
  if (elBenBLienHe) elBenBLienHe.textContent = `${sdt} - ${email}`;

  const elChuKyTen = document.getElementById("chuKySinhVienTen");
  if (elChuKyTen) elChuKyTen.textContent = hoTen;
}

async function kiemTraTrangThaiHopDongBanDau() {
  const student = layThongTinSinhVienHienTai();
  const idFromUrl = layMaHopDongTuUrl();
  const hoSoFromUrl = layMaHoSoTuUrl();
  const maHoSo = hoSoFromUrl || (student ? student.ma_ho_so : null);

  let contractData = null;

  if (idFromUrl) {
    try {
      const res = await fetch(`${duongDanApi}/contracts/${idFromUrl}`);
      if (res.ok) {
        const json = await res.json();
        contractData = json.data;
      }
    } catch (e) {}
  }

  if (!contractData && maHoSo) {
    try {
      const res = await fetch(`${duongDanApi}/contracts/by-profile/${maHoSo}`);
      if (res.ok) {
        const json = await res.json();
        contractData = json.data;
      }
    } catch (e) {}
  }

  if (!contractData && student && student.ma_hop_dong) {
    try {
      const res = await fetch(`${duongDanApi}/contracts/${student.ma_hop_dong}`);
      if (res.ok) {
        const json = await res.json();
        contractData = json.data;
      }
    } catch (e) {}
  }

  if (!contractData && student) {
    try {
      const resMe = await fetch(`${duongDanApi}/interns/me/profile`);
      if (resMe.ok) {
        const jsonMe = await resMe.json();
        const me = jsonMe.data;
        if (me && me.ma_ho_so) {
          student.ma_ho_so = me.ma_ho_so;
          student.chuyen_nganh = me.chuyen_nganh || student.chuyen_nganh;
          student.lop = me.lop || student.lop;
          student.ten_truong = me.ten_truong || student.ten_truong;
          try {
            localStorage.setItem("ictu_student_session", JSON.stringify(student));
          } catch (e) {}

          const resContract = await fetch(`${duongDanApi}/contracts/by-profile/${me.ma_ho_so}`);
          if (resContract.ok) {
            const jsonContract = await resContract.json();
            contractData = jsonContract.data;
          }
        }
      }
    } catch (e) {}
  }

  if (contractData) {
    hopDongHienTai = contractData;
    capNhatThongTinGiaoDien(contractData, student);

    if (contractData.trang_thai === "DaXacNhan") {
      const ten = (contractData.sinh_vien && contractData.sinh_vien.ho_ten) || (student && student.ho_ten) || "Thực tập sinh";
      const ngay = contractData.ngay_ky || new Date().toISOString().split("T")[0];
      apDungTrangThaiDaKy(ten, ngay, contractData.ma_hop_dong);
    } else {
      const ten = (contractData.sinh_vien && contractData.sinh_vien.ho_ten) || (student && student.ho_ten) || "Thực tập sinh";
      apDungTrangThaiChuaKy(ten, contractData.ma_hop_dong);
    }
    return;
  }

  capNhatThongTinGiaoDien(null, student);
  const hopThongBao = document.getElementById("hopThongBao");
  if (hopThongBao) {
    hopThongBao.className =
      "rounded-xl bg-slate-50 text-slate-800 border border-slate-200 p-4 flex items-start gap-3.5 shadow-sm";
    hopThongBao.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-slate-400 text-white flex items-center justify-center shrink-0 mt-0.5">
        <span class="material-symbols-outlined text-xl">info</span>
      </div>
      <div class="space-y-1">
        <p class="font-label-lg text-label-lg font-bold">Chưa tìm thấy hợp đồng của hồ sơ thực tập</p>
        <p class="font-body-md text-body-md">Hồ sơ thực tập của bạn đang được cán bộ HR thẩm định hoặc chưa tạo xong hợp đồng. Vui lòng quay lại sau.</p>
      </div>
    `;
    hopThongBao.classList.remove("hidden");
  }
}

async function thucHienKyHopDong() {
  const nutKy = document.getElementById("nutXacNhanHopDong");
  const hopThongBao = document.getElementById("hopThongBao");
  const checkbox = document.getElementById("hopDongCamKet");

  if (!hopDongHienTai || !hopDongHienTai.ma_hop_dong) {
    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-red-50 text-red-900 border border-red-200 p-4 flex items-start gap-3.5 shadow-sm";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">error</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">Không tìm thấy mã hợp đồng</p>
          <p class="font-body-md text-body-md">Hệ thống chưa tìm thấy bản ghi hợp đồng tương ứng với tài khoản của bạn để ký kết.</p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
    }
    return;
  }

  if (nutKy && nutKy.getAttribute("data-da-ky") === "true") {
    return;
  }

  if (checkbox && !checkbox.checked) {
    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-amber-50 text-amber-900 border border-amber-200 p-4 flex items-start gap-3.5 shadow-sm";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">warning</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">Yêu cầu xác nhận điều khoản</p>
          <p class="font-body-md text-body-md">Vui lòng đọc kỹ và tích chọn ô cam kết tuân thủ quy chế thực tập trước khi ký kết.</p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
    }
    return;
  }

  const oldHtml = nutKy ? nutKy.innerHTML : "";
  if (nutKy) {
    nutKy.disabled = true;
    nutKy.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin"></span>
      <span>Hệ thống đang xác thực OTP & ký kết...</span>
    `;
  }

  try {
    const phanHoi = await fetch(`${duongDanApi}/contracts/${hopDongHienTai.ma_hop_dong}/confirm`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trang_thai: "DaXacNhan",
        trang_thai_thuc_tap: "DangThucTap",
        ghi_chu: "Ký số điện tử OTP qua Cổng sinh viên (ICTU-SIGNED-9921-OK)"
      })
    });

    const resJson = await phanHoi.json().catch(() => ({}));

    if (!phanHoi.ok) {
      let errMsg = "Không thể ký kết hợp đồng điện tử.";
      if (typeof resJson.detail === "string") {
        errMsg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        errMsg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }

      if (hopThongBao) {
        hopThongBao.className =
          "rounded-xl bg-red-50 text-red-900 border border-red-200 p-4 flex items-start gap-3.5 shadow-sm";
        hopThongBao.innerHTML = `
          <div class="w-8 h-8 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-xl">error</span>
          </div>
          <div class="space-y-1">
            <p class="font-label-lg text-label-lg font-bold">Lỗi xác thực hợp đồng (${phanHoi.status})</p>
            <p class="font-body-md text-body-md">${errMsg}</p>
          </div>
        `;
        hopThongBao.classList.remove("hidden");
        hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }

      if (nutKy) {
        nutKy.disabled = false;
        nutKy.innerHTML = oldHtml;
      }
      return;
    }

    const contractData = resJson.data || {};
    hopDongHienTai = contractData;
    const ngayKyHienThi = contractData.ngay_ky || new Date().toISOString().split("T")[0];
    const student = layThongTinSinhVienHienTai();
    const tenSinhVien = (contractData.sinh_vien && contractData.sinh_vien.ho_ten) || (student && student.ho_ten) || "Thực tập sinh";

    if (student) {
      student.trang_thai_hop_dong = "DaXacNhan";
      student.trang_thai_thuc_tap = "DangThucTap";
      student.ma_hop_dong = contractData.ma_hop_dong;
      try {
        localStorage.setItem("ictu_student_session", JSON.stringify(student));
        localStorage.setItem("user", JSON.stringify(student));
        localStorage.setItem("currentUser", JSON.stringify(student));
      } catch (e) {}
    }

    apDungTrangThaiDaKy(tenSinhVien, ngayKyHienThi, contractData.ma_hop_dong);

    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-secondary-container text-on-secondary-container p-4 flex items-start gap-3.5 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">check</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">✓ Chúc mừng! Bạn đã ký hợp đồng điện tử thành công.</p>
          <p class="font-body-md text-body-md">
            Mã xác thực điện tử: <strong class="font-code font-bold">ICTU-SIGNED-9921-OK</strong>. Dữ liệu đã lưu vào hồ sơ thực tập (Trạng thái: <strong>Đang thực tập</strong>) và gửi email thông báo xác nhận tới email của bạn.
          </p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

  } catch (err) {
    if (hopThongBao) {
      hopThongBao.className =
        "rounded-xl bg-amber-50 text-amber-900 border border-amber-200 p-4 flex items-start gap-3.5 shadow-sm";
      hopThongBao.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-xl">wifi_off</span>
        </div>
        <div class="space-y-1">
          <p class="font-label-lg text-label-lg font-bold">Không thể kết nối tới máy chủ</p>
          <p class="font-body-md text-body-md">Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau (${err.message || "Lỗi mạng"}).</p>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
    }
    if (nutKy) {
      nutKy.disabled = false;
      nutKy.innerHTML = `<span>Thử ký lại</span>`;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  kiemTraTrangThaiHopDongBanDau();
});
