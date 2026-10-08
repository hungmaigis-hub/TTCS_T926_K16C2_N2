function kichHoatHienThi() {
  document.documentElement.classList.add("loaded");
}

window.addEventListener("DOMContentLoaded", kichHoatHienThi);
setTimeout(kichHoatHienThi, 300);

const THOI_HAN_SESSION_MS = 2 * 60 * 60 * 1000;

function layThongTinSession(loai) {
  try {
    const key = loai === "student" ? "ictu_student_session" : "ictu_admin_session";
    let raw = localStorage.getItem(key);
    if (!raw) {
      const fallback = localStorage.getItem("user") || localStorage.getItem("currentUser");
      if (fallback) {
        const parsed = JSON.parse(fallback);
        if (loai === "student" && parsed.vai_tro === "ThucTapSinh") {
          raw = fallback;
        } else if (loai === "manager" && parsed.vai_tro !== "ThucTapSinh") {
          raw = fallback;
        }
      }
    }
    if (!raw) return null;
    const session = JSON.parse(raw);
    const now = Date.now();
    if (session.expires_at && now > parseInt(session.expires_at, 10)) {
      localStorage.removeItem(key);
      return null;
    }
    return session;
  } catch {
    return null;
  }
}

function luuThongTinSession(loai, user) {
  try {
    const key = loai === "student" ? "ictu_student_session" : "ictu_admin_session";
    user.expires_at = Date.now() + THOI_HAN_SESSION_MS;
    localStorage.setItem(key, JSON.stringify(user));
    localStorage.setItem("user", JSON.stringify(user));
    localStorage.setItem("currentUser", JSON.stringify(user));
  } catch {}
}

function layTenVietTat(hoTen) {
  if (!hoTen) return "AD";
  const words = hoTen.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
  }
  return hoTen.substring(0, 2).toUpperCase();
}

function dongBoThongTinNguoiDung() {
  const isStudentPage =
    window.location.pathname.includes("/sinhvien/") ||
    document.querySelector("#sidebarTenSinhVien") !== null;
  const isManagerPage =
    window.location.pathname.includes("/quanly/") ||
    document.querySelector("#adminSidebarName") !== null ||
    (document.querySelector("aside") && window.location.pathname.includes("/quanly/"));

  if (isStudentPage) {
    let student = layThongTinSession("student");
    if (!student) {
      window.location.href = "../public/dangnhap.html";
      return;
    }

    const hoTen = student.ho_ten || "Vũ Quang Huy";
    const email = student.email || "quanghuy.dtc@ictu.edu.vn";
    const maSV = student.ma_sinh_vien || (email.includes("@") ? email.split("@")[0].toUpperCase() : "DTC2051060124");
    const initials = layTenVietTat(hoTen);

    const elTenSinhVien = document.getElementById("sidebarTenSinhVien");
    if (elTenSinhVien) elTenSinhVien.textContent = hoTen;

    const elMaSinhVien = document.getElementById("sidebarMaSinhVien");
    if (elMaSinhVien) elMaSinhVien.textContent = `${maSV} - K19`;

    const elAvatarInitials = document.getElementById("avatarInitials");
    if (elAvatarInitials) elAvatarInitials.textContent = initials;

    const elWelcome = document.getElementById("welcomeTenSinhVien");
    if (elWelcome) {
      elWelcome.textContent = hoTen;
    } else {
      document.querySelectorAll("h1").forEach((h1) => {
        if (h1.textContent.includes("Xin chào,")) {
          h1.innerHTML = `Xin chào, ${hoTen}! 👋`;
        }
      });
    }

    const elChuKy = document.getElementById("chuKySinhVienTen");
    if (elChuKy) elChuKy.textContent = hoTen;

    const aside = document.querySelector("aside");
    if (aside) {
      const userCard = aside.querySelector(".rounded-2xl");
      if (userCard) {
        const textContainer = userCard.querySelector(".flex-1");
        if (textContainer) {
          const h4 = textContainer.querySelector("h4");
          if (h4) h4.textContent = hoTen;
          const p = textContainer.querySelector("p");
          if (p) p.textContent = `${maSV} - K19`;
        }
        const avt = userCard.querySelector(".rounded-full.bg-gradient-to-tr");
        if (avt) avt.textContent = initials;
      }
    }

    document.querySelectorAll("a[title='Đăng xuất'], [data-action='logout']").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        localStorage.removeItem("ictu_student_session");
        localStorage.removeItem("user");
        localStorage.removeItem("currentUser");
        window.location.href = "../public/dangnhap.html";
      });
    });
  }

  if (isManagerPage) {
    let admin = layThongTinSession("manager");
    if (!admin) {
      window.location.href = "../public/dangnhap.html";
      return;
    }

    const hoTen = admin.ho_ten || "Ban Đào Tạo & QLTT";
    const email = admin.email || "admin@ictu.edu.vn";
    const initials = layTenVietTat(hoTen);

    let vaiTroText = "Quản trị viên";
    if (admin.vai_tro === "HR" || admin.vai_tro === "hr") vaiTroText = "Cán bộ HR";
    else if (admin.vai_tro === "Mentor" || admin.vai_tro === "mentor") vaiTroText = "Mentor hướng dẫn";
    else if (admin.vai_tro === "NhaTruong") vaiTroText = "Đại diện Nhà trường";

    const elAdminName = document.getElementById("adminSidebarName");
    if (elAdminName) elAdminName.textContent = hoTen;

    const elAdminEmail = document.getElementById("adminSidebarEmail");
    if (elAdminEmail) elAdminEmail.textContent = email;

    const elAdminRole = document.getElementById("adminSidebarRole");
    if (elAdminRole) elAdminRole.textContent = vaiTroText;

    const elAdminAvatar = document.getElementById("adminAvatarInitials");
    if (elAdminAvatar) elAdminAvatar.textContent = initials;

    const aside = document.querySelector("aside");
    if (aside) {
      const userCard = aside.querySelector(".rounded-2xl");
      if (userCard) {
        const textContainer = userCard.querySelector(".flex-1");
        if (textContainer) {
          const h4 = textContainer.querySelector("h4");
          if (h4) h4.textContent = hoTen;
          const p = textContainer.querySelector("p");
          if (p) p.textContent = email;
          const roleBadge = textContainer.querySelector("span.rounded-full");
          if (roleBadge) roleBadge.textContent = vaiTroText;
        }
        const avt = userCard.querySelector(".rounded-full.bg-gradient-to-tr");
        if (avt) avt.textContent = initials;
        const statusDot = userCard.querySelector(".relative span.rounded-full");
        if (statusDot) statusDot.textContent = "";
      }
    }

    document.querySelectorAll("a[title='Đăng xuất'], [data-action='logout']").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        localStorage.removeItem("ictu_admin_session");
        localStorage.removeItem("user");
        localStorage.removeItem("currentUser");
        window.location.href = "../public/dangnhap.html";
      });
    });
  }
}

