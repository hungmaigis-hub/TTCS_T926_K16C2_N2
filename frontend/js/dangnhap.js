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

function submitLogin() {
  const submitBtn = document.querySelector('button[type="submit"]');
  if (!submitBtn) return;
  const originalContent = submitBtn.innerHTML;
  submitBtn.innerHTML = `
    <span class="inline-block w-4 h-4 rounded-full border-2 border-on-primary border-t-transparent animate-spin"></span>
    <span>Đang xác thực bảo mật...</span>
  `;
  submitBtn.disabled = true;

  setTimeout(() => {
    submitBtn.innerHTML = originalContent;
    submitBtn.disabled = false;
    if (vaiTroHienTai === "student") {
      window.location.href = "../sinhvien/dashboard.html";
    } else {
      window.location.href = "../quanly/dashboard.html";
    }
  }, 900);
}
