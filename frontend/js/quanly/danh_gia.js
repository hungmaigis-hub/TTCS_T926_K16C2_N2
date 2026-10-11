const duongDanApi = "http://127.0.0.1:8000/api/v1";

let danhSachSinhVienData = {
  1: {
    maHoSo: 1,
    hoTen: "Nguyễn Văn A",
    maSV: "DTC2051060124",
    lop: "K19 Kỹ thuật Phần mềm",
    viTri: "Fullstack Web",
    tienDo: 85,
    diemKM: 8.5,
    diemTD: 9.0,
    nhanXet: "Sinh viên nắm vững kiến thức thực tế, hoàn thành xuất sắc các module backend & frontend được giao, có tinh thần cầu tiến và hòa nhập nhanh với văn hóa doanh nghiệp. Luôn chủ động trao đổi khi gặp bài toán phức tạp và hoàn thành các task sprint đúng hạn cam kết."
  },
  2: {
    maHoSo: 2,
    hoTen: "Trần Thị B",
    maSV: "DTC2051060188",
    lop: "K19 Khoa học Máy tính",
    viTri: "AI & Data Engineer Intern",
    tienDo: 90,
    diemKM: 9.2,
    diemTD: 9.4,
    nhanXet: "Khả năng tự nghiên cứu các mô hình Deep Learning và Computer Vision vượt trội. Hoàn thành pipeline xử lý dữ liệu cho hệ thống phân tích hình ảnh trước thời hạn được giao."
  }
};

async function taiDanhSachSinhVienTuApi() {
  const selectEl = document.getElementById("thucTapSinh");
  if (!selectEl) return;

  try {
    const res = await fetch(`${duongDanApi}/interns?limit=50`);
    if (!res.ok) return;

    const json = await res.json();
    const items = json.data || [];
    if (!items.length) return;

    const newData = {};
    selectEl.innerHTML = "";

    items.forEach((it, idx) => {
      const maHs = it.ma_ho_so || (idx + 1);
      const email = it.email || "";
      const maSV = it.ma_sinh_vien || (email.includes("@") ? email.split("@")[0].toUpperCase() : `DTC2051060${String(100 + maHs).slice(-3)}`);
      const hoTen = it.ho_ten || `Sinh viên #${maHs}`;
      const chuyenNganh = it.chuyen_nganh || "Công nghệ Thông tin";
      const lop = `K19 ${chuyenNganh}`;

      newData[maHs] = {
        maHoSo: maHs,
        hoTen: hoTen,
        maSV: maSV,
        lop: lop,
        viTri: it.ten_chuong_trinh || "Thực tập sinh Phần mềm",
        tienDo: 85,
        diemKM: 8.5,
        diemTD: 9.0,
        nhanXet: `Sinh viên ${hoTen} thể hiện tinh thần trách nhiệm cao, hoàn thành đầy đủ các nhiệm vụ và báo cáo tuần đúng hạn cam kết.`
      };

      const opt = document.createElement("option");
      opt.value = maHs;
      opt.textContent = `${hoTen} - ${maSV} (${chuyenNganh})`;
      selectEl.appendChild(opt);
    });

    danhSachSinhVienData = newData;
    capNhatSinhVien();
  } catch (err) {}
}

function capNhatSinhVien() {
  const selectEl = document.getElementById("thucTapSinh");
  if (!selectEl) return;
  const maHs = selectEl.value;
  const data = danhSachSinhVienData[maHs];
  if (!data) return;

  const theHoTen = document.getElementById("theHoTen");
  const theMaSV = document.getElementById("theMaSV");
  const theLop = document.getElementById("theLop");
  const theViTri = document.getElementById("theViTri");
  const phanTramTienDo = document.getElementById("phanTramTienDo");
  const thanhTienDo = document.getElementById("thanhTienDo");
  const diemKyNang = document.getElementById("diemKyNang");
  const diemThaiDo = document.getElementById("diemThaiDo");
  const nhanXet = document.getElementById("nhanXet");

  if (theHoTen) theHoTen.textContent = data.hoTen;
  if (theMaSV) theMaSV.textContent = data.maSV;
  if (theLop) theLop.textContent = data.lop;
  if (theViTri) theViTri.textContent = data.viTri;
  if (phanTramTienDo) phanTramTienDo.textContent = `${data.tienDo}%`;
  if (thanhTienDo) thanhTienDo.style.width = `${data.tienDo}%`;
  if (diemKyNang) diemKyNang.value = data.diemKM;
  if (diemThaiDo) diemThaiDo.value = data.diemTD;
  if (nhanXet) nhanXet.value = data.nhanXet;

  tinhDiemTrungBinh();
}

