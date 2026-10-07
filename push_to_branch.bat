@echo off
chcp 65001 >nul
echo ===============================================================
echo   DAY CODE LEN GITHUB CHO NGUYEN VAN HIEU (NHANH RIENG)
echo   Repo: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2
echo ===============================================================

echo.
echo [1/4] Bat longpaths cho Git Windows...
git config --global core.longpaths true
git config core.longpaths true

echo.
echo [2/4] Them file va tao commit...
git add app tests requirements.txt README.md .env.example .gitignore
git commit -m "feat(backend): thiet ke model yeu_cau_ho_tro va endpoint POST /api/v1/support-requests - Nguyen Van Hieu"

echo.
echo [3/4] Dat ten nhanh rieng nguyen-van-hieu va gan remote...
git branch -M nguyen-van-hieu
git remote remove origin 2>nul
git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

echo.
echo [4/4] Dang day code len GitHub...
git push -u origin nguyen-van-hieu --force

echo.
echo ===============================================================
echo   HOAN TAT! KIEM TRA TREN GITHUB TAI NHANH nguyen-van-hieu NHE!
echo ===============================================================
pause
