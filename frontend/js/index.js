function selectRole(vaiTro, nutChon) {
  const danhSachNut = document.querySelectorAll(".role-btn");
  danhSachNut.forEach((nut) => {
    nut.classList.remove("active");
  });

  nutChon.classList.add("active");

  const nhanNhapLieu = document.getElementById("identifierLabel");
  const oNhapLieu = document.getElementById("identifier");

  if (vaiTro === "student") {
    nhanNhapLieu.textContent = "Email hoặc Mã sinh viên *";
    oNhapLieu.placeholder = "sv.nguyenvana@ictu.edu.vn";
  } else if (vaiTro === "mentor") {
    nhanNhapLieu.textContent = "Email Doanh nghiệp / Mã Mentor *";
    oNhapLieu.placeholder = "mentor.career@ictu.edu.vn";
  } else if (vaiTro === "faculty") {
    nhanNhapLieu.textContent = "Email Giảng viên / Quản lý khoa *";
    oNhapLieu.placeholder = "gv.truongkhoa@ictu.edu.vn";
  }
}

function togglePasswordVisibility() {
  const oMatKhau = document.getElementById("password");
  const nutMat = document.getElementById("eyeIcon");
  if (oMatKhau.type === "password") {
    oMatKhau.type = "text";
    nutMat.textContent = "Ẩn";
  } else {
    oMatKhau.type = "password";
    nutMat.textContent = "Hiện";
  }
}

function submitLogin() {
  const nutDangNhap = document.querySelector(".btn-login");
  nutDangNhap.textContent = "Đang xác thực bảo mật...";
  nutDangNhap.disabled = true;

  setTimeout(() => {
    window.location.href = "../quanly/dashboard.html";
  }, 900);
}
