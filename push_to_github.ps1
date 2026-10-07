Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  DANG XU LY VA DAY CODE LEN GITHUB CHO NGUYEN VAN HIEU" -ForegroundColor Green
Write-Host "  Repository: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2" -ForegroundColor Yellow
Write-Host "===============================================================" -ForegroundColor Cyan

# 1. Bật tính năng cho phép đường dẫn dài trên Windows (khắc phục lỗi Filename too long)
Write-Host "`n[1/5] Bật tính năng core.longpaths..." -ForegroundColor Cyan
git config --global core.longpaths true

# 2. Khởi tạo Git trong thư mục hiện tại
Write-Host "[2/5] Khởi tạo Git repository..." -ForegroundColor Cyan
git init
git config core.longpaths true

# 3. Chỉ add các tệp của dự án Backend (không dính các tệp rác của ổ D:)
Write-Host "[3/5] Thêm mã nguồn Backend..." -ForegroundColor Cyan
git add app tests requirements.txt README.md .env.example .gitignore

# 4. Commit mã nguồn
Write-Host "[4/5] Tạo commit..." -ForegroundColor Cyan
git commit -m "feat(backend): thiet ke model yeu_cau_ho_tro va endpoint POST /api/v1/support-requests - Nguyen Van Hieu"

# 5. Cấu hình remote và push
Write-Host "[5/5] Cấu hình remote và đẩy code..." -ForegroundColor Cyan
git branch -M main
git remote remove origin 2>$null
git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

Write-Host "`nĐang đẩy code lên GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nThử kéo dữ liệu cũ trên remote về để gộp..." -ForegroundColor Yellow
    git pull origin main --allow-unrelated-histories --no-rebase -m "Merge remote main"
    git push -u origin main

    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nĐẩy lên nhánh riêng feature/backend-hieu..." -ForegroundColor Yellow
        git checkout -b feature/backend-hieu
        git push -u origin feature/backend-hieu
    }
}

Write-Host "`n===============================================================" -ForegroundColor Green
Write-Host "  HOAN TAT! KIEM TRA TREN GITHUB CUA NHOM NHE!" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