function tinhDiemTrungBinh() {
  const kmEl = document.getElementById("diemKyNang");
  const tdEl = document.getElementById("diemThaiDo");
  const diemKM = kmEl ? parseFloat(kmEl.value) || 0 : 0;
  const diemTD = tdEl ? parseFloat(tdEl.value) || 0 : 0;
  const safeKM = Math.min(Math.max(diemKM, 0), 10);
  const safeTD = Math.min(Math.max(diemTD, 0), 10);
  const dtb = (safeKM * 0.6 + safeTD * 0.4).toFixed(1);

  const dtbEl = document.getElementById("hienThiDiemTrungBinh");
  if (dtbEl) dtbEl.textContent = dtb;

  const khungXepLoai = document.getElementById("hienThiXepLoai");
  if (!khungXepLoai) return;

  if (dtb >= 8.5) {
    khungXepLoai.textContent = "Xếp loại: Xuất sắc";
    khungXepLoai.className = "inline-block px-3 py-1 rounded-full text-xs font-bold bg-emerald-600 text-white shadow-sm";
  } else if (dtb >= 7.0) {
    khungXepLoai.textContent = "Xếp loại: Khá";
    khungXepLoai.className = "inline-block px-3 py-1 rounded-full text-xs font-bold bg-ictu-600 text-white shadow-sm";
  } else if (dtb >= 5.5) {
    khungXepLoai.textContent = "Xếp loại: Trung bình";
    khungXepLoai.className = "inline-block px-3 py-1 rounded-full text-xs font-bold bg-slate-600 text-white shadow-sm";
  } else {
    khungXepLoai.textContent = "Xếp loại: Chưa đạt";
    khungXepLoai.className = "inline-block px-3 py-1 rounded-full text-xs font-bold bg-rose-600 text-white shadow-sm";
  }
}

function resetFormDanhGia() {
  capNhatSinhVien();
}

