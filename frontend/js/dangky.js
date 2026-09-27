function selectRole(roleKey) {
  const roles = ["intern", "mentor", "university"];
  roles.forEach((role) => {
    const btn = document.getElementById("role-" + role);
    if (!btn) return;
    const radio = btn.querySelector(".role-radio");
    const roleLabel = btn.querySelector("p.font-label-lg");

    if (role === roleKey) {
      btn.classList.remove("bg-surface-container-low", "opacity-85");
      btn.classList.add("bg-surface-container-high", "opacity-100");
      if (radio) {
        radio.className =
          "role-radio flex h-4 w-4 rounded-full bg-primary items-center justify-center text-white";
        radio.innerHTML =
          '<span class="material-symbols-outlined text-[12px]">check</span>';
      }
      if (roleLabel) {
        roleLabel.classList.add("text-primary");
        roleLabel.classList.remove("text-on-surface");
      }
    } else {
      btn.classList.remove("bg-surface-container-high", "opacity-100");
      btn.classList.add("bg-surface-container-low", "opacity-85");
      if (radio) {
        radio.className =
          "role-radio flex h-4 w-4 rounded-full bg-surface-dim items-center justify-center";
        radio.innerHTML = "";
      }
      if (roleLabel) {
        roleLabel.classList.remove("text-primary");
        roleLabel.classList.add("text-on-surface");
      }
    }
  });
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

function handleRegistrationSubmit() {
  const pwd = document.getElementById("password")
    ? document.getElementById("password").value
    : "";
  const confirmPwd = document.getElementById("confirmPassword")
    ? document.getElementById("confirmPassword").value
    : "";
  if (pwd !== confirmPwd) {
    alert("Mật khẩu và xác nhận mật khẩu không khớp. Vui lòng kiểm tra lại!");
    return;
  }
  alert("Đăng ký tài khoản thành công! Vui lòng đăng nhập.");
  window.location.href = "dangnhap.html";
}
