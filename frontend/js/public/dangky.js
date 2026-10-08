let selectedRole = "intern";

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

  const alertBox = document.getElementById("registerAlertBox");

  const config = {
    error: {
      bg: "bg-red-50 text-red-950 border-red-200",
      iconBg: "bg-red-500 text-white",
      icon: "error",
      defaultTitle: "Đăng ký không thành công",
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
      defaultTitle: "Thông báo phân quyền",
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

function selectRole(roleKey) {
  if (roleKey !== "intern") {
    showToast(
      "Cổng đăng ký trực tuyến chỉ dành cho Sinh viên / Thực tập sinh. Tài khoản Mentor Doanh nghiệp và Khoa / Nhà trường được cấp trực tiếp bởi Ban Quản trị hệ thống (Admin).",
      "info",
      "Thông báo phân quyền"
    );
    return;
  }
  selectedRole = "intern";
}

function togglePasswordVisibility(fieldId, triggerBtn) {
  const field = document.getElementById(fieldId);
  if (!field || !triggerBtn) return;
  const icon = triggerBtn.querySelector(".material-symbols-outlined");
  if (field.type === "password") {
    field.type = "text";
    if (icon) icon.textContent = "visibility_off";
  } else {
    field.type = "password";
    if (icon) icon.textContent = "visibility";
  }
}

function assessPasswordStrength(val) {
  const bar1 = document.getElementById("bar-1");
  const bar2 = document.getElementById("bar-2");
  const bar3 = document.getElementById("bar-3");
  const text = document.getElementById("strengthText");
  if (!bar1 || !bar2 || !bar3 || !text) return;

  if (!val || val.length === 0) {
    text.textContent = "Chưa nhập";
    text.className =
      "font-label-sm text-label-sm font-bold text-on-surface-variant";
    bar1.className = "h-full w-1/3 bg-transparent rounded-full transition-all";
    bar2.className = "h-full w-1/3 bg-transparent rounded-full transition-all";
    bar3.className = "h-full w-1/3 bg-transparent rounded-full transition-all";
    return;
  }

  let score = 0;
  if (val.length >= 8) score++;
  if (/[A-Z]/.test(val) && /[0-9]/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  if (score === 1 || val.length < 8) {
    text.textContent = "Yếu";
    text.className = "font-label-sm text-label-sm font-bold text-error";
    bar1.className = "h-full w-1/3 bg-error rounded-full transition-all";
    bar2.className = "h-full w-1/3 bg-transparent rounded-full transition-all";
    bar3.className = "h-full w-1/3 bg-transparent rounded-full transition-all";
  } else if (score === 2) {
    text.textContent = "Trung bình";
    text.className = "font-label-sm text-label-sm font-bold text-tertiary";
    bar1.className = "h-full w-1/3 bg-tertiary rounded-full transition-all";
    bar2.className = "h-full w-1/3 bg-tertiary rounded-full transition-all";
    bar3.className = "h-full w-1/3 bg-transparent rounded-full transition-all";
  } else {
    text.textContent = "Mạnh";
    text.className = "font-label-sm text-label-sm font-bold text-secondary";
    bar1.className = "h-full w-1/3 bg-secondary rounded-full transition-all";
    bar2.className = "h-full w-1/3 bg-secondary rounded-full transition-all";
    bar3.className = "h-full w-1/3 bg-secondary rounded-full transition-all";
  }
}

async function handleRegistrationSubmit() {
  const fullName = document.getElementById("fullName") ? document.getElementById("fullName").value.trim() : "";
  const email = document.getElementById("email") ? document.getElementById("email").value.trim() : "";
  const institution = document.getElementById("institution") ? document.getElementById("institution").value : "";
  const major = document.getElementById("major") ? document.getElementById("major").value.trim() : "";
  const pwd = document.getElementById("password") ? document.getElementById("password").value : "";
  const confirmPwd = document.getElementById("confirmPassword") ? document.getElementById("confirmPassword").value : "";
  const termsCheck = document.getElementById("termsCheck");

  if (!fullName) {
    showToast("Vui lòng nhập họ và tên.", "warning", "Thiếu thông tin");
    return;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRegex.test(email)) {
    showToast("Địa chỉ email không đúng định dạng chuẩn (ví dụ: sinhvien@ictu.edu.vn).", "warning", "Email không hợp lệ");
    return;
  }
  if (!pwd || pwd.length < 6) {
    showToast("Mật khẩu phải có tối thiểu 6 ký tự.", "warning", "Mật khẩu quá ngắn");
    return;
  }
  if (pwd !== confirmPwd) {
    showToast("Mật khẩu và xác nhận mật khẩu không khớp. Vui lòng kiểm tra lại!", "warning", "Mật khẩu không khớp");
    return;
  }
  if (termsCheck && !termsCheck.checked) {
    showToast("Vui lòng đồng ý với điều khoản sử dụng.", "warning", "Chưa đồng ý điều khoản");
    return;
  }

  const universityMapping = {
    vnuhcm: 3,
    hust: 2,
    fpt: 4,
    neu: 5,
    uit: 6,
    other: 1
  };

  const ma_truong = universityMapping[institution] || 1;

  const submitBtn = document.querySelector('button[type="submit"]');
  const originalContent = submitBtn ? submitBtn.innerHTML : "";
  if (submitBtn) {
    submitBtn.innerHTML = `
      <span class="inline-block w-4 h-4 rounded-full border-2 border-on-primary border-t-transparent animate-spin"></span>
      <span>Đang xử lý đăng ký...</span>
    `;
    submitBtn.disabled = true;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ho_ten: fullName,
        email: email,
        mat_khau: pwd,
        vai_tro: "ThucTapSinh",
        chuyen_nganh: major || null,
        ma_truong: ma_truong
      })
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok && data.status_code === 201) {
      const expireTime = Date.now() + 2 * 60 * 60 * 1000;
      const regUser = {
        ho_ten: fullName,
        email: email,
        vai_tro: "ThucTapSinh",
        ma_sinh_vien: email.split("@")[0].toUpperCase(),
        expires_at: expireTime
      };
      localStorage.setItem("ictu_student_session", JSON.stringify(regUser));
      localStorage.setItem("user", JSON.stringify(regUser));
      localStorage.setItem("currentUser", JSON.stringify(regUser));
      showToast(
        "Đăng ký tài khoản thực tập sinh thành công! Đang chuyển hướng sang trang đăng nhập...",
        "success",
        "Đăng ký thành công"
      );
      setTimeout(() => {
        window.location.href = "dangnhap.html";
      }, 1000);
      return;
    }

    let errorMsg = "Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.";
    if (data.detail) {
      if (typeof data.detail === "string") {
        errorMsg = data.detail;
      } else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
        errorMsg = data.detail[0].msg;
      }
    }
    showToast(errorMsg, "error", "Đăng ký thất bại");
    if (submitBtn) {
      submitBtn.innerHTML = originalContent;
      submitBtn.disabled = false;
    }
  } catch (err) {
    showToast(
      "Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại đường truyền mạng hoặc thử lại sau.",
      "error",
      "Mất kết nối máy chủ"
    );
    if (submitBtn) {
      submitBtn.innerHTML = originalContent;
      submitBtn.disabled = false;
    }
  }
}
