@echo off
chcp 65001 >nul
echo ========================================================
echo   ĐẨY CODE NHẬT KÝ HOẠT ĐỘNG (AUDIT LOGS) LÊN GITHUB
echo   Tác giả: Nguyễn Văn Hiếu
echo   Kho lưu trữ: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2
echo ========================================================
echo.

:: 1. Khởi tạo git nếu chưa có
if not exist .git (
    echo [*] Khởi tạo git repository...
    git init
    git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git
)

:: 2. Fetch nhánh develop mới nhất từ GitHub
echo [*] Đang tải thông tin nhánh develop từ origin...
git fetch origin develop

:: 3. Tạo nhánh backup code hiện tại
echo [*] Lưu tạm nhánh hiện tại thành backup-audit-logs...
git checkout -B backup-audit-logs

:: 4. Tạo nhánh mới xuất phát trực tiếp từ gốc develop
echo [*] Tạo nhánh feature/audit-logs-hieu từ origin/develop...
git checkout -B feature/audit-logs-hieu origin/develop

:: 5. Lấy toàn bộ code vừa viết vào nhánh mới
echo [*] Đang chuyển code vào nhánh feature/audit-logs-hieu...
git checkout backup-audit-logs -- .

:: 6. Thêm và Commit
echo [*] Đang commit code...
git add .
git commit -m "feat(audit-logs): thiết kế model nhat_ky_hoat_dong, middleware và endpoint GET audit-logs - Nguyễn Văn Hiếu"

:: 7. Push lên GitHub (không cần force)
echo [*] Đang push nhánh feature/audit-logs-hieu lên GitHub...
git push -u origin feature/audit-logs-hieu

echo.
echo ========================================================
echo [OK] ĐÃ PUSH THÀNH CÔNG LÊN GITHUB!
echo Bây giờ bạn hãy mở liên kết bên dưới để tạo Pull Request:
echo https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2/compare/develop...feature/audit-logs-hieu?expand=1
echo ========================================================
pause
