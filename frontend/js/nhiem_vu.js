document.addEventListener("DOMContentLoaded", () => {
  const danhSach = document.getElementById("danhSachNhiemVu");
  const hopThongBao = document.getElementById("hopThongBao");
  danhSach.addEventListener("input", (e) => {
    if (e.target && e.target.classList.contains("thanh-tien-do")) {
      const card = e.target.closest("article");
      const value = e.target.value;
      const labelChiSo = card.querySelector(".chi-so-tien-do");
      const badgeTrangThai = card.querySelector(".trang-thai-chu");
      if (labelChiSo) {
        labelChiSo.textContent = `${value}%`;
      }
      if (badgeTrangThai) {
        if (parseInt(value) === 0) {
          badgeTrangThai.textContent = "Trạng thái: Chưa bắt đầu";
        } else if (parseInt(value) === 100) {
          badgeTrangThai.textContent = "Trạng thái: Đã hoàn thành";
        } else {
          badgeTrangThai.textContent = "Trạng thái: Đang thực hiện";
        }
      }
    }
  });
  danhSach.addEventListener("click", (e) => {
    const nutLuu = e.target.closest(".nut-luu-tien-do");
    if (nutLuu) {
      const card = nutLuu.closest("article");
      const tenNhiemVu =
        card.querySelector("h4")?.textContent.trim() || "Nhiệm vụ";
      const tienDo = card.querySelector(".thanh-tien-do")?.value || "0";
      const originalContent = nutLuu.innerHTML;
      nutLuu.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang lưu...</span>`;
      nutLuu.disabled = true;
      setTimeout(() => {
        nutLuu.innerHTML = originalContent;
        nutLuu.disabled = false;
        if (hopThongBao) {
          hopThongBao.className =
            "rounded-xl bg-surface-container-low p-4 shadow-sm flex items-start gap-3.5 transition-all";
          hopThongBao.innerHTML = `
                <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                  <span class="material-symbols-outlined text-[20px]">check_circle</span>
                </div>
                <div class="flex-1 text-body-sm text-on-surface">
                  <div class="flex items-center justify-between">
                    <span class="font-label-lg text-secondary text-body-md font-bold">Cập nhật tiến độ thành công!</span>
                    <span class="font-label-sm text-outline">Vừa xong</span>
                  </div>
                  <p class="text-on-surface-variant mt-1 leading-relaxed">
                    Đã ghi nhận mức hoàn thành <strong>${tienDo}%</strong> cho nhiệm vụ: <em>"${tenNhiemVu}"</em>. Mentor doanh nghiệp sẽ nhận được thông báo kiểm tra.
                  </p>
                </div>
                <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-outline hover:text-on-surface p-1 rounded-md transition-colors" title="Đóng">
                  <span class="material-symbols-outlined text-[18px]">close</span>
                </button>
              `;
          hopThongBao.classList.remove("hidden");
          hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }, 500);
    }
  });
});
