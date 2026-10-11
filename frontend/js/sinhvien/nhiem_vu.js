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

function hienThiThongBaoChung(loai, tieuDe, noiDung) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) return;

  let bgClass = "bg-emerald-50 text-emerald-950 border border-emerald-200";
  let iconColor = "bg-emerald-600 text-white";
  let iconName = "check_circle";

  if (loai === "error") {
    bgClass = "bg-rose-50 text-rose-950 border border-rose-200";
    iconColor = "bg-rose-600 text-white";
    iconName = "error";
  } else if (loai === "warning") {
    bgClass = "bg-amber-50 text-amber-950 border border-amber-200";
    iconColor = "bg-amber-600 text-white";
    iconName = "warning";
  } else if (loai === "info") {
    bgClass = "bg-blue-50 text-blue-950 border border-blue-200";
    iconColor = "bg-blue-600 text-white";
    iconName = "info";
  }

  hopThongBao.className = `rounded-xl ${bgClass} p-4 shadow-sm flex items-start gap-3.5 transition-all`;
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-lg ${iconColor} flex items-center justify-center shrink-0 shadow-sm mt-0.5">
      <span class="material-symbols-outlined text-[20px]">${iconName}</span>
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

async function guiBaoCaoTuan() {
  const maHoSo = layMaHoSoHienTai();
  const tuanSoEl = document.getElementById("baoCaoTuanSo");
  const tuanSo = parseInt(tuanSoEl?.value || "1", 10);
  const noiDung = document.getElementById("baoCaoNoiDung")?.value.trim();
  const ketQua = document.getElementById("baoCaoKetQua")?.value.trim();
  const nutGui = document.getElementById("nutGuiBaoCao");

  if (isNaN(tuanSo) || tuanSo < 1 || tuanSo > 52) {
    hienThiThongBaoChung("warning", "Tuần báo cáo không hợp lệ", "Vui lòng chọn tuần báo cáo hợp lệ trong khoảng từ tuần 1 đến tuần 52.");
    return;
  }

  if (!noiDung || noiDung.length < 10) {
    hienThiThongBaoChung("warning", "Nội dung báo cáo quá ngắn", "Vui lòng nhập nội dung chi tiết công việc đã thực hiện trong tuần (tối thiểu 10 ký tự).");
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

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      dongModalBaoCao();
      document.getElementById("formNopBaoCao")?.reset();
      hienThiThongBaoChung(
        "success",
        `Nộp báo cáo tuần ${tuanSo} thành công!`,
        `Báo cáo tiến độ tuần ${tuanSo} của bạn đã được ghi nhận vào cơ sở dữ liệu. Mentor phụ trách sẽ nhận thông báo để thẩm định và nhận xét.`
      );
    } else {
      let errMsg = "Không thể gửi báo cáo tuần!";
      if (typeof resJson.detail === "string") {
        errMsg = resJson.detail;
      } else if (Array.isArray(resJson.detail) && resJson.detail[0]?.msg) {
        errMsg = resJson.detail[0].msg;
      }
      hienThiThongBaoChung("error", "Lỗi nộp báo cáo", errMsg);
    }
  } catch (err) {
    hienThiThongBaoChung("error", "Mất kết nối máy chủ", "Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau.");
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

    if (data.ten_chuong_trinh) {
      const bannerEl = document.getElementById("theHocKyNhiemVuBanner");
      if (bannerEl) bannerEl.textContent = data.ten_chuong_trinh;
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

            const badgeHan = card.querySelector("div.shrink-0 span:last-child");
            if (badgeHan && task.han_hoan_thanh) {
              const pts = task.han_hoan_thanh.split("-");
              const fDate = pts.length === 3 ? `${pts[2]}/${pts[1]}/${pts[0]}` : task.han_hoan_thanh;
              badgeHan.textContent = `Hạn chót: ${fDate}`;
            }

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

function capNhatNienKhoaNhiemVu() {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;
  const elSidebar = document.getElementById("theHocKyNhiemVuSidebar");
  if (elSidebar) elSidebar.textContent = `Học kỳ ${nienKhoa}`;
  const elBanner = document.getElementById("theHocKyNhiemVuBanner");
  if (elBanner && !elBanner.getAttribute("data-loaded-program")) {
    elBanner.textContent = `Kỳ ${nienKhoa}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  capNhatNienKhoaNhiemVu();
  taiLichTrinhVaNhiemVu();

  const danhSach = document.getElementById("danhSachNhiemVu");
  const hopThongBao = document.getElementById("hopThongBao");

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
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Máy chủ: Đã kết nối`;
      badge.classList.remove("hidden");
    } catch {
      badge.className =
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Ngoại tuyến`;
      badge.classList.remove("hidden");
    }
  }

  if (danhSach) {
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

    danhSach.addEventListener("click", async (e) => {
      const nutLuu = e.target.closest(".nut-luu-tien-do");
      if (!nutLuu) return;

      const card = nutLuu.closest("article");
      const taskId = card?.getAttribute("data-task-id") || "1";
      const tenNhiemVu =
        card?.querySelector("h4")?.textContent.trim() || "Nhiệm vụ";
      const thanhTienDo = card?.querySelector(".thanh-tien-do");
      const rawTienDo = parseInt(thanhTienDo ? thanhTienDo.value : "0", 10);
      const tienDo = Math.min(100, Math.max(0, isNaN(rawTienDo) ? 0 : rawTienDo));
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

        const resJson = await response.json().catch(() => ({}));

        if (!response.ok) {
          let errMsg = "Không thể cập nhật tiến độ công việc!";
          if (typeof resJson.detail === "string") {
            errMsg = resJson.detail;
          } else if (Array.isArray(resJson.detail) && resJson.detail[0]?.msg) {
            errMsg = resJson.detail[0].msg;
          }
          hienThiThongBaoChung("error", "Lỗi cập nhật tiến độ", errMsg);
          return;
        }

        const taskData = resJson.data;

        if (badgeTrangThai && taskData && taskData.trang_thai) {
          badgeTrangThai.textContent = `Trạng thái: ${taskData.trang_thai}`;
        }

        hienThiThongBaoChung(
          "success",
          "Cập nhật tiến độ thành công!",
          `Đã lưu mức hoàn thành <strong>${tienDo}%</strong> cho nhiệm vụ: <em>"${tenNhiemVu}"</em> lên cơ sở dữ liệu. Trạng thái hiện tại: <strong>${
            taskData?.trang_thai || "Đã lưu"
          }</strong>.`
        );
      } catch (err) {
        hienThiThongBaoChung(
          "error",
          "Mất kết nối máy chủ",
          `Không thể lưu tiến độ cho nhiệm vụ: <em>"${tenNhiemVu}"</em>. Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau.`
        );
      } finally {
        nutLuu.innerHTML = originalContent;
        nutLuu.disabled = false;
      }
    });
  }
});
