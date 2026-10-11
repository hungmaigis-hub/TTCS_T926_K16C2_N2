/**
 * ==============================================================================
 * DASHBOARD KPI MANAGEMENT & REAL-TIME UPDATES VIA FETCH API
 * Endpoint: GET /api/v1/reports/completion-rate
 * ==============================================================================
 */

// Cấu hình hằng số
const API_CONFIG = {
  ENDPOINT: '/api/v1/reports/completion-rate',
  DEFAULT_INTERVAL_MS: 10000, // Mặc định 10 giây gọi API 1 lần
  CIRCUMFERENCE: 2 * Math.PI * 68, // Bán kính r = 68 => ~427.26
};

// State lưu trữ dữ liệu hiện tại để chạy animation số nhảy mượt mà
const dashboardState = {
  timerId: null,
  isFetching: false,
  previousData: {
    totalStudents: 0,
    active: 0,
    completed: 0,
    onLeave: 0,
    dropped: 0,
    completionRate: 0,
    onTime: 0,
    delayed: 0,
    warning: 0
  }
};

// Bộ tham chiếu DOM Elements
const elements = {
  // Trạng thái & Điều khiển
  realtimeStatusPill: document.getElementById('realtimeStatusPill'),
  connectionStatusText: document.getElementById('connectionStatusText'),
  dataSourceMode: document.getElementById('dataSourceMode'),
  refreshIntervalSelect: document.getElementById('refreshIntervalSelect'),
  btnManualRefresh: document.getElementById('btnManualRefresh'),
  lastUpdatedTime: document.getElementById('lastUpdatedTime'),

  // Vòng tròn tiến độ hoàn thành SVG
  circularProgressBar: document.getElementById('circularProgressBar'),
  completionRateValue: document.getElementById('completionRateValue'),
  completionTrendBadge: document.getElementById('completionTrendBadge'),
  completionTrendText: document.getElementById('completionTrendText'),
  completionStatusLabel: document.getElementById('completionStatusLabel'),
  targetRateValue: document.getElementById('targetRateValue'),
  targetProgressBarFill: document.getElementById('targetProgressBarFill'),
  onTimeGraduationCount: document.getElementById('onTimeGraduationCount'),
  delayedGraduationCount: document.getElementById('delayedGraduationCount'),
  academicWarningCount: document.getElementById('academicWarningCount'),
  kpiEvaluationBox: document.getElementById('kpiEvaluationBox'),
  kpiEvaluationText: document.getElementById('kpiEvaluationText'),

  // Các thẻ KPI số lượng sinh viên theo trạng thái
  kpiTotalStudents: document.getElementById('kpiTotalStudents'),
  totalTrendBadge: document.getElementById('totalTrendBadge'),
  kpiActiveStudents: document.getElementById('kpiActiveStudents'),
  activeRatioPill: document.getElementById('activeRatioPill'),
  activeProgressFill: document.getElementById('activeProgressFill'),
  kpiCompletedStudents: document.getElementById('kpiCompletedStudents'),
  completedProgressFill: document.getElementById('completedProgressFill'),
  kpiOnLeaveStudents: document.getElementById('kpiOnLeaveStudents'),
  onLeaveRatioPill: document.getElementById('onLeaveRatioPill'),
  onLeaveProgressFill: document.getElementById('onLeaveProgressFill'),
  kpiDroppedStudents: document.getElementById('kpiDroppedStudents'),
  droppedProgressFill: document.getElementById('droppedProgressFill'),

  // Toast
  toastMessage: document.getElementById('toastMessage'),
  toastText: document.getElementById('toastText')
};

/**
 * Hàm định dạng số hiển thị có dấu chấm ngăn cách phần nghìn
 * @param {number} num 
 * @returns {string} Ví dụ: 12500 -> "12.500"
 */
function formatNumber(num) {
  return new Intl.NumberFormat('vi-VN').format(Math.round(num));
}

/**
 * Hiệu ứng Count-Up animation mượt mà cho các con số
 * @param {HTMLElement} element - Phần tử hiển thị số
 * @param {number} startVal - Giá trị bắt đầu
 * @param {number} endVal - Giá trị kết thúc
 * @param {number} duration - Thời gian animation (ms)
 * @param {boolean} isFloat - Có hiển thị số thập phân 1 chữ số hay không
 */
