/**
 * Hệ thống Tra cứu Tuyển sinh & Lọc Ngành - Trường Đại học
 * Dynamic HTML Table Rendering & Multi-criteria Filtering
 */

// Chờ DOM tải hoàn tất
document.addEventListener('DOMContentLoaded', () => {
  // Lấy các phần tử DOM
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const schoolSelect = document.getElementById('schoolSelect');
  const categorySelect = document.getElementById('categorySelect');
  const subjectSelect = document.getElementById('subjectSelect');
  const sortSelect = document.getElementById('sortSelect');
  const resetBtn = document.getElementById('resetBtn');
  const emptyResetBtn = document.getElementById('emptyResetBtn');

  const tableBody = document.getElementById('tableBody');
  const resultsTable = document.getElementById('resultsTable');
  const emptyState = document.getElementById('emptyState');
  const resultCount = document.getElementById('resultCount');
  const activeFilterTags = document.getElementById('activeFilterTags');

  // Modal elements
  const detailModal = document.getElementById('detailModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalDismissBtn = document.getElementById('modalDismissBtn');
  const modalSchoolCode = document.getElementById('modalSchoolCode');
  const modalSchoolName = document.getElementById('modalSchoolName');
  const modalBody = document.getElementById('modalBody');
  const modalWebsiteLink = document.getElementById('modalWebsiteLink');

  /**
   * 1. KHỞI TẠO CÁC THẺ <SELECT> ĐỘNG TỪ DỮ LIỆU
   */
  function initSelectOptions() {
    // 1.1 Khởi tạo danh sách các Trường Đại học duy nhất (Unique Schools)
    const schoolMap = new Map();
    universitiesData.forEach(item => {
      if (!schoolMap.has(item.schoolCode)) {
        schoolMap.set(item.schoolCode, item.schoolName);
      }
    });

    // Sắp xếp tên trường theo thứ tự bảng chữ cái A-Z
    const sortedSchools = Array.from(schoolMap.entries()).sort((a, b) => a[1].localeCompare(b[1], 'vi'));

    sortedSchools.forEach(([code, name]) => {
      const option = document.createElement('option');
      option.value = code;
      option.textContent = `[${code}] ${name}`;
      schoolSelect.appendChild(option);
    });

    // 1.2 Khởi tạo danh sách Nhóm ngành đào tạo duy nhất (Unique Categories)
    const categories = Array.from(new Set(universitiesData.map(item => item.category))).sort((a, b) => a.localeCompare(b, 'vi'));

    categories.forEach(cat => {
      const option = document.createElement('option');
      option.value = cat;
      option.textContent = cat;
      categorySelect.appendChild(option);
    });
  }

  /**
   * 2. HÀM CHUYỂN ĐỔI CHỮ TIẾNG VIỆT CÓ DẤU THÀNH KHÔNG DẤU (Để tìm kiếm thông minh)
   */
  function removeVietnameseTones(str) {
    if (!str) return '';
    str = str.toLowerCase();
    str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
    str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e");
    str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
    str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o");
    str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
    str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y");
    str = str.replace(/đ/g, "d");
    return str.trim();
  }

  /**
   * 3. HÀM HIGHLIGHT TỪ KHÓA TÌM KIẾM TRONG VĂN BẢN
   */
  function highlightText(text, keyword) {
    if (!keyword || !text) return text;
    const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedKeyword})`, 'gi');
    return text.replace(regex, '<mark class="highlight">$1</mark>');
  }

  /**
   * 4. HÀM XỬ LÝ LỌC & SẮP XẾP DỮ LIỆU CHÍNH (FILTER & SORT)
   */
  function getFilteredAndSortedData() {
    const rawKeyword = searchInput.value.trim();
    const searchNormalized = removeVietnameseTones(rawKeyword);
    const selectedSchool = schoolSelect.value;
    const selectedCategory = categorySelect.value;
    const selectedSubject = subjectSelect.value;
    const selectedSort = sortSelect.value;

    // Lọc theo tất cả tiêu chuẩn
    let filtered = universitiesData.filter(item => {
      // 4.1 Lọc theo Trường
      if (selectedSchool && item.schoolCode !== selectedSchool) {
        return false;
      }

      // 4.2 Lọc theo Ngành / Nhóm ngành
      if (selectedCategory && item.category !== selectedCategory) {
        return false;
      }

      // 4.3 Lọc theo Khối / Tổ hợp môn
      if (selectedSubject && !item.subjectGroups.includes(selectedSubject)) {
        return false;
      }

      // 4.4 Lọc theo Từ khóa tìm kiếm (hỗ trợ cả có dấu và không dấu)
      if (searchNormalized) {
        const fullContent = `${item.schoolName} ${item.schoolCode} ${item.majorName} ${item.majorCode} ${item.category} ${item.location}`;
        const normalizedContent = removeVietnameseTones(fullContent);
        if (!normalizedContent.includes(searchNormalized)) {
          return false;
        }
      }

      return true;
    });

    // Sắp xếp dữ liệu (Sort)
    if (selectedSort === 'score-desc') {
      filtered.sort((a, b) => b.benchmarkScore - a.benchmarkScore);
    } else if (selectedSort === 'score-asc') {
      filtered.sort((a, b) => a.benchmarkScore - b.benchmarkScore);
    } else if (selectedSort === 'school-az') {
      filtered.sort((a, b) => a.schoolName.localeCompare(b.schoolName, 'vi'));
    } else if (selectedSort === 'major-az') {
      filtered.sort((a, b) => a.majorName.localeCompare(b.majorName, 'vi'));
    }

    return { filtered, rawKeyword };
  }

  /**
   * 5. HÀM RENDER BẢNG KẾT QUẢ BẰNG HTML ĐỘNG
   */
  function renderTable() {
    const { filtered, rawKeyword } = getFilteredAndSortedData();

    // Cập nhật số lượng kết quả
    resultCount.textContent = filtered.length;

    // Cập nhật các tags bộ lọc đang hoạt động
    renderFilterTags();

    // Hiển thị/Ẩn nút xóa từ khóa ở thanh tìm kiếm
    clearSearchBtn.style.display = searchInput.value ? 'flex' : 'none';

    // Xử lý khi không có kết quả phù hợp (Empty State)
    if (filtered.length === 0) {
      tableBody.innerHTML = '';
      resultsTable.style.display = 'none';
      emptyState.style.display = 'block';
      return;
    }

    // Khi có kết quả: Hiển thị lại bảng và ẩn empty state
    resultsTable.style.display = 'table';
    emptyState.style.display = 'none';

    // Xây dựng chuỗi HTML động
    let htmlRows = '';

    filtered.forEach((item, index) => {
      // Highlight từ khóa
      const highlightedSchool = highlightText(item.schoolName, rawKeyword);
      const highlightedMajor = highlightText(item.majorName, rawKeyword);
      const highlightedCode = highlightText(item.majorCode, rawKeyword);

      // Render danh sách khối xét tuyển
      const subjectBadgesHtml = item.subjectGroups
        .map(sg => `<span class="subject-badge">${sg}</span>`)
        .join(' ');

      // Badge điểm chuẩn theo mức
      let scoreBadgeClass = 'score-high';
      if (item.benchmarkScore > 30) {
        scoreBadgeClass = 'score-special'; // Thang 40
      } else if (item.benchmarkScore < 25) {
        scoreBadgeClass = 'score-mid';
      }

      htmlRows += `
        <tr>
          <td class="text-center font-medium">${index + 1}</td>
          <td>
            <div class="school-cell">
              <span class="school-badge">${item.schoolCode}</span>
              <div class="school-title">${highlightedSchool}</div>
            </div>
          </td>
          <td>
            <div class="major-cell">
              <span class="major-name">${highlightedMajor}</span>
              <span class="major-code">Mã ngành: ${highlightedCode}</span>
            </div>
          </td>
          <td>
            <span class="category-tag">${item.category}</span>
          </td>
          <td class="text-center">
            <div class="subject-badges">
              ${subjectBadgesHtml}
            </div>
          </td>
          <td class="text-center">
            <span class="score-badge ${scoreBadgeClass}">
              ${item.benchmarkScore.toFixed(2)}
            </span>
          </td>
          <td>
            <span class="fee-text"><i class="fa-solid fa-coins text-muted"></i> ${item.tuitionFee}</span>
          </td>
          <td class="text-center">
            <button class="btn btn-outline btn-sm btn-detail" data-id="${item.id}">
              <i class="fa-solid fa-eye"></i> Chi tiết
            </button>
          </td>
        </tr>
      `;
    });

    // Render toàn bộ HTML động vào tbody
    tableBody.innerHTML = htmlRows;

    // Gán sự kiện click cho các nút Chi tiết vừa tạo
    const detailButtons = tableBody.querySelectorAll('.btn-detail');
    detailButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.getAttribute('data-id'), 10);
        showDetailModal(id);
      });
    });
  }

  /**
   * 6. RENDER CÁC TAG BỘ LỌC ĐANG ÁP DỤNG
   */
  function renderFilterTags() {
    activeFilterTags.innerHTML = '';

    const tags = [];
    if (searchInput.value.trim()) {
      tags.push({ label: `Tìm: "${searchInput.value.trim()}"`, type: 'search' });
    }
    if (schoolSelect.value) {
      const selectedOption = schoolSelect.options[schoolSelect.selectedIndex].text;
      tags.push({ label: `Trường: ${selectedOption}`, type: 'school' });
    }
    if (categorySelect.value) {
      tags.push({ label: `Ngành: ${categorySelect.value}`, type: 'category' });
    }
    if (subjectSelect.value) {
      tags.push({ label: `Khối: ${subjectSelect.value}`, type: 'subject' });
    }

    tags.forEach(tag => {
      const tagEl = document.createElement('span');
      tagEl.className = 'tag-badge';
      tagEl.innerHTML = `${tag.label} <i class="fa-solid fa-xmark remove-tag" title="Gỡ bộ lọc"></i>`;

      tagEl.querySelector('.remove-tag').addEventListener('click', () => {
        if (tag.type === 'search') searchInput.value = '';
        if (tag.type === 'school') schoolSelect.value = '';
        if (tag.type === 'category') categorySelect.value = '';
        if (tag.type === 'subject') subjectSelect.value = '';
        renderTable();
      });

      activeFilterTags.appendChild(tagEl);
    });
  }

  /**
   * 7. HIỂN THỊ MODAL CHI TIẾT
   */
  function showDetailModal(id) {
    const item = universitiesData.find(u => u.id === id);
    if (!item) return;

    modalSchoolCode.textContent = item.schoolCode;
    modalSchoolName.textContent = item.schoolName;

    modalBody.innerHTML = `
      <div style="margin-bottom: 14px;">
        <h4 style="font-size: 1.15rem; color: #1e3a8a; margin-bottom: 4px;">${item.majorName}</h4>
        <p style="color: #64748b; font-size: 0.875rem;">Mã ngành tuyển sinh: <strong>${item.majorCode}</strong></p>
      </div>

      <div class="modal-detail-grid">
        <div class="detail-item">
          <div class="label"><i class="fa-solid fa-layer-group"></i> Nhóm ngành</div>
          <div class="value">${item.category}</div>
        </div>
        <div class="detail-item">
          <div class="label"><i class="fa-solid fa-award"></i> Điểm chuẩn trúng tuyển</div>
          <div class="value" style="color: #16a34a; font-size: 1.1rem;">
            ${item.benchmarkScore} ${item.benchmarkScore > 30 ? '(Thang 40)' : '(Thang 30)'}
          </div>
        </div>
        <div class="detail-item">
          <div class="label"><i class="fa-solid fa-book"></i> Tổ hợp xét tuyển</div>
          <div class="value">${item.subjectGroups.join(', ')}</div>
        </div>
        <div class="detail-item">
          <div class="label"><i class="fa-solid fa-user-graduate"></i> Chỉ tiêu dự kiến</div>
          <div class="value">${item.quota} sinh viên</div>
        </div>
        <div class="detail-item">
          <div class="label"><i class="fa-solid fa-location-dot"></i> Địa điểm đào tạo</div>
          <div class="value">${item.location}</div>
        </div>
        <div class="detail-item">
          <div class="label"><i class="fa-solid fa-money-bill-wave"></i> Mức học phí dự kiến</div>
          <div class="value">${item.tuitionFee}</div>
        </div>
      </div>
    `;

    modalWebsiteLink.href = item.website;
    detailModal.style.display = 'flex';
  }

  function closeModal() {
    detailModal.style.display = 'none';
  }

  /**
   * 8. HÀM ĐẶT LẠI TẤT CẢ BỘ LỌC (RESET)
   */
  function resetAllFilters() {
    searchInput.value = '';
    schoolSelect.value = '';
    categorySelect.value = '';
    subjectSelect.value = '';
    sortSelect.value = 'default';
    renderTable();
  }

  /**
   * 9. ĐĂNG KÝ CÁC EVENT LISTENERS
   */
  // Thanh tìm kiếm: Lọc thời gian thực ngay khi người dùng gõ
  searchInput.addEventListener('input', () => {
    renderTable();
  });

  // Xóa nhanh thanh tìm kiếm
  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchInput.focus();
    renderTable();
  });

  // Sự kiện change trên các thẻ <select>
  schoolSelect.addEventListener('change', renderTable);
  categorySelect.addEventListener('change', renderTable);
  subjectSelect.addEventListener('change', renderTable);
  sortSelect.addEventListener('change', renderTable);

  // Nút đặt lại bộ lọc
  resetBtn.addEventListener('click', resetAllFilters);
  emptyResetBtn.addEventListener('click', resetAllFilters);

  // Modal đóng
  closeModalBtn.addEventListener('click', closeModal);
  modalDismissBtn.addEventListener('click', closeModal);
  detailModal.addEventListener('click', (e) => {
    if (e.target === detailModal) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && detailModal.style.display === 'flex') {
      closeModal();
    }
  });

  // 10. KHỞI CHẠY LẦN ĐẦU TIÊN
  initSelectOptions();
  renderTable();
});
