/**
 * ============================================================================
 * Quản trị Nhật ký Hoạt động (Audit Logs)
 * Giao tiếp qua Fetch API với Endpoint: GET /api/v1/admin/audit-logs
 * Có hỗ trợ bộ lọc đa điều kiện, chuyển trang (Pagination) & Chế độ Mock dữ liệu
 * ============================================================================
 */

// 1. Cấu hình Endpoint API
const API_CONFIG = {
  endpoint: '/api/v1/admin/audit-logs',
  // Nếu có token lưu trong cookie hoặc localStorage:
  getAuthToken: () => localStorage.getItem('auth_token') || 'demo-bearer-token'
};

// 2. Trạng thái ứng dụng (Application State)
const state = {
  currentPage: 1,
  pageSize: 10,
  totalPages: 1,
  totalRecords: 0,
  filters: {
    user: '',
    action: '',
    from_date: '',
    to_date: '',
    status: ''
  },
  currentData: [],
  isMockMode: false
};

// 3. Khởi tạo khi DOM đã sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  // Tải dữ liệu trang đầu tiên
  fetchAuditLogs(1);
});

/**
 * Đăng ký các sự kiện lắng nghe (Event Listeners)
 */
function initEventListeners() {
  const filterForm = document.getElementById('filterForm');
  const btnReset = document.getElementById('btnReset');
  const btnResetEmpty = document.getElementById('btnResetEmpty');
  const btnRefresh = document.getElementById('btnRefresh');
  const btnRetry = document.getElementById('btnRetry');
  const pageSizeSelect = document.getElementById('pageSizeSelect');
  const btnExport = document.getElementById('btnExport');

  // Sự kiện gửi form lọc
  filterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    state.filters.user = document.getElementById('filterUser').value.trim();
    state.filters.action = document.getElementById('filterAction').value;
    state.filters.from_date = document.getElementById('filterFromDate').value;
    state.filters.to_date = document.getElementById('filterToDate').value;
    state.filters.status = document.getElementById('filterStatus').value;

    updateActiveFilterBadge();
    // Khi lọc mới, luôn quay về trang 1
    fetchAuditLogs(1);
  });

  // Nút đặt lại bộ lọc
  btnReset.addEventListener('click', resetFilters);
  if (btnResetEmpty) btnResetEmpty.addEventListener('click', resetFilters);

  // Nút làm mới dữ liệu
  btnRefresh.addEventListener('click', () => {
    fetchAuditLogs(state.currentPage);
  });

  // Nút thử lại khi gặp lỗi
  btnRetry.addEventListener('click', () => {
    fetchAuditLogs(state.currentPage);
  });

  // Thay đổi số lượng dòng hiển thị trên một trang
  pageSizeSelect.addEventListener('change', (e) => {
    state.pageSize = parseInt(e.target.value, 10);
    fetchAuditLogs(1);
  });

  // Các nút chuyển trang
  document.getElementById('btnFirstPage').addEventListener('click', () => {
    if (state.currentPage > 1) fetchAuditLogs(1);
  });

  document.getElementById('btnPrevPage').addEventListener('click', () => {
    if (state.currentPage > 1) fetchAuditLogs(state.currentPage - 1);
  });

  document.getElementById('btnNextPage').addEventListener('click', () => {
    if (state.currentPage < state.totalPages) fetchAuditLogs(state.currentPage + 1);
  });

  document.getElementById('btnLastPage').addEventListener('click', () => {
    if (state.currentPage < state.totalPages) fetchAuditLogs(state.totalPages);
  });

  // Modal events
  document.getElementById('btnCloseModal').addEventListener('click', closeModal);
  document.getElementById('btnCloseModalBtn').addEventListener('click', closeModal);
  document.getElementById('detailModal').addEventListener('click', (e) => {
    if (e.target.id === 'detailModal') closeModal();
  });

  // Export CSV demo
  btnExport.addEventListener('click', exportToCSV);
}

/**
 * Hàm gọi API lấy danh sách Audit Logs bằng Fetch API
 * @param {number} page - Số trang cần tải
 */
