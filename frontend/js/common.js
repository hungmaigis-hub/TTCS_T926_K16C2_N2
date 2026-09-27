function kichHoatHienThi() {
  document.documentElement.classList.add("loaded");
}

window.addEventListener("DOMContentLoaded", kichHoatHienThi);
setTimeout(kichHoatHienThi, 300);

function thongBaoDangCapNhat(tenTinhNang, moTa) {
  let modal = document.getElementById("modal-thong-bao-cap-nhat");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "modal-thong-bao-cap-nhat";
    modal.className =
      "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm transition-opacity opacity-0 pointer-events-none duration-200";
    modal.innerHTML = `
      <div id="modal-thong-bao-card" class="relative w-full max-w-md bg-white rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-100 flex flex-col items-center text-center transform scale-95 transition-transform duration-200">
        <button type="button" onclick="dongThongBaoCapNhat()" class="absolute top-4 right-4 w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 flex items-center justify-center transition-colors">
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
        <div class="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 mb-4 shadow-sm ring-4 ring-amber-50">
          <span class="material-symbols-outlined text-[32px]">hourglass_top</span>
        </div>
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 mb-2.5">
          <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
          Tính năng đang cập nhật
        </div>
        <h3 id="modal-cap-nhat-tieude" class="text-lg sm:text-xl font-bold text-slate-900 mb-2">
          Đang hoàn thiện tính năng
        </h3>
        <p id="modal-cap-nhat-noidung" class="text-sm text-slate-600 leading-relaxed mb-6">
          Chức năng hiện đang được phát triển trong kế hoạch Sprint tiếp theo. Vui lòng quay lại sau!
        </p>
        <div class="w-full p-3.5 rounded-2xl bg-slate-50 border border-slate-100 text-left mb-6 flex items-start gap-3">
          <span class="material-symbols-outlined text-[20px] text-emerald-600 shrink-0 mt-0.5">tips_and_updates</span>
          <p class="text-xs text-slate-600 leading-relaxed">
            Bạn có thể trải nghiệm các phân hệ đã sẵn sàng: <strong class="text-slate-800">Tổng quan thực tập</strong>, <strong class="text-slate-800">Nộp tài liệu &amp; CV</strong>, <strong class="text-slate-800">Ký hợp đồng</strong>, và <strong class="text-slate-800">Bảng nhiệm vụ</strong>.
          </p>
        </div>
        <div class="w-full flex gap-3">
          <button type="button" onclick="dongThongBaoCapNhat()" class="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold shadow-sm hover:shadow transition-all">
            Đã hiểu, đóng thông báo
          </button>
        </div>
      </div>
    `;
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        dongThongBaoCapNhat();
      }
    });
    document.body.appendChild(modal);
  }

  const tieuDeEl = document.getElementById("modal-cap-nhat-tieude");
  const noiDungEl = document.getElementById("modal-cap-nhat-noidung");

  if (tenTinhNang) {
    tieuDeEl.textContent = tenTinhNang;
    noiDungEl.innerHTML =
      moTa ||
      `Chức năng <span class="font-semibold text-slate-900">${tenTinhNang}</span> hiện đang được hoàn thiện theo kế hoạch mở rộng của hệ thống. Bạn sẽ nhận được thông báo khi phân hệ này được mở khóa!`;
  } else {
    tieuDeEl.textContent = "Tính năng đang hoàn thiện";
    noiDungEl.innerHTML =
      moTa ||
      "Chức năng này thuộc kế hoạch phát triển bổ sung và đang được hoàn tất. Vui lòng quay lại sau!";
  }

  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
  const card = document.getElementById("modal-thong-bao-card");
  if (card) {
    card.classList.remove("scale-95");
    card.classList.add("scale-100");
  }
}

function dongThongBaoCapNhat() {
  const modal = document.getElementById("modal-thong-bao-cap-nhat");
  if (!modal) return;
  const card = document.getElementById("modal-thong-bao-card");
  if (card) {
    card.classList.remove("scale-100");
    card.classList.add("scale-95");
  }
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    dongThongBaoCapNhat();
  }
});

document.addEventListener("click", function (e) {
  const target = e.target.closest("[data-coming-soon], [data-chua-hoan-thien]");
  if (target) {
    e.preventDefault();
    const ten =
      target.getAttribute("data-coming-soon") ||
      target.getAttribute("data-chua-hoan-thien") ||
      target.textContent.trim();
    thongBaoDangCapNhat(ten);
  }
});
