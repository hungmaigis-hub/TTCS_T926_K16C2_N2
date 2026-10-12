const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let danhSachNhiemVuGoc = [];
let tenMentorGoc = "TS. Nguyễn Hướng Dẫn";

function layMaHoSoHienTai() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);

  try {
    const raw = localStorage.getItem("ictu_student_session") || localStorage.getItem("currentUser") || localStorage.getItem("user");
    if (raw) {
      const u = JSON.parse(raw);
      if (u.ma_ho_so) return parseInt(u.ma_ho_so, 10);
      if (u.id) return parseInt(u.id, 10);
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

function dinhDangNgayVN(str) {
  if (!str) return "--";
  const pts = str.split("-");
  return pts.length === 3 ? `${pts[2]}/${pts[1]}/${pts[0]}` : str;
}

function renderDanhSachNhiemVu(tasks) {
  const container = document.getElementById("danhSachTheNhiemVu");
  if (!container) return;

  const total = tasks.length;
  const completed = tasks.filter((t) => (t.tien_do_phantram || 0) === 100).length;
  const inProgress = tasks.filter((t) => (t.tien_do_phantram || 0) > 0 && (t.tien_do_phantram || 0) < 100).length;
  const notStarted = tasks.filter((t) => (t.tien_do_phantram || 0) === 0).length;
  const avg = total > 0 ? Math.round(tasks.reduce((sum, t) => sum + (t.tien_do_phantram || 0), 0) / total) : 0;

  const elAvg = document.getElementById("tienDoTongThePhanTram");
  if (elAvg) elAvg.textContent = `${avg}%`;
  const elBar = document.getElementById("thanhTienDoTongThe");
  if (elBar) elBar.style.width = `${avg}%`;

  const elTong = document.getElementById("soTongNhiemVu");
  if (elTong) elTong.textContent = `${total} việc`;
  const elHoanThanh = document.getElementById("soNhiemVuHoanThanh");
  if (elHoanThanh) elHoanThanh.textContent = `${completed} việc`;
  const elDangLam = document.getElementById("soNhiemVuDangTienHanh");
  if (elDangLam) elDangLam.textContent = `${inProgress} việc`;
  const elChuaLam = document.getElementById("soNhiemVuChuaBatDau");
  if (elChuaLam) elChuaLam.textContent = `${notStarted} việc`;
  const elBadge = document.getElementById("soLuongNhiemVuBadge");
  if (elBadge) elBadge.textContent = `${total} mục hiển thị`;

  if (tasks.length === 0) {
    container.innerHTML = `
      <div class="bg-white rounded-2xl p-10 text-center border border-slate-200/80 shadow-xs space-y-3">
        <div class="w-14 h-14 mx-auto rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
          <span class="material-symbols-outlined text-[32px]">task</span>
        </div>
        <h4 class="text-base font-bold text-slate-800">Chưa có nhiệm vụ nào được phân công</h4>
        <p class="text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
          Mentor phụ trách chưa giao nhiệm vụ Sprint cho bạn. Khi Mentor phân công nhiệm vụ mới, các đầu việc và thanh trượt tiến độ sẽ xuất hiện tại đây.
        </p>
      </div>
    `;
    return;
  }

  container.innerHTML = tasks
    .map((task) => {
      const progress = task.tien_do_phantram !== undefined ? task.tien_do_phantram : 0;
      let badgeClass = "bg-blue-50 text-blue-700 border border-blue-200";
      let ttText = "Đang thực hiện";

      if (progress === 0) {
        badgeClass = "bg-slate-100 text-slate-600 border border-slate-200";
        ttText = "Chưa bắt đầu";
      } else if (progress === 100) {
        badgeClass = "bg-emerald-50 text-emerald-700 border border-emerald-200";
        ttText = "Hoàn thành";
      }

      const fDate = dinhDangNgayVN(task.han_hoan_thanh);

      return `
        <article data-task-id="${task.ma_nhiem_vu}" class="bg-white rounded-2xl p-6 shadow-xs border border-slate-200/80 space-y-4 hover:shadow-md transition-all">
          <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
            <div class="space-y-1">
              <div class="flex items-center gap-2.5 flex-wrap">
                <span class="font-label-sm px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-50 text-emerald-800 border border-emerald-200">Sprint Task</span>
                <span class="trang-thai-chu font-label-sm px-2.5 py-0.5 rounded-full text-xs font-semibold ${badgeClass}">Trạng thái: ${ttText}</span>
              </div>
              <h4 class="font-headline-sm text-slate-900 font-bold text-base pt-1">${task.ten_nhiem_vu}</h4>
            </div>
            <div class="flex items-center gap-1.5 text-xs bg-slate-50 border border-slate-200/70 text-slate-700 px-3 py-1.5 rounded-xl shrink-0 font-medium">
              <span class="material-symbols-outlined text-[16px] text-slate-500">event</span>
              <span>Hạn chót: ${fDate}</span>
            </div>
          </div>
          <p class="text-sm text-slate-600 leading-relaxed">${task.mo_ta || "Hoàn thành đầu việc theo yêu cầu phân công của Mentor hướng dẫn."}</p>
          <div class="bg-slate-50/80 p-4 rounded-xl space-y-2 border border-slate-200/70">
            <div class="flex items-center justify-between">
              <label class="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[18px] text-emerald-600">linear_scale</span>
                <span>Điều chỉnh thanh trượt tiến độ công việc:</span>
              </label>
              <span class="chi-so-tien-do text-lg font-bold text-emerald-700 font-mono">${progress}%</span>
            </div>
            <div class="relative flex items-center">
              <input class="thanh-tien-do w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600" max="100" min="0" type="range" value="${progress}" />
            </div>
            <div class="flex justify-between text-[11px] text-slate-400 px-0.5 font-medium">
              <span>0% (Bắt đầu)</span>
              <span>50% (Đang test)</span>
              <span>100% (Hoàn thiện)</span>
            </div>
          </div>
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1 border-t border-slate-100">
            <div class="flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white font-bold text-xs shadow-xs">MT</div>
              <div>
                <p class="text-[11px] text-slate-400">Mentor hướng dẫn:</p>
                <p class="text-xs font-bold text-slate-800">${tenMentorGoc}</p>
              </div>
            </div>
            <div class="flex items-center gap-2.5 flex-wrap">
              <button class="nut-luu-tien-do flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-4 py-2.5 rounded-xl shadow-xs transition-all cursor-pointer" type="button">
                <span class="material-symbols-outlined text-[18px]">save</span>
                <span>Lưu tiến độ</span>
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function locNhiemVuTheoTrangThai() {
  const filterVal = document.getElementById("boLocTrangThai")?.value || "tat-ca";
  if (filterVal === "tat-ca") {
    renderDanhSachNhiemVu(danhSachNhiemVuGoc);
    return;
  }

  const filtered = danhSachNhiemVuGoc.filter((t) => {
    const p = t.tien_do_phantram || 0;
    if (filterVal === "HoanThanh") return p === 100;
    if (filterVal === "ChuaBatDau") return p === 0;
    if (filterVal === "DangThucHien") return p > 0 && p < 100;
    return true;
  });

  renderDanhSachNhiemVu(filtered);
}

async function taiLichTrinhVaNhiemVu() {
  const maHoSo = layMaHoSoHienTai();
  try {
    const res = await fetch(`${duongDanApi}/interns/my-schedule?ho_so_id=${maHoSo}`);
    if (!res.ok) {
      renderDanhSachNhiemVu([]);
      return;
    }

    const resJson = await res.json();
    const data = resJson.data;
    if (!data) {
      renderDanhSachNhiemVu([]);
      return;
    }

    if (data.ho_ten) {
      const tenSinhVienEl = document.querySelector("header h2");
      if (tenSinhVienEl) tenSinhVienEl.textContent = `Nhiệm vụ: ${data.ho_ten}`;
    }

    if (data.ten_chuong_trinh) {
      const bannerEl = document.getElementById("theHocKyNhiemVuBanner");
      if (bannerEl) bannerEl.textContent = data.ten_chuong_trinh;
    }

    if (data.mentor) {
      tenMentorGoc = data.mentor;
    }

    if (data.ngay_ket_thuc) {
      const dEnd = new Date(data.ngay_ket_thuc);
      const now = new Date();
      const diffMs = dEnd.getTime() - now.getTime();
      const diffDays = Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)));
      const elRemaining = document.getElementById("soNgayConLai");
      if (elRemaining) elRemaining.textContent = `${diffDays} ngày`;
    }

    danhSachNhiemVuGoc = data.danh_sach_nhiem_vu || [];
    renderDanhSachNhiemVu(danhSachNhiemVuGoc);
  } catch (e) {
    renderDanhSachNhiemVu([]);
  }
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

  const danhSach = document.getElementById("danhSachTheNhiemVu");

  kiemTraKetNoiApi();

  async function kiemTraKetNoiApi() {
    const badge = document.getElementById("badgeTrangThaiApi");
    if (!badge) return;
    try {
      const baseUrlDocs = typeof layDuongDanGocBackend === "function" ? layDuongDanGocBackend() : "http://127.0.0.1:8000";
      await fetch(`${baseUrlDocs}/docs`, {
        method: "HEAD",
        mode: "no-cors",
      });
      badge.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Máy chủ: Đã kết nối`;
      badge.classList.remove("hidden");
    } catch {
      badge.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs";
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
            badgeTrangThai.className = "trang-thai-chu font-label-sm px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200";
            badgeTrangThai.textContent = "Trạng thái: Chưa bắt đầu";
          } else if (value === 100) {
            badgeTrangThai.className = "trang-thai-chu font-label-sm px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200";
            badgeTrangThai.textContent = "Trạng thái: Hoàn thành";
          } else {
            badgeTrangThai.className = "trang-thai-chu font-label-sm px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200";
            badgeTrangThai.textContent = "Trạng thái: Đang thực hiện";
          }
        }
      }
    });

    danhSach.addEventListener("click", async (e) => {
      const nutLuu = e.target.closest(".nut-luu-tien-do");
      if (!nutLuu) return;

      const card = nutLuu.closest("article");
      const taskId = card?.getAttribute("data-task-id");
      if (!taskId) return;

      const tenNhiemVu = card?.querySelector("h4")?.textContent.trim() || "Nhiệm vụ";
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

        const idx = danhSachNhiemVuGoc.findIndex((t) => String(t.ma_nhiem_vu) === String(taskId));
        if (idx !== -1) {
          danhSachNhiemVuGoc[idx].tien_do_phantram = tienDo;
          if (taskData?.trang_thai) danhSachNhiemVuGoc[idx].trang_thai = taskData.trang_thai;
        }

        if (badgeTrangThai && taskData && taskData.trang_thai) {
          badgeTrangThai.textContent = `Trạng thái: ${taskData.trang_thai}`;
        }

        const total = danhSachNhiemVuGoc.length;
        const avg = total > 0 ? Math.round(danhSachNhiemVuGoc.reduce((sum, t) => sum + (t.tien_do_phantram || 0), 0) / total) : 0;
        const elAvg = document.getElementById("tienDoTongThePhanTram");
        if (elAvg) elAvg.textContent = `${avg}%`;
        const elBar = document.getElementById("thanhTienDoTongThe");
        if (elBar) elBar.style.width = `${avg}%`;

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
