const duongDanApiUpload = "http://127.0.0.1:8000/api/v1/documents/upload";
const duongDanApiDocuments = "http://127.0.0.1:8000/api/v1/documents";

const tepInput = document.getElementById("tepDinhKem");
const vungKeoTha = document.getElementById("vungKeoTha");
const tenTepVanBan = document.getElementById("tenTepVanBan");
const dungLuongTep = document.getElementById("dungLuongTep");
const tenTepHienThi = document.getElementById("tenTepHienThi");

function layMaHoSoHienTai() {
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get("id");
  if (idFromUrl) return parseInt(idFromUrl, 10);

  try {
    const raw = localStorage.getItem("ictu_student_session") || localStorage.getItem("currentUser") || localStorage.getItem("user");
    if (raw) {
      const u = JSON.parse(raw);
      if (u.ma_ho_so) return parseInt(u.ma_ho_so, 10);
    }
  } catch (e) {}

  return 1;
}

function updateFileView(file) {
  if (file) {
    if (tenTepVanBan) tenTepVanBan.textContent = file.name;
    const sizeInMb = (file.size / (1024 * 1024)).toFixed(2);
    if (dungLuongTep) dungLuongTep.textContent = `${sizeInMb} MB`;
    if (tenTepHienThi) {
      tenTepHienThi.classList.remove("bg-surface-container-low");
      tenTepHienThi.classList.add("bg-surface-container");
    }
  } else {
    if (tenTepVanBan) tenTepVanBan.textContent = "Chưa có tệp nào được chọn";
    if (dungLuongTep) dungLuongTep.textContent = "0 KB";
    if (tenTepHienThi) {
      tenTepHienThi.classList.remove("bg-surface-container");
      tenTepHienThi.classList.add("bg-surface-container-low");
    }
  }
}

if (tepInput) {
  tepInput.addEventListener("change", function (e) {
    if (e.target.files && e.target.files.length > 0) {
      updateFileView(e.target.files[0]);
    }
  });
}

if (vungKeoTha) {
  ["dragenter", "dragover"].forEach((eventName) => {
    vungKeoTha.addEventListener(
      eventName,
      (e) => {
        e.preventDefault();
        e.stopPropagation();
        vungKeoTha.classList.add("bg-surface-container-high");
      },
      false,
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    vungKeoTha.addEventListener(
      eventName,
      (e) => {
        e.preventDefault();
        e.stopPropagation();
        vungKeoTha.classList.remove("bg-surface-container-high");
      },
      false,
    );
  });

  vungKeoTha.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      tepInput.files = files;
      updateFileView(files[0]);
    }
  });
}

function datLaiForm() {
  const inputEl = document.getElementById("tepDinhKem");
  const ghiChuEl = document.getElementById("ghiChu");
  const loaiEl = document.getElementById("loaiTaiLieu");
  if (inputEl) inputEl.value = "";
  if (ghiChuEl) ghiChuEl.value = "";
  if (loaiEl) loaiEl.selectedIndex = 0;
  updateFileView(null);
}

