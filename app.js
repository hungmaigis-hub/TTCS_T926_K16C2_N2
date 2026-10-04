/**
 * Quản lý Form Ca Làm Việc & Modal Chọn Thực Tập Sinh Áp Dụng
 */

// 1. Dữ liệu mẫu danh sách thực tập sinh
const INITIAL_INTERNS = [
  {
    id: 1,
    name: "Nguyễn Văn An",
    code: "TTS-2026-001",
    department: "Frontend",
    role: "Frontend React Intern",
    email: "vanan.nguyen@company.vn",
    phone: "0912 345 678",
    avatarColor: "bg-avatar-frontend",
    initials: "NA"
  },
  {
    id: 2,
    name: "Trần Thị Mai",
    code: "TTS-2026-002",
    department: "UI/UX",
    role: "UI/UX Product Designer",
    email: "mai.tran@company.vn",
    phone: "0988 123 456",
    avatarColor: "bg-avatar-uiux",
    initials: "TM"
  },
  {
    id: 3,
    name: "Lê Hoàng Long",
    code: "TTS-2026-003",
    department: "Backend",
    role: "Backend Node.js/Go Intern",
    email: "long.le@company.vn",
    phone: "0905 789 123",
    avatarColor: "bg-avatar-backend",
    initials: "HL"
  },
  {
    id: 4,
    name: "Phạm Minh Đức",
    code: "TTS-2026-004",
    department: "QA",
    role: "QA / Automation Tester",
    email: "duc.pham@company.vn",
    phone: "0934 567 890",
    avatarColor: "bg-avatar-qa",
    initials: "MD"
  },
  {
    id: 5,
    name: "Đỗ Thu Hà",
    code: "TTS-2026-005",
    department: "Frontend",
    role: "Frontend Vue/Nuxt Intern",
    email: "ha.do@company.vn",
    phone: "0977 654 321",
    avatarColor: "bg-avatar-frontend",
    initials: "TH"
  },
  {
    id: 6,
    name: "Vũ Hải Đăng",
    code: "TTS-2026-006",
    department: "Mobile",
    role: "Mobile Flutter/iOS Intern",
    email: "dang.vu@company.vn",
    phone: "0922 334 455",
    avatarColor: "bg-avatar-mobile",
    initials: "HD"
  },
  {
    id: 7,
    name: "Bùi Quốc Bảo",
    code: "TTS-2026-007",
    department: "Backend",
    role: "Backend Java Spring Boot",
    email: "bao.bui@company.vn",
    phone: "0944 556 677",
    avatarColor: "bg-avatar-backend",
    initials: "QB"
  },
  {
    id: 8,
    name: "Hoàng Thùy Linh",
    code: "TTS-2026-008",
    department: "DevOps",
    role: "DevOps & Cloud Intern",
    email: "linh.hoang@company.vn",
    phone: "0966 778 899",
    avatarColor: "bg-avatar-devops",
    initials: "TL"
  },
  {
    id: 9,
    name: "Đặng Tuấn Kiệt",
    code: "TTS-2026-009",
    department: "QA",
    role: "Manual QA Tester Intern",
    email: "kiet.dang@company.vn",
    phone: "0918 223 344",
    avatarColor: "bg-avatar-qa",
    initials: "TK"
  },
  {
    id: 10,
    name: "Ngô Bảo Trâm",
    code: "TTS-2026-010",
    department: "HR",
    role: "HR Recruitment Intern",
    email: "tram.ngo@company.vn",
    phone: "0989 334 455",
    avatarColor: "bg-avatar-hr",
    initials: "BT"
  }
];

// 2. Dữ liệu mẫu ca làm việc ban đầu
let shiftsList = [
  {
    id: "SHIFT-001",
    name: "Ca Sáng - Đội ngũ Frontend & UI/UX",
    startTime: "08:30",
    endTime: "12:00",
    daysOfWeek: ["T2", "T3", "T4", "T5", "T6"],
    internIds: [1, 2, 5],
    notes: "Họp daily standup vào 08:45"
  },
  {
    id: "SHIFT-002",
    name: "Ca Chiều - Đội ngũ Kỹ Thuật Backend & QA",
    startTime: "13:30",
    endTime: "17:30",
    daysOfWeek: ["T2", "T4", "T6"],
    internIds: [3, 4, 7],
    notes: "Review code định kỳ thứ Sáu hàng tuần"
  }
];

