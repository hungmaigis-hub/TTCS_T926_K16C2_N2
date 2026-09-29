const duongDanApi = "http://127.0.0.1:8000/api/v1";

function layMaHoSoHienTai() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl);

  try {
    const userStr = localStorage.getItem("currentUser");
    if (userStr) {
      const user = JSON.parse(userStr);
      if (user.ma_ho_so) return parseInt(user.ma_ho_so);
    }
  } catch (e) {}

  return 1;
}

function moModalBaoCao() {
  const modal = document.getElementById("modalBaoCaoTuan");
  if (modal) modal.classList.remove("hidden");
}

function dongModalBaoCao() {
  const modal = document.getElementById("modalBaoCaoTuan");
  if (modal) modal.classList.add("hidden");
}

async function guiBaoCaoTuan() {
  const maHoSo = layMaHoSoHienTai();
  const tuanSo = parseInt(document.getElementById("baoCaoTuanSo")?.value || "1");
  const noiDung = document.getElementById("baoCaoNoiDung")?.value.trim();
  const ketQua = document.getElementById("baoCaoKetQua")?.value.trim();
  const nutGui = document.getElementById("nutGuiBaoCao");
  const hopThongBao = document.getElementById("hopThongBao");

  if (!noiDung) {
    alert("Vui lòng nhập nội dung công việc đã thực hiện trong tuần.");
    return;
  }

  const oldBtnHtml = nutGui ? nutGui.innerHTML : "";
  if (nutGui) {
    nutGui.disabled = true;
    nutGui.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span> <span>Đang gửi...</span>`;
  }

  try {
    const payload = {
      ma_ho_so: maHoSo,
      tuan_so: tuanSo,
      noi_dung_cong_viec: noiDung,
      ket_qua_dat_duoc: ketQua || null,
    };

    const res = await fetch(`${duongDanApi}/reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const resJson = await res.json();

    if (res.ok) {
      dongModalBaoCao();
      document.getElementById("formNopBaoCao")?.reset();

      if (hopThongBao) {
        hopThongBao.className =
          "rounded-xl bg-secondary-container text-on-secondary-container p-4 shadow-sm flex items-start gap-3.5 transition-all";
        hopThongBao.innerHTML = `
          <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 shadow-sm mt-0.5">
            <span class="material-symbols-outlined text-[20px]">check_circle</span>
          </div>
          <div class="flex-1 text-body-sm text-on-surface">
            <div class="flex items-center justify-between">
              <span class="font-label-lg text-secondary text-body-md font-bold">Nộp báo cáo tuần ${tuanSo} thành công!</span>
              <span class="font-label-sm text-outline">Vừa xong</span>
            </div>
            <p class="text-on-surface-variant mt-1 leading-relaxed">
              Báo cáo tiến độ tuần ${tuanSo} của bạn đã được lưu vào hệ thống CSDL Backend. Mentor phụ trách sẽ nhận thông báo để thẩm định và cho nhận xét.
            </p>
          </div>
          <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-outline hover:text-on-surface p-1 rounded-md transition-colors" title="Đóng">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        `;
        hopThongBao.classList.remove("hidden");
        hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    } else {
      const errMsg =
        typeof resJson.detail === "string"
          ? resJson.detail
          : resJson.detail?.[0]?.msg || "Không thể gửi báo cáo tuần!";
      alert(`Lỗi nộp báo cáo: ${errMsg}`);
    }
  } catch (err) {
    alert("Không thể kết nối đến máy chủ Backend (http://127.0.0.1:8000). Vui lòng đảm bảo server đang chạy!");
  } finally {
    if (nutGui) {
      nutGui.disabled = false;
      nutGui.innerHTML = oldBtnHtml;
    }
  }
}

async function taiLichTrinhVaNhiemVu() {
  const maHoSo = layMaHoSoHienTai();
  try {
    const res = await fetch(`${duongDanApi}/interns/my-schedule?ho_so_id=${maHoSo}`);
    if (!res.ok) return;

    const resJson = await res.json();
    const data = resJson.data;
    if (!data) return;

    if (data.ho_ten) {
      const tenSinhVienEl = document.querySelector("header h2");
      if (tenSinhVienEl) tenSinhVienEl.textContent = `Nhiệm vụ: ${data.ho_ten}`;
    }

    const tasks = data.danh_sach_nhiem_vu || [];
    if (tasks.length > 0) {
      const danhSachEl = document.getElementById("danhSachNhiemVu");
      if (danhSachEl) {
        const danhSachArticles = danhSachEl.querySelectorAll("article");
        tasks.forEach((task, idx) => {
          if (danhSachArticles[idx]) {
            const card = danhSachArticles[idx];
            if (task.ma_nhiem_vu) {
              card.setAttribute("data-task-id", task.ma_nhiem_vu);
            }
            const h4 = card.querySelector("h4");
            if (h4) h4.textContent = task.ten_nhiem_vu;

            const pDesc = card.querySelector("p");
            if (pDesc && task.mo_ta) pDesc.textContent = task.mo_ta;

            const slider = card.querySelector(".thanh-tien-do");
            const labelChiSo = card.querySelector(".chi-so-tien-do");
            const badgeTrangThai = card.querySelector(".trang-thai-chu");
            if (slider && task.tien_do_phantram !== undefined) {
              slider.value = task.tien_do_phantram;
              if (labelChiSo) labelChiSo.textContent = `${task.tien_do_phantram}%`;
              if (badgeTrangThai && task.trang_thai) {
                badgeTrangThai.textContent = `Trạng thái: ${task.trang_thai}`;
              }
            }
          }
        });
      }
    }
  } catch (e) {}
}

document.addEventListener("DOMContentLoaded", () => {
  taiLichTrinhVaNhiemVu();

  const danhSach = document.getElementById("danhSachNhiemVu");
  const hopThongBao = document.getElementById("hopThongBao");

  // Kiểm tra trạng thái kết nối tới Backend API
  kiemTraKetNoiApi();

  async function kiemTraKetNoiApi() {
    const badge = document.getElementById("badgeTrangThaiApi");
    if (!badge) return;
    try {
      await fetch("http://127.0.0.1:8000/docs", {
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

  if (danhSach) {
    // Lắng nghe sự kiện trượt thanh tiến độ để cập nhật hiển thị tức thì trên giao diện
    danhSach.addEventListener("input", (e) => {
      if (e.target && e.target.classList.contains("thanh-tien-do")) {
        const card = e.target.closest("article");
        const value = parseInt(e.target.value, 10);
        const labelChiSo = card?.querySelector(".chi-so-tien-do");
        const badgeTrangThai = card?.querySelector(".trang-thai-chu");

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
      const taskId = card?.getAttribute("data-task-id") || "1";
      const tenNhiemVu =
        card?.querySelector("h4")?.textContent.trim() || "Nhiệm vụ";
      const thanhTienDo = card?.querySelector(".thanh-tien-do");
      const tienDo = parseInt(thanhTienDo ? thanhTienDo.value : "0", 10);
      const badgeTrangThai = card?.querySelector(".trang-thai-chu");

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
  }

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
