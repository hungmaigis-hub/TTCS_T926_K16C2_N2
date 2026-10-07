@echo off
chcp 65001 >nul
echo ===============================================================
echo   DANG XU LY VA DAY CODE LEN GITHUB CHO NGUYEN VAN HIEU
echo   Repository: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2
echo ===============================================================

echo.
echo [1/6] Bat tinh nang duong dan dai (longpaths) cho Git Windows...
git config --global core.longpaths true

echo.
echo [2/6] Khoi tao Git repository trong thu muc hien tai...
git init
git config core.longpaths true

echo.
echo [3/6] Them cac tep ma nguon Backend cua Hieu vao Git...
git add app tests requirements.txt README.md .env.example .gitignore

echo.
echo [4/6] Tao commit ma nguon...
git commit -m "feat(backend): thiet ke model yeu_cau_ho_tro va endpoint POST /api/v1/support-requests - Nguyen Van Hieu"

echo.
echo [5/6] Cau hinh nhanh va remote...
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

echo.
echo [6/6] Dang day code len GitHub (nhanh main)...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ----------------------------------------------------------------------
    echo Nhap lenh pull de dong bo neu repo da co commit san tren GitHub...
    git pull origin main --allow-unrelated-histories --no-rebase -m "Merge remote main"
    git push -u origin main
    
    if errorlevel 1 (
        echo.
        echo Dang thu day len nhanh rieng feature/backend-hieu...
        git checkout -b feature/backend-hieu
        git push -u origin feature/backend-hieu
    )
)

echo.
echo ===============================================================
echo   HOAN TAT! KIEM TRA TREN GITHUB NHOM NHE!
echo ===============================================================
pause