// Trạng thái ứng dụng
let selectedInternIds = new Set([1, 2]); // Mặc định chọn 2 TTS ban đầu để demo
let tempModalSelectedIds = new Set();
let internModalInstance = null;
let toastInstance = null;

// DOM Elements
const shiftForm = document.getElementById("shiftForm");
const shiftNameInput = document.getElementById("shiftName");
const startTimeInput = document.getElementById("startTime");
const endTimeInput = document.getElementById("endTime");
const shiftDurationBadge = document.getElementById("shiftDurationBadge");
const overnightNotice = document.getElementById("overnightNotice");
const timeErrorFeedback = document.getElementById("timeErrorFeedback");

const dayCheckboxes = document.querySelectorAll(".day-checkbox");
const dayErrorFeedback = document.getElementById("dayErrorFeedback");
const btnSelectWeekdays = document.getElementById("btnSelectWeekdays");
const btnSelectWeekend = document.getElementById("btnSelectWeekend");
const btnSelectAllDays = document.getElementById("btnSelectAllDays");
const btnClearDays = document.getElementById("btnClearDays");

const btnSelectedBadge = document.getElementById("btnSelectedBadge");
const emptyInternAlert = document.getElementById("emptyInternAlert");
const selectedInternTags = document.getElementById("selectedInternTags");
const internErrorFeedback = document.getElementById("internErrorFeedback");
const shiftNotes = document.getElementById("shiftNotes");
const btnResetForm = document.getElementById("btnResetForm");

// Modal Elements
const internModalEl = document.getElementById("internSelectionModal");
const modalSearchInput = document.getElementById("modalSearchInput");
const modalDepartmentFilter = document.getElementById("modalDepartmentFilter");
const modalSelectAll = document.getElementById("modalSelectAll");
const modalSelectedCounter = document.getElementById("modalSelectedCounter");
const modalTotalCounter = document.getElementById("modalTotalCounter");
const modalInternList = document.getElementById("modalInternList");
const modalNoResults = document.getElementById("modalNoResults");
const modalClearSelection = document.getElementById("modalClearSelection");
const modalBtnConfirm = document.getElementById("modalBtnConfirm");
const modalConfirmCount = document.getElementById("modalConfirmCount");

// Table Elements
const shiftTableBody = document.getElementById("shiftTableBody");
const shiftCountBadge = document.getElementById("shiftCountBadge");

// Toast Elements
const actionToastEl = document.getElementById("actionToast");
const toastMessageEl = document.getElementById("toastMessage");
const toastIconEl = document.getElementById("toastIcon");

// ==========================================
// KHỞI TẠO ỨNG DỤNG
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  // Khởi tạo Bootstrap components
  if (typeof bootstrap !== "undefined") {
    internModalInstance = new bootstrap.Modal(internModalEl);
    toastInstance = new bootstrap.Toast(actionToastEl, { delay: 3500 });
  }

  // Cập nhật tính toán thời lượng ban đầu
  calculateShiftDuration();

  // Hiển thị danh sách TTS đã chọn trên form
  renderSelectedInternTags();

  // Hiển thị bảng ca làm việc
  renderShiftsTable();

  // Đăng ký các sự kiện tương tác
  bindEventListeners();
});

// ==========================================
// XỬ LÝ TÍNH TOÁN GIỜ (TYPE="TIME")
// ==========================================
function calculateShiftDuration() {
  const startVal = startTimeInput.value;
  const endVal = endTimeInput.value;

  if (!startVal || !endVal) {
    shiftDurationBadge.textContent = "--:--";
    return;
  }

  const [startHour, startMin] = startVal.split(":").map(Number);
  const [endHour, endMin] = endVal.split(":").map(Number);

  const startTotalMinutes = startHour * 60 + startMin;
  const endTotalMinutes = endHour * 60 + endMin;

  if (startTotalMinutes === endTotalMinutes) {
    shiftDurationBadge.className = "badge bg-danger ms-2 fs-6";
    shiftDurationBadge.textContent = "0 giờ (Trùng nhau)";
    timeErrorFeedback.classList.remove("d-none");
    overnightNotice.classList.add("d-none");
    return;
  }

  timeErrorFeedback.classList.add("d-none");

  let diffMinutes = endTotalMinutes - startTotalMinutes;
  let isOvernight = false;

  if (diffMinutes < 0) {
    // Ca qua đêm (Ví dụ từ 22:00 hôm trước đến 06:00 hôm sau)
    diffMinutes += 24 * 60;
    isOvernight = true;
    overnightNotice.classList.remove("d-none");
  } else {
    overnightNotice.classList.add("d-none");
  }

  const hours = Math.floor(diffMinutes / 60);
  const minutes = diffMinutes % 60;

  shiftDurationBadge.className = "badge bg-primary ms-2 fs-6";
  let durationText = `${hours} giờ`;
  if (minutes > 0) {
    durationText += ` ${minutes} phút`;
  }
  if (isOvernight) {
    durationText += " (Qua đêm)";
  }

  shiftDurationBadge.textContent = durationText;
}