async function fetchAuditLogs(page = 1) {
  state.currentPage = page;
  showLoading();

  // 1. Tạo Query Parameters sử dụng URLSearchParams
  const params = new URLSearchParams({
    page: state.currentPage,
    limit: state.pageSize
  });

  if (state.filters.user) params.append('user', state.filters.user);
  if (state.filters.action) params.append('action', state.filters.action);
  if (state.filters.from_date) params.append('from_date', state.filters.from_date);
  if (state.filters.to_date) params.append('to_date', state.filters.to_date);
  if (state.filters.status) params.append('status', state.filters.status);

  const requestUrl = `${API_CONFIG.endpoint}?${params.toString()}`;

  try {
    // 2. Thực hiện gọi HTTP GET bằng Fetch API
    const response = await fetch(requestUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_CONFIG.getAuthToken()}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }

    const json = await response.json();
    handleApiResponse(json);

  } catch (error) {
    console.warn(`[AuditLogs] Không thể kết nối tới ${requestUrl}:`, error.message);
    
    // Tự động fallback về Mock Data để tiện lợi cho việc kiểm thử giao diện
    enableMockFallback(params);
  } finally {
    hideLoading();
  }
}

/**
 * Xử lý dữ liệu trả về từ API backend thực tế
 * Hỗ trợ các chuẩn cấu trúc response phổ biến:
 * { success: true, data: { items: [...], pagination: { ... } } }
 * hoặc { items: [...], total: 100, page: 1, limit: 10 }
 */
function handleApiResponse(json) {
  let items = [];
  let total = 0;
  let page = state.currentPage;
  let totalPages = 1;

  if (json.data && Array.isArray(json.data.items)) {
    items = json.data.items;
    total = json.data.pagination?.total_records || items.length;
    totalPages = json.data.pagination?.total_pages || Math.ceil(total / state.pageSize);
  } else if (Array.isArray(json.items)) {
    items = json.items;
    total = json.total || items.length;
    totalPages = Math.ceil(total / state.pageSize);
  } else if (Array.isArray(json)) {
    items = json;
    total = json.length;
    totalPages = Math.ceil(total / state.pageSize);
  }

  state.currentData = items;
  state.totalRecords = total;
  state.totalPages = Math.max(1, totalPages);

  showBanner('online', `Đã kết nối thành công tới API: <code>GET ${API_CONFIG.endpoint}</code>`);
  renderTable(items);
  renderPagination();
}

/**
 * Render dữ liệu vào thẻ <tbody> của bảng
 */
