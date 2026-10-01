document.addEventListener('DOMContentLoaded', () => {
    // Form elements
    const form = document.getElementById('registrationForm');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const fullNameInput = document.getElementById('fullName');
    const birthDateInput = document.getElementById('birthDate');
    const phoneInput = document.getElementById('phone');
    const idNumberInput = document.getElementById('idNumber');
    const provinceSelect = document.getElementById('province');
    const addressInput = document.getElementById('detailedAddress');
    const positionSelect = document.getElementById('position');
    const educationSelect = document.getElementById('education');
    const experienceSelect = document.getElementById('experience');
    const startDateInput = document.getElementById('startDate');
    const termsCheck = document.getElementById('termsCheck');

    // Avatar preview
    const avatarUpload = document.getElementById('avatarUpload');
    const avatarPreview = document.getElementById('avatarPreview');
    const avatarError = document.getElementById('avatarError');

    // File dropzone elements
    const dropZone = document.getElementById('dropZone');
    const cvFileInput = document.getElementById('cvFile');
    const dropzoneContent = document.getElementById('dropzoneContent');
    const fileSelectedBadge = document.getElementById('fileSelectedBadge');
    const selectedFileName = document.getElementById('selectedFileName');
    const selectedFileSize = document.getElementById('selectedFileSize');
    const btnRemoveFile = document.getElementById('btnRemoveFile');
    const cvFileError = document.getElementById('cvFileError');

    // Password strength
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');

    // Success Modal
    const successModal = document.getElementById('successModal');
    const modalSummary = document.getElementById('modalSummary');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const btnReset = document.getElementById('btnReset');

    /* ==========================================================================
       1. Toggle Password Visibility
       ========================================================================== */
    document.querySelectorAll('.btn-toggle-pwd').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);
            const icon = btn.querySelector('i');

            if (targetInput.type === 'password') {
                targetInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                targetInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    /* ==========================================================================
       2. Real-time Password Strength Checking
       ========================================================================== */
    passwordInput.addEventListener('input', () => {
        const val = passwordInput.value;
        let score = 0;

        if (val.length >= 8) score++;
        if (/[A-Z]/.test(val)) score++;
        if (/[0-9]/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;

        if (val.length === 0) {
            strengthFill.style.width = '0%';
            strengthFill.style.backgroundColor = '#e2e8f0';
            strengthText.textContent = 'Độ mạnh mật khẩu';
            strengthText.style.color = 'var(--text-muted)';
        } else if (score <= 1) {
            strengthFill.style.width = '25%';
            strengthFill.style.backgroundColor = '#ef4444';
            strengthText.textContent = 'Mật khẩu yếu';
            strengthText.style.color = '#ef4444';
        } else if (score === 2) {
            strengthFill.style.width = '50%';
            strengthFill.style.backgroundColor = '#f59e0b';
            strengthText.textContent = 'Mật khẩu trung bình';
            strengthText.style.color = '#f59e0b';
        } else if (score === 3) {
            strengthFill.style.width = '75%';
            strengthFill.style.backgroundColor = '#3b82f6';
            strengthText.textContent = 'Mật khẩu khá';
            strengthText.style.color = '#3b82f6';
        } else {
            strengthFill.style.width = '100%';
            strengthFill.style.backgroundColor = '#10b981';
            strengthText.textContent = 'Mật khẩu rất mạnh';
            strengthText.style.color = '#10b981';
        }

        if (confirmPasswordInput.value.length > 0) {
            checkPasswordMatch();
        }
    });

    confirmPasswordInput.addEventListener('input', checkPasswordMatch);

    function checkPasswordMatch() {
        if (confirmPasswordInput.value !== passwordInput.value) {
            showError('confirmPassword', 'Mật khẩu xác nhận không trùng khớp.');
            return false;
        } else {
            clearError('confirmPassword');
            return true;
        }
    }

    /* ==========================================================================
       3. Avatar Preview Handler
       ========================================================================== */
    avatarUpload.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;

        // Check file size (max 2MB)
        if (file.size > 2 * 1024 * 1024) {
            showError('avatar', 'Dung lượng ảnh không được vượt quá 2MB.');
            this.value = '';
            return;
        }

        clearError('avatar');
        const reader = new FileReader();
        reader.onload = (e) => {
            avatarPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });

    /* ==========================================================================
       4. File Dropzone & CV Upload Handler
       ========================================================================== */
    // Open file dialog when clicking dropzone
    dropZone.addEventListener('click', (e) => {
        if (!e.target.closest('#btnRemoveFile')) {
            cvFileInput.click();
        }
    });

    // Drag & Drop effects
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleCVFile(files[0]);
        }
    });

    cvFileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            handleCVFile(this.files[0]);
        }
    });

    function handleCVFile(file) {
        const validExtensions = ['.pdf', '.doc', '.docx'];
        const fileName = file.name.toLowerCase();
        const isValidExt = validExtensions.some(ext => fileName.endsWith(ext));

        if (!isValidExt) {
            showError('cvFile', 'Định dạng file không hợp lệ! Vui lòng chọn .pdf, .doc hoặc .docx');
            cvFileInput.value = '';
            return;
        }

        // Check size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('cvFile', 'Dung lượng file vượt quá giới hạn 10MB.');
            cvFileInput.value = '';
            return;
        }

        clearError('cvFile');

        // Ensure cvFileInput.files has the file (especially if dropped)
        try {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            cvFileInput.files = dataTransfer.files;
        } catch (err) {
            console.warn('DataTransfer sync warning:', err);
        }

        // Update UI
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        
        // Update icon based on file type
        const icon = fileSelectedBadge.querySelector('.file-type-icon');
        if (fileName.endsWith('.pdf')) {
            icon.className = 'fa-solid fa-file-pdf file-type-icon';
            icon.style.color = '#ef4444';
        } else {
            icon.className = 'fa-solid fa-file-word file-type-icon';
            icon.style.color = '#2563eb';
        }

        dropzoneContent.classList.add('d-none');
        fileSelectedBadge.classList.remove('d-none');
    }

    btnRemoveFile.addEventListener('click', (e) => {
        e.stopPropagation();
        cvFileInput.value = '';
        dropzoneContent.classList.remove('d-none');
        fileSelectedBadge.classList.add('d-none');
    });

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /* ==========================================================================
       5. Form Validation Helpers
       ========================================================================== */
    function showError(fieldId, message) {
        const errorEl = document.getElementById(`${fieldId}Error`);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('visible');
        }
        const fieldEl = document.getElementById(fieldId);
        if (fieldEl) {
            const formGroup = fieldEl.closest('.form-group') || fieldEl.closest('.avatar-upload-box') || fieldEl.closest('.file-dropzone');
            if (formGroup) formGroup.classList.add('has-error');
        }
    }

    function clearError(fieldId) {
        const errorEl = document.getElementById(`${fieldId}Error`);
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.remove('visible');
        }
        const fieldEl = document.getElementById(fieldId);
        if (fieldEl) {
            const formGroup = fieldEl.closest('.form-group') || fieldEl.closest('.avatar-upload-box') || fieldEl.closest('.file-dropzone');
            if (formGroup) formGroup.classList.remove('has-error');
        }
    }

    // Auto clear error when user types or changes input
    const inputsToWatch = [
        usernameInput, emailInput, passwordInput, confirmPasswordInput,
        fullNameInput, birthDateInput, phoneInput, idNumberInput,
        provinceSelect, addressInput, positionSelect, educationSelect,
        experienceSelect, startDateInput, termsCheck
    ];

    inputsToWatch.forEach(input => {
        if (!input) return;
        ['input', 'change'].forEach(evt => {
            input.addEventListener(evt, () => {
                clearError(input.id);
            });
        });
    });

    /* ==========================================================================
       6. Main Validation & Submit Handler
       ========================================================================== */
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        let isValid = true;
        let firstInvalidElement = null;

        function markInvalid(element, fieldId, message) {
            showError(fieldId, message);
            if (!firstInvalidElement) {
                firstInvalidElement = element;
            }
            isValid = false;
        }

        // 1. Tên đăng nhập
        const usernameVal = usernameInput.value.trim();
        if (!usernameVal) {
            markInvalid(usernameInput, 'username', 'Vui lòng nhập tên đăng nhập.');
        } else if (usernameVal.length < 4) {
            markInvalid(usernameInput, 'username', 'Tên đăng nhập phải có ít nhất 4 ký tự.');
        } else if (!/^[a-zA-Z0-9_]+$/.test(usernameVal)) {
            markInvalid(usernameInput, 'username', 'Tên đăng nhập chỉ chứa chữ cái, số và dấu gạch dưới (_).');
        }

        // 2. Email
        const emailVal = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailVal) {
            markInvalid(emailInput, 'email', 'Vui lòng nhập địa chỉ email.');
        } else if (!emailRegex.test(emailVal)) {
            markInvalid(emailInput, 'email', 'Địa chỉ email không đúng định dạng.');
        }

        // 3. Mật khẩu
        const pwdVal = passwordInput.value;
        if (!pwdVal) {
            markInvalid(passwordInput, 'password', 'Vui lòng nhập mật khẩu.');
        } else if (pwdVal.length < 8) {
            markInvalid(passwordInput, 'password', 'Mật khẩu phải chứa ít nhất 8 ký tự.');
        }

        // 4. Xác nhận mật khẩu
        if (!confirmPasswordInput.value) {
            markInvalid(confirmPasswordInput, 'confirmPassword', 'Vui lòng nhập lại mật khẩu.');
        } else if (confirmPasswordInput.value !== pwdVal) {
            markInvalid(confirmPasswordInput, 'confirmPassword', 'Mật khẩu xác nhận không trùng khớp.');
        }

        // 5. Họ tên
        if (!fullNameInput.value.trim()) {
            markInvalid(fullNameInput, 'fullName', 'Vui lòng nhập họ và tên của bạn.');
        }

        // 6. Ngày sinh
        if (!birthDateInput.value) {
            markInvalid(birthDateInput, 'birthDate', 'Vui lòng chọn ngày sinh.');
        } else {
            const birthYear = new Date(birthDateInput.value).getFullYear();
            const currentYear = new Date().getFullYear();
            if (currentYear - birthYear < 16) {
                markInvalid(birthDateInput, 'birthDate', 'Ứng viên phải từ đủ 16 tuổi trở lên.');
            }
        }

        // 7. Số điện thoại (Việt Nam)
        const phoneVal = phoneInput.value.trim();
        const phoneRegex = /^(0|\+84)(3[2-9]|5[6|8|9]|7[0|6-9]|8[1-5|8|9]|9[0-4|6-9])[0-9]{7}$/;
        if (!phoneVal) {
            markInvalid(phoneInput, 'phone', 'Vui lòng nhập số điện thoại liên hệ.');
        } else if (!phoneRegex.test(phoneVal)) {
            markInvalid(phoneInput, 'phone', 'Số điện thoại không hợp lệ (vd: 0912345678).');
        }

        // 8. CCCD / CMND
        const idVal = idNumberInput.value.trim();
        if (!idVal) {
            markInvalid(idNumberInput, 'idNumber', 'Vui lòng nhập số CCCD/CMND.');
        } else if (!/^\d{9}$|^\d{12}$/.test(idVal)) {
            markInvalid(idNumberInput, 'idNumber', 'Số CCCD/CMND phải gồm 9 hoặc 12 chữ số.');
        }

        // 9. Tỉnh thành
        if (!provinceSelect.value) {
            markInvalid(provinceSelect, 'province', 'Vui lòng chọn Tỉnh/Thành phố sinh sống.');
        }

        // 10. Địa chỉ chi tiết
        if (!addressInput.value.trim()) {
            markInvalid(addressInput, 'detailedAddress', 'Vui lòng cung cấp địa chỉ chi tiết.');
        }

        // 11. Vị trí ứng tuyển
        if (!positionSelect.value) {
            markInvalid(positionSelect, 'position', 'Vui lòng chọn vị trí muốn ứng tuyển.');
        }

        // 12. Trình độ học vấn
        if (!educationSelect.value) {
            markInvalid(educationSelect, 'education', 'Vui lòng chọn trình độ học vấn cao nhất.');
        }

        // 13. Kinh nghiệm làm việc
        if (!experienceSelect.value) {
            markInvalid(experienceSelect, 'experience', 'Vui lòng chọn số năm kinh nghiệm.');
        }

        // 14. Ngày bắt đầu làm việc
        if (!startDateInput.value) {
            markInvalid(startDateInput, 'startDate', 'Vui lòng chọn ngày có thể bắt đầu làm việc.');
        }

        // 15. Tải lên CV
        if (!cvFileInput.files || cvFileInput.files.length === 0) {
            markInvalid(dropZone, 'cvFile', 'Vui lòng đính kèm file hồ sơ (CV).');
        }

        // 16. Đồng ý điều khoản
        if (!termsCheck.checked) {
            markInvalid(termsCheck, 'termsCheck', 'Bạn cần đọc và đồng ý với điều khoản & cam kết trước khi nộp.');
        }

        // Xử lý khi có lỗi hoặc thành công
        if (!isValid) {
            if (firstInvalidElement) {
                firstInvalidElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                if (firstInvalidElement.focus) firstInvalidElement.focus();
            }
            return;
        }

        // Hiển thị Popup Modal thành công
        const genderVal = document.querySelector('input[name="gender"]:checked')?.parentElement?.textContent?.trim() || 'Nam';
        const fileName = cvFileInput.files[0]?.name || 'Chưa đính kèm';

        modalSummary.innerHTML = `
            <div class="modal-summary-item">
                <span class="modal-summary-label">Tài khoản:</span>
                <span class="modal-summary-value">${escapeHtml(usernameVal)}</span>
            </div>
            <div class="modal-summary-item">
                <span class="modal-summary-label">Ứng viên:</span>
                <span class="modal-summary-value">${escapeHtml(fullNameInput.value.trim())} (${genderVal})</span>
            </div>
            <div class="modal-summary-item">
                <span class="modal-summary-label">Email &amp; SĐT:</span>
                <span class="modal-summary-value">${escapeHtml(emailVal)} | ${escapeHtml(phoneVal)}</span>
            </div>
            <div class="modal-summary-item">
                <span class="modal-summary-label">Vị trí ứng tuyển:</span>
                <span class="modal-summary-value">${escapeHtml(positionSelect.value)}</span>
            </div>
            <div class="modal-summary-item">
                <span class="modal-summary-label">Tệp CV đính kèm:</span>
                <span class="modal-summary-value" style="color: #2563eb;">${escapeHtml(fileName)}</span>
            </div>
        `;

        successModal.classList.remove('d-none');
    });

    // Set date bounds
    const today = new Date().toISOString().split('T')[0];
    if (birthDateInput) birthDateInput.max = today;
    if (startDateInput) startDateInput.min = today;

    // Close Modal when clicking outside modal card
    successModal.addEventListener('click', (e) => {
        if (e.target === successModal) {
            closeSuccessModal();
        }
    });

    // Close Modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !successModal.classList.contains('d-none')) {
            closeSuccessModal();
        }
    });

    function closeSuccessModal() {
        successModal.classList.add('d-none');
        form.reset();
        // Reset preview states
        dropzoneContent.classList.remove('d-none');
        fileSelectedBadge.classList.add('d-none');
        avatarPreview.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='150' viewBox='0 0 120 150'%3E%3Crect width='100%25' height='100%25' fill='%23f1f5f9'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2394a3b8' font-family='sans-serif' font-size='13'%3E%E1%BA%A2nh 3x4%3C/text%3E%3C/svg%3E";
        strengthFill.style.width = '0%';
        strengthText.textContent = 'Độ mạnh mật khẩu';
        strengthText.style.color = 'var(--text-muted)';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Close Modal Button
    modalCloseBtn.addEventListener('click', closeSuccessModal);

    // Form Reset Handler
    btnReset.addEventListener('click', () => {
        // Clear all visible errors
        document.querySelectorAll('.error-msg').forEach(el => el.classList.remove('visible'));
        document.querySelectorAll('.has-error').forEach(el => el.classList.remove('has-error'));
        dropzoneContent.classList.remove('d-none');
        fileSelectedBadge.classList.add('d-none');
        avatarPreview.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='150' viewBox='0 0 120 150'%3E%3Crect width='100%25' height='100%25' fill='%23f1f5f9'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2394a3b8' font-family='sans-serif' font-size='13'%3E%E1%BA%A2nh 3x4%3C/text%3E%3C/svg%3E";
        strengthFill.style.width = '0%';
        strengthText.textContent = 'Độ mạnh mật khẩu';
        strengthText.style.color = 'var(--text-muted)';
    });

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