// ==========================================
// XỬ LÝ CHỌN CÁC NGÀY TRONG TUẦN
// ==========================================
function setDaysSelection(values) {
  dayCheckboxes.forEach(cb => {
    cb.checked = values.includes(cb.value);
  });
  dayErrorFeedback.classList.add("d-none");
}

function getSelectedDays() {
  return Array.from(dayCheckboxes)
    .filter(cb => cb.checked)
    .map(cb => cb.value);
}

// ==========================================
// RENDER TAGS THỰC TẬP SINH ĐÃ CHỌN TRÊN FORM
// ==========================================
function renderSelectedInternTags() {
  btnSelectedBadge.textContent = selectedInternIds.size;

  if (selectedInternIds.size === 0) {
    emptyInternAlert.classList.remove("d-none");
    selectedInternTags.classList.add("d-none");
    selectedInternTags.innerHTML = "";
    return;
  }

  emptyInternAlert.classList.add("d-none");
  selectedInternTags.classList.remove("d-none");
  internErrorFeedback.classList.add("d-none");

  const selectedList = INITIAL_INTERNS.filter(intern => selectedInternIds.has(intern.id));

  selectedInternTags.innerHTML = selectedList.map(intern => `
    <div class="intern-tag" data-id="${intern.id}">
      <span class="intern-avatar-sm ${intern.avatarColor}">${intern.initials}</span>
      <span class="fw-semibold text-dark">${intern.name}</span>
      <span class="badge bg-light text-secondary border small">${intern.code}</span>
      <button type="button" class="intern-tag-btn-remove" title="Xóa thực tập sinh" data-remove-id="${intern.id}">
        <i class="bi bi-x-lg" style="font-size: 0.75rem;"></i>
      </button>
    </div>
  `).join("");

  // Bắt sự kiện xóa tag trực tiếp trên form
  selectedInternTags.querySelectorAll(".intern-tag-btn-remove").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const idToRemove = Number(btn.getAttribute("data-remove-id"));
      selectedInternIds.delete(idToRemove);
      renderSelectedInternTags();
      showToast(`Đã bỏ chọn thực tập sinh khỏi ca`, "info");
    });
  });
}

// ==========================================
// MODAL DANH SÁCH THỰC TẬP SINH
// ==========================================
function openInternModal() {
  // Đồng bộ danh sách đang chọn sang bộ nhớ tạm của modal
  tempModalSelectedIds = new Set(selectedInternIds);
  modalSearchInput.value = "";
  modalDepartmentFilter.value = "ALL";
  renderModalInternList();
}

function getFilteredInterns() {
  const searchTerm = modalSearchInput.value.trim().toLowerCase();
  const departmentFilter = modalDepartmentFilter.value;

  return INITIAL_INTERNS.filter(intern => {
    const matchesSearch = 
      intern.name.toLowerCase().includes(searchTerm) ||
      intern.code.toLowerCase().includes(searchTerm) ||
      intern.email.toLowerCase().includes(searchTerm) ||
      intern.role.toLowerCase().includes(searchTerm);

    const matchesDept = (departmentFilter === "ALL") || (intern.department === departmentFilter);

    return matchesSearch && matchesDept;
  });
}

