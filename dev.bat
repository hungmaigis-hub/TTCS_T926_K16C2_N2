@echo off
title ICTU Internship - Backend Server
echo ========================================================
echo   Dang khoi dong may chu Backend FastAPI (Port 8000)...
echo ========================================================
python -m uvicorn main:app --reload --port 8000 --app-dir backend
pause
