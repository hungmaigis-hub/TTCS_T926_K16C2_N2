let vaiTroHienTai = "student";

function showToast(message, type = "error", title = "") {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className =
      "fixed right-5 sm:right-8 flex flex-col gap-3 max-w-sm sm:max-w-md w-full px-4 sm:px-0 pointer-events-none";
    container.style.cssText = "top: 84px; z-index: 999999;";
    document.body.appendChild(container);
  }

  const alertBox = document.getElementById("loginAlertBox");

  const config = {
    error: {
      bg: "bg-red-50 text-red-950 border-red-200",
      iconBg: "bg-red-500 text-white",
      icon: "error",
      defaultTitle: "Đăng nhập không thành công",
      boxBg: "bg-red-50/90 text-red-900 border-red-200"
    },
    warning: {
      bg: "bg-amber-50 text-amber-950 border-amber-200",
      iconBg: "bg-amber-500 text-white",
      icon: "warning",
      defaultTitle: "Cảnh báo",
      boxBg: "bg-amber-50/90 text-amber-900 border-amber-200"
    },
    success: {
      bg: "bg-emerald-50 text-emerald-950 border-emerald-200",
      iconBg: "bg-emerald-500 text-white",
      icon: "check_circle",
      defaultTitle: "Thành công",
      boxBg: "bg-emerald-50/90 text-emerald-900 border-emerald-200"
    },
    info: {
      bg: "bg-blue-50 text-blue-950 border-blue-200",
      iconBg: "bg-blue-500 text-white",
      icon: "info",
      defaultTitle: "Thông báo",
      boxBg: "bg-blue-50/90 text-blue-900 border-blue-200"
    }
  };

  const style = config[type] || config.error;
  const toastTitle = title || style.defaultTitle;

  if (alertBox) {
    alertBox.className = `mb-4 p-3.5 rounded-xl text-sm border flex items-start gap-3 transition-all duration-300 ${style.boxBg}`;
    alertBox.innerHTML = `
      <span class="material-symbols-outlined text-[20px] shrink-0 mt-0.5">${style.icon}</span>
      <div class="flex-1">
        <div class="font-bold text-xs uppercase tracking-wide opacity-80">${toastTitle}</div>
        <div class="mt-0.5 leading-snug">${message}</div>
      </div>
      <button type="button" onclick="this.parentElement.classList.add('hidden')" class="text-slate-400 hover:text-slate-600 p-0.5 transition-colors">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    `;
    alertBox.classList.remove("hidden");
  }

  const toast = document.createElement("div");
  toast.className = `pointer-events-auto transform translate-y-2 opacity-0 transition-all duration-300 ease-out shadow-lg rounded-xl border p-4 flex items-start gap-3 ${style.bg}`;
  toast.innerHTML = `
    <div class="w-8 h-8 rounded-lg ${style.iconBg} flex items-center justify-center shrink-0 shadow-xs mt-0.5">
      <span class="material-symbols-outlined text-[20px]">${style.icon}</span>
    </div>
    <div class="flex-1 min-w-0 pr-1">
      <div class="font-bold text-sm leading-tight">${toastTitle}</div>
      <div class="text-xs mt-1 leading-relaxed opacity-90 break-words">${message}</div>
    </div>
    <button type="button" class="text-slate-400 hover:text-slate-600 transition-colors p-1 -mr-1 rounded-md shrink-0">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;

  const closeBtn = toast.querySelector("button");
  if (closeBtn) {
    closeBtn.onclick = () => {
      toast.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => toast.remove(), 300);
    };
  }

  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove("opacity-0", "translate-y-2");
    toast.classList.add("opacity-100", "translate-y-0");
  });

  setTimeout(() => {
    if (toast.parentElement) {
      toast.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => toast.remove(), 300);
    }
  }, 4500);
}

function selectRole(role, targetButton) {
  vaiTroHienTai = role;

  const alertBox = document.getElementById("loginAlertBox");
  if (alertBox) alertBox.classList.add("hidden");

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
    showToast("Vui lòng nhập đầy đủ thông tin đăng nhập.", "warning", "Thiếu thông tin");
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
      body: JSON.stringify({ email, mat_khau, vai_tro: vaiTroHienTai })
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok && data.data) {
      const userData = data.data;

      if (vaiTroHienTai === "mentor" && userData.vai_tro === "ThucTapSinh") {
        showToast(
          "Tài khoản Sinh viên không có quyền đăng nhập vào cổng Doanh nghiệp / Mentor. Vui lòng chuyển sang cổng Sinh viên.",
          "error",
          "Truy cập bị từ chối"
        );
        submitBtn.innerHTML = originalContent;
        submitBtn.disabled = false;
        return;
      }

      if (vaiTroHienTai === "faculty" && userData.vai_tro === "ThucTapSinh") {
        showToast(
          "Tài khoản Sinh viên không có quyền đăng nhập vào cổng Nhà trường / Quản lý. Vui lòng chuyển sang cổng Sinh viên.",
          "error",
          "Truy cập bị từ chối"
        );
        submitBtn.innerHTML = originalContent;
        submitBtn.disabled = false;
        return;
      }

      if (vaiTroHienTai === "student" && userData.vai_tro !== "ThucTapSinh") {
        showToast(
          "Tài khoản này thuộc vai trò Quản lý / Mentor. Vui lòng chuyển sang cổng Doanh nghiệp hoặc Nhà trường.",
          "error",
          "Sai cổng đăng nhập"
        );
        submitBtn.innerHTML = originalContent;
        submitBtn.disabled = false;
        return;
      }

      const expireTime = Date.now() + 2 * 60 * 60 * 1000;
      userData.expires_at = expireTime;
      showToast("Đăng nhập thành công! Đang chuyển hướng...", "success", "Xác thực thành công");

      setTimeout(() => {
        if (userData.vai_tro === "ThucTapSinh") {
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
      }, 500);
      return;
    }

    let errorMsg = "Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản và mật khẩu.";
    if (data.detail) {
      if (typeof data.detail === "string") {
        errorMsg = data.detail;
      } else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
        errorMsg = data.detail[0].msg;
      }
    }
    showToast(errorMsg, "error", "Đăng nhập không thành công");
    submitBtn.innerHTML = originalContent;
    submitBtn.disabled = false;
  } catch (err) {
    showToast(
      "Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại đường truyền mạng hoặc thử lại sau.",
      "error",
      "Mất kết nối máy chủ"
    );
    submitBtn.innerHTML = originalContent;
    submitBtn.disabled = false;
  }
}