function renderModalInternList() {
  const filtered = getFilteredInterns();

  modalTotalCounter.textContent = filtered.length;
  modalSelectedCounter.textContent = tempModalSelectedIds.size;
  modalConfirmCount.textContent = tempModalSelectedIds.size;

  if (filtered.length === 0) {
    modalInternList.innerHTML = "";
    modalNoResults.classList.remove("d-none");
    modalSelectAll.checked = false;
    modalSelectAll.disabled = true;
    return;
  }

  modalNoResults.classList.add("d-none");
  modalSelectAll.disabled = false;

  // Kiểm tra trạng thái checkbox "Chọn tất cả"
  const allFilteredSelected = filtered.length > 0 && filtered.every(i => tempModalSelectedIds.has(i.id));
  modalSelectAll.checked = allFilteredSelected;

  modalInternList.innerHTML = filtered.map(intern => {
    const isChecked = tempModalSelectedIds.has(intern.id);
    return `
      <label class="list-group-item intern-list-item d-flex align-items-center justify-content-between ${isChecked ? 'selected' : ''}" for="modal_tts_${intern.id}">
        <div class="d-flex align-items-center gap-3">
          <input 
            class="form-check-input intern-modal-checkbox flex-shrink-0" 
            type="checkbox" 
            id="modal_tts_${intern.id}" 
            value="${intern.id}" 
            ${isChecked ? 'checked' : ''}
          >
          <div class="intern-avatar ${intern.avatarColor}">
            ${intern.initials}
          </div>
          <div>
            <div class="d-flex align-items-center gap-2">
              <span class="fw-bold text-dark">${intern.name}</span>
              <span class="badge bg-secondary-subtle text-secondary small border">${intern.code}</span>
            </div>
            <div class="small text-muted">
              <span>${intern.role}</span> &bull; <span>${intern.email}</span>
            </div>
          </div>
        </div>
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-1 small">
          ${intern.department}
        </span>
      </label>
    `;
  }).join("");

  // Bắt sự kiện check/uncheck từng dòng
  modalInternList.querySelectorAll(".intern-modal-checkbox").forEach(cb => {
    cb.addEventListener("change", (e) => {
      const id = Number(e.target.value);
      if (e.target.checked) {
        tempModalSelectedIds.add(id);
      } else {
        tempModalSelectedIds.delete(id);
      }
      updateModalSelectionUI();
    });
  });
}

function updateModalSelectionUI() {
  const filtered = getFilteredInterns();
  modalSelectedCounter.textContent = tempModalSelectedIds.size;
  modalConfirmCount.textContent = tempModalSelectedIds.size;

  // Cập nhật trạng thái class "selected" trên danh sách
  modalInternList.querySelectorAll(".intern-list-item").forEach(item => {
    const cb = item.querySelector(".intern-modal-checkbox");
    if (cb && cb.checked) {
      item.classList.add("selected");
    } else {
      item.classList.remove("selected");
    }
  });

  const allFilteredSelected = filtered.length > 0 && filtered.every(i => tempModalSelectedIds.has(i.id));
  modalSelectAll.checked = allFilteredSelected;
}

