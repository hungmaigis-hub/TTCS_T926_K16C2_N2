function tinhToanThoiGian() {
  const batDau = document.getElementById("ngayBatDau").value;
  const ketThuc = document.getElementById("ngayKetThuc").value;
  const labelSoNgay = document.getElementById("soNgayThucTap");
  if (!batDau || !ketThuc) return;
  const d1 = new Date(batDau);
  const d2 = new Date(ketThuc);
  const diffTime = d2.getTime() - d1.getTime();
  if (diffTime < 0) {
    labelSoNgay.textContent = "Ngày không hợp lệ (kết thúc trước bắt đầu)";
    labelSoNgay.className = "font-bold text-error";
    return;
  }
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  const diffWeeks = Math.round((diffDays / 7) * 10) / 10;
  labelSoNgay.textContent = `${diffDays} ngày (${diffWeeks} tuần)`;
  labelSoNgay.className = "font-bold text-primary";
}
function datLaiForm() {
  document.getElementById("bieuMauChuongTrinh").reset();
  setTimeout(tinhToanThoiGian, 50);
}
function xuLyLuuLich() {
  const ten = document.getElementById("tenChuongTrinh").value.trim();
  const pb = document.getElementById("phongBan").value;
  const batDau = document.getElementById("ngayBatDau").value;
  const ketThuc = document.getElementById("ngayKetThuc").value;
  const nut = document.getElementById("nutLuuLich");
  const hop = document.getElementById("hopThongBao");
  if (!ten || !batDau || !ketThuc) {
    alert("Vui lòng điền đầy đủ thông tin bắt buộc của chương trình.");
    return;
  }
  const oldContent = nut.innerHTML;
  nut.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang lưu lịch trình...</span>
    `;
  nut.disabled = true;
  setTimeout(() => {
    hop.className =
      "rounded-xl bg-secondary-container p-4 shadow-sm flex items-start gap-3.5 transition-all text-on-secondary-container";
    hop.innerHTML = `
        <div class="w-9 h-9 rounded-lg bg-secondary flex items-center justify-center text-on-secondary shrink-0 shadow-sm mt-0.5">
          <span class="material-symbols-outlined text-xl">check_circle</span>
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between">
            <h4 class="font-label-lg text-label-lg font-bold">Lưu Thành Công Lịch Trình Thực Tập</h4>
            <span class="font-code text-label-sm bg-surface-container-lowest px-2 py-0.5 rounded text-secondary font-semibold">VỪA XONG</span>
          </div>
          <p class="font-body-md text-body-md mt-1 leading-relaxed">
            Đã đồng bộ lịch trình cho chương trình <strong>"${ten}"</strong> (${pb}) từ ngày <strong>${batDau}</strong> đến <strong>${ketThuc}</strong>. Thông báo tự động đã chuyển đến cổng thông tin sinh viên và hệ sinh thái liên kết ICTU.
          </p>
        </div>
        <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="hover:opacity-75 p-1 rounded-md transition-opacity" title="Đóng">
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
      `;
    hop.classList.remove("hidden");
    nut.innerHTML = oldContent;
    nut.disabled = false;
    hop.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, 700);
}
document.addEventListener("DOMContentLoaded", () => {
  tinhToanThoiGian();
});