function animateValue(element, startVal, endVal, duration = 800, isFloat = false) {
  if (!element) return;
  if (startVal === endVal) {
    element.textContent = isFloat ? endVal.toFixed(1) : formatNumber(endVal);
    return;
  }

  const startTime = performance.now();

  function updateCount(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Easing cubic out
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    const currentVal = startVal + (endVal - startVal) * easeProgress;

    element.textContent = isFloat ? currentVal.toFixed(1) : formatNumber(currentVal);

    if (progress < 1) {
      requestAnimationFrame(updateCount);
    } else {
      element.textContent = isFloat ? endVal.toFixed(1) : formatNumber(endVal);
    }
  }

  requestAnimationFrame(updateCount);
}

/**
 * Cập nhật góc quay của Vòng Tròn Phần Trăm SVG
 * @param {number} percentage - Tỷ lệ phần trăm từ 0 đến 100
 */
function updateCircularProgress(percentage) {
  const safePercentage = Math.max(0, Math.min(100, percentage));
  const circumference = API_CONFIG.CIRCUMFERENCE;
  
  // Tính độ lệch stroke-dashoffset: 0% thì lệch nguyên chu vi, 100% thì lệch 0
  const offset = circumference - (safePercentage / 100) * circumference;
  
  if (elements.circularProgressBar) {
    elements.circularProgressBar.style.strokeDashoffset = offset.toFixed(2);
  }
}

/**
 * Cập nhật toàn bộ giao diện dựa trên dữ liệu báo cáo từ API
 * @param {Object} reportData - Cấu trúc dữ liệu trả về từ backend
 */
function renderDashboard(reportData) {
  const prev = dashboardState.previousData;
  const current = reportData;

  // 1. Cập nhật Vòng tròn phần trăm tiến độ hoàn thành
  animateValue(elements.completionRateValue, prev.completionRate, current.completionRate, 1000, true);
  updateCircularProgress(current.completionRate);

  // Hiển thị tiến độ so với Mục tiêu
  if (elements.targetRateValue) {
    elements.targetRateValue.textContent = current.targetRate.toFixed(1);
  }
  if (elements.targetProgressBarFill) {
    const targetRatio = Math.min(100, (current.completionRate / current.targetRate) * 100);
    elements.targetProgressBarFill.style.width = `${targetRatio}%`;
  }

  // Đánh giá KPI
  if (elements.kpiEvaluationBox && elements.kpiEvaluationText) {
    if (current.completionRate >= current.targetRate) {
      elements.kpiEvaluationBox.style.color = 'var(--emerald-500)';
      elements.kpiEvaluationBox.style.borderColor = 'rgba(16, 185, 129, 0.3)';
      elements.kpiEvaluationBox.style.backgroundColor = 'rgba(16, 185, 129, 0.08)';
      elements.kpiEvaluationText.textContent = `Vượt mục tiêu đề ra (+${(current.completionRate - current.targetRate).toFixed(1)}%)`;
    } else {
      const diff = (current.targetRate - current.completionRate).toFixed(1);
      elements.kpiEvaluationBox.style.color = 'var(--amber-500)';
      elements.kpiEvaluationBox.style.borderColor = 'rgba(245, 158, 11, 0.3)';
      elements.kpiEvaluationBox.style.backgroundColor = 'rgba(245, 158, 11, 0.08)';
      elements.kpiEvaluationText.textContent = `Còn thiếu ${diff}% để đạt KPI hoàn thành`;
    }
  }

  // Xu hướng hoàn thành
  if (elements.completionTrendBadge && elements.completionTrendText && current.trend) {
    elements.completionTrendText.textContent = current.trend.completionRateChange || '+0.0%';
    const isNegative = (current.trend.completionRateChange || '').startsWith('-');
    elements.completionTrendBadge.classList.toggle('negative', isNegative);
    elements.completionTrendBadge.querySelector('.trend-arrow').textContent = isNegative ? '▼' : '▲';
  }

  // Chi tiết phân loại tốt nghiệp
  if (current.details) {
    animateValue(elements.onTimeGraduationCount, prev.onTime, current.details.onTimeGraduation, 800);
    animateValue(elements.delayedGraduationCount, prev.delayed, current.details.delayedGraduation, 800);
    animateValue(elements.academicWarningCount, prev.warning, current.details.academicWarning, 800);
  }

  // 2. Cập nhật Khối Thẻ Tổng sinh viên
  animateValue(elements.kpiTotalStudents, prev.totalStudents, current.totalStudents, 900);
  if (elements.totalTrendBadge && current.trend) {
    elements.totalTrendBadge.textContent = current.trend.totalChange || '+0%';
  }

  // Tính phần trăm các trạng thái so với Tổng
  const total = current.totalStudents > 0 ? current.totalStudents : 1;
  const activePct = ((current.active / total) * 100).toFixed(1);
  const completedPct = ((current.completed / total) * 100).toFixed(1);
  const onLeavePct = ((current.onLeave / total) * 100).toFixed(1);
  const droppedPct = ((current.dropped / total) * 100).toFixed(1);

  // 3. Khối Thẻ: Đang theo học
  animateValue(elements.kpiActiveStudents, prev.active, current.active, 900);
  if (elements.activeRatioPill) elements.activeRatioPill.textContent = `${activePct}% tổng số`;
  if (elements.activeProgressFill) elements.activeProgressFill.style.width = `${activePct}%`;

  // 4. Khối Thẻ: Đã hoàn thành / Tốt nghiệp
  animateValue(elements.kpiCompletedStudents, prev.completed, current.completed, 900);
  if (elements.completedProgressFill) elements.completedProgressFill.style.width = `${completedPct}%`;

  // 5. Khối Thẻ: Bảo lưu / Chờ xử lý
  animateValue(elements.kpiOnLeaveStudents, prev.onLeave, current.onLeave, 900);
  if (elements.onLeaveRatioPill) elements.onLeaveRatioPill.textContent = `${onLeavePct}% tổng số`;
  if (elements.onLeaveProgressFill) elements.onLeaveProgressFill.style.width = `${onLeavePct}%`;

  // 6. Khối Thẻ: Thôi học / Cảnh báo
  animateValue(elements.kpiDroppedStudents, prev.dropped, current.dropped, 900);
  if (elements.droppedProgressFill) elements.droppedProgressFill.style.width = `${droppedPct}%`;

  // Cập nhật timestamp lần lấy dữ liệu gần nhất
  const now = new Date();
  elements.lastUpdatedTime.textContent = now.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  // Lưu lại giá trị hiện tại làm mốc cho lần sau
  dashboardState.previousData = {
    totalStudents: current.totalStudents,
    active: current.active,
    completed: current.completed,
    onLeave: current.onLeave,
    dropped: current.dropped,
    completionRate: current.completionRate,
    onTime: current.details ? current.details.onTimeGraduation : 0,
    delayed: current.details ? current.details.delayedGraduation : 0,
    warning: current.details ? current.details.academicWarning : 0
  };
}