// ==========================================
// RENDER BẢNG DANH SÁCH CA LÀM VIỆC
// ==========================================
function renderShiftsTable() {
  shiftCountBadge.textContent = shiftsList.length;

  if (shiftsList.length === 0) {
    shiftTableBody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-5 text-muted">
          <i class="bi bi-inbox fs-2 d-block mb-2 text-secondary opacity-50"></i>
          <span>Chưa có ca làm việc nào. Hãy tạo ca đầu tiên ở form bên trên!</span>
        </td>
      </tr>
    `;
    return;
  }

  shiftTableBody.innerHTML = shiftsList.map(shift => {
    // Lấy thông tin các thực tập sinh của ca
    const assignedInterns = INITIAL_INTERNS.filter(i => shift.internIds.includes(i.id));

    // Render badge các ngày trong tuần
    const daysHtml = shift.daysOfWeek.map(d => {
      const isWeekend = d === "T7" || d === "CN";
      return `<span class="day-badge ${isWeekend ? 'weekend-badge' : ''}">${d}</span>`;
    }).join("");

    // Render avatar stack của thực tập sinh
    const avatarStackHtml = `
      <div class="d-flex align-items-center gap-2">
        <div class="avatar-stack">
          ${assignedInterns.slice(0, 4).map(intern => `
            <span class="avatar-stack-item ${intern.avatarColor}" title="${intern.name} (${intern.code})">
              ${intern.initials}
            </span>
          `).join("")}
          ${assignedInterns.length > 4 ? `
            <span class="avatar-stack-item bg-secondary" title="Và ${assignedInterns.length - 4} thực tập sinh khác">
              +${assignedInterns.length - 4}
            </span>
          ` : ''}
        </div>
        <span class="small fw-semibold text-secondary">(${assignedInterns.length} TTS)</span>
      </div>
    `;

    return `
      <tr>
        <td class="ps-4">
          <div class="fw-bold text-dark">${escapeHtml(shift.name)}</div>
          ${shift.notes ? `<div class="small text-muted fst-italic"><i class="bi bi-chat-text me-1"></i>${escapeHtml(shift.notes)}</div>` : ''}
        </td>
        <td>
          <span class="badge bg-light text-dark border fs-7 font-monospace px-2 py-1">
            <i class="bi bi-clock me-1 text-primary"></i>${shift.startTime} - ${shift.endTime}
          </span>
        </td>
        <td>${daysHtml}</td>
        <td>${avatarStackHtml}</td>
        <td class="text-end pe-4">
          <button type="button" class="btn btn-outline-danger btn-sm rounded-pill btn-delete-shift" data-shift-id="${shift.id}" title="Xóa ca này">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `;
  }).join("");

  // Bắt sự kiện xóa ca
  shiftTableBody.querySelectorAll(".btn-delete-shift").forEach(btn => {
    btn.addEventListener("click", () => {
      const shiftId = btn.getAttribute("data-shift-id");
      if (confirm(`Bạn có chắc chắn muốn xóa ca làm việc này không?`)) {
        shiftsList = shiftsList.filter(s => s.id !== shiftId);
        renderShiftsTable();
        showToast("Đã xóa ca làm việc thành công!", "warning");
      }
    });
  });
}

// ==========================================
// TIỆN ÍCH HIỂN THỊ TOAST THÔNG BÁO
// ==========================================
function showToast(message, type = "success") {
  if (!toastInstance) return;

  toastMessageEl.textContent = message;
  actionToastEl.classList.remove("bg-success", "bg-danger", "bg-warning", "bg-primary", "bg-info");

  if (type === "success") {
    actionToastEl.classList.add("bg-success");
    toastIconEl.className = "bi bi-check-circle-fill fs-5 me-2";
  } else if (type === "danger") {
    actionToastEl.classList.add("bg-danger");
    toastIconEl.className = "bi bi-exclamation-octagon-fill fs-5 me-2";
  } else if (type === "warning") {
    actionToastEl.classList.add("bg-warning", "text-dark");
    toastIconEl.className = "bi bi-exclamation-triangle-fill fs-5 me-2";
  } else {
    actionToastEl.classList.add("bg-primary");
    toastIconEl.className = "bi bi-info-circle-fill fs-5 me-2";
  }

  toastInstance.show();
}

function escapeHtml(string) {
  if (!string) return "";
  return String(string)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ==========================================
// BIND TẤT CẢ SỰ KIỆN GIAO DIỆN
// ==========================================
function bindEventListeners() {
  // Thay đổi input type="time"
  startTimeInput.addEventListener("input", calculateShiftDuration);
  endTimeInput.addEventListener("input", calculateShiftDuration);

  // Chọn nhanh ngày trong tuần
  btnSelectWeekdays.addEventListener("click", () => {
    setDaysSelection(["T2", "T3", "T4", "T5", "T6"]);
  });

  btnSelectWeekend.addEventListener("click", () => {
    setDaysSelection(["T7", "CN"]);
  });

  btnSelectAllDays.addEventListener("click", () => {
    setDaysSelection(["T2", "T3", "T4", "T5", "T6", "T7", "CN"]);
  });

  btnClearDays.addEventListener("click", () => {
    setDaysSelection([]);
  });

  dayCheckboxes.forEach(cb => {
    cb.addEventListener("change", () => {
      const selected = getSelectedDays();
      if (selected.length > 0) {
        dayErrorFeedback.classList.add("d-none");
      }
    });
  });

  // Chọn mẫu nhanh từ dropdown
  document.querySelectorAll(".quick-preset").forEach(btn => {
    btn.addEventListener("click", () => {
      shiftNameInput.value = btn.getAttribute("data-name");
      startTimeInput.value = btn.getAttribute("data-start");
      endTimeInput.value = btn.getAttribute("data-end");
      calculateShiftDuration();
      shiftNameInput.focus();
    });
  });

  // Sự kiện khi mở modal
  internModalEl.addEventListener("show.bs.modal", openInternModal);

  // Tìm kiếm và lọc trong modal
  modalSearchInput.addEventListener("input", renderModalInternList);
  modalDepartmentFilter.addEventListener("change", renderModalInternList);

  // Checkbox "Chọn tất cả" trong modal
  modalSelectAll.addEventListener("change", (e) => {
    const isChecked = e.target.checked;
    const filtered = getFilteredInterns();
    filtered.forEach(intern => {
      if (isChecked) {
        tempModalSelectedIds.add(intern.id);
      } else {
        tempModalSelectedIds.delete(intern.id);
      }
    });
    renderModalInternList();
  });

  // Nút bỏ chọn tất cả trong modal
  modalClearSelection.addEventListener("click", () => {
    tempModalSelectedIds.clear();
    renderModalInternList();
  });

  // Xác nhận chọn thực tập sinh từ modal
  modalBtnConfirm.addEventListener("click", () => {
    selectedInternIds = new Set(tempModalSelectedIds);
    renderSelectedInternTags();
    if (internModalInstance) {
      internModalInstance.hide();
    }
    showToast(`Đã áp dụng ${selectedInternIds.size} thực tập sinh cho ca làm việc!`, "success");
  });

  // Nút đặt lại form (Reset)
  btnResetForm.addEventListener("click", () => {
    if (confirm("Bạn có muốn đặt lại toàn bộ thông tin trong form không?")) {
      shiftForm.reset();
      shiftForm.classList.remove("was-validated");
      startTimeInput.value = "08:00";
      endTimeInput.value = "12:00";
      calculateShiftDuration();
      setDaysSelection(["T2", "T3", "T4", "T5", "T6"]);
      selectedInternIds.clear();
      renderSelectedInternTags();
      dayErrorFeedback.classList.add("d-none");
      internErrorFeedback.classList.add("d-none");
      timeErrorFeedback.classList.add("d-none");
    }
  });

  // SUBMIT FORM TẠO CA LÀM VIỆC
  shiftForm.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopPropagation();

    let isValid = true;

    // 1. Kiểm tra tên ca
    const nameVal = shiftNameInput.value.trim();
    if (!nameVal || nameVal.length < 3) {
      isValid = false;
      shiftNameInput.classList.add("is-invalid");
    } else {
      shiftNameInput.classList.remove("is-invalid");
    }

    // 2. Kiểm tra giờ
    if (startTimeInput.value === endTimeInput.value) {
      isValid = false;
      timeErrorFeedback.classList.remove("d-none");
    } else {
      timeErrorFeedback.classList.add("d-none");
    }

    // 3. Kiểm tra ngày trong tuần
    const selectedDays = getSelectedDays();
    if (selectedDays.length === 0) {
      isValid = false;
      dayErrorFeedback.classList.remove("d-none");
    } else {
      dayErrorFeedback.classList.add("d-none");
    }

    // 4. Kiểm tra chọn thực tập sinh
    if (selectedInternIds.size === 0) {
      isValid = false;
      internErrorFeedback.classList.remove("d-none");
    } else {
      internErrorFeedback.classList.add("d-none");
    }

    if (!isValid) {
      shiftForm.classList.add("was-validated");
      showToast("Vui lòng hoàn thành đầy đủ thông tin các mục bắt buộc!", "danger");
      return;
    }

    // Tạo đối tượng ca làm việc mới
    const newShift = {
      id: "SHIFT-" + Date.now().toString().slice(-4),
      name: nameVal,
      startTime: startTimeInput.value,
      endTime: endTimeInput.value,
      daysOfWeek: selectedDays,
      internIds: Array.from(selectedInternIds),
      notes: shiftNotes.value.trim()
    };

    // Thêm vào đầu danh sách
    shiftsList.unshift(newShift);
    renderShiftsTable();

    // Hiển thị thông báo
    showToast(`Tạo thành công ca làm việc: "${newShift.name}"!`, "success");

    // Cuộn nhẹ xuống bảng kết quả
    document.getElementById("shiftListSection").scrollIntoView({ behavior: "smooth" });

    // Reset các trường nhập
    shiftNameInput.value = "";
    shiftNotes.value = "";
    shiftForm.classList.remove("was-validated");
  });
}
