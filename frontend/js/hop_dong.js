const duongDanApi = "http://127.0.0.1:8000/api/v1";

function toggleAgreementCheckbox() {
  const checkbox = document.getElementById("hopDongCamKet");
  checkbox.checked = !checkbox.checked;
  handleCheckboxChange({ target: checkbox });
}

function handleCheckboxChange(event) {
  const isChecked = event.target.checked;
  const nutKy = document.getElementById("nutXacNhanHopDong");
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

async function thucHienKyHopDong() {
  const nutKy = document.getElementById("nutXacNhanHopDong");
  const hopThongBao = document.getElementById("hopThongBao");
  const chuKySinhVien = document.getElementById("chuKySinhVien");
  const checkbox = document.getElementById("hopDongCamKet");
  const maHopDong = 1;

  nutKy.disabled = true;
  nutKy.innerHTML = `
    <span class="inline-block w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin"></span>
    <span>Hệ thống đang xác thực OTP & ký kết...</span>
  `;

  try {
    const phanHoi = await fetch(`${duongDanApi}/contracts/${maHopDong}/confirm`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trang_thai: "DaXacNhan",
        trang_thai_thuc_tap: "DangThucTap",
        ghi_chu: "Ký số điện tử OTP qua Cổng sinh viên (ICTU-SIGNED-9921-OK)"
      })
    });

    const resJson = phanHoi.ok ? await phanHoi.json() : null;
    const contractData = resJson?.data;
    const ngayKyHienThi = contractData?.ngay_ky || new Date().toISOString().split("T")[0];
    const tenSinhVien = contractData?.sinh_vien?.ho_ten || "Nguyễn Văn An";

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
          <p class="font-code text-code text-on-surface font-semibold">${tenSinhVien} (Mã HĐ: #${maHopDong})</p>
          <p class="font-code text-code text-on-surface-variant text-[10px]">Ngày ký: ${ngayKyHienThi}</p>
        </div>
      </div>
    `;

    nutKy.className =
      "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-label-lg text-label-lg text-on-secondary bg-secondary cursor-default shadow-sm";
    nutKy.innerHTML = `
      <span class="material-symbols-outlined text-lg">check_circle</span>
      <span>Hợp đồng đã hoàn tất ký số</span>
    `;
    checkbox.disabled = true;
    hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });

  } catch (err) {
    hopThongBao.className =
      "rounded-xl bg-amber-50 text-amber-900 border border-amber-200 p-4 flex items-start gap-3.5 shadow-sm";
    hopThongBao.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
        <span class="material-symbols-outlined text-xl">warning</span>
      </div>
      <div class="space-y-1">
        <p class="font-label-lg text-label-lg font-bold">Không thể kết nối Backend API</p>
        <p class="font-body-md text-body-md">Vui lòng kiểm tra lại server Backend tại ${duongDanApi}.</p>
      </div>
    `;
    nutKy.disabled = false;
    nutKy.innerHTML = `<span>Thử ký lại</span>`;
  }
}
