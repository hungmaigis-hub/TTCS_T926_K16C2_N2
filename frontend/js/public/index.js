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
    nhanNhapLieu.textContent = "Email Mentor / Người hướng dẫn *";
    oNhapLieu.placeholder = "mentor.career@ictu.edu.vn";
  } else if (vaiTro === "hr" || vaiTro === "admin" || vaiTro === "faculty") {
    nhanNhapLieu.textContent = "Email Cán bộ HR / Quản lý *";
    oNhapLieu.placeholder = "admin.daotao@ictu.edu.vn";
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
  window.location.href = "dangnhap.html";
}
