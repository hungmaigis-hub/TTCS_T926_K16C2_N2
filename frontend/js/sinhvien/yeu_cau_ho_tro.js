const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

function layIdSinhVien() {
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

function layTenLoaiYeuCau(loai) {
  const map = {
    XinChungNhan: "Chứng nhận thực tập",
    GiayXacNhan: "Xác nhận hoàn thành",
    DongDauMoc: "Đóng dấu mộc",
    TaiLieu: "Tài liệu dự án",
    Khac: "Yêu cầu khác"
  };
  return map[loai] || loai || "Yêu cầu";
}

function taoBadgeTrangThai(trangThai) {
  if (trangThai === "DaXuLy") {
    return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
      Đã xử lý
    </span>`;
  }
  if (trangThai === "TuChoi") {
    return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800">
      <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
      Từ chối
    </span>`;
  }
  return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800">
    <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
    Chờ xử lý
  </span>`;
}

function hienThongBao(msg, laLoi = false) {
  const box = document.getElementById("thongBaoYeuCau");
  const txt = document.getElementById("noiDungThongBaoYeuCau");
  const icon = document.getElementById("iconThongBaoYeuCau");
  if (!box || !txt) return;

  txt.textContent = msg;
  box.classList.remove("hidden");
  if (laLoi) {
    box.className = "p-3.5 rounded-xl text-xs flex items-start gap-2.5 bg-rose-50 border border-rose-200 text-rose-800";
    if (icon) icon.textContent = "error";
  } else {
    box.className = "p-3.5 rounded-xl text-xs flex items-start gap-2.5 bg-emerald-50 border border-emerald-200 text-emerald-800";
    if (icon) icon.textContent = "check_circle";
  }
}

async function taiDanhSachYeuCau() {
  const maHoSo = layIdSinhVien();
  const tbody = document.getElementById("tbodyDanhSachYeuCau");
  const badgeTotal = document.getElementById("badgeTongSoYeuCau");
  if (!tbody) return;

  try {
    const res = await fetch(`${duongDanApi}/support-requests?ma_ho_so=${maHoSo}`);
    if (!res.ok) throw new Error("Không thể tải danh sách yêu cầu hỗ trợ");
    const json = await res.json();
    const items = json.data || [];

    if (badgeTotal) badgeTotal.textContent = `${items.length} yêu cầu`;

    if (items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="py-10 text-center text-slate-400">
            <span class="material-symbols-outlined text-3xl mb-1 text-slate-300">inbox</span>
            <p>Bạn chưa gửi yêu cầu hỗ trợ nào.</p>
          </td>
        </tr>
      `;
      return;
    }

    let html = "";
    items.forEach(it => {
      const tenLoai = layTenLoaiYeuCau(it.loai_yeu_cau);
      const phanHoi = it.phan_hoi_hr ? `<span class="text-slate-700 font-medium">${it.phan_hoi_hr}</span>` : `<span class="text-slate-400 italic">Chưa có phản hồi</span>`;
      html += `
        <tr class="hover:bg-slate-50/80 transition-colors">
          <td class="py-3 px-4 font-mono font-bold text-slate-700">#${it.ma_yeu_cau}</td>
          <td class="py-3 px-4 font-bold text-slate-800">${tenLoai}</td>
          <td class="py-3 px-4 text-slate-600 max-w-xs break-words">${it.noi_dung}</td>
          <td class="py-3 px-4 text-center whitespace-nowrap">${taoBadgeTrangThai(it.trang_thai)}</td>
          <td class="py-3 px-4 max-w-xs break-words">${phanHoi}</td>
        </tr>
      `;
    });
    tbody.innerHTML = html;
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="py-8 text-center text-rose-500 font-semibold">
          Lỗi: ${err.message || "Không thể tải danh sách"}
        </td>
      </tr>
    `;
  }
}

async function guiYeuCauHoTro() {
  const maHoSo = layIdSinhVien();
  const selectLoai = document.getElementById("selectLoaiYeuCau");
  const inputTieuDe = document.getElementById("inputTieuDeYeuCau");
  const textareaNoiDung = document.getElementById("textareaNoiDungYeuCau");
  const btn = document.getElementById("btnGuiYeuCau");
  const icon = document.getElementById("iconGuiYeuCau");
  const text = document.getElementById("textGuiYeuCau");

  const loaiYeuCau = selectLoai ? selectLoai.value : "";
  const tieuDe = inputTieuDe ? inputTieuDe.value.trim() : "";
  const noiDung = textareaNoiDung ? textareaNoiDung.value.trim() : "";

  if (!loaiYeuCau) {
    hienThongBao("Vui lòng chọn loại yêu cầu hỗ trợ", true);
    return;
  }
  if (!tieuDe) {
    hienThongBao("Vui lòng nhập tiêu đề yêu cầu", true);
    if (inputTieuDe) inputTieuDe.focus();
    return;
  }
  if (!noiDung) {
    hienThongBao("Vui lòng nhập nội dung chi tiết", true);
    if (textareaNoiDung) textareaNoiDung.focus();
    return;
  }

  const noiDungGop = tieuDe ? `[${tieuDe}] - ${noiDung}` : noiDung;

  if (btn) {
    btn.disabled = true;
    if (icon) icon.className = "material-symbols-outlined text-[18px] animate-spin";
    if (icon) icon.textContent = "progress_activity";
    if (text) text.textContent = "Đang gửi...";
  }

  try {
    const payload = {
      ma_ho_so: maHoSo,
      loai_yeu_cau: loaiYeuCau,
      noi_dung: noiDungGop
    };

    const res = await fetch(`${duongDanApi}/support-requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      hienThongBao("Gửi yêu cầu hỗ trợ thành công! HR sẽ sớm phản hồi cho bạn.", false);
      if (inputTieuDe) inputTieuDe.value = "";
      if (textareaNoiDung) textareaNoiDung.value = "";
      taiDanhSachYeuCau();
    } else {
      let msg = "Không thể gửi yêu cầu hỗ trợ";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail)) {
        msg = resJson.detail.map(e => e.msg || e.message).join(", ");
      }
      hienThongBao(msg, true);
    }
  } catch (err) {
    hienThongBao(`Lỗi kết nối máy chủ: ${err.message || err}`, true);
  } finally {
    if (btn) {
      btn.disabled = false;
      if (icon) icon.className = "material-symbols-outlined text-[18px]";
      if (icon) icon.textContent = "send";
      if (text) text.textContent = "Gửi yêu cầu hỗ trợ";
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  taiDanhSachYeuCau();
});
