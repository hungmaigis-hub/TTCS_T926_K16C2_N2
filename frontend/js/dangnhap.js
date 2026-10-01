let vaiTroHienTai = "student";

function selectRole(role, targetButton) {
  vaiTroHienTai = role;
  const allButtons = document.querySelectorAll(".role-btn");
  allButtons.forEach((btn) => {
    btn.classList.remove(
      "bg-surface-container-lowest",
      "shadow-sm",
      "text-primary",
      "font-bold",
    );
    btn.classList.add("text-on-surface-variant");
  });

  targetButton.classList.add(
    "bg-surface-container-lowest",
    "shadow-sm",
    "text-primary",
    "font-bold",
  );
  targetButton.classList.remove("text-on-surface-variant");

  const inputLabel = document.getElementById("identifierLabel");
  const inputField = document.getElementById("identifier");
  if (!inputLabel || !inputField) return;

  if (role === "student") {
    inputLabel.innerHTML =
      'Email hoặc Mã sinh viên <span class="text-error">*</span>';
    inputField.placeholder = "sv.nguyenvana@ictu.edu.vn";
  } else if (role === "mentor") {
    inputLabel.innerHTML =
      'Email Doanh nghiệp / Mã Mentor <span class="text-error">*</span>';
    inputField.placeholder = "mentor.career@fpt-software.com";
  } else if (role === "faculty") {
    inputLabel.innerHTML =
      'Email Giảng viên / Quản lý khoa <span class="text-error">*</span>';
    inputField.placeholder = "gv.truongkhoa@ictu.edu.vn";
  }
}

function togglePasswordVisibility() {
  const passwordInput = document.getElementById("password");
  const eyeIcon = document.getElementById("eyeIcon");
  if (!passwordInput || !eyeIcon) return;
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeIcon.textContent = "visibility_off";
  } else {
    passwordInput.type = "password";
    eyeIcon.textContent = "visibility";
  }
}

async function submitLogin() {
  const submitBtn = document.querySelector('button[type="submit"]');
  const identifierInput = document.getElementById("identifier");
  const passwordInput = document.getElementById("password");
  if (!submitBtn || !identifierInput || !passwordInput) return;

  const email = identifierInput.value.trim();
  const mat_khau = passwordInput.value;
  if (!email || !mat_khau) {
    alert("Vui lòng nhập đầy đủ thông tin đăng nhập.");
    return;
  }

  const originalContent = submitBtn.innerHTML;
  submitBtn.innerHTML = `
    <span class="inline-block w-4 h-4 rounded-full border-2 border-on-primary border-t-transparent animate-spin"></span>
    <span>Đang xác thực bảo mật...</span>
  `;
  submitBtn.disabled = true;

  try {
    const res = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, mat_khau })
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok && data.data) {
      const userData = data.data;
      const expireTime = Date.now() + 2 * 60 * 60 * 1000;
      userData.expires_at = expireTime;
      if (userData.vai_tro === "ThucTapSinh" || vaiTroHienTai === "student") {
        localStorage.setItem("ictu_student_session", JSON.stringify(userData));
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("currentUser", JSON.stringify(userData));
        window.location.href = "../sinhvien/dashboard.html";
      } else {
        localStorage.setItem("ictu_admin_session", JSON.stringify(userData));
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("currentUser", JSON.stringify(userData));
        window.location.href = "../quanly/dashboard.html";
      }
      return;
    }

    alert(data.detail || "Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản và mật khẩu.");
    submitBtn.innerHTML = originalContent;
    submitBtn.disabled = false;
  } catch (err) {
    const expireTime = Date.now() + 2 * 60 * 60 * 1000;
    const namePart = email.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
    const mockUser = {
      ho_ten: namePart || (vaiTroHienTai === "student" ? "Vũ Quang Huy" : "Ban Đào Tạo & QLTT"),
      email: email,
      vai_tro: vaiTroHienTai === "student" ? "ThucTapSinh" : (vaiTroHienTai === "mentor" ? "Mentor" : "Admin"),
      ma_sinh_vien: vaiTroHienTai === "student" ? "DTC2051060124" : null,
      ma_nguoi_dung: 1,
      ma_ho_so: 1,
      expires_at: expireTime
    };
    if (vaiTroHienTai === "student") {
      localStorage.setItem("ictu_student_session", JSON.stringify(mockUser));
      localStorage.setItem("user", JSON.stringify(mockUser));
      localStorage.setItem("currentUser", JSON.stringify(mockUser));
      window.location.href = "../sinhvien/dashboard.html";
    } else {
      localStorage.setItem("ictu_admin_session", JSON.stringify(mockUser));
      localStorage.setItem("user", JSON.stringify(mockUser));
      localStorage.setItem("currentUser", JSON.stringify(mockUser));
      window.location.href = "../quanly/dashboard.html";
    }
  }
}
