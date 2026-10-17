/* ============================================================
   QUẢN LÝ SAO LƯU - JavaScript (Fetch API)
   Endpoints:
   - POST /api/v1/system/backup (Kích hoạt sao lưu thủ công)
   - GET  /api/v1/system/backups (Lấy danh sách file backup & tải file)
   ============================================================ */

const duongDanApi = typeof layDuongDanApi === "function" ? layDuongDanApi() : "http://127.0.0.1:8000/api/v1";

let danhSachBackups = [];

// ==========================================
// 1. KHỞI TẠO TRANG
// ==========================================
document.addEventListener("DOMContentLoaded", function () {
  capNhatNgayHeader();
  taiDanhSachBackup();
});

/** Cập nhật ngày hiện tại trên header */
function capNhatNgayHeader() {
  const now = new Date();
  const opts = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
  const el = document.getElementById("ngayHienTaiHeader");
  if (el) el.textContent = now.toLocaleDateString("vi-VN", opts);
}

// ==========================================
// 2. TẢI DANH SÁCH FILE BACKUP (GET /api/v1/system/backups)
// ==========================================
async function taiDanhSachBackup() {
  try {
    const res = await fetch(`${duongDanApi}/system/backups`, {
      method: "GET",
      headers: {
        'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || localStorage.getItem('token') || '')
      }
    });

    if (!res.ok) {
      throw new Error("Không thể tải danh sách bản sao lưu");
    }

    const json = await res.json();
    // Hỗ trợ cả cấu trúc trả về trực tiếp dạng mảng hoặc { data: [...] }
    if (Array.isArray(json)) {
      danhSachBackups = json;
    } else if (json.data && Array.isArray(json.data)) {
      danhSachBackups = json.data;
    } else {
      danhSachBackups = [];
    }

    hienThiBangBackup(danhSachBackups);
  } catch (err) {
    console.error("Lỗi tải danh sách backup:", err);
    hienThiBangBackupTrong();
    hienThiToast("Không thể tải danh sách bản sao lưu từ máy chủ!", "error");
  }
}

function hienThiBangBackup(danhSach) {
  const tbody = document.getElementById("bangDanhSachBackup");
  if (!tbody) return;

  if (!danhSach || danhSach.length === 0) {
    hienThiBangBackupTrong();
    return;
  }

  tbody.innerHTML = danhSach.map((file, idx) => {
    const tenFile = file.filename || file.name || "backup.sql.gz";
    const dungLuong = dinhDangDungLuong(file.size || file.dung_luong || 0);
    const ngayTao = dinhDangThoiGian(file.created_at || file.date || file.ngay_tao);
    const urlTaiVe = `${duongDanApi}/system/backups/${encodeURIComponent(tenFile)}`;

    return `
      <tr class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
        <td class="py-3 px-3 text-xs text-slate-400 font-mono">${idx + 1}</td>
        <td class="py-3 px-3">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-ictu-600 text-lg">archive</span>
            <span class="text-xs font-bold font-mono text-slate-800">${tenFile}</span>
          </div>
        </td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono">${dungLuong}</td>
        <td class="py-3 px-3 text-xs text-slate-600 font-mono">${ngayTao}</td>
        <td class="py-3 px-3 text-right">
          <a
            href="${urlTaiVe}"
            download
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-ictu-50 hover:bg-ictu-100 text-ictu-700 text-xs font-semibold transition-colors border border-ictu-200 cursor-pointer"
          >
            <span class="material-symbols-outlined text-sm">download</span>
            <span>Tải về</span>
          </a>
        </td>
      </tr>
    `;
  }).join("");
}

function hienThiBangBackupTrong() {
  const tbody = document.getElementById("bangDanhSachBackup");
  if (!tbody) return;
  tbody.innerHTML = `
    <tr>
      <td colspan="5" class="py-10 text-center text-xs text-slate-400">
        <span class="material-symbols-outlined text-4xl text-slate-300 block mb-2">folder_off</span>
        Chưa có bản sao lưu nào được tạo. Hãy nhấn "Tạo bản sao lưu ngay"!
      </td>
    </tr>
  `;
}

// ==========================================
// 3. TẠO BẢN SAO LƯU NGAY (POST /api/v1/system/backup)
// ==========================================
async function taoBanSaoLuuNgay() {
  const nutTao = document.getElementById("nutTaoSaoLuu");
  if (nutTao) {
    nutTao.disabled = true;
    nutTao.innerHTML = `
      <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
      <span>Đang tạo sao lưu...</span>
    `;
  }

  try {
    const res = await fetch(`${duongDanApi}/system/backup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || localStorage.getItem('token') || '')
      }
    });

    const json = await res.json().catch(() => ({}));

    if (res.ok) {
      hienThiToast("Tạo bản sao lưu thành công!", "success");
      // Tải lại danh sách sau khi tạo thành công
      taiDanhSachBackup();
    } else {
      const msg = json.detail || json.message || "Không thể tạo bản sao lưu";
      hienThiToast(`Lỗi: ${msg}`, "error");
    }
  } catch (err) {
    console.error("Lỗi tạo bản sao lưu:", err);
    hienThiToast("Không thể kết nối đến máy chủ. Vui lòng thử lại!", "error");
  } finally {
    if (nutTao) {
      nutTao.disabled = false;
      nutTao.innerHTML = `
        <span class="material-symbols-outlined text-lg">cloud_upload</span>
        <span>Tạo bản sao lưu ngay</span>
      `;
    }
  }
}

// ==========================================
// 4. TIỆN ÍCH (Hàm hỗ trợ định dạng)
// ==========================================

/** Định dạng dung lượng tệp từ Bytes sang KB, MB, GB */
function dinhDangDungLuong(bytes) {
  if (!bytes || bytes === 0) return "0 KB";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

/** Định dạng thời gian ISO sang dạng ngày giờ Việt Nam */
function dinhDangThoiGian(isoStr) {
  if (!isoStr) return "--";
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return isoStr;
    const ngay = String(d.getDate()).padStart(2, "0");
    const thang = String(d.getMonth() + 1).padStart(2, "0");
    const nam = d.getFullYear();
    const gio = String(d.getHours()).padStart(2, "0");
    const phut = String(d.getMinutes()).padStart(2, "0");
    const giay = String(d.getSeconds()).padStart(2, "0");
    return `${ngay}/${thang}/${nam} ${gio}:${phut}:${giay}`;
  } catch {
    return isoStr;
  }
}

/** Hiển thị Toast thông báo trạng thái */
function hienThiToast(noiDung, loai) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const colors = {
    success: "bg-emerald-600 text-white",
    error: "bg-rose-600 text-white",
    warning: "bg-amber-500 text-white",
    info: "bg-ictu-600 text-white"
  };
  const icons = {
    success: "check_circle",
    error: "error",
    warning: "warning",
    info: "info"
  };

  const toast = document.createElement("div");
  toast.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-lg ${colors[loai] || colors.info} transform translate-x-full opacity-0 transition-all duration-300`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-xl">${icons[loai] || icons.info}</span>
    <span class="text-sm font-semibold">${noiDung}</span>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove("translate-x-full", "opacity-0");
    toast.classList.add("translate-x-0", "opacity-100");
  });

  setTimeout(() => {
    toast.classList.add("translate-x-full", "opacity-0");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}