/**
 * Tạo dữ liệu Mock ngẫu nhiên mô phỏng số liệu thời gian thực
 * Phục vụ trường hợp chạy thử trực tiếp giao diện khi chưa dựng server backend
 */
function generateMockKpiData() {
  const baseTotal = 12500;
  // Giả lập biến động nhỏ ngẫu nhiên theo thời gian thực
  const delta = Math.floor((Math.random() - 0.48) * 15);
  const totalStudents = Math.max(12000, baseTotal + delta);

  const completed = Math.floor(totalStudents * (0.17 + Math.random() * 0.03));
  const onLeave = Math.floor(totalStudents * (0.03 + Math.random() * 0.008));
  const dropped = Math.floor(totalStudents * (0.012 + Math.random() * 0.005));
  const active = totalStudents - completed - onLeave - dropped;

  // Tỷ lệ hoàn thành dao động quanh 82.5% - 87.5%
  const completionRate = parseFloat((82.5 + Math.random() * 4.5).toFixed(1));

  return {
    success: true,
    timestamp: new Date().toISOString(),
    data: {
      totalStudents,
      active,
      completed,
      onLeave,
      dropped,
      completionRate,
      targetRate: 85.0,
      trend: {
        totalChange: '+4.8%',
        completionRateChange: `+${(Math.random() * 2.5 + 1.2).toFixed(1)}%`
      },
      details: {
        onTimeGraduation: Math.floor(completed * 0.88),
        delayedGraduation: Math.floor(completed * 0.12),
        academicWarning: Math.floor(dropped * 0.7)
      }
    }
  };
}

/**
 * Hiển thị thông báo Toast nhanh
 * @param {string} msg 
 * @param {string} type 'info' | 'error' | 'success'
 */
function showToast(msg, type = 'info') {
  if (!elements.toastMessage || !elements.toastText) return;
  
  elements.toastText.textContent = msg;
  elements.toastMessage.classList.remove('hidden');

  clearTimeout(elements.toastMessage._timeout);
  elements.toastMessage._timeout = setTimeout(() => {
    elements.toastMessage.classList.add('hidden');
  }, 4000);
}

/**
 * Gọi Fetch API GET /api/v1/reports/completion-rate để lấy dữ liệu KPI mới nhất
 */