window.addEventListener("DOMContentLoaded", dongBoThongTinNguoiDung);

function thongBaoDangCapNhat(tenTinhNang, moTa) {
  let modal = document.getElementById("modal-thong-bao-cap-nhat");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "modal-thong-bao-cap-nhat";
    modal.className =
      "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm transition-opacity opacity-0 pointer-events-none duration-200";
    modal.innerHTML = `
      <div id="modal-thong-bao-card" class="relative w-full max-w-md bg-white rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-100 flex flex-col items-center text-center transform scale-95 transition-transform duration-200">
        <button type="button" onclick="dongThongBaoCapNhat()" class="absolute top-4 right-4 w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 flex items-center justify-center transition-colors">
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
        <div class="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 mb-4 shadow-sm ring-4 ring-amber-50">
          <span class="material-symbols-outlined text-[32px]">hourglass_top</span>
        </div>
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 mb-2.5">
          <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
          Tính năng đang cập nhật
        </div>
        <h3 id="modal-cap-nhat-tieude" class="text-lg sm:text-xl font-bold text-slate-900 mb-2">
          Đang hoàn thiện tính năng
        </h3>
        <p id="modal-cap-nhat-noidung" class="text-sm text-slate-600 leading-relaxed mb-6">
          Chức năng hiện đang được phát triển trong kế hoạch Sprint tiếp theo. Vui lòng quay lại sau!
        </p>
        <div class="w-full p-3.5 rounded-2xl bg-slate-50 border border-slate-100 text-left mb-6 flex items-start gap-3">
          <span class="material-symbols-outlined text-[20px] text-emerald-600 shrink-0 mt-0.5">tips_and_updates</span>
          <p class="text-xs text-slate-600 leading-relaxed">
            Bạn có thể trải nghiệm các phân hệ đã sẵn sàng: <strong class="text-slate-800">Tổng quan thực tập</strong>, <strong class="text-slate-800">Nộp tài liệu &amp; CV</strong>, <strong class="text-slate-800">Ký hợp đồng</strong>, và <strong class="text-slate-800">Bảng nhiệm vụ</strong>.
          </p>
        </div>
        <div class="w-full flex gap-3">
          <button type="button" onclick="dongThongBaoCapNhat()" class="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold shadow-sm hover:shadow transition-all">
            Đã hiểu, đóng thông báo
          </button>
        </div>
      </div>
    `;
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        dongThongBaoCapNhat();
      }
    });
    document.body.appendChild(modal);
  }

  const tieuDeEl = document.getElementById("modal-cap-nhat-tieude");
  const noiDungEl = document.getElementById("modal-cap-nhat-noidung");

  if (tenTinhNang) {
    tieuDeEl.textContent = tenTinhNang;
    noiDungEl.innerHTML =
      moTa ||
      `Chức năng <span class="font-semibold text-slate-900">${tenTinhNang}</span> hiện đang được hoàn thiện theo kế hoạch mở rộng của hệ thống. Bạn sẽ nhận được thông báo khi phân hệ này được mở khóa!`;
  } else {
    tieuDeEl.textContent = "Tính năng đang hoàn thiện";
    noiDungEl.innerHTML =
      moTa ||
      "Chức năng này thuộc kế hoạch phát triển bổ sung và đang được hoàn tất. Vui lòng quay lại sau!";
  }

  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
  const card = document.getElementById("modal-thong-bao-card");
  if (card) {
    card.classList.remove("scale-95");
    card.classList.add("scale-100");
  }
}

function dongThongBaoCapNhat() {
  const modal = document.getElementById("modal-thong-bao-cap-nhat");
  if (!modal) return;
  const card = document.getElementById("modal-thong-bao-card");
  if (card) {
    card.classList.remove("scale-100");
    card.classList.add("scale-95");
  }
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    dongThongBaoCapNhat();
  }
});

document.addEventListener("click", function (e) {
  const target = e.target.closest("[data-coming-soon], [data-chua-hoan-thien]");
  if (target) {
    e.preventDefault();
    const ten =
      target.getAttribute("data-coming-soon") ||
      target.getAttribute("data-chua-hoan-thien") ||
      target.textContent.trim();
    thongBaoDangCapNhat(ten);
  }
});