function renderTable(logs) {
  const tbody = document.getElementById('logsTableBody');
  const emptyState = document.getElementById('emptyState');
  const errorState = document.getElementById('errorState');

  errorState.classList.add('hidden');

  if (!logs || logs.length === 0) {
    tbody.innerHTML = '';
    emptyState.classList.remove('hidden');
    document.getElementById('paginationFooter').classList.add('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  document.getElementById('paginationFooter').classList.remove('hidden');

  const rowsHtml = logs.map(log => {
    const user = log.user || { name: 'Hệ thống', email: 'system@internal', role: 'System' };
    const avatarChar = (user.name || 'U').charAt(0).toUpperCase();

    return `
      <tr>
        <td class="text-center log-id">#${escapeHtml(String(log.id || ''))}</td>
        <td>
          <div class="log-time">
            <span class="time-full">${formatDate(log.timestamp)}</span>
            <span class="time-relative">${getRelativeTime(log.timestamp)}</span>
          </div>
        </td>
        <td>
          <div class="user-cell">
            <div class="user-avatar" style="background-color: ${generateAvatarBg(user.name)}">${avatarChar}</div>
            <div class="user-meta">
              <span class="user-name" title="${escapeHtml(user.name)}">${escapeHtml(user.name)}</span>
              <span class="user-email" title="${escapeHtml(user.email || '')}">${escapeHtml(user.email || '')}</span>
            </div>
          </div>
        </td>
        <td>
          ${renderActionBadge(log.action)}
        </td>
        <td>
          <div class="resource-text">${escapeHtml(log.resource || 'Tài nguyên không xác định')}</div>
          <div class="resource-desc">${escapeHtml(log.description || log.details?.summary || '')}</div>
        </td>
        <td>
          <span class="ip-text"><i class="fa-solid fa-network-wired"></i> ${escapeHtml(log.ip_address || '127.0.0.1')}</span>
        </td>
        <td class="text-center">
          ${renderStatusBadge(log.status)}
        </td>
        <td class="text-center">
          <button class="btn-icon" title="Xem chi tiết" onclick="viewLogDetail('${escapeHtml(String(log.id))}')">
            <i class="fa-regular fa-eye"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');

  tbody.innerHTML = rowsHtml;
}

/**
 * Hiển thị và xử lý thanh phân trang (Pagination)
 */
function renderPagination() {
  const { currentPage, totalPages, totalRecords, pageSize } = state;

  // Tính khoảng hiển thị
  const start = totalRecords === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const end = Math.min(currentPage * pageSize, totalRecords);

  document.getElementById('infoStart').textContent = start;
  document.getElementById('infoEnd').textContent = end;
  document.getElementById('infoTotal').textContent = totalRecords;

  // Cập nhật trạng thái nút bấm phân trang
  document.getElementById('btnFirstPage').disabled = (currentPage <= 1);
  document.getElementById('btnPrevPage').disabled = (currentPage <= 1);
  document.getElementById('btnNextPage').disabled = (currentPage >= totalPages);
  document.getElementById('btnLastPage').disabled = (currentPage >= totalPages);

  // Tạo các nút số trang thông minh
  renderPageNumbers(totalPages, currentPage);
}

/**
 * Tạo danh sách nút số trang (1, 2, ..., n) với logic ellipsis thông minh
 */
function renderPageNumbers(totalPages, currentPage) {
  const container = document.getElementById('pageNumbersContainer');
  container.innerHTML = '';

  const maxVisiblePages = 5;
  let pages = [];

  if (totalPages <= maxVisiblePages + 2) {
    for (let i = 1; i <= totalPages; i++) pages.push(i);
  } else {
    pages.push(1);

    let left = Math.max(2, currentPage - 1);
    let right = Math.min(totalPages - 1, currentPage + 1);

    if (currentPage <= 3) {
      right = 4;
    }
    if (currentPage >= totalPages - 2) {
      left = totalPages - 3;
    }

    if (left > 2) pages.push('...');
    for (let i = left; i <= right; i++) pages.push(i);
    if (right < totalPages - 1) pages.push('...');

    pages.push(totalPages);
  }

  pages.forEach(item => {
    if (item === '...') {
      const span = document.createElement('span');
      span.className = 'page-ellipsis';
      span.textContent = '...';
      container.appendChild(span);
    } else {
      const btn = document.createElement('button');
      btn.className = `page-btn ${item === currentPage ? 'active' : ''}`;
      btn.textContent = item;
      btn.onclick = () => fetchAuditLogs(item);
      container.appendChild(btn);
    }
  });
}

/**
 * Hiển thị Badge cho loại Hành động (Action)
 */
function renderActionBadge(action) {
  const act = (action || '').toUpperCase();
  const map = {
    'LOGIN': { class: 'badge-action-login', icon: 'fa-right-to-bracket', text: 'Đăng nhập' },
    'LOGOUT': { class: 'badge-action-logout', icon: 'fa-right-from-bracket', text: 'Đăng xuất' },
    'CREATE': { class: 'badge-action-create', icon: 'fa-plus', text: 'Tạo mới' },
    'UPDATE': { class: 'badge-action-update', icon: 'fa-pen-to-square', text: 'Cập nhật' },
    'DELETE': { class: 'badge-action-delete', icon: 'fa-trash-can', text: 'Xóa' },
    'EXPORT': { class: 'badge-action-export', icon: 'fa-file-export', text: 'Xuất dữ liệu' },
    'PERMISSION_CHANGE': { class: 'badge-action-permission', icon: 'fa-key', text: 'Phân quyền' }
  };

  const config = map[act] || { class: 'badge-action-login', icon: 'fa-circle-dot', text: act };
  return `<span class="badge ${config.class}"><i class="fa-solid ${config.icon}"></i> ${config.text}</span>`;
}

/**
 * Hiển thị Badge cho Trạng thái thực thi (Status)
 */
function renderStatusBadge(status) {
  const st = (status || 'SUCCESS').toUpperCase();
  if (st === 'SUCCESS') {
    return `<span class="badge badge-status-success"><i class="fa-solid fa-check"></i> Thành công</span>`;
  } else if (st === 'FAILED') {
    return `<span class="badge badge-status-failed"><i class="fa-solid fa-xmark"></i> Thất bại</span>`;
  }
  return `<span class="badge badge-status-warning"><i class="fa-solid fa-triangle-exclamation"></i> Cảnh báo</span>`;
}

/**
 * Xem chi tiết bản ghi nhật ký trong Modal
 */
function viewLogDetail(logId) {
  const item = state.currentData.find(d => String(d.id) === String(logId));
  if (!item) return;

  const modalBody = document.getElementById('modalBodyContent');
  modalBody.innerHTML = `
    <table class="detail-table">
      <tr>
        <th>Mã ID:</th>
        <td><code>#${escapeHtml(String(item.id))}</code></td>
      </tr>
      <tr>
        <th>Thời gian:</th>
        <td>${formatDate(item.timestamp)} (<code>${escapeHtml(item.timestamp || '')}</code>)</td>
      </tr>
      <tr>
        <th>Người thực hiện:</th>
        <td>
          <strong>${escapeHtml(item.user?.name || 'Unknown')}</strong> 
          (${escapeHtml(item.user?.email || 'N/A')}) - 
          <span class="badge badge-action-permission">${escapeHtml(item.user?.role || 'User')}</span>
        </td>
      </tr>
      <tr>
        <th>Hành động:</th>
        <td>${renderActionBadge(item.action)}</td>
      </tr>
      <tr>
        <th>Đối tượng tài nguyên:</th>
        <td><strong>${escapeHtml(item.resource || 'N/A')}</strong></td>
      </tr>
      <tr>
        <th>Mô tả chi tiết:</th>
        <td>${escapeHtml(item.description || item.details?.summary || 'Không có mô tả chi tiết')}</td>
      </tr>
      <tr>
        <th>Địa chỉ IP:</th>
        <td><code>${escapeHtml(item.ip_address || '127.0.0.1')}</code></td>
      </tr>
      <tr>
        <th>Trình duyệt (User Agent):</th>
        <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(item.user_agent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')}</td>
      </tr>
      <tr>
        <th>Trạng thái:</th>
        <td>${renderStatusBadge(item.status)}</td>
      </tr>
    </table>

    <div class="json-payload-title"><i class="fa-solid fa-code"></i> Dữ liệu thay đổi (Payload / Changes JSON):</div>
    <pre class="json-payload-block"><code>${escapeHtml(JSON.stringify(item.details || {}, null, 2))}</code></pre>
  `;

  document.getElementById('detailModal').classList.remove('hidden');
}

/**
 * Đóng Modal
 */
function closeModal() {
  document.getElementById('detailModal').classList.add('hidden');
}

/**
 * Đặt lại toàn bộ bộ lọc
 */
function resetFilters() {
  document.getElementById('filterForm').reset();
  state.filters = {
    user: '',
    action: '',
    from_date: '',
    to_date: '',
    status: ''
  };
  updateActiveFilterBadge();
  fetchAuditLogs(1);
}

/**
 * Cập nhật hiển thị badge khi đang áp dụng bộ lọc
 */
function updateActiveFilterBadge() {
  const isFiltering = Object.values(state.filters).some(v => v !== '');
  const badge = document.getElementById('activeFilterBadge');
  if (isFiltering) {
    badge.style.display = 'inline-block';
  } else {
    badge.style.display = 'none';
  }
}

/**
 * Điều khiển trạng thái Loading
 */
function showLoading() {
  document.getElementById('tableLoading').classList.remove('hidden');
  document.getElementById('logsTableBody').style.opacity = '0.35';
}

function hideLoading() {
  document.getElementById('tableLoading').classList.add('hidden');
  document.getElementById('logsTableBody').style.opacity = '1';
}

/**
 * Hiển thị Banner trạng thái API
 */
function showBanner(type, htmlMessage) {
  const banner = document.getElementById('apiStatusBanner');
  const text = document.getElementById('apiStatusText');
  banner.classList.remove('hidden');
  text.innerHTML = htmlMessage;

  if (type === 'mock') {
    banner.classList.add('mock-mode');
  } else {
    banner.classList.remove('mock-mode');
  }
}

/**
 * Định dạng ngày giờ: DD/MM/YYYY HH:mm:ss
 */
function formatDate(dateStr) {
  if (!dateStr) return '--';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  
  const pad = (n) => String(n).padStart(2, '0');
  const day = pad(d.getDate());
  const month = pad(d.getMonth() + 1);
  const year = d.getFullYear();
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  const seconds = pad(d.getSeconds());

  return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}

/**
 * Hiển thị thời gian tương đối (VD: 5 phút trước)
 */
function getRelativeTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '';
  
  const diffSec = Math.floor((new Date() - d) / 1000);
  if (diffSec < 60) return 'Vừa xong';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} phút trước`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} giờ trước`;
  return `${Math.floor(diffSec / 86400)} ngày trước`;
}

/**
 * Sinh màu nền ngẫu nhiên hài hòa cho avatar
 */
function generateAvatarBg(name = '') {
  const colors = ['#e0f2fe', '#dcfce7', '#fef3c7', '#fee2e2', '#f3e8ff', '#ffedd5'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

/**
 * Escape chuỗi HTML để phòng chống XSS
 */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Demo chức năng Xuất CSV
 */
function exportToCSV() {
  if (!state.currentData || state.currentData.length === 0) {
    alert('Không có dữ liệu để xuất!');
    return;
  }

  let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
  csvContent += "ID,Thời gian,Người thực hiện,Email,Hành động,Tài nguyên,IP,Trạng thái\n";

  state.currentData.forEach(row => {
    const user = row.user || {};
    const line = [
      `"${row.id}"`,
      `"${formatDate(row.timestamp)}"`,
      `"${user.name || ''}"`,
      `"${user.email || ''}"`,
      `"${row.action}"`,
      `"${row.resource || ''}"`,
      `"${row.ip_address || ''}"`,
      `"${row.status}"`
    ].join(',');
    csvContent += line + "\n";
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `audit_logs_page_${state.currentPage}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ============================================================================
// MOCK DATA FALLBACK ENGINE
// Tự động kích hoạt khi chưa có backend server thực tế,
// giúp việc preview giao diện, bộ lọc và phân trang hoạt động hoàn hảo 100%
// ============================================================================
function enableMockFallback(params) {
  state.isMockMode = true;
  showBanner('mock', `<strong>Chế độ Xem trước (Mock Data):</strong> Không thể kết nối tới backend <code>GET ${API_CONFIG.endpoint}</code>. Đang hiển thị 45 bản ghi giả lập đầy đủ tính năng lọc, tìm kiếm và phân trang!`);

  // Sinh 45 bản ghi mock dữ liệu phong phú
  if (!window._mockDatabase) {
    window._mockDatabase = generateMockAuditLogs(45);
  }

  // Giả lập lọc trên client
  let filtered = [...window._mockDatabase];

  if (state.filters.user) {
    const keyword = state.filters.user.toLowerCase();
    filtered = filtered.filter(item => 
      item.user.name.toLowerCase().includes(keyword) ||
      item.user.email.toLowerCase().includes(keyword) ||
      String(item.user.id).includes(keyword)
    );
  }

  if (state.filters.action) {
    filtered = filtered.filter(item => item.action === state.filters.action);
  }

  if (state.filters.status) {
    filtered = filtered.filter(item => item.status === state.filters.status);
  }

  if (state.filters.from_date) {
    const fromTime = new Date(state.filters.from_date).setHours(0, 0, 0, 0);
    filtered = filtered.filter(item => new Date(item.timestamp).getTime() >= fromTime);
  }

  if (state.filters.to_date) {
    const toTime = new Date(state.filters.to_date).setHours(23, 59, 59, 999);
    filtered = filtered.filter(item => new Date(item.timestamp).getTime() <= toTime);
  }

  // Phân trang
  const total = filtered.length;
  const totalPages = Math.ceil(total / state.pageSize) || 1;
  const offset = (state.currentPage - 1) * state.pageSize;
  const pagedItems = filtered.slice(offset, offset + state.pageSize);

  state.currentData = pagedItems;
  state.totalRecords = total;
  state.totalPages = totalPages;

  // Giả lập độ trễ mạng nhỏ để quan sát hiệu ứng loading
  setTimeout(() => {
    renderTable(pagedItems);
    renderPagination();
  }, 200);
}

/**
 * Hàm sinh danh sách dữ liệu mẫu ngẫu nhiên và đa dạng
 */
function generateMockAuditLogs(count = 45) {
  const users = [
    { id: 101, name: 'Nguyễn Văn An', email: 'an.nguyen@company.com', role: 'Super Admin' },
    { id: 102, name: 'Trần Thị Bích', email: 'bich.tran@company.com', role: 'HR Manager' },
    { id: 103, name: 'Lê Hoàng Minh', email: 'minh.le@company.com', role: 'System Auditor' },
    { id: 104, name: 'Phạm Hồng Đào', email: 'dao.pham@company.com', role: 'Operator' },
    { id: 105, name: 'Vũ Quốc Khánh', email: 'khanh.vu@company.com', role: 'Developer' }
  ];

  const actions = ['LOGIN', 'LOGOUT', 'CREATE', 'UPDATE', 'DELETE', 'EXPORT', 'PERMISSION_CHANGE'];
  const resources = [
    'Người dùng #104 (Phạm Hồng Đào)',
    'Hợp đồng lao động #HD-2026-89',
    'Chính sách bảo mật hệ thống (Security Policy)',
    'Báo cáo doanh thu quý 3/2026',
    'Nhóm quyền hạn Quản trị viên (Admin Group)',
    'Cấu hình cổng thanh toán VNPAY',
    'Danh sách nhân viên phòng Kỹ thuật'
  ];

  const ips = ['192.168.1.15', '14.241.12.89', '118.69.182.10', '172.16.0.42', '10.0.8.101'];

  const logs = [];
  const now = new Date();

  for (let i = 1; i <= count; i++) {
    const user = users[i % users.length];
    const action = actions[i % actions.length];
    const resource = resources[i % resources.length];
    const status = (i % 9 === 0) ? 'FAILED' : 'SUCCESS';
    
    // Tạo mốc thời gian lùi dần từ hôm nay
    const logTime = new Date(now.getTime() - (i * 42 * 60 * 1000));

    logs.push({
      id: 1000 + i,
      timestamp: logTime.toISOString(),
      user: user,
      action: action,
      resource: resource,
      description: `Thực hiện thao tác [${action}] trên tài nguyên [${resource.split(' ')[0]}]`,
      ip_address: ips[i % ips.length],
      user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36',
      status: status,
      details: {
        operation_id: `OP-${Date.now()}-${i}`,
        endpoint_called: `/api/v1/resources/${100 + i}`,
        http_method: action === 'CREATE' ? 'POST' : (action === 'DELETE' ? 'DELETE' : 'PUT'),
        diff: action === 'UPDATE' ? {
          field_modified: 'status',
          old_value: 'PENDING',
          new_value: 'ACTIVE'
        } : null,
        execution_time_ms: Math.floor(Math.random() * 120) + 15
      }
    });
  }

  return logs;
}

// Gắn các hàm gọi từ thuộc tính HTML onclick lên window scope
window.viewLogDetail = viewLogDetail;
window.closeModal = closeModal;
window.fetchAuditLogs = fetchAuditLogs;
