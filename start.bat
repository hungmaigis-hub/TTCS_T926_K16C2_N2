@echo off
title TTCS Web Server
color 0A
echo ==========================================
echo   TTCS - Quan ly Thuc tap sinh
echo ==========================================

:: Start MySQL (XAMPP)
echo [1/3] Khoi dong MySQL...
start "" "C:\xampp\mysql\bin\mysqld.exe" --defaults-file="C:\xampp\mysql\bin\my.ini"
timeout /t 3 /nobreak >nul

:: Start Backend FastAPI
echo [2/3] Khoi dong Backend API (port 8000)...
start "Backend API" cmd /k "cd /d ""%~dp0backend"" && python -m uvicorn main:app --reload --port 8000"
timeout /t 2 /nobreak >nul

:: Start Frontend HTTP Server
echo [3/3] Khoi dong Frontend (port 5500)...
start "Frontend" cmd /k "cd /d ""%~dp0"" && python script\serve_frontend.py"
timeout /t 2 /nobreak >nul

:: Open browser
echo Dang mo trinh duyet...
start "" "http://localhost:5500/html/public/index.html"

echo.
echo ==========================================
echo  Frontend : http://localhost:5500/html/public/index.html
echo  API Docs : http://localhost:8000/docs
echo ==========================================
pause
