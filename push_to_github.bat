@echo off
chcp 65001 >nul
echo =====================================================================
echo  ĐẨY CODE LÊN GITHUB & TẠO PULL REQUEST VÀO NHÁNH DEVELOP
echo  Repository: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2
echo  Phụ trách: Nguyễn Văn Hiếu (Backend Developer)
echo =====================================================================
echo.

:: 1. Khởi tạo Git nếu chưa có
if not exist ".git" (
    echo [1/5] Khởi tạo git repository...
    git init
    git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git
) else (
    echo [1/5] Git đã được khởi tạo.
)

:: 2. Đổi remote nếu cần
git remote set-url origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

:: 3. Tạo và chuyển sang nhánh tính năng mới
echo [2/5] Tạo và chuyển sang nhánh feature/admin-users-hieu...
git checkout -B feature/admin-users-hieu

:: 4. Thêm các file và commit
echo [3/5] Thêm file và commit code...
git add .
git commit -m "feat(admin-users): hoàn thiện endpoint POST /api/v1/admin/users tạo tài khoản người dùng - Nguyễn Văn Hiếu"

:: 5. Push lên GitHub
echo [4/5] Đang đẩy (push) code lên GitHub...
git push -u origin feature/admin-users-hieu

echo.
echo =====================================================================
echo [5/5] ĐÃ PUSH THÀNH CÔNG LÊN GITHUB!
echo Bây giờ bạn hãy mở đường link sau trên trình duyệt để tạo Pull Request vào nhánh develop:
echo.
echo https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2/compare/develop...feature/admin-users-hieu?expand=1
echo =====================================================================
pause
