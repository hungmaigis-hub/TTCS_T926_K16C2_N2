@echo off
chcp 65001 >nul
echo =====================================================================
echo  ĐANG MỞ TRANG TẠO PULL REQUEST VÀO NHÁNH DEVELOP TRÊN GITHUB...
echo =====================================================================

set URL=https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2/compare/develop...feature/admin-users-hieu?expand=1

echo Đang mở trình duyệt tới địa chỉ:
echo %URL%

start "" "%URL%"

echo.
echo =====================================================================
echo Đã mở trình duyệt! Bạn chỉ cần kiểm tra tiêu đề và bấm 'Create pull request'.
echo =====================================================================
timeout /t 5 >nul