async function xuLyLuuDanhGia() {
  const nutLuu = document.getElementById("nutLuuDanhGia");
  const hopThongBao = document.getElementById("hopThongBao");
  const hoTen = document.getElementById("theHoTen")?.textContent || "Sinh viên";
  const maSV = document.getElementById("theMaSV")?.textContent || "";
  const dtb = document.getElementById("hienThiDiemTrungBinh")?.textContent || "0.0";
  const xepLoai = document.getElementById("hienThiXepLoai")?.textContent || "";
  const selectEl = document.getElementById("thucTapSinh");
  const maHoSo = selectEl ? parseInt(selectEl.value, 10) || 1 : 1;

  const kmEl = document.getElementById("diemKyNang");
  const tdEl = document.getElementById("diemThaiDo");
  const nxEl = document.getElementById("nhanXet");
  const dxEl = document.getElementById("deXuatTuyenDung");

  const diemKM = kmEl ? parseFloat(kmEl.value) : NaN;
  const diemTD = tdEl ? parseFloat(tdEl.value) : NaN;
  const nhanXetVal = nxEl ? nxEl.value.trim() : "";
  const deXuatVal = dxEl ? dxEl.checked : false;

  if (isNaN(diemKM) || diemKM < 0 || diemKM > 10) {
    if (hopThongBao) {
      hopThongBao.className =
        "w-full bg-rose-50 border border-rose-200 rounded-xl p-4 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
              <span class="material-symbols-outlined text-[20px]">error</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-rose-900">Điểm kỹ năng không hợp lệ</span>
                <span class="text-[11px] font-semibold bg-rose-100 text-rose-800 px-2 py-0.5 rounded">Thang điểm 0 - 10</span>
              </div>
              <p class="text-xs text-rose-800 mt-1 leading-relaxed">
                Điểm đánh giá kỹ năng chuyên môn phải là số hợp lệ từ 0.0 đến 10.0. Vui lòng kiểm tra lại.
              </p>
            </div>
          </div>
          <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-rose-600 hover:text-rose-800 p-1 rounded-lg">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    kmEl?.focus();
    return;
  }

  if (isNaN(diemTD) || diemTD < 0 || diemTD > 10) {
    if (hopThongBao) {
      hopThongBao.className =
        "w-full bg-rose-50 border border-rose-200 rounded-xl p-4 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
              <span class="material-symbols-outlined text-[20px]">error</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-rose-900">Điểm thái độ không hợp lệ</span>
                <span class="text-[11px] font-semibold bg-rose-100 text-rose-800 px-2 py-0.5 rounded">Thang điểm 0 - 10</span>
              </div>
              <p class="text-xs text-rose-800 mt-1 leading-relaxed">
                Điểm đánh giá thái độ làm việc phải là số hợp lệ từ 0.0 đến 10.0. Vui lòng kiểm tra lại.
              </p>
            </div>
          </div>
          <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-rose-600 hover:text-rose-800 p-1 rounded-lg">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    tdEl?.focus();
    return;
  }

  if (!nhanXetVal || nhanXetVal.length < 5) {
    if (hopThongBao) {
      hopThongBao.className =
        "w-full bg-amber-50 border border-amber-200 rounded-xl p-4 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-lg bg-amber-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
              <span class="material-symbols-outlined text-[20px]">warning</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-amber-900">Thiếu nhận xét đánh giá</span>
              </div>
              <p class="text-xs text-amber-800 mt-1 leading-relaxed">
                Vui lòng nhập nhận xét chi tiết về quá trình thực tập của sinh viên (tối thiểu 5 ký tự).
              </p>
            </div>
          </div>
          <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-amber-600 hover:text-amber-800 p-1 rounded-lg">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    nxEl?.focus();
    return;
  }

  let mentorId = 3;
  try {
    const rawUser = localStorage.getItem("ictu_admin_session") || localStorage.getItem("currentUser");
    if (rawUser) {
      const u = JSON.parse(rawUser);
      if (u.ma_nguoi_dung) mentorId = parseInt(u.ma_nguoi_dung, 10);
    }
  } catch (e) {}

  const originalHTML = nutLuu.innerHTML;
  nutLuu.innerHTML = `
    <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
    <span>Đang đồng bộ máy chủ...</span>
  `;
  nutLuu.disabled = true;

  try {
    const payload = {
      ma_ho_so: maHoSo,
      ma_nguoi_danh_gia: mentorId,
      loai_danh_gia: "CuoiKy",
      diem_ky_nang: diemKM,
      diem_thai_do: diemTD,
      nhan_xet: nhanXetVal,
      nhan_xet_chi_tiet: nhanXetVal,
      de_xuat_tuyen_dung: deXuatVal,
      de_xuat_tuyen_chinh_thuc: deXuatVal
    };

    const res = await fetch(`${duongDanApi}/evaluations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const resJson = await res.json().catch(() => ({}));

    if (res.ok) {
      hopThongBao.className =
        "w-full bg-emerald-50 border border-emerald-200 rounded-xl p-4 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
              <span class="material-symbols-outlined text-[20px]">check_circle</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-emerald-900">Lưu kết quả đánh giá thành công!</span>
                <span class="text-[11px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">Đã lưu CSDL</span>
              </div>
              <p class="text-xs text-emerald-800 mt-1 leading-relaxed">
                Đã ghi nhận kết quả đánh giá cho sinh viên <strong>${hoTen}</strong> (${maSV}) với điểm tổng kết <strong>${dtb} / 10.0</strong> (${xepLoai}). Hồ sơ đã được đồng bộ lên máy chủ và cổng thông tin khoa.
              </p>
            </div>
          </div>
          <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-emerald-600 hover:text-emerald-800 p-1 rounded-lg">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      let msg = "Không thể lưu đánh giá vào cơ sở dữ liệu.";
      if (typeof resJson.detail === "string") {
        msg = resJson.detail;
      } else if (Array.isArray(resJson.detail) && resJson.detail[0]?.msg) {
        msg = resJson.detail[0].msg;
      }
      if (typeof msg === "string" && msg.includes("đã có đánh giá")) {
        msg = `Hồ sơ của sinh viên <strong>${hoTen}</strong> đã được đánh giá kỳ này trong cơ sở dữ liệu.`;
      }
      hopThongBao.className =
        "w-full bg-amber-50 border border-amber-200 rounded-xl p-4 shadow-sm transition-all duration-300";
      hopThongBao.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-lg bg-amber-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
              <span class="material-symbols-outlined text-[20px]">warning</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-amber-900">Thông báo từ máy chủ</span>
              </div>
              <p class="text-xs text-amber-800 mt-1 leading-relaxed">${msg}</p>
            </div>
          </div>
          <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-amber-600 hover:text-amber-800 p-1 rounded-lg">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
      `;
      hopThongBao.classList.remove("hidden");
      hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  } catch (err) {
    hopThongBao.className =
      "w-full bg-rose-50 border border-rose-200 rounded-xl p-4 shadow-sm transition-all duration-300";
    hopThongBao.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
            <span class="material-symbols-outlined text-[20px]">error</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-rose-900">Mất kết nối máy chủ</span>
            </div>
            <p class="text-xs text-rose-800 mt-1 leading-relaxed">
              Không thể kết nối đến máy chủ để lưu đánh giá cho sinh viên <strong>${hoTen}</strong>. Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau.
            </p>
          </div>
        </div>
        <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-rose-600 hover:text-rose-800 p-1 rounded-lg">
          <span class="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>
    `;
    hopThongBao.classList.remove("hidden");
    hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } finally {
    nutLuu.innerHTML = originalHTML;
    nutLuu.disabled = false;
  }
}

function xuatBaoCaoDanhGia(dinhDang) {
  const url = `${duongDanApi}/evaluations/summary?format=${dinhDang}`;
  window.open(url, "_blank");
}

function capNhatHocKyDanhGia() {
  const now = new Date();
  const curY = now.getFullYear();
  const startY = now.getMonth() >= 8 ? curY : curY - 1;
  const nienKhoa = `${startY} - ${startY + 1}`;
  const hocKy = now.getMonth() >= 8 || now.getMonth() <= 1 ? "Học kỳ I" : "Học kỳ II";
  const elHocKy = document.getElementById("theHocKyDanhGia");
  if (elHocKy) elHocKy.textContent = `${hocKy} (${nienKhoa})`;
  const elMoTa = document.getElementById("moTaDotDanhGia");
  if (elMoTa) elMoTa.textContent = `Dữ liệu đánh giá trực tiếp ${hocKy.toLowerCase()} năm học ${nienKhoa}`;
}

document.addEventListener("DOMContentLoaded", () => {
  capNhatHocKyDanhGia();
  tinhDiemTrungBinh();
  taiDanhSachSinhVienTuApi();
});
