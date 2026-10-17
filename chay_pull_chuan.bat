@echo off
chcp 65001 >nul
echo =====================================================================
echo  ĐẨY CODE CHUẨN XUẤT PHÁT TỪ GỐC ORIGIN/DEVELOP (GIỐNG TASK TRƯỚC)
echo  Phụ trách: Nguyễn Văn Hiếu
echo =====================================================================

:: 1. Lưu backup code
echo [1/5] Lưu backup code hiện tại vào branch backup-hieu...
git branch -f backup-hieu

:: 2. Lấy develop mới nhất và tạo nhánh mới từ origin/develop
echo [2/5] Lấy develop từ GitHub về và tạo nhánh feature/admin-create-user-hieu...
git fetch origin develop
git checkout -B feature/admin-create-user-hieu origin/develop

:: 3. Lấy code từ backup sang
echo [3/5] Lấy toàn bộ code của bạn vào nhánh mới...
git checkout backup-hieu -- .

:: 4. Add và Commit
echo [4/5] Add và Commit...
git add .
git commit -m "feat(admin-users): hoàn thiện endpoint POST /api/v1/admin/users tạo tài khoản người dùng - Nguyễn Văn Hiếu"

:: 5. Push lên GitHub
echo [5/5] Push nhánh mới lên GitHub...
git push -u origin feature/admin-create-user-hieu

echo.
echo =====================================================================
echo THÀNH CÔNG! Đang mở trang tạo Pull Request trên trình duyệt...
echo =====================================================================
start "" "https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2/compare/develop...feature/admin-create-user-hieu?expand=1"
pause
