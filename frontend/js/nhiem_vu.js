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
            const h4 = card.querySelector("h4");
            if (h4) h4.textContent = task.ten_nhiem_vu;

            const pDesc = card.querySelector("p");
            if (pDesc && task.mo_ta) pDesc.textContent = task.mo_ta;

            const slider = card.querySelector(".thanh-tien-do");
            const labelChiSo = card.querySelector(".chi-so-tien-do");
            if (slider && task.tien_do_phantram !== undefined) {
              slider.value = task.tien_do_phantram;
              if (labelChiSo) labelChiSo.textContent = `${task.tien_do_phantram}%`;
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

  if (danhSach) {
    danhSach.addEventListener("input", (e) => {
      if (e.target && e.target.classList.contains("thanh-tien-do")) {
        const card = e.target.closest("article");
        const value = e.target.value;
        const labelChiSo = card?.querySelector(".chi-so-tien-do");
        const badgeTrangThai = card?.querySelector(".trang-thai-chu");
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
          card?.querySelector("h4")?.textContent.trim() || "Nhiệm vụ";
        const tienDo = card?.querySelector(".thanh-tien-do")?.value || "0";
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
        }, 400);
      }
    });
  }
});
