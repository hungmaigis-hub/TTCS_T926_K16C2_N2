/**
 * JAVASCRIPT LOGIC: HỆ THỐNG TẢI LÊN & QUẢN LÝ HỢP ĐỒNG
 * Xử lý: Format tiền tệ, đọc số thành chữ tiếng Việt, kéo thả upload file,
 * validation form, lưu nháp LocalStorage và modal kết quả.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('contractUploadForm');
    const contractNumberInput = document.getElementById('contractNumber');
    const signingDateInput = document.getElementById('signingDate');
    const contractTypeSelect = document.getElementById('contractType');
    const employeeNameInput = document.getElementById('employeeName');
    const effectiveDateInput = document.getElementById('effectiveDate');
    const expirationDateInput = document.getElementById('expirationDate');
    
    // Salary & Allowance
    const baseSalaryInput = document.getElementById('baseSalary');
    const baseSalaryWords = document.getElementById('baseSalaryWords');
    const allowanceAmountInput = document.getElementById('allowanceAmount');
    const allowanceWords = document.getElementById('allowanceWords');
    const quickChips = document.querySelectorAll('.chip-item');

    // File Upload Elements
    const dropZone = document.getElementById('dropZone');
    const contractFileInput = document.getElementById('contractFileInput');
    const filePreviewCard = document.getElementById('filePreviewCard');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const previewFileType = document.getElementById('previewFileType');
    const previewFileIcon = document.getElementById('previewFileIcon');
    const btnRemoveFile = document.getElementById('btnRemoveFile');
    const uploadProgressContainer = document.getElementById('uploadProgressContainer');
    const progressBarFill = document.getElementById('progressBarFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressStatusText = document.getElementById('progressStatusText');

    // Action buttons & helpers
    const btnGenContractNum = document.getElementById('btnGenContractNum');
    const btnToday = document.getElementById('btnToday');
    const btnSaveDraft = document.getElementById('btnSaveDraft');
    const btnResetForm = document.getElementById('btnResetForm');
    const btnHelp = document.getElementById('btnHelp');

    // Modal elements
    const successModal = document.getElementById('successModal');
    const btnCloseModal = document.getElementById('btnCloseModal');
    const btnPrintReceipt = document.getElementById('btnPrintReceipt');

    let currentSelectedFile = null;

    // ==========================================
    // 1. TIỆN ÍCH FORMAT TIỀN TỆ & ĐỌC SỐ THÀNH CHỮ
    // ==========================================

    /**
     * Định dạng số có dấu chấm phân cách hàng nghìn (VD: 2500000 -> 2.500.000)
     */
    function formatCurrencyNumber(value) {
        if (!value) return '';
        // Loại bỏ mọi ký tự không phải số
        const numeric = value.toString().replace(/\D/g, '');
        if (!numeric) return '';
        return new Intl.NumberFormat('vi-VN').format(numeric);
    }

    /**
     * Lấy giá trị số nguyên từ chuỗi format (VD: "2.500.000" -> 2500000)
     */
    function getNumericValue(formattedString) {
        if (!formattedString) return 0;
        return parseInt(formattedString.replace(/\D/g, ''), 10) || 0;
    }

    /**
     * Thuật toán đọc số tiền tiếng Việt chuẩn
     */
    function readVietnameseCurrency(n) {
        if (!n || n <= 0) return 'Chưa nhập';
        
        const units = ['', 'nghìn', 'triệu', 'tỷ', 'nghìn tỷ', 'triệu tỷ'];
        const digits = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín'];

        function readGroupThree(group, isFirst) {
            let str = '';
            const h = Math.floor(group / 100);
            const t = Math.floor((group % 100) / 10);
            const u = group % 10;

            if (h > 0 || !isFirst) {
                str += digits[h] + ' trăm ';
            }

            if (t > 1) {
                str += digits[t] + ' mươi ';
                if (u === 1) str += 'mốt ';
                else if (u === 5) str += 'lăm ';
                else if (u > 0) str += digits[u] + ' ';
            } else if (t === 1) {
                str += 'mười ';
                if (u === 5) str += 'lăm ';
                else if (u > 0) str += digits[u] + ' ';
            } else {
                if (u > 0) {
                    if (h > 0 || !isFirst) str += 'lẻ ' + digits[u] + ' ';
                    else str += digits[u] + ' ';
                }
            }
            return str;
        }

        let numStr = n.toString();
        let groups = [];
        while (numStr.length > 0) {
            groups.unshift(parseInt(numStr.slice(-3), 10));
            numStr = numStr.slice(0, -3);
        }

        let result = '';
        for (let i = 0; i < groups.length; i++) {
            const groupVal = groups[i];
            const unitIdx = groups.length - 1 - i;
            if (groupVal > 0) {
                const groupText = readGroupThree(groupVal, i === 0);
                result += groupText + units[unitIdx] + ' ';
            }
        }

        result = result.trim();
        if (!result) return 'Không đồng';

        // Viết hoa chữ cái đầu và thêm từ 'đồng'
        result = result.charAt(0).toUpperCase() + result.slice(1) + ' đồng';
        return result;
    }

    // Sự kiện nhập liệu Phụ Cấp (Bắt buộc theo yêu cầu)
    allowanceAmountInput.addEventListener('input', (e) => {
        const raw = e.target.value;
        const formatted = formatCurrencyNumber(raw);
        e.target.value = formatted;
        
        const numVal = getNumericValue(formatted);
        if (numVal > 0) {
            allowanceWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: ${readVietnameseCurrency(numVal)}</em>`;
            clearFieldError(allowanceAmountInput, 'allowanceError');
        } else {
            allowanceWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: Chưa nhập</em>`;
        }
    });

    // Sự kiện nhập liệu Lương Cơ Bản
    baseSalaryInput.addEventListener('input', (e) => {
        const raw = e.target.value;
        const formatted = formatCurrencyNumber(raw);
        e.target.value = formatted;
        
        const numVal = getNumericValue(formatted);
        if (numVal > 0) {
            baseSalaryWords.style.display = 'inline-flex';
            baseSalaryWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: ${readVietnameseCurrency(numVal)}</em>`;
        } else {
            baseSalaryWords.style.display = 'none';
        }
    });

    // Chọn nhanh phụ cấp từ chip
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const amount = chip.getAttribute('data-amount');
            const formatted = formatCurrencyNumber(amount);
            allowanceAmountInput.value = formatted;
            const numVal = parseInt(amount, 10);
            allowanceWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: ${readVietnameseCurrency(numVal)}</em>`;
            clearFieldError(allowanceAmountInput, 'allowanceError');
            showToast(`Đã chọn mức phụ cấp: ${formatted} VNĐ`, 'info');
        });
    });

    // ==========================================
    // 2. GỢI Ý MÃ HỢP ĐỒNG & CHỌN NGÀY HÔM NAY
    // ==========================================
    btnGenContractNum.addEventListener('click', () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const randNum = Math.floor(1000 + Math.random() * 9000);
        const generatedCode = `HDLD-${year}/${month}/VN-${randNum}`;
        contractNumberInput.value = generatedCode;
        clearFieldError(contractNumberInput, 'contractNumberError');
        showToast(`Đã sinh số hợp đồng gợi ý: ${generatedCode}`, 'success');
    });

    btnToday.addEventListener('click', () => {
        const today = new Date().toISOString().split('T')[0];
        signingDateInput.value = today;
        clearFieldError(signingDateInput, 'signingDateError');
        showToast(`Đã đặt ngày ký là hôm nay (${today})`, 'info');
    });

    // ==========================================
    // 3. XỬ LÝ KÉO THẢ & UPLOAD FILE HỢP ĐỒNG
    // ==========================================

    // Mở file browser khi nhấp vào vùng dropzone
    dropZone.addEventListener('click', () => {
        contractFileInput.click();
    });

    // Hỗ trợ phím Enter / Space khi focus dropzone
    dropZone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            contractFileInput.click();
        }
    });

    // Kéo thả events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        }, false);
    });

    // Khi người dùng thả file
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleSelectedFile(files[0]);
        }
    });

    // Khi người dùng chọn file qua input
    contractFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    /**
     * Kiểm tra định dạng và hiển thị tệp hợp đồng
     */
    function handleSelectedFile(file) {
        const allowedExtensions = ['.pdf', '.doc', '.docx'];
        const fileName = file.name.toLowerCase();
        const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));

        if (!isValidExtension) {
            showFieldError('contractFileError', 'Định dạng tệp không hợp lệ! Vui lòng chỉ tải lên tệp .PDF, .DOC hoặc .DOCX');
            showToast('Chỉ chấp nhận tệp định dạng PDF hoặc DOC/DOCX!', 'danger');
            return;
        }

        const maxSizeBytes = 25 * 1024 * 1024; // 25MB
        if (file.size > maxSizeBytes) {
            showFieldError('contractFileError', 'Dung lượng tệp vượt quá giới hạn 25MB!');
            showToast('Tệp quá lớn! Vui lòng chọn tệp nhỏ hơn 25MB', 'danger');
            return;
        }

        currentSelectedFile = file;
        clearFieldError(null, 'contractFileError');

        // Hiển thị thông tin tệp
        previewFileName.textContent = file.name;
        previewFileSize.textContent = formatFileSize(file.size);

        if (fileName.endsWith('.pdf')) {
            previewFileType.textContent = 'Tài liệu PDF';
            previewFileIcon.className = 'preview-icon';
            previewFileIcon.innerHTML = '<i class="fa-solid fa-file-pdf"></i>';
        } else {
            previewFileType.textContent = 'Văn bản Microsoft Word';
            previewFileIcon.className = 'preview-icon doc-icon';
            previewFileIcon.innerHTML = '<i class="fa-solid fa-file-word"></i>';
        }

        dropZone.style.display = 'none';
        filePreviewCard.style.display = 'flex';

        showToast(`Đã đính kèm tệp: ${file.name}`, 'success');
    }

    // Xóa tệp đã chọn
    btnRemoveFile.addEventListener('click', () => {
        currentSelectedFile = null;
        contractFileInput.value = '';
        filePreviewCard.style.display = 'none';
        dropZone.style.display = 'block';
        showToast('Đã hủy đính kèm tệp hợp đồng', 'warning');
    });

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // ==========================================
    // 4. VALIDATION FORM & SUBMIT
    // ==========================================

    function showFieldError(errorElementId, message) {
        const errorEl = document.getElementById(errorElementId);
        if (errorEl) {
            errorEl.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${message}`;
            errorEl.classList.add('show');
        }
    }

    function clearFieldError(inputEl, errorElementId) {
        if (inputEl) {
            inputEl.classList.remove('is-invalid');
        }
        const errorEl = document.getElementById(errorElementId);
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.remove('show');
        }
    }

    // Gắn sự kiện xóa lỗi khi người dùng thay đổi dữ liệu
    contractNumberInput.addEventListener('input', () => clearFieldError(contractNumberInput, 'contractNumberError'));
    signingDateInput.addEventListener('change', () => clearFieldError(signingDateInput, 'signingDateError'));
    contractTypeSelect.addEventListener('change', () => clearFieldError(contractTypeSelect, 'contractTypeError'));
    employeeNameInput.addEventListener('input', () => clearFieldError(employeeNameInput, 'employeeNameError'));

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        let isValid = true;
        let firstInvalidInput = null;

        // 1. Kiểm tra Số Hợp Đồng (Bắt buộc)
        const contractNum = contractNumberInput.value.trim();
        if (!contractNum) {
            showFieldError('contractNumberError', 'Vui lòng nhập số hợp đồng');
            contractNumberInput.classList.add('is-invalid');
            if (!firstInvalidInput) firstInvalidInput = contractNumberInput;
            isValid = false;
        } else if (contractNum.length < 3) {
            showFieldError('contractNumberError', 'Số hợp đồng phải có ít nhất 3 ký tự');
            contractNumberInput.classList.add('is-invalid');
            if (!firstInvalidInput) firstInvalidInput = contractNumberInput;
            isValid = false;
        }

        // 2. Kiểm tra Ngày Ký (Bắt buộc)
        const signingDate = signingDateInput.value;
        if (!signingDate) {
            showFieldError('signingDateError', 'Vui lòng chọn ngày ký kết hợp đồng');
            signingDateInput.classList.add('is-invalid');
            if (!firstInvalidInput) firstInvalidInput = signingDateInput;
            isValid = false;
        }

        // 3. Kiểm tra Họ Tên Người Lao Động / Đối Tác
        const employeeName = employeeNameInput.value.trim();
        if (!employeeName) {
            showFieldError('employeeNameError', 'Vui lòng nhập tên người lao động hoặc đối tác');
            employeeNameInput.classList.add('is-invalid');
            if (!firstInvalidInput) firstInvalidInput = employeeNameInput;
            isValid = false;
        }

        // 4. Kiểm tra Loại Hợp Đồng
        if (!contractTypeSelect.value) {
            showFieldError('contractTypeError', 'Vui lòng chọn phân loại hợp đồng');
            contractTypeSelect.classList.add('is-invalid');
            if (!firstInvalidInput) firstInvalidInput = contractTypeSelect;
            isValid = false;
        }

        // 5. Kiểm tra logic ngày tháng (Ngày hết hạn >= Ngày hiệu lực)
        if (effectiveDateInput.value && expirationDateInput.value) {
            if (new Date(expirationDateInput.value) < new Date(effectiveDateInput.value)) {
                showToast('Ngày hết hạn không được trước ngày có hiệu lực!', 'danger');
                expirationDateInput.classList.add('is-invalid');
                if (!firstInvalidInput) firstInvalidInput = expirationDateInput;
                isValid = false;
            }
        }

        // 6. Kiểm tra Ô Phụ Cấp (Bắt buộc theo yêu cầu)
        const allowanceVal = getNumericValue(allowanceAmountInput.value);
        if (!allowanceVal || allowanceVal <= 0) {
            showFieldError('allowanceError', 'Vui lòng nhập mức phụ cấp hàng tháng hợp lệ (> 0 VNĐ)');
            allowanceAmountInput.classList.add('is-invalid');
            if (!firstInvalidInput) firstInvalidInput = allowanceAmountInput;
            isValid = false;
        }

        // 7. Kiểm tra Tệp Đính Kèm Hợp Đồng
        if (!currentSelectedFile) {
            showFieldError('contractFileError', 'Vui lòng tải lên tệp tin hợp đồng (.PDF hoặc .DOCX)');
            if (!firstInvalidInput) firstInvalidInput = dropZone;
            isValid = false;
        }

        // 8. Cam kết điều khoản
        const agreeTerms = document.getElementById('agreeTerms');
        if (!agreeTerms.checked) {
            showFieldError('agreeTermsError', 'Bạn cần tích chọn xác nhận cam kết trước khi tải lên.');
            isValid = false;
        } else {
            clearFieldError(null, 'agreeTermsError');
        }

        if (!isValid) {
            if (firstInvalidInput && typeof firstInvalidInput.focus === 'function') {
                firstInvalidInput.focus();
            }
            showToast('Vui lòng kiểm tra lại các trường thông tin còn thiếu hoặc chưa hợp lệ!', 'danger');
            return;
        }

        // Nếu hợp lệ: Mô phỏng quá trình Upload tệp lên hệ thống
        simulateUploadProcess();
    });

    /**
     * Giả lập tiến trình Upload lên Server và hiển thị kết quả
     */
    function simulateUploadProcess() {
        const submitBtn = document.getElementById('btnSubmit');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tải lên...';
        
        uploadProgressContainer.style.display = 'block';
        let progress = 0;

        const interval = setInterval(() => {
            progress += 15;
            if (progress > 100) progress = 100;

            progressBarFill.style.width = progress + '%';
            progressPercent.textContent = progress + '%';

            if (progress === 100) {
                clearInterval(interval);
                progressStatusText.textContent = 'Xác thực hồ sơ & lưu vào cơ sở dữ liệu...';

                setTimeout(() => {
                    uploadProgressContainer.style.display = 'none';
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Tải Lên Hợp Đồng';

                    // Điền dữ liệu vào modal xác nhận
                    populateAndOpenModal();
                    // Xóa bản nháp sau khi nộp thành công
                    localStorage.removeItem('hr_contract_draft');
                }, 700);
            }
        }, 120);
    }

    /**
     * Mở modal hiển thị tóm tắt thông tin hợp đồng vừa upload
     */
    function populateAndOpenModal() {
        document.getElementById('resContractNumber').textContent = contractNumberInput.value.trim();
        document.getElementById('resSigningDate').textContent = formatDateDisplay(signingDateInput.value);
        document.getElementById('resEmployeeName').textContent = employeeNameInput.value.trim();
        document.getElementById('resContractType').textContent = contractTypeSelect.options[contractTypeSelect.selectedIndex].text;
        document.getElementById('resAllowanceAmount').textContent = allowanceAmountInput.value + ' VNĐ / tháng';

        // Lấy danh sách các loại phụ cấp đã chọn
        const selectedTypes = [];
        document.querySelectorAll('input[name="allowanceTypes"]:checked').forEach(cb => {
            selectedTypes.push(cb.value);
        });
        document.getElementById('resAllowanceTypes').textContent = selectedTypes.length > 0 ? selectedTypes.join(', ') : 'Không chỉ định';

        document.getElementById('resFileName').textContent = currentSelectedFile ? currentSelectedFile.name : 'N/A';

        // Mở modal
        successModal.style.display = 'flex';
        showToast('Tải hợp đồng lên hệ thống thành công!', 'success');
    }

    function formatDateDisplay(dateStr) {
        if (!dateStr) return 'N/A';
        const parts = dateStr.split('-');
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}/${parts[0]}`; // DD/MM/YYYY
        }
        return dateStr;
    }

    // Đóng Modal
    btnCloseModal.addEventListener('click', () => {
        successModal.style.display = 'none';
        form.reset();
        currentSelectedFile = null;
        filePreviewCard.style.display = 'none';
        dropZone.style.display = 'block';
        allowanceWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: Chưa nhập</em>`;
        baseSalaryWords.style.display = 'none';
    });

    // In biên nhận
    btnPrintReceipt.addEventListener('click', () => {
        window.print();
    });

    // ==========================================
    // 5. LƯU & KHÔI PHỤC BẢN NHÁP (LOCALSTORAGE)
    // ==========================================
    btnSaveDraft.addEventListener('click', () => {
        const draftData = {
            contractNumber: contractNumberInput.value,
            signingDate: signingDateInput.value,
            contractType: contractTypeSelect.value,
            employeeName: employeeNameInput.value,
            effectiveDate: effectiveDateInput.value,
            expirationDate: expirationDateInput.value,
            baseSalary: baseSalaryInput.value,
            allowanceAmount: allowanceAmountInput.value,
            notes: document.getElementById('contractNotes').value,
            timestamp: new Date().toISOString()
        };

        localStorage.setItem('hr_contract_draft', JSON.stringify(draftData));
        showToast('Đã lưu bản nháp vào trình duyệt thành công!', 'success');
    });

    // Khôi phục bản nháp nếu có
    const savedDraft = localStorage.getItem('hr_contract_draft');
    if (savedDraft) {
        try {
            const data = JSON.parse(savedDraft);
            if (data.contractNumber || data.allowanceAmount) {
                contractNumberInput.value = data.contractNumber || '';
                signingDateInput.value = data.signingDate || '';
                contractTypeSelect.value = data.contractType || '';
                employeeNameInput.value = data.employeeName || '';
                effectiveDateInput.value = data.effectiveDate || '';
                expirationDateInput.value = data.expirationDate || '';
                baseSalaryInput.value = data.baseSalary || '';
                allowanceAmountInput.value = data.allowanceAmount || '';
                if (data.notes) document.getElementById('contractNotes').value = data.notes;

                if (data.allowanceAmount) {
                    const numVal = getNumericValue(data.allowanceAmount);
                    if (numVal > 0) {
                        allowanceWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: ${readVietnameseCurrency(numVal)}</em>`;
                    }
                }
                showToast('Đã tự động tải lại bản nháp chưa nộp từ phiên trước.', 'info');
            }
        } catch (e) {
            console.error('Lỗi khi đọc draft:', e);
        }
    }

    // Reset Form
    btnResetForm.addEventListener('click', () => {
        setTimeout(() => {
            currentSelectedFile = null;
            filePreviewCard.style.display = 'none';
            dropZone.style.display = 'block';
            allowanceWords.innerHTML = `<i class="fa-solid fa-spell-check"></i> <em>Bằng chữ: Chưa nhập</em>`;
            baseSalaryWords.style.display = 'none';
            document.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));
            document.querySelectorAll('.form-feedback').forEach(el => {
                el.textContent = '';
                el.classList.remove('show');
            });
            showToast('Đã làm mới lại toàn bộ biểu mẫu', 'info');
        }, 10);
    });

    // Trợ giúp
    btnHelp.addEventListener('click', () => {
        alert(
            "HƯỚNG DẪN TẢI HỢP ĐỒNG LÊN HỆ THỐNG:\n\n" +
            "1. Nhập Số hợp đồng theo quy định nội bộ (hoặc bấm 'Gợi ý' để tạo mã mẫu).\n" +
            "2. Chọn Ngày ký kết hợp đồng (hoặc bấm 'Hôm nay').\n" +
            "3. Nhập Mức phụ cấp hàng tháng: Hệ thống sẽ tự định dạng tiền tệ và đọc thành chữ tiếng Việt.\n" +
            "4. Tải lên tệp hợp đồng: Hỗ trợ kéo & thả tệp .PDF, .DOCX dung lượng tối đa 25MB.\n" +
            "5. Bấm 'Tải Lên Hợp Đồng' để gửi dữ liệu lên hệ thống."
        );
    });

    // ==========================================
    // 6. TOAST NOTIFICATION UTILITY
    // ==========================================
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        let iconClass = 'fa-solid fa-circle-info';
        if (type === 'success') iconClass = 'fa-solid fa-circle-check';
        if (type === 'danger') iconClass = 'fa-solid fa-circle-exclamation';
        if (type === 'warning') iconClass = 'fa-solid fa-triangle-exclamation';

        toast.innerHTML = `
            <div class="toast-icon"><i class="${iconClass}"></i></div>
            <div class="toast-message">${message}</div>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300);
        }, 3500);
    }
});
