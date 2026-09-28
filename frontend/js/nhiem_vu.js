const duongDanApi = "http://127.0.0.1:8000/api/v1";

document.addEventListener("DOMContentLoaded", () => {
  const danhSach = document.getElementById("danhSachNhiemVu");
  const hopThongBao = document.getElementById("hopThongBao");

  // Kiểm tra trạng thái kết nối tới Backend API
  kiemTraKetNoiApi();

  async function kiemTraKetNoiApi() {
    const badge = document.getElementById("badgeTrangThaiApi");
    if (!badge) return;
    try {
      const phanHoi = await fetch("http://127.0.0.1:8000/docs", {
        method: "HEAD",
        mode: "no-cors",
      });
      badge.className =
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Backend: Đã kết nối API`;
      badge.classList.remove("hidden");
    } catch {
      badge.className =
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Chế độ Thử nghiệm (Offline)`;
      badge.classList.remove("hidden");
    }
  }

  // Lắng nghe sự kiện trượt thanh tiến độ để cập nhật hiển thị tức thì trên giao diện
  danhSach.addEventListener("input", (e) => {
    if (e.target && e.target.classList.contains("thanh-tien-do")) {
      const card = e.target.closest("article");
      const value = parseInt(e.target.value, 10);
      const labelChiSo = card.querySelector(".chi-so-tien-do");
      const badgeTrangThai = card.querySelector(".trang-thai-chu");

      if (labelChiSo) {
        labelChiSo.textContent = `${value}%`;
      }
      if (badgeTrangThai) {
        if (value === 0) {
          badgeTrangThai.textContent = "Trạng thái: Chưa bắt đầu";
        } else if (value === 100) {
          badgeTrangThai.textContent = "Trạng thái: Hoàn thành";
        } else {
          badgeTrangThai.textContent = "Trạng thái: Đang thực hiện";
        }
      }
    }
  });

  // Lắng nghe sự kiện click nút "Lưu tiến độ" -> Gọi API PATCH /api/v1/tasks/{id}/progress
  danhSach.addEventListener("click", async (e) => {
    const nutLuu = e.target.closest(".nut-luu-tien-do");
    if (!nutLuu) return;

    const card = nutLuu.closest("article");
    const taskId = card.getAttribute("data-task-id") || "1";
    const tenNhiemVu =
      card.querySelector("h4")?.textContent.trim() || "Nhiệm vụ";
    const thanhTienDo = card.querySelector(".thanh-tien-do");
    const tienDo = parseInt(thanhTienDo ? thanhTienDo.value : "0", 10);
    const badgeTrangThai = card.querySelector(".trang-thai-chu");

    const originalContent = nutLuu.innerHTML;
    nutLuu.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang lưu...</span>`;
    nutLuu.disabled = true;

    try {
      const response = await fetch(`${duongDanApi}/tasks/${taskId}/progress`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          tien_do_phantram: tienDo,
        }),
      });

      if (!response.ok) {
        throw new Error(`Máy chủ phản hồi mã lỗi HTTP ${response.status}`);
      }

      const resJson = await response.json();
      const taskData = resJson.data;

      // Cập nhật trạng thái chuẩn xác từ CSDL Backend trả về
      if (badgeTrangThai && taskData && taskData.trang_thai) {
        badgeTrangThai.textContent = `Trạng thái: ${taskData.trang_thai}`;
      }

      hienThiThongBao(
        "success",
        "Cập nhật tiến độ thành công!",
        `Đã lưu mức hoàn thành <strong>${tienDo}%</strong> cho nhiệm vụ: <em>"${tenNhiemVu}"</em> lên cơ sở dữ liệu. Trạng thái hiện tại: <strong>${
          taskData?.trang_thai || "Đã lưu"
        }</strong>.`
      );
    } catch (err) {
      console.warn("Backend offline hoặc gặp lỗi, sử dụng fallback:", err);

      // Fallback cục bộ khi chưa bật backend
      let fallbackStatus = "Đang thực hiện";
      if (tienDo === 100) fallbackStatus = "Hoàn thành";
      else if (tienDo === 0) fallbackStatus = "Chưa bắt đầu";

      if (badgeTrangThai) {
        badgeTrangThai.textContent = `Trạng thái: ${fallbackStatus}`;
      }

      hienThiThongBao(
        "info",
        "Đã ghi nhận tiến độ (Chế độ mô phỏng)!",
        `Đã lưu mức hoàn thành <strong>${tienDo}%</strong> cho nhiệm vụ: <em>"${tenNhiemVu}"</em>. (Lưu ý: Đang chạy ở chế độ thử nghiệm cục bộ do server Backend chưa bật).`
      );
    } finally {
      nutLuu.innerHTML = originalContent;
      nutLuu.disabled = false;
    }
  });

  // Hàm hiển thị thông báo phản hồi thao tác trực quan
  function hienThiThongBao(loai, tieuDe, noiDung) {
    if (!hopThongBao) return;

    const isSuccess = loai === "success";
    const bgClass = isSuccess
      ? "bg-emerald-50 text-emerald-950 border border-emerald-200"
      : "bg-surface-container-low text-on-surface border border-outline-variant";
    const iconColor = isSuccess
      ? "bg-emerald-600 text-white"
      : "bg-secondary text-on-secondary";

    hopThongBao.className = `rounded-xl ${bgClass} p-4 shadow-sm flex items-start gap-3.5 transition-all`;
    hopThongBao.innerHTML = `
      <div class="w-8 h-8 rounded-lg ${iconColor} flex items-center justify-center shrink-0 shadow-sm mt-0.5">
        <span class="material-symbols-outlined text-[20px]">${
          isSuccess ? "check_circle" : "info"
        }</span>
      </div>
      <div class="flex-1 text-body-sm">
        <div class="flex items-center justify-between">
          <span class="font-label-lg font-bold text-body-md">${tieuDe}</span>
          <span class="font-label-sm text-outline">Vừa xong</span>
        </div>
        <p class="mt-1 leading-relaxed text-sm">
          ${noiDung}
        </p>
      </div>
      <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-outline hover:text-on-surface p-1 rounded-md transition-colors" title="Đóng">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    `;
    hopThongBao.classList.remove("hidden");
    hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
});