function hienThiThongBaoLoi(tieuDe, noiDung) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) return;
  hopThongBao.className =
    "rounded-xl bg-red-50 text-red-900 border border-red-200 p-4 shadow-sm flex items-start gap-3.5 transition-all duration-300";
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
      <span class="material-symbols-outlined text-[20px]">error</span>
    </div>
    <div class="flex-1 font-body-sm text-body-sm">
      <div class="flex items-center justify-between">
        <span class="font-label-lg text-label-lg font-bold text-red-800">${tieuDe}</span>
        <span class="font-label-sm text-label-sm font-semibold text-red-600">LỖI XÁC THỰC</span>
      </div>
      <p class="mt-1 leading-relaxed text-red-700">
        ${noiDung}
      </p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="p-1 rounded-md text-red-600 hover:bg-red-100 transition-colors">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hopThongBao.classList.remove("hidden");
  hopThongBao.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function taiDanhSachTaiLieu() {
  const tbody = document.getElementById("bangDanhSachTaiLieu");
  if (!tbody) return;

  const maHoSo = layMaHoSoHienTai();
  try {
    const res = await fetch(`${duongDanApiDocuments}/${maHoSo}`);
    if (!res.ok) return;

    const json = await res.json();
    const docs = json.data || [];
    if (!docs.length) return;

    tbody.innerHTML = "";
    docs.forEach((doc) => {
      const fileName = doc.duong_dan_file ? doc.duong_dan_file.split("/").pop() : "TaiLieu.pdf";
      const fileUrl = `http://127.0.0.1:8000/${doc.duong_dan_file}`;

      let loaiLabel = doc.loai_tai_lieu || "Tài liệu";
      if (loaiLabel === "CV") loaiLabel = "CV / Hồ sơ năng lực";
      else if (loaiLabel === "DonXinThucTap") loaiLabel = "Đơn xin thực tập";
      else if (loaiLabel === "GiayGioiThieu") loaiLabel = "Giấy giới thiệu";
      else if (loaiLabel === "HopDong") loaiLabel = "Hợp đồng thực tập";

      let statusBadge = "";
      if (doc.trang_thai_duyet === "DaDuyet") {
        statusBadge = `
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 font-label-sm text-label-sm font-semibold border border-emerald-200">
            <span class="material-symbols-outlined text-[14px]">check_circle</span>
            <span>Đã duyệt</span>
          </span>
        `;
      } else if (doc.trang_thai_duyet === "TuChoi") {
        statusBadge = `
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-50 text-red-800 font-label-sm text-label-sm font-semibold border border-red-200">
            <span class="material-symbols-outlined text-[14px]">cancel</span>
            <span>Từ chối</span>
          </span>
        `;
      } else {
        statusBadge = `
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 font-label-sm text-label-sm font-semibold border border-amber-200">
            <span class="material-symbols-outlined text-[14px]">hourglass_top</span>
            <span>Chờ duyệt</span>
          </span>
        `;
      }

      const tr = document.createElement("tr");
      tr.className = "hover:bg-surface-container-low/50 transition-colors border-b border-surface-container-low/50";
      tr.innerHTML = `
        <td class="py-4 px-6 font-label-md text-label-md text-on-surface flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-error-container text-error flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-[20px]">picture_as_pdf</span>
          </div>
          <div>
            <span class="font-bold block truncate max-w-xs">${fileName}</span>
            <span class="font-body-sm text-body-sm text-on-surface-variant">Tài liệu đã số hóa</span>
          </div>
        </td>
        <td class="py-4 px-4 font-body-sm text-body-sm">
          <span class="px-2.5 py-1 rounded-md bg-surface-container text-primary font-medium">${loaiLabel}</span>
        </td>
        <td class="py-4 px-4 font-code text-code text-on-surface-variant">
          Đã lưu trữ
        </td>
        <td class="py-4 px-4 font-body-sm text-body-sm text-on-surface-variant">
          Gần đây
        </td>
        <td class="py-4 px-4">
          ${statusBadge}
        </td>
        <td class="py-4 px-6 text-right">
          <div class="inline-flex items-center gap-1">
            <a href="${fileUrl}" target="_blank" class="p-1.5 rounded-lg text-outline hover:text-primary hover:bg-surface-container transition-colors inline-block" title="Xem / Tải về">
              <span class="material-symbols-outlined text-[18px]">download</span>
            </a>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {}
}

async function xuLyTaiLen() {
  let loaiTaiLieu = document.getElementById("loaiTaiLieu")?.value || "CV";
  if (loaiTaiLieu.includes("CV")) loaiTaiLieu = "CV";
  else if (loaiTaiLieu.includes("Đơn xin") || loaiTaiLieu.includes("DonXin")) loaiTaiLieu = "DonXinThucTap";
  else if (loaiTaiLieu.includes("Giới thiệu") || loaiTaiLieu.includes("GiayGioiThieu")) loaiTaiLieu = "GiayGioiThieu";
  else if (loaiTaiLieu.includes("Hợp đồng") || loaiTaiLieu.includes("HopDong")) loaiTaiLieu = "HopDong";

  const nutGuiTep = document.getElementById("nutGuiTep");
  const file = tepInput?.files?.[0];

  if (!file) {
    hienThiThongBaoLoi("Chưa chọn tệp", "Vui lòng chọn hoặc kéo thả tệp tài liệu trước khi bấm tải lên.");
    return;
  }

  const fileNameLower = file.name.toLowerCase();
  const dangerousExtensions = [".exe", ".bat", ".sh", ".cmd", ".msi", ".vbs", ".js", ".zip", ".rar", ".7z", ".tar"];
  for (const ext of dangerousExtensions) {
    if (fileNameLower.endsWith(ext)) {
      hienThiThongBaoLoi(
        "Tệp không an toàn",
        `Định dạng tệp "${ext}" bị chặn vì lý do an ninh hệ thống. Vui lòng chỉ tải lên tệp văn bản (PDF, DOCX, PNG, JPG).`
      );
      return;
    }
  }

  const allowedExtensions = [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"];
  const isAllowed = allowedExtensions.some(ext => fileNameLower.endsWith(ext));
  if (!isAllowed) {
    hienThiThongBaoLoi(
      "Sai định dạng tệp",
      "Hệ thống chỉ chấp nhận các tệp hồ sơ định dạng PDF, DOCX, PNG hoặc JPG."
    );
    return;
  }

  const maxSizeBytes = 10 * 1024 * 1024;
  if (file.size > maxSizeBytes) {
    const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
    hienThiThongBaoLoi(
      "Tệp vượt quá kích thước cho phép",
      `Dung lượng tệp của bạn là ${sizeMb} MB, vượt quá giới hạn tối đa là 10 MB.`
    );
    return;
  }

  const originalHtml = nutGuiTep ? nutGuiTep.innerHTML : "";
  if (nutGuiTep) {
    nutGuiTep.innerHTML = `<span class="inline-block w-4 h-4 rounded-full border-2 border-on-primary border-t-transparent animate-spin"></span> <span>Đang tải lên máy chủ...</span>`;
    nutGuiTep.disabled = true;
  }

  const maHoSo = layMaHoSoHienTai();

  const duLieuForm = new FormData();
  duLieuForm.append("file", file);
  duLieuForm.append("ma_ho_so", maHoSo);
  duLieuForm.append("loai_tai_lieu", loaiTaiLieu);

  try {
    const phanHoi = await fetch(duongDanApiUpload, {
      method: "POST",
      body: duLieuForm,
    });

    const ketQua = await phanHoi.json().catch(() => ({}));

    if (!phanHoi.ok) {
      let errMsg = "Không thể tải lên tệp tài liệu.";
      if (typeof ketQua.detail === "string") {
        errMsg = ketQua.detail;
      } else if (Array.isArray(ketQua.detail)) {
        errMsg = ketQua.detail.map(e => e.msg || e.message).join(", ");
      }
      hienThiThongBaoLoi("Lỗi tải lên máy chủ", errMsg);
      return;
    }

    hienThiThongBaoUpload(file, loaiTaiLieu, ketQua.message);
    datLaiForm();
    await taiDanhSachTaiLieu();
  } catch (err) {
    hienThiThongBaoLoi(
      "Mất kết nối máy chủ",
      `Không thể kết nối tới dịch vụ tải tệp (${err.message || "Lỗi mạng"}). Vui lòng kiểm tra lại dịch vụ Backend.`
    );
  } finally {
    if (nutGuiTep) {
      nutGuiTep.innerHTML = originalHtml;
      nutGuiTep.disabled = false;
    }
  }
}

function hienThiThongBaoUpload(file, loaiTaiLieu, thongDiepTuyChinh) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) return;
  hopThongBao.className =
    "rounded-xl bg-secondary-container text-on-secondary-container p-4 shadow-sm flex items-start gap-3.5 transition-all duration-300";
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
      <span class="material-symbols-outlined text-[20px]">check_circle</span>
    </div>
    <div class="flex-1 font-body-sm text-body-sm">
      <div class="flex items-center justify-between">
        <span class="font-label-lg text-label-lg font-bold">Tải lên tài liệu thành công!</span>
        <span class="font-label-sm text-label-sm font-semibold">Vừa xong</span>
      </div>
      <p class="mt-1 leading-relaxed">
        ${thongDiepTuyChinh || `Tệp <strong>${file.name}</strong> (${(file.size / (1024 * 1024)).toFixed(2)} MB) thuộc phân loại <strong>"${loaiTaiLieu}"</strong> đã được tải lên và lưu trữ an toàn trên máy chủ.`}
      </p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="p-1 rounded-md hover:bg-secondary/10 transition-colors">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hopThongBao.classList.remove("hidden");
  hopThongBao.scrollIntoView({ behavior: "smooth", block: "center" });
}

document.addEventListener("DOMContentLoaded", () => {
  taiDanhSachTaiLieu();
});