async function fetchCompletionRateKpi() {
  if (dashboardState.isFetching) return;
  dashboardState.isFetching = true;

  // Hiệu ứng xoay icon nút refresh
  if (elements.btnManualRefresh) {
    elements.btnManualRefresh.classList.add('loading');
  }

  const mode = elements.dataSourceMode ? elements.dataSourceMode.value : 'api';

  try {
    let reportData = null;

    if (mode === 'mock') {
      // Chế độ mô phỏng trực quan
      await new Promise(res => setTimeout(res, 400)); // Giả lập độ trễ mạng 400ms
      const mockResponse = generateMockKpiData();
      reportData = mockResponse.data;
      setOnlineStatus(true, 'Chế độ mô phỏng Realtime');
    } else {
      // Chế độ gọi API thật dùng Fetch API
      const response = await fetch(API_CONFIG.ENDPOINT, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        }
      });

      if (!response.ok) {
        throw new Error(`Mã lỗi HTTP: ${response.status} (${response.statusText})`);
      }

      const result = await response.json();
      
      // Kiểm tra cấu trúc payload
      if (result && result.data) {
        reportData = result.data;
      } else if (result && result.totalStudents !== undefined) {
        reportData = result;
      } else {
        throw new Error('Dữ liệu API không đúng định dạng');
      }

      setOnlineStatus(true, 'Đã đồng bộ từ API');
    }

    // Tiến hành render giao diện với dữ liệu vừa nhận được
    renderDashboard(reportData);

  } catch (error) {
    console.warn(`[KPI Fetch Warning]: ${error.message}`);
    
    // Nếu gọi API backend thất bại (ví dụ: server chưa khởi động khi test file HTML cục bộ),
    // tự động fallback sang Mock Data kèm thông báo hướng dẫn người dùng
    setOnlineStatus(false, 'Mất kết nối API (Dùng Fallback)');
    showToast(`Không kết nối được ${API_CONFIG.ENDPOINT}. Tự động hiển thị dữ liệu mẫu.`);

    const fallbackData = generateMockKpiData().data;
    renderDashboard(fallbackData);

  } finally {
    dashboardState.isFetching = false;
    if (elements.btnManualRefresh) {
      elements.btnManualRefresh.classList.remove('loading');
    }
  }
}

/**
 * Cập nhật giao diện badge trạng thái kết nối
 */
function setOnlineStatus(isOnline, statusMessage) {
  if (!elements.realtimeStatusPill || !elements.connectionStatusText) return;

  if (isOnline) {
    elements.realtimeStatusPill.classList.remove('offline');
    elements.connectionStatusText.textContent = statusMessage || 'Thời gian thực (Live)';
  } else {
    elements.realtimeStatusPill.classList.add('offline');
    elements.connectionStatusText.textContent = statusMessage || 'Mất kết nối API';
  }
}

/**
 * Khởi động tiến trình cập nhật tự động (Polling interval)
 * @param {number} intervalMs 
 */
function startAutoRefresh(intervalMs) {
  if (dashboardState.timerId) {
    clearInterval(dashboardState.timerId);
    dashboardState.timerId = null;
  }

  if (intervalMs > 0) {
    dashboardState.timerId = setInterval(() => {
      fetchCompletionRateKpi();
    }, intervalMs);
    console.log(`[KPI Monitor]: Bắt đầu tự động cập nhật mỗi ${intervalMs / 1000}s`);
  } else {
    console.log('[KPI Monitor]: Đã tắt tự động cập nhật');
  }
}

/**
 * Khởi tạo sự kiện và chạy lần đầu tiên khi trang tải xong
 */
function initDashboard() {
  // Lắng nghe nút bấm Làm Mới thủ công
  if (elements.btnManualRefresh) {
    elements.btnManualRefresh.addEventListener('click', () => {
      fetchCompletionRateKpi();
    });
  }

  // Lắng nghe thay đổi tần suất cập nhật
  if (elements.refreshIntervalSelect) {
    elements.refreshIntervalSelect.addEventListener('change', (e) => {
      const newInterval = parseInt(e.target.value, 10);
      startAutoRefresh(newInterval);
    });
  }

  // Lắng nghe chuyển đổi nguồn dữ liệu (API vs Mock)
  if (elements.dataSourceMode) {
    elements.dataSourceMode.addEventListener('change', () => {
      fetchCompletionRateKpi();
    });
  }

  // Gọi API lần đầu tiên
  fetchCompletionRateKpi();

  // Khởi động chu kỳ Polling cập nhật tự động theo thời gian thực
  const initialInterval = parseInt(elements.refreshIntervalSelect.value, 10);
  startAutoRefresh(initialInterval);
}

// Chạy khởi tạo khi tài liệu DOM đã sẵn sàng
document.addEventListener('DOMContentLoaded', initDashboard);
