const danhSachSinhVienData = {
  DTC2051060124: {
    hoTen: "Nguyễn Văn An",
    maSV: "DTC2051060124",
    lop: "K19 Kỹ thuật Phần mềm",
    viTri: "Fullstack Web",
    tienDo: 85,
    diemKM: 8.5,
    diemTD: 9.0,
    nhanXet:
      "Sinh viên nắm vững kiến thức thực tế, hoàn thành xuất sắc các module backend & frontend được giao, có tinh thần cầu tiến và hòa nhập nhanh với văn hóa doanh nghiệp. Luôn chủ động trao đổi khi gặp bài toán phức tạp và hoàn thành các task sprint đúng hạn cam kết.",
  },
  DTC2051060188: {
    hoTen: "Trần Thị Mai Anh",
    maSV: "DTC2051060188",
    lop: "K19 Khoa học Máy tính",
    viTri: "AI & Data Engineer Intern",
    tienDo: 90,
    diemKM: 9.2,
    diemTD: 9.4,
    nhanXet:
      "Khả năng tự nghiên cứu các mô hình Deep Learning và Computer Vision vượt trội. Hoàn thành pipeline xử lý dữ liệu cho hệ thống phân tích hình ảnh trước thời hạn được giao.",
  },
  DTC2051060045: {
    hoTen: "Hoàng Minh Đức",
    maSV: "DTC2051060045",
    lop: "K19 Mạng máy tính & ATTT",
    viTri: "Chuyên viên An toàn thông tin",
    tienDo: 78,
    diemKM: 8.0,
    diemTD: 8.5,
    nhanXet:
      "Nắm vững quy chuẩn bảo mật OWASP Top 10 và các giao thức mạng. Có tinh thần trách nhiệm cao trong việc giám sát nhật ký bảo mật hệ thống.",
  },
  DTC2051060312: {
    hoTen: "Lê Thu Trang",
    maSV: "DTC2051060312",
    lop: "K19 Hệ thống Thông tin",
    viTri: "Business Analyst Intern (BA)",
    tienDo: 82,
    diemKM: 8.4,
    diemTD: 8.8,
    nhanXet:
      "Kỹ năng phân tích yêu cầu nghiệp vụ khách hàng chuẩn xác, viết tài liệu SRS rõ ràng, giao tiếp giữa đội ngũ kỹ thuật và khách hàng mạch lạc.",
  },
};
function capNhatSinhVien() {
  const maSV = document.getElementById("thucTapSinh").value;
  const data = danhSachSinhVienData[maSV];
  if (!data) return;
  document.getElementById("theHoTen").textContent = data.hoTen;
  document.getElementById("theMaSV").textContent = data.maSV;
  document.getElementById("theLop").textContent = data.lop;
  document.getElementById("theViTri").textContent = data.viTri;
  document.getElementById("phanTramTienDo").textContent = data.tienDo + "%";
  document.getElementById("thanhTienDo").style.width = data.tienDo + "%";
  document.getElementById("diemKyNang").value = data.diemKM;
  document.getElementById("diemThaiDo").value = data.diemTD;
  document.getElementById("nhanXet").value = data.nhanXet;
  tinhDiemTrungBinh();
}
function tinhDiemTrungBinh() {
  const diemKM = parseFloat(document.getElementById("diemKyNang").value) || 0;
  const diemTD = parseFloat(document.getElementById("diemThaiDo").value) || 0;
  const safeKM = Math.min(Math.max(diemKM, 0), 10);
  const safeTD = Math.min(Math.max(diemTD, 0), 10);
  const dtb = (safeKM * 0.6 + safeTD * 0.4).toFixed(1);
  document.getElementById("hienThiDiemTrungBinh").textContent = dtb;
  const khungXepLoai = document.getElementById("hienThiXepLoai");
  if (dtb >= 8.5) {
    khungXepLoai.textContent = "Xếp loại: Xuất sắc";
    khungXepLoai.className =
      "inline-block px-3 py-1 rounded-full text-xs font-bold bg-emerald-600 text-white shadow-sm";
  } else if (dtb >= 7.0) {
    khungXepLoai.textContent = "Xếp loại: Khá";
    khungXepLoai.className =
      "inline-block px-3 py-1 rounded-full text-xs font-bold bg-ictu-600 text-white shadow-sm";
  } else if (dtb >= 5.5) {
    khungXepLoai.textContent = "Xếp loại: Trung bình";
    khungXepLoai.className =
      "inline-block px-3 py-1 rounded-full text-xs font-bold bg-slate-600 text-white shadow-sm";
  } else {
    khungXepLoai.textContent = "Xếp loại: Chưa đạt";
    khungXepLoai.className =
      "inline-block px-3 py-1 rounded-full text-xs font-bold bg-rose-600 text-white shadow-sm";
  }
}
function resetFormDanhGia() {
  capNhatSinhVien();
}
function xuLyLuuDanhGia() {
  const nutLuu = document.getElementById("nutLuuDanhGia");
  const hopThongBao = document.getElementById("hopThongBao");
  const hoTen = document.getElementById("theHoTen").textContent;
  const maSV = document.getElementById("theMaSV").textContent;
  const dtb = document.getElementById("hienThiDiemTrungBinh").textContent;
  const xepLoai = document.getElementById("hienThiXepLoai").textContent;
  const originalHTML = nutLuu.innerHTML;
  nutLuu.innerHTML = `
        <span class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <span>Đang gửi điểm...</span>
      `;
  nutLuu.disabled = true;
  setTimeout(() => {
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
                  <span class="text-[11px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">Vừa xong</span>
                </div>
                <p class="text-xs text-emerald-800 mt-1 leading-relaxed">
                  Đã ghi nhận kết quả đánh giá cho sinh viên <strong>${hoTen}</strong> (${maSV}) với điểm tổng kết <strong>${dtb} / 10.0</strong> (${xepLoai}). Hồ sơ đã được đồng bộ lên cổng thông tin khoa.
                </p>
              </div>
            </div>
            <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="text-emerald-600 hover:text-emerald-800 p-1 rounded-lg">
              <span class="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>
        `;
    hopThongBao.classList.remove("hidden");
    nutLuu.innerHTML = originalHTML;
    nutLuu.disabled = false;
    hopThongBao.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, 500);
}
document.addEventListener("DOMContentLoaded", () => {
  tinhDiemTrungBinh();
});
