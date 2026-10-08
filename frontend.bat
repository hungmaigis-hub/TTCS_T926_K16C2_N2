@echo off
title ICTU Internship - Frontend Server
echo ========================================================
echo   Dang khoi dong may chu Frontend tai Port 5500...
echo   Dia chi: http://127.0.0.1:5500/frontend/html/quanly/them_ho_so.html
echo ========================================================
npx -y live-server --port=5500 . --open=frontend/html/quanly/them_ho_so.html
pause
