let selectedRole = "intern";

function selectRole(roleKey) {
  if (roleKey !== "intern") {
    alert("Cổng đăng ký trực tuyến chỉ dành cho Sinh viên / Thực tập sinh. Tài khoản Mentor Doanh nghiệp và Khoa / Nhà trường được cấp trực tiếp bởi Ban Quản trị hệ thống (Admin).");
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
    alert("Vui lòng nhập họ và tên.");
    return;
  }
  if (!email) {
    alert("Vui lòng nhập địa chỉ email.");
    return;
  }
  if (!pwd || pwd.length < 6) {
    alert("Mật khẩu phải có tối thiểu 6 ký tự.");
    return;
  }
  if (pwd !== confirmPwd) {
    alert("Mật khẩu và xác nhận mật khẩu không khớp. Vui lòng kiểm tra lại!");
    return;
  }
  if (termsCheck && !termsCheck.checked) {
    alert("Vui lòng đồng ý với điều khoản sử dụng.");
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
      alert("Đăng ký tài khoản thực tập sinh thành công! Đang chuyển hướng sang trang đăng nhập.");
      window.location.href = "dangnhap.html";
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
    alert(errorMsg);
    if (submitBtn) {
      submitBtn.innerHTML = originalContent;
      submitBtn.disabled = false;
    }
  } catch (err) {
    alert("Không thể kết nối đến máy chủ. Vui lòng thử lại sau.");
    if (submitBtn) {
      submitBtn.innerHTML = originalContent;
      submitBtn.disabled = false;
    }
  }
}